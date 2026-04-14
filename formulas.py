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
    inflation = max(0.0, (gdp - cfg.get('CURRENT_GDP', 5000.0)) / cfg.get('GDP_INFLATION_DIVISOR', 10000.0))
    base_cost = (0.5 / b_norm) * (2 ** (2 * decay - 1))
    return base_cost * (1 + inflation)

def calc_economy(cfg, gdp, budget_t, proj_fund, bid_cost, build_abi, forecast_decay, corr_amt=0.0, crony_base=0.0, override_unit_cost=None, r_pays=0.0):
    l_gdp = gdp * (forecast_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
    
    if override_unit_cost is not None:
        unit_cost = override_unit_cost
    else:
        unit_cost = calc_unit_cost(cfg, gdp, build_abi, forecast_decay)
        
    req_cost = bid_cost * unit_cost
    available_fund = max(0.0, proj_fund + r_pays - corr_amt)
    
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
    h_project_profit = payout_h + r_pays - act_fund
    
    return {
        'est_gdp': est_gdp, 'payout_h': payout_h, 'payout_r': payout_r,
        'h_idx': h_idx, 'c_net': c_net, 'l_gdp': l_gdp, 
        'unit_cost': unit_cost, 'act_fund': act_fund, 
        'h_project_profit': h_project_profit, 'req_cost': req_cost
    }

def calc_performance_amounts(cfg, hp, rp, ruling_party_name, new_gdp, curr_gdp, claimed_decay, sanity, emotion, bid_cost, c_net):
    # 1. 預期經濟跌幅與實際跌幅
    expected_drop_pct = claimed_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE']
    expected_drop_amt = curr_gdp * expected_drop_pct
    actual_drop_amt = curr_gdp - new_gdp
    
    perf_const = 0.01 # 基礎常數
    
    # 2. GDP政績基準
    if expected_drop_amt > 0.001:
        gdp_perf_base = - (actual_drop_amt / expected_drop_amt) * curr_gdp * perf_const
    else:
        gdp_perf_base = - actual_drop_amt * perf_const
        
    # 3. 思辨與情緒矯正 (S濾鏡)
    crit_think = sanity / 100.0
    emo_val = emotion / 100.0
    s_filter = max(0.0, min(1.0, crit_think * (1.0 - emo_val * 0.5))) 
    
    shifts = {hp.name: {'perf': 0.0, 'camp': 0.0, 'backlash': 0.0}, 
              rp.name: {'perf': 0.0, 'camp': 0.0, 'backlash': 0.0}}
              
    # 4. 分配 GDP 大環境政績
    ruling_gdp_perf = gdp_perf_base * s_filter
    exec_gdp_perf = gdp_perf_base * (1.0 - s_filter)
    
    shifts[ruling_party_name]['perf'] += ruling_gdp_perf
    shifts[hp.name]['perf'] += exec_gdp_perf
    
    # 5. 標案達標政績 (記錄並疊加)
    project_perf_base = (c_net / max(1.0, bid_cost)) * curr_gdp * perf_const
    shifts[hp.name]['perf'] += project_perf_base
    
    # 暴露出履約政績，讓 UI 可以在 Phase 1 選擇將它剝離顯示
    shifts['project_perf'] = project_perf_base
    
    return shifts

def get_formula_explanation(game, view_party, plan, cfg):
    tt_drop = view_party.current_forecast
    build_abi = game.h_role_party.build_ability
    res = calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], build_abi, tt_drop, r_pays=plan.get('r_pays', 0.0))
    
    lines = []
    lines.append(f"**我方預估試算完成。**")
    lines.append(f"**預期 GDP 變化:** `{res['est_gdp']:.1f}`")
    lines.append(f"> 估算建設淨值 (C_net): {res['c_net']:.1f} / 標案承諾 (Bid_cost): {plan['bid_cost']:.1f}")
    return lines
