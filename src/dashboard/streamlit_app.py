"""
CYBER MIRAGE v5.0 - Advanced Deception Intelligence Platform
=============================================================
PhD-Level Adaptive Honeypot System with Deep Reinforcement Learning
20 Elite Deception Actions | Real-time Threat Intelligence | Global Attack Mapping
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

# 20 Elite Deception Actions - Academic Reference
ELITE_ACTIONS = {
    'maintain_session': {'id': 1, 'name': 'Maintain Session', 'category': 'Session Control', 'color': '#00D4FF'},
    'drop_session': {'id': 2, 'name': 'Drop Session', 'category': 'Session Control', 'color': '#FF4757'},
    'throttle_session': {'id': 3, 'name': 'Throttle Session', 'category': 'Session Control', 'color': '#FFA502'},
    'redirect_session': {'id': 4, 'name': 'Redirect Session', 'category': 'Session Control', 'color': '#7B2CBF'},
    'inject_delay': {'id': 5, 'name': 'Inject Delay', 'category': 'Delay Tactics', 'color': '#3498DB'},
    'progressive_delay': {'id': 6, 'name': 'Progressive Delay', 'category': 'Delay Tactics', 'color': '#1ABC9C'},
    'random_delay': {'id': 7, 'name': 'Random Delay', 'category': 'Delay Tactics', 'color': '#9B59B6'},
    'swap_service_banner': {'id': 8, 'name': 'Swap Banner', 'category': 'Identity Manipulation', 'color': '#E67E22'},
    'randomize_banner': {'id': 9, 'name': 'Randomize Banner', 'category': 'Identity Manipulation', 'color': '#16A085'},
    'mimic_vulnerable': {'id': 10, 'name': 'Mimic Vulnerable', 'category': 'Identity Manipulation', 'color': '#C0392B'},
    'present_lure': {'id': 11, 'name': 'Present Lure', 'category': 'Deception', 'color': '#8E44AD'},
    'deploy_breadcrumb': {'id': 12, 'name': 'Deploy Breadcrumb', 'category': 'Deception', 'color': '#2980B9'},
    'inject_fake_creds': {'id': 13, 'name': 'Inject Fake Credentials', 'category': 'Deception', 'color': '#27AE60'},
    'simulate_target': {'id': 14, 'name': 'Simulate Target', 'category': 'Deception', 'color': '#D35400'},
    'capture_tools': {'id': 15, 'name': 'Capture Tools', 'category': 'Active Defense', 'color': '#7F8C8D'},
    'log_enhanced': {'id': 16, 'name': 'Enhanced Logging', 'category': 'Active Defense', 'color': '#95A5A6'},
    'fingerprint': {'id': 17, 'name': 'Fingerprint Attacker', 'category': 'Active Defense', 'color': '#34495E'},
    'tarpit': {'id': 18, 'name': 'Tarpit', 'category': 'Advanced Tactics', 'color': '#2C3E50'},
    'honeypot_upgrade': {'id': 19, 'name': 'Honeypot Upgrade', 'category': 'Advanced Tactics', 'color': '#1A252F'},
    'alert_track': {'id': 20, 'name': 'Alert and Track', 'category': 'Advanced Tactics', 'color': '#E74C3C'}
}

ACTION_CATEGORIES = {
    'Session Control': {'color': '#00D4FF', 'actions': [1, 2, 3, 4]},
    'Delay Tactics': {'color': '#F39C12', 'actions': [5, 6, 7]},
    'Identity Manipulation': {'color': '#E67E22', 'actions': [8, 9, 10]},
    'Deception': {'color': '#9B59B6', 'actions': [11, 12, 13, 14]},
    'Active Defense': {'color': '#7F8C8D', 'actions': [15, 16, 17]},
    'Advanced Tactics': {'color': '#E74C3C', 'actions': [18, 19, 20]}
}

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Cyber Mirage v5.0 | Defense Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# PROFESSIONAL CSS - No Emojis, Clean Academic Design
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    
    .main { background: #0a0a0f; }
    .stApp { background: linear-gradient(180deg, #0a0a0f 0%, #0f0f1a 100%); }
    
    /* Header */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 1px solid #1a1a2e;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-top: 0.5rem;
    }
    
    .version-badge {
        display: inline-block;
        background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
        vertical-align: middle;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #12121a;
        border: 1px solid #1f1f2e;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    .metric-trend {
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    .trend-positive { color: #10b981; }
    .trend-negative { color: #ef4444; }
    .trend-neutral { color: #6b7280; }
    
    /* Section Headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #ffffff;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #1f1f2e;
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.375rem 0.75rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-online {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10b981;
    }
    
    .status-offline {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #ef4444;
    }
    
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: currentColor;
    }
    
    /* Data Table */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }
    
    .data-table th {
        background: #1a1a2e;
        color: #9ca3af;
        padding: 0.75rem 1rem;
        text-align: left;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.5px;
    }
    
    .data-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #1f1f2e;
        color: #e5e7eb;
    }
    
    .data-table tr:hover td {
        background: #12121a;
    }
    
    /* Action Reference Table */
    .action-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .action-table th {
        background: #0f0f1a;
        color: #9ca3af;
        padding: 0.75rem;
        text-align: left;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 1px solid #1f1f2e;
    }
    
    .action-table td {
        padding: 0.5rem 0.75rem;
        border-bottom: 1px solid #1a1a2e;
        font-size: 0.8rem;
    }
    
    .action-id {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: #00d4ff;
    }
    
    .action-name {
        color: #ffffff;
        font-weight: 500;
    }
    
    .action-category-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 3px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    /* Category Colors */
    .cat-session { background: rgba(0, 212, 255, 0.15); color: #00d4ff; }
    .cat-delay { background: rgba(243, 156, 18, 0.15); color: #f39c12; }
    .cat-identity { background: rgba(230, 126, 34, 0.15); color: #e67e22; }
    .cat-deception { background: rgba(155, 89, 182, 0.15); color: #9b59b6; }
    .cat-defense { background: rgba(127, 140, 141, 0.15); color: #7f8c8d; }
    .cat-advanced { background: rgba(231, 76, 60, 0.15); color: #e74c3c; }
    
    /* IP Address Styling */
    .ip-address {
        font-family: 'JetBrains Mono', monospace;
        color: #00d4ff;
        font-weight: 500;
    }
    
    /* Timestamp */
    .timestamp {
        font-family: 'JetBrains Mono', monospace;
        color: #6b7280;
        font-size: 0.8rem;
    }
    
    /* Service Badge */
    .service-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        background: #1f1f2e;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #e5e7eb;
    }
    
    /* Reward Value */
    .reward-positive { color: #10b981; font-weight: 600; }
    .reward-negative { color: #ef4444; font-weight: 600; }
    .reward-neutral { color: #6b7280; }
    
    /* Chart Container */
    .chart-container {
        background: #12121a;
        border: 1px solid #1f1f2e;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar */
    .css-1d391kg { background: #0a0a0f; }
    
    /* Plotly Chart Background */
    .js-plotly-plot .plotly .main-svg { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATABASE CONNECTIONS
# =============================================================================

@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS,
            connect_timeout=5
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

@st.cache_resource
def get_redis_connection():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, decode_responses=True)
        r.ping()
        return r
    except Exception as e:
        return None

# =============================================================================
# DATA FETCHING FUNCTIONS
# =============================================================================

def fetch_agent_decisions(limit=100):
    """Fetch recent agent decisions with rewards."""
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
        
        df = pd.DataFrame(rows, columns=['id', 'session_id', 'action', 'strategy', 'reward', 'state', 'created_at'])
        return df
    except Exception as e:
        return pd.DataFrame()

def fetch_attack_sessions(limit=50):
    """Fetch recent attack sessions."""
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
        
        df = pd.DataFrame(rows, columns=[
            'id', 'source_ip', 'target_port', 'service_type', 'attack_type', 
            'threat_level', 'country', 'city', 'session_start', 'session_end'
        ])
        return df
    except Exception as e:
        return pd.DataFrame()

def fetch_ppo_metrics():
    """Fetch PPO agent performance metrics."""
    metrics = {
        'total_decisions': 0,
        'unique_sessions': 0,
        'avg_reward': 0.0,
        'max_reward': 0.0,
        'min_reward': 0.0,
        'action_distribution': {},
        'hourly_decisions': 0
    }
    
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        # Total decisions
        cur.execute("SELECT COUNT(*) FROM agent_decisions")
        row = cur.fetchone()
        metrics['total_decisions'] = row[0] if row else 0
        
        # Unique sessions
        cur.execute("SELECT COUNT(DISTINCT session_id) FROM agent_decisions")
        row = cur.fetchone()
        metrics['unique_sessions'] = row[0] if row else 0
        
        # Reward statistics
        cur.execute("SELECT AVG(reward), MAX(reward), MIN(reward) FROM agent_decisions WHERE reward IS NOT NULL")
        row = cur.fetchone()
        if row:
            metrics['avg_reward'] = float(row[0]) if row[0] else 0.0
            metrics['max_reward'] = float(row[1]) if row[1] else 0.0
            metrics['min_reward'] = float(row[2]) if row[2] else 0.0
        
        # Hourly decisions
        cur.execute("""
            SELECT COUNT(*) FROM agent_decisions 
            WHERE created_at > NOW() - INTERVAL '1 hour'
        """)
        row = cur.fetchone()
        metrics['hourly_decisions'] = row[0] if row else 0
        
        # Action distribution
        cur.execute("""
            SELECT action, COUNT(*) as cnt 
            FROM agent_decisions 
            GROUP BY action 
            ORDER BY cnt DESC
        """)
        for row in cur.fetchall():
            metrics['action_distribution'][row[0]] = row[1]
        
        cur.close()
        conn.close()
    except Exception as e:
        pass
    
    return metrics

def fetch_system_health():
    """Fetch system component health status."""
    health = {
        'postgres': False,
        'redis': False,
        'postgres_latency': None,
        'redis_latency': None
    }
    
    # PostgreSQL
    start = time.time()
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, connect_timeout=3)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        health['postgres'] = True
        health['postgres_latency'] = round((time.time() - start) * 1000, 1)
    except:
        pass
    
    # Redis
    start = time.time()
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, decode_responses=True, socket_timeout=3)
        r.ping()
        health['redis'] = True
        health['redis_latency'] = round((time.time() - start) * 1000, 1)
    except:
        pass
    
    return health

def get_geolocation(ip):
    """Get geolocation for IP address."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0),
                    'isp': data.get('isp', 'Unknown')
                }
    except:
        pass
    return None

# =============================================================================
# MAIN DASHBOARD
# =============================================================================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">CYBER MIRAGE<span class="version-badge">v5.0</span></h1>
        <p class="main-subtitle">Adaptive Honeypot Defense Platform with Deep Reinforcement Learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### System Status")
        health = fetch_system_health()
        
        # PostgreSQL Status
        pg_status = "status-online" if health['postgres'] else "status-offline"
        pg_text = f"Connected ({health['postgres_latency']}ms)" if health['postgres'] else "Disconnected"
        st.markdown(f"""
        <div class="status-indicator {pg_status}">
            <span class="status-dot"></span>
            PostgreSQL: {pg_text}
        </div>
        """, unsafe_allow_html=True)
        
        # Redis Status
        redis_status = "status-online" if health['redis'] else "status-offline"
        redis_text = f"Connected ({health['redis_latency']}ms)" if health['redis'] else "Disconnected"
        st.markdown(f"""
        <div class="status-indicator {redis_status}" style="margin-top: 0.5rem;">
            <span class="status-dot"></span>
            Redis: {redis_text}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Refresh control - using proper streamlit auto-refresh
        auto_refresh = st.checkbox("Auto Refresh", value=False)
        refresh_interval = st.selectbox("Refresh Interval", [10, 30, 60], index=1, format_func=lambda x: f"{x} seconds")
        
        if st.button("Refresh Now"):
            st.cache_data.clear()
            st.rerun()
        
        # Auto refresh using fragment or manual timing
        if auto_refresh:
            st.markdown(f"""
            <div style="font-size: 0.75rem; color: #f39c12; margin-top: 0.5rem;">
                Auto-refresh every {refresh_interval}s
            </div>
            """, unsafe_allow_html=True)
            time.sleep(refresh_interval)
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"""
        <div style="font-size: 0.75rem; color: #6b7280;">
            Last Update: {datetime.now().strftime('%H:%M:%S')}<br>
            Dashboard Version: 5.0.2
        </div>
        """, unsafe_allow_html=True)
    
    # Fetch data
    metrics = fetch_ppo_metrics()
    decisions_df = fetch_agent_decisions(100)
    sessions_df = fetch_attack_sessions(50)
    
    # ==========================================================================
    # KEY METRICS
    # ==========================================================================
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_decisions']:,}</div>
            <div class="metric-label">Total Decisions</div>
            <div class="metric-trend trend-neutral">All Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['unique_sessions']:,}</div>
            <div class="metric-label">Attack Sessions</div>
            <div class="metric-trend trend-neutral">Unique</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        reward_class = "trend-positive" if metrics['avg_reward'] > 0 else "trend-negative" if metrics['avg_reward'] < 0 else "trend-neutral"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {'#10b981' if metrics['avg_reward'] > 0 else '#ef4444' if metrics['avg_reward'] < 0 else '#ffffff'}">
                {metrics['avg_reward']:.2f}
            </div>
            <div class="metric-label">Average Reward</div>
            <div class="metric-trend {reward_class}">Per Decision</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['hourly_decisions']:,}</div>
            <div class="metric-label">Hourly Activity</div>
            <div class="metric-trend trend-neutral">Last Hour</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        action_count = len(metrics['action_distribution'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{action_count}/20</div>
            <div class="metric-label">Actions Used</div>
            <div class="metric-trend trend-neutral">Elite Actions</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==========================================================================
    # TWO COLUMN LAYOUT
    # ==========================================================================
    
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        # Attack World Map
        st.markdown('<div class="section-header">Global Attack Distribution</div>', unsafe_allow_html=True)
        
        if not sessions_df.empty and 'source_ip' in sessions_df.columns:
            # Get unique IPs and their geolocations
            map_data = []
            unique_ips = sessions_df['source_ip'].dropna().unique()[:20]  # Limit API calls
            
            for ip in unique_ips:
                if ip and not ip.startswith('10.') and not ip.startswith('192.168.') and not ip.startswith('172.'):
                    geo = get_geolocation(ip)
                    if geo and geo['lat'] != 0:
                        attack_count = len(sessions_df[sessions_df['source_ip'] == ip])
                        map_data.append({
                            'ip': ip,
                            'lat': geo['lat'],
                            'lon': geo['lon'],
                            'country': geo['country'],
                            'city': geo['city'],
                            'count': attack_count,
                            'size': min(attack_count * 5 + 10, 50)
                        })
            
            if map_data:
                map_df = pd.DataFrame(map_data)
                
                fig = go.Figure()
                
                # Add base map
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
                    text=map_df.apply(lambda x: f"IP: {x['ip']}<br>Location: {x['city']}, {x['country']}<br>Attacks: {x['count']}", axis=1),
                    hoverinfo='text',
                    name='Attack Sources'
                ))
                
                fig.update_layout(
                    geo=dict(
                        projection_type='natural earth',
                        showland=True,
                        landcolor='#1a1a2e',
                        showocean=True,
                        oceancolor='#0a0a0f',
                        showlakes=False,
                        showcountries=True,
                        countrycolor='#2d2d44',
                        showcoastlines=True,
                        coastlinecolor='#2d2d44',
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No external IP geolocation data available yet.")
        else:
            st.info("No attack session data available.")
        
        # Action Distribution Chart
        st.markdown('<div class="section-header">Action Distribution Analysis</div>', unsafe_allow_html=True)
        
        if metrics['action_distribution']:
            # Create action distribution chart
            action_data = []
            for action, count in metrics['action_distribution'].items():
                action_info = ELITE_ACTIONS.get(action, {'name': action, 'category': 'Unknown', 'color': '#6b7280'})
                action_data.append({
                    'action': action_info['name'],
                    'count': count,
                    'category': action_info['category'],
                    'color': action_info['color']
                })
            
            action_df = pd.DataFrame(action_data)
            
            fig = px.bar(
                action_df.head(10),
                x='count',
                y='action',
                orientation='h',
                color='category',
                color_discrete_map={
                    'Session Control': '#00d4ff',
                    'Delay Tactics': '#f39c12',
                    'Identity Manipulation': '#e67e22',
                    'Deception': '#9b59b6',
                    'Active Defense': '#7f8c8d',
                    'Advanced Tactics': '#e74c3c'
                }
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e5e7eb'),
                xaxis=dict(
                    title='Execution Count',
                    gridcolor='#1f1f2e',
                    showgrid=True
                ),
                yaxis=dict(
                    title='',
                    gridcolor='#1f1f2e'
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1,
                    bgcolor='rgba(0,0,0,0)'
                ),
                height=350,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No action data available yet.")
    
    with right_col:
        # 20 Elite Actions Reference
        st.markdown('<div class="section-header">20 Elite Deception Actions</div>', unsafe_allow_html=True)
        
        # Group by category
        for category, info in ACTION_CATEGORIES.items():
            cat_class = {
                'Session Control': 'cat-session',
                'Delay Tactics': 'cat-delay',
                'Identity Manipulation': 'cat-identity',
                'Deception': 'cat-deception',
                'Active Defense': 'cat-defense',
                'Advanced Tactics': 'cat-advanced'
            }.get(category, 'cat-session')
            
            st.markdown(f"""
            <div style="margin: 1rem 0 0.5rem 0;">
                <span class="action-category-badge {cat_class}">{category}</span>
            </div>
            """, unsafe_allow_html=True)
            
            for action_key, action_info in ELITE_ACTIONS.items():
                if action_info['category'] == category:
                    count = metrics['action_distribution'].get(action_key, 0)
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid #1a1a2e;">
                        <span style="color: #e5e7eb; font-size: 0.8rem;">
                            <span class="action-id">{action_info['id']:02d}</span> {action_info['name']}
                        </span>
                        <span style="color: #6b7280; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace;">
                            {count}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
    
    # ==========================================================================
    # RECENT DECISIONS TABLE
    # ==========================================================================
    
    st.markdown('<div class="section-header">Recent Agent Decisions</div>', unsafe_allow_html=True)
    
    if not decisions_df.empty:
        # Format the dataframe for display
        display_df = decisions_df[['created_at', 'action', 'strategy', 'reward']].head(15).copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df.columns = ['Timestamp', 'Action', 'Strategy', 'Reward']
        
        # Create HTML table
        table_html = """
        <table class="data-table">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Action</th>
                    <th>Strategy</th>
                    <th>Reward</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for _, row in display_df.iterrows():
            reward = float(row['Reward']) if row['Reward'] else 0
            reward_class = "reward-positive" if reward > 0 else "reward-negative" if reward < 0 else "reward-neutral"
            
            action_info = ELITE_ACTIONS.get(row['Action'], {'name': row['Action'], 'category': 'Unknown'})
            
            table_html += f"""
            <tr>
                <td class="timestamp">{row['Timestamp']}</td>
                <td class="action-name">{action_info['name']}</td>
                <td style="color: #9ca3af;">{row['Strategy'][:50]}...</td>
                <td class="{reward_class}">{reward:+.2f}</td>
            </tr>
            """
        
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No decision data available.")
    
    # ==========================================================================
    # REWARD TREND CHART
    # ==========================================================================
    
    st.markdown('<div class="section-header">Reward Trend Analysis</div>', unsafe_allow_html=True)
    
    if not decisions_df.empty and 'reward' in decisions_df.columns:
        reward_df = decisions_df[['created_at', 'reward']].copy()
        reward_df['created_at'] = pd.to_datetime(reward_df['created_at'])
        reward_df = reward_df.sort_values('created_at')
        reward_df['cumulative_reward'] = reward_df['reward'].cumsum()
        reward_df['rolling_avg'] = reward_df['reward'].rolling(window=5, min_periods=1).mean()
        
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Individual Rewards', 'Cumulative Reward'))
        
        # Individual rewards
        fig.add_trace(
            go.Scatter(
                x=list(range(len(reward_df))),
                y=reward_df['reward'],
                mode='lines+markers',
                name='Reward',
                line=dict(color='#00d4ff', width=1),
                marker=dict(size=4)
            ),
            row=1, col=1
        )
        
        # Rolling average
        fig.add_trace(
            go.Scatter(
                x=list(range(len(reward_df))),
                y=reward_df['rolling_avg'],
                mode='lines',
                name='Rolling Avg (5)',
                line=dict(color='#f39c12', width=2, dash='dash')
            ),
            row=1, col=1
        )
        
        # Cumulative reward
        fig.add_trace(
            go.Scatter(
                x=list(range(len(reward_df))),
                y=reward_df['cumulative_reward'],
                mode='lines',
                name='Cumulative',
                line=dict(color='#10b981', width=2),
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.1)'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e5e7eb'),
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
                bgcolor='rgba(0,0,0,0)'
            )
        )
        
        fig.update_xaxes(gridcolor='#1f1f2e', showgrid=True)
        fig.update_yaxes(gridcolor='#1f1f2e', showgrid=True)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data for reward trend analysis.")

# =============================================================================
# RUN DASHBOARD
# =============================================================================

if __name__ == "__main__":
    main()
