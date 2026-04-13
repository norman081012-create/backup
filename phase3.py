# ==========================================
# phase3.py
# 負責 第三階段 (年度總結算報告與視覺化)
# ==========================================
import streamlit as st
import i18n
t = i18n.t

def render(game, cfg):
    st.header(t("⚖️ Phase 3: 年度結算報告", "⚖️ Phase 3: Annual Report"))
    rep = game.last_year_report
    if not rep:
        st.error(t("無法取得結算資料。", "No report data found."))
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(t("#### 💰 經濟與財政", "#### 💰 Economy & Finance"))
        st.write(t(f"GDP 變化: `{rep['old_gdp']:.0f} ➔ {game.gdp:.0f}`", f"GDP Shift: `{rep['old_gdp']:.0f} ➔ {game.gdp:.0f}`"))
        st.write(t(f"執行系統收益: `${rep['h_inc']:.0f}`", f"H-System Profit: `${rep['h_inc']:.0f}`"))
        st.write(t(f"監管系統收益: `${rep['r_inc']:.0f}`", f"R-System Profit: `${rep['r_inc']:.0f}`"))
        if rep.get('corr_caught'):
            st.error(t(f"🚨 貪污醜聞爆發！執行系統貪污被情報處查獲，沒收所有非法所得並重挫民意。", f"🚨 Corruption Scandal! Funds seized & support heavily damaged."))
        if rep.get('crony_caught'):
            st.error(t(f"🚨 圖利爭議！執行系統圖利親信遭舉發，強制沒收資金返還國庫與監管系統。", "🚨 Cronyism Caught! Funds seized & returned to R-System."))

    with c2:
        st.markdown(t("#### 🧠 社會與民意", "#### 🧠 Society & Opinion"))
        st.write(t(f"資訊辨識: `{rep['old_san']:.1f} ➔ {game.sanity:.1f}`", f"Civic Lit: `{rep['old_san']:.1f} ➔ {game.sanity:.1f}`"))
        st.write(t(f"選民情緒: `{rep['old_emo']:.1f} ➔ {game.emotion:.1f}`", f"Voter Emo: `{rep['old_emo']:.1f} ➔ {game.emotion:.1f}`"))
        st.write(t(f"施政滿意度位移 (執行/監管): `{rep['h_perf']:.1f}% / {rep['r_perf']:.1f}%`", f"Perf Shift (H / R): `{rep['h_perf']:.1f}% / {rep['r_perf']:.1f}%`"))

    st.markdown("---")
    if st.button(t("⏩ 確認報告並進入下一年", "⏩ Confirm & Next Year"), type="primary", use_container_width=True):
        game.year += 1
        game.phase = 1
        game.p1_step = 'draft_r'
        game.p1_proposals = {'R': None, 'H': None}
        game.p1_selected_plan = None
        for k in list(st.session_state.keys()):
            if k.endswith('_acts'): del st.session_state[k]
        if 'turn_initialized' in st.session_state: del st.session_state.turn_initialized
        st.rerun()
