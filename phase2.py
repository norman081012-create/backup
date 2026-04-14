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
        ra = st.session_state.get(f"{rp.name}_acts", {})
        ha = st.session_state.get(f"{hp.name}_acts", {})
        d = st.session_state.get('turn_data', {})
        
        returned_to_r = 0.0
        confiscated_to_budget = 0.0
        corr_support_penalty = 0.0
        corr_caught = False
        crony_caught = False
        
        proj_fund = float(d.get('proj_fund') or 0.0)
        bid_cost = float(d.get('bid_cost') or 1.0)
        claimed_decay = float(d.get('claimed_decay') or 0.0)
        r_pays = float(d.get('r_pays') or 0.0)
        h_pays = float(d.get('h_pays') or 0.0)
        
        corr_amt = proj_fund * (float(ha.get('corr') or 0) / 100.0)
        crony_base = proj_fund * (float(ha.get('crony') or 0) / 100.0)
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
            
        res_exec = formulas.calc_economy(cfg, float(game.gdp), float(game.total_budget), proj_fund, bid_cost, float(hp.build_ability), float(game.current_real_decay), corr_amt)
        budg = cfg['BASE_TOTAL_BUDGET'] + (res_exec['est_gdp'] * cfg['HEALTH_MULTIPLIER'])
        
        hp_base = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == hp.name else 0)
        rp_base = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == rp.name else 0)
        
        hp_project_net = res_exec['payout_h'] - res_exec['act_fund'] + r_pays
        rp_project_net = res_exec['payout_r'] - r_pays
        
        hp_inc = hp_base + hp_project_net + corr_amt + crony_income
        rp_inc = rp_base + rp_project_net + returned_to_r
        
        shift = formulas.calc_support_shift(cfg, hp, rp, game.ruling_party.name, res_exec['payout_h'], res_exec['est_gdp'], proj_fund, game.gdp, ha, ra, res_exec['h_idx'], claimed_decay, game.current_real_decay, game.sanity, game.emotion)
        hp_sup_new = max(0.0, min(100.0, hp.support + shift['actual_shift'] - corr_support_penalty))
        
        gdp_grw_bonus = ((res_exec['est_gdp'] - game.gdp)/max(1.0, game.gdp)) * 100.0
        emotion_delta = (float(ha.get('incite') or 0) + float(ra.get('incite') or 0)) * 0.1 - gdp_grw_bonus - (game.sanity * 0.20)
        new_emotion = max(0.0, min(100.0, game.emotion + emotion_delta))
        
        f_target_san = max(0.0, min(100.0, 50.0 + (float(ra.get('edu_amt') or 0) / 500.0) * 50.0))
        f_san_move = (f_target_san - game.sanity) * 0.2
        new_sanity = max(0.0, min(100.0, game.sanity - (new_emotion * 0.02) + f_san_move))
        
        h_tot_action = float(ha.get('tot_action') or 0)
        r_tot_action = float(ra.get('tot_action') or 0)
        h_tot_maint = float(ha.get('tot_maint') or 0)
        r_tot_maint = float(ra.get('tot_maint') or 0)
        
        game.last_year_report = {
            'old_gdp': game.gdp, 'old_san': game.sanity, 'old_emo': game.emotion, 'old_budg': game.total_budget, 'old_h_fund': game.h_fund,
            'h_party_name': hp.name, 'h_perf': shift['h_perf'], 'r_perf': shift['r_perf'],
            'h_inc': hp_inc, 'r_inc': rp_inc, 
            'h_base': hp_base, 'r_base': rp_base, 
            'h_payout': res_exec['payout_h'], 'r_payout': res_exec['payout_r'],
            'h_act_fund': res_exec['act_fund'],
            'r_pays': r_pays, 'h_pays': h_pays,
            'h_extra': corr_amt + crony_income, 'r_extra': returned_to_r,
            'h_pol_cost': h_tot_action, 'r_pol_cost': r_tot_action,
            'h_maint': h_tot_maint, 'r_maint': r_tot_maint,
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
        
        hp.wealth += hp_inc - h_tot_action - h_tot_maint
        rp.wealth += rp_inc - r_tot_action - r_tot_maint

        rp.investigate_ability = float(ra.get('t_inv') or rp.investigate_ability)
        rp.predict_ability = float(ra.get('t_pre') or rp.predict_ability)
        rp.media_ability = float(ra.get('t_med') or rp.media_ability)
        rp.stealth_ability = float(ra.get('t_stl') or rp.stealth_ability)
        rp.build_ability = float(ra.get('t_bld') or rp.build_ability)
        
        hp.investigate_ability = float(ha.get('t_inv') or hp.investigate_ability)
        hp.predict_ability = float(ha.get('t_pre') or hp.predict_ability)
        hp.media_ability = float(ha.get('t_med') or hp.media_ability)
        hp.stealth_ability = float(ha.get('t_stl') or hp.stealth_ability)
        hp.build_ability = float(ha.get('t_bld') or hp.build_ability)
        
        hp.last_acts = ha.copy()
        rp.last_acts = ra.copy()
        
        game.record_history(is_election=(game.year % cfg['ELECTION_CYCLE'] == 1))
    
    rep = game.last_year_report
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(t("#### 💰 經濟與財政"))
        st.write(f"GDP 變化: `{rep['old_gdp']:.1f} ➔ {game.gdp:.1f}`")
        st.write(f"**執行系統收益總結:** `(基礎 {rep['h_base']:.1f} + 標案 {rep['h_payout']:.1f} - 工程成本 {rep['h_act_fund']:.1f} + 監管補貼 {rep['r_pays']:.1f} + 業外 {rep['h_extra']:.1f}) - (政策花費 {rep['h_pol_cost']:.1f} + 維護費 {rep['h_maint']:.1f}) = {rep['h_inc'] - rep['h_pol_cost'] - rep['h_maint']:.1f}`")
        st.write(f"**監管系統收益總結:** `(基礎 {rep['r_base']:.1f} + 國庫剩餘 {rep['r_payout']:.1f} - 提案出資 {rep['r_pays']:.1f} + 業外 {rep['r_extra']:.1f}) - (政策花費 {rep['r_pol_cost']:.1f} + 維護費 {rep['r_maint']:.1f}) = {rep['r_inc'] - rep['r_pol_cost'] - rep['r_maint']:.1f}`")
        
        if rep.get('corr_caught'): st.error(t("🚨 貪污醜聞爆發！執行系統貪污被情報處查獲，沒收所有非法所得並重挫民意。"))
        if rep.get('crony_caught'): st.error(t("🚨 圖利爭議！執行系統圖利親信遭舉發，強制沒收資金返還國庫與監管系統。"))

    with c2:
        st.markdown(t("#### 🧠 社會與民意"))
        st.write(f"{t('資訊辨識')}: `{rep['old_san']:.1f} ➔ {game.sanity:.1f}`")
        st.write(f"{t('選民情緒')}: `{rep['old_emo']:.1f} ➔ {game.emotion:.1f}`")
        st.write(f"{t('施政滿意度位移 (執行/監管)')}: `{rep['h_perf']:.1f}% / {rep['r_perf']:.1f}%`")

    st.markdown("---")
    if st.button(t("⏩ 確認報告並進入下一年"), type="primary", use_container_width=True):
        game.year += 1
        if game.year > cfg['END_YEAR']:
            game.phase = 4
        else:
            game.phase = 1
            game.p1_step = 'draft_r'
            game.p1_proposals = {'R': None, 'H': None}
            game.p1_selected_plan = None
            for k in list(st.session_state.keys()):
                if k.endswith('_acts'): del st.session_state[k]
            if 'turn_initialized' in st.session_state: del st.session_state.turn_initialized
        st.rerun()
