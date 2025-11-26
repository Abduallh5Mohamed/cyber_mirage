#!/usr/bin/env python3
"""
🧠 AI Analyzer - Real Attack Analysis with Machine Learning
تحليل ذكي للهجمات مع تصنيف MITRE ATT&CK
"""

import os
import sys
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import psycopg2
import redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Environment configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'changeme123')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'cyber_mirage')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'cybermirage')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')


# MITRE ATT&CK Mappings
MITRE_TACTICS = {
    'SSH': {
        'tactic': 'Initial Access',
        'technique': 'T1078 - Valid Accounts / T1110 - Brute Force',
        'description': 'Attempting SSH authentication to gain initial access'
    },
    'FTP': {
        'tactic': 'Initial Access',
        'technique': 'T1078 - Valid Accounts',
        'description': 'Attempting FTP access for file transfer'
    },
    'HTTP': {
        'tactic': 'Reconnaissance / Initial Access',
        'technique': 'T1595 - Active Scanning / T1190 - Exploit Public-Facing Application',
        'description': 'Web application scanning or exploitation attempt'
    },
    'HTTPS': {
        'tactic': 'Initial Access',
        'technique': 'T1190 - Exploit Public-Facing Application',
        'description': 'Encrypted web attack attempt'
    },
    'MySQL': {
        'tactic': 'Initial Access / Collection',
        'technique': 'T1078 - Valid Accounts / T1213 - Data from Information Repositories',
        'description': 'Database access attempt for data exfiltration'
    },
    'PostgreSQL': {
        'tactic': 'Initial Access / Collection',
        'technique': 'T1078 - Valid Accounts / T1213 - Data from Information Repositories',
        'description': 'PostgreSQL database attack attempt'
    },
    'Telnet': {
        'tactic': 'Initial Access',
        'technique': 'T1078 - Valid Accounts / T1021 - Remote Services',
        'description': 'Legacy remote access attempt (high risk indicator)'
    },
    'Modbus': {
        'tactic': 'Initial Access / Impact',
        'technique': 'T0886 - Remote Services / T0831 - Manipulation of Control',
        'description': 'ICS/SCADA system attack (critical infrastructure)'
    },
    'Unknown': {
        'tactic': 'Reconnaissance',
        'technique': 'T1595 - Active Scanning',
        'description': 'Unknown service probing'
    }
}

# Skill level indicators
SKILL_INDICATORS = {
    'low': {
        'patterns': ['admin', 'root', 'test', '123456', 'password'],
        'behavior': 'Simple brute force with common credentials',
        'level': 1.0
    },
    'medium': {
        'patterns': ['nmap', 'nikto', 'sqlmap'],
        'behavior': 'Using automated scanning tools',
        'level': 5.0
    },
    'high': {
        'patterns': ['metasploit', 'cobalt', 'beacon'],
        'behavior': 'Using advanced exploitation frameworks',
        'level': 8.0
    },
    'expert': {
        'patterns': ['0day', 'custom', 'apt'],
        'behavior': 'Custom exploits or APT-like behavior',
        'level': 10.0
    }
}


class AIAnalyzer:
    """AI-powered attack analyzer"""
    
    def __init__(self):
        self.redis_client = None
        self.db_connection = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis and PostgreSQL"""
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
        
        try:
            self.db_connection = psycopg2.connect(
                host=POSTGRES_HOST,
                database=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
            logger.info("✅ Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
    
    def calculate_threat_score(self, ip: str, service: str, attack_count: int) -> float:
        """Calculate threat score (0-100) based on multiple factors"""
        score = 0.0
        
        # Base score from attack count
        if attack_count >= 100:
            score += 40
        elif attack_count >= 50:
            score += 30
        elif attack_count >= 20:
            score += 20
        elif attack_count >= 5:
            score += 10
        else:
            score += 5
        
        # Service risk multiplier
        service_risk = {
            'SSH': 1.5,
            'MySQL': 1.8,
            'PostgreSQL': 1.8,
            'Telnet': 2.0,
            'Modbus': 2.5,
            'HTTP': 1.0,
            'FTP': 1.2
        }
        score *= service_risk.get(service, 1.0)
        
        # Check for persistence (attacking over time)
        if self.redis_client:
            try:
                threat_data = self.redis_client.hgetall(f"threat:{ip}")
                if threat_data:
                    first_seen = threat_data.get('first_seen')
                    if first_seen:
                        # Persistent attacker bonus
                        score += 15
            except:
                pass
        
        return min(score, 100.0)
    
    def determine_skill_level(self, attacker_name: str, service: str) -> Tuple[float, str]:
        """Determine attacker skill level"""
        name_lower = attacker_name.lower()
        
        # Check for tool indicators
        if any(tool in name_lower for tool in ['metasploit', 'cobalt', 'empire']):
            return 8.0, 'Advanced Persistent Threat (APT)'
        
        if any(tool in name_lower for tool in ['nmap', 'nikto', 'sqlmap', 'burp']):
            return 5.0, 'Automated Scanner / Penetration Tester'
        
        if any(cred in name_lower for cred in ['admin', 'root', 'test', '123456']):
            return 2.0, 'Script Kiddie / Opportunistic'
        
        # Service-based estimation
        service_skill = {
            'Modbus': (7.0, 'ICS/SCADA Specialist'),
            'PostgreSQL': (5.0, 'Database Expert'),
            'MySQL': (4.0, 'Database Attacker'),
            'SSH': (3.0, 'System Attacker'),
            'HTTP': (2.5, 'Web Attacker'),
            'FTP': (2.0, 'Basic Attacker'),
            'Telnet': (1.5, 'Legacy System Hunter')
        }
        
        return service_skill.get(service, (3.0, 'Unknown Profile'))
    
    def get_mitre_mapping(self, service: str) -> Dict:
        """Get MITRE ATT&CK mapping for service"""
        return MITRE_TACTICS.get(service, MITRE_TACTICS['Unknown'])
    
    def analyze_attack(self, ip: str, service: str, attacker_name: str) -> Dict:
        """Full AI analysis of an attack"""
        
        # Get attack count from Redis
        attack_count = 1
        if self.redis_client:
            try:
                count = self.redis_client.hget(f"threat:{ip}", 'count')
                if count:
                    attack_count = int(count)
            except:
                pass
        
        # Calculate metrics
        threat_score = self.calculate_threat_score(ip, service, attack_count)
        skill_level, skill_desc = self.determine_skill_level(attacker_name, service)
        mitre = self.get_mitre_mapping(service)
        
        # Determine threat level
        if threat_score >= 80:
            threat_level = 'CRITICAL'
            recommendation = 'IMMEDIATE BLOCK - Active threat detected'
        elif threat_score >= 60:
            threat_level = 'HIGH'
            recommendation = 'Monitor closely - Consider blocking'
        elif threat_score >= 40:
            threat_level = 'MEDIUM'
            recommendation = 'Track activity - Gather more intel'
        else:
            threat_level = 'LOW'
            recommendation = 'Log and monitor - Opportunistic scan'
        
        analysis = {
            'ip': ip,
            'service': service,
            'threat_score': round(threat_score, 1),
            'threat_level': threat_level,
            'skill_level': round(skill_level, 1),
            'skill_description': skill_desc,
            'attack_count': attack_count,
            'mitre_tactic': mitre['tactic'],
            'mitre_technique': mitre['technique'],
            'mitre_description': mitre['description'],
            'recommendation': recommendation,
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Cache in Redis
        if self.redis_client:
            try:
                self.redis_client.hset(f"ai_analysis:{ip}", mapping={
                    'threat_score': str(analysis['threat_score']),
                    'threat_level': analysis['threat_level'],
                    'skill_level': str(analysis['skill_level']),
                    'mitre_tactic': analysis['mitre_tactic'],
                    'last_analyzed': analysis['analyzed_at']
                })
                self.redis_client.expire(f"ai_analysis:{ip}", 3600)  # 1 hour cache
            except Exception as e:
                logger.error(f"Failed to cache analysis: {e}")
        
        return analysis
    
    def get_all_analyses(self, limit: int = 50) -> List[Dict]:
        """Get AI analyses for recent attacks"""
        analyses = []
        
        if not self.db_connection:
            return analyses
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT DISTINCT origin, attacker_name
                FROM attack_sessions
                WHERE origin IS NOT NULL
                ORDER BY start_time DESC
                LIMIT %s
            """, (limit,))
            
            rows = cursor.fetchall()
            cursor.close()
            
            for ip, attacker_name in rows:
                # Extract service from attacker_name
                service = 'Unknown'
                if attacker_name:
                    parts = attacker_name.split('_')
                    if len(parts) >= 3:
                        service = parts[-1]
                
                analysis = self.analyze_attack(ip, service, attacker_name or '')
                analyses.append(analysis)
            
        except Exception as e:
            logger.error(f"Failed to get analyses: {e}")
        
        return analyses
    
    def get_threat_summary(self) -> Dict:
        """Get overall threat summary"""
        summary = {
            'critical_threats': 0,
            'high_threats': 0,
            'medium_threats': 0,
            'low_threats': 0,
            'total_analyzed': 0,
            'avg_threat_score': 0.0,
            'top_tactics': {},
            'top_skills': {}
        }
        
        analyses = self.get_all_analyses(100)
        
        if not analyses:
            return summary
        
        scores = []
        tactics = {}
        skills = {}
        
        for a in analyses:
            summary['total_analyzed'] += 1
            scores.append(a['threat_score'])
            
            # Count threat levels
            level = a['threat_level']
            if level == 'CRITICAL':
                summary['critical_threats'] += 1
            elif level == 'HIGH':
                summary['high_threats'] += 1
            elif level == 'MEDIUM':
                summary['medium_threats'] += 1
            else:
                summary['low_threats'] += 1
            
            # Count tactics
            tactic = a['mitre_tactic']
            tactics[tactic] = tactics.get(tactic, 0) + 1
            
            # Count skill descriptions
            skill = a['skill_description']
            skills[skill] = skills.get(skill, 0) + 1
        
        summary['avg_threat_score'] = round(sum(scores) / len(scores), 1) if scores else 0
        summary['top_tactics'] = dict(sorted(tactics.items(), key=lambda x: x[1], reverse=True)[:5])
        summary['top_skills'] = dict(sorted(skills.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return summary


# Flask API for Dashboard
def create_api():
    """Create Flask API for AI analysis"""
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    analyzer = AIAnalyzer()
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'AI Analyzer'})
    
    @app.route('/analyze/<ip>')
    def analyze_ip(ip):
        service = 'Unknown'
        analysis = analyzer.analyze_attack(ip, service, f"Attacker_{ip}")
        return jsonify(analysis)
    
    @app.route('/analyses')
    def get_analyses():
        analyses = analyzer.get_all_analyses(50)
        return jsonify(analyses)
    
    @app.route('/summary')
    def get_summary():
        summary = analyzer.get_threat_summary()
        return jsonify(summary)
    
    return app


if __name__ == '__main__':
    # Test mode
    analyzer = AIAnalyzer()
    
    # Test analysis
    test_analysis = analyzer.analyze_attack(
        ip='192.168.1.100',
        service='SSH',
        attacker_name='Attacker_192.168.1.100_SSH'
    )
    
    print("\n🧠 AI Analysis Result:")
    print(json.dumps(test_analysis, indent=2))
    
    # Get summary
    summary = analyzer.get_threat_summary()
    print("\n📊 Threat Summary:")
    print(json.dumps(summary, indent=2))
