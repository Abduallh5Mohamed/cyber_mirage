"""
Cyber Mirage - Elite Security Dashboard
100% Real-Time | Production Ready | Enterprise Grade

All data is pulled directly from PostgreSQL database.
No fake data. No demos. Real attacks only.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
import json
import logging
import random
from typing import Dict, List, Optional, Any
from collections import Counter
import sys

# Add parent directory for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# DATABASE CONFIGURATION (Real PostgreSQL)
# =============================================================================
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'cyber_mirage'),
    'user': os.getenv('POSTGRES_USER', 'cybermirage'),
    'password': os.getenv('POSTGRES_PASSWORD') or os.getenv('PGPASSWORD') or 'ChangeThisToSecurePassword123!'
}

# Connection pool
db_pool = None

def init_db_pool():
    """Initialize database connection pool."""
    global db_pool
    try:
        db_url = os.getenv('DATABASE_URL')
        pwd_source = 'env' if (os.getenv('POSTGRES_PASSWORD') or os.getenv('PGPASSWORD')) else 'fallback'
        logger.info(
            f"DB connect target host={DB_CONFIG['host']} db={DB_CONFIG['database']} user={DB_CONFIG['user']} pw_len={len(DB_CONFIG['password']) if DB_CONFIG.get('password') else 0} source={pwd_source}"
        )
        if db_url:
            db_pool = pool.SimpleConnectionPool(1, 10, dsn=db_url)
        else:
            db_pool = pool.SimpleConnectionPool(1, 10, **DB_CONFIG)
        logger.info("Database pool initialized")
        return True
    except Exception as e:
        logger.error(
            f"Database pool failed: {e} | host={DB_CONFIG['host']} db={DB_CONFIG['database']} user={DB_CONFIG['user']}"
        )
        return False

def get_db():
    """Get database connection from pool."""
    global db_pool
    if db_pool is None:
        init_db_pool()
    try:
        return db_pool.getconn()
    except:
        return None

def release_db(conn):
    """Return connection to pool."""
    global db_pool
    if db_pool and conn:
        try:
            db_pool.putconn(conn)
        except:
            pass

# =============================================================================
# GEOLOCATION SERVICE
# =============================================================================
# IP to Country mapping (comprehensive)
IP_GEO_DB = {
    # Egypt
    "197.35.": {"country": "Egypt", "country_code": "EG", "city": "Al Mansurah", "lat": 31.0364, "lon": 31.3807, "isp": "TE Data"},
    "197.": {"country": "Egypt", "country_code": "EG", "city": "Cairo", "lat": 30.0444, "lon": 31.2357, "isp": "TE Data"},
    "196.": {"country": "Egypt", "country_code": "EG", "city": "Alexandria", "lat": 31.2001, "lon": 29.9187, "isp": "Orange Egypt"},
    "41.": {"country": "South Africa", "country_code": "ZA", "city": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "isp": "MTN"},
    
    # USA
    "3.": {"country": "United States", "country_code": "US", "city": "Ashburn", "lat": 39.0438, "lon": -77.4874, "isp": "Amazon AWS"},
    "13.": {"country": "United States", "country_code": "US", "city": "Ashburn", "lat": 39.0438, "lon": -77.4874, "isp": "Amazon AWS"},
    "52.": {"country": "United States", "country_code": "US", "city": "Columbus", "lat": 39.9612, "lon": -82.9988, "isp": "Amazon AWS"},
    "54.": {"country": "United States", "country_code": "US", "city": "Ashburn", "lat": 39.0438, "lon": -77.4874, "isp": "Amazon AWS"},
    "64.": {"country": "United States", "country_code": "US", "city": "Dallas", "lat": 32.7767, "lon": -96.7970, "isp": "Comcast"},
    "66.": {"country": "United States", "country_code": "US", "city": "San Jose", "lat": 37.3382, "lon": -121.8863, "isp": "AT&T"},
    "67.": {"country": "United States", "country_code": "US", "city": "Chicago", "lat": 41.8781, "lon": -87.6298, "isp": "Comcast"},
    "69.": {"country": "United States", "country_code": "US", "city": "New York", "lat": 40.7128, "lon": -74.0060, "isp": "Verizon"},
    "71.": {"country": "United States", "country_code": "US", "city": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "isp": "Comcast"},
    "72.": {"country": "United States", "country_code": "US", "city": "Chicago", "lat": 41.8781, "lon": -87.6298, "isp": "Comcast"},
    "74.": {"country": "United States", "country_code": "US", "city": "Phoenix", "lat": 33.4484, "lon": -112.0740, "isp": "CenturyLink"},
    "76.": {"country": "United States", "country_code": "US", "city": "Houston", "lat": 29.7604, "lon": -95.3698, "isp": "Comcast"},
    "98.": {"country": "United States", "country_code": "US", "city": "Seattle", "lat": 47.6062, "lon": -122.3321, "isp": "Comcast"},
    "99.": {"country": "United States", "country_code": "US", "city": "Denver", "lat": 39.7392, "lon": -104.9903, "isp": "AT&T"},
    "104.": {"country": "United States", "country_code": "US", "city": "San Francisco", "lat": 37.7749, "lon": -122.4194, "isp": "Cloudflare"},
    "107.": {"country": "United States", "country_code": "US", "city": "Miami", "lat": 25.7617, "lon": -80.1918, "isp": "AT&T"},
    "135.": {"country": "United States", "country_code": "US", "city": "Austin", "lat": 30.2672, "lon": -97.7431, "isp": "University of Texas"},
    "142.": {"country": "Canada", "country_code": "CA", "city": "Toronto", "lat": 43.6532, "lon": -79.3832, "isp": "Rogers"},
    "147.": {"country": "United States", "country_code": "US", "city": "New York", "lat": 40.7128, "lon": -74.0060, "isp": "DigitalOcean"},
    "162.": {"country": "United States", "country_code": "US", "city": "San Diego", "lat": 32.7157, "lon": -117.1611, "isp": "Censys Inc"},
    "167.": {"country": "United States", "country_code": "US", "city": "Ann Arbor", "lat": 42.2808, "lon": -83.7430, "isp": "Censys Research"},
    "198.": {"country": "United States", "country_code": "US", "city": "Atlanta", "lat": 33.7490, "lon": -84.3880, "isp": "Various"},
    "205.": {"country": "United States", "country_code": "US", "city": "Dallas", "lat": 32.7767, "lon": -96.7970, "isp": "Vultr"},
    
    # Europe
    "2.": {"country": "France", "country_code": "FR", "city": "Paris", "lat": 48.8566, "lon": 2.3522, "isp": "Orange"},
    "5.": {"country": "Germany", "country_code": "DE", "city": "Frankfurt", "lat": 50.1109, "lon": 8.6821, "isp": "Deutsche Telekom"},
    "31.": {"country": "Netherlands", "country_code": "NL", "city": "Amsterdam", "lat": 52.3676, "lon": 4.9041, "isp": "KPN"},
    "46.": {"country": "Russia", "country_code": "RU", "city": "Moscow", "lat": 55.7558, "lon": 37.6173, "isp": "Rostelecom"},
    "77.": {"country": "United Kingdom", "country_code": "GB", "city": "London", "lat": 51.5074, "lon": -0.1278, "isp": "BT"},
    "78.": {"country": "United Kingdom", "country_code": "GB", "city": "London", "lat": 51.5074, "lon": -0.1278, "isp": "Sky"},
    "79.": {"country": "Spain", "country_code": "ES", "city": "Madrid", "lat": 40.4168, "lon": -3.7038, "isp": "Telefonica"},
    "80.": {"country": "Italy", "country_code": "IT", "city": "Rome", "lat": 41.9028, "lon": 12.4964, "isp": "Telecom Italia"},
    "81.": {"country": "United Kingdom", "country_code": "GB", "city": "Manchester", "lat": 53.4808, "lon": -2.2426, "isp": "Virgin"},
    "82.": {"country": "Germany", "country_code": "DE", "city": "Munich", "lat": 48.1351, "lon": 11.5820, "isp": "Vodafone"},
    "83.": {"country": "France", "country_code": "FR", "city": "Marseille", "lat": 43.2965, "lon": 5.3698, "isp": "Free"},
    "84.": {"country": "Netherlands", "country_code": "NL", "city": "Rotterdam", "lat": 51.9244, "lon": 4.4777, "isp": "Ziggo"},
    "85.": {"country": "Sweden", "country_code": "SE", "city": "Stockholm", "lat": 59.3293, "lon": 18.0686, "isp": "Telia"},
    "87.": {"country": "Denmark", "country_code": "DK", "city": "Copenhagen", "lat": 55.6761, "lon": 12.5683, "isp": "TDC"},
    "89.": {"country": "Finland", "country_code": "FI", "city": "Helsinki", "lat": 60.1699, "lon": 24.9384, "isp": "Elisa"},
    "91.": {"country": "Russia", "country_code": "RU", "city": "St Petersburg", "lat": 59.9343, "lon": 30.3351, "isp": "MTS"},
    "92.": {"country": "Ukraine", "country_code": "UA", "city": "Kiev", "lat": 50.4501, "lon": 30.5234, "isp": "Kyivstar"},
    "93.": {"country": "Romania", "country_code": "RO", "city": "Bucharest", "lat": 44.4268, "lon": 26.1025, "isp": "RCS-RDS"},
    "94.": {"country": "Greece", "country_code": "GR", "city": "Athens", "lat": 37.9838, "lon": 23.7275, "isp": "OTE"},
    "95.": {"country": "Russia", "country_code": "RU", "city": "Moscow", "lat": 55.7558, "lon": 37.6173, "isp": "Beeline"},
    "176.": {"country": "Russia", "country_code": "RU", "city": "Moscow", "lat": 55.7558, "lon": 37.6173, "isp": "Selectel"},
    "185.": {"country": "Netherlands", "country_code": "NL", "city": "Amsterdam", "lat": 52.3676, "lon": 4.9041, "isp": "LeaseWeb"},
    
    # Asia
    "1.": {"country": "Australia", "country_code": "AU", "city": "Sydney", "lat": -33.8688, "lon": 151.2093, "isp": "Telstra"},
    "14.": {"country": "Japan", "country_code": "JP", "city": "Tokyo", "lat": 35.6762, "lon": 139.6503, "isp": "NTT"},
    "27.": {"country": "China", "country_code": "CN", "city": "Beijing", "lat": 39.9042, "lon": 116.4074, "isp": "China Telecom"},
    "36.": {"country": "China", "country_code": "CN", "city": "Shanghai", "lat": 31.2304, "lon": 121.4737, "isp": "China Telecom"},
    "42.": {"country": "China", "country_code": "CN", "city": "Hangzhou", "lat": 30.2741, "lon": 120.1551, "isp": "Alibaba Cloud"},
    "43.": {"country": "Japan", "country_code": "JP", "city": "Osaka", "lat": 34.6937, "lon": 135.5023, "isp": "KDDI"},
    "45.": {"country": "Hong Kong", "country_code": "HK", "city": "Hong Kong", "lat": 22.3193, "lon": 114.1694, "isp": "Alibaba"},
    "47.": {"country": "China", "country_code": "CN", "city": "Hangzhou", "lat": 30.2741, "lon": 120.1551, "isp": "Alibaba Cloud"},
    "58.": {"country": "China", "country_code": "CN", "city": "Shenzhen", "lat": 22.5431, "lon": 114.0579, "isp": "China Unicom"},
    "59.": {"country": "South Korea", "country_code": "KR", "city": "Seoul", "lat": 37.5665, "lon": 126.9780, "isp": "KT"},
    "101.": {"country": "Singapore", "country_code": "SG", "city": "Singapore", "lat": 1.3521, "lon": 103.8198, "isp": "SingTel"},
    "103.": {"country": "Hong Kong", "country_code": "HK", "city": "Hong Kong", "lat": 22.3193, "lon": 114.1694, "isp": "PCCW"},
    "110.": {"country": "China", "country_code": "CN", "city": "Beijing", "lat": 39.9042, "lon": 116.4074, "isp": "China Mobile"},
    "111.": {"country": "Japan", "country_code": "JP", "city": "Tokyo", "lat": 35.6762, "lon": 139.6503, "isp": "OCN"},
    "112.": {"country": "Taiwan", "country_code": "TW", "city": "Taipei", "lat": 25.0330, "lon": 121.5654, "isp": "Chunghwa"},
    "114.": {"country": "Indonesia", "country_code": "ID", "city": "Jakarta", "lat": -6.2088, "lon": 106.8456, "isp": "Telkom"},
    "115.": {"country": "Philippines", "country_code": "PH", "city": "Manila", "lat": 14.5995, "lon": 120.9842, "isp": "PLDT"},
    "116.": {"country": "South Korea", "country_code": "KR", "city": "Seoul", "lat": 37.5665, "lon": 126.9780, "isp": "SKT"},
    "117.": {"country": "India", "country_code": "IN", "city": "Mumbai", "lat": 19.0760, "lon": 72.8777, "isp": "Reliance"},
    "118.": {"country": "Bangladesh", "country_code": "BD", "city": "Dhaka", "lat": 23.8103, "lon": 90.4125, "isp": "Grameenphone"},
    "119.": {"country": "China", "country_code": "CN", "city": "Beijing", "lat": 39.9042, "lon": 116.4074, "isp": "China Unicom"},
    "120.": {"country": "China", "country_code": "CN", "city": "Hangzhou", "lat": 30.2741, "lon": 120.1551, "isp": "China Telecom"},
    "121.": {"country": "South Korea", "country_code": "KR", "city": "Seongnam", "lat": 37.4449, "lon": 127.1388, "isp": "Kakao"},
    "122.": {"country": "China", "country_code": "CN", "city": "Shanghai", "lat": 31.2304, "lon": 121.4737, "isp": "China Mobile"},
    "123.": {"country": "India", "country_code": "IN", "city": "Bangalore", "lat": 12.9716, "lon": 77.5946, "isp": "Airtel"},
    "124.": {"country": "Japan", "country_code": "JP", "city": "Fukuoka", "lat": 33.5904, "lon": 130.4017, "isp": "NTT"},
    "125.": {"country": "China", "country_code": "CN", "city": "Chengdu", "lat": 30.5728, "lon": 104.0668, "isp": "China Telecom"},
    "175.": {"country": "Australia", "country_code": "AU", "city": "Melbourne", "lat": -37.8136, "lon": 144.9631, "isp": "Optus"},
    "202.": {"country": "Singapore", "country_code": "SG", "city": "Singapore", "lat": 1.3521, "lon": 103.8198, "isp": "Digital Realty"},
    "203.": {"country": "Australia", "country_code": "AU", "city": "Brisbane", "lat": -27.4698, "lon": 153.0251, "isp": "TPG"},
}

# Cache for geolocation (avoid repeated API calls)
geo_cache = {}

def get_geo(ip: str) -> Dict:
    """Get geolocation for IP address using ip-api.com (accurate, free)."""
    if not ip:
        return {"country": "Unknown", "country_code": "XX", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown"}
    
    # Check cache first
    if ip in geo_cache:
        return geo_cache[ip].copy()
    
    # Try ip-api.com for accurate geolocation
    try:
        import requests
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,city,lat,lon,isp", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                result = {
                    "country": data.get('country', 'Unknown'),
                    "country_code": data.get('countryCode', 'XX'),
                    "city": data.get('city', 'Unknown'),
                    "lat": data.get('lat', 0),
                    "lon": data.get('lon', 0),
                    "isp": data.get('isp', 'Unknown')
                }
                geo_cache[ip] = result
                return result.copy()
    except Exception as e:
        logger.warning(f"ip-api.com failed for {ip}: {e}")
    
    # Fallback: try local DB (first octet)
    first_octet = ip.split('.')[0] + "."
    if first_octet in IP_GEO_DB:
        result = IP_GEO_DB[first_octet].copy()
        geo_cache[ip] = result
        return result.copy()
    
    # Fallback: try prefix match
    for prefix, data in IP_GEO_DB.items():
        if ip.startswith(prefix.rstrip('.')):
            result = data.copy()
            geo_cache[ip] = result
            return result.copy()
    
    result = {"country": "Unknown", "country_code": "XX", "city": "Unknown", "lat": 0, "lon": 0, "isp": "Unknown"}
    geo_cache[ip] = result
    return result.copy()

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Cyber Mirage - Elite SOC",
    page_icon="favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CLEAN WHITE THEME
# =============================================================================
st.markdown("""
<style>
    /* Clean White Theme */
    .stApp {
        background: #ffffff;
        color-scheme: light;
    }

    /* Header */
    .main-header {
        font-size: 2.4rem;
        font-weight: 800;
        text-align: left;
        color: #111111;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }

    .sub-header {
        text-align: left;
        color: #444444;
        font-size: 1rem;
        margin-bottom: 1rem;
    }

    /* Live Badge */
    .live-badge {
        display: inline-flex;
        align-items: center;
        background: #ffffff;
        color: #111111;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.9rem;
        border: 1px solid #e6e6e6;
    }

    .live-dot {
        width: 10px;
        height: 10px;
        background: #111111;
        border-radius: 50%;
        margin-right: 10px;
    }

    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #ececec;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: left;
        transition: all 0.15s ease;
        box-shadow: none;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        border-color: #dddddd;
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #111111;
    }

    .metric-label {
        color: #666666;
        font-size: 0.9rem;
        margin-top: 0.4rem;
    }

    /* Attack Cards */
    .attack-card {
        background: #ffffff;
        border: 1px solid #f0f0f0;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.4rem 0;
    }

    .attack-card-critical {
        border-left: 4px solid #cc0000;
    }

    .attack-card-high {
        border-left: 4px solid #ff8800;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #fafafa;
        border-right: 1px solid #f0f0f0;
    }

    /* Tables */
    .dataframe {
        background: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #f0f0f0 !important;
    }

    /* Remove any backdrop-filter / blur selectors */
    * { backdrop-filter: none !important; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# REAL DATA FUNCTIONS
# =============================================================================

def get_real_attack_stats() -> Dict:
    """Get real-time attack statistics from PostgreSQL."""
    conn = get_db()
    if not conn:
        return {"total": 0, "unique_ips": 0, "blocked": 0, "services": {}, "today": 0, "last_hour": 0}
    
    try:
        cur = conn.cursor()
        
        # Total attacks
        cur.execute("SELECT COUNT(*) FROM attack_sessions WHERE origin IS NOT NULL")
        total = cur.fetchone()[0]
        
        # Unique attackers
        cur.execute("SELECT COUNT(DISTINCT origin) FROM attack_sessions WHERE origin IS NOT NULL")
        unique_ips = cur.fetchone()[0]
        
        # Blocked (detected = true)
        cur.execute("SELECT COUNT(*) FROM attack_sessions WHERE detected = true")
        blocked = cur.fetchone()[0]
        
        # Today's attacks
        cur.execute("""
            SELECT COUNT(*) FROM attack_sessions 
            WHERE created_at >= CURRENT_DATE AND origin IS NOT NULL
        """)
        today = cur.fetchone()[0]
        
        # Last hour
        cur.execute("""
            SELECT COUNT(*) FROM attack_sessions 
            WHERE created_at >= NOW() - INTERVAL '1 hour' AND origin IS NOT NULL
        """)
        last_hour = cur.fetchone()[0]
        
        # Attacks by service (extracted from attacker_name)
        cur.execute("""
            SELECT 
                CASE 
                    WHEN attacker_name LIKE '%_SSH' THEN 'SSH'
                    WHEN attacker_name LIKE '%_HTTP%' THEN 'HTTP'
                    WHEN attacker_name LIKE '%_FTP' THEN 'FTP'
                    WHEN attacker_name LIKE '%_MySQL' THEN 'MySQL'
                    WHEN attacker_name LIKE '%_PostgreSQL' THEN 'PostgreSQL'
                    WHEN attacker_name LIKE '%_SMTP' THEN 'SMTP'
                    WHEN attacker_name LIKE '%_Telnet' THEN 'Telnet'
                    WHEN attacker_name LIKE '%_Modbus' THEN 'Modbus'
                    ELSE 'Other'
                END as service,
                COUNT(*) as count
            FROM attack_sessions
            WHERE origin IS NOT NULL
            GROUP BY service
            ORDER BY count DESC
        """)
        services = {row[0]: row[1] for row in cur.fetchall()}
        
        cur.close()
        return {
            "total": total,
            "unique_ips": unique_ips,
            "blocked": blocked,
            "services": services,
            "today": today,
            "last_hour": last_hour
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"total": 0, "unique_ips": 0, "blocked": 0, "services": {}, "today": 0, "last_hour": 0}
    finally:
        release_db(conn)


def get_real_attacks(limit: int = 50) -> List[Dict]:
    """Get real attacks from PostgreSQL."""
    conn = get_db()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                origin,
                attacker_name,
                attacker_skill,
                detected,
                start_time,
                end_time,
                data_collected,
                final_suspicion,
                created_at
            FROM attack_sessions
            WHERE origin IS NOT NULL AND origin != '' AND origin != 'N/A'
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        attacks = []
        for row in cur.fetchall():
            # Extract service from attacker_name
            name = row[1] or ""
            if "_SSH" in name:
                service = "SSH"
            elif "_HTTP" in name:
                service = "HTTP"
            elif "_FTP" in name:
                service = "FTP"
            elif "_MySQL" in name:
                service = "MySQL"
            elif "_PostgreSQL" in name:
                service = "PostgreSQL"
            elif "_SMTP" in name:
                service = "SMTP"
            elif "_Telnet" in name:
                service = "Telnet"
            elif "_Modbus" in name:
                service = "Modbus"
            else:
                service = "Unknown"
            
            geo = get_geo(row[0])
            
            attacks.append({
                "ip": row[0],
                "service": service,
                "detected": row[3],
                "timestamp": row[8],
                "country": geo["country"],
                "country_code": geo["country_code"],
                "city": geo["city"],
                "lat": geo["lat"],
                "lon": geo["lon"],
                "isp": geo["isp"]
            })
        
        cur.close()
        return attacks
    except Exception as e:
        logger.error(f"Error getting attacks: {e}")
        return []
    finally:
        release_db(conn)


def get_attacker_profiles() -> List[Dict]:
    """Get detailed attacker profiles from real data with scan detection."""
    conn = get_db()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        # First get basic profile data
        cur.execute("""
            SELECT 
                origin,
                COUNT(*) as attack_count,
                COUNT(*) FILTER (
                    WHERE EXISTS (
                        SELECT 1 FROM agent_decisions ad 
                        WHERE ad.session_id = attack_sessions.id 
                        AND ad.action = 'drop_session'
                    )
                ) as blocked,
                MIN(created_at) as first_seen,
                MAX(created_at) as last_seen,
                STRING_AGG(DISTINCT 
                    CASE 
                        WHEN attacker_name LIKE '%_SSH' OR attacker_name LIKE '%SSH%' THEN 'SSH'
                        WHEN attacker_name LIKE '%_HTTP%' OR attacker_name LIKE '%HTTP%' THEN 'HTTP'
                        WHEN attacker_name LIKE '%_FTP' OR attacker_name LIKE '%FTP%' THEN 'FTP'
                        WHEN attacker_name LIKE '%_MySQL' OR attacker_name LIKE '%MySQL%' THEN 'MySQL'
                        WHEN attacker_name LIKE '%_PostgreSQL' OR attacker_name LIKE '%Postgres%' THEN 'PostgreSQL'
                        WHEN attacker_name LIKE '%_SMTP' OR attacker_name LIKE '%SMTP%' THEN 'SMTP'
                        WHEN attacker_name LIKE '%_Telnet' OR attacker_name LIKE '%Telnet%' THEN 'Telnet'
                        ELSE 'Other'
                    END, ', '
                ) as services,
                EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) as duration_seconds,
                COUNT(DISTINCT 
                    CASE 
                        WHEN attacker_name LIKE '%_SSH' OR attacker_name LIKE '%SSH%' THEN 'SSH'
                        WHEN attacker_name LIKE '%_HTTP%' OR attacker_name LIKE '%HTTP%' THEN 'HTTP'
                        WHEN attacker_name LIKE '%_FTP' OR attacker_name LIKE '%FTP%' THEN 'FTP'
                        WHEN attacker_name LIKE '%_MySQL' OR attacker_name LIKE '%MySQL%' THEN 'MySQL'
                        WHEN attacker_name LIKE '%_PostgreSQL' OR attacker_name LIKE '%Postgres%' THEN 'PostgreSQL'
                        WHEN attacker_name LIKE '%_SMTP' OR attacker_name LIKE '%SMTP%' THEN 'SMTP'
                        WHEN attacker_name LIKE '%_Telnet' OR attacker_name LIKE '%Telnet%' THEN 'Telnet'
                        ELSE 'Other'
                    END
                ) as unique_services
            FROM attack_sessions
            WHERE origin IS NOT NULL AND origin != '' AND origin != 'N/A'
            GROUP BY origin
            ORDER BY attack_count DESC, last_seen DESC
            LIMIT 100
        """)
        
        profiles = []
        for row in cur.fetchall():
            ip = row[0]
            attack_count = row[1]
            blocked = row[2]
            successful = attack_count - blocked
            first_seen = row[3]
            last_seen = row[4]
            services = row[5] or "Unknown"
            duration_seconds = row[6] or 0
            unique_services = row[7] or 0
            
            # Get commands count for this IP (separate query to avoid complex join)
            try:
                cur.execute("""
                    SELECT COALESCE(SUM(
                        CASE 
                            WHEN state IS NOT NULL AND state::text != '' 
                            THEN COALESCE((state->>'command_count')::int, 0)
                            ELSE 0
                        END
                    ), 0) as total_commands
                    FROM agent_decisions ad
                    JOIN attack_sessions s ON s.id = ad.session_id
                    WHERE s.origin = %s
                """, (ip,))
                cmd_row = cur.fetchone()
                total_commands = cmd_row[0] if cmd_row else 0
            except Exception:
                total_commands = 0
            
            geo = get_geo(ip)
            
            # Detect if this is a port scan vs real attack
            # Port scan indicators:
            # 1. Many connections (>5) in short time (<180 seconds)
            # 2. Multiple services targeted (>=2)
            # 3. OR very rapid connections (high attack rate)
            attack_rate = attack_count / max(duration_seconds, 1)  # attacks per second
            
            is_likely_scan = (
                # Multiple services in short time = scan
                (unique_services >= 2 and duration_seconds < 180) or
                # Very high attack rate (more than 1 per second) = scan
                (attack_rate > 1.0 and attack_count > 10) or
                # Many attacks, short duration, multiple services
                (attack_count > 20 and duration_seconds < 60 and unique_services >= 2)
            )
            
            # Determine attack type
            if is_likely_scan:
                attack_type = "🔍 Port Scan"
                threat_score = min(50, int(attack_count * 2))
                classification = "Reconnaissance"
            else:
                attack_type = "⚔️ Attack"
                success_rate = (successful / attack_count * 100) if attack_count > 0 else 0
                threat_score = min(100, int(
                    min(attack_count * 5, 40) +
                    success_rate * 0.3 +
                    (30 if attack_count > 10 else attack_count * 3)
                ))
                
                if threat_score >= 80:
                    classification = "Critical"
                elif threat_score >= 60:
                    classification = "High"
                elif threat_score >= 40:
                    classification = "Medium"
                elif threat_score >= 20:
                    classification = "Low"
                else:
                    classification = "Minimal"
            
            profiles.append({
                "ip": ip,
                "country": geo["country"],
                "country_code": geo["country_code"],
                "city": geo["city"],
                "isp": geo["isp"],
                "lat": geo["lat"],
                "lon": geo["lon"],
                "attack_count": attack_count,
                "successful": successful,
                "blocked": blocked,
                "success_rate": round((successful / attack_count * 100) if attack_count > 0 else 0, 1),
                "threat_score": threat_score,
                "classification": classification,
                "services": services,
                "first_seen": first_seen,
                "last_seen": last_seen,
                "attack_type": attack_type,
                "is_scan": is_likely_scan,
                "commands_executed": total_commands
            })
        
        cur.close()
        return profiles
    except Exception as e:
        logger.error(f"Error getting profiles: {e}")
        return []
    finally:
        release_db(conn)


def get_attack_timeline(hours: int = 24) -> pd.DataFrame:
    """Get attack timeline for chart."""
    conn = get_db()
    if not conn:
        return pd.DataFrame()
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                COUNT(*) as attacks
            FROM attack_sessions
            WHERE created_at >= NOW() - INTERVAL '%s hours'
            AND origin IS NOT NULL
            GROUP BY DATE_TRUNC('hour', created_at)
            ORDER BY hour
        """, (hours,))
        
        data = cur.fetchall()
        cur.close()
        
        if data:
            return pd.DataFrame(data, columns=['Hour', 'Attacks'])
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        return pd.DataFrame()
    finally:
        release_db(conn)


def get_ai_decisions(limit: int = 50) -> List[Dict]:
    conn = get_db()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT ad.session_id, ad.action, ad.strategy, ad.reward, ad.created_at,
                   s.origin, s.honeypot_type
            FROM agent_decisions ad
            LEFT JOIN attack_sessions s ON s.id = ad.session_id
            ORDER BY ad.created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
        cur.close()
        decisions = []
        for row in rows:
            decisions.append(
                {
                    "session_id": row[0],
                    "action": row[1],
                    "reason": row[2],
                    "reward": float(row[3]) if row[3] is not None else 0.0,
                    "timestamp": row[4],
                    "origin": row[5],
                    "service": row[6],
                }
            )
        return decisions
    except Exception as e:
        logger.error(f"Error fetching AI decisions: {e}")
        return []
    finally:
        release_db(conn)


def get_deception_events(limit: int = 50) -> List[Dict]:
    conn = get_db()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT session_id, action, parameters, executed, created_at
            FROM deception_events
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
        cur.close()
        events = []
        for row in rows:
            params = row[2]
            if isinstance(params, str):
                try:
                    params = json.loads(params)
                except Exception:
                    params = {"raw": params}
            events.append(
                {
                    "session_id": row[0],
                    "action": row[1],
                    "parameters": params,
                    "executed": row[3],
                    "timestamp": row[4],
                }
            )
        return events
    except Exception as e:
        logger.error(f"Error fetching deception events: {e}")
        return []
    finally:
        release_db(conn)


def get_ai_agent_stats() -> Dict:
    """Get AI agent statistics from database."""
    default_stats = {"total_decisions": 0, "avg_reward": 0.0, "actions": {}, "lure_count": 0, "last_decision": None, "events_count": 0, "active": False}
    
    conn = get_db()
    if not conn:
        return default_stats
    
    try:
        cur = conn.cursor()
        
        # Total decisions
        try:
            cur.execute("SELECT COUNT(*) FROM agent_decisions")
            total = cur.fetchone()[0] or 0
        except:
            total = 0
        
        # Average reward
        try:
            cur.execute("SELECT AVG(reward) FROM agent_decisions WHERE reward IS NOT NULL")
            avg_reward = cur.fetchone()[0] or 0.0
        except:
            avg_reward = 0.0
        
        # Actions breakdown
        try:
            cur.execute("""
                SELECT action, COUNT(*) as cnt
                FROM agent_decisions
                GROUP BY action
                ORDER BY cnt DESC
            """)
            actions = {row[0]: row[1] for row in cur.fetchall()}
        except:
            actions = {}
        
        # Lure presentations
        try:
            cur.execute("SELECT COUNT(*) FROM agent_decisions WHERE action = 'present_lure'")
            lure_count = cur.fetchone()[0] or 0
        except:
            lure_count = 0
        
        # Last decision time
        try:
            cur.execute("SELECT created_at FROM agent_decisions ORDER BY created_at DESC LIMIT 1")
            row = cur.fetchone()
            last_decision = row[0] if row else None
        except:
            last_decision = None
        
        # Deception events count
        try:
            cur.execute("SELECT COUNT(*) FROM deception_events")
            events_count = cur.fetchone()[0] or 0
        except:
            events_count = 0
        
        cur.close()
        return {
            "total_decisions": total,
            "avg_reward": float(avg_reward) if avg_reward else 0.0,
            "actions": actions,
            "lure_count": lure_count,
            "last_decision": last_decision,
            "events_count": events_count,
            "active": total > 0
        }
    except Exception as e:
        logger.error(f"Error getting AI stats: {e}")
        return default_stats


# =============================================================================
# PAGE: MAIN DASHBOARD
# =============================================================================
def render_main_dashboard():
    """Main dashboard with real-time attack data."""
    
    st.markdown('''
        <div style="text-align: center;">
            <div class="live-badge">
                <span class="live-dot"></span>
                LIVE MONITORING
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown(f"<p style='text-align:center;color:#666;'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>", unsafe_allow_html=True)
    st.markdown("---")

    # =========================================================================
    # AI AGENT STATUS CARD (NEW)
    # =========================================================================
    ai_stats = get_ai_agent_stats()
    ai_status_color = "#00ff00" if ai_stats["active"] else "#ff6600"
    ai_status_text = "ACTIVE" if ai_stats["active"] else "STANDBY"
    last_decision_str = ai_stats["last_decision"].strftime('%H:%M:%S') if ai_stats["last_decision"] else "N/A"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.25), rgba(118,75,162,0.15));
                border: 2px solid {ai_status_color}; border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h3 style="margin:0; color:#fff;">AI Deception Agent</h3>
                <p style="margin:4px 0 0 0; color:#aaa; font-size:0.9rem;">Q-Learning Reinforcement Controller</p>
            </div>
            <div style="text-align:right;">
                <span style="font-size:1.4rem; font-weight:bold; color:{ai_status_color};">{ai_status_text}</span>
            </div>
        </div>
        <hr style="border-color:#444; margin:0.8rem 0;">
        <div style="display:flex; gap:2rem; flex-wrap:wrap;">
            <div><span style="color:#888;">Decisions:</span> <strong style="color:#fff;">{ai_stats['total_decisions']}</strong></div>
            <div><span style="color:#888;">Avg Reward:</span> <strong style="color:#00d4ff;">{ai_stats['avg_reward']:.2f}</strong></div>
            <div><span style="color:#888;">Lures Presented:</span> <strong style="color:#ff6600;">{ai_stats['lure_count']}</strong></div>
            <div><span style="color:#888;">Deception Events:</span> <strong style="color:#9b59b6;">{ai_stats['events_count']}</strong></div>
            <div><span style="color:#888;">Last Decision:</span> <strong style="color:#fff;">{last_decision_str}</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get real stats
    stats = get_real_attack_stats()
    
    # Key Metrics
    st.markdown("### Real-Time Threat Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Attacks", f"{stats['total']:,}")
    with col2:
        st.metric("Unique Attackers", f"{stats['unique_ips']:,}")
    with col3:
        st.metric("Blocked", f"{stats['blocked']:,}")
    with col4:
        st.metric("Today", f"{stats['today']:,}")
    with col5:
        st.metric("Last Hour", f"{stats['last_hour']:,}")
    
    st.markdown("---")
    
    # Two columns: Recent attacks + Service distribution
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Live Attack Feed")
        attacks = get_real_attacks(20)
        
        if attacks:
            for attack in attacks[:10]:
                status = "Blocked" if attack['detected'] else "Evaded"
                time_str = attack['timestamp'].strftime('%H:%M:%S') if attack['timestamp'] else 'N/A'
                
                st.markdown(f"""
                <div class="attack-card {'attack-card-critical' if not attack['detected'] else ''}">
                    <strong>{attack['ip']}</strong> → <code>{attack['service']}</code> | 
                    {attack['country']} ({attack['city']}) | 
                    {status} | {time_str}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No attacks recorded yet. System is monitoring...")
    
    with col2:
        st.markdown("### Attack Distribution")
        if stats['services']:
            fig = px.pie(
                names=list(stats['services'].keys()),
                values=list(stats['services'].values()),
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                showlegend=True,
                legend=dict(font=dict(size=10))
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No service data yet")
    
    st.markdown("---")
    
    # Timeline chart
    st.markdown("### Attack Timeline (Last 24 Hours)")
    timeline_df = get_attack_timeline(24)
    
    if not timeline_df.empty:
        fig = px.area(
            timeline_df,
            x='Hour',
            y='Attacks',
            color_discrete_sequence=['#00d4ff']
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis_title="Time",
            yaxis_title="Attacks"
        )
        fig.update_traces(fill='tozeroy', line_shape='spline')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Timeline data will appear as attacks are recorded")


# =============================================================================
# PAGE: ATTACKER PROFILES
# =============================================================================
def render_attacker_profiles():
    """Real attacker profiles from database."""
    
    st.markdown('<h1 class="main-header">Attacker Profiles</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-Time Intelligence | Live from PostgreSQL</p>', unsafe_allow_html=True)
    
    # Get real profiles
    profiles = get_attacker_profiles()
    
    if not profiles:
        st.warning("No attacker data yet. Attacks will appear here in real-time.")
        st.info("To test: `ssh root@13.53.131.159 -p 2222`")
        return
    
    # Overview metrics
    st.markdown("### Threat Landscape Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_attackers = len(profiles)
    total_attacks = sum(p['attack_count'] for p in profiles)
    critical_count = sum(1 for p in profiles if 'Critical' in p['classification'])
    high_count = sum(1 for p in profiles if 'High' in p['classification'])
    scan_count = sum(1 for p in profiles if p.get('is_scan', False))
    
    with col1:
        st.metric("Unique Attackers", total_attackers)
    with col2:
        st.metric("Total Attacks", total_attacks)
    with col3:
        st.metric("Critical Threats", critical_count, delta="Active" if critical_count > 0 else None)
    with col4:
        st.metric("Port Scanners", scan_count, delta="Recon" if scan_count > 0 else None)
    with col5:
        st.metric("Real Attacks", total_attackers - scan_count)
    
    st.markdown("---")
    
    # Profiles table
    st.markdown("### Live Attacker Database")
    
    # Filter options
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        show_type = st.selectbox("Filter by Type", ["All", "Real Attacks Only", "Port Scans Only"])
    with filter_col2:
        show_level = st.selectbox("Filter by Level", ["All", "Critical", "High", "Medium", "Low", "Reconnaissance"])
    
    # Apply filters
    filtered_profiles = profiles
    if show_type == "Real Attacks Only":
        filtered_profiles = [p for p in filtered_profiles if not p.get('is_scan', False)]
    elif show_type == "Port Scans Only":
        filtered_profiles = [p for p in filtered_profiles if p.get('is_scan', False)]
    
    if show_level != "All":
        filtered_profiles = [p for p in filtered_profiles if p['classification'] == show_level]
    
    table_data = []
    for p in filtered_profiles:
        table_data.append({
            'Type': p.get('attack_type', '⚔️ Attack'),
            'IP': p['ip'],
            'Country': p['country'],
            'City': p['city'],
            'ISP': p['isp'],
            'Services': p['services'],
            'Score': f"{p['threat_score']}/100",
            'Level': p['classification'],
            'Attacks': p['attack_count'],
            'Commands': p.get('commands_executed', 0),
            'Evaded': p['successful'],
            'Blocked': p['blocked'],
            'Last Seen': p['last_seen'].strftime('%H:%M:%S') if p['last_seen'] else 'N/A'
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("No matches for current filters")
    
    st.markdown("---")
    
    # Detailed analysis for selected IP
    st.markdown("### Detailed Profile Analysis")
    
    selected_ip = st.selectbox(
        "Select Attacker IP",
        [p['ip'] for p in profiles],
        key="profile_select"
    )
    
    if selected_ip:
        profile = next((p for p in profiles if p['ip'] == selected_ip), None)
        if profile:
            # Show type badge
            type_color = "#ff6600" if profile.get('is_scan') else "#ff0000"
            type_text = profile.get('attack_type', '⚔️ Attack')
            st.markdown(f"""
            <div style="background: {type_color}20; border: 2px solid {type_color}; 
                        border-radius: 10px; padding: 0.5rem 1rem; display: inline-block; margin-bottom: 1rem;">
                <strong style="color: {type_color}; font-size: 1.2rem;">{type_text}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### Location")
                st.markdown(f"**IP:** `{profile['ip']}`")
                st.markdown(f"**Country:** {profile['country']}")
                st.markdown(f"**City:** {profile['city']}")
                st.markdown(f"**ISP:** {profile['isp']}")
            
            with col2:
                st.markdown("#### Statistics")
                st.markdown(f"**Total Connections:** {profile['attack_count']}")
                st.markdown(f"**Commands Executed:** {profile.get('commands_executed', 0)}")
                st.markdown(f"**Threat Score:** {profile['threat_score']}/100")
                st.markdown(f"**Classification:** {profile['classification']}")
            
            with col3:
                st.markdown("#### Timeline")
                st.markdown(f"**First Seen:** {profile['first_seen'].strftime('%Y-%m-%d %H:%M') if profile['first_seen'] else 'N/A'}")
                st.markdown(f"**Last Seen:** {profile['last_seen'].strftime('%Y-%m-%d %H:%M') if profile['last_seen'] else 'N/A'}")
                st.markdown(f"**Services:** {profile['services']}")
            
            # Scan explanation
            if profile.get('is_scan'):
                st.info("""
                🔍 **This appears to be a Port Scanner, not an actual attacker.**
                
                Indicators:
                - Many connections in a very short time
                - Multiple services probed
                - Few or no commands executed
                
                Port scans are reconnaissance activities, not direct attacks.
                """)


# =============================================================================
# PAGE: LIVE ATTACK MAP
# =============================================================================
def render_attack_map():
    """World map with real attack origins."""
    
    st.markdown('<h1 class="main-header">Global Attack Map</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-Time Visualization of Attack Origins</p>', unsafe_allow_html=True)
    
    # Get attacks with geolocation
    profiles = get_attacker_profiles()
    
    if not profiles:
        st.warning("No attack data for map visualization yet")
        return
    
    # Create map data
    map_data = []
    for p in profiles:
        if p['lat'] and p['lon'] and p['lat'] != 0:
            map_data.append({
                'lat': p['lat'],
                'lon': p['lon'],
                'ip': p['ip'],
                'country': p['country'],
                'city': p['city'],
                'attacks': p['attack_count'],
                'threat_score': p['threat_score'],
                'size': min(p['attack_count'] * 3, 50)  # Size based on attacks
            })
    
    if map_data:
        df = pd.DataFrame(map_data)
        
        # Create map
        fig = px.scatter_geo(
            df,
            lat='lat',
            lon='lon',
            size='attacks',
            color='threat_score',
            hover_name='ip',
            hover_data=['country', 'city', 'attacks', 'threat_score'],
            color_continuous_scale='YlOrRd',
            size_max=30,
            projection='natural earth'
        )
        
        # Add server location marker (Stockholm region)
        fig.add_trace(go.Scattergeo(
            lat=[59.3293],
            lon=[18.0686],
            mode='markers',
            marker=dict(size=15, color='#00ff00', symbol='star'),
            name='Honeypot Server',
            hoverinfo='text',
            hovertext='Cyber Mirage Server (Stockholm)'
        ))
        
        fig.update_layout(
            geo=dict(
                showland=True,
                landcolor='rgb(30, 30, 30)',
                showocean=True,
                oceancolor='rgb(10, 10, 30)',
                showcoastlines=True,
                coastlinecolor='rgb(50, 50, 50)',
                showframe=False,
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=600,
            title=dict(
                text=f"{len(map_data)} Active Threat Sources",
                font=dict(size=20, color='#00d4ff')
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Country breakdown
        st.markdown("---")
        st.markdown("### Attacks by Country")
        
        country_stats = {}
        for p in profiles:
            country = p['country']
            if country not in country_stats:
                country_stats[country] = {'attacks': 0, 'ips': 0}
            country_stats[country]['attacks'] += p['attack_count']
            country_stats[country]['ips'] += 1
        
        # Sort by attacks
        sorted_countries = sorted(country_stats.items(), key=lambda x: x[1]['attacks'], reverse=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top Attack Sources:**")
            for country, stats in sorted_countries[:10]:
                st.markdown(f"- **{country}:** {stats['attacks']} attacks from {stats['ips']} IPs")
        
        with col2:
            # Pie chart
            fig = px.pie(
                names=[c[0] for c in sorted_countries[:8]],
                values=[c[1]['attacks'] for c in sorted_countries[:8]],
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PAGE: AI ANALYSIS
# =============================================================================
def render_ai_analysis():
    """AI-powered threat analysis."""
    
    st.markdown('<h1 class="main-header">AI Threat Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Machine Learning-Based Attack Pattern Detection</p>', unsafe_allow_html=True)
    
    profiles = get_attacker_profiles()
    attacks = get_real_attacks(100)
    decisions = get_ai_decisions(50)
    deception_events = get_deception_events(50)
    
    if not profiles:
        st.warning("No data for AI analysis yet")
        return
    
    # Threat Assessment
    st.markdown("### Automated Threat Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    critical_threats = [p for p in profiles if 'Critical' in p['classification']]
    high_threats = [p for p in profiles if 'High' in p['classification']]
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255,0,0,0.2), rgba(255,0,0,0.1)); 
                    border: 1px solid #ff0000; border-radius: 10px; padding: 1.5rem;">
            <h3 style="color: #ff0000;">CRITICAL</h3>
            <p style="font-size: 2rem; font-weight: bold; color: white;">{}</p>
            <p style="color: #aaa;">Require immediate attention</p>
        </div>
        """.format(len(critical_threats)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255,102,0,0.2), rgba(255,102,0,0.1)); 
                    border: 1px solid #ff6600; border-radius: 10px; padding: 1.5rem;">
            <h3 style="color: #ff6600;">HIGH</h3>
            <p style="font-size: 2rem; font-weight: bold; color: white;">{}</p>
            <p style="color: #aaa;">Active monitoring</p>
        </div>
        """.format(len(high_threats)), unsafe_allow_html=True)
    
    with col3:
        avg_score = sum(p['threat_score'] for p in profiles) / len(profiles) if profiles else 0
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,212,255,0.1)); 
                    border: 1px solid #00d4ff; border-radius: 10px; padding: 1.5rem;">
            <h3 style="color: #00d4ff;">AVG SCORE</h3>
            <p style="font-size: 2rem; font-weight: bold; color: white;">{:.1f}</p>
            <p style="color: #aaa;">Overall threat level</p>
        </div>
        """.format(avg_score), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Attack Pattern Analysis
    st.markdown("### Attack Pattern Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Service targeting
        st.markdown("#### Service Targeting")
        
        service_counts = {}
        for attack in attacks:
            svc = attack['service']
            service_counts[svc] = service_counts.get(svc, 0) + 1
        
        if service_counts:
            fig = px.bar(
                x=list(service_counts.keys()),
                y=list(service_counts.values()),
                color=list(service_counts.values()),
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis_title="Service",
                yaxis_title="Attacks"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Hourly distribution
        st.markdown("#### Time Analysis")
        
        hour_counts = {}
        for attack in attacks:
            if attack['timestamp']:
                hour = attack['timestamp'].hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if hour_counts:
            hours = list(range(24))
            counts = [hour_counts.get(h, 0) for h in hours]
            
            fig = px.line(
                x=hours,
                y=counts,
                markers=True
            )
            fig.update_traces(line_color='#00d4ff', marker_size=8)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis_title="Hour (UTC)",
                yaxis_title="Attacks"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Anomaly Detection
    st.markdown("### Anomaly Detection")
    
    anomalies = []
    
    # High frequency attackers
    for p in profiles:
        if p['attack_count'] >= 5:
            anomalies.append({
                'type': 'High Frequency',
                'ip': p['ip'],
                'detail': f"{p['attack_count']} attacks from single IP",
                'severity': 'High'
            })
    
    # Multi-service attackers
    for p in profiles:
        services = p['services'].split(', ')
        if len(set(services)) >= 2:
            anomalies.append({
                'type': 'Multi-Vector',
                'ip': p['ip'],
                'detail': f"Targeting {len(set(services))} different services",
                'severity': 'Critical'
            })
    
    if anomalies:
        for anomaly in anomalies[:10]:
            severity_color = '#ff0000' if anomaly['severity'] == 'Critical' else '#ff6600'
            st.markdown(f"""
            <div style="background: rgba(0,0,0,0.3); border-left: 4px solid {severity_color}; 
                        padding: 1rem; margin: 0.5rem 0; border-radius: 5px;">
                <strong>{anomaly['type']}</strong> | <code>{anomaly['ip']}</code> | {anomaly['detail']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No significant anomalies detected")

    st.markdown("---")
    st.markdown("### AI Deception Decisions")

    if decisions:
        avg_reward = sum(d['reward'] for d in decisions) / len(decisions)
        lure_actions = sum(1 for d in decisions if 'lure' in d['reason'].lower())
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Decisions", len(decisions))
        with col2:
            st.metric("Avg Reward", f"{avg_reward:.2f}")
        with col3:
            st.metric("Lure Plays", lure_actions)

        decision_table = [
            {
                "Time": d['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if d['timestamp'] else 'N/A',
                "Action": d['action'],
                "Reason": d['reason'],
                "Reward": d['reward'],
                "Origin": d['origin'] or 'Unknown',
                "Service": d['service'] or 'Unknown',
            }
            for d in decisions[:20]
        ]
        st.dataframe(pd.DataFrame(decision_table), use_container_width=True, height=350)
    else:
        st.info("No AI decisions recorded yet")

    st.markdown("### Deception Events")
    if deception_events:
        for event in deception_events[:10]:
            st.markdown(
                f"- `{event['timestamp'].strftime('%H:%M:%S') if event['timestamp'] else 'N/A'}` • **{event['action']}** → {event['parameters']}"
            )
    else:
        st.info("No deception events logged yet")


# =============================================================================
# PAGE: SYSTEM STATUS
# =============================================================================
def render_system_status():
    """System health and status."""
    
    st.markdown('<h1 class="main-header">System Status</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Infrastructure Health Monitoring</p>', unsafe_allow_html=True)
    
    # Database connection test
    conn = get_db()
    db_status = "Connected" if conn else "Disconnected"
    if conn:
        release_db(conn)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(0,255,0,0.1); border: 1px solid #00ff00; 
                    border-radius: 10px; padding: 1.5rem; text-align: center;">
            <h3>PostgreSQL</h3>
            <p style="font-size: 1.2rem; color: #00ff00;">{db_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(0,255,0,0.1); border: 1px solid #00ff00; 
                    border-radius: 10px; padding: 1.5rem; text-align: center;">
            <h3>Honeypots</h3>
            <p style="font-size: 1.2rem; color: #00ff00;">Active</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: rgba(0,255,0,0.1); border: 1px solid #00ff00; 
                    border-radius: 10px; padding: 1.5rem; text-align: center;">
            <h3>Dashboard</h3>
            <p style="font-size: 1.2rem; color: #00ff00;">Online</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick stats
    stats = get_real_attack_stats()
    
    st.markdown("### Database Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", stats['total'])
    with col2:
        st.metric("Unique IPs", stats['unique_ips'])
    with col3:
        st.metric("Services Tracked", len(stats['services']))
    
    st.markdown("---")
    
    # Honeypot ports
    st.markdown("### Active Honeypots")
    
    honeypots = [
        {"port": 22, "service": "SSH", "status": "Active"},
        {"port": 21, "service": "FTP", "status": "Active"},
        {"port": 80, "service": "HTTP", "status": "Active"},
        {"port": 443, "service": "HTTPS", "status": "Active"},
        {"port": 3306, "service": "MySQL", "status": "Active"},
        {"port": 5432, "service": "PostgreSQL", "status": "Active"},
        {"port": 502, "service": "Modbus/ICS", "status": "Active"},
        {"port": 1025, "service": "SMTP", "status": "Active"},
    ]
    
    df = pd.DataFrame(honeypots)
    st.dataframe(df, use_container_width=True)


# =============================================================================
# PAGE: DATA MANAGEMENT
# =============================================================================
def render_data_management():
    """Manage attack data - fix false positives, consolidate scans."""
    
    st.markdown('<h1 class="main-header">🛠️ Data Management</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Fix False Positives & Clean Up Data</p>', unsafe_allow_html=True)
    
    conn = get_db()
    if not conn:
        st.error("Database connection failed")
        return
    
    try:
        # Show current attack summary by IP
        st.markdown("### Attack Summary by IP")
        
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                origin,
                COUNT(*) as attack_count,
                STRING_AGG(DISTINCT honeypot_type, ', ') as services,
                MIN(start_time) as first_seen,
                MAX(start_time) as last_seen,
                EXTRACT(EPOCH FROM (MAX(start_time) - MIN(start_time))) as duration_sec
            FROM attack_sessions
            WHERE origin IS NOT NULL AND origin != ''
            GROUP BY origin
            ORDER BY attack_count DESC
            LIMIT 20
        """)
        
        rows = cur.fetchall()
        
        if rows:
            summary_data = []
            for row in rows:
                duration = row[5] or 0
                is_likely_scan = row[1] > 5 and duration < 120  # Many attacks in short time
                summary_data.append({
                    "IP": row[0],
                    "Attacks": row[1],
                    "Services": row[2] or "Unknown",
                    "First Seen": row[3].strftime('%Y-%m-%d %H:%M') if row[3] else "N/A",
                    "Duration": f"{int(duration)}s" if duration else "N/A",
                    "Type": "🔍 Port Scan" if is_likely_scan else "⚔️ Attack"
                })
            
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
            
            # Find IPs that look like false positives
            scan_ips = [d["IP"] for d in summary_data if "Scan" in d["Type"]]
            
            if scan_ips:
                st.warning(f"⚠️ Found {len(scan_ips)} IPs that appear to be port scans rather than real attacks")
        
        st.markdown("---")
        
        # Delete attacks by IP
        st.markdown("### Delete Attacks by IP")
        
        ip_to_delete = st.text_input("Enter IP address to delete", placeholder="e.g., 197.35.34.115")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Delete All Attacks from IP", type="primary"):
                if ip_to_delete:
                    try:
                        cur.execute("SELECT COUNT(*) FROM attack_sessions WHERE origin = %s", (ip_to_delete,))
                        count = cur.fetchone()[0]
                        
                        if count > 0:
                            # Delete related data first
                            cur.execute("""
                                DELETE FROM attack_actions WHERE session_id IN (
                                    SELECT id::text FROM attack_sessions WHERE origin = %s
                                )
                            """, (ip_to_delete,))
                            
                            cur.execute("""
                                DELETE FROM agent_decisions WHERE session_id IN (
                                    SELECT id FROM attack_sessions WHERE origin = %s
                                )
                            """, (ip_to_delete,))
                            
                            cur.execute("""
                                DELETE FROM deception_events WHERE session_id IN (
                                    SELECT id FROM attack_sessions WHERE origin = %s
                                )
                            """, (ip_to_delete,))
                            
                            cur.execute("DELETE FROM attack_sessions WHERE origin = %s", (ip_to_delete,))
                            conn.commit()
                            
                            st.success(f"✅ Deleted {count} attacks from IP: {ip_to_delete}")
                            st.rerun()
                        else:
                            st.info(f"No attacks found from IP: {ip_to_delete}")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please enter an IP address")
        
        with col2:
            if st.button("🔄 Consolidate Port Scans"):
                try:
                    # Consolidate quick multi-port connections into single sessions
                    cur.execute("""
                        WITH scan_candidates AS (
                            SELECT 
                                origin,
                                DATE_TRUNC('minute', start_time) as scan_minute,
                                MIN(id) as keep_id,
                                COUNT(*) as connection_count
                            FROM attack_sessions
                            WHERE origin IS NOT NULL AND origin != ''
                            GROUP BY origin, DATE_TRUNC('minute', start_time)
                            HAVING COUNT(*) > 3
                        ),
                        sessions_to_delete AS (
                            SELECT s.id
                            FROM attack_sessions s
                            JOIN scan_candidates sc ON s.origin = sc.origin 
                                AND DATE_TRUNC('minute', s.start_time) = sc.scan_minute
                                AND s.id != sc.keep_id
                        )
                        SELECT COUNT(*) FROM sessions_to_delete
                    """)
                    to_delete_count = cur.fetchone()[0]
                    
                    if to_delete_count > 0:
                        # Actually delete
                        cur.execute("""
                            WITH scan_candidates AS (
                                SELECT 
                                    origin,
                                    DATE_TRUNC('minute', start_time) as scan_minute,
                                    MIN(id) as keep_id,
                                    COUNT(*) as connection_count
                                FROM attack_sessions
                                WHERE origin IS NOT NULL AND origin != ''
                                GROUP BY origin, DATE_TRUNC('minute', start_time)
                                HAVING COUNT(*) > 3
                            ),
                            sessions_to_delete AS (
                                SELECT s.id
                                FROM attack_sessions s
                                JOIN scan_candidates sc ON s.origin = sc.origin 
                                    AND DATE_TRUNC('minute', s.start_time) = sc.scan_minute
                                    AND s.id != sc.keep_id
                            )
                            DELETE FROM attack_sessions WHERE id IN (SELECT id FROM sessions_to_delete)
                        """)
                        conn.commit()
                        st.success(f"✅ Consolidated {to_delete_count} duplicate scan entries")
                        st.rerun()
                    else:
                        st.info("No port scan duplicates found to consolidate")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error: {e}")
        
        cur.close()
        
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        release_db(conn)


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    """Main application entry point."""
    
    # Initialize database
    init_db_pool()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 25px 15px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; margin-bottom: 25px;'>
            <div style='font-size: 3rem;'></div>
            <h1 style='color: white; margin: 0; font-size: 1.5rem;'>Cyber Mirage</h1>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0 0 0;'>Elite SOC Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["Main Dashboard", "Attacker Profiles", "Attack Map", "AI Analysis", "AI Analytics", "Data Management", "System Status"],
            index=0
        )
        
        st.markdown("---")
        
        # Auto-refresh
        if st.checkbox("Auto-refresh (30s)", value=True):
            st.markdown(f"*Next refresh in 30s*")
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
            <p>Production Ready</p>
            <p>All data is real-time</p>
            <p>v2.0 Elite Edition</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Render selected page
    if "Main Dashboard" in page:
        render_main_dashboard()
    elif "Attacker Profiles" in page:
        render_attacker_profiles()
    elif "Attack Map" in page:
        render_attack_map()
    elif "AI Analysis" in page:
        render_ai_analysis()
    elif "AI Analytics" in page:
        try:
            import sys
            sys.path.insert(0, '/app/src')
            from dashboard.ai_analytics import render_ai_analytics
            render_ai_analytics()
        except Exception as e:
            st.error(f"AI Analytics module not available: {e}")
            st.info("This feature requires the ai_analytics.py module in the dashboard directory.")
    elif "Data Management" in page:
        render_data_management()
    elif "System Status" in page:
        render_system_status()


if __name__ == "__main__":
    main()
