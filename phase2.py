# ==========================================
# phase2.py
# 負責 第二階段 (政策執行與行動選擇) 的 UI 與邏輯
# ==========================================
import streamlit as st
import config
import formulas
import ui_core
import i18n
t = i18n.t

def render(game, view_party, opponent_party, cfg):
    is_h = (view_party.name == game.h_role_party.name)
    h_label = t('🛡️ 執行系統', '🛡️ H-System')
    r_label = t('⚖️ 監管系統', '⚖️ R-System')
    st.subheader(f"{t('🛠️ Phase 2: 政策執行與行動 - 輪到', '🛠️ Phase 2: Execution - Turn:')} {view_party.name} ({h_label if is_h else r_label})")
    
    if not hasattr(view_party, 'edu_stance'): view_party.edu_stance = 0.0
    if not hasattr(opponent_party, 'edu_stance'): opponent_party.edu_stance = 0.0
    
    d = st.session_state.get('turn_data', {})
    req_pay = float(d.get('h_pays') or 0.0) if is_h else float(d.get('r_pays') or 0.0)
    cw = max(0.0, float(view_party.wealth))
    proj_fund = float(d.get('proj_fund') or 0.0)
    inflation = max(0.0, (game.gdp - cfg.get('CURRENT_GDP', 5000.0)) / cfg.get('GDP_INFLATION_DIVISOR', 10000.0))
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(t("#### 📣 政策、媒體與暗盤", "#### 📣 Policy & Media"))
        if is_h: st.caption(t("💡 **執行系統特性**: 媒體操控值 1.2 倍加成", "💡 **H-System Perk**: Media Control x1.2"))
        else: st.caption(t("💡 **監管系統特性**: 調查能力值 1.2 倍加成", "💡 **R-System Perk**: Intelligence x1.2"))
        
        h_corr_amt = 0.0; h_crony_amt = 0.0
        judicial_amt = 0.0; new_edu = view_party.edu_stance
        edu_shift_cost = 0.0; edu_maint_cost = 0.0
        
        last_media = min(float(view_party.last_acts.get('media', 0.0)), cw)
        last_camp = min(float(view_party.last_acts.get('camp', 0.0)), cw)
        last_incite = min(float(view_party.last_acts.get('incite', 0.0)), cw)
        last_judicial = min(float(view_party.last_acts.get('judicial', 0.0)), cw)
        
        if is_h:
            st.markdown("##### 🕵️ 檯面下操作 (線性查扣制)")
            my_stl_pct = view_party.stealth_ability / 10.0
            opp_inv_obs = ui_core.get_observed_abilities(view_party, opponent_party, game, cfg)['investigate'] / 10.0
            est_catch_mult = max(0.1, (opp_inv_obs * cfg['R_INV_BONUS']) - my_stl_pct + 1.0)
            
            last_corr = min(float(view_party.last_acts.get('corr_amt', 0.0)), proj_fund)
            h_corr_amt = st.slider(t("💸 秘密貪污 ($)", "💸 Secret Corruption ($)"), 0.0, proj_fund, last_corr, 1.0)
            
            # 🚀 顯示預期查扣比例與淨利 (貪污)
            corr_catch_ratio = min(1.0, cfg.get('CATCH_RATE_PER_DOLLAR', 0.10) * est_catch_mult)
            est_caught_amt = h_corr_amt * corr_catch_ratio
            est_fine = est_caught_amt * cfg.get('CORRUPTION_FINE_MULT', 0.4)
            est_net_corr = h_corr_amt - est_caught_amt - est_fine
            
            risk_color = "red" if corr_catch_ratio > 0.5 else "orange" if corr_catch_ratio > 0.2 else "green"
            st.caption(f"*(⚠️ 預期查扣損失率: <span style='color:{risk_color}'>`{corr_catch_ratio*100:.1f}%`</span> | 預估淨賺: `${est_net_corr:.1f}`)*", unsafe_allow_html=True)
            
            max_crony = max(0.0, proj_fund - h_corr_amt)
            last_crony = min(float(view_party.last_acts.get('crony_amt', 0.0)), max_crony)
            h_crony_amt = st.slider(t("🏢 圖利自身廠商 ($)", "🏢 Cronyism ($)"), 0.0, max_crony, last_crony, 1.0)
            
            # 🚀 顯示預期查扣比例與淨利 (圖利)
            crony_catch_ratio = min(1.0, cfg.get('CRONY_CATCH_RATE_DOLLAR', 0.05) * est_catch_mult)
            est_crony_caught_base = h_crony_amt * crony_catch_ratio
            est_crony_profit = (h_crony_amt - est_crony_caught_base) * cfg.get('CRONY_PROFIT_RATE', 0.2)
            est_crony_fine = est_crony_caught_base * (cfg.get('CRONY_PROFIT_RATE', 0.2) + 0.5) # 吐回利潤 + 0.5罰款 = 0.7倍合約值
            est_net_crony = est_crony_profit - est_crony_fine
            
            risk_color_c = "red" if crony_catch_ratio > 0.5 else "orange" if crony_catch_ratio > 0.2 else "green"
            st.caption(f"*(⚠️ 預期合約查扣率: <span style='color:{risk_color_c}'>`{crony_catch_ratio*100:.1f}%`</span> | 預估淨賺: `${est_net_crony:.1f}`)*", unsafe_allow_html=True)

        else:
            st.markdown("##### 🎓 意識形態與社會控制")
            judicial_amt = st.slider(t("⚖️ 媒體審查 (投入資金)(打壓對手黨媒，依對手支持度反噬自身)", "⚖️ Media Censorship"), 0.0, cw, last_judicial)
            
            new_edu = st.slider(t("🎓 教育方針 (左: 極端填鴨 | 右: 極端思辨)", "🎓 Education Policy"), -100.0, 100.0, float(view_party.edu_stance), 1.0)
            edu_shift_cost = abs(new_edu - view_party.edu_stance) * 1.5
            edu_maint_cost = abs(new_edu) * 0.5
            st.caption(f"🔄 路線轉型花費: `${edu_shift_cost:.1f}` | 🛠️ 常態維護費: `${edu_maint_cost:.1f}`/年")
            
        st.markdown("##### 📺 競選與媒體公關")
        media_ctrl = st.slider(t("📺 媒體操控 (投入資金)(改變施政政績歸因)", "📺 Media Control"), 0.0, cw, last_media)
        camp_amt = st.slider(t("🎉 舉辦造勢競選 (投入資金)(思辨越低越有效)", "🎉 Campaign"), 0.0, cw, last_camp)
        incite_emo = st.slider(t("🔥 煽動情緒 (投入資金)(短暫降低全國思辨力與生產力)", "🔥 Incite Emotion"), 0.0, cw, last_incite)
        
    with c2:
        c_dept1, c_dept2 = st.columns([0.65, 0.35])
        c_dept1.markdown(t("#### 🔒 內部機關擴編", "#### 🔒 Dept. Investment"))
        
        if c_dept2.button(t("🔄 放棄升級", "Reset to Current Maintenance"), use_container_width=True):
            st.session_state[f'up_pre_{view_party.name}_{game.year}'] = view_party.predict_ability * 10.0
            st.session_state[f'up_inv_{view_party.name}_{game.year}'] = view_party.investigate_ability * 10.0
            st.session_state[f'up_med_{view_party.name}_{game.year}'] = view_party.media_ability * 10.0
            st.session_state[f'up_stl_{view_party.name}_{game.year}'] = view_party.stealth_ability * 10.0
            st.session_state[f'up_bld_{view_party.name}_{game.year}'] = view_party.build_ability * 10.0
            st.rerun()

        t_pre, c_pre = ui_core.ability_slider(t("智庫 (精準預估，降低施政誤差)", "Think Tank"), f"up_pre_{view_party.name}_{game.year}", view_party.predict_ability, cw, cfg, view_party.build_ability, is_build=False)
        t_inv, c_inv = ui_core.ability_slider(t("情報處 (抓包對手，提升觀測準度)", "Intelligence"), f"up_inv_{view_party.name}_{game.year}", view_party.investigate_ability, cw, cfg, view_party.build_ability, is_build=False)
        t_med, c_med = ui_core.ability_slider(t("黨媒 (放大操控與造勢效果)", "Media Dept"), f"up_med_{view_party.name}_{game.year}", view_party.media_ability, cw, cfg, view_party.build_ability, is_build=False)
        t_stl, c_stl = ui_core.ability_slider(t("反情報處 (掩護貪污，干擾對手觀測)", "Counter-Intel"), f"up_stl_{view_party.name}_{game.year}", view_party.stealth_ability, cw, cfg, view_party.build_ability, is_build=False)
        t_bld, c_bld = ui_core.ability_slider(t("工程處 (降升級成本，提升建設效率)", "Engineering"), f"up_bld_{view_party.name}_{game.year}", view_party.build_ability, cw, cfg, view_party.build_ability, is_build=True)

    tot_action = float(media_ctrl) + float(camp_amt) + float(incite_emo) + float(judicial_amt) + float(edu_shift_cost)
    tot_maint = float(c_inv) + float(c_pre) + float(c_med) + float(c_stl) + float(c_bld) + float(edu_maint_cost)
    tot_spending_now = tot_action + tot_maint
    
    st.write(f"**政策與媒體:** `{tot_action:.1f}` / **部門維護與升級:** `{tot_maint:.1f}` / **剩餘可用現金:** `{cw - tot_spending_now:.1f}`")
    st.info(f"📌 **法定專案承諾款 (`{req_pay:.1f}`) 將由『次年國家撥款收益』中優先抵扣，不佔用當前現金餘額。**")
    
    if tot_spending_now > cw:
        st.error(f"🚨 資金不足！當前行動預算已超支 {tot_spending_now - cw:.1f} 元，請降低投入資金或放棄升級。")
    
    ra_dummy = {'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 'edu_stance': new_edu, 'judicial': judicial_amt}
    ha_dummy = {'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 'corr_amt': h_corr_amt, 'crony_amt': h_crony_amt}
    
    act_ra = ra_dummy if not is_h else {'media': 0, 'camp': 0, 'incite': 0, 'edu_stance': view_party.edu_stance, 'judicial': 0}
    act_ha = ha_dummy if is_h else {'media': 0, 'camp': 0, 'incite': 0, 'corr_amt': 0, 'crony_amt': 0}
    
    if f"{opponent_party.name}_acts" in st.session_state:
        opp_acts = st.session_state[f"{opponent_party.name}_acts"]
        if is_h: act_ra = opp_acts
        else: act_ha = opp_acts

    bid_cost = float(d.get('bid_cost') or 1.0)
    claimed_decay = float(d.get('claimed_decay') or 0.0)
    r_pays = float(d.get('r_pays') or 0.0)

    corr_val = float(h_corr_amt) if is_h else 0.0
    crony_val = float(h_crony_amt) if is_h else 0.0
    orig_corr_amt = corr_val
    orig_crony_income = crony_val * cfg.get('CRONY_PROFIT_RATE', 0.2)
    
    h_base_expected = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == game.h_role_party.name else 0))
    expected_h_wealth = cw - tot_spending_now + h_base_expected if is_h else float(game.h_role_party.wealth)
    
    res_prev = formulas.calc_economy(cfg, float(game.gdp), float(game.total_budget), proj_fund, bid_cost, float(game.h_role_party.build_ability), float(view_party.current_forecast), corr_amt=orig_corr_amt, r_pays=r_pays, h_wealth=expected_h_wealth)
    h_base = h_base_expected
    r_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == game.r_role_party.name else 0))
    
    hp_net_est = h_base + res_prev['h_project_profit'] + orig_corr_amt + orig_crony_income
    rp_net_est = r_base + res_prev['payout_r'] - r_pays

    shift_preview = formulas.calc_performance_preview(
        cfg, game.h_role_party, game.r_role_party, game.ruling_party.name,
        res_prev['est_gdp'], game.gdp, 
        claimed_decay, game.sanity, game.emotion, bid_cost, res_prev['c_net']
    )
    
    preview_data = {
        'gdp': res_prev['est_gdp'], 'budg': game.total_budget, 'h_fund': res_prev['payout_h'],
        'san': game.sanity, 'emo': game.emotion,
        'h_inc': hp_net_est, 'r_inc': rp_net_est,
        'my_perf_gdp': shift_preview[view_party.name]['perf_gdp'],
        'my_perf_proj': shift_preview[view_party.name]['perf_proj'],
        'opp_perf_gdp': shift_preview[opponent_party.name]['perf_gdp'],
        'opp_perf_proj': shift_preview[opponent_party.name]['perf_proj']
    }
    
    ui_core.render_dashboard(game, view_party, cfg, is_preview=True, preview_data=preview_data)
    
    if tot_spending_now <= cw and st.button(t("確認行動/結算", "Confirm Action/Settle"), use_container_width=True, type="primary"):
        my_acts = {
            'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 
            'edu_stance': new_edu, 'judicial': judicial_amt,
            'corr_amt': h_corr_amt, 'crony_amt': h_crony_amt, 
            't_inv': t_inv, 't_pre': t_pre, 't_med': t_med, 't_stl': t_stl, 't_bld': t_bld,
            'legal': req_pay, 'tot_action': tot_action, 'tot_maint': tot_maint
        }
        st.session_state[f"{view_party.name}_acts"] = my_acts
        
        if f"{opponent_party.name}_acts" not in st.session_state:
            game.proposing_party = opponent_party
            st.rerun()
        else:
            game.phase = 3
            game.proposing_party = game.r_role_party
            st.rerun()
