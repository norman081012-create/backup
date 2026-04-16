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

