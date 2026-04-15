# ==========================================
# ui_proposal.py
# 負責 提案草案渲染
# ==========================================
import streamlit as st
import formulas
import ui_core
import config
import i18n
t = i18n.t

def render_proposal_component(title, plan, game, view_party, cfg):
    st.markdown(f"#### {title}")
    
    c_tog1, c_tog2 = st.columns(2)
    use_tt = c_tog1.toggle(t("切換至 智庫預估 試算 (預設為公告數值)"), False, key=f"tg_tt_{title}_{plan.get('author', 'sys')}")
    use_claimed = not use_tt
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

    # === 情報基準脫鉤 ===
    tt_decay = view_party.current_forecast
    obs_abis = ui_core.get_observed_abilities(view_party, sim_h_party, game, cfg)
    obs_bld = obs_abis['build']
    tt_unit_cost = round(formulas.calc_unit_cost(cfg, game.gdp, obs_bld, tt_decay), 2)
    
    cl_decay = plan.get('claimed_decay', tt_decay)
    cl_cost = plan.get('claimed_cost', tt_unit_cost)

    if use_claimed:
        eval_decay = cl_decay
        eval_cost = cl_cost
    else:
        eval_decay = tt_decay
        eval_cost = tt_unit_cost

    res = formulas.calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], sim_h_party.build_ability, eval_decay, override_unit_cost=eval_cost, r_pays=plan['r_pays'], h_wealth=sim_h_party.wealth)
    
    eval_req_cost = res['req_cost']          
    eval_unit_cost = res.get('unit_cost', 1.0)
    eval_r_pays = plan['r_pays']             
    eval_h_pays = eval_req_cost - eval_r_pays 
    
    with c1:
        conv_rate = cfg.get('GDP_CONVERSION_RATE', 0.2)
        equiv_infra_loss = (game.gdp * (cl_decay * cfg.get('DECAY_WEIGHT_MULT', 0.05) + cfg.get('BASE_DECAY_RATE', 0.0))) / conv_rate
        
        st.write(f"**{t('公告衰退率')}:** {cl_decay:.3f}")
        st.write(f"**(相當於 {equiv_infra_loss:.1f} 建設損失)**")
        st.write(f"**{t('計畫達成獎勵金')}:** {plan['proj_fund']:.1f} | **{t('計畫總效益')}:** {plan['bid_cost']:.1f}")
        
        if simulate_swap:
            st.info(f"🔧 **{t('模擬執行方出資')}:** {t('總額')} {eval_req_cost:.1f} ({t('監管出資')}: {eval_r_pays:.1f} | {t('執行出資')}: {eval_h_pays:.1f})")
        else:
            st.write(f"**{t('出資總額')}:** {eval_req_cost:.1f} ({t('監管出資')}: {eval_r_pays:.1f} | {t('執行出資')}: {eval_h_pays:.1f})")
            
    with c2:
        h_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if sim_ruling_name == sim_h_party.name else 0))
        r_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if sim_ruling_name == sim_r_party.name else 0))
        
        h_project_profit = res['h_project_profit']
        r_project_profit = res['payout_r'] - eval_r_pays
        
        o_h_roi = (h_project_profit / float(eval_h_pays)) * 100.0 if eval_h_pays > 0 else float('inf')
        o_r_roi = (r_project_profit / float(eval_r_pays)) * 100.0 if eval_r_pays > 0 else float('inf')
        
        my_roi = o_h_roi if my_is_h else o_r_roi
        opp_roi = o_r_roi if my_is_h else o_h_roi
        
        my_net = h_base + h_project_profit if my_is_h else r_base + r_project_profit
        opp_net = r_base + r_project_profit if my_is_h else h_base + h_project_profit
        
        # 開啟 is_preview 獲取正確歸因率和期望值
        shift_preview = formulas.calc_performance_amounts(
            cfg, sim_h_party, sim_r_party, sim_ruling_name,
            res['est_gdp'], game.gdp, 
            cl_decay, game.sanity, game.emotion, plan['bid_cost'], res['c_net'],
            is_preview=True
        )
        
        # 抓取雙方單純的大環境政績 (GDP)
        opp_party_name = sim_r_party.name if my_is_h else sim_h_party.name
        base_my_perf = shift_preview[view_party.name]['perf_gdp']
        base_opp_perf = shift_preview[opp_party_name]['perf_gdp']
        
        # 抓取專案苦勞的預期分配點數
        h_gain = shift_preview['h_proj_preview']
        r_gain = shift_preview['r_proj_preview']
        prob = shift_preview['correct_prob']
        
        o_gdp_pct = ((res['est_gdp'] - game.gdp) / max(1.0, game.gdp)) * 100.0
        def fmt_roi(val): return "∞%" if val == float('inf') else f"{val:+.1f}%"

        st.markdown(t("### 📝 智庫分析報告"))
        st.markdown(f"1. {t('我方預估總收益')}: **{my_net:.1f}** (專案 ROI: {fmt_roi(my_roi)})")
        st.markdown(f"2. {t('對方預估總收益')}: **{opp_net:.1f}** (專案 ROI: {fmt_roi(opp_roi)})")
        
        st.markdown(f"3. {t('預期大環境政績 (未經媒體)')}: 我方 **{base_my_perf:+.1f}** / 對手 **{base_opp_perf:+.1f}**")
        st.caption(f"*(⚠️ 草案階段不預設完工。若執行方 100% 履約，因選民正確歸因率僅 `{prob*100:.1f}%`，預期：執行方獲得 `{h_gain:+.1f}` 點 / 監管方獲得 `{r_gain:+.1f}` 點)*")
        
        st.markdown(f"4. {t('預期 GDP 變化')}: {game.gdp:.1f} ➔ **{res['est_gdp']:.1f}** ({o_gdp_pct:+.2f}%)")
        
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
        
        diff_c = cl_cost - tt_unit_cost
        abs_diff_c = abs(diff_c)

        if abs_diff_c > 0.5:
            light_c = "🔴"
            if is_self:
                if cl_cost > tt_unit_cost: risk_txt_c = t("收到，長官。高報單價將為我們爭取更寬裕的操作空間。")
                else: risk_txt_c = t("長官，刻意低報單價能展現行政效率，但過度壓榨預算恐引發工程隱患。")
            else:
                if cl_cost > tt_unit_cost:
                    risk_txt_c = t("對手（執行）意圖套取超額工程款！") if author_role == 'H' else t("對手（監管）惡意墊高基準單價建立預算門檻！")
                else:
                    risk_txt_c = t("對手（執行）企圖掩飾低效能！") if author_role == 'H' else t("對手（監管）正惡意低估單價剝削我們的預算！")
        elif abs_diff_c > 0.2:
            light_c, risk_txt_c = "🟡", t("中度風險 (單價略有出入，需留意工程品質或超支)")
        else:
            light_c, risk_txt_c = "🟢", t("差異極小 (公告單價與情報處估算相符，屬正常估值)")

        st.markdown(f"6. {t('建設單價判讀')}: {light_c} {risk_txt_c} ({t('公告')}: {cl_cost:.2f} / {t('情報')}: {tt_unit_cost:.2f})")
