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
            fig3.add_trace(go.Scatter(x=df['Year'], y=df['A_Avg_Abi'], name=f"{cfg['PARTY_A_NAME']} 平均部門能力", line=dict(color=cfg['PARTY_A_COLOR'], width=3)))
            fig3.add_trace(go.Scatter(x=df['Year'], y=df['B_Avg_Abi'], name=f"{cfg['PARTY_B_NAME']} 平均部門能力", line=dict(color=cfg['PARTY_B_COLOR'], width=3)))
            fig3.update_layout(title="制度能力的演進")
            st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    if st.button("🔄 重新開始新一局遊戲", use_container_width=True, type="primary"): 
        st.session_state.clear()
        st.rerun()
