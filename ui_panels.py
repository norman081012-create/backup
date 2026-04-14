# ==========================================
# ui_panels.py
# 負責所有大型儀表板、情報處與卡片的渲染
# ==========================================
import streamlit as st
import random
import math
import config
import formulas
import engine
import i18n
t = i18n.t

# [核心實裝] 基於「量(資金)」的觀測誤差系統
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
        label_gdp = t("預期 GDP") if is_preview else t("當前 GDP")
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
                
                st.markdown(f"{t('預期政績 (未經媒體)')}: 我方 **{preview_data['my_perf']:+.1f}** / 對方 **{preview_data['opp_perf']:+.1f}**")
                if 'project_perf' in preview_data:
                    st.caption(f"*(包含執行方當前貪污設定下的履約政績: `{preview_data['project_perf']:+.1f}`)*")
    st.markdown("---")

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
            crown_str = cfg.get('
