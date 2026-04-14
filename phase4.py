# ==========================================
# phase4.py
# 負責 遊戲結束與總結算圖表
# ==========================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import i18n
t = i18n.t

def render(game, cfg):
    st.balloons()
    st.title(t("🏁 遊戲結束！共生內閣軌跡總結算"))
    
    df = pd.DataFrame(game.history)
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(x=df['Year'], y=df['GDP'], name="總 GDP", line=dict(color='blue', width=3)), secondary_y=False)
    fig1.add_trace(go.Scatter(x=df['Year'], y=df['Sanity'], name="資訊辨識 (0-100)", line=dict(color='purple', width=3)), secondary_y=True)
    
    for _, row in df.iterrows():
        y = row['Year']
        if row['Is_Swap']: fig1.add_vline(x=y, line_dash="dot", line_color="red", annotation_text="倒閣!", annotation_position="top left")
        if row['Is_Election']: fig1.add_vline(x=y, line_dash="dash", line_color="green", annotation_text="選舉", annotation_position="bottom right")

    st.plotly_chart(fig1, use_container_width=True)
    
    if st.button(t("🔄 重新開始全新遊戲", "🔄 Restart Game"), use_container_width=True, type="primary"): 
        st.session_state.clear()
        st.rerun()
