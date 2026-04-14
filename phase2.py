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
    h_label = t('🛡️ 執行系統')
    r_label = t('⚖️ 監管系統')
    st.subheader(f"{t('🛠️ Phase 2: 政策執行與行動 - 輪到')} {view_party.name} ({h_label if is_h else r_label})")
    
    d = st.session_state.get('turn_data', {})
    req_pay = float(d.get('h_pays') or 0.0) if is_h else float(d.get('r_pays') or 0.0)
    cw = max(0.0, float(view_party.wealth))
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(t("#### 📣 政策與媒體"))
        if is_h: st.caption(t("💡 **執行系統特性**: 媒體操控值 1.2 倍加成"))
        else: st.caption(t("💡 **監管系統特性**: 調查能力值 1.2 倍加成"))
        
        h_corr_pct = 0; h_crony_pct = 0
        judicial_amt = 0.0; edu_policy_amt = 0.0
        
        if is_h:
            h_corr_pct = st.slider(t("💸 秘密貪污 (%)"), 0, 100, 0)
            max_crony = max(0, 100 - h_corr_pct)
            h_crony_pct = st.slider(t("🏢 圖利自身廠商 (%)"), 0, max_crony, 0)
        else:
            judicial_amt = st.slider(t("⚖️ 司法審查 (投入資金)(降低全體黨媒效果，引起高思辯選民反感)"), 0.0, cw, 0.0)
            edu_policy_amt = st.slider(t("🎓 教育方針 (投入資金)(左:填鴨(提升低媒體影響) 右:思辨(降低媒體影響))"), -cw, cw, 0.0)
            
        media_ctrl = st.slider(t("📺 媒體操控 (投入資金)(改變施政產生的影響力 像是 甩鍋搶功勞邀功)"), 0.0, cw, 0.0)
        camp_amt = st.slider(t("🎉 舉辦競選 (投入資金)(思辨越低填鴨越高越有效)"), 0.0, cw, 0.0)
        incite_emo = st.slider(t("🔥 煽動情緒 (投入資金)(高情緒高於思辨降低思辨力 / 高情緒高填鴨降低生產力，時效短)"), 0.0, cw, 0.0)
        
    with c2:
        st.markdown(t("#### 🔒 內部部門投資"))
        
        if st.button(t("🔄 全部回歸當前維護費 (放棄升級)"), use_container_width=True):
            st.session_state['up_pre'] = view_party.predict_ability * 10.0
            st.session_state['up_inv'] = view_party.investigate_ability * 10.0
            st.session_state['up_med'] = view_party.media_ability * 10.0
            st.session_state['up_stl'] = view_party.stealth_ability * 10.0
            st.session_state['up_bld'] = view_party.build_ability * 10.0
            st.rerun()

        t_pre, c_pre = ui_core.ability_slider(t("智庫 (精準預測衰退，降低施政誤差)"), "up_pre", view_party.predict_ability, cw, cfg, view_party.build_ability)
        t_inv, c_inv = ui_core.ability_slider(t("情報處 (抓包對手貪污圖利，提升觀測準確度)"), "up_inv", view_party.investigate_ability, cw, cfg, view_party.build_ability)
        t_med, c_med = ui_core.ability_slider(t("黨媒 (放大媒體操控、煽動與競選效果)"), "up_med", view_party.media_ability, cw, cfg, view_party.build_ability)
        t_stl, c_stl = ui_core.ability_slider(t("反情報處 (掩護自身貪污圖利，干擾對手觀測)"), "up_stl", view_party.stealth_ability, cw, cfg, view_party.build_ability)
        t_bld, c_bld = ui_core.ability_slider(t("工程處 (提升建設產出，降低各部門升級成本)"), "up_bld", view_party.build_ability, cw, cfg, view_party.build_ability)

    tot_action = float(media_ctrl) + float(camp_amt) + float(incite_emo) + abs(float(edu_policy_amt)) + float(judicial_amt)
    tot_maint = float(c_inv) + float(c_pre) + float(c_med) + float(c_stl) + float(c_bld)
    tot = req_pay + tot_action + tot_maint
    
    st.write(f"**法定專案款:** `{req_pay:.1f}` / **政策與媒體:** `{tot_action:.1f}` / **內部部門投資:** `{tot_maint:.1f}` / **剩餘可用淨值:** `{cw - tot:.1f}`")
    
    if tot > cw:
        st.error(f"{t('🚨 資金不足！當前行動預算已超支')} {tot - cw:.1f} 元，請降低投入資金。")
    
    ra_dummy = {'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 'edu_amt': edu_policy_amt, 'judicial': judicial_amt}
    ha_dummy = {'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 'corr': h_corr_pct, 'crony': h_crony_pct}
    
    act_ra = ra_dummy if not is_h else {'media': 0, 'camp': 0, 'incite': 0, 'edu_amt': 0, 'judicial': 0}
    act_ha = ha_dummy if is_h else {'media': 0, 'camp': 0, 'incite': 0, 'corr': 0, 'crony': 0}
    
    if f"{opponent_party.name}_acts" in st.session_state:
        opp_acts = st.session_state[f"{opponent_party.name}_acts"]
        if is_h: act_ra = opp_acts
        else: act_ha = opp_acts

    proj_fund = float(d.get('proj_fund') or 0.0)
    bid_cost = float(d.get('bid_cost') or 1.0)
    claimed_decay = float(d.get('claimed_decay') or 0.0)
    r_pays = float(d.get('r_pays') or 0.0)

    corr_val = float(act_ha.get('corr') or 0.0)
    orig_corr_amt = proj_fund * (corr_val / 100.0)
    
    res_prev = formulas.calc_economy(cfg, float(game.gdp), float(game.total_budget), proj_fund, bid_cost, float(game.h_role_party.build_ability), float(view_party.current_forecast), orig_corr_amt)
    
    h_base = float(cfg['DEFAULT_BONUS']) + (float(cfg['RULING_BONUS']) if game.ruling_party.name == game.h_role_party.name else 0.0)
    r_base = float(cfg['DEFAULT_BONUS']) + (float(cfg['RULING_BONUS']) if game.ruling_party.name == game.r_role_party.name else 0.0)
    
    hp_net_est = h_base + res_prev['payout_h'] - res_prev['act_fund'] + r_pays
    rp_net_est = r_base + res_prev['payout_r'] - r_pays

    shift_preview = formulas.calc_support_shift(
        cfg, game.h_role_party, game.r_role_party, game.ruling_party.name,
        res_prev['payout_h'], res_prev['est_gdp'], proj_fund, game.gdp, 
        act_ha, act_ra, res_prev['h_idx'], claimed_decay, float(view_party.current_forecast), game.sanity, game.emotion
    )
    
    preview_data = {
        'gdp': res_prev['est_gdp'], 'budg': game.total_budget, 'h_fund': res_prev['payout_h'],
        'san': game.sanity, 'emo': game.emotion,
        'h_inc': hp_net_est, 'r_inc': rp_net_est,
        'my_sup_shift': shift_preview['actual_shift'] if is_h else -shift_preview['actual_shift'],
        'opp_sup_shift': -shift_preview['actual_shift'] if is_h else shift_preview['actual_shift']
    }
    
    ui_core.render_dashboard(game, view_party, cfg, is_preview=True, preview_data=preview_data)
    
    if tot <= cw and st.button(t("確認行動/結算"), use_container_width=True, type="primary"):
        my_acts = {
            'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 
            'edu_amt': edu_policy_amt, 'judicial': judicial_amt,
            'corr': h_corr_pct, 'crony': h_crony_pct, 
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
