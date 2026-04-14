# ==========================================
# phase2.py
# 負責 第二階段 (政策執行與結算) 的 UI 與邏輯
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
    
    d = st.session_state.turn_data
    req_pay = d.get('h_pays', 0) if is_h else d.get('r_pays', 0)
    cw = max(0.0, float(view_party.wealth))
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(t("#### 📣 政策與媒體"))
        if is_h: st.caption(t("💡 **執行系統特性**: 媒體操控值 1.2 倍加成"))
        else: st.caption(t("💡 **監管系統特性**: 調查能力值 1.2 倍加成"))
        
        h_corr_pct = st.slider(t("💸 秘密貪污 (%)"), 0, 100, 0) if is_h else 0
        h_crony_pct = st.slider(t("🏢 圖利自身廠商 (%)"), 0, max(0, 100 - h_corr_pct), 0) if is_h else 0
        
        judicial_amt = st.slider(t("⚖️ 司法審查 (降低全體黨媒效果，但會引起高思辯選民反感)"), 0.0, cw, 0.0) if not is_h else 0.0
        media_ctrl = st.slider(t("📺 媒體操控 (提升競選與煽動效果)"), 0.0, cw, 0.0)
        
        edu_policy_amt = st.slider(t("🎓 教育方針 (左:填鴨 右:思辨, 投入資金)"), -cw, cw, 0.0) if not is_h else 0.0
        camp_amt = st.slider(t("🎉 舉辦競選 (投入資金)"), 0.0, cw, 0.0)
        incite_emo = st.slider(t("🔥 煽動情緒 (投入資金)"), 0.0, cw, 0.0)
        
    with c2:
        st.markdown(t("#### 🔒 內部部門投資"))
        
        if st.button(t("🔄 全部回歸當前維護費 (放棄升級)"), use_container_width=True):
            st.session_state['up_pre'] = view_party.predict_ability * 10.0
            st.session_state['up_inv'] = view_party.investigate_ability * 10.0
            st.session_state['up_med'] = view_party.media_ability * 10.0
            st.session_state['up_stl'] = view_party.stealth_ability * 10.0
            st.session_state['up_bld'] = view_party.build_ability * 10.0
            st.rerun()

        # 監管系統現在也可以看到與升級工程處了
        t_pre, c_pre = ui_core.ability_slider(t("智庫"), "up_pre", view_party.predict_ability, cw, cfg, view_party.build_ability)
        t_inv, c_inv = ui_core.ability_slider(t("情報處"), "up_inv", view_party.investigate_ability, cw, cfg, view_party.build_ability)
        t_med, c_med = ui_core.ability_slider(t("黨媒"), "up_med", view_party.media_ability, cw, cfg, view_party.build_ability)
        t_stl, c_stl = ui_core.ability_slider(t("反情報處"), "up_stl", view_party.stealth_ability, cw, cfg, view_party.build_ability)
        t_bld, c_bld = ui_core.ability_slider(t("工程處"), "up_bld", view_party.build_ability, cw, cfg, view_party.build_ability)

    tot_action = media_ctrl + camp_amt + incite_emo + abs(edu_policy_amt) + judicial_amt
    tot_maint = c_inv + c_pre + c_med + c_stl + c_bld
    tot = req_pay + tot_action + tot_maint
    
    st.write(f"**法定專案款:** `{req_pay:.1f}` / **政策與媒體:** `{tot_action:.1f}` / **內部部門投資:** `{tot_maint:.1f}` / **剩餘可用淨值:** `{cw - tot:.1f}`")
    
    if tot > cw:
        st.error(f"{t('🚨 資金不足！當前行動預算已超支')} {tot - cw:.1f} 元，請降低投入資金。")
    
    ra, ha = {}, {}
    if f"{opponent_party.name}_acts" in st.session_state:
        opp_acts = st.session_state[f"{opponent_party.name}_acts"]
        ra = opp_acts if is_h else {'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 'edu_amt': edu_policy_amt, 'corr': h_corr_pct, 'crony': h_crony_pct, 'judicial': judicial_amt}
        ha = {'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 'edu_amt': edu_policy_amt, 'corr': h_corr_pct, 'crony': h_crony_pct, 'judicial': judicial_amt} if is_h else opp_acts
    else:
        ra = {'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 'edu_amt': edu_policy_amt, 'corr
