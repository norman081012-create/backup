# ==========================================
# ui_core.py
# 負責共用 UI 底層渲染與核心數學拉桿組件
# ==========================================
import streamlit as st
import math
import config
import formulas
import i18n
t = i18n.t

def sync_party_names(game, cfg):
    game.party_A.name = cfg['PARTY_A_NAME']; game.party_B.name = cfg['PARTY_B_NAME']

def render_global_settings(cfg, game):
    st.sidebar.title(t("🎛️ 控制台"))
    lang = st.session_state.get('lang', 'EN')
    btn_text = "🌐 切換至中文" if lang == 'EN' else "🌐 Switch to English"
    if st.sidebar.button(btn_text, use_container_width=True):
        st.session_state.lang = 'ZH' if lang == 'EN' else 'EN'
        st.rerun()

    with st.sidebar.expander(t("📝 參數調整(即時)"), expanded=False):
        trans = config.get_config_translations()
        for key, default_val in config.DEFAULT_CONFIG.items():
            label = trans.get(key, key)
            if 'COLOR' in key: cfg[key] = st.color_picker(label, value=cfg[key], key=f"cfg_{key}")
            elif isinstance(default_val, float): cfg[key] = st.number_input(label, value=float(cfg[key]), step=0.1, format="%.2f", key=f"cfg_{key}")
            elif isinstance(default_val, int): cfg[key] = st.number_input(label, value=int(cfg[key]), step=1, key=f"cfg_{key}")
            elif isinstance(default_val, str): cfg[key] = st.text_input(label, value=str(cfg[key]), key=f"cfg_{key}")
    sync_party_names(game, cfg)

def render_message_board(game):
    if st.session_state.get('news_flash'):
        st.warning(st.session_state.news_flash)
        st.session_state.news_flash = None
        
    if game.phase == 1:
        if game.year == 1: st.info("📢 **【年度通報】** 新的一年開始了，國家百廢待舉，請盡快展開預算與目標協商。")
        elif game.last_year_report: st.info("📢 **【年度通報】** 新的一年開始了，請盡快展開預算與目標協商。")
    elif game.phase == 2:
        st.info("📢 **【年度通報】** 法案已通過，請分配黨產資金進行內部升級、競選造勢與媒體攻防。")

def render_formula_panel(game, view_party, cfg):
    with st.expander(t("🧮 遊戲公式與計算過程監控 (智庫解析)"), expanded=False):
        plan = None
        if game.phase == 1 and getattr(game, 'p1_selected_plan', None):
            plan = game.p1_selected_plan
        elif game.phase >= 2:
            plan = st.session_state.get('turn_data')
            
        if plan and 'proj_fund' in plan:
            lines = formulas.get_formula_explanation(game, view_party, plan, cfg)
            for line in lines: st.markdown(line)
        else:
            st.info("目前階段尚無具體標案數據可供計算。")

# [核心實裝] 物理慣性與殘值保護的升降級拉桿
def ability_slider(label, dept_key, current_lvl, wealth, cfg, build_ability=0.0):
    current_pct = current_lvl * 10.0
    current_amt = (2**current_lvl - 1) * 50.0

    t_pct = st.slider(f"{label}", 0.0, 100.0, float(current_pct), 1.0, key=f"up_{dept_key}")
    t_lvl = t_pct / 10.0
    t_amt = (2**t_lvl - 1) * 50.0
    
    max_drop_amt = cfg['DEPT_MAX_DECAY_AMT'].get(dept_key, 100.0)
    
    if t_amt > current_amt:
        cost = formulas.calculate_upgrade_cost(current_lvl, t_lvl, build_ability)
        maint = formulas.get_ability_maintenance(t_lvl, cfg)
        actual_next_lvl = t_lvl
        st.caption(f"📈 <span style='color:orange'>**升級花費**: ${cost:.1f}</span> | 能力: {current_pct:.1f}% ➔ {t_pct:.1f}% | 維護費將達 ${maint:.1f}", unsafe_allow_html=True)
    elif t_amt < current_amt:
        cost = 0.0
        maint = formulas.get_ability_maintenance(t_lvl, cfg)
        
        actual_next_amt = max(t_amt, current_amt - max_drop_amt)
        actual_next_lvl = math.log2(actual_next_amt / 50.0 + 1) if actual_next_amt > 0 else 0.0
        
        if actual_next_amt > t_amt:
            st.caption(f"📉 <span style='color:blue'>**殘值保護中**</span> | 支付維護費: ${maint:.1f} | 組織僵固性吸收衝擊，明年實際保留至 **{actual_next_lvl*10:.1f}%**", unsafe_allow_html=True)
        else:
            st.caption(f"📉 <span style='color:blue'>**全面降級**</span> | 支付維護費: ${maint:.1f} | 明年降至 {actual_next_lvl*10:.1f}%", unsafe_allow_html=True)
    else:
        cost = 0.0
        actual_next_lvl = current_lvl
        maint = formulas.get_ability_maintenance(t_lvl, cfg)
        st.caption(f"🛡️ 穩定維持 | 能力: {current_pct:.1f}% | 維護費: ${maint:.1f}")
        
    return actual_next_lvl, cost, maint
