# ==========================================
# phase3.py
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
        
        fine_mult = float(d.get('fine_mult', 0.3)) 
        
        if 't_pre' in ra: rp.predict_ability = float(ra['t_pre'])
        if 't_inv' in ra: rp.investigate_ability = float(ra['t_inv'])
        if 't_med' in ra: rp.media_ability = float(ra['t_med'])
        if 't_stl' in ra: rp.stealth_ability = float(ra['t_stl'])
        if 't_bld' in ra: rp.build_ability = float(ra['t_bld'])
        if 'edu_stance' in ra: rp.edu_stance = float(ra['edu_stance'])
        
        if 't_pre' in ha: hp.predict_ability = float(ha['t_pre'])
        if 't_inv' in ha: hp.investigate_ability = float(ha['t_inv'])
        if 't_med' in ha: hp.media_ability = float(ha['t_med'])
        if 't_stl' in ha: hp.stealth_ability = float(ha['t_stl'])
        if 't_bld' in ha: hp.build_ability = float(ha['t_bld'])
        if 'edu_stance' in ha: hp.edu_stance = float(ha['edu_stance'])
        
        returned_to_r = 0.0
        confiscated_to_budget = 0.0
        hp_wealth_penalty = 0.0
        corr_caught = False
        crony_caught = False
        
        proj_fund = float(d.get('proj_fund') or 0.0)
        bid_cost = float(d.get('bid_cost') or 1.0)
        claimed_decay = float(d.get('claimed_decay') or 0.0)
        r_pays = float(d.get('r_pays') or 0.0)
        
        # 🚀 引入行動花費與退費
        h_tot_action = float(ha.get('tot_action') or 0)
        r_tot_action = float(ra.get('tot_action') or 0)
        h_tot_maint = float(ha.get('tot_maint') or 0)
        r_tot_maint = float(ra.get('tot_maint') or 0)
        h_refund = float(ha.get('refund_action') or 0)
        r_refund = float(ra.get('refund_action') or 0)
        
        corr_amt = float(ha.get('corr_amt') or 0.0)
        crony_base = float(ha.get('crony_amt') or 0.0)
        
        rp_inv_pct = rp.investigate_ability / 10.0
        hp_stl_pct = hp.stealth_ability / 10.0
        actual_catch_mult = max(0.1, (rp_inv_pct * cfg.get('R_INV_BONUS', 1.2)) - hp_stl_pct + 1.0)
        
        inflation = max(0.0, (game.gdp - cfg.get('CURRENT_GDP', 5000.0)) / cfg.get('GDP_INFLATION_DIVISOR', 10000.0))
        
        # 1. 貪污結算
        adj_corr_amt = corr_amt / (1.0 + inflation)
        rolls_corr = adj_corr_amt * actual_catch_mult
        catch_rate_per_dollar = cfg.get('CATCH_RATE_PER_DOLLAR', 0.10)
        catch_prob_corr = 1.0 - (1.0 - catch_rate_per_dollar)**rolls_corr
        
        if corr_amt > 0 and random.random() < catch_prob_corr:
            original_corr_amt = corr_amt
            returned_to_r += original_corr_amt
            penalty = original_corr_amt * fine_mult
            hp_wealth_penalty += penalty
            confiscated_to_budget += penalty
            corr_caught = True
            corr_amt = 0 

        # 2. 圖利結算
        crony_profit_rate = cfg.get('CRONY_PROFIT_RATE', 0.20)
        crony_income = crony_base * crony_profit_rate
        
        adj_crony_base = crony_base / (1.0 + inflation)
        rolls_crony = adj_crony_base * actual_catch_mult
        crony_catch_rate_dollar = catch_rate_per_dollar * 0.2 
        catch_prob_crony = 1.0 - (1.0 - crony_catch_rate_dollar)**rolls_crony
        
        if crony_base > 0 and random.random() < catch_prob_crony:
            original_crony_base = crony_base
            returned_to_r += original_crony_base
            penalty = original_crony_base * fine_mult
            hp_wealth_penalty += penalty
            confiscated_to_budget += penalty
            crony_caught = True
            crony_income = 0
            
        hp_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == hp.name else 0))
        rp_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == rp.name else 0))
        
        actual_h_wealth_available = max(0.0, hp.wealth - h_tot_action - h_tot_maint + h_refund - hp_wealth_penalty + hp_base)
        res_exec = formulas.calc_economy(cfg, float(game.gdp), float(game.total_budget), proj_fund, bid_cost, float(hp.build_ability), float(game.current_real_decay), corr_amt=corr_amt, r_pays=r_pays, h_wealth=actual_h_wealth_available)
        budg = cfg['BASE_TOTAL_BUDGET'] + (res_exec['est_gdp'] * cfg['HEALTH_MULTIPLIER'])
        
        hp_project_net = res_exec['h_project_profit']
        rp_project_net = res_exec['payout_r'] - r_pays
        
        hp_inc = hp_base + hp_project_net + corr_amt + crony_income
        rp_inc = rp_base + rp_project_net + returned_to_r
        
        # 媒體與意識形態準備階段
        s_val = max(0.0, (game.sanity - 50.0) / 50.0) 
        c_val = max(0.0, (50.0 - game.sanity) / 50.0) 
        censor_factor = 1.0 + s_val - c_val           
        
        media_multiplier = max(0.1, 1.0 - s_val + c_val + (game.emotion / 100.0))
        
        # 媒體審查運作與固著度反噬
        judicial_lvl = float(ra.get('judicial_lvl', 0.0))
        
        B = game.boundary_B
        opp_indices = range(B + 1, 201) if hp.name == game.party_A.name else range(1, B + 1)
        censor_successes = 0
        censor_failures = 0
        
        for i in opp_indices:
            rig = formulas.get_rigidity(i, game.sanity, getattr(game, 'h_rigidity_buff', {}).get('amount', 0.0), getattr(game, 'h_rigidity_buff', {}).get('party'), B, game.party_A.name)
            if random.random() > rig:
                censor_successes += 1
            else:
                censor_failures += 1
        
        censor_weight = judicial_lvl / 100.0 
        censor_emotion_add = censor_weight * censor_successes * censor_factor
        
        if (censor_successes + censor_failures) > 0:
            censor_rigidity_buff = censor_weight * (censor_successes / (censor_successes + censor_failures)) * censor_factor
        else:
            censor_rigidity_buff = 0.0
            
        if judicial_lvl > 0:
            game.h_rigidity_buff = {'amount': censor_rigidity_buff, 'duration': 2, 'party': hp.name}
            
        h_censor_penalty = max(0.1, 1.0 - censor_weight) 
        
        # 🚀 套用公關金錢倍率
        pr_mult = cfg.get('PR_EFFICIENCY_MULT', 3.0)
        h_media_pwr = float(ha.get('media', 0.0)) * pr_mult * (hp.media_ability / 10.0) * cfg.get('H_MEDIA_BONUS', 1.2) * media_multiplier * h_censor_penalty
        r_media_pwr = float(ra.get('media', 0.0)) * pr_mult * (rp.media_ability / 10.0) * media_multiplier
        
        raw_p_plan, raw_p_exec, d_a, d_e, d_c = formulas.generate_raw_support(cfg, res_exec['est_gdp'], game.gdp, claimed_decay, bid_cost, res_exec['c_net'])
        
        plan_correct, plan_wrong, correct_prob = formulas.apply_sanity_filter(raw_p_plan, game.sanity, game.emotion, is_preview=False)
        exec_correct, exec_wrong, _ = formulas.apply_sanity_filter(raw_p_exec, game.sanity, game.emotion, is_preview=False)
        
        ruling_name = game.ruling_party.name
        if ruling_name == hp.name:
            ruling_media_pwr = h_media_pwr; opp_media_pwr = r_media_pwr
        else:
            ruling_media_pwr = r_media_pwr; opp_media_pwr = h_media_pwr
            
        ruling_spun_plan, opp_spun_plan = formulas.apply_media_spin(plan_wrong, ruling_media_pwr, opp_media_pwr)
        h_spun_exec, r_spun_exec = formulas.apply_media_spin(exec_wrong, h_media_pwr, r_media_pwr)

        ammo_A = 0.0; ammo_B = 0.0

        if ruling_name == game.party_A.name:
            ammo_A += plan_correct + ruling_spun_plan; ammo_B += opp_spun_plan
        else:
            ammo_B += plan_correct + ruling_spun_plan; ammo_A += opp_spun_plan

        if hp.name == game.party_A.name:
            ammo_A += exec_correct + h_spun_exec; ammo_B += r_spun_exec
        else:
            ammo_B += exec_correct + h_spun_exec; ammo_A += r_spun_exec
            
        # 實裝造勢競選點數 (套用倍率)
        h_camp_pwr = float(ha.get('camp', 0.0)) * pr_mult * (hp.media_ability / 10.0) * media_multiplier * h_censor_penalty * 0.5
        r_camp_pwr = float(ra.get('camp', 0.0)) * pr_mult * (rp.media_ability / 10.0) * media_multiplier * 0.5

        if hp.name == game.party_A.name: ammo_A += h_camp_pwr; ammo_B += r_camp_pwr
        else: ammo_B += h_camp_pwr; ammo_A += r_camp_pwr

        net_ammo_A = ammo_A - ammo_B
        old_boundary = game.boundary_B
        
        buff_amt = getattr(game, 'h_rigidity_buff', {}).get('amount', 0.0)
        buff_party = getattr(game, 'h_rigidity_buff', {}).get('party')
        new_boundary, used_ammo, conquered = formulas.run_conquest(game.boundary_B, net_ammo_A, game.sanity, buff_amt, buff_party, game.party_A.name)
        
        game.boundary_B = new_boundary
        game.party_A.support = new_boundary * 0.5
        game.party_B.support = 100.0 - game.party_A.support
        
        gdp_grw_bonus = ((res_exec['est_gdp'] - game.gdp)/max(1.0, game.gdp)) * 100.0
        
        # 實裝非線性情緒煽動 (套用倍率)
        h_incite_rolls = float(ha.get('incite', 0.0)) * pr_mult * media_multiplier * h_censor_penalty
        r_incite_rolls = float(ra.get('incite', 0.0)) * pr_mult * media_multiplier
        total_incite_rolls = h_incite_rolls + r_incite_rolls
        
        incite_points = formulas.calc_incite_success(total_incite_rolls, game.emotion)
        
        emotion_delta = (incite_points * 0.1) + censor_emotion_add - gdp_grw_bonus - (game.sanity * 0.15)
        new_emotion = max(0.0, min(100.0, game.emotion + emotion_delta))
        
        f_target_san = max(0.0, min(100.0, 50.0 + (ha.get('edu_stance', 0) + ra.get('edu_stance', 0)) * 0.5))
        f_san_move = (f_target_san - game.sanity) * 0.2
        new_sanity = max(0.0, min(100.0, game.sanity - (new_emotion * 0.02) + f_san_move))
        
        total_bonus_deduction = game.total_budget * ((cfg['BASE_INCOME_RATIO'] * 2) + cfg['RULING_BONUS_RATIO'])
        
        game.last_year_report = {
            'old_gdp': game.gdp, 'old_san': game.sanity, 'old_emo': game.emotion, 'old_budg': game.total_budget, 'old_h_fund': game.h_fund,
            'new_san': new_sanity, 'new_emo': new_emotion,
            'h_party_name': hp.name, 'r_party_name': rp.name,
            'raw_p_plan': raw_p_plan, 'raw_p_exec': raw_p_exec,
            'ammo_A': ammo_A, 'ammo_B': ammo_B, 'net_ammo_A': net_ammo_A,
            'old_boundary': old_boundary, 'new_boundary': new_boundary, 'used_ammo': used_ammo, 'conquered': conquered,
            'correct_prob': correct_prob,
            'h_spun_exec': h_spun_exec, 'r_spun_exec': r_spun_exec, 
            'censor_successes': censor_successes, 'censor_failures': censor_failures, 'censor_emotion_add': censor_emotion_add, 'censor_buff': censor_rigidity_buff,
            'h_inc': hp_inc, 'r_inc': rp_inc, 
            'h_base': hp_base, 'r_base': rp_base, 
            'h_project_net': hp_project_net, 'r_project_net': rp_project_net,
            'payout_h': res_exec['payout_h'], 'act_fund': res_exec['act_fund'], 'r_pays': r_pays,
            'h_extra': corr_amt + crony_income, 'r_extra': returned_to_r,
            'h_pol_cost': h_tot_action, 'r_pol_cost': r_tot_action,
            'h_maint': h_tot_maint, 'r_maint': r_tot_maint,
            'h_refund': h_refund, 'r_refund': r_refund,
            'hp_penalty': hp_wealth_penalty,
            'corr_caught': corr_caught, 'crony_caught': crony_caught,
            'fine_mult': fine_mult,
            'proj_fund': proj_fund, 'h_idx': res_exec['h_idx'], 'total_bonus_deduction': total_bonus_deduction
        }
        
        game.gdp = res_exec['est_gdp']
        game.sanity = new_sanity
        game.emotion = new_emotion
        game.h_fund = res_exec['payout_h']
        game.total_budget = budg + confiscated_to_budget
        
        hp.wealth += hp_inc - h_tot_action - h_tot_maint + h_refund - hp_wealth_penalty
        rp.wealth += rp_inc - r_tot_action - r_tot_maint + r_refund

        if hasattr(game, 'h_rigidity_buff') and game.h_rigidity_buff['duration'] > 0:
            game.h_rigidity_buff['duration'] -= 1
            if game.h_rigidity_buff['duration'] <= 0:
                game.h_rigidity_buff = {'amount': 0.0, 'duration': 0, 'party': None}

        is_election_end = (game.year % cfg['ELECTION_CYCLE'] == 0)
        if is_election_end:
            winner = game.party_A if game.party_A.support > game.party_B.support else game.party_B
            game.ruling_party = winner

        hp.last_acts = ha.copy(); rp.last_acts = ra.copy()
        game.record_history(is_election=is_election_end)
    
    rep = game.last_year_report
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### 💰 {t('經濟與財政結算')}")
        st.write(f"**GDP:** `{rep['old_gdp']:.1f}` ➔ `{game.gdp:.1f}`")
        
        with st.expander(f"📊 {rep['h_party_name']} ({t('執行系統')}) 專案與收益明細"):
            st.write(f"- 📥 領取計畫獎勵金: `${rep['payout_h']:.1f}`")
            st.write(f"- 📥 收取監管方補貼: `${rep['r_pays']:.1f}`")
            st.write(f"- 📤 實際工程款支出: `-${rep['act_fund']:.1f}`")
            st.write(f"**= 專案結算淨盈虧: `${rep['h_project_net']:.1f}`**")
            st.markdown("---")
            st.write(f"- 基礎撥款 (含執政紅利): `${rep['h_base']:.1f}`")
            if rep['h_extra'] > 0:
                st.write(f"- 秘密所得 (洗白後貪污/圖利): `${rep['h_extra']:.1f}`")
            if rep.get('hp_penalty', 0) > 0:
                st.write(f"- 🚨 查扣罰金繳納國庫 (倍率 {rep['fine_mult']}x): `-${rep['hp_penalty']:.1f}`")
            st.write(f"- 公關行動與轉型費: `-${rep['h_pol_cost']:.1f}`")
            st.write(f"- 部門與政策維護費: `-${rep['h_maint']:.1f}`")
            if rep['h_refund'] > 0: st.write(f"- 降級退款回收: `+${rep['h_refund']:.1f}`")
            net_cash = rep['h_inc'] - rep['h_pol_cost'] - rep['h_maint'] + rep['h_refund'] - rep.get('hp_penalty', 0)
            st.write(f"**💰 最終總淨現金流: `${net_cash:.1f}`**")

        with st.expander(f"📊 {rep['r_party_name']} ({t('監管系統')}) 結餘與收益明細"):
            st.write(f"- 基礎撥款 (含執政紅利): `${rep['r_base']:.1f}`")
            st.write(f"- 📤 支付監管補貼: `-${rep['r_pays']:.1f}`")
            unspent_proj = rep['proj_fund'] * (1.0 - rep['h_idx'])
            st.write(f"- 📥 未執行專案款繳回: `${unspent_proj:.1f}`")
            base_r_surplus = rep['old_budg'] - rep['total_bonus_deduction'] - rep['proj_fund']
            st.write(f"- 📥 監管預算結餘: `${max(0.0, base_r_surplus):.1f}`")
            if rep['r_extra'] > 0:
                st.write(f"- 🏆 沒收對手全額違規金: `${rep['r_extra']:.1f}`")
            st.write(f"- 公關行動與轉型費: `-${rep['r_pol_cost']:.1f}`")
            st.write(f"- 部門與政策維護費: `-${rep['r_maint']:.1f}`")
            if rep['r_refund'] > 0: st.write(f"- 降級退款回收: `+${rep['r_refund']:.1f}`")
            net_cash_r = rep['r_inc'] - rep['r_pol_cost'] - rep['r_maint'] + rep['r_refund']
            st.write(f"**💰 最終總淨現金流: `${net_cash_r:.1f}`**")

        if rep.get('corr_caught'): st.error(t("🚨 偵獲執行方貪污！非法資金全額移交監管方，執行方並遭裁罰額外罰金入國庫。"))
        if rep.get('crony_caught'): st.error(t("🚨 偵獲執行方圖利廠商！執行方遭強制繳回全額合約金予監管方，並追加罰金入國庫。"))

    with c2:
        st.markdown(f"### 🧠 {t('社會指標與選民變化')}")
        s_move = game.sanity - rep['old_san']
        e_move = game.emotion - rep['old_emo']
        
        st.write(f"**{t('資訊辨識 (思辨)')}:** `{rep['old_san']:.1f}` ➔ `{game.sanity:.1f}` ({s_move:+.1f})")
        st.write(f"**{t('選民情緒 (波動)')}:** `{rep['old_emo']:.1f}` ➔ `{game.emotion:.1f}` ({e_move:+.1f})")
        
        st.markdown("---")
        st.markdown(f"### ⚔️ 支持度影響結算")
        
        if st.session_state.get('god_mode'):
            st.caption(f"*(👁️ 上帝視角 | 大環境規劃政績: `{rep['raw_p_plan']/cfg['AMMO_MULTIPLIER']:+.2f}` | 執行政績: `{rep['raw_p_exec']/cfg['AMMO_MULTIPLIER']:+.2f}`)*")
        
        st.caption(f"*(📡 今年度選民思辨正確歸因率: `{rep['correct_prob']*100:.1f}%`)*")
        
        if rep['h_spun_exec'] != 0 or rep['r_spun_exec'] != 0:
            st.info(f"📺 **本年媒體風向：** 執行方透過媒體操控轉移了 `{rep['h_spun_exec']:+.1f}` 點政績；監管方帶風向轉移了 `{rep['r_spun_exec']:+.1f}` 點！")
            
        if rep.get('censor_buff', 0) > 0:
            st.warning(f"⚖️ **審查反噬：** 監管方強制打壓媒體，激怒了 `{rep['censor_successes']}` 單位對立選民！執行方支持者的固著度未來兩年內大幅強化 `+{rep['censor_buff']:.3f}`！")

        st.write(f"**{game.party_A.name} 總支持量:** `{rep['ammo_A']:.1f}` | **{game.party_B.name} 總支持量:** `{rep['ammo_B']:.1f}`")
        
        net_ammo = rep['net_ammo_A']
        atk_party = game.party_A.name if net_ammo > 0 else game.party_B.name
        def_party = game.party_B.name if net_ammo > 0 else game.party_A.name
        
        if abs(net_ammo) < 1.0:
            st.info("🤝 雙方支持量僵持不下，民意版圖無變化。")
        else:
            st.success(f"**淨支持量優勢:** `{abs(net_ammo):.1f}` 點！由 **{atk_party}** 向 **{def_party}** 的選民發起影響！")
            
            if st.session_state.get('god_mode'):
                st.write(f"👁️ *(上帝視角)* 經歷殘酷的固著度裝甲檢定，消耗了 `{rep['used_ammo']:.1f}` 點支持量，成功攻克 **{rep['conquered']}** 個對手陣地 (每格 0.5%)！")
                old_sup = rep['old_boundary'] * 0.5; new_sup = rep['new_boundary'] * 0.5
                st.write(f"📊 👁️ **{game.party_A.name} 新支持度:** `{old_sup:.1f}%` ➔ `{new_sup:.1f}%`")

    st.markdown("---")
    if st.button(t("⏩ 確認報告並進入下一年"), type="primary", use_container_width=True):
        is_election_end = (game.year % cfg['ELECTION_CYCLE'] == 0)
        game.year += 1
        
        if game.year > cfg['END_YEAR']: game.phase = 4
        else:
            game.phase = 1; game.p1_step = 'draft_r'
            game.p1_proposals = {'R': None, 'H': None}; game.p1_selected_plan = None
            
            if is_election_end:
                game.r_role_party = game.ruling_party
                game.h_role_party = game.party_B if game.ruling_party.name == game.party_A.name else game.party_A
            
            game.proposing_party = game.r_role_party
            game.last_year_report = None
            
            for k in list(st.session_state.keys()):
                if k.endswith('_acts') or k.startswith('up_'): del st.session_state[k]
            if 'turn_initialized' in st.session_state: del st.session_state.turn_initialized
        st.rerun()
