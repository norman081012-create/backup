# ==========================================
# config.py
# 負責管理遊戲全域設定與判讀邏輯
# ==========================================
import i18n
t = i18n.t

DEFAULT_CONFIG = {
    'CALENDAR_NAME': "星曆", 'PARTY_A_COLOR': "#2E8B57", 'PARTY_B_COLOR': "#4169E1",
    'PARTY_A_NAME': "Prosperity", 'PARTY_B_NAME': "Equity", 
    'INITIAL_WEALTH': 1000.0, 'END_YEAR': 12,
    'DECAY_MIN': 0.2, 'DECAY_MAX': 1.2,  
    'RESISTANCE_MULT': 1.0, 
    'BUILD_DIFF': 1.0, 'INVESTIGATE_DIFF': 1.0, 'PREDICT_DIFF': 1.0, 'MEDIA_DIFF': 1.0,
    'CURRENT_GDP': 5000.0, 
    'HEALTH_MULTIPLIER': 0.2, 
    'BASE_TOTAL_BUDGET': 0.0,  
    'RULING_BONUS': 50.0, 'DEFAULT_BONUS': 100.0, 
    'H_FUND_DEFAULT': 600.0, 
    'H_MEDIA_BONUS': 1.2, 'R_INV_BONUS': 1.2,
    'CORRUPTION_PENALTY': 2.0,
    'MAX_ABILITY': 10.0, 
    'ABILITY_DEFAULT': 3.0,          
    'BUILD_ABILITY_DEFAULT': 6.0,    
    'MAINTENANCE_RATE': 10.0,        
    'TRUST_BREAK_PENALTY_RATIO': 0.05,
    'ELECTION_CYCLE': 4,
    'SANITY_DEFAULT': 60.0, 
    'EMOTION_DEFAULT': 30.0,
    'SUPPORT_CONVERSION_RATE': 0.05, 
    'PERF_IMPACT_BASE': 1000.0,
    'OBS_ERR_BASE': 0.4  # 觀測誤差基數更新為 0.4
}

def get_economic_forecast_text(decay_val):
    if decay_val <= 0.35: return "🌟 景氣極佳"
    elif decay_val <= 0.65: return "📈 穩定成長"
    elif decay_val <= 0.95: return "⚖️ 持平放緩"
    elif decay_val <= 1.15: return "📉 衰退警報"
    else: return "⚠️ 經濟風暴"

def get_civic_index_text(score):
    if score < 15: return f"易受灌輸 ({score:.1f})"
    elif score < 30: return f"較易受灌輸 ({score:.1f})"
    elif score < 45: return f"略受灌輸 ({score:.1f})"
    elif score < 60: return f"理性中等 ({score:.1f})"
    elif score < 75: return f"略具思辨 ({score:.1f})"
    elif score < 90: return f"思辨成熟 ({score:.1f})"
    else: return f"高度獨立思考 ({score:.1f})"

def get_emotion_text(emotion_val):
    if emotion_val < 20: return f"平穩冷靜 ({emotion_val:.1f})"
    elif emotion_val < 50: return f"些微躁動 ({emotion_val:.1f})"
    elif emotion_val < 80: return f"群情激憤 ({emotion_val:.1f})"
    else: return f"陷入狂熱 ({emotion_val:.1f})"

def get_election_icon(year, cycle):
    rem = year % cycle
    if rem == 1: return "🗳️ 大選年"
    elif rem == 2: return "🌱 施政元年"
    elif rem == cycle - 1: return "⏳ 距選舉 2 年"
    elif rem == 0: return "🚨 明年選舉"
    else: return f"距大選 {cycle - rem + 1} 年"

def get_party_logo(name):
    return "🦅" if name == "Prosperity" else "🤝"
