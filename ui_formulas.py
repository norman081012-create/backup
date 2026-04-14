# ==========================================
# ui_formulas.py
# 負責 公式計算與過程監控 (智庫深度解析)
# ==========================================
import streamlit as st
import formulas
import config
import i18n
t = i18n.t

def render_formula_panel(game, view_party, cfg):
    with st.expander(t("🧮 遊戲公式與計算過程監控 (智庫解析)"), expanded=False):
        plan = None
        if game.phase == 1 and getattr(game, 'p1_selected_plan', None):
            plan = game.p1_selected_plan
        elif game.phase >= 2:
            plan = st.session_state.get('turn_data')
            
        if not plan or 'proj_fund' not in plan:
            st.info("目前階段尚無具體標案數據可供計算。")
            return

        # 抓取基礎參數
        gdp = game.gdp
        budg = game.total_budget
        h_party = game.h_role_party
        
        # 抓取情境參數
        tt_decay = view_party.current_forecast
        cl_decay = plan.get('claimed_decay', tt_decay)
        bid_cost = plan.get('bid_cost', 0.0)
        proj_fund = plan.get('proj_fund', 0.0)
        r_pays = plan.get('r_pays', 0.0)
        h_wealth = h_party.wealth
        
        st.markdown("### 📊 當前環境基礎參數 (Variables)")
        st.markdown(f"- **GDP (國內生產毛額)**: `{gdp:.1f}`")
        st.markdown(f"- **Total Budget (總預算)**: `{budg:.1f}`")
        st.markdown(f"- **Think Tank Decay (情報處預估衰退)**: `{tt_decay:.3f}`")
        st.markdown(f"- **Claimed Decay (公告衰退)**: `{cl_decay:.3f}`")
        st.markdown(f"- **Build Ability (執行方工程能力)**: `{h_party.build_ability:.1f}`")
        
        st.markdown("---")
        st.markdown("### 🧮 核心公式逐步拆解 (Core Formulas Step-by-Step)")
        
        # 1. 基礎衰退量
        loss = gdp * (tt_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
        st.markdown("**1. 預期經濟萎縮量 (Expected Economic Loss)**")
        st.latex(r"Loss = GDP \times (Decay \times Weight + Base)")
        st.markdown(f"> **計算**: `{gdp:.1f}` $\\times$ (`{tt_decay:.3f}` $\\times$ `{cfg['DECAY_WEIGHT_MULT']}` + `{cfg['BASE_DECAY_RATE']}`) = **`{loss:.2f}`**")

        # 2. 單位建設成本
        b_norm = max(0.01, h_party.build_ability / 10.0)
        inflation = max(0.0, (gdp - cfg.get('CURRENT_GDP', 5000.0)) / cfg.get('GDP_INFLATION_DIVISOR', 10000.0))
        unit_cost = (0.5 / b_norm) * (2 ** (2 * tt_decay - 1)) * (1 + inflation)
        
        st.markdown("**2. 單位工程成本 (Unit Construction Cost)**")
        st.latex(r"Cost = \left( \frac{0.5}{Build / 10} \right) \times 2^{(2 \times Decay - 1)} \times (1 + Inflation)")
        st.markdown(f"> **計算**: $(0.5 / {b_norm:.2f}) \\times 2^{(2 \\times {tt_decay:.3f} - 1)} \\times (1 + {inflation:.3f})$ = **`{unit_cost:.2f}`**")

        # 3. 專案資金檢驗
        req_cost = bid_cost * unit_cost
        available = proj_fund + r_pays + h_wealth
        
        st.markdown("**3. 專案資金水位檢驗 (Funding Check)**")
        st.latex(r"Required = BidCost \times UnitCost")
        st.markdown(f"> **計算 Required**: `{bid_cost:.1f}` $\\times$ `{unit_cost:.2f}` = **`{req_cost:.2f}`**")
        st.latex(r"Available = ProjFund + RPays + HWealth")
        st.markdown(f"> **計算 Available**: `{proj_fund:.1f}` + `{r_pays:.1f}` + `{h_wealth:.1f}` = **`{available:.2f}`**")
        
        if req_cost <= available:
            st.success(f"✅ 資金充足 (Available `{available:.1f}` $\\ge$ Required `{req_cost:.1f}`)，計畫可 100% 執行。")
            c_net = bid_cost
        else:
            st.error(f"❌ 資金斷裂 (Available `{available:.1f}` < Required `{req_cost:.1f}`)，工程將依比例爛尾！")
            c_net = available / unit_cost
            
        # 4. GDP 結算
        conv = cfg.get('GDP_CONVERSION_RATE', 0.2)
        new_gdp = gdp - loss + (c_net * conv)
        st.markdown("**4. 最終 GDP 預測 (Final GDP Forecast)**")
        st.latex(r"GDP_{new} = GDP_{old} - Loss + (C_{net} \times ConvRate)")
        st.markdown(f"> **計算**: `{gdp:.1f}` - `{loss:.2f}` + (`{c_net:.2f}` $\\times$ `{conv}`) = **`{new_gdp:.2f}`**")
