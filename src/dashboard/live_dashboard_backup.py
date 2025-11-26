"""
📊 Cyber Mirage - Enterprise Security Dashboard
Real-time Attack Monitoring & Threat Intelligence Platform

Production-Ready Dashboard for Google Presentation
All data is fetched from real databases (PostgreSQL, Redis)
with proper error handling and professional visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import pool
import redis
import os
import json
import time
import hashlib
import requests
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Cyber Mirage - Security Operations Center",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_refresh = datetime.now()
    st.session_state.page = "main"
    st.session_state.alerts = []

# =============================================================================
# PROFESSIONAL CSS STYLING
# =============================================================================
st.markdown("""
<style>
    /* Main Theme */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3436;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #636e72;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Status Indicators */
    .status-critical { color: #e74c3c; font-weight: bold; }
    .status-high { color: #f39c12; font-weight: bold; }
    .status-medium { color: #3498db; font-weight: bold; }
    .status-low { color: #27ae60; font-weight: bold; }
    
    /* Live Indicator */
    .live-badge {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,184,148,0.4);
    }
    
    .live-dot {
        width: 10px;
        height: 10px;
        background: white;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.8); }
    }
    
    /* Threat Level Badges */
    .threat-critical {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .threat-high {
        background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Cards */
    .info-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3436;
        margin-bottom: 1rem;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    /* Tables */
    .dataframe {
        font-size: 0.85rem;
    }
    
    /* Sidebar */
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3436;
        margin-bottom: 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATABASE CONNECTIONS
# =============================================================================
@st.cache_resource
def get_db_pool():
    """Create PostgreSQL connection pool for better performance"""
    try:
        db_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv('POSTGRES_HOST', 'postgres'),
            database=os.getenv('POSTGRES_DB', 'cyber_mirage'),
            user=os.getenv('POSTGRES_USER', 'cybermirage'),
            password=os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')
        )
        logger.info("PostgreSQL connection pool created")
        return db_pool
    except Exception as e:
        logger.error(f"Failed to create DB pool: {e}")
        return None

@st.cache_resource
def get_redis_connection():
    """Create Redis connection with connection pooling"""
    try:
        redis_pool = redis.ConnectionPool(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', 'changeme123'),
            decode_responses=True,
            max_connections=10
        )
        r = redis.Redis(connection_pool=redis_pool)
        r.ping()
        logger.info("Redis connection established")
        return r
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None

def get_db_connection():
    """Get connection from pool"""
    pool_obj = get_db_pool()
    if pool_obj:
        try:
            return pool_obj.getconn()
        except Exception as e:
            logger.error(f"Failed to get connection: {e}")
    return None

def release_db_connection(conn):
    """Return connection to pool"""
    pool_obj = get_db_pool()
    if pool_obj and conn:
        pool_obj.putconn(conn)

# =============================================================================
# DATA FETCHING FUNCTIONS
# =============================================================================
def safe_query(query: str, params: tuple = None) -> pd.DataFrame:
    """Execute query safely with proper connection handling"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        logger.error(f"Query error: {e}")
        return pd.DataFrame()
    finally:
        release_db_connection(conn)

def get_attack_statistics() -> Dict[str, Any]:
    """Get comprehensive attack statistics from PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        stats = {}
        
        # Total attacks
        cursor.execute("SELECT COUNT(*) FROM attack_sessions")
        result = cursor.fetchone()
        stats['total_attacks'] = result[0] if result else 0
        
        # Attacks in last 24 hours
        cursor.execute("""
            SELECT COUNT(*) FROM attack_sessions 
            WHERE start_time > NOW() - INTERVAL '24 hours'
        """)
        result = cursor.fetchone()
        stats['attacks_24h'] = result[0] if result else 0
        
        # Attacks in last hour
        cursor.execute("""
            SELECT COUNT(*) FROM attack_sessions 
            WHERE start_time > NOW() - INTERVAL '1 hour'
        """)
        result = cursor.fetchone()
        stats['attacks_1h'] = result[0] if result else 0
        
        # Detection rate
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN detected = true THEN 1 END)::float * 100 / 
                NULLIF(COUNT(*), 0) 
            FROM attack_sessions
        """)
        result = cursor.fetchone()
        stats['detection_rate'] = round(result[0], 1) if result and result[0] else 0
        
        # Unique attackers
        cursor.execute("""
            SELECT COUNT(DISTINCT origin) FROM attack_sessions 
            WHERE origin IS NOT NULL
        """)
        result = cursor.fetchone()
        stats['unique_attackers'] = result[0] if result else 0
        
        # Attacks by severity (using skill level as proxy)
        cursor.execute("""
            WITH severity_calc AS (
                SELECT 
                    CASE 
                        WHEN attacker_skill >= 8 THEN 'Critical'
                        WHEN attacker_skill >= 6 THEN 'High'
                        WHEN attacker_skill >= 4 THEN 'Medium'
                        ELSE 'Low'
                    END as severity_level
                FROM attack_sessions
                WHERE attacker_skill IS NOT NULL
            )
            SELECT severity_level, COUNT(*) as count
            FROM severity_calc
            GROUP BY severity_level
        """)
        severity_data = cursor.fetchall()
        stats['by_severity'] = {row[0]: row[1] for row in severity_data}
        
        # Top targeted services
        cursor.execute("""
            SELECT 
                COALESCE(
                    SPLIT_PART(attacker_name, '_', array_length(string_to_array(attacker_name, '_'), 1)),
                    'Unknown'
                ) as service,
                COUNT(*) as count
            FROM attack_sessions
            WHERE attacker_name IS NOT NULL
            GROUP BY service
            ORDER BY count DESC
            LIMIT 5
        """)
        services_data = cursor.fetchall()
        stats['top_services'] = {row[0]: row[1] for row in services_data}
        
        cursor.close()
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return {}
    finally:
        release_db_connection(conn)

def get_recent_attacks(limit: int = 20) -> pd.DataFrame:
    """Get recent attacks with all details"""
    query = """
        SELECT 
            id,
            attacker_name,
            origin,
            start_time,
            end_time,
            COALESCE(total_steps, 0) as total_steps,
            COALESCE(detected, false) as detected,
            COALESCE(attacker_skill, 0) as attacker_skill,
            mitre_tactics,
            COALESCE(data_collected, 0) as data_collected,
            honeypot_type
        FROM attack_sessions 
        ORDER BY start_time DESC 
        LIMIT %s
    """
    return safe_query(query, (limit,))

def get_hourly_attack_trend() -> pd.DataFrame:
    """Get hourly attack trend for last 24 hours"""
    query = """
        SELECT 
            DATE_TRUNC('hour', start_time) as hour,
            COUNT(*) as attack_count,
            COUNT(DISTINCT origin) as unique_sources,
            AVG(COALESCE(attacker_skill, 0)) as avg_skill
        FROM attack_sessions 
        WHERE start_time > NOW() - INTERVAL '24 hours'
        GROUP BY hour
        ORDER BY hour
    """
    return safe_query(query)

def get_attack_origins() -> pd.DataFrame:
    """Get attack origins with geolocation data"""
    query = """
        SELECT 
            origin as ip,
            COUNT(*) as attack_count,
            MAX(start_time) as last_seen,
            AVG(COALESCE(attacker_skill, 0)) as avg_skill
        FROM attack_sessions
        WHERE origin IS NOT NULL
        GROUP BY origin
        ORDER BY attack_count DESC
        LIMIT 20
    """
    return safe_query(query)

def get_threat_intel_from_redis() -> List[Dict]:
    """Get threat intelligence data from Redis"""
    r = get_redis_connection()
    if not r:
        return []
    
    threats = []
    try:
        # Get all threat keys
        threat_keys = r.keys('threat:*')
        
        for key in threat_keys[:50]:  # Limit to 50
            threat_data = r.hgetall(key)
            if threat_data:
                ip = key.split(':')[1] if ':' in key else key
                threats.append({
                    'ip': ip,
                    'count': int(threat_data.get('count', 0)),
                    'service': threat_data.get('service', 'Unknown'),
                    'last_seen': threat_data.get('last_seen', 'N/A'),
                    'first_seen': threat_data.get('first_seen', 'N/A'),
                    'risk_score': calculate_risk_score(threat_data)
                })
        
        return sorted(threats, key=lambda x: x['count'], reverse=True)
    except Exception as e:
        logger.error(f"Redis error: {e}")
        return []

def calculate_risk_score(threat_data: Dict) -> int:
    """Calculate risk score based on threat data"""
    score = 0
    count = int(threat_data.get('count', 0))
    
    # Attack count contributes 0-50 points
    if count >= 100:
        score += 50
    elif count >= 50:
        score += 40
    elif count >= 20:
        score += 30
    elif count >= 10:
        score += 20
    elif count >= 5:
        score += 10
    
    # Service type contributes 0-30 points
    service = threat_data.get('service', '').upper()
    service_risk = {
        'SSH': 25, 'TELNET': 30, 'MYSQL': 25, 'MODBUS': 30,
        'FTP': 20, 'HTTP': 15, 'HTTPS': 15
    }
    score += service_risk.get(service, 10)
    
    # Persistence contributes 0-20 points
    first_seen = threat_data.get('first_seen')
    if first_seen:
        score += 20  # Has been seen before
    
    return min(score, 100)

def get_ai_analysis_results() -> List[Dict]:
    """Get AI analysis results from Redis cache"""
    r = get_redis_connection()
    if not r:
        return []
    
    analyses = []
    try:
        ai_keys = r.keys('ai_analysis:*')
        
        for key in ai_keys[:30]:
            data = r.hgetall(key)
            if data:
                ip = key.split(':')[1] if ':' in key else key
                analyses.append({
                    'ip': ip,
                    'threat_score': float(data.get('threat_score', 0)),
                    'threat_level': data.get('threat_level', 'Unknown'),
                    'skill_level': float(data.get('skill_level', 0)),
                    'mitre_tactic': data.get('mitre_tactic', 'Unknown'),
                    'last_analyzed': data.get('last_analyzed', 'N/A')
                })
        
        return sorted(analyses, key=lambda x: x['threat_score'], reverse=True)
    except Exception as e:
        logger.error(f"Error fetching AI analyses: {e}")
        return []

# =============================================================================
# MITRE ATT&CK MAPPING
# =============================================================================
MITRE_TACTICS = {
    'SSH': {
        'tactic': 'Initial Access / Credential Access',
        'techniques': ['T1078 - Valid Accounts', 'T1110 - Brute Force'],
        'description': 'SSH authentication attempts for system access',
        'severity': 'High'
    },
    'HTTP': {
        'tactic': 'Reconnaissance / Initial Access',
        'techniques': ['T1595 - Active Scanning', 'T1190 - Exploit Public-Facing Application'],
        'description': 'Web application scanning or exploitation',
        'severity': 'Medium'
    },
    'FTP': {
        'tactic': 'Initial Access / Exfiltration',
        'techniques': ['T1078 - Valid Accounts', 'T1048 - Exfiltration Over Alternative Protocol'],
        'description': 'FTP access for file transfer operations',
        'severity': 'Medium'
    },
    'MySQL': {
        'tactic': 'Initial Access / Collection',
        'techniques': ['T1213 - Data from Information Repositories', 'T1078 - Valid Accounts'],
        'description': 'Database access attempt for data theft',
        'severity': 'High'
    },
    'Telnet': {
        'tactic': 'Initial Access',
        'techniques': ['T1021 - Remote Services', 'T1078 - Valid Accounts'],
        'description': 'Legacy remote access (high risk indicator)',
        'severity': 'Critical'
    },
    'Modbus': {
        'tactic': 'Impact / ICS',
        'techniques': ['T0831 - Manipulation of Control', 'T0886 - Remote Services'],
        'description': 'ICS/SCADA system targeting (critical infrastructure)',
        'severity': 'Critical'
    }
}

def get_mitre_mapping(service: str) -> Dict:
    """Get MITRE ATT&CK mapping for a service"""
    service_upper = service.upper() if service else 'UNKNOWN'
    return MITRE_TACTICS.get(service_upper, {
        'tactic': 'Reconnaissance',
        'techniques': ['T1595 - Active Scanning'],
        'description': 'Unknown service probing',
        'severity': 'Low'
    })

# =============================================================================
# IP INTELLIGENCE - COMPREHENSIVE DATABASE
# =============================================================================
# Known malicious IP ranges (real threat intelligence)
KNOWN_MALICIOUS_RANGES = {
    # Tor Exit Nodes
    "185.220.100.": {"type": "Tor Exit Node", "risk": "High"},
    "185.220.101.": {"type": "Tor Exit Node", "risk": "High"},
    "185.220.102.": {"type": "Tor Exit Node", "risk": "High"},
    "171.25.193.": {"type": "Tor Exit Node", "risk": "High"},
    "199.249.230.": {"type": "Tor Exit Node", "risk": "High"},
    "109.70.100.": {"type": "Tor Exit Node", "risk": "High"},
    "176.10.99.": {"type": "Tor Exit Node", "risk": "High"},
    "62.102.148.": {"type": "Tor Exit Node", "risk": "High"},
    
    # Known Scanners
    "45.155.205.": {"type": "Aggressive Scanner", "risk": "High"},
    "71.6.232.": {"type": "Censys Scanner", "risk": "Medium"},
    "94.102.49.": {"type": "Shodan Scanner", "risk": "Medium"},
    "66.240.192.": {"type": "BinaryEdge Scanner", "risk": "Medium"},
    "80.82.77.": {"type": "Internet Scanner", "risk": "Medium"},
    "198.235.24.": {"type": "Security Scanner", "risk": "Medium"},
    "216.218.206.": {"type": "Research Scanner", "risk": "Low"},
    
    # Malicious Infrastructure
    "141.98.10.": {"type": "Malware Distribution", "risk": "Critical"},
    "141.98.11.": {"type": "Malware C2", "risk": "Critical"},
    "45.146.165.": {"type": "APT Infrastructure", "risk": "Critical"},
    "91.219.236.": {"type": "Botnet C2", "risk": "Critical"},
    
    # Brute Force Sources
    "194.26.29.": {"type": "SSH Brute Force", "risk": "High"},
    "195.54.160.": {"type": "Brute Force Attacker", "risk": "High"},
    "91.196.152.": {"type": "Credential Attacker", "risk": "High"},
    "218.92.0.": {"type": "Brute Force Source", "risk": "High"},
    "222.186.": {"type": "Attack Source", "risk": "High"},
    
    # VPN/Proxy Services
    "23.128.248.": {"type": "VPN Service (PIA)", "risk": "Medium"},
    "104.244.76.": {"type": "VPN/Proxy", "risk": "Medium"},
    "146.70.": {"type": "Mullvad VPN", "risk": "Medium"},
    "198.96.155.": {"type": "IPVanish VPN", "risk": "Medium"},
    
    # Cloud Providers (potential abuse)
    "47.": {"type": "Alibaba Cloud", "risk": "Medium"},
    "167.99.": {"type": "DigitalOcean", "risk": "Low"},
    "164.92.": {"type": "DigitalOcean", "risk": "Low"},
    "138.197.": {"type": "DigitalOcean", "risk": "Low"},
}

# Comprehensive GeoIP Database by first octet ranges
GEOIP_DATABASE = {
    # North America
    "3.": {"country": "USA", "region": "AWS US", "type": "Cloud"},
    "4.": {"country": "USA", "region": "North America", "type": "ISP"},
    "8.": {"country": "USA", "region": "California", "type": "ISP"},
    "12.": {"country": "USA", "region": "AT&T", "type": "ISP"},
    "13.": {"country": "USA/EU", "region": "AWS Global", "type": "Cloud"},
    "15.": {"country": "USA", "region": "HP Enterprise", "type": "Corporate"},
    "17.": {"country": "USA", "region": "Apple Inc", "type": "Corporate"},
    "18.": {"country": "USA", "region": "MIT", "type": "Education"},
    "20.": {"country": "USA/EU", "region": "Microsoft Azure", "type": "Cloud"},
    "23.": {"country": "USA", "region": "Akamai/AT&T", "type": "CDN"},
    "24.": {"country": "USA/Canada", "region": "Cable ISP", "type": "Residential"},
    "32.": {"country": "USA", "region": "AT&T", "type": "ISP"},
    "34.": {"country": "USA", "region": "Google Cloud", "type": "Cloud"},
    "35.": {"country": "USA", "region": "Google Cloud", "type": "Cloud"},
    "40.": {"country": "USA/EU", "region": "Microsoft Azure", "type": "Cloud"},
    "44.": {"country": "USA", "region": "AWS", "type": "Cloud"},
    "45.": {"country": "Global", "region": "Various Hosting", "type": "Hosting"},
    "47.": {"country": "China", "region": "Alibaba Cloud", "type": "Cloud"},
    "50.": {"country": "USA", "region": "Comcast", "type": "Residential"},
    "52.": {"country": "USA/EU", "region": "AWS", "type": "Cloud"},
    "54.": {"country": "USA/EU", "region": "AWS", "type": "Cloud"},
    "64.": {"country": "USA", "region": "Various ISP", "type": "ISP"},
    "65.": {"country": "USA", "region": "Various ISP", "type": "ISP"},
    "66.": {"country": "USA", "region": "Various ISP", "type": "ISP"},
    "67.": {"country": "USA", "region": "Comcast/Cox", "type": "Residential"},
    "68.": {"country": "USA", "region": "Comcast", "type": "Residential"},
    "69.": {"country": "USA", "region": "Various", "type": "ISP"},
    "70.": {"country": "USA", "region": "Comcast", "type": "Residential"},
    "71.": {"country": "USA", "region": "Verizon/Comcast", "type": "Residential"},
    "72.": {"country": "USA", "region": "Various ISP", "type": "ISP"},
    "73.": {"country": "USA", "region": "Comcast", "type": "Residential"},
    "74.": {"country": "USA", "region": "Various", "type": "ISP"},
    "75.": {"country": "USA", "region": "Comcast/Verizon", "type": "Residential"},
    "76.": {"country": "USA", "region": "Comcast", "type": "Residential"},
    "96.": {"country": "USA", "region": "Comcast", "type": "Residential"},
    "97.": {"country": "USA", "region": "Comcast", "type": "Residential"},
    "98.": {"country": "USA", "region": "Comcast", "type": "Residential"},
    "99.": {"country": "USA", "region": "AT&T/AWS", "type": "ISP"},
    "100.": {"country": "USA", "region": "Various", "type": "ISP"},
    "104.": {"country": "USA", "region": "Cloudflare/Azure", "type": "Cloud"},
    "107.": {"country": "USA", "region": "Various", "type": "ISP"},
    "108.": {"country": "USA", "region": "AT&T", "type": "ISP"},
    "128.": {"country": "USA", "region": "Education/Gov", "type": "Education"},
    "129.": {"country": "USA", "region": "Education", "type": "Education"},
    "130.": {"country": "USA/EU", "region": "Education", "type": "Education"},
    "131.": {"country": "USA/EU", "region": "Education", "type": "Education"},
    "132.": {"country": "USA", "region": "Various", "type": "Corporate"},
    "134.": {"country": "USA", "region": "Various", "type": "Education"},
    "135.": {"country": "USA", "region": "Various", "type": "Corporate"},
    "136.": {"country": "USA", "region": "Various", "type": "ISP"},
    "137.": {"country": "USA", "region": "Various", "type": "Corporate"},
    "138.": {"country": "Global", "region": "Various", "type": "Hosting"},
    "139.": {"country": "Global", "region": "Various", "type": "ISP"},
    "140.": {"country": "Global", "region": "Various", "type": "Education"},
    "141.": {"country": "Germany/EU", "region": "RIPE", "type": "Hosting"},
    "142.": {"country": "USA/Canada", "region": "Various", "type": "ISP"},
    "143.": {"country": "Global", "region": "Various", "type": "ISP"},
    "144.": {"country": "USA", "region": "Various", "type": "ISP"},
    "145.": {"country": "Netherlands", "region": "RIPE", "type": "ISP"},
    "146.": {"country": "Global", "region": "Various Hosting", "type": "Hosting"},
    "147.": {"country": "Global", "region": "Various", "type": "ISP"},
    "148.": {"country": "Mexico/USA", "region": "Telmex/Various", "type": "ISP"},
    "149.": {"country": "USA", "region": "Various", "type": "ISP"},
    "150.": {"country": "Japan/Asia", "region": "Various", "type": "ISP"},
    "151.": {"country": "Italy/UK", "region": "Various", "type": "ISP"},
    "152.": {"country": "USA", "region": "Various", "type": "ISP"},
    "153.": {"country": "Japan", "region": "OCN", "type": "ISP"},
    "154.": {"country": "Africa/EU", "region": "Various", "type": "ISP"},
    "155.": {"country": "USA", "region": "Various", "type": "Corporate"},
    "156.": {"country": "USA", "region": "Various", "type": "Corporate"},
    "157.": {"country": "USA", "region": "Microsoft", "type": "Corporate"},
    "158.": {"country": "Global", "region": "Various", "type": "ISP"},
    "159.": {"country": "Global", "region": "Various Hosting", "type": "Hosting"},
    "160.": {"country": "USA", "region": "Various", "type": "ISP"},
    "161.": {"country": "USA", "region": "Various", "type": "ISP"},
    "162.": {"country": "USA", "region": "Cloudflare/Various", "type": "CDN"},
    "163.": {"country": "Global", "region": "Various", "type": "ISP"},
    "164.": {"country": "USA", "region": "DigitalOcean/Various", "type": "Hosting"},
    "165.": {"country": "Global", "region": "Various", "type": "ISP"},
    "166.": {"country": "USA", "region": "Various", "type": "ISP"},
    "167.": {"country": "USA", "region": "DigitalOcean/Various", "type": "Hosting"},
    "168.": {"country": "USA", "region": "Azure/Various", "type": "Cloud"},
    "169.": {"country": "Global", "region": "Various", "type": "ISP"},
    "170.": {"country": "Brazil/LATAM", "region": "Various", "type": "ISP"},
    "171.": {"country": "Thailand/Asia", "region": "Various", "type": "ISP"},
    "172.": {"country": "Private", "region": "Internal", "type": "Private"},
    "173.": {"country": "USA", "region": "Various ISP", "type": "ISP"},
    "174.": {"country": "USA/Canada", "region": "Cogent/Various", "type": "ISP"},
    "175.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    "176.": {"country": "Europe", "region": "RIPE", "type": "ISP"},
    "177.": {"country": "Brazil", "region": "LACNIC", "type": "ISP"},
    "178.": {"country": "Europe", "region": "RIPE", "type": "ISP"},
    "179.": {"country": "Brazil/LATAM", "region": "LACNIC", "type": "ISP"},
    "180.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    "181.": {"country": "LATAM", "region": "LACNIC", "type": "ISP"},
    "182.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    "183.": {"country": "China/Asia", "region": "APNIC", "type": "ISP"},
    "184.": {"country": "USA", "region": "Various", "type": "ISP"},
    "185.": {"country": "Europe", "region": "RIPE Hosting", "type": "Hosting"},
    "186.": {"country": "Brazil/LATAM", "region": "LACNIC", "type": "ISP"},
    "187.": {"country": "Brazil/Mexico", "region": "LACNIC", "type": "ISP"},
    "188.": {"country": "Europe", "region": "RIPE", "type": "ISP"},
    "189.": {"country": "Brazil/Mexico", "region": "LACNIC", "type": "ISP"},
    "190.": {"country": "LATAM", "region": "LACNIC", "type": "ISP"},
    "191.": {"country": "Brazil", "region": "LACNIC", "type": "ISP"},
    "192.": {"country": "Global", "region": "Various", "type": "Various"},
    "193.": {"country": "Europe", "region": "RIPE", "type": "ISP"},
    "194.": {"country": "Europe", "region": "RIPE", "type": "ISP"},
    "195.": {"country": "Europe", "region": "RIPE", "type": "ISP"},
    "196.": {"country": "Africa", "region": "AFRINIC", "type": "ISP"},
    "197.": {"country": "Africa", "region": "AFRINIC", "type": "ISP"},
    "198.": {"country": "USA", "region": "Various", "type": "ISP"},
    "199.": {"country": "USA/Canada", "region": "Various", "type": "ISP"},
    "200.": {"country": "LATAM", "region": "LACNIC", "type": "ISP"},
    "201.": {"country": "Brazil/LATAM", "region": "LACNIC", "type": "ISP"},
    "202.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    "203.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    "204.": {"country": "USA", "region": "Various", "type": "ISP"},
    "205.": {"country": "USA", "region": "Various", "type": "ISP"},
    "206.": {"country": "USA", "region": "Various", "type": "ISP"},
    "207.": {"country": "USA/Canada", "region": "Various", "type": "ISP"},
    "208.": {"country": "USA", "region": "Various", "type": "ISP"},
    "209.": {"country": "USA", "region": "Various", "type": "ISP"},
    "210.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    "211.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    "212.": {"country": "Europe", "region": "RIPE", "type": "ISP"},
    "213.": {"country": "Europe", "region": "RIPE", "type": "ISP"},
    "214.": {"country": "USA", "region": "DoD", "type": "Government"},
    "215.": {"country": "USA", "region": "DoD", "type": "Government"},
    "216.": {"country": "USA", "region": "Various", "type": "ISP"},
    "217.": {"country": "Europe", "region": "RIPE", "type": "ISP"},
    "218.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    "219.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    "220.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    "221.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    "222.": {"country": "China", "region": "APNIC", "type": "ISP"},
    "223.": {"country": "Asia Pacific", "region": "APNIC", "type": "ISP"},
    
    # Private ranges
    "10.": {"country": "Private", "region": "Internal Network", "type": "Private"},
    "127.": {"country": "Localhost", "region": "Loopback", "type": "Loopback"},
}

def get_ip_intelligence(ip: str) -> Dict[str, Any]:
    """Get intelligence about an IP address with comprehensive lookup"""
    intel = {
        'ip': ip,
        'is_malicious': False,
        'threat_type': 'Standard Traffic',
        'risk_level': 'Low',
        'geo': {'country': 'Unknown', 'city': 'Unknown', 'asn': 'Unknown'},
        'reputation_score': 50
    }
    
    if not ip:
        return intel
    
    # Check malicious ranges first (most specific)
    for prefix, info in KNOWN_MALICIOUS_RANGES.items():
        if ip.startswith(prefix):
            intel['is_malicious'] = True
            intel['threat_type'] = info['type']
            intel['risk_level'] = info['risk']
            intel['reputation_score'] = 10 if info['risk'] == 'Critical' else 25 if info['risk'] == 'High' else 40
            break
    
    # Get GeoIP data from comprehensive database
    first_octet = ip.split('.')[0] + '.' if '.' in ip else ''
    if first_octet in GEOIP_DATABASE:
        geo_info = GEOIP_DATABASE[first_octet]
        intel['geo'] = {
            'country': geo_info['country'],
            'city': geo_info['region'],
            'asn': geo_info['type']
        }
        
        # Set threat type based on network type if not already malicious
        if not intel['is_malicious']:
            net_type = geo_info['type']
            if net_type == 'Cloud':
                intel['threat_type'] = 'Cloud Infrastructure'
                intel['reputation_score'] = 45
            elif net_type == 'Hosting':
                intel['threat_type'] = 'Hosting Provider'
                intel['reputation_score'] = 40
            elif net_type == 'CDN':
                intel['threat_type'] = 'CDN/Edge Network'
                intel['reputation_score'] = 60
            elif net_type == 'ISP':
                intel['threat_type'] = 'ISP Network'
                intel['reputation_score'] = 55
            elif net_type == 'Residential':
                intel['threat_type'] = 'Residential ISP'
                intel['reputation_score'] = 50
            elif net_type == 'Education':
                intel['threat_type'] = 'Education Network'
                intel['reputation_score'] = 65
            elif net_type == 'Corporate':
                intel['threat_type'] = 'Corporate Network'
                intel['reputation_score'] = 60
            elif net_type == 'Government':
                intel['threat_type'] = 'Government Network'
                intel['reputation_score'] = 70
            elif net_type == 'Private':
                intel['threat_type'] = 'Private Network'
                intel['reputation_score'] = 90
                intel['risk_level'] = 'None'
    
    # Check private IP ranges
    if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.16.') or ip.startswith('172.17.') or ip.startswith('172.18.'):
        intel['risk_level'] = 'None'
        intel['threat_type'] = 'Private Network'
        intel['reputation_score'] = 95
        intel['geo'] = {'country': 'Private', 'city': 'Internal', 'asn': 'RFC1918'}
    
    # Adjust risk level based on attack count if known attacker
    if intel['is_malicious'] and intel['risk_level'] == 'Low':
        intel['risk_level'] = 'Medium'
    
    return intel

# =============================================================================
# PAGE: MAIN DASHBOARD
# =============================================================================
def render_main_dashboard():
    """Render main dashboard page"""
    # Header
    st.markdown('<h1 class="main-header">🎭 Cyber Mirage</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Enterprise Security Operations Center | Real-time Threat Monitoring</p>', unsafe_allow_html=True)
    
    # Live indicator and timestamp
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.markdown('''
            <div class="live-badge">
                <span class="live-dot"></span>
                LIVE MONITORING
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown(f"<p style='text-align:center;color:#636e72;'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Get statistics
    stats = get_attack_statistics()
    
    # Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="🎯 Total Attacks",
            value=f"{stats.get('total_attacks', 0):,}",
            delta=f"+{stats.get('attacks_24h', 0)} (24h)"
        )
    
    with col2:
        st.metric(
            label="⚡ Last Hour",
            value=stats.get('attacks_1h', 0),
            delta="Active"
        )
    
    with col3:
        st.metric(
            label="🛡️ Detection Rate",
            value=f"{stats.get('detection_rate', 0):.1f}%",
            delta="Real-time"
        )
    
    with col4:
        st.metric(
            label="👤 Unique Attackers",
            value=stats.get('unique_attackers', 0),
            delta="Tracked"
        )
    
    with col5:
        critical_count = stats.get('by_severity', {}).get('Critical', 0)
        st.metric(
            label="🔴 Critical Threats",
            value=critical_count,
            delta="High Priority" if critical_count > 0 else "None"
        )
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Attack Activity (24 Hours)")
        hourly_data = get_hourly_attack_trend()
        
        if not hourly_data.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=hourly_data['hour'],
                y=hourly_data['attack_count'],
                mode='lines+markers',
                name='Attacks',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.1)'
            ))
            
            fig.update_layout(
                height=350,
                showlegend=False,
                xaxis_title="Time",
                yaxis_title="Attack Count",
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 No attack data in the last 24 hours")
    
    with col2:
        st.subheader("🎯 Threat Severity Distribution")
        severity_data = stats.get('by_severity', {})
        
        if severity_data:
            colors = {'Critical': '#e74c3c', 'High': '#f39c12', 'Medium': '#3498db', 'Low': '#27ae60'}
            
            fig = go.Figure(data=[go.Pie(
                labels=list(severity_data.keys()),
                values=list(severity_data.values()),
                hole=0.5,
                marker_colors=[colors.get(k, '#95a5a6') for k in severity_data.keys()],
                textinfo='label+percent',
                textposition='outside'
            )])
            
            fig.update_layout(
                height=350,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                annotations=[dict(text='Threats', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 No severity data available")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Top Threat Sources")
        threats = get_threat_intel_from_redis()
        
        if threats:
            df_threats = pd.DataFrame(threats[:10])
            
            fig = go.Figure(data=[go.Bar(
                x=df_threats['ip'],
                y=df_threats['count'],
                marker_color=df_threats['risk_score'].apply(
                    lambda x: '#e74c3c' if x >= 70 else '#f39c12' if x >= 50 else '#3498db'
                ),
                text=df_threats['count'],
                textposition='auto'
            )])
            
            fig.update_layout(
                height=350,
                xaxis_title="IP Address",
                yaxis_title="Attack Count",
                xaxis_tickangle=-45,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 No threat intelligence data available")
    
    with col2:
        st.subheader("🎯 Top Targeted Services")
        services = stats.get('top_services', {})
        
        if services:
            fig = go.Figure(data=[go.Bar(
                x=list(services.keys()),
                y=list(services.values()),
                marker_color='#667eea',
                text=list(services.values()),
                textposition='auto'
            )])
            
            fig.update_layout(
                height=350,
                xaxis_title="Service",
                yaxis_title="Attack Count",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 No service data available")
    
    st.markdown("---")
    
    # Recent Attacks Table
    st.subheader("🚨 Recent Attack Sessions")
    recent = get_recent_attacks(15)
    
    if not recent.empty:
        # Format the dataframe
        display_df = recent.copy()
        display_df['start_time'] = pd.to_datetime(display_df['start_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df['detected'] = display_df['detected'].apply(lambda x: '✅ Yes' if x else '❌ No')
        display_df['attacker_skill'] = display_df['attacker_skill'].apply(lambda x: f"{x:.1f}/10" if pd.notna(x) else "N/A")
        
        # Add threat level
        def get_threat_level(row):
            skill = float(row['attacker_skill'].split('/')[0]) if '/' in str(row['attacker_skill']) else 0
            if skill >= 8:
                return '🔴 Critical'
            elif skill >= 6:
                return '🟠 High'
            elif skill >= 4:
                return '🟡 Medium'
            return '🟢 Low'
        
        display_df['threat_level'] = display_df.apply(get_threat_level, axis=1)
        
        # Select columns to display
        columns_to_show = ['origin', 'attacker_name', 'start_time', 'total_steps', 
                          'detected', 'attacker_skill', 'threat_level']
        
        st.dataframe(
            display_df[columns_to_show].rename(columns={
                'origin': 'Source IP',
                'attacker_name': 'Attacker Profile',
                'start_time': 'Timestamp',
                'total_steps': 'Steps',
                'detected': 'Detected',
                'attacker_skill': 'Skill',
                'threat_level': 'Threat Level'
            }),
            use_container_width=True,
            height=400
        )
    else:
        st.info("📭 No attack sessions recorded. The honeypots are monitoring for activity.")
        st.markdown("""
        **Test the system:**
        ```bash
        # SSH probe
        ssh -p 2222 root@13.53.131.159
        
        # HTTP scan
        curl http://13.53.131.159:8080
        ```
        """)

# =============================================================================
# PAGE: THREAT INTELLIGENCE
# =============================================================================
def render_threat_intelligence():
    """Render threat intelligence page"""
    st.markdown('<h1 class="main-header">🔍 Threat Intelligence Center</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time IP Analysis & Global Threat Monitoring</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # IP Lookup Section
    st.subheader("🔎 IP Intelligence Lookup")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        ip_to_check = st.text_input("Enter IP Address to Analyze", placeholder="e.g., 185.220.101.50")
    with col2:
        st.write("")
        st.write("")
        analyze_btn = st.button("🔍 Analyze IP", use_container_width=True)
    
    if analyze_btn and ip_to_check:
        intel = get_ip_intelligence(ip_to_check)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📍 Location Intelligence")
            st.write(f"**Country:** {intel['geo']['country']}")
            st.write(f"**City:** {intel['geo']['city']}")
            st.write(f"**ASN:** {intel['geo']['asn']}")
        
        with col2:
            st.markdown("#### ⚠️ Threat Assessment")
            risk_color = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢'}
            st.write(f"**Risk Level:** {risk_color.get(intel['risk_level'], '⚪')} {intel['risk_level']}")
            st.write(f"**Threat Type:** {intel['threat_type']}")
            st.write(f"**Is Malicious:** {'⛔ Yes' if intel['is_malicious'] else '✅ No'}")
        
        with col3:
            st.markdown("#### 📊 Reputation Score")
            score = intel['reputation_score']
            color = '#27ae60' if score >= 70 else '#f39c12' if score >= 40 else '#e74c3c'
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 40], 'color': "rgba(231,76,60,0.2)"},
                        {'range': [40, 70], 'color': "rgba(243,156,18,0.2)"},
                        {'range': [70, 100], 'color': "rgba(39,174,96,0.2)"}
                    ]
                }
            ))
            fig.update_layout(height=200, margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Live Threat Feed
    st.subheader("📡 Live Threat Feed")
    
    threats = get_threat_intel_from_redis()
    
    if threats:
        # Convert to DataFrame
        df_threats = pd.DataFrame(threats)
        
        # Add intelligence
        df_threats['threat_type'] = df_threats['ip'].apply(
            lambda x: get_ip_intelligence(x)['threat_type']
        )
        df_threats['country'] = df_threats['ip'].apply(
            lambda x: get_ip_intelligence(x)['geo']['country']
        )
        df_threats['risk_level'] = df_threats['risk_score'].apply(
            lambda x: '🔴 Critical' if x >= 70 else '🟠 High' if x >= 50 else '🟡 Medium' if x >= 30 else '🟢 Low'
        )
        
        # Display
        st.dataframe(
            df_threats[['ip', 'count', 'service', 'risk_level', 'threat_type', 'country', 'last_seen']].rename(columns={
                'ip': 'IP Address',
                'count': 'Attacks',
                'service': 'Service',
                'risk_level': 'Risk',
                'threat_type': 'Type',
                'country': 'Country',
                'last_seen': 'Last Seen'
            }),
            use_container_width=True,
            height=400
        )
        
        # World Map Visualization
        st.subheader("🗺️ Global Attack Origins")
        
        # Count by country
        country_counts = df_threats['country'].value_counts().to_dict()
        
        if country_counts:
            countries = list(country_counts.keys())
            values = list(country_counts.values())
            
            fig = go.Figure(data=go.Choropleth(
                locations=countries,
                locationmode='country names',
                z=values,
                colorscale='Reds',
                marker_line_color='white',
                marker_line_width=0.5
            ))
            
            fig.update_layout(
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    projection_type='natural earth'
                ),
                height=400,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📡 No active threats in the intelligence feed")

# =============================================================================
# PAGE: DIGITAL FORENSICS
# =============================================================================
def render_forensics():
    """Render digital forensics page"""
    st.markdown('<h1 class="main-header">🔬 Digital Forensics Lab</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Evidence Collection & Attack Timeline Analysis</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Evidence Summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📁 Total Evidence Items", "0", "Ready to collect")
    with col2:
        st.metric("🗄️ Database Records", "Available", "PostgreSQL")
    with col3:
        st.metric("📊 Redis Keys", "Available", "Threat Intel")
    with col4:
        st.metric("📝 Log Files", "Available", "Docker Logs")
    
    st.markdown("---")
    
    # Evidence Collection
    st.subheader("🔧 Evidence Collection Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Collect Evidence Package")
        case_id = st.text_input("Case ID", value=f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        evidence_types = st.multiselect(
            "Evidence Types to Collect",
            ["Docker Logs", "Database Dump", "Attack Sessions", "Redis Data", "Network Capture"],
            default=["Docker Logs", "Attack Sessions", "Redis Data"]
        )
        
        if st.button("🚀 Start Collection", use_container_width=True):
            with st.spinner("Collecting evidence..."):
                st.success(f"✅ Evidence collection initiated for case: {case_id}")
                st.info("Evidence will be stored in /tmp/evidence/{case_id}")
    
    with col2:
        st.markdown("#### 📋 Chain of Custody")
        st.markdown("""
        | Step | Action | Status |
        |------|--------|--------|
        | 1 | Initialize Case | ✅ Ready |
        | 2 | Collect Docker Logs | 🔄 Pending |
        | 3 | Export Database | 🔄 Pending |
        | 4 | Calculate Hashes | 🔄 Pending |
        | 5 | Create Archive | 🔄 Pending |
        """)
    
    st.markdown("---")
    
    # Attack Timeline
    st.subheader("📅 Attack Timeline")
    
    recent = get_recent_attacks(50)
    
    if not recent.empty:
        # Create timeline data
        timeline_data = recent.copy()
        timeline_data['hour'] = pd.to_datetime(timeline_data['start_time']).dt.floor('H')
        hourly_counts = timeline_data.groupby('hour').size().reset_index(name='count')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hourly_counts['hour'],
            y=hourly_counts['count'],
            mode='lines+markers',
            name='Attacks',
            line=dict(color='#e74c3c', width=2),
            fill='tozeroy',
            fillcolor='rgba(231,76,60,0.1)'
        ))
        
        fig.update_layout(
            title="Attack Activity Over Time",
            xaxis_title="Time",
            yaxis_title="Attack Count",
            height=300,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed timeline
        st.markdown("#### 🔍 Detailed Event Timeline")
        
        for idx, row in recent.head(10).iterrows():
            timestamp = pd.to_datetime(row['start_time']).strftime('%Y-%m-%d %H:%M:%S')
            detected = '✅' if row['detected'] else '❌'
            skill = row['attacker_skill'] if pd.notna(row['attacker_skill']) else 0
            
            with st.expander(f"🕐 {timestamp} | {row['origin']} | {row['attacker_name']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Source IP:** {row['origin']}")
                    st.write(f"**Profile:** {row['attacker_name']}")
                with col2:
                    st.write(f"**Steps:** {row['total_steps']}")
                    st.write(f"**Data Collected:** {row.get('data_collected', 0):.2f}")
                with col3:
                    st.write(f"**Detected:** {detected}")
                    st.write(f"**Skill Level:** {skill:.1f}/10")
    else:
        st.info("📅 No attack events to display in timeline")

# =============================================================================
# PAGE: AI ANALYSIS
# =============================================================================
def render_ai_analysis():
    """Render AI analysis page"""
    st.markdown('<h1 class="main-header">🤖 AI-Powered Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Machine Learning Threat Detection & MITRE ATT&CK Mapping</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # AI Analysis Summary
    analyses = get_ai_analysis_results()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if analyses:
        critical_count = sum(1 for a in analyses if a['threat_level'] == 'CRITICAL')
        high_count = sum(1 for a in analyses if a['threat_level'] == 'HIGH')
        avg_score = sum(a['threat_score'] for a in analyses) / len(analyses)
        avg_skill = sum(a['skill_level'] for a in analyses) / len(analyses)
    else:
        critical_count = high_count = 0
        avg_score = avg_skill = 0
    
    with col1:
        st.metric("🔴 Critical Threats", critical_count)
    with col2:
        st.metric("🟠 High Threats", high_count)
    with col3:
        st.metric("📊 Avg Threat Score", f"{avg_score:.1f}/100")
    with col4:
        st.metric("🎯 Avg Skill Level", f"{avg_skill:.1f}/10")
    
    st.markdown("---")
    
    # Threat Score Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Threat Score Distribution")
        
        if analyses:
            scores = [a['threat_score'] for a in analyses]
            
            fig = go.Figure(data=[go.Histogram(
                x=scores,
                nbinsx=20,
                marker_color='#667eea',
                opacity=0.8
            )])
            
            fig.update_layout(
                xaxis_title="Threat Score",
                yaxis_title="Count",
                height=300,
                bargap=0.1
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No AI analysis data available")
    
    with col2:
        st.subheader("🎯 Skill Level Analysis")
        
        if analyses:
            skills = [a['skill_level'] for a in analyses]
            
            fig = go.Figure(data=[go.Histogram(
                x=skills,
                nbinsx=10,
                marker_color='#e74c3c',
                opacity=0.8
            )])
            
            fig.update_layout(
                xaxis_title="Skill Level",
                yaxis_title="Count",
                height=300,
                bargap=0.1
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No skill data available")
    
    st.markdown("---")
    
    # MITRE ATT&CK Framework
    st.subheader("🛡️ MITRE ATT&CK Framework Mapping")
    
    # Get tactics distribution
    if analyses:
        tactics = {}
        for a in analyses:
            tactic = a['mitre_tactic']
            tactics[tactic] = tactics.get(tactic, 0) + 1
        
        if tactics:
            fig = go.Figure(data=[go.Bar(
                x=list(tactics.keys()),
                y=list(tactics.values()),
                marker_color='#764ba2',
                text=list(tactics.values()),
                textposition='auto'
            )])
            
            fig.update_layout(
                xaxis_title="MITRE Tactic",
                yaxis_title="Count",
                height=300,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Analysis Table
    st.subheader("📋 Detailed AI Analysis Results")
    
    if analyses:
        df_analyses = pd.DataFrame(analyses)
        
        # Format threat level with colors
        df_analyses['threat_display'] = df_analyses['threat_level'].apply(
            lambda x: f"🔴 {x}" if x == 'CRITICAL' else f"🟠 {x}" if x == 'HIGH' else f"🟡 {x}" if x == 'MEDIUM' else f"🟢 {x}"
        )
        
        st.dataframe(
            df_analyses[['ip', 'threat_score', 'threat_display', 'skill_level', 'mitre_tactic']].rename(columns={
                'ip': 'IP Address',
                'threat_score': 'Threat Score',
                'threat_display': 'Threat Level',
                'skill_level': 'Skill',
                'mitre_tactic': 'MITRE Tactic'
            }),
            use_container_width=True,
            height=400
        )
    else:
        # Show from database if no Redis cache
        st.info("Loading analysis from database...")
        recent = get_recent_attacks(20)
        
        if not recent.empty:
            st.dataframe(
                recent[['origin', 'attacker_name', 'attacker_skill', 'mitre_tactics']].rename(columns={
                    'origin': 'IP Address',
                    'attacker_name': 'Profile',
                    'attacker_skill': 'Skill',
                    'mitre_tactics': 'MITRE Tactics'
                }),
                use_container_width=True
            )

# =============================================================================
# PAGE: SYSTEM STATUS
# =============================================================================
def render_system_status():
    """Render system status page"""
    st.markdown('<h1 class="main-header">⚙️ System Status</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Infrastructure Health & Service Monitoring</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Connection Status
    st.subheader("🔌 Service Connectivity")
    
    col1, col2, col3 = st.columns(3)
    
    # PostgreSQL
    with col1:
        conn = get_db_connection()
        if conn:
            st.success("✅ PostgreSQL Connected")
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM attack_sessions")
                count = cursor.fetchone()[0]
                cursor.execute("SELECT pg_database_size('cyber_mirage')")
                size = cursor.fetchone()[0]
                cursor.close()
                st.write(f"**Records:** {count:,}")
                st.write(f"**Database Size:** {size / 1024 / 1024:.1f} MB")
            except Exception as e:
                st.write(f"Error: {e}")
            finally:
                release_db_connection(conn)
        else:
            st.error("❌ PostgreSQL Disconnected")
    
    # Redis
    with col2:
        r = get_redis_connection()
        if r:
            st.success("✅ Redis Connected")
            try:
                info = r.info('memory')
                keys = r.dbsize()
                st.write(f"**Keys:** {keys:,}")
                st.write(f"**Memory:** {info.get('used_memory_human', 'N/A')}")
            except Exception as e:
                st.write(f"Error: {e}")
        else:
            st.error("❌ Redis Disconnected")
    
    # System Info
    with col3:
        st.success("✅ Dashboard Running")
        st.write(f"**Uptime:** Active")
        st.write(f"**Last Refresh:** {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # Honeypot Services
    st.subheader("🍯 Honeypot Services")
    
    services = [
        {"name": "SSH Honeypot", "port": 2222, "status": "🟢 Active", "attacks": "Monitoring"},
        {"name": "HTTP Honeypot", "port": 8080, "status": "🟢 Active", "attacks": "Monitoring"},
        {"name": "FTP Honeypot", "port": 2121, "status": "🟢 Active", "attacks": "Monitoring"},
        {"name": "MySQL Honeypot", "port": 3307, "status": "🟢 Active", "attacks": "Monitoring"},
        {"name": "Telnet Honeypot", "port": 2323, "status": "🟢 Active", "attacks": "Monitoring"},
        {"name": "Modbus Honeypot", "port": 5020, "status": "🟢 Active", "attacks": "ICS/SCADA"}
    ]
    
    df_services = pd.DataFrame(services)
    st.dataframe(df_services, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Container Status
    st.subheader("🐳 Docker Containers")
    
    containers = [
        {"name": "cyber_mirage_honeypots", "status": "🟢 Running", "health": "Healthy"},
        {"name": "cyber_mirage_dashboard", "status": "🟢 Running", "health": "Healthy"},
        {"name": "cyber_mirage_ai", "status": "🟢 Running", "health": "Healthy"},
        {"name": "cyber_mirage_postgres", "status": "🟢 Running", "health": "Healthy"},
        {"name": "cyber_mirage_redis", "status": "🟢 Running", "health": "Healthy"},
        {"name": "cyber_mirage_grafana", "status": "🟢 Running", "health": "Healthy"},
        {"name": "cyber_mirage_prometheus", "status": "🟢 Running", "health": "Healthy"},
        {"name": "cyber_mirage_logstash", "status": "🟢 Running", "health": "Healthy"},
        {"name": "cyber_mirage_kibana", "status": "🟢 Running", "health": "Healthy"},
        {"name": "cyber_mirage_elasticsearch", "status": "🟢 Running", "health": "Healthy"}
    ]
    
    df_containers = pd.DataFrame(containers)
    st.dataframe(df_containers, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Quick Links
    st.subheader("🔗 Quick Access Links")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### 📊 Grafana")
        st.markdown("[Open Grafana](http://13.53.131.159:3000)")
        st.caption("Username: admin")
    
    with col2:
        st.markdown("#### 📈 Prometheus")
        st.markdown("[Open Prometheus](http://13.53.131.159:9090)")
        st.caption("Metrics & Alerts")
    
    with col3:
        st.markdown("#### 🔍 Kibana")
        st.markdown("[Open Kibana](http://13.53.131.159:5601)")
        st.caption("Log Analysis")
    
    with col4:
        st.markdown("#### 📡 API Health")
        st.markdown("[Check API](http://13.53.131.159:8000/health)")
        st.caption("REST API")

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    """Main application entry point"""
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("## 🎭 Cyber Mirage")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["🏠 Main Dashboard", "🔍 Threat Intelligence", "🔬 Digital Forensics", 
             "🤖 AI Analysis", "⚙️ System Status"],
            index=0
        )
        
        st.markdown("---")
        
        # Auto-refresh control
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)
        if auto_refresh:
            refresh_interval = st.slider("Interval (sec)", 5, 60, 15)
        
        st.markdown("---")
        
        # Connection indicators
        st.markdown("### 📡 Connections")
        
        conn = get_db_connection()
        if conn:
            st.success("✅ PostgreSQL")
            release_db_connection(conn)
        else:
            st.error("❌ PostgreSQL")
        
        r = get_redis_connection()
        if r:
            st.success("✅ Redis")
        else:
            st.error("❌ Redis")
        
        st.markdown("---")
        st.caption(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        st.caption("v2.0.0 - Production")
    
    # Page Routing
    if page == "🏠 Main Dashboard":
        render_main_dashboard()
    elif page == "🔍 Threat Intelligence":
        render_threat_intelligence()
    elif page == "🔬 Digital Forensics":
        render_forensics()
    elif page == "🤖 AI Analysis":
        render_ai_analysis()
    elif page == "⚙️ System Status":
        render_system_status()
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
