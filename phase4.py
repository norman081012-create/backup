# ==========================================
# phase4.py
# 負責 遊戲結束與總結算圖表
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
    st.title(t("🏁 遊戲結束！共生內閣軌跡總結算"))
    
    df = pd.DataFrame(game.history)
    
    # 確保資料格式相容 (防止舊存檔缺少欄位報錯)
    if 'Ruling' in df.columns:
        st.subheader("📊 1. 政權輪替與系統分工狀態")
        st.write("精準檢視兩黨是否有「一黨獨大」或「長期拒絕輪替分工」的僵化現象。")
        c1, c2 = st.columns(2)
        with c1:
            rule_counts = df['Ruling'].value_counts().reset_index()
            rule_counts.columns = ['Party', 'Years']
            fig_ruling = px.pie(rule_counts, names='Party', values='Years', title="歷屆執政黨年份佔比", hole=0.3, color='Party', color_discrete_map={cfg['PARTY_A_NAME']: cfg['PARTY_A_COLOR'], cfg['PARTY_B_NAME']: cfg['PARTY_B_COLOR']})
            st.plotly_chart(fig_ruling, use_container_width=True)
        with c2:
            h_counts = df['H_Party'].value_counts().reset_index()
            h_counts.columns = ['Party', 'Years']
            fig_h = px.pie(h_counts, names='Party', values='Years', title="擔任執行系統(H)年份佔比", hole=0.3, color='Party', color_discrete_map={cfg['PARTY_A_NAME']: cfg['PARTY_A_COLOR'], cfg['PARTY_B_NAME']: cfg['PARTY_B_COLOR']})
            st.plotly_chart(fig_h, use_container_width=True)

    st.subheader("📈 2. 總體經濟與社會理智發展")
    st.write("檢視政黨互動是否將國家推向繁榮與思辨，或是陷入經濟停滯與情緒極化。")
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(x=df['Year'], y=df['GDP'], name="總 GDP", line=dict(color='blue', width=3)), secondary_y=False)
    fig1.add_trace(go.Scatter(x=df['Year'], y=df['Sanity'], name="資訊辨識 (0-100)", line=dict(color='purple', width=3)), secondary_y=True)
    
    for _, row in df.iterrows():
        y = row['Year']
        if row['Is_Swap']: fig1.add_vline(x=y, line_dash="dot", line_color="red", annotation_text="倒閣!", annotation_position="top left")
        if row['Is_Election']: fig1.add_vline(x=y, line_dash="dash", line_color="green", annotation_text="選舉", annotation_position="bottom right")

    st.plotly_chart(fig1, use_container_width=True)
    
    if 'A_Edu' in df.columns:
        st.subheader("🏛️ 3. 政策路線與部門效率演進")
        st.write("檢視兩黨在教育方針上的偏好 (填鴨 vs 思辨) 以及內部機構能力的平均升級曲線。")
        c3, c4 = st.columns(2)
        with c3:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=df['Year'], y=df['A_Edu'], name=f"{cfg['PARTY_A_NAME']} 黨 教育投資", marker_color=cfg['PARTY_A_COLOR']))
            fig2.add_trace(go.Bar(x=df['Year'], y=df['B_Edu'], name=f"{cfg['PARTY_B_NAME']} 黨 教育投資", marker_color=cfg['PARTY_B_COLOR']))
            fig2.update_layout(title="歷年教育方針路線 (負值:填鴨 / 正值:思辨)", barmode='group')
            st.plotly_chart(fig2, use_container_width=True)
        with c4:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=df['Year'], y=df['A_Avg_Abi'], name=f"{cfg['PARTY_A_NAME']} 部門平均能力", line=dict(color=cfg['PARTY_A_COLOR'], width=3)))
            fig3.add_trace(go.Scatter(x=df['Year'], y=df['B_Avg_Abi'], name=f"{cfg['PARTY_B_NAME']} 部門平均能力", line=dict(color=cfg['PARTY_B_COLOR'], width=3)))
            fig3.update_layout(title="內部機關綜合能力演進")
            st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    if st.button(t("🔄 重新開始全新遊戲", "🔄 Restart Game"), use_container_width=True, type="primary"): 
        st.session_state.clear()
        st.rerun()
