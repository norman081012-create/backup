# ==========================================
# ui_proposal.py
# 負責 提案草案渲染 (政府公文風格)
# ==========================================
import streamlit as st
import formulas
import ui_core
import config
import i18n
t = i18n.t

def render_proposal_component(title, plan, game, view_party, cfg):
    st.markdown(f"### 📄 {title}")
    
    c_tog1, c_tog2 = st.columns(2)
    use_tt = c_tog1.toggle(t("切換至 智庫預估 試算 (預設為公告數值)"), False, key=f"tg_tt_{title}_{plan.get('author', 'sys')}")
    use_claimed = not use_tt
    simulate_swap = c_tog2.toggle(t("模擬如果發生倒閣換位"), False, key=f"sim_sw_{title}_{plan.get('author', 'sys')}")
    
    if simulate_swap:
        sim_h = game.r_role_party; sim_r = game.h_role_party
        sim_rule = game.party_B.name if game.ruling_party.name == game.party_A.name else game.party_A.name
    else:
        sim_h = game.h_role_party; sim_r = game.r_role_party
        sim_rule = game.ruling_party.name

    tt_decay = view_party.current_forecast
    obs = ui_core.get_observed_abilities(view_party, sim_h, game, cfg)
    tt_cost = round(formulas.calc_unit_cost(cfg, game.gdp, obs['build'], tt_decay), 2)
    
    cl_decay = plan.get('claimed_decay', tt_decay)
    cl_cost = plan.get('claimed_cost', tt_cost)

    eval_d = cl_decay if use_claimed else tt_decay
    eval_c = cl_cost if use_claimed else tt_cost

    res = formulas.calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], sim_h.build_ability, eval_d, override_unit_cost=eval_c, r_pays=plan['r_pays'], h_wealth=sim_h.wealth)
    
    c1, c2 = st.columns([1.1, 0.9])
    
    with c1:
        with st.container(border=True):
            st.markdown("#### 📁 [政府採購卷宗] 標案參數公告")
            conv = cfg.get('GDP_CONVERSION_RATE', 0.2)
            loss = (game.gdp * (cl_decay * 0.05)) / conv
            st.write(f"📉 **公告衰退率**: `{cl_decay:.3f}` *(建設損失: {loss:.1f})*")
            st.write(f"🏗️ **公告基準單價**: `{cl_cost:.2f}`")
            st.markdown("---")
            st.write(f"💰 **計畫獎勵金**: `{plan['proj_fund']:.1f}` | 📈 **計畫總效益**: `{plan['bid_cost']:.1f}`")
            
            # 出資比例條
            req = res['req_cost']
            r_p, h_p = plan['r_pays'], (req - plan['r_pays'])
            r_pct = (r_p / max(1, req)) * 100
            st.markdown(f"""
            <div style='display:flex; height:22px; border-radius:11px; overflow:hidden; margin:10px 0; border:1px solid #cbd5e1;'>
                <div style='width:{r_pct}%; background-color:#3b82f6; color:white; font-size:11px; display:flex; align-items:center; justify-content:center;'>監管 {r_p:.1f}</div>
                <div style='width:{100-r_pct}%; background-color:#10b981; color:white; font-size:11px; display:flex; align-items:center; justify-content:center;'>執行 {h_p:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
            
    with c2:
        with st.container(border=True):
            st.markdown("<div class='think-tank-report'>", unsafe_allow_html=True)
            st.markdown("#### 👁️ [機密] 智庫風險分析")
            my_is_h = (view_party.name == sim_h.name)
            
            h_inc = formulas.calc_economy(cfg, game.gdp, game.total_budget, plan['proj_fund'], plan['bid_cost'], sim_h.build_ability, tt_decay, override_unit_cost=tt_cost, r_pays=plan['r_pays'], h_wealth=sim_h.wealth)
            my_net = (plan['proj_fund'] + plan['r_pays'] - h_inc['act_fund']) if my_is_h else (h_inc['payout_r'] - plan['r_pays'])
            
            st.write(f"- **預估我方淨利**: `{'🟢' if my_net>0 else '🔴'} {my_net:.1f}`")
            st.write(f"- **GDP 衝擊預測**: `{game.gdp:.1f}` ➔ `{res['est_gdp']:.1f}`")
            
            st.markdown("---")
            # 風險判讀
            diff_d = cl_decay - tt_decay
            st.write(f"⚠️ **數據異常掃描**:")
            st.write(f"{'🟢' if abs(diff_d)<0.1 else '🔴'} 衰退偏離: `{diff_d:+.3f}`")
            st.write(f"{'🟢' if abs(cl_cost-tt_cost)<0.2 else '🔴'} 單價偏離: `{cl_cost-tt_cost:+.2f}`")
            st.markdown("</div>", unsafe_allow_html=True)
