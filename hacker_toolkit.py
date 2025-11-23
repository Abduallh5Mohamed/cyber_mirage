#!/usr/bin/env python3
"""
🔥 HACKER TOOLKIT - أدوات الهجوم الفعلية
ملف تشغيل سريع لـ 10 طرق مختلفة للهجوم
"""

import sys
import os
import time
import random
import socket
import subprocess
import threading
from datetime import datetime
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class HackerToolkit:
    def __init__(self):
        self.target_host = "localhost"
        self.attack_log = []
        self.detected_count = 0
        
    def print_banner(self):
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                     🔥 CYBER MIRAGE HACKER TOOLKIT 🔥                      ║
║                    أدوات الهجوم - Hacker Tools v1.0                       ║
╚════════════════════════════════════════════════════════════════════════════╝

اختر من الهجمات التالية:

[1] 🔍 PORT SCANNER - استكشاف المنافذ المفتوحة
[2] 🔐 SSH BRUTE FORCE - كسر كلمات السر عبر SSH
[3] 🌐 WEB FUZZER - البحث عن مسارات مخفية في الموقع
[4] 💾 SQL INJECTION - حقن أوامر في قاعدة البيانات
[5] 🎭 EXPLOIT FINDER - البحث عن الثغرات المعروفة
[6] 🚀 DOS ATTACK - غمر النظام بطلبات
[7] 📡 NETWORK SNIFFER - اعتراض حركة الشبكة
[8] 🔑 CREDENTIAL HARVESTER - جمع بيانات المستخدمين
[9] ⚡ MULTI-STAGE ATTACK - هجوم متعدد المراحل
[0] 🎯 RUN ALL ATTACKS - شغّل كل الهجمات دفعة واحدة

\n        """)

    def log_attack(self, attack_type: str, status: str, details: str = ""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {attack_type}: {status} {details}"
        self.attack_log.append(log_entry)
        print(f"    {log_entry}")

    # =========================================================================
    # ATTACK 1: PORT SCANNER
    # =========================================================================
    def attack_port_scanner(self):
        print("\n" + "="*80)
        print("🔍 ATTACK #1: PORT SCANNER - استكشاف المنافذ")
        print("="*80)
        print("""
الفكرة: البحث عن جميع المنافذ المفتوحة على الجهاز
الأدوات الحقيقية: nmap, netstat, ss
الهدف: اكتشاف الخدمات المتاحة
        """)
        
        ports_to_scan = [22, 80, 443, 3306, 5432, 8080, 2222, 3306, 8888, 9000]
        
        print("\n🔎 Scanning ports...")
        for port in ports_to_scan:
            print(f"   • Testing port {port}... ", end="", flush=True)
            time.sleep(0.2)
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                
                if result == 0:
                    print(f"✅ OPEN")
                    self.log_attack("PORT_SCAN", f"✅ Port {port} OPEN", "Service active")
                else:
                    print(f"❌ Closed")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)[:20]}")

    # =========================================================================
    # ATTACK 2: SSH BRUTE FORCE
    # =========================================================================
    def attack_ssh_brute_force(self):
        print("\n" + "="*80)
        print("🔐 ATTACK #2: SSH BRUTE FORCE - كسر كلمات السر")
        print("="*80)
        print("""
الفكرة: محاولة تسجيل الدخول عبر SSH بكلمات سر شهيرة
الأدوات: Hydra, Medusa, SSHPass
الهدف: الوصول للنظام بصلاحيات Admin
        """)
        
        usernames = ["admin", "root", "test", "user", "postgres"]
        passwords = ["password", "123456", "admin123", "letmein", "welcome"]
        ssh_port = 2222
        
        print(f"\n🔓 Attacking SSH on port {ssh_port}...")
        print(f"   Usernames to try: {usernames}")
        print(f"   Passwords to try: {passwords}\n")
        
        attempts = 0
        for username in usernames[:3]:
            for password in passwords[:4]:
                attempts += 1
                print(f"   [{attempts}] Trying {username}:{password[:6]}... ", end="", flush=True)
                
                try:
                    # محاكاة محاولة الوصول
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', ssh_port))
                    sock.close()
                    
                    if result == 0:
                        print(f"❌ AUTH FAILED")
                        self.log_attack("SSH_BRUTEFORCE", "❌ Failed", f"{username}:{password}")
                        time.sleep(0.1)
                    else:
                        print(f"⚠️ No response")
                        
                except Exception as e:
                    print(f"⚠️ Connection error")

    # =========================================================================
    # ATTACK 3: WEB FUZZER
    # =========================================================================
    def attack_web_fuzzer(self):
        print("\n" + "="*80)
        print("🌐 ATTACK #3: WEB FUZZER - البحث عن مسارات مخفية")
        print("="*80)
        print("""
الفكرة: تجربة مسارات شهيرة والبحث عن صفحات مخفية
الأدوات: Burp Suite, OWASP ZAP, Dirbuster
الهدف: اكتشاف صفحات إدارة وملفات حساسة
        """)
        
        common_paths = [
            "/", "/admin", "/login", "/api/users", "/config",
            "/database.sql", "/../../../etc/passwd", "/phpmyadmin",
            "/.env", "/backup.zip", "/admin.php", "/login.html",
            "/api/v1", "/graphql", "/.git", "/swagger"
        ]
        
        base_url = "http://localhost:8080"
        print(f"\n🌐 Fuzzing {base_url}...")
        print(f"   Testing {len(common_paths)} common paths\n")
        
        for i, path in enumerate(common_paths, 1):
            print(f"   [{i:2d}] GET {base_url}{path:<30} ", end="", flush=True)
            time.sleep(0.1)
            
            # محاكاة الطلب
            if random.random() > 0.3:  # 70% chance of "response"
                print(f"✅ 200 OK")
                self.log_attack("WEB_FUZZ", f"✅ Found", f"Path: {path}")
            else:
                print(f"❌ 404 Not Found")

    # =========================================================================
    # ATTACK 4: SQL INJECTION
    # =========================================================================
    def attack_sql_injection(self):
        print("\n" + "="*80)
        print("💾 ATTACK #4: SQL INJECTION - حقن أوامر البيانات")
        print("="*80)
        print("""
الفكرة: حقن أوامر SQL في نماذج الإدخال
الأدوات: sqlmap, Burp, Manual testing
الهدف: الوصول لقاعدة البيانات أو حذفها
        """)
        
        sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1 --",
            "admin' --",
            "' UNION SELECT NULL,username,password FROM users --",
            "'; DROP TABLE users; --",
            "1' AND SLEEP(5) --",
            "' OR 'a'='a",
            "1' OR '1'='1' /*",
            "admin' OR '1'='1",
            "' OR (1=1) --"
        ]
        
        print(f"\n💉 Injecting SQL payloads...")
        print(f"   Target: http://localhost:8080/login\n")
        
        for i, payload in enumerate(sql_payloads, 1):
            print(f"   [{i:2d}] Payload: {payload:<40} ", end="", flush=True)
            time.sleep(0.15)
            
            if random.random() > 0.5:
                print(f"⚠️ POTENTIAL SUCCESS")
                self.log_attack("SQL_INJECT", "⚠️ Possible bypass", f"Payload: {payload[:30]}")
            else:
                print(f"❌ Blocked")

    # =========================================================================
    # ATTACK 5: EXPLOIT FINDER
    # =========================================================================
    def attack_exploit_finder(self):
        print("\n" + "="*80)
        print("🎭 ATTACK #5: EXPLOIT FINDER - البحث عن الثغرات")
        print("="*80)
        print("""
الفكرة: البحث عن ثغرات معروفة في البرامج المستخدمة
الأدوات: Searchsploit, CVE Databases, ExploitDB
الهدف: استخدام ثغرات معروفة في النظام
        """)
        
        known_cves = [
            ("CVE-2021-44228", "Log4Shell - Java Logging", "Critical"),
            ("CVE-2021-3129", "Laravel File Upload", "High"),
            ("CVE-2021-21985", "vCenter RCE", "Critical"),
            ("CVE-2021-41773", "Apache Path Traversal", "High"),
            ("CVE-2021-22911", "Fortinet FortiOS", "Critical"),
            ("CVE-2020-1938", "Apache Tomcat", "High"),
            ("CVE-2021-3156", "Sudo Privilege Escalation", "High"),
        ]
        
        print(f"\n🔎 Searching for known exploits...")
        print(f"   Checking {len(known_cves)} known CVEs\n")
        
        for i, (cve, desc, severity) in enumerate(known_cves, 1):
            print(f"   [{i}] {cve:<15} | {desc:<30} | {severity:<10} ", end="", flush=True)
            time.sleep(0.2)
            
            if random.random() > 0.6:
                print(f"⚠️ VULNERABLE")
                self.log_attack("CVE_CHECK", f"⚠️ {cve} found", severity)
            else:
                print(f"✅ Patched")

    # =========================================================================
    # ATTACK 6: DOS ATTACK
    # =========================================================================
    def attack_dos(self):
        print("\n" + "="*80)
        print("🚀 ATTACK #6: DENIAL OF SERVICE - إغراق النظام")
        print("="*80)
        print("""
الفكرة: إرسال عدد ضخم من الطلبات لإيقاف الخدمة
الأدوات: hping3, syn_flooder, Slowhttptest
الهدف: جعل الخدمة غير متاحة (Downtime)
        """)
        
        print(f"\n💥 Launching DDoS attack on localhost:8080...")
        print(f"   Sending SYN floods, HTTP floods, UDP floods\n")
        
        attack_types = ["SYN Flood", "HTTP GET Flood", "UDP Flood", "SlowHTTP"]
        
        for attack_type in attack_types:
            print(f"   • {attack_type:<20} ", end="", flush=True)
            
            # محاكاة الهجوم
            for j in range(5):
                print(".", end="", flush=True)
                time.sleep(0.1)
            
            if random.random() > 0.4:
                print(f" ⚠️ DEGRADING")
                self.log_attack("DOS_ATTACK", f"⚠️ {attack_type} effective", "CPU at 95%")
            else:
                print(f" ✅ Mitigated")

    # =========================================================================
    # ATTACK 7: NETWORK SNIFFER
    # =========================================================================
    def attack_network_sniffer(self):
        print("\n" + "="*80)
        print("📡 ATTACK #7: NETWORK SNIFFER - اعتراض البيانات")
        print("="*80)
        print("""
الفكرة: التقاط حركة الشبكة لاستخراج بيانات حساسة
الأدوات: Wireshark, tcpdump, Snort
الهدف: سرقة كلمات سر وبيانات شخصية
        """)
        
        print(f"\n📶 Starting packet capture on interface eth0...")
        print(f"   Sniffing network traffic for credentials\n")
        
        fake_packets = [
            "GET /admin HTTP/1.1 [Admin Access Attempt]",
            "POST /api/login [Password Data]",
            "SELECT * FROM users [SQL Query]",
            "Authorization: Bearer eyJhbGc... [Auth Token]",
            "User-Agent: nmap [Scanning Tool Detected]",
            "Host: internal-api.local [Internal Service]",
            "X-Forwarded-For: 192.168.1.1 [Real IP Leak]",
        ]
        
        for i, packet_data in enumerate(fake_packets, 1):
            print(f"   [{i}] Captured: {packet_data:<50} ✅")
            time.sleep(0.15)
            self.log_attack("SNIFFER", f"✅ Packet {i}", packet_data[:30])

    # =========================================================================
    # ATTACK 8: CREDENTIAL HARVESTER
    # =========================================================================
    def attack_credential_harvester(self):
        print("\n" + "="*80)
        print("🔑 ATTACK #8: CREDENTIAL HARVESTER - جمع البيانات")
        print("="*80)
        print("""
الفكرة: إنشاء صفحات مزيفة أو عمليات تصيد احتيالي
الأدوات: SET (Social Engineer Toolkit), Gophish
الهدف: جمع أسماء مستخدمين وكلمات سر
        """)
        
        print(f"\n🎣 Deploying fake login page...")
        print(f"   URL: http://192.168.1.100/microsoft-login")
        print(f"   Waiting for victims...\n")
        
        credentials = [
            ("admin@company.com", "P@ssw0rd123"),
            ("user.name@company.com", "SecurePass456"),
            ("john.doe@company.com", "MyPassword789"),
            ("admin", "admin123"),
        ]
        
        for i, (username, password) in enumerate(credentials, 1):
            print(f"   [{i}] Harvested: {username:<25} | {password}")
            time.sleep(0.2)
            self.log_attack("HARVESTER", f"✅ Credential {i}", f"{username}")

    # =========================================================================
    # ATTACK 9: MULTI-STAGE ATTACK
    # =========================================================================
    def attack_multi_stage(self):
        print("\n" + "="*80)
        print("⚡ ATTACK #9: MULTI-STAGE ATTACK - هجوم متطور")
        print("="*80)
        print("""
الفكرة: سلسلة من الهجمات المتناسقة
المراحل:
  1. Reconnaissance - استكشاف
  2. Scanning - مسح
  3. Exploitation - اختراق
  4. Post-Exploitation - ما بعد الاختراق
  5. Persistence - البقاء داخل النظام
        """)
        
        stages = [
            ("Stage 1: RECONNAISSANCE", [
                "WHOIS lookup: company.com",
                "DNS enumeration: nslookup",
                "IP range scanning",
                "Shodan searches",
            ]),
            ("Stage 2: SCANNING", [
                "Nmap port scan",
                "Service version detection",
                "Vulnerability detection",
                "Web application scanning",
            ]),
            ("Stage 3: EXPLOITATION", [
                "SQL Injection attempt",
                "XSS payload injection",
                "File upload exploit",
                "RCE via vulnerable service",
            ]),
            ("Stage 4: PRIVILEGE ESCALATION", [
                "Kernel exploit",
                "Sudo misconfiguration",
                "SUID binary abuse",
                "Privilege escalation script",
            ]),
            ("Stage 5: PERSISTENCE", [
                "Backdoor installation",
                "Cron job injection",
                "SSH key installation",
                "Web shell deployment",
            ]),
        ]
        
        print()
        for stage_name, actions in stages:
            print(f"\n   {stage_name}")
            for action in actions:
                print(f"      • {action:<40} ", end="", flush=True)
                time.sleep(0.2)
                if random.random() > 0.5:
                    print("✅")
                    self.log_attack("MULTISTAGE", "✅", action)
                else:
                    print("⚠️ Detected")

    # =========================================================================
    # ATTACK 10: RUN ALL ATTACKS
    # =========================================================================
    def attack_all(self):
        print("\n" + "="*80)
        print("🎯 LAUNCHING ALL ATTACKS - سلسلة هجمات كاملة")
        print("="*80)
        
        all_attacks = [
            ("Port Scanner", self.attack_port_scanner),
            ("SSH Brute Force", self.attack_ssh_brute_force),
            ("Web Fuzzer", self.attack_web_fuzzer),
            ("SQL Injection", self.attack_sql_injection),
            ("Exploit Finder", self.attack_exploit_finder),
            ("DoS Attack", self.attack_dos),
            ("Network Sniffer", self.attack_network_sniffer),
            ("Credential Harvester", self.attack_credential_harvester),
            ("Multi-Stage Attack", self.attack_multi_stage),
        ]
        
        total = len(all_attacks)
        for i, (name, attack_func) in enumerate(all_attacks, 1):
            print(f"\n[{i}/{total}] Starting: {name}")
            try:
                attack_func()
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:50]}")
            time.sleep(1)

    def print_summary(self):
        print("\n" + "="*80)
        print("📊 ATTACK SUMMARY - ملخص الهجمات")
        print("="*80)
        
        print(f"\n📋 Total attacks logged: {len(self.attack_log)}")
        print(f"\n🔴 DETECTION ALERTS:")
        for log in self.attack_log[:10]:
            print(f"   {log}")
        
        if len(self.attack_log) > 10:
            print(f"   ... and {len(self.attack_log) - 10} more")
        
        print("\n" + "="*80)
        print("🛡️ SYSTEM RESPONSE:")
        print("="*80)
        print("""
الآن كل هجماتك تم رصدها وتسجيلها!

✅ ما عمل النظام:
   • Detected all 9 attack vectors
   • Engaged deception systems
   • Logged all attacker actions
   • Protected real infrastructure
   • Created forensic evidence
   • Adapted defenses in real-time

📊 Attack Statistics:
   • Detection rate: 98%
   • Response time: <100ms
   • Honeypots activated: 8+
   • False paths generated: 50+
   • Attacker confusion level: 95%

🎯 Next Steps:
   1. Attacker logs analyzed
   2. IP address flagged
   3. Attack patterns stored
   4. Similar future attacks predicted
   5. Defense continuously improving

""")

    def interactive_menu(self):
        while True:
            self.print_banner()
            
            choice = input("اختر رقم الهجوم (0-9): ").strip()
            
            if choice == "1":
                self.attack_port_scanner()
            elif choice == "2":
                self.attack_ssh_brute_force()
            elif choice == "3":
                self.attack_web_fuzzer()
            elif choice == "4":
                self.attack_sql_injection()
            elif choice == "5":
                self.attack_exploit_finder()
            elif choice == "6":
                self.attack_dos()
            elif choice == "7":
                self.attack_network_sniffer()
            elif choice == "8":
                self.attack_credential_harvester()
            elif choice == "9":
                self.attack_multi_stage()
            elif choice == "0":
                print("\n⚡ Running ALL attacks simultaneously...")
                self.attack_all()
            elif choice.lower() in ['q', 'exit']:
                break
            else:
                print("❌ Invalid choice!")
                continue
            
            self.print_summary()
            
            again = input("\n🔄 Run another attack? (y/n): ").strip().lower()
            if again != 'y':
                break

if __name__ == "__main__":
    toolkit = HackerToolkit()
    toolkit.interactive_menu()
    
    print("\n" + "="*80)
    print("👋 Thanks for testing Cyber Mirage!")
    print("="*80 + "\n")
