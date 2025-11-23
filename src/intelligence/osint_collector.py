"""
🔍 OSINT Collector - Open Source Intelligence
جمع المعلومات الاستخبارية من مصادر مفتوحة

يدعم: VirusTotal, AbuseIPDB, AlienVault OTX, GreyNoise, Shodan
"""

import requests
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ThreatIntelligence:
    """معلومات استخبارية عن تهديد"""
    ip: str
    reputation_score: int  # 0-100
    is_malicious: bool
    categories: List[str]
    last_seen: str
    reports: int
    sources: List[str]
    country: str = "Unknown"
    asn: str = "Unknown"


class OSINTCollector:
    """
    جامع استخبارات من مصادر متعددة
    """
    
    def __init__(self):
        # قراءة API keys من environment variables
        self.virustotal_key = os.getenv('VIRUSTOTAL_API_KEY')
        self.abuseipdb_key = os.getenv('ABUSEIPDB_API_KEY')
        self.alienvault_key = os.getenv('ALIENVAULT_API_KEY')
        self.greynoise_key = os.getenv('GREYNOISE_API_KEY')
        self.shodan_key = os.getenv('SHODAN_API_KEY')
        
        self.cache: Dict[str, ThreatIntelligence] = {}
        
        logger.info("🔍 OSINT Collector initialized")
        self._log_available_sources()
    
    def _log_available_sources(self):
        """عرض المصادر المتاحة"""
        sources = []
        if self.virustotal_key:
            sources.append("VirusTotal")
        if self.abuseipdb_key:
            sources.append("AbuseIPDB")
        if self.alienvault_key:
            sources.append("AlienVault OTX")
        if self.greynoise_key:
            sources.append("GreyNoise")
        if self.shodan_key:
            sources.append("Shodan")
        
        if sources:
            logger.info(f"   Available sources: {', '.join(sources)}")
        else:
            logger.warning("   ⚠️ No API keys configured - using mock data")
    
    def check_ip(self, ip: str) -> ThreatIntelligence:
        """
        فحص IP من جميع المصادر
        """
        # التحقق من الكاش أولاً
        if ip in self.cache:
            logger.info(f"📦 Using cached data for {ip}")
            return self.cache[ip]
        
        logger.info(f"🔍 Checking IP: {ip}")
        
        results = []
        
        # جمع من جميع المصادر المتاحة
        if self.virustotal_key:
            vt_result = self._check_virustotal(ip)
            if vt_result:
                results.append(vt_result)
        
        if self.abuseipdb_key:
            abuse_result = self._check_abuseipdb(ip)
            if abuse_result:
                results.append(abuse_result)
        
        if self.alienvault_key:
            otx_result = self._check_alienvault(ip)
            if otx_result:
                results.append(otx_result)
        
        if self.greynoise_key:
            grey_result = self._check_greynoise(ip)
            if grey_result:
                results.append(grey_result)
        
        if self.shodan_key:
            shodan_result = self._check_shodan(ip)
            if shodan_result:
                results.append(shodan_result)
        
        # دمج النتائج
        intel = self._merge_results(ip, results)
        
        # حفظ في الكاش
        self.cache[ip] = intel
        
        return intel
    
    def _check_virustotal(self, ip: str) -> Optional[Dict]:
        """
        فحص عبر VirusTotal
        Free: 500 requests/day
        """
        try:
            url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
            headers = {'x-apikey': self.virustotal_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                attrs = data['data']['attributes']
                stats = attrs['last_analysis_stats']
                
                logger.info(f"   ✓ VirusTotal: {stats.get('malicious', 0)} malicious")
                
                return {
                    'source': 'VirusTotal',
                    'malicious': stats.get('malicious', 0),
                    'suspicious': stats.get('suspicious', 0),
                    'harmless': stats.get('harmless', 0),
                    'country': attrs.get('country', 'Unknown')
                }
            elif response.status_code == 429:
                logger.warning("   ⚠️ VirusTotal: Rate limit exceeded")
            
        except Exception as e:
            logger.error(f"   ✗ VirusTotal error: {e}")
        
        return None
    
    def _check_abuseipdb(self, ip: str) -> Optional[Dict]:
        """
        فحص عبر AbuseIPDB
        Free: 1000 checks/day
        """
        try:
            url = "https://api.abuseipdb.com/api/v2/check"
            headers = {
                'Key': self.abuseipdb_key,
                'Accept': 'application/json'
            }
            params = {
                'ipAddress': ip,
                'maxAgeInDays': 90,
                'verbose': ''
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()['data']
                
                logger.info(f"   ✓ AbuseIPDB: {data.get('abuseConfidenceScore', 0)}% confidence")
                
                return {
                    'source': 'AbuseIPDB',
                    'abuse_score': data.get('abuseConfidenceScore', 0),
                    'total_reports': data.get('totalReports', 0),
                    'is_whitelisted': data.get('isWhitelisted', False),
                    'country': data.get('countryCode', 'Unknown'),
                    'usage_type': data.get('usageType', 'Unknown')
                }
            
        except Exception as e:
            logger.error(f"   ✗ AbuseIPDB error: {e}")
        
        return None
    
    def _check_alienvault(self, ip: str) -> Optional[Dict]:
        """
        فحص عبر AlienVault OTX
        Free: Unlimited! (أفضل خيار مجاني)
        """
        try:
            url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
            headers = {'X-OTX-API-KEY': self.alienvault_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pulse_info = data.get('pulse_info', {})
                
                logger.info(f"   ✓ AlienVault: {pulse_info.get('count', 0)} pulses")
                
                return {
                    'source': 'AlienVault OTX',
                    'pulse_count': pulse_info.get('count', 0),
                    'reputation': data.get('reputation', 0),
                    'country': data.get('country_name', 'Unknown')
                }
        
        except Exception as e:
            logger.error(f"   ✗ AlienVault error: {e}")
        
        return None
    
    def _check_greynoise(self, ip: str) -> Optional[Dict]:
        """
        فحص عبر GreyNoise
        Free: 50 queries/day
        """
        try:
            url = f"https://api.greynoise.io/v3/community/{ip}"
            headers = {'key': self.greynoise_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                logger.info(f"   ✓ GreyNoise: {data.get('classification', 'Unknown')}")
                
                return {
                    'source': 'GreyNoise',
                    'classification': data.get('classification', 'unknown'),
                    'noise': data.get('noise', False),
                    'riot': data.get('riot', False)
                }
        
        except Exception as e:
            logger.error(f"   ✗ GreyNoise error: {e}")
        
        return None
    
    def _check_shodan(self, ip: str) -> Optional[Dict]:
        """
        فحص عبر Shodan
        Free: 100 results/month
        """
        try:
            url = f"https://api.shodan.io/shodan/host/{ip}?key={self.shodan_key}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                logger.info(f"   ✓ Shodan: {len(data.get('ports', []))} ports")
                
                return {
                    'source': 'Shodan',
                    'ports': data.get('ports', []),
                    'vulns': data.get('vulns', []),
                    'hostnames': data.get('hostnames', []),
                    'country': data.get('country_name', 'Unknown'),
                    'org': data.get('org', 'Unknown')
                }
        
        except Exception as e:
            logger.error(f"   ✗ Shodan error: {e}")
        
        return None
    
    def _merge_results(self, ip: str, results: List[Dict]) -> ThreatIntelligence:
        """
        دمج النتائج من مصادر متعددة
        """
        if not results:
            return ThreatIntelligence(
                ip=ip,
                reputation_score=50,  # محايد
                is_malicious=False,
                categories=[],
                last_seen="Unknown",
                reports=0,
                sources=[]
            )
        
        # حساب النتيجة الإجمالية
        total_score = 0
        malicious_count = 0
        total_reports = 0
        sources = []
        categories = []
        country = "Unknown"
        
        for result in results:
            sources.append(result['source'])
            
            if 'country' in result and result['country'] != 'Unknown':
                country = result['country']
            
            if result['source'] == 'VirusTotal':
                if result['malicious'] > 5:
                    malicious_count += 1
                    total_score -= 20
                    categories.append('malware')
                if result['suspicious'] > 3:
                    total_score -= 10
            
            elif result['source'] == 'AbuseIPDB':
                abuse_score = result['abuse_score']
                total_score -= (abuse_score / 5)  # 0-100 -> 0-20
                total_reports += result['total_reports']
                if abuse_score > 50:
                    malicious_count += 1
                    categories.append('abuse')
                if result['is_whitelisted']:
                    total_score += 20
            
            elif result['source'] == 'AlienVault OTX':
                if result['pulse_count'] > 0:
                    malicious_count += 1
                    total_score -= 15
                    categories.append('threat_intel')
            
            elif result['source'] == 'GreyNoise':
                if result['classification'] == 'malicious':
                    malicious_count += 1
                    total_score -= 25
                    categories.append('scanner')
                elif result['classification'] == 'benign':
                    total_score += 10
            
            elif result['source'] == 'Shodan':
                if result.get('vulns'):
                    malicious_count += 1
                    total_score -= 15
                    categories.append('vulnerable')
        
        # النتيجة النهائية
        reputation_score = max(0, min(100, 50 + total_score))
        is_malicious = malicious_count >= 2 or reputation_score < 30
        
        return ThreatIntelligence(
            ip=ip,
            reputation_score=int(reputation_score),
            is_malicious=is_malicious,
            categories=list(set(categories)),
            last_seen=datetime.now().isoformat(),
            reports=total_reports,
            sources=sources,
            country=country
        )
    
    def get_cached_intelligence(self) -> Dict[str, ThreatIntelligence]:
        """الحصول على جميع البيانات المحفوظة"""
        return self.cache.copy()
    
    def clear_cache(self):
        """مسح الكاش"""
        self.cache.clear()
        logger.info("Cache cleared")


# Demo بدون API keys (محاكاة)
class MockOSINTCollector(OSINTCollector):
    """
    نسخة تجريبية بدون API keys
    """
    
    def __init__(self):
        super().__init__()
        self.mock_data = {
            '185.220.101.45': {
                'malicious': True,
                'score': 15,
                'reports': 150,
                'country': 'Russia',
                'categories': ['malware', 'scanner']
            },
            '8.8.8.8': {
                'malicious': False,
                'score': 95,
                'reports': 0,
                'country': 'United States',
                'categories': []
            },
            '45.142.120.50': {
                'malicious': True,
                'score': 20,
                'reports': 89,
                'country': 'Netherlands',
                'categories': ['abuse', 'scanning']
            }
        }
    
    def check_ip(self, ip: str) -> ThreatIntelligence:
        """
        محاكاة الفحص
        """
        if ip in self.mock_data:
            data = self.mock_data[ip]
            return ThreatIntelligence(
                ip=ip,
                reputation_score=data['score'],
                is_malicious=data['malicious'],
                categories=data['categories'],
                last_seen=datetime.now().isoformat(),
                reports=data['reports'],
                sources=['Mock Data'],
                country=data['country']
            )
        
        return ThreatIntelligence(
            ip=ip,
            reputation_score=50,
            is_malicious=False,
            categories=[],
            last_seen="Unknown",
            reports=0,
            sources=[],
            country="Unknown"
        )


# Demo
if __name__ == "__main__":
    print("🔍 OSINT COLLECTOR - DEMO")
    print("="*80)
    
    # استخدام Mock (بدون API keys)
    print("\n📝 Using Mock Data (no API keys required)")
    collector = MockOSINTCollector()
    
    # فحص IPs
    test_ips = ['185.220.101.45', '8.8.8.8', '45.142.120.50', '192.168.1.1']
    
    for ip in test_ips:
        intel = collector.check_ip(ip)
        
        print(f"\n{'='*60}")
        print(f"🔍 IP: {intel.ip}")
        print(f"   📍 Country: {intel.country}")
        print(f"   📊 Reputation: {intel.reputation_score}/100")
        print(f"   🚨 Malicious: {'🔴 YES' if intel.is_malicious else '✅ NO'}")
        print(f"   📝 Reports: {intel.reports}")
        print(f"   🏷️  Categories: {', '.join(intel.categories) if intel.categories else 'None'}")
        print(f"   🔎 Sources: {', '.join(intel.sources)}")
    
    print("\n" + "="*80)
    print("\n📚 للاستخدام الحقيقي:")
    print("\n1️⃣ احصل على API keys المجانية:")
    print("   ✅ VirusTotal (500/day): https://www.virustotal.com/gui/join-us")
    print("   ✅ AbuseIPDB (1000/day): https://www.abuseipdb.com/register")
    print("   ✅ AlienVault OTX (Unlimited!): https://otx.alienvault.com/")
    print("   ⚠️ GreyNoise (50/day): https://www.greynoise.io/")
    print("   💰 Shodan (100/month): https://account.shodan.io/")
    
    print("\n2️⃣ ضع في environment variables:")
    print("   Windows PowerShell:")
    print("   $env:VIRUSTOTAL_API_KEY='your_key_here'")
    print("   $env:ABUSEIPDB_API_KEY='your_key_here'")
    print("   $env:ALIENVAULT_API_KEY='your_key_here'")
    
    print("\n   Linux/macOS:")
    print("   export VIRUSTOTAL_API_KEY='your_key_here'")
    print("   export ABUSEIPDB_API_KEY='your_key_here'")
    print("   export ALIENVAULT_API_KEY='your_key_here'")
    
    print("\n3️⃣ استخدم OSINTCollector (بدلاً من Mock):")
    print("   collector = OSINTCollector()")
    print("   intel = collector.check_ip('185.220.101.45')")
    
    print("\n✅ Demo Complete!")
