# ==========================================
# config.py
# ==========================================
import i18n
t = i18n.t

DEFAULT_CONFIG = {
    'CALENDAR_NAME': "星曆", 'PARTY_A_COLOR': "#2E8B57", 'PARTY_B_COLOR': "#4169E1",
    'PARTY_A_NAME': "繁榮黨", 'PARTY_B_NAME': "平權黨", 
    'CROWN_WINNER': "👑 當權", 'CROWN_LOSER': "🎯 候選",
    'INITIAL_WEALTH': 500.0, 'END_YEAR': 12,  # 初始資金下修為 500
    
    'DECAY_MIN': 0.1, 'DECAY_MAX': 0.7,  
    'DECAY_WEIGHT_MULT': 0.05,
    'BASE_DECAY_RATE': 0.0,
    
    'DECAY_AMOUNT_DEFAULT': 1500.0,
    'DECAY_AMOUNT_BUILD': 500.0,
    
    # Fake EV Audit Parameters
    'FAKE_EV_CATCH_BASE_RATE': 0.20,      # 基礎抓包率調升至 20%
    'FAKE_EV_COST_RATIO': 0.20,            
    'CORRUPTION_FINE_MULT': 0.4,          
    'CATCH_RATE_PER_PERCENT': 0.02,
    
    'RESISTANCE_MULT': 1.0, 
    'BUILD_DIFF': 1.0, 'INVESTIGATE_DIFF': 1.0, 'PREDICT_DIFF': 1.0, 'MEDIA_DIFF': 1.0,
    'CURRENT_GDP': 5000.0, 
    'GDP_INFLATION_DIVISOR': 10000.0, 
    'GDP_CONVERSION_RATE': 0.2,   
    'HEALTH_MULTIPLIER': 0.2, 
    'BASE_TOTAL_BUDGET': 0.0,  
    
    'BASE_INCOME_RATIO': 0.05,    
    'RULING_BONUS_RATIO': 0.10,   
    
    'H_FUND_DEFAULT': 600.0, 
    'H_MEDIA_BONUS': 1.2, 'R_INV_BONUS': 1.2,
    'MAX_ABILITY': 10.0, 
    'ABILITY_DEFAULT': 3.0,          
    'BUILD_ABILITY_DEFAULT': 3.0, 
    'EDU_ABILITY_DEFAULT': 3.0,
    'MAINTENANCE_RATE': 10.0,        
    'TRUST_BREAK_PENALTY_RATIO': 0.05,
    'ELECTION_CYCLE': 4,
    'SANITY_DEFAULT': 50.0,   
    'EMOTION_DEFAULT': 30.0,
    
    'CLAIMED_DECAY_WEIGHT': 0.2,
    'AMMO_MULTIPLIER': 50.0,
    
    'MAX_UPGRADE_SPEED': 20.0,
    'UPGRADE_COST_MULT': 0.15,      
    'PR_EFFICIENCY_MULT': 3.0,      
    
    'PREDICT_ACCURACY_WEIGHT': 0.8,     
    'INVESTIGATE_ACCURACY_WEIGHT': 0.8, 
    
    'PERF_IMPACT_BASE': 1000.0,
    'OBS_ERR_BASE': 0.7,      
}

def get_config_translations():
    return {
        'DECAY_MIN': "最小衰退率", 'DECAY_MAX': "最大衰退率",  
        'FAKE_EV_CATCH_BASE_RATE': "假 EV 基礎抓包率",
        'DECAY_WEIGHT_MULT': "衰退率轉換 GDP 權重 (預設 0.05)", 'BASE_DECAY_RATE': "基礎衰退下限",
        'CLAIMED_DECAY_WEIGHT': "預期落差權重", 'AMMO_MULTIPLIER': "政績轉換支持度倍率",
        'PREDICT_ACCURACY_WEIGHT': "智庫預測準確度權重", 'INVESTIGATE_ACCURACY_WEIGHT': "情報調查準確度權重",
        'UPGRADE_COST_MULT': "升級成本基數", 'PR_EFFICIENCY_MULT': "公關效率倍率"
    }

def get_intel_market_eval(unit_cost):
    if unit_cost < 0.8: return "🌟 極度低估"
    elif unit_cost < 1.2: return "🟢 市場穩定"
    elif unit_cost < 1.8: return "🟡 通膨溢價"
    elif unit_cost < 2.5: return "🔴 過熱警告"
    else: return "💀 經濟惡化"

def get_economic_forecast_text(drop_val):
    if drop_val <= 10.0: return "🌟 經濟繁榮"
    elif drop_val <= 30.0: return "📈 穩定成長"
    elif drop_val <= 50.0: return "⚖️ 經濟放緩"
    elif drop_val <= 70.0: return "📉 衰退警告"
    else: return "⚠️ 經濟風暴"

def get_civic_index_text(score):
    if score < 15: return f"極易被洗腦 ({score:.1f})"
    elif score < 30: return f"高度易受影響 ({score:.1f})"
    elif score < 45: return f"輕度易受影響 ({score:.1f})"
    elif score < 60: return f"具備中度理性 ({score:.1f})"
    elif score < 75: return f"具備輕度批判力 ({score:.1f})"
    elif score < 90: return f"成熟的批判思考 ({score:.1f})"
    else: return f"高度獨立自主 ({score:.1f})"

def get_emotion_text(emotion_val):
    if emotion_val < 20: return f"冷靜穩定 ({emotion_val:.1f})"
    elif emotion_val < 50: return f"略顯浮躁 ({emotion_val:.1f})"
    elif emotion_val < 80: return f"群情激憤 ({emotion_val:.1f})"
    else: return f"極度狂熱 ({emotion_val:.1f})"

def get_election_icon(year, cycle):
    rem = year % cycle
    if rem == 1: return "🗳️ 選舉年"
    elif rem == 2: return "🌱 任期第一年"
    elif rem == cycle - 1: return "⏳ 距大選 2 年"
    elif rem == 0: return "🚨 明年大選"
    else: return f"距大選 {cycle - rem + 1} 年"

def get_party_logo(name):
    if name == "繁榮黨": return "🦅"
    elif name == "平權黨": return "🤝"
    return "🚩"

def get_thinktank_eval(ability, diff):
    abi_lvl = "high" if ability >= 7 else "med" if ability >= 4 else "low"
    acc_lvl = "high" if diff <= 5.0 else "med" if diff <= 15.0 else "low" 
    matrix = {
        ('high', 'high'): "頂級表現", ('high', 'med'): "微小誤差", ('high', 'low'): "黑天鵝事件",
        ('med', 'high'): "超乎水準", ('med', 'med'): "標準表現", ('med', 'low'): "嚴重誤判",
        ('low', 'high'): "盲目運氣", ('low', 'med'): "尚可接受", ('low', 'low'): "系統完全失能"
    }
    return matrix.get((abi_lvl, acc_lvl), "系統故障")

# ==========================================
# ai_bot.py (The Symbiocracy AI Engine)
# ==========================================
import random
import formulas
import streamlit as st

def take_turn(game, cfg):
    """
    AI 自動運算核心。攔截遊戲狀態，並將結果直接寫入系統後推進。
    """
    ai_party = game.party_A if game.party_A.name == game.ai_party_name else game.party_B
    is_h = (game.h_role_party.name == ai_party.name)
    active_role = 'H' if is_h else 'R'

    # ==========================================
    # PHASE 1: 預算與法案談判
    # ==========================================
    if game.phase == 1:
        if game.p1_step in ['draft_r', 'draft_h', 'ultimatum_draft_r']:
            # AI 分析當前經濟局勢
            total_bonus = game.total_budget * ((cfg['BASE_INCOME_RATIO'] * 2) + cfg['RULING_BONUS_RATIO'])
            max_proj = max(10.0, float(game.total_budget) - total_bonus)
            unit_cost = formulas.calc_unit_cost(cfg, game.gdp, ai_party.build_ability, ai_party.current_forecast)

            if is_h:
                # 貪婪的 H 黨：要超高獎金，還要 R 黨幫忙出錢
                proj_fund = max_proj * random.uniform(0.7, 0.9) 
                bid_cost = proj_fund * random.uniform(0.8, 1.2) 
                req_cost = bid_cost * unit_cost
                r_pays = min(req_cost * random.uniform(0.2, 0.4), max_proj)
                fine_mult = 0.3 
            else:
                # 刻薄的 R 黨：給極低獎金，要求超高建設量，且違約金極高
                proj_fund = max_proj * random.uniform(0.2, 0.4) 
                bid_cost = proj_fund * random.uniform(1.2, 1.5)
                req_cost = bid_cost * unit_cost
                r_pays = 0.0 
                fine_mult = random.uniform(0.8, 1.5) 

            plan = {
                'proj_fund': proj_fund, 'bid_cost': bid_cost,
                'r_pays': r_pays, 'h_pays': max(0.0, req_cost - r_pays),
                'claimed_decay': ai_party.current_forecast, 'claimed_cost': unit_cost,
                'author': active_role, 'author_party': ai_party.name,
                'req_cost': req_cost, 'fine_mult': fine_mult
            }

            if game.p1_step == 'ultimatum_draft_r':
                game.p1_selected_plan = plan
                game.p1_step = 'ultimatum_resolve_h'
                game.proposing_party = game.h_role_party
            else:
                game.p1_proposals[active_role] = plan
                if game.p1_step == 'draft_r':
                    game.p1_step = 'draft_h'
                    game.proposing_party = game.h_role_party
                else:
                    game.p1_step = 'voting_pick'
                    game.proposing_party = game.ruling_party

        elif game.p1_step == 'voting_pick':
            # AI 作為執政黨，必然選擇自己撰寫的草案
            my_draft = game.p1_proposals.get(active_role)
            if not my_draft: my_draft = game.p1_proposals.get('H' if active_role == 'R' else 'R')
            game.p1_selected_plan = my_draft
            game.p1_step = 'voting_confirm'
            game.proposing_party = game.party_B if game.ruling_party.name == game.party_A.name else game.party_A

        elif game.p1_step in ['voting_confirm', 'ultimatum_resolve_h']:
            # 談判心理戰：在前兩輪有 40% 的機率強硬退回法案逼迫玩家讓步
            if game.p1_step == 'voting_confirm' and game.proposal_count < 3 and random.random() < 0.4:
                game.proposal_count += 1
                game.p1_step = 'draft_r'
                game.proposing_party = game.r_role_party
                st.session_state.news_flash = f"🗞️ **[快訊]** {ai_party.name} 拒絕了草案，重新展開談判。"
            else:
                # 妥協接受
                st.session_state.turn_data.update(game.p1_selected_plan)
                game.phase = 2
                game.proposing_party = game.ruling_party
                st.session_state.news_flash = f"🗞️ **[快訊]** {ai_party.name} 接受了草案，法案通過！"

    # ==========================================
    # PHASE 2: 資源分配與部門操作
    # ==========================================
    elif game.phase == 2:
        d = st.session_state.get('turn_data', {})
        bid_cost = float(d.get('bid_cost', 1.0))
        
        inv_cap = ai_party.investigate_ability * 10 * (1.2 if not is_h else 1.0)
        ci_cap = ai_party.stealth_ability * 10
        med_cap = ai_party.media_ability * 10 * (1.2 if is_h else 1.0)
        
        # AI 的基礎分配面板 (它會保守地維持現狀，只付維護費不亂升級以免破產)
        my_acts = {
            'w_i_cen': 0, 'w_i_org': 0, 'w_i_fin': 0,
            'alloc_inv_censor': 0, 'alloc_inv_audit': 0, 'alloc_inv_fin': 0,
            'w_c_cen': 0, 'w_c_org': 0, 'w_c_fin': 0,
            'alloc_ci_anticen': 0, 'alloc_ci_hideorg': 0, 'alloc_ci_hidefin': 0,
            'w_m_cam': 50, 'w_m_inc': 0, 'w_m_con': 50,
            'alloc_med_camp': med_cap * 0.5, 'alloc_med_incite': 0, 'alloc_med_control': med_cap * 0.5,
            'edu_stance': ai_party.edu_stance, 'fake_ev': 0.0,
            't_pre': ai_party.predict_ability, 't_inv': ai_party.investigate_ability,
            't_med': ai_party.media_ability, 't_stl': ai_party.stealth_ability,
            't_bld': ai_party.build_ability, 't_edu': ai_party.edu_ability,
            'invest_wealth': 0.0, 'c_net': 0.0
        }

        unit_cost = formulas.calc_unit_cost(cfg, game.gdp, ai_party.build_ability, game.current_real_decay)
        maint_ev = sum([ai_party.predict_ability, ai_party.investigate_ability, ai_party.media_ability, ai_party.stealth_ability, ai_party.build_ability, ai_party.edu_ability]) * 5.0
        eng_base_ev = ai_party.build_ability * 10 * (1.2 if is_h else 1.0)

        if is_h:
            # AI 擔任執行方 (H)：戰略核心為隱藏金流，並機率性搞豆腐渣工程
            my_acts['w_c_fin'] = 100
            my_acts['alloc_ci_hidefin'] = ci_cap
            
            c_net = bid_cost
            # 40% 機率貪婪大爆發，塞入 10%~30% 的假 EV
            fake_ev = bid_cost * random.uniform(0.1, 0.3) if random.random() < 0.4 else 0.0
            
            my_acts['fake_ev'] = fake_ev
            my_acts['c_net'] = c_net

            total_ev_req = c_net + (fake_ev * cfg.get('FAKE_EV_COST_RATIO', 0.2)) + maint_ev
            ev_to_buy = max(0.0, total_ev_req - eng_base_ev)
            my_acts['invest_wealth'] = ev_to_buy * max(0.01, unit_cost)
        else:
            # AI 擔任監管方 (R)：瘋狗模式，所有 Ops 全部拿去查金流！
            my_acts['w_i_fin'] = 100
            my_acts['alloc_inv_fin'] = inv_cap
            
            total_ev_req = maint_ev
            ev_to_buy = max(0.0, total_ev_req - eng_base_ev)
            my_acts['invest_wealth'] = ev_to_buy * max(0.01, unit_cost)

        st.session_state[f"{ai_party.name}_acts"] = my_acts

        # 自動推進下一個階段
        opp_name = game.human_party_name
        if f"{opp_name}_acts" not in st.session_state:
            game.proposing_party = game.party_A if game.party_A.name == opp_name else game.party_B
        else:
            game.phase = 3
            game.proposing_party = game.r_role_party

# ==========================================
# engine.py
# ==========================================
import random
import streamlit as st
import i18n
t = i18n.t

class Party:
    def __eq__(self, other): return self.name == other.name if hasattr(other, 'name') else False
    def __init__(self, name, cfg):
        self.name = name
        self.wealth = cfg['INITIAL_WEALTH']
        self.support = 50.0 
        
        self.build_ability = cfg.get('BUILD_ABILITY_DEFAULT', 3.0)
        self.investigate_ability = cfg.get('ABILITY_DEFAULT', 3.0)
        self.media_ability = cfg.get('ABILITY_DEFAULT', 3.0)
        self.predict_ability = cfg.get('ABILITY_DEFAULT', 3.0)
        self.stealth_ability = cfg.get('ABILITY_DEFAULT', 3.0)
        self.edu_ability = cfg.get('EDU_ABILITY_DEFAULT', 3.0)
        self.edu_stance = 0.0 
        
        self.current_forecast = 0.0
        self.poll_history = {'Small': [], 'Medium': [], 'Large': []}
        self.latest_poll = None
        self.poll_count = 0
        self.last_acts = {}

class GameEngine:
    def __init__(self, cfg):
        self.year = 1
        self.party_A = Party(cfg['PARTY_A_NAME'], cfg)
        self.party_B = Party(cfg['PARTY_B_NAME'], cfg)
        self.gdp = cfg['CURRENT_GDP']
        self.total_budget = cfg['BASE_TOTAL_BUDGET'] + (self.gdp * cfg['HEALTH_MULTIPLIER'])
        self.h_fund = cfg['H_FUND_DEFAULT']
        
        self.phase = 0 # 📌 Phase 0 為遊戲初始設定階段
        self.is_pve = False
        self.human_party_name = None
        self.ai_party_name = None

        self.p1_step = 'draft_r' 
        self.p1_proposals = {'R': None, 'H': None}
        self.p1_selected_plan = None
        self.ruling_party = self.party_A
        self.r_role_party = self.party_A
        self.h_role_party = self.party_B  
        
        self.sanity = cfg['SANITY_DEFAULT']
        self.emotion = cfg['EMOTION_DEFAULT']
        self.current_real_decay = 0.0
        self.proposal_count = 1
        self.proposing_party = self.party_A
        self.history = []
        self.swap_triggered_this_year = False
        self.last_year_report = None
        
        self.boundary_B = 100 
        self.h_rigidity_buff = {'amount': 0.0, 'duration': 0, 'party': None}

    def record_history(self, is_election):
        self.history.append({
            'Year': self.year, 'GDP': self.gdp, 'Sanity': self.sanity, 'Emotion': self.emotion,
            'A_Support': self.party_A.support, 'B_Support': self.party_B.support,
            'A_Wealth': self.party_A.wealth, 'B_Wealth': self.party_B.wealth,
            'Is_Election': is_election, 'Is_Swap': self.swap_triggered_this_year,
            'Ruling': self.ruling_party.name, 'H_Party': self.h_role_party.name,
            'R_Party': self.r_role_party.name,
            'A_Edu': float(self.party_A.edu_stance),
            'B_Edu': float(self.party_B.edu_stance),
            'A_Avg_Abi': (self.party_A.build_ability + self.party_A.investigate_ability + self.party_A.media_ability + self.party_A.predict_ability + self.party_A.stealth_ability + self.party_A.edu_ability)/6,
            'B_Avg_Abi': (self.party_B.build_ability + self.party_B.investigate_ability + self.party_B.media_ability + self.party_B.predict_ability + self.party_B.stealth_ability + self.party_B.edu_ability)/6
        })
        self.swap_triggered_this_year = False

def execute_poll(game, view_party, cost):
    view_party.wealth -= cost
    error_margin = max(0.0, 15.0 - (view_party.predict_ability * 0.5) - (cost * 0.4))
    a_actual = game.party_A.support
    a_poll = max(0.0, min(100.0, a_actual + random.uniform(-error_margin, error_margin)))
    
    poll_type = 'Small' if cost == 5 else 'Medium' if cost == 10 else 'Large'
    game.party_A.latest_poll = a_poll
    game.party_A.poll_history[poll_type].append(a_poll)
    b_poll = 100.0 - a_poll
    game.party_B.latest_poll = b_poll
    game.party_B.poll_history[poll_type].append(b_poll)
    view_party.poll_count += 1

def trigger_swap(game, penalty_amt, msg_prefix="政治動盪！"):
    game.party_A.wealth -= penalty_amt; game.party_B.wealth -= penalty_amt
    game.h_role_party, game.r_role_party = game.r_role_party, game.h_role_party
    game.swap_triggered_this_year = True
    game.emotion = min(100.0, game.emotion + 30.0) 
    
    st.session_state.news_flash = f"🗞️ **[快訊] {msg_prefix}** 雙方被迫向慈善機構支付 {penalty_amt:.1f} 罰金，觸發立即的內閣倒閣換位！"
    st.session_state.anim = 'snow'
    game.phase = 2

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

def calc_economy(cfg, gdp, budget_t, proj_fund, bid_cost, build_abi, forecast_decay, r_pays=0.0, h_wealth=0.0, c_net_override=None, override_unit_cost=None, fake_ev_spent=0.0, fake_ev_safe=0.0):
    l_gdp = gdp * (forecast_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
    unit_cost = override_unit_cost if override_unit_cost is not None else calc_unit_cost(cfg, gdp, build_abi, forecast_decay)
    req_cost = bid_cost * unit_cost
    
    available_fund = max(0.0, proj_fund + r_pays + h_wealth)
    
    if c_net_override is not None:
        c_net_real = min(float(bid_cost), c_net_override)
        c_net_total = c_net_real + fake_ev_safe
        act_fund = (c_net_real + fake_ev_spent * cfg.get('FAKE_EV_COST_RATIO', 0.2)) * unit_cost
        h_idx = min(1.0, c_net_total / max(1.0, float(bid_cost)))
    else:
        if req_cost <= available_fund:
            act_fund = req_cost
            c_net_real = float(bid_cost)
            c_net_total = c_net_real + fake_ev_safe
            h_idx = min(1.0, c_net_total / max(1.0, float(bid_cost)))
        else:
            act_fund = available_fund
            c_net_real = act_fund / max(0.01, unit_cost)
            c_net_total = c_net_real + fake_ev_safe
            h_idx = min(1.0, c_net_total / max(1.0, float(bid_cost)))

    payout_h = min(budget_t, proj_fund * h_idx)
    total_bonus_deduction = budget_t * ((cfg['BASE_INCOME_RATIO'] * 2) + cfg['RULING_BONUS_RATIO'])
    payout_r = max(0.0, budget_t - total_bonus_deduction - proj_fund)
    
    est_gdp = max(0.0, gdp - l_gdp + (c_net_real * cfg.get('GDP_CONVERSION_RATE', 0.2)))
    
    h_project_profit = payout_h + r_pays - act_fund
    
    return {
        'est_gdp': est_gdp, 'payout_h': payout_h, 'payout_r': payout_r,
        'h_idx': h_idx, 'c_net': c_net_real, 'c_net_total': c_net_total, 'l_gdp': l_gdp, 
        'unit_cost': unit_cost, 'act_fund': act_fund, 
        'h_project_profit': h_project_profit, 'req_cost': req_cost
    }

def generate_raw_support(cfg, new_gdp, curr_gdp, claimed_decay, bid_cost, c_net_total):
    delta_A = ((new_gdp - curr_gdp) / max(1.0, curr_gdp)) * 100.0
    expected_loss_pct = (claimed_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE']) * 100.0
    delta_E = -expected_loss_pct

    gap = delta_A - delta_E
    p_plan = (delta_A * 0.05) + (gap * 0.15)

    completion_rate = c_net_total / max(1.0, float(bid_cost))
    delta_C = (completion_rate - 0.5) * 2.0 
    
    target_gdp_growth = (bid_cost * cfg.get('GDP_CONVERSION_RATE', 0.2)) / max(1.0, curr_gdp) * 100.0
    p_exec = target_gdp_growth * delta_C * 0.1

    support_mult = cfg.get('AMMO_MULTIPLIER', 50.0) 
    return p_plan * support_mult, p_exec * support_mult, delta_A, delta_E, delta_C

def apply_sanity_filter(raw_support, sanity, emotion, is_preview=False):
    crit_think = sanity / 100.0
    emo_val = emotion / 100.0
    correct_prob = max(0.05, min(0.95, crit_think * (1.0 - emo_val * 0.5)))

    if is_preview:
        return raw_support * correct_prob, raw_support * (1.0 - correct_prob), correct_prob

    correct_support = 0.0
    wrong_support = 0.0
    sign = 1.0 if raw_support >= 0 else -1.0
    abs_total = abs(raw_support)
    int_parts = int(abs_total)
    remainder = abs_total - int_parts

    for _ in range(int_parts):
        if random.random() < correct_prob:
            correct_support += 1.0
        else:
            wrong_support += 1.0
            
    if remainder > 0:
        if random.random() < correct_prob:
            correct_support += remainder
        else:
            wrong_support += remainder

    return correct_support * sign, wrong_support * sign, correct_prob

def apply_media_spin(blind_support, rightful_media, opp_media, is_preview=False):
    base_inertia = 5.0 
    total_power = rightful_media + opp_media + base_inertia
    
    if blind_support >= 0:
        move_prob = rightful_media / total_power
    else:
        move_prob = opp_media / total_power

    if is_preview:
        goes_to_rightful = blind_support * move_prob
        stays_with_opp = blind_support * (1.0 - move_prob)
        return goes_to_rightful, stays_with_opp

    goes_to_rightful = 0.0
    stays_with_opp = 0.0
    sign = 1.0 if blind_support >= 0 else -1.0
    abs_total = abs(blind_support)
    int_parts = int(abs_total)
    remainder = abs_total - int_parts

    for _ in range(int_parts):
        if random.random() < move_prob:
            goes_to_rightful += 1.0
        else:
            stays_with_opp += 1.0
            
    if remainder > 0:
        if random.random() < move_prob:
            goes_to_rightful += remainder
        else:
            stays_with_opp += remainder

    return goes_to_rightful * sign, stays_with_opp * sign

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

def get_spin_rigidity(i, sanity=50.0, buff_amt=0.0, buff_party=None, h_boundary=100, party_a_name=None):
    base_rigidity = get_base_rigidity(i, buff_amt, buff_party, h_boundary, party_a_name)
    sanity_defense = (sanity / 100.0) * 0.5 
    return min(1.0, base_rigidity + sanity_defense)

def run_conquest_split(boundary_B, net_perf_A, net_spin_A, sanity=50.0, buff_amt=0.0, buff_party=None, party_a_name=None):
    B = int(boundary_B)
    perf_used = 0.0; perf_conquered = 0
    if net_perf_A > 0:
        sup = net_perf_A
        while sup >= 1.0 and B < 200:
            sup -= 1.0; perf_used += 1.0
            rigidity = get_base_rigidity(B + 1, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B += 1; perf_conquered += 1
    elif net_perf_A < 0:
        sup = abs(net_perf_A)
        while sup >= 1.0 and B > 0:
            sup -= 1.0; perf_used += 1.0
            rigidity = get_base_rigidity(B, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B -= 1; perf_conquered += 1
            
    spin_used = 0.0; spin_conquered = 0
    if net_spin_A > 0:
        sup = net_spin_A
        while sup >= 1.0 and B < 200:
            sup -= 1.0; spin_used += 1.0
            rigidity = get_spin_rigidity(B + 1, sanity, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B += 1; spin_conquered += 1
    elif net_spin_A < 0:
        sup = abs(net_spin_A)
        while sup >= 1.0 and B > 0:
            sup -= 1.0; spin_used += 1.0
            rigidity = get_spin_rigidity(B, sanity, buff_amt, buff_party, boundary_B, party_a_name)
            if random.random() < (1.0 - rigidity):
                B -= 1; spin_conquered += 1

    return B, perf_used, perf_conquered, spin_used, spin_conquered

def calc_performance_preview(cfg, hp, rp, ruling_party_name, new_gdp, curr_gdp, claimed_decay, sanity, emotion, bid_cost, c_net_total, h_media_pwr=0.0, r_media_pwr=0.0):
    p_plan, p_exec, d_a, d_e, d_c = generate_raw_support(cfg, new_gdp, curr_gdp, claimed_decay, bid_cost, c_net_total)

    plan_correct, plan_wrong, correct_prob = apply_sanity_filter(p_plan, sanity, emotion, is_preview=True)
    exec_correct, exec_wrong, _ = apply_sanity_filter(p_exec, sanity, emotion, is_preview=True)
    
    if ruling_party_name == hp.name:
        ruling_media_pwr = h_media_pwr; opp_media_pwr = r_media_pwr
    else:
        ruling_media_pwr = r_media_pwr; opp_media_pwr = h_media_pwr
        
    ruling_reclaimed, opp_kept_plan = apply_media_spin(plan_wrong, ruling_media_pwr, opp_media_pwr, is_preview=True)
    h_reclaimed_exec, r_kept_exec = apply_media_spin(exec_wrong, h_media_pwr, r_media_pwr, is_preview=True)

    if ruling_party_name == hp.name:
        h_plan_sup = plan_correct + ruling_reclaimed
        r_plan_sup = opp_kept_plan
    else:
        r_plan_sup = plan_correct + ruling_reclaimed
        h_plan_sup = opp_kept_plan
        
    h_exec_sup = exec_correct + h_reclaimed_exec
    r_exec_sup = r_kept_exec

    return {
        hp.name: {'perf_gdp': h_plan_sup, 'perf_proj': h_exec_sup, 'spun_gdp': ruling_reclaimed if ruling_party_name == hp.name else opp_kept_plan, 'spun_proj': h_reclaimed_exec},
        rp.name: {'perf_gdp': r_plan_sup, 'perf_proj': r_exec_sup, 'spun_gdp': ruling_reclaimed if ruling_party_name == rp.name else opp_kept_plan, 'spun_proj': r_kept_exec},
        'correct_prob': correct_prob,
        'p_plan': p_plan, 'p_exec': p_exec,
        'delta_A': d_a, 'delta_E': d_e, 'delta_C': d_c
    }

# ==========================================
# i18n.py
# ==========================================
import streamlit as st

def t(text, fallback=None):
    # 由於我們已經全面中文化，這裡只是一個單純的直通通道
    return text

# ==========================================
# main.py
# ==========================================
import ui_formulas
import streamlit as st
import random
import config
import engine
import ui_core
import ui_proposal 
import phase1
import phase2
import phase3
import phase4
import i18n
import ai_bot  # 📌 引入全新的 AI 神經中樞

st.set_page_config(page_title="共生體制模擬器 v3.0.0", layout="wide")
st.components.v1.html("<script>window.parent.document.querySelector('.main').scrollTo(0,0);</script>", height=0)

if 'lang' not in st.session_state: st.session_state.lang = 'ZH' # 強制繁體中文
t = i18n.t

if 'cfg' not in st.session_state: st.session_state.cfg = config.DEFAULT_CONFIG.copy()
cfg = st.session_state.cfg

if 'game' not in st.session_state:
    st.session_state.game = engine.GameEngine(cfg)
    st.session_state.turn_data = {
        'r_value': 1.0, 'target_h_fund': 600.0, 'target_gdp_growth': 0.0,
        'r_pays': 0, 'total_funds': 0, 'agreed': False, 'target_gdp': 5000.0, 'h_ratio': 1.0
    }

game = st.session_state.game

if st.session_state.get('anim') == 'balloons':
    st.balloons()
    st.session_state.anim = None
elif st.session_state.get('anim') == 'snow':
    st.snow()
    st.session_state.anim = None

if game.phase == 4:
    phase4.render(game, cfg)
    st.stop()

# ==========================================
# PHASE 0: 遊戲初始設定 (僅在剛啟動時出現)
# ==========================================
if game.phase == 0:
    st.title("🏛️ 共生體制模擬器 - 遊戲設定")
    st.markdown("---")
    
    st.markdown("### 選擇遊戲模式")
    mode = st.radio("請選擇遊玩方式：", ["PvE (單人對戰 AI)", "PvP (單機雙人)"], label_visibility="collapsed")
    
    human_party = None
    if mode == "PvE (單人對戰 AI)":
        st.markdown("### 選擇你的政黨")
        human_party = st.radio("選擇你的陣營：", [f"{cfg['PARTY_A_NAME']} (老鷹)", f"{cfg['PARTY_B_NAME']} (握手)"], label_visibility="collapsed")
        # 清除附帶的說明文字，抓取純黨名
        human_party = human_party.split(" (")[0]
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("開始模擬 🚀", type="primary"):
        game.phase = 1
        if mode == "PvE (單人對戰 AI)":
            game.is_pve = True
            game.human_party_name = human_party
            game.ai_party_name = cfg['PARTY_B_NAME'] if human_party == cfg['PARTY_A_NAME'] else cfg['PARTY_A_NAME']
        else:
            game.is_pve = False
        st.rerun()
    st.stop()  # 阻擋渲染，直到玩家按下開始

# ==========================================
# AI 自動攔截系統 (無縫代打)
# ==========================================
if getattr(game, 'is_pve', False) and game.phase in [1, 2] and game.proposing_party.name == game.ai_party_name:
    st.title("🏛️ 共生體制模擬器 v3.0.0")
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.spinner(f"🤖 **{game.ai_party_name}** 正在制定策略並採取行動..."):
        import time
        time.sleep(0.8) # 稍微延遲 0.8 秒，讓玩家有對手在思考的沉浸感
        ai_bot.take_turn(game, cfg)
        st.rerun()
# ==========================================

if 'turn_initialized' not in st.session_state:
    game.current_real_decay = max(0.0, round(random.uniform(cfg['DECAY_MIN'], cfg['DECAY_MAX']), 3))
    real_infra_loss = game.gdp * (game.current_real_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
    
    for p in [game.party_A, game.party_B]:
        p_acc_weight = cfg.get('PREDICT_ACCURACY_WEIGHT', 0.8)
        error_margin_pct = 1.0 - ((p.predict_ability / 10.0) * p_acc_weight)
        error_range = real_infra_loss * error_margin_pct
        observed_loss = max(0.0, real_infra_loss + random.uniform(-error_range, error_range))
        
        p.current_forecast = max(0.0, round(((observed_loss / max(1.0, game.gdp)) - cfg['BASE_DECAY_RATE']) / cfg['DECAY_WEIGHT_MULT'], 3))
        p.poll_history = {'Small': [], 'Medium': [], 'Large': []}
        p.latest_poll = None
        p.poll_count = 0 
    
    if not hasattr(game, 'p1_step'):
        game.p1_step = 'draft_r'
        game.p1_proposals = {'R': None, 'H': None}
        game.p1_selected_plan = None

    for k in list(st.session_state.keys()):
        if k.startswith('ui_decay_') or k.endswith('_acts'): del st.session_state[k]
    
    st.session_state.turn_initialized = True
    
    if game.year == 1:
        st.session_state.news_flash = f"🎉 **[建國大選]** 模擬開始！{game.ruling_party.name} 贏得了首屆執政權。"

view_party = game.proposing_party
opponent_party = game.party_B if view_party.name == game.party_A.name else game.party_A
is_election_year = (game.year % cfg['ELECTION_CYCLE'] == 1)

with st.sidebar:
    ui_core.render_global_settings(cfg, game)
    ui_core.render_sidebar_intel_audit(game, view_party, cfg)
    god_mode = st.toggle("👁️ 上帝模式", False)
    st.session_state.god_mode = god_mode 
    if st.button("🔄 重新開始遊戲", use_container_width=True): st.session_state.clear(); st.rerun()

st.title("🏛️ 共生體制模擬器 v3.0.0")

elec_status = config.get_election_icon(game.year, cfg['ELECTION_CYCLE'])
st.subheader(f"📅 {cfg['CALENDAR_NAME']} 第 {game.year} 年 ({elec_status})")

if god_mode:
    real_loss = game.gdp * (game.current_real_decay * cfg['DECAY_WEIGHT_MULT'] + cfg['BASE_DECAY_RATE'])
    st.error(f"👁️ **上帝模式:** 真實衰退率為 **{game.current_real_decay:.3f}** (EV 損失: {real_loss:.1f})")

if game.phase == 1 or game.phase == 2:
    if game.phase == 1: ui_core.render_dashboard(game, view_party, cfg, is_preview=False)
    ui_core.render_party_cards(game, view_party, god_mode, is_election_year, cfg)
    ui_core.render_message_board(game)

if game.phase == 1: phase1.render(game, view_party, cfg)
elif game.phase == 2: phase2.render(game, view_party, opponent_party, cfg)
elif game.phase == 3: phase3.render(game, cfg)

if game.phase != 4: ui_formulas.render_formula_panel(game, view_party, cfg)

# ==========================================
# phase1.py
# ==========================================
import streamlit as st
import formulas
import engine
import ui_core
import ui_proposal  
import i18n
t = i18n.t

def render(game, view_party, cfg):
    penalty_amt = int(game.total_budget * cfg['TRUST_BREAK_PENALTY_RATIO'])
    st.subheader(f"🤝 第一階段：監管系統提案 (第 {game.proposal_count} 回合)")
    
    if game.p1_step in ['draft_r', 'draft_h', 'ultimatum_draft_r']:
        active_role = 'R' if game.p1_step in ['draft_r', 'ultimatum_draft_r'] else 'H'
        
        if game.p1_step == 'ultimatum_draft_r':
            st.error("🚨 **最後通牒啟動：** 監管系統必須提出最終決議！")
            
        if view_party.name != (game.r_role_party.name if active_role == 'R' else game.h_role_party.name):
            st.warning(f"⏳ 等待對手提出草案...")
        else:
            role_text_zh = '監管系統' if active_role == 'R' else '執行系統'
            
            c_title, c_fine, c_btn = st.columns([0.5, 0.3, 0.2])
            with c_title:
                st.markdown(f"#### 📝 {view_party.name} ({role_text_zh}) 提案室")
            
            opp_role = 'H' if active_role == 'R' else 'R'
            opp_plan = game.p1_proposals.get(opp_role)
            
            with c_fine:
                if active_role == 'R':
                    fine_mult = st.number_input("⚖️ 司法罰金倍率", min_value=0.0, max_value=5.0, value=0.3, step=0.1)
                else:
                    fine_mult = opp_plan.get('fine_mult', 0.3) if opp_plan else 0.3
                    st.info(f"⚖️ 司法罰金：**{fine_mult}x**")
            
            input_decay_key = f"ui_decay_val_{game.year}_{active_role}"
            input_cost_key = f"ui_cost_val_{game.year}_{active_role}"
            widget_decay_key = f"num_{input_decay_key}"
            widget_cost_key = f"num_{input_cost_key}"
            
            obs_abis = ui_core.get_observed_abilities(view_party, game.h_role_party, game, cfg)
            tt_decay = float(view_party.current_forecast)
            suggested_unit_cost = formulas.calc_unit_cost(cfg, game.gdp, obs_abis['build'], view_party.current_forecast)
            tt_cost = round(suggested_unit_cost, 2)
            
            if widget_decay_key not in st.session_state: st.session_state[widget_decay_key] = tt_decay
            if widget_cost_key not in st.session_state: st.session_state[widget_cost_key] = tt_cost

            with c_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 自動帶入智庫預測", use_container_width=True):
                    st.session_state[widget_decay_key] = tt_decay
                    st.session_state[widget_cost_key] = tt_cost
                    st.rerun()

            c_ann1, c_ann2 = st.columns(2)
            with c_ann1:
                opp_claimed_decay = opp_plan.get('claimed_decay') if opp_plan else None
                opp_txt1 = f"對手宣告: {opp_claimed_decay:.3f}" if opp_claimed_decay is not None else "等待對手中"
                
                current_val = st.session_state.get(widget_decay_key, tt_decay)
                conv_rate = cfg.get('GDP_CONVERSION_RATE', 0.2)
                gdp_loss = game.gdp * (current_val * cfg.get('DECAY_WEIGHT_MULT', 0.05) + cfg.get('BASE_DECAY_RATE', 0.0))
                req_infra_to_balance = gdp_loss / conv_rate
                
                st.markdown(f"**宣告衰退率 (當前: {current_val:.3f}) (等同於 {req_infra_to_balance:.1f} 建設損失)** | {opp_txt1}")
                claimed_decay = st.number_input("宣告衰退率", step=0.001, min_value=0.0, key=widget_decay_key, label_visibility="collapsed")
                st.session_state[input_decay_key] = claimed_decay
                
            with c_ann2:
                opp_claimed_cost = opp_plan.get('claimed_cost') if opp_plan else None
                opp_txt2 = f"對手宣告: {opp_claimed_cost:.2f}" if opp_claimed_cost is not None else "等待對手中"
                st.markdown(f"**宣告單位成本 (當前: {st.session_state.get(widget_cost_key, tt_cost):.2f})** | {opp_txt2}")
                claimed_cost = st.number_input("宣告單位成本", step=0.01, key=widget_cost_key, label_visibility="collapsed")
                st.session_state[input_cost_key] = claimed_cost
            
            total_bonus_deduction = game.total_budget * ((cfg['BASE_INCOME_RATIO'] * 2) + cfg['RULING_BONUS_RATIO'])
            max_proj_fund = max(0.0, float(game.total_budget) - total_bonus_deduction)
            
            def_proj = float(opp_plan.get('proj_fund', 0.0)) if opp_plan else 0.0
            def_bid = float(opp_plan.get('bid_cost', 0.0)) if opp_plan else 0.0
            def_rpays = float(opp_plan.get('r_pays', 0.0)) if opp_plan else 0.0
            
            proj_fund = st.slider("專案總獎金 (上限=總預算扣除薪資)", 0.0, max_proj_fund, min(def_proj, max_proj_fund), 10.0)
            bid_cost = st.slider("專案總效益 (建設規模/產值)", 0.0, max_proj_fund * 1.5, def_bid, 10.0)
            r_pays = st.slider("💰 監管方墊付款", 0.0, max_proj_fund, def_rpays, 10.0)
            
            req_cost = bid_cost * claimed_cost
            h_pays = req_cost - r_pays
            
            is_invalid = False
            warning_msg = ""
            if proj_fund <= 0:
                is_invalid = True; warning_msg = "⚠️ 錯誤：獎金必須大於 0！"
            elif bid_cost <= 0:
                is_invalid = True; warning_msg = "⚠️ 錯誤：效益必須大於 0！"
            elif r_pays > req_cost:
                is_invalid = True; warning_msg = "⚠️ 錯誤：監管方墊付款不能超過專案總需成本！"

            r_pct = (r_pays / max(1.0, req_cost)) * 100 if req_cost > 0 else 0
            h_pct = (h_pays / max(1.0, req_cost)) * 100 if req_cost > 0 else 0
            
            if is_invalid:
                st.error(warning_msg)
            else:
                st.markdown(f"<h4><span style='font-size: 1.2em; color: {cfg['PARTY_B_COLOR']}'>監管墊付: {r_pays:.1f} ({r_pct:.1f}%)</span> / 總需成本: {req_cost:.1f} / <span style='font-size: 1.2em; color: {cfg['PARTY_A_COLOR']}'>執行自籌: {h_pays:.1f} ({h_pct:.1f}%)</span></h4>", unsafe_allow_html=True)
            
            plan_dict = {
                'proj_fund': proj_fund, 'bid_cost': bid_cost, 
                'r_pays': r_pays, 'h_pays': h_pays, 
                'claimed_decay': claimed_decay, 'claimed_cost': claimed_cost,
                'author': active_role, 
                'author_party': view_party.name, 
                'req_cost': req_cost,
                'fine_mult': fine_mult 
            }

            st.markdown("<br>", unsafe_allow_html=True)
            c_btn1, c_btn2, c_btn3 = st.columns(3)
            if c_btn1.button("📤 送出提案草案", use_container_width=True, type="primary", disabled=is_invalid):
                if game.p1_step == 'ultimatum_draft_r':
                    game.p1_selected_plan = plan_dict; game.p1_step = 'ultimatum_resolve_h'; game.proposing_party = game.h_role_party
                else:
                    game.p1_proposals[active_role] = plan_dict
                    if game.p1_step == 'draft_r': game.p1_step = 'draft_h'; game.proposing_party = game.h_role_party
                    else: game.p1_step = 'voting_pick'; game.proposing_party = game.ruling_party
                st.rerun()
                
            if active_role == 'R' and game.p1_step == 'draft_r':
                if c_btn2.button("💥 下達最後通牒", use_container_width=True, disabled=is_invalid):
                    game.p1_selected_plan = plan_dict
                    game.p1_step = 'ultimatum_resolve_h'
                    game.proposing_party = game.h_role_party
                    st.session_state.news_flash = f"🗞️ **[快訊] 監管系統下達最後通牒！** {view_party.name} 迫使執行系統接受，否則將觸發內閣換位！"
                    st.rerun()
                
                swap_cost = 0 if view_party.name == game.ruling_party.name else penalty_amt
                if c_btn3.button(f"🔄 強制通過並換位 (成本: {swap_cost:.1f})", use_container_width=True, disabled=is_invalid):
                    st.session_state.turn_data.update(plan_dict)
                    engine.trigger_swap(game, swap_cost, "監管系統強制接管！")
                    game.proposing_party = game.ruling_party; st.rerun()

            if not is_invalid or opp_plan:
                st.markdown("---")
                c_prop1, c_prop2 = st.columns(2)
                if not is_invalid:
                    with c_prop1:
                        ui_proposal.render_proposal_component('📜 當前草案預覽', plan_dict, game, view_party, cfg)
                if opp_plan:
                    with c_prop2:
                        ui_proposal.render_proposal_component('📜 對手草案參考', opp_plan, game, view_party, cfg)

    elif game.p1_step == 'voting_pick':
        st.markdown(f"### 🗳️ 執政黨裁決 ({game.ruling_party.name})")
        if view_party.name != game.ruling_party.name:
            st.warning("⏳ 等待執政黨裁決...")
        else:
            c_prop1, c_prop2 = st.columns(2)
            for idx, key in enumerate(['R', 'H']):
                plan = game.p1_proposals.get(key)
                col = c_prop1 if key == 'R' else c_prop2
                with col:
                    if plan is None:
                        st.info("等待對手提出草案...")
                        continue
                    ui_proposal.render_proposal_component('⚖️ 監管系統草案' if key=='R' else '🛡️ 執行系統草案', plan, game, view_party, cfg)
                    if st.button(f"✅ 選擇此草案", key=f"pick_{key}", use_container_width=True):
                        game.p1_selected_plan = plan; game.p1_step = 'voting_confirm'
                        game.proposing_party = game.party_B if game.ruling_party.name == game.party_A.name else game.party_A; st.rerun()

    elif game.p1_step == 'voting_confirm':
        if view_party.name != game.proposing_party.name: st.warning("⏳ 等待對手確認...")
        else:
            ui_proposal.render_proposal_component('📜 待確認草案', game.p1_selected_plan, game, view_party, cfg)
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("✅ 同意法案並簽署", use_container_width=True, type="primary"):
                st.session_state.turn_data.update(game.p1_selected_plan)
                st.session_state.news_flash = f"🗞️ **[快訊] 法案通過！** 經過 {game.proposal_count} 回合，法案已正式簽署。"
                st.session_state.anim = 'balloons'
                game.phase = 2; game.proposing_party = game.ruling_party; st.rerun()
            
            if c2.button("❌ 拒絕並重新談判", use_container_width=True):
                game.proposal_count += 1; game.p1_step = 'draft_r'; game.proposing_party = game.r_role_party; st.rerun()
            
            if c3.button(f"🔄 同意並換位\n(成本: {penalty_amt:.1f})", use_container_width=True):
                st.session_state.turn_data.update(game.p1_selected_plan)
                engine.trigger_swap(game, penalty_amt, "政權轉移！")
                game.proposing_party = game.ruling_party; st.rerun()
            
            if game.proposing_party.name == game.h_role_party.name:
                if c4.button("💥 強制最終決定 (最後通牒)", use_container_width=True):
                    st.session_state.news_flash = f"🗞️ **[快訊] 執行系統下達最後通牒！** 監管系統只剩最後一次機會。"
                    game.p1_step = 'ultimatum_draft_r'; game.proposing_party = game.r_role_party; st.rerun()

    elif game.p1_step == 'ultimatum_resolve_h':
        st.markdown("### 🚨 最終決定 (僅限執行系統)")
        if view_party.name != game.h_role_party.name: 
            st.warning(f"⏳ 等待執行系統 {game.h_role_party.name}...")
        else:
            ui_proposal.render_proposal_component('📜 監管系統最終通牒草案', game.p1_selected_plan, game, view_party, cfg)
            st.markdown("---")
            c1, c2 = st.columns(2)
            if c1.button("✅ 接受最後通牒", use_container_width=True, type="primary"):
                st.session_state.turn_data.update(game.p1_selected_plan)
                st.session_state.news_flash = f"🗞️ **[快訊] 接受最後通牒！** 執行系統妥協了。"
                st.session_state.anim = 'balloons'
                game.phase = 2; game.proposing_party = game.ruling_party; st.rerun()
                
            if c2.button(f"🔄 翻桌並換位\n(警告：成本 {penalty_amt:.1f})", use_container_width=True):
                st.session_state.turn_data.update(game.p1_selected_plan)
                engine.trigger_swap(game, penalty_amt, "內閣倒台！")
                game.proposing_party = game.r_role_party; st.rerun()

# ==========================================
# phase2.py
# ==========================================
import streamlit as st
import config
import formulas
import ui_core
import i18n
t = i18n.t

def render(game, view_party, opponent_party, cfg):
    is_h = (view_party.name == game.h_role_party.name)
    h_label = '🛡️ 執行系統'
    r_label = '⚖️ 監管系統'
    st.subheader(f"🛠️ 第二階段：資源分配與執行 - 輪到： {view_party.name} ({h_label if is_h else r_label})")
    
    d = st.session_state.get('turn_data', {})
    req_cost = float(d.get('req_cost', 0.0))
    bid_cost = float(d.get('bid_cost', 1.0))
    
    if is_h: cw = float(view_party.wealth) + float(d.get('r_pays', 0.0))
    else: cw = float(view_party.wealth) - float(d.get('r_pays', 0.0))
    
    h_bonus = 1.2 if is_h else 1.0
    r_bonus = 1.2 if not is_h else 1.0
    
    med_cap = view_party.media_ability * 10.0 * h_bonus
    inv_cap = view_party.investigate_ability * 10.0 * r_bonus
    ci_cap = view_party.stealth_ability * 10.0
    edu_cap = view_party.edu_ability * 10.0 * r_bonus
    eng_base_ev = view_party.build_ability * 10.0 * h_bonus
    eng_limit = 100.0 + (view_party.build_ability * 100.0) 
    
    last_acts = view_party.last_acts if hasattr(view_party, 'last_acts') else {}

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📣 資源分配")
        
        st.write(f"**情報調查處 (量能: {inv_cap:.1f} 操作點)**")
        col_i1, col_i2, col_i3 = st.columns(3)
        if not is_h:
            w_i_cen = col_i1.number_input("媒體審查", min_value=0, max_value=100, value=last_acts.get('w_i_cen', 0), key=f"w_i_cen_{view_party.name}")
        else:
            w_i_cen = 0
            col_i1.write(f"**媒體審查**")
            col_i1.caption("(僅限監管系統)")
            
        w_i_org = col_i2.number_input("組織審計", min_value=0, max_value=100, value=last_acts.get('w_i_org', 0), key=f"w_i_org_{view_party.name}")
        w_i_fin = col_i3.number_input("調查金流", min_value=0, max_value=100, value=last_acts.get('w_i_fin', 0), key=f"w_i_fin_{view_party.name}")
        i_tot = max(1, w_i_cen + w_i_org + w_i_fin)
        alloc_inv_censor = inv_cap * (w_i_cen / i_tot) if w_i_cen else 0
        alloc_inv_audit = inv_cap * (w_i_org / i_tot) if w_i_org else 0
        alloc_inv_fin = inv_cap * (w_i_fin / i_tot) if w_i_fin else 0
        
        st.write(f"**反情報與隱蔽處 (量能: {ci_cap:.1f} 操作點)**")
        col_c1, col_c2, col_c3 = st.columns(3)
        if is_h:
            w_c_cen = col_c1.number_input("反媒體審查", min_value=0, max_value=100, value=last_acts.get('w_c_cen', 0), key=f"w_c_cen_{view_party.name}")
        else:
            w_c_cen = 0
            col_c1.write(f"**反媒體審查**")
            col_c1.caption("(僅限執行系統)")
            
        w_c_org = col_c2.number_input("隱藏組織", min_value=0, max_value=100, value=last_acts.get('w_c_org', 0), key=f"w_c_org_{view_party.name}")
        w_c_fin = col_c3.number_input("隱藏金流", min_value=0, max_value=100, value=last_acts.get('w_c_fin', 0), key=f"w_c_fin_{view_party.name}")
        c_tot = max(1, w_c_cen + w_c_org + w_c_fin)
        alloc_ci_anticen = ci_cap * (w_c_cen / c_tot) if w_c_cen else 0
        alloc_ci_hideorg = ci_cap * (w_c_org / c_tot) if w_c_org else 0
        alloc_ci_hidefin = ci_cap * (w_c_fin / c_tot) if w_c_fin else 0
        
        st.write(f"**黨媒公關處 (量能: {med_cap:.1f} 影響力)**")
        col_m1, col_m2, col_m3 = st.columns(3)
        w_m_cam = col_m1.number_input("公關造勢", min_value=0, max_value=100, value=last_acts.get('w_m_cam', 0), key=f"w_m_cam_{view_party.name}")
        w_m_inc = col_m2.number_input("煽動情緒", min_value=0, max_value=100, value=last_acts.get('w_m_inc', 0), key=f"w_m_inc_{view_party.name}")
        w_m_con = col_m3.number_input("媒體控制", min_value=0, max_value=100, value=last_acts.get('w_m_con', 0), key=f"w_m_con_{view_party.name}")
        m_tot = max(1, w_m_cam + w_m_inc + w_m_con)
        alloc_med_camp = med_cap * (w_m_cam / m_tot) if w_m_cam else 0
        alloc_med_incite = med_cap * (w_m_inc / m_tot) if w_m_inc else 0
        alloc_med_control = med_cap * (w_m_con / m_tot) if w_m_con else 0
        
        st.write(f"**教育處 (量能: {edu_cap:.1f} 影響力)**")
        old_edu_stance = view_party.edu_stance
        e_dir = st.radio("教育方針轉變", ["維持現狀", "向左偏移 (填鴨愚民)", "向右偏移 (批判思考)"], horizontal=True, key=f"e_dir_{view_party.name}")
        if e_dir == "向左偏移 (填鴨愚民)": edu_shift = -edu_cap * 0.5
        elif e_dir == "向右偏移 (批判思考)": edu_shift = edu_cap * 0.5
        else: edu_shift = 0.0
        new_edu_stance = max(-100.0, min(100.0, old_edu_stance + edu_shift))
        st.info(f"教育方針: `{old_edu_stance:.1f}` ➔ `{new_edu_stance:.1f}`")

    with c2:
        st.markdown("#### 🔒 財政與工程建設 (工程值)")
        
        fake_ev = 0.0
        c_net = 0.0
        
        unit_cost = formulas.calc_unit_cost(cfg, game.gdp, view_party.build_ability, game.current_real_decay)
        
        if is_h:
            c_net = st.number_input(f"分配真實 EV 至國家專案 (目標 EV: {bid_cost})", min_value=0.0, value=float(last_acts.get('c_net', min(cw/max(0.01, unit_cost), bid_cost))), key=f"c_net_{view_party.name}")
            fake_ev_cost_ratio = cfg.get('FAKE_EV_COST_RATIO', 0.2)
            fake_label = f"注入假 EV (每 1 單位假 EV 需花費 {fake_ev_cost_ratio} EV 成本)"
            fake_ev = st.number_input(fake_label, min_value=0.0, value=float(last_acts.get('fake_ev', 0.0)), key=f"fake_ev_{view_party.name}")
            
            project_ev_cost = c_net + (fake_ev * fake_ev_cost_ratio)
        else:
            project_ev_cost = 0.0

        st.markdown("##### 🛠️ 升級部門 (目標等級)")
        st.caption(f"*(所有能力值可無限升級。每年最大升級 EV 上限: `{eng_limit:.1f}`)*")
        
        def render_dept(label, key, obj_val, cap_text_func):
            old_ui_val = obj_val * 10.0
            col_l, col_r = st.columns([1, 2.5])
            with col_l:
                new_ui_val = st.number_input(label, min_value=1.0, value=float(old_ui_val), step=1.0, key=key)
            with col_r:
                old_raw = old_ui_val / 10.0
                new_raw = new_ui_val / 10.0
                maint_now = old_raw * 5.0
                maint_new = new_raw * 5.0
                
                if new_ui_val > old_ui_val:
                    cost = (new_raw**2 - old_raw**2) * 10.0
                    st.caption(f"**當前:** `{old_ui_val:.0f}` (維護費: -{maint_now:.1f}) ➔ **新:** `{new_ui_val:.0f}` (維護費: -{maint_new:.1f}) | <span style='color:orange'>**升級成本:** -{cost:.1f} EV</span>", unsafe_allow_html=True)
                    ev_cost = cost
                    is_up = True
                elif new_ui_val < old_ui_val:
                    refund = (old_raw**2 - new_raw**2) * 5.0
                    st.caption(f"**當前:** `{old_ui_val:.0f}` (維護費: -{maint_now:.1f}) ➔ **新:** `{new_ui_val:.0f}` (維護費: -{maint_new:.1f}) | <span style='color:blue'>**降級退款:** +{refund:.1f} EV</span>", unsafe_allow_html=True)
                    ev_cost = -refund
                    is_up = False
                else:
                    st.caption(f"**當前:** `{old_ui_val:.0f}` (維護費: -{maint_now:.1f}) ➔ **未改變**", unsafe_allow_html=True)
                    ev_cost = 0.0
                    is_up = False

                st.caption(f"💡 *{cap_text_func(new_ui_val)}*")
            return new_raw, ev_cost, maint_new, (ev_cost if is_up else 0.0)

        t_pre, pre_cost, pre_maint, pre_up = render_dept("智庫預測處", f"tt_pre_{view_party.name}", view_party.predict_ability, lambda v: f"產出 {v:.1f} EV 用於提升預測準確度")
        t_inv, inv_cost, inv_maint, inv_up = render_dept("情報調查處", f"tt_inv_{view_party.name}", view_party.investigate_ability, lambda v: f"產出 {v * r_bonus:.1f} 操作點用於情報調查")
        t_med, med_cost, med_maint, med_up = render_dept("黨媒公關處", f"tt_med_{view_party.name}", view_party.media_ability, lambda v: f"產出 {v * h_bonus:.1f} 影響力用於公關與控制")
        t_stl, stl_cost, stl_maint, stl_up = render_dept("反情報與隱蔽處", f"tt_stl_{view_party.name}", view_party.stealth_ability, lambda v: f"產出 {v:.1f} 操作點用於隱蔽行動")
        t_bld, bld_cost, bld_maint, bld_up = render_dept("工程建設處", f"tt_bld_{view_party.name}", view_party.build_ability, lambda v: f"解鎖 {100.0 + (v * 100.0):.1f} EV 升級上限")
        t_edu, edu_cost, edu_maint, edu_up = render_dept("教育處", f"tt_edu_{view_party.name}", view_party.edu_ability, lambda v: f"產出 {v * r_bonus:.1f} 影響力用於意識形態轉變")

        total_upgrade_cost = pre_cost + inv_cost + med_cost + stl_cost + bld_cost + edu_cost
        total_maint_cost = pre_maint + inv_maint + med_maint + stl_maint + bld_maint + edu_maint
        pure_upgrades = pre_up + inv_up + med_up + stl_up + bld_up + edu_up
        
        total_ev_required = project_ev_cost + total_maint_cost + total_upgrade_cost
        invest_wealth = total_ev_required * max(0.01, unit_cost)
        
        remaining_wealth = cw - invest_wealth
        
        st.markdown("---")
        st.markdown(f"**💰 財政結算**")
        st.write(f"- 總 EV 成本: `{total_ev_required:.1f}` EV *(單位成本: `${unit_cost:.2f}`)*")
        st.write(f"- 總資金花費: `${invest_wealth:.1f}`")
        
        is_invalid = False
        if remaining_wealth < 0:
            st.error(f"🚨 **資金不足**：預估剩餘資金為 `${remaining_wealth:.1f}`。請減少 EV 花費或降低部門維護等級！")
            is_invalid = True
        else:
            st.success(f"✅ **預估剩餘資金:** `${cw:.1f}` - `${invest_wealth:.1f}` = **`${remaining_wealth:.1f}`**")

        if pure_upgrades > eng_limit:
            st.error(f"🚨 升級超過工程上限！最大允許升級 EV： `{eng_limit:.1f}`。 (當前純升級花費： `{pure_upgrades:.1f}`)")
            is_invalid = True

    my_acts = {
        'w_i_cen': w_i_cen, 'w_i_org': w_i_org, 'w_i_fin': w_i_fin,
        'alloc_inv_censor': alloc_inv_censor, 'alloc_inv_audit': alloc_inv_audit, 'alloc_inv_fin': alloc_inv_fin,
        'w_c_cen': w_c_cen, 'w_c_org': w_c_org, 'w_c_fin': w_c_fin,
        'alloc_ci_anticen': alloc_ci_anticen, 'alloc_ci_hideorg': alloc_ci_hideorg, 'alloc_ci_hidefin': alloc_ci_hidefin,
        'w_m_cam': w_m_cam, 'w_m_inc': w_m_inc, 'w_m_con': w_m_con,
        'alloc_med_camp': alloc_med_camp, 'alloc_med_incite': alloc_med_incite, 'alloc_med_control': alloc_med_control,
        'edu_stance': new_edu_stance, 'fake_ev': fake_ev, 
        't_pre': t_pre, 't_inv': t_inv, 't_med': t_med, 't_stl': t_stl, 't_bld': t_bld, 't_edu': t_edu,
        'invest_wealth': invest_wealth, 'c_net': c_net
    }
    
    st.markdown("---")
    
    if is_h:
        act_ha = my_acts
        act_ra = st.session_state.get(f"{opponent_party.name}_acts", {'alloc_med_control': 0, 'alloc_med_camp': 0, 'alloc_med_incite': 0, 'alloc_inv_censor': 0, 'alloc_inv_fin': 0, 'invest_wealth': 0})
    else:
        act_ra = my_acts
        act_ha = st.session_state.get(f"{opponent_party.name}_acts", {'alloc_med_control': 0, 'alloc_med_camp': 0, 'alloc_med_incite': 0, 'fake_ev': 0, 'c_net': float(d.get('bid_cost') or 1.0), 'alloc_ci_hidefin': 0, 'invest_wealth': 0})

    eval_c_net = float(act_ha.get('c_net', 0))
    eval_fake_ev = float(act_ha.get('fake_ev', 0))
    r_pays = float(d.get('r_pays', 0.0))
    proj_fund = float(d.get('proj_fund', 0.0))
    
    # Preview using fake_ev_spent and fake_ev_safe as the same since it's not audited yet
    res_prev = formulas.calc_economy(cfg, float(game.gdp), float(game.total_budget), proj_fund, bid_cost, float(game.h_role_party.build_ability), float(game.current_real_decay), r_pays=r_pays, c_net_override=eval_c_net, fake_ev_spent=eval_fake_ev, fake_ev_safe=eval_fake_ev)
    
    h_media_pwr = float(act_ha.get('alloc_med_control', 0.0))
    r_media_pwr = float(act_ra.get('alloc_med_control', 0.0))

    shift_preview = formulas.calc_performance_preview(
        cfg, game.h_role_party, game.r_role_party, game.ruling_party.name,
        res_prev['est_gdp'], game.gdp, 
        float(d.get('claimed_decay', 0.0)), game.sanity, game.emotion, bid_cost, res_prev['c_net_total'],
        h_media_pwr, r_media_pwr
    )
    
    # --- NEW CALCULATION LOGIC ADDED HERE ---
    # 1. Calculate Base Income
    h_base_prev = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == game.h_role_party.name else 0))
    r_base_prev = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == game.r_role_party.name else 0))

    # 2. Calculate Project Profit
    r_project_profit = res_prev['payout_r'] + (proj_fund * (1.0 - res_prev['h_idx'])) - r_pays
    
    h_inc_prev = h_base_prev + res_prev['h_project_profit']
    r_inc_prev = r_base_prev + r_project_profit

    # 3. Calculate ROI
    eval_h_pays = max(0.0, req_cost - r_pays)
    h_roi = (res_prev['h_project_profit'] / eval_h_pays) * 100.0 if eval_h_pays > 0 else float('inf')
    r_roi = (r_project_profit / r_pays) * 100.0 if r_pays > 0 else float('inf')
    # --- END NEW LOGIC ---

    # Include the calculated keys in the dictionary
    preview_data = {
        'gdp': res_prev['est_gdp'], 'budg': game.total_budget, 'h_fund': res_prev['payout_h'],
        'san': game.sanity, 'emo': game.emotion,
        'my_perf_gdp': shift_preview[view_party.name]['perf_gdp'],
        'my_perf_proj': shift_preview[view_party.name]['perf_proj'],
        'opp_perf_gdp': shift_preview[opponent_party.name]['perf_gdp'],
        'opp_perf_proj': shift_preview[opponent_party.name]['perf_proj'],
        'h_inc': h_inc_prev,
        'r_inc': r_inc_prev,
        'my_roi': h_roi if is_h else r_roi,
        'opp_roi': r_roi if is_h else h_roi
    }
    
    ui_core.render_dashboard(game, view_party, cfg, is_preview=True, preview_data=preview_data)
    
    if not is_invalid and st.button("確認行動並執行", use_container_width=True, type="primary"):
        st.session_state[f"{view_party.name}_acts"] = my_acts
        if f"{opponent_party.name}_acts" not in st.session_state:
            game.proposing_party = opponent_party
            st.rerun()
        else:
            game.phase = 3
            game.proposing_party = game.r_role_party
            st.rerun()

# ==========================================
# phase3.py
# ==========================================
import streamlit as st
import random
import formulas
import i18n
t = i18n.t

def render(game, cfg):
    st.header("共生體制時報 - 年度結算報告")
    
    if not game.last_year_report:
        rp, hp = game.r_role_party, game.h_role_party
        ra = st.session_state.get(f"{rp.name}_acts", {})
        ha = st.session_state.get(f"{hp.name}_acts", {})
        d = st.session_state.get('turn_data', {})
        
        fine_mult = float(d.get('fine_mult', 0.3)) 
        
        for k in ['t_pre', 't_inv', 't_med', 't_stl', 't_bld', 't_edu', 'edu_stance']:
            if k in ra: setattr(rp, 'predict_ability' if k == 't_pre' else 'investigate_ability' if k == 't_inv' else 'media_ability' if k == 't_med' else 'stealth_ability' if k == 't_stl' else 'build_ability' if k == 't_bld' else 'edu_ability' if k == 't_edu' else 'edu_stance', float(ra[k]))
            if k in ha: setattr(hp, 'predict_ability' if k == 't_pre' else 'investigate_ability' if k == 't_inv' else 'media_ability' if k == 't_med' else 'stealth_ability' if k == 't_stl' else 'build_ability' if k == 't_bld' else 'edu_ability' if k == 't_edu' else 'edu_stance', float(ha[k]))
        
        returned_to_r = 0.0
        confiscated_to_budget = 0.0
        hp_wealth_penalty = 0.0
        
        req_cost = float(d.get('req_cost', 0.0))
        proj_fund = float(d.get('proj_fund') or 0.0)
        bid_cost = float(d.get('bid_cost') or 1.0)
        claimed_decay = float(d.get('claimed_decay') or 0.0)
        r_pays = float(d.get('r_pays') or 0.0)
        
        fake_ev = float(ha.get('fake_ev') or 0.0)
        c_net_h = float(ha.get('c_net', 0))
        
        r_inv_fin = float(ra.get('alloc_inv_fin', 0))
        h_ci_fin = float(ha.get('alloc_ci_hidefin', 0))
        net_fin_ev = r_inv_fin - h_ci_fin
        
        if net_fin_ev > 0:
            chunk_size = max(0.01, 10.0 / net_fin_ev)
            catch_prob = min(1.0, cfg.get('FAKE_EV_CATCH_BASE_RATE', 0.10) * max(1.0, net_fin_ev * 0.1))
        else:
            chunk_size = float('inf')
            catch_prob = 0.0

        unit_cost_real = formulas.calc_unit_cost(cfg, game.gdp, hp.build_ability, game.current_real_decay)
        
        caught_fake_ev = safe_fake_ev = caught_value = fine_value = 0.0
        fake_ev_caught = False

        if 'pending_dice_roll' not in st.session_state:
             st.session_state.pending_dice_roll = {
                 'fake_ev': fake_ev,
                 'catch_prob': catch_prob,
                 'chunk_size': chunk_size,
                 'fine_mult': fine_mult,
                 'unit_cost_real': unit_cost_real,
                 'is_rolled': False
             }
        
        dice_data = st.session_state.pending_dice_roll

        if dice_data['is_rolled']:
            caught_fake_ev, safe_fake_ev, caught_value, fine_value = dice_data['fake_ev_results']
            
            returned_to_r += caught_value
            hp_wealth_penalty += (caught_value + fine_value)
            confiscated_to_budget += fine_value
            fake_ev_caught = (caught_fake_ev > 0)
            
        hp_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == hp.name else 0))
        rp_base = game.total_budget * (cfg['BASE_INCOME_RATIO'] + (cfg['RULING_BONUS_RATIO'] if game.ruling_party.name == rp.name else 0))
        
        actual_h_wealth_available = max(0.0, hp.wealth + req_cost - float(ha.get('invest_wealth', 0)) - hp_wealth_penalty + hp_base)
        
        # --- 修正假 EV 的傳遞參數 ---
        eval_fake_ev_safe = safe_fake_ev if dice_data['is_rolled'] else fake_ev
        res_exec = formulas.calc_economy(
            cfg, float(game.gdp), float(game.total_budget), proj_fund, bid_cost, 
            float(hp.build_ability), float(game.current_real_decay), 
            r_pays=r_pays, h_wealth=actual_h_wealth_available, 
            c_net_override=c_net_h, fake_ev_spent=fake_ev, fake_ev_safe=eval_fake_ev_safe
        )
        
        budg = cfg['BASE_TOTAL_BUDGET'] + (res_exec['est_gdp'] * cfg['HEALTH_MULTIPLIER'])
        
        hp_project_net = res_exec['h_project_profit']
        total_bonus_deduction = game.total_budget * ((cfg['BASE_INCOME_RATIO'] * 2) + cfg['RULING_BONUS_RATIO'])
        base_r_surplus = max(0.0, game.total_budget - total_bonus_deduction - proj_fund)
        unspent_proj = proj_fund * (1.0 - res_exec['h_idx'])
        
        rp_project_net = base_r_surplus + unspent_proj - r_pays
        
        hp_inc = hp_base + hp_project_net + req_cost
        rp_inc = rp_base + rp_project_net + returned_to_r
        
        r_censor_alloc = float(ra.get('alloc_inv_censor', 0))
        h_anti_censor_alloc = float(ha.get('alloc_ci_anticen', 0))
        censor_diff = r_censor_alloc - h_anti_censor_alloc

        B = game.boundary_B
        opp_indices = range(B + 1, 201) if hp.name == game.party_A.name else range(1, B + 1)
        censor_successes = 0; censor_failures = 0
        
        for i in opp_indices:
            rig = formulas.get_spin_rigidity(i, game.sanity, getattr(game, 'h_rigidity_buff', {}).get('amount', 0.0), getattr(game, 'h_rigidity_buff', {}).get('party'), B, game.party_A.name)
            if random.random() > rig: censor_successes += 1
            else: censor_failures += 1
        
        censor_weight = max(0.0, censor_diff / 100.0) 
        censor_emotion_add = censor_weight * censor_successes
        censor_rigidity_buff = censor_weight * (censor_successes / (censor_successes + censor_failures)) if (censor_successes + censor_failures) > 0 else 0.0
            
        if censor_diff > 0: game.h_rigidity_buff = {'amount': censor_rigidity_buff, 'duration': 2, 'party': hp.name}
            
        h_media_pwr = float(ha.get('alloc_med_control', 0.0))
        r_media_pwr = float(ra.get('alloc_med_control', 0.0))
        
        raw_p_plan, raw_p_exec, d_a, d_e, d_c = formulas.generate_raw_support(cfg, res_exec['est_gdp'], game.gdp, claimed_decay, bid_cost, res_exec['c_net_total'])
        
        plan_correct, plan_wrong, correct_prob = formulas.apply_sanity_filter(raw_p_plan, game.sanity, game.emotion, is_preview=False)
        exec_correct, exec_wrong, _ = formulas.apply_sanity_filter(raw_p_exec, game.sanity, game.emotion, is_preview=False)
        
        ruling_name = game.ruling_party.name
        ruling_media_pwr = h_media_pwr if ruling_name == hp.name else r_media_pwr
        opp_media_pwr = r_media_pwr if ruling_name == hp.name else h_media_pwr
            
        ruling_spun_plan, opp_spun_plan = formulas.apply_media_spin(plan_wrong, ruling_media_pwr, opp_media_pwr)
        h_spun_exec, r_spun_exec = formulas.apply_media_spin(exec_wrong, h_media_pwr, r_media_pwr)

        perf_A = 0.0; perf_B = 0.0
        spin_A = 0.0; spin_B = 0.0

        if ruling_name == game.party_A.name: 
            perf_A += plan_correct; spin_A += ruling_spun_plan
            spin_B += opp_spun_plan
        else: 
            perf_B += plan_correct; spin_B += ruling_spun_plan
            spin_A += opp_spun_plan

        if hp.name == game.party_A.name: 
            perf_A += exec_correct; spin_A += h_spun_exec
            spin_B += r_spun_exec
        else: 
            perf_B += exec_correct; spin_B += h_spun_exec
            spin_A += r_spun_exec
            
        def get_camp_pwr(alloc, san, emo, edu_stance):
            rote_factor = max(0.0, -edu_stance / 100.0)
            return alloc * max(0.0, (1.0 - (san/100.0) + (emo/100.0) + rote_factor))

        h_camp_pwr = get_camp_pwr(float(ha.get('alloc_med_camp', 0.0)), game.sanity, game.emotion, hp.edu_stance)
        r_camp_pwr = get_camp_pwr(float(ra.get('alloc_med_camp', 0.0)), game.sanity, game.emotion, rp.edu_stance)

        if hp.name == game.party_A.name: spin_A += h_camp_pwr; spin_B += r_camp_pwr
        else: spin_B += h_camp_pwr; spin_A += r_camp_pwr

        net_perf_A = perf_A - perf_B
        net_spin_A = spin_A - spin_B
        old_boundary = game.boundary_B
        
        new_boundary, perf_used, perf_conquered, spin_used, spin_conquered = formulas.run_conquest_split(
            game.boundary_B, net_perf_A, net_spin_A, game.sanity, 
            getattr(game, 'h_rigidity_buff', {}).get('amount', 0.0), getattr(game, 'h_rigidity_buff', {}).get('party'), game.party_A.name
        )
        
        game.boundary_B = new_boundary
        game.party_A.support = new_boundary * 0.5
        game.party_B.support = 100.0 - game.party_A.support
        
        gdp_grw_bonus = ((res_exec['est_gdp'] - game.gdp)/max(1.0, game.gdp)) * 100.0
        
        total_incite_rolls = float(ha.get('alloc_med_incite', 0.0)) + float(ra.get('alloc_med_incite', 0.0))
        incite_points = formulas.calc_incite_success(total_incite_rolls, game.emotion)
        emotion_delta = (incite_points * 0.1) + censor_emotion_add - gdp_grw_bonus - (game.sanity * 0.15)
        new_emotion = max(0.0, min(100.0, game.emotion + emotion_delta))
        
        f_target_san = max(0.0, min(100.0, 50.0 + (ha.get('edu_stance', 0) + ra.get('edu_stance', 0)) * 0.5))
        f_san_move = (f_target_san - game.sanity) * 0.2
        new_sanity = max(0.0, min(100.0, game.sanity - (new_emotion * 0.02) + f_san_move))
        
        game.last_year_report = {
            'old_gdp': game.gdp, 'old_san': game.sanity, 'old_emo': game.emotion, 'old_budg': game.total_budget, 'old_h_fund': game.h_fund,
            'new_san': new_sanity, 'new_emo': new_emotion,
            'h_party_name': hp.name, 'r_party_name': rp.name,
            'raw_p_plan': raw_p_plan, 'raw_p_exec': raw_p_exec,
            'perf_A': perf_A, 'perf_B': perf_B, 'net_perf_A': net_perf_A,
            'spin_A': spin_A, 'spin_B': spin_B, 'net_spin_A': net_spin_A,
            'perf_used': perf_used, 'perf_conquered': perf_conquered,
            'spin_used': spin_used, 'spin_conquered': spin_conquered,
            'old_boundary': old_boundary, 'new_boundary': new_boundary,
            'correct_prob': correct_prob,
            'h_spun_exec': h_spun_exec, 'r_spun_exec': r_spun_exec, 
            'censor_successes': censor_successes, 'censor_failures': censor_failures, 'censor_emotion_add': censor_emotion_add, 'censor_buff': censor_rigidity_buff,
            'h_inc': hp_inc, 'r_inc': rp_inc, 
            'h_base': hp_base, 'r_base': rp_base, 
            'h_project_net': hp_project_net, 'r_project_net': rp_project_net,
            'payout_h': res_exec['payout_h'], 'act_fund': res_exec['act_fund'], 'r_pays': r_pays,
            'r_extra': returned_to_r,
            'caught_fake_ev': caught_fake_ev,
            'caught_value': caught_value,
            'fine_value': fine_value,
            'hp_penalty': hp_wealth_penalty,
            'fake_ev_caught': fake_ev_caught,
            'fake_ev_attempted': fake_ev,
            'chunk_size': chunk_size,
            'fine_mult': fine_mult,
            'proj_fund': proj_fund, 'h_idx': res_exec['h_idx'], 
            'total_bonus_deduction': total_bonus_deduction, 'base_r_surplus': base_r_surplus, 'unspent_proj': unspent_proj,
            'h_invest_wealth': float(ha.get('invest_wealth', 0)), 'r_invest_wealth': float(ra.get('invest_wealth', 0))
        }
        
        game.gdp = res_exec['est_gdp']
        game.sanity = new_sanity
        game.emotion = new_emotion
        game.h_fund = res_exec['payout_h']
        game.total_budget = budg + confiscated_to_budget
        
        hp.wealth += hp_inc - float(ha.get('invest_wealth', 0)) - hp_wealth_penalty
        rp.wealth += rp_inc - float(ra.get('invest_wealth', 0))

        if hasattr(game, 'h_rigidity_buff') and game.h_rigidity_buff['duration'] > 0:
            game.h_rigidity_buff['duration'] -= 1
            if game.h_rigidity_buff['duration'] <= 0:
                game.h_rigidity_buff = {'amount': 0.0, 'duration': 0, 'party': None}

        is_election_end = (game.year % cfg['ELECTION_CYCLE'] == 0)
        if is_election_end:
            winner = game.party_A if game.party_A.support > game.party_B.support else game.party_B
            game.ruling_party = winner

        hp.last_acts = ha.copy(); rp.last_acts = ra.copy()
        game.record_history(is_election=is_election_end)
    
    dice_data = st.session_state.get('pending_dice_roll')
    if dice_data and not dice_data['is_rolled']:
        st.markdown("---")
        st.markdown(f"### 🎲 啟動財務查核")
        if dice_data['chunk_size'] == float('inf'):
            st.info("監管系統缺乏足夠的操作量能來啟動查核。金流成功隱蔽。")
            if st.button("⏩ 進入最終結算", type="primary", use_container_width=True):
                st.session_state.pending_dice_roll['fake_ev_results'] = (0.0, dice_data['fake_ev'], 0.0, 0.0)
                st.session_state.pending_dice_roll['is_rolled'] = True
                st.rerun()
        else:
            st.warning(f"**目標：** `{dice_data['fake_ev']:.1f}` 假 EV | **抓包機率：** 每 `{dice_data['chunk_size']:.2f}` 單位有 `{dice_data['catch_prob']*100:.1f}%` 機率。")

            if st.button("🎲 執行財務查核！", type="primary", use_container_width=True):
                with st.spinner('調查員正在追蹤金流...'):
                    import time
                    time.sleep(1.5) 
                    fake_ev_res = formulas.calc_fake_ev_dice(dice_data['fake_ev'], dice_data['catch_prob'], dice_data['fine_mult'], dice_data['chunk_size'], dice_data['unit_cost_real'])
                    st.session_state.pending_dice_roll['fake_ev_results'] = fake_ev_res
                    st.session_state.pending_dice_roll['is_rolled'] = True
                st.rerun() 
        st.stop()

    rep = game.last_year_report
    
    st.markdown("---")
    st.markdown("### 🗞️ **[頭版頭條]**")
    if rep.get('caught_fake_ev', 0) > 0:
        st.error(f"**[貪腐醜聞] 豆腐渣工程曝光！**\n\n調查員揭發了 `{rep['caught_fake_ev']:.1f}` 單位的造假工程 (假 EV)。\n- **{rep['h_party_name']}** 遭沒收非法所得 `${rep['caught_value']:.1f}` 並裁罰 `${rep['fine_value']:.1f}`。\n- **{rep['r_party_name']}** 獲得全額吹哨者獎金 `${rep['caught_value']:.1f}`。\n- 國庫收取 `${rep['fine_value']:.1f}` 的懲罰性罰金。")
    else:
        if rep.get('chunk_size', float('inf')) == float('inf'):
            st.success(f"**[粉飾太平] 查無不法？**\n\n監管系統未能徹底調查金流。所有帳目在「字面上」皆合法過關。")
        elif rep.get('fake_ev_attempted', 0) > 0:
            st.success(f"**[全身而退] 查核過關！**\n\n儘管進行了嚴格調查，執政黨的「特別帳戶」依然滴水不漏。")
        else:
            st.success(f"**[廉能政府] 零造假工程！**\n\n調查員翻遍了帳冊，確認所有專案皆為 100% 真材實料。")
            
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### 📊 經濟指標")
        st.write(f"- **GDP:** `{rep['old_gdp']:.1f}` ➔ **`{game.gdp:.1f}`**")
        st.write(f"- **公民素養:** `{rep['old_san']:.1f}` ➔ **`{game.sanity:.1f}`** ({game.sanity - rep['old_san']:+.1f})")
        st.write(f"- **選民情緒:** `{rep['old_emo']:.1f}` ➔ **`{game.emotion:.1f}`** ({game.emotion - rep['old_emo']:+.1f})")
        
        st.markdown(f"### 🏛️ 財政總結")
        if rep['fine_value'] > 0:
            st.success(f"國庫收入: +`${rep['fine_value']:.1f}` (懲罰性罰金)")
            
        with st.expander(f"💼 {rep['h_party_name']} (執行方) 財務報表"):
            st.write(f"**專案淨利潤:** `${rep['h_project_net']:.1f}`")
            st.write(f"+ 基本收入: `${rep['h_base']:.1f}`")
            if rep['caught_fake_ev'] > 0:
                st.write(f"- 沒收不法所得: `-${rep['caught_value']:.1f}`")
                st.write(f"- 懲罰性罰金: `-${rep['fine_value']:.1f}`")
            st.write(f"- 工程/部門升級成本: `-${rep['h_invest_wealth']:.1f}`")
            net_cash = rep['h_project_net'] + rep['h_base'] - rep.get('hp_penalty', 0) - rep['h_invest_wealth']
            st.write(f"**最終現金流:** `${net_cash:.1f}`")

        with st.expander(f"⚖️ {rep['r_party_name']} (監管方) 財務報表"):
            st.write(f"**基本收入:** `${rep['r_base']:.1f}`")
            st.write(f"- 支付監管墊付款: `-${rep['r_pays']:.1f}`")
            st.write(f"+ 追回未執行資金: `${rep['unspent_proj']:.1f}`")
            st.write(f"+ 預算結餘: `${rep['base_r_surplus']:.1f}`")
            if rep['r_extra'] > 0: 
                st.write(f"+ 吹哨者獎金: `${rep['r_extra']:.1f}`")
            st.write(f"- 部門升級成本: `-${rep['r_invest_wealth']:.1f}`")
            net_cash_r = rep['r_base'] - rep['r_pays'] + rep['unspent_proj'] + rep['base_r_surplus'] + rep['r_extra'] - rep['r_invest_wealth']
            st.write(f"**最終現金流:** `${net_cash_r:.1f}`")

    with c2:
        st.markdown(f"### 🗳️ 選舉板塊位移 (支持度)")
        
        net_ammo = rep['net_perf_A'] + rep['net_spin_A']
        atk_party = game.party_A.name if net_ammo > 0 else game.party_B.name
        def_party = game.party_B.name if net_ammo > 0 else game.party_A.name
        
        if abs(net_ammo) < 1.0: 
            st.info("🤝 雙方支持度僵持不下，未產生顯著的板塊位移。")
        else:
            st.success(f"🔥 **淨優勢:** `{abs(net_ammo):.1f}`！**{atk_party}** 對 **{def_party}** 發動了影響力攻勢！")

        if st.session_state.get('god_mode'):
            with st.expander("👁️ 上帝模式：選舉機制與真實支持度", expanded=True):
                st.write(f"*(理性歸因率: `{rep['correct_prob']*100:.1f}%`)*")
                
                st.markdown(f"**政績表現 (真實傷害)**: {game.party_A.name} `{rep['perf_A']:.1f}` | {game.party_B.name} `{rep['perf_B']:.1f}`")
                if abs(rep['net_perf_A']) >= 1.0:
                    atk_p = game.party_A.name if rep['net_perf_A'] > 0 else game.party_B.name
                    st.success(f"⚡ {atk_p} 造成了 `{rep['perf_used']:.1f}` 點無法防禦的影響，征服了 **{rep['perf_conquered']}** 個票倉！")
                    
                st.markdown(f"**媒體與公關 (可防禦)**: {game.party_A.name} `{rep['spin_A']:.1f}` | {game.party_B.name} `{rep['spin_B']:.1f}`")
                if abs(rep['net_spin_A']) >= 1.0:
                    atk_s = game.party_A.name if rep['net_spin_A'] > 0 else game.party_B.name
                    blocked = rep['spin_used'] - rep['spin_conquered']
                    st.warning(f"🛡️ 選民理性護甲吸收了 `{blocked:.1f}` 點公關影響。{atk_s} 征服了 **{rep['spin_conquered']}** 個票倉。")

                old_sup_A = rep['old_boundary'] * 0.5
                new_sup_A = rep['new_boundary'] * 0.5
                old_sup_B = 100.0 - old_sup_A
                new_sup_B = 100.0 - new_sup_A
                
                st.markdown(f"#### 📊 **{game.party_A.name} 真實支持度:** `{old_sup_A:.1f}%` ➔ **`{new_sup_A:.1f}%`** ({new_sup_A - old_sup_A:+.1f}%)")
                st.markdown(f"#### 📊 **{game.party_B.name} 真實支持度:** `{old_sup_B:.1f}%` ➔ **`{new_sup_B:.1f}%`** ({new_sup_B - old_sup_B:+.1f}%)")
        else:
            st.caption("*(真實支持度百分比已隱藏。請進行民調以揭露當前局勢。)*")

    st.markdown("---")
    if st.button("⏩ 進入下一年", type="primary", use_container_width=True):
        if 'pending_dice_roll' in st.session_state: del st.session_state.pending_dice_roll
        
        is_election_end = (game.year % cfg['ELECTION_CYCLE'] == 0)
        game.year += 1
        
        if game.year > cfg['END_YEAR']: game.phase = 4
        else:
            game.phase = 1; game.p1_step = 'draft_r'
            game.p1_proposals = {'R': None, 'H': None}; game.p1_selected_plan = None
            
            if is_election_end:
                game.r_role_party = game.ruling_party
                game.h_role_party = game.party_B if game.ruling_party.name == game.party_A.name else game.party_A
            
            game.proposing_party = game.r_role_party
            game.last_year_report = None
            
            for k in list(st.session_state.keys()):
                if k.endswith('_acts') or k.startswith('up_'): del st.session_state[k]
            if 'turn_initialized' in st.session_state: del st.session_state.turn_initialized
        st.rerun()

# ==========================================
# phase4.py
# ==========================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import i18n
t = i18n.t

def render(game, cfg):
    st.balloons()
    st.title("🏁 遊戲結束！共生體制最終歷史結算")
    
    df = pd.DataFrame(game.history)
    
    if 'Ruling' in df.columns:
        st.subheader("📊 1. 政黨輪替與系統分佈")
        st.write("分析是否出現了「一黨獨大」的局面，或是權力被動態共享。")
        c1, c2 = st.columns(2)
        with c1:
            rule_counts = df['Ruling'].value_counts().reset_index()
            rule_counts.columns = ['Party', 'Years']
            fig_ruling = px.pie(rule_counts, names='Party', values='Years', title="作為執政黨的年數", hole=0.3, color='Party', color_discrete_map={cfg['PARTY_A_NAME']: cfg['PARTY_A_COLOR'], cfg['PARTY_B_NAME']: cfg['PARTY_B_COLOR']})
            st.plotly_chart(fig_ruling, use_container_width=True)
        with c2:
            h_counts = df['H_Party'].value_counts().reset_index()
            h_counts.columns = ['Party', 'Years']
            fig_h = px.pie(h_counts, names='Party', values='Years', title="作為執行系統 (H) 的年數", hole=0.3, color='Party', color_discrete_map={cfg['PARTY_A_NAME']: cfg['PARTY_A_COLOR'], cfg['PARTY_B_NAME']: cfg['PARTY_B_COLOR']})
            st.plotly_chart(fig_h, use_container_width=True)

    st.subheader("📈 2. 總體經濟與社會素養")
    st.write("政黨間的互動是帶領國家走向繁榮與具備批判思考的公民社會，還是陷入經濟停滯與極端對立？")
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(x=df['Year'], y=df['GDP'], name="總 GDP", line=dict(color='blue', width=3)), secondary_y=False)
    fig1.add_trace(go.Scatter(x=df['Year'], y=df['Sanity'], name="公民素養 (0-100)", line=dict(color='purple', width=3)), secondary_y=True)
    
    for _, row in df.iterrows():
        y = row['Year']
        if row['Is_Swap']: fig1.add_vline(x=y, line_dash="dot", line_color="red", annotation_text="內閣倒閣!", annotation_position="top left")
        if row['Is_Election']: fig1.add_vline(x=y, line_dash="dash", line_color="green", annotation_text="選舉", annotation_position="bottom right")

    st.plotly_chart(fig1, use_container_width=True)
    
    if 'A_Edu' in df.columns:
        st.subheader("🏛️ 3. 政策軌跡與制度效率")
        st.write("回顧教育意識形態 (填鴨愚民 vs 批判思考) 以及內部制度的平均升級曲線。")
        c3, c4 = st.columns(2)
        with c3:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=df['Year'], y=df['A_Edu'], name=f"{cfg['PARTY_A_NAME']} 教育方針", marker_color=cfg['PARTY_A_COLOR']))
            fig2.add_trace(go.Bar(x=df['Year'], y=df['B_Edu'], name=f"{cfg['PARTY_B_NAME']} 教育方針", marker_color=cfg['PARTY_B_COLOR']))
            fig2.update_layout(title="歷史教育意識形態 (負值: 填鴨愚民 / 正值: 批判思考)", barmode='group')
            st.plotly_chart(fig2, use_container_width=True)
        with c4:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=df['Year'], y=df['A_Avg_Abi'], name=f"{cfg['PARTY_A_NAME']} 平均部門能力", line=
