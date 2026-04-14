# ==========================================
# ui_core.py
# 負責 政府 OS 視覺核心儀表板
# ==========================================
import streamlit as st
import random
import math
import config
import formulas
import engine
import i18n
t = i18n.t

def render_dashboard(game, view_party, cfg, is_preview=False, preview_data=None):
    rep = game.last_year_report
    st.markdown("### 🏛️ [國家發展委員會] 總體經濟與社會指標監控")
    
    disp_gdp = preview_data['gdp'] if is_preview and preview_data else game.gdp
    disp_san = preview_data['san'] if is_preview and preview_data else game.sanity
    disp_emo = preview_data['emo'] if is_preview and preview_data else game.emotion
    disp_h_fund = preview_data['h_fund'] if is_preview and preview_data else game.h_fund
    disp_budg = preview_data['budg'] if is_preview and preview_data else game.total_budget
    
    with st.container(border=True):
        m1, m2, m3, m4 = st.columns(4)
        
        # 1. 社會指標
        with m1:
            san_chg = (disp_san - rep['old_san']) if rep else 0
            st.metric(label=f"🧠 資訊辨識度 ({config.get_civic_index_text(disp_san)})", value=f"{disp_san:.1f}", delta=f"{san_chg:+.1f}")
            emo_chg = (disp_emo - rep['old_emo']) if rep else 0
            st.metric(label=f"🔥 社會情緒 ({config.get_emotion_text(disp_emo)})", value=f"{disp_emo:.1f}", delta=f"{emo_chg:+.1f}", delta_color="inverse")
            
        # 2. 經濟指標
        with m2:
            gdp_base = rep['old_gdp'] if rep else game.gdp
            gdp_diff = disp_gdp - gdp_base
            gdp_pct = (gdp_diff / max(1.0, gdp_base)) * 100.0
            label_gdp = "預估 GDP" if is_preview else "當前 GDP"
            st.metric(label=f"💵 {label_gdp}", value=f"{disp_gdp:.1f}", delta=f"{gdp_diff:+.1f} ({gdp_pct:+.2f}%)")
            
            budg_chg = disp_budg - rep['old_budg'] if rep else 0
            current_h_ratio = (disp_h_fund / disp_budg) * 100 if disp_budg > 0 else 50
            st.metric(label="💰 國庫總預算池", value=f"{disp_budg:.1f}", delta=f"{budg_chg:+.1f}")
            st.caption(f"*(專案獎勵基金佔比: {current_h_ratio:.1f}%)*")

        # 3. 智庫情報
        with m3:
            fc = view_party.current_forecast
            acc = min(100, max(0, int((1.0 - (cfg.get('OBS_ERR_BASE', 0.4) / (view_party.predict_ability/3.0))) * 100))) 
            st.markdown(f"**👁️ 國家智庫 (準確率 ~{acc}%)**")
            conv_rate = cfg.get('GDP_CONVERSION_RATE', 0.2)
            gdp_loss = game.gdp * (fc * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
            req_infra_to_balance = gdp_loss / conv_rate
            st.write(f"📉 預估衰退值: `{fc:.3f}`")
            st.write(f"🏗️ 需平抑建設量: `{req_infra_to_balance:.1f}`")
            
            if rep:
                my_is_h = view_party.name == rep['h_party_name']
                past_forecast = rep.get('h_forecast') if my_is_h else rep.get('r_forecast')
                if past_forecast is not None:
                    diff = abs(past_forecast - rep['real_decay'])
                    st.caption(f"去年度預測誤差: `{diff:.3f}`")

        # 4. 財報與黨產
        with m4:
            if not is_preview:
                st.markdown("**🧾 黨部可用資金**")
                total_maint = (
                    formulas.get_ability_maintenance(view_party.predict_ability, cfg, False, view_party.build_ability) +
                    formulas.get_ability_maintenance(view_party.investigate_ability, cfg, False, view_party.build_ability) +
                    formulas.get_ability_maintenance(view_party.media_ability, cfg, False, view_party.build_ability) +
                    formulas.get_ability_maintenance(view_party.stealth_ability, cfg, False, view_party.build_ability) +
                    formulas.get_ability_maintenance(view_party.build_ability, cfg, True, view_party.build_ability)
                )
                st.metric(label="黨產淨值", value=f"${view_party.wealth:.1f}", delta=f"維護費 -{total_maint:.1f}", delta_color="inverse")
            else:
                st.markdown("**📊 智庫行動評估報告**")
                my_net = preview_data['h_inc'] if view_party.name == game.h_role_party.name else preview_data['r_inc']
                st.write(f"🟢 預估總收益: **{my_net:.1f}**")
                st.caption(f"預期政績: 我方 **{preview_data['my_perf']:+.1f}**")

def sync_party_names(game, cfg):
    game.party_A.name = cfg['PARTY_A_NAME']; game.party_B.name = cfg['PARTY_B_NAME']

def render_global_settings(cfg, game):
    st.sidebar.title(t("🎛️ 控制台"))
    lang = st.session_state.get('lang', 'EN')
    btn_text = "🌐 切換至中文" if lang == 'EN' else "🌐 Switch to English"
    if st.sidebar.button(btn_text, use_container_width=True):
        st.session_state.lang = 'ZH' if lang == 'EN' else 'EN'; st.rerun()
    with st.sidebar.expander(t("📝 參數調整(即時)"), expanded=False):
        trans = config.get_config_translations()
        for key, default_val in config.DEFAULT_CONFIG.items():
            label = trans.get(key, key)
            if 'COLOR' in key: cfg[key] = st.color_picker(label, value=cfg[key], key=f"cfg_{key}")
            elif isinstance(default_val, float): cfg[key] = st.number_input(label, value=float(cfg[key]), step=0.1, key=f"cfg_{key}")
            elif isinstance(default_val, int): cfg[key] = st.number_input(label, value=int(cfg[key]), step=1, key=f"cfg_{key}")
            elif isinstance(default_val, str): cfg[key] = st.text_input(label, value=str(cfg[key]), key=f"cfg_{key}")

def render_message_board(game):
    if st.session_state.get('news_flash'):
        st.warning(st.session_state.news_flash); st.session_state.news_flash = None
    if game.phase == 1:
        st.info("📢 **【年度通報】** 請擬定預算草案或展開最後通牒協商。")
    elif game.phase == 2:
        st.info("📢 **【年度通報】** 法案三讀通過，進入資金分配與機構升級。")

def render_party_cards(game, view_party, god_mode, is_election_year, cfg):
    st.header(t("👤 執政聯盟概況", "👤 Coalition Status"))
    c1, c2 = st.columns(2)
    opp = game.party_B if view_party.name == game.party_A.name else game.party_A
    for col, party in zip([c1, c2], [view_party, opp]):
        with col:
            with st.container(border=True):
                role = "🛡️ [執行系統]" if game.h_role_party.name == party.name else "⚖️ [監管系統]"
                is_ruling = game.ruling_party.name == party.name
                crown = "👑" if is_ruling else "🎯"
                st.markdown(f"## {crown} {party.name}")
                st.markdown(f"#### {role}")
                if party.name == view_party.name:
                    st.write(f"💰 黨產: `${party.wealth:.1f}`")
                else:
                    rng = random.Random(f"wealth_{party.name}_{game.year}")
                    blur = max(0.1, (1.0 - view_party.investigate_ability/10.0)) * 0.5
                    est = party.wealth * (1 + rng.uniform(-blur, blur))
                    st.write(f"💰 黨產: `${est:.1f}` *(智庫預估)*")
                st.write(f"📊 支持度: **{party.support:.1f}%**")
                
                if party.name == view_party.name and not is_election_year:
                    b1, b2, b3 = st.columns(3)
                    if b1.button(t("小民調 ($5)"), key=f"p1_{party.name}"): engine.execute_poll(game, view_party, 5); st.rerun()
                    if b2.button(t("中民調 ($10)"), key=f"p2_{party.name}"): engine.execute_poll(game, view_party, 10); st.rerun()
                    if b3.button(t("大民調 ($20)", "Big Poll ($20)"), key=f"p3_{party.name}"): engine.execute_poll(game, view_party, 20); st.rerun()

def get_observed_abilities(viewer, target, game, cfg):
    if viewer.name == target.name or st.session_state.get('god_mode'):
        return {'predict': target.predict_ability, 'investigate': target.investigate_ability, 'media': target.media_ability, 'stealth': target.stealth_ability, 'build': target.build_ability}
    opp_stl = target.stealth_ability / 10.0
    my_inv = viewer.investigate_ability / 10.0
    err_margin = max(0.0, 1.0 + opp_stl - my_inv) * cfg.get('OBS_ERR_BASE', 0.7)
    rng = random.Random(f"intel_{target.name}_{game.year}")
    def get_obs(v):
        if err_margin == 0.0: return v
        true_amt = (2**v - 1) * 50
        obs_amt = max(0.0, true_amt * (1 + rng.uniform(-err_margin, err_margin)))
        return math.log2(obs_amt / 50.0 + 1)
    return {k: get_obs(v) for k, v in {'predict': target.predict_ability, 'investigate': target.investigate_ability, 'media': target.media_ability, 'stealth': target.stealth_ability, 'build': target.build_ability}.items()}

def render_sidebar_intel_audit(game, view_party, cfg):
    opp = game.party_B if view_party.name == game.party_A.name else game.party_A
    st.markdown("---")
    st.title(t("🕵️ 情報處報告", "🕵️ Intel Report"))
    obs = get_observed_abilities(view_party, opp, game, cfg)
    st.write(f"對手機構概況:")
    st.progress(view_party.investigate_ability/10.0, text=f"偵查深度: {view_party.investigate_ability*10:.0f}%")
    st.write(f"智庫: {obs['predict']*10:.1f}% | 工程: {obs['build']*10:.1f}%")

def ability_slider(label, key, current_val, wealth, cfg, build_ability=0.0, is_build=False):
    a_c = (2**current_val - 1) * 50.0
    max_dec = cfg.get('DECAY_AMOUNT_BUILD', 500.0) if is_build else cfg.get('DECAY_AMOUNT_DEFAULT', 1500.0)
    a_base = max(0.0, a_c - max_dec)
    min_val = math.log2(a_base / 50.0 + 1)
    t_pct = st.slider(f"{label}", float(min_val*10), 100.0, float(current_val*10), 0.1, key=key)
    t_val = t_pct / 10.0
    cost = formulas.calculate_upgrade_cost(current_val, t_val, cfg, is_build, build_ability)
    maint = formulas.get_ability_maintenance(current_val, cfg, is_build, build_ability)
    if t_val > current_val: st.caption(f"📈 擴編費: ${cost:.1f}")
    elif t_val < current_val: st.caption(f"📉 萎縮中 (省下 ${maint-cost:.1f})")
    else: st.caption(f"🛡️ 穩定維持 (費 ${cost:.1f})")
    return t_val, cost
