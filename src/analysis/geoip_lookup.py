"""
GeoIP Lookup Module - تحديد الموقع الجغرافي
Cyber Mirage - Role 4: Threat Intelligence Analyst

يقوم بـ:
- تحديد الموقع الجغرافي لعناوين IP
- تحليل توزيع الهجمات جغرافياً
- إنشاء خرائط حرارية للتهديدات
"""

import json
import logging
import math
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GeoLocation:
    """معلومات الموقع الجغرافي"""
    ip_address: str
    country_code: str
    country_name: str
    region: str
    city: str
    latitude: float
    longitude: float
    timezone: str
    isp: str
    organization: str
    asn: str
    asn_name: str
    is_proxy: bool
    is_vpn: bool
    is_tor: bool
    is_datacenter: bool
    confidence: float
    lookup_time: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass 
class GeoStatistics:
    """إحصائيات جغرافية"""
    total_lookups: int
    by_country: Dict[str, int]
    by_region: Dict[str, int]
    by_city: Dict[str, int]
    by_asn: Dict[str, int]
    proxy_count: int
    vpn_count: int
    tor_count: int
    datacenter_count: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


class GeoIPLookup:
    """
    نظام تحديد الموقع الجغرافي لعناوين IP
    """
    
    # قاعدة بيانات مبسطة للـ IP ranges (للتجربة)
    # في الإنتاج: استخدم MaxMind GeoIP2 أو ip-api.com
    IP_DATABASE = {
        # أمثلة لنطاقات معروفة
        "185.220.": {
            "country_code": "DE",
            "country_name": "Germany",
            "region": "Europe",
            "city": "Frankfurt",
            "latitude": 50.1109,
            "longitude": 8.6821,
            "timezone": "Europe/Berlin",
            "isp": "Tor Network",
            "is_tor": True
        },
        "45.33.": {
            "country_code": "US",
            "country_name": "United States",
            "region": "North America",
            "city": "Fremont",
            "latitude": 37.5485,
            "longitude": -121.9886,
            "timezone": "America/Los_Angeles",
            "isp": "Linode",
            "is_datacenter": True
        },
        "167.99.": {
            "country_code": "US",
            "country_name": "United States",
            "region": "North America",
            "city": "New York",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York",
            "isp": "DigitalOcean",
            "is_datacenter": True
        },
        "94.102.": {
            "country_code": "NL",
            "country_name": "Netherlands",
            "region": "Europe",
            "city": "Amsterdam",
            "latitude": 52.3676,
            "longitude": 4.9041,
            "timezone": "Europe/Amsterdam",
            "isp": "Serverius",
            "is_datacenter": True
        },
        "141.98.": {
            "country_code": "RU",
            "country_name": "Russia",
            "region": "Europe",
            "city": "Moscow",
            "latitude": 55.7558,
            "longitude": 37.6173,
            "timezone": "Europe/Moscow",
            "isp": "Unknown Hosting"
        },
        "192.168.": {
            "country_code": "XX",
            "country_name": "Private Network",
            "region": "Local",
            "city": "Internal",
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC",
            "isp": "Internal Network"
        },
        "10.": {
            "country_code": "XX",
            "country_name": "Private Network",
            "region": "Local",
            "city": "Internal",
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC",
            "isp": "Internal Network"
        },
        "172.": {
            "country_code": "XX",
            "country_name": "Private Network",
            "region": "Local",
            "city": "Internal",
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC",
            "isp": "Internal Network"
        }
    }
    
    # ASN Database (مبسطة)
    ASN_DATABASE = {
        "AS174": {"name": "Cogent Communications", "type": "isp"},
        "AS3356": {"name": "Lumen Technologies", "type": "isp"},
        "AS7922": {"name": "Comcast", "type": "isp"},
        "AS14618": {"name": "Amazon AWS", "type": "datacenter"},
        "AS15169": {"name": "Google", "type": "datacenter"},
        "AS8075": {"name": "Microsoft Azure", "type": "datacenter"},
        "AS63949": {"name": "Linode", "type": "datacenter"},
        "AS14061": {"name": "DigitalOcean", "type": "datacenter"},
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize GeoIP lookup system
        
        Args:
            api_key: API key for external service (optional)
        """
        self.api_key = api_key
        self.cache: Dict[str, GeoLocation] = {}
        self.statistics = GeoStatistics(
            total_lookups=0,
            by_country=defaultdict(int),
            by_region=defaultdict(int),
            by_city=defaultdict(int),
            by_asn=defaultdict(int),
            proxy_count=0,
            vpn_count=0,
            tor_count=0,
            datacenter_count=0
        )
        
        logger.info("GeoIP Lookup system initialized")
    
    def lookup(self, ip: str, use_cache: bool = True) -> GeoLocation:
        """
        البحث عن الموقع الجغرافي لـ IP
        
        Args:
            ip: عنوان IP
            use_cache: استخدام الكاش
        
        Returns:
            معلومات الموقع
        """
        # فحص الكاش
        if use_cache and ip in self.cache:
            return self.cache[ip]
        
        # البحث في قاعدة البيانات المحلية
        geo_data = self._lookup_local(ip)
        
        # إنشاء النتيجة
        result = GeoLocation(
            ip_address=ip,
            country_code=geo_data.get("country_code", "XX"),
            country_name=geo_data.get("country_name", "Unknown"),
            region=geo_data.get("region", "Unknown"),
            city=geo_data.get("city", "Unknown"),
            latitude=geo_data.get("latitude", 0.0),
            longitude=geo_data.get("longitude", 0.0),
            timezone=geo_data.get("timezone", "UTC"),
            isp=geo_data.get("isp", "Unknown"),
            organization=geo_data.get("organization", "Unknown"),
            asn=geo_data.get("asn", ""),
            asn_name=geo_data.get("asn_name", ""),
            is_proxy=geo_data.get("is_proxy", False),
            is_vpn=geo_data.get("is_vpn", False),
            is_tor=geo_data.get("is_tor", False),
            is_datacenter=geo_data.get("is_datacenter", False),
            confidence=geo_data.get("confidence", 0.5),
            lookup_time=datetime.now().isoformat()
        )
        
        # تحديث الكاش والإحصائيات
        self.cache[ip] = result
        self._update_statistics(result)
        
        return result
    
    def _lookup_local(self, ip: str) -> Dict[str, Any]:
        """البحث في قاعدة البيانات المحلية"""
        
        # البحث حسب البادئة
        for prefix, data in self.IP_DATABASE.items():
            if ip.startswith(prefix):
                return {
                    **data,
                    "confidence": 0.8,
                    "asn": self._guess_asn(data.get("isp", "")),
                    "asn_name": data.get("isp", ""),
                    "organization": data.get("isp", "")
                }
        
        # إذا لم يُعثر - توليد بيانات افتراضية
        return self._generate_default_geo(ip)
    
    def _generate_default_geo(self, ip: str) -> Dict[str, Any]:
        """توليد بيانات جغرافية افتراضية"""
        
        # تحليل بسيط حسب أول octet
        try:
            first_octet = int(ip.split('.')[0])
        except:
            first_octet = 0
        
        # تخمين المنطقة حسب النطاق
        if first_octet < 50:
            return {
                "country_code": "US",
                "country_name": "United States",
                "region": "North America",
                "city": "Unknown",
                "latitude": 37.0902,
                "longitude": -95.7129,
                "timezone": "America/Chicago",
                "isp": "Unknown",
                "confidence": 0.3
            }
        elif first_octet < 100:
            return {
                "country_code": "EU",
                "country_name": "Europe",
                "region": "Europe",
                "city": "Unknown",
                "latitude": 50.0,
                "longitude": 10.0,
                "timezone": "Europe/Berlin",
                "isp": "Unknown",
                "confidence": 0.3
            }
        elif first_octet < 150:
            return {
                "country_code": "AS",
                "country_name": "Asia",
                "region": "Asia",
                "city": "Unknown",
                "latitude": 35.0,
                "longitude": 105.0,
                "timezone": "Asia/Shanghai",
                "isp": "Unknown",
                "confidence": 0.3
            }
        else:
            return {
                "country_code": "XX",
                "country_name": "Unknown",
                "region": "Unknown",
                "city": "Unknown",
                "latitude": 0.0,
                "longitude": 0.0,
                "timezone": "UTC",
                "isp": "Unknown",
                "confidence": 0.2
            }
    
    def _guess_asn(self, isp: str) -> str:
        """تخمين ASN من اسم الـ ISP"""
        isp_lower = isp.lower()
        
        if "amazon" in isp_lower or "aws" in isp_lower:
            return "AS14618"
        elif "google" in isp_lower:
            return "AS15169"
        elif "microsoft" in isp_lower or "azure" in isp_lower:
            return "AS8075"
        elif "linode" in isp_lower:
            return "AS63949"
        elif "digitalocean" in isp_lower:
            return "AS14061"
        elif "comcast" in isp_lower:
            return "AS7922"
        else:
            return ""
    
    def _update_statistics(self, geo: GeoLocation):
        """تحديث الإحصائيات"""
        self.statistics.total_lookups += 1
        self.statistics.by_country[geo.country_code] += 1
        self.statistics.by_region[geo.region] += 1
        self.statistics.by_city[geo.city] += 1
        
        if geo.asn:
            self.statistics.by_asn[geo.asn] += 1
        
        if geo.is_proxy:
            self.statistics.proxy_count += 1
        if geo.is_vpn:
            self.statistics.vpn_count += 1
        if geo.is_tor:
            self.statistics.tor_count += 1
        if geo.is_datacenter:
            self.statistics.datacenter_count += 1
    
    def bulk_lookup(self, ips: List[str]) -> Dict[str, GeoLocation]:
        """
        بحث مجموعة من عناوين IP
        
        Args:
            ips: قائمة عناوين IP
        
        Returns:
            نتائج البحث
        """
        results = {}
        for ip in ips:
            results[ip] = self.lookup(ip)
        return results
    
    def calculate_distance(self, ip1: str, ip2: str) -> float:
        """
        حساب المسافة بين موقعين (بالكيلومتر)
        
        Args:
            ip1: عنوان IP الأول
            ip2: عنوان IP الثاني
        
        Returns:
            المسافة بالكيلومتر
        """
        geo1 = self.lookup(ip1)
        geo2 = self.lookup(ip2)
        
        return self._haversine(
            geo1.latitude, geo1.longitude,
            geo2.latitude, geo2.longitude
        )
    
    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """حساب المسافة باستخدام صيغة Haversine"""
        R = 6371  # نصف قطر الأرض بالكيلومتر
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def get_attack_heatmap_data(self) -> List[Dict]:
        """
        الحصول على بيانات الخريطة الحرارية
        
        Returns:
            بيانات للخريطة
        """
        heatmap_data = []
        
        for ip, geo in self.cache.items():
            if geo.latitude != 0.0 or geo.longitude != 0.0:
                heatmap_data.append({
                    "lat": geo.latitude,
                    "lon": geo.longitude,
                    "ip": ip,
                    "country": geo.country_name,
                    "city": geo.city,
                    "weight": 1
                })
        
        return heatmap_data
    
    def get_country_summary(self) -> Dict[str, Dict]:
        """
        ملخص حسب الدول
        
        Returns:
            ملخص الدول
        """
        summary = {}
        
        for country, count in self.statistics.by_country.items():
            # الحصول على عينة IP من هذه الدولة
            sample_ip = None
            for ip, geo in self.cache.items():
                if geo.country_code == country:
                    sample_ip = ip
                    break
            
            if sample_ip:
                geo = self.cache[sample_ip]
                summary[country] = {
                    "country_name": geo.country_name,
                    "attack_count": count,
                    "region": geo.region,
                    "sample_cities": list(set(
                        g.city for g in self.cache.values() 
                        if g.country_code == country
                    ))[:5]
                }
        
        return summary
    
    def get_statistics(self) -> Dict[str, Any]:
        """الحصول على الإحصائيات"""
        return {
            "total_lookups": self.statistics.total_lookups,
            "cached_ips": len(self.cache),
            "countries": len(self.statistics.by_country),
            "top_countries": dict(
                sorted(self.statistics.by_country.items(), 
                       key=lambda x: x[1], reverse=True)[:10]
            ),
            "top_cities": dict(
                sorted(self.statistics.by_city.items(),
                       key=lambda x: x[1], reverse=True)[:10]
            ),
            "anonymization": {
                "proxy": self.statistics.proxy_count,
                "vpn": self.statistics.vpn_count,
                "tor": self.statistics.tor_count,
                "datacenter": self.statistics.datacenter_count
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_report(self) -> str:
        """توليد تقرير"""
        stats = self.get_statistics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║              CYBER MIRAGE - GEOIP ANALYSIS REPORT                ║
╠══════════════════════════════════════════════════════════════════╣
║  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<50} ║
╠══════════════════════════════════════════════════════════════════╣

📊 STATISTICS:
═══════════════════════════════════════════════════════════════════
  Total Lookups: {stats['total_lookups']}
  Cached IPs: {stats['cached_ips']}
  Unique Countries: {stats['countries']}

🌍 TOP COUNTRIES:
"""
        for country, count in stats['top_countries'].items():
            flag = self._get_country_flag(country)
            report += f"  {flag} {country}: {count} attacks\n"
        
        report += "\n🏙️ TOP CITIES:\n"
        for city, count in stats['top_cities'].items():
            report += f"  📍 {city}: {count}\n"
        
        report += f"""
🔒 ANONYMIZATION DETECTION:
  🧅 Tor Exit Nodes: {stats['anonymization']['tor']}
  🔐 VPN: {stats['anonymization']['vpn']}
  🌐 Proxy: {stats['anonymization']['proxy']}
  🖥️ Datacenter: {stats['anonymization']['datacenter']}

═══════════════════════════════════════════════════════════════════
                    End of GeoIP Analysis Report
╚══════════════════════════════════════════════════════════════════╝
"""
        return report
    
    def _get_country_flag(self, country_code: str) -> str:
        """الحصول على علم الدولة (emoji)"""
        flags = {
            "US": "🇺🇸", "DE": "🇩🇪", "NL": "🇳🇱", "RU": "🇷🇺",
            "CN": "🇨🇳", "GB": "🇬🇧", "FR": "🇫🇷", "JP": "🇯🇵",
            "BR": "🇧🇷", "IN": "🇮🇳", "KR": "🇰🇷", "AU": "🇦🇺",
            "CA": "🇨🇦", "IT": "🇮🇹", "ES": "🇪🇸", "XX": "🏳️"
        }
        return flags.get(country_code, "🏳️")
    
    def export_geojson(self) -> str:
        """
        تصدير البيانات بتنسيق GeoJSON
        
        Returns:
            GeoJSON string
        """
        features = []
        
        for ip, geo in self.cache.items():
            if geo.latitude != 0.0 or geo.longitude != 0.0:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [geo.longitude, geo.latitude]
                    },
                    "properties": {
                        "ip": ip,
                        "country": geo.country_name,
                        "city": geo.city,
                        "isp": geo.isp,
                        "is_tor": geo.is_tor,
                        "is_datacenter": geo.is_datacenter
                    }
                })
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return json.dumps(geojson, indent=2)


if __name__ == "__main__":
    # اختبار
    geo = GeoIPLookup()
    
    # فحص IPs
    test_ips = ["185.220.101.50", "167.99.45.100", "192.168.1.100", "8.8.8.8"]
    
    for ip in test_ips:
        result = geo.lookup(ip)
        print(f"\n{ip}:")
        print(f"  Country: {result.country_name} ({result.country_code})")
        print(f"  City: {result.city}")
        print(f"  Location: {result.latitude}, {result.longitude}")
        print(f"  ISP: {result.isp}")
        print(f"  Tor: {result.is_tor}, Datacenter: {result.is_datacenter}")
    
    print("\n" + geo.generate_report())
