"""
Cyber Mirage - Digital Forensics Module
مهندس الأدلة الجنائية الرقمية

This module provides tools for:
- Evidence collection from honeypots
- Timeline analysis of attacks
- Log parsing and analysis
- PCAP file analysis
- Chain of custody management
"""

from .evidence_collector import EvidenceCollector
from .timeline_builder import TimelineBuilder
from .log_parser import LogParser
from .pcap_analyzer import PcapAnalyzer
from .chain_of_custody import ChainOfCustody

__all__ = [
    'EvidenceCollector',
    'TimelineBuilder', 
    'LogParser',
    'PcapAnalyzer',
    'ChainOfCustody'
]

__version__ = '1.0.0'
__author__ = 'Cyber Mirage Team - Role 6'
