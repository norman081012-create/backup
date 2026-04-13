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
    # 1. 衰退與阻力
    r_decay = forecast_decay * 0.072
    l_gdp = gdp * r_decay
    resistance = l_gdp * 5.0
    
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

def calc_support_shift(cfg, hp, rp, payout_h, new_gdp, proj_fund, curr_gdp, ha, ra):
    r_judicial = ra.get('judicial', 0)
    jud_factor = min(0.5, r_judicial / 500.0) 
    
    effective_h_media = hp.media_ability * (1 - jud_factor)
    effective_r_media = rp.media_ability * (1 - jud_factor)

    # 政績評估基準：標案收益是否超越最初爭取的總額、以及 GDP 成長
    h_perf_val = (payout_h - proj_fund) / max(1.0, float(proj_fund))
    r_perf_val = (new_gdp - curr_gdp) / max(1.0, curr_gdp)

    h_fail_pct = abs(h_perf_val) if h_perf_val < 0 else 0.0
    r_fail_pct = abs(r_perf_val) if r_perf_val < 0 else 0.0

    h_media_pow = ha.get('media', 0) * effective_h_media * cfg['H_MEDIA_BONUS'] * cfg['MEDIA_DIFF']
    r_media_pow = ra.get('media', 0) * effective_r_media * cfg['MEDIA_DIFF']

    h_blame_qty = h_fail_pct * cfg['PERF_IMPACT_BASE'] * max(1.0, r_media_pow * 0.01)
    r_blame_qty = r_fail_pct * cfg['PERF_IMPACT_BASE'] * max(1.0, h_media_pow * 0.01)

    h_camp_pow = ha.get('camp', 0) * effective_h_media * cfg['MEDIA_DIFF']
    r_camp_pow = ra.get('camp', 0) * effective_r_media * cfg['MEDIA_DIFF']
    total_camp_pow = max(1.0, h_camp_pow + r_camp_pow)
    
    h_eff_camp_qty = (h_camp_pow / total_camp_pow) * ha.get('camp', 0)
    r_eff_camp_qty = (r_camp_pow / total_camp_pow) * ra.get('camp', 0)

    h_steal = (ha.get('media', 0) * effective_h_media) / 500.0
    r_steal = (ra.get('media', 0) * effective_r_media) / 500.0

    r_jud_penalty = r_judicial * 0.1

    hp_shift = (h_eff_camp_qty - h_blame_qty + r_blame_qty + h_steal - r_steal) * cfg['SUPPORT_CONVERSION_RATE']
    rp_shift = (r_eff_camp_qty - r_blame_qty + h_blame_qty + r_steal - h_steal - r_jud_penalty) * cfg['SUPPORT_CONVERSION_RATE']

    act_h_shift = hp_shift * ((100.0 - hp.support) / 100.0) if hp_shift > 0 else hp_shift * (hp.support / 100.0)
    
    return {
        'actual_shift': act_h_shift, 
        'h_perf': h_perf_val * 100.0, 
        'r_perf': r_perf_val * 100.0,
        'h_blame_qty': h_blame_qty, 'r_blame_qty': r_blame_qty
    }
