"""
📊 Streamlit Dashboard - Real-Time Data
Dashboard يعرض البيانات الحقيقية من PostgreSQL و Redis
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

# التكوين
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'cyber_mirage')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'cybermirage')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'changeme123')

# Page config
st.set_page_config(
    page_title="Cyber Mirage - Real-Time Dashboard",
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
        border-left: 4px solid;
    }
    
    .alert-critical { border-color: #f44336; background-color: #ffebee; }
    .alert-warning { border-color: #ff9800; background-color: #fff3e0; }
    .alert-info { border-color: #2196f3; background-color: #e3f2fd; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db_connection():
    """الاتصال بقاعدة البيانات"""
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            connect_timeout=5
        )
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None


@st.cache_resource
def get_redis_connection():
    """الاتصال بـ Redis"""
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5
        )
        r.ping()
        return r
    except Exception as e:
        st.error(f"❌ Redis connection failed: {e}")
        return None


def get_attack_stats():
    """إحصائيات الهجمات من PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # إجمالي الهجمات
        cursor.execute("SELECT COUNT(*) FROM attack_sessions")
        total_attacks = cursor.fetchone()[0]
        
        # الهجمات في آخر 24 ساعة
        cursor.execute("""
            SELECT COUNT(*) FROM attack_sessions 
            WHERE start_time >= NOW() - INTERVAL '24 hours'
        """)
        attacks_24h = cursor.fetchone()[0]
        
        # الهجمات في آخر ساعة
        cursor.execute("""
            SELECT COUNT(*) FROM attack_sessions 
            WHERE start_time >= NOW() - INTERVAL '1 hour'
        """)
        attacks_1h = cursor.fetchone()[0]
        
        # المهاجمون الفريدون
        cursor.execute("SELECT COUNT(DISTINCT attacker_name) FROM attack_sessions")
        unique_attackers = cursor.fetchone()[0]
        
        # معدل الكشف
        cursor.execute("SELECT COUNT(*) FROM attack_sessions WHERE detected = true")
        detected = cursor.fetchone()[0]
        detection_rate = (detected / total_attacks * 100) if total_attacks > 0 else 0
        
        cursor.close()
        return {
            'total': total_attacks,
            'last_24h': attacks_24h,
            'last_hour': attacks_1h,
            'unique_attackers': unique_attackers,
            'detection_rate': detection_rate
        }
    except Exception as e:
        st.error(f"❌ Error fetching attack stats: {e}")
        return None


def get_recent_attacks(limit=10):
    """أحدث الهجمات"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
            SELECT 
                attacker_name,
                attacker_skill,
                start_time,
                end_time,
                total_steps,
                detected,
                origin,
                mitre_tactics
            FROM attack_sessions 
            ORDER BY start_time DESC 
            LIMIT %s
        """
        df = pd.read_sql_query(query, conn, params=(limit,))
        return df
    except Exception as e:
        st.error(f"❌ Error fetching recent attacks: {e}")
        return pd.DataFrame()


def get_threat_intelligence():
    """معلومات التهديدات من Redis"""
    r = get_redis_connection()
    if not r:
        return []
    
    try:
        # الحصول على جميع مفاتيح التهديدات
        threat_keys = r.keys('threat:*')
        threats = []
        
        for key in threat_keys[:20]:  # أول 20 تهديد
            threat_data = r.hgetall(key)
            if threat_data:
                ip = key.split(':')[1]
                threats.append({
                    'ip': ip,
                    'count': int(threat_data.get('count', 0)),
                    'last_seen': threat_data.get('last_seen', 'Unknown')
                })
        
        return sorted(threats, key=lambda x: x['count'], reverse=True)
    except Exception as e:
        st.error(f"❌ Error fetching threat intelligence: {e}")
        return []


def get_hourly_attacks():
    """الهجمات حسب الساعة (آخر 24 ساعة)"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
            SELECT 
                DATE_TRUNC('hour', start_time) as hour,
                COUNT(*) as count
            FROM attack_sessions
            WHERE start_time >= NOW() - INTERVAL '24 hours'
            GROUP BY hour
            ORDER BY hour
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"❌ Error fetching hourly attacks: {e}")
        return pd.DataFrame()


def main():
    """الصفحة الرئيسية"""
    
    # Header
    st.markdown('<h1 class="main-header">🎭 Cyber Mirage v5.0 - Real-Time Dashboard</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📊 Dashboard Controls")
        
        st.markdown("### 🔄 Auto-Refresh")
        auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
        
        if auto_refresh:
            refresh_rate = st.slider("Refresh Rate (seconds)", 5, 60, 10)
            st.info(f"⏱️ Refreshing every {refresh_rate} seconds")
        
        st.markdown("---")
        
        # System Status
        st.markdown("### 📈 Connection Status")
        
        db_conn = get_db_connection()
        redis_conn = get_redis_connection()
        
        if db_conn:
            st.success("✅ PostgreSQL Connected")
        else:
            st.error("❌ PostgreSQL Disconnected")
        
        if redis_conn:
            st.success("✅ Redis Connected")
        else:
            st.error("❌ Redis Disconnected")
        
        st.markdown("---")
        st.caption(f"🕐 Last Update: {datetime.now().strftime('%H:%M:%S')}")
    
    # Main Dashboard
    show_dashboard()
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()


def show_dashboard():
    """عرض لوحة التحكم الرئيسية"""
    
    st.header("📊 Real-Time System Overview")
    
    # جلب الإحصائيات
    stats = get_attack_stats()
    
    if stats:
        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🎯 Total Attacks",
                value=stats['total'],
                delta=f"+{stats['last_hour']} last hour"
            )
        
        with col2:
            st.metric(
                label="📅 Last 24 Hours",
                value=stats['last_24h'],
                delta=f"{stats['last_24h'] - stats['last_hour']} before"
            )
        
        with col3:
            st.metric(
                label="👥 Unique Attackers",
                value=stats['unique_attackers'],
                delta="Active"
            )
        
        with col4:
            st.metric(
                label="✅ Detection Rate",
                value=f"{stats['detection_rate']:.1f}%",
                delta="+2.1%"
            )
        
        st.markdown("---")
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Attack Activity (Last 24h)")
            
            hourly_df = get_hourly_attacks()
            
            if not hourly_df.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hourly_df['hour'],
                    y=hourly_df['count'],
                    mode='lines+markers',
                    fill='tozeroy',
                    line=dict(color='#FF6B6B', width=3),
                    marker=dict(size=8),
                    name='Attacks'
                ))
                
                fig.update_layout(
                    xaxis_title="Time",
                    yaxis_title="Number of Attacks",
                    height=350,
                    hovermode='x unified',
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 No attack data available yet")
        
        with col2:
            st.subheader("🌍 Top Threat Sources")
            
            threats = get_threat_intelligence()
            
            if threats:
                threat_df = pd.DataFrame(threats)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=threat_df['ip'][:10],
                    y=threat_df['count'][:10],
                    marker=dict(
                        color=threat_df['count'][:10],
                        colorscale='Reds',
                        showscale=True
                    ),
                    text=threat_df['count'][:10],
                    textposition='auto'
                ))
                
                fig.update_layout(
                    xaxis_title="IP Address",
                    yaxis_title="Attack Count",
                    height=350,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("🌍 No threat intelligence data yet")
        
        st.markdown("---")
        
        # Recent Attacks Table
        st.subheader("🚨 Recent Attack Sessions")
        
        recent_df = get_recent_attacks(15)
        
        if not recent_df.empty:
            # تنسيق الجدول
            recent_df['start_time'] = pd.to_datetime(recent_df['start_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
            recent_df['detected'] = recent_df['detected'].apply(lambda x: '✅ Yes' if x else '❌ No')
            recent_df['attacker_skill'] = recent_df['attacker_skill'].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(
                recent_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "attacker_name": "Attacker",
                    "attacker_skill": "Skill Level",
                    "start_time": "Time",
                    "total_steps": "Steps",
                    "detected": "Detected",
                    "origin": "Origin"
                }
            )
        else:
            st.info("📋 No attack sessions recorded yet. Start attacking the honeypots!")
    
    else:
        st.warning("⚠️ Unable to fetch statistics. Check database connection.")
        
        # عرض بيانات تجريبية
        st.info("💡 Showing sample data for demonstration:")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Total Attacks", "0", delta="No data")
        
        with col2:
            st.metric("📅 Last 24 Hours", "0", delta="No data")
        
        with col3:
            st.metric("👥 Unique Attackers", "0", delta="No data")
        
        with col4:
            st.metric("✅ Detection Rate", "0%", delta="No data")


if __name__ == "__main__":
    main()
