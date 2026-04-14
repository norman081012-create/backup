# ==========================================
# i18n.py
# 負責全系統的多語系文字切換字典
# ==========================================
import streamlit as st

def t(zh_text, en_text=None):
    lang = st.session_state.get('lang', 'ZH')
    if lang == 'ZH':
        return zh_text
    return en_text if en_text else zh_text
