# ==========================================
# phase2.py
# ==========================================
import streamlit as st
import config
import formulas
import ui_core
import i18n
t = i18n.t

def render(game, view_party, opponent_party, cfg):
    is_h = (view_party.name == game.h_role_party.name)
    h_label = t('🛡️ H-System')
    r_label = t('⚖️ R-System')
    st.subheader(f"{t('🛠️ Phase 2: Execution - Turn:')} {view_party.name} ({h_label if is_h else r_label})")
    
    d = st.session_state.get('turn_data', {})
    req_cost = float(d.get('req_cost', 0.0))
    bid_cost = float(d.get('bid_cost', 1.0))
    
    # 執行系統的資金池是 黨產 + Req. Cost
    if is_h: cw = float(view_party.wealth) + req_cost
    else: cw = float(view_party.wealth)
    
    # Calculate Capacities (EV)
    h_bonus = 1.2 if is_h else 1.0
    r_bonus = 1.2 if not is_h else 1.0
    
    med_cap = view_party.media_ability * 10.0 * h_bonus
    inv_cap = view_party.investigate_ability * 10.0 * r_bonus
    ci_cap = view_party.stealth_ability * 10.0
    edu_cap = view_party.edu_ability * 10.0 * r_bonus
    eng_limit = view_party.build_ability * 10.0 * 2.0  # 升級上限受限於 Engineering
    
    last_acts = view_party.last_acts if hasattr(view_party, 'last_acts') else {}

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(t("#### 📣 Resource Allocation"))
        
        st.write(f"**{t('Intelligence')} (Capacity: {inv_cap:.1f} EV)**")
        col_i1, col_i2 = st.columns(2)
        w_i_cen = col_i1.number_input(t("Media Censorship"), min_value=0, max_value=100, value=last_acts.get('w_i_cen', 0))
        w_i_org = col_i2.number_input(t("Org Audit"), min_value=0, max_value=100, value=last_acts.get('w_i_org', 0))
        i_tot = max(1, w_i_cen + w_i_org)
        alloc_inv_censor = inv_cap * (w_i_cen / i_tot)
        alloc_inv_audit = inv_cap * (w_i_org / i_tot)
        
        st.write(f"**{t('Counter-Intel')} (Capacity: {ci_cap:.1f} EV)**")
        col_c1, col_c2 = st.columns(2)
        w_c_cen = col_c1.number_input(t("Anti-Censorship"), min_value=0, max_value=100, value=last_acts.get('w_c_cen', 0))
        w_c_org = col_c2.number_input(t("Hide Org"), min_value=0, max_value=100, value=last_acts.get('w_c_org', 0))
        c_tot = max(1, w_c_cen + w_c_org)
        alloc_ci_anticen = ci_cap * (w_c_cen / c_tot)
        alloc_ci_hideorg = ci_cap * (w_c_org / c_tot)
        
        st.write(f"**{t('Media Dept')} (Capacity: {med_cap:.1f} EV)**")
        col_m1, col_m2, col_m3 = st.columns(3)
        w_m_cam = col_m1.number_input(t("Campaign"), min_value=0, max_value=100, value=last_acts.get('w_m_cam', 0))
        w_m_inc = col_m2.number_input(t("Incite Emotion"), min_value=0, max_value=100, value=last_acts.get('w_m_inc', 0))
        w_m_con = col_m3.number_input(t("Media Control"), min_value=0, max_value=100, value=last_acts.get('w_m_con', 0))
        m_tot = max(1, w_m_cam + w_m_inc + w_m_con)
        alloc_med_camp = med_cap * (w_m_cam / m_tot)
        alloc_med_incite = med_cap * (w_m_inc / m_tot)
        alloc_med_control = med_cap * (w_m_con / m_tot)
        
        st.write(f"**{t('Edu Dept')} (Capacity: {edu_cap:.1f} EV)**")
        old_edu_stance = view_party.edu_stance
        e_dir = st.radio(t("Education Shift Direction"), ["Maintain", "Shift Left (Rote)", "Shift Right (Critical)"], horizontal=True)
        if e_dir == "Shift Left (Rote)": edu_shift = -edu_cap * 0.5
        elif e_dir == "Shift Right (Critical)": edu_shift = edu_cap * 0.5
        else: edu_shift = 0.0
        new_edu_stance = max(-100.0, min(100.0, old_edu_stance + edu_shift))
        st.info(f"Education Stance: `{old_edu_stance:.1f}` ➔ `{new_edu_stance:.1f}`")

    with c2:
        st.markdown(t("#### 🔒 Financial & Engineering (EV)"))
        
        h_crony_amt = 0.0
        invest_wealth = 0.0
        total_ev = 0.0
        c_net = 0.0
        
        unit_cost = formulas.calc_unit_cost(cfg, game.gdp, view_party.build_ability, view_party.current_forecast)
        
        if is_h:
            invest_wealth = st.number_input(t("Invest Party Wealth into Engineering ($)"), min_value=0.0, max_value=float(view_party.wealth), value=min(req_cost, float(view_party.wealth)))
            # 根據要求：Cronyism 上限等於 Invest Wealth (但不超過 Req Cost)
            crony_max = min(invest_wealth, req_cost)
            h_crony_amt = st.number_input(t("Cronyism ($)"), min_value=0.0, max_value=float(crony_max), value=float(min(last_acts.get('crony_amt', 0.0), crony_max)))
            
            total_money = invest_wealth - h_crony_amt
            total_ev = total_money / max(0.01, unit_cost)
            
            st.markdown(f"**💰 {t('Total Available EV')}:** `{total_ev:.1f}` EV")
            
            c_net = st.number_input(f"Allocate EV to National Project (Target EV: {bid_cost})", min_value=0.0, max_value=float(total_ev), value=float(min(total_ev, bid_cost)))
            available_upgrade_ev = total_ev - c_net
        else:
            invest_wealth = st.number_input(t("Invest Party Wealth into Engineering ($)"), min_value=0.0, max_value=float(view_party.wealth), value=0.0)
            total_money = invest_wealth
            total_ev = total_money / max(0.01, unit_cost)
            st.markdown(f"**💰 {t('Total Available EV')}:** `{total_ev:.1f}` EV")
            available_upgrade_ev = total_ev

        st.markdown("##### 🛠️ Upgrade Departments (Target Value)")
        st.caption(f"*(All abilities scale from 0 to infinity. EV Upgrades limited to `{eng_limit:.1f}` by Engineering.)*")
        
        u1, u2 = st.columns(2)
        t_pre = u1.number_input(t("Think Tank"), min_value=0.0, value=float(view_party.predict_ability*10.0))
        t_inv = u1.number_input(t("Intelligence"), min_value=0.0, value=float(view_party.investigate_ability*10.0))
        t_med = u1.number_input(t("Media Dept"), min_value=0.0, value=float(view_party.media_ability*10.0))
        t_stl = u2.number_input(t("Counter-Intel"), min_value=0.0, value=float(view_party.stealth_ability*10.0))
        t_bld = u2.number_input(t("Engineering"), min_value=0.0, value=float(view_party.build_ability*10.0))
        t_edu = u2.number_input(t("Edu Dept"), min_value=0.0, value=float(view_party.edu_ability*10.0))
        
        def calc_upgrade_ev(new_val, old_val):
            return max(0, (new_val - old_val * 10.0) * 1.5)
            
        upgrade_ev = sum([calc_upgrade_ev(n, o) for n, o in zip(
            [t_pre, t_inv, t_med, t_stl, t_bld, t_edu],
            [view_party.predict_ability, view_party.investigate_ability, view_party.media_ability, view_party.stealth_ability, view_party.build_ability, view_party.edu_ability]
        )])
        
        maint_ev = (view_party.predict_ability + view_party.investigate_ability + view_party.media_ability + view_party.stealth_ability + view_party.build_ability + view_party.edu_ability) * 1.5
        
        net_ev = available_upgrade_ev - maint_ev - upgrade_ev
        
        st.write(f"**Total Costs EV:** `{maint_ev + upgrade_ev:.1f}` (Maint: {maint_ev:.1f} + Upgrades: {upgrade_ev:.1f})")
        
        is_invalid = False
        if upgrade_ev > eng_limit:
            st.error(f"🚨 Upgrades exceed Engineering Limit! Max upgrade EV allowed: `{eng_limit:.1f}`.")
            is_invalid = True
        elif net_ev < 0:
            st.error(f"🚨 Insufficient EV! Deficit of {-net_ev:.1f} EV. Downgrade departments or inject more Party Wealth.")
            is_invalid = True
        else:
            if is_h:
                st.success(f"✅ EV flow is valid. Excess `{net_ev:.1f}` EV will be discarded at year-end.")
            else:
                st.info(f"✅ EV flow is valid. Excess `{net_ev:.1f}` EV will be discarded at year-end.")

    my_acts = {
        'w_i_cen': w_i_cen, 'w_i_org': w_i_org,
        'alloc_inv_censor': alloc_inv_censor, 'alloc_inv_audit': alloc_inv_audit,
        'w_c_cen': w_c_cen, 'w_c_org': w_c_org,
        'alloc_ci_anticen': alloc_ci_anticen, 'alloc_ci_hideorg': alloc_ci_hideorg,
        'w_m_cam': w_m_cam, 'w_m_inc': w_m_inc, 'w_m_con': w_m_con,
        'alloc_med_camp': alloc_med_camp, 'alloc_med_incite': alloc_med_incite, 'alloc_med_control': alloc_med_control,
        'edu_stance': new_edu_stance, 'crony_amt': h_crony_amt, 
        't_pre': t_pre/10.0, 't_inv': t_inv/10.0, 't_med': t_med/10.0, 't_stl': t_stl/10.0, 't_bld': t_bld/10.0, 't_edu': t_edu/10.0,
        'invest_wealth': invest_wealth, 'c_net': c_net
    }
    
    st.markdown("---")
    
    if is_h:
        act_ha = my_acts
        act_ra = st.session_state.get(f"{opponent_party.name}_acts", {'alloc_med_control': 0, 'alloc_med_camp': 0, 'alloc_med_incite': 0, 'alloc_inv_censor': 0})
    else:
        act_ra = my_acts
        act_ha = st.session_state.get(f"{opponent_party.name}_acts", {'alloc_med_control': 0, 'alloc_med_camp': 0, 'alloc_med_incite': 0, 'crony_amt': 0, 'c_net': float(d.get('bid_cost') or 1.0)})

    claimed_decay = float(d.get('claimed_decay') or 0.0)
    r_pays = float(d.get('r_pays') or 0.0)
    proj_fund = float(d.get('proj_fund') or 0.0)
    
    orig_crony_income = float(act_ha.get('crony_amt', 0.0)) * cfg.get('CRONY_PROFIT_RATE', 0.2)
    
    h_base_expected = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == game.h_role_party.name else 0))
    expected_h_wealth = view_party.wealth - act_ha.get('invest_wealth', 0) + req_cost if is_h else float(game.h_role_party.wealth) - float(act_ha.get('invest_wealth', 0)) + req_cost
    
    eval_c_net = float(act_ha.get('c_net', 0))
    
    res_prev = formulas.calc_economy(cfg, float(game.gdp), float(game.total_budget), proj_fund, bid_cost, float(game.h_role_party.build_ability), float(view_party.current_forecast), r_pays=r_pays, h_wealth=expected_h_wealth, c_net_override=eval_c_net)
    
    hp_net_est = h_base_expected + res_prev['h_project_profit'] + orig_crony_income
    rp_net_est = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == game.r_role_party.name else 0)) + res_prev['payout_r'] - r_pays

    eval_req_cost = res_prev['req_cost']
    eval_h_pays = eval_req_cost - r_pays
    
    o_h_roi = (res_prev['h_project_profit'] / eval_h_pays) * 100.0 if eval_h_pays > 0 else float('inf')
    o_r_roi = ((res_prev['payout_r'] - r_pays) / r_pays) * 100.0 if r_pays > 0 else float('inf')

    h_media_pwr = float(act_ha.get('alloc_med_control', 0.0))
    r_media_pwr = float(act_ra.get('alloc_med_control', 0.0))

    shift_preview = formulas.calc_performance_preview(
        cfg, game.h_role_party, game.r_role_party, game.ruling_party.name,
        res_prev['est_gdp'], game.gdp, 
        claimed_decay, game.sanity, game.emotion, bid_cost, res_prev['c_net'],
        h_media_pwr, r_media_pwr
    )
    
    preview_data = {
        'gdp': res_prev['est_gdp'], 'budg': game.total_budget, 'h_fund': res_prev['payout_h'],
        'san': game.sanity, 'emo': game.emotion,
        'h_inc': hp_net_est, 'r_inc': rp_net_est,
        'my_roi': o_h_roi if is_h else o_r_roi,
        'opp_roi': o_r_roi if is_h else o_h_roi,
        'my_perf_gdp': shift_preview[view_party.name]['perf_gdp'],
        'my_perf_proj': shift_preview[view_party.name]['perf_proj'],
        'opp_perf_gdp': shift_preview[opponent_party.name]['perf_gdp'],
        'opp_perf_proj': shift_preview[opponent_party.name]['perf_proj']
    }
    
    ui_core.render_dashboard(game, view_party, cfg, is_preview=True, preview_data=preview_data)
    
    if not is_invalid and st.button(t("Confirm Action & Execute"), use_container_width=True, type="primary"):
        st.session_state[f"{view_party.name}_acts"] = my_acts
        if f"{opponent_party.name}_acts" not in st.session_state:
            game.proposing_party = opponent_party
            st.rerun()
        else:
            game.phase = 3
            game.proposing_party = game.r_role_party
            st.rerun()
