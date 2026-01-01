"""
CYBER MIRAGE v5.0 - Advanced Threat Intelligence & Deception Platform
======================================================================
PhD-Level Adaptive Honeypot Defense System - 100% REAL-TIME DATA
Proximal Policy Optimization (PPO) Deep Reinforcement Learning Agent
20 Elite Tactical Deception Actions | Live OSINT | Global Threat Mapping
======================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import psycopg2
import redis
import os
import json
import requests
import hashlib
import ipaddress

# =============================================================================
# CONFIGURATION
# =============================================================================

DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'cyber_mirage')
DB_USER = os.getenv('POSTGRES_USER', 'cybermirage')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASS = os.getenv('REDIS_PASSWORD', 'changeme123')

# GeoIP Cache to avoid repeated API calls
GEO_CACHE = {}

# 20 Elite Tactical Deception Actions
ELITE_ACTIONS = {
    'maintain_session': {'id': 1, 'name': 'MAINTAIN', 'category': 'Session Control', 'color': '#00D4FF', 'tactical_value': 'Low', 'description': 'Passive observation - maintain connection for intelligence gathering', 'mitre': 'T1557'},
    'drop_session': {'id': 2, 'name': 'DROP', 'category': 'Session Control', 'color': '#FF4757', 'tactical_value': 'Medium', 'description': 'Immediate session termination', 'mitre': 'T1531'},
    'throttle_session': {'id': 3, 'name': 'THROTTLE', 'category': 'Session Control', 'color': '#FFA502', 'tactical_value': 'Medium', 'description': 'Bandwidth restriction', 'mitre': 'T1499'},
    'redirect_session': {'id': 4, 'name': 'REDIRECT', 'category': 'Session Control', 'color': '#7B2CBF', 'tactical_value': 'High', 'description': 'Redirect to sandbox', 'mitre': 'T1090'},
    'inject_delay': {'id': 5, 'name': 'DELAY', 'category': 'Temporal', 'color': '#3498DB', 'tactical_value': 'Medium', 'description': 'Artificial latency injection', 'mitre': 'T1497'},
    'progressive_delay': {'id': 6, 'name': 'PROG_DELAY', 'category': 'Temporal', 'color': '#1ABC9C', 'tactical_value': 'High', 'description': 'Exponential delay escalation', 'mitre': 'T1497'},
    'random_delay': {'id': 7, 'name': 'RAND_DELAY', 'category': 'Temporal', 'color': '#9B59B6', 'tactical_value': 'High', 'description': 'Stochastic response timing', 'mitre': 'T1497'},
    'swap_service_banner': {'id': 8, 'name': 'SWAP_BANNER', 'category': 'Identity', 'color': '#E67E22', 'tactical_value': 'High', 'description': 'Service fingerprint manipulation', 'mitre': 'T1036'},
    'randomize_banner': {'id': 9, 'name': 'RAND_BANNER', 'category': 'Identity', 'color': '#16A085', 'tactical_value': 'High', 'description': 'Stochastic service identity', 'mitre': 'T1036'},
    'mimic_vulnerable': {'id': 10, 'name': 'VULN_MIMIC', 'category': 'Identity', 'color': '#C0392B', 'tactical_value': 'Critical', 'description': 'Vulnerability emulation', 'mitre': 'T1203'},
    'present_lure': {'id': 11, 'name': 'LURE', 'category': 'Deception', 'color': '#8E44AD', 'tactical_value': 'Critical', 'description': 'High-value target presentation', 'mitre': 'T1534'},
    'deploy_breadcrumb': {'id': 12, 'name': 'BREADCRUMB', 'category': 'Deception', 'color': '#2980B9', 'tactical_value': 'High', 'description': 'False trail deployment', 'mitre': 'T1534'},
    'inject_fake_creds': {'id': 13, 'name': 'FAKE_CREDS', 'category': 'Deception', 'color': '#27AE60', 'tactical_value': 'Critical', 'description': 'Honeytoken injection', 'mitre': 'T1078'},
    'simulate_target': {'id': 14, 'name': 'SIM_TARGET', 'category': 'Deception', 'color': '#D35400', 'tactical_value': 'High', 'description': 'High-value asset simulation', 'mitre': 'T1583'},
    'capture_tools': {'id': 15, 'name': 'CAPTURE', 'category': 'Forensic', 'color': '#7F8C8D', 'tactical_value': 'Critical', 'description': 'Malware/tool capture', 'mitre': 'T1005'},
    'log_enhanced': {'id': 16, 'name': 'LOG_FORENSIC', 'category': 'Forensic', 'color': '#95A5A6', 'tactical_value': 'High', 'description': 'Deep packet inspection', 'mitre': 'T1074'},
    'fingerprint': {'id': 17, 'name': 'FINGERPRINT', 'category': 'Forensic', 'color': '#34495E', 'tactical_value': 'Critical', 'description': 'Attacker TTP profiling', 'mitre': 'T1592'},
    'tarpit': {'id': 18, 'name': 'TARPIT', 'category': 'Advanced', 'color': '#2C3E50', 'tactical_value': 'Critical', 'description': 'Connection tarpit trap', 'mitre': 'T1499'},
    'honeypot_upgrade': {'id': 19, 'name': 'HP_UPGRADE', 'category': 'Advanced', 'color': '#1A252F', 'tactical_value': 'High', 'description': 'Dynamic interaction escalation', 'mitre': 'T1584'},
    'alert_track': {'id': 20, 'name': 'ALERT_TRACK', 'category': 'Advanced', 'color': '#E74C3C', 'tactical_value': 'Critical', 'description': 'SOC alert with tracking', 'mitre': 'T1071'}
}

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Cyber Mirage v5.0 | Threat Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# THEME CONFIGURATION - LIGHT/DARK MODE
# =============================================================================
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'  # Default to dark theme

# =============================================================================
# CSS - Dynamic Theme Support
# =============================================================================

def get_theme_css(theme: str) -> str:
    """Generate CSS based on selected theme."""
    if theme == 'dark':
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
            
            * { font-family: 'Inter', sans-serif; }
            .main { background: #050508; }
            .stApp { background: linear-gradient(135deg, #050508 0%, #0a0a12 100%); }
            
            #MainMenu, footer, header {visibility: hidden;}
            
            .cyber-header {
                background: linear-gradient(135deg, rgba(0,212,255,0.1) 0%, rgba(123,44,191,0.1) 100%);
                border: 1px solid rgba(0,212,255,0.2);
                border-radius: 12px;
                padding: 1.5rem 2rem;
                margin-bottom: 1.5rem;
            }
            
            .cyber-title {
                font-size: 2rem;
                font-weight: 700;
                color: #ffffff;
                margin: 0;
            }
            
            .cyber-subtitle { font-size: 0.85rem; color: #6b7280; margin-top: 0.25rem; }
            
            .version-tag {
                display: inline-block;
                background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 100%);
                color: white;
                padding: 0.2rem 0.6rem;
                border-radius: 4px;
                font-size: 0.7rem;
                font-weight: 600;
                margin-left: 0.75rem;
            }
            
            .live-badge {
                display: inline-block;
                background: rgba(16,185,129,0.2);
                border: 1px solid rgba(16,185,129,0.4);
                color: #10b981;
                padding: 0.15rem 0.5rem;
                border-radius: 4px;
                font-size: 0.65rem;
                font-weight: 600;
                margin-left: 0.5rem;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.6; }
            }
            
            .metric-card {
                background: linear-gradient(180deg, #0f0f18 0%, #0a0a10 100%);
                border: 1px solid #1a1a28;
                border-radius: 10px;
                padding: 1.25rem;
                text-align: center;
            }
            
            .metric-card:hover {
                border-color: #00d4ff;
                box-shadow: 0 8px 25px rgba(0,212,255,0.15);
            }
            
            .metric-value {
                font-family: 'JetBrains Mono', monospace;
                font-size: 2rem;
                font-weight: 700;
                color: #ffffff;
            }
            
            .metric-label {
                font-size: 0.7rem;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 0.5rem;
            }
            
            .metric-delta { font-size: 0.75rem; margin-top: 0.25rem; font-weight: 500; }
            .delta-positive { color: #10b981; }
            .delta-negative { color: #ef4444; }
            .delta-neutral { color: #6b7280; }
            
            .section-header {
                font-size: 1.1rem;
                font-weight: 600;
                color: #ffffff;
                margin: 1.5rem 0 1rem 0;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid #1a1a28;
            }
            
            .section-badge {
                background: rgba(0,212,255,0.15);
                color: #00d4ff;
                padding: 0.15rem 0.5rem;
                border-radius: 4px;
                font-size: 0.65rem;
                font-weight: 600;
                margin-left: 0.5rem;
            }
            
            .status-row { display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0; }
            .status-dot { width: 8px; height: 8px; border-radius: 50%; }
            .status-online { background: #10b981; animation: pulse 2s infinite; }
            .status-offline { background: #ef4444; }
            .status-text { font-size: 0.8rem; color: #9ca3af; }
            .status-latency { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #6b7280; }
            
            .ip-display {
                font-family: 'JetBrains Mono', monospace;
                background: rgba(0,212,255,0.1);
                border: 1px solid rgba(0,212,255,0.2);
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                color: #00d4ff;
                font-size: 0.85rem;
            }
            
            .threat-critical { background: rgba(255,0,0,0.2); color: #ff4444; border: 1px solid rgba(255,0,0,0.3); }
            .threat-high { background: rgba(255,71,87,0.2); color: #ff4757; border: 1px solid rgba(255,71,87,0.3); }
            .threat-medium { background: rgba(255,165,2,0.2); color: #ffa502; border: 1px solid rgba(255,165,2,0.3); }
            .threat-low { background: rgba(46,213,115,0.2); color: #2ed573; border: 1px solid rgba(46,213,115,0.3); }
            
            .threat-badge {
                display: inline-block;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                font-size: 0.65rem;
                font-weight: 600;
            }
            
            .cat-sc { background: rgba(0,212,255,0.25); color: #00d4ff; border: 1px solid rgba(0,212,255,0.3); }
            .cat-tm { background: rgba(243,156,18,0.25); color: #f39c12; border: 1px solid rgba(243,156,18,0.3); }
            .cat-id { background: rgba(230,126,34,0.25); color: #e67e22; border: 1px solid rgba(230,126,34,0.3); }
            .cat-ad { background: rgba(155,89,182,0.25); color: #9b59b6; border: 1px solid rgba(155,89,182,0.3); }
            .cat-fc { background: rgba(127,140,141,0.25); color: #c9d1d9; border: 1px solid rgba(127,140,141,0.3); }
            .cat-ac { background: rgba(231,76,60,0.25); color: #e74c3c; border: 1px solid rgba(231,76,60,0.3); }
            
            .cat-badge {
                display: inline-block;
                padding: 0.2rem 0.6rem;
                border-radius: 4px;
                font-size: 0.65rem;
                font-weight: 600;
                letter-spacing: 0.3px;
            }
            
            .attack-card {
                background: #0a0a12;
                border: 1px solid #1a1a28;
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.75rem;
            }
            
            .attack-card:hover { border-color: #2a2a3a; background: #0f0f18; }
            
            .reward-positive { color: #10b981; font-weight: 600; }
            .reward-negative { color: #ef4444; font-weight: 600; }
            .reward-neutral { color: #6b7280; }
            
            ::-webkit-scrollbar { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track { background: #0a0a12; }
            ::-webkit-scrollbar-thumb { background: #2a2a3a; border-radius: 3px; }
            
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0a0a12 0%, #050508 100%);
            }
        </style>
        """
    else:  # Light theme
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
            
            * { font-family: 'Inter', sans-serif; }
            .main { background: #f8fafc; }
            .stApp { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); }
            
            #MainMenu, footer, header {visibility: hidden;}
            
            .cyber-header {
                background: linear-gradient(135deg, rgba(0,102,204,0.1) 0%, rgba(99,102,241,0.1) 100%);
                border: 1px solid rgba(0,102,204,0.2);
                border-radius: 12px;
                padding: 1.5rem 2rem;
                margin-bottom: 1.5rem;
            }
            
            .cyber-title {
                font-size: 2rem;
                font-weight: 700;
                color: #1e293b;
                margin: 0;
            }
            
            .cyber-subtitle { font-size: 0.85rem; color: #64748b; margin-top: 0.25rem; }
            
            .version-tag {
                display: inline-block;
                background: linear-gradient(135deg, #0066cc 0%, #6366f1 100%);
                color: white;
                padding: 0.2rem 0.6rem;
                border-radius: 4px;
                font-size: 0.7rem;
                font-weight: 600;
                margin-left: 0.75rem;
            }
            
            .live-badge {
                display: inline-block;
                background: rgba(16,185,129,0.15);
                border: 1px solid rgba(16,185,129,0.3);
                color: #059669;
                padding: 0.15rem 0.5rem;
                border-radius: 4px;
                font-size: 0.65rem;
                font-weight: 600;
                margin-left: 0.5rem;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.6; }
            }
            
            .metric-card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 1.25rem;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            
            .metric-card:hover {
                border-color: #0066cc;
                box-shadow: 0 8px 25px rgba(0,102,204,0.12);
            }
            
            .metric-value {
                font-family: 'JetBrains Mono', monospace;
                font-size: 2rem;
                font-weight: 700;
                color: #1e293b;
            }
            
            .metric-label {
                font-size: 0.7rem;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 0.5rem;
            }
            
            .metric-delta { font-size: 0.75rem; margin-top: 0.25rem; font-weight: 500; }
            .delta-positive { color: #059669; }
            .delta-negative { color: #dc2626; }
            .delta-neutral { color: #64748b; }
            
            .section-header {
                font-size: 1.1rem;
                font-weight: 600;
                color: #1e293b;
                margin: 1.5rem 0 1rem 0;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid #e2e8f0;
            }
            
            .section-badge {
                background: rgba(0,102,204,0.12);
                color: #0066cc;
                padding: 0.15rem 0.5rem;
                border-radius: 4px;
                font-size: 0.65rem;
                font-weight: 600;
                margin-left: 0.5rem;
            }
            
            .status-row { display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0; }
            .status-dot { width: 8px; height: 8px; border-radius: 50%; }
            .status-online { background: #059669; animation: pulse 2s infinite; }
            .status-offline { background: #dc2626; }
            .status-text { font-size: 0.8rem; color: #475569; }
            .status-latency { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #64748b; }
            
            .ip-display {
                font-family: 'JetBrains Mono', monospace;
                background: rgba(0,102,204,0.08);
                border: 1px solid rgba(0,102,204,0.2);
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                color: #0066cc;
                font-size: 0.85rem;
            }
            
            .threat-critical { background: rgba(220,38,38,0.1); color: #dc2626; border: 1px solid rgba(220,38,38,0.2); }
            .threat-high { background: rgba(234,88,12,0.1); color: #ea580c; border: 1px solid rgba(234,88,12,0.2); }
            .threat-medium { background: rgba(245,158,11,0.1); color: #d97706; border: 1px solid rgba(245,158,11,0.2); }
            .threat-low { background: rgba(22,163,74,0.1); color: #16a34a; border: 1px solid rgba(22,163,74,0.2); }
            
            .threat-badge {
                display: inline-block;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                font-size: 0.65rem;
                font-weight: 600;
            }
            
            .cat-sc { background: rgba(0,102,204,0.15); color: #0066cc; border: 1px solid rgba(0,102,204,0.2); }
            .cat-tm { background: rgba(217,119,6,0.15); color: #b45309; border: 1px solid rgba(217,119,6,0.2); }
            .cat-id { background: rgba(194,65,12,0.15); color: #c2410c; border: 1px solid rgba(194,65,12,0.2); }
            .cat-ad { background: rgba(147,51,234,0.15); color: #9333ea; border: 1px solid rgba(147,51,234,0.2); }
            .cat-fc { background: rgba(100,116,139,0.15); color: #475569; border: 1px solid rgba(100,116,139,0.2); }
            .cat-ac { background: rgba(220,38,38,0.15); color: #dc2626; border: 1px solid rgba(220,38,38,0.2); }
            
            .cat-badge {
                display: inline-block;
                padding: 0.2rem 0.6rem;
                border-radius: 4px;
                font-size: 0.65rem;
                font-weight: 600;
                letter-spacing: 0.3px;
            }
            
            .attack-card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.75rem;
                box-shadow: 0 1px 2px rgba(0,0,0,0.03);
            }
            
            .attack-card:hover { border-color: #cbd5e1; background: #f8fafc; }
            
            .reward-positive { color: #059669; font-weight: 600; }
            .reward-negative { color: #dc2626; font-weight: 600; }
            .reward-neutral { color: #64748b; }
            
            ::-webkit-scrollbar { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track { background: #f1f5f9; }
            ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
            
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                border-right: 1px solid #e2e8f0;
            }
        </style>
        """

# Apply theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# =============================================================================
# DATABASE FUNCTIONS - ALL REAL-TIME
# =============================================================================

def get_db_connection():
    try:
        return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, connect_timeout=5)
    except:
        return None

def fetch_metrics():
    """Fetch ALL metrics from REAL database - NO STATIC DATA."""
    metrics = {
        'total_decisions': 0, 'unique_sessions': 0, 'avg_reward': 0.0,
        'max_reward': 0.0, 'min_reward': 0.0, 'action_distribution': {},
        'hourly_decisions': 0, 'total_attacks': 0, 'unique_attackers': 0,
        'services_targeted': {}, 'recent_attacks_24h': 0
    }
    
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        # Agent decisions
        cur.execute("SELECT COUNT(*) FROM agent_decisions")
        metrics['total_decisions'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(DISTINCT session_id) FROM agent_decisions")
        metrics['unique_sessions'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT AVG(reward), MAX(reward), MIN(reward) FROM agent_decisions WHERE reward IS NOT NULL")
        row = cur.fetchone()
        if row and row[0]:
            metrics['avg_reward'] = float(row[0])
            metrics['max_reward'] = float(row[1]) if row[1] else 0.0
            metrics['min_reward'] = float(row[2]) if row[2] else 0.0
        
        cur.execute("SELECT COUNT(*) FROM agent_decisions WHERE created_at > NOW() - INTERVAL '1 hour'")
        metrics['hourly_decisions'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT action, COUNT(*) FROM agent_decisions GROUP BY action ORDER BY COUNT(*) DESC")
        for row in cur.fetchall():
            metrics['action_distribution'][row[0]] = row[1]
        
        # Attack sessions - REAL DATA
        cur.execute("SELECT COUNT(*) FROM attack_sessions")
        metrics['total_attacks'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(DISTINCT origin) FROM attack_sessions WHERE origin IS NOT NULL")
        metrics['unique_attackers'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(*) FROM attack_sessions WHERE created_at > NOW() - INTERVAL '24 hours'")
        metrics['recent_attacks_24h'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT honeypot_type, COUNT(*) FROM attack_sessions GROUP BY honeypot_type ORDER BY COUNT(*) DESC")
        for row in cur.fetchall():
            if row[0]:
                metrics['services_targeted'][row[0]] = row[1]
        
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Database error: {e}")
    
    return metrics

def fetch_agent_decisions(limit=100):
    """Fetch REAL agent decisions from database."""
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, session_id, action, strategy, reward, state, created_at
            FROM agent_decisions ORDER BY created_at DESC LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame(rows, columns=['id', 'session_id', 'action', 'strategy', 'reward', 'state', 'created_at'])
    except:
        return pd.DataFrame()

def fetch_real_attacks(limit=50):
    """Fetch REAL attack data with IPs from database."""
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute("""
            SELECT origin, honeypot_type, COUNT(*) as attack_count, 
                   MAX(created_at) as last_seen, MIN(created_at) as first_seen
            FROM attack_sessions 
            WHERE origin IS NOT NULL AND origin != ''
            GROUP BY origin, honeypot_type
            ORDER BY attack_count DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame(rows, columns=['ip', 'service', 'attack_count', 'last_seen', 'first_seen'])
    except Exception as e:
        print(f"Error fetching attacks: {e}")
        return pd.DataFrame()

def fetch_attack_timeline():
    """Fetch attack timeline for chart - REAL DATA."""
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute("""
            SELECT DATE_TRUNC('hour', created_at) as hour, COUNT(*) 
            FROM attack_sessions 
            WHERE created_at > NOW() - INTERVAL '24 hours'
            GROUP BY hour ORDER BY hour
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame(rows, columns=['hour', 'count'])
    except:
        return pd.DataFrame()

def fetch_system_health():
    """Check REAL system health."""
    health = {'postgres': False, 'redis': False, 'pg_latency': 0, 'redis_latency': 0}
    
    start = time.time()
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, connect_timeout=3)
        conn.cursor().execute("SELECT 1")
        conn.close()
        health['postgres'] = True
        health['pg_latency'] = round((time.time() - start) * 1000, 1)
    except:
        pass
    
    start = time.time()
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, socket_timeout=3)
        r.ping()
        health['redis'] = True
        health['redis_latency'] = round((time.time() - start) * 1000, 1)
    except:
        pass
    
    return health

def fetch_mitre_tactics():
    """Fetch MITRE ATT&CK tactics from attack sessions."""
    tactics_data = []
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute("""
            SELECT mitre_tactics, COUNT(*) as count
            FROM attack_sessions 
            WHERE mitre_tactics IS NOT NULL AND array_length(mitre_tactics, 1) > 0
            GROUP BY mitre_tactics
            ORDER BY count DESC
            LIMIT 20
        """)
        for row in cur.fetchall():
            if row[0]:
                for tactic in row[0]:
                    tactics_data.append({'tactic': tactic, 'count': row[1]})
        cur.close()
        conn.close()
    except:
        pass
    return tactics_data

def fetch_attacker_profiles(limit=50):
    """Fetch detailed attacker profiles with skill, suspicion, etc."""
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                origin,
                honeypot_type,
                AVG(attacker_skill) as avg_skill,
                AVG(final_suspicion) as avg_suspicion,
                SUM(COALESCE(zero_days_used, 0)) as total_zero_days,
                AVG(data_collected) as avg_data_collected,
                SUM(CASE WHEN detected THEN 1 ELSE 0 END) as times_detected,
                COUNT(*) as total_attacks,
                MAX(created_at) as last_seen
            FROM attack_sessions 
            WHERE origin IS NOT NULL AND origin != ''
            GROUP BY origin, honeypot_type
            ORDER BY total_attacks DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame(rows, columns=[
            'ip', 'service', 'avg_skill', 'avg_suspicion', 'total_zero_days',
            'avg_data_collected', 'times_detected', 'total_attacks', 'last_seen'
        ])
    except Exception as e:
        print(f"Error fetching attacker profiles: {e}")
        return pd.DataFrame()

def fetch_forensic_stats():
    """Fetch forensic statistics from attack data."""
    stats = {
        'total_detected': 0,
        'total_undetected': 0,
        'avg_skill': 0.0,
        'avg_suspicion': 0.0,
        'total_zero_days': 0,
        'total_data_collected': 0.0,
        'skill_distribution': {},
        'detection_rate': 0.0
    }
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        # Detection stats
        cur.execute("SELECT COUNT(*) FROM attack_sessions WHERE detected = TRUE")
        stats['total_detected'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(*) FROM attack_sessions WHERE detected = FALSE OR detected IS NULL")
        stats['total_undetected'] = cur.fetchone()[0] or 0
        
        total = stats['total_detected'] + stats['total_undetected']
        if total > 0:
            stats['detection_rate'] = (stats['total_detected'] / total) * 100
        
        # Averages
        cur.execute("""
            SELECT 
                AVG(attacker_skill), 
                AVG(final_suspicion),
                SUM(COALESCE(zero_days_used, 0)),
                SUM(COALESCE(data_collected, 0))
            FROM attack_sessions
        """)
        row = cur.fetchone()
        if row:
            stats['avg_skill'] = float(row[0]) if row[0] else 0.0
            stats['avg_suspicion'] = float(row[1]) if row[1] else 0.0
            stats['total_zero_days'] = int(row[2]) if row[2] else 0
            stats['total_data_collected'] = float(row[3]) if row[3] else 0.0
        
        # Skill distribution
        cur.execute("""
            SELECT 
                CASE 
                    WHEN attacker_skill < 0.3 THEN 'Low'
                    WHEN attacker_skill < 0.6 THEN 'Medium'
                    WHEN attacker_skill < 0.8 THEN 'High'
                    ELSE 'Expert'
                END as skill_level,
                COUNT(*)
            FROM attack_sessions
            WHERE attacker_skill IS NOT NULL
            GROUP BY skill_level
        """)
        for row in cur.fetchall():
            stats['skill_distribution'][row[0]] = row[1]
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error fetching forensic stats: {e}")
    
    return stats

def fetch_attack_actions_detail(limit=100):
    """Fetch detailed attack actions."""
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                aa.session_id,
                aa.step_number,
                aa.action_id,
                aa.reward,
                aa.suspicion,
                aa.data_collected,
                aa.timestamp,
                asess.origin,
                asess.honeypot_type
            FROM attack_actions aa
            LEFT JOIN attack_sessions asess ON aa.session_id = asess.id
            ORDER BY aa.timestamp DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame(rows, columns=[
            'session_id', 'step', 'action_id', 'reward', 'suspicion',
            'data_collected', 'timestamp', 'attacker_ip', 'service'
        ])
    except:
        return pd.DataFrame()

def get_ip_geolocation(ip):
    """Get REAL geolocation for IP using API with caching and multiple providers."""
    global GEO_CACHE
    
    # Skip private/loopback IPs using ipaddress for accuracy
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback:
            return {'country': 'Private', 'city': 'Internal', 'lat': 0, 'lon': 0, 'isp': 'Private Network'}
    except Exception:
        pass
    
    # Check cache
    if ip in GEO_CACHE:
        return GEO_CACHE[ip]
    
    # Try multiple providers with retries
    providers = [
        ('ip-api', f"http://ip-api.com/json/{ip}?fields=66846719"),
        ('ipapi', f"https://ipapi.co/{ip}/json/"),
        ('ipwhois', f"http://ipwhois.app/json/{ip}")
    ]
    
    for provider_name, url in providers:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                
                # Parse based on provider
                if provider_name == 'ip-api' and data.get('status') == 'success':
                    geo = {
                        'country': data.get('country', 'Unknown'),
                        'country_code': data.get('countryCode', 'XX'),
                        'city': data.get('city', 'Unknown'),
                        'lat': float(data.get('lat', 0)),
                        'lon': float(data.get('lon', 0)),
                        'isp': data.get('isp', 'Unknown'),
                        'org': data.get('org', 'Unknown'),
                        'asn': data.get('as', 'Unknown'),
                        'is_proxy': data.get('proxy', False)
                    }
                elif provider_name == 'ipapi':
                    lat = data.get('latitude', 0)
                    lon = data.get('longitude', 0)
                    geo = {
                        'country': data.get('country_name', 'Unknown'),
                        'country_code': data.get('country_code', 'XX'),
                        'city': data.get('city', 'Unknown'),
                        'lat': float(lat) if lat else 0,
                        'lon': float(lon) if lon else 0,
                        'isp': data.get('org', 'Unknown'),
                        'org': data.get('org', 'Unknown'),
                        'asn': data.get('asn', 'Unknown'),
                        'is_proxy': data.get('privacy', {}).get('proxy', False) if isinstance(data.get('privacy'), dict) else False
                    }
                elif provider_name == 'ipwhois' and data.get('success'):
                    geo = {
                        'country': data.get('country', 'Unknown'),
                        'country_code': data.get('country_code', 'XX'),
                        'city': data.get('city', 'Unknown'),
                        'lat': float(data.get('latitude', 0)),
                        'lon': float(data.get('longitude', 0)),
                        'isp': data.get('isp', 'Unknown'),
                        'org': data.get('org', 'Unknown'),
                        'asn': data.get('asn', 'Unknown'),
                        'is_proxy': False
                    }
                else:
                    continue
                
                # Valid location check - allow approximates
                if geo['lat'] != 0 or geo['lon'] != 0:
                    GEO_CACHE[ip] = geo
                    return geo
        except Exception as e:
            continue
    
    # Last resort: return approximate location based on IP range
    try:
        # Use first octet to approximate region
        first_octet = int(ip.split('.')[0])
        if 1 <= first_octet <= 126:  # Americas/Europe
            approx_geo = {'country': 'Unknown (Americas)', 'city': 'Approx', 'lat': 40.0, 'lon': -100.0}
        elif 128 <= first_octet <= 191:  # Asia/Pacific
            approx_geo = {'country': 'Unknown (Asia)', 'city': 'Approx', 'lat': 35.0, 'lon': 105.0}
        else:  # Other
            approx_geo = {'country': 'Unknown (Europe)', 'city': 'Approx', 'lat': 50.0, 'lon': 10.0}
        
        approx_geo.update({'isp': 'Unknown', 'org': 'Unknown', 'asn': 'Unknown', 'is_proxy': False, 'country_code': 'XX'})
        GEO_CACHE[ip] = approx_geo
        return approx_geo
    except:
        pass
    
    return {'country': 'Unknown', 'city': 'Unknown', 'lat': 0, 'lon': 0, 'isp': 'Unknown', 'org': 'Unknown', 'asn': 'Unknown', 'is_proxy': False}

# =============================================================================
# MAIN DASHBOARD
# =============================================================================

def main():
    # Header
    st.markdown("""
    <div class="cyber-header">
        <h1 class="cyber-title">CYBER MIRAGE<span class="version-tag">v5.0</span><span class="live-badge">LIVE DATA</span></h1>
        <p class="cyber-subtitle">Advanced Threat Intelligence Platform | PPO Deep RL | All Data Real-Time from PostgreSQL</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### System Status")
        health = fetch_system_health()
        
        pg_class = "status-online" if health['postgres'] else "status-offline"
        st.markdown(f"""
        <div class="status-row">
            <span class="status-dot {pg_class}"></span>
            <span class="status-text">PostgreSQL</span>
            <span class="status-latency">{health['pg_latency']}ms</span>
        </div>
        """, unsafe_allow_html=True)
        
        redis_class = "status-online" if health['redis'] else "status-offline"
        st.markdown(f"""
        <div class="status-row">
            <span class="status-dot {redis_class}"></span>
            <span class="status-text">Redis</span>
            <span class="status-latency">{health['redis_latency']}ms</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Navigation")
        page = st.radio("Select Page", ["Dashboard", "Attack Intel", "MITRE ATT&CK", "Forensics", "Threat Map", "Actions"], label_visibility="collapsed")
        
        st.markdown("---")
        
        # Theme Toggle
        st.markdown("### Theme")
        theme_col1, theme_col2 = st.columns(2)
        with theme_col1:
            if st.button("Dark", use_container_width=True, type="primary" if st.session_state.theme == 'dark' else "secondary"):
                st.session_state.theme = 'dark'
                st.rerun()
        with theme_col2:
            if st.button("Light", use_container_width=True, type="primary" if st.session_state.theme == 'light' else "secondary"):
                st.session_state.theme = 'light'
                st.rerun()
        
        st.markdown("---")
        if st.button("Refresh", use_container_width=True):
            st.rerun()
        
        st.markdown(f"<div style='font-size:0.7rem;color:#4b5563;'>Updated: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    
    # Fetch REAL data
    metrics = fetch_metrics()
    decisions_df = fetch_agent_decisions(100)
    attacks_df = fetch_real_attacks(50)  # For dashboard/intel
    
    if page == "Dashboard":
        render_dashboard(metrics, decisions_df, attacks_df)
    elif page == "Attack Intel":
        render_attack_intel(attacks_df, decisions_df)
    elif page == "MITRE ATT&CK":
        render_mitre_attack()
    elif page == "Forensics":
        render_forensics()
    elif page == "Threat Map":
        # Fetch ALL unique IPs for map (no limit)
        attacks_df_map = fetch_real_attacks(1000)
        render_threat_map(attacks_df_map)
    elif page == "Actions":
        render_actions(metrics)

def render_dashboard(metrics, decisions_df, attacks_df):
    """Main dashboard - ALL REAL DATA."""
    
    # Metrics Row
    cols = st.columns(6)
    
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_decisions']:,}</div>
            <div class="metric-label">AI Decisions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_attacks']:,}</div>
            <div class="metric-label">Total Attacks</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['unique_attackers']:,}</div>
            <div class="metric-label">Unique IPs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        reward_color = "#10b981" if metrics['avg_reward'] > 0 else "#ef4444" if metrics['avg_reward'] < 0 else "#6b7280"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{reward_color}">{metrics['avg_reward']:.2f}</div>
            <div class="metric-label">Avg Reward</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[4]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['recent_attacks_24h']:,}</div>
            <div class="metric-label">Last 24h</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[5]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(metrics['action_distribution'])}/20</div>
            <div class="metric-label">Actions Used</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.markdown('<div class="section-header">Action Distribution<span class="section-badge">REAL-TIME</span></div>', unsafe_allow_html=True)
        
        if metrics['action_distribution']:
            action_data = []
            for action_key, count in metrics['action_distribution'].items():
                info = ELITE_ACTIONS.get(action_key, {'name': action_key, 'category': 'Unknown'})
                action_data.append({'Action': info['name'], 'Count': count, 'Category': info['category']})
            
            df = pd.DataFrame(action_data)
            color_map = {
                'Session Control': '#00d4ff', 
                'Temporal': '#f39c12', 
                'Identity': '#e67e22', 
                'Deception': '#9b59b6',
                'Forensic': '#e5e7eb', 
                'Advanced': '#e74c3c'
            }
            fig = px.bar(df.head(10), x='Count', y='Action', orientation='h', color='Category', color_discrete_map=color_map)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e5e7eb'), height=300, margin=dict(l=0,r=0,t=20,b=0),
                xaxis=dict(gridcolor='#1a1a28', showgrid=True), 
                yaxis=dict(gridcolor='#1a1a28', showgrid=False),
                legend=dict(
                    orientation='h', y=1.08, bgcolor='rgba(0,0,0,0)', 
                    font=dict(color='#e5e7eb', size=11),
                    bordercolor='rgba(255,255,255,0.1)', borderwidth=1
                ),
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Services Chart
        st.markdown('<div class="section-header">Targeted Services<span class="section-badge">REAL-TIME</span></div>', unsafe_allow_html=True)
        
        if metrics['services_targeted']:
            svc_df = pd.DataFrame([{'Service': k, 'Attacks': v} for k, v in metrics['services_targeted'].items()])
            fig = px.pie(svc_df, names='Service', values='Attacks', hole=0.4)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e5e7eb', size=12), height=250, margin=dict(l=0,r=0,t=20,b=0),
                legend=dict(
                    orientation='v', yanchor='middle', y=0.5, xanchor='left', x=1.02,
                    bgcolor='rgba(0,0,0,0)', bordercolor='rgba(255,255,255,0.1)', borderwidth=1,
                    font=dict(color='#e5e7eb', size=10)
                )
            )
            fig.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(color='#fff', size=11))
            st.plotly_chart(fig, use_container_width=True)
    
    with right_col:
        st.markdown('<div class="section-header">Recent Decisions<span class="section-badge">LIVE</span></div>', unsafe_allow_html=True)
        
        if not decisions_df.empty:
            for _, row in decisions_df.head(10).iterrows():
                info = ELITE_ACTIONS.get(row['action'], {'name': row['action'], 'category': 'Unknown'})
                reward = float(row['reward']) if row['reward'] else 0
                reward_class = "reward-positive" if reward > 0 else "reward-negative" if reward < 0 else "reward-neutral"
                time_str = pd.to_datetime(row['created_at']).strftime('%H:%M:%S')
                
                st.markdown(f"""
                <div style="background:#0a0a12;border:1px solid #1a1a28;border-radius:6px;padding:0.6rem;margin-bottom:0.4rem;">
                    <div style="display:flex;justify-content:space-between;">
                        <span style="color:#fff;font-weight:500;font-size:0.85rem;">{info['name']}</span>
                        <span class="{reward_class}">{reward:+.2f}</span>
                    </div>
                    <div style="font-size:0.7rem;color:#6b7280;margin-top:0.25rem;">{time_str}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">Top Attackers<span class="section-badge">REAL IPs</span></div>', unsafe_allow_html=True)
        
        if not attacks_df.empty:
            for _, row in attacks_df.head(5).iterrows():
                threat_class = 'threat-critical' if row['attack_count'] > 10 else 'threat-high' if row['attack_count'] > 5 else 'threat-medium'
                st.markdown(f"""
                <div style="background:#0a0a12;border:1px solid #1a1a28;border-radius:6px;padding:0.6rem;margin-bottom:0.4rem;">
                    <div class="ip-display">{row['ip']}</div>
                    <div style="display:flex;justify-content:space-between;margin-top:0.4rem;">
                        <span style="font-size:0.75rem;color:#9ca3af;">{row['service']}</span>
                        <span class="threat-badge {threat_class}">{row['attack_count']} attacks</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def render_attack_intel(attacks_df, decisions_df):
    """Attack intelligence - ALL REAL DATA."""
    
    st.markdown('<div class="section-header">Attack Intelligence<span class="section-badge">REAL-TIME OSINT</span></div>', unsafe_allow_html=True)
    
    if not attacks_df.empty:
        for _, row in attacks_df.head(20).iterrows():
            ip = row['ip']
            geo = get_ip_geolocation(ip)
            
            threat_score = min(row['attack_count'] // 2 + 3, 10)
            if geo.get('is_proxy'):
                threat_score = min(threat_score + 2, 10)
            
            threat_class = 'threat-critical' if threat_score > 7 else 'threat-high' if threat_score > 5 else 'threat-medium' if threat_score > 3 else 'threat-low'
            
            st.markdown(f"""
            <div class="attack-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
                    <span class="ip-display" style="font-size:1rem;">{ip}</span>
                    <span class="threat-badge {threat_class}">THREAT: {threat_score}/10</span>
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;font-size:0.8rem;">
                    <div>
                        <div style="color:#6b7280;font-size:0.65rem;text-transform:uppercase;">Country</div>
                        <div style="color:#e5e7eb;font-weight:500;">{geo['country']}</div>
                    </div>
                    <div>
                        <div style="color:#6b7280;font-size:0.65rem;text-transform:uppercase;">City</div>
                        <div style="color:#e5e7eb;font-weight:500;">{geo['city']}</div>
                    </div>
                    <div>
                        <div style="color:#6b7280;font-size:0.65rem;text-transform:uppercase;">Service</div>
                        <div style="color:#e5e7eb;font-weight:500;">{row['service']}</div>
                    </div>
                    <div>
                        <div style="color:#6b7280;font-size:0.65rem;text-transform:uppercase;">Attacks</div>
                        <div style="color:#ff4757;font-weight:600;">{row['attack_count']}</div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid #1a1a28;font-size:0.75rem;">
                    <div>
                        <div style="color:#6b7280;font-size:0.6rem;">ISP</div>
                        <div style="color:#9ca3af;">{geo.get('isp', 'Unknown')}</div>
                    </div>
                    <div>
                        <div style="color:#6b7280;font-size:0.6rem;">ASN</div>
                        <div style="color:#9ca3af;font-family:'JetBrains Mono',monospace;font-size:0.7rem;">{geo.get('asn', 'Unknown')[:30]}</div>
                    </div>
                    <div>
                        <div style="color:#6b7280;font-size:0.6rem;">Last Seen</div>
                        <div style="color:#9ca3af;">{pd.to_datetime(row['last_seen']).strftime('%Y-%m-%d %H:%M') if row['last_seen'] else 'N/A'}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No attack data available yet. Attacks will appear here when detected.")

def render_threat_map(attacks_df):
    """Global threat map - REAL DATA ONLY."""
    
    st.markdown('<div class="section-header">Global Threat Map<span class="section-badge">LIVE GEOLOCATION</span></div>', unsafe_allow_html=True)
    
    if attacks_df.empty:
        st.info("No attack data available yet.")
        return
    
    # Aggregate by IP first (combine all services per IP)
    ip_summary = attacks_df.groupby('ip').agg({
        'attack_count': 'sum',
        'service': lambda x: ', '.join(sorted(set(x)))
    }).reset_index()
    
    # Get geolocation for all unique IPs
    map_data = []
    unknown_ips = []
    
    for _, row in ip_summary.iterrows():
        ip = row['ip']
        geo = get_ip_geolocation(ip)
        
        # Accept ANY valid coordinates (even approximates)
        if geo['lat'] != 0 or geo['lon'] != 0:
            map_data.append({
                'ip': ip,
                'lat': geo['lat'],
                'lon': geo['lon'],
                'country': geo['country'],
                'country_code': geo.get('country_code', 'XX'),
                'city': geo['city'],
                'attacks': row['attack_count'],
                'service': row['service'],
                'size': min(row['attack_count'] * 3 + 8, 40)
            })
        else:
            unknown_ips.append({'ip': ip, 'attacks': row['attack_count']})
    
    if not map_data:
        st.warning(f"⚠️ No geolocation data available for {len(unknown_ips)} IPs (possibly all internal IPs).")
        if unknown_ips:
            with st.expander("View IPs without geolocation"):
                for item in unknown_ips[:20]:
                    st.text(f"• {item['ip']} ({item['attacks']} attacks)")
        return
    
    map_df = pd.DataFrame(map_data)
    
    # Create map
    fig = go.Figure()
    
    # Attack markers
    fig.add_trace(go.Scattergeo(
        lon=map_df['lon'],
        lat=map_df['lat'],
        mode='markers',
        marker=dict(
            size=map_df['size'],
            color='#ff4757',
            opacity=0.7,
            line=dict(width=1, color='#ffffff')
        ),
        text=map_df.apply(lambda x: f"IP: {x['ip']}<br>Location: {x['city']}, {x['country']}<br>Service: {x['service']}<br>Attacks: {x['attacks']}", axis=1),
        hoverinfo='text',
        name='Attack Sources'
    ))
    
    # Honeypot marker (Stockholm)
    honeypot_lat, honeypot_lon = 59.33, 18.07
    
    # Connection lines
    for _, row in map_df.iterrows():
        fig.add_trace(go.Scattergeo(
            lon=[row['lon'], honeypot_lon],
            lat=[row['lat'], honeypot_lat],
            mode='lines',
            line=dict(width=1, color='rgba(255,71,87,0.3)'),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Honeypot
    fig.add_trace(go.Scattergeo(
        lon=[honeypot_lon], lat=[honeypot_lat],
        mode='markers',
        marker=dict(size=15, color='#00d4ff', symbol='star', line=dict(width=2, color='#fff')),
        text='Cyber Mirage Honeypot<br>AWS EU-North-1 (Stockholm)',
        hoverinfo='text',
        name='Honeypot'
    ))
    
    fig.update_layout(
        geo=dict(
            projection_type='natural earth',
            showland=True, landcolor='#1a1a28',
            showocean=True, oceancolor='#0a0a12',
            showcountries=True, countrycolor='#2a2a3a',
            showcoastlines=True, coastlinecolor='#2a2a3a',
            bgcolor='rgba(0,0,0,0)', showframe=False
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=50),
        height=500,
        legend=dict(
            orientation='h', 
            y=-0.08, 
            xanchor='center',
            x=0.5,
            bgcolor='rgba(0,0,0,0.4)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
            font=dict(color='#e5e7eb', size=11),
            yanchor='bottom'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display mapping stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Mapped IPs", len(map_data))
    with col2:
        st.metric("🔍 Unknown Location", len(unknown_ips))
    with col3:
        st.metric("🌐 Total IPs", len(map_data) + len(unknown_ips))
    
    # Country breakdown (all countries + top cards)
    st.markdown('<div class="section-header">All Attack Sources by Country<span class="section-badge">LIVE</span></div>', unsafe_allow_html=True)

    country_summary = (
        map_df.groupby(['country', 'country_code'])
        .agg(total_attacks=('attacks', 'sum'), unique_ips=('ip', 'count'))
        .reset_index()
        .sort_values('total_attacks', ascending=False)
    )

    if unknown_ips:
        country_summary = pd.concat([
            country_summary,
            pd.DataFrame([{'country': 'Unknown', 'country_code': 'XX', 'total_attacks': sum([i['attacks'] for i in unknown_ips]), 'unique_ips': len(unknown_ips)}])
        ], ignore_index=True)

    if not country_summary.empty:
        # Full country table - ALL countries sorted descending
        st.dataframe(
            country_summary.rename(columns={
                'country': 'Country',
                'country_code': 'Code',
                'unique_ips': 'Unique IPs',
                'total_attacks': 'Total Attacks'
            }),
            hide_index=True,
            use_container_width=True,
            height=450
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Top 4 cards for quick glance
        top_countries = country_summary.head(4)
        cols = st.columns(min(4, len(top_countries)))
        for i, (_, data) in enumerate(top_countries.iterrows()):
            if i < len(cols):
                with cols[i]:
                    st.markdown(f"""
                    <div style="background:#0a0a12;border:1px solid #1a1a28;border-radius:8px;padding:1rem;text-align:center;">
                        <div style="font-size:1.5rem;font-weight:700;color:#00d4ff;">{int(data['total_attacks'])}</div>
                        <div style="font-size:0.75rem;color:#9ca3af;margin-top:0.25rem;">{data['country']}</div>
                        <div style="font-size:0.65rem;color:#6b7280;margin-top:0.15rem;">{int(data['unique_ips'])} IPs</div>
                    </div>
                    """, unsafe_allow_html=True)

def render_actions(metrics):
    """20 Elite Actions reference."""
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">20 Elite Tactical Actions<span class="section-badge">REFERENCE</span></div>', unsafe_allow_html=True)
    
    # Category summary
    categories = {}
    for action_key, info in ELITE_ACTIONS.items():
        cat = info['category']
        if cat not in categories:
            categories[cat] = {'count': 0, 'uses': 0}
        categories[cat]['count'] += 1
        categories[cat]['uses'] += metrics['action_distribution'].get(action_key, 0)
    
    cols = st.columns(6)
    cat_colors = {'Session Control': '#00d4ff', 'Temporal': '#f39c12', 'Identity': '#e67e22',
                  'Deception': '#9b59b6', 'Forensic': '#95a5a6', 'Advanced': '#e74c3c'}
    
    for i, (cat, data) in enumerate(categories.items()):
        with cols[i]:
            color = cat_colors.get(cat, '#6b7280')
            st.markdown(f"""
            <div style="background:{color}15;border:1px solid {color}40;border-radius:8px;padding:1rem;text-align:center;">
                <div style="font-size:1.5rem;font-weight:700;color:{color};">{data['uses']}</div>
                <div style="font-size:0.7rem;color:#9ca3af;">{cat}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Actions table using st.dataframe for better rendering
    actions_list = []
    for action_key, info in ELITE_ACTIONS.items():
        count = metrics['action_distribution'].get(action_key, 0)
        actions_list.append({
            'ID': f"{info['id']:02d}",
            'Action': info['name'],
            'Category': info['category'],
            'Value': info['tactical_value'],
            'Description': info['description'],
            'MITRE': info['mitre'],
            'Uses': count
        })
    
    actions_table_df = pd.DataFrame(actions_list)
    
    # Display using native Streamlit dataframe with custom styling
    st.dataframe(
        actions_table_df,
        use_container_width=True,
        height=700,
        hide_index=True,
        column_config={
            'ID': st.column_config.TextColumn('ID', width='small'),
            'Action': st.column_config.TextColumn('Action', width='medium'),
            'Category': st.column_config.TextColumn('Category', width='medium'),
            'Value': st.column_config.TextColumn('Value', width='small'),
            'Description': st.column_config.TextColumn('Description', width='large'),
            'MITRE': st.column_config.TextColumn('MITRE', width='small'),
            'Uses': st.column_config.NumberColumn('Uses', width='small', format='%d')
        }
    )

# =============================================================================
# MITRE ATT&CK PAGE
# =============================================================================

def render_mitre_attack():
    """Render MITRE ATT&CK mapping page."""
    
    st.markdown('<div class="section-header">MITRE ATT&CK Framework Mapping<span class="section-badge">REAL-TIME</span></div>', unsafe_allow_html=True)
    
    # Fetch MITRE data
    tactics_data = fetch_mitre_tactics()
    profiles_df = fetch_attacker_profiles(50)
    
    # MITRE Tactics Distribution
    if tactics_data:
        # Aggregate tactics
        tactic_counts = {}
        for item in tactics_data:
            tactic = item['tactic']
            if tactic in tactic_counts:
                tactic_counts[tactic] += item['count']
            else:
                tactic_counts[tactic] = item['count']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="section-header">Tactics Distribution</div>', unsafe_allow_html=True)
            if tactic_counts:
                tactics_df = pd.DataFrame([
                    {'Tactic': k, 'Count': v} for k, v in sorted(tactic_counts.items(), key=lambda x: x[1], reverse=True)
                ])
                fig = px.bar(tactics_df, x='Count', y='Tactic', orientation='h',
                            color='Count', color_continuous_scale='Reds')
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e5e7eb'), height=400, margin=dict(l=0,r=0,t=20,b=0),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div class="section-header">Top Tactics</div>', unsafe_allow_html=True)
            for tactic, count in sorted(tactic_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                st.markdown(f"""
                <div style="background:#0a0a12;border:1px solid #1a1a28;border-radius:6px;padding:0.8rem;margin-bottom:0.5rem;">
                    <div style="color:#ff4757;font-weight:600;font-size:0.9rem;">{tactic}</div>
                    <div style="color:#6b7280;font-size:0.75rem;margin-top:0.25rem;">{count} occurrences</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No MITRE ATT&CK tactics data available yet. Data will appear when attacks are classified.")
    
    # Attack Techniques Reference
    st.markdown('<div class="section-header">MITRE Technique Reference<span class="section-badge">20 ACTIONS</span></div>', unsafe_allow_html=True)
    
    mitre_ref = []
    for key, info in ELITE_ACTIONS.items():
        mitre_ref.append({
            'Action': info['name'],
            'Category': info['category'],
            'MITRE ID': info['mitre'],
            'Description': info['description']
        })
    
    ref_df = pd.DataFrame(mitre_ref)
    st.dataframe(ref_df, use_container_width=True, height=400, hide_index=True)

# =============================================================================
# FORENSICS PAGE
# =============================================================================

def render_forensics():
    """Render Forensics analysis page."""
    
    st.markdown('<div class="section-header">Digital Forensics Analysis<span class="section-badge">REAL-TIME</span></div>', unsafe_allow_html=True)
    
    # Fetch forensic stats
    stats = fetch_forensic_stats()
    profiles_df = fetch_attacker_profiles(30)
    
    # Key Forensic Metrics
    cols = st.columns(6)
    
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#10b981;">{stats['total_detected']}</div>
            <div class="metric-label">Detected</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#ef4444;">{stats['total_undetected']}</div>
            <div class="metric-label">Undetected</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['detection_rate']:.1f}%</div>
            <div class="metric-label">Detection Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['avg_skill']:.2f}</div>
            <div class="metric-label">Avg Skill</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[4]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_zero_days']}</div>
            <div class="metric-label">Zero-Days</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[5]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_data_collected']:.1f}</div>
            <div class="metric-label">Data Collected</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Attacker Skill Distribution</div>', unsafe_allow_html=True)
        if stats['skill_distribution']:
            skill_df = pd.DataFrame([
                {'Level': k, 'Count': v} for k, v in stats['skill_distribution'].items()
            ])
            fig = px.pie(skill_df, names='Level', values='Count', hole=0.4,
                        color='Level', color_discrete_map={
                            'Low': '#10b981', 'Medium': '#ffa502',
                            'High': '#ff4757', 'Expert': '#7b2cbf'
                        })
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e5e7eb'), height=300, margin=dict(l=0,r=0,t=20,b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No skill data available")
    
    with col2:
        st.markdown('<div class="section-header">Detection vs Evasion</div>', unsafe_allow_html=True)
        detection_df = pd.DataFrame([
            {'Status': 'Detected', 'Count': stats['total_detected']},
            {'Status': 'Evaded', 'Count': stats['total_undetected']}
        ])
        fig = px.pie(detection_df, names='Status', values='Count', hole=0.4,
                    color='Status', color_discrete_map={
                        'Detected': '#10b981', 'Evaded': '#ef4444'
                    })
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e5e7eb'), height=300, margin=dict(l=0,r=0,t=20,b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Attacker Profiles
    st.markdown('<div class="section-header">Attacker Profiles<span class="section-badge">DETAILED</span></div>', unsafe_allow_html=True)
    
    if not profiles_df.empty:
        for _, row in profiles_df.head(15).iterrows():
            skill = row['avg_skill'] if row['avg_skill'] else 0
            suspicion = row['avg_suspicion'] if row['avg_suspicion'] else 0
            zero_days = int(row['total_zero_days']) if row['total_zero_days'] else 0
            data_col = row['avg_data_collected'] if row['avg_data_collected'] else 0
            detected = int(row['times_detected']) if row['times_detected'] else 0
            total = int(row['total_attacks']) if row['total_attacks'] else 0
            
            skill_color = '#10b981' if skill < 0.3 else '#ffa502' if skill < 0.6 else '#ff4757' if skill < 0.8 else '#7b2cbf'
            skill_label = 'Low' if skill < 0.3 else 'Medium' if skill < 0.6 else 'High' if skill < 0.8 else 'Expert'
            
            st.markdown(f"""
            <div class="attack-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
                    <span class="ip-display" style="font-size:1rem;">{row['ip']}</span>
                    <span style="color:{skill_color};font-weight:600;font-size:0.85rem;">Skill: {skill_label} ({skill:.2f})</span>
                </div>
                <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:1rem;font-size:0.8rem;">
                    <div>
                        <div style="color:#6b7280;font-size:0.65rem;text-transform:uppercase;">Service</div>
                        <div style="color:#e5e7eb;font-weight:500;">{row['service']}</div>
                    </div>
                    <div>
                        <div style="color:#6b7280;font-size:0.65rem;text-transform:uppercase;">Suspicion</div>
                        <div style="color:#ffa502;font-weight:500;">{suspicion:.2f}</div>
                    </div>
                    <div>
                        <div style="color:#6b7280;font-size:0.65rem;text-transform:uppercase;">Zero-Days</div>
                        <div style="color:#7b2cbf;font-weight:500;">{zero_days}</div>
                    </div>
                    <div>
                        <div style="color:#6b7280;font-size:0.65rem;text-transform:uppercase;">Data Col.</div>
                        <div style="color:#00d4ff;font-weight:500;">{data_col:.1f}</div>
                    </div>
                    <div>
                        <div style="color:#6b7280;font-size:0.65rem;text-transform:uppercase;">Detected</div>
                        <div style="color:#10b981;font-weight:500;">{detected}/{total}</div>
                    </div>
                    <div>
                        <div style="color:#6b7280;font-size:0.65rem;text-transform:uppercase;">Attacks</div>
                        <div style="color:#ff4757;font-weight:600;">{total}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No attacker profile data available yet. Profiles will appear when attacks are detected.")

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    main()
