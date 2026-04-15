# ==========================================
# phase3.py
# 負責 第三階段 (年度總結算報告與視覺化)
# ==========================================
import streamlit as st
import random
import formulas
import i18n
t = i18n.t

def render(game, cfg):
    st.header(t("⚖️ Phase 3: 年度結算報告"))
    
    if not game.last_year_report:
        rp, hp = game.r_role_party, game.h_role_party
        ra = st.session_state.get(f"{rp.name}_acts", {})
        ha = st.session_state.get(f"{hp.name}_acts", {})
        d = st.session_state.get('turn_data', {})
        
        returned_to_r = 0.0
        confiscated_to_budget = 0.0
        corr_caught = False
        crony_caught = False
        
        proj_fund = float(d.get('proj_fund') or 0.0)
        bid_cost = float(d.get('bid_cost') or 1.0)
        claimed_decay = float(d.get('claimed_decay') or 0.0)
        r_pays = float(d.get('r_pays') or 0.0)
        h_pays = float(d.get('h_pays') or 0.0)
        
        # 費用宣告提前，防止 UnboundLocalError
        h_tot_action = float(ha.get('tot_action') or 0)
        r_tot_action = float(ra.get('tot_action') or 0)
        h_tot_maint = float(ha.get('tot_maint') or 0)
        r_tot_maint = float(ra.get('tot_maint') or 0)
        
        corr_pct_val = float(ha.get('corr') or 0)
        crony_pct_val = float(ha.get('crony') or 0)
        
        corr_amt = proj_fund * (corr_pct_val / 100.0)
        crony_base = proj_fund * (crony_pct_val / 100.0)
        crony_income = crony_base * 0.1  
        
        rp_inv_pct = rp.investigate_ability / 10.0
        hp_stl_pct = hp.stealth_ability / 10.0
        actual_catch_mult = max(0.1, (rp_inv_pct * cfg['R_INV_BONUS']) - hp_stl_pct + 1.0)
        
        rolls_corr = corr_pct_val * actual_catch_mult
        catch_prob_corr = 1.0 - (1.0 - cfg['CATCH_RATE_PER_PERCENT'])**rolls_corr
        
        rolls_crony = crony_pct_val * actual_catch_mult
        catch_prob_crony = 1.0 - (1.0 - cfg['CRONY_CATCH_RATE_PER_PERCENT'])**rolls_crony
        
        if corr_amt > 0 and random.random() < catch_prob_corr:
            returned_to_r += corr_amt
            confiscated_to_budget += corr_amt * 0.4
            corr_caught = True
            corr_amt = 0

        if crony_base > 0 and random.random() < catch_prob_crony:
            returned_to_r += crony_base
            confiscated_to_budget += crony_base * 0.5
            crony_caught = True
            crony_base = 0
            crony_income = 0
            
        actual_h_wealth_available = hp.wealth - h_tot_action - h_tot_maint
        res_exec = formulas.calc_economy(cfg, float(game.gdp), float(game.total_budget), proj_fund, bid_cost, float(hp.build_ability), float(game.current_real_decay), corr_amt=corr_amt, r_pays=r_pays, h_wealth=max(0.0, actual_h_wealth_available))
        budg = cfg['BASE_TOTAL_BUDGET'] + (res_exec['est_gdp'] * cfg['HEALTH_MULTIPLIER'])
        
        hp_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == hp.name else 0))
        rp_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == rp.name else 0))
        
        hp_project_net = res_exec['h_project_profit']
        rp_project_net = res_exec['payout_r'] - r_pays
        
        hp_inc = hp_base + hp_project_net + corr_amt + crony_income
        rp_inc = rp_base + rp_project_net + returned_to_r
        
        shifts = formulas.calc_performance_amounts(
            cfg, hp, rp, game.ruling_party.name, 
            res_exec['est_gdp'], game.gdp, 
            claimed_decay, game.sanity, game.emotion, bid_cost, res_exec['c_net']
        )
        
        h_media = hp.media_ability / 10.0
        r_media = rp.media_ability / 10.0
        shifts[hp.name]['camp'] = float(ha.get('camp', 0)) * h_media * 0.1
        shifts[rp.name]['camp'] = float(ra.get('camp', 0)) * r_media * 0.1
        shifts[hp.name]['backlash'] = 0.0
        shifts[rp.name]['backlash'] = 0.0
        
        a_sup_amt, b_sup_amt = game.update_support_queues({
            game.party_A.name: shifts[game.party_A.name],
            game.party_B.name: shifts[game.party_B.name]
        })
        
        # 國家指標變化計算
        gdp_grw_bonus = ((res_exec['est_gdp'] - game.gdp)/max(1.0, game.gdp)) * 100.0
        emotion_delta = (float(ha.get('incite') or 0) + float(ra.get('incite') or 0)) * 0.1 - gdp_grw_bonus - (game.sanity * 0.20)
        new_emotion = max(0.0, min(100.0, game.emotion + emotion_delta))
        
        f_target_san = max(0.0, min(100.0, 50.0 + (float(ra.get('edu_amt') or 0) / 500.0) * 50.0))
        f_san_move = (f_target_san - game.sanity) * 0.2
        new_sanity = max(0.0, min(100.0, game.sanity - (new_emotion * 0.02) + f_san_move))
        
        game.last_year_report = {
            'old_gdp': game.gdp, 'old_san': game.sanity, 'old_emo': game.emotion, 'old_budg': game.total_budget, 'old_h_fund': game.h_fund,
            'new_san': new_sanity, 'new_emo': new_emotion,
            'h_party_name': hp.name, 'r_party_name': rp.name,
            'shifts': shifts, 
            'h_inc': hp_inc, 'r_inc': rp_inc, 
            'h_base': hp_base, 'r_base': rp_base, 
            'h_project_net': hp_project_net, 'r_project_net': rp_project_net,
            'h_extra': corr_amt + crony_income, 'r_extra': returned_to_r,
            'h_pol_cost': h_tot_action, 'r_pol_cost': r_tot_action,
            'h_maint': h_tot_maint, 'r_maint': r_tot_maint,
            'corr_caught': corr_caught, 'crony_caught': crony_caught
        }
        
        # 更新國家數值
        game.gdp = res_exec['est_gdp']
        game.sanity = new_sanity
        game.emotion = new_emotion
        game.h_fund = res_exec['payout_h']
        game.total_budget = budg + confiscated_to_budget
        
        hp.wealth += hp_inc - h_tot_action - h_tot_maint
        rp.wealth += rp_inc - r_tot_action - r_tot_maint

        if game.year % cfg['ELECTION_CYCLE'] == 1:
            winner = hp if hp.support > rp.support else rp
            game.ruling_party = winner

        hp.last_acts = ha.copy(); rp.last_acts = ra.copy()
        game.record_history(is_election=(game.year % cfg['ELECTION_CYCLE'] == 1))
    
    rep = game.last_year_report
    
    # === UI 渲染區 ===
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### 💰 {t('經濟與收益結算')}")
        st.write(f"**GDP:** `{rep['old_gdp']:.1f}` ➔ `{game.gdp:.1f}`")
        
        # 執行系統收益明細
        with st.expander(f"📊 {rep['h_party_name']} ({t('執行系統')}) {t('收益明細')}"):
            st.write(f"- {t('基礎撥款 (含執政紅利)')}: `${rep['h_base']:.1f}`")
            st.write(f"- {t('專案執行利潤')}: `${rep['h_project_net']:.1f}`")
            if rep['h_extra'] > 0:
                st.write(f"- {t('秘密所得 (貪污/圖利)')}: `${rep['h_extra']:.1f}`")
            st.write(f"- {t('行政與部門支出')}: `-${rep['h_pol_cost'] + rep['h_maint']:.1f}`")
            st.write(f"**{t('最終淨收益')}: `${rep['h_inc'] - (rep['h_pol_cost'] + rep['h_maint']):.1f}`**")

        # 監管系統收益明細
        with st.expander(f"📊 {rep['r_party_name']} ({t('監管系統')}) {t('收益明細')}"):
            st.write(f"- {t('基礎撥款 (含執政紅利)')}: `${rep['r_base']:.1f}`")
            st.write(f"- {t('專案監管剩餘')}: `${rep['r_project_net']:.1f}`")
            if rep['r_extra'] > 0:
                st.write(f"- {t('沒收所得/查獲獎金')}: `${rep['r_extra']:.1f}`")
            st.write(f"- {t('行政與部門支出')}: `-${rep['r_pol_cost'] + rep['r_maint']:.1f}`")
            st.write(f"**{t('最終淨收益')}: `${rep['r_inc'] - (rep['r_pol_cost'] + rep['r_maint']):.1f}`**")

        if rep.get('corr_caught'): st.error(t("🚨 偵獲執行方貪污行為，非法資金已沒收並繳回國庫。"))
        if rep.get('crony_caught'): st.error(t("🚨 偵獲執行方圖利爭議，關聯資金已全數凍結。"))

    with c2:
        st.markdown(f"### 🧠 {t('社會指標與國家變化')}")
        s_move = game.sanity - rep['old_san']
        e_move = game.emotion - rep['old_emo']
        
        st.write(f"**{t('資訊辨識 (思辨)')}:** `{rep['old_san']:.1f}` ➔ `{game.sanity:.1f}` ({s_move:+.1f})")
        st.write(f"**{t('選民情緒 (波動)')}:** `{rep['old_emo']:.1f}` ➔ `{game.emotion:.1f}` ({e_move:+.1f})")
        
        st.markdown("---")
        st.markdown(f"### 📈 {t('支持量歸因分析')}")
        
        for p_name in [rep['h_party_name'], rep['r_party_name']]:
            is_h = (p_name == rep['h_party_name'])
            role_label = t("執行") if is_h else t("監管")
            shift = rep['shifts'][p_name]
            
            with st.expander(f"🔎 {p_name} ({role_label}) {t('支持量來源')}"):
                # 這裡顯示政績歸因
                # 我們假設在 shifts 中已經拆分好，或者在這裡進行說明
                # 根據您的描述，我們在顯示上強調「專案表現」與「大環境紅利」
                if is_h:
                    st.write(f"- 🏗️ **{t('專案執行政績')}**: `{shift['perf'] * 0.7:+.1f}` (來自工程產出)")
                    st.write(f"- 🌐 **{t('大環境歸因紅利')}**: `{shift['perf'] * 0.3:+.1f}` (民眾對經濟成長的印象)")
                else:
                    st.write(f"- ⚖️ **{t('制度監督政績')}**: `{shift['perf'] * 0.4:+.1f}` (維護預算紀律)")
                    st.write(f"- 👑 **{t('執政名望紅利')}**: `{shift['perf'] * 0.6:+.1f}` (當權者的天然優勢)")
                
                st.write(f"- 📢 **{t('媒體與造勢')}**: `{shift['camp']:+.1f}`")

    st.markdown("---")
    if st.button(t("⏩ 確認報告並進入下一年"), type="primary", use_container_width=True):
        game.year += 1
        if game.year > cfg['END_YEAR']: game.phase = 4
        else:
            game.phase = 1; game.p1_step = 'draft_r'
            game.p1_proposals = {'R': None, 'H': None}; game.p1_selected_plan = None
            for k in list(st.session_state.keys()):
                if k.endswith('_acts'): del st.session_state[k]
            if 'turn_initialized' in st.session_state: del st.session_state.turn_initialized
        st.rerun()
