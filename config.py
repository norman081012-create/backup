# ==========================================
# config.py
# ==========================================
import i18n
t = i18n.t

DEFAULT_CONFIG = {
    'CALENDAR_NAME': "星曆", 'PARTY_A_COLOR': "#2E8B57", 'PARTY_B_COLOR': "#4169E1",
    'PARTY_A_NAME': "繁榮黨", 'PARTY_B_NAME': "平權黨", 
    'CROWN_WINNER': "👑 當權", 'CROWN_LOSER': "🎯 候選",
    'INITIAL_WEALTH': 500.0, 'END_YEAR': 12,  # 初始資金下修為 500
    
    'DECAY_MIN': 0.1, 'DECAY_MAX': 0.7,  
    'DECAY_WEIGHT_MULT': 0.05,
    'BASE_DECAY_RATE': 0.0,
    
    'DECAY_AMOUNT_DEFAULT': 1500.0,
    'DECAY_AMOUNT_BUILD': 500.0,
    
    # Fake EV Audit Parameters
    'FAKE_EV_CATCH_BASE_RATE': 0.20,      # 基礎抓包率調升至 20%
    'FAKE_EV_COST_RATIO': 0.20,            
    'CORRUPTION_FINE_MULT': 0.4,          
    'CATCH_RATE_PER_PERCENT': 0.02,
    
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
    'MAX_ABILITY': 10.0, 
    'ABILITY_DEFAULT': 3.0,          
    'BUILD_ABILITY_DEFAULT': 3.0, 
    'EDU_ABILITY_DEFAULT': 3.0,
    'MAINTENANCE_RATE': 10.0,        
    'TRUST_BREAK_PENALTY_RATIO': 0.05,
    'ELECTION_CYCLE': 4,
    'SANITY_DEFAULT': 50.0,   
    'EMOTION_DEFAULT': 30.0,
    
    'CLAIMED_DECAY_WEIGHT': 0.2,
    'AMMO_MULTIPLIER': 50.0,
    
    'MAX_UPGRADE_SPEED': 20.0,
    'UPGRADE_COST_MULT': 0.15,      
    'PR_EFFICIENCY_MULT': 3.0,      
    
    'PREDICT_ACCURACY_WEIGHT': 0.8,     
    'INVESTIGATE_ACCURACY_WEIGHT': 0.8, 
    
    'PERF_IMPACT_BASE': 1000.0,
    'OBS_ERR_BASE': 0.7,      
}

def get_config_translations():
    return {
        'DECAY_MIN': "最小衰退率", 'DECAY_MAX': "最大衰退率",  
        'FAKE_EV_CATCH_BASE_RATE': "假 EV 基礎抓包率",
        'DECAY_WEIGHT_MULT': "衰退率轉換 GDP 權重 (預設 0.05)", 'BASE_DECAY_RATE': "基礎衰退下限",
        'CLAIMED_DECAY_WEIGHT': "預期落差權重", 'AMMO_MULTIPLIER': "政績轉換支持度倍率",
        'PREDICT_ACCURACY_WEIGHT': "智庫預測準確度權重", 'INVESTIGATE_ACCURACY_WEIGHT': "情報調查準確度權重",
        'UPGRADE_COST_MULT': "升級成本基數", 'PR_EFFICIENCY_MULT': "公關效率倍率"
    }

def get_intel_market_eval(unit_cost):
    if unit_cost < 0.8: return "🌟 極度低估"
    elif unit_cost < 1.2: return "🟢 市場穩定"
    elif unit_cost < 1.8: return "🟡 通膨溢價"
    elif unit_cost < 2.5: return "🔴 過熱警告"
    else: return "💀 經濟惡化"

def get_economic_forecast_text(drop_val):
    if drop_val <= 10.0: return "🌟 經濟繁榮"
    elif drop_val <= 30.0: return "📈 穩定成長"
    elif drop_val <= 50.0: return "⚖️ 經濟放緩"
    elif drop_val <= 70.0: return "📉 衰退警告"
    else: return "⚠️ 經濟風暴"

def get_civic_index_text(score):
    if score < 15: return f"極易被洗腦 ({score:.1f})"
    elif score < 30: return f"高度易受影響 ({score:.1f})"
    elif score < 45: return f"輕度易受影響 ({score:.1f})"
    elif score < 60: return f"具備中度理性 ({score:.1f})"
    elif score < 75: return f"具備輕度批判力 ({score:.1f})"
    elif score < 90: return f"成熟的批判思考 ({score:.1f})"
    else: return f"高度獨立自主 ({score:.1f})"

def get_emotion_text(emotion_val):
    if emotion_val < 20: return f"冷靜穩定 ({emotion_val:.1f})"
    elif emotion_val < 50: return f"略顯浮躁 ({emotion_val:.1f})"
    elif emotion_val < 80: return f"群情激憤 ({emotion_val:.1f})"
    else: return f"極度狂熱 ({emotion_val:.1f})"

def get_election_icon(year, cycle):
    rem = year % cycle
    if rem == 1: return "🗳️ 選舉年"
    elif rem == 2: return "🌱 任期第一年"
    elif rem == cycle - 1: return "⏳ 距大選 2 年"
    elif rem == 0: return "🚨 明年大選"
    else: return f"距大選 {cycle - rem + 1} 年"

def get_party_logo(name):
    if name == "繁榮黨": return "🦅"
    elif name == "平權黨": return "🤝"
    return "🚩"

def get_thinktank_eval(ability, diff):
    abi_lvl = "high" if ability >= 7 else "med" if ability >= 4 else "low"
    acc_lvl = "high" if diff <= 5.0 else "med" if diff <= 15.0 else "low" 
    matrix = {
        ('high', 'high'): "頂級表現", ('high', 'med'): "微小誤差", ('high', 'low'): "黑天鵝事件",
        ('med', 'high'): "超乎水準", ('med', 'med'): "標準表現", ('med', 'low'): "嚴重誤判",
        ('low', 'high'): "盲目運氣", ('low', 'med'): "尚可接受", ('low', 'low'): "系統完全失能"
    }
    return matrix.get((abi_lvl, acc_lvl), "系統故障")
