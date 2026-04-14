# ==========================================
# ui_core.py
# 負責共用 UI 渲染、圖表繪製、標準化組件
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
        c_color = "green" if san_chg > 0 else "red" if san_chg < 0 else "gray"
        st.markdown(f"**{t('資訊辨識')}:** `{config.get_civic_index_text(disp_san)}` <span style='color:{c_color}'>*({san_chg:+.1f})*</span>", unsafe_allow_html=True)
        
        emo_chg = disp_emo - rep['old_emo'] if rep else 0
        e_color = "red" if emo_chg > 0 else "green" if emo_chg < 0 else "gray"
        st.markdown(f"**{t('選民情緒')}:** `{config.get_emotion_text(disp_emo)}` <span style='color:{e_color}'>*({emo_chg:+.1f})*</span>", unsafe_allow_html=True)
        
        gdp_base = rep['old_gdp'] if rep else game.gdp
        gdp_diff = disp_gdp - gdp_base
        gdp_pct = (gdp_diff / max(1.0, gdp_base)) * 100.0
        g_color = "green" if gdp_diff > 0 else "red" if gdp_diff < 0 else "gray"
        label_gdp = t("預估 GDP") if is_preview else t("當前 GDP")
        st.markdown(f"**{label_gdp}:** `{disp_gdp:.1f}` <span style='color:{g_color}'>*({gdp_diff:+.1f}, {gdp_pct:+.2f}%)*</span>", unsafe_allow_html=True)

    with c2:
        st.markdown(t("### 💰 執行系統資源"))
        if game.year == 1 and not is_preview: st.info("首年重整中，尚未配發獎勵。")
        else:
            current_h_ratio = (disp_h_fund / disp_budg) * 100 if disp_budg > 0 else 50
            budg_chg = disp_budg - rep['old_budg'] if rep else 0
            b_color = "green" if budg_chg > 0 else "red" if budg_chg < 0 else "gray"
            st.markdown(f"**{t('總預算池')}:** `{disp_budg:.1f}` <span style='color:{b_color}'>*({budg_chg:+.1f})*</span>", unsafe_allow_html=True)
            st.markdown(f"**{t('獎勵基金')}:** `{disp_h_fund:.1f}` *({t('佔比')}: {current_h_ratio:.1f}%)*")

    with c3:
        fc = view_party.current_forecast
        acc = min(100, max(0, int((1.0 - (cfg.get('OBS_ERR_BASE', 0.4) / (view_party.predict_ability/3.0))) * 100))) 
        st.markdown(f"### 🕵️ {t('智庫')} {t('準確度')}: ~{acc}%")
        
        conv_rate = cfg.get('GDP_CONVERSION_RATE', 0.2)
        gdp_loss = game.gdp * (fc * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
        req_infra_to_balance = gdp_loss / conv_rate
        
        st.write(f"預估衰退值: `{fc:.3f}`")
        st.write(f"平抑衰退所需建設量: `{req_infra_to_balance:.1f}`")
        
        if rep:
            my_is_h = view_party.name == rep['h_party_name']
            past_forecast = rep.get('h_forecast') if my_is_h else rep.get('r_forecast')
            if past_forecast is not None:
                diff = abs(past_forecast - rep['real_decay'])
                eval_txt = config.get_thinktank_eval(view_party.predict_ability, diff)
                st.write(f"({cfg['CALENDAR_NAME']} {game.year-1} 內部檢討: **{eval_txt}**)")
        else:
            st.write("(尚無去年歷史資料以供檢討)")

    with c4:
        if game.phase == 1:
            st.markdown(t("### 📊 財報"))
            total_maint = (
                formulas.get_ability_maintenance(view_party.predict_ability, cfg, False, view_party.build_ability) +
                formulas.get_ability_maintenance(view_party.investigate_ability, cfg, False, view_party.build_ability) +
                formulas.get_ability_maintenance(view_party.media_ability, cfg, False, view_party.build_ability) +
                formulas.get_ability_maintenance(view_party.stealth_ability, cfg, False, view_party.build_ability) +
                formulas.get_ability_maintenance(view_party.build_ability, cfg, True, view_party.build_ability)
            )
            if game.year == 1:
                st.write(f"{t('可用淨資產')}: **{view_party.wealth:.1f}** ({view_party.wealth:.1f} - 0.0)")
            else:
                st.write(f"{t('可用淨資產')}: **{view_party.wealth:.1f}** ({(view_party.wealth + total_maint):.1f} - {total_maint:.1f})")
                
            if rep:
                my_is_h = view_party.name == rep['h_party_name']
                real_inc = rep['h_inc'] if my_is_h else rep['r_inc']
                est_inc = rep.get('est_h_inc', 0.0) if my_is_h else rep.get('est_r_inc', 0.0)
                st.write(f"{t('淨利')}: {t('真')}:**{real_inc:.1f}** ({t('去年估')}:{est_inc:.1f})")
        else:
            if is_preview:
                my_is_h = view_party.name == game.h_role_party.name
                my_net = preview_data['h_inc'] if my_is_h else preview_data['r_inc']
                opp_net = preview_data['r_inc'] if my_is_h else preview_data['h_inc']
                
                st.markdown(t("### 📊 智庫評估報告"))
                st.markdown(f"{t('我方預估總收益')}: **{my_net:.1f}**")
                st.markdown(f"{t('對方預估總收益')}: **{opp_net:.1f}**")
                
                st.markdown(f"{t('預期政績 (未經媒體)')}: 我方 **{preview_data['my_perf']:+.1f}** / 對方 **{preview_data['opp_perf']:+.1f}**")
                if 'project_perf' in preview_data:
                    st.caption(f"*(包含執行方當前貪污設定下的履約政績: `{preview_data['project_perf']:+.1f}`)*")
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
    st.header(t("👤 兩黨概況"))
    c1, c2 = st.columns(2)
    opp = game.party_B if view_party.name == game.party_A.name else game.party_A
    
    st.markdown(f"""
    <style>
    div[data-testid="column"]:nth-child(1) {{ background-color: {cfg['PARTY_A_COLOR']}1A; padding: 15px; border-radius: 10px; border-left: 5px solid {cfg['PARTY_A_COLOR']}; }}
    div[data-testid="column"]:nth-child(2) {{ background-color: {cfg['PARTY_B_COLOR']}1A; padding: 15px; border-radius: 10px; border-left: 5px solid {cfg['PARTY_B_COLOR']}; }}
    </style>
    """, unsafe_allow_html=True)

    a_pts = sum([x['val'] * (1.0 - (x['age']/7.0)) for x in game.support_queues[game.party_A.name]['perf']]) + \
            sum([x['val'] * (1.0 - (x['age']/3.0)) for x in game.support_queues[game.party_A.name]['camp']]) + 5000.0
    b_pts = sum([x['val'] * (1.0 - (x['age']/7.0)) for x in game.support_queues[game.party_B.name]['perf']]) + \
            sum([x['val'] * (1.0 - (x['age']/3.0)) for x in game.support_queues[game.party_B.name]['camp']]) + 5000.0

    for col, party, pts in zip([c1, c2], [view_party, opp], [a_pts if view_party.name == game.party_A.name else b_pts, b_pts if view_party.name == game.party_A.name else a_pts]):
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
                st.markdown(f"### 💰 **{t('黨產資金')}:** `${party.wealth:.1f}`")
            else:
                rng = random.Random(f"wealth_{party.name}_{game.year}")
                opp_stl = party.stealth_ability / 10.0
                my_inv = view_party.investigate_ability / 10.0
                err_margin = max(0.0, 1.0 + opp_stl - my_inv) * cfg.get('OBS_ERR_BASE', 0.7)
                blur = err_margin if not god_mode else 0.0
                est_wealth = party.wealth * (1 + rng.uniform(-blur, blur))
                st.markdown(f"### 💰 **{t('黨產資金')}:** `${est_wealth:.1f}` *({t('預估')})*")

            if is_election_year or god_mode: 
                disp_sup = f"{party.support:.1f}% 🏆(當選!)" if is_winner else f"{party.support:.1f}% 💀(落選)"
            else:
                if party.latest_poll is not None:
                    best_type = None
                    for pt in ['大型', '中型', '小型']:
                        if len(party.poll_history[pt]) > 0: best_type = pt; break
                    if best_type:
                        avg = sum(party.poll_history[best_type]) / len(party.poll_history[best_type])
                        count = len(party.poll_history[best_type])
                        disp_sup = f"{party.latest_poll:.1f}%(最新民調) ({count}次{best_type}平均: {avg:.1f}%)"
                    else: disp_sup = f"{party.latest_poll:.1f}%(最新民調)"
                else:
                    disp_sup = "??? (需作民調)"
            
            st.markdown(f"### 📊 支持量: `{pts:.1f} 點` (佔比: {disp_sup})")
            
            if party.name == view_party.name and not is_election_year:
                b1, b2, b3 = st.columns(3)
                if b1.button(t("小民調 ($5)"), key=f"p1_{party.name}"): engine.execute_poll(game, view_party, 5); st.rerun()
                if b2.button(t("中民調 ($10)"), key=f"p2_{party.name}"): engine.execute_poll(game, view_party, 10); st.rerun()
                if b3.button(t("大民調 ($20)", "Big Poll ($20)"), key=f"p3_{party.name}"): engine.execute_poll(game, view_party, 20); st.rerun()

def get_observed_abilities(viewer, target, game, cfg):
    if viewer.name == target.name or st.session_state.get('god_mode'):
        return {
            'predict': target.predict_ability,
            'investigate': target.investigate_ability,
            'media': target.media_ability,
            'stealth': target.stealth_ability,
            'build': target.build_ability
        }
    
    opp_stl = target.stealth_ability / 10.0
    my_inv = viewer.investigate_ability / 10.0
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
        'build': get_obs(target.build_ability)
    }

def render_sidebar_intel_audit(game, view_party, cfg):
    opp = game.party_B if view_party.name == game.party_A.name else game.party_A
    st.markdown("---")
    st.title(t("🕵️ 情報處 - 對手機構指標"))
    
    opp_stl = opp.stealth_ability / 10.0
    my_inv = view_party.investigate_ability / 10.0
    err_margin = max(0.0, 1.0 + opp_stl - my_inv) * cfg.get('OBS_ERR_BASE', 0.7)
    acc = max(0, min(100, int((1.0 - err_margin) * 100)))
    
    st.progress(acc / 100.0, text=f"{t('準確度')}: {acc}%")
    
    obs_abis = get_observed_abilities(view_party, opp, game, cfg)
    
    st.write(f"{t('智庫')}: {obs_abis['predict']*10:.1f}% | {t('情報處')}: {obs_abis['investigate']*10:.1f}%")
    st.write(f"{t('黨媒')}: {obs_abis['media']*10:.1f}% | {t('反情報處')}: {obs_abis['stealth']*10:.1f}%")
    
    my_inv_pct = view_party.investigate_ability / 10.0
    r_bonus = cfg['R_INV_BONUS'] if view_party.name == game.r_role_party.name else 1.0
    obs_stl_pct = obs_abis['stealth'] / 10.0
    
    catch_mult = max(0.1, (my_inv_pct * r_bonus) - obs_stl_pct + 1.0)
    
    def get_catch_prob(c_pct, base_rate):
        rolls = c_pct * catch_mult
        return (1.0 - (1.0 - base_rate)**rolls) * 100.0
        
    catch_10 = get_catch_prob(10.0, cfg['CATCH_RATE_PER_PERCENT'])
    catch_30 = get_catch_prob(30.0, cfg['CATCH_RATE_PER_PERCENT'])
    
    st.write(f"**{t('防貪污能力估算')}**: 偵測擲骰倍率 `{catch_mult:.2f}x`")
    st.caption(f"*(若對手貪污 10% $\\rightarrow$ 查獲率約 `{catch_10:.1f}%` | 貪 30% $\\rightarrow$ `{catch_30:.1f}%`)*")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.write(f"{t('工程處')}: {obs_abis['build']*10:.1f}%")
    
    est_unit_cost = formulas.calc_unit_cost(cfg, game.gdp, obs_abis['build'], view_party.current_forecast)
    eval_txt = config.get_intel_market_eval(est_unit_cost)
    
    inflation_rate = max(0.0, (game.gdp - cfg.get('CURRENT_GDP', 5000.0)) / cfg.get('GDP_INFLATION_DIVISOR', 10000.0)) * 100.0
    
    st.write(f"**{t('建設估價')}**: {eval_txt}")
    st.write(f"*(預估單位產出成本: `{est_unit_cost:.2f}` / 包含當前通膨 `{inflation_rate:.1f}%`)*")

    st.markdown("---")
    st.title(t("🧾 審計處 - 內部部門報告"))
    st.write(f"**當前通膨指數:** `{inflation_rate:.1f}%`")
    total_maint = (
        formulas.get_ability_maintenance(view_party.predict_ability, cfg, False, view_party.build_ability) +
        formulas.get_ability_maintenance(view_party.investigate_ability, cfg, False, view_party.build_ability) +
        formulas.get_ability_maintenance(view_party.media_ability, cfg, False, view_party.build_ability) +
        formulas.get_ability_maintenance(view_party.stealth_ability, cfg, False, view_party.build_ability) +
        formulas.get_ability_maintenance(view_party.build_ability, cfg, True, view_party.build_ability)
    )
    st.write(f"{t('智庫')}: {view_party.predict_ability*10:.1f}% | {t('情報處')}: {view_party.investigate_ability*10:.1f}%")
    st.write(f"{t('黨媒')}: {view_party.media_ability*10:.1f}% | {t('反情報處')}: {view_party.stealth_ability*10:.1f}%")
    st.write(f"{t('工程處')}: {view_party.build_ability*10:.1f}%")
    st.write(f"**(依據當前機構投資，明年維護費估算: -${total_maint:.1f})**")

def ability_slider(label, key, current_val, wealth, cfg, build_ability=0.0, is_build=False):
    a_c = (2**current_val - 1) * 50.0
    max_decay = cfg.get('DECAY_AMOUNT_BUILD', 500.0) if is_build else cfg.get('DECAY_AMOUNT_DEFAULT', 1500.0)
    
    a_base = max(0.0, a_c - max_decay)
    min_val = math.log2(a_base / 50.0 + 1)
    
    current_pct = current_val * 10.0
    min_pct = min_val * 10.0
    
    t_pct = st.slider(f"{label}", float(min_pct), 100.0, float(current_pct), 0.1, key=key)
    t_val = t_pct / 10.0
    
    cost = formulas.calculate_upgrade_cost(current_val, t_val, cfg, is_build, build_ability)
    maint = formulas.get_ability_maintenance(current_val, cfg, is_build, build_ability)
    
    if t_val > current_val: 
        st.caption(f"📈 <span style='color:orange'>**{t('擴編總花費')}**: ${cost:.1f}</span> | 能力: {current_pct:.1f}% ➔ {t_pct:.1f}%", unsafe_allow_html=True)
    elif t_val < current_val: 
        st.caption(f"📉 <span style='color:blue'>**{t('放任萎縮 (節省經費)')}**</span> | 能力: {current_pct:.1f}% ➔ {t_pct:.1f}% | 花費: ${cost:.1f} *(省下 ${maint - cost:.1f})*", unsafe_allow_html=True)
    else: 
        st.caption(f"🛡️ {t('穩定維持')} | 能力: {current_pct:.1f}% | {t('維護費')} ${cost:.1f}")
        
    return t_val, cost
