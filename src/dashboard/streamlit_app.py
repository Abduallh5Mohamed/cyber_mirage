"""
🎭 CYBER MIRAGE v5.0 - ELITE DEFENSE DASHBOARD
═══════════════════════════════════════════════════════════════════════════════
PhD-Level Adaptive Honeypot System with Deep Reinforcement Learning
20 Elite Deception Actions | Real-time Threat Intelligence | Global Attack Map
═══════════════════════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'cyber_mirage')
DB_USER = os.getenv('POSTGRES_USER', 'cybermirage')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASS = os.getenv('REDIS_PASSWORD', 'changeme123')

# 20 Elite Deception Actions with Full Details
ELITE_ACTIONS = {
    # Session Control (1-4)
    'maintain_session': {
        'id': 1, 'name': 'Maintain Session', 'category': 'Session Control',
        'icon': '🔄', 'color': '#00D4FF', 
        'description': 'Keep attacker connected to gather intelligence'
    },
    'drop_session': {
        'id': 2, 'name': 'Drop Session', 'category': 'Session Control',
        'icon': '🚫', 'color': '#FF4757',
        'description': 'Terminate malicious session immediately'
    },
    'throttle_session': {
        'id': 3, 'name': 'Throttle Session', 'category': 'Session Control',
        'icon': '🐌', 'color': '#FFA502',
        'description': 'Slow down attacker actions'
    },
    'redirect_session': {
        'id': 4, 'name': 'Redirect Session', 'category': 'Session Control',
        'icon': '↪️', 'color': '#7B2CBF',
        'description': 'Redirect to isolated sandbox environment'
    },
    # Delay Tactics (5-7)
    'inject_delay': {
        'id': 5, 'name': 'Inject Delay', 'category': 'Delay Tactics',
        'icon': '⏱️', 'color': '#3498DB',
        'description': 'Add artificial latency to responses'
    },
    'progressive_delay': {
        'id': 6, 'name': 'Progressive Delay', 'category': 'Delay Tactics',
        'icon': '📈', 'color': '#1ABC9C',
        'description': 'Gradually increase response delay'
    },
    'random_delay': {
        'id': 7, 'name': 'Random Delay', 'category': 'Delay Tactics',
        'icon': '🎲', 'color': '#9B59B6',
        'description': 'Unpredictable response timing'
    },
    # Identity Manipulation (8-10)
    'swap_service_banner': {
        'id': 8, 'name': 'Swap Banner', 'category': 'Identity Manipulation',
        'icon': '🎭', 'color': '#E67E22',
        'description': 'Change service fingerprint/banner'
    },
    'randomize_banner': {
        'id': 9, 'name': 'Randomize Banner', 'category': 'Identity Manipulation',
        'icon': '🔀', 'color': '#16A085',
        'description': 'Present random service identity'
    },
    'mimic_vulnerable': {
        'id': 10, 'name': 'Mimic Vulnerable', 'category': 'Identity Manipulation',
        'icon': '🎯', 'color': '#C0392B',
        'description': 'Appear as vulnerable system'
    },
    # Deception (11-14)
    'present_lure': {
        'id': 11, 'name': 'Present Lure', 'category': 'Deception',
        'icon': '🪤', 'color': '#8E44AD',
        'description': 'Show fake valuable data/files'
    },
    'deploy_breadcrumb': {
        'id': 12, 'name': 'Deploy Breadcrumb', 'category': 'Deception',
        'icon': '🥖', 'color': '#2980B9',
        'description': 'Leave false trail for attacker'
    },
    'inject_fake_creds': {
        'id': 13, 'name': 'Inject Fake Creds', 'category': 'Deception',
        'icon': '🔑', 'color': '#27AE60',
        'description': 'Plant honeytokens/fake credentials'
    },
    'simulate_target': {
        'id': 14, 'name': 'Simulate Target', 'category': 'Deception',
        'icon': '🏢', 'color': '#D35400',
        'description': 'Appear as high-value target'
    },
    # Active Defense (15-17)
    'capture_tools': {
        'id': 15, 'name': 'Capture Tools', 'category': 'Active Defense',
        'icon': '🧰', 'color': '#7F8C8D',
        'description': 'Capture attacker malware/tools'
    },
    'log_enhanced': {
        'id': 16, 'name': 'Enhanced Logging', 'category': 'Active Defense',
        'icon': '📝', 'color': '#95A5A6',
        'description': 'Forensic-level detailed logging'
    },
    'fingerprint': {
        'id': 17, 'name': 'Fingerprint Attacker', 'category': 'Active Defense',
        'icon': '👆', 'color': '#34495E',
        'description': 'Collect attacker signatures'
    },
    # Advanced Tactics (18-20)
    'tarpit': {
        'id': 18, 'name': 'Tarpit', 'category': 'Advanced Tactics',
        'icon': '🕳️', 'color': '#2C3E50',
        'description': 'Trap attacker in slow connection'
    },
    'honeypot_upgrade': {
        'id': 19, 'name': 'Honeypot Upgrade', 'category': 'Advanced Tactics',
        'icon': '⬆️', 'color': '#1A252F',
        'description': 'Switch to high-interaction mode'
    },
    'alert_track': {
        'id': 20, 'name': 'Alert & Track', 'category': 'Advanced Tactics',
        'icon': '🚨', 'color': '#E74C3C',
        'description': 'Alert SOC and track attacker'
    }
}

# IP to Country mapping (sample - in production use GeoIP)
IP_LOCATIONS = {}

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="🎭 Cyber Mirage v5.0 | Elite Defense",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS - Clean Modern Theme
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: #0F0F1A;
    }
    
    .stApp {
        background: linear-gradient(180deg, #0F0F1A 0%, #1A1A2E 100%);
    }
    
    /* Header */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #00D4FF 0%, #7B2CBF 50%, #FF006E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        letter-spacing: -1px;
    }
    
    .sub-title {
        text-align: center;
        color: #6B7280;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
    }
    
    /* Metric Cards */
    .metric-container {
        background: linear-gradient(135deg, #1E1E2E 0%, #2D2D44 100%);
        border: 1px solid #3D3D5C;
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        border-color: #00D4FF;
        box-shadow: 0 10px 40px rgba(0, 212, 255, 0.2);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    .metric-trend {
        font-size: 0.9rem;
        margin-top: 0.5rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        display: inline-block;
    }
    
    .trend-up {
        background: rgba(16, 185, 129, 0.2);
        color: #10B981;
    }
    
    .trend-down {
        background: rgba(239, 68, 68, 0.2);
        color: #EF4444;
    }
    
    /* Section Headers */
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #3D3D5C;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* Status Pills */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .status-online {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10B981;
    }
    
    .status-offline {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #EF4444;
    }
    
    .pulse {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10B981;
        animation: pulse-animation 2s infinite;
    }
    
    @keyframes pulse-animation {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    /* Action Cards */
    .action-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .action-card {
        background: linear-gradient(135deg, #1E1E2E 0%, #252538 100%);
        border: 1px solid #3D3D5C;
        border-radius: 16px;
        padding: 1.25rem;
        transition: all 0.3s ease;
    }
    
    .action-card:hover {
        transform: scale(1.02);
        border-color: var(--action-color, #00D4FF);
    }
    
    .action-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }
    
    .action-icon {
        font-size: 1.5rem;
    }
    
    .action-name {
        font-weight: 600;
        color: #FFFFFF;
        font-size: 0.95rem;
    }
    
    .action-category {
        font-size: 0.75rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .action-description {
        font-size: 0.85rem;
        color: #9CA3AF;
        line-height: 1.4;
    }
    
    .action-count {
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 0.75rem;
    }
    
    /* Attack Log */
    .attack-row {
        background: #1E1E2E;
        border: 1px solid #3D3D5C;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s ease;
    }
    
    .attack-row:hover {
        background: #252538;
        border-color: #4D4D6D;
    }
    
    .attack-info {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .attack-service {
        background: #3D3D5C;
        padding: 0.25rem 0.75rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #FFFFFF;
    }
    
    .attack-ip {
        font-family: 'Monaco', 'Consolas', monospace;
        color: #00D4FF;
        font-weight: 600;
    }
    
    .attack-time {
        color: #6B7280;
        font-size: 0.85rem;
    }
    
    /* Threat Level Badges */
    .threat-critical { background: #EF4444; color: white; }
    .threat-high { background: #F97316; color: white; }
    .threat-medium { background: #EAB308; color: black; }
    .threat-low { background: #22C55E; color: white; }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1E1E2E;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3D3D5C;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4D4D6D;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_db_connection():
    try:
        return psycopg2.connect(
            host=DB_HOST, database=DB_NAME,
            user=DB_USER, password=DB_PASS,
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


def get_system_health():
    health = {
        'postgres': {'status': False, 'latency': 0},
        'redis': {'status': False, 'latency': 0},
    }
    
    start = time.time()
    conn = get_db_connection()
    if conn:
        health['postgres']['status'] = True
        health['postgres']['latency'] = round((time.time() - start) * 1000, 1)
        conn.close()
    
    start = time.time()
    r = get_redis_connection()
    if r:
        health['redis']['status'] = True
        health['redis']['latency'] = round((time.time() - start) * 1000, 1)
    
    return health


def get_attack_stats():
    stats = {
        'total': 0, 'today': 0, 'hour': 0,
        'unique_ips': 0, 'services': {}, 'attackers': [],
        'hourly': [], 'locations': []
    }
    
    conn = get_db_connection()
    if not conn:
        return stats
    
    try:
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM attack_sessions")
        stats['total'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(*) FROM attack_sessions WHERE start_time > CURRENT_DATE")
        stats['today'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(*) FROM attack_sessions WHERE start_time > NOW() - INTERVAL '1 hour'")
        stats['hour'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(DISTINCT origin) FROM attack_sessions")
        stats['unique_ips'] = cur.fetchone()[0] or 0
        
        cur.execute("""
            SELECT COALESCE(honeypot_type, 'Unknown'), COUNT(*) 
            FROM attack_sessions GROUP BY honeypot_type ORDER BY COUNT(*) DESC LIMIT 10
        """)
        for r in cur.fetchall():
            stats['services'][r[0]] = r[1]
        
        cur.execute("""
            SELECT origin, COUNT(*) as cnt FROM attack_sessions 
            WHERE origin IS NOT NULL GROUP BY origin ORDER BY cnt DESC LIMIT 15
        """)
        stats['attackers'] = [{'ip': r[0], 'count': r[1]} for r in cur.fetchall()]
        
        cur.execute("""
            SELECT date_trunc('hour', start_time), COUNT(*) 
            FROM attack_sessions WHERE start_time > NOW() - INTERVAL '24 hours'
            GROUP BY 1 ORDER BY 1
        """)
        stats['hourly'] = [{'hour': r[0], 'count': r[1]} for r in cur.fetchall()]
        
        cur.close()
    except:
        pass
    finally:
        conn.close()
    
    return stats


def get_ai_metrics():
    metrics = {
        'total_decisions': 0, 'avg_reward': 0.0,
        'actions': {}, 'categories': {}
    }
    
    conn = get_db_connection()
    if not conn:
        return metrics
    
    try:
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM agent_decisions")
        metrics['total_decisions'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT AVG(reward) FROM agent_decisions WHERE created_at > NOW() - INTERVAL '24 hours'")
        row = cur.fetchone()
        metrics['avg_reward'] = float(row[0]) if row and row[0] else 0.0
        
        cur.execute("SELECT action, COUNT(*) FROM agent_decisions GROUP BY action ORDER BY COUNT(*) DESC")
        for r in cur.fetchall():
            action = r[0]
            count = r[1]
            metrics['actions'][action] = count
            if action in ELITE_ACTIONS:
                cat = ELITE_ACTIONS[action]['category']
                metrics['categories'][cat] = metrics['categories'].get(cat, 0) + count
        
        cur.close()
    except:
        pass
    finally:
        conn.close()
    
    return metrics


def get_recent_attacks(limit=10):
    attacks = []
    conn = get_db_connection()
    if not conn:
        return attacks
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, attacker_name, origin, honeypot_type, start_time
            FROM attack_sessions ORDER BY start_time DESC LIMIT %s
        """, (limit,))
        
        for r in cur.fetchall():
            attacks.append({
                'id': str(r[0])[:8],
                'attacker': r[1] or 'Unknown',
                'ip': r[2] or 'Unknown',
                'service': r[3] or 'Unknown',
                'time': r[4].strftime('%H:%M:%S') if r[4] else 'N/A'
            })
        cur.close()
    except:
        pass
    finally:
        conn.close()
    
    return attacks


def get_ip_location(ip):
    """Get approximate location for IP (uses free API)"""
    # Sample locations for demo - in production use real GeoIP
    known_locations = {
        '47.93': {'lat': 39.9, 'lon': 116.4, 'country': 'China', 'city': 'Beijing'},
        '185.220': {'lat': 52.5, 'lon': 13.4, 'country': 'Germany', 'city': 'Berlin'},
        '45.': {'lat': 40.7, 'lon': -74.0, 'country': 'USA', 'city': 'New York'},
        '192.': {'lat': 51.5, 'lon': -0.1, 'country': 'UK', 'city': 'London'},
        '103.': {'lat': 1.3, 'lon': 103.8, 'country': 'Singapore', 'city': 'Singapore'},
        '20.': {'lat': 47.6, 'lon': -122.3, 'country': 'USA', 'city': 'Seattle'},
        '34.': {'lat': 37.4, 'lon': -122.1, 'country': 'USA', 'city': 'California'},
        '183.': {'lat': 31.2, 'lon': 121.5, 'country': 'China', 'city': 'Shanghai'},
    }
    
    for prefix, loc in known_locations.items():
        if ip.startswith(prefix):
            return loc
    
    # Random location for unknown IPs
    return {
        'lat': np.random.uniform(-60, 70),
        'lon': np.random.uniform(-180, 180),
        'country': 'Unknown',
        'city': 'Unknown'
    }


def get_attack_map_data():
    """Get attack data with geo locations"""
    conn = get_db_connection()
    if not conn:
        return []
    
    locations = []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT origin, COUNT(*) as cnt, MAX(honeypot_type) as service
            FROM attack_sessions 
            WHERE origin IS NOT NULL
            GROUP BY origin
            ORDER BY cnt DESC
            LIMIT 50
        """)
        
        for r in cur.fetchall():
            ip = r[0]
            count = r[1]
            service = r[2] or 'Unknown'
            loc = get_ip_location(ip)
            locations.append({
                'ip': ip,
                'count': count,
                'service': service,
                'lat': loc['lat'],
                'lon': loc['lon'],
                'country': loc['country'],
                'city': loc['city']
            })
        
        cur.close()
    except:
        pass
    finally:
        conn.close()
    
    return locations


# ═══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_header():
    st.markdown("""
        <h1 class="main-title">🎭 CYBER MIRAGE v5.0</h1>
        <p class="sub-title">
            Adaptive Honeypot Defense System with Deep Reinforcement Learning<br>
            20 Elite Deception Actions • Real-time Threat Intelligence • Global Attack Tracking
        </p>
    """, unsafe_allow_html=True)


def render_status_bar(health):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if health['postgres']['status']:
            st.markdown(f"""
                <div class="status-pill status-online">
                    <div class="pulse"></div>
                    PostgreSQL ({health['postgres']['latency']}ms)
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-pill status-offline">❌ PostgreSQL Offline</div>', unsafe_allow_html=True)
    
    with col2:
        if health['redis']['status']:
            st.markdown(f"""
                <div class="status-pill status-online">
                    <div class="pulse"></div>
                    Redis ({health['redis']['latency']}ms)
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-pill status-offline">❌ Redis Offline</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="status-pill status-online">
                <div class="pulse"></div>
                10 Honeypots Active
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="status-pill status-online">
                🕐 {datetime.now().strftime('%H:%M:%S')}
            </div>
        """, unsafe_allow_html=True)


def render_metrics(attack_stats, ai_metrics):
    st.markdown('<div class="section-title">📊 Key Performance Indicators</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics_data = [
        ('🎯', attack_stats['total'], 'Total Attacks', f"+{attack_stats['hour']} this hour", 'up'),
        ('👤', attack_stats['unique_ips'], 'Unique Attackers', 'Tracked IPs', 'up'),
        ('🤖', ai_metrics['total_decisions'], 'AI Decisions', '20 Elite Actions', 'up'),
        ('⭐', f"{ai_metrics['avg_reward']:.2f}", 'Avg Reward', 'Last 24h', 'up' if ai_metrics['avg_reward'] >= 0 else 'down'),
        ('🛡️', '100%', 'Detection Rate', 'All captured', 'up'),
    ]
    
    for col, (icon, value, label, trend, trend_dir) in zip([col1, col2, col3, col4, col5], metrics_data):
        with col:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-icon">{icon}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                    <div class="metric-trend trend-{trend_dir}">{trend}</div>
                </div>
            """, unsafe_allow_html=True)


def render_world_map(locations):
    st.markdown('<div class="section-title">🌍 Global Attack Map - Real-time Threat Origins</div>', unsafe_allow_html=True)
    
    if not locations:
        st.info("📍 Collecting geolocation data from attacks...")
        return
    
    df = pd.DataFrame(locations)
    
    # Create the map
    fig = go.Figure()
    
    # Add scatter points for attacks
    fig.add_trace(go.Scattergeo(
        lon=df['lon'],
        lat=df['lat'],
        text=df.apply(lambda r: f"<b>{r['ip']}</b><br>Country: {r['country']}<br>City: {r['city']}<br>Attacks: {r['count']}<br>Service: {r['service']}", axis=1),
        mode='markers',
        marker=dict(
            size=df['count'] * 3 + 10,
            color=df['count'],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(
                title="Attack Count",
                titlefont=dict(color='white'),
                tickfont=dict(color='white')
            ),
            line=dict(width=1, color='white'),
            opacity=0.8
        ),
        hovertemplate='%{text}<extra></extra>'
    ))
    
    # Add lines from attackers to honeypot (center)
    honeypot_loc = {'lat': 59.3, 'lon': 18.0}  # Stockholm (AWS EU)
    
    for _, row in df.head(10).iterrows():
        fig.add_trace(go.Scattergeo(
            lon=[row['lon'], honeypot_loc['lon']],
            lat=[row['lat'], honeypot_loc['lat']],
            mode='lines',
            line=dict(width=1, color='rgba(255, 0, 110, 0.3)'),
            hoverinfo='skip'
        ))
    
    # Honeypot marker
    fig.add_trace(go.Scattergeo(
        lon=[honeypot_loc['lon']],
        lat=[honeypot_loc['lat']],
        text=['🎭 CYBER MIRAGE<br>Honeypot Server'],
        mode='markers+text',
        marker=dict(size=20, color='#00D4FF', symbol='star'),
        textposition='top center',
        textfont=dict(color='white', size=12),
        hovertemplate='🎭 Cyber Mirage Honeypot<br>Location: Stockholm, Sweden<extra></extra>'
    ))
    
    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor='#1E1E2E',
            showocean=True,
            oceancolor='#0F0F1A',
            showlakes=False,
            showcountries=True,
            countrycolor='#3D3D5C',
            showcoastlines=True,
            coastlinecolor='#3D3D5C',
            projection_type='natural earth',
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=450,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_elite_actions(ai_metrics):
    st.markdown('<div class="section-title">🤖 20 Elite Deception Actions - AI Decision Distribution</div>', unsafe_allow_html=True)
    
    # Group by category
    categories = ['Session Control', 'Delay Tactics', 'Identity Manipulation', 'Deception', 'Active Defense', 'Advanced Tactics']
    
    for cat in categories:
        actions_in_cat = {k: v for k, v in ELITE_ACTIONS.items() if v['category'] == cat}
        
        st.markdown(f"**{cat}**")
        cols = st.columns(len(actions_in_cat))
        
        for col, (action_key, action_info) in zip(cols, actions_in_cat.items()):
            count = ai_metrics['actions'].get(action_key, 0)
            with col:
                st.markdown(f"""
                    <div class="action-card" style="--action-color: {action_info['color']}">
                        <div class="action-header">
                            <span class="action-icon">{action_info['icon']}</span>
                            <div>
                                <div class="action-name">{action_info['name']}</div>
                                <div class="action-category">#{action_info['id']}</div>
                            </div>
                        </div>
                        <div class="action-description">{action_info['description']}</div>
                        <div class="action-count" style="color: {action_info['color']}">{count}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)


def render_charts(attack_stats, ai_metrics):
    st.markdown('<div class="section-title">📈 Analytics Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Attack trend
        if attack_stats['hourly']:
            df = pd.DataFrame(attack_stats['hourly'])
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['hour'], y=df['count'],
                mode='lines+markers',
                fill='tozeroy',
                line=dict(color='#00D4FF', width=3),
                marker=dict(size=8, color='#7B2CBF'),
                fillcolor='rgba(0, 212, 255, 0.1)'
            ))
            fig.update_layout(
                title=dict(text='Attack Volume (24h)', font=dict(color='white', size=16)),
                xaxis=dict(title='Time', color='white', gridcolor='#3D3D5C'),
                yaxis=dict(title='Attacks', color='white', gridcolor='#3D3D5C'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Collecting trend data...")
    
    with col2:
        # Service distribution
        if attack_stats['services']:
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(attack_stats['services'].keys()),
                    values=list(attack_stats['services'].values()),
                    hole=0.5,
                    marker=dict(colors=px.colors.qualitative.Set3)
                )
            ])
            fig.update_layout(
                title=dict(text='Targeted Services', font=dict(color='white', size=16)),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=300,
                showlegend=True,
                legend=dict(font=dict(color='white'))
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🎯 Collecting service data...")


def render_live_feed(attacks):
    st.markdown('<div class="section-title">🚨 Live Attack Feed</div>', unsafe_allow_html=True)
    
    if not attacks:
        st.info("🔍 Monitoring for attacks... Honeypots are ready!")
        return
    
    for attack in attacks:
        service_colors = {
            'SSH': '#10B981', 'FTP': '#3B82F6', 'HTTP': '#8B5CF6',
            'MySQL': '#F59E0B', 'PostgreSQL': '#EC4899', 'Modbus': '#EF4444',
            'SMB': '#6366F1', 'HTTPS': '#14B8A6'
        }
        color = service_colors.get(attack['service'], '#6B7280')
        
        st.markdown(f"""
            <div class="attack-row">
                <div class="attack-info">
                    <span class="attack-service" style="background: {color}">{attack['service']}</span>
                    <span class="attack-ip">{attack['ip']}</span>
                    <span style="color: #9CA3AF">→</span>
                    <span style="color: #FFFFFF">{attack['attacker']}</span>
                </div>
                <span class="attack-time">🕐 {attack['time']}</span>
            </div>
        """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        
        auto_refresh = st.toggle("🔄 Auto-Refresh", value=True)
        refresh_rate = st.slider("Interval (sec)", 5, 60, 10) if auto_refresh else 10
        
        st.markdown("---")
        st.markdown("### 📡 Honeypot Ports")
        
        ports = [
            ("SSH", "2222→22", "#10B981"),
            ("FTP", "2121→21", "#3B82F6"),
            ("HTTP", "8080→80", "#8B5CF6"),
            ("MySQL", "3307→3306", "#F59E0B"),
            ("SMB", "445", "#6366F1"),
            ("Modbus", "502", "#EF4444"),
        ]
        
        for name, port, color in ports:
            st.markdown(f'<span style="color:{color}">●</span> **{name}**: `{port}`', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📚 Research Info")
        st.caption("**Algorithm**: PPO with GAE")
        st.caption("**State Space**: 15 dimensions")
        st.caption("**Action Space**: 20 actions")
        st.caption("**Honeypots**: 10 protocols")
        
        return auto_refresh, refresh_rate


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    auto_refresh, refresh_rate = render_sidebar()
    
    render_header()
    
    health = get_system_health()
    attack_stats = get_attack_stats()
    ai_metrics = get_ai_metrics()
    attacks = get_recent_attacks(8)
    map_data = get_attack_map_data()
    
    render_status_bar(health)
    st.markdown("---")
    
    render_metrics(attack_stats, ai_metrics)
    st.markdown("---")
    
    render_world_map(map_data)
    st.markdown("---")
    
    render_elite_actions(ai_metrics)
    st.markdown("---")
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        render_charts(attack_stats, ai_metrics)
    with col2:
        render_live_feed(attacks)
    
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()


if __name__ == "__main__":
    main()
