import streamlit as st
import random
import formulas

def run_ai_turn(game, cfg, ai_party_name="Equity"):
    """
    攔截並執行 AI 的回合。如果成功執行返回 True，否則返回 False。
    """
    # 如果現在不是 AI 的回合，直接跳出
    if game.proposing_party.name != ai_party_name:
        return False 

    ai_party = game.party_A if game.party_A.name == ai_party_name else game.party_B
    is_h = (game.h_role_party.name == ai_party_name)
    active_role = 'H' if is_h else 'R'

    # ==========================================
    # PHASE 1: 預算與法案談判
    # ==========================================
    if game.phase == 1:
        if game.p1_step in ['draft_r', 'draft_h', 'ultimatum_draft_r']:
            # 1. 讀取大環境預測與計算資金上限
            total_bonus = game.total_budget * ((cfg['BASE_INCOME_RATIO'] * 2) + cfg['RULING_BONUS_RATIO'])
            max_proj = max(10.0, float(game.total_budget) - total_bonus)

            obs_bld = ai_party.build_ability
            tt_decay = ai_party.current_forecast
            unit_cost = formulas.calc_unit_cost(cfg, game.gdp, obs_bld, tt_decay)

            # 2. 依照角色生成極端草案
            if is_h:
                proj_fund = max_proj * random.uniform(0.7, 0.9) # H 想要超高獎金
                bid_cost = proj_fund * random.uniform(0.8, 1.2) 
                r_pays = (bid_cost * unit_cost) * random.uniform(0.2, 0.5) # 要求 R 黨大量墊款
                fine_mult = 0.3 
            else:
                proj_fund = max_proj * random.uniform(0.2, 0.4) # R 黨極度摳門
                bid_cost = proj_fund * random.uniform(1.2, 1.8) # 要求超高建設量
                r_pays = 0.0 # R 黨一毛不拔
                fine_mult = random.uniform(0.8, 1.5) # 要求極高違約金

            req_cost = bid_cost * unit_cost
            r_pays = min(r_pays, req_cost) # 防呆

            plan = {
                'proj_fund': proj_fund, 'bid_cost': bid_cost,
                'r_pays': r_pays, 'h_pays': max(0.0, req_cost - r_pays),
                'claimed_decay': tt_decay, 'claimed_cost': unit_cost,
                'author': active_role, 'author_party': ai_party_name,
                'req_cost': req_cost, 'fine_mult': fine_mult
            }

            # 3. 提交草案並推進狀態機
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
            st.rerun()

        elif game.p1_step == 'voting_pick':
            # 執政黨挑選法案 (AI 絕對選自己提的)
            my_draft = game.p1_proposals.get(active_role)
            game.p1_selected_plan = my_draft
            game.p1_step = 'voting_confirm'
            game.proposing_party = game.party_B if game.ruling_party.name == game.party_A.name else game.party_A
            st.rerun()

        elif game.p1_step in ['voting_confirm', 'ultimatum_resolve_h']:
            # 投票決議：前兩輪有 40% 機率翻桌重談，否則同意法案
            if game.p1_step == 'voting_confirm' and game.proposal_count < 3 and random.random() < 0.4:
                game.proposal_count += 1
                game.p1_step = 'draft_r'
                game.proposing_party = game.r_role_party
            else:
                st.session_state.turn_data.update(game.p1_selected_plan)
                game.phase = 2
                game.proposing_party = game.ruling_party
                st.session_state.news_flash = "🗞️ **[BREAKING] Bill Passed!** AI Opponent has signed the bill."
            st.rerun()

    # ==========================================
    # PHASE 2: 資源分配與部門操作
    # ==========================================
    elif game.phase == 2:
        d = st.session_state.get('turn_data', {})
        bid_cost = float(d.get('bid_cost', 1.0))

        # 初始化所有動作 (不升級以避免 EV 破產)
        my_acts = {
            'w_i_cen': 0, 'w_i_org': 0, 'w_i_fin': 0,
            'alloc_inv_censor': 0, 'alloc_inv_audit': 0, 'alloc_inv_fin': 0,
            'w_c_cen': 0, 'w_c_org': 0, 'w_c_fin': 0,
            'alloc_ci_anticen': 0, 'alloc_ci_hideorg': 0, 'alloc_ci_hidefin': 0,
            'w_m_cam': 50, 'w_m_inc': 0, 'w_m_con': 50,
            'alloc_med_camp': ai_party.media_ability * 10 * 0.5 * (1.2 if is_h else 1.0),
            'alloc_med_incite': 0,
            'alloc_med_control': ai_party.media_ability * 10 * 0.5 * (1.2 if is_h else 1.0),
            'edu_stance': ai_party.edu_stance,
            'fake_ev': 0.0,
            't_pre': ai_party.predict_ability, 't_inv': ai_party.investigate_ability,
            't_med': ai_party.media_ability, 't_stl': ai_party.stealth_ability,
            't_bld': ai_party.build_ability, 't_edu': ai_party.edu_ability,
            'invest_wealth': 0.0, 'c_net': 0.0
        }

        inv_cap = ai_party.investigate_ability * 10 * (1.2 if not is_h else 1.0)
        ci_cap = ai_party.stealth_ability * 10
        unit_cost = formulas.calc_unit_cost(cfg, game.gdp, ai_party.build_ability, game.current_real_decay)
        maint_ev = sum([ai_party.predict_ability, ai_party.investigate_ability, ai_party.media_ability, ai_party.stealth_ability, ai_party.build_ability, ai_party.edu_ability]) * 1.5

        if is_h:
            # H 黨戰略：全力隱藏金流，並有一定機率使用豆腐渣工程
            my_acts['w_c_fin'] = 100
            my_acts['alloc_ci_hidefin'] = ci_cap
            
            c_net = bid_cost
            # AI 的貪婪設定：40% 機率會塞入 10%~30% 的假 EV
            fake_ev = bid_cost * random.uniform(0.1, 0.3) if random.random() < 0.4 else 0.0
            
            my_acts['fake_ev'] = fake_ev
            my_acts['c_net'] = c_net

            # 計算維持這些操作需要花多少黨產買 EV
            eng_base_ev = ai_party.build_ability * 10 * 1.2
            total_ev_req = c_net + (fake_ev * cfg.get('FAKE_EV_COST_RATIO', 0.2)) + maint_ev
            ev_to_buy = max(0.0, total_ev_req - eng_base_ev)
            my_acts['invest_wealth'] = ev_to_buy * max(0.01, unit_cost)
            
        else:
            # R 黨戰略：瘋狗模式，全力追查金流
            my_acts['w_i_fin'] = 100
            my_acts['alloc_inv_fin'] = inv_cap
            
            eng_base_ev = ai_party.build_ability * 10 * 1.0
            total_ev_req = maint_ev
            ev_to_buy = max(0.0, total_ev_req - eng_base_ev)
            my_acts['invest_wealth'] = ev_to_buy * max(0.01, unit_cost)

        # 寫入狀態並結束回合
        st.session_state[f"{ai_party.name}_acts"] = my_acts

        opp = game.party_B if ai_party.name == game.party_A.name else game.party_A
        if f"{opp.name}_acts" not in st.session_state:
            game.proposing_party = opp
        else:
            game.phase = 3
            game.proposing_party = game.r_role_party
        st.rerun()

    return False
