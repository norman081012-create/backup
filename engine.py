# ==========================================
# engine.py
# 負責遊戲引擎、政黨類別與全域事件觸發邏輯
# ==========================================
import random
import streamlit as st
import i18n
t = i18n.t

class Party:
    def __eq__(self, other): return self.name == other.name if hasattr(other, 'name') else False
    def __init__(self, name, cfg):
        self.name = name; self.wealth = cfg['INITIAL_WEALTH']; self.support = 50.0 
        
        self.build_ability = cfg.get('BUILD_ABILITY_DEFAULT', 6.0)
        self.investigate_ability = cfg.get('ABILITY_DEFAULT', 3.0)
        self.media_ability = cfg.get('ABILITY_DEFAULT', 3.0)
        self.predict_ability = cfg.get('ABILITY_DEFAULT', 3.0)
        self.stealth_ability = cfg.get('ABILITY_DEFAULT', 3.0)
        
        self.current_forecast = 0.0
        
        self.poll_history = {'小型': [], '中型': [], '大型': []}
        self.latest_poll = None
        self.poll_count = 0
        
        self.last_acts = {'media': 0, 'camp': 0, 'incite': 0, 'judicial': 0, 'edu_amt': 0, 'tot_action': 0, 'legal': 0, 'tot_maint': 0, 'corr': 0, 'crony': 0}

class GameEngine:
    def __init__(self, cfg):
        self.year = 1
        self.party_A = Party(cfg['PARTY_A_NAME'], cfg); self.party_B = Party(cfg['PARTY_B_NAME'], cfg)
        self.gdp = cfg['CURRENT_GDP']; self.total_budget = cfg['BASE_TOTAL_BUDGET'] + (self.gdp * cfg['HEALTH_MULTIPLIER'])
        self.h_fund = cfg['H_FUND_DEFAULT']
        self.phase = 1; self.p1_step = 'draft_r' 
        self.p1_proposals = {'R': None, 'H': None}; self.p1_selected_plan = None
        self.ruling_party = self.party_A; self.r_role_party = self.party_A; self.h_role_party = self.party_B  
        self.sanity = cfg['SANITY_DEFAULT']; self.emotion = cfg['EMOTION_DEFAULT']
        self.current_real_decay = 0.0; self.last_real_decay = 0.0
        self.proposal_count = 1; self.proposing_party = self.party_A
        self.history = []; self.swap_triggered_this_year = False
        self.last_year_report = None

    def record_history(self, is_election):
        self.history.append({
            'Year': self.year, 'GDP': self.gdp, 'Sanity': self.sanity, 'Emotion': self.emotion,
            'A_Support': self.party_A.support, 'B_Support': self.party_B.support,
            'A_Wealth': self.party_A.wealth, 'B_Wealth': self.party_B.wealth,
            'Is_Election': is_election, 'Is_Swap': self.swap_triggered_this_year,
            'Ruling': self.ruling_party.name,
            'H_Party': self.h_role_party.name,
            'R_Party': self.r_role_party.name,
            'A_Edu': float(self.party_A.last_acts.get('edu_amt', 0)),
            'B_Edu': float(self.party_B.last_acts.get('edu_amt', 0)),
            'A_Avg_Abi': (self.party_A.build_ability + self.party_A.investigate_ability + self.party_A.media_ability + self.party_A.predict_ability + self.party_A.stealth_ability)/5,
            'B_Avg_Abi': (self.party_B.build_ability + self.party_B
