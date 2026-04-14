# ==========================================
# ui_formulas.py
# 負責 科學數據與公式逐步拆解 (智庫解析)
# ==========================================
import streamlit as st
import formulas
import i18n
t = i18n.t

def render_formula_panel(game, view_party, cfg):
    with st.expander(t("🧮 國家發展公式精確拆解"), expanded=False):
        plan = None
        is_cfm = False
        if game.phase == 1:
            plan = game.p1_selected_plan if getattr(game, 'p1_selected_plan', None) else game.p1_proposals.get('R' if 'draft_r' in game.p1_step else 'H')
        else:
            plan = st.session_state.get('turn_data'); is_cfm = True
            
        if not plan:
            st.info("💡 標案數據 `pending (空)`，公式暫停演算。")
            return

        tag_est, tag_tmp, tag_cfm, tag_con = " (估)", " (暫)", " (確)", " (常)"
        p_tag = tag_cfm if is_cfm else tag_tmp

        st.markdown("### 📊 實時變數監測")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"- GDP: `{game.gdp:.1f}{tag_cfm}`")
            st.write(f"- 智庫衰退預測: `{view_party.current_forecast:.3f}{tag_est}`")
        with c2:
            st.write(f"- 獎勵金: `{plan.get('proj_fund', 0):.1f}{p_tag}`")
            st.write(f"- 承諾效益: `{plan.get('bid_cost', 0):.1f}{p_tag}`")

        st.markdown("---")
        # 衰退計算
        loss = game.gdp * (view_party.current_forecast * 0.05)
        st.markdown("**1. 預期萎縮量 (Economic Loss)**")
        st.latex(r"Loss = GDP \times (Decay \times 0.05)")
        st.write(f"> `{game.gdp:.1f}{tag_cfm}` × `{view_party.current_forecast:.3f}{tag_est}` × `0.05{tag_con}` = **{loss:.2f}**")

        # 成本計算
        b_norm = max(0.01, game.h_role_party.build_ability / 10.0)
        u_cost = (0.5 / b_norm) * (2 ** (2 * view_party.current_forecast - 1))
        st.markdown("**2. 單位建設成本 (Construction Cost)**")
        st.latex(r"Cost = \frac{0.5}{Build/10} \times 2^{(2 \times Decay - 1)}")
        st.write(f"> (0.5 / `{b_norm:.2f}{tag_cfm}`) × 2^... = **{u_cost:.2f}**")

        # 資金缺口
        req = plan['bid_cost'] * u_cost
        avail = plan['proj_fund'] + plan['r_pays'] + game.h_role_party.wealth
        st.markdown("**3. 資金水位檢驗 (Funding Check)**")
        if avail >= req:
            st.success(f"✅ 資金充沛: `{avail:.1f}{tag_cfm}` ≥ `{req:.1f}{tag_tmp}`")
        else:
            st.error(f"❌ 資金缺口: `{avail:.1f}{tag_cfm}` < `{req:.1f}{tag_tmp}`")
