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
    st.sidebar.title(t("🎛️ 控制台", "🎛️ Control Panel"))
    
    lang = st.session_state.get('lang', 'EN')
    btn_text = "🌐 切換至中文" if lang == 'EN' else "🌐 Switch to English"
    if st.sidebar.button(btn_text, use_container_width=True):
        st.session_state.lang = 'ZH' if lang == 'EN' else 'EN'
        st.rerun()

    with st.sidebar.expander(t("📝 參數調整(即時)", "📝 Parameter Settings"), expanded=False):
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
        st.markdown(t("### 🌐 國家總體現況", "### 🌐 National Status"))
        san_chg = (disp_san - rep['old_san']) if rep else 0
        st.markdown(t(f"**資訊辨識:** `{config.get_civic_index_text(disp_san)}` *(變動: {san_chg:+.1f})*", f"**Civic Literacy:** `{config.get_civic_index_text(disp_san)}` *(Change: {san_chg:+.1f})*"))
        emo_chg = disp_emo - rep['old_emo'] if rep else 0
        st.markdown(t(f"**選民情緒:** `{config.get_emotion_text(disp_emo)}` *(變動: {emo_chg:+.1f})*", f"**Voter Emotion:** `{config.get_emotion_text(disp_emo)}` *(Change: {emo_chg:+.1f})*"))
        if is_preview:
            st.markdown(t(f"**預估 GDP:** `{disp_gdp:.0f}` *(變動: {disp_gdp - game.gdp:+.0f})*", f"**Est. GDP:** `{disp_gdp:.0f}` *(Change: {disp_gdp - game.gdp:+.0f})*"))
        else:
            t_gdp = st.session_state.turn_data.get('target_gdp', 0) if game.year > 1 else 0
            st.markdown(t(f"**當前 GDP:** `{disp_gdp:.1f}` *(變動: {disp_gdp - rep['old_gdp'] if rep else 0:+.0f})*", f"**Current GDP:** `{disp_gdp:.1f}` *(Change: {disp_gdp - rep['old_gdp'] if rep else 0:+.0f})*"))

    with c2:
        st.markdown(t("### 💰 執行系統資源", "### 💰 Executive Resources"))
        if game.year == 1 and not is_preview: st.info(t("首年重整中，尚未配發獎勵。", "Year 1: Reorganizing, no funds distributed yet."))
        else:
            current_h_ratio = (disp_h_fund / disp_budg) * 100 if disp_budg > 0 else 50
            st.markdown(t(f"**總預算池:** `{disp_budg:.0f}` *(變動: {disp_budg - rep['old_budg'] if rep else 0:+.0f})*", f"**Total Budget:** `{disp_budg:.0f}` *(Change: {disp_budg - rep['old_budg'] if rep else 0:+.0f})*"))
            t_h = st.session_state.turn_data.get('target_h_fund', 0) if game.year > 1 else 0
            st.markdown(t(f"**獎勵基金:** `{disp_h_fund:.0f}` *(佔比: {current_h_ratio:.1f}%)*", f"**Reward Fund:** `{disp_h_fund:.0f}` *(Share: {current_h_ratio:.1f}%)*"))

    with c3:
        fc = view_party.current_forecast
        acc = min(100, int((view_party.predict_ability / cfg['MAX_ABILITY']) * 100))
        st.markdown(t(f"### 🕵️ 智庫 準確度: {acc}%", f"### 🕵️ Think Tank Acc: {acc}%"))
        st.write(t(f"經濟預估: {config.get_economic_forecast_text(fc)}(預估衰退值: -{fc:.2f})", f"Forecast: {config.get_economic_forecast_text(fc)} (Est. Decay: -{fc:.2f})"))
        if rep:
            diff = abs(rep['view_party_forecast'] - rep['real_decay'])
            eval_txt = config.get_thinktank_eval(view_party.predict_ability, diff)
            st.write(t(f"\n({cfg['CALENDAR_NAME']} {game.year-1} 年度內部檢討報告: \n", f"\n({cfg['CALENDAR_NAME']} Year {game.year-1} Review: \n"))
            st.write(f"{eval_txt}\n")
            st.write(t(f"判讀誤差值: {diff:.2f} / 實真: -{rep['real_decay']:.2f} / 估值: -{rep['view_party_forecast']:.2f})", f"Error: {diff:.2f} / Real: -{rep['real_decay']:.2f} / Est: -{rep['view_party_forecast']:.2f})"))
        else:
            st.write(t("\n(尚無去年歷史資料以供檢討)", "\n(No historical data for review)"))

    with c4:
        if game.phase == 1:
            st.markdown(t("### 📊 財報", "### 📊 Finances"))
            total_maint = sum([formulas.get_ability_maintenance(a, cfg) for a in [view_party.build_ability, view_party.investigate_ability, view_party.media_ability, view_party.predict_ability, view_party.stealth_ability]])
            
            if game.year == 1:
                st.write(t(f"可用淨資產: {int(view_party.wealth)} ({int(view_party.wealth)} - 0)", f"Net Assets: {int(view_party.wealth)} ({int(view_party.wealth)} - 0)"))
            else:
                st.write(t(f"可用淨資產: {int(view_party.wealth)} ({int(view_party.wealth + total_maint)} - {int(total_maint)})", f"Net Assets: {int(view_party.wealth)} ({int(view_party.wealth + total_maint)} - {int(total_maint)})"))
                
            if rep:
                my_is_h = view_party.name == rep['h_party_name']
                real_inc = rep['h_inc'] if my_is_h else rep['r_inc']
                est_inc = rep['est_h_inc'] if my_is_h else rep['est_r_inc']
                pol_cost = view_party.last_acts.get('policy', 0)
                
                st.write(t(f"淨利: 真:{real_inc:.0f} (去年估:{est_inc:.0f})", f"Net: Real:{real_inc:.0f} (Est:{est_inc:.0f})"))
                st.write(t(f"去年施政花費: {pol_cost:.0f} 維護成本: {total_maint:.0f}", f"Last Yr Policy Cost: {pol_cost:.0f} Maint: {total_maint:.0f}"))
                final_profit = real_inc - pol_cost - total_maint
                st.write(t(f"收益總結: {real_inc:.0f} - {pol_cost:.0f} - {total_maint:.0f} = **{final_profit:.0f}**", f"Profit Summary: {real_inc:.0f} - {pol_cost:.0f} - {total_maint:.0f} = **{final_profit:.0f}**"))
        else:
            if is_preview:
                my_is_h = view_party.name == game.h_role_party.name
                my_net = preview_data['h_inc'] if my_is_h else preview_data['r_inc']
                opp_net = preview_data['r_inc'] if my_is_h else preview_data['h_inc']
                my_roi = preview_data['h_roi'] if my_is_h else preview_data['r_roi']
                opp_roi = preview_data['r_roi'] if my_is_h else preview_data['h_roi']
                
                st.markdown(t("### 📊 智庫評估報告", "### 📊 Think Tank Report"))
                st.markdown(t(f"我方預估收益: {my_net:.0f} (ROI: {my_roi:.1f}%)", f"Our Est. Profit: {my_net:.0f} (ROI: {my_roi:.1f}%)"))
                st.markdown(t(f"對方預估收益: {opp_net:.0f} (ROI: {opp_roi:.1f}%)", f"Opp Est. Profit: {opp_net:.0f} (ROI: {opp_roi:.1f}%)"))
                st.markdown(t(f"支持度預估: {preview_data['my_sup_shift']:+.2f}%", f"Est. Support: {preview_data['my_sup_shift']:+.2f}%"))
                st.markdown(t(f"📈 預期 GDP: {game.gdp:.0f} ➔ {disp_gdp:.0f} ({((disp_gdp-game.gdp)/max(1.0, game.gdp))*100:+.2f}%)", f"📈 Exp. GDP: {game.gdp:.0f} ➔ {disp_gdp:.0f} ({((disp_gdp-game.gdp)/max(1.0, game.gdp))*100:+.2f}%)"))
                st.markdown(t(f"衰退值判讀: 🟢 風險極低 (基準比對)", f"Decay Risk: 🟢 Low Risk (Baseline)"))
    st.markdown("---")

def render_message_board(game):
    if st.session_state.get('news_flash'):
        st.warning(st.session_state.news_flash)
        st.session_state.news_flash = None
        
    if game.phase == 1:
        if game.year == 1: st.info(t("📢 **【年度通報】** 新的一年開始了，國家百廢待舉，請盡快展開預算與目標協商。", "📢 **[ANNUAL UPDATE]** A new year begins. Please start budget negotiations."))
        elif game.last_year_report:
            st.info(t(f"📢 **【年度通報】** 新的一年開始了，請盡快展開預算與目標協商。", "📢 **[ANNUAL UPDATE]** A new year begins. Please start budget negotiations."))
    elif game.phase == 2:
        st.info(t("📢 **【年度通報】** 法案已通過，請分配黨產資金進行內部升級、競選造勢與媒體攻防。", "📢 **[ANNUAL UPDATE]** Bill passed. Allocate funds for upgrades, campaigns, and media."))

def render_party_cards(game, view_party, god_mode, is_election_year, cfg):
    st.header(t("👤 玩家頁面", "👤 Player View"))
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
            role_badge = t("🛡️ [執行系統]", "🛡️ [H-System]") if is_h else t("⚖️ [監管系統]", "⚖️ [R-System]")
            is_winner = (game.ruling_party.name == party.name)
            crown_str = cfg.get('CROWN_WINNER', t('👑 當權', '👑 Ruling')) if is_winner else cfg.get('CROWN_LOSER', t('🎯 候選', '🎯 Candidate'))
            logo = config.get_party_logo(party.name)
            
            eye = "👁️ " if party.name == view_party.name else ""
            st.markdown(f"## {eye}{logo} {party.name} {crown_str}")
            st.markdown(f"#### {role_badge}")

            if is_election_year or god_mode: 
                disp_sup = f"{party.support:.1f}%" + (t(" 🏆(當選!)", " 🏆(Elected!)") if is_winner else t(" 💀(落選)", " 💀(Lost)"))
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
                        disp_sup = t(f"{party.latest_poll:.1f}%(最新民調) ({count}次{best_type}民調平均: {avg:.1f}%)", f"{party.latest_poll:.1f}%(Latest Poll) ({count} {best_type} avg: {avg:.1f}%)")
                    else:
                        disp_sup = t(f"{party.latest_poll:.1f}%(最新民調)", f"{party.latest_poll:.1f}%(Latest Poll)")
                else:
                    disp_sup = t("??? (需作民調)", "??? (Needs Poll)")
            
            st.markdown(t(f"### 📊 支持度: {disp_sup}", f"### 📊 Support: {disp_sup}"))
            
            if party.name == view_party.name and not is_election_year:
