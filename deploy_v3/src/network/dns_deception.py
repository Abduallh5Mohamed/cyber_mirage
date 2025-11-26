"""
🌐 DNS Deception Module
خداع DNS لتحويل المهاجمين إلى Honeypots

يستخدم DNS poisoning لإعادة توجيه الطلبات إلى خدمات وهمية
"""

from scapy.all import DNS, DNSQR, DNSRR, IP, UDP, send, sniff, conf
import threading
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DNSRule:
    """قاعدة DNS deception"""
    domain: str
    fake_ip: str
    record_type: str = "A"  # A, AAAA, CNAME, etc.
    ttl: int = 300


class DNSDeceptionServer:
    """
    خادم DNS خادع
    يعيد توجيه طلبات DNS إلى honeypots
    """
    
    def __init__(self, interface: str = "eth0", dns_port: int = 53):
        self.interface = interface
        self.dns_port = dns_port
        self.deception_rules: Dict[str, DNSRule] = {}
        self.running = False
        self.server_thread = None
        
        # تعطيل رسائل Scapy الزائدة
        conf.verb = 0
    
    def add_rule(self, rule: DNSRule):
        """
        إضافة قاعدة خداع DNS
        """
        self.deception_rules[rule.domain.lower()] = rule
        logger.info(f"Added DNS rule: {rule.domain} -> {rule.fake_ip}")
    
    def remove_rule(self, domain: str):
        """
        إزالة قاعدة خداع
        """
        if domain.lower() in self.deception_rules:
            del self.deception_rules[domain.lower()]
            logger.info(f"Removed DNS rule: {domain}")
    
    def should_deceive(self, domain: str) -> Optional[DNSRule]:
        """
        التحقق من وجوب خداع النطاق
        """
        domain_lower = domain.lower()
        
        # مطابقة مباشرة
        if domain_lower in self.deception_rules:
            return self.deception_rules[domain_lower]
        
        # مطابقة wildcard (*.example.com)
        for rule_domain, rule in self.deception_rules.items():
            if rule_domain.startswith("*."):
                pattern = rule_domain[2:]  # إزالة *.
                if domain_lower.endswith(pattern):
                    return rule
        
        return None
    
    def create_fake_response(self, packet, rule: DNSRule):
        """
        إنشاء استجابة DNS مزيفة
        """
        try:
            # استخراج الطلب
            query = packet[DNSQR]
            
            # بناء الاستجابة
            dns_response = DNS(
                id=packet[DNS].id,
                qr=1,  # Response
                aa=1,  # Authoritative Answer
                qd=packet[DNS].qd,
                an=DNSRR(
                    rrname=query.qname,
                    type=rule.record_type,
                    rdata=rule.fake_ip,
                    ttl=rule.ttl
                )
            )
            
            # بناء IP packet
            ip_response = IP(
                src=packet[IP].dst,
                dst=packet[IP].src
            )
            
            # بناء UDP packet
            udp_response = UDP(
                sport=packet[UDP].dport,
                dport=packet[UDP].sport
            )
            
            # دمج الكل
            response_packet = ip_response / udp_response / dns_response
            
            return response_packet
            
        except Exception as e:
            logger.error(f"Error creating fake DNS response: {e}")
            return None
    
    def process_dns_packet(self, packet):
        """
        معالجة DNS packet
        """
        try:
            if packet.haslayer(DNSQR):
                query = packet[DNSQR]
                domain = query.qname.decode('utf-8').rstrip('.')
                
                logger.debug(f"DNS Query: {domain}")
                
                # التحقق من وجوب الخداع
                rule = self.should_deceive(domain)
                
                if rule:
                    logger.info(
                        f"🎭 Deceiving DNS query for {domain} "
                        f"-> redirecting to {rule.fake_ip}"
                    )
                    
                    # إنشاء استجابة مزيفة
                    fake_response = self.create_fake_response(packet, rule)
                    
                    if fake_response:
                        # إرسال الاستجابة
                        send(fake_response, iface=self.interface, verbose=False)
                        
                        return True  # تم الخداع
                
        except Exception as e:
            logger.error(f"Error processing DNS packet: {e}")
        
        return False
    
    def start(self):
        """
        تشغيل خادم DNS الخادع
        """
        logger.info(f"🌐 Starting DNS Deception Server on port {self.dns_port}")
        self.running = True
        
        self.server_thread = threading.Thread(target=self._server_loop)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def _server_loop(self):
        """
        حلقة الخادم الرئيسية
        """
        try:
            sniff(
                iface=self.interface,
                filter=f"udp port {self.dns_port}",
                prn=self.process_dns_packet,
                store=False,
                stop_filter=lambda x: not self.running
            )
        except Exception as e:
            logger.error(f"Error in DNS server loop: {e}")
    
    def stop(self):
        """
        إيقاف الخادم
        """
        logger.info("🌐 Stopping DNS Deception Server")
        self.running = False


class DNSPoisoner:
    """
    محرك DNS Poisoning
    يسمم DNS cache للمهاجمين
    """
    
    def __init__(self):
        self.poisoning_active = False
        self.poison_thread = None
    
    def poison_cache(self, target_ip: str, domain: str, fake_ip: str):
        """
        تسميم DNS cache لهدف معين
        """
        try:
            # إنشاء DNS response غير مطلوب
            dns_poison = IP(dst=target_ip) / \
                        UDP(dport=53) / \
                        DNS(
                            id=12345,
                            qr=1,
                            aa=1,
                            qd=DNSQR(qname=domain),
                            an=DNSRR(
                                rrname=domain,
                                rdata=fake_ip,
                                ttl=3600
                            )
                        )
            
            # إرسال عدة مرات لضمان النجاح
            send(dns_poison, count=5, verbose=False)
            
            logger.info(
                f"💉 Poisoned DNS cache: {domain} -> {fake_ip} "
                f"for target {target_ip}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error poisoning DNS cache: {e}")
            return False


class DNSMonitor:
    """
    مراقب DNS لكشف الأنشطة المشبوهة
    """
    
    def __init__(self, interface: str = "eth0"):
        self.interface = interface
        self.monitoring = False
        self.monitor_thread = None
        self.query_stats: Dict[str, int] = {}
    
    def start_monitoring(self):
        """
        بدء مراقبة DNS
        """
        logger.info("📊 Starting DNS monitoring")
        self.monitoring = True
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """
        حلقة المراقبة
        """
        def process_packet(packet):
            try:
                if packet.haslayer(DNSQR):
                    query = packet[DNSQR]
                    domain = query.qname.decode('utf-8').rstrip('.')
                    
                    # إحصائيات
                    self.query_stats[domain] = self.query_stats.get(domain, 0) + 1
                    
                    # كشف الأنشطة المشبوهة
                    if self.is_suspicious(domain):
                        logger.warning(f"⚠️ Suspicious DNS query: {domain}")
                        
            except Exception as e:
                logger.debug(f"Error monitoring DNS packet: {e}")
        
        sniff(
            iface=self.interface,
            filter="udp port 53",
            prn=process_packet,
            store=False,
            stop_filter=lambda x: not self.monitoring
        )
    
    def is_suspicious(self, domain: str) -> bool:
        """
        التحقق من كون النطاق مشبوه
        """
        # نطاقات C2 معروفة
        suspicious_patterns = [
            'dyn.com', 'no-ip', 'ddns',
            'ngrok', 'localtunnel',
            '.tk', '.ml', '.ga'  # نطاقات مجانية مشبوهة
        ]
        
        for pattern in suspicious_patterns:
            if pattern in domain.lower():
                return True
        
        # استعلامات متكررة جداً (DGA detection)
        if self.query_stats.get(domain, 0) > 100:
            return True
        
        return False
    
    def stop_monitoring(self):
        """
        إيقاف المراقبة
        """
        logger.info("📊 Stopping DNS monitoring")
        self.monitoring = False
    
    def get_stats(self) -> Dict:
        """
        الحصول على إحصائيات DNS
        """
        return {
            'total_queries': sum(self.query_stats.values()),
            'unique_domains': len(self.query_stats),
            'top_domains': sorted(
                self.query_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }


class DNSDeceptionEngine:
    """
    محرك خداع DNS متكامل
    """
    
    def __init__(self, interface: str = "eth0"):
        self.server = DNSDeceptionServer(interface)
        self.poisoner = DNSPoisoner()
        self.monitor = DNSMonitor(interface)
    
    def add_honeypot_redirect(self, domain: str, honeypot_ip: str):
        """
        إضافة إعادة توجيه إلى honeypot
        """
        rule = DNSRule(
            domain=domain,
            fake_ip=honeypot_ip,
            ttl=300
        )
        self.server.add_rule(rule)
    
    def add_wildcard_redirect(self, pattern: str, honeypot_ip: str):
        """
        إضافة إعادة توجيه wildcard (*.example.com)
        """
        rule = DNSRule(
            domain=pattern,
            fake_ip=honeypot_ip,
            ttl=300
        )
        self.server.add_rule(rule)
    
    def start(self):
        """
        تشغيل المحرك
        """
        logger.info("🌐 DNS Deception Engine Started")
        self.monitor.start_monitoring()
        self.server.start()
    
    def stop(self):
        """
        إيقاف المحرك
        """
        logger.info("🌐 DNS Deception Engine Stopped")
        self.server.stop()
        self.monitor.stop_monitoring()
    
    def get_statistics(self) -> Dict:
        """
        الحصول على إحصائيات شاملة
        """
        return {
            'active_rules': len(self.server.deception_rules),
            'dns_stats': self.monitor.get_stats()
        }


# Demo
if __name__ == "__main__":
    print("🌐 DNS DECEPTION - DEMO")
    print("="*80)
    
    print("""
⚠️ WARNING: This tool is for AUTHORIZED TESTING ONLY!
⚠️ Using DNS poisoning without permission is ILLEGAL!
⚠️ Use only in isolated lab environments!
    """)
    
    print("\n1️⃣ Creating DNS Deception Engine...")
    engine = DNSDeceptionEngine(interface="eth0")
    
    print("\n2️⃣ Adding deception rules...")
    
    # إعادة توجيه نطاقات محددة إلى honeypots
    engine.add_honeypot_redirect("evil-c2-server.com", "192.168.1.100")
    engine.add_honeypot_redirect("malware-download.net", "192.168.1.101")
    
    # إعادة توجيه wildcard
    engine.add_wildcard_redirect("*.attacker.com", "192.168.1.102")
    
    print("\n3️⃣ Rules added:")
    print("   evil-c2-server.com -> 192.168.1.100")
    print("   malware-download.net -> 192.168.1.101")
    print("   *.attacker.com -> 192.168.1.102")
    
    print("\n4️⃣ Starting DNS deception engine...")
    print("   (In production, this would intercept real DNS queries)")
    
    # engine.start()
    
    print("\n✅ Demo complete!")
    print("\n📝 Note: Actual DNS deception requires:")
    print("   - Root/Admin privileges")
    print("   - Valid network interface")
    print("   - Ability to intercept DNS traffic")
    print("   - Isolated test environment")
    print("   - Legal authorization")
    
    # engine.stop()
