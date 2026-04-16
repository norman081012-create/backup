# ==========================================
# ui_formulas.py
# ==========================================
import streamlit as st
import formulas
import ui_core
import i18n
t = i18n.t

def render_formula_panel(game, view_party, cfg):
    with st.expander("🧮 智庫公式與計算監控", expanded=False):
        plan = None
        is_selected = False
        
        if game.phase == 1:
            if getattr(game, 'p1_selected_plan', None):
                plan = game.p1_selected_plan
                is_selected = True
            else:
                active_role = 'R' if game.p1_step in ['draft_r', 'ultimatum_draft_r'] else 'H'
                plan = game.p1_proposals.get(active_role)
        elif game.phase >= 2:
            plan = st.session_state.get('turn_data')
            is_selected = True

        TAG_EST = " (預估)"  
        TAG_TMP = " (暫定)"  
        TAG_CFM = " (確認)"  
        TAG_CON = " (常數)"  

        gdp_val = game.gdp
        gdp_str = f"{gdp_val:.1f}{TAG_CFM}"
        
        decay_val = view_party.current_forecast
        decay_str = f"{decay_val:.3f}{TAG_EST}"
        
        is_simulating = st.session_state.get("sim_sw_📜 當前草案預覽_R") or st.session_state.get("sim_sw_📜 對手草案參考_H")
        if is_simulating:
            active_h = game.r_role_party
        else:
            active_h = game.h_role_party
            
        obs_abis = ui_core.get_observed_abilities(view_party, active_h, game, cfg)
        build_val = obs_abis['build']
        is_my_h = (view_party.name == active_h.name)
        build_tag = TAG_CFM if (is_my_h or st.session_state.get('god_mode')) else TAG_EST
        build_str = f"{build_val:.1f}{build_tag}"
        
        h_wealth_val = active_h.wealth
        h_wealth_str = f"{h_wealth_val:.1f}{TAG_CFM}"

        plan_tag = TAG_CFM if is_selected else TAG_TMP
        
        def get_val(key, fmt=".1f"):
            if plan and key in plan and plan[key] is not None:
                return plan[key], f"{plan[key]:{fmt}}{plan_tag}"
            return None, "等待中"

        proj_fund_v, proj_fund_s = get_val('proj_fund')
        bid_cost_v, bid_cost_s = get_val('bid_cost')
        r_pays_v, r_pays_s = get_val('r_pays')
        
        st.markdown("### 📊 智庫即時變數")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"- 當前 GDP: `{gdp_str}`")
            st.write(f"- 預估衰退率: `{decay_str}`")
            st.write(f"- 執行系統工程能力: `{build_str}`" + (" *(模擬中)*" if is_simulating else "")) 
        with col2:
            st.write(f"- 專案總獎金: `{proj_fund_s}`")
            st.write(f"- 專案總效益: `{bid_cost_s}`")
            st.write(f"- 監管方墊付: `{r_pays_s}`")

        st.markdown("---")
        st.markdown("### 🧮 支持度引擎 2.0")
        st.markdown("**1. 大環境支持度** - *結合絕對成長與預期落差*")
        st.latex(r"P_{plan} = (\Delta A \times 0.05) + (\Delta A - \Delta E) \times 0.15")
        st.markdown("**2. 專案執行支持度** - *與規模及完成度掛鉤*")
        st.latex(r"TargetGrowth = \frac{BidCost \times 0.2}{GDP} \times 100\%")
        st.latex(r"P_{exec} = TargetGrowth \times \left(\frac{C_{actual}}{C_{target}} - 0.5\right) \times 2.0 \times 0.1")
        st.markdown("**3. 支持度板塊位移勝率**")
        st.latex(r"WinProb = 1.0 - Rigidity(target\_index)")

        st.markdown("---")
        st.markdown("### 🧮 核心經濟拆解")

        st.markdown("**1. 預期經濟損失**")
        st.latex(r"Loss = GDP \times (Decay \times 0.05 + 0)")
        loss_v = gdp_val * (decay_val * 0.05)
        st.write(f"> **計算**: `{gdp_str}` × (`{decay_str}` × `0.05{TAG_CON}` + `0{TAG_CON}`) = **{loss_v:.2f}**")

        st.markdown("**2. 單位建設成本 (含通膨)**")
        st.latex(r"Cost = \frac{0.85}{Build / 10} \times 2^{(2 \times Decay - 1)} \times (1 + Inflation)")
        
        b_norm = max(0.01, build_val / 10.0)
        inflation = max(0.0, (gdp_val - 5000.0) / 10000.0)
        unit_cost_v = (0.85 / b_norm) * (2 ** (2 * decay_val - 1)) * (1 + inflation)
        st.write(f"> **計算**: (0.85 / `{build_val/10:.2f}{TAG_CFM}`) × 2^(2 × `{decay_val:.3f}{TAG_EST}` - 1) × (1 + `{inflation:.2f} Inf{TAG_CON}`) = **{unit_cost_v:.2f}**")

        st.markdown("---")
        st.markdown(f"### ⚖️ 假 EV 查核模型 (金流查核)")
        
        st.markdown("**🔍 區塊分批擲骰**")
        st.latex(r"Net\_Fin\_EV = R\_Investigate\_Fin - H\_Hide\_Fin")
        st.latex(r"ChunkSize = \frac{10}{Net\_Fin\_EV}")
        st.latex(r"CatchProb = BaseRate \times \max(1.0, Net\_Fin\_EV \times 0.1)")
        st.write(f"> **1 單位假 EV 成本**: `{cfg.get('FAKE_EV_COST_RATIO', 0.2)}x 單位成本`")
        
        st.markdown("**💸 預期罰款**")
        st.latex(r"CaughtValue = Caught\_Fake\_EV \times RealUnitCost")
        st.latex(r"Fine = CaughtValue \times FineMult")

