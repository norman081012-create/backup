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

def calc_unit_cost(cfg, gdp, build_abi, drop_rate_pct):
    b_norm = max(0.01, build_abi / 10.0)
    inflation = max(0.0, (gdp - cfg.get('CURRENT_GDP', 5000.0)) / cfg.get('GDP_INFLATION_DIVISOR', 10000.0))
    decay_norm = drop_rate_pct / 100.0
    base_cost = (0.5 / b_norm) * (2 ** (2 * decay_norm - 1))
    return base_cost * (1 + inflation)

def calc_economy(cfg, gdp, budget_t, proj_fund, bid_cost, build_abi, forecast_drop, corr_amt=0.0, crony_base=0.0, override_unit_cost=None):
    l_gdp = gdp * (forecast_drop / 100.0)
    
    if override_unit_cost is not None:
        unit_cost = override_unit_cost
    else:
        unit_cost = calc_unit_cost(cfg, gdp, build_abi, forecast_drop)
        
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

def calc_support_amounts(cfg, hp, rp, ruling_party_name, new_gdp, curr_gdp, ha, ra, claimed_drop, sanity, emotion, bid_cost, c_net):
    # 1. 社會基底濾鏡
    crit_think = sanity / 100.0       # 思辨度
    canned_edu = 1.0 - crit_think     # 填鴨度
    emo_val = emotion / 100.0         # 情緒度
    S = max(0.0, 1.0 + crit_think - emo_val) # 理智濾鏡
    
    # 2. 黨媒能力 (受填鴨度絕對放大)
    h_media_raw = hp.media_ability / 10.0
    r_media_raw = rp.media_ability / 10.0
    h_media = h_media_raw * (1.0 + canned_edu)
    r_media = r_media_raw * (1.0 + canned_edu)
    
    # 3. 達標率計算 (當權看GDP，執行看標案)
    claimed_gdp_change = -curr_gdp * (claimed_drop / 100.0)
    actual_gdp_change = new_gdp - curr_gdp
    perf_ruling = (actual_gdp_change - claimed_gdp_change) / max(1.0, abs(claimed_gdp_change))
    
    perf_exec = (c_net - bid_cost) / max(1.0, bid_cost)
    
    # 4. 基礎政績支持量
    weight = 1000.0
    def get_perf_score(perf, media, is_exec):
        bonus = 1.2 if is_exec else 1.0
        return perf * weight * S * (1.0 + media) * max(0.1, 1.0 - canned_edu) * (1.0 + crit_think) * bonus
    
    ruling_score_raw = get_perf_score(perf_ruling, r_media if rp.name == ruling_party_name else h_media, False)
    exec_score_raw = get_perf_score(perf_exec, h_media, True)
    
    h_perf_final = exec_score_raw
    r_perf_final = ruling_score_raw if rp.name == ruling_party_name else 0.0
    
    # 若 H 也是執政黨，分數合併
    if hp.name == ruling_party_name: h_perf_final += ruling_score_raw
    
    # 5. 搶功與甩鍋機制 (依賴情緒與黨媒)
    # H 黨視角
    if h_perf_final < 0: # 甩鍋給 R
        scapegoat_rate = min(1.0, h_media * emo_val * max(0.0, 1.0 - crit_think))
        blamed = abs(h_perf_final) * scapegoat_rate
        h_perf_final += blamed
        r_perf_final -= blamed
    elif h_perf_final > 0 and hp.name != ruling_party_name and ruling_score_raw > 0: # 搶 R 的功勞
        steal_rate = min(1.0, h_media * emo_val)
        stolen = ruling_score_raw * steal_rate
        h_perf_final += stolen
        r_perf_final -= stolen
        
    # R 黨視角
    if r_perf_final < 0: # 甩鍋給 H
        scapegoat_rate = min(1.0, r_media * emo_val * max(0.0, 1.0 - crit_think))
        blamed = abs(r_perf_final) * scapegoat_rate
        r_perf_final += blamed
        h_perf_final -= blamed
        
    # 6. 競選造勢 (吃情緒與填鴨紅利)
    def get_camp_score(budget, media):
        return budget * media * (1.0 + emo_val) * max(0.0, 1.0 + canned_edu - crit_think)
    
    h_camp = get_camp_score(float(ha.get('camp', 0)), h_media)
    r_camp = get_camp_score(float(ra.get('camp', 0)), r_media)
    
    # 7. 監管媒體審查 (核彈級扼流圈)
    censor_budget = float(ra.get('judicial', 0))
    r_intel = rp.investigate_ability / 10.0
    censor_param = max(0.1, 1.0 - ((censor_budget / max(1.0, rp.wealth)) * (1.0 + r_intel)))
    
    # 審查壓制 H 黨所有正向分數
    if h_perf_final > 0: h_perf_final *= censor_param
    h_camp *= censor_param
    
    # 8. 審查民意反噬 (作用力與反作用力)
    h_total_support = (hp.support / 100.0) * 10000.0 # 粗估總體積
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
    
    res = calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], build_abi, tt_drop)
    my_is_h = (view_party.name == game.h_role_party.name)
    
    lines = []
    lines.append(f"**我方預估試算完成。由於民意系統已轉為支持量遞減陣列，詳細的 S濾鏡與搶功甩鍋結算，請參考年度結算報告。**")
    lines.append(f"**預期 GDP 變化:** `{res['est_gdp']:.1f}`")
    lines.append(f"> 估算建設淨值 (C_net): {res['c_net']:.1f} / 標案承諾 (Bid_cost): {plan['bid_cost']:.1f}")
    
    return lines
