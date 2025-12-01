#!/usr/bin/env python3
"""
Attack Filter Script - Distinguishes between Port Scans and Real Attacks
"""
import psycopg2
import os
from datetime import datetime

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'database': 'cyber_mirage',
    'user': 'cybermirage',
    'password': os.getenv('POSTGRES_PASSWORD', 'ChangeThisToSecurePassword123!'),
    'port': 5433
}

def get_attacks(attack_type='all'):
    """
    Get attacks from database with filtering.
    attack_type: 'all', 'real', or 'reconnaissance'
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Base query
    query = """
        SELECT 
            origin as ip,
            attacker_name,
            honeypot_type as service,
            detected,
            created_at,
            ai_analysis
        FROM attack_sessions
        WHERE origin IS NOT NULL
    """
    
    # Add filter based on type
    if attack_type == 'real':
        # Real attacks have actions logged or specific patterns
        query += """
            AND (
                EXISTS (SELECT 1 FROM attack_actions WHERE session_id = attack_sessions.id)
                OR ai_analysis LIKE '%Brute Force%'
                OR ai_analysis LIKE '%SQL Injection%'
                OR ai_analysis LIKE '%exploitation%'
            )
        """
    elif attack_type == 'reconnaissance':
        # Port scans typically have NO actions logged
        query += """
            AND NOT EXISTS (SELECT 1 FROM attack_actions WHERE session_id = attack_sessions.id)
            AND ai_analysis NOT LIKE '%Brute Force%'
            AND ai_analysis NOT LIKE '%SQL Injection%'
        """
    
    query += " ORDER BY created_at DESC LIMIT 50"
    
    cur.execute(query)
    attacks = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return attacks


def print_report(attack_type='all'):
    """Print formatted attack report."""
    attacks = get_attacks(attack_type)
    
    type_labels = {
        'all': 'ALL ACTIVITY',
        'real': 'REAL ATTACKS ONLY (Exploitation Attempts)',
        'reconnaissance': 'RECONNAISSANCE ONLY (Port Scans / Nmap)'
    }
    
    print("\n" + "="*80)
    print(f" CYBER MIRAGE - {type_labels[attack_type]}")
    print("="*80)
    print(f" Total Records: {len(attacks)}")
    print("="*80)
    print(f"{'IP':<18} {'Service':<15} {'Detected':<10} {'Timestamp':<20} {'Analysis'}")
    print("-"*80)
    
    for attack in attacks:
        ip, name, service, detected, timestamp, analysis = attack
        detected_str = "YES" if detected else "NO"
        time_str = timestamp.strftime('%Y-%m-%d %H:%M') if timestamp else 'N/A'
        analysis_short = (analysis[:40] + '...') if analysis and len(analysis) > 40 else (analysis or 'N/A')
        
        print(f"{ip:<18} {service:<15} {detected_str:<10} {time_str:<20} {analysis_short}")
    
    print("="*80)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        filter_type = sys.argv[1].lower()
    else:
        filter_type = 'all'
    
    if filter_type not in ['all', 'real', 'reconnaissance']:
        print("Usage: python filter_attacks.py [all|real|reconnaissance]")
        sys.exit(1)
    
    print_report(filter_type)
