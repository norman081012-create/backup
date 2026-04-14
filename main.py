# ==========================================
# main.py
# 主程式入口：負責路由、CSS 注入與全域初始化
# ==========================================
import streamlit as st
import random
import config
import engine
import ui_core
import ui_proposal
import ui_formulas
import phase1
import phase2
import phase3
import phase4
import i18n

# 1. 頁面配置與 CSS 注入
st.set_page_config(page_title="GovOS - 國家發展監控系統 v3.0.0", layout="wide")

st.markdown("""
<style>
    /* 儀表板數字採用等寬字體，增加專業終端機感 */
    div[data-testid="stMetricValue"] {
        font-family: 'Courier New', Courier, monospace;
        color: #1E3A8A;
    }
    /* 讓帶邊框的 Container 看起來像官方卷宗/公文夾 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #F8FAFC;
        border-radius: 6px;
        border: 1px solid #CBD5E1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        padding: 5px;
    }
    /* 強調智庫機密報告的顏色 */
    .think-tank-report {
        background-color: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 15px;
        border-radius: 4px;
        color: #451a03;
    }
    /* 強調財政赤字或警告 */
    .alert-text { color: #DC2626; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.components.v1.html("<script>window.parent.document.querySelector('.main').scrollTo(0,0);</script>", height=0)

if 'lang' not in st.session_state: st.session_state.lang = 'ZH'
t = i18n.t

if 'cfg' not in st.session_state: st.session_state.cfg = config.DEFAULT_CONFIG.copy()
cfg = st.session_state.cfg

if 'game' not in st.session_state:
    st.session_state.game = engine.GameEngine(cfg)
    st.session_state.turn_data = {
        'r_value': 1.0, 'target_h_fund': 600.0, 'target_gdp_growth': 0.0,
        'r_pays': 0, 'total_funds': 0, 'agreed': False, 'target_gdp': 5000.0, 'h_ratio': 1.0
    }

game = st.session_state.game

if st.session_state.get('anim') == 'balloons':
    st.balloons(); st.session_state.anim = None
elif st.session_state.get('anim') == 'snow':
    st.snow(); st.session_state.anim = None

if game.phase == 4:
    phase4.render(game, cfg); st.stop()

if 'turn_initialized' not in st.session_state:
    game.current_real_decay = max(0.1, round(random.uniform(cfg['DECAY_MIN'], cfg['DECAY_MAX']), 3))
    real_infra_loss = game.gdp * (game.current_real_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
    for p in [game.party_A, game.party_B]:
        error_range = (cfg['PREDICT_DIFF'] / max(0.1, p.predict_ability)) * (game.gdp * 0.01)
        observed_loss = max(0.0, real_infra_loss + random.uniform(-error_range, error_range))
        p.current_forecast = max(0.0, round(((observed_loss / max(1.0, game.gdp)) - cfg['BASE_DECAY_RATE']) / cfg['DECAY_WEIGHT_MULT'], 3))
        p.poll_history = {'小型': [], '中型': [], '大型': []}; p.latest_poll = None; p.poll_count = 0 
    if not hasattr(game, 'p1_step'):
        game.p1_step = 'draft_r'; game.p1_proposals = {'R': None, 'H': None}; game.p1_selected_plan = None
    for k in list(st.session_state.keys()):
        if k.startswith('ui_decay_') or k.endswith('_acts'): del st.session_state[k]
    st.session_state.turn_initialized = True
    if game.year == 1:
        st.session_state.news_flash = f"🎉 **【建國大選：勢均力敵】** 遊戲開始！{game.ruling_party.name} 黨獲得初代執政權。"

view_party = game.proposing_party
opponent_party = game.party_B if view_party.name == game.party_A.name else game.party_A
is_election_year = (game.year % cfg['ELECTION_CYCLE'] == 1)

with st.sidebar:
    ui_core.render_global_settings(cfg, game)
    ui_core.render_sidebar_intel_audit(game, view_party, cfg)
    god_mode = st.toggle(t("👁️ 上帝視角", "👁️ God Mode"), False)
    if st.button(t("🔄 重新開始遊戲", "🔄 Restart Game"), use_container_width=True): st.session_state.clear(); st.rerun()

st.title(t("🏛️ 國家發展委員會：共生民主決策系統", "🏛️ NDC: Symbiocracy Management System"))

elec_status = config.get_election_icon(game.year, cfg['ELECTION_CYCLE'])
st.subheader(t(f"📅 {cfg['CALENDAR_NAME']} {game.year} 年 ({elec_status})", f"📅 {cfg['CALENDAR_NAME']} Year {game.year} ({elec_status})"))

if god_mode:
    real_loss = game.gdp * (game.current_real_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
    st.error(t(f"👁️ **上帝視角：** 真實衰退值為 **{game.current_real_decay:.3f}** (損失建設量: {real_loss:.1f})"))

if game.phase == 1 or game.phase == 2:
    ui_core.render_dashboard(game, view_party, cfg, is_preview=(game.phase==2))
    ui_core.render_party_cards(game, view_party, god_mode, is_election_year, cfg)
    ui_core.render_message_board(game)

if game.phase == 1:
    phase1.render(game, view_party, cfg)
elif game.phase == 2:
    phase2.render(game, view_party, opponent_party, cfg)
elif game.phase == 3:
    phase3.render(game, cfg)

if game.phase != 4:
    ui_formulas.render_formula_panel(game, view_party, cfg)
