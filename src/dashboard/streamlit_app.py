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
import textwrap

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
# CSS
# =============================================================================

st.markdown("""
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
</style>
""", unsafe_allow_html=True)

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
    except:
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

def get_ip_geolocation(ip):
    """Get REAL geolocation for IP using API with caching."""
    global GEO_CACHE
    
    # Skip private IPs
    if ip.startswith(('10.', '192.168.', '172.', '127.', '0.')):
        return {'country': 'Private', 'city': 'Internal', 'lat': 0, 'lon': 0, 'isp': 'Private Network'}
    
    # Check cache
    if ip in GEO_CACHE:
        return GEO_CACHE[ip]
    
    # Primary provider
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                geo = {
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', 'XX'),
                    'city': data.get('city', 'Unknown'),
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0),
                    'isp': data.get('isp', 'Unknown'),
                    'org': data.get('org', 'Unknown'),
                    'asn': data.get('as', 'Unknown'),
                    'is_proxy': data.get('proxy', False)
                }
                GEO_CACHE[ip] = geo
                return geo
    except:
        pass
    
    # Fallback provider (ipapi.co) to reduce blank map issues
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=2)
        if response.status_code == 200:
            data = response.json()
            lat = data.get('latitude', 0)
            lon = data.get('longitude', 0)
            geo = {
                'country': data.get('country_name', 'Unknown'),
                'country_code': data.get('country_code', 'XX'),
                'city': data.get('city', 'Unknown'),
                'lat': lat if lat else 0,
                'lon': lon if lon else 0,
                'isp': data.get('org', 'Unknown'),
                'org': data.get('org', 'Unknown'),
                'asn': data.get('asn', 'Unknown'),
                'is_proxy': data.get('privacy', {}).get('proxy', False) if isinstance(data.get('privacy'), dict) else False
            }
            GEO_CACHE[ip] = geo
            return geo
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
        page = st.radio("Select Page", ["Dashboard", "Attack Intel", "Threat Map", "Actions"], label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("Refresh", use_container_width=True):
            st.rerun()
        
        st.markdown(f"<div style='font-size:0.7rem;color:#4b5563;'>Updated: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    
    # Fetch REAL data
    metrics = fetch_metrics()
    decisions_df = fetch_agent_decisions(100)
    attacks_df = fetch_real_attacks(50)
    
    if page == "Dashboard":
        render_dashboard(metrics, decisions_df, attacks_df)
    elif page == "Attack Intel":
        render_attack_intel(attacks_df, decisions_df)
    elif page == "Threat Map":
        render_threat_map(attacks_df)
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
    
    # Service Legend
    service_colors = {
        'SMB': '#3b82f6', 'HTTP': '#10b981', 'HTTPS': '#ef4444', 
        'SSH': '#f59e0b', 'SMTP': '#06b6d4', 'Modbus': '#8b5cf6',
        'WebSocket': '#14b8a6', 'FTP': '#f97316', 'MySQL': '#a855f7'
    }
    
    legend_html = '<div style="display:flex;gap:1rem;margin-bottom:1rem;flex-wrap:wrap;">'
    for service, color in service_colors.items():
        legend_html += f'<div style="display:flex;align-items:center;gap:0.4rem;background:rgba(255,255,255,0.05);padding:0.4rem 0.8rem;border-radius:6px;border:1px solid rgba(255,255,255,0.1);"><div style="width:12px;height:12px;background:{color};border-radius:50%;"></div><span style="color:#e5e7eb;font-size:0.8rem;font-weight:500;">{service}</span></div>'
    legend_html += '</div>'
    st.markdown(legend_html, unsafe_allow_html=True)
    
    if attacks_df.empty:
        st.info("No attack data available yet.")
        return
    
    # Get geolocation for all IPs
    map_data = []
    for _, row in attacks_df.iterrows():
        ip = row['ip']
        geo = get_ip_geolocation(ip)
        
        if geo['lat'] != 0 and geo['lon'] != 0:
            map_data.append({
                'ip': ip,
                'lat': geo['lat'],
                'lon': geo['lon'],
                'country': geo['country'],
                'city': geo['city'],
                'attacks': row['attack_count'],
                'service': row['service'],
                'size': min(row['attack_count'] * 3 + 8, 40)
            })
    
    if not map_data:
        st.warning("No geolocation data available for current attacks (possibly all internal IPs).")
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
    
    # Stats
    st.markdown('<div class="section-header">Attack Statistics<span class="section-badge">LIVE</span></div>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    countries = map_df['country'].value_counts().head(4)
    for i, (country, count) in enumerate(countries.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="background:#0a0a12;border:1px solid #1a1a28;border-radius:8px;padding:1rem;text-align:center;">
                <div style="font-size:1.5rem;font-weight:700;color:#00d4ff;">{count}</div>
                <div style="font-size:0.75rem;color:#9ca3af;">{country}</div>
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
    
    # Full table (dedented to avoid Markdown code formatting)
    table_html = textwrap.dedent("""
    <table style="width:100%;border-collapse:collapse;font-size:0.8rem;margin-top:2rem;">
        <thead>
            <tr style="background:#0a0a12;">
                <th style="padding:0.6rem;text-align:left;color:#e5e7eb;font-weight:600;border-bottom:2px solid #2a2a3a;">ID</th>
                <th style="padding:0.6rem;text-align:left;color:#e5e7eb;font-weight:600;border-bottom:2px solid #2a2a3a;">Action</th>
                <th style="padding:0.6rem;text-align:left;color:#e5e7eb;font-weight:600;border-bottom:2px solid #2a2a3a;">Category</th>
                <th style="padding:0.6rem;text-align:left;color:#e5e7eb;font-weight:600;border-bottom:2px solid #2a2a3a;">Value</th>
                <th style="padding:0.6rem;text-align:left;color:#e5e7eb;font-weight:600;border-bottom:2px solid #2a2a3a;">Description</th>
                <th style="padding:0.6rem;text-align:left;color:#e5e7eb;font-weight:600;border-bottom:2px solid #2a2a3a;">MITRE</th>
                <th style="padding:0.6rem;text-align:right;color:#e5e7eb;font-weight:600;border-bottom:2px solid #2a2a3a;">Uses</th>
            </tr>
        </thead>
        <tbody>
    """)
    
    cat_classes = {'Session Control': 'cat-sc', 'Temporal': 'cat-tm', 'Identity': 'cat-id',
                   'Deception': 'cat-ad', 'Forensic': 'cat-fc', 'Advanced': 'cat-ac'}
    
    for action_key, info in ELITE_ACTIONS.items():
        count = metrics['action_distribution'].get(action_key, 0)
        cat_class = cat_classes.get(info['category'], 'cat-sc')
        value_color = {'Critical': '#ef4444', 'High': '#f59e0b', 'Medium': '#10b981', 'Low': '#6b7280'}.get(info['tactical_value'], '#6b7280')
        
        table_html += f"""
        <tr style="border-bottom:1px solid #1a1a28;">
            <td style="padding:0.5rem;color:#00d4ff;font-family:'JetBrains Mono',monospace;">{info['id']:02d}</td>
            <td style="padding:0.5rem;color:#fff;font-weight:500;">{info['name']}</td>
            <td style="padding:0.5rem;"><span class="cat-badge {cat_class}">{info['category']}</span></td>
            <td style="padding:0.5rem;color:{value_color};font-weight:500;">{info['tactical_value']}</td>
            <td style="padding:0.5rem;color:#c9d1d9;font-size:0.75rem;">{info['description']}</td>
            <td style="padding:0.5rem;color:#9ca3af;font-size:0.75rem;">{info['mitre']}</td>
            <td style="padding:0.5rem;text-align:right;color:#10b981;font-family:'JetBrains Mono',monospace;font-weight:600;">{count}</td>
        </tr>
        """
    
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    main()
