"""
🕸️ ARP Spoofing & Deception Module
خداع ARP لتحويل المهاجمين إلى Honeypots

يستخدم Scapy لتطبيق ARP spoofing داخل الشبكة المعزولة
"""

from scapy.all import ARP, Ether, sendp, sniff, conf
from typing import Dict, List, Optional
import threading
import time
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ARPTarget:
    """هدف ARP للخداع"""
    victim_ip: str
    victim_mac: str
    gateway_ip: str
    gateway_mac: str
    honeypot_ip: str
    honeypot_mac: str


class ARPSpoofer:
    """
    محرك خداع ARP
    يقوم بتحويل المهاجمين إلى honeypots بدلاً من الأهداف الحقيقية
    """
    
    def __init__(self, interface: str = "eth0"):
        self.interface = interface
        self.active_spoofs: Dict[str, ARPTarget] = {}
        self.spoofing_active = False
        self.spoof_thread = None
        
        # تعطيل الرسائل الزائدة من Scapy
        conf.verb = 0
    
    def get_mac(self, ip: str) -> Optional[str]:
        """
        الحصول على MAC address من IP
        """
        try:
            # إرسال ARP request
            arp_request = ARP(pdst=ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            
            answered_list = sendp(arp_request_broadcast, 
                                  iface=self.interface, 
                                  timeout=2, 
                                  verbose=False)
            
            if answered_list:
                return answered_list[0][1].hwsrc
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting MAC for {ip}: {e}")
            return None
    
    def spoof_arp(self, target_ip: str, spoof_ip: str, target_mac: str):
        """
        إرسال ARP reply مزيف
        """
        # بناء ARP reply يدعي أن spoof_ip له MAC الخاص بنا
        arp_reply = ARP(
            op=2,  # ARP reply
            pdst=target_ip,
            hwdst=target_mac,
            psrc=spoof_ip
        )
        
        sendp(Ether(dst=target_mac) / arp_reply, 
              iface=self.interface, 
              verbose=False)
    
    def restore_arp(self, target_ip: str, gateway_ip: str, 
                    target_mac: str, gateway_mac: str):
        """
        استعادة ARP الطبيعي
        """
        arp_reply = ARP(
            op=2,
            pdst=target_ip,
            hwdst=target_mac,
            psrc=gateway_ip,
            hwsrc=gateway_mac
        )
        
        sendp(Ether(dst=target_mac) / arp_reply, 
              iface=self.interface, 
              count=5, 
              verbose=False)
    
    def start_spoofing(self, target: ARPTarget):
        """
        بدء خداع ARP لهدف معين
        """
        logger.info(f"Starting ARP spoofing for {target.victim_ip}")
        self.active_spoofs[target.victim_ip] = target
        
        if not self.spoofing_active:
            self.spoofing_active = True
            self.spoof_thread = threading.Thread(target=self._spoof_loop)
            self.spoof_thread.daemon = True
            self.spoof_thread.start()
    
    def _spoof_loop(self):
        """
        حلقة الخداع المستمرة
        """
        logger.info("ARP spoofing loop started")
        
        while self.spoofing_active:
            for victim_ip, target in self.active_spoofs.items():
                try:
                    # خداع الضحية: أخبره أن gateway هو honeypot
                    self.spoof_arp(
                        target_ip=target.victim_ip,
                        spoof_ip=target.gateway_ip,
                        target_mac=target.victim_mac
                    )
                    
                    # خداع gateway: أخبره أن الضحية هي honeypot
                    self.spoof_arp(
                        target_ip=target.gateway_ip,
                        spoof_ip=target.victim_ip,
                        target_mac=target.gateway_mac
                    )
                    
                except Exception as e:
                    logger.error(f"Error spoofing {victim_ip}: {e}")
            
            # إرسال كل 2 ثانية
            time.sleep(2)
    
    def stop_spoofing(self, victim_ip: str):
        """
        إيقاف خداع هدف معين
        """
        if victim_ip in self.active_spoofs:
            target = self.active_spoofs[victim_ip]
            
            logger.info(f"Stopping ARP spoofing for {victim_ip}")
            
            # استعادة ARP الطبيعي
            self.restore_arp(
                target_ip=target.victim_ip,
                gateway_ip=target.gateway_ip,
                target_mac=target.victim_mac,
                gateway_mac=target.gateway_mac
            )
            
            del self.active_spoofs[victim_ip]
            
            # إيقاف الخيط إذا لم يعد هناك أهداف
            if not self.active_spoofs:
                self.spoofing_active = False
    
    def stop_all(self):
        """
        إيقاف جميع عمليات الخداع
        """
        logger.info("Stopping all ARP spoofing")
        
        victims = list(self.active_spoofs.keys())
        for victim_ip in victims:
            self.stop_spoofing(victim_ip)
        
        self.spoofing_active = False


class ARPMonitor:
    """
    مراقب ARP لكشف التهديدات
    """
    
    def __init__(self, interface: str = "eth0"):
        self.interface = interface
        self.arp_table: Dict[str, str] = {}
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """
        بدء مراقبة ARP
        """
        logger.info("Starting ARP monitoring")
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """
        حلقة المراقبة
        """
        def process_packet(packet):
            if packet.haslayer(ARP):
                if packet[ARP].op == 2:  # ARP reply
                    ip = packet[ARP].psrc
                    mac = packet[ARP].hwsrc
                    
                    # كشف ARP spoofing
                    if ip in self.arp_table:
                        if self.arp_table[ip] != mac:
                            logger.warning(
                                f"⚠️ ARP Spoofing Detected! "
                                f"IP {ip} changed MAC from "
                                f"{self.arp_table[ip]} to {mac}"
                            )
                    
                    self.arp_table[ip] = mac
        
        sniff(iface=self.interface, 
              prn=process_packet, 
              filter="arp", 
              store=False,
              stop_filter=lambda x: not self.monitoring)
    
    def stop_monitoring(self):
        """
        إيقاف المراقبة
        """
        logger.info("Stopping ARP monitoring")
        self.monitoring = False


class ARPDeceptionEngine:
    """
    محرك خداع ARP متقدم
    يدمج الخداع مع الذكاء الاصطناعي
    """
    
    def __init__(self, interface: str = "eth0"):
        self.spoofer = ARPSpoofer(interface)
        self.monitor = ARPMonitor(interface)
        self.deception_rules: List[Dict] = []
    
    def add_deception_rule(self, rule: Dict):
        """
        إضافة قاعدة خداع
        
        rule = {
            'victim_subnet': '192.168.1.0/24',
            'honeypot_ip': '192.168.1.100',
            'condition': 'suspicious_activity',
            'duration': 300  # seconds
        }
        """
        self.deception_rules.append(rule)
        logger.info(f"Added deception rule: {rule}")
    
    def activate_deception(self, victim_ip: str, honeypot_ip: str):
        """
        تفعيل الخداع لهدف معين
        """
        # الحصول على MAC addresses
        victim_mac = self.spoofer.get_mac(victim_ip)
        gateway_mac = self.spoofer.get_mac("192.168.1.1")  # افتراضي
        honeypot_mac = self.spoofer.get_mac(honeypot_ip)
        
        if not all([victim_mac, gateway_mac, honeypot_mac]):
            logger.error(f"Cannot get MAC addresses for deception")
            return False
        
        target = ARPTarget(
            victim_ip=victim_ip,
            victim_mac=victim_mac,
            gateway_ip="192.168.1.1",
            gateway_mac=gateway_mac,
            honeypot_ip=honeypot_ip,
            honeypot_mac=honeypot_mac
        )
        
        self.spoofer.start_spoofing(target)
        return True
    
    def start(self):
        """
        تشغيل محرك الخداع
        """
        logger.info("🕸️ ARP Deception Engine Started")
        self.monitor.start_monitoring()
    
    def stop(self):
        """
        إيقاف محرك الخداع
        """
        logger.info("🕸️ ARP Deception Engine Stopped")
        self.spoofer.stop_all()
        self.monitor.stop_monitoring()


# Demo
if __name__ == "__main__":
    print("🕸️ ARP SPOOFING & DECEPTION - DEMO")
    print("="*80)
    
    print("""
⚠️ WARNING: This tool is for AUTHORIZED TESTING ONLY!
⚠️ Using ARP spoofing without permission is ILLEGAL!
⚠️ Use only in isolated lab environments!
    """)
    
    print("\n1️⃣ Creating ARP Deception Engine...")
    engine = ARPDeceptionEngine(interface="eth0")
    
    print("\n2️⃣ Starting ARP monitoring...")
    engine.start()
    
    print("\n3️⃣ Simulating deception activation...")
    print("   (In production, this would redirect attacker to honeypot)")
    
    # في بيئة حقيقية:
    # engine.activate_deception(
    #     victim_ip="192.168.1.50",
    #     honeypot_ip="192.168.1.100"
    # )
    
    print("\n✅ Demo complete!")
    print("\n📝 Note: Actual spoofing requires:")
    print("   - Root/Admin privileges")
    print("   - Valid network interface")
    print("   - Isolated test environment")
    print("   - Legal authorization")
    
    engine.stop()
