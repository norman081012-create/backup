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
    discount_factor = max(0.1, discount_factor)
    return base_cost * discount_factor

def calc_economy(cfg, gdp, budget_t, proj_fund, bid_cost, build_abi, forecast_decay, corr_amt=0.0):
    r_decay = forecast_decay * 0.072
    l_gdp = gdp * r_decay
    res_mult = cfg.get('RESISTANCE_MULT', 1.0)
    resistance = l_gdp * res_mult
    
    act_fund = max(0.0, proj_fund - corr_amt)
    gross = act_fund * (build_abi / 10.0) 
    c_net = max(0.0, gross - resistance)
    
    h_idx = c_net / max(1.0, float(bid_cost))
    payout_h = min(budget_t, proj_fund * h_idx)
    payout_r = max(0.0, budget_t - payout_h)
    
    est_gdp = max(0.0, gdp - l_gdp + c_net)
    
    return {
        'est_gdp': est_gdp, 'payout_h': payout_h, 'payout_r': payout_r,
        'h_idx': h_idx, 'c_net': c_net, 'l_gdp': l_gdp, 
        'resistance': resistance, 'gross': gross, 'r_decay': r_decay,
        'act_fund': act_fund
    }

def calc_support_shift(cfg, hp, rp, payout_h, new_gdp, proj_fund, curr_gdp, ha, ra, h_idx, claimed_decay, sanity, emotion):
    r_judicial = ra.get('judicial', 0)
    h_judicial = ha.get('judicial', 0)
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
    
    return {
        'actual_shift': act_h_shift, 
        'h_perf': h_perf_val * 100.0, 
        'r_perf': r_perf_val * 100.0
    }

def get_formula_explanation(game, view_party, plan, cfg):
    tt_decay = view_party.current_forecast
    build_abi = game.h_role_party.build_ability
    
    res = calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], build_abi, tt_decay)
    res_mult = cfg.get('RESISTANCE_MULT', 1.0)
    
    lines = []
    lines.append(t("### 💡 智庫預估推算解析 (核心計算過程)"))
    lines.append(f"以下為智庫基於 **真實標案總額 ({plan['proj_fund']:.1f})**、**真實標案成本 ({plan['bid_cost']:.1f})**、**對手工程處能力 ({build_abi:.1f})** 與 **自身預估衰退值 ({tt_decay:.2f})** 進行之沙盤推演：")
    
    lines.append(f"- **衰退損耗** = 當前 GDP ({game.gdp:.1f}) × (預估衰退 {tt_decay:.2f} × 0.072) = `{res['l_gdp']:.1f}`")
    lines.append(f"- **建設阻力** = 衰退損耗 ({res['l_gdp']:.1f}) × 阻力倍率 {res_mult} = `{res['resistance']:.1f}`")
    lines.append(f"- **實質投入資金** = 標案總額 ({plan['proj_fund']:.1f}) = `{res['act_fund']:.1f}` *(註: 此處無法預知對手潛在貪污)*")
    lines.append(f"- **毛建設產出** = 實質投入 ({res['act_fund']:.1f}) × (對手工程能力 {build_abi:.1f} / 10) = `{res['gross']:.1f}`")
    lines.append(f"- **淨建設量** = 毛產出 ({res['gross']:.1f}) - 建設阻力 ({res['resistance']:.1f}) = `{res['c_net']:.1f}`")
    lines.append(f"- **預估達標率** = 淨建設量 ({res['c_net']:.1f}) / 標案成本 ({plan['bid_cost']:.1f}) = `{res['h_idx']*100:.1f}%`")
    lines.append(f"- **預估執行系統收益** = 標案總額 ({plan['proj_fund']:.1f}) × 達標率 = `{res['payout_h']:.1f}`")
    lines.append(f"- **預估監管系統收益** = 總預算 - 執行系統收益 = `{res['payout_r']:.1f}`")
    
    lines.append(t("### 🎭 民意期望與政績管理"))
    public_expected_gdp = max(0.0, game.gdp - (game.gdp * plan.get('claimed_decay', 0.0) * 0.072))
    lines.append(f"- **民眾預期 GDP** = 當前 GDP - 宣告衰退損耗 = `{public_expected_gdp:.1f}`")
    lines.append(f"- **監管政績表現** = (最終預測 GDP ({res['est_gdp']:.1f}) - 民眾預期 GDP) / 當前 GDP = `{((res['est_gdp'] - public_expected_gdp) / game.gdp)*100:.1f}%`")
    
    return lines
