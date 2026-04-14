# ==========================================
# formulas.py
# 負責核心無狀態的純數學模型計算
# ==========================================
import math
import i18n
t = i18n.t

def calc_log_gain(invest_amount, base_cost=50.0):
    return math.log2(1 + (invest_amount / base_cost)) if invest_amount > 0 else 0.0

def get_ability_maintenance(ability, cfg):
    return max(0.0, ability * cfg['MAINTENANCE_RATE'])

def calculate_upgrade_cost(current, target, build_ability=0.0):
    base_cost = max(0.0, (2**(target - current) - 1) * 50) if target > current else 0.0
    discount_factor = 1.0 - (build_ability * 0.02)
    return base_cost * max(0.1, discount_factor)

def calc_economy(cfg, gdp, budget_t, proj_fund, bid_cost, build_abi, forecast_decay, corr_amt=0.0, crony_base=0.0):
    r_decay = forecast_decay * 0.072
    l_gdp = gdp * r_decay
    res_mult = cfg.get('RESISTANCE_MULT', 1.0)
    resistance = l_gdp * res_mult
    
    available_fund = max(0.0, proj_fund - corr_amt)
    
    # 精算達標所需成本 (反推)
    req_cost = (bid_cost + resistance) / max(0.01, (build_abi / 10.0))
    
    if req_cost <= available_fund:
        act_fund = req_cost
        c_net = float(bid_cost)
        h_idx = 1.0
    else:
        act_fund = available_fund
        gross = act_fund * (build_abi / 10.0)
        c_net = max(0.0, gross - resistance)
        h_idx = c_net / max(1.0, float(bid_cost))

    payout_h = min(budget_t, proj_fund * h_idx)
    payout_r = max(0.0, budget_t - payout_h)
    est_gdp = max(0.0, gdp - l_gdp + c_net)
    
    h_project_profit = payout_h - act_fund
    
    return {
        'est_gdp': est_gdp, 'payout_h': payout_h, 'payout_r': payout_r,
        'h_idx': h_idx, 'c_net': c_net, 'l_gdp': l_gdp, 
        'resistance': resistance, 'act_fund': act_fund, 
        'h_project_profit': h_project_profit, 'req_cost': req_cost
    }

def calc_support_shift(cfg, hp, rp, payout_h, new_gdp, proj_fund, curr_gdp, ha, ra, h_idx, claimed_decay, sanity, emotion):
    r_judicial = ra.get('judicial', 0); h_judicial = ha.get('judicial', 0)
    jud_factor_total = min(0.8, (r_judicial + h_judicial) / 1000.0) 
    
    effective_h_media = hp.media_ability * (1.0 - jud_factor_total)
    effective_r_media = rp.media_ability * (1.0 - jud_factor_total)

    S = (sanity / 100.0) * (1.0 - (emotion / 100.0))
    S = max(0.0, min(1.0, S))

    h_media_power = ha.get('media', 0) * effective_h_media * cfg['H_MEDIA_BONUS']
    r_media_power = ra.get('media', 0) * effective_r_media
    norm_M_H = (h_media_power - r_media_power) / 1000.0
    norm_M_R = -norm_M_H

    public_expected_gdp = max(0.0, curr_gdp - (curr_gdp * claimed_decay * 0.072))
    r_perf_val = (new_gdp - public_expected_gdp) / max(1.0, curr_gdp)
    h_perf_val = h_idx - 1.0

    base_h_perf = h_perf_val * cfg['PERF_IMPACT_BASE']
    base_r_perf = r_perf_val * cfg['PERF_IMPACT_BASE']

    h_gain = 0.0; r_gain = 0.0
    if base_h_perf >= 0:
        if norm_M_H >= 0: h_gain += base_h_perf * (1.0 + norm_M_H)
        else: r_gain += base_h_perf * abs(norm_M_H) 
    else: 
        if norm_M_R >= 0: r_gain += abs(base_h_perf) * (1.0 + norm_M_R) 
        else: h_gain += abs(base_h_perf) * abs(norm_M_H) 

    if base_r_perf >= 0: 
        if norm_M_R >= 0: r_gain += base_r_perf * (1.0 + norm_M_R) 
        else: h_gain += base_r_perf * abs(norm_M_H) 
    else: 
        if norm_M_H >= 0: h_gain += abs(base_r_perf) * (1.0 + norm_M_H) 
        else: r_gain += abs(base_r_perf) * abs(norm_M_R) 

    total_perf_shift_H = (h_gain - r_gain) * S

    h_camp_pow = ha.get('camp', 0) * effective_h_media
    r_camp_pow = ra.get('camp', 0) * effective_r_media
    camp_shift_H = (h_camp_pow - r_camp_pow) * (1.0 - S) * 0.05 

    r_jud_penalty = r_judicial * 0.05 * (sanity / 100.0)
    h_jud_penalty = h_judicial * 0.05 * (sanity / 100.0)
    
    net_shift_H = (total_perf_shift_H + camp_shift_H + r_jud_penalty - h_jud_penalty) * cfg['SUPPORT_CONVERSION_RATE']
    act_h_shift = net_shift_H * ((100.0 - hp.support) / 100.0) if net_shift_H > 0 else net_shift_H * (hp.support / 100.0)
    
    return {'actual_shift': act_h_shift, 'h_perf': h_perf_val * 100.0, 'r_perf': r_perf_val * 100.0, 'norm_M_H': norm_M_H, 'S': S}

def get_formula_explanation(game, view_party, plan, cfg):
    tt_decay = view_party.current_forecast
    build_abi = game.h_role_party.build_ability
    
    res = calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], build_abi, tt_decay)
    
    my_is_h = (view_party.name == game.h_role_party.name)
    h_base = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == game.h_role_party.name else 0)
    r_base = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == game.r_role_party.name else 0)
    
    h_profit = h_base + res['h_project_profit'] - plan['h_pays']
    r_profit = r_base + res['payout_r'] - plan['r_pays']
    
    my_profit = h_profit if my_is_h else r_profit
    opp_profit = r_profit if my_is_h else h_profit
    
    my_roi = (my_profit / max(1.0, float(plan['h_pays'] if my_is_h else plan['r_pays']))) * 100.0
    opp_roi = (opp_profit / max(1.0, float(plan['r_pays'] if my_is_h else plan['h_pays']))) * 100.0

    ha_dummy = {'media': 0, 'camp': 0, 'incite': 0, 'judicial': 0}
    ra_dummy = {'media': 0, 'camp': 0, 'incite': 0, 'judicial': 0}
    shift = calc_support_shift(cfg, game.h_role_party, game.r_role_party, res['payout_h'], res['est_gdp'], plan['proj_fund'], game.gdp, ha_dummy, ra_dummy, res['h_idx'], plan.get('claimed_decay', 0.0), game.sanity, game.emotion)
    my_sup = shift['actual_shift'] if my_is_h else -shift['actual_shift']
    gdp_diff = res['est_gdp'] - game.gdp

    lines = []
    lines.append("### 📝 智庫分析 (公式與計算推演)")
    
    lines.append(f"**1. 我方預估收益:** `{my_profit:.1f}` (ROI: `{my_roi:.1f}%`)")
    if my_is_h:
        lines.append(f"*(公式: 基礎金 {h_base:.1f} + 標案收益 {res['payout_h']:.1f} - 實際需花費 {res['act_fund']:.1f} - 提案出資 {plan['h_pays']:.1f} = {my_profit:.1f})*")
    else:
        lines.append(f"*(公式: 基礎金 {r_base:.1f} + 國庫剩餘殘值 {res['payout_r']:.1f} - 提案出資 {plan['r_pays']:.1f} = {my_profit:.1f})*")

    lines.append(f"**2. 對方預估收益:** `{opp_profit:.1f}` (ROI: `{opp_roi:.1f}%`)")
    if not my_is_h:
        lines.append(f"*(公式: 基礎金 {h_base:.1f} + 標案收益 {res['payout_h']:.1f} - 實際需花費 {res['act_fund']:.1f} - 對方出資 {plan['h_pays']:.1f} = {opp_profit:.1f})*")
    else:
        lines.append(f"*(公式: 基礎金 {r_base:.1f} + 國庫剩餘殘值 {res['payout_r']:.1f} - 對方出資 {plan['r_pays']:.1f} = {opp_profit:.1f})*")

    lines.append(f"**3. 支持度變化預估:** `{my_sup:+.2f}%`")
    lines.append(f"*(公式: [H政績 {shift['h_perf']:.1f} 與 R政績 {shift['r_perf']:.1f} + 雙方媒體/競選攻防估算 {shift['norm_M_H']:.2f}] × 理智乘數S {shift['S']:.2f} × 轉換率 {cfg['SUPPORT_CONVERSION_RATE']})*")

    lines.append(f"**4. 預期 GDP 變化:** `{gdp_diff:+.1f}`")
    lines.append(f"*(公式: 淨建設量 {res['c_net']:.1f} - [當前GDP {game.gdp:.1f} × 觀測衰退 {tt_decay:.2f} × 0.072] = {gdp_diff:+.1f})*")

    diff = abs(plan.get('claimed_decay', 0.0) - tt_decay)
    if diff > 0.3: light, risk_txt = "🔴", "高"
    elif diff > 0.1: light, risk_txt = "🟡", "中"
    else: light, risk_txt = "🟢", "低"
    lines.append(f"**5. 衰退值差異:** {light} 風險{risk_txt} (公告: `{plan.get('claimed_decay', 0.0):.2f}` / 智庫: `{tt_decay:.2f}`)")

    return lines
