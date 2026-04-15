# ==========================================
# ui_proposal.py
# 負責 提案草案渲染 (修正換位模擬邏輯與支持度明細)
# ==========================================
import streamlit as st
import formulas
import ui_core
import config
import i18n
t = i18n.t

def render_proposal_component(title, plan, game, view_party, cfg):
    st.markdown(t("#### 📝 智庫分析報告", "#### 📝 Think Tank Analysis Report"))
    
    c_tog1, c_tog2 = st.columns(2)
    use_tt = c_tog1.toggle(t("切換至 智庫預估 試算", "Switch to Think Tank Estimate"), False, key=f"tg_tt_{title}_{plan.get('author', 'sys')}")
    use_claimed = not use_tt
    simulate_swap = c_tog2.toggle(t("模擬如果發生倒閣換位 (角色互換)", "Simulate Role Swap"), False, key=f"sim_sw_{title}_{plan.get('author', 'sys')}")
    
    if simulate_swap:
        sim_h_party = game.r_role_party
        sim_r_party = game.h_role_party
        sim_ruling_name = game.ruling_party.name 
        my_is_h_in_sim = (view_party.name == sim_h_party.name)
        my_is_ruling_in_sim = (view_party.name == sim_ruling_name)
        swap_penalty = game.total_budget * cfg.get('TRUST_BREAK_PENALTY_RATIO', 0.05)
        st.warning("⚠️ 模擬換位中：您將模擬扮演對手角色進行損益評估。")
    else:
        sim_h_party = game.h_role_party
        sim_r_party = game.r_role_party
        sim_ruling_name = game.ruling_party.name
        my_is_h_in_sim = (view_party.name == sim_h_party.name)
        my_is_ruling_in_sim = (view_party.name == sim_ruling_name)
        swap_penalty = 0.0

    tt_decay = view_party.current_forecast
    obs_abis = ui_core.get_observed_abilities(view_party, sim_h_party, game, cfg)
    obs_bld = obs_abis['build']
    
    tt_unit_cost = round(formulas.calc_unit_cost(cfg, game.gdp, obs_bld, tt_decay), 2)
    
    cl_decay = plan.get('claimed_decay', tt_decay)
    cl_cost = plan.get('claimed_cost', tt_unit_cost)

    eval_decay = cl_decay if use_claimed else tt_decay
    eval_cost = cl_cost if use_claimed else tt_unit_cost

    res = formulas.calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], sim_h_party.build_ability, eval_decay, override_unit_cost=eval_cost, r_pays=plan['r_pays'], h_wealth=sim_h_party.wealth)
    
    eval_req_cost = res['req_cost']          
    eval_r_pays = plan['r_pays']             
    eval_h_pays = eval_req_cost - eval_r_pays 

    h_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if sim_ruling_name == sim_h_party.name else 0))
    r_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if sim_ruling_name == sim_r_party.name else 0))
    
    h_project_profit = res['h_project_profit']
    r_project_profit = res['payout_r'] - eval_r_pays
    
    my_net = (h_base + h_project_profit if my_is_h_in_sim else r_base + r_project_profit) - swap_penalty
    opp_net = (r_base + r_project_profit if my_is_h_in_sim else h_base + h_project_profit) - swap_penalty
    
    o_h_roi = (h_project_profit / float(eval_h_pays)) * 100.0 if eval_h_pays > 0 else float('inf')
    o_r_roi = (r_project_profit / float(eval_r_pays)) * 100.0 if eval_r_pays > 0 else float('inf')
    
    my_roi = o_h_roi if my_is_h_in_sim else o_r_roi
    opp_roi = o_r_roi if my_is_h_in_sim else o_h_roi
    
    shift_preview = formulas.calc_performance_preview(
        cfg, sim_h_party, sim_r_party, sim_ruling_name,
        res['est_gdp'], game.gdp, 
        cl_decay, game.sanity, game.emotion, plan['bid_cost'], res['c_net']
    )
    
    opp_party_name = sim_r_party.name if my_is_h_in_sim else sim_h_party.name
    
    my_gdp_perf = shift_preview[view_party.name]['perf_gdp']
    my_proj_perf = shift_preview[view_party.name]['perf_proj']
    my_total_perf = my_gdp_perf + my_proj_perf
    
    opp_gdp_perf = shift_preview[opp_party_name]['perf_gdp']
    opp_proj_perf = shift_preview[opp_party_name]['perf_proj']
    opp_total_perf = opp_gdp_perf + opp_proj_perf
    
    # 🚀 動態判定思辨正確或錯誤
    my_gdp_label = "思辨正確" if my_is_ruling_in_sim else "思辨錯誤"
    opp_gdp_label = "思辨錯誤" if my_is_ruling_in_sim else "思辨正確"
    
    my_proj_label = "思辨正確" if my_is_h_in_sim else "思辨錯誤"
    opp_proj_label = "思辨錯誤" if my_is_h_in_sim else "思辨正確"

    prob = shift_preview['correct_prob']
    o_gdp_pct = ((res['est_gdp'] - game.gdp) / max(1.0, game.gdp)) * 100.0
    
    def fmt_roi(val): return "∞%" if val == float('inf') else f"{val:+.1f}%"

    st.markdown(f"1. {t('我方預估總淨利', 'Our Est. Net Profit')}: **{my_net:.1f}** (專案 ROI: {fmt_roi(my_roi)})")
    st.markdown(f"2. {t('對方預估總淨利', 'Opp. Est. Net Profit')}: **{opp_net:.1f}** (專案 ROI: {fmt_roi(opp_roi)})")
    
    # 🚀 將思辨歸因率與 100% 完工提示直接內嵌在數值旁邊
    st.markdown(f"3. {t('預期產生總支持量', 'Total Expected Support')}:")
    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;🔹 **我方總和: `{my_total_perf:+.1f}`** *(大環境: {my_gdp_perf:+.1f} ({my_gdp_label} {prob*100:.1f}%) | 專案: {my_proj_perf:+.1f} ({my_proj_label} / 若 100% 完工))*")
    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;🔸 **對手總和: `{opp_total_perf:+.1f}`** *(大環境: {opp_gdp_perf:+.1f} ({opp_gdp_label} {prob*100:.1f}%) | 專案: {opp_proj_perf:+.1f} ({opp_proj_label} / 若 100% 完工))*")
    
    st.markdown(f"4. {t('預期 GDP 變化', 'Expected GDP Shift')}: {game.gdp:.1f} ➔ **{res['est_gdp']:.1f}** ({o_gdp_pct:+.2f}%)")
    
    is_self_draft = (plan.get('author_party') == view_party.name)
    
    diff = cl_decay - tt_decay
    if abs(diff) > 0.3: 
        light = "🔴"
        if is_self_draft:
            risk_txt = t("長官，這是我們精心設計的「反差紅利」方案。", "Sir, this is our contrast bonus strategy.")
        else:
            risk_txt = t("警告！對手正試圖操弄選民預期心理！", "Warning! Opponent is manipulating expectations!")
    elif abs(diff) > 0.1: light, risk_txt = "🟡", t("中度預期誤差", "Medium Expectation Gap")
    else: light, risk_txt = "🟢", t("誠實且精準", "Honest and Accurate")
        
    st.markdown(f"5. {t('衰退值判讀', 'Drop Analysis')}: {light} {risk_txt} (公告: {cl_decay:.3f} / 智庫: {tt_decay:.3f})")
    
    diff_c = cl_cost - tt_unit_cost
    if abs(diff_c) > 0.5:
        light_c = "🔴"
        if is_self_draft:
            risk_txt_c = t("長官，這份定價為後續行動預留了極大空間。", "Understood sir, pricing for future options.")
        else:
            risk_txt_c = t("此定價與我方（模擬執行）成本嚴重脫節！", "This price is detached from our simulated costs!")
    elif abs(diff_c) > 0.2: light_c, risk_txt_c = "🟡", t("單價偏離基準", "Price Deviation")
    else: light_c, risk_txt_c = "🟢", t("符合市場行情", "Fair Market Value")

    st.markdown(f"6. {t('建設單價判讀', 'Unit Cost Analysis')}: {light_c} {risk_txt_c} (公告: {cl_cost:.2f} / 智庫基準: {tt_unit_cost:.2f})")

    st.markdown("---")
    st.markdown(f"#### {title}")
    conv_rate = cfg.get('GDP_CONVERSION_RATE', 0.2)
    equiv_infra_loss = (game.gdp * (cl_decay * cfg.get('DECAY_WEIGHT_MULT', 0.05))) / conv_rate
    st.write(f"**{t('公告衰退率', 'Claimed Decay')}:** {cl_decay:.3f} **({t(f'相當於 {equiv_infra_loss:.1f} 建設損失', f'Equivalent to {equiv_infra_loss:.1f} loss')})**")
    st.write(f"**{t('計畫達成獎勵金', 'Plan Reward')}:** {plan['proj_fund']:.1f} | **{t('計畫總效益', 'Plan Total Benefit')}:** {plan['bid_cost']:.1f}")
    
    if simulate_swap:
        st.info(f"🔧 **{t('模擬執行方出資', 'Simulated H-System Pays')}:** {t('總額', 'Total')} {eval_req_cost:.1f} ({t('監管出資', 'R-Pays')}: {eval_r_pays:.1f} | {t('執行出資', 'H-Pays')}: {eval_h_pays:.1f})")
    else:
        st.write(f"**{t('出資總額', 'Total Req. Cost')}:** {eval_req_cost:.1f} ({t('監管出資', 'R-Pays')}: {eval_r_pays:.1f} | {t('執行出資', 'H-Pays')}: {eval_h_pays:.1f})")
