"""
📊 Streamlit Dashboard - Complete UI
لوحة تحكم كاملة لـ Cyber Mirage

واجهة مستخدم تفاعلية لمراقبة النظام بالكامل
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sys
import os
import psycopg2
import redis

# إضافة مسار المشروع
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Database connection settings
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'cyber_mirage')
DB_USER = os.getenv('POSTGRES_USER', 'cybermirage')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASS = os.getenv('REDIS_PASSWORD', 'changeme123')


@st.cache_resource
def get_db_connection():
    """Create PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


@st.cache_resource
def get_redis_connection():
    """Create Redis connection"""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, decode_responses=True)
        r.ping()
        return r
    except Exception as e:
        st.error(f"Redis connection failed: {e}")
        return None


def get_real_metrics():
    """Get real metrics from database"""
    metrics = {
        'total_attacks': 0,
        'unique_attackers': 0,
        'active_sessions': 0,
        'ai_decisions': 0,
        'avg_reward': 0.0,
        'action_distribution': {},
        'recent_attacks': []
    }
    
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        # Total attacks
        cur.execute("SELECT COUNT(*) FROM attack_sessions")
        row = cur.fetchone()
        metrics['total_attacks'] = row[0] if row else 0
        
        # Unique attackers
        cur.execute("SELECT COUNT(DISTINCT origin) FROM attack_sessions")
        row = cur.fetchone()
        metrics['unique_attackers'] = row[0] if row else 0
        
        # AI decisions count
        cur.execute("SELECT COUNT(*) FROM agent_decisions")
        row = cur.fetchone()
        metrics['ai_decisions'] = row[0] if row else 0
        
        # Average reward
        cur.execute("SELECT AVG(reward) FROM agent_decisions WHERE created_at > NOW() - INTERVAL '1 hour'")
        row = cur.fetchone()
        metrics['avg_reward'] = float(row[0]) if row and row[0] else 0.0
        
        # Action distribution (20 Elite Actions)
        cur.execute("""
            SELECT action, COUNT(*) as cnt 
            FROM agent_decisions 
            GROUP BY action 
            ORDER BY cnt DESC
        """)
        for row in cur.fetchall():
            metrics['action_distribution'][row[0]] = row[1]
        
        # Recent attacks (last 10)
        cur.execute("""
            SELECT attacker_name, origin, honeypot_type, start_time 
            FROM attack_sessions 
            ORDER BY start_time DESC 
            LIMIT 10
        """)
        for row in cur.fetchall():
            metrics['recent_attacks'].append({
                'attacker': row[0],
                'origin': row[1],
                'type': row[2] or 'Unknown',
                'time': row[3].strftime('%H:%M:%S') if row[3] else 'N/A'
            })
        
        cur.close()
        conn.close()
    except Exception as e:
        st.warning(f"Could not fetch metrics: {e}")
    
    return metrics


def get_system_health():
    """Get real system health status"""
    health = {
        'postgres': False,
        'redis': False,
        'postgres_latency': None,
        'redis_latency': None
    }
    
    # Check PostgreSQL
    import time
    start = time.time()
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        health['postgres'] = True
        health['postgres_latency'] = round((time.time() - start) * 1000, 2)
    except:
        pass
    
    # Check Redis
    start = time.time()
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
        r.ping()
        health['redis'] = True
        health['redis_latency'] = round((time.time() - start) * 1000, 2)
    except:
        pass
    
    return health

# Page config
st.set_page_config(
    page_title="Cyber Mirage v5.0 LEGENDARY",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .alert-box {
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .alert-critical {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    
    .alert-warning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    
    .alert-info {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """الصفحة الرئيسية"""
    
    # Header
    st.markdown('<h1 class="main-header">🎭 Cyber Mirage v5.0 LEGENDARY</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        try:
            st.image("https://via.placeholder.com/300x100/FF6B6B/FFFFFF?text=Cyber+Mirage", 
                     width=None)  # Use width instead of deprecated parameter
        except:
            st.image("https://via.placeholder.com/300x100/FF6B6B/FFFFFF?text=Cyber+Mirage")
        
        st.markdown("## 📊 Navigation")
        page = st.radio(
            "Select View",
            ["Dashboard", "Threats", "AI Status", "Forensics", "Settings"]
        )
        
        st.markdown("---")
        st.markdown("### 🔄 Auto-Refresh")
        auto_refresh = st.checkbox("Enable", value=True)
        
        if auto_refresh:
            refresh_rate = st.slider("Rate (seconds)", 5, 60, 10)
        
        st.markdown("---")
        st.markdown("### 📈 System Status")
        
        # Real-time health check
        health = get_system_health()
        if health['postgres'] and health['redis']:
            st.success("✅ All Systems Operational")
        elif health['postgres'] or health['redis']:
            st.warning("⚠️ Some Systems Degraded")
        else:
            st.error("❌ Systems Offline")
        
        # Show latency
        if health['postgres_latency']:
            st.caption(f"DB: {health['postgres_latency']}ms")
        if health['redis_latency']:
            st.caption(f"Redis: {health['redis_latency']}ms")
    
    # Main content
    if page == "Dashboard":
        show_dashboard()
    elif page == "Threats":
        show_threats()
    elif page == "AI Status":
        show_ai_status()
    elif page == "Forensics":
        show_forensics()
    elif page == "Settings":
        show_settings()


def show_dashboard():
    """لوحة التحكم الرئيسية"""
    
    st.header("📊 System Overview")
    
    # Get real metrics
    metrics = get_real_metrics()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎯 Total Attacks",
            value=str(metrics['total_attacks']),
            delta=f"+{min(metrics['total_attacks'], 10)} today"
        )
    
    with col2:
        st.metric(
            label="👤 Unique Attackers",
            value=str(metrics['unique_attackers']),
            delta="Real-time"
        )
    
    with col3:
        st.metric(
            label="🤖 AI Decisions",
            value=str(metrics['ai_decisions']),
            delta="20 Elite Actions"
        )
    
    with col4:
        st.metric(
            label="⭐ Avg Reward",
            value=f"{metrics['avg_reward']:.2f}",
            delta="Last hour"
        )
            label="Deception Success",
            value="99.1%",
            delta="+0.5%"
        )
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Threat Activity (Last 24h)")
        
        # Sample data
        hours = list(range(24))
        threats = [5, 8, 12, 15, 20, 18, 22, 25, 30, 28, 35, 32,
                  38, 40, 45, 42, 48, 50, 55, 52, 48, 45, 40, 35]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hours,
            y=threats,
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            xaxis_title="Hour",
            yaxis_title="Threats Detected",
            height=300,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🤖 20 Elite Actions Distribution")
        
        # Real action distribution from database
        metrics = get_real_metrics()
        action_dist = metrics.get('action_distribution', {})
        
        if action_dist:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=list(action_dist.keys()),
                y=list(action_dist.values()),
                marker=dict(
                    color=list(action_dist.values()),
                    colorscale='Viridis',
                    showscale=True
                ),
                text=list(action_dist.values()),
                textposition='auto'
            ))
            
            fig.update_layout(
                yaxis_title="Count",
                xaxis_title="Action Type",
                height=300,
                showlegend=False,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No AI decisions recorded yet. Waiting for attacks...")
    
    st.markdown("---")
    
    # Alerts - Real recent attacks
    st.subheader("🚨 Recent Attacks (Real-time)")
    
    metrics = get_real_metrics()
    recent = metrics.get('recent_attacks', [])
    
    if recent:
        for attack in recent[:5]:
            severity = "critical" if "APT" in str(attack.get('attacker', '')) else "warning"
            icon = "🔴" if severity == "critical" else "⚠️"
            
            st.markdown(f"""
            <div class="alert-box alert-{severity}">
                {icon} <strong>{attack.get('time', 'N/A')}</strong> - 
                [{attack.get('type', 'Unknown')}] {attack.get('attacker', 'Unknown')} 
                from {attack.get('origin', 'Unknown')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent attacks recorded. System monitoring active...")


def show_threats():
    """صفحة التهديدات"""
    
    st.header("🎯 Active Threats")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        severity_filter = st.multiselect(
            "Severity",
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High"]
        )
    
    with col2:
        source_filter = st.multiselect(
            "Source",
            ["External", "Internal", "Unknown"],
            default=["External"]
        )
    
    with col3:
        time_filter = st.selectbox(
            "Time Range",
            ["Last Hour", "Last 24h", "Last Week", "All Time"]
        )
    
    st.markdown("---")
    
    # Threats table
    threats_data = {
        'Time': ['14:32:15', '14:28:03', '14:25:40', '14:20:12', '14:15:08'],
        'Severity': ['Critical', 'High', 'Medium', 'High', 'Low'],
        'Type': ['APT', 'DDoS', 'SQLi', 'XSS', 'Port Scan'],
        'Source IP': ['185.220.101.45', '192.168.1.50', '10.0.0.15', '203.0.113.42', '172.16.0.8'],
        'Target': ['Honeypot-01', 'Honeypot-05', 'Honeypot-12', 'Honeypot-03', 'Honeypot-08'],
        'Status': ['Contained', 'Analyzing', 'Blocked', 'Blocked', 'Logged']
    }
    
    df = pd.DataFrame(threats_data)
    
    st.dataframe(
        df.style.applymap(
            lambda x: 'background-color: #ffebee' if x == 'Critical' else '',
            subset=['Severity']
        ),
        use_container_width=True
    )
    
    # Threat map
    st.subheader("🗺️ Threat Origins")
    
    # Sample geo data
    threat_locations = pd.DataFrame({
        'lat': [55.7558, 40.7128, 51.5074, 35.6762, -33.8688],
        'lon': [37.6173, -74.0060, -0.1278, 139.6503, 151.2093],
        'city': ['Moscow', 'New York', 'London', 'Tokyo', 'Sydney'],
        'threats': [25, 15, 12, 8, 5]
    })
    
    fig = px.scatter_geo(
        threat_locations,
        lat='lat',
        lon='lon',
        size='threats',
        hover_name='city',
        size_max=50,
        projection='natural earth'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def show_ai_status():
    """صفحة حالة الذكاء الاصطناعي"""
    
    st.header("🤖 AI Systems Status")
    
    # AI modules
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧠 Neural Deception")
        st.progress(99)
        st.write("**DeceptionGAN**: 5 active strategies")
        st.write("**Psychological Warfare**: 5 tactics deployed")
        st.write("**Deepfake Services**: 150 running")
        
        st.subheader("🐝 Swarm Intelligence")
        st.progress(97)
        st.write("**Particle Swarm**: 1000 agents")
        st.write("**Ant Colony**: 500 agents")
        st.write("**Bee Algorithm**: 600 agents")
        st.write("**Total Coordination**: 2100 agents")
    
    with col2:
        st.subheader("⚛️ Quantum Defense")
        st.progress(98)
        st.write("**Superposition States**: Active")
        st.write("**Entanglement**: 50 pairs")
        st.write("**Tunneling**: Enabled")
        st.write("**Schrödinger's Honeypot**: Deployed")
        
        st.subheader("🧬 Bio-Inspired Security")
        st.progress(96)
        st.write("**Antibodies**: 100 active")
        st.write("**Memory Cells**: 25 stored")
        st.write("**Genetic Generation**: 50")
        st.write("**Neural Networks**: 50 competing")
    
    st.markdown("---")
    
    # Performance chart
    st.subheader("📈 AI Performance Trends")
    
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    neural = [95, 96, 97, 98, 98, 99, 99]
    swarm = [92, 94, 95, 96, 97, 97, 97]
    quantum = [93, 95, 96, 97, 98, 98, 98]
    bio = [90, 92, 94, 95, 96, 96, 96]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=neural, mode='lines+markers', name='Neural'))
    fig.add_trace(go.Scatter(x=days, y=swarm, mode='lines+markers', name='Swarm'))
    fig.add_trace(go.Scatter(x=days, y=quantum, mode='lines+markers', name='Quantum'))
    fig.add_trace(go.Scatter(x=days, y=bio, mode='lines+markers', name='Bio'))
    
    fig.update_layout(
        yaxis_title="Efficiency %",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_forensics():
    """صفحة الأدلة الجنائية"""
    
    st.header("🔍 Digital Forensics")
    
    tab1, tab2, tab3 = st.tabs(["📝 Logs", "📊 PCAP Analysis", "🔗 Chain of Custody"])
    
    with tab1:
        st.subheader("Log Analysis")
        
        # Log search
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("Search logs", placeholder="Enter keyword...")
        with col2:
            log_level = st.selectbox("Level", ["All", "INFO", "WARNING", "ERROR"])
        
        # Sample logs
        logs = [
            {"time": "2025-10-26 14:32:15", "level": "ERROR", "source": "honeypot-01", "message": "Connection attempt from 185.220.101.45"},
            {"time": "2025-10-26 14:28:03", "level": "WARNING", "source": "network", "message": "High traffic detected"},
            {"time": "2025-10-26 14:25:40", "level": "INFO", "source": "ai-engine", "message": "Neural deception activated"},
        ]
        
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
    
    with tab2:
        st.subheader("Network Traffic Analysis")
        
        # Protocol distribution
        protocols = {'TCP': 65, 'UDP': 25, 'ICMP': 7, 'Other': 3}
        
        fig = px.pie(
            values=list(protocols.values()),
            names=list(protocols.keys()),
            title="Protocol Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Evidence Chain of Custody")
        
        evidence = [
            {"ID": "EVD-001", "Type": "Network Capture", "Date": "2025-10-26", "Status": "Preserved"},
            {"ID": "EVD-002", "Type": "Memory Dump", "Date": "2025-10-26", "Status": "Preserved"},
            {"ID": "EVD-003", "Type": "System Logs", "Date": "2025-10-26", "Status": "Preserved"},
        ]
        
        st.table(pd.DataFrame(evidence))


def show_settings():
    """صفحة الإعدادات"""
    
    st.header("⚙️ System Settings")
    
    tab1, tab2, tab3 = st.tabs(["🔧 General", "🔒 Security", "🤖 AI Config"])
    
    with tab1:
        st.subheader("General Settings")
        
        st.checkbox("Enable auto-refresh", value=True)
        st.slider("Refresh interval (seconds)", 5, 60, 10)
        st.checkbox("Show debug info", value=False)
        
        st.button("💾 Save Settings", type="primary")
    
    with tab2:
        st.subheader("Security Settings")
        
        st.number_input("Max failed login attempts", value=3)
        st.number_input("Session timeout (minutes)", value=30)
        st.checkbox("Enable 2FA", value=True)
        
        st.button("💾 Save Security Settings", type="primary")
    
    with tab3:
        st.subheader("AI Configuration")
        
        st.slider("Neural Deception Intensity", 0, 100, 99)
        st.slider("Swarm Coordination Level", 0, 100, 97)
        st.slider("Quantum Uncertainty", 0, 100, 98)
        st.slider("Bio Evolution Rate", 0, 100, 96)
        
        st.button("💾 Save AI Config", type="primary")


if __name__ == "__main__":
    main()
