"""
🔬 Digital Forensics - MITRE ATT&CK Mapping
Maps attack sessions to MITRE ATT&CK framework tactics and techniques.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import psycopg2
import os

# MITRE ATT&CK Mapping for Honeypot Activities
MITRE_ATTACK_MAP = {
    # Initial Access
    'ssh_brute_force': {
        'tactic': 'TA0001 - Initial Access',
        'technique': 'T1078 - Valid Accounts',
        'sub_technique': 'T1078.003 - Local Accounts',
        'description': 'SSH brute force attempts to gain initial access'
    },
    'ftp_anonymous': {
        'tactic': 'TA0001 - Initial Access',
        'technique': 'T1190 - Exploit Public-Facing Application',
        'description': 'FTP anonymous login attempts'
    },
    'http_scan': {
        'tactic': 'TA0043 - Reconnaissance',
        'technique': 'T1595 - Active Scanning',
        'sub_technique': 'T1595.002 - Vulnerability Scanning',
        'description': 'HTTP service scanning and enumeration'
    },
    
    # Discovery
    'directory_listing': {
        'tactic': 'TA0007 - Discovery',
        'technique': 'T1083 - File and Directory Discovery',
        'description': 'Listing files and directories (LIST, NLST commands)'
    },
    'system_info': {
        'tactic': 'TA0007 - Discovery',
        'technique': 'T1082 - System Information Discovery',
        'description': 'Gathering system information'
    },
    
    # Collection
    'file_download': {
        'tactic': 'TA0009 - Collection',
        'technique': 'T1005 - Data from Local System',
        'description': 'Attempting to download files (RETR command)'
    },
    
    # Exfiltration
    'data_exfil': {
        'tactic': 'TA0010 - Exfiltration',
        'technique': 'T1041 - Exfiltration Over C2 Channel',
        'description': 'Data exfiltration attempts'
    },
    
    # Persistence
    'file_upload': {
        'tactic': 'TA0003 - Persistence',
        'technique': 'T1505 - Server Software Component',
        'sub_technique': 'T1505.003 - Web Shell',
        'description': 'Uploading files for persistence (STOR command)'
    },
    
    # Lateral Movement
    'smb_lateral': {
        'tactic': 'TA0008 - Lateral Movement',
        'technique': 'T1021 - Remote Services',
        'sub_technique': 'T1021.002 - SMB/Windows Admin Shares',
        'description': 'SMB enumeration and lateral movement attempts'
    },
    
    # Credential Access
    'password_spray': {
        'tactic': 'TA0006 - Credential Access',
        'technique': 'T1110 - Brute Force',
        'sub_technique': 'T1110.003 - Password Spraying',
        'description': 'Password spraying attacks'
    },
    
    # Impact
    'ransomware_activity': {
        'tactic': 'TA0040 - Impact',
        'technique': 'T1486 - Data Encrypted for Impact',
        'description': 'Ransomware-like file encryption attempts'
    },
    
    # Command and Control
    'c2_beacon': {
        'tactic': 'TA0011 - Command and Control',
        'technique': 'T1071 - Application Layer Protocol',
        'sub_technique': 'T1071.001 - Web Protocols',
        'description': 'C2 beacon activity detected'
    }
}


class MITREMapper:
    """Maps honeypot activities to MITRE ATT&CK framework."""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'cyber_mirage'),
            'user': os.getenv('POSTGRES_USER', 'cybermirage'),
            'password': os.getenv('POSTGRES_PASSWORD', 'ChangeThisToSecurePassword123!')
        }
    
    def get_db(self):
        """Get database connection."""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            print(f"Database connection failed: {e}")
            return None
    
    def classify_attack_action(self, action_text: str, service: str) -> Optional[str]:
        """Classify an attack action into MITRE ATT&CK category."""
        action_lower = action_text.lower()
        
        # SSH-specific
        if service == 'SSH':
            if 'pass' in action_lower or 'password' in action_lower:
                return 'ssh_brute_force'
            elif 'uname' in action_lower or 'whoami' in action_lower:
                return 'system_info'
        
        # FTP-specific
        elif service == 'FTP':
            if action_lower.startswith('user anonymous'):
                return 'ftp_anonymous'
            elif action_lower.startswith('list') or action_lower.startswith('nlst'):
                return 'directory_listing'
            elif action_lower.startswith('retr'):
                return 'file_download'
            elif action_lower.startswith('stor'):
                return 'file_upload'
        
        # HTTP-specific
        elif service == 'HTTP' or service == 'HTTPS':
            if 'scan' in action_lower or 'nmap' in action_lower:
                return 'http_scan'
            elif 'nikto' in action_lower or 'dirb' in action_lower:
                return 'http_scan'
        
        # SMB-specific
        elif service == 'SMB':
            return 'smb_lateral'
        
        # Mysql-specific - SQL Injection attempts
        elif service == 'MySQL':
            if 'select' in action_lower and ('union' in action_lower or 'or 1=1' in action_lower):
                return 'sql_injection'
        
        # Generic patterns
        if 'download' in action_lower or 'get' in action_lower:
            return 'data_exfil'
        elif 'upload' in action_lower or 'put' in action_lower:
            return 'file_upload'
        elif 'encrypt' in action_lower or 'ransom' in action_lower:
            return 'ransomware_activity'
        
        return None
    
    def map_session_to_mitre(self, session_id: str) -> Dict:
        """Map an attack session to MITRE ATT&CK framework."""
        conn = self.get_db()
        if not conn:
            return {}
        
        try:
            cur = conn.cursor()
            
            # Get session info
            cur.execute("""
                SELECT attacker_name, origin, honeypot_type, start_time, end_time, 
                       detected, final_suspicion
                FROM attack_sessions
                WHERE id = %s
            """, (session_id,))
            
            session = cur.fetchone()
            if not session:
                return {}
            
            attacker_name, origin, service, start_time, end_time, detected, suspicion = session
            service = service or 'Unknown'
            
            # Get all actions for this session
            cur.execute("""
                SELECT step_number, action_id, timestamp,  suspicion, data_collected
                FROM attack_actions
                WHERE session_id = %s
                ORDER BY step_number
            """, (session_id,))
            
            actions = cur.fetchall()
            
            # Map actions to MITRE
            mitre_techniques = []
            technique_counts = {}
            
            for action in actions:
                step, action_id, timestamp, suspicion, data_collected = action
                action_text = str(action_id) if action_id else ""
                
                category = self.classify_attack_action(action_text, service)
                if category and category in MITRE_ATTACK_MAP:
                    mitre_info = MITRE_ATTACK_MAP[category]
                    technique_id = mitre_info['technique']
                    
                    # Count occurrences
                    if technique_id not in technique_counts:
                        technique_counts[technique_id] = 0
                    technique_counts[technique_id] += 1
                    
                    mitre_techniques.append({
                        'step': step,
                        'timestamp': timestamp.isoformat() if timestamp else None,
                        'tactic': mitre_info['tactic'],
                        'technique': mitre_info['technique'],
                        'sub_technique': mitre_info.get('sub_technique'),
                        'description': mitre_info['description'],
                        'suspicion_score': float(suspicion) if suspicion else 0.0
                    })
            
            # Calculate attack sophistication
            unique_tactics = len(set(t['tactic'] for t in mitre_techniques))
            unique_techniques = len(set(t['technique'] for t in mitre_techniques))
            
            sophistication = "Low"
            if unique_techniques >= 5:
                sophistication = "High"
            elif unique_techniques >= 3:
                sophistication = "Medium"
            
            cur.close()
            
            return {
                'session_id': session_id,
                'attacker_ip': origin,
                'service': service,
                'start_time': start_time.isoformat() if start_time else None,
                'end_time': end_time.isoformat() if end_time else None,
                'detected': detected,
                'suspicion_score': float(suspicion) if suspicion else 0.0,
                'mitre_techniques': mitre_techniques,
                'unique_tactics': unique_tactics,
                'unique_techniques': unique_techniques,
                'sophistication': sophistication,
                'technique_summary': technique_counts
            }
            
        except Exception as e:
            print(f"Error mapping MITRE ATT&CK: {e}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def generate_mitre_report(self, session_id: str, output_format: str = 'json') -> str:
        """Generate MITRE ATT&CK report for a session."""
        mapping = self.map_session_to_mitre(session_id)
        
        if not mapping:
            return "No data available"
        
        if output_format == 'json':
            return json.dumps(mapping, indent=2)
        
        elif output_format == 'markdown':
            md = f"""# MITRE ATT&CK Mapping Report

## Session Information
- **Session ID**: {mapping['session_id']}
- **Attacker IP**: {mapping['attacker_ip']}
- **Target Service**: {mapping['service']}
- **Start Time**: {mapping['start_time']}
- **End Time**: {mapping['end_time']}
- **Detected**: {'✅ Yes' if mapping['detected'] else '❌ No'}
- **Suspicion Score**: {mapping['suspicion_score']:.2f}

## Attack Analysis
- **Sophistication Level**: {mapping['sophistication']}
- **Unique Tactics**: {mapping['unique_tactics']}
- **Unique Techniques**: {mapping['unique_techniques']}

## MITRE ATT&CK Techniques Observed

"""
            for tech in mapping['mitre_techniques']:
                md += f"""### {tech['technique']}
- **Tactic**: {tech['tactic']}
- **Sub-Technique**: {tech.get('sub_technique', 'N/A')}
- **Description**: {tech['description']}
- **Timestamp**: {tech['timestamp']}
- **Suspicion**: {tech['suspicion_score']:.2f}

---

"""
            
            md += f"""## Technique Summary

"""
            for tech_id, count in sorted(mapping['technique_summary'].items(), key=lambda x: x[1], reverse=True):
                md += f"- **{tech_id}**: {count} occurrences\n"
            
            return md
        
        else:
            return "Unsupported format"


# Example usage
if __name__ == "__main__":
    mapper = MITREMapper()
    
    # Test with a session (replace with actual session ID)
    print("MITRE ATT&CK Mapper initialized")
    print("Sample techniques available:")
    for key, value in list(MITRE_ATTACK_MAP.items())[:5]:
        print(f"  - {key}: {value['technique']}")
