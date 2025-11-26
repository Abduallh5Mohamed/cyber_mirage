"""
Timeline Builder - بناء الجدول الزمني للأحداث
Cyber Mirage Forensics Module

يقوم ببناء Timeline شامل من:
- سجلات الهجمات
- سجلات النظام
- أحداث الشبكة
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """أنواع الأحداث"""
    ATTACK_START = "attack_start"
    ATTACK_END = "attack_end"
    LOGIN_ATTEMPT = "login_attempt"
    COMMAND_EXECUTED = "command_executed"
    FILE_ACCESS = "file_access"
    DATA_EXFILTRATION = "data_exfiltration"
    NETWORK_CONNECTION = "network_connection"
    SERVICE_ACCESS = "service_access"
    ALERT_TRIGGERED = "alert_triggered"
    SYSTEM_EVENT = "system_event"


class Severity(Enum):
    """مستويات الخطورة"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TimelineEvent:
    """حدث في الجدول الزمني"""
    timestamp: str
    event_type: str
    source: str
    description: str
    severity: str
    attacker_ip: Optional[str] = None
    service: Optional[str] = None
    details: Optional[Dict] = None
    mitre_technique: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class TimelineBuilder:
    """
    بناء الجدول الزمني للأحداث الأمنية
    """
    
    def __init__(self, case_id: str = None):
        """
        Initialize timeline builder
        
        Args:
            case_id: معرف القضية
        """
        self.case_id = case_id or f"TL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.events: List[TimelineEvent] = []
        self.metadata = {
            "case_id": self.case_id,
            "created_at": datetime.now().isoformat(),
            "tool": "Cyber Mirage Timeline Builder"
        }
    
    def add_event(self, 
                  timestamp: str,
                  event_type: EventType,
                  source: str,
                  description: str,
                  severity: Severity = Severity.INFO,
                  attacker_ip: str = None,
                  service: str = None,
                  details: Dict = None,
                  mitre_technique: str = None) -> TimelineEvent:
        """
        إضافة حدث للجدول الزمني
        
        Args:
            timestamp: وقت الحدث
            event_type: نوع الحدث
            source: مصدر الحدث
            description: وصف الحدث
            severity: مستوى الخطورة
            attacker_ip: IP المهاجم
            service: الخدمة المستهدفة
            details: تفاصيل إضافية
            mitre_technique: تقنية MITRE ATT&CK
        
        Returns:
            الحدث المُضاف
        """
        event = TimelineEvent(
            timestamp=timestamp,
            event_type=event_type.value,
            source=source,
            description=description,
            severity=severity.value,
            attacker_ip=attacker_ip,
            service=service,
            details=details,
            mitre_technique=mitre_technique
        )
        self.events.append(event)
        return event
    
    def parse_attack_sessions(self, 
                              container_name: str = "cyber_mirage_postgres",
                              database: str = "cyber_mirage",
                              user: str = "cybermirage") -> int:
        """
        استخراج الأحداث من جدول attack_sessions
        
        Returns:
            عدد الأحداث المُضافة
        """
        try:
            query = """
            SELECT id, attacker_name, origin, start_time, end_time, 
                   duration, commands_count
            FROM attack_sessions 
            ORDER BY start_time ASC
            """
            
            result = subprocess.run(
                ["docker", "exec", "-e", "PGPASSWORD=SecurePass123!",
                 container_name, "psql", "-h", "localhost", "-U", user,
                 "-d", database, "-t", "-A", "-F", "|", "-c", query],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            count = 0
            for line in result.stdout.strip().split('\n'):
                if line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        session_id = parts[0]
                        attacker_name = parts[1]
                        origin = parts[2]
                        start_time = parts[3]
                        end_time = parts[4] if len(parts) > 4 and parts[4] else None
                        
                        # تحديد الخدمة من اسم المهاجم
                        service = self._extract_service(attacker_name)
                        
                        # تحديد تقنية MITRE
                        mitre = self._get_mitre_technique(service)
                        
                        # حدث بداية الهجوم
                        self.add_event(
                            timestamp=start_time,
                            event_type=EventType.ATTACK_START,
                            source="attack_sessions",
                            description=f"Attack started from {origin} on {service}",
                            severity=Severity.HIGH,
                            attacker_ip=origin,
                            service=service,
                            details={"session_id": session_id, "attacker_name": attacker_name},
                            mitre_technique=mitre
                        )
                        count += 1
                        
                        # حدث نهاية الهجوم (إذا موجود)
                        if end_time and end_time.strip():
                            self.add_event(
                                timestamp=end_time,
                                event_type=EventType.ATTACK_END,
                                source="attack_sessions",
                                description=f"Attack ended from {origin}",
                                severity=Severity.MEDIUM,
                                attacker_ip=origin,
                                service=service,
                                details={"session_id": session_id}
                            )
                            count += 1
            
            logger.info(f"Parsed {count} events from attack_sessions")
            return count
            
        except Exception as e:
            logger.error(f"Error parsing attack sessions: {e}")
            return 0
    
    def parse_docker_logs(self, 
                          container_name: str,
                          lines: int = 1000) -> int:
        """
        استخراج الأحداث من سجلات Docker
        
        Args:
            container_name: اسم الحاوية
            lines: عدد الأسطر لقراءتها
        
        Returns:
            عدد الأحداث المُضافة
        """
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), container_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            count = 0
            for line in result.stdout.split('\n') + result.stderr.split('\n'):
                event = self._parse_log_line(line, container_name)
                if event:
                    self.events.append(event)
                    count += 1
            
            logger.info(f"Parsed {count} events from {container_name} logs")
            return count
            
        except Exception as e:
            logger.error(f"Error parsing Docker logs: {e}")
            return 0
    
    def _parse_log_line(self, line: str, source: str) -> Optional[TimelineEvent]:
        """
        تحليل سطر سجل وتحويله لحدث
        
        Args:
            line: سطر السجل
            source: مصدر السجل
        
        Returns:
            حدث أو None
        """
        if not line.strip():
            return None
        
        # أنماط مهمة للبحث عنها
        patterns = {
            "Connection on port": (EventType.NETWORK_CONNECTION, Severity.MEDIUM),
            "Logged.*attack": (EventType.ATTACK_START, Severity.HIGH),
            "Login attempt": (EventType.LOGIN_ATTEMPT, Severity.MEDIUM),
            "ERROR": (EventType.SYSTEM_EVENT, Severity.HIGH),
            "WARNING": (EventType.SYSTEM_EVENT, Severity.MEDIUM),
            "threat intel": (EventType.ALERT_TRIGGERED, Severity.MEDIUM),
        }
        
        for pattern, (event_type, severity) in patterns.items():
            if pattern.lower() in line.lower():
                # استخراج الوقت من السطر
                timestamp = self._extract_timestamp(line)
                
                # استخراج IP إذا موجود
                ip = self._extract_ip(line)
                
                return TimelineEvent(
                    timestamp=timestamp or datetime.now().isoformat(),
                    event_type=event_type.value,
                    source=source,
                    description=line[:200],  # أول 200 حرف
                    severity=severity.value,
                    attacker_ip=ip
                )
        
        return None
    
    def _extract_timestamp(self, line: str) -> Optional[str]:
        """استخراج الوقت من سطر السجل"""
        import re
        
        # أنماط الوقت الشائعة
        patterns = [
            r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})',
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_ip(self, line: str) -> Optional[str]:
        """استخراج IP من سطر السجل"""
        import re
        
        ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        match = re.search(ip_pattern, line)
        
        if match:
            return match.group(1)
        return None
    
    def _extract_service(self, attacker_name: str) -> str:
        """استخراج اسم الخدمة من اسم المهاجم"""
        services = ["SSH", "FTP", "HTTP", "MySQL", "Modbus", "HTTPS"]
        for service in services:
            if service in attacker_name:
                return service
        return "Unknown"
    
    def _get_mitre_technique(self, service: str) -> str:
        """الحصول على تقنية MITRE حسب الخدمة"""
        mitre_map = {
            "SSH": "T1078 - Valid Accounts / T1110 - Brute Force",
            "FTP": "T1078 - Valid Accounts",
            "HTTP": "T1190 - Exploit Public-Facing Application",
            "HTTPS": "T1190 - Exploit Public-Facing Application",
            "MySQL": "T1213 - Data from Information Repositories",
            "Modbus": "T0831 - Manipulation of Control"
        }
        return mitre_map.get(service, "Unknown")
    
    def sort_events(self):
        """ترتيب الأحداث حسب الوقت"""
        self.events.sort(key=lambda e: e.timestamp)
    
    def filter_by_ip(self, ip: str) -> List[TimelineEvent]:
        """
        فلترة الأحداث حسب IP محدد
        
        Args:
            ip: عنوان IP
        
        Returns:
            قائمة الأحداث
        """
        return [e for e in self.events if e.attacker_ip == ip]
    
    def filter_by_service(self, service: str) -> List[TimelineEvent]:
        """
        فلترة الأحداث حسب الخدمة
        
        Args:
            service: اسم الخدمة
        
        Returns:
            قائمة الأحداث
        """
        return [e for e in self.events if e.service == service]
    
    def filter_by_severity(self, severity: Severity) -> List[TimelineEvent]:
        """
        فلترة الأحداث حسب الخطورة
        
        Args:
            severity: مستوى الخطورة
        
        Returns:
            قائمة الأحداث
        """
        return [e for e in self.events if e.severity == severity.value]
    
    def filter_by_time_range(self, 
                             start: datetime, 
                             end: datetime) -> List[TimelineEvent]:
        """
        فلترة الأحداث حسب نطاق زمني
        
        Args:
            start: بداية النطاق
            end: نهاية النطاق
        
        Returns:
            قائمة الأحداث
        """
        filtered = []
        for event in self.events:
            try:
                event_time = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
                if start <= event_time <= end:
                    filtered.append(event)
            except:
                continue
        return filtered
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات الجدول الزمني
        
        Returns:
            إحصائيات
        """
        stats = {
            "total_events": len(self.events),
            "by_type": {},
            "by_severity": {},
            "by_service": {},
            "unique_attackers": set(),
            "time_range": {
                "start": None,
                "end": None
            }
        }
        
        for event in self.events:
            # حسب النوع
            stats["by_type"][event.event_type] = stats["by_type"].get(event.event_type, 0) + 1
            
            # حسب الخطورة
            stats["by_severity"][event.severity] = stats["by_severity"].get(event.severity, 0) + 1
            
            # حسب الخدمة
            if event.service:
                stats["by_service"][event.service] = stats["by_service"].get(event.service, 0) + 1
            
            # المهاجمين الفريدين
            if event.attacker_ip:
                stats["unique_attackers"].add(event.attacker_ip)
        
        stats["unique_attackers"] = len(stats["unique_attackers"])
        
        # النطاق الزمني
        if self.events:
            self.sort_events()
            stats["time_range"]["start"] = self.events[0].timestamp
            stats["time_range"]["end"] = self.events[-1].timestamp
        
        return stats
    
    def export_json(self, file_path: str) -> str:
        """
        تصدير الجدول الزمني لملف JSON
        
        Args:
            file_path: مسار الملف
        
        Returns:
            مسار الملف
        """
        self.sort_events()
        
        export_data = {
            "metadata": self.metadata,
            "statistics": self.get_statistics(),
            "events": [e.to_dict() for e in self.events]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Timeline exported to {file_path}")
        return file_path
    
    def export_csv(self, file_path: str) -> str:
        """
        تصدير الجدول الزمني لملف CSV
        
        Args:
            file_path: مسار الملف
        
        Returns:
            مسار الملف
        """
        import csv
        
        self.sort_events()
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # الرأس
            writer.writerow([
                'Timestamp', 'Event Type', 'Source', 'Description',
                'Severity', 'Attacker IP', 'Service', 'MITRE Technique'
            ])
            
            # البيانات
            for event in self.events:
                writer.writerow([
                    event.timestamp,
                    event.event_type,
                    event.source,
                    event.description,
                    event.severity,
                    event.attacker_ip or '',
                    event.service or '',
                    event.mitre_technique or ''
                ])
        
        logger.info(f"Timeline exported to {file_path}")
        return file_path
    
    def generate_report(self) -> str:
        """
        توليد تقرير نصي للجدول الزمني
        
        Returns:
            التقرير النصي
        """
        self.sort_events()
        stats = self.get_statistics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║              CYBER MIRAGE - FORENSIC TIMELINE REPORT             ║
╠══════════════════════════════════════════════════════════════════╣
║  Case ID: {self.case_id:<52} ║
║  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<50} ║
╠══════════════════════════════════════════════════════════════════╣

📊 STATISTICS:
═══════════════════════════════════════════════════════════════════
  Total Events: {stats['total_events']}
  Unique Attackers: {stats['unique_attackers']}
  Time Range: {stats['time_range']['start']} to {stats['time_range']['end']}

📈 BY SEVERITY:
"""
        for sev, count in stats['by_severity'].items():
            report += f"  - {sev.upper()}: {count}\n"
        
        report += "\n📋 BY SERVICE:\n"
        for svc, count in stats['by_service'].items():
            report += f"  - {svc}: {count}\n"
        
        report += "\n📅 EVENT TIMELINE:\n"
        report += "═" * 67 + "\n"
        
        for event in self.events[:50]:  # أول 50 حدث
            severity_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
                "info": "⚪"
            }.get(event.severity, "⚪")
            
            report += f"""
{severity_icon} [{event.timestamp}]
   Type: {event.event_type}
   Source: {event.source}
   Description: {event.description[:80]}...
   IP: {event.attacker_ip or 'N/A'} | Service: {event.service or 'N/A'}
"""
        
        if len(self.events) > 50:
            report += f"\n... and {len(self.events) - 50} more events\n"
        
        report += """
═══════════════════════════════════════════════════════════════════
                    End of Timeline Report
╚══════════════════════════════════════════════════════════════════╝
"""
        return report


def build_full_timeline(case_id: str = None) -> TimelineBuilder:
    """
    بناء جدول زمني شامل
    
    Args:
        case_id: معرف القضية
    
    Returns:
        كائن TimelineBuilder
    """
    builder = TimelineBuilder(case_id=case_id)
    
    # استخراج من قاعدة البيانات
    builder.parse_attack_sessions()
    
    # استخراج من سجلات Docker
    containers = ["cyber_mirage_honeypots", "cyber_mirage_ai"]
    for container in containers:
        builder.parse_docker_logs(container)
    
    builder.sort_events()
    
    return builder


if __name__ == "__main__":
    # اختبار
    builder = TimelineBuilder("TEST_CASE")
    print(f"Timeline Builder initialized: {builder.case_id}")
