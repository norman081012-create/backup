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

def calc_unit_cost(cfg, gdp, build_abi, decay):
    b_norm = max(0.01, build_abi / 10.0)
    inflation = gdp / cfg.get('GDP_INFLATION_DIVISOR', 10000.0)
    base_cost = (0.5 / b_norm) * (2 ** (2 * decay - 1))
    return base_cost * (1 + inflation)

def calc_economy(cfg, gdp, budget_t, proj_fund, bid_cost, build_abi, forecast_decay, corr_amt=0.0, crony_base=0.0, override_unit_cost=None):
    l_gdp = gdp * forecast_decay * 0.072
    
    if override_unit_cost is not None:
        unit_cost = override_unit_cost
    else:
        unit_cost = calc_unit_cost(cfg, gdp, build_abi, forecast_decay)
        
    req_cost = bid_cost * unit_cost
    available_fund = max(0.0, proj_fund - corr_amt)
    
    if req_cost <= available_fund:
        act_fund = req_cost
        c_net = float(bid_cost)
        h_idx = 1.0
    else:
        act_fund = available_fund
        c_net = act_fund / max(0.01, unit_cost)
        h_idx = c_net / max(1.0, float(bid_cost))

    payout_h = min(budget_t, proj_fund * h_idx)
    total_bonus_deduction = budget_t * ((cfg['BASE_INCOME_RATIO'] * 2) + cfg['RULING_BONUS_RATIO'])
    payout_r = max(0.0, budget_t - total_bonus_deduction - proj_fund)
    
    est_gdp = max(0.0, gdp - l_gdp + c_net)
    h_project_profit = payout_h - act_fund
    
    return {
        'est_gdp': est_gdp, 'payout_h': payout_h, 'payout_r': payout_r,
        'h_idx': h_idx, 'c_net': c_net, 'l_gdp': l_gdp, 
        'unit_cost': unit_cost, 'act_fund': act_fund, 
        'h_project_profit': h_project_profit, 'req_cost': req_cost
    }

def calc_support_shift(cfg, hp, rp, ruling_party_name, payout_h, new_gdp, proj_fund, curr_gdp, ha, ra, h_idx, claimed_decay, eval_decay, sanity, emotion):
    true_expected_gdp = max(0.0, curr_gdp - (curr_gdp * eval_decay * 0.072))
    public_expected_gdp = max(0.0, curr_gdp - (curr_gdp * claimed_decay * 0.072))

    base_ruling_perf = (new_gdp - true_expected_gdp) / max(1.0, curr_gdp)
    claimed_weight = cfg.get('CLAIMED_DECAY_WEIGHT', 0.2)
    claim_bonus = (true_expected_gdp - public_expected_gdp) / max(1.0, curr_gdp) * claimed_weight
    
    ruling_perf_val = base_ruling_perf + claim_bonus
    h_perf_val = h_idx - 1.0
    
    h_raw_perf = h_perf_val + (ruling_perf_val if hp.name == ruling_party_name else 0)
    r_raw_perf = ruling_perf_val if rp.name == ruling_party_name else 0

    # [修改] 媒體審查邏輯：僅打壓對手黨媒
    r_judicial = ra.get('judicial', 0); h_judicial = ha.get('judicial', 0)
    opp_media_penalty_r = min(0.8, r_judicial / 1000.0) 
    opp_media_penalty_h = min(0.8, h_judicial / 1000.0) 
    
    effective_h_media = hp.media_ability * (1.0 - opp_media_penalty_r)
    effective_r_media = rp.media_ability * (1.0 - opp_media_penalty_h)

    S = (sanity / 100.0) * (1.0 - (emotion / 100.0))
    S = max(0.0, min(1.0, S))

    h_media_power = ha.get('media', 0) * effective_h_media * cfg['H_MEDIA_BONUS']
    r_media_power = ra.get('media', 0) * effective_r_media
    norm_M_H = (h_media_power - r_media_power) / 1000.0
    norm_M_R = -norm_M_H

    base_h_perf = h_raw_perf * cfg['PERF_IMPACT_BASE']
    base_r_perf = r_raw_perf * cfg['PERF_IMPACT_BASE']

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

    # [修改] 打壓民調反噬邏輯：扣除民調強度依據對手當前支持度計算
    r_jud_penalty = r_judicial * 0.05 * (hp.support / 100.0)
    h_jud_penalty = h_judicial * 0.05 * (rp.support / 100.0)
    
    net_shift_H = (total_perf_shift_H + camp_shift_H + r_jud_penalty - h_jud_penalty) * cfg['SUPPORT_CONVERSION_RATE']
    act_h_shift = net_shift_H * ((100.0 - hp.support) / 100.0) if net_shift_H > 0 else net_shift_H * (hp.support / 100.0)
    
    return {'actual_shift': act_h_shift, 'h_perf': h_perf_val * 100.0, 'r_perf': ruling_perf_val * 100.0, 'norm_M_H': norm_M_H, 'S': S}

def get_formula_explanation(game, view_party, plan, cfg):
    tt_decay = view_party.current_forecast
    build_abi = game.h_role_party.build_ability
    
    res = calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], build_abi, tt_decay)
    
    my_is_h = (view_party.name == game.h_role_party.name)
    
    h_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == game.h_role_party.name else 0))
    r_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == game.r_role_party.name else 0))
    
    h_profit = h_base + res['payout_h'] - res['act_fund'] + plan['r_pays']
    r_profit = r_base + res['payout_r'] - plan['r_pays']
    
    my_profit = h_profit if my_is_h else r_profit
    opp_profit = r_profit if my_is_h else h_profit
    
    lines = []
    
    lines.append(f"**我方預估收益:** `{my_profit:.1f}`")
    if my_is_h:
        lines.append(f"> 公式: (基本額 {h_base:.1f} + 計畫獎勵 {res['payout_h']:.1f} - 工程成本 {res['act_fund']:.1f}) + 監管補貼 {plan['r_pays']:.1f} = {my_profit:.1f}")
    else:
        lines.append(f"> 公式: 基本額 {r_base:.1f} + 國庫剩餘 {res['payout_r']:.1f} - 提案出資 {plan['r_pays']:.1f} = {my_profit:.1f}")

    lines.append(f"**對方預估收益:** `{opp_profit:.1f}`")
    if not my_is_h:
        lines.append(f"> 公式: (基本額 {h_base:.1f} + 計畫獎勵 {res['payout_h']:.1f} - 工程成本 {res['act_fund']:.1f}) + 監管補貼 {plan['r_pays']:.1f} = {opp_profit:.1f}")
    else:
        lines.append(f"> 公式: 基本額 {r_base:.1f} + 國庫剩餘 {res['payout_r']:.1f} - 提案出資 {plan['r_pays']:.1f} = {opp_profit:.1f}")

    ha_dummy = {'media': 0, 'camp': 0, 'incite': 0, 'judicial': 0}
    ra_dummy = {'media': 0, 'camp': 0, 'incite': 0, 'judicial': 0}
    
    shift = calc_support_shift(cfg, game.h_role_party, game.r_role_party, game.ruling_party.name, res['payout_h'], res['est_gdp'], plan['proj_fund'], game.gdp, ha_dummy, ra_dummy, res['h_idx'], plan.get('claimed_decay', 0.0), tt_decay, game.sanity, game.emotion)
    my_sup = shift['actual_shift'] if my_is_h else -shift['actual_shift']
    gdp_diff = res['est_gdp'] - game.gdp

    lines.append(f"**支持度變化預估:** `{my_sup:+.2f}%`")
    lines.append(f"> 公式: [H政績 {shift['h_perf']:.1f} 與 R政績 {shift['r_perf']:.1f} + 雙方媒體/競選攻防估算 {shift['norm_M_H']:.2f}] × 理智乘數S {shift['S']:.2f} × 轉換率 {cfg['SUPPORT_CONVERSION_RATE']}")

    lines.append(f"**預期 GDP 變化:** `{res['est_gdp']:.1f} ({gdp_diff:+.1f})`")
    lines.append(f"> 公式: 當前GDP {game.gdp:.1f} - 自然衰退量 {res['l_gdp']:.1f} + 淨建設量 {res['c_net']:.1f} = {res['est_gdp']:.1f}")

    return lines
