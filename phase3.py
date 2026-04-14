# ==========================================
# phase3.py
# 負責 第三階段 (年度總結算報告與視覺化)
# ==========================================
import streamlit as st
import random
import formulas
import i18n
t = i18n.t

def render(game, cfg):
    st.header(t("⚖️ Phase 3: 年度結算報告"))
    
    if not game.last_year_report:
        rp, hp = game.r_role_party, game.h_role_party
        ra, ha = st.session_state[f"{rp.name}_acts"], st.session_state[f"{hp.name}_acts"]
        d = st.session_state.turn_data
        
        returned_to_r = 0.0
        confiscated_to_budget = 0.0
        corr_support_penalty = 0.0
        corr_caught = False
        crony_caught = False
        
        proj_fund = d.get('proj_fund', 0)
        corr_amt = proj_fund * (ha.get('corr', 0) / 100.0)
        crony_base = proj_fund * (ha.get('crony', 0) / 100.0)
        crony_income = crony_base * 0.1
        
        catch_prob_base = max(0.1, (rp.investigate_ability - hp.stealth_ability)) * 2.0
        
        if corr_amt > 0 and random.random() < min(1.0, catch_prob_base * (corr_amt / max(1.0, proj_fund))):
            returned_to_r += corr_amt
            confiscated_to_budget += corr_amt * 0.4
            corr_support_penalty = (corr_amt * max(1.0, hp.build_ability)) / max(1.0, proj_fund) * 100.0 * cfg['SUPPORT_CONVERSION_RATE']
            corr_caught = True
            corr_amt = 0

        if crony_base > 0 and random.random() < min(1.0, catch_prob_base * (crony_base / max(1.0, proj_fund))):
            returned_to_r += crony_base
            confiscated_to_budget += crony_base * 0.5
            crony_caught = True
            crony_base = 0
            crony_income = 0
            
        res_exec = formulas.calc_economy(cfg, game.gdp, game.total_budget, proj_fund, d.get('bid_cost', 1), hp.build_ability, game.current_real_decay, corr_amt)
        budg = cfg['BASE_TOTAL_BUDGET'] + (res_exec['est_gdp'] * cfg['HEALTH_MULTIPLIER'])
        
        hp_base = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == hp.name else 0)
        rp_base = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == rp.name else 0)
        
        hp_inc = hp_base + res_exec['payout_h'] + corr_amt + crony_income
        rp_inc = rp_base + res_exec['payout_r'] + returned_to_r
        
        shift = formulas.calc_support_shift(cfg, hp, rp, res_exec['payout_h'], res_exec['est_gdp'], proj_fund, game.gdp, ha, ra, res_exec['h_idx'], d.get('claimed_decay', 0.0), game.sanity, game.emotion)
        hp_sup_new = max(0.0, min(100.0, hp.support + shift['actual_shift'] - corr_support_penalty))
        
        gdp_grw_bonus = ((res_exec['est_gdp'] - game.gdp)/max(1.0, game.gdp)) * 100.0
        emotion_delta = (ha.get('incite', 0) + ra.get('incite', 0)) * 0.1 - gdp_grw_bonus - (game.sanity * 0.20)
        new_emotion = max(0.0, min(100.0, game.emotion + emotion_delta))
        
        f_target_san = max(0.0, min(100.0, 50.0 + (ra.get('edu_amt', 0) / 500.0) * 50.0))
        f_san_move = (f_target_san - game.sanity) * 0.2
        new_sanity = max(0.0, min(100.0, game.sanity - (new_emotion * 0.02) + f_san_move))
        
        game.last_year_report = {
            'old_gdp': game.gdp, 'old_san': game.sanity, 'old_emo': game.emotion, 'old_budg': game.total_budget, 'old_h_fund': game.h_fund,
            'h_party_name': hp.name, 'h_perf': shift['h_perf'], 'r_perf': shift['r_perf'],
            'h_inc': hp_inc, 'r_inc': rp_inc, 
            'h_base': hp_base, 'r_base': rp_base, 'h_payout': res_exec['payout_h'], 'r_payout': res_exec['payout_r'],
            'h_extra': corr_amt + crony_income, 'r_extra': returned_to_r,
            'h_pol_cost': ha.get('tot_action', 0) + ha.get('legal', 0), 'r_pol_cost': ra.get('tot_action', 0) + ra.get('legal', 0),
            'h_maint': ha.get('tot_maint', 0), 'r_maint': ra.get('tot_maint', 0),
            'real_decay': game.current_real_decay, 
            'corr_caught': corr_caught, 'crony_caught': crony_caught
        }

        hp.support, rp.support = hp_sup_new, 100.0 - hp_sup_new
        if game.year % cfg['ELECTION_CYCLE'] == 1:
            winner = hp if hp.support > rp.support else rp
            st.session_state.news_flash = f"🎉 **【大選結果】** {winner.name} 取勝，成為當權派！"
            st.session_state.anim = 'balloons'
            game.ruling_party = winner

        game.gdp = res_exec['est_gdp']
        game.h_fund = res_exec['payout_h']
        game.total_budget = budg + confiscated_to_budget
        
        hp.wealth += hp_inc - game.last_year_report['h_pol_cost'] - game.last_year_report['h_maint']
        rp.wealth += rp_inc - game.last_year_report['r_pol_cost'] - game.last_year_report['r_maint']

        rp.investigate_ability = ra.get('t_inv', rp.investigate_ability)
        rp.predict_ability = ra.get('t_pre', rp.predict_ability)
        rp.media_ability = ra.get('t_med', rp.media_ability)
        rp.stealth_ability = ra.get('t_stl', rp.stealth_ability)
        rp.build_ability = ra.get('t_bld', rp.build_ability)
        
        hp.investigate_ability = ha.get('t_inv', hp.investigate_ability)
        hp.predict_ability = ha.get('t_pre', hp.predict_ability)
        hp.media_ability = ha.get('t_med', hp.media_ability)
        hp.stealth_ability = ha.get('t_stl', hp.stealth_ability)
        hp.build_ability = ha.get('t_bld', hp.build_ability)
        
        # 將對手動作完整記錄供明年的預估參考
        hp.last_acts = ha.copy()
        rp.last_acts = ra.copy()
        
        game.record_history(is_election=(game.year % cfg['ELECTION_CYCLE'] == 1))
    
    rep = game.last_year_report
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(t("#### 💰 經濟與財政"))
        st.write(f"GDP 變化: `{rep['old_gdp']:.1f} ➔ {game.gdp:.1f}`")
        
        st.write(f"**執行系統收益總結:** `(基礎 {rep['h_base']:.1f} + 標案 {rep['h_payout']:.1f} + 業外 {rep['h_extra']:.1f}) - (政策花費 {rep['h_pol_cost']:.1f} + 維護費 {rep['h_maint']:.1f}) = {rep['h_inc'] - rep['h_pol_cost'] - rep['h_maint']:.1f}`")
        st.write(f"**監管系統收益總結:** `(基礎 {rep['r_base']:.1f} + 標案 {rep['r_payout']:.1f} + 業外 {rep['r_extra']:.1f}) - (政策花費 {rep['r_pol_cost']:.1f} + 維護費 {rep['r_maint']:.1f}) = {rep['r_inc'] - rep['r_pol_cost'] - rep['r_maint']:.1f}`")
        
        if rep.get('corr_caught'):
            st.error(t("🚨 貪污醜聞爆發！執行系統貪污被情報處查獲，沒收所有非法所得並重挫民意。"))
        if rep.get('crony_caught'):
            st.error(t("🚨 圖利爭議！執行系統圖利親信遭舉發，強制沒收資金返還國庫與監管系統。"))

    with c2:
        st.markdown(t("#### 🧠 社會與民意"))
        st.write(f"{t('資訊辨識')}: `{rep['old_san']:.1f} ➔ {game.sanity:.1f}`")
        st.write(f"{t('選民情緒')}: `{rep['old_emo']:.1f} ➔ {game.emotion:.1f}`")
        st.write(f"{t('施政滿意度位移 (執行/監管)')}: `{rep['h_perf']:.1f}% / {rep['r_perf']:.1f}%`")

    st.markdown("---")
    if st.button(t("⏩ 確認報告並進入下一年"), type="primary", use_container_width=True):
        game.year += 1
        game.phase = 1
        game.p1_step = 'draft_r'
        game.p1_proposals = {'R': None, 'H': None}
        game.p1_selected_plan = None
        for k in list(st.session_state.keys()):
            if k.endswith('_acts'): del st.session_state[k]
        if 'turn_initialized' in st.session_state: del st.session_state.turn_initialized
        st.rerun()
