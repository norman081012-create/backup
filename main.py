# ==========================================
# main.py
# ==========================================
import ui_formulas
import streamlit as st
import random
import config
import engine
import ui_core
import ui_proposal 
import phase1
import phase2
import phase3
import phase4
import i18n
import ai_bot  # 📌 引入全新的 AI 神經中樞

st.set_page_config(page_title="共生體制模擬器 v3.0.0", layout="wide")
st.components.v1.html("<script>window.parent.document.querySelector('.main').scrollTo(0,0);</script>", height=0)

if 'lang' not in st.session_state: st.session_state.lang = 'ZH' # 強制繁體中文
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
    st.balloons()
    st.session_state.anim = None
elif st.session_state.get('anim') == 'snow':
    st.snow()
    st.session_state.anim = None

if game.phase == 4:
    phase4.render(game, cfg)
    st.stop()

# ==========================================
# PHASE 0: 遊戲初始設定 (僅在剛啟動時出現)
# ==========================================
if game.phase == 0:
    st.title("🏛️ 共生體制模擬器 - 遊戲設定")
    st.markdown("---")
    
    st.markdown("### 選擇遊戲模式")
    mode = st.radio("請選擇遊玩方式：", ["PvE (單人對戰 AI)", "PvP (單機雙人)"], label_visibility="collapsed")
    
    human_party = None
    if mode == "PvE (單人對戰 AI)":
        st.markdown("### 選擇你的政黨")
        human_party = st.radio("選擇你的陣營：", [f"{cfg['PARTY_A_NAME']} (老鷹)", f"{cfg['PARTY_B_NAME']} (握手)"], label_visibility="collapsed")
        # 清除附帶的說明文字，抓取純黨名
        human_party = human_party.split(" (")[0]
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("開始模擬 🚀", type="primary"):
        game.phase = 1
        if mode == "PvE (單人對戰 AI)":
            game.is_pve = True
            game.human_party_name = human_party
            game.ai_party_name = cfg['PARTY_B_NAME'] if human_party == cfg['PARTY_A_NAME'] else cfg['PARTY_A_NAME']
        else:
            game.is_pve = False
        st.rerun()
    st.stop()  # 阻擋渲染，直到玩家按下開始

# ==========================================
# AI 自動攔截系統 (無縫代打)
# ==========================================
if getattr(game, 'is_pve', False) and game.phase in [1, 2] and game.proposing_party.name == game.ai_party_name:
    st.title("🏛️ 共生體制模擬器 v3.0.0")
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.spinner(f"🤖 **{game.ai_party_name}** 正在制定策略並採取行動..."):
        import time
        time.sleep(0.8) # 稍微延遲 0.8 秒，讓玩家有對手在思考的沉浸感
        ai_bot.take_turn(game, cfg)
        st.rerun()
# ==========================================

if 'turn_initialized' not in st.session_state:
    game.current_real_decay = max(0.0, round(random.uniform(cfg['DECAY_MIN'], cfg['DECAY_MAX']), 3))
    real_infra_loss = game.gdp * (game.current_real_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
    
    for p in [game.party_A, game.party_B]:
        p_acc_weight = cfg.get('PREDICT_ACCURACY_WEIGHT', 0.8)
        error_margin_pct = 1.0 - ((p.predict_ability / 10.0) * p_acc_weight)
        error_range = real_infra_loss * error_margin_pct
        observed_loss = max(0.0, real_infra_loss + random.uniform(-error_range, error_range))
        
        p.current_forecast = max(0.0, round(((observed_loss / max(1.0, game.gdp)) - cfg['BASE_DECAY_RATE']) / cfg['DECAY_WEIGHT_MULT'], 3))
        p.poll_history = {'Small': [], 'Medium': [], 'Large': []}
        p.latest_poll = None
        p.poll_count = 0 
    
    if not hasattr(game, 'p1_step'):
        game.p1_step = 'draft_r'
        game.p1_proposals = {'R': None, 'H': None}
        game.p1_selected_plan = None

    for k in list(st.session_state.keys()):
        if k.startswith('ui_decay_') or k.endswith('_acts'): del st.session_state[k]
    
    st.session_state.turn_initialized = True
    
    if game.year == 1:
        st.session_state.news_flash = f"🎉 **[建國大選]** 模擬開始！{game.ruling_party.name} 贏得了首屆執政權。"

view_party = game.proposing_party
opponent_party = game.party_B if view_party.name == game.party_A.name else game.party_A
is_election_year = (game.year % cfg['ELECTION_CYCLE'] == 1)

with st.sidebar:
    ui_core.render_global_settings(cfg, game)
    ui_core.render_sidebar_intel_audit(game, view_party, cfg)
    god_mode = st.toggle("👁️ 上帝模式", False)
    st.session_state.god_mode = god_mode 
    if st.button("🔄 重新開始遊戲", use_container_width=True): st.session_state.clear(); st.rerun()

st.title("🏛️ 共生體制模擬器 v3.0.0")

elec_status = config.get_election_icon(game.year, cfg['ELECTION_CYCLE'])
st.subheader(f"📅 {cfg['CALENDAR_NAME']} 第 {game.year} 年 ({elec_status})")

if god_mode:
    real_loss = game.gdp * (game.current_real_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
    st.error(f"👁️ **上帝模式:** 真實衰退率為 **{game.current_real_decay:.3f}** (EV 損失: {real_loss:.1f})")

if game.phase == 1 or game.phase == 2:
    if game.phase == 1: ui_core.render_dashboard(game, view_party, cfg, is_preview=False)
    ui_core.render_party_cards(game, view_party, god_mode, is_election_year, cfg)
    ui_core.render_message_board(game)

if game.phase == 1: phase1.render(game, view_party, cfg)
elif game.phase == 2: phase2.render(game, view_party, opponent_party, cfg)
elif game.phase == 3: phase3.render(game, cfg)

if game.phase != 4: ui_formulas.render_formula_panel(game, view_party, cfg)

