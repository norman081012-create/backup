# ==========================================
# ui_core.py
# ==========================================
import streamlit as st
import random
import math
import config
import formulas
import engine
import i18n
t = i18n.t

def sync_party_names(game, cfg):
    game.party_A.name = cfg['PARTY_A_NAME']; game.party_B.name = cfg['PARTY_B_NAME']

def render_global_settings(cfg, game):
    st.sidebar.title("🎛️ 控制面板")

    with st.sidebar.expander("📝 即時參數設定", expanded=False):
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
        st.markdown("### 🌐 國家總體狀態")
        san_chg = (disp_san - rep['old_san']) if rep else 0
        c_color = "green" if san_chg > 0 else "red" if san_chg < 0 else "gray"
        
        emo_chg = disp_emo - rep['old_emo'] if rep else 0
        e_color = "red" if emo_chg > 0 else "green" if emo_chg < 0 else "gray"
        
        st.markdown(f"**公民素養:** {config.get_civic_index_text(disp_san)} <span style='color:{c_color}'>*({san_chg:+.1f})*</span> &nbsp;&nbsp; **選民情緒:** {config.get_emotion_text(disp_emo)} <span style='color:{e_color}'>*({emo_chg:+.1f})*</span>", unsafe_allow_html=True)
        
        crit_think = disp_san / 100.0
        emo_val = disp_emo / 100.0
        prob = max(0.05, min(0.95, crit_think * (1.0 - emo_val * 0.5)))
        st.markdown(f"**理性歸因率:** `{prob*100:.1f}%`")
        
        gdp_base = rep['old_gdp'] if rep else game.gdp
        gdp_diff = disp_gdp - gdp_base
        gdp_pct = (gdp_diff / max(1.0, gdp_base)) * 100.0
        g_color = "green" if gdp_diff > 0 else "red" if gdp_diff < 0 else "gray"
        label_gdp = "預估 GDP" if is_preview else "當前 GDP"
        st.markdown(f"**{label_gdp}:** `{disp_gdp:.1f}` <span style='color:{g_color}'>*({gdp_diff:+.1f}, {gdp_pct:+.2f}%)*</span>", unsafe_allow_html=True)

    with c2:
        st.markdown("### 💰 執行系統資源池")
        if game.year == 1 and not is_preview: st.info("首年重組，獎勵暫緩。")
        else:
            current_h_ratio = (disp_h_fund / disp_budg) * 100 if disp_budg > 0 else 50
            budg_chg = disp_budg - rep['old_budg'] if rep else 0
            b_color = "green" if budg_chg > 0 else "red" if budg_chg < 0 else "gray"
            st.markdown(f"**國家總預算池:** `{disp_budg:.1f}` <span style='color:{b_color}'>*({budg_chg:+.1f})*</span>", unsafe_allow_html=True)
            st.markdown(f"**專案獎金池:** `{disp_h_fund:.1f}` *(佔比: {current_h_ratio:.1f}%)*")

    with c3:
        fc = view_party.current_forecast
        p_acc_weight = cfg.get('PREDICT_ACCURACY_WEIGHT', 0.8)
        acc = int(((view_party.predict_ability / 10.0) * p_acc_weight) * 100)
        st.markdown(f"### 🕵️ 智庫情報分析 (準確率: {acc}%)")
        
        st.write(f"預估衰退: `{fc:.3f}`")
        eval_scenario = config.get_economic_forecast_text(fc * 100)
        st.info(eval_scenario)
        
        if rep:
            my_is_h = view_party.name == rep['h_party_name']
            past_forecast = rep.get('h_forecast') if my_is_h else rep.get('r_forecast')
            if past_forecast is not None:
                diff = abs(past_forecast - rep['real_decay'])
                eval_txt = config.get_thinktank_eval(view_party.predict_ability, diff)
                st.write(f"({cfg['CALENDAR_NAME']} 第 {game.year-1} 年 內部審計: **{eval_txt}**)")

    with c4:
        if game.phase == 1:
            st.markdown("### 📊 財務收支報告")
            if game.year == 1:
                st.write(f"可用淨資產: **{view_party.wealth:.1f}**")
            else:
                st.write(f"可用淨資產: **{view_party.wealth:.1f}**")
                
            if rep:
                my_is_h = view_party.name == rep['h_party_name']
                base = rep['h_base'] if my_is_h else rep['r_base']
                proj = rep['h_project_net'] if my_is_h else rep['r_project_net']
                extra = rep['h_extra'] if my_is_h else rep['r_extra']
                penalty = rep.get('hp_penalty', 0.0) if my_is_h else 0.0
                inv_w = rep['h_invest_wealth'] if my_is_h else rep['r_invest_wealth']
                
                real_inc_gross = base + proj + extra
                expenses = inv_w + penalty
                real_inc_net = real_inc_gross - expenses
                
                st.markdown(f"**去年淨現金流: `{real_inc_net:+.1f}`**")
                st.caption(f"*(➕ 基本 `{base:.1f}` | 專案 `{proj:.1f}` | 額外 `{extra:.1f}`)*")
                st.caption(f"*(➖ 投資 `{inv_w:.1f}` | 罰款 `{penalty:.1f}`)*")
        else:
            if is_preview:
                my_net = preview_data['h_inc'] if (view_party.name == game.h_role_party.name) else preview_data['r_inc']
                opp_net = preview_data['r_inc'] if (view_party.name == game.h_role_party.name) else preview_data['h_inc']
                
                st.markdown("### 📊 智庫預測報告")
                def fmt_roi(val): return "∞%" if val == float('inf') else f"{val:+.1f}%"
                
                st.markdown(f"我方預估淨利: **{my_net:.1f}** (投資報酬率: {fmt_roi(preview_data.get('my_roi', 0))})")
                st.markdown(f"對手預估淨利: **{opp_net:.1f}** (投資報酬率: {fmt_roi(preview_data.get('opp_roi', 0))})")
                
                my_gdp_perf = preview_data['my_perf_gdp']
                my_proj_perf = preview_data['my_perf_proj']
                my_total_perf = my_gdp_perf + my_proj_perf

                opp_gdp_perf = preview_data['opp_perf_gdp']
                opp_proj_perf = preview_data['opp_perf_proj']
                opp_total_perf = opp_gdp_perf + opp_proj_perf

                st.markdown(f"預估獲得總支持度:")
                st.markdown(f"&nbsp;&nbsp;🔹 **我方總和: `{my_total_perf:+.1f}`** *(大環境: {my_gdp_perf:+.1f} | 專案: {my_proj_perf:+.1f})*")
                st.markdown(f"&nbsp;&nbsp;🔸 **對手總和: `{opp_total_perf:+.1f}`** *(大環境: {opp_gdp_perf:+.1f} | 專案: {opp_proj_perf:+.1f})*")
                
    st.markdown("---")

def render_message_board(game):
    if st.session_state.get('news_flash'):
        st.warning(st.session_state.news_flash)
        st.session_state.news_flash = None
        
    if game.phase == 1:
        if game.year == 1: st.info("📢 **[年度通知]** 新的一年開始了。百廢待舉，請立即展開預算協商。")
        elif game.last_year_report: st.info("📢 **[年度通知]** 新的一年開始了。請展開預算協商。")
    elif game.phase == 2:
        st.info("📢 **[年度通知]** 法案已通過。請分配政黨資金用於內部升級、公關造勢與媒體戰。")

def render_party_cards(game, view_party, god_mode, is_election_year, cfg):
    st.header("👤 政黨狀態總覽")
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
            crown_str = cfg.get('CROWN_WINNER', '👑 當權') if is_winner else cfg.get('CROWN_LOSER', '🎯 候選')
            logo = config.get_party_logo(party.name)
            
            eye = "👁️ " if party.name == view_party.name else ""
            st.markdown(f"## {eye}{logo} {party.name} {crown_str}")
            st.markdown(f"#### {role_badge}")

            if party.name == view_party.name:
                st.markdown(f"### 💰 **政黨資金:** `${party.wealth:.1f}`")
            else:
                rng = random.Random(f"wealth_{party.name}_{game.year}")
                opp_stl = party.stealth_ability / 10.0
                my_inv_raw = view_party.investigate_ability / 10.0
                err_margin = max(0.0, 1.0 + opp_stl - my_inv_raw) * cfg.get('OBS_ERR_BASE', 0.7)
                blur = err_margin if not god_mode else 0.0
                est_wealth = party.wealth * (1 + rng.uniform(-blur, blur))
                st.markdown(f"### 💰 **政黨資金:** `${est_wealth:.1f}` *(預估)*")

            if is_election_year or god_mode: 
                disp_sup = f"{party.support:.1f}% 🏆(勝選!)" if is_winner else f"{party.support:.1f}% 💀(敗選)"
            else:
                if party.latest_poll is not None:
                    best_type = None
                    for pt in ['Large', 'Medium', 'Small']:
                        if len(party.poll_history[pt]) > 0: best_type = pt; break
                    if best_type:
                        avg = sum(party.poll_history[best_type]) / len(party.poll_history[best_type])
                        count = len(party.poll_history[best_type])
                        disp_sup = f"{party.latest_poll:.1f}% (最新) ({count}x {best_type} 平均: {avg:.1f}%)"
                    else: disp_sup = f"{party.latest_poll:.1f}% (最新)"
                else:
                    disp_sup = "??? (需要民調)"
            
            st.markdown(f"### 📊 支持度: **{disp_sup}**")
            
            if party.name == view_party.name and not is_election_year:
                b1, b2, b3 = st.columns(3)
                if b1.button("小型民調 ($5)", key=f"p1_{party.name}"): engine.execute_poll(game, view_party, 5); st.rerun()
                if b2.button("中型民調 ($10)", key=f"p2_{party.name}"): engine.execute_poll(game, view_party, 10); st.rerun()
                if b3.button("大型民調 ($20)", key=f"p3_{party.name}"): engine.execute_poll(game, view_party, 20); st.rerun()

def get_observed_abilities(viewer, target, game, cfg):
    if viewer.name == target.name or st.session_state.get('god_mode'):
        return {
            'predict': target.predict_ability,
            'investigate': target.investigate_ability,
            'media': target.media_ability,
            'stealth': target.stealth_ability,
            'build': target.build_ability,
            'edu': getattr(target, 'edu_ability', cfg.get('EDU_ABILITY_DEFAULT', 3.0))
        }
    
    opp_stl = target.stealth_ability / 10.0
    i_acc_weight = cfg.get('INVESTIGATE_ACCURACY_WEIGHT', 0.8)
    my_inv = (viewer.investigate_ability / 10.0) * i_acc_weight
    
    err_margin = max(0.0, 1.0 + opp_stl - my_inv) * cfg.get('OBS_ERR_BASE', 0.7)
    
    rng = random.Random(f"intel_{target.name}_{game.year}")
    def get_obs(v):
        if err_margin == 0.0: return v
        true_cost = (2**v - 1) * 50
        obs_cost = max(0.0, true_cost * (1 + rng.uniform(-err_margin, err_margin)))
        return math.log2(obs_cost / 50.0 + 1)
        
    return {
        'predict': get_obs(target.predict_ability),
        'investigate': get_obs(target.investigate_ability),
        'media': get_obs(target.media_ability),
        'stealth': get_obs(target.stealth_ability),
        'build': get_obs(target.build_ability),
        'edu': get_obs(getattr(target, 'edu_ability', cfg.get('EDU_ABILITY_DEFAULT', 3.0)))
    }

def render_sidebar_intel_audit(game, view_party, cfg):
    opp = game.party_B if view_party.name == game.party_A.name else game.party_A
    st.markdown("---")
    st.title("🕵️ 情報調查 - 對手數值")
    
    opp_stl = opp.stealth_ability / 10.0
    i_acc_weight = cfg.get('INVESTIGATE_ACCURACY_WEIGHT', 0.8)
    my_inv = (view_party.investigate_ability / 10.0) * i_acc_weight
    
    err_margin = max(0.0, 1.0 + opp_stl - my_inv) * cfg.get('OBS_ERR_BASE', 0.7)
    acc = max(0, min(100, int((1.0 - err_margin) * 100)))
    
    st.progress(acc / 100.0, text=f"觀測準確率: {acc}%")
    
    obs_abis = get_observed_abilities(view_party, opp, game, cfg)
    
    st.write(f"智庫預測處: {obs_abis['predict']*10:.1f}% | 情報調查處: {obs_abis['investigate']*10:.1f}%")
    st.write(f"黨媒公關處: {obs_abis['media']*10:.1f}% | 反情報與隱蔽處: {obs_abis['stealth']*10:.1f}%")
    st.write(f"工程建設處: {obs_abis['build']*10:.1f}% | 教育處: {obs_abis['edu']*10:.1f}%")
    
    est_unit_cost = formulas.calc_unit_cost(cfg, game.gdp, obs_abis['build'], view_party.current_forecast)
    eval_txt = config.get_intel_market_eval(est_unit_cost)
    
    inflation_rate = max(0.0, (game.gdp - cfg.get('CURRENT_GDP', 5000.0)) / cfg.get('GDP_INFLATION_DIVISOR', 10000.0)) * 100.0
    
    st.write(f"**工程建設估值**: {eval_txt}")
    st.write(f"*(預估單位產出成本: `{est_unit_cost:.2f}` )*")

    st.markdown("---")
    st.title("🧾 內部部門審計")
    st.write(f"**當前通膨指數:** `{inflation_rate:.1f}%\`")
    total_maint = (view_party.predict_ability + view_party.investigate_ability + view_party.media_ability + view_party.stealth_ability + view_party.build_ability + view_party.edu_ability) * 1.5
    
    st.write(f"智庫預測處: {view_party.predict_ability*10:.0f} | 情報調查處: {view_party.investigate_ability*10:.0f}")
    st.write(f"黨媒公關處: {view_party.media_ability*10:.0f} | 反情報與隱蔽處: {view_party.stealth_ability*10:.0f}")
    st.write(f"工程建設處: {view_party.build_ability*10:.0f} | 教育處: {view_party.edu_ability*10:.0f}")
    st.write(f"**(明年預估維護費: -{total_maint:.1f} EV)**")
