# ==========================================
# formulas.py
# ==========================================
import math
import random
import numpy as np
import i18n
t = i18n.t

# 📌 全局裝甲權重 (用來調整擊穿難度)
RIGIDITY_WEIGHT = 2.5

def calc_log_gain(invest_amount, base_cost=50.0):
    return math.log2(1 + (invest_amount / base_cost)) if invest_amount > 0 else 0.0

def calc_unit_cost(cfg, gdp, build_abi, decay):
    discount_factor = 1.0 - (build_abi / 10.0) * 0.5 
    inflation = max(0.0, (gdp - cfg.get('CURRENT_GDP', 5000.0)) / cfg.get('GDP_INFLATION_DIVISOR', 10000.0))
    base_cost = 0.85 * (2 ** (2 * decay - 1))
    return base_cost * discount_factor * (1 + inflation)

def calc_fake_ev_dice(total_fake_ev: float, catch_prob: float, fine_mult: float, chunk_size: float = 5.0, unit_cost: float = 1.0):
    if total_fake_ev <= 0 or catch_prob <= 0 or chunk_size == float('inf'):
        return 0.0, total_fake_ev, 0.0, 0.0
        
    num_chunks = int(total_fake_ev / chunk_size)
    remainder = total_fake_ev - (num_chunks * chunk_size)
    
    caught_chunks = float(np.random.binomial(n=num_chunks, p=catch_prob)) if num_chunks > 0 else 0.0
    caught_remainder = remainder if random.random() < catch_prob else 0.0
    
    caught_fake_ev = (caught_chunks * chunk_size) + caught_remainder
    safe_fake_ev = total_fake_ev - caught_fake_ev
    
    caught_value = caught_fake_ev * unit_cost
    fine = caught_value * fine_mult
    
    return caught_fake_ev, safe_fake_ev, caught_value, fine

def calc_economy(cfg, gdp, budget_t, proj_fund, total_bid_cost, build_abi, real_decay, override_unit_cost=None, r_pays=0.0, h_wealth=0.0, c_net_override=None, fake_ev_spent=0.0, fake_ev_safe=0.0, active_projects=None, allocations=None, fake_ev_caught=0.0, current_year=1):
    active_projects = active_projects or []
    allocations = allocations or {}
    
    l_gdp = gdp * (real_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
    unit_cost = override_unit_cost if override_unit_cost is not None else calc_unit_cost(cfg, gdp, build_abi, real_decay)
    
    unit_cost_eff = unit_cost / 1.2
    
    req_cost = total_bid_cost * unit_cost
    available_fund = max(0.0, proj_fund + r_pays + h_wealth)
    
    c_net_real = sum(data.get('real', 0.0) for data in allocations.values())
    total_fake_spent = sum(data.get('fake', 0.0) for data in allocations.values())
    c_net_total = c_net_real + total_fake_spent
    
    h_idx = min(1.0, c_net_total / max(1.0, float(total_bid_cost))) if total_bid_cost > 0 else 0.0
    act_fund = (c_net_real + total_fake_spent * cfg.get('FAKE_EV_COST_RATIO', 0.2)) * unit_cost_eff
    
    scale_down_ratio = 1.0
    if act_fund > available_fund and act_fund > 0:
        scale_down_ratio = available_fund / act_fund
        act_fund = available_fund
        c_net_real *= scale_down_ratio
        total_fake_spent *= scale_down_ratio
        c_net_total = c_net_real + total_fake_spent
        h_idx = min(1.0, c_net_total / max(1.0, float(total_bid_cost))) if total_bid_cost > 0 else 0.0

    payout_h = min(budget_t, proj_fund * h_idx)
    total_bonus_deduction = budget_t * ((cfg['BASE_INCOME_RATIO'] * 2) + cfg['RULING_BONUS_RATIO'])
    payout_r = max(0.0, budget_t - total_bonus_deduction - proj_fund)
    
    total_allocated = sum(d.get('real', 0) + d.get('fake', 0) for d in allocations.values())
    effective_allocs = {}
    for pid, data in allocations.items():
        real_amt = data.get('real', 0.0) * scale_down_ratio
        fake_amt = data.get('fake', 0.0) * scale_down_ratio
        
        # Apply catch penalty to this specific project's fake EV if caught
        total_fake_this_year = sum(d.get('fake', 0.0) * scale_down_ratio for d in allocations.values())
        if fake_ev_caught > 0 and total_fake_this_year > 0:
            caught_ratio = fake_ev_caught / total_fake_this_year
            fake_amt = max(0.0, fake_amt * (1.0 - caught_ratio))
            
        effective_allocs[pid] = {'real': real_amt, 'fake': fake_amt}

    completed_projects = []
    failed_projects = []
    ongoing_projects = []
    total_gdp_addition = 0.0

    for p in active_projects:
        p_copy = dict(p)
        p_copy['investments'] = list(p.get('investments', []))
        
        invested_so_far = sum(inv.get('real', inv['amount']) + inv.get('fake', 0.0) for inv in p_copy['investments'])
        remaining_ev = p_copy['ev'] - invested_so_far
        
        alloc_data = effective_allocs.get(p_copy['id'], {'real': 0.0, 'fake': 0.0})
        alloc_real = alloc_data['real']
        alloc_fake = alloc_data['fake']
        alloc_total = alloc_real + alloc_fake
        
        if alloc_total > 0:
            # Record who invested (we assume Party A and Party B's allocations are handled via their respective turns, but here we just store the amount. The caller handles attribution.)
            p_copy['investments'].append({'year': current_year, 'amount': alloc_total, 'real': alloc_real, 'fake': alloc_fake})
            
        total_invested_now = invested_so_far + alloc_total
        
        if total_invested_now >= p_copy['ev'] * 0.99:
            tot_real = sum(inv.get('real', inv['amount']) for inv in p_copy['investments'])
            tot_fake = sum(inv.get('fake', 0.0) for inv in p_copy['investments'])
            tot_amt = tot_real + tot_fake
            
            quality_ratio = (tot_real + 0.2 * tot_fake) / max(1.0, tot_amt)
            
            p_copy['exec_mult'] *= quality_ratio
            p_copy['macro_mult'] *= quality_ratio
            
            completed_projects.append(p_copy)
            total_gdp_addition += p_copy['ev'] * p_copy['macro_mult'] * cfg.get('GDP_CONVERSION_RATE', 0.2)
        else:
            min_req = remaining_ev * 0.2
            effective_survival_alloc = alloc_real + (alloc_fake * 0.2)
            
            if effective_survival_alloc < min_req - 0.01:
                failed_projects.append(p_copy)
            else:
                ongoing_projects.append(p_copy)
    
    est_gdp = max(0.0, gdp - l_gdp + total_gdp_addition)
    
    cost_real_ev = c_net_real * unit_cost_eff
    cost_fake_ev = (total_fake_spent * cfg.get('FAKE_EV_COST_RATIO', 0.2)) * unit_cost_eff
    
    h_project_profit = payout_h + r_pays - (cost_real_ev + cost_fake_ev)
    
    return {
        'est_gdp': est_gdp, 'payout_h': payout_h, 'payout_r': payout_r,
        'h_idx': h_idx, 'c_net': c_net_real, 'c_net_total': c_net_total, 'l_gdp': l_gdp, 
        'unit_cost': unit_cost_eff, 'act_fund': act_fund, 
        'cost_real_ev': cost_real_ev, 'cost_fake_ev': cost_fake_ev,
        'h_project_profit': h_project_profit, 'req_cost': req_cost,
        'completed_projects': completed_projects,
        'failed_projects': failed_projects,
        'ongoing_projects': ongoing_projects,
        'total_fake_spent': total_fake_spent * scale_down_ratio
    }

def get_depreciated_perf(party, perf_type, current_year):
    """計算特定政黨、特定種類政績，經過 6 年線性衰退後的總和"""
    total = 0.0
    history = party.perf_history[perf_type]
    # Remove items older than 6 years
    history = [item for item in history if (current_year - item['year']) < 6]
    party.perf_history[perf_type] = history
    
    for item in history:
        age = current_year - item['year']
        # 6 年線性衰退 (0年: 100%, 1年: 83.3%, ..., 5年: 16.6%, 6年: 0%)
        retention = max(0.0, (6.0 - age) / 6.0)
        total += item['amount'] * retention
        
    return total

def generate_raw_support(cfg, curr_gdp, est_gdp, claimed_decay, completed_projects, current_year, party_a, party_b, ruling_name):
    # 1. Ruling Perf: 純看 GDP 變化對抗預期
    delta_A = ((est_gdp - curr_gdp) / max(1.0, curr_gdp)) * 100.0
    expected_loss_pct = (claimed_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE']) * 100.0
    delta_E = -expected_loss_pct
    
    gap = delta_A - delta_E
    p_ruling_new = ((delta_A * 0.05) + (gap * 0.15)) * cfg.get('AMMO_MULTIPLIER', 50.0)
    
    # 寫入 Ruling Perf
    for p in [party_a, party_b]:
        if p.name == ruling_name:
            p.perf_history['ruling'].append({'year': current_year, 'amount': p_ruling_new})
            
    # 2. Prop Perf & Exec Perf 結算
    for p_obj in completed_projects:
        author = p_obj.get('author', 'System')
        # Prop Perf = 專案產生的 GDP 變化 %
        prop_perf_new = (p_obj['ev'] * p_obj['macro_mult'] * cfg.get('GDP_CONVERSION_RATE', 0.2)) / max(1.0, curr_gdp) * 100.0 * cfg.get('AMMO_MULTIPLIER', 50.0)
        
        # 寫入 Prop Perf
        for p in [party_a, party_b]:
            if p.name == author:
                p.perf_history['prop'].append({'year': current_year, 'amount': prop_perf_new})

        # Exec Perf = 分配給 EV 投資者 (依比例)
        # 此處簡化：預設全由當年的 Executive 黨投入 (如果你後續支援雙方同時投資專案，可再依 investment 比例拆分)
        # 目前邏輯：在 Phase 2 只有 H-System 能投資專案，所以 Exec Perf 全歸 H-System
        exec_perf_new = prop_perf_new * p_obj['exec_mult'] # Exec 額外乘上執行倍率
        # (在此架構下，外部迴圈會確保傳入正確的 party_a / party_b 供紀錄)
        # 暫時不在此處寫入 Exec Perf，交由外部呼叫者統一寫入 (因為我們需要判斷誰是 H_System)
        
    return p_ruling_new, delta_A, delta_E

def calc_incite_success(base_incite_rolls, current_emotion, is_preview=False):
    if is_preview:
        success_rate = (100.0 - current_emotion) / 100.0
        return base_incite_rolls * success_rate

    successful_incites = 0.0
    temp_emotion = current_emotion
    int_rolls = int(base_incite_rolls)
    
    for _ in range(int_rolls):
        if temp_emotion >= 100.0: break
        success_prob = (100.0 - temp_emotion) / 100.0
        if random.random() < success_prob:
            successful_incites += 1.0
            temp_emotion += 1.0 
            
    return successful_incites

def get_base_rigidity(i, buff_amt=0.0, buff_party=None, h_boundary=100, party_a_name=None):
    x = (i - 100.5) / 99.5
    base_rigidity = 0.95 * (x**2) + 0.05
    if buff_amt > 0 and buff_party and party_a_name:
        belongs_to_A = (i <= h_boundary)
        if (buff_party == party_a_name and belongs_to_A) or (buff_party != party_a_name and not belongs_to_A):
            base_rigidity += buff_amt
    return min(1.0, base_rigidity)

def get_sanity_accuracy(sanity, emotion):
    # 思辨正確率: 0.0 到 1.0 之間
    # Sanity 提供正向，Emotion 提供負向 (除以 200 降低破壞力)
    acc = (sanity / 100.0) - (emotion / 200.0)
    return max(0.01, min(1.0, acc))

def get_perf_rigidity(i, sanity, emotion, buff_amt=0.0, buff_party=None, h_boundary=100, party_a_name=None):
    base_rigidity = get_base_rigidity(i, buff_amt, buff_party, h_boundary, party_a_name)
    sanity_acc = get_sanity_accuracy(sanity, emotion)
    
    # 裝甲 = Base * Weight * (1 - 思辨正確率)
    # 思辨越正確，裝甲越薄 (政績越容易穿透)
    final_rig = base_rigidity * RIGIDITY_WEIGHT * (1.0 - sanity_acc)
    return max(0.01, min(1.0, final_rig))

def get_spin_rigidity(i, sanity, emotion, censor_penalty=0.0, buff_amt=0.0, buff_party=None, h_boundary=100, party_a_name=None):
    base_rigidity = get_base_rigidity(i, buff_amt, buff_party, h_boundary, party_a_name)
    sanity_acc = get_sanity_accuracy(sanity, emotion)
    
    # 裝甲 = Base * Weight * (思辨正確率) * (1 - 媒體審查懲罰)
    # 思辨越正確，裝甲越厚 (越難被公關洗腦)；但會被審查削弱
    final_rig = base_rigidity * RIGIDITY_WEIGHT * sanity_acc * max(0.1, (1.0 - censor_penalty))
    return max(0.01, min(1.0, final_rig))

def run_conquest_split(boundary_B, net_perf_A, net_spin_A, sanity=50.0, emotion=30.0, censor_penalty_A=0.0, censor_penalty_B=0.0, buff_amt=0.0, buff_party=None, party_a_name=None):
    B = int(boundary_B)
    perf_used = 0.0; perf_conquered = 0
    
    # 政績穿透結算
    if net_perf_A > 0:
        sup = net_perf_A
        while sup >= 1.0 and B < 200:
            sup -= 1.0; perf_used += 1.0
            rigidity = get_perf_rigidity(B + 1, sanity, emotion, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B += 1; perf_conquered += 1
    elif net_perf_A < 0:
        sup = abs(net_perf_A)
        while sup >= 1.0 and B > 0:
            sup -= 1.0; perf_used += 1.0
            rigidity = get_perf_rigidity(B, sanity, emotion, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B -= 1; perf_conquered += 1
            
    # 公關洗腦結算 (包含對手的審查懲罰)
    spin_used = 0.0; spin_conquered = 0
    if net_spin_A > 0:
        sup = net_spin_A
        while sup >= 1.0 and B < 200:
            sup -= 1.0; spin_used += 1.0
            # A 攻擊，受 B 選民的護甲抵抗 (此時套用 B 陣營遭受的審查懲罰)
            rigidity = get_spin_rigidity(B + 1, sanity, emotion, censor_penalty_B, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B += 1; spin_conquered += 1
    elif net_spin_A < 0:
        sup = abs(net_spin_A)
        while sup >= 1.0 and B > 0:
            sup -= 1.0; spin_used += 1.0
            # B 攻擊，受 A 選民的護甲抵抗 (此時套用 A 陣營遭受的審查懲罰)
            rigidity = get_spin_rigidity(B, sanity, emotion, censor_penalty_A, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B -= 1; spin_conquered += 1

    return B, perf_used, perf_conquered, spin_used, spin_conquered
