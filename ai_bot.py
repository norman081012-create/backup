# ==========================================
# ai_bot.py (The Symbiocracy AI Engine)
# ==========================================
import random
import formulas
import streamlit as st

def take_turn(game, cfg):
    ai_party = game.party_A if game.party_A.name == game.ai_party_name else game.party_B
    is_h = (game.h_role_party.name == ai_party.name)
    active_role = 'H' if is_h else 'R'

    if game.phase == 1:
        if game.p1_step in ['draft_r', 'draft_h', 'ultimatum_draft_r']:
            total_bonus = game.total_budget * ((cfg['BASE_INCOME_RATIO'] * 2) + cfg['RULING_BONUS_RATIO'])
            max_proj = max(10.0, float(game.total_budget) - total_bonus)
            unit_cost = formulas.calc_unit_cost(cfg, game.gdp, ai_party.build_ability, ai_party.current_forecast)

            # 📌 AI 自動從生成的建案池中挑選
            my_projects = ai_party.projects
            if is_h:
                # 執行方傾向挑選 EV 較大、有賺頭的案子 (中/高階)
                selected_proj = sorted(my_projects, key=lambda x: x['ev'], reverse=True)[0]
                proj_fund = max_proj * random.uniform(0.7, 0.9) 
                bid_cost = selected_proj['ev']
                req_cost = bid_cost * unit_cost
                r_pays = min(req_cost * random.uniform(0.2, 0.4), max_proj)
                fine_mult = 0.3 
            else:
                # 監管方傾向挑選 EV 較小、容易壓榨的案子 (低階)
                selected_proj = sorted(my_projects, key=lambda x: x['ev'])[0]
                proj_fund = max_proj * random.uniform(0.2, 0.4) 
                bid_cost = selected_proj['ev']
                req_cost = bid_cost * unit_cost
                r_pays = 0.0 
                fine_mult = random.uniform(0.8, 1.5) 

            plan = {
                'proj_fund': proj_fund, 'bid_cost': bid_cost,
                'r_pays': r_pays, 'h_pays': max(0.0, req_cost - r_pays),
                'claimed_decay': ai_party.current_forecast, 'claimed_cost': unit_cost,
                'author': active_role, 'author_party': ai_party.name,
                'req_cost': req_cost, 'fine_mult': fine_mult,
                'proj_name': selected_proj['name'],
                'proj_tier': selected_proj['tier'],
                'proj_exec_mult': selected_proj['exec_mult'],
                'proj_macro_mult': selected_proj['macro_mult'],
                'proj_obs_min': selected_proj['obs_min'],
                'proj_obs_max': selected_proj['obs_max']
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
            my_draft = game.p1_proposals.get(active_role)
            if not my_draft: my_draft = game.p1_proposals.get('H' if active_role == 'R' else 'R')
            game.p1_selected_plan = my_draft
            game.p1_step = 'voting_confirm'
            game.proposing_party = game.party_B if game.ruling_party.name == game.party_A.name else game.party_A

        elif game.p1_step in ['voting_confirm', 'ultimatum_resolve_h']:
            if game.p1_step == 'voting_confirm' and game.proposal_count < 3 and random.random() < 0.4:
                game.proposal_count += 1
                game.p1_step = 'draft_r'
                game.proposing_party = game.r_role_party
                st.session_state.news_flash = f"🗞️ **[BREAKING]** {ai_party.name} rejected the draft. Renegotiation started."
            else:
                st.session_state.turn_data.update(game.p1_selected_plan)
                game.phase = 2
                game.proposing_party = game.ruling_party
                st.session_state.news_flash = f"🗞️ **[BREAKING]** {ai_party.name} accepted the draft. Bill passed!"

    elif game.phase == 2:
        d = st.session_state.get('turn_data', {})
        bid_cost = float(d.get('bid_cost', 1.0))
        
        inv_cap = ai_party.investigate_ability * 10 * (1.2 if not is_h else 1.0)
        ci_cap = ai_party.stealth_ability * 10
        med_cap = ai_party.media_ability * 10 * (1.2 if is_h else 1.0)
        
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
            my_acts['w_c_fin'] = 100
            my_acts['alloc_ci_hidefin'] = ci_cap
            
            c_net = bid_cost
            fake_ev = bid_cost * random.uniform(0.1, 0.3) if random.random() < 0.4 else 0.0
            
            my_acts['fake_ev'] = fake_ev
            my_acts['c_net'] = c_net

            total_ev_req = c_net + (fake_ev * cfg.get('FAKE_EV_COST_RATIO', 0.2)) + maint_ev
            ev_to_buy = max(0.0, total_ev_req - eng_base_ev)
            my_acts['invest_wealth'] = ev_to_buy * max(0.01, unit_cost)
        else:
            my_acts['w_i_fin'] = 100
            my_acts['alloc_inv_fin'] = inv_cap
            
            total_ev_req = maint_ev
            ev_to_buy = max(0.0, total_ev_req - eng_base_ev)
            my_acts['invest_wealth'] = ev_to_buy * max(0.01, unit_cost)

        st.session_state[f"{ai_party.name}_acts"] = my_acts

        opp_name = game.human_party_name
        if f"{opp_name}_acts" not in st.session_state:
            game.proposing_party = game.party_A if game.party_A.name == opp_name else game.party_B
        else:
            game.phase = 3
            game.proposing_party = game.r_role_party
