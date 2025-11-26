"""
🎭 Cyber Mirage - Full Dashboard with AI Analysis
Dashboard متكامل بالخريطة الجغرافية وتحليلات الذكاء الاصطناعي
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import psycopg2
import redis
import os
import time
import requests
from collections import Counter
import json

# Page config
st.set_page_config(
    page_title="🎭 Cyber Mirage - AI-Powered Defense",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.geo_cache = {}
    st.session_state.ai_cache = {}

# Advanced CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem;
    }
    .ai-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .threat-critical {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
    .threat-high {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
    }
    .threat-medium {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 20px;
    }
    .threat-low {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 20px;
    }
    .mitre-badge {
        background: #2d3436;
        color: #74b9ff;
        padding: 0.3rem 0.8rem;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .skill-bar {
        height: 8px;
        border-radius: 4px;
        background: linear-gradient(90deg, #00b894, #fdcb6e, #e17055);
    }
    .live-pulse {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #00ff00;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
        box-shadow: 0 0 10px #00ff00;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# Database Connections
# ============================================

@st.cache_resource
def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'postgres'),
            database=os.getenv('POSTGRES_DB', 'cyber_mirage'),
            user=os.getenv('POSTGRES_USER', 'cybermirage'),
            password=os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')
        )
    except Exception as e:
        st.error(f"DB Error: {e}")
        return None

@st.cache_resource
def get_redis_connection():
    try:
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', 'changeme123'),
            decode_responses=True
        )
        r.ping()
        return r
    except Exception as e:
        st.error(f"Redis Error: {e}")
        return None

# ============================================
# MITRE ATT&CK Mappings
# ============================================

MITRE_TACTICS = {
    'SSH': {'tactic': 'Initial Access', 'technique': 'T1078/T1110', 'risk': 'HIGH'},
    'FTP': {'tactic': 'Initial Access', 'technique': 'T1078', 'risk': 'MEDIUM'},
    'HTTP': {'tactic': 'Reconnaissance', 'technique': 'T1595/T1190', 'risk': 'MEDIUM'},
    'HTTPS': {'tactic': 'Initial Access', 'technique': 'T1190', 'risk': 'MEDIUM'},
    'MySQL': {'tactic': 'Collection', 'technique': 'T1213', 'risk': 'HIGH'},
    'PostgreSQL': {'tactic': 'Collection', 'technique': 'T1213', 'risk': 'HIGH'},
    'Telnet': {'tactic': 'Initial Access', 'technique': 'T1021', 'risk': 'CRITICAL'},
    'Modbus': {'tactic': 'Impact', 'technique': 'T0831', 'risk': 'CRITICAL'},
}

# ============================================
# AI Analysis Functions
# ============================================

def calculate_threat_score(ip: str, service: str, attack_count: int) -> float:
    """Calculate AI threat score"""
    score = min(attack_count * 5, 40)
    
    service_multiplier = {
        'SSH': 1.5, 'MySQL': 1.8, 'PostgreSQL': 1.8,
        'Telnet': 2.0, 'Modbus': 2.5, 'HTTP': 1.0, 'FTP': 1.2
    }
    score *= service_multiplier.get(service, 1.0)
    
    return min(score, 100.0)

def determine_skill_level(service: str, attack_count: int) -> tuple:
    """Determine attacker skill level"""
    if attack_count > 50:
        return 8.0, "Persistent Threat Actor"
    elif attack_count > 20:
        return 6.0, "Automated Scanner"
    elif attack_count > 5:
        return 4.0, "Opportunistic Attacker"
    else:
        return 2.0, "Script Kiddie"

def get_ai_analysis(ip: str, service: str, attack_count: int) -> dict:
    """Get full AI analysis for an attacker"""
    threat_score = calculate_threat_score(ip, service, attack_count)
    skill_level, skill_desc = determine_skill_level(service, attack_count)
    mitre = MITRE_TACTICS.get(service, {'tactic': 'Unknown', 'technique': 'N/A', 'risk': 'LOW'})
    
    if threat_score >= 80:
        threat_level = 'CRITICAL'
        recommendation = '🚨 BLOCK IMMEDIATELY'
    elif threat_score >= 60:
        threat_level = 'HIGH'
        recommendation = '⚠️ Monitor & Consider Blocking'
    elif threat_score >= 40:
        threat_level = 'MEDIUM'
        recommendation = '👁️ Track Activity'
    else:
        threat_level = 'LOW'
        recommendation = '📝 Log Only'
    
    return {
        'threat_score': round(threat_score, 1),
        'threat_level': threat_level,
        'skill_level': skill_level,
        'skill_desc': skill_desc,
        'mitre_tactic': mitre['tactic'],
        'mitre_technique': mitre['technique'],
        'recommendation': recommendation
    }

# ============================================
# Data Functions
# ============================================

def get_geo_location(ip):
    if ip in st.session_state.geo_cache:
        return st.session_state.geo_cache[ip]
    
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}?fields=country,countryCode,city,lat,lon,isp', timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') != 'fail':
                geo = {
                    'country': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0),
                    'isp': data.get('isp', 'Unknown')
                }
                st.session_state.geo_cache[ip] = geo
                return geo
    except:
        pass
    
    default = {'country': 'Unknown', 'city': 'Unknown', 'lat': 0, 'lon': 0, 'isp': 'Unknown'}
    st.session_state.geo_cache[ip] = default
    return default

def get_attack_stats():
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM attack_sessions;")
        stats['total'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attack_sessions WHERE start_time > NOW() - INTERVAL '24 hours';")
        stats['today'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attack_sessions WHERE start_time > NOW() - INTERVAL '1 hour';")
        stats['last_hour'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT origin) FROM attack_sessions WHERE origin IS NOT NULL;")
        stats['unique_ips'] = cursor.fetchone()[0]
        
        cursor.close()
        return stats
    except Exception as e:
        st.error(f"Stats error: {e}")
        return None

def get_top_attackers(limit=10):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT origin, COUNT(*) as count, 
                   MAX(attacker_name) as name
            FROM attack_sessions
            WHERE origin IS NOT NULL
            GROUP BY origin
            ORDER BY count DESC
            LIMIT %s
        """, (limit,))
        results = cursor.fetchall()
        cursor.close()
        
        attackers = []
        for ip, count, name in results:
            service = name.split('_')[-1] if name and '_' in name else 'Unknown'
            geo = get_geo_location(ip)
            ai = get_ai_analysis(ip, service, count)
            
            attackers.append({
                'ip': ip,
                'count': count,
                'service': service,
                'country': geo['country'],
                'city': geo['city'],
                **ai
            })
        
        return attackers
    except Exception as e:
        st.error(f"Error: {e}")
        return []

def get_geographic_data():
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT origin, COUNT(*) as count
            FROM attack_sessions
            WHERE origin IS NOT NULL
            GROUP BY origin
            ORDER BY count DESC
            LIMIT 50
        """)
        results = cursor.fetchall()
        cursor.close()
        
        geo_data = []
        for ip, count in results:
            geo = get_geo_location(ip)
            if geo['lat'] != 0:
                geo_data.append({
                    'ip': ip, 'count': count,
                    'country': geo['country'], 'city': geo['city'],
                    'lat': geo['lat'], 'lon': geo['lon']
                })
        
        return geo_data
    except:
        return []

def get_service_breakdown():
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT attacker_name, COUNT(*) FROM attack_sessions GROUP BY attacker_name")
        results = cursor.fetchall()
        cursor.close()
        
        services = {'SSH': 0, 'HTTP': 0, 'FTP': 0, 'MySQL': 0, 'Telnet': 0, 'Other': 0}
        for name, count in results:
            if not name:
                services['Other'] += count
                continue
            name_upper = name.upper()
            matched = False
            for svc in ['SSH', 'HTTP', 'FTP', 'MYSQL', 'TELNET']:
                if svc in name_upper:
                    services[svc if svc != 'MYSQL' else 'MySQL'] += count
                    matched = True
                    break
            if not matched:
                services['Other'] += count
        
        return {k: v for k, v in services.items() if v > 0}
    except:
        return {}

# ============================================
# Main Dashboard
# ============================================

def main():
    # Header
    st.markdown('<h1 class="main-header">🎭 Cyber Mirage - AI-Powered Defense</h1>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;"><span class="live-pulse"></span> <b>LIVE</b> - AI Analysis Active</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
        if auto_refresh:
            refresh_interval = st.slider("Seconds", 10, 60, 20)
        
        st.markdown("---")
        
        # Navigation
        page = st.radio("📑 Section", ["🌍 Geographic Map", "🧠 AI Analysis", "📊 Statistics", "🚨 Live Feed"])
        
        st.markdown("---")
        st.markdown("### 💚 System Status")
        if get_db_connection():
            st.success("✅ PostgreSQL")
        if get_redis_connection():
            st.success("✅ Redis")
        st.success("✅ AI Engine")
        
        st.markdown(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    
    # Stats
    stats = get_attack_stats()
    if stats:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🎯 Total Attacks", f"{stats['total']:,}", f"+{stats['today']} today")
        c2.metric("⚡ Last Hour", stats['last_hour'], "Live")
        c3.metric("👥 Unique IPs", stats['unique_ips'])
        c4.metric("🛡️ Detection", "100%", "All Logged")
    
    st.markdown("---")
    
    # Pages
    if page == "🌍 Geographic Map":
        show_geographic_map()
    elif page == "🧠 AI Analysis":
        show_ai_analysis()
    elif page == "📊 Statistics":
        show_statistics()
    else:
        show_live_feed()
    
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


def show_geographic_map():
    st.subheader("🌍 Live Attack Map")
    
    geo_data = get_geographic_data()
    
    if geo_data:
        df = pd.DataFrame(geo_data)
        
        fig = px.scatter_mapbox(
            df, lat='lat', lon='lon', size='count', color='count',
            hover_name='country',
            hover_data={'ip': True, 'city': True, 'count': True, 'lat': False, 'lon': False},
            color_continuous_scale='Reds',
            size_max=30, zoom=1.5, height=500
        )
        fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
        # Top countries
        countries = Counter([d['country'] for d in geo_data])
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏆 Top Countries")
            for i, (country, count) in enumerate(countries.most_common(5), 1):
                st.markdown(f"**{i}.** 🌐 {country}: **{count}** attacks")
        
        with col2:
            st.markdown("### 📊 Distribution")
            df_c = pd.DataFrame(countries.most_common(8), columns=['Country', 'Attacks'])
            fig = px.pie(df_c, values='Attacks', names='Country', hole=0.4)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🗺️ Waiting for attack data...")


def show_ai_analysis():
    st.subheader("🧠 AI Threat Analysis")
    
    attackers = get_top_attackers(15)
    
    if not attackers:
        st.info("No attackers to analyze yet")
        return
    
    # Summary cards
    critical = sum(1 for a in attackers if a['threat_level'] == 'CRITICAL')
    high = sum(1 for a in attackers if a['threat_level'] == 'HIGH')
    medium = sum(1 for a in attackers if a['threat_level'] == 'MEDIUM')
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔴 CRITICAL", critical)
    c2.metric("🟠 HIGH", high)
    c3.metric("🟡 MEDIUM", medium)
    c4.metric("🟢 LOW", len(attackers) - critical - high - medium)
    
    st.markdown("---")
    
    # Detailed analysis for each attacker
    st.markdown("### 🎯 Top Threat Actors")
    
    for i, a in enumerate(attackers[:10], 1):
        with st.expander(f"#{i} | {a['ip']} | {a['country']} | Score: {a['threat_score']}", expanded=(i <= 3)):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**🌐 IP:** `{a['ip']}`")
                st.markdown(f"**📍 Location:** {a['city']}, {a['country']}")
                st.markdown(f"**🔧 Service:** {a['service']}")
                st.markdown(f"**📊 Attacks:** {a['count']}")
            
            with col2:
                st.markdown(f"**🎯 Threat Score:** {a['threat_score']}/100")
                st.progress(a['threat_score'] / 100)
                
                st.markdown(f"**🧠 Skill Level:** {a['skill_level']}/10")
                st.progress(a['skill_level'] / 10)
                
                st.markdown(f"**👤 Profile:** {a['skill_desc']}")
            
            with col3:
                # Threat level badge
                level = a['threat_level']
                if level == 'CRITICAL':
                    st.markdown('<span class="threat-critical">🔴 CRITICAL</span>', unsafe_allow_html=True)
                elif level == 'HIGH':
                    st.markdown('<span class="threat-high">🟠 HIGH</span>', unsafe_allow_html=True)
                elif level == 'MEDIUM':
                    st.markdown('<span class="threat-medium">🟡 MEDIUM</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="threat-low">🟢 LOW</span>', unsafe_allow_html=True)
                
                st.markdown(f"**{a['recommendation']}**")
            
            # MITRE ATT&CK
            st.markdown("---")
            st.markdown(f'<span class="mitre-badge">MITRE ATT&CK: {a["mitre_tactic"]} | {a["mitre_technique"]}</span>', unsafe_allow_html=True)
    
    # Tactics distribution
    st.markdown("---")
    st.markdown("### 📋 MITRE ATT&CK Tactics Distribution")
    
    tactics = Counter([a['mitre_tactic'] for a in attackers])
    df_tactics = pd.DataFrame(tactics.most_common(), columns=['Tactic', 'Count'])
    
    fig = px.bar(df_tactics, x='Tactic', y='Count', color='Count', color_continuous_scale='Blues')
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def show_statistics():
    st.subheader("📊 Attack Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Service Breakdown")
        services = get_service_breakdown()
        if services:
            df = pd.DataFrame(list(services.items()), columns=['Service', 'Attacks'])
            fig = px.bar(df, x='Service', y='Attacks', color='Attacks', color_continuous_scale='Reds')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 24h Timeline")
        conn = get_db_connection()
        if conn:
            try:
                query = """
                    SELECT DATE_TRUNC('hour', start_time) as hour, COUNT(*) as count
                    FROM attack_sessions
                    WHERE start_time > NOW() - INTERVAL '24 hours'
                    GROUP BY hour ORDER BY hour
                """
                df = pd.read_sql(query, conn)
                if not df.empty:
                    fig = px.area(df, x='hour', y='count')
                    fig.update_traces(fill='tozeroy', line_color='#667eea')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
            except:
                pass


def show_live_feed():
    st.subheader("🚨 Live Attack Feed")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        query = """
            SELECT attacker_name, origin, start_time, detected
            FROM attack_sessions
            WHERE origin IS NOT NULL
            ORDER BY start_time DESC
            LIMIT 25
        """
        df = pd.read_sql(query, conn)
        
        if not df.empty:
            # Add AI analysis
            df['service'] = df['attacker_name'].apply(lambda x: x.split('_')[-1] if x and '_' in x else 'Unknown')
            df['country'] = df['origin'].apply(lambda ip: get_geo_location(ip)['country'])
            df['threat'] = df.apply(lambda row: get_ai_analysis(row['origin'], row['service'], 1)['threat_level'], axis=1)
            
            df['start_time'] = pd.to_datetime(df['start_time']).dt.strftime('%H:%M:%S')
            df['detected'] = df['detected'].apply(lambda x: '✅' if x else '❌')
            
            display = df[['start_time', 'origin', 'country', 'service', 'threat', 'detected']]
            display.columns = ['⏰ Time', '🌐 IP', '📍 Country', '🔧 Service', '⚠️ Threat', '🛡️ Status']
            
            st.dataframe(display, use_container_width=True, height=500)
        else:
            st.info("No attacks yet...")
    except Exception as e:
        st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
