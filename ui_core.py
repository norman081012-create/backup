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
        
        equiv_loss = game.gdp * (fc * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
        st.write(f"預估衰退值: `{fc:.3f}`")
        st.write(f"預估建設損失: `{equiv_loss:.1f}`")
        
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
            total_maint = sum([formulas.get_ability_maintenance(a, cfg) for a in [view_party.build_ability, view_party.investigate_ability, view_party.media_ability, view_party.predict_ability, view_party.stealth_ability]])
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
                
                sup_c = "green" if preview_data['my_sup_shift'] > 0 else "red"
                st.markdown(f"{t('新增支持量預估')}: <span style='color:{sup_c}'>**{preview_data['my_sup_shift']:+.1f} 點**</span>", unsafe_allow_html=True)
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
    total_maint = sum([formulas.get_ability_maintenance(a, cfg) for a in [view_party.build_ability, view_party.investigate_ability, view_party.media_ability, view_party.predict_ability, view_party.stealth_ability]])
    st.write(f"{t('智庫')}: {view_party.predict_ability*10:.1f}% | {t('情報處')}: {view_party.investigate_ability*10:.1f}%")
    st.write(f"{t('黨媒')}: {view_party.media_ability*10:.1f}% | {t('反情報處')}: {view_party.stealth_ability*10:.1f}%")
    st.write(f"{t('工程處')}: {view_party.build_ability*10:.1f}%")
    st.write(f"**(依據當前機構投資，明年維護費估算: -${total_maint:.1f})**")

def render_proposal_component(title, plan, game, view_party, cfg):
    st.markdown(f"#### {title}")
    
    c_tog1, c_tog2 = st.columns(2)
    use_claimed = c_tog1.toggle(t("切換以 公告數字 試算 (預設為智庫/真實預估)"), False, key=f"tg_{title}_{plan.get('author', 'sys')}")
    simulate_swap = c_tog2.toggle(t("模擬如果發生倒閣換位 (依據新定位試算)"), False, key=f"sim_sw_{title}_{plan.get('author', 'sys')}")
    
    c1, c2 = st.columns(2)
    
    if simulate_swap:
        sim_h_party = game.r_role_party
        sim_r_party = game.h_role_party
        sim_ruling_name = game.party_B.name if game.ruling_party.name == game.party_A.name else game.party_A.name
        my_is_h = (view_party.name == sim_h_party.name)
    else:
        sim_h_party = game.h_role_party
        sim_r_party = game.r_role_party
        sim_ruling_name = game.ruling_party.name
        my_is_h = (view_party.name == sim_h_party.name)

    obs_abis = get_observed_abilities(view_party, sim_h_party, game, cfg)
    obs_bld = obs_abis['build']

    if use_claimed:
        eval_decay = plan.get('claimed_decay', 0.0)
        override_cost = plan.get('claimed_cost', 1.0)
    else:
        eval_decay = view_party.current_forecast
        override_cost = round(formulas.calc_unit_cost(cfg, game.gdp, obs_bld, eval_decay), 2)

    # [修正] 將 r_pays 傳入 calc_economy 確保引擎能認知到這筆補貼
    res = formulas.calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], sim_h_party.build_ability, eval_decay, override_unit_cost=override_cost, r_pays=plan['r_pays'])
    
    eval_req_cost = res['req_cost']          
    eval_unit_cost = res.get('unit_cost', 1.0)
    eval_r_pays = plan['r_pays']             
    eval_h_pays = eval_req_cost - eval_r_pays 
    
    with c1:
        equiv_loss = game.gdp * (plan.get('claimed_decay', 0.0) * cfg.get('DECAY_WEIGHT_MULT', 0.05) + cfg.get('BASE_DECAY_RATE', 0.0))
        st.write(f"**{t('公告衰退率(0~1)')}:** {plan.get('claimed_decay', 0.0):.3f}")
        st.write(f"**(相當於 {equiv_loss:.1f} 建設損失)**")
        st.write(f"**{t('計畫達成獎勵金')}:** {plan['proj_fund']:.1f} | **{t('計畫總效益')}:** {plan['bid_cost']:.1f}")
        
        if simulate_swap:
            st.info(f"🔧 **{t('模擬執行方出資')}:** {t('總額')} {eval_req_cost:.1f} ({t('監管出資')}: {eval_r_pays:.1f} | {t('執行出資')}: {eval_h_pays:.1f})")
        else:
            st.write(f"**{t('出資總額')}:** {eval_req_cost:.1f} ({t('監管出資')}: {eval_r_pays:.1f} | {t('執行出資')}: {eval_h_pays:.1f})")
            
    with c2:
        h_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if sim_ruling_name == sim_h_party.name else 0))
        r_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if sim_ruling_name == sim_r_party.name else 0))
        
        # [修正] 專案淨利潤：嚴格排除底薪
        h_project_profit = res['h_project_profit']
        r_project_profit = res['payout_r'] - eval_r_pays
        
        # [修正] 計算真正的 ROI：專案淨利 / 各自承擔的出資額
        o_h_roi = (h_project_profit / float(eval_h_pays)) * 100.0 if eval_h_pays > 0 else float('inf')
        o_r_roi = (r_project_profit / float(eval_r_pays)) * 100.0 if eval_r_pays > 0 else float('inf')
        
        my_roi = o_h_roi if my_is_h else o_r_roi
        opp_roi = o_r_roi if my_is_h else o_h_roi
        
        # 計算加上底薪後的整體總淨收（為了讓玩家清楚年終會拿到多少）
        my_net = h_base + h_project_profit if my_is_h else r_base + r_project_profit
        opp_net = r_base + r_project_profit if my_is_h else h_base + h_project_profit
        
        ha_dummy = game.h_role_party.last_acts if not simulate_swap else game.r_role_party.last_acts
        ra_dummy = game.r_role_party.last_acts if not simulate_swap else game.h_role_party.last_acts
        
        shift_preview = formulas.calc_support_amounts(
            cfg, sim_h_party, sim_r_party, sim_ruling_name,
            res['est_gdp'], game.gdp, 
            ha_dummy, ra_dummy, 
            plan.get('claimed_decay', 0.0), game.sanity, game.emotion, plan['bid_cost'], res['c_net'], eval_decay
        )
        my_shifts = shift_preview[view_party.name]
        my_sup = my_shifts['perf'] + my_shifts['camp'] + my_shifts['backlash']
        
        o_gdp_pct = ((res['est_gdp'] - game.gdp) / max(1.0, game.gdp)) * 100.0

        def fmt_roi(val): return "∞%" if val == float('inf') else f"{val:+.1f}%"

        st.markdown(t("### 📝 智庫分析報告"))
        # 標籤改為「預估總收益」避免誤導，並附上純淨的「專案 ROI」
        st.markdown(f"1. {t('我方預估總收益')}: **{my_net:.1f}** (專案 ROI: {fmt_roi(my_roi)})")
        st.markdown(f"2. {t('對方預估總收益')}: **{opp_net:.1f}** (專案 ROI: {fmt_roi(opp_roi)})")
        
        sup_c = "green" if my_sup > 0 else "red"
        st.markdown(f"3. {t('新增支持量預估')}: <span style='color:{sup_c}'>**{my_sup:+.1f} 點**</span>", unsafe_allow_html=True)
        st.markdown(f"4. {t('預期 GDP 變化')}: {game.gdp:.1f} ➔ **{res['est_gdp']:.1f}** ({o_gdp_pct:+.2f}%)")
        
        tt_decay = view_party.current_forecast
        cl_decay = plan.get('claimed_decay', 0.0)
        diff = cl_decay - tt_decay
        abs_diff = abs(diff)
        
        author_role = plan.get('author')
        viewer_role = 'H' if my_is_h else 'R'
        is_self = (author_role == viewer_role)

        if abs_diff > 0.3: 
            light = "🔴"
            if is_self:
                if cl_decay > tt_decay: risk_txt = t("高明的手法，長官。刻意高估衰退能有效壓低民眾期望，若結算超標，我們將收割巨大的預期紅利。")
                else: risk_txt = t("明智的抉擇，長官。低估衰退粉飾太平雖有奇效，但若最終經濟不如預期，須防範民意反噬。")
            else:
                if cl_decay > tt_decay: risk_txt = t("警報！對手惡意高估衰退率。企圖製造恐慌降低施政期望，藉此收割反差紅利！")
                else: risk_txt = t("根據比對，對手正惡意低估衰退率粉飾太平。若最終施政破功，他們將面臨嚴重的反撲！")
        elif abs_diff > 0.1: 
            light, risk_txt = "🟡", t("中度風險 (公告衰退率與預期略有出入，可能影響選民心理預期)")
        else: 
            light, risk_txt = "🟢", t("差異極小 (公告衰退率誠實，無心理預期操弄空間)")
            
        st.markdown(f"5. {t('衰退值判讀')}: {light} {risk_txt} ({t('公告')}: {cl_decay:.3f} / {t('智庫')}: {tt_decay:.3f})")
        
        cl_cost = plan.get('claimed_cost', eval_unit_cost)
        diff_c = cl_cost - eval_unit_cost
        abs_diff_c = abs(diff_c)

        if abs_diff_c > 0.5:
            light_c = "🔴"
            if is_self:
                if cl_cost > eval_unit_cost: risk_txt_c = t("收到，長官。高報單價將為我們爭取更寬裕的操作空間。")
                else: risk_txt_c = t("長官，刻意低報單價能展現行政效率，但過度壓榨預算恐引發工程隱患。")
            else:
                if cl_cost > eval_unit_cost:
                    risk_txt_c = t("對手（執行）意圖套取超額工程款！") if author_role == 'H' else t("對手（監管）惡意墊高基準單價建立預算門檻！")
                else:
                    risk_txt_c = t("對手（執行）企圖掩飾低效能！") if author_role == 'H' else t("對手（監管）正惡意低估單價剝削我們的預算！")
        elif abs_diff_c > 0.2:
            light_c, risk_txt_c = "🟡", t("中度風險 (單價略有出入，需留意工程品質或超支)")
        else:
            light_c, risk_txt_c = "🟢", t("差異極小 (公告單價與情報處估算相符，屬正常估值)")

        st.markdown(f"6. {t('建設單價判讀')}: {light_c} {risk_txt_c} ({t('公告')}: {cl_cost:.2f} / {t('情報')}: {eval_unit_cost:.2f})")

def ability_slider(label, key, current_val, wealth, cfg, build_ability=0.0):
    current_pct = current_val * 10.0
    t_pct = st.slider(f"{label}", 0.0, 100.0, float(current_pct), 1.0, key=key)
    t_val = t_pct / 10.0
    cost = formulas.calculate_upgrade_cost(current_val, t_val, build_ability)
    maint = formulas.get_ability_maintenance(t_val, cfg)
    
    if t_val > current_val: st.caption(f"📈 <span style='color:orange'>**{t('升級花費')}**: ${cost:.1f}</span> | 能力: {current_pct:.1f}% ➔ {t_pct:.1f}% | {t('維護費將達')} ${maint:.1f}", unsafe_allow_html=True)
    elif t_val < current_val: st.caption(f"📉 <span style='color:blue'>**{t('降級退回')}**</span> | 能力: {current_pct:.1f}% ➔ {t_pct:.1f}% | {t('維護費降至')} ${maint:.1f}", unsafe_allow_html=True)
    else: st.caption(f"🛡️ {t('穩定維持')} | 能力: {current_pct:.1f}% | {t('維護費')} ${maint:.1f}")
        
    return t_val, cost

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
