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
    
    # === 確保 Phase 3 結算只執行一次 ===
    if not game.last_year_report:
        rp, hp = game.r_role_party, game.h_role_party
        ra, ha = st.session_state[f"{rp.name}_acts"], st.session_state[f"{hp.name}_acts"]
        d = st.session_state.turn_data
        
        returned_to_r = 0.0; confiscated_to_budget = 0.0
        corr_support_penalty = 0.0
        corr_caught = False; crony_caught = False
        
        proj_fund = d.get('proj_fund', 0)
        corr_amt = proj_fund * (ha['corr'] / 100.0)
        crony_base = proj_fund * (ha['crony'] / 100.0)
        crony_income = crony_base * 0.1
        
        catch_prob_base = max(0.1, (rp.investigate_ability - hp.stealth_ability)) * 2.0
        
        if corr_amt > 0 and random.random() < min(1.0, catch_prob_base * (corr_amt / max(1.0, proj_fund))):
            returned_to_r += corr_amt; confiscated_to_budget += corr_amt * 0.4
            corr_support_penalty = (corr_amt * max(1.0, hp.build_ability)) / max(1.0, proj_fund) * 100.0 * cfg['SUPPORT_CONVERSION_RATE']
            corr_caught = True; corr_amt = 0

        if crony_base > 0 and random.random() < min(1.0, catch_prob_base * (crony_base / max(1.0, proj_fund))):
            returned_to_r += crony_base
