"""
Log Parser - محلل السجلات
Cyber Mirage Forensics Module

يقوم بتحليل:
- Docker container logs
- System logs
- Application logs
- Security logs
"""

import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, asdict
from enum import Enum
from collections import Counter, defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """مستويات السجلات"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ParsedLogEntry:
    """سجل محلّل"""
    timestamp: str
    level: str
    source: str
    message: str
    raw_line: str
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AttackIndicator:
    """مؤشر هجوم"""
    indicator_type: str
    value: str
    confidence: float
    context: str
    timestamp: str


class LogParser:
    """
    محلل السجلات متعدد الأنماط
    """
    
    # أنماط التعرف على السجلات
    LOG_PATTERNS = {
        # Python logging format
        "python": r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\s+(\w+)\s+(.+)$',
        
        # Syslog format
        "syslog": r'^(\w{3}\s+\d{1,2} \d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+):\s+(.+)$',
        
        # Apache/Nginx access log
        "access": r'^(\S+)\s+-\s+-\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+)',
        
        # Docker timestamp format
        "docker": r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z?)\s+(.+)$',
        
        # Generic timestamp
        "generic": r'^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[^\s]*)\s+(.+)$'
    }
    
    # أنماط الكشف عن الهجمات
    ATTACK_PATTERNS = {
        "brute_force": [
            r'failed.*login|invalid.*password|authentication.*fail',
            r'too many.*attempts|blocked.*ip|banned',
        ],
        "sql_injection": [
            r"union.*select|'.*or.*'|drop.*table|insert.*into",
            r"exec\(|eval\(|system\(",
        ],
        "xss": [
            r'<script>|javascript:|onerror=|onload=',
            r'document\.cookie|alert\(',
        ],
        "path_traversal": [
            r'\.\./|\.\.\\|%2e%2e|%252e',
            r'/etc/passwd|/etc/shadow|win\.ini',
        ],
        "command_injection": [
            r';\s*cat\s|;\s*ls\s|;\s*rm\s|;\s*wget\s',
            r'\|.*cat|\|.*ls|\|.*rm',
            r'`.*`|\$\(.*\)',
        ],
        "port_scan": [
            r'connection.*refused|port.*scan|nmap',
            r'syn.*scan|fin.*scan',
        ]
    }
    
    # أنماط استخراج IPs
    IP_PATTERN = re.compile(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b')
    
    # أنماط استخراج URLs
    URL_PATTERN = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
    
    def __init__(self):
        """Initialize log parser"""
        self.parsed_entries: List[ParsedLogEntry] = []
        self.attack_indicators: List[AttackIndicator] = []
        self.statistics = defaultdict(int)
    
    def parse_file(self, file_path: str, log_format: str = "auto") -> List[ParsedLogEntry]:
        """
        تحليل ملف سجل
        
        Args:
            file_path: مسار الملف
            log_format: نوع السجل (auto للكشف التلقائي)
        
        Returns:
            قائمة السجلات المحللة
        """
        entries = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                entry = self.parse_line(line.strip(), log_format)
                if entry:
                    entry.metadata = entry.metadata or {}
                    entry.metadata["line_number"] = line_num
                    entry.metadata["file"] = file_path
                    entries.append(entry)
        
        self.parsed_entries.extend(entries)
        logger.info(f"Parsed {len(entries)} entries from {file_path}")
        
        return entries
    
    def parse_line(self, line: str, log_format: str = "auto") -> Optional[ParsedLogEntry]:
        """
        تحليل سطر سجل واحد
        
        Args:
            line: سطر السجل
            log_format: نوع السجل
        
        Returns:
            سجل محلل أو None
        """
        if not line.strip():
            return None
        
        # محاولة التعرف على النمط
        if log_format == "auto":
            for fmt, pattern in self.LOG_PATTERNS.items():
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    return self._create_entry(match, fmt, line)
        else:
            pattern = self.LOG_PATTERNS.get(log_format)
            if pattern:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    return self._create_entry(match, log_format, line)
        
        # إذا لم يتطابق مع أي نمط
        return ParsedLogEntry(
            timestamp=datetime.now().isoformat(),
            level="UNKNOWN",
            source="unknown",
            message=line,
            raw_line=line
        )
    
    def _create_entry(self, match: re.Match, log_format: str, raw_line: str) -> ParsedLogEntry:
        """إنشاء سجل محلل من التطابق"""
        groups = match.groups()
        
        if log_format == "python":
            return ParsedLogEntry(
                timestamp=groups[0],
                level=groups[1],
                source="python",
                message=groups[2],
                raw_line=raw_line
            )
        elif log_format == "docker":
            return ParsedLogEntry(
                timestamp=groups[0],
                level="INFO",
                source="docker",
                message=groups[1],
                raw_line=raw_line
            )
        elif log_format == "access":
            return ParsedLogEntry(
                timestamp=groups[1],
                level="INFO",
                source=groups[0],  # IP
                message=f"{groups[2]} - Status: {groups[3]}",
                raw_line=raw_line,
                metadata={
                    "ip": groups[0],
                    "request": groups[2],
                    "status_code": groups[3],
                    "bytes": groups[4]
                }
            )
        else:
            return ParsedLogEntry(
                timestamp=groups[0] if groups else datetime.now().isoformat(),
                level="INFO",
                source=log_format,
                message=groups[-1] if groups else raw_line,
                raw_line=raw_line
            )
    
    def detect_attacks(self, entries: List[ParsedLogEntry] = None) -> List[AttackIndicator]:
        """
        الكشف عن مؤشرات الهجمات
        
        Args:
            entries: السجلات للتحليل (أو كل السجلات المحفوظة)
        
        Returns:
            قائمة مؤشرات الهجمات
        """
        if entries is None:
            entries = self.parsed_entries
        
        indicators = []
        
        for entry in entries:
            message = entry.message.lower()
            
            for attack_type, patterns in self.ATTACK_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, message, re.IGNORECASE):
                        indicator = AttackIndicator(
                            indicator_type=attack_type,
                            value=entry.message[:100],
                            confidence=0.8,
                            context=entry.raw_line[:200],
                            timestamp=entry.timestamp
                        )
                        indicators.append(indicator)
                        self.statistics[f"attack_{attack_type}"] += 1
                        break
        
        self.attack_indicators.extend(indicators)
        logger.info(f"Detected {len(indicators)} attack indicators")
        
        return indicators
    
    def extract_ips(self, entries: List[ParsedLogEntry] = None) -> Dict[str, int]:
        """
        استخراج وإحصاء عناوين IP
        
        Args:
            entries: السجلات للتحليل
        
        Returns:
            قاموس {IP: عدد الظهور}
        """
        if entries is None:
            entries = self.parsed_entries
        
        ip_counter = Counter()
        
        for entry in entries:
            ips = self.IP_PATTERN.findall(entry.raw_line)
            for ip in ips:
                # تجاهل IPs المحلية
                if not ip.startswith(('127.', '0.', '255.')):
                    ip_counter[ip] += 1
        
        return dict(ip_counter.most_common())
    
    def extract_urls(self, entries: List[ParsedLogEntry] = None) -> List[str]:
        """
        استخراج URLs من السجلات
        
        Args:
            entries: السجلات للتحليل
        
        Returns:
            قائمة URLs
        """
        if entries is None:
            entries = self.parsed_entries
        
        urls = set()
        
        for entry in entries:
            found_urls = self.URL_PATTERN.findall(entry.raw_line)
            urls.update(found_urls)
        
        return list(urls)
    
    def filter_by_level(self, level: LogLevel) -> List[ParsedLogEntry]:
        """
        فلترة السجلات حسب المستوى
        
        Args:
            level: مستوى السجل
        
        Returns:
            السجلات المطابقة
        """
        return [e for e in self.parsed_entries if e.level == level.value]
    
    def filter_by_ip(self, ip: str) -> List[ParsedLogEntry]:
        """
        فلترة السجلات حسب IP
        
        Args:
            ip: عنوان IP
        
        Returns:
            السجلات المطابقة
        """
        return [e for e in self.parsed_entries if ip in e.raw_line]
    
    def filter_by_keyword(self, keyword: str) -> List[ParsedLogEntry]:
        """
        فلترة السجلات حسب كلمة مفتاحية
        
        Args:
            keyword: الكلمة المفتاحية
        
        Returns:
            السجلات المطابقة
        """
        keyword_lower = keyword.lower()
        return [e for e in self.parsed_entries if keyword_lower in e.raw_line.lower()]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        ملخص الأخطاء في السجلات
        
        Returns:
            ملخص الأخطاء
        """
        errors = self.filter_by_level(LogLevel.ERROR)
        criticals = self.filter_by_level(LogLevel.CRITICAL)
        warnings = self.filter_by_level(LogLevel.WARNING)
        
        # تجميع الأخطاء المتشابهة
        error_patterns = Counter()
        for entry in errors + criticals:
            # استخراج أول 50 حرف كمفتاح
            key = entry.message[:50]
            error_patterns[key] += 1
        
        return {
            "total_errors": len(errors),
            "total_criticals": len(criticals),
            "total_warnings": len(warnings),
            "top_errors": dict(error_patterns.most_common(10)),
            "first_error": errors[0].to_dict() if errors else None,
            "last_error": errors[-1].to_dict() if errors else None
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        إحصائيات شاملة للسجلات
        
        Returns:
            إحصائيات
        """
        level_counts = Counter(e.level for e in self.parsed_entries)
        source_counts = Counter(e.source for e in self.parsed_entries)
        
        return {
            "total_entries": len(self.parsed_entries),
            "by_level": dict(level_counts),
            "by_source": dict(source_counts.most_common(10)),
            "attack_indicators": len(self.attack_indicators),
            "unique_ips": len(self.extract_ips()),
            "unique_urls": len(self.extract_urls()),
            "attack_statistics": dict(self.statistics)
        }
    
    def export_json(self, file_path: str) -> str:
        """
        تصدير النتائج لملف JSON
        
        Args:
            file_path: مسار الملف
        
        Returns:
            مسار الملف
        """
        export_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "tool": "Cyber Mirage Log Parser"
            },
            "statistics": self.get_statistics(),
            "attack_indicators": [
                {
                    "type": i.indicator_type,
                    "value": i.value,
                    "confidence": i.confidence,
                    "timestamp": i.timestamp
                }
                for i in self.attack_indicators
            ],
            "ip_analysis": self.extract_ips(),
            "entries": [e.to_dict() for e in self.parsed_entries[:1000]]  # أول 1000
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported analysis to {file_path}")
        return file_path
    
    def generate_report(self) -> str:
        """
        توليد تقرير تحليل السجلات
        
        Returns:
            التقرير النصي
        """
        stats = self.get_statistics()
        error_summary = self.get_error_summary()
        ips = self.extract_ips()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║              CYBER MIRAGE - LOG ANALYSIS REPORT                  ║
╠══════════════════════════════════════════════════════════════════╣
║  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<50} ║
╠══════════════════════════════════════════════════════════════════╣

📊 GENERAL STATISTICS:
═══════════════════════════════════════════════════════════════════
  Total Log Entries: {stats['total_entries']}
  Attack Indicators: {stats['attack_indicators']}
  Unique IPs: {stats['unique_ips']}

📈 BY LOG LEVEL:
"""
        for level, count in stats['by_level'].items():
            icon = {"ERROR": "🔴", "CRITICAL": "⛔", "WARNING": "🟡", "INFO": "🟢"}.get(level, "⚪")
            report += f"  {icon} {level}: {count}\n"
        
        report += "\n⚠️ ERROR SUMMARY:\n"
        report += f"  Total Errors: {error_summary['total_errors']}\n"
        report += f"  Total Criticals: {error_summary['total_criticals']}\n"
        
        report += "\n🎯 ATTACK INDICATORS:\n"
        for attack_type, count in stats['attack_statistics'].items():
            report += f"  - {attack_type.replace('attack_', '').upper()}: {count}\n"
        
        report += "\n🌐 TOP IPs:\n"
        for ip, count in list(ips.items())[:10]:
            report += f"  - {ip}: {count} occurrences\n"
        
        report += """
═══════════════════════════════════════════════════════════════════
                    End of Log Analysis Report
╚══════════════════════════════════════════════════════════════════╝
"""
        return report


class HoneypotLogParser(LogParser):
    """
    محلل مخصص لسجلات Honeypots
    """
    
    # أنماط خاصة بالـ Honeypots
    HONEYPOT_PATTERNS = {
        "connection": r'Connection on port (\d+) from \(\'([^\']+)\', (\d+)\)',
        "attack_logged": r'Logged (\w+) attack from ([\d.]+) to PostgreSQL',
        "threat_intel": r'Logged threat intel to Redis for ([\d.]+)',
        "login_attempt": r'Login attempt.*user[name]*[=:]\s*["\']?(\w+)',
        "command": r'Command executed[=:]\s*(.+)',
    }
    
    def parse_honeypot_log(self, log_content: str) -> Dict[str, Any]:
        """
        تحليل سجل Honeypot
        
        Args:
            log_content: محتوى السجل
        
        Returns:
            نتائج التحليل
        """
        results = {
            "connections": [],
            "attacks": [],
            "threat_intel": [],
            "login_attempts": [],
            "commands": []
        }
        
        for line in log_content.split('\n'):
            # اتصالات
            match = re.search(self.HONEYPOT_PATTERNS["connection"], line)
            if match:
                results["connections"].append({
                    "port": match.group(1),
                    "ip": match.group(2),
                    "source_port": match.group(3),
                    "raw": line
                })
            
            # هجمات مسجلة
            match = re.search(self.HONEYPOT_PATTERNS["attack_logged"], line)
            if match:
                results["attacks"].append({
                    "service": match.group(1),
                    "ip": match.group(2),
                    "raw": line
                })
            
            # Threat Intel
            match = re.search(self.HONEYPOT_PATTERNS["threat_intel"], line)
            if match:
                results["threat_intel"].append({
                    "ip": match.group(1),
                    "raw": line
                })
        
        return results


if __name__ == "__main__":
    # اختبار
    parser = LogParser()
    print("Log Parser initialized")
    print(f"Available patterns: {list(parser.LOG_PATTERNS.keys())}")
