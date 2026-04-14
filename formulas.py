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

# [核心修正] 新增 h_wealth 參數，代表執行方當前的可用黨產
def calc_economy(cfg, gdp, budget_t, proj_fund, bid_cost, build_abi, forecast_decay, corr_amt=0.0, crony_base=0.0, override_unit_cost=None, r_pays=0.0, h_wealth=0.0):
    l_gdp = gdp * (forecast_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
    
    if override_unit_cost is not None:
        unit_cost = override_unit_cost
    else:
        unit_cost = calc_unit_cost(cfg, gdp, build_abi, forecast_decay)
        
    req_cost = bid_cost * unit_cost
    
    # [核心修正] 執行方能動用的總資金 = 計畫獎勵金 + 監管補貼 - 貪污款 + 【執行方自己的黨產老本】
    available_fund = max(0.0, proj_fund + r_pays - corr_amt + h_wealth)
    
    # 判斷這筆總資金夠不夠付真實工程款
    if req_cost <= available_fund:
        act_fund = req_cost
        c_net = float(bid_cost)
        h_idx = 1.0
    else:
        # 如果連老本都賠進去還是不夠，那工程就會按照比例爛尾
        act_fund = available_fund
        c_net = act_fund / max(0.01, unit_cost)
        h_idx = c_net / max(1.0, float(bid_cost))

    payout_h = min(budget_t, proj_fund * h_idx)
    total_bonus_deduction = budget_t * ((cfg['BASE_INCOME_RATIO'] * 2) + cfg['RULING_BONUS_RATIO'])
    payout_r = max(0.0, budget_t - total_bonus_deduction - proj_fund)
    
    est_gdp = max(0.0, gdp - l_gdp + (c_net * cfg.get('GDP_CONVERSION_RATE', 0.2)))
    
    # 結算 H 黨的專案淨利潤
    # 注意：這裡不扣除 h_wealth，因為 h_wealth 只是用來計算「能不能蓋出來」的資金池上限。
    # 實際付出的成本是 act_fund，所以淨利依然是 (收到的錢 - 付出的錢)。如果 act_fund 大於收到的錢，這筆淨利就會是負的（代表燒了黨產）。
    h_project_profit = payout_h + r_pays - act_fund
    
    return {
        'est_gdp': est_gdp, 'payout_h': payout_h, 'payout_r': payout_r,
        'h_idx': h_idx, 'c_net': c_net, 'l_gdp': l_gdp, 
        'unit_cost': unit_cost, 'act_fund': act_fund, 
        'h_project_profit': h_project_profit, 'req_cost': req_cost
    }

def calc_performance_amounts(cfg, hp, rp, ruling_party_name, new_gdp, curr_gdp, claimed_decay, sanity, emotion, bid_cost, c_net):
    expected_drop_pct = claimed_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE']
    expected_drop_amt = curr_gdp * expected_drop_pct
    actual_drop_amt = curr_gdp - new_gdp
    
    perf_const = 0.01 
    
    if expected_drop_amt > 0.001:
        gdp_perf_base = - (actual_drop_amt / expected_drop_amt) * curr_gdp * perf_const
    else:
        gdp_perf_base = - actual_drop_amt * perf_const
        
    crit_think = sanity / 100.0
    emo_val = emotion / 100.0
    s_filter = max(0.0, min(1.0, crit_think * (1.0 - emo_val * 0.5))) 
    
    shifts = {hp.name: {'perf': 0.0, 'camp': 0.0, 'backlash': 0.0}, 
              rp.name: {'perf': 0.0, 'camp': 0.0, 'backlash': 0.0}}
              
    ruling_gdp_perf = gdp_perf_base * s_filter
    exec_gdp_perf = gdp_perf_base * (1.0 - s_filter)
    
    shifts[ruling_party_name]['perf'] += ruling_gdp_perf
    shifts[hp.name]['perf'] += exec_gdp_perf
    
    project_perf_base = (c_net / max(1.0, bid_cost)) * curr_gdp * perf_const
    shifts[hp.name]['perf'] += project_perf_base
    
    shifts['project_perf'] = project_perf_base
    
    return shifts

def get_formula_explanation(game, view_party, plan, cfg):
    tt_drop = view_party.current_forecast
    build_abi = game.h_role_party.build_ability
    # 這裡也要補上 h_wealth 的預設傳遞，避免報錯
    res = calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], build_abi, tt_drop, r_pays=plan.get('r_pays', 0.0), h_wealth=game.h_role_party.wealth)
    
    lines = []
    lines.append(f"**我方預估試算完成。**")
    lines.append(f"**預期 GDP 變化:** `{res['est_gdp']:.1f}`")
    lines.append(f"> 估算建設淨值 (C_net): {res['c_net']:.1f} / 標案承諾 (Bid_cost): {plan['bid_cost']:.1f}")
    return lines
