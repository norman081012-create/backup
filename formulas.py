# ==========================================
# formulas.py
# 負責核心無狀態的純數學模型計算
# ==========================================
import math

def calc_log_gain(invest_amount, base_cost=50.0):
    return math.log2(1 + (invest_amount / base_cost)) if invest_amount > 0 else 0.0

def get_ability_maintenance(ability, cfg):
    # 維護費從0開始，0即為0成本維護費
    return max(0, ability * cfg['MAINTENANCE_RATE'])

def calculate_upgrade_cost(current, target, build_ability=0.0):
    # 工程處(A_build)讓各部門能力提升效率增加（打折）
    base_cost = max(0, (2**(target - current) - 1) * 50) if target > current else 0
    discount_factor = 1.0 + (build_ability * 0.1)
    return base_cost / discount_factor

def calc_economy(cfg, gdp, budget_t, proj_fund, bid_cost, build_abi, forecast_decay, corr_amt=0.0, crony_base=0.0):
    # 1. 衰退與阻力 (套用大幅調降後的阻力倍率)
    r_decay = forecast_decay * 0.072
    l_gdp = gdp * r_decay
    res_mult = cfg.get('RESISTANCE_MULT', 1.0)
    resistance = l_gdp * res_mult
    
    # 2. 實質建設產出
    act_fund = max(0.0, proj_fund - corr_amt - crony_base)
    gross = act_fund * (build_abi / 10.0) 
    c_net = max(0.0, gross - resistance)
    
    # 3. 達標率與跨期分潤 (核心邏輯：執行系統拿 總額 × 達標率，最高拿盡當年預算，剩餘給監管系統)
    h_idx = c_net / max(1.0, float(bid_cost))
    payout_h = min(budget_t, proj_fund * h_idx)
    payout_r = max(0.0, budget_t - payout_h)
    
    # 4. GDP 更新
    est_gdp = max(0.0, gdp - l_gdp + c_net)
    
    return {
        'est_gdp': est_gdp, 'payout_h': payout_h, 'payout_r': payout_r,
        'h_idx': h_idx, 'c_net': c_net, 'l_gdp': l_gdp, 
        'resistance': resistance, 'gross': gross, 'r_decay': r_decay,
        'act_fund': act_fund
    }

def calc_support_shift(cfg, hp, rp, payout_h, new_gdp, proj_fund, curr_gdp, ha, ra, h_idx, claimed_decay, sanity, emotion):
    r_judicial = ra.get('judicial', 0)
    jud_factor = min(0.5, r_judicial / 500.0) 
    
    effective_h_media = hp.media_ability * (1 - jud_factor)
    effective_r_media = rp.media_ability * (1 - jud_factor)

    # 1. 理智乘數 (S) = 思辨度 * (1 - 情緒遮蔽)
    S = (sanity / 100.0) * (1.0 - (emotion / 100.0))
    S = max(0.0, min(1.0, S))

    # 2. 媒體對抗值 (Delta M)
    h_media_power = ha.get('media', 0) * effective_h_media * cfg['H_MEDIA_BONUS']
    r_media_power = ra.get('media', 0) * effective_r_media
    norm_M_H = (h_media_power - r_media_power) / 1000.0
    norm_M_R = -norm_M_H

    # 3. 政績評估基準 (V)
    public_expected_gdp = max(0.0, curr_gdp - (curr_gdp * claimed_decay * 0.072))
    r_perf_val = (new_gdp - public_expected_gdp) / max(1.0, curr_gdp)
    h_perf_val = h_idx - 1.0

    base_h_perf = h_perf_val * cfg['PERF_IMPACT_BASE']
    base_r_perf = r_perf_val * cfg['PERF_IMPACT_BASE']

    h_gain = 0.0
    r_gain = 0.0

    # === 四大政績影響邏輯 ===
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

    # 4. 競選造勢 (無腦砸錢洗腦)
    h_camp_pow = ha.get('camp', 0) * effective_h_media
    r_camp_pow = ra.get('camp', 0) * effective_r_media
    camp_shift_H = (h_camp_pow - r_camp_pow) * (1.0 - S) * 0.05 

    # 5. 總結算
    r_jud_penalty = r_judicial * 0.1
    net_shift_H = (total_perf_shift_H + camp_shift_H + r_jud_penalty) * cfg['SUPPORT_CONVERSION_RATE']
    
    act_h_shift = net_shift_H * ((100.0 - hp.support) / 100.0) if net_shift_H > 0 else net_shift_H * (hp.support / 100.0)
    
    return {
        'actual_shift': act_h_shift, 
        'h_perf': h_perf_val * 100.0, 
        'r_perf': r_perf_val * 100.0
    }
