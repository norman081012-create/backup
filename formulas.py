# ==========================================
# formulas.py
# ==========================================
import math
import random
import numpy as np
import i18n
t = i18n.t

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
    
    # Exec效率加成 1.2x -> 實際花費的 EV 會以更低的單位成本計算
    unit_cost_eff = unit_cost / 1.2
    
    req_cost = total_bid_cost * unit_cost
    available_fund = max(0.0, proj_fund + r_pays + h_wealth)
    
    if c_net_override is not None:
        c_net_real = min(float(total_bid_cost), c_net_override)
        c_net_total = c_net_real + fake_ev_safe
        act_fund = (c_net_real + fake_ev_spent * cfg.get('FAKE_EV_COST_RATIO', 0.2)) * unit_cost_eff
        h_idx = min(1.0, c_net_total / max(1.0, float(total_bid_cost))) if total_bid_cost > 0 else 0.0
    else:
        if req_cost <= available_fund:
            act_fund = req_cost
            c_net_real = float(total_bid_cost)
            c_net_total = c_net_real + fake_ev_safe
            h_idx = min(1.0, c_net_total / max(1.0, float(total_bid_cost))) if total_bid_cost > 0 else 0.0
        else:
            act_fund = available_fund
            c_net_real = act_fund / max(0.01, unit_cost_eff)
            c_net_total = c_net_real + fake_ev_safe
            h_idx = min(1.0, c_net_total / max(1.0, float(total_bid_cost))) if total_bid_cost > 0 else 0.0

    payout_h = min(budget_t, proj_fund * h_idx)
    total_bonus_deduction = budget_t * ((cfg['BASE_INCOME_RATIO'] * 2) + cfg['RULING_BONUS_RATIO'])
    payout_r = max(0.0, budget_t - total_bonus_deduction - proj_fund)
    
    total_allocated = sum(allocations.values())
    effective_allocs = {}
    for pid, amt in allocations.items():
        if fake_ev_caught > 0 and total_allocated > 0:
            effective_allocs[pid] = amt - (fake_ev_caught * (amt / total_allocated))
        else:
            effective_allocs[pid] = amt

    completed_projects = []
    failed_projects = []
    ongoing_projects = []
    total_gdp_addition = 0.0

    for p in active_projects:
        p_copy = dict(p)
        p_copy['investments'] = list(p.get('investments', []))
        
        invested_so_far = sum(inv['amount'] for inv in p_copy['investments'])
        remaining_ev = p_copy['ev'] - invested_so_far
        alloc = effective_allocs.get(p_copy['id'], 0.0)
        
        if alloc > 0:
            p_copy['investments'].append({'year': current_year, 'amount': alloc})
            
        total_invested_now = invested_so_far + alloc
        
        if total_invested_now >= p_copy['ev'] * 0.99:
            completed_projects.append(p_copy)
            total_gdp_addition += p_copy['ev'] * p_copy['macro_mult'] * cfg.get('GDP_CONVERSION_RATE', 0.2)
        else:
            min_req = remaining_ev * 0.2
            if alloc < min_req - 0.01:
                failed_projects.append(p_copy)
            else:
                ongoing_projects.append(p_copy)
    
    est_gdp = max(0.0, gdp - l_gdp + total_gdp_addition)
    h_project_profit = payout_h + r_pays - act_fund
    
    return {
        'est_gdp': est_gdp, 'payout_h': payout_h, 'payout_r': payout_r,
        'h_idx': h_idx, 'c_net': c_net_real, 'c_net_total': c_net_total, 'l_gdp': l_gdp, 
        'unit_cost': unit_cost_eff, 'act_fund': act_fund, 
        'h_project_profit': h_project_profit, 'req_cost': req_cost,
        'completed_projects': completed_projects,
        'failed_projects': failed_projects,
        'ongoing_projects': ongoing_projects
    }

def generate_raw_support(cfg, curr_gdp, claimed_decay, completed_projects, real_decay, current_year):
    # 1. Ruling Perf (Macro / GDP)
    target_gdp_growth_val = sum(p['ev'] * p['macro_mult'] * cfg.get('GDP_CONVERSION_RATE', 0.2) for p in completed_projects)
    delta_A = (target_gdp_growth_val / max(1.0, curr_gdp)) * 100.0
    
    expected_loss_pct = (claimed_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE']) * 100.0
    delta_E = -expected_loss_pct
    gap = delta_A - delta_E
    
    p_ruling_raw = (delta_A * 0.05) + (gap * 0.15)
    p_ruling = p_ruling_raw * cfg.get('AMMO_MULTIPLIER', 50.0)
    
    # 2. Exec & Proposal Perf (w/ Depreciation)
    exec_perf = 0.0
    proposal_perf = {}
    inflation_corr = 5000.0 / max(1.0, curr_gdp)
    
    for p in completed_projects:
        depreciated_ev = 0.0
        for inv in p.get('investments', []):
            age = current_year - inv['year']
            retention = max(0.1, 1.0 - real_decay) ** age
            depreciated_ev += inv['amount'] * retention
            
        base_perf = (depreciated_ev * p['exec_mult'] * inflation_corr) / 20.0
        exec_perf += base_perf
        
        author = p.get('author', 'System')
        proposal_perf[author] = proposal_perf.get(author, 0.0) + base_perf
        
    return p_ruling, exec_perf, proposal_perf, delta_A, delta_E

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

def get_defense_modifier(sanity, emotion, edu_stance):
    return (sanity / 100.0) * 0.5 - (emotion / 100.0) * 0.5 + (edu_stance / 100.0) * 0.5

def get_perf_rigidity(i, sanity, emotion, edu_stance, buff_amt=0.0, buff_party=None, h_boundary=100, party_a_name=None):
    base_rigidity = get_base_rigidity(i, buff_amt, buff_party, h_boundary, party_a_name)
    modifier = get_defense_modifier(sanity, emotion, edu_stance)
    return max(0.01, min(1.0, base_rigidity - modifier))

def get_spin_rigidity(i, sanity, emotion, edu_stance, buff_amt=0.0, buff_party=None, h_boundary=100, party_a_name=None):
    base_rigidity = get_base_rigidity(i, buff_amt, buff_party, h_boundary, party_a_name)
    modifier = get_defense_modifier(sanity, emotion, edu_stance)
    return max(0.01, min(1.0, base_rigidity + modifier))

def run_conquest_split(boundary_B, net_perf_A, net_spin_A, sanity=50.0, emotion=30.0, edu_stance=0.0, buff_amt=0.0, buff_party=None, party_a_name=None):
    B = int(boundary_B)
    perf_used = 0.0; perf_conquered = 0
    
    if net_perf_A > 0:
        sup = net_perf_A
        while sup >= 1.0 and B < 200:
            sup -= 1.0; perf_used += 1.0
            rigidity = get_perf_rigidity(B + 1, sanity, emotion, edu_stance, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B += 1; perf_conquered += 1
    elif net_perf_A < 0:
        sup = abs(net_perf_A)
        while sup >= 1.0 and B > 0:
            sup -= 1.0; perf_used += 1.0
            rigidity = get_perf_rigidity(B, sanity, emotion, edu_stance, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B -= 1; perf_conquered += 1
            
    spin_used = 0.0; spin_conquered = 0
    if net_spin_A > 0:
        sup = net_spin_A
        while sup >= 1.0 and B < 200:
            sup -= 1.0; spin_used += 1.0
            rigidity = get_spin_rigidity(B + 1, sanity, emotion, edu_stance, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B += 1; spin_conquered += 1
    elif net_spin_A < 0:
        sup = abs(net_spin_A)
        while sup >= 1.0 and B > 0:
            sup -= 1.0; spin_used += 1.0
            rigidity = get_spin_rigidity(B, sanity, emotion, edu_stance, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B -= 1; spin_conquered += 1

    return B, perf_used, perf_conquered, spin_used, spin_conquered

def calc_performance_preview(cfg, hp, rp, ruling_party_name, curr_gdp, claimed_decay, sanity, emotion, projects, h_spin_pwr=0.0, r_spin_pwr=0.0, avg_edu=0.0, real_decay=0.0, current_year=1):
    p_ruling, p_exec, p_prop, d_a, d_e = generate_raw_support(cfg, curr_gdp, claimed_decay, projects, real_decay, current_year)

    h_perf = p_exec + p_prop.get(hp.name, 0.0)
    r_perf = p_prop.get(rp.name, 0.0)
    
    if ruling_party_name == hp.name: h_perf += p_ruling
    else: r_perf += p_ruling

    perf_ap_center = 1.0 - get_perf_rigidity(100, sanity, emotion, avg_edu)
    spin_ap_center = 1.0 - get_spin_rigidity(100, sanity, emotion, avg_edu)

    return {
        hp.name: {'perf': h_perf, 'spin': h_spin_pwr, 'ruling': p_ruling if ruling_party_name==hp.name else 0, 'exec': p_exec, 'prop': p_prop.get(hp.name, 0)},
        rp.name: {'perf': r_perf, 'spin': r_spin_pwr, 'ruling': p_ruling if ruling_party_name==rp.name else 0, 'exec': 0, 'prop': p_prop.get(rp.name, 0)},
        'perf_ap_center': perf_ap_center,
        'spin_ap_center': spin_ap_center,
        'delta_A': d_a, 'delta_E': d_e
    }
