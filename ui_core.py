# ==========================================
# ui_core.py
# 負責共用 UI 渲染、圖表繪製、標準化組件
# ==========================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import config
import formulas
import engine
import random

def render_global_settings(cfg, game):
    st.sidebar.title("🎛️ 控制台")
    with st.sidebar.expander("📝 參數調整(即時)", expanded=False):
        for key, default_val in config.DEFAULT_CONFIG.items():
            if 'COLOR' in key: cfg[key] = st.color_picker(key, value=cfg[key], key=f"cfg_{key}")
            elif isinstance(default_val, float): cfg[key] = st.number_input(key, value=float(cfg[key]), step=0.1, format="%.2f", key=f"cfg_{key}")
            elif isinstance(default_val, int): cfg[key] = st.number_input(key, value=int(cfg[key]), step=1, key=f"cfg_{key}")
    game.party_A.name = cfg['PARTY_A_NAME']; game.party_B.name = cfg['PARTY_B_NAME']

def render_dashboard(game, view_party, cfg, is_preview=False, preview_data=None):
    rep = game.last_year_report
    st.markdown("---")
    
    disp_gdp = preview_data['gdp'] if is_preview else game.gdp
    disp_san = preview_data['san'] if is_preview else game.sanity
    disp_emo = preview_data['emo'] if is_preview else game.emotion
    disp_h_fund = preview_data['h_fund'] if is_preview else game.h_fund
    disp_budg = preview_data['budg'] if is_preview else game.total_budget
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("### 🌐 國家總體現況")
        san_chg = (disp_san - rep['old_san']) if rep else 0
        st.markdown(f"**資訊辨識:** `{config.get_civic_index_text(disp_san)}` *(變動: {san_chg:+.1f})*")
        emo_chg = disp_emo - rep['old_emo'] if rep else 0
        st.markdown(f"**選民情緒:** `{config.get_emotion_text(disp_emo)}` *(變動: {emo_chg:+.1f})*")
        
        gdp_base = rep['old_gdp'] if rep else game.gdp
        gdp_diff = disp_gdp - gdp_base
        gdp_pct = (gdp_diff / max(1.0, gdp_base)) * 100.0
        label_gdp = "預估 GDP" if is_preview else "當前 GDP"
        st.markdown(f"**{label_gdp}:** `{disp_gdp:.1f}` *(變動: {gdp_diff:+.1f}, {gdp_pct:+.2f}%)*")

    with c2:
        st.markdown("### 💰 執行系統資源")
        if game.year == 1 and not is_preview: st.info("首年重整中，尚未配發獎勵。")
        else:
            current_h_ratio = (disp_h_fund / disp_budg) * 100 if disp_budg > 0 else 50
            st.markdown(f"**總預算池:** `{disp_budg:.1f}` *(變動: {disp_budg - rep['old_budg'] if rep else 0:+.1f})*")
            st.markdown(f"**獎勵基金:** `{disp_h_fund:.1f}` *(佔比: {current_h_ratio:.1f}%)*")

    with c3:
        fc = view_party.current_forecast
        acc = min(100, int((view_party.predict_ability / cfg['MAX_ABILITY']) * 100))
        st.markdown(f"### 🕵️ 智庫 準確度: {acc}%")
        st.write(f"經濟預估: {config.get_economic_forecast_text(fc)} (預估衰退值: -{fc:.2f})")

    with c4:
        if game.phase == 1:
            st.markdown("### 📊 財報")
            total_maint = sum([formulas.get_ability_maintenance(a, cfg) for a in [view_party.build_ability, view_party.investigate_ability, view_party.media_ability, view_party.predict_ability, view_party.stealth_ability]])
            st.write(f"可用淨資產: {view_party.wealth:.1f}")
        else:
            st.markdown("### 📊 智庫評估")
            st.markdown("請參考下方詳細智庫報告。")
    st.markdown("---")

def render_message_board(game):
    if st.session_state.get('news_flash'):
        st.warning(st.session_state.news_flash)
        st.session_state.news_flash = None
        
    if game.phase == 1:
        if game.year == 1: st.info("📢 **【年度通報】** 新的一年開始了，國家百廢待舉，請盡快展開預算與目標協商。")
        elif game.last_year_report: st.info("📢 **【年度通報】** 新的一年開始了，請盡快展開預算與目標協商。")
    elif game.phase == 2:
        st.info("📢 **【年度通報】** 法案已通過，請分配黨產資金進行內部升級、競選造勢與媒體攻防。")

def render_party_cards(game, view_party, god_mode, is_election_year, cfg):
    st.header("👤 玩家頁面")
    c1, c2 = st.columns(2)
    opp = game.party_B if view_party.name == game.party_A.name else game.party_A
    
    st.markdown(f"""
    <style>
    div[data-testid="column"]:nth-child(1) {{ background-color: {cfg['PARTY_A_COLOR']}1A; padding: 15px; border-radius: 10px; border-left: 5px solid {cfg['PARTY_A_COLOR']}; }}
    div[data-testid="column"]:nth-child(2) {{ background-color: {cfg['PARTY_B_COLOR']}1A; padding: 15px; border-radius: 10px; border-left: 5px solid {cfg['PARTY_B_COLOR']}; }}
    </style>
    """, unsafe_allow_html=True)

    for col, party in zip([c1, c2], [view_party, opp]):
        with col:
            is_h = (game.h_role_party.name == party.name)
            role_badge = "🛡️ [執行系統]" if is_h else "⚖️ [監管系統]"
            is_winner = (game.ruling_party.name == party.name)
            crown_str = "👑 當權" if is_winner else "🎯 候選"
            logo = config.get_party_logo(party.name)
            
            eye = "👁️ " if party.name == view_party.name else ""
            st.markdown(f"## {eye}{logo} {party.name} {crown_str}")
            st.markdown(f"#### {role_badge}")

            if party.name == view_party.name:
                st.markdown(f"**黨產資金:** `${party.wealth:.1f}`")
            else:
                rng = random.Random(f"wealth_{party.name}_{game.year}")
                opp_stl = party.stealth_ability / 10.0
                my_inv = view_party.investigate_ability / 10.0
                err_margin = max(0.0, 1.0 + opp_stl - my_inv) * cfg.get('OBS_ERR_BASE', 0.4)
                blur = err_margin if not god_mode else 0.0
                est_wealth = party.wealth * (1 + rng.uniform(-blur, blur))
                st.markdown(f"**黨產資金:** `${est_wealth:.1f}` *(預估)*")

            if is_election_year or god_mode: 
                disp_sup = f"{party.support:.1f}%" + (" 🏆(當選!)" if is_winner else " 💀(落選)")
            else:
                disp_sup = f"{party.latest_poll:.1f}%(最新民調)" if party.latest_poll is not None else "??? (需作民調)"
            
            st.markdown(f"### 📊 支持度: {disp_sup}")
            
            if party.name == view_party.name and not is_election_year:
                b1, b2, b3 = st.columns(3)
                if b1.button("小民調 ($5)", key=f"p1_{party.name}"): engine.execute_poll(game, view_party, 5); st.rerun()
                if b2.button("中民調 ($10)", key=f"p2_{party.name}"): engine.execute_poll(game, view_party, 10); st.rerun()
                if b3.button("大民調 ($20)", key=f"p3_{party.name}"): engine.execute_poll(game, view_party, 20); st.rerun()

def render_sidebar_intel_audit(game, view_party, cfg):
    opp = game.party_B if view_party.name == game.party_A.name else game.party_A
    st.markdown("---")
    st.title("🕵️ 情報處 - 對手機構指標")
    
    opp_stl = opp.stealth_ability / 10.0
    my_inv = view_party.investigate_ability / 10.0
    err_margin = max(0.0, 1.0 + opp_stl - my_inv) * cfg.get('OBS_ERR_BASE', 0.4)
    blur = err_margin if not st.session_state.get('god_mode') else 0.0
    acc = max(0, min(100, int((1.0 - err_margin) * 100)))
    
    st.progress(acc / 100.0, text=f"準確度: {acc}%")
    rng = random.Random(f"intel_{opp.name}_{game.year}")
    
    st.write(f"智庫: {max(0, opp.predict_ability*(1+rng.uniform(-blur, blur))*10):.1f}% | 情報處: {max(0, opp.investigate_ability*(1+rng.uniform(-blur, blur))*10):.1f}%")
    st.write(f"黨媒: {max(0, opp.media_ability*(1+rng.uniform(-blur, blur))*10):.1f}% | 反情報處: {max(0, opp.stealth_ability*(1+rng.uniform(-blur, blur))*10):.1f}%")
    st.write(f"工程處: {max(0, opp.build_ability*(1+rng.uniform(-blur, blur))*10):.1f}%")

    st.markdown("---")
    st.title("🏢 審計處 - 內部部門報告")
    total_maint = sum([formulas.get_ability_maintenance(a, cfg) for a in [view_party.build_ability, view_party.investigate_ability, view_party.media_ability, view_party.predict_ability, view_party.stealth_ability]])
    st.write(f"智庫: {view_party.predict_ability*10:.1f}% | 情報處: {view_party.investigate_ability*10:.1f}%")
    st.write(f"黨媒: {view_party.media_ability*10:.1f}% | 反情報處: {view_party.stealth_ability*10:.1f}%")
    st.write(f"工程處: {view_party.build_ability*10:.1f}%")
    st.write(f"**(明年維護費估算: -${total_maint:.1f})**")

def render_proposal_component(title, plan, game, view_party, cfg):
    st.markdown(f"#### {title}")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**公告衰退值:** {plan['claimed_decay']:.2f} | **標案總額:** {plan['proj_fund']:.1f}")
        st.write(f"**標案成本 (要求值):** {plan['bid_cost']:.1f} (監管出資: {plan['r_pays']:.1f} | 執行出資: {plan['h_pays']:.1f})")
    with c2:
        st.write("👉 詳見下方公式與計算過程監控面板")

def ability_slider(label, key, current_val, wealth, cfg, build_ability=0.0):
    current_pct = current_val * 10.0
    t_pct = st.slider(f"{label}", 0.0, 100.0, float(current_pct), 1.0, key=key)
    
    t_val = t_pct / 10.0
    cost = formulas.calculate_upgrade_cost(current_val, t_val, build_ability)
    maint = formulas.get_ability_maintenance(t_val, cfg)
    
    if t_val > current_val:
        st.caption(f"📈 升級花費: ${cost:.1f} | 能力: {current_pct:.1f}% ➔ {t_pct:.1f}% | 維護費將達 ${maint:.1f}")
    elif t_val < current_val:
        st.caption(f"📉 降級退回 | 能力: {current_pct:.1f}% ➔ {t_pct:.1f}% | 維護費降至 ${maint:.1f}")
    else:
        st.caption(f"🛡️ 穩定維持 | 能力: {current_pct:.1f}% | 維護費 ${maint:.1f}")
    return t_val, cost

def render_formula_panel(game, view_party, cfg):
    with st.expander("🧮 遊戲公式與計算過程監控 (智庫解析)", expanded=False):
        plan = None
        if game.phase == 1 and getattr(game, 'p1_selected_plan', None): plan = game.p1_selected_plan
        elif game.phase >= 2: plan = st.session_state.get('turn_data')
            
        if plan and 'proj_fund' in plan:
            lines = formulas.get_formula_explanation(game, view_party, plan, cfg)
            for line in lines: st.markdown(line)
        else:
            st.info("目前階段尚無具體標案數據可供計算。")
