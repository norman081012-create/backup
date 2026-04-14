# ==========================================
# ui_formulas.py
# 負責 公式計算與過程監控 (智庫深度解析)
# ==========================================
import streamlit as st
import formulas
import i18n

t = i18n.t

def render_formula_panel(game, view_party, cfg):
    with st.expander(t("🧮 遊戲公式與計算過程監控 (智庫解析)"), expanded=False):
        # 1. 抓取數據源
        plan = None
        is_selected = False
        
        # 判定當前數據來源
        if game.phase == 1:
            if getattr(game, 'p1_selected_plan', None):
                plan = game.p1_selected_plan
                is_selected = True
            else:
                # 抓取目前正在操作角色的草案（R 或 H）
                active_role = 'R' if game.p1_step in ['draft_r', 'ultimatum_draft_r'] else 'H'
                plan = game.p1_proposals.get(active_role)
        elif game.phase >= 2:
            plan = st.session_state.get('turn_data')
            is_selected = True

        # 定義狀態標籤
        TAG_EST = " (估)"  # 估值 (來自智庫)
        TAG_TMP = " (暫)"  # 暫時 (提案階段草稿)
        TAG_CFM = " (確)"  # 已確認 (已三讀通過或現有資產)
        TAG_CON = " (常)"  # 常數 (系統固定參數)

        # 基礎參數抓取
        gdp_val = game.gdp
        gdp_str = f"{gdp_val:.1f}{TAG_CFM}"
        
        decay_val = view_party.current_forecast
        decay_str = f"{decay_val:.3f}{TAG_EST}"
        
        build_val = game.h_role_party.build_ability
        build_str = f"{build_val:.1f}{TAG_CFM}"
        
        h_wealth_val = game.h_role_party.wealth
        h_wealth_str = f"{h_wealth_val:.1f}{TAG_CFM}"

        # 標案動態數據判定
        plan_tag = TAG_CFM if is_selected else TAG_TMP
        
        def get_val(key, fmt=".1f"):
            if plan and key in plan and plan[key] is not None:
                return plan[key], f"{plan[key]:{fmt}}{plan_tag}"
            return None, "pending (空)"

        proj_fund_v, proj_fund_s = get_val('proj_fund')
        bid_cost_v, bid_cost_s = get_val('bid_cost')
        r_pays_v, r_pays_s = get_val('r_pays')
        
        st.markdown("### 📊 智庫實時變數監測")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"- GDP: `{gdp_str}`")
            st.write(f"- 預估衰退: `{decay_str}`")
            st.write(f"- 工程能力: `{build_str}`")
        with col2:
            st.write(f"- 計畫獎勵: `{proj_fund_s}`")
            st.write(f"- 總效益值: `{bid_cost_s}`")
            st.write(f"- 監管出資: `{r_pays_s}`")

        st.markdown("---")
        st.markdown("### 🧮 核心經濟公式拆解")

        # 1. 經濟萎縮量
        st.markdown("**1. 預期經濟萎縮量 (Expected Economic Loss)**")
        st.latex(r"Loss = GDP \times (Decay \times 0.05 + 0)")
        loss_v = gdp_val * (decay_val * 0.05)
        st.write(f"> **計算**: `{gdp_str}` × (`{decay_str}` × `0.05{TAG_CON}` + `0{TAG_CON}`) = **{loss_v:.2f}**")

        # 2. 單位建設成本
        st.markdown("**2. 單位工程成本 (Unit Construction Cost)**")
        st.latex(r"Cost = \frac{0.5}{Build / 10} \times 2^{(2 \times Decay - 1)} \times (1 + Inflation)")
        
        b_norm = max(0.01, build_val / 10.0)
        inflation = max(0.0, (gdp_val - 5000.0) / 10000.0)
        unit_cost_v = (0.5 / b_norm) * (2 ** (2 * decay_val - 1)) * (1 + inflation)
        st.write(f"> **計算**: (0.5 / `{build_val/10:.2f}{TAG_CFM}`) × 2^(2 × `{decay_val:.3f}{TAG_EST}` - 1) × (1 + `{inflation:.2f}通膨{TAG_CON}`) = **{unit_cost_v:.2f}**")

        # 3. 資金檢驗與 GDP 結算
        st.markdown("**3. 專案執行力與最終 GDP 預測**")
        st.latex(r"Required = BidCost \times UnitCost")
        st.latex(r"Available = ProjFund + RPays + HWealth")
        
        # 判定是否足以計算
        can_calc = all(v is not None for v in [proj_fund_v, bid_cost_v, r_pays_v])
        
        if can_calc:
            req_v = bid_cost_v * unit_cost_v
            avail_v = proj_fund_v + r_pays_v + h_wealth_val
            st.write(f"> **所需資金**: `{bid_cost_s}` × `{unit_cost_v:.2f}` = **{req_v:.2f}**")
            st.write(f"> **可用資金**: `{proj_fund_s}` + `{r_pays_s}` + `{h_wealth_str}` = **{avail_v:.2f}**")
            
            if avail_v >= req_v:
                st.success(f"✅ 資金足夠 (Available {avail_v:.1f} ≥ Required {req_v:.1f})，計畫 100% 完成。")
                c_net = bid_cost_v
            else:
                st.error(f"❌ 資金缺口 (Available {avail_v:.1f} < Required {req_v:.1f})，計畫將依比例爛尾。")
                c_net = avail_v / unit_cost_v
            
            # GDP 預測
            st.latex(r"GDP_{new} = GDP_{old} - Loss + (C_{net} \times 0.2)")
            new_gdp = gdp_val - loss_v + (c_net * 0.2)
            st.write(f"> **結算**: `{gdp_str}` - `{loss_v:.2f}` + (`{c_net:.2f}{TAG_EST}` × `0.2{TAG_CON}`) = **{new_gdp:.2f}**")
        else:
            st.info("💡 部分關鍵數據（如獎勵金或效益）尚在 `pending (空)` 狀態，無法完成預測計算。")
