"""
PCAP Analyzer - محلل حزم الشبكة
Cyber Mirage Forensics Module

يقوم بتحليل:
- ملفات PCAP/PCAPNG
- حركة مرور الشبكة
- استخراج بيانات الجلسات
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
import struct
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PacketInfo:
    """معلومات حزمة الشبكة"""
    timestamp: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    length: int
    flags: Optional[str] = None
    payload_preview: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class NetworkSession:
    """جلسة شبكة"""
    session_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    start_time: str
    end_time: Optional[str] = None
    packet_count: int = 0
    bytes_transferred: int = 0
    flags: List[str] = None


@dataclass
class SuspiciousActivity:
    """نشاط مشبوه"""
    activity_type: str
    description: str
    src_ip: str
    dst_ip: str
    confidence: float
    evidence: str
    timestamp: str


class PcapAnalyzer:
    """
    محلل ملفات PCAP لحركة مرور الشبكة
    """
    
    # المنافذ المعروفة
    KNOWN_PORTS = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        502: "Modbus",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        6379: "Redis",
        8080: "HTTP-Alt",
        2222: "SSH-Honeypot",
        2121: "FTP-Honeypot"
    }
    
    # أنماط الهجمات
    ATTACK_SIGNATURES = {
        "port_scan": {
            "description": "Port scanning activity",
            "indicator": "multiple_ports_same_src"
        },
        "syn_flood": {
            "description": "SYN flood attack",
            "indicator": "excessive_syn_flags"
        },
        "brute_force": {
            "description": "Brute force attempt",
            "indicator": "repeated_auth_ports"
        },
        "data_exfil": {
            "description": "Data exfiltration",
            "indicator": "large_outbound_transfer"
        }
    }
    
    def __init__(self):
        """Initialize PCAP analyzer"""
        self.packets: List[PacketInfo] = []
        self.sessions: Dict[str, NetworkSession] = {}
        self.suspicious_activities: List[SuspiciousActivity] = []
        self.statistics = defaultdict(int)
    
    def analyze_with_tshark(self, pcap_file: str) -> Dict[str, Any]:
        """
        تحليل PCAP باستخدام TShark
        
        Args:
            pcap_file: مسار ملف PCAP
        
        Returns:
            نتائج التحليل
        """
        results = {
            "file": pcap_file,
            "analyzed_at": datetime.now().isoformat(),
            "packets": [],
            "conversations": [],
            "protocols": {},
            "endpoints": {}
        }
        
        try:
            # معلومات أساسية عن الملف
            capinfos = subprocess.run(
                ["capinfos", "-c", "-d", "-u", pcap_file],
                capture_output=True,
                text=True,
                timeout=60
            )
            results["file_info"] = capinfos.stdout
            
            # استخراج الحزم
            tshark_cmd = [
                "tshark", "-r", pcap_file,
                "-T", "fields",
                "-e", "frame.time",
                "-e", "ip.src",
                "-e", "ip.dst",
                "-e", "tcp.srcport",
                "-e", "tcp.dstport",
                "-e", "udp.srcport",
                "-e", "udp.dstport",
                "-e", "frame.len",
                "-e", "_ws.col.Protocol",
                "-E", "separator=|"
            ]
            
            result = subprocess.run(
                tshark_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            for line in result.stdout.strip().split('\n'):
                if line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 8:
                        packet = PacketInfo(
                            timestamp=parts[0],
                            src_ip=parts[1],
                            dst_ip=parts[2],
                            src_port=int(parts[3] or parts[5] or 0),
                            dst_port=int(parts[4] or parts[6] or 0),
                            length=int(parts[7] or 0),
                            protocol=parts[8] if len(parts) > 8 else "Unknown"
                        )
                        self.packets.append(packet)
                        results["packets"].append(packet.to_dict())
            
            # إحصائيات البروتوكولات
            protocol_stats = subprocess.run(
                ["tshark", "-r", pcap_file, "-q", "-z", "io,phs"],
                capture_output=True,
                text=True,
                timeout=60
            )
            results["protocol_hierarchy"] = protocol_stats.stdout
            
            # المحادثات
            conv_stats = subprocess.run(
                ["tshark", "-r", pcap_file, "-q", "-z", "conv,tcp"],
                capture_output=True,
                text=True,
                timeout=60
            )
            results["tcp_conversations"] = conv_stats.stdout
            
            logger.info(f"Analyzed {len(self.packets)} packets from {pcap_file}")
            
        except FileNotFoundError:
            logger.warning("TShark not found, using basic analysis")
            results["error"] = "TShark not installed"
        except subprocess.TimeoutExpired:
            logger.error("Analysis timeout")
            results["error"] = "Timeout"
        except Exception as e:
            logger.error(f"Error analyzing PCAP: {e}")
            results["error"] = str(e)
        
        return results
    
    def analyze_basic(self, pcap_file: str) -> Dict[str, Any]:
        """
        تحليل أساسي بدون TShark (قراءة PCAP يدوياً)
        
        Args:
            pcap_file: مسار ملف PCAP
        
        Returns:
            نتائج التحليل
        """
        results = {
            "file": pcap_file,
            "analyzed_at": datetime.now().isoformat(),
            "packet_count": 0,
            "ip_addresses": set(),
            "ports": set()
        }
        
        try:
            with open(pcap_file, 'rb') as f:
                # قراءة PCAP header
                header = f.read(24)
                if len(header) < 24:
                    return {"error": "Invalid PCAP file"}
                
                magic = struct.unpack('I', header[0:4])[0]
                
                if magic == 0xa1b2c3d4:
                    # Little endian
                    byte_order = '<'
                elif magic == 0xd4c3b2a1:
                    # Big endian
                    byte_order = '>'
                else:
                    return {"error": "Unknown PCAP format"}
                
                # قراءة الحزم
                while True:
                    packet_header = f.read(16)
                    if len(packet_header) < 16:
                        break
                    
                    ts_sec, ts_usec, incl_len, orig_len = struct.unpack(
                        f'{byte_order}IIII', packet_header
                    )
                    
                    packet_data = f.read(incl_len)
                    if len(packet_data) < incl_len:
                        break
                    
                    results["packet_count"] += 1
                    
                    # تحليل Ethernet + IP header
                    if len(packet_data) >= 34:  # Ethernet (14) + IP (20)
                        ip_header_start = 14  # After Ethernet
                        
                        # IP addresses
                        if len(packet_data) >= ip_header_start + 20:
                            src_ip = socket.inet_ntoa(packet_data[ip_header_start+12:ip_header_start+16])
                            dst_ip = socket.inet_ntoa(packet_data[ip_header_start+16:ip_header_start+20])
                            
                            results["ip_addresses"].add(src_ip)
                            results["ip_addresses"].add(dst_ip)
                            
                            # Protocol
                            protocol = packet_data[ip_header_start + 9]
                            
                            # TCP/UDP ports
                            if protocol in (6, 17) and len(packet_data) >= ip_header_start + 24:
                                ihl = (packet_data[ip_header_start] & 0x0F) * 4
                                transport_start = ip_header_start + ihl
                                
                                if len(packet_data) >= transport_start + 4:
                                    src_port = struct.unpack('!H', packet_data[transport_start:transport_start+2])[0]
                                    dst_port = struct.unpack('!H', packet_data[transport_start+2:transport_start+4])[0]
                                    
                                    results["ports"].add(src_port)
                                    results["ports"].add(dst_port)
            
            results["ip_addresses"] = list(results["ip_addresses"])
            results["ports"] = list(results["ports"])
            
            logger.info(f"Basic analysis: {results['packet_count']} packets")
            
        except Exception as e:
            logger.error(f"Error in basic analysis: {e}")
            results["error"] = str(e)
        
        return results
    
    def detect_port_scan(self, threshold: int = 10) -> List[SuspiciousActivity]:
        """
        الكشف عن فحص المنافذ
        
        Args:
            threshold: الحد الأدنى لعدد المنافذ للاعتبار كـ scan
        
        Returns:
            قائمة الأنشطة المشبوهة
        """
        # تجميع المنافذ لكل IP مصدر
        src_ports = defaultdict(set)
        
        for packet in self.packets:
            if packet.src_ip and packet.dst_port:
                key = (packet.src_ip, packet.dst_ip)
                src_ports[key].add(packet.dst_port)
        
        suspicious = []
        for (src, dst), ports in src_ports.items():
            if len(ports) >= threshold:
                activity = SuspiciousActivity(
                    activity_type="port_scan",
                    description=f"Port scan detected: {len(ports)} ports scanned",
                    src_ip=src,
                    dst_ip=dst,
                    confidence=min(0.9, 0.5 + (len(ports) / 100)),
                    evidence=f"Scanned ports: {sorted(list(ports))[:20]}...",
                    timestamp=datetime.now().isoformat()
                )
                suspicious.append(activity)
                self.suspicious_activities.append(activity)
        
        return suspicious
    
    def detect_brute_force(self, 
                           auth_ports: List[int] = None,
                           threshold: int = 20) -> List[SuspiciousActivity]:
        """
        الكشف عن هجمات Brute Force
        
        Args:
            auth_ports: منافذ المصادقة
            threshold: الحد الأدنى للمحاولات
        
        Returns:
            قائمة الأنشطة المشبوهة
        """
        if auth_ports is None:
            auth_ports = [21, 22, 23, 2222, 2121, 3306, 3389]
        
        # عد الاتصالات لكل IP على منافذ المصادقة
        auth_attempts = defaultdict(int)
        
        for packet in self.packets:
            if packet.dst_port in auth_ports:
                key = (packet.src_ip, packet.dst_ip, packet.dst_port)
                auth_attempts[key] += 1
        
        suspicious = []
        for (src, dst, port), count in auth_attempts.items():
            if count >= threshold:
                service = self.KNOWN_PORTS.get(port, f"Port {port}")
                activity = SuspiciousActivity(
                    activity_type="brute_force",
                    description=f"Possible brute force on {service}: {count} attempts",
                    src_ip=src,
                    dst_ip=dst,
                    confidence=min(0.95, 0.6 + (count / 200)),
                    evidence=f"Port: {port}, Attempts: {count}",
                    timestamp=datetime.now().isoformat()
                )
                suspicious.append(activity)
                self.suspicious_activities.append(activity)
        
        return suspicious
    
    def detect_data_exfiltration(self, 
                                 size_threshold: int = 1000000) -> List[SuspiciousActivity]:
        """
        الكشف عن تسريب البيانات
        
        Args:
            size_threshold: حد حجم البيانات (bytes)
        
        Returns:
            قائمة الأنشطة المشبوهة
        """
        # تجميع حجم البيانات المرسلة لكل IP
        outbound_data = defaultdict(int)
        
        for packet in self.packets:
            if packet.src_ip and packet.length:
                key = (packet.src_ip, packet.dst_ip)
                outbound_data[key] += packet.length
        
        suspicious = []
        for (src, dst), total_bytes in outbound_data.items():
            if total_bytes >= size_threshold:
                activity = SuspiciousActivity(
                    activity_type="data_exfiltration",
                    description=f"Large data transfer: {total_bytes / 1024:.2f} KB",
                    src_ip=src,
                    dst_ip=dst,
                    confidence=min(0.8, 0.4 + (total_bytes / 10000000)),
                    evidence=f"Total bytes: {total_bytes}",
                    timestamp=datetime.now().isoformat()
                )
                suspicious.append(activity)
                self.suspicious_activities.append(activity)
        
        return suspicious
    
    def build_sessions(self) -> Dict[str, NetworkSession]:
        """
        بناء جلسات الشبكة من الحزم
        
        Returns:
            قاموس الجلسات
        """
        for packet in self.packets:
            # معرف الجلسة (bidirectional)
            session_key = self._get_session_key(
                packet.src_ip, packet.dst_ip,
                packet.src_port, packet.dst_port
            )
            
            if session_key not in self.sessions:
                self.sessions[session_key] = NetworkSession(
                    session_id=session_key,
                    src_ip=packet.src_ip,
                    dst_ip=packet.dst_ip,
                    src_port=packet.src_port,
                    dst_port=packet.dst_port,
                    protocol=packet.protocol,
                    start_time=packet.timestamp,
                    packet_count=0,
                    bytes_transferred=0,
                    flags=[]
                )
            
            session = self.sessions[session_key]
            session.packet_count += 1
            session.bytes_transferred += packet.length
            session.end_time = packet.timestamp
            
            if packet.flags:
                session.flags.append(packet.flags)
        
        return self.sessions
    
    def _get_session_key(self, src_ip: str, dst_ip: str, 
                         src_port: int, dst_port: int) -> str:
        """توليد مفتاح جلسة bidirectional"""
        endpoints = sorted([
            f"{src_ip}:{src_port}",
            f"{dst_ip}:{dst_port}"
        ])
        return f"{endpoints[0]}<->{endpoints[1]}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        إحصائيات شاملة
        
        Returns:
            إحصائيات
        """
        if not self.packets:
            return {"error": "No packets analyzed"}
        
        protocol_counts = Counter(p.protocol for p in self.packets)
        port_counts = Counter(p.dst_port for p in self.packets)
        src_ip_counts = Counter(p.src_ip for p in self.packets)
        dst_ip_counts = Counter(p.dst_ip for p in self.packets)
        
        total_bytes = sum(p.length for p in self.packets)
        
        return {
            "total_packets": len(self.packets),
            "total_bytes": total_bytes,
            "unique_src_ips": len(set(p.src_ip for p in self.packets)),
            "unique_dst_ips": len(set(p.dst_ip for p in self.packets)),
            "protocols": dict(protocol_counts.most_common(10)),
            "top_dst_ports": dict(port_counts.most_common(10)),
            "top_src_ips": dict(src_ip_counts.most_common(10)),
            "top_dst_ips": dict(dst_ip_counts.most_common(10)),
            "sessions": len(self.sessions),
            "suspicious_activities": len(self.suspicious_activities)
        }
    
    def analyze_honeypot_traffic(self, pcap_file: str) -> Dict[str, Any]:
        """
        تحليل خاص بحركة مرور Honeypots
        
        Args:
            pcap_file: مسار ملف PCAP
        
        Returns:
            نتائج التحليل
        """
        # تحليل أساسي أولاً
        self.analyze_with_tshark(pcap_file)
        
        # منافذ الـ Honeypots
        honeypot_ports = [2222, 2121, 8080, 3306, 502]
        
        honeypot_traffic = {
            "by_port": defaultdict(list),
            "attackers": set(),
            "attack_timeline": []
        }
        
        for packet in self.packets:
            if packet.dst_port in honeypot_ports:
                service = self.KNOWN_PORTS.get(packet.dst_port, f"Port {packet.dst_port}")
                honeypot_traffic["by_port"][service].append(packet.to_dict())
                honeypot_traffic["attackers"].add(packet.src_ip)
                
                honeypot_traffic["attack_timeline"].append({
                    "timestamp": packet.timestamp,
                    "attacker": packet.src_ip,
                    "service": service,
                    "port": packet.dst_port
                })
        
        # تحويل set إلى list للـ JSON
        honeypot_traffic["attackers"] = list(honeypot_traffic["attackers"])
        honeypot_traffic["by_port"] = dict(honeypot_traffic["by_port"])
        
        # الكشف عن الأنشطة المشبوهة
        self.detect_port_scan()
        self.detect_brute_force()
        
        honeypot_traffic["suspicious_activities"] = [
            {
                "type": a.activity_type,
                "description": a.description,
                "src_ip": a.src_ip,
                "confidence": a.confidence
            }
            for a in self.suspicious_activities
        ]
        
        return honeypot_traffic
    
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
                "tool": "Cyber Mirage PCAP Analyzer"
            },
            "statistics": self.get_statistics(),
            "suspicious_activities": [
                {
                    "type": a.activity_type,
                    "description": a.description,
                    "src_ip": a.src_ip,
                    "dst_ip": a.dst_ip,
                    "confidence": a.confidence,
                    "evidence": a.evidence
                }
                for a in self.suspicious_activities
            ],
            "sessions": [
                {
                    "id": s.session_id,
                    "src": f"{s.src_ip}:{s.src_port}",
                    "dst": f"{s.dst_ip}:{s.dst_port}",
                    "packets": s.packet_count,
                    "bytes": s.bytes_transferred
                }
                for s in self.sessions.values()
            ][:100]  # أول 100 جلسة
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported analysis to {file_path}")
        return file_path
    
    def generate_report(self) -> str:
        """
        توليد تقرير تحليل PCAP
        
        Returns:
            التقرير النصي
        """
        stats = self.get_statistics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║              CYBER MIRAGE - PCAP ANALYSIS REPORT                 ║
╠══════════════════════════════════════════════════════════════════╣
║  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<50} ║
╠══════════════════════════════════════════════════════════════════╣

📊 TRAFFIC STATISTICS:
═══════════════════════════════════════════════════════════════════
  Total Packets: {stats.get('total_packets', 0)}
  Total Bytes: {stats.get('total_bytes', 0) / 1024:.2f} KB
  Unique Source IPs: {stats.get('unique_src_ips', 0)}
  Unique Dest IPs: {stats.get('unique_dst_ips', 0)}
  Sessions: {stats.get('sessions', 0)}

📈 TOP PROTOCOLS:
"""
        for proto, count in stats.get('protocols', {}).items():
            report += f"  - {proto}: {count}\n"
        
        report += "\n🎯 TOP DESTINATION PORTS:\n"
        for port, count in stats.get('top_dst_ports', {}).items():
            service = self.KNOWN_PORTS.get(int(port), "Unknown")
            report += f"  - {port} ({service}): {count}\n"
        
        report += "\n🌐 TOP SOURCE IPs:\n"
        for ip, count in stats.get('top_src_ips', {}).items():
            report += f"  - {ip}: {count} packets\n"
        
        report += f"\n⚠️ SUSPICIOUS ACTIVITIES: {len(self.suspicious_activities)}\n"
        for activity in self.suspicious_activities[:10]:
            report += f"""
  🔴 {activity.activity_type.upper()}
     From: {activity.src_ip} → {activity.dst_ip}
     Description: {activity.description}
     Confidence: {activity.confidence:.0%}
"""
        
        report += """
═══════════════════════════════════════════════════════════════════
                    End of PCAP Analysis Report
╚══════════════════════════════════════════════════════════════════╝
"""
        return report


if __name__ == "__main__":
    # اختبار
    analyzer = PcapAnalyzer()
    print("PCAP Analyzer initialized")
    print(f"Known ports: {len(analyzer.KNOWN_PORTS)}")
