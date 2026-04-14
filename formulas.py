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
    
    # [修正] 可動用資金必須包含監管系統給的補貼
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
    
    # [修正] H黨的專案淨利潤 = 收到的獎勵 + 收到的補貼 - 實際付給工程的費用
    h_project_profit = payout_h + r_pays - act_fund
    
    return {
        'est_gdp': est_gdp, 'payout_h': payout_h, 'payout_r': payout_r,
        'h_idx': h_idx, 'c_net': c_net, 'l_gdp': l_gdp, 
        'unit_cost': unit_cost, 'act_fund': act_fund, 
        'h_project_profit': h_project_profit, 'req_cost': req_cost
    }

def calc_support_amounts(cfg, hp, rp, ruling_party_name, new_gdp, curr_gdp, ha, ra, claimed_decay, sanity, emotion, bid_cost, c_net, eval_decay):
    crit_think = sanity / 100.0       
    canned_edu = 1.0 - crit_think     
    emo_val = emotion / 100.0         
    S = max(0.0, 1.0 + crit_think - emo_val) 
    
    h_media_raw = hp.media_ability / 10.0
    r_media_raw = rp.media_ability / 10.0
    h_media = h_media_raw * (1.0 + canned_edu)
    r_media = r_media_raw * (1.0 + canned_edu)
    
    true_drop_pct = eval_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE']
    public_drop_pct = claimed_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE']
    true_expected_gdp = max(0.0, curr_gdp - (curr_gdp * true_drop_pct))
    public_expected_gdp = max(0.0, curr_gdp - (curr_gdp * public_drop_pct))

    claimed_gdp_change = public_expected_gdp - curr_gdp
    actual_gdp_change = new_gdp - curr_gdp
    perf_ruling = (actual_gdp_change - claimed_gdp_change) / max(1.0, abs(claimed_gdp_change))
    
    perf_exec = (c_net - bid_cost) / max(1.0, bid_cost)
    
    weight = 1000.0
    def get_perf_score(perf, media, is_exec):
        bonus = 1.2 if is_exec else 1.0
        return perf * weight * S * (1.0 + media) * max(0.1, 1.0 - canned_edu) * (1.0 + crit_think) * bonus
    
    ruling_score_raw = get_perf_score(perf_ruling, r_media if rp.name == ruling_party_name else h_media, False)
    exec_score_raw = get_perf_score(perf_exec, h_media, True)
    
    h_perf_final = exec_score_raw
    r_perf_final = ruling_score_raw if rp.name == ruling_party_name else 0.0
    
    if hp.name == ruling_party_name: h_perf_final += ruling_score_raw
    
    if h_perf_final < 0: 
        scapegoat_rate = min(1.0, h_media * emo_val * max(0.0, 1.0 - crit_think))
        blamed = abs(h_perf_final) * scapegoat_rate
        h_perf_final += blamed
        r_perf_final -= blamed
    elif h_perf_final > 0 and hp.name != ruling_party_name and ruling_score_raw > 0: 
        steal_rate = min(1.0, h_media * emo_val)
        stolen = ruling_score_raw * steal_rate
        h_perf_final += stolen
        r_perf_final -= stolen
        
    if r_perf_final < 0: 
        scapegoat_rate = min(1.0, r_media * emo_val * max(0.0, 1.0 - crit_think))
        blamed = abs(r_perf_final) * scapegoat_rate
        r_perf_final += blamed
        h_perf_final -= blamed
        
    def get_camp_score(budget, media):
        return budget * media * (1.0 + emo_val) * max(0.0, 1.0 + canned_edu - crit_think)
    
    h_camp = get_camp_score(float(ha.get('camp', 0)), h_media)
    r_camp = get_camp_score(float(ra.get('camp', 0)), r_media)
    
    censor_budget = float(ra.get('judicial', 0))
    r_intel = rp.investigate_ability / 10.0
    censor_param = max(0.1, 1.0 - ((censor_budget / max(1.0, rp.wealth)) * (1.0 + r_intel)))
    
    if h_perf_final > 0: h_perf_final *= censor_param
    h_camp *= censor_param
    
    h_total_support = (hp.support / 100.0) * 10000.0 
    backlash_r = 0.0
    if censor_budget > 0:
        backlash_r = -(h_total_support * 0.05 * (1.0 - censor_param) * max(0.1, 1.0 + emo_val + crit_think - canned_edu))

    shifts = {
        hp.name: {'perf': h_perf_final, 'camp': h_camp, 'backlash': 0.0},
        rp.name: {'perf': r_perf_final, 'camp': r_camp, 'backlash': backlash_r}
    }
    
    return shifts

def get_formula_explanation(game, view_party, plan, cfg):
    tt_drop = view_party.current_forecast
    build_abi = game.h_role_party.build_ability
    
    res = calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], build_abi, tt_drop, r_pays=plan.get('r_pays', 0.0))
    
    lines = []
    lines.append(f"**我方預估試算完成。由於民意系統已轉為支持量遞減陣列，詳細的 S濾鏡與搶功甩鍋結算，請參考年度結算報告。**")
    lines.append(f"**預期 GDP 變化:** `{res['est_gdp']:.1f}`")
    lines.append(f"> 估算建設淨值 (C_net): {res['c_net']:.1f} / 標案承諾 (Bid_cost): {plan['bid_cost']:.1f}")
    
    return lines
