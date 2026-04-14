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
        corr_caught = False
        crony_caught = False
        
        proj_fund = float(d.get('proj_fund') or 0.0)
        bid_cost = float(d.get('bid_cost') or 1.0)
        claimed_decay = float(d.get('claimed_decay') or 0.0)
        r_pays = float(d.get('r_pays') or 0.0)
        h_pays = float(d.get('h_pays') or 0.0)
        
        corr_pct_val = float(ha.get('corr') or 0)
        crony_pct_val = float(ha.get('crony') or 0)
        
        corr_amt = proj_fund * (corr_pct_val / 100.0)
        crony_base = proj_fund * (crony_pct_val / 100.0)
        crony_income = crony_base * 0.1  
        
        rp_inv_pct = rp.investigate_ability / 10.0
        hp_stl_pct = hp.stealth_ability / 10.0
        actual_catch_mult = max(0.1, (rp_inv_pct * cfg['R_INV_BONUS']) - hp_stl_pct + 1.0)
        
        rolls_corr = corr_pct_val * actual_catch_mult
        catch_prob_corr = 1.0 - (1.0 - cfg['CATCH_RATE_PER_PERCENT'])**rolls_corr
        
        rolls_crony = crony_pct_val * actual_catch_mult
        catch_prob_crony = 1.0 - (1.0 - cfg['CRONY_CATCH_RATE_PER_PERCENT'])**rolls_crony
        
        if corr_amt > 0 and random.random() < catch_prob_corr:
            returned_to_r += corr_amt
            confiscated_to_budget += corr_amt * 0.4
            corr_caught = True
            corr_amt = 0

        if crony_base > 0 and random.random() < catch_prob_crony:
            returned_to_r += crony_base
            confiscated_to_budget += crony_base * 0.5
            crony_caught = True
            crony_base = 0
            crony_income = 0
            
        # [修正] 最終結算傳入 r_pays 確保正確計算
        res_exec = formulas.calc_economy(cfg, float(game.gdp), float(game.total_budget), proj_fund, bid_cost, float(hp.build_ability), float(game.current_real_decay), corr_amt=corr_amt, r_pays=r_pays)
        budg = cfg['BASE_TOTAL_BUDGET'] + (res_exec['est_gdp'] * cfg['HEALTH_MULTIPLIER'])
        
        hp_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == hp.name else 0))
        rp_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == rp.name else 0))
        
        hp_project_net = res_exec['h_project_profit']
        rp_project_net = res_exec['payout_r'] - r_pays
        
        hp_inc = hp_base + hp_project_net + corr_amt + crony_income
        rp_inc = rp_base + rp_project_net + returned_to_r
        
        shifts = formulas.calc_support_amounts(
            cfg, hp, rp, game.ruling_party.name, res_exec['est_gdp'], game.gdp, 
            ha, ra, claimed_decay, game.sanity, game.emotion, bid_cost, res_exec['c_net'], game.current_real_decay
        )
        
        a_sup_amt, b_sup_amt = game.update_support_queues({
            game.party_A.name: shifts[game.party_A.name],
            game.party_B.name: shifts[game.party_B.name]
        })
        
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
            'h_party_name': hp.name,
            'shifts': shifts, 
            'h_inc': hp_inc, 'r_inc': rp_inc, 
            'h_base': hp_base, 'r_base': rp_base, 
            'h_payout': res_exec['payout_h'], 'r_payout': res_exec['payout_r'],
            'h_act_fund': res_exec['act_fund'],
            'r_pays': r_pays, 'h_pays': h_pays,
            'h_extra': corr_amt + crony_income, 'r_extra': returned_to_r,
            'h_pol_cost': h_tot_action, 'r_pol_cost': r_tot_action,
            'h_maint': h_tot_maint, 'r_maint': r_tot_maint,
            'corr_caught': corr_caught, 'crony_caught': crony_caught
        }
        
        if game.year % cfg['ELECTION_CYCLE'] == 1:
            winner = hp if hp.support > rp.support else rp
            gap = abs(hp.support - rp.support)
            if gap > 20: msg = f"🎉 **【大選結果：狂勝！】** {winner.name} 黨以 {gap:.1f}% 的差距取得壓倒性勝利！"
            elif gap > 5: msg = f"🎉 **【大選結果：穩定勝選】** {winner.name} 黨穩紮穩打贏得執政權！"
            else: msg = f"🎉 **【大選結果：驚險過關】** 選情陷入泥沼！{winner.name} 黨微幅險勝！"
            
            st.session_state.news_flash = msg
            st.session_state.anim = 'balloons'
            game.ruling_party = winner

        game.gdp = res_exec['est_gdp']
        game.h_fund = res_exec['payout_h']
        game.total_budget = budg + confiscated_to_budget
        
        hp.wealth += hp_inc - h_tot_action - h_tot_maint
        rp.wealth += rp_inc - r_tot_action - r_tot_maint

        hp.last_acts = ha.copy(); rp.last_acts = ra.copy()
        game.record_history(is_election=(game.year % cfg['ELECTION_CYCLE'] == 1))
    
    rep = game.last_year_report
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(t("#### 💰 經濟與財政"))
        st.write(f"GDP 變化: `{rep['old_gdp']:.1f} ➔ {game.gdp:.1f}`")
        if rep.get('corr_caught'): st.error(t("🚨 貪污醜聞爆發！執行系統貪污被查獲，沒收非法所得。"))
        if rep.get('crony_caught'): st.error(t("🚨 圖利爭議！執行系統圖利遭舉發，強制沒收資金。"))

    with c2:
        st.markdown(t("#### 📈 支持量變動 (點數)"))
        h_shift = rep['shifts'][game.h_role_party.name]
        r_shift = rep['shifts'][game.r_role_party.name]
        
        st.write(f"**執行系統新增支持量**:")
        h_perf_color = "green" if h_shift['perf'] > 0 else "red"
        h_camp
