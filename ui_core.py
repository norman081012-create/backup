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
        st.markdown(t("### 🌐 國家總體現況"))
        san_chg = (disp_san - rep['old_san']) if rep else 0
        st.markdown(f"**{t('資訊辨識')}:** `{config.get_civic_index_text(disp_san)}` *({t('變動')}: {san_chg:+.1f})*")
        emo_chg = disp_emo - rep['old_emo'] if rep else 0
        st.markdown(f"**{t('選民情緒')}:** `{config.get_emotion_text(disp_emo)}` *({t('變動')}: {emo_chg:+.1f})*")
        
        gdp_base = rep['old_gdp'] if rep else game.gdp
        gdp_diff = disp_gdp - gdp_base
        gdp_pct = (gdp_diff / max(1.0, gdp_base)) * 100.0
        label_gdp = t("預估 GDP") if is_preview else t("當前 GDP")
        st.markdown(f"**{label_gdp}:** `{disp_gdp:.1f}` *({t('變動')}: {gdp_diff:+.1f}, {gdp_pct:+.2f}%)*")

    with c2:
        st.markdown(t("### 💰 執行系統資源"))
        if game.year == 1 and not is_preview: st.info("首年重整中，尚未配發獎勵。")
        else:
            current_h_ratio = (disp_h_fund / disp_budg) * 100 if disp_budg > 0 else 50
            st.markdown(f"**{t('總預算池')}:** `{disp_budg:.1f}` *({t('變動')}: {disp_budg - rep['old_budg'] if rep else 0:+.1f})*")
            st.markdown(f"**{t('獎勵基金')}:** `{disp_h_fund:.1f}` *({t('佔比')}: {current_h_ratio:.1f}%)*")

    with c3:
        fc = view_party.current_forecast
        acc = min(100, int((view_party.predict_ability / cfg['MAX_ABILITY']) * 100))
        st.markdown(f"### 🕵️ {t('智庫')} {t('準確度')}: {acc}%")
        st.write(f"{t('經濟預估')}: {config.get_economic_forecast_text(fc)} ({t('預估衰退值')}: -{fc:.2f})")
        if rep:
            diff = abs(rep['view_party_forecast'] - rep['real_decay'])
            eval_txt = config.get_thinktank_eval(view_party.predict_ability, diff)
            st.write(f"\n({cfg['CALENDAR_NAME']} {game.year-1} 年度內部檢討報告: \n")
            st.write(f"{eval_txt}\n")
        else:
            st.write("\n(尚無去年歷史資料以供檢討)")

    with c4:
        if game.phase == 1:
            st.markdown(t("### 📊 財報"))
            total_maint = sum([formulas.get_ability_maintenance(a, cfg) for a in [view_party.build_ability, view_party.investigate_ability, view_party.media_ability, view_party.predict_ability, view_party.stealth_ability]])
            if game.year == 1:
                st.write(f"{t('可用淨資產')}: {view_party.wealth:.1f} ({view_party.wealth:.1f} - 0.0)")
            else:
                st.write(f"{t('可用淨資產')}: {view_party.wealth:.1f} ({(view_party.wealth + total_maint):.1f} - {total_maint:.1f})")
                
            if rep:
                my_is_h = view_party.name == rep['h_party_name']
                real_inc = rep['h_inc'] if my_is_h else rep['r_inc']
                est_inc = rep['est_h_inc'] if my_is_h else rep['est_r_inc']
                pol_cost = view_party.last_acts.get('policy', 0)
                st.write(f"{t('淨利')}: {t('真')}:{real_inc:.1f} ({t('去年估')}:{est_inc:.1f})")
        else:
            if is_preview:
                my_is_h = view_party.name == game.h_role_party.name
                my_net = preview_data['h_inc'] if my_is_h else preview_data['r_inc']
                opp_net = preview_data['r_inc'] if my_is_h else preview_data['h_inc']
                
                st.markdown(t("### 📊 智庫評估報告"))
                st.markdown(f"{t('我方預估收益')}: {my_net:.1f}")
                st.markdown(f"{t('對方預估收益')}: {opp_net:.1f}")
                st.markdown(f"{t('支持度預估')}: {preview_data['my_sup_shift']:+.2f}%")
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
    st.header(t("👤 玩家頁面"))
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
            role_badge = t("🛡️ [執行系統]") if is_h else t("⚖️ [監管系統]")
            is_winner = (game.ruling_party.name == party.name)
            crown_str = cfg.get('CROWN_WINNER', t('👑 當權')) if is_winner else cfg.get('CROWN_LOSER', t('🎯 候選'))
            logo = config.get_party_logo(party.name)
            
            eye = "👁️ " if party.name == view_party.name else ""
            st.markdown(f"## {eye}{logo} {party.name} {crown_str}")
            st.markdown(f"#### {role_badge}")

            if party.name == view_party.name:
                st.markdown(f"**{t('黨產資金')}:** `${party.wealth:.1f}`")
            else:
                rng = random.Random(f"wealth_{party.name}_{game.year}")
                
                opp_stl = party.stealth_ability / 10.0
                my_inv = view_party.investigate_ability / 10.0
                err_margin = max(0.0, 1.0 + opp_stl - my_inv) * cfg.get('OBS_ERR_BASE', 0.2)
                blur = err_margin if not god_mode else 0.0
                est_wealth = party.wealth * (1 + rng.uniform(-blur, blur))
                st.markdown(f"**{t('黨產資金')}:** `${est_wealth:.1f}` *({t('預估')})*")

            if is_election_year or god_mode: 
                disp_sup = f"{party.support:.1f}%" + (" 🏆(當選!)" if is_winner else " 💀(落選)")
            else:
                if party.latest_poll is not None:
                    best_type = None
                    for pt in ['大型', '中型', '小型']:
                        if len(party.poll_history[pt]) > 0:
                            best_type = pt
                            break
                    if best_type:
                        avg = sum(party.poll_history[best_type]) / len(party.poll_history[best_type])
                        count = len(party.poll_history[best_type])
                        disp_sup = f"{party.latest_poll:.1f}%(最新民調) ({count}次{best_type}民調平均: {avg:.1f}%)"
                    else:
                        disp_sup = f"{party.latest_poll:.1f}%(最新民調)"
                else:
                    disp_sup = "??? (需作民調)"
            
            st.markdown(f"### 📊 {t('支持度')}: {disp_sup}")
            
            if party.name == view_party.name and not is_election_year:
                b1, b2, b3 = st.columns(3)
                if b1.button(t("小民調 ($5)"), key=f"p1_{party.name}"): engine.execute_poll(game, view_party, 5); st.rerun()
                if b2.button(t("中民調 ($10)"), key=f"p2_{party.name}"): engine.execute_poll(game, view_party, 10); st.rerun()
                if b3.button(t("大民調 ($20)", "Big Poll ($20)"), key=f"p3_{party.name}"): engine.execute_poll(game, view_party, 20); st.rerun()

def render_sidebar_intel_audit(game, view_party, cfg):
    opp = game.party_B if view_party.name == game.party_A.name else game.party_A
    st.markdown("---")
    st.title(t("🕵️ 情報處 - 對手機構指標"))
    
    # 真實觀測誤差計算公式
    opp_stl = opp.stealth_ability / 10.0
    my_inv = view_party.investigate_ability / 10.0
    err_margin = max(0.0, 1.0 + opp_stl - my_inv) * cfg.get('OBS_ERR_BASE', 0.2)
    blur = err_margin if not st.session_state.get('god_mode') else 0.0
    acc = max(0, min(100, int((1.0 - err_margin) * 100)))
    
    st.progress(acc / 100.0, text=f"{t('準確度')}: {acc}%")
    rng = random.Random(f"intel_{opp.name}_{game.year}")
    
    st.write(f"{t('智庫')}: {max(0, opp.predict_ability*(1+rng.uniform(-blur, blur))*10):.1f}% | {t('情報處')}: {max(0, opp.investigate_ability*(1+rng.uniform(-blur, blur))*10):.1f}%")
    st.write(f"{t('黨媒')}: {max(0, opp.media_ability*(1+rng.uniform(-blur, blur))*10):.1f}% | {t('反情報處')}: {max(0, opp.stealth_ability*(1+rng.uniform(-blur, blur))*10):.1f}%")
    st.write(f"{t('工程處')}: {max(0, opp.build_ability*(1+rng.uniform(-blur, blur))*10):.1f}%")

    st.markdown("---")
    st.title(t("🧾 審計處 - 內部部門報告"))
    total_maint = sum([formulas.get_ability_maintenance(a, cfg) for a in [view_party.build_ability, view_party.investigate_ability, view_party.media_ability, view_party.predict_ability, view_party.stealth_ability]])
    st.write(f"{t('智庫')}: {view_party.predict_ability*10:.1f}% | {t('情報處')}: {view_party.investigate_ability*10:.1f}%")
    st.write(f"{t('黨媒')}: {view_party.media_ability*10:.1f}% | {t('反情報處')}: {view_party.stealth_ability*10:.1f}%")
    st.write(f"{t('工程處')}: {view_party.build_ability*10:.1f}%")
    st.write(f"**(依據當前機構投資，明年維護費估算: -${total_maint:.1f})**")

def render_proposal_component(title, plan, game, view_party, cfg):
    st.markdown(f"#### {title}")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write(f"**{t('公告衰退值')}:** {plan['claimed_decay']:.2f} | **{t('標案總額 (最高不超過當年總預算)')}:** {plan['proj_fund']:.1f}")
        st.write(f"**{t('標案成本 (要求之建設產出值，留點利潤給對手賺)')}:** {plan['bid_cost']:.1f} ({t('監管出資')}: {plan['r_pays']:.1f} | {t('執行出資')}: {plan['h_pays']:.1f})")
        
    with c2:
        opp = game.party_B if view_party.name == game.party_A.name else game.party_A
        my_is_h = (view_party.name == game.h_role_party.name)
        
        # 依照對手真實能力推演經濟
        target_build_abi = game.h_role_party.build_ability
        res = formulas.calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], target_build_abi, view_party.current_forecast)
        
        h_gross = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == game.h_role_party.name else 0) + res['payout_h']
        r_gross = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == game.r_role_party.name else 0) + res['payout_r']
        h_net = h_gross - plan['h_pays']
        r_net = r_gross - plan['r_pays']
        
        o_h_roi = (h_net / max(1.0, float(plan['h_pays']))) * 100.0 if plan['h_pays'] > 0 else float('inf')
        o_r_roi = (r_net / max(1.0, float(plan['r_pays']))) * 100.0 if plan['r_pays'] > 0 else float('inf')
        
        my_net, my_roi = (h_net, o_h_roi) if my_is_h else (r_net, o_r_roi)
        opp_net, opp_roi = (r_net, o_r_roi) if my_is_h else (h_net, o_h_roi)

        # 依據上一回合的雙方媒體預算進行估算
        shift_preview = formulas.calc_support_shift(
            cfg, game.h_role_party, game.r_role_party, 
            res['payout_h'], res['est_gdp'], plan['proj_fund'], game.gdp, 
            game.h_role_party.last_acts, game.r_role_party.last_acts, 
            res['h_idx'], plan.get('claimed_decay', 0.0), game.sanity, game.emotion
        )
        my_sup = shift_preview['actual_shift'] if my_is_h else -shift_preview['actual_shift']
        o_gdp_pct = ((res['est_gdp'] - game.gdp) / max(1.0, game.gdp)) * 100.0

        st.markdown(t("### 📝 智庫分析報告"))
        st.markdown(f"1. {t('我方預估收益')}: {my_net:.1f} (ROI: {my_roi:.1f}%)")
        st.markdown(f"2. {t('對方預估收益')}: {opp_net:.1f} (ROI: {opp_roi:.1f}%)")
        st.markdown(f"3. {t('支持度變化預估')}: {my_sup:+.2f}%")
        st.markdown(f"4. {t('預期 GDP 變化')}: {game.gdp:.1f} ➔ {res['est_gdp']:.1f} ({o_gdp_pct:+.2f}%)")
        
        diff = abs(plan.get('claimed_decay', 0.0) - view_party.current_forecast)
        if diff > 0.3: light, risk_txt = "🔴", t("差異極大 (對方恐隱瞞嚴重衰退或灌水)")
        elif diff > 0.1: light, risk_txt = "🟡", t("中等差異 (數據略有出入)")
        else: light, risk_txt = "🟢", t("差異極小 (雙方預測基準一致)")
        st.markdown(f"5. {t('衰退值差異')}: {light} {risk_txt} ({t('公告')}: {plan.get('claimed_decay', 0.0):.2f} / {t('智庫')}: {view_party.current_forecast:.2f})")

def ability_slider(label, key, current_val, wealth, cfg, build_ability=0.0):
    current_pct = current_val * 10.0
    t_pct = st.slider(f"{label}", 0.0, 100.0, float(current_pct), 1.0, key=key)
    
    t_val = t_pct / 10.0
    cost = formulas.calculate_upgrade_cost(current_val, t_val, build_ability)
    maint = formulas.get_ability_maintenance(t_val, cfg)
    
    if t_val > current_val:
        st.caption(f"📈 {t('升級花費')}: ${cost:.1f} | 能力: {current_pct:.1f}% ➔ {t_pct:.1f}% | {t('維護費將達')} ${maint:.1f}")
    elif t_val < current_val:
        st.caption(f"📉 {t('降級退回')} | 能力: {current_pct:.1f}% ➔ {t_pct:.1f}% | {t('維護費降至')} ${maint:.1f}")
    else:
        st.caption(f"🛡️ {t('穩定維持')} | 能力: {current_pct:.1f}% | {t('維護費')} ${maint:.1f}")
        
    return t_val, cost

def add_event_vlines(fig, history_df):
    for _, row in history_df.iterrows():
        y = row['Year']
        if row['Is_Swap']: fig.add_vline(x=y, line_dash="dot", line_color="red", annotation_text="倒閣!", annotation_position="top left")
        if row['Is_Election']: fig.add_vline(x=y, line_dash="dash", line_color="green", annotation_text="選舉", annotation_position="bottom right")

def render_endgame_charts(history_data, cfg):
    st.balloons()
    st.title("🏁 遊戲結束！共生內閣軌跡總結算")
    df = pd.DataFrame(history_data)
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(x=df['Year'], y=df['GDP'], name="總 GDP", line=dict(color='blue', width=3)), secondary_y=False)
    fig1.add_trace(go.Scatter(x=df['Year'], y=df['Sanity'], name="資訊辨識 (0-100)", line=dict(color='purple', width=3)), secondary_y=True)
    add_event_vlines(fig1, df)
    st.plotly_chart(fig1, use_container_width=True)

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
