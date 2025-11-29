"""
📊 Threat Intelligence - Local Database & OSINT Integration
Local threat intelligence database with fallback support and automated enrichment.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import requests
from dataclasses import dataclass, asdict
import time

@dataclass
class ThreatIntelRecord:
    """Threat intelligence record."""
    ip_address: str
    reputation_score: int  # 0-100 (0=safe, 100=malicious)
    threat_level: str  # low, medium, high, critical
    country: str
    city: str
    isp: str
    abuse_confidence: int
    total_reports: int
    last_seen: str
    source: str  # local, abuseipdb, virustotal, shodan
    categories: List[str]
    notes: str
    created_at: str
    updated_at: str


class LocalThreatDatabase:
    """Local threat intelligence database with SQLite."""
    
    def __init__(self, db_path: str = "data/threat_intel.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS threat_intel (
                ip_address TEXT PRIMARY KEY,
                reputation_score INTEGER,
                threat_level TEXT,
                country TEXT,
                city TEXT,
                isp TEXT,
                abuse_confidence INTEGER,
                total_reports INTEGER,
                last_seen TEXT,
                source TEXT,
                categories TEXT,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS threat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                event_type TEXT,
                event_data TEXT,
                timestamp TEXT,
                FOREIGN KEY(ip_address) REFERENCES threat_intel(ip_address)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_threat(self, record: ThreatIntelRecord):
        """Add or update threat intelligence record."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT OR REPLACE INTO threat_intel
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.ip_address,
            record.reputation_score,
            record.threat_level,
            record.country,
            record.city,
            record.isp,
            record.abuse_confidence,
            record.total_reports,
            record.last_seen,
            record.source,
            json.dumps(record.categories),
            record.notes,
            record.created_at,
            record.updated_at
        ))
        
        conn.commit()
        conn.close()
    
    def get_threat(self, ip_address: str) -> Optional[ThreatIntelRecord]:
        """Get threat intelligence for an IP."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM threat_intel WHERE ip_address = ?", (ip_address,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            return ThreatIntelRecord(
                ip_address=row[0],
                reputation_score=row[1],
                threat_level=row[2],
                country=row[3],
                city=row[4],
                isp=row[5],
                abuse_confidence=row[6],
                total_reports=row[7],
                last_seen=row[8],
                source=row[9],
                categories=json.loads(row[10]) if row[10] else [],
                notes=row[11] or "",
                created_at=row[12],
                updated_at=row[13]
            )
        return None
    
    def search_threats(self, threat_level: Optional[str] = None, min_score: int = 0) -> List[ThreatIntelRecord]:
        """Search threat database."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        query  = "SELECT * FROM threat_intel WHERE reputation_score >= ?"
        params = [min_score]
        
        if threat_level:
            query += " AND threat_level = ?"
            params.append(threat_level)
        
        query += " ORDER BY reputation_score DESC"
        
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        
        threats = []
        for row in rows:
            threats.append(ThreatIntelRecord(
                ip_address=row[0],
                reputation_score=row[1],
                threat_level=row[2],
                country=row[3],
                city=row[4],
                isp=row[5],
                abuse_confidence=row[6],
                total_reports=row[7],
                last_seen=row[8],
                source=row[9],
                categories=json.loads(row[10]) if row[10] else [],
                notes=row[11] or "",
                created_at=row[12],
                updated_at=row[13]
            ))
        
        return threats


class ThreatIntelligenceEnricher:
    """Enrich IPs with threat intelligence from multiple sources."""
    
    def __init__(self):
        self.local_db = LocalThreatDatabase()
        self.abuseipdb_key = os.getenv('ABUSEIPDB_API_KEY', '')
        self.virustotal_key = os.getenv('VIRUSTOTAL_API_KEY', '')
        self.shodan_key = os.getenv('SHODAN_API_KEY', '')
    
    def enrich_ip(self, ip_address: str) -> ThreatIntelRecord:
        """Enrich IP with threat intelligence from all available sources."""
        
        # Check local database first
        local_record = self.local_db.get_threat(ip_address)
        if local_record:
            # Check if record is fresh (< 24 hours old)
            updated_time = datetime.fromisoformat(local_record.updated_at)
            if datetime.now() - updated_time < timedelta(hours=24):
                return local_record
        
        # Try external APIs
        record = None
        
        # Try AbuseIPDB
        if self.abuseipdb_key:
            record = self._check_abuseipdb(ip_address)
            if record:
                self.local_db.add_threat(record)
                return record
        
        # Fallback: Create basic record
        if not record:
            record = ThreatIntelRecord(
                ip_address=ip_address,
                reputation_score=50,  # Unknown
                threat_level="unknown",
                country="Unknown",
                city="Unknown",
                isp="Unknown",
                abuse_confidence=0,
                total_reports=0,
                last_seen=datetime.now().isoformat(),
                source="local",
                categories=[],
                notes="No external threat intel available",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            self.local_db.add_threat(record)
        
        return record
    
    def _check_abuseipdb(self, ip_address: str) -> Optional[ThreatIntelRecord]:
        """Check IP against AbuseIPDB."""
        if not self.abuseipdb_key:
            return None
        
        try:
            headers = {
                'Key': self.abuseipdb_key,
                'Accept': 'application/json'
            }
            
            params = {
                'ipAddress': ip_address,
                'maxAgeInDays': 90,
                'verbose': ''
            }
            
            response = requests.get(
                'https://api.abuseipdb.com/api/v2/check',
                headers=headers,
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()['data']
                
                # Calculate threat level
                confidence = data['abuseConfidenceScore']
                if confidence >= 80:
                    threat_level = "critical"
                elif confidence >= 60:
                    threat_level = "high"
                elif confidence >= 40:
                    threat_level = "medium"
                else:
                    threat_level = "low"
                
                return ThreatIntelRecord(
                    ip_address=ip_address,
                    reputation_score=confidence,
                    threat_level=threat_level,
                    country=data.get('countryCode', 'Unknown'),
                    city="Unknown",  # AbuseIPDB doesn't provide city
                    isp=data.get('isp', 'Unknown'),
                    abuse_confidence=confidence,
                    total_reports=data.get('totalReports', 0),
                    last_seen=data.get('lastReportedAt', datetime.now().isoformat()),
                    source="abuseipdb",
                    categories=[],  # Can be parsed from data['reports']
                    notes=f"Domain: {data.get('domain', 'N/A')}, Usage: {data.get('usageType', 'N/A')}",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
        except Exception as e:
            print(f"AbuseIPDB API error: {e}")
        
        return None
    
    def generate_daily_report(self) -> Dict:
        """Generate daily threat intelligence summary."""
        threats = self.local_db.search_threats(min_score=50)
        
        # Group by threat level
        by_level = {}
        for threat in threats:
            level = threat.threat_level
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(threat)
        
        # Top attackers
        top_attackers = sorted(threats, key=lambda x: x.reputation_score, reverse=True)[:10]
        
        # Country distribution
        countries = {}
        for threat in threats:
            country = threat.country
            if country not in countries:
                countries[country] = 0
            countries[country] += 1
        
        return {
            'generated_at': datetime.now().isoformat(),
            'total_threats': len(threats),
            'by_level': {k: len(v) for k, v in by_level.items()},
            'top_attackers': [asdict(t) for t in top_attackers],
            'country_distribution': countries
        }


# Example usage
if __name__ == "__main__":
    enricher = ThreatIntelligenceEnricher()
    
    # Test enrichment
    test_ip = "1.2.3.4"
    record = enricher.enrich_ip(test_ip)
    print(f"Enriched {test_ip}:")
    print(json.dumps(asdict(record), indent=2))
    
    # Generate report
    report = enricher.generate_daily_report()
    print("\nDaily Threat Report:")
    print(json.dumps(report, indent=2))
