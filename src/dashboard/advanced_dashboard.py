"""
🗺️ Advanced Dashboard - Geographic Maps + AI Analysis
Dashboard متقدم بخريطة جغرافية وتحليلات ذكية
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

# تكوين الصفحة
st.set_page_config(
    page_title="🎭 Cyber Mirage - Advanced Analytics",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_refresh = datetime.now()
    st.session_state.auto_refresh = True
    st.session_state.geo_cache = {}

# CSS مخصص متقدم
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
    }
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #00ff00;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
        box-shadow: 0 0 10px #00ff00;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.1); }
    }
    .attack-alert {
        background: linear-gradient(90deg, #ff6b6b, #ff8e53);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        font-weight: bold;
        animation: slideIn 0.5s;
    }
    @keyframes slideIn {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }
    .service-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.2rem;
    }
    .ssh-badge { background: #667eea; color: white; }
    .http-badge { background: #f093fb; color: white; }
    .ftp-badge { background: #4facfe; color: white; }
    .db-badge { background: #43e97b; color: white; }
</style>
""", unsafe_allow_html=True)

# Database Connection
@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'postgres'),
            database=os.getenv('POSTGRES_DB', 'cyber_mirage'),
            user=os.getenv('POSTGRES_USER', 'cybermirage'),
            password=os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')
        )
        return conn
    except Exception as e:
        st.error(f"❌ Database Error: {e}")
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
        st.error(f"❌ Redis Error: {e}")
        return None

def get_geo_location(ip):
    """جلب الموقع الجغرافي للـ IP"""
    if ip in st.session_state.geo_cache:
        return st.session_state.geo_cache[ip]
    
    try:
        # استخدام ip-api.com (مجاني)
        response = requests.get(f'http://ip-api.com/json/{ip}?fields=country,countryCode,city,lat,lon,isp', timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') != 'fail':
                geo_data = {
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', 'UN'),
                    'city': data.get('city', 'Unknown'),
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0),
                    'isp': data.get('isp', 'Unknown')
                }
                st.session_state.geo_cache[ip] = geo_data
                return geo_data
    except:
        pass
    
    # Default fallback
    default = {'country': 'Unknown', 'country_code': 'UN', 'city': 'Unknown', 'lat': 0, 'lon': 0, 'isp': 'Unknown'}
    st.session_state.geo_cache[ip] = default
    return default

def get_attack_stats():
    """إحصائيات متقدمة"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        stats = {}
        
        # Total attacks
        cursor.execute("SELECT COUNT(*) FROM attack_sessions;")
        stats['total'] = cursor.fetchone()[0]
        
        # Today attacks
        cursor.execute("SELECT COUNT(*) FROM attack_sessions WHERE start_time > NOW() - INTERVAL '24 hours';")
        stats['today'] = cursor.fetchone()[0]
        
        # Last hour
        cursor.execute("SELECT COUNT(*) FROM attack_sessions WHERE start_time > NOW() - INTERVAL '1 hour';")
        stats['last_hour'] = cursor.fetchone()[0]
        
        # Detection rate
        cursor.execute("""
            SELECT COUNT(CASE WHEN detected = true THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)
            FROM attack_sessions;
        """)
        stats['detection_rate'] = cursor.fetchone()[0] or 100.0
        
        # Attacks by service (from attacker_name pattern)
        cursor.execute("""
            SELECT attacker_name, COUNT(*) as count
            FROM attack_sessions
            GROUP BY attacker_name
            ORDER BY count DESC
            LIMIT 100;
        """)
        stats['by_service'] = cursor.fetchall()
        
        # Unique attackers
        cursor.execute("SELECT COUNT(DISTINCT origin) FROM attack_sessions WHERE origin IS NOT NULL;")
        stats['unique_attackers'] = cursor.fetchone()[0]
        
        cursor.close()
        return stats
    except Exception as e:
        st.error(f"Stats Error: {e}")
        return None

def get_geographic_data():
    """بيانات جغرافية للهجمات"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT origin, COUNT(*) as attack_count
            FROM attack_sessions
            WHERE origin IS NOT NULL AND origin != ''
            GROUP BY origin
            ORDER BY attack_count DESC
            LIMIT 50;
        """)
        results = cursor.fetchall()
        cursor.close()
        
        geo_data = []
        for ip, count in results:
            geo = get_geo_location(ip)
            if geo['lat'] != 0 and geo['lon'] != 0:
                geo_data.append({
                    'ip': ip,
                    'count': count,
                    'country': geo['country'],
                    'city': geo['city'],
                    'lat': geo['lat'],
                    'lon': geo['lon'],
                    'isp': geo['isp']
                })
        
        return geo_data
    except Exception as e:
        st.error(f"Geo Error: {e}")
        return []

def get_service_breakdown():
    """تحليل الهجمات حسب الخدمة"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT attacker_name, COUNT(*) as count
            FROM attack_sessions
            GROUP BY attacker_name;
        """)
        results = cursor.fetchall()
        cursor.close()
        
        services = {'SSH': 0, 'HTTP': 0, 'FTP': 0, 'MySQL': 0, 'PostgreSQL': 0, 'Telnet': 0, 'Other': 0}
        
        for name, count in results:
            if 'SSH' in name.upper():
                services['SSH'] += count
            elif 'HTTP' in name.upper() or 'HTTPS' in name.upper():
                services['HTTP'] += count
            elif 'FTP' in name.upper():
                services['FTP'] += count
            elif 'MYSQL' in name.upper():
                services['MySQL'] += count
            elif 'POSTGRES' in name.upper():
                services['PostgreSQL'] += count
            elif 'TELNET' in name.upper():
                services['Telnet'] += count
            else:
                services['Other'] += count
        
        return {k: v for k, v in services.items() if v > 0}
    except Exception as e:
        st.error(f"Service breakdown error: {e}")
        return {}

def get_recent_attacks(limit=20):
    """أحدث الهجمات مع معلومات جغرافية"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = f"""
            SELECT 
                attacker_name,
                origin,
                start_time,
                detected
            FROM attack_sessions 
            WHERE origin IS NOT NULL
            ORDER BY start_time DESC 
            LIMIT {limit};
        """
        df = pd.read_sql(query, conn)
        
        # Add geo info
        if not df.empty:
            df['country'] = df['origin'].apply(lambda ip: get_geo_location(ip)['country'])
            df['city'] = df['origin'].apply(lambda ip: get_geo_location(ip)['city'])
        
        return df
    except Exception as e:
        st.error(f"Recent attacks error: {e}")
        return pd.DataFrame()

def main():
    # Header
    st.markdown('<h1 class="main-header">🗺️ Cyber Mirage - Geographic Intelligence</h1>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center;"><span class="live-indicator"></span> <b>LIVE TRACKING</b> - Real-time Attack Map</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
        if auto_refresh:
            refresh_interval = st.slider("Refresh (seconds)", 5, 60, 15)
        
        st.markdown("---")
        st.markdown("### 📊 System Status")
        
        conn = get_db_connection()
        redis_conn = get_redis_connection()
        
        if conn:
            st.success("✅ PostgreSQL Online")
        else:
            st.error("❌ PostgreSQL Offline")
        
        if redis_conn:
            st.success("✅ Redis Online")
        else:
            st.error("❌ Redis Offline")
        
        st.markdown("---")
        st.markdown(f"🕒 **Last Update:** {datetime.now().strftime('%H:%M:%S')}")
    
    # Get data
    stats = get_attack_stats()
    
    if stats:
        # Top metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🎯 Total Attacks", f"{stats['total']:,}", delta=f"+{stats['today']} today")
        
        with col2:
            st.metric("🔥 Last Hour", stats['last_hour'], delta="Live")
        
        with col3:
            st.metric("🛡️ Detection Rate", f"{stats['detection_rate']:.1f}%", delta="100%")
        
        with col4:
            st.metric("👥 Unique IPs", stats['unique_attackers'], delta=f"{stats['today']} new")
        
        with col5:
            st.metric("⚡ Active Now", stats['last_hour'], delta="Real-time")
    
    st.markdown("---")
    
    # Geographic Map
    st.subheader("🌍 Live Attack Map - Global Threat Intelligence")
    
    geo_data = get_geographic_data()
    
    if geo_data:
        df_geo = pd.DataFrame(geo_data)
        
        # Create map
        fig = px.scatter_mapbox(
            df_geo,
            lat='lat',
            lon='lon',
            size='count',
            color='count',
            hover_name='country',
            hover_data={'ip': True, 'city': True, 'count': True, 'isp': True, 'lat': False, 'lon': False},
            color_continuous_scale='Reds',
            size_max=30,
            zoom=1.2,
            height=500,
            title='Attack Sources Worldwide'
        )
        
        fig.update_layout(
            mapbox_style="carto-darkmatter",
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top countries
        country_counts = Counter([item['country'] for item in geo_data])
        top_countries = country_counts.most_common(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌐 Top Attack Countries")
            for i, (country, count) in enumerate(top_countries[:5], 1):
                st.markdown(f"**{i}.** 🏴 {country}: **{count}** attacks")
        
        with col2:
            st.markdown("### 🎯 Attack Distribution")
            df_countries = pd.DataFrame(top_countries, columns=['Country', 'Attacks'])
            fig_pie = px.pie(df_countries, values='Attacks', names='Country', hole=0.4)
            fig_pie.update_layout(height=300, showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("🗺️ No geographic data yet. Attacks will appear here in real-time!")
    
    st.markdown("---")
    
    # Service Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Service Breakdown")
        services = get_service_breakdown()
        
        if services:
            df_services = pd.DataFrame(list(services.items()), columns=['Service', 'Attacks'])
            fig = px.bar(
                df_services,
                x='Service',
                y='Attacks',
                color='Attacks',
                color_continuous_scale='Blues',
                title='Attacks by Honeypot Service'
            )
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Service badges
            st.markdown("### Service Status:")
            for service, count in services.items():
                badge_class = f"{service.lower()}-badge" if service.lower() in ['ssh', 'http', 'ftp'] else 'service-badge'
                st.markdown(f'<span class="service-badge {badge_class}">{service}: {count} attacks</span>', unsafe_allow_html=True)
        else:
            st.info("No service data available")
    
    with col2:
        st.subheader("📈 Attack Timeline (24h)")
        conn = get_db_connection()
        if conn:
            try:
                query = """
                    SELECT DATE_TRUNC('hour', start_time) as hour, COUNT(*) as count
                    FROM attack_sessions
                    WHERE start_time > NOW() - INTERVAL '24 hours'
                    GROUP BY hour
                    ORDER BY hour;
                """
                df_timeline = pd.read_sql(query, conn)
                
                if not df_timeline.empty:
                    fig = px.area(
                        df_timeline,
                        x='hour',
                        y='count',
                        title='Hourly Attack Frequency',
                        labels={'count': 'Attacks', 'hour': 'Time'}
                    )
                    fig.update_traces(fill='tozeroy', line_color='#667eea')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No attacks in last 24 hours")
            except Exception as e:
                st.error(f"Timeline error: {e}")
    
    st.markdown("---")
    
    # Recent Attacks Table
    st.subheader("🚨 Recent Attacks - Live Feed")
    recent = get_recent_attacks(25)
    
    if not recent.empty:
        recent['start_time'] = pd.to_datetime(recent['start_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        recent['detected'] = recent['detected'].apply(lambda x: '✅ Detected' if x else '❌ Missed')
        recent['location'] = recent['city'] + ', ' + recent['country']
        
        display_df = recent[['start_time', 'origin', 'location', 'attacker_name', 'detected']]
        display_df.columns = ['⏰ Time', '🌐 IP Address', '📍 Location', '🎯 Target Service', '🛡️ Status']
        
        st.dataframe(display_df, use_container_width=True, height=400)
    else:
        st.info("📭 No attacks recorded. System is monitoring...")
        st.markdown("""
        **Test the system:**
        ```bash
        ssh -p 2222 root@13.53.131.159
        curl http://13.53.131.159:8080
        ftp 13.53.131.159 2121
        ```
        """)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
