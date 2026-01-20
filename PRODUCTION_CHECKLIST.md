# ✅ Production Deployment Checklist - Cyber Mirage

## المرحلة 1: إعداد AWS EC2 Instance (أنت هنا حالياً!)

### الإعدادات الحالية من الشاشة:
- ✅ Name: Cyber mirage
- ✅ AMI: Ubuntu 24.04 LTS
- ✅ Instance Type: m7i-flex.large

### ما يجب عمله الآن في AWS Console:

#### 1. التعديلات المطلوبة:

**Instance Type:**
- الحالي: m7i-flex.large (جيد جداً!)
- أو استخدم: `t2.large` أو `t3.large` (أرخص)
- **توصيتي:** إذا Budget محدود، استخدم `t2.large`

#### 2. Key Pair (مفتاح الدخول):
- إذا عندك key موجود، اختره
- إذا مافيش، اضغط "Create new key pair":
  - Name: `cyber-mirage-key`
  - Type: RSA
  - Format: `.pem` (لو هتستخدم PowerShell/Linux)
  - **احفظ الملف في مكان آمن!**

#### 3. Network Settings:
انزل تحت وعدل Security Group:

**Inbound Rules المطلوبة:**
```
Port 22   → My IP (SSH للإدارة)
Port 80   → 0.0.0.0/0 (HTTP)
Port 445  → 0.0.0.0/0 (SMB Honeypot)
Port 502  → 0.0.0.0/0 (Modbus Honeypot)
Port 1025 → 0.0.0.0/0 (Custom Honeypot)
Port 2121 → 0.0.0.0/0 (FTP Honeypot)
Port 2222 → 0.0.0.0/0 (SSH Honeypot)
Port 3000 → 0.0.0.0/0 (Grafana Dashboard)
Port 3307 → 0.0.0.0/0 (MySQL Honeypot)
Port 5434 → 0.0.0.0/0 (PostgreSQL Honeypot)
Port 8080 → 0.0.0.0/0 (HTTP Honeypot)
Port 8443 → 0.0.0.0/0 (HTTPS Honeypot)
Port 8501 → 0.0.0.0/0 (Streamlit Dashboard - الواجهة الرئيسية)
Port 9090 → My IP (Prometheus - للأمان)
```

#### 4. Storage:
- غيّر من 8 GB إلى **50 GB minimum**
- Type: gp3 (أفضل أداء)

#### 5. Launch Instance:
- اضغط "Launch instance" (الزر البرتقالي)
- انتظر 2-3 دقائق حتى يصبح Running

---

## المرحلة 2: الاتصال بالسيرفر

بعد ما الـ Instance يشتغل:

### 1. احصل على Public IP:
```
في AWS Console → EC2 → Instances → اختر Instance
شوف "Public IPv4 address"
```

### 2. اتصل بالسيرفر:

**من PowerShell (Windows):**
```powershell
# غيّر مسار الـ key والـ IP
ssh -i "C:\path\to\cyber-mirage-key.pem" ubuntu@YOUR_EC2_IP
```

**أول مرة قد تحتاج:**
```powershell
# لو الـ key file permissions غلط
icacls "C:\path\to\cyber-mirage-key.pem" /inheritance:r
icacls "C:\path\to\cyber-mirage-key.pem" /grant:r "%username%:R"
```

---

## المرحلة 3: تثبيت Docker على السيرفر

بعد ما تدخل SSH:

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker

# تثبيت Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# تأكد من التثبيت
docker --version
docker-compose --version
```

---

## المرحلة 4: رفع المشروع للسيرفر

### الطريقة 1: Git Clone (الأسهل)
```bash
git clone https://github.com/YOUR_USERNAME/cyber_mirage.git
cd cyber_mirage
```

### الطريقة 2: رفع الملفات يدوياً
**من جهازك (PowerShell):**
```powershell
# ضغط المشروع
cd A:\cyber_mirage
tar -czf cyber_mirage.tar.gz .

# رفع للسيرفر
scp -i "path\to\key.pem" cyber_mirage.tar.gz ubuntu@YOUR_EC2_IP:~/

# على السيرفر
ssh -i "path\to\key.pem" ubuntu@YOUR_EC2_IP
mkdir cyber_mirage
tar -xzf cyber_mirage.tar.gz -C cyber_mirage/
cd cyber_mirage
```

---

## المرحلة 5: إعداد Environment Variables

```bash
# انسخ ملف البيئة
cp .env.example .env

# عدّل الملف
nano .env
```

**غيّر هذه القيم:**
```bash
POSTGRES_PASSWORD=ضع_باسورد_قوي_هنا_123!
REDIS_PASSWORD=ضع_باسورد_قوي_للريدس_456!
GRAFANA_PASSWORD=ضع_باسورد_لجرافانا_789!

# اختياري - API Keys للتحليل
VIRUSTOTAL_API_KEY=your_key
ABUSEIPDB_API_KEY=your_key
SHODAN_API_KEY=your_key
```

اضغط `Ctrl+X` ثم `Y` ثم `Enter` للحفظ

---

## المرحلة 6: تشغيل المشروع

```bash
# تشغيل Production Mode
docker-compose -f docker-compose.production.yml up -d

# شوف الـ logs
docker-compose -f docker-compose.production.yml logs -f

# لو كل شيء شغال، اضغط Ctrl+C للخروج من الـ logs
```

---

## المرحلة 7: الاختبار

### 1. افتح Dashboard:
```
http://YOUR_EC2_IP:8501
```

### 2. افتح Grafana:
```
http://YOUR_EC2_IP:3000
Username: admin
Password: اللي حطيته في GRAFANA_PASSWORD
```

### 3. اختبر الـ Honeypots:
```bash
# من جهازك
telnet YOUR_EC2_IP 2222  # SSH Honeypot
telnet YOUR_EC2_IP 2121  # FTP Honeypot
```

---

## المرحلة 8: المراقبة والصيانة

### التأكد من صحة السيرفر:
```bash
# حالة الـ containers
docker ps

# استهلاك الموارد
docker stats

# مساحة القرص
df -h

# الذاكرة
free -h
```

### للتوقف:
```bash
docker-compose -f docker-compose.production.yml down
```

### للتحديث:
```bash
git pull
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
```

---

## 🔒 نصائح الأمان

1. **غيّر Port 22 للـ SSH:**
```bash
sudo nano /etc/ssh/sshd_config
# غيّر Port 22 إلى رقم آخر مثل 2244
sudo systemctl restart sshd
```

2. **فعّل Firewall:**
```bash
sudo ufw allow 2244/tcp  # SSH port الجديد
sudo ufw allow 8501/tcp  # Dashboard
sudo ufw allow 3000/tcp  # Grafana
sudo ufw enable
```

3. **النسخ الاحتياطي التلقائي:**
```bash
# أضف لـ crontab
crontab -e

# اضف هذا السطر (نسخة احتياطية يومية)
0 2 * * * cd ~/cyber_mirage && tar -czf ~/backups/backup_$(date +\%Y\%m\%d).tar.gz data/
```

---

## 📞 إذا واجهت مشاكل

### السيرفر بطيء:
```bash
# شوف الـ container اللي بياكل موارد
docker stats

# أعد تشغيل container معين
docker-compose -f docker-compose.production.yml restart SERVICE_NAME
```

### مافيش اتصال بالـ Dashboard:
```bash
# تأكد من Security Group في AWS
# تأكد من Container شغال
docker ps | grep streamlit
```

### مشاكل الـ Database:
```bash
# شوف logs الـ postgres
docker-compose -f docker-compose.production.yml logs postgres
```

---

## ✅ Checklist النهائي

- [ ] EC2 Instance شغال
- [ ] Security Group مضبوط صح
- [ ] Docker مثبت
- [ ] المشروع متحمّل
- [ ] Environment variables مضبوطة
- [ ] Containers شغالة (docker ps)
- [ ] Dashboard يفتح على البورت 8501
- [ ] Grafana يفتح على البورت 3000
- [ ] Honeypots تستقبل connections
- [ ] النسخ الاحتياطي مفعّل

---

## 🎯 الخطوة القادمة

أنت الآن جاهز للإنتاج! المشروع سيبدأ في جمع البيانات من المهاجمين تلقائياً.

**للمراقبة المستمرة:**
- راقب Dashboard يومياً
- تحقق من Grafana للإحصائيات
- راجع logs الـ honeypots

**التكلفة المتوقعة:**
- t2.large: ~$68/شهر
- Storage 50GB: ~$5/شهر
- **الإجمالي: ~$73/شهر**

🎉 مبروك! نظامك الآن في الإنتاج!
