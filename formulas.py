# ==========================================
# formulas.py (節錄修改部分)
# ==========================================
import math

# [修改] 套用全新的衰退率轉 GDP 公式
def calc_economy(cfg, gdp, budget_t, proj_fund, bid_cost, build_abi, forecast_decay, corr_amt=0.0, crony_base=0.0, override_unit_cost=None):
    # 公式： GDP * (衰退率 * 權重 + 最低參數)
    l_gdp = gdp * (forecast_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
    
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
    
    est_gdp = max(0.0, gdp - l_gdp + (c_net * cfg.get('GDP_CONVERSION_RATE', 0.2)))
    h_project_profit = payout_h - act_fund
    
    return {
        'est_gdp': est_gdp, 'payout_h': payout_h, 'payout_r': payout_r,
        'h_idx': h_idx, 'c_net': c_net, 'l_gdp': l_gdp, 
        'unit_cost': unit_cost, 'act_fund': act_fund, 
        'h_project_profit': h_project_profit, 'req_cost': req_cost
    }

def calc_support_amounts(cfg, hp, rp, ruling_party_name, new_gdp, curr_gdp, ha, ra, claimed_decay, sanity, emotion, bid_cost, c_net, eval_decay):
    # [修改] 期望值的計算同步套用新衰退公式
    true_drop_pct = eval_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE']
    public_drop_pct = claimed_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE']
    
    true_expected_gdp = max(0.0, curr_gdp - (curr_gdp * true_drop_pct))
    public_expected_gdp = max(0.0, curr_gdp - (curr_gdp * public_drop_pct))
    
    # ...下方保留上一版你確認過的列隊、S濾鏡、搶功與審查反噬計算...
