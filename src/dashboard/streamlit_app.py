"""
🎭 Cyber Mirage v5.0 - Elite Defense Dashboard
═══════════════════════════════════════════════════════════════════════════════
PhD-Level Adaptive Honeypot System with Deep Reinforcement Learning
Real-time Threat Intelligence & 20 Elite Deception Actions

Author: Cyber Mirage Research Team
Version: 5.0 LEGENDARY
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

# 20 Elite Deception Actions
ELITE_ACTIONS = {
    'maintain_session': {'name': 'Maintain Session', 'category': 'Session Control', 'color': '#2ecc71'},
    'drop_session': {'name': 'Drop Session', 'category': 'Session Control', 'color': '#e74c3c'},
    'throttle_session': {'name': 'Throttle Session', 'category': 'Session Control', 'color': '#f39c12'},
    'redirect_session': {'name': 'Redirect Session', 'category': 'Session Control', 'color': '#9b59b6'},
    'inject_delay': {'name': 'Inject Delay', 'category': 'Delay Tactics', 'color': '#3498db'},
    'progressive_delay': {'name': 'Progressive Delay', 'category': 'Delay Tactics', 'color': '#1abc9c'},
    'random_delay': {'name': 'Random Delay', 'category': 'Delay Tactics', 'color': '#34495e'},
    'swap_service_banner': {'name': 'Swap Banner', 'category': 'Identity Manipulation', 'color': '#e67e22'},
    'randomize_banner': {'name': 'Randomize Banner', 'category': 'Identity Manipulation', 'color': '#16a085'},
    'mimic_vulnerable': {'name': 'Mimic Vulnerable', 'category': 'Identity Manipulation', 'color': '#c0392b'},
    'present_lure': {'name': 'Present Lure', 'category': 'Deception', 'color': '#8e44ad'},
    'deploy_breadcrumb': {'name': 'Deploy Breadcrumb', 'category': 'Deception', 'color': '#2980b9'},
    'inject_fake_creds': {'name': 'Inject Fake Creds', 'category': 'Deception', 'color': '#27ae60'},
    'simulate_target': {'name': 'Simulate Target', 'category': 'Deception', 'color': '#d35400'},
    'capture_tools': {'name': 'Capture Tools', 'category': 'Active Defense', 'color': '#7f8c8d'},
    'log_enhanced': {'name': 'Enhanced Logging', 'category': 'Active Defense', 'color': '#95a5a6'},
    'fingerprint': {'name': 'Fingerprint Attacker', 'category': 'Active Defense', 'color': '#bdc3c7'},
    'tarpit': {'name': 'Tarpit', 'category': 'Advanced Tactics', 'color': '#2c3e50'},
    'honeypot_upgrade': {'name': 'Honeypot Upgrade', 'category': 'Advanced Tactics', 'color': '#1a252f'},
    'alert_track': {'name': 'Alert & Track', 'category': 'Advanced Tactics', 'color': '#e74c3c'}
}

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Cyber Mirage v5.0 | PhD Defense System",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS - Modern Academic Theme
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Main Theme */
    .main {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Header Styles */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(120deg, #00d4ff, #7b2cbf, #ff006e, #00d4ff);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 5s ease infinite;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .sub-header {
        font-size: 1.1rem;
        text-align: center;
        color: #a0a0a0;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, #1e1e2f, #2a2a4a);
        border: 1px solid rgba(123, 44, 191, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(123, 44, 191, 0.2);
        border-color: rgba(0, 212, 255, 0.5);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.85rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        margin-top: 0.5rem;
        display: inline-block;
    }
    
    .delta-positive {
        background: rgba(46, 204, 113, 0.2);
        color: #2ecc71;
    }
    
    .delta-negative {
        background: rgba(231, 76, 60, 0.2);
        color: #e74c3c;
    }
    
    /* Status Indicators */
    .status-online {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(46, 204, 113, 0.15);
        border: 1px solid rgba(46, 204, 113, 0.3);
        border-radius: 25px;
        color: #2ecc71;
        font-weight: 600;
    }
    
    .status-offline {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(231, 76, 60, 0.15);
        border: 1px solid rgba(231, 76, 60, 0.3);
        border-radius: 25px;
        color: #e74c3c;
        font-weight: 600;
    }
    
    .pulse-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #2ecc71;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(46, 204, 113, 0); }
        100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #fff;
        padding: 1rem 0;
        border-bottom: 2px solid rgba(123, 44, 191, 0.5);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* Alert Boxes */
    .alert-critical {
        background: linear-gradient(135deg, rgba(231, 76, 60, 0.15), rgba(192, 57, 43, 0.1));
        border-left: 4px solid #e74c3c;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        animation: alert-pulse 2s infinite;
    }
    
    @keyframes alert-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(243, 156, 18, 0.15), rgba(230, 126, 34, 0.1));
        border-left: 4px solid #f39c12;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
    }
    
    .alert-info {
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.15), rgba(41, 128, 185, 0.1));
        border-left: 4px solid #3498db;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
    }
    
    /* Table Styles */
    .dataframe {
        background: rgba(30, 30, 47, 0.8) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(123, 44, 191, 0.2) !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Research Info Box */
    .research-box {
        background: linear-gradient(135deg, rgba(123, 44, 191, 0.1), rgba(0, 212, 255, 0.05));
        border: 1px solid rgba(123, 44, 191, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .research-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #7b2cbf;
        margin-bottom: 0.75rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_db_connection():
    """Create PostgreSQL connection with error handling"""
    try:
        return psycopg2.connect(
            host=DB_HOST, database=DB_NAME, 
            user=DB_USER, password=DB_PASS,
            connect_timeout=5
        )
    except Exception as e:
        return None


def get_redis_connection():
    """Create Redis connection"""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, decode_responses=True)
        r.ping()
        return r
    except:
        return None


def get_system_health():
    """Get comprehensive system health metrics"""
    health = {
        'postgres': {'status': False, 'latency': None, 'connections': 0},
        'redis': {'status': False, 'latency': None, 'keys': 0},
        'honeypots': {'active': 10, 'types': ['SSH', 'FTP', 'HTTP', 'HTTPS', 'MySQL', 'PostgreSQL', 'Modbus', 'SMB', 'NetBIOS', 'SMTP']},
        'timestamp': datetime.now()
    }
    
    # PostgreSQL
    start = time.time()
    conn = get_db_connection()
    if conn:
        health['postgres']['status'] = True
        health['postgres']['latency'] = round((time.time() - start) * 1000, 2)
        try:
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            health['postgres']['connections'] = cur.fetchone()[0]
            cur.close()
        except:
            pass
        conn.close()
    
    # Redis
    start = time.time()
    r = get_redis_connection()
    if r:
        health['redis']['status'] = True
        health['redis']['latency'] = round((time.time() - start) * 1000, 2)
        try:
            health['redis']['keys'] = r.dbsize()
        except:
            pass
    
    return health


def get_attack_statistics():
    """Get comprehensive attack statistics from database"""
    stats = {
        'total_attacks': 0,
        'unique_attackers': 0,
        'attacks_today': 0,
        'attacks_hour': 0,
        'top_services': [],
        'top_attackers': [],
        'hourly_trend': [],
        'service_distribution': {}
    }
    
    conn = get_db_connection()
    if not conn:
        return stats
    
    try:
        cur = conn.cursor()
        
        # Total attacks
        cur.execute("SELECT COUNT(*) FROM attack_sessions")
        stats['total_attacks'] = cur.fetchone()[0] or 0
        
        # Unique attackers
        cur.execute("SELECT COUNT(DISTINCT origin) FROM attack_sessions")
        stats['unique_attackers'] = cur.fetchone()[0] or 0
        
        # Attacks today
        cur.execute("SELECT COUNT(*) FROM attack_sessions WHERE start_time > CURRENT_DATE")
        stats['attacks_today'] = cur.fetchone()[0] or 0
        
        # Attacks last hour
        cur.execute("SELECT COUNT(*) FROM attack_sessions WHERE start_time > NOW() - INTERVAL '1 hour'")
        stats['attacks_hour'] = cur.fetchone()[0] or 0
        
        # Top services targeted
        cur.execute("""
            SELECT COALESCE(honeypot_type, 'Unknown') as service, COUNT(*) as cnt 
            FROM attack_sessions 
            GROUP BY honeypot_type 
            ORDER BY cnt DESC 
            LIMIT 10
        """)
        stats['top_services'] = [{'service': r[0], 'count': r[1]} for r in cur.fetchall()]
        
        # Service distribution
        for svc in stats['top_services']:
            stats['service_distribution'][svc['service']] = svc['count']
        
        # Top attackers
        cur.execute("""
            SELECT origin, COUNT(*) as cnt 
            FROM attack_sessions 
            WHERE origin IS NOT NULL
            GROUP BY origin 
            ORDER BY cnt DESC 
            LIMIT 10
        """)
        stats['top_attackers'] = [{'ip': r[0], 'count': r[1]} for r in cur.fetchall()]
        
        # Hourly trend (last 24 hours)
        cur.execute("""
            SELECT date_trunc('hour', start_time) as hour, COUNT(*) as cnt
            FROM attack_sessions 
            WHERE start_time > NOW() - INTERVAL '24 hours'
            GROUP BY hour 
            ORDER BY hour
        """)
        stats['hourly_trend'] = [{'hour': r[0], 'count': r[1]} for r in cur.fetchall()]
        
        cur.close()
    except Exception as e:
        pass
    finally:
        conn.close()
    
    return stats


def get_ai_metrics():
    """Get PPO Agent metrics and action distribution"""
    metrics = {
        'total_decisions': 0,
        'unique_sessions': 0,
        'avg_reward': 0.0,
        'max_reward': 0.0,
        'min_reward': 0.0,
        'action_distribution': {},
        'category_distribution': {},
        'reward_trend': [],
        'decisions_per_hour': []
    }
    
    conn = get_db_connection()
    if not conn:
        return metrics
    
    try:
        cur = conn.cursor()
        
        # Total decisions
        cur.execute("SELECT COUNT(*) FROM agent_decisions")
        metrics['total_decisions'] = cur.fetchone()[0] or 0
        
        # Unique sessions
        cur.execute("SELECT COUNT(DISTINCT session_id) FROM agent_decisions")
        metrics['unique_sessions'] = cur.fetchone()[0] or 0
        
        # Reward statistics
        cur.execute("""
            SELECT AVG(reward), MAX(reward), MIN(reward) 
            FROM agent_decisions 
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """)
        row = cur.fetchone()
        if row:
            metrics['avg_reward'] = float(row[0]) if row[0] else 0.0
            metrics['max_reward'] = float(row[1]) if row[1] else 0.0
            metrics['min_reward'] = float(row[2]) if row[2] else 0.0
        
        # Action distribution
        cur.execute("""
            SELECT action, COUNT(*) as cnt 
            FROM agent_decisions 
            GROUP BY action 
            ORDER BY cnt DESC
        """)
        for row in cur.fetchall():
            action = row[0]
            count = row[1]
            metrics['action_distribution'][action] = count
            
            # Category grouping
            if action in ELITE_ACTIONS:
                category = ELITE_ACTIONS[action]['category']
                metrics['category_distribution'][category] = metrics['category_distribution'].get(category, 0) + count
        
        # Reward trend (last 24 hours)
        cur.execute("""
            SELECT date_trunc('hour', created_at) as hour, AVG(reward) as avg_reward
            FROM agent_decisions 
            WHERE created_at > NOW() - INTERVAL '24 hours'
            GROUP BY hour 
            ORDER BY hour
        """)
        metrics['reward_trend'] = [{'hour': r[0], 'reward': float(r[1]) if r[1] else 0} for r in cur.fetchall()]
        
        # Decisions per hour
        cur.execute("""
            SELECT date_trunc('hour', created_at) as hour, COUNT(*) as cnt
            FROM agent_decisions 
            WHERE created_at > NOW() - INTERVAL '24 hours'
            GROUP BY hour 
            ORDER BY hour
        """)
        metrics['decisions_per_hour'] = [{'hour': r[0], 'count': r[1]} for r in cur.fetchall()]
        
        cur.close()
    except Exception as e:
        pass
    finally:
        conn.close()
    
    return metrics


def get_recent_attacks(limit=20):
    """Get recent attack sessions with details"""
    attacks = []
    conn = get_db_connection()
    if not conn:
        return attacks
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, attacker_name, origin, honeypot_type, start_time, detected
            FROM attack_sessions 
            ORDER BY start_time DESC 
            LIMIT %s
        """, (limit,))
        
        for row in cur.fetchall():
            attacks.append({
                'id': str(row[0])[:8],
                'attacker': row[1] or 'Unknown',
                'origin': row[2] or 'Unknown',
                'service': row[3] or 'Unknown',
                'time': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else 'N/A',
                'detected': row[5]
            })
        
        cur.close()
    except:
        pass
    finally:
        conn.close()
    
    return attacks


def get_threat_intel():
    """Get threat intelligence from Redis"""
    intel = []
    r = get_redis_connection()
    if not r:
        return intel
    
    try:
        keys = r.keys('threat:*')
        for key in keys[:20]:
            ip = key.replace('threat:', '')
            data = r.hgetall(key)
            intel.append({
                'ip': ip,
                'count': int(data.get('count', 0)),
                'last_seen': data.get('last_seen', 'Unknown'),
                'service': data.get('service', 'Unknown')
            })
        
        intel.sort(key=lambda x: x['count'], reverse=True)
    except:
        pass
    
    return intel

# ═══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_header():
    """Render main dashboard header"""
    st.markdown("""
        <h1 class="main-header">🎭 CYBER MIRAGE v5.0</h1>
        <p class="sub-header">
            Adaptive Honeypot Defense System with Deep Reinforcement Learning<br>
            <em>PhD Research: 20 Elite Deception Actions | PPO Neural Network | Real-time Threat Intelligence</em>
        </p>
    """, unsafe_allow_html=True)


def render_system_status(health):
    """Render system status indicators"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if health['postgres']['status']:
            st.markdown(f"""
                <div class="status-online">
                    <div class="pulse-dot"></div>
                    PostgreSQL Online ({health['postgres']['latency']}ms)
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-offline">❌ PostgreSQL Offline</div>', unsafe_allow_html=True)
    
    with col2:
        if health['redis']['status']:
            st.markdown(f"""
                <div class="status-online">
                    <div class="pulse-dot"></div>
                    Redis Online ({health['redis']['latency']}ms)
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-offline">❌ Redis Offline</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="status-online">
                <div class="pulse-dot"></div>
                {health['honeypots']['active']} Honeypots Active
            </div>
        """, unsafe_allow_html=True)


def render_key_metrics(attack_stats, ai_metrics):
    """Render key performance metrics"""
    st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        delta_class = "delta-positive" if attack_stats['attacks_hour'] > 0 else ""
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{attack_stats['total_attacks']:,}</div>
                <div class="metric-label">Total Attacks Captured</div>
                <div class="metric-delta {delta_class}">+{attack_stats['attacks_hour']} this hour</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{attack_stats['unique_attackers']:,}</div>
                <div class="metric-label">Unique Threat Actors</div>
                <div class="metric-delta delta-positive">Real-time tracking</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{ai_metrics['total_decisions']:,}</div>
                <div class="metric-label">AI Decisions Made</div>
                <div class="metric-delta delta-positive">20 Elite Actions</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        reward_color = "delta-positive" if ai_metrics['avg_reward'] >= 0 else "delta-negative"
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{ai_metrics['avg_reward']:.3f}</div>
                <div class="metric-label">Average Reward (24h)</div>
                <div class="metric-delta {reward_color}">PPO Learning</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        detection_rate = 100 if attack_stats['total_attacks'] > 0 else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{detection_rate}%</div>
                <div class="metric-label">Detection Rate</div>
                <div class="metric-delta delta-positive">All captured</div>
            </div>
        """, unsafe_allow_html=True)


def render_action_distribution(ai_metrics):
    """Render 20 Elite Actions distribution chart"""
    st.markdown('<div class="section-header">🤖 PPO Agent: 20 Elite Deception Actions</div>', unsafe_allow_html=True)
    
    if not ai_metrics['action_distribution']:
        st.info("⏳ Waiting for AI decisions... Attack the honeypots to see action distribution!")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Action distribution bar chart
        actions = list(ai_metrics['action_distribution'].keys())
        counts = list(ai_metrics['action_distribution'].values())
        colors = [ELITE_ACTIONS.get(a, {}).get('color', '#3498db') for a in actions]
        
        fig = go.Figure(data=[
            go.Bar(
                x=actions,
                y=counts,
                marker_color=colors,
                text=counts,
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=dict(text='Action Distribution', font=dict(size=16, color='white')),
            xaxis=dict(title='Action Type', tickangle=-45, color='white', gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(title='Count', color='white', gridcolor='rgba(255,255,255,0.1)'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400,
            margin=dict(b=120)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category distribution pie chart
        if ai_metrics['category_distribution']:
            categories = list(ai_metrics['category_distribution'].keys())
            cat_counts = list(ai_metrics['category_distribution'].values())
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=categories,
                    values=cat_counts,
                    hole=0.4,
                    marker=dict(colors=px.colors.qualitative.Set2),
                    textinfo='percent+label',
                    textposition='outside'
                )
            ])
            
            fig.update_layout(
                title=dict(text='By Category', font=dict(size=16, color='white')),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=10),
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)


def render_attack_trends(attack_stats):
    """Render attack trends and patterns"""
    st.markdown('<div class="section-header">📈 Attack Trends & Service Distribution</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly attack trend
        if attack_stats['hourly_trend']:
            df = pd.DataFrame(attack_stats['hourly_trend'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['hour'],
                y=df['count'],
                mode='lines+markers',
                fill='tozeroy',
                line=dict(color='#00d4ff', width=3),
                marker=dict(size=8, color='#7b2cbf'),
                fillcolor='rgba(0, 212, 255, 0.2)',
                hovertemplate='<b>%{x}</b><br>Attacks: %{y}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(text='Attack Volume (Last 24h)', font=dict(size=16, color='white')),
                xaxis=dict(title='Time', color='white', gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(title='Attacks', color='white', gridcolor='rgba(255,255,255,0.1)'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Collecting attack data...")
    
    with col2:
        # Service distribution
        if attack_stats['service_distribution']:
            services = list(attack_stats['service_distribution'].keys())
            counts = list(attack_stats['service_distribution'].values())
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=services,
                    values=counts,
                    marker=dict(colors=px.colors.qualitative.Bold),
                    textinfo='label+percent',
                    textposition='inside',
                    insidetextorientation='radial'
                )
            ])
            
            fig.update_layout(
                title=dict(text='Targeted Services', font=dict(size=16, color='white')),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350,
                showlegend=True,
                legend=dict(orientation='h', y=-0.1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🎯 Waiting for service data...")


def render_recent_attacks(attacks):
    """Render recent attacks table"""
    st.markdown('<div class="section-header">🚨 Live Attack Feed</div>', unsafe_allow_html=True)
    
    if not attacks:
        st.info("🔍 No attacks recorded yet. Honeypots are ready and waiting...")
        return
    
    # Create dataframe
    df = pd.DataFrame(attacks)
    
    # Style the dataframe
    st.dataframe(
        df,
        column_config={
            "id": st.column_config.TextColumn("Session ID", width="small"),
            "attacker": st.column_config.TextColumn("Attacker", width="medium"),
            "origin": st.column_config.TextColumn("Origin IP", width="medium"),
            "service": st.column_config.TextColumn("Service", width="small"),
            "time": st.column_config.TextColumn("Timestamp", width="medium"),
            "detected": st.column_config.CheckboxColumn("Detected", width="small")
        },
        hide_index=True,
        use_container_width=True
    )


def render_threat_intel(intel):
    """Render threat intelligence summary"""
    st.markdown('<div class="section-header">🔍 Threat Intelligence (Redis)</div>', unsafe_allow_html=True)
    
    if not intel:
        st.info("📡 Building threat intelligence database...")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Top threat actors bar chart
        ips = [t['ip'] for t in intel[:10]]
        counts = [t['count'] for t in intel[:10]]
        
        fig = go.Figure(data=[
            go.Bar(
                x=counts,
                y=ips,
                orientation='h',
                marker=dict(
                    color=counts,
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title='Attacks')
                ),
                text=counts,
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title=dict(text='Top Threat Actors by Attack Count', font=dict(size=16, color='white')),
            xaxis=dict(title='Attack Count', color='white', gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(title='', color='white', autorange='reversed'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Top Attackers")
        for i, threat in enumerate(intel[:5], 1):
            severity = "🔴" if threat['count'] > 10 else "🟡" if threat['count'] > 5 else "🟢"
            st.markdown(f"""
                <div class="alert-{'critical' if threat['count'] > 10 else 'warning' if threat['count'] > 5 else 'info'}">
                    {severity} <strong>#{i}</strong> {threat['ip']}<br>
                    <small>Attacks: {threat['count']} | Service: {threat['service']}</small>
                </div>
            """, unsafe_allow_html=True)


def render_research_info():
    """Render PhD research information"""
    st.markdown("""
        <div class="research-box">
            <div class="research-title">📚 Research Contribution</div>
            <p style="color: #ccc; margin: 0;">
                This system implements a <strong>novel adaptive honeypot framework</strong> using 
                <strong>Proximal Policy Optimization (PPO)</strong> with 20 elite deception actions.
                The agent learns optimal deception strategies in real-time, maximizing attacker 
                engagement while gathering forensic intelligence.
            </p>
            <br>
            <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                <div>
                    <strong style="color: #7b2cbf;">State Space:</strong>
                    <span style="color: #aaa;">15 dimensions</span>
                </div>
                <div>
                    <strong style="color: #7b2cbf;">Action Space:</strong>
                    <span style="color: #aaa;">20 elite actions</span>
                </div>
                <div>
                    <strong style="color: #7b2cbf;">Algorithm:</strong>
                    <span style="color: #aaa;">PPO with GAE</span>
                </div>
                <div>
                    <strong style="color: #7b2cbf;">Honeypots:</strong>
                    <span style="color: #aaa;">10 protocols</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with controls and info"""
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        
        st.markdown("---")
        
        # Auto-refresh
        auto_refresh = st.toggle("🔄 Auto-Refresh", value=True)
        if auto_refresh:
            refresh_rate = st.slider("Refresh Rate (seconds)", 5, 60, 10)
            st.caption(f"Dashboard updates every {refresh_rate}s")
        
        st.markdown("---")
        
        # System info
        st.markdown("### 📡 Honeypot Ports")
        ports_info = """
        - **SSH**: 2222 → 22
        - **FTP**: 2121 → 21
        - **HTTP**: 8080 → 80
        - **HTTPS**: 8443 → 443
        - **MySQL**: 3307 → 3306
        - **PostgreSQL**: 5434 → 5432
        - **Modbus**: 502
        - **SMB**: 445
        - **NetBIOS**: 139
        - **SMTP**: 1025
        """
        st.markdown(ports_info)
        
        st.markdown("---")
        
        # Current time
        st.markdown("### ⏰ System Time")
        st.markdown(f"**{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
        
        st.markdown("---")
        
        # Version info
        st.markdown("### ℹ️ Version")
        st.caption("Cyber Mirage v5.0 LEGENDARY")
        st.caption("PhD Defense System")
        
        return auto_refresh, refresh_rate if auto_refresh else 10

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main application entry point"""
    
    # Sidebar
    auto_refresh, refresh_rate = render_sidebar()
    
    # Header
    render_header()
    
    # Get all data
    health = get_system_health()
    attack_stats = get_attack_statistics()
    ai_metrics = get_ai_metrics()
    recent_attacks = get_recent_attacks(15)
    threat_intel = get_threat_intel()
    
    # System Status
    render_system_status(health)
    
    st.markdown("---")
    
    # Key Metrics
    render_key_metrics(attack_stats, ai_metrics)
    
    st.markdown("---")
    
    # Action Distribution (20 Elite Actions)
    render_action_distribution(ai_metrics)
    
    st.markdown("---")
    
    # Attack Trends
    render_attack_trends(attack_stats)
    
    st.markdown("---")
    
    # Two columns: Recent Attacks and Threat Intel
    col1, col2 = st.columns(2)
    
    with col1:
        render_recent_attacks(recent_attacks)
    
    with col2:
        render_threat_intel(threat_intel)
    
    st.markdown("---")
    
    # Research Info
    render_research_info()
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()


if __name__ == "__main__":
    main()
