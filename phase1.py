# ==========================================
# phase1.py
# 負責 第一階段 (提案與談判) 的 UI 與邏輯
# ==========================================
import streamlit as st
import formulas
import engine
import ui_core
import i18n
t = i18n.t

def render(game, view_party, cfg):
    penalty_amt = int(game.total_budget * cfg['TRUST_BREAK_PENALTY_RATIO'])
    st.subheader(t(f"🤝 Phase 1: 監管系統委託執行系統建設提案 (輪數: {game.proposal_count})", f"🤝 Phase 1: R-System Proposal (Round: {game.proposal_count})"))
    
    if game.p1_step in ['draft_r', 'draft_h', 'ultimatum_draft_r']:
        active_role = 'R' if game.p1_step in ['draft_r', 'ultimatum_draft_r'] else 'H'
        
        if game.p1_step == 'ultimatum_draft_r':
            st.error(t("🚨 **最後通牒啟動中：** 監管系統必須擬定最終裁決草案！", "🚨 **Ultimatum Active:** R-System must draft final resolution!"))
            
        if view_party.name != (game.r_role_party.name if active_role == 'R' else game.h_role_party.name):
            st.warning(t(f"⏳ 等待對手公布草案...", f"⏳ Waiting for opponent's draft..."))
        else:
            role_text_zh = '監管系統' if active_role == 'R' else '執行系統'
            role_text_en = 'R-System' if active_role == 'R' else 'H-System'
            st.markdown(t(f"#### 📝 {view_party.name} ({role_text_zh}黨) 草案擬定室", f"#### 📝 {view_party.name} ({role_text_en}) Draft Room"))
            
            opp_role = 'H' if active_role == 'R' else 'R'
            opp_plan = game.p1_proposals.get(opp_role)
            opp_claimed = opp_plan['claimed_decay'] if opp_plan else None
            
            input_key = f"ui_decay_val_{game.year}_{active_role}"
            if input_key not in st.session_state: st.session_state[input_key] = float(view_party.current_forecast)
            
            opp_txt = t(f"對手公告: {opp_claimed:.2f}", f"Opp. Claimed: {opp_claimed:.2f}") if opp_claimed is not None else t("等待對手公告", "Awaiting Opp.")
            st.markdown(t(f"**公告衰退值 (當前估算: {st.session_state[input_key]:.2f})** | {opp_txt}", f"**Claimed Decay (Current: {st.session_state[input_key]:.2f})** | {opp_txt}"))
            claimed_decay = st.number_input(t("公告衰退值", "Claimed Decay"), value=float(st.session_state[input_key]), step=0.01, key=f"num_{input_key}", label_visibility="collapsed")
            st.session_state[input_key] = claimed_decay
                
            max_p = max(10.0, float(game.total_budget))
            proj_fund = st.slider(t("標案總額 (最高不超過當年總預算)", "Total Bid Amount (Max=Budget)"), 0.0, max_p, float(min(1000.0, max_p)), 10.0)
            bid_cost = st.slider(t("標案成本 (要求之建設產出值，留點利潤給對手賺)", "Bid Cost (Required construction)"), 1.0, max(1.0, float(proj_fund)), max(1.0, float(proj_fund * 0.8)), 10.0)
            
            safe_req = max(1, int(proj_fund))
            r_pays = st.slider(t(f"💰 資金分配調整 (監管出資額)", f"💰 Funding Distribution (R-Pays)"), 0, safe_req, int(safe_req * 0.5))
            h_pays = proj_fund - r_pays
            r_pct = (r_pays / max(1, proj_fund)) * 100
            h_pct = (h_pays / max(1, proj_fund)) * 100
            
            st.markdown(t(f"<h4><span style='font-size: 1.2em'>監管出資: {r_pays} ({r_pct:.1f}%)</span> / 總額: {proj_fund} / <span style='font-size: 1.2em'>執行出資: {h_pays} ({h_pct:.1f}%)</span></h4>", f"<h4><span style='font-size: 1.2em'>R-Pays: {r_pays} ({r_pct:.1f}%)</span> / Total: {proj_fund} / <span style='font-size: 1.2em'>H-Pays: {h_pays} ({h_pct:.1f}%)</span></h4>"), unsafe_allow_html=True)
            
            plan_dict = {
                'proj_fund': proj_fund, 'bid_cost': bid_cost, 
                'r_pays': r_pays, 'h_pays': h_pays, 'claimed_decay': claimed_decay,
                'author': active_role
            }

            c_btn1, c_btn2, c_btn3 = st.columns(3)
            if c_btn1.button(t("📤 送出常規草案", "📤 Submit Draft"), use_container_width=True, type="primary"):
                if game.p1_step == 'ultimatum_draft_r':
                    game.p1_selected_plan = plan_dict; game.p1_step = 'ultimatum_resolve_h'; game.proposing_party = game.h_role_party
                else:
                    game.p1_proposals[active_role] = plan_dict
                    if game.p1_step == 'draft_r': game.p1_step = 'draft_h'; game.proposing_party = game.h_role_party
                    else: game.p1_step = 'voting_pick'; game.proposing_party = game.ruling_party
                st.rerun()
                
            if active_role == 'R' and game.p1_step == 'draft_r':
                if c_btn2.button(t("💥 發布最後通牒", "💥 Issue Ultimatum"), use_container_width=True):
                    game.p1_selected_plan = plan_dict
                    game.p1_step = 'ultimatum_resolve_h'
                    game.proposing_party = game.h_role_party
                    st.session_state.news_flash = t(f"🗞️ **【快訊】監管系統下達最後通牒！** {view_party.name} 逼迫執行系統必須接受此案，否則將引發倒閣！", f"🗞️ **[BREAKING] R-System Ultimatum!** {view_party.name} forces H-System to accept or trigger swap!")
                    st.rerun()
                
                swap_cost = 0 if view_party.name == game.ruling_party.name else penalty_amt
                if c_btn3.button(t(f"🔄 強制通過並換位 (費用: {swap_cost})", f"🔄 Force Pass & Swap (Cost: {swap_cost})"), use_container_width=True):
                    st.session_state.turn_data.update(plan_dict)
                    engine.trigger_swap(game, swap_cost, t("監管系統強制接管！", "R-System Forced Takeover!"))
                    game.proposing_party = game.ruling_party; st.rerun()

            st.markdown("---")
            ui_core.render_proposal_component(t('📜 當前草案預覽', '📜 Current Draft Preview'), plan_dict, game, view_party, cfg)

            if opp_plan:
                st.markdown("---")
                ui_core.render_proposal_component(t('📜 對手 (執行系統) 既有草案參考', '📜 Opponent Draft Ref.'), opp_plan, game, view_party, cfg)

    elif game.p1_step == 'voting_pick':
        st.markdown(t(f"### 🗳️ 執政黨定奪 ({game.ruling_party.name})", f"### 🗳️ Ruling Party Decision ({game.ruling_party.name})"))
        if view_party.name != game.ruling_party.name:
            st.warning(t("⏳ 等待執政黨定奪...", "⏳ Waiting for ruling party..."))
        else:
            for idx, key in enumerate(['R', 'H']):
                plan = game.p1_proposals.get(key)
                if plan is None: st.info(t("等待對方發布草案...", "Waiting for opponent draft...")); continue
                st.markdown("---")
                ui_core.render_proposal_component(t('⚖️ 監管系統草案', '⚖️ R-System Draft') if key=='R' else t('🛡️ 執行系統草案', '🛡️ H-System Draft'), plan, game, view_party, cfg)
                if st.button(t(f"✅ 選擇此方案", f"✅ Select this draft"), key=f"pick_{key}"):
                    game.p1_selected_plan = plan; game.p1_step = 'voting_confirm'
                    game.proposing_party = game.party_B if game.ruling_party.name == game.party_A.name else game.party_A; st.rerun()

    elif game.p1_step == 'voting_confirm':
        if view_party.name != game.proposing_party.name: st.warning(t("⏳ 等待對手覆議...", "⏳ Waiting for opponent confirmation..."))
        else:
            ui_core.render_proposal_component(t('📜 待覆議草案內容', '📜 Draft to Confirm'), game.p1_selected_plan, game, view_party, cfg)
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            if c1.button(t("✅ 同意法案", "✅ Agree to Bill"), use_container_width=True, type="primary"):
                st.session_state.turn_data.update(game.p1_selected_plan)
                st.session_state.news_flash = t(f"🗞️ **【快訊】預算案三讀通過！** 歷經 {game.proposal_count} 輪黨團協商，雙方正式簽署法案。", f"🗞️ **[BREAKING] Bill Passed!** After {game.proposal_count} rounds, bill is signed.")
                st.session_state.anim = 'balloons'
                game.phase = 2; game.proposing_party = game.ruling_party; st.rerun()
            
            if c2.button(t("❌ 拒絕並重談", "❌ Reject & Renegotiate"), use_container_width=True):
                game.proposal_count += 1; game.p1_step = 'draft_r'; game.proposing_party = game.r_role_party; st.rerun()
            
            if c3.button(t(f"🔄 同意但換位\n(各付 {penalty_amt})", f"🔄 Agree & Swap\n(Cost: {penalty_amt})"), use_container_width=True):
                st.session_state.turn_data.update(game.p1_selected_plan)
                engine.trigger_swap(game, penalty_amt, t("執政權轉移！", "Power Shift!"))
                game.proposing_party = game.ruling_party; st.rerun()
            
            if game.proposing_party.name == game.h_role_party.name:
                if c4.button(t("💥 逼迫最終提案 (通牒)", "💥 Force Final (Ultimatum)"), use_container_width=True):
                    st.session_state.news_flash = t(f"🗞️ **【快訊】執行系統下達最後通牒！** {view_party.name} 逼迫監管系統只能再提最後一次案！", f"🗞️ **[BREAKING] H-System Ultimatum!** R-System has one last chance.")
                    game.p1_step = 'ultimatum_draft_r'; game.proposing_party = game.r_role_party; st.rerun()

    elif game.p1_step == 'ultimatum_resolve_h':
        st.markdown(t("### 🚨 最終方案決斷 (執行系統專屬)", "### 🚨 Final Decision (H-System Only)"))
        if view_party.name != game.h_role_party.name: 
            st.warning(t(f"⏳ 等待執行系統 {game.h_role_party.name} 決斷...", f"⏳ Waiting for H-System {game.h_role_party.name}..."))
        else:
            ui_core.render_proposal_component(t('📜 監管系統最終底線/通牒方案', '📜 R-System Final Ultimatum Draft'), game.p1_selected_plan, game, view_party, cfg)
            st.markdown("---")
            c1, c2 = st.columns(2)
            if c1.button(t("✅ 忍辱負重 (接受通牒)", "✅ Accept Ultimatum"), use_container_width=True, type="primary"):
                st.session_state.turn_data.update(game.p1_selected_plan)
                st.session_state.news_flash = t(f"🗞️ **【快訊】通牒生效！** 執行系統妥協吞下底線方案。", f"🗞️ **[BREAKING] Ultimatum Accepted!** H-System compromises.")
                st.session_state.anim = 'balloons'
                game.phase = 2; game.proposing_party = game.ruling_party; st.rerun()
            if c2.button(t(f"🔄 掀桌倒閣換位\n(警告: 各付 {penalty_amt})", f"🔄 Flip Table & Swap\n(Warning: Cost {penalty_amt})"), use_container_width=True):
                st.session_state.turn_data.update(game.p1_selected_plan)
                engine.trigger_swap(game, penalty_amt, t("掀桌倒閣！", "Cabinet Fall!"))
                game.proposing_party = game.r_role_party; st.rerun()
