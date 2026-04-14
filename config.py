# ==========================================
# config.py
# ==========================================
import i18n
t = i18n.t

DEFAULT_CONFIG = {
    'CALENDAR_NAME': "星曆", 'PARTY_A_COLOR': "#2E8B57", 'PARTY_B_COLOR': "#4169E1",
    'PARTY_A_NAME': "Prosperity", 'PARTY_B_NAME': "Equity", 
    'CROWN_WINNER': "👑 當權", 'CROWN_LOSER': "🎯 候選",
    'INITIAL_WEALTH': 1000.0, 'END_YEAR': 12,
    
    # [修改] 衰退率回歸 0~1.0，並新增權重參數
    'DECAY_MIN': 0.0, 'DECAY_MAX': 1.0,  
    'DECAY_WEIGHT_MULT': 0.05,  # 權重(5%)
    'BASE_DECAY_RATE': 0.0,     # 最低衰退參數(0)
    
    # [新增] 貪污擲骰基礎機率
    'CATCH_RATE_PER_PERCENT': 0.02,       # 秘密貪污每 1% 的被抓機率 (2%)
    'CRONY_CATCH_RATE_PER_PERCENT': 0.01, # 圖利自身每 1% 的被抓機率 (1%)
    
    'RESISTANCE_MULT': 1.0, 
    'BUILD_DIFF': 1.0, 'INVESTIGATE_DIFF': 1.0, 'PREDICT_DIFF': 1.0, 'MEDIA_DIFF': 1.0,
    'CURRENT_GDP': 5000.0, 
    'GDP_INFLATION_DIVISOR': 10000.0, 
    'GDP_CONVERSION_RATE': 0.2,   
    'HEALTH_MULTIPLIER': 0.2, 
    'BASE_TOTAL_BUDGET': 0.0,  
    'BASE_INCOME_RATIO': 0.05,    
    'RULING_BONUS_RATIO': 0.10,   
    'H_FUND_DEFAULT': 600.0, 
    'H_MEDIA_BONUS': 1.2, 'R_INV_BONUS': 1.2,
    'CORRUPTION_PENALTY': 2.0,
    'MAX_ABILITY': 10.0, 
    'ABILITY_DEFAULT': 3.0,          
    'BUILD_ABILITY_DEFAULT': 6.0,    
    'MAINTENANCE_RATE': 10.0,        
    'TRUST_BREAK_PENALTY_RATIO': 0.05,
    'ELECTION_CYCLE': 4,
    'SANITY_DEFAULT': 50.0,   
    'EMOTION_DEFAULT': 30.0,
    'SUPPORT_CONVERSION_RATE': 0.05, 
    'PERF_IMPACT_BASE': 1000.0,
    'OBS_ERR_BASE': 0.7,      
    'CLAIMED_DECAY_WEIGHT': 0.2  
}

def get_config_translations():
    return {
        'DECAY_MIN': "最小衰退率 (0~1)", 'DECAY_MAX': "最大衰退率 (0~1)",  
        'DECAY_WEIGHT_MULT': "衰退率GDP權重 (預設0.05)", 'BASE_DECAY_RATE': "最低衰退下限",
        'CATCH_RATE_PER_PERCENT': "貪污每%基礎被抓率", 'CRONY_CATCH_RATE_PER_PERCENT': "圖利每%基礎被抓率",
        # ...其餘省略以維持簡潔...
    }
    
def get_intel_market_eval(unit_cost):
    if unit_cost < 0.8: return "🌟 市場極度低估 (產能過剩，進入建設絕對紅利期)"
    elif unit_cost < 1.2: return "🟢 市場報價平穩 (供需均衡，營建成本符合預期)"
    elif unit_cost < 1.8: return "🟡 通膨溢價浮現 (原物料與勞動力緊繃，成本開始攀升)"
    elif unit_cost < 2.5: return "🔴 市場過熱警報 (系統性阻力高，預算消耗劇烈)"
    else: return "💀 經濟結構惡化 (成本呈現毀滅性通膨，建議暫緩非必要開發)"

# [修改] 配合 0~90% 的跌幅重新調整門檻
def get_economic_forecast_text(drop_val):
    if drop_val <= 10.0: return "🌟 景氣極佳 (跌幅微小)"
    elif drop_val <= 30.0: return "📈 穩定成長 (跌幅可控)"
    elif drop_val <= 50.0: return "⚖️ 持平放緩 (面臨衰退)"
    elif drop_val <= 70.0: return "📉 衰退警報 (百業蕭條)"
    else: return "⚠️ 經濟風暴 (系統性崩潰)"

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
    if name == "Prosperity": return "🦅"
    elif name == "Equity": return "🤝"
    return "🚩"

def get_thinktank_eval(ability, diff):
    abi_lvl = "high" if ability >= 7 else "med" if ability >= 4 else "low"
    acc_lvl = "high" if diff <= 5.0 else "med" if diff <= 15.0 else "low"  # [修改] 容錯率隨 0-90 尺度放大
    matrix = {
        ('high', 'high'): "頂尖發揮，完美預判", ('high', 'med'): "微幅誤差，戰略可控", ('high', 'low'): "黑天鵝事件！未能看透劇變",
        ('med', 'high'): "表現超常，精準命中", ('med', 'med'): "中規中矩，誤差預期內", ('med', 'low'): "嚴重誤判，建議升級",
        ('low', 'high'): "瞎貓碰死耗子，幸運猜中", ('low', 'med'): "表現尚可，參考價值低", ('low', 'low'): "完全失能，嚴重誤導決策！"
    }
    return matrix.get((abi_lvl, acc_lvl), "運作異常")
