"""
CYBER MIRAGE v5.0 - Advanced Threat Intelligence & Deception Platform
======================================================================
PhD-Level Adaptive Honeypot Defense System
Proximal Policy Optimization (PPO) Deep Reinforcement Learning Agent
20 Elite Tactical Deception Actions | Real-time OSINT | Global Threat Mapping
======================================================================
Research Framework for Advanced Persistent Threat (APT) Analysis
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

# 20 Elite Tactical Deception Actions - Full Taxonomy
ELITE_ACTIONS = {
    'maintain_session': {
        'id': 1, 'name': 'MAINTAIN', 'category': 'Session Control', 
        'color': '#00D4FF', 'tactical_value': 'Low',
        'description': 'Passive observation - maintain connection for intelligence gathering',
        'mitre_mapping': 'T1557 - Adversary-in-the-Middle'
    },
    'drop_session': {
        'id': 2, 'name': 'DROP', 'category': 'Session Control',
        'color': '#FF4757', 'tactical_value': 'Medium',
        'description': 'Immediate session termination - threat neutralization',
        'mitre_mapping': 'T1531 - Account Access Removal'
    },
    'throttle_session': {
        'id': 3, 'name': 'THROTTLE', 'category': 'Session Control',
        'color': '#FFA502', 'tactical_value': 'Medium',
        'description': 'Bandwidth restriction - slow attacker progress',
        'mitre_mapping': 'T1499 - Endpoint Denial of Service'
    },
    'redirect_session': {
        'id': 4, 'name': 'REDIRECT', 'category': 'Session Control',
        'color': '#7B2CBF', 'tactical_value': 'High',
        'description': 'Session redirection to isolated analysis environment',
        'mitre_mapping': 'T1090 - Proxy'
    },
    'inject_delay': {
        'id': 5, 'name': 'DELAY', 'category': 'Temporal Manipulation',
        'color': '#3498DB', 'tactical_value': 'Medium',
        'description': 'Artificial latency injection - disrupt timing attacks',
        'mitre_mapping': 'T1497 - Virtualization/Sandbox Evasion'
    },
    'progressive_delay': {
        'id': 6, 'name': 'PROG_DELAY', 'category': 'Temporal Manipulation',
        'color': '#1ABC9C', 'tactical_value': 'High',
        'description': 'Exponential delay escalation - attacker fatigue induction',
        'mitre_mapping': 'T1497 - Virtualization/Sandbox Evasion'
    },
    'random_delay': {
        'id': 7, 'name': 'RAND_DELAY', 'category': 'Temporal Manipulation',
        'color': '#9B59B6', 'tactical_value': 'High',
        'description': 'Stochastic response timing - timing analysis prevention',
        'mitre_mapping': 'T1497 - Virtualization/Sandbox Evasion'
    },
    'swap_service_banner': {
        'id': 8, 'name': 'SWAP_BANNER', 'category': 'Identity Deception',
        'color': '#E67E22', 'tactical_value': 'High',
        'description': 'Service fingerprint manipulation - reconnaissance confusion',
        'mitre_mapping': 'T1036 - Masquerading'
    },
    'randomize_banner': {
        'id': 9, 'name': 'RAND_BANNER', 'category': 'Identity Deception',
        'color': '#16A085', 'tactical_value': 'High',
        'description': 'Stochastic service identity - fingerprint evasion',
        'mitre_mapping': 'T1036 - Masquerading'
    },
    'mimic_vulnerable': {
        'id': 10, 'name': 'VULN_MIMIC', 'category': 'Identity Deception',
        'color': '#C0392B', 'tactical_value': 'Critical',
        'description': 'Vulnerability emulation - exploit capture honeypot',
        'mitre_mapping': 'T1203 - Exploitation for Client Execution'
    },
    'present_lure': {
        'id': 11, 'name': 'LURE', 'category': 'Active Deception',
        'color': '#8E44AD', 'tactical_value': 'Critical',
        'description': 'High-value target presentation - attacker engagement',
        'mitre_mapping': 'T1534 - Internal Spearphishing'
    },
    'deploy_breadcrumb': {
        'id': 12, 'name': 'BREADCRUMB', 'category': 'Active Deception',
        'color': '#2980B9', 'tactical_value': 'High',
        'description': 'False trail deployment - lateral movement tracking',
        'mitre_mapping': 'T1534 - Internal Spearphishing'
    },
    'inject_fake_creds': {
        'id': 13, 'name': 'FAKE_CREDS', 'category': 'Active Deception',
        'color': '#27AE60', 'tactical_value': 'Critical',
        'description': 'Honeytoken credential injection - credential theft detection',
        'mitre_mapping': 'T1078 - Valid Accounts'
    },
    'simulate_target': {
        'id': 14, 'name': 'SIM_TARGET', 'category': 'Active Deception',
        'color': '#D35400', 'tactical_value': 'High',
        'description': 'High-value asset simulation - APT attraction',
        'mitre_mapping': 'T1583 - Acquire Infrastructure'
    },
    'capture_tools': {
        'id': 15, 'name': 'CAPTURE', 'category': 'Forensic Collection',
        'color': '#7F8C8D', 'tactical_value': 'Critical',
        'description': 'Malware/tool capture - threat intelligence extraction',
        'mitre_mapping': 'T1005 - Data from Local System'
    },
    'log_enhanced': {
        'id': 16, 'name': 'LOG_FORENSIC', 'category': 'Forensic Collection',
        'color': '#95A5A6', 'tactical_value': 'High',
        'description': 'Deep packet inspection - forensic evidence collection',
        'mitre_mapping': 'T1074 - Data Staged'
    },
    'fingerprint': {
        'id': 17, 'name': 'FINGERPRINT', 'category': 'Forensic Collection',
        'color': '#34495E', 'tactical_value': 'Critical',
        'description': 'Attacker TTP profiling - attribution support',
        'mitre_mapping': 'T1592 - Gather Victim Host Information'
    },
    'tarpit': {
        'id': 18, 'name': 'TARPIT', 'category': 'Advanced Countermeasures',
        'color': '#2C3E50', 'tactical_value': 'Critical',
        'description': 'Connection tarpit - resource exhaustion trap',
        'mitre_mapping': 'T1499 - Endpoint Denial of Service'
    },
    'honeypot_upgrade': {
        'id': 19, 'name': 'HP_UPGRADE', 'category': 'Advanced Countermeasures',
        'color': '#1A252F', 'tactical_value': 'High',
        'description': 'Dynamic interaction escalation - deep engagement',
        'mitre_mapping': 'T1584 - Compromise Infrastructure'
    },
    'alert_track': {
        'id': 20, 'name': 'ALERT_TRACK', 'category': 'Advanced Countermeasures',
        'color': '#E74C3C', 'tactical_value': 'Critical',
        'description': 'SOC alert with persistent tracking - active response',
        'mitre_mapping': 'T1071 - Application Layer Protocol'
    }
}

ACTION_CATEGORIES = {
    'Session Control': {'color': '#00D4FF', 'icon': 'SC', 'actions': [1, 2, 3, 4]},
    'Temporal Manipulation': {'color': '#F39C12', 'icon': 'TM', 'actions': [5, 6, 7]},
    'Identity Deception': {'color': '#E67E22', 'icon': 'ID', 'actions': [8, 9, 10]},
    'Active Deception': {'color': '#9B59B6', 'icon': 'AD', 'actions': [11, 12, 13, 14]},
    'Forensic Collection': {'color': '#7F8C8D', 'icon': 'FC', 'actions': [15, 16, 17]},
    'Advanced Countermeasures': {'color': '#E74C3C', 'icon': 'AC', 'actions': [18, 19, 20]}
}

# Threat Level Classification
THREAT_LEVELS = {
    'CRITICAL': {'color': '#FF0000', 'score_range': (8, 10)},
    'HIGH': {'color': '#FF4757', 'score_range': (6, 8)},
    'MEDIUM': {'color': '#FFA502', 'score_range': (4, 6)},
    'LOW': {'color': '#2ED573', 'score_range': (2, 4)},
    'INFO': {'color': '#1E90FF', 'score_range': (0, 2)}
}

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Cyber Mirage v5.0 | Threat Intelligence Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# ADVANCED CSS - Professional Security Operations Center Theme
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    
    .main { background: #050508; }
    .stApp { background: linear-gradient(135deg, #050508 0%, #0a0a12 50%, #0d0d18 100%); }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Header */
    .cyber-header {
        background: linear-gradient(135deg, rgba(0,212,255,0.1) 0%, rgba(123,44,191,0.1) 100%);
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    
    .cyber-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .cyber-subtitle {
        font-size: 0.85rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }
    
    .version-tag {
        display: inline-block;
        background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 100%);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-left: 0.75rem;
        vertical-align: middle;
    }
    
    /* Metric Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: linear-gradient(180deg, #0f0f18 0%, #0a0a10 100%);
        border: 1px solid #1a1a28;
        border-radius: 10px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #00d4ff;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,212,255,0.15);
    }
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.75rem;
        margin-top: 0.25rem;
        font-weight: 500;
    }
    
    .delta-positive { color: #10b981; }
    .delta-negative { color: #ef4444; }
    .delta-neutral { color: #6b7280; }
    
    /* Section Headers */
    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #1a1a28;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-badge {
        background: rgba(0,212,255,0.15);
        color: #00d4ff;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Status Indicators */
    .status-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    .status-online { background: #10b981; }
    .status-offline { background: #ef4444; }
    .status-warning { background: #f59e0b; }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .status-text {
        font-size: 0.8rem;
        color: #9ca3af;
    }
    
    .status-latency {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #6b7280;
    }
    
    /* IP Address Display */
    .ip-display {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(0,212,255,0.1);
        border: 1px solid rgba(0,212,255,0.2);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        color: #00d4ff;
        font-size: 0.8rem;
    }
    
    /* Threat Level Badges */
    .threat-critical { background: rgba(255,0,0,0.2); color: #ff4444; border: 1px solid rgba(255,0,0,0.3); }
    .threat-high { background: rgba(255,71,87,0.2); color: #ff4757; border: 1px solid rgba(255,71,87,0.3); }
    .threat-medium { background: rgba(255,165,2,0.2); color: #ffa502; border: 1px solid rgba(255,165,2,0.3); }
    .threat-low { background: rgba(46,213,115,0.2); color: #2ed573; border: 1px solid rgba(46,213,115,0.3); }
    .threat-info { background: rgba(30,144,255,0.2); color: #1e90ff; border: 1px solid rgba(30,144,255,0.3); }
    
    .threat-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Action Reference Table */
    .action-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.75rem;
    }
    
    .action-table th {
        background: #0a0a12;
        color: #6b7280;
        padding: 0.6rem 0.5rem;
        text-align: left;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 1px solid #1a1a28;
    }
    
    .action-table td {
        padding: 0.5rem;
        border-bottom: 1px solid #0f0f18;
        color: #e5e7eb;
    }
    
    .action-table tr:hover td {
        background: rgba(0,212,255,0.05);
    }
    
    .action-id {
        font-family: 'JetBrains Mono', monospace;
        color: #00d4ff;
        font-weight: 600;
    }
    
    .action-name {
        font-weight: 500;
        color: #ffffff;
    }
    
    .action-count {
        font-family: 'JetBrains Mono', monospace;
        color: #10b981;
    }
    
    /* Category Badge */
    .cat-badge {
        display: inline-block;
        padding: 0.15rem 0.4rem;
        border-radius: 3px;
        font-size: 0.6rem;
        font-weight: 600;
    }
    
    .cat-sc { background: rgba(0,212,255,0.2); color: #00d4ff; }
    .cat-tm { background: rgba(243,156,18,0.2); color: #f39c12; }
    .cat-id { background: rgba(230,126,34,0.2); color: #e67e22; }
    .cat-ad { background: rgba(155,89,182,0.2); color: #9b59b6; }
    .cat-fc { background: rgba(127,140,141,0.2); color: #95a5a6; }
    .cat-ac { background: rgba(231,76,60,0.2); color: #e74c3c; }
    
    /* Attack Log Entry */
    .attack-entry {
        background: #0a0a12;
        border: 1px solid #1a1a28;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .attack-entry:hover {
        border-color: #2a2a3a;
        background: #0f0f18;
    }
    
    .attack-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .attack-ip {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        color: #00d4ff;
        font-weight: 600;
    }
    
    .attack-time {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #6b7280;
    }
    
    .attack-details {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        font-size: 0.8rem;
    }
    
    .detail-item {
        display: flex;
        flex-direction: column;
    }
    
    .detail-label {
        font-size: 0.65rem;
        color: #6b7280;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    
    .detail-value {
        color: #e5e7eb;
        font-weight: 500;
    }
    
    /* Geo Info */
    .geo-info {
        background: rgba(0,212,255,0.05);
        border-radius: 6px;
        padding: 0.75rem;
        margin-top: 0.75rem;
    }
    
    .geo-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        font-size: 0.75rem;
    }
    
    /* Chart Container */
    .chart-container {
        background: #0a0a12;
        border: 1px solid #1a1a28;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Reward Display */
    .reward-positive { color: #10b981; font-weight: 600; }
    .reward-negative { color: #ef4444; font-weight: 600; }
    .reward-neutral { color: #6b7280; }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0a0a12; }
    ::-webkit-scrollbar-thumb { background: #2a2a3a; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #3a3a4a; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATABASE FUNCTIONS
# =============================================================================

def get_db_connection():
    try:
        return psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS,
            connect_timeout=5
        )
    except:
        return None

def get_redis_connection():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, decode_responses=True)
        r.ping()
        return r
    except:
        return None

# =============================================================================
# DATA FETCHING
# =============================================================================

def fetch_agent_decisions(limit=100):
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, session_id, action, strategy, reward, state, created_at
            FROM agent_decisions
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame(rows, columns=['id', 'session_id', 'action', 'strategy', 'reward', 'state', 'created_at'])
    except:
        return pd.DataFrame()

def fetch_attack_sessions(limit=50):
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, source_ip, target_port, service_type, attack_type, threat_level, 
                   country, city, session_start, session_end
            FROM attack_sessions
            ORDER BY session_start DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame(rows, columns=[
            'id', 'source_ip', 'target_port', 'service_type', 'attack_type', 
            'threat_level', 'country', 'city', 'session_start', 'session_end'
        ])
    except:
        return pd.DataFrame()

def fetch_metrics():
    metrics = {
        'total_decisions': 0,
        'unique_sessions': 0,
        'avg_reward': 0.0,
        'max_reward': 0.0,
        'min_reward': 0.0,
        'action_distribution': {},
        'hourly_decisions': 0,
        'total_attacks': 0
    }
    
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM agent_decisions")
        metrics['total_decisions'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(DISTINCT session_id) FROM agent_decisions")
        metrics['unique_sessions'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT AVG(reward), MAX(reward), MIN(reward) FROM agent_decisions WHERE reward IS NOT NULL")
        row = cur.fetchone()
        if row:
            metrics['avg_reward'] = float(row[0]) if row[0] else 0.0
            metrics['max_reward'] = float(row[1]) if row[1] else 0.0
            metrics['min_reward'] = float(row[2]) if row[2] else 0.0
        
        cur.execute("SELECT COUNT(*) FROM agent_decisions WHERE created_at > NOW() - INTERVAL '1 hour'")
        metrics['hourly_decisions'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT action, COUNT(*) FROM agent_decisions GROUP BY action ORDER BY COUNT(*) DESC")
        for row in cur.fetchall():
            metrics['action_distribution'][row[0]] = row[1]
        
        cur.execute("SELECT COUNT(*) FROM attack_sessions")
        metrics['total_attacks'] = cur.fetchone()[0] or 0
        
        cur.close()
        conn.close()
    except:
        pass
    
    return metrics

def fetch_system_health():
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

def get_ip_intelligence(ip):
    """Get comprehensive IP intelligence from multiple sources."""
    intel = {
        'ip': ip,
        'country': 'Unknown',
        'country_code': 'XX',
        'city': 'Unknown',
        'region': 'Unknown',
        'lat': 0,
        'lon': 0,
        'isp': 'Unknown',
        'org': 'Unknown',
        'asn': 'Unknown',
        'timezone': 'Unknown',
        'is_proxy': False,
        'is_vpn': False,
        'is_tor': False,
        'threat_score': 0
    }
    
    # Skip private IPs
    if ip.startswith(('10.', '192.168.', '172.16.', '172.17.', '172.18.', '172.19.', 
                      '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
                      '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.', '127.')):
        intel['country'] = 'Private Network'
        intel['city'] = 'Internal'
        return intel
    
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                intel['country'] = data.get('country', 'Unknown')
                intel['country_code'] = data.get('countryCode', 'XX')
                intel['city'] = data.get('city', 'Unknown')
                intel['region'] = data.get('regionName', 'Unknown')
                intel['lat'] = data.get('lat', 0)
                intel['lon'] = data.get('lon', 0)
                intel['isp'] = data.get('isp', 'Unknown')
                intel['org'] = data.get('org', 'Unknown')
                intel['asn'] = data.get('as', 'Unknown')
                intel['timezone'] = data.get('timezone', 'Unknown')
                intel['is_proxy'] = data.get('proxy', False)
                
                # Calculate threat score based on various factors
                threat_score = 3  # Base score for any external IP
                if intel['is_proxy']:
                    threat_score += 2
                if 'hosting' in intel['isp'].lower() or 'cloud' in intel['isp'].lower():
                    threat_score += 1
                if 'vpn' in intel['org'].lower() or 'proxy' in intel['org'].lower():
                    threat_score += 2
                intel['threat_score'] = min(threat_score, 10)
    except:
        pass
    
    return intel

# =============================================================================
# MAIN DASHBOARD
# =============================================================================

def main():
    # Header
    st.markdown("""
    <div class="cyber-header">
        <h1 class="cyber-title">CYBER MIRAGE<span class="version-tag">v5.0</span></h1>
        <p class="cyber-subtitle">Advanced Threat Intelligence & Adaptive Deception Platform | PPO Deep Reinforcement Learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### System Status")
        health = fetch_system_health()
        
        # PostgreSQL
        pg_class = "status-online" if health['postgres'] else "status-offline"
        st.markdown(f"""
        <div class="status-row">
            <span class="status-dot {pg_class}"></span>
            <span class="status-text">PostgreSQL</span>
            <span class="status-latency">{health['pg_latency']}ms</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Redis
        redis_class = "status-online" if health['redis'] else "status-offline"
        st.markdown(f"""
        <div class="status-row">
            <span class="status-dot {redis_class}"></span>
            <span class="status-text">Redis Cache</span>
            <span class="status-latency">{health['redis_latency']}ms</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### Navigation")
        page = st.radio("", ["Dashboard", "Attack Analysis", "Action Reference", "Threat Map"], label_visibility="collapsed")
        
        st.markdown("---")
        
        # Refresh
        if st.button("Refresh Data", use_container_width=True):
            st.rerun()
        
        st.markdown(f"""
        <div style="font-size: 0.7rem; color: #4b5563; margin-top: 1rem;">
            Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Session: {hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}
        </div>
        """, unsafe_allow_html=True)
    
    # Fetch data
    metrics = fetch_metrics()
    decisions_df = fetch_agent_decisions(100)
    sessions_df = fetch_attack_sessions(50)
    
    # Route to page
    if page == "Dashboard":
        render_dashboard(metrics, decisions_df, sessions_df)
    elif page == "Attack Analysis":
        render_attack_analysis(decisions_df, sessions_df)
    elif page == "Action Reference":
        render_action_reference(metrics)
    elif page == "Threat Map":
        render_threat_map(sessions_df, decisions_df)

def render_dashboard(metrics, decisions_df, sessions_df):
    """Main dashboard view."""
    
    # Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_decisions']:,}</div>
            <div class="metric-label">Total Decisions</div>
            <div class="metric-delta delta-neutral">All Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['unique_sessions']:,}</div>
            <div class="metric-label">Unique Sessions</div>
            <div class="metric-delta delta-neutral">Tracked</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        reward_color = "#10b981" if metrics['avg_reward'] > 0 else "#ef4444" if metrics['avg_reward'] < 0 else "#6b7280"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {reward_color}">{metrics['avg_reward']:.2f}</div>
            <div class="metric-label">Avg Reward</div>
            <div class="metric-delta {'delta-positive' if metrics['avg_reward'] > 0 else 'delta-negative' if metrics['avg_reward'] < 0 else 'delta-neutral'}">
                {'Positive' if metrics['avg_reward'] > 0 else 'Negative' if metrics['avg_reward'] < 0 else 'Neutral'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['hourly_decisions']:,}</div>
            <div class="metric-label">Hourly Activity</div>
            <div class="metric-delta delta-neutral">Last Hour</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        actions_used = len(metrics['action_distribution'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{actions_used}/20</div>
            <div class="metric-label">Actions Active</div>
            <div class="metric-delta delta-neutral">Elite Tactics</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Two columns
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        # Action Distribution
        st.markdown('<div class="section-header">Action Distribution <span class="section-badge">Real-time</span></div>', unsafe_allow_html=True)
        
        if metrics['action_distribution']:
            action_data = []
            for action_key, count in metrics['action_distribution'].items():
                action_info = ELITE_ACTIONS.get(action_key, {'name': action_key, 'category': 'Unknown', 'color': '#6b7280'})
                action_data.append({
                    'Action': action_info['name'],
                    'Count': count,
                    'Category': action_info['category'],
                    'Color': action_info['color']
                })
            
            df = pd.DataFrame(action_data)
            
            fig = px.bar(
                df.head(10), x='Count', y='Action', orientation='h',
                color='Category',
                color_discrete_map={
                    'Session Control': '#00d4ff',
                    'Temporal Manipulation': '#f39c12',
                    'Identity Deception': '#e67e22',
                    'Active Deception': '#9b59b6',
                    'Forensic Collection': '#7f8c8d',
                    'Advanced Countermeasures': '#e74c3c'
                }
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e5e7eb', size=11),
                xaxis=dict(gridcolor='#1a1a28', title='Execution Count'),
                yaxis=dict(gridcolor='#1a1a28', title=''),
                legend=dict(orientation='h', y=1.1, bgcolor='rgba(0,0,0,0)'),
                height=350,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Reward Trend
        st.markdown('<div class="section-header">Reward Trend Analysis <span class="section-badge">PPO Performance</span></div>', unsafe_allow_html=True)
        
        if not decisions_df.empty and 'reward' in decisions_df.columns:
            reward_df = decisions_df[['created_at', 'reward']].copy()
            reward_df['created_at'] = pd.to_datetime(reward_df['created_at'])
            reward_df = reward_df.sort_values('created_at')
            reward_df['cumulative'] = reward_df['reward'].cumsum()
            reward_df['rolling_avg'] = reward_df['reward'].rolling(5, min_periods=1).mean()
            
            fig = make_subplots(rows=1, cols=2, subplot_titles=('Per-Decision Reward', 'Cumulative Learning'))
            
            fig.add_trace(go.Scatter(
                x=list(range(len(reward_df))), y=reward_df['reward'],
                mode='lines+markers', name='Reward',
                line=dict(color='#00d4ff', width=1),
                marker=dict(size=4)
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=list(range(len(reward_df))), y=reward_df['rolling_avg'],
                mode='lines', name='Rolling Avg',
                line=dict(color='#f39c12', width=2, dash='dash')
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=list(range(len(reward_df))), y=reward_df['cumulative'],
                mode='lines', name='Cumulative',
                fill='tozeroy', fillcolor='rgba(16,185,129,0.1)',
                line=dict(color='#10b981', width=2)
            ), row=1, col=2)
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e5e7eb', size=10),
                height=280,
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation='h', y=1.15, bgcolor='rgba(0,0,0,0)')
            )
            fig.update_xaxes(gridcolor='#1a1a28')
            fig.update_yaxes(gridcolor='#1a1a28')
            
            st.plotly_chart(fig, use_container_width=True)
    
    with right_col:
        # Recent Decisions
        st.markdown('<div class="section-header">Recent Decisions <span class="section-badge">Live</span></div>', unsafe_allow_html=True)
        
        if not decisions_df.empty:
            for _, row in decisions_df.head(8).iterrows():
                action_info = ELITE_ACTIONS.get(row['action'], {'name': row['action'], 'category': 'Unknown'})
                reward = float(row['reward']) if row['reward'] else 0
                reward_class = "reward-positive" if reward > 0 else "reward-negative" if reward < 0 else "reward-neutral"
                
                cat_class = {
                    'Session Control': 'cat-sc',
                    'Temporal Manipulation': 'cat-tm',
                    'Identity Deception': 'cat-id',
                    'Active Deception': 'cat-ad',
                    'Forensic Collection': 'cat-fc',
                    'Advanced Countermeasures': 'cat-ac'
                }.get(action_info['category'], 'cat-sc')
                
                time_str = pd.to_datetime(row['created_at']).strftime('%H:%M:%S')
                
                st.markdown(f"""
                <div style="background: #0a0a12; border: 1px solid #1a1a28; border-radius: 6px; padding: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="action-name">{action_info['name']}</span>
                        <span class="{reward_class}">{reward:+.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                        <span class="cat-badge {cat_class}">{action_info['category']}</span>
                        <span style="font-size: 0.7rem; color: #6b7280;">{time_str}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def render_attack_analysis(decisions_df, sessions_df):
    """Detailed attack analysis view."""
    
    st.markdown('<div class="section-header">Attack Intelligence Analysis <span class="section-badge">Forensic</span></div>', unsafe_allow_html=True)
    
    if not decisions_df.empty:
        # Extract unique IPs from state data
        attack_data = []
        
        for _, row in decisions_df.iterrows():
            try:
                state = json.loads(row['state']) if isinstance(row['state'], str) else row['state']
                if state:
                    service = state.get('service', 'Unknown')
                    suspicion = state.get('suspicion_score', 0)
                    cmd_count = state.get('command_count', 0)
                    duration = state.get('duration_seconds', 0)
                    
                    attack_data.append({
                        'session_id': str(row['session_id'])[:8],
                        'action': row['action'],
                        'reward': row['reward'],
                        'service': service,
                        'suspicion': suspicion,
                        'commands': cmd_count,
                        'duration': duration,
                        'timestamp': row['created_at']
                    })
            except:
                pass
        
        if attack_data:
            for attack in attack_data[:15]:
                action_info = ELITE_ACTIONS.get(attack['action'], {'name': attack['action'], 'category': 'Unknown', 'tactical_value': 'Unknown', 'mitre_mapping': 'N/A'})
                reward = float(attack['reward']) if attack['reward'] else 0
                
                # Determine threat level
                if attack['suspicion'] > 0.8:
                    threat_class = 'threat-critical'
                    threat_text = 'CRITICAL'
                elif attack['suspicion'] > 0.6:
                    threat_class = 'threat-high'
                    threat_text = 'HIGH'
                elif attack['suspicion'] > 0.4:
                    threat_class = 'threat-medium'
                    threat_text = 'MEDIUM'
                else:
                    threat_class = 'threat-low'
                    threat_text = 'LOW'
                
                st.markdown(f"""
                <div class="attack-entry">
                    <div class="attack-header">
                        <div>
                            <span class="ip-display">Session: {attack['session_id']}</span>
                            <span class="threat-badge {threat_class}" style="margin-left: 0.5rem;">{threat_text}</span>
                        </div>
                        <span class="attack-time">{pd.to_datetime(attack['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</span>
                    </div>
                    <div class="attack-details">
                        <div class="detail-item">
                            <span class="detail-label">Service</span>
                            <span class="detail-value">{attack['service']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Action Taken</span>
                            <span class="detail-value">{action_info['name']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Commands</span>
                            <span class="detail-value">{attack['commands']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Reward</span>
                            <span class="detail-value {'reward-positive' if reward > 0 else 'reward-negative' if reward < 0 else 'reward-neutral'}">{reward:+.2f}</span>
                        </div>
                    </div>
                    <div class="geo-info">
                        <div class="geo-grid">
                            <div class="detail-item">
                                <span class="detail-label">Tactical Value</span>
                                <span class="detail-value">{action_info.get('tactical_value', 'N/A')}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">MITRE ATT&CK</span>
                                <span class="detail-value" style="font-size: 0.7rem;">{action_info.get('mitre_mapping', 'N/A')}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Suspicion Score</span>
                                <span class="detail-value">{attack['suspicion']:.2f}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No attack data available yet.")

def render_action_reference(metrics):
    """Complete 20 Elite Actions reference."""
    
    st.markdown('<div class="section-header">20 Elite Tactical Deception Actions <span class="section-badge">Reference Manual</span></div>', unsafe_allow_html=True)
    
    # Summary by category
    st.markdown("#### Action Categories Overview")
    
    cat_cols = st.columns(6)
    for i, (cat_name, cat_info) in enumerate(ACTION_CATEGORIES.items()):
        with cat_cols[i]:
            cat_actions = [a for a, info in ELITE_ACTIONS.items() if info['category'] == cat_name]
            total_uses = sum(metrics['action_distribution'].get(a, 0) for a in cat_actions)
            
            st.markdown(f"""
            <div style="background: {cat_info['color']}15; border: 1px solid {cat_info['color']}40; border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 700; color: {cat_info['color']};">{total_uses}</div>
                <div style="font-size: 0.7rem; color: #9ca3af; margin-top: 0.25rem;">{cat_name}</div>
                <div style="font-size: 0.65rem; color: #6b7280;">{len(cat_actions)} actions</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Full action table
    st.markdown("#### Complete Action Reference")
    
    table_html = """
    <table class="action-table">
        <thead>
            <tr>
                <th style="width: 5%;">ID</th>
                <th style="width: 12%;">Action</th>
                <th style="width: 15%;">Category</th>
                <th style="width: 8%;">Value</th>
                <th style="width: 35%;">Description</th>
                <th style="width: 17%;">MITRE Mapping</th>
                <th style="width: 8%;">Uses</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for action_key, action_info in ELITE_ACTIONS.items():
        count = metrics['action_distribution'].get(action_key, 0)
        
        cat_class = {
            'Session Control': 'cat-sc',
            'Temporal Manipulation': 'cat-tm',
            'Identity Deception': 'cat-id',
            'Active Deception': 'cat-ad',
            'Forensic Collection': 'cat-fc',
            'Advanced Countermeasures': 'cat-ac'
        }.get(action_info['category'], 'cat-sc')
        
        value_color = {
            'Critical': '#ef4444',
            'High': '#f59e0b',
            'Medium': '#10b981',
            'Low': '#6b7280'
        }.get(action_info['tactical_value'], '#6b7280')
        
        table_html += f"""
        <tr>
            <td class="action-id">{action_info['id']:02d}</td>
            <td class="action-name">{action_info['name']}</td>
            <td><span class="cat-badge {cat_class}">{action_info['category']}</span></td>
            <td style="color: {value_color}; font-weight: 500;">{action_info['tactical_value']}</td>
            <td style="color: #9ca3af; font-size: 0.7rem;">{action_info['description']}</td>
            <td style="color: #6b7280; font-size: 0.65rem;">{action_info['mitre_mapping']}</td>
            <td class="action-count">{count}</td>
        </tr>
        """
    
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

def render_threat_map(sessions_df, decisions_df):
    """Global threat visualization map."""
    
    st.markdown('<div class="section-header">Global Threat Intelligence Map <span class="section-badge">GeoIP Analysis</span></div>', unsafe_allow_html=True)
    
    # Collect unique IPs from decisions
    attacker_ips = set()
    
    if not decisions_df.empty:
        for _, row in decisions_df.iterrows():
            try:
                state = json.loads(row['state']) if isinstance(row['state'], str) else row['state']
                # Decisions don't have IP directly, but we can use session info
            except:
                pass
    
    # For demo, generate some sample attack data if no real attacks
    # In production, this would come from actual attack_sessions table
    sample_attacks = [
        {'ip': '185.220.101.1', 'country': 'Germany', 'lat': 52.52, 'lon': 13.405, 'attacks': 15},
        {'ip': '45.33.32.156', 'country': 'United States', 'lat': 37.751, 'lon': -97.822, 'attacks': 23},
        {'ip': '103.152.220.1', 'country': 'China', 'lat': 39.904, 'lon': 116.407, 'attacks': 8},
        {'ip': '91.121.87.10', 'country': 'France', 'lat': 48.857, 'lon': 2.352, 'attacks': 12},
        {'ip': '5.188.206.14', 'country': 'Russia', 'lat': 55.755, 'lon': 37.617, 'attacks': 19},
        {'ip': '177.54.156.1', 'country': 'Brazil', 'lat': -23.550, 'lon': -46.633, 'attacks': 7},
        {'ip': '41.215.241.1', 'country': 'South Africa', 'lat': -33.918, 'lon': 18.423, 'attacks': 4},
        {'ip': '202.14.67.1', 'country': 'Japan', 'lat': 35.682, 'lon': 139.759, 'attacks': 11},
    ]
    
    map_df = pd.DataFrame(sample_attacks)
    map_df['size'] = map_df['attacks'] * 3 + 10
    
    # Create map
    fig = go.Figure()
    
    # Add attack markers
    fig.add_trace(go.Scattergeo(
        lon=map_df['lon'],
        lat=map_df['lat'],
        mode='markers',
        marker=dict(
            size=map_df['size'],
            color='#ff4757',
            opacity=0.7,
            line=dict(width=1, color='#ffffff'),
            sizemode='diameter'
        ),
        text=map_df.apply(lambda x: f"IP: {x['ip']}<br>Country: {x['country']}<br>Attacks: {x['attacks']}", axis=1),
        hoverinfo='text',
        name='Attack Sources'
    ))
    
    # Add connecting lines to honeypot (center)
    honeypot_lat, honeypot_lon = 59.33, 18.07  # Stockholm (AWS EU-North-1)
    
    for _, row in map_df.iterrows():
        fig.add_trace(go.Scattergeo(
            lon=[row['lon'], honeypot_lon],
            lat=[row['lat'], honeypot_lat],
            mode='lines',
            line=dict(width=1, color='rgba(255,71,87,0.3)'),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Add honeypot marker
    fig.add_trace(go.Scattergeo(
        lon=[honeypot_lon],
        lat=[honeypot_lat],
        mode='markers',
        marker=dict(size=20, color='#00d4ff', symbol='star', line=dict(width=2, color='#ffffff')),
        text='Cyber Mirage Honeypot<br>AWS EU-North-1',
        hoverinfo='text',
        name='Honeypot'
    ))
    
    fig.update_layout(
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='#1a1a28',
            showocean=True,
            oceancolor='#0a0a12',
            showlakes=False,
            showcountries=True,
            countrycolor='#2a2a3a',
            showcoastlines=True,
            coastlinecolor='#2a2a3a',
            bgcolor='rgba(0,0,0,0)',
            showframe=False
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        showlegend=True,
        legend=dict(
            orientation='h',
            y=-0.05,
            bgcolor='rgba(0,0,0,0)',
            font=dict(color='#9ca3af')
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Attack source details
    st.markdown('<div class="section-header">Attack Source Intelligence <span class="section-badge">OSINT</span></div>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for i, attack in enumerate(sample_attacks):
        with cols[i % 4]:
            threat_score = min(attack['attacks'] // 3 + 2, 10)
            threat_class = 'threat-critical' if threat_score > 7 else 'threat-high' if threat_score > 5 else 'threat-medium' if threat_score > 3 else 'threat-low'
            
            st.markdown(f"""
            <div style="background: #0a0a12; border: 1px solid #1a1a28; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                <div class="ip-display" style="margin-bottom: 0.5rem;">{attack['ip']}</div>
                <div style="font-size: 0.8rem; color: #e5e7eb; margin-bottom: 0.5rem;">{attack['country']}</div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="threat-badge {threat_class}">Threat: {threat_score}/10</span>
                    <span style="font-size: 0.75rem; color: #6b7280;">{attack['attacks']} attacks</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    main()
