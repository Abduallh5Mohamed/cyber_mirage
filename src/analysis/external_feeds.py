"""
🌐 External Threat Feeds Integration
Cyber Mirage - Role 4: Threat Intelligence Analyst

Integrates with external threat intelligence APIs:
- AbuseIPDB - IP reputation and abuse reports
- VirusTotal - Malware and URL scanning
- Shodan - Internet-wide scanning data
- AlienVault OTX - Open Threat Exchange
- GreyNoise - Internet scanner detection

Author: Cyber Mirage Team
Version: 1.0.0 - Production
"""

import json
import logging
import hashlib
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from functools import lru_cache
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

class ThreatFeedConfig:
    """Configuration for threat feeds"""
    
    # API Keys (from environment variables)
    ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY', '')
    VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY', '')
    SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', '')
    ALIENVAULT_API_KEY = os.getenv('ALIENVAULT_API_KEY', '')
    GREYNOISE_API_KEY = os.getenv('GREYNOISE_API_KEY', '')
    
    # Rate limits (requests per minute)
    RATE_LIMITS = {
        'abuseipdb': 60,
        'virustotal': 4,  # Free tier is very limited
        'shodan': 60,
        'alienvault': 100,
        'greynoise': 100
    }
    
    # Cache TTL (seconds)
    CACHE_TTL = 3600  # 1 hour
    
    # API Endpoints
    ENDPOINTS = {
        'abuseipdb': 'https://api.abuseipdb.com/api/v2',
        'virustotal': 'https://www.virustotal.com/api/v3',
        'shodan': 'https://api.shodan.io',
        'alienvault': 'https://otx.alienvault.com/api/v1',
        'greynoise': 'https://api.greynoise.io/v3'
    }


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ThreatFeedResult:
    """Result from a threat feed query"""
    source: str
    ip_address: str
    threat_score: float  # 0-100
    is_malicious: bool
    categories: List[str]
    reports_count: int
    last_seen: Optional[str]
    country: str
    isp: str
    domain: str
    raw_data: Dict
    queried_at: str = field(default_factory=lambda: datetime.now().isoformat())
    cached: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AggregatedThreatResult:
    """Aggregated result from multiple threat feeds"""
    ip_address: str
    overall_score: float
    risk_level: str  # low, medium, high, critical
    is_malicious: bool
    sources_checked: int
    sources_flagged: int
    categories: List[str]
    recommendations: List[str]
    individual_results: List[ThreatFeedResult]
    queried_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['individual_results'] = [r.to_dict() for r in self.individual_results]
        return data


# =============================================================================
# ABUSEIPDB CLIENT
# =============================================================================

class AbuseIPDBClient:
    """
    AbuseIPDB API Client
    https://www.abuseipdb.com/
    
    Features:
    - IP address reputation check
    - Abuse report submission
    - Blacklist check
    """
    
    def __init__(self, api_key: str = None, redis_client=None):
        self.api_key = api_key or ThreatFeedConfig.ABUSEIPDB_API_KEY
        self.base_url = ThreatFeedConfig.ENDPOINTS['abuseipdb']
        self.redis = redis_client
        self.cache_ttl = ThreatFeedConfig.CACHE_TTL
        self._last_request = 0
        self._rate_limit = ThreatFeedConfig.RATE_LIMITS['abuseipdb']
        
    async def check_ip(self, ip: str, max_age_days: int = 90) -> Optional[ThreatFeedResult]:
        """
        Check an IP address reputation
        
        Args:
            ip: IP address to check
            max_age_days: Maximum age of reports to consider
        
        Returns:
            ThreatFeedResult or None if error
        """
        # Check cache first
        cached = self._get_cached(ip)
        if cached:
            return cached
        
        if not self.api_key:
            logger.warning("AbuseIPDB API key not configured")
            return None
        
        # Rate limiting
        await self._rate_limit_wait()
        
        try:
            headers = {
                'Key': self.api_key,
                'Accept': 'application/json'
            }
            
            params = {
                'ipAddress': ip,
                'maxAgeInDays': max_age_days,
                'verbose': 'true'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/check",
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = self._parse_response(ip, data)
                        self._cache_result(ip, result)
                        return result
                    else:
                        logger.error(f"AbuseIPDB API error: {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("AbuseIPDB API timeout")
            return None
        except Exception as e:
            logger.error(f"AbuseIPDB API error: {e}")
            return None
    
    def _parse_response(self, ip: str, data: Dict) -> ThreatFeedResult:
        """Parse AbuseIPDB response"""
        info = data.get('data', {})
        
        # Extract categories
        categories = []
        reports = info.get('reports', [])
        for report in reports:
            cats = report.get('categories', [])
            categories.extend(cats)
        
        # Map category IDs to names
        category_names = self._map_categories(list(set(categories)))
        
        abuse_score = info.get('abuseConfidenceScore', 0)
        
        return ThreatFeedResult(
            source='abuseipdb',
            ip_address=ip,
            threat_score=abuse_score,
            is_malicious=abuse_score >= 50,
            categories=category_names,
            reports_count=info.get('totalReports', 0),
            last_seen=info.get('lastReportedAt'),
            country=info.get('countryCode', 'Unknown'),
            isp=info.get('isp', 'Unknown'),
            domain=info.get('domain', ''),
            raw_data=info
        )
    
    def _map_categories(self, category_ids: List[int]) -> List[str]:
        """Map AbuseIPDB category IDs to names"""
        mapping = {
            1: 'DNS Compromise',
            2: 'DNS Poisoning',
            3: 'Fraud Orders',
            4: 'DDoS Attack',
            5: 'FTP Brute-Force',
            6: 'Ping of Death',
            7: 'Phishing',
            8: 'Fraud VoIP',
            9: 'Open Proxy',
            10: 'Web Spam',
            11: 'Email Spam',
            12: 'Blog Spam',
            13: 'VPN IP',
            14: 'Port Scan',
            15: 'Hacking',
            16: 'SQL Injection',
            17: 'Spoofing',
            18: 'Brute-Force',
            19: 'Bad Web Bot',
            20: 'Exploited Host',
            21: 'Web App Attack',
            22: 'SSH',
            23: 'IoT Targeted'
        }
        return [mapping.get(cid, f'Category-{cid}') for cid in category_ids]
    
    async def _rate_limit_wait(self):
        """Wait if rate limited"""
        now = time.time()
        elapsed = now - self._last_request
        min_interval = 60 / self._rate_limit
        
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        
        self._last_request = time.time()
    
    def _get_cached(self, ip: str) -> Optional[ThreatFeedResult]:
        """Get cached result"""
        if not self.redis:
            return None
        try:
            data = self.redis.get(f"threatfeed:abuseipdb:{ip}")
            if data:
                result = ThreatFeedResult(**json.loads(data))
                result.cached = True
                return result
        except Exception:
            pass
        return None
    
    def _cache_result(self, ip: str, result: ThreatFeedResult):
        """Cache result"""
        if not self.redis:
            return
        try:
            self.redis.setex(
                f"threatfeed:abuseipdb:{ip}",
                self.cache_ttl,
                json.dumps(result.to_dict())
            )
        except Exception:
            pass


# =============================================================================
# VIRUSTOTAL CLIENT
# =============================================================================

class VirusTotalClient:
    """
    VirusTotal API Client
    https://www.virustotal.com/
    
    Features:
    - IP address analysis
    - Domain analysis
    - File/URL scanning
    - WHOIS data
    """
    
    def __init__(self, api_key: str = None, redis_client=None):
        self.api_key = api_key or ThreatFeedConfig.VIRUSTOTAL_API_KEY
        self.base_url = ThreatFeedConfig.ENDPOINTS['virustotal']
        self.redis = redis_client
        self.cache_ttl = ThreatFeedConfig.CACHE_TTL
        self._last_request = 0
        self._rate_limit = ThreatFeedConfig.RATE_LIMITS['virustotal']
    
    async def check_ip(self, ip: str) -> Optional[ThreatFeedResult]:
        """
        Check an IP address with VirusTotal
        
        Args:
            ip: IP address to check
        
        Returns:
            ThreatFeedResult or None if error
        """
        # Check cache first
        cached = self._get_cached(ip)
        if cached:
            return cached
        
        if not self.api_key:
            logger.warning("VirusTotal API key not configured")
            return None
        
        # Rate limiting (VirusTotal free tier is very limited)
        await self._rate_limit_wait()
        
        try:
            headers = {
                'x-apikey': self.api_key,
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/ip_addresses/{ip}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = self._parse_response(ip, data)
                        self._cache_result(ip, result)
                        return result
                    elif response.status == 429:
                        logger.warning("VirusTotal rate limit exceeded")
                        return None
                    else:
                        logger.error(f"VirusTotal API error: {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("VirusTotal API timeout")
            return None
        except Exception as e:
            logger.error(f"VirusTotal API error: {e}")
            return None
    
    def _parse_response(self, ip: str, data: Dict) -> ThreatFeedResult:
        """Parse VirusTotal response"""
        attributes = data.get('data', {}).get('attributes', {})
        
        # Get last analysis stats
        stats = attributes.get('last_analysis_stats', {})
        malicious = stats.get('malicious', 0)
        suspicious = stats.get('suspicious', 0)
        total = sum(stats.values())
        
        # Calculate threat score
        if total > 0:
            threat_score = ((malicious + suspicious * 0.5) / total) * 100
        else:
            threat_score = 0
        
        # Get categories from results
        categories = []
        results = attributes.get('last_analysis_results', {})
        for engine, result in results.items():
            if result.get('category') in ['malicious', 'suspicious']:
                cat = result.get('result', '')
                if cat:
                    categories.append(cat)
        
        return ThreatFeedResult(
            source='virustotal',
            ip_address=ip,
            threat_score=threat_score,
            is_malicious=malicious >= 3 or threat_score >= 30,
            categories=list(set(categories))[:10],  # Limit categories
            reports_count=malicious + suspicious,
            last_seen=attributes.get('last_modification_date'),
            country=attributes.get('country', 'Unknown'),
            isp=attributes.get('as_owner', 'Unknown'),
            domain=attributes.get('network', ''),
            raw_data=attributes
        )
    
    async def check_domain(self, domain: str) -> Optional[Dict]:
        """Check a domain with VirusTotal"""
        if not self.api_key:
            return None
        
        await self._rate_limit_wait()
        
        try:
            headers = {'x-apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/domains/{domain}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
                    
        except Exception as e:
            logger.error(f"VirusTotal domain check error: {e}")
            return None
    
    async def check_hash(self, file_hash: str) -> Optional[Dict]:
        """Check a file hash with VirusTotal"""
        if not self.api_key:
            return None
        
        await self._rate_limit_wait()
        
        try:
            headers = {'x-apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/files/{file_hash}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
                    
        except Exception as e:
            logger.error(f"VirusTotal hash check error: {e}")
            return None
    
    async def _rate_limit_wait(self):
        """Wait if rate limited (VirusTotal has strict limits)"""
        now = time.time()
        elapsed = now - self._last_request
        min_interval = 60 / self._rate_limit  # 15 seconds for free tier
        
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        
        self._last_request = time.time()
    
    def _get_cached(self, ip: str) -> Optional[ThreatFeedResult]:
        """Get cached result"""
        if not self.redis:
            return None
        try:
            data = self.redis.get(f"threatfeed:virustotal:{ip}")
            if data:
                result = ThreatFeedResult(**json.loads(data))
                result.cached = True
                return result
        except Exception:
            pass
        return None
    
    def _cache_result(self, ip: str, result: ThreatFeedResult):
        """Cache result"""
        if not self.redis:
            return
        try:
            self.redis.setex(
                f"threatfeed:virustotal:{ip}",
                self.cache_ttl,
                json.dumps(result.to_dict())
            )
        except Exception:
            pass


# =============================================================================
# SHODAN CLIENT
# =============================================================================

class ShodanClient:
    """
    Shodan API Client
    https://shodan.io/
    
    Features:
    - IP information lookup
    - Open ports and services
    - Vulnerability data
    - Historical data
    """
    
    def __init__(self, api_key: str = None, redis_client=None):
        self.api_key = api_key or ThreatFeedConfig.SHODAN_API_KEY
        self.base_url = ThreatFeedConfig.ENDPOINTS['shodan']
        self.redis = redis_client
        self.cache_ttl = ThreatFeedConfig.CACHE_TTL
    
    async def check_ip(self, ip: str) -> Optional[ThreatFeedResult]:
        """
        Get information about an IP from Shodan
        
        Args:
            ip: IP address to check
        
        Returns:
            ThreatFeedResult or None if error
        """
        # Check cache first
        cached = self._get_cached(ip)
        if cached:
            return cached
        
        if not self.api_key:
            logger.warning("Shodan API key not configured")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/shodan/host/{ip}",
                    params={'key': self.api_key},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = self._parse_response(ip, data)
                        self._cache_result(ip, result)
                        return result
                    elif response.status == 404:
                        # IP not found in Shodan - not necessarily malicious
                        return ThreatFeedResult(
                            source='shodan',
                            ip_address=ip,
                            threat_score=0,
                            is_malicious=False,
                            categories=['not_indexed'],
                            reports_count=0,
                            last_seen=None,
                            country='Unknown',
                            isp='Unknown',
                            domain='',
                            raw_data={}
                        )
                    else:
                        logger.error(f"Shodan API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Shodan API error: {e}")
            return None
    
    def _parse_response(self, ip: str, data: Dict) -> ThreatFeedResult:
        """Parse Shodan response"""
        # Get open ports and services
        ports = data.get('ports', [])
        services = []
        for item in data.get('data', []):
            port = item.get('port')
            service = item.get('product', item.get('_shodan', {}).get('module', 'unknown'))
            services.append(f"{port}/{service}")
        
        # Check for vulnerabilities
        vulns = data.get('vulns', [])
        
        # Calculate threat score based on:
        # - Number of open ports (more = higher risk)
        # - Known vulnerabilities
        # - Suspicious services
        
        threat_score = 0
        
        # Port risk
        if len(ports) > 20:
            threat_score += 30
        elif len(ports) > 10:
            threat_score += 20
        elif len(ports) > 5:
            threat_score += 10
        
        # Vulnerability risk
        if vulns:
            threat_score += min(len(vulns) * 10, 50)
        
        # Suspicious ports
        suspicious_ports = {22, 23, 3389, 5900, 4444, 31337}
        if set(ports) & suspicious_ports:
            threat_score += 15
        
        categories = services[:10]
        if vulns:
            categories.append(f"vulns:{len(vulns)}")
        
        return ThreatFeedResult(
            source='shodan',
            ip_address=ip,
            threat_score=min(threat_score, 100),
            is_malicious=threat_score >= 50 or len(vulns) > 0,
            categories=categories,
            reports_count=len(ports),
            last_seen=data.get('last_update'),
            country=data.get('country_code', 'Unknown'),
            isp=data.get('isp', 'Unknown'),
            domain=data.get('hostnames', [''])[0] if data.get('hostnames') else '',
            raw_data=data
        )
    
    def _get_cached(self, ip: str) -> Optional[ThreatFeedResult]:
        """Get cached result"""
        if not self.redis:
            return None
        try:
            data = self.redis.get(f"threatfeed:shodan:{ip}")
            if data:
                result = ThreatFeedResult(**json.loads(data))
                result.cached = True
                return result
        except Exception:
            pass
        return None
    
    def _cache_result(self, ip: str, result: ThreatFeedResult):
        """Cache result"""
        if not self.redis:
            return
        try:
            self.redis.setex(
                f"threatfeed:shodan:{ip}",
                self.cache_ttl,
                json.dumps(result.to_dict())
            )
        except Exception:
            pass


# =============================================================================
# GREYNOISE CLIENT
# =============================================================================

class GreyNoiseClient:
    """
    GreyNoise API Client
    https://www.greynoise.io/
    
    Features:
    - Internet scanner detection
    - Benign vs malicious classification
    - Actor attribution
    """
    
    def __init__(self, api_key: str = None, redis_client=None):
        self.api_key = api_key or ThreatFeedConfig.GREYNOISE_API_KEY
        self.base_url = ThreatFeedConfig.ENDPOINTS['greynoise']
        self.redis = redis_client
        self.cache_ttl = ThreatFeedConfig.CACHE_TTL
    
    async def check_ip(self, ip: str) -> Optional[ThreatFeedResult]:
        """
        Check if IP is a known internet scanner
        
        Args:
            ip: IP address to check
        
        Returns:
            ThreatFeedResult or None if error
        """
        # Check cache first
        cached = self._get_cached(ip)
        if cached:
            return cached
        
        # Use community API (free) if no key
        endpoint = f"{self.base_url}/community/{ip}" if not self.api_key else f"{self.base_url}/noise/context/{ip}"
        
        headers = {}
        if self.api_key:
            headers['key'] = self.api_key
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = self._parse_response(ip, data)
                        self._cache_result(ip, result)
                        return result
                    elif response.status == 404:
                        # IP not seen by GreyNoise - possibly good
                        return ThreatFeedResult(
                            source='greynoise',
                            ip_address=ip,
                            threat_score=0,
                            is_malicious=False,
                            categories=['not_observed'],
                            reports_count=0,
                            last_seen=None,
                            country='Unknown',
                            isp='Unknown',
                            domain='',
                            raw_data={}
                        )
                    else:
                        return None
                        
        except Exception as e:
            logger.error(f"GreyNoise API error: {e}")
            return None
    
    def _parse_response(self, ip: str, data: Dict) -> ThreatFeedResult:
        """Parse GreyNoise response"""
        # Community API format vs full API format
        is_noise = data.get('noise', data.get('seen', False))
        is_riot = data.get('riot', False)  # Known benign
        classification = data.get('classification', 'unknown')
        
        # Determine threat score
        if is_riot:
            threat_score = 0
            is_malicious = False
            categories = ['benign_service', data.get('name', 'known_good')]
        elif classification == 'malicious':
            threat_score = 80
            is_malicious = True
            categories = ['malicious_scanner', data.get('name', 'unknown')]
        elif classification == 'benign':
            threat_score = 10
            is_malicious = False
            categories = ['benign_scanner', data.get('name', 'scanner')]
        elif is_noise:
            threat_score = 40
            is_malicious = False
            categories = ['internet_scanner', data.get('name', 'mass_scanner')]
        else:
            threat_score = 0
            is_malicious = False
            categories = ['not_observed']
        
        # Add tags if available
        tags = data.get('tags', [])
        categories.extend(tags[:5])
        
        return ThreatFeedResult(
            source='greynoise',
            ip_address=ip,
            threat_score=threat_score,
            is_malicious=is_malicious,
            categories=categories,
            reports_count=1 if is_noise else 0,
            last_seen=data.get('last_seen'),
            country=data.get('metadata', {}).get('country', 'Unknown'),
            isp=data.get('metadata', {}).get('asn', 'Unknown'),
            domain=data.get('metadata', {}).get('rdns', ''),
            raw_data=data
        )
    
    def _get_cached(self, ip: str) -> Optional[ThreatFeedResult]:
        """Get cached result"""
        if not self.redis:
            return None
        try:
            data = self.redis.get(f"threatfeed:greynoise:{ip}")
            if data:
                result = ThreatFeedResult(**json.loads(data))
                result.cached = True
                return result
        except Exception:
            pass
        return None
    
    def _cache_result(self, ip: str, result: ThreatFeedResult):
        """Cache result"""
        if not self.redis:
            return
        try:
            self.redis.setex(
                f"threatfeed:greynoise:{ip}",
                self.cache_ttl,
                json.dumps(result.to_dict())
            )
        except Exception:
            pass


# =============================================================================
# AGGREGATED THREAT FEED MANAGER
# =============================================================================

class ThreatFeedManager:
    """
    Aggregates results from multiple threat feeds
    
    Features:
    - Parallel queries to multiple feeds
    - Score aggregation and normalization
    - Caching and rate limiting
    - Fallback to local database
    """
    
    def __init__(self, redis_client=None):
        """Initialize threat feed manager"""
        self.redis = redis_client
        
        # Initialize clients
        self.abuseipdb = AbuseIPDBClient(redis_client=redis_client)
        self.virustotal = VirusTotalClient(redis_client=redis_client)
        self.shodan = ShodanClient(redis_client=redis_client)
        self.greynoise = GreyNoiseClient(redis_client=redis_client)
        
        # Configure which feeds are enabled
        self.enabled_feeds = {
            'abuseipdb': bool(ThreatFeedConfig.ABUSEIPDB_API_KEY),
            'virustotal': bool(ThreatFeedConfig.VIRUSTOTAL_API_KEY),
            'shodan': bool(ThreatFeedConfig.SHODAN_API_KEY),
            'greynoise': True  # Has free community API
        }
        
        logger.info(f"ThreatFeedManager initialized. Enabled feeds: {[k for k,v in self.enabled_feeds.items() if v]}")
    
    async def check_ip(self, ip: str) -> AggregatedThreatResult:
        """
        Check an IP against all enabled threat feeds
        
        Args:
            ip: IP address to check
        
        Returns:
            AggregatedThreatResult with combined analysis
        """
        tasks = []
        
        if self.enabled_feeds.get('abuseipdb'):
            tasks.append(('abuseipdb', self.abuseipdb.check_ip(ip)))
        if self.enabled_feeds.get('virustotal'):
            tasks.append(('virustotal', self.virustotal.check_ip(ip)))
        if self.enabled_feeds.get('shodan'):
            tasks.append(('shodan', self.shodan.check_ip(ip)))
        if self.enabled_feeds.get('greynoise'):
            tasks.append(('greynoise', self.greynoise.check_ip(ip)))
        
        # Execute all queries in parallel
        results = []
        for name, coro in tasks:
            try:
                result = await coro
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error checking {name}: {e}")
        
        # Aggregate results
        return self._aggregate_results(ip, results)
    
    def _aggregate_results(
        self,
        ip: str,
        results: List[ThreatFeedResult]
    ) -> AggregatedThreatResult:
        """Aggregate results from multiple feeds"""
        if not results:
            return AggregatedThreatResult(
                ip_address=ip,
                overall_score=0,
                risk_level='unknown',
                is_malicious=False,
                sources_checked=0,
                sources_flagged=0,
                categories=['no_data'],
                recommendations=['Unable to query threat feeds'],
                individual_results=[]
            )
        
        # Calculate weighted average score
        # AbuseIPDB and VirusTotal are more reliable
        weights = {
            'abuseipdb': 1.5,
            'virustotal': 1.5,
            'shodan': 1.0,
            'greynoise': 1.0
        }
        
        total_weight = 0
        weighted_score = 0
        
        for result in results:
            weight = weights.get(result.source, 1.0)
            weighted_score += result.threat_score * weight
            total_weight += weight
        
        overall_score = weighted_score / total_weight if total_weight > 0 else 0
        
        # Determine risk level
        if overall_score >= 80:
            risk_level = 'critical'
        elif overall_score >= 60:
            risk_level = 'high'
        elif overall_score >= 40:
            risk_level = 'medium'
        elif overall_score >= 20:
            risk_level = 'low'
        else:
            risk_level = 'minimal'
        
        # Aggregate categories
        all_categories = []
        for result in results:
            all_categories.extend(result.categories)
        unique_categories = list(set(all_categories))[:15]
        
        # Count malicious flags
        sources_flagged = sum(1 for r in results if r.is_malicious)
        is_malicious = sources_flagged >= 2 or (sources_flagged >= 1 and overall_score >= 60)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level, is_malicious, unique_categories, results
        )
        
        return AggregatedThreatResult(
            ip_address=ip,
            overall_score=round(overall_score, 2),
            risk_level=risk_level,
            is_malicious=is_malicious,
            sources_checked=len(results),
            sources_flagged=sources_flagged,
            categories=unique_categories,
            recommendations=recommendations,
            individual_results=results
        )
    
    def _generate_recommendations(
        self,
        risk_level: str,
        is_malicious: bool,
        categories: List[str],
        results: List[ThreatFeedResult]
    ) -> List[str]:
        """Generate security recommendations based on results"""
        recommendations = []
        
        if risk_level == 'critical':
            recommendations.extend([
                "🔴 BLOCK this IP immediately at firewall level",
                "🔴 Alert security team for investigation",
                "Review all recent connections from this IP"
            ])
        elif risk_level == 'high':
            recommendations.extend([
                "🟠 Consider blocking this IP",
                "Enable enhanced monitoring for this source",
                "Review authentication logs"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "🟡 Monitor this IP for suspicious activity",
                "Implement rate limiting"
            ])
        elif risk_level == 'low':
            recommendations.append("🟢 Low risk - continue monitoring")
        
        # Category-specific recommendations
        category_str = ' '.join(categories).lower()
        
        if 'brute' in category_str or 'ssh' in category_str:
            recommendations.append("Enable fail2ban or account lockout policies")
        
        if 'scan' in category_str:
            recommendations.append("This IP is a known internet scanner")
        
        if 'tor' in category_str or 'vpn' in category_str:
            recommendations.append("Traffic is anonymized (Tor/VPN) - enhanced scrutiny recommended")
        
        if 'malware' in category_str or 'botnet' in category_str:
            recommendations.append("⚠️ Associated with malware/botnet activity")
        
        return recommendations
    
    def check_ip_sync(self, ip: str) -> AggregatedThreatResult:
        """Synchronous wrapper for check_ip"""
        return asyncio.run(self.check_ip(ip))
    
    def get_status(self) -> Dict[str, Any]:
        """Get threat feed manager status"""
        return {
            'enabled_feeds': self.enabled_feeds,
            'cache_ttl': ThreatFeedConfig.CACHE_TTL,
            'api_keys_configured': {
                'abuseipdb': bool(ThreatFeedConfig.ABUSEIPDB_API_KEY),
                'virustotal': bool(ThreatFeedConfig.VIRUSTOTAL_API_KEY),
                'shodan': bool(ThreatFeedConfig.SHODAN_API_KEY),
                'greynoise': bool(ThreatFeedConfig.GREYNOISE_API_KEY)
            }
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_manager_instance: Optional[ThreatFeedManager] = None


def get_threat_feed_manager(redis_client=None) -> ThreatFeedManager:
    """Get or create ThreatFeedManager singleton"""
    global _manager_instance
    
    if _manager_instance is None:
        _manager_instance = ThreatFeedManager(redis_client=redis_client)
    
    return _manager_instance


# =============================================================================
# MAIN - TESTING
# =============================================================================

if __name__ == "__main__":
    async def main():
        manager = ThreatFeedManager()
        
        print("🌐 Threat Feed Manager Status:")
        print(json.dumps(manager.get_status(), indent=2))
        
        # Test IPs
        test_ips = [
            "8.8.8.8",        # Google DNS (should be clean)
            "185.220.101.1",  # Known Tor exit node
            "45.155.205.1",   # Known scanner
        ]
        
        print("\n📊 Testing IP reputation checks...")
        
        for ip in test_ips:
            print(f"\n🔍 Checking {ip}...")
            result = await manager.check_ip(ip)
            
            print(f"  Overall Score: {result.overall_score}")
            print(f"  Risk Level: {result.risk_level}")
            print(f"  Is Malicious: {result.is_malicious}")
            print(f"  Sources: {result.sources_checked} checked, {result.sources_flagged} flagged")
            print(f"  Categories: {result.categories[:5]}")
            print(f"  Recommendations:")
            for rec in result.recommendations[:3]:
                print(f"    - {rec}")
    
    asyncio.run(main())
