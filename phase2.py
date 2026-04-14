# ==========================================
# phase2.py
# 負責 第二階段 (政策執行與行動選擇) 的 UI 與邏輯
# ==========================================
import streamlit as st
import formulas
import ui_core

def render(game, view_party, opponent_party, cfg):
    is_h = (view_party.name == game.h_role_party.name)
    st.subheader(f"🛠️ Phase 2: 政策執行與行動 - 輪到 {view_party.name} ({'🛡️ 執行系統' if is_h else '⚖️ 監管系統'})")
    
    d = st.session_state.get('turn_data', {})
    req_pay = d.get('h_pays', 0) if is_h else d.get('r_pays', 0)
    cw = max(0.0, float(view_party.wealth))
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📣 政策與媒體")
        if is_h: st.caption("💡 **執行系統特性**: 媒體操控值 1.2 倍加成")
        else: st.caption("💡 **監管系統特性**: 調查能力值 1.2 倍加成")
        
        h_corr_pct = 0; h_crony_pct = 0
        judicial_amt = 0.0; edu_policy_amt = 0.0
        
        if is_h:
            h_corr_pct = st.slider("💸 秘密貪污 (%)", 0, 100, 0)
            h_crony_pct = st.slider("🏢 圖利自身廠商 (%)", 0, max(0, 100 - h_corr_pct), 0)
        else:
            judicial_amt = st.slider("⚖️ 司法審查 (投入資金)(降低全體黨媒效果，引起高思辨選民反感)", 0.0, cw, 0.0)
            edu_policy_amt = st.slider("🎓 教育方針 (投入資金)(左:填鴨[提升競選洗腦] 右:思辨[降低媒體洗腦])", -cw, cw, 0.0)
            
        media_ctrl = st.slider("📺 媒體操控 (投入資金)(改變施政產生的影響力，如甩鍋或搶功勞)", 0.0, cw, 0.0)
        camp_amt = st.slider("🎉 舉辦競選 (投入資金)(無腦砸錢洗腦，社會思辨越低/填鴨越高越有效)", 0.0, cw, 0.0)
        incite_emo = st.slider("🔥 煽動情緒 (投入資金)(高情緒會短暫降低生產力與社會思辨力，時效短)", 0.0, cw, 0.0)
        
    with c2:
        st.markdown("#### 🔒 內部部門投資")
        if st.button("🔄 全部回歸當前維護費 (放棄升級)", use_container_width=True):
            st.session_state['up_pre'] = view_party.predict_ability * 10.0
            st.session_state['up_inv'] = view_party.investigate_ability * 10.0
            st.session_state['up_med'] = view_party.media_ability * 10.0
            st.session_state['up_stl'] = view_party.stealth_ability * 10.0
            st.session_state['up_bld'] = view_party.build_ability * 10.0
            st.rerun()

        t_pre, c_pre = ui_core.ability_slider("智庫 (精準預測衰退，降低施政誤差)", "up_pre", view_party.predict_ability, cw, cfg, view_party.build_ability)
        t_inv, c_inv = ui_core.ability_slider("情報處 (抓包對手貪污圖利，提升觀測準確度)", "up_inv", view_party.investigate_ability, cw, cfg, view_party.build_ability)
        t_med, c_med = ui_core.ability_slider("黨媒 (放大媒體操控、煽動與競選效果)", "up_med", view_party.media_ability, cw, cfg, view_party.build_ability)
        t_stl, c_stl = ui_core.ability_slider("反情報處 (掩護自身貪污圖利，干擾對手觀測)", "up_stl", view_party.stealth_ability, cw, cfg, view_party.build_ability)
        t_bld, c_bld = ui_core.ability_slider("工程處 (提升建設產出，降低各部門升級成本)", "up_bld", view_party.build_ability, cw, cfg, view_party.build_ability)

    tot_action = media_ctrl + camp_amt + incite_emo + abs(edu_policy_amt) + judicial_amt
    tot_maint = c_inv + c_pre + c_med + c_stl + c_bld
    tot = req_pay + tot_action + tot_maint
    
    st.write(f"**法定專案款:** `{req_pay:.1f}` / **政策與媒體:** `{tot_action:.1f}` / **內部部門投資:** `{tot_maint:.1f}` / **剩餘可用淨值:** `{cw - tot:.1f}`")
    if tot > cw: st.error(f"🚨 資金不足！當前行動預算已超支 {tot - cw:.1f} 元，請降低投入資金。")
    
    if tot <= cw and st.button("確認行動/結束回合", use_container_width=True, type="primary"):
        st.session_state[f"{view_party.name}_acts"] = {
            'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 
            'edu_amt': edu_policy_amt, 'judicial': judicial_amt,
            'corr': h_corr_pct, 'crony': h_crony_pct, 
            't_inv': t_inv, 't_pre': t_pre, 't_med': t_med, 't_stl': t_stl, 't_bld': t_bld,
            'legal': req_pay, 'tot_action': tot_action, 'tot_maint': tot_maint
        }
        
        if f"{opponent_party.name}_acts" not in st.session_state:
            game.proposing_party = opponent_party
            st.rerun()
        else:
            game.phase = 3
            game.proposing_party = game.r_role_party
            st.rerun()
