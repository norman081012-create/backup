# ==========================================
# phase2.py
# 負責 第二階段 (政策執行與結算) 的 UI 與邏輯
# ==========================================
import streamlit as st
import random
import formulas
import ui_core

def render(game, view_party, opponent_party, cfg):
    is_h = (view_party.name == game.h_role_party.name)
    st.subheader(f"🛠️ Phase 2: 政策執行與行動 - 輪到 {view_party.name} ({'🛡️ 執行系統' if is_h else '⚖️ 監管系統'})")
    
    d = st.session_state.turn_data
    req_pay = d.get('h_pays', 0) if is_h else d.get('r_pays', 0)
    cw = int(view_party.wealth)
    max_cost = formulas.get_max_ability_cost(cfg['CURRENT_GDP'], cfg['ABILITY_CAP_DIVISOR'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📣 政策與媒體")
        st.info(f"📜法定專案款 (不可動用): `${req_pay}`")
        if is_h: st.caption("💡 **執行系統特性**: 媒體操控值 1.2 倍加成")
        else: st.caption("💡 **監管系統特性**: 調查情報值 1.2 倍加成")
        
        h_corr_pct = st.slider("💸 秘密貪污 (%)", 0, 100, 0) if is_h else 0
        h_crony_pct = st.slider("🏢 圖利自身廠商 (%)", 0, max(0, 100 - h_corr_pct), 0) if is_h else 0
        if is_h: st.caption("圖利增加制度外收益(預設100)。貪污+圖利不可超100%，總和被調查皆視為違法。")
        
        media_ctrl = st.slider("📺 媒體操控 (推卸責任/攻擊)", 0, cw, min(50, cw))
        camp_amt = st.slider("🎉 舉辦競選 (提升自身支持度)", 0, cw, 0)
        incite_emo = st.slider("🔥 煽動情緒 (短期降理智)", 0, cw, 0)
        
        judicial_active = st.checkbox(f"⚖️ 啟動司法審查 (維護費 ${cfg['JUDICIAL_REVIEW_COST']})")
        jud_cost = cfg['JUDICIAL_REVIEW_COST'] if judicial_active else 0
        
    with c2:
        st.markdown("#### 🔒 內部部門投資")
        t_int, c_int = ui_core.ability_slider("🕵️ 情報處", f"up_int", view_party.intel_ability, cw, cfg, max_cost)
        t_c_int, c_c_int = ui_core.ability_slider("🛡️ 反情報處", f"up_c_int", view_party.counter_intel_ability, cw, cfg, max_cost)
        t_thk, c_thk = ui_core.ability_slider("🧠 智庫", f"up_thk", view_party.thinktank_ability, cw, cfg, max_cost)
        t_med, c_med = ui_core.ability_slider("📺 黨媒", f"up_med", view_party.media_ability, cw, cfg, max_cost)
        t_bld, c_bld = ui_core.ability_slider("🏗️ 建設能力", f"up_bld", view_party.build_ability, cw, cfg, max_cost) if is_h else (view_party.build_ability, 0)

    tot = req_pay + media_ctrl + camp_amt + incite_emo + jud_cost + c_int + c_c_int + c_thk + c_med + c_bld
    st.write(f"**總花費:** `{int(tot)}` / `{cw}`")
    
    ra, ha = {}, {}
    if f"{opponent_party.name}_acts" in st.session_state:
        opp_acts = st.session_state[f"{opponent_party.name}_acts"]
        ra = opp_acts if is_h else {'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 'corr': h_corr_pct, 'crony': h_crony_pct, 'judicial': judicial_active}
        ha = {'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 'corr': h_corr_pct, 'crony': h_crony_pct, 'judicial': judicial_active} if is_h else opp_acts
    else:
        ra = {'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 'corr': h_corr_pct, 'crony': h_crony_pct, 'judicial': judicial_active} if not is_h else {'media': 0, 'camp': 0, 'incite': 0, 'corr': 0, 'crony': 0, 'judicial': False}
        ha = {'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo, 'corr': h_corr_pct, 'crony': h_crony_pct, 'judicial': judicial_active} if is_h else {'media': 0, 'camp': 0, 'incite': 0, 'corr': 0, 'crony': 0, 'judicial': False}

    corr_amt = d.get('total_funds', 0) * (ha.get('corr', 0) / 100.0)
    crony_base = d.get('total_funds', 0) * (ha.get('crony', 0) / 100.0)
    crony_income = crony_base * 0.1 * d.get('r_value', 1.0)
    act_build = d.get('total_funds', 0) - corr_amt
    
    h_bst = (act_build * d.get('h_ratio', 1.0) * (game.h_role_party.build_ability/10.0)) / max(0.1, d.get('r_value', 1.0)**2)
    new_h_fund = max(0.0, game.h_fund + h_bst - (view_party.current_forecast * (d.get('r_value', 1.0)**2) * 0.2 * game.h_fund))
    gdp_bst = (act_build * (game.h_role_party.build_ability/10.0)) / cfg['BUILD_DIFF']
    new_gdp = max(0.0, game.gdp + gdp_bst - (view_party.current_forecast * 1000))
    budg = cfg['BASE_TOTAL_BUDGET'] + (new_gdp * cfg['HEALTH_MULTIPLIER'])
    h_shr = new_h_fund / max(1.0, budg) if budg > 0 else 0.5
    
    hp_inc_est = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == game.h_role_party.name else 0) + (budg * h_shr) - d.get('h_pays',0) + corr_amt + crony_income
    rp_inc_est = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == game.r_role_party.name else 0) + (budg * (1 - h_shr)) - d.get('r_pays',0)

    shift_preview = formulas.calc_support_shift(cfg, game.h_role_party, game.r_role_party, new_h_fund, new_gdp, d.get('target_h_fund', 600), d.get('target_gdp', 5000), game.gdp, ha, ra)
    
    preview_data = {
        'gdp': new_gdp, 'budg': budg, 'h_fund': new_h_fund,
        'san': max(0.0, min(1.0, game.sanity - (game.emotion * 0.002))),
        'emo': max(0.0, min(100.0, game.emotion + (ha['incite'] + ra['incite']) * 0.1 - (((new_gdp - game.gdp)/max(1.0, game.gdp))*100) - (game.sanity * 20.0))),
        'h_inc': hp_inc_est, 'r_inc': rp_inc_est,
        'h_roi': (hp_inc_est / max(1.0, float(d.get('h_pays',0)))) * 100.0 if d.get('h_pays',0) > 0 else float('inf'),
        'r_roi': (rp_inc_est / max(1.0, float(d.get('r_pays',0)))) * 100.0 if d.get('r_pays',0) > 0 else float('inf'),
        'my_sup_shift': shift_preview['actual_shift'] if is_h else -shift_preview['actual_shift'],
        'opp_sup_shift': -shift_preview['actual_shift'] if is_h else shift_preview['actual_shift']
    }
    
    ui_core.render_dashboard(game, view_party, cfg, is_preview=True, preview_data=preview_data)
    
    if tot <= cw and st.button("確認行動/結算", use_container_width=True, type="primary"):
        st.session_state[f"{view_party.name}_acts"] = {
            'media': media_ctrl, 'camp': camp_amt, 'incite': incite_emo,
            'corr': h_corr_pct, 'crony': h_crony_pct, 'judicial': judicial_active, 'jud_cost': jud_cost,
            't_int': t_int, 't_c_int': t_c_int, 't_thk': t_thk, 't_med': t_med, 't_bld': t_bld,
            'legal': req_pay
        }
        
        if f"{opponent_party.name}_acts" not in st.session_state:
            game.proposing_party = opponent_party; st.rerun()
        else:
            rp, hp = game.r_role_party, game.h_role_party
            ra, ha = st.session_state[f"{rp.name}_acts"], st.session_state[f"{hp.name}_acts"]
            
            hp.last_acts = {'policy': ha['media']+ha['camp']+ha['incite']+ha['jud_cost'], 'legal': ha['legal']}
            rp.last_acts = {'policy': ra['media']+ra['camp']+ra['incite']+ra['jud_cost'], 'legal': ra['legal']}

            confiscated = 0.0; caught = False; fine = 0.0
            corr_amt = d.get('total_funds', 0) * (ha['corr'] / 100.0)
            crony_base = d.get('total_funds', 0) * (ha['crony'] / 100.0)
            crony_income = crony_base * 0.1 * d.get('r_value', 1.0)
            suspicious_total = corr_amt + crony_base
            act_build = d.get('total_funds', 0) - corr_amt
            
            if suspicious_total > 0:
                intel_acc = max(0.0, (rp.intel_ability * cfg['R_INV_BONUS']) - hp.counter_intel_ability)
                catch_prob = min(1.0, (intel_acc / 100.0) * (suspicious_total / max(1.0, hp.wealth)) * 5.0)
                if random.random() < catch_prob:
                    caught = True; fine = suspicious_total * cfg['CORRUPTION_PENALTY']; confiscated = suspicious_total; corr_amt = 0; crony_income = 0
            
            h_bst = (act_build * d.get('h_ratio', 1.0) * (hp.build_ability/10.0)) / max(0.1, d.get('r_value', 1.0)**2)
            new_h_fund = max(0.0, game.h_fund + h_bst - (game.current_real_decay * (d.get('r_value', 1.0)**2) * 0.2 * game.h_fund))
            
            gdp_bst = (act_build * (hp.build_ability/10.0)) / cfg['BUILD_DIFF']
            new_gdp = max(0.0, game.gdp + gdp_bst - (game.current_real_decay * 1000))
            budg = cfg['BASE_TOTAL_BUDGET'] + (new_gdp * cfg['HEALTH_MULTIPLIER'])
            h_shr = new_h_fund / max(1.0, budg) if budg > 0 else 0.5
            
            hp_inc = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == hp.name else 0) + (budg * h_shr) - d.get('h_pays',0) + corr_amt + crony_income - fine
            rp_inc = cfg['DEFAULT_BONUS'] + (cfg['RULING_BONUS'] if game.ruling_party.name == rp.name else 0) + (budg * (1 - h_shr)) - d.get('r_pays',0)
            
            shift = formulas.calc_support_shift(cfg, hp, rp, new_h_fund, new_gdp, d.get('target_h_fund', 600), d.get('target_gdp', 5000), game.gdp, ha, ra)
            if caught: shift['actual_shift'] -= 5.0
            hp_sup_new = max(0.0, min(100.0, hp.support + shift['actual_shift']))
            
            gdp_grw_bonus = ((new_gdp - game.gdp)/max(1.0, game.gdp)) * 100.0
            emotion_delta = (ha['incite'] + ra['incite']) * 0.1 - gdp_grw_bonus - (game.sanity * 20.0)
            game.emotion = max(0.0, min(100.0, game.emotion + emotion_delta))
            
            game.sanity = max(0.0, min(1.0, game.sanity - (game.emotion * 0.002)))
            
            game.last_year_report = {
                'old_gdp': game.gdp, 'old_san': game.sanity, 'old_emo': game.emotion, 'old_budg': game.total_budget, 'old_h_fund': game.h_fund,
                'h_party_name': hp.name, 'h_perf': shift['h_perf'], 'r_perf': shift['r_perf'],
                'h_inc': hp_inc, 'r_inc': rp_inc, 'est_h_inc': preview_data['h_inc'], 'est_r_inc': preview_data['r_inc'],
                'real_decay': game.current_real_decay, 'view_party_forecast': view_party.current_forecast
            }

            hp.support, rp.support = hp_sup_new, 100.0 - hp_sup_new
            
            if game.year % cfg['ELECTION_CYCLE'] == 1:
                winner = hp if hp.support > rp.support else rp
                st.session_state.news_flash = f"🎉 **【大選結果】** {winner.name} 取勝，成為當權！"
                st.session_state.anim = 'balloons'
                game.ruling_party = winner

            game.h_fund, game.gdp = new_h_fund, new_gdp
            game.total_budget = budg + confiscated
            hp.wealth += hp_inc; rp.wealth += rp_inc

            rp.intel_ability = ra['t_int']; rp.counter_intel_ability = ra['t_c_int']; rp.thinktank_ability = ra['t_thk']; rp.media_ability = ra['t_med']
            hp.intel_ability = ha['t_int']; hp.counter_intel_ability = ha['t_c_int']; hp.thinktank_ability = ha['t_thk']; hp.media_ability = ha['t_med']; hp.build_ability = ha['t_bld']

            game.record_history(is_election=(game.year % cfg['ELECTION_CYCLE'] == 1))
            
            game.year += 1; game.phase = 1; game.p1_step = 'draft_r'
            game.p1_proposals = {'R': None, 'H': None}; game.p1_selected_plan = None
            game.proposing_party = game.r_role_party
            for k in list(st.session_state.keys()):
                if k.startswith('ui_decay_') or k.endswith('_acts'): del st.session_state[k]
            del st.session_state.turn_initialized; st.rerun()
