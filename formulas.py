# ==========================================
# formulas.py
# 負責核心無狀態的純數學模型計算，與動態生成 UI 說明文本
# ==========================================
import math
import i18n
t = i18n.t

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
    r_decay = forecast_decay * 0.072
    l_gdp = gdp * r_decay
    res_mult = cfg.get('RESISTANCE_MULT', 1.0)
    resistance = l_gdp * res_mult
    
    act_fund = max(0.0, proj_fund - corr_amt - crony_base)
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
    jud_factor = min(0.5, r_judicial / 500.0) 
    
    effective_h_media = hp.media_ability * (1 - jud_factor)
    effective_r_media = rp.media_ability * (1 - jud_factor)

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

    r_jud_penalty = r_judicial * 0.1
    net_shift_H = (total_perf_shift_H + camp_shift_H + r_jud_penalty) * cfg['SUPPORT_CONVERSION_RATE']
    
    act_h_shift = net_shift_H * ((100.0 - hp.support) / 100.0) if net_shift_H > 0 else net_shift_H * (hp.support / 100.0)
    
    return {
        'actual_shift': act_h_shift, 
        'h_perf': h_perf_val * 100.0, 
        'r_perf': r_perf_val * 100.0
    }

def get_formula_explanation(game, plan, cfg):
    """動態生成 UI 顯示的公式推演字串列表"""
    decay_to_use = game.current_real_decay if game.phase > 1 else plan.get('claimed_decay', game.current_real_decay)
    res = calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], game.h_role_party.build_ability, decay_to_use)
    res_mult = cfg.get('RESISTANCE_MULT', 1.0)
    
    lines = []
    lines.append(t("### 🏛️ 經濟與建設引擎", "### 🏛️ Economic Engine"))
    lines.append(t(f"- **衰退損耗 (L_gdp)** = 當前 GDP ({game.gdp:.1f}) × (衰退值 {decay_to_use:.2f} × 0.072) = `{res['l_gdp']:.1f}`", f"- **Decay Loss** = GDP ({game.gdp:.1f}) × (Decay {decay_to_use:.2f} × 0.072) = `{res['l_gdp']:.1f}`"))
    lines.append(t(f"- **建設阻力 (Resistance)** = 衰退損耗 ({res['l_gdp']:.1f}) × 阻力倍率 {res_mult} = `{res['resistance']:.1f}`", f"- **Resistance** = Decay Loss ({res['l_gdp']:.1f}) × Mult {res_mult} = `{res['resistance']:.1f}`"))
    lines.append(t(f"- **實質投入資金 (Act_Fund)** = 標案總額 ({plan['proj_fund']:.0f}) - 貪污/圖利 = `{res['act_fund']:.0f}`", f"- **Actual Funds** = Total Bid ({plan['proj_fund']:.0f}) - Corruption/Cronyism = `{res['act_fund']:.0f}`"))
    lines.append(t(f"- **毛建設產出 (Gross)** = 實質投入 ({res['act_fund']:.0f}) × (工程處能力 {game.h_role_party.build_ability:.1f} / 10) = `{res['gross']:.0f}`", f"- **Gross Output** = Act Funds ({res['act_fund']:.0f}) × (Build Ability {game.h_role_party.build_ability:.1f} / 10) = `{res['gross']:.0f}`"))
    lines.append(t(f"- **淨建設量 (C_net)** = 毛產出 ({res['gross']:.0f}) - 建設阻力 ({res['resistance']:.1f}) = `{res['c_net']:.0f}`", f"- **Net Construct** = Gross ({res['gross']:.0f}) - Resistance ({res['resistance']:.1f}) = `{res['c_net']:.0f}`"))
    lines.append(t(f"- **達標率 (H_Index)** = 淨建設量 ({res['c_net']:.0f}) / 標案成本 ({plan['bid_cost']:.0f}) = `{res['h_idx']:.2f}`", f"- **H_Index** = Net Construct ({res['c_net']:.0f}) / Bid Cost ({plan['bid_cost']:.0f}) = `{res['h_idx']:.2f}`"))
    lines.append(t(f"- **執行系統收益** = 標案總額 ({plan['proj_fund']:.0f}) × 達標率 (受限於總預算 {game.total_budget:.0f}) = `{res['payout_h']:.0f}`", f"- **H-System Payout** = Total Bid ({plan['proj_fund']:.0f}) × H_Index (Capped by Budget {game.total_budget:.0f}) = `{res['payout_h']:.0f}`"))
    lines.append(t(f"- **監管系統收益** = 總預算 - 執行系統收益 = `{res['payout_r']:.0f}`", f"- **R-System Payout** = Total Budget - H Payout = `{res['payout_r']:.0f}`"))
    
    lines.append(t("### 🎭 民意期望與政績管理", "### 🎭 Expectation Management"))
    public_expected_gdp = max(0.0, game.gdp - (game.gdp * plan.get('claimed_decay', 0.0) * 0.072))
    lines.append(t(f"- **民眾預期 GDP** = 當前 GDP - 宣告衰退損耗 = `{public_expected_gdp:.1f}`", f"- **Public Expected GDP** = Current GDP - Claimed Decay Loss = `{public_expected_gdp:.1f}`"))
    lines.append(t(f"- **監管政績表現** = (最終預測 GDP ({res['est_gdp']:.0f}) - 民眾預期 GDP) / 當前 GDP = `{((res['est_gdp'] - public_expected_gdp) / game.gdp)*100:.1f}%`", f"- **R-System Performance** = (Final Est GDP ({res['est_gdp']:.0f}) - Public Expected GDP) / Current GDP = `{((res['est_gdp'] - public_expected_gdp) / game.gdp)*100:.1f}%`"))
    
    lines.append(t("### 💡 智庫預估推算解析 (標案陷阱與 ROI 暴跌原理)", "### 💡 Think Tank ROI Analysis (The Bid Trap)"))
    lines.append(t("當你看到標案總額極高，要求成本極低時，可能會覺得能輕鬆 100% 達標賺取暴利。但請注意 **大環境的惡意 (建設阻力)** 考量：", "When you see high bid amounts and low cost requirements, you may expect easy 100% completion and massive profit. But consider the **Environmental Resistance**: "))
    lines.append(t(f"1. **打折的毛產出**：即使出資 {plan['proj_fund']:.0f}，工程能力若只有 {game.h_role_party.build_ability:.1f} ({game.h_role_party.build_ability*10:.0f}%)，毛產出也只有 {res['act_fund'] * (game.h_role_party.build_ability/10.0):.0f}。", f"1. **Discounted Gross**: Even if you bid {plan['proj_fund']:.0f}, with {game.h_role_party.build_ability*10:.0f}% engineering ability, Gross Output is only {res['act_fund'] * (game.h_role_party.build_ability/10.0):.0f}."))
    lines.append(t(f"2. **阻力吃掉產出**：毛產出必須先扣除「衰退帶來的建設阻力」，剩下的才是 **淨建設量**。若阻力高達 {res['resistance']:.0f}，淨建設量就只剩 {res['c_net']:.0f}。", f"2. **Resistance Eats Output**: Gross must subtract Decay Resistance. If resistance is {res['resistance']:.0f}, Net Construction is only {res['c_net']:.0f}."))
    lines.append(t(f"3. **真實達標率 (H-Index) 結算**：系統以 {res['c_net']:.0f} (淨建設量) ÷ {plan['bid_cost']:.0f} (標案成本要求) = {res['h_idx']*100:.1f}% 結算達標率。", f"3. **H-Index Calculation**: {res['c_net']:.0f} (Net) ÷ {plan['bid_cost']:.0f} (Cost) = {res['h_idx']*100:.1f}% H-Index."))
    lines.append(t(f"4. **真實結算 ROI**：執行系統最終只能領回 {plan['proj_fund']:.0f} × {res['h_idx']*100:.1f}% = {res['payout_h']:.0f}。這就是監管系統利用「高衰退環境」合法坑殺執行黨的權謀！", f"4. **Deficit Settlement**: H-System only gets {plan['proj_fund']:.0f} × {res['h_idx']*100:.1f}% = {res['payout_h']:.0f}. This is how R-System uses high decay to legally trap H-System!"))
    
    return lines
