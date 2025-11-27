"""
Cyber Mirage - Analysis Module
تحليل التهديدات والذكاء الاصطناعي

This module provides tools for:
- External threat intelligence feeds (AbuseIPDB, VirusTotal, Shodan)
- IP reputation analysis
- GeoIP lookups
- Attack pattern recognition
- A/B testing for deception strategies
- Explainable AI decisions
"""

from .external_feeds import ExternalThreatFeeds
from .threat_intel import ThreatIntelligence
from .ip_reputation import IPReputationChecker
from .geoip_lookup import GeoIPLookup
from .attack_patterns import AttackPatternAnalyzer

__all__ = [
    'ExternalThreatFeeds',
    'ThreatIntelligence',
    'IPReputationChecker',
    'GeoIPLookup',
    'AttackPatternAnalyzer',
]

__version__ = '1.0.0'
__author__ = 'Cyber Mirage Team'
