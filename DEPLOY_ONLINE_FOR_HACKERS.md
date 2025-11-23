# 🌐 نشر Cyber Mirage على الإنترنت - دليل كامل
## اجعل نظامك هدفاً حقيقياً للهاكرز! 🎯

═══════════════════════════════════════════════════════════════════════
⚠️ تحذير: هذا الدليل لنشر النظام على الإنترنت الحقيقي!
   ستتعرض لهجمات حقيقية من هاكرز حقيقيين!
═══════════════════════════════════════════════════════════════════════

---

## 📋 الخيارات المتاحة للنشر:

### 🎯 **الخيار 1: VPS/Cloud Server (الأفضل)**
   - **DigitalOcean** - سهل جداً ($5-20/شهر)
   - **AWS EC2** - قوي ($10-50/شهر)
   - **Vultr** - رخيص ($5-10/شهر)
   - **Linode** - مستقر ($5-20/شهر)
   - **Contabo** - أرخص ($5/شهر)

### 🎯 **الخيار 2: من جهازك (مجاني لكن خطير)**
   - فتح Router ports
   - Dynamic DNS
   - مخاطر أمنية على شبكتك المنزلية

---

## 🚀 الطريقة الموصى بها: DigitalOcean

═══════════════════════════════════════════════════════════════════════
### الخطوة 1: إنشاء حساب وخادم
═══════════════════════════════════════════════════════════════════════

**1. اذهب إلى:**
   https://www.digitalocean.com

**2. أنشئ حساب جديد**
   - ستحصل على $200 credit مجاناً لمدة 60 يوم!

**3. اضغط "Create Droplet"**

**4. اختر المواصفات:**
   ```
   Image: Ubuntu 22.04 LTS
   Plan: 
      - Basic: $12/month (2 CPU, 4GB RAM) ← منصوح به
      - أو $24/month (4 CPU, 8GB RAM) ← للأداء العالي
   
   Datacenter: 
      - اختر قريب من موقعك (مثل Frankfurt)
   
   SSH Keys: 
      - أضف SSH key (أو استخدم password)
   
   Hostname: cyber-mirage-honeypot
   ```

**5. اضغط "Create Droplet"**
   - انتظر 1-2 دقيقة حتى يصبح جاهز
   - ستحصل على IP address (مثل: 134.209.89.123)

═══════════════════════════════════════════════════════════════════════
### الخطوة 2: الاتصال بالخادم
═══════════════════════════════════════════════════════════════════════

**من Windows PowerShell:**
```powershell
# استبدل IP_ADDRESS بالـ IP اللي حصلت عليه
ssh root@134.209.89.123

# اكتب yes للموافقة
# ادخل password (إذا طلب)
```

**ستصبح داخل الخادم!** 🎉

═══════════════════════════════════════════════════════════════════════
### الخطوة 3: تثبيت Docker على السيرفر
═══════════════════════════════════════════════════════════════════════

**قم بتشغيل هذه الأوامر واحدة تلو الأخرى:**

```bash
# 1. تحديث النظام
apt update && apt upgrade -y

# 2. تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. تثبيت Docker Compose
apt install docker-compose-plugin -y

# 4. التحقق من التثبيت
docker --version
docker compose version

# 5. تفعيل Docker للبدء التلقائي
systemctl enable docker
systemctl start docker
```

═══════════════════════════════════════════════════════════════════════
### الخطوة 4: رفع ملفات المشروع للسيرفر
═══════════════════════════════════════════════════════════════════════

**من جهازك (Windows PowerShell):**

```powershell
# انتقل لمجلد المشروع
cd A:\cyber_mirage

# انشئ ملف zip للمشروع (بدون venv و __pycache__)
Compress-Archive -Path src,docker,config,data,requirements*.txt,docker-compose.production.yml,Dockerfile.production,.env.example -DestinationPath cyber_mirage.zip

# ارفع الملف للسيرفر (غير IP_ADDRESS)
scp cyber_mirage.zip root@134.209.89.123:/root/

# البديل: استخدم WinSCP أو FileZilla
# أو ارفع على GitHub وسحبه من السيرفر
```

**على السيرفر:**
```bash
# فك الضغط
cd /root
apt install unzip -y
unzip cyber_mirage.zip -d cyber_mirage
cd cyber_mirage

# أنشئ .env.production
cp .env.example .env.production

# عدّل كلمات السر
nano .env.production
```

═══════════════════════════════════════════════════════════════════════
### الخطوة 5: إعداد Firewall (مهم جداً!)
═══════════════════════════════════════════════════════════════════════

**افتح المنافذ الضرورية فقط:**

```bash
# تثبيت ufw
apt install ufw -y

# السماح بـ SSH (ضروري!)
ufw allow 22/tcp

# المنافذ العامة (للهاكرز)
ufw allow 2222/tcp    # SSH Honeypot
ufw allow 8080/tcp    # Web Honeypot
ufw allow 2121/tcp    # FTP Honeypot
ufw allow 3306/tcp    # MySQL Honeypot

# Dashboard (اختياري - يفضل حمايته)
ufw allow 8501/tcp    # Streamlit Dashboard

# Monitoring (للمراقبة فقط - اتركها مغلقة)
# ufw allow 3000/tcp  # Grafana (لا تفتحه للعامة!)
# ufw allow 9090/tcp  # Prometheus (لا تفتحه!)

# تفعيل الجدار الناري
ufw --force enable

# التحقق من الحالة
ufw status verbose
```

═══════════════════════════════════════════════════════════════════════
### الخطوة 6: تشغيل النظام!
═══════════════════════════════════════════════════════════════════════

**على السيرفر:**

```bash
cd /root/cyber_mirage

# بناء الصور
docker compose -f docker-compose.production.yml build

# تشغيل جميع الخدمات
docker compose -f docker-compose.production.yml up -d

# التحقق من الحالة
docker compose -f docker-compose.production.yml ps

# مشاهدة اللوجات
docker compose -f docker-compose.production.yml logs -f
```

═══════════════════════════════════════════════════════════════════════
### الخطوة 7: الوصول للنظام
═══════════════════════════════════════════════════════════════════════

**من أي مكان في العالم:**

```
🎯 Honeypots (الأهداف للهاكرز):
   ssh://134.209.89.123:2222       ← SSH Honeypot
   http://134.209.89.123:8080      ← Web Honeypot
   ftp://134.209.89.123:2121       ← FTP Honeypot
   mysql://134.209.89.123:3306     ← MySQL Honeypot

📊 Dashboard (للمراقبة):
   http://134.209.89.123:8501      ← Streamlit Dashboard
   
🔧 Monitoring (من SSH فقط):
   http://localhost:3000           ← Grafana
   http://localhost:9090           ← Prometheus
```

═══════════════════════════════════════════════════════════════════════
### الخطوة 8: الإعلان عن النظام للهاكرز! 📢
═══════════════════════════════════════════════════════════════════════

**1. Shodan (محرك بحث الأجهزة المتصلة):**
   - الهاكرز يستخدمونه للبحث عن أهداف
   - نظامك سيظهر تلقائياً بعد أيام
   - لتسريع: https://www.shodan.io/host/134.209.89.123

**2. منتديات الهاكرز (احذر - للتجربة فقط):**
   ```
   🚨 Challenge: SSH Honeypot
   IP: 134.209.89.123:2222
   Prize: Try to break in! (Safe environment)
   ```

**3. مواقع تدريب الـ Pentesting:**
   - HackTheBox Discord
   - TryHackMe Forums
   - Reddit: r/netsec, r/AskNetsec

**4. Twitter/X:**
   ```
   🎯 New Honeypot Challenge!
   IP: 134.209.89.123
   Ports: 2222 (SSH), 8080 (Web), 3306 (MySQL)
   
   Try to hack it! All attempts are being monitored.
   #CyberSecurity #Honeypot #HackingChallenge
   ```

═══════════════════════════════════════════════════════════════════════
### الخطوة 9: مراقبة الهجمات 👁️
═══════════════════════════════════════════════════════════════════════

**A. من Dashboard (الأسهل):**
```bash
# افتح في متصفحك
http://134.209.89.123:8501
```

**B. من SSH Tunnel (Grafana الآمن):**
```powershell
# من جهازك المحلي
ssh -L 3000:localhost:3000 root@134.209.89.123

# ثم افتح في المتصفح
http://localhost:3000
# Username: admin
# Password: (من .env.production)
```

**C. من اللوجات المباشرة:**
```bash
# مشاهدة الهجمات Live
tail -f /root/cyber_mirage/logs/*.log

# أو من Docker
docker compose -f docker-compose.production.yml logs -f honeypots
```

═══════════════════════════════════════════════════════════════════════
### الخطوة 10: جمع البيانات والتحليل 📊
═══════════════════════════════════════════════════════════════════════

**بعد أسبوع/شهر، احصل على الإحصائيات:**

```bash
# عدد الهجمات
docker exec cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -c "SELECT COUNT(*) FROM attacks;"

# أكثر IPs هجوماً
docker exec cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -c "SELECT source_ip, COUNT(*) FROM attacks GROUP BY source_ip ORDER BY COUNT(*) DESC LIMIT 10;"

# أنواع الهجمات
docker exec cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -c "SELECT attack_type, COUNT(*) FROM attacks GROUP BY attack_type;"

# تصدير البيانات
docker exec cyber_mirage_postgres pg_dump -U cybermirage cyber_mirage > backup_$(date +%Y%m%d).sql
```

═══════════════════════════════════════════════════════════════════════
## 🔒 نصائح الأمان المهمة!
═══════════════════════════════════════════════════════════════════════

✅ **افعل:**
   1. غيّر كلمات السر في .env.production
   2. استخدم SSH Keys بدلاً من passwords
   3. راقب استخدام الموارد (CPU/RAM/Bandwidth)
   4. اقرأ اللوجات يومياً
   5. خذ نسخ احتياطية منتظمة

❌ **لا تفعل:**
   1. تضع بيانات حقيقية في الهني بوت
   2. تربط الهني بوت بشبكتك الداخلية
   3. تفتح جميع المنافذ
   4. تترك Grafana/Prometheus مفتوح للعامة
   5. تستخدم كلمات سر ضعيفة

═══════════════════════════════════════════════════════════════════════
## 💰 التكاليف المتوقعة
═══════════════════════════════════════════════════════════════════════

**DigitalOcean (موصى به):**
```
Droplet 4GB RAM: $12/month
Bandwidth: 4TB included (كافي جداً)
Snapshots/Backups: +$1-2/month
──────────────────────────────
Total: ~$14/month
```

**مجاني لأول شهرين بـ $200 credit!**

═══════════════════════════════════════════════════════════════════════
## 📊 ماذا تتوقع؟
═══════════════════════════════════════════════════════════════════════

**بعد 24 ساعة:**
   • 10-50 port scan
   • 5-20 SSH brute force attempts
   • 2-10 web scans

**بعد أسبوع:**
   • 500-2000 port scans
   • 100-500 SSH attempts
   • 50-200 web attacks
   • 10-50 SQL injection attempts

**بعد شهر:**
   • 5,000-20,000 attacks total!
   • IPs من 30+ دولة
   • Botnets سيحاولون استغلاله

═══════════════════════════════════════════════════════════════════════
## 🛑 إيقاف النظام
═══════════════════════════════════════════════════════════════════════

**على السيرفر:**
```bash
# إيقاف جميع الخدمات
cd /root/cyber_mirage
docker compose -f docker-compose.production.yml down

# حذف كل شيء (احذر!)
docker compose -f docker-compose.production.yml down -v
```

**على DigitalOcean:**
```
Settings → Destroy Droplet
```

═══════════════════════════════════════════════════════════════════════
## 🎓 أوامر مفيدة
═══════════════════════════════════════════════════════════════════════

```bash
# مشاهدة الموارد
docker stats

# مشاهدة اللوجات
docker compose logs -f honeypots

# إعادة تشغيل خدمة
docker compose restart honeypots

# الدخول لـ container
docker exec -it cyber_mirage_honeypots bash

# نسخة احتياطية للبيانات
docker exec cyber_mirage_postgres pg_dump -U cybermirage cyber_mirage > backup.sql

# تنظيف Docker
docker system prune -af
```

═══════════════════════════════════════════════════════════════════════
## 🎯 البديل السريع: من جهازك المحلي (للتجربة فقط)
═══════════════════════════════════════════════════════════════════════

**⚠️ تحذير: هذا يعرض شبكتك المنزلية للخطر!**

**1. افتح Router Admin Panel:**
   - عادة: http://192.168.1.1
   - Username/Password من ورقة الراوتر

**2. Port Forwarding:**
   ```
   External Port → Internal IP:Internal Port
   2222 → 192.168.1.X:2222 (SSH Honeypot)
   8080 → 192.168.1.X:8080 (Web Honeypot)
   8501 → 192.168.1.X:8501 (Dashboard)
   ```

**3. احصل على Public IP:**
   ```powershell
   # من PowerShell
   (Invoke-WebRequest -Uri "http://ifconfig.me/ip").Content
   ```

**4. Dynamic DNS (اختياري):**
   - استخدم No-IP.com أو DuckDNS
   - احصل على domain مجاني مثل: myhoneypot.ddns.net

═══════════════════════════════════════════════════════════════════════
## 📚 مصادر إضافية
═══════════════════════════════════════════════════════════════════════

**Documentation:**
   - DigitalOcean: https://docs.digitalocean.com
   - Docker: https://docs.docker.com
   - Docker Compose: https://docs.docker.com/compose

**مجتمعات:**
   - r/cybersecurity
   - r/netsec
   - HackTheBox Discord

═══════════════════════════════════════════════════════════════════════
## ✅ Checklist قبل النشر
═══════════════════════════════════════════════════════════════════════

- [ ] غيرت كلمات السر في .env.production
- [ ] ثبّت Docker و Docker Compose
- [ ] رفعت الملفات للسيرفر
- [ ] فتحت المنافذ الضرورية فقط في UFW
- [ ] شغّلت النظام بنجاح
- [ ] تأكدت من Dashboard يعمل
- [ ] جهّزت أدوات المراقبة
- [ ] أخذت نسخة احتياطية من إعدادات الـ server

═══════════════════════════════════════════════════════════════════════
🎉 مبروك! نظام Cyber Mirage الآن ONLINE ويستقبل هجمات حقيقية!
═══════════════════════════════════════════════════════════════════════

الآن راقب Dashboard وشاهد الهاكرز يحاولون الاختراق! 🔥

Good luck! 🚀
