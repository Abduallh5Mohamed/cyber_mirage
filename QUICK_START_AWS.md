# 🚀 Cyber Mirage - Quick Start Guide (AWS)

## أنت الآن في هذه المرحلة:
✅ EC2 Instance شغال ومستني التثبيت

---

## الطريقة 1️⃣: باستخدام السكريبت الآلي (الأسهل! 🎯)

### الخطوات:

#### 1. **احصل على المعلومات من AWS Console:**

في صفحة EC2 Instances، اضغط على Instance "Cyber mirage" وشوف:
- **Public IPv4 address** (مثال: 13.60.19.225)
- **Security group ID** (مثال: sg-0abc123def)

#### 2. **عدّل Security Group:**

في AWS Console:
1. اذهب لـ **Security Groups** من القائمة اليسرى
2. اختر الـ Security Group بتاع الـ Instance
3. اضغط **"Edit inbound rules"**
4. اضغط **"Add rule"** لكل port من الملف `aws_security_rules.txt`
5. أو استخدم السكريبت:

```powershell
# لو عندك AWS CLI
.\fix_security_group_aws.ps1 -SecurityGroupId "sg-xxxxx"
```

#### 3. **حمّل الـ Key File:**

لو نسيت تحمّل الـ key:
- مش هتقدر تحمله تاني من AWS
- هتحتاج تعمل Key Pair جديد وتربطه بالـ Instance

لو عندك الـ key، احفظه في:
```
C:\Keys\cyber-mirage-key.pem
```

#### 4. **شغّل سكريبت الـ Deployment:**

افتح PowerShell **في مجلد المشروع** وشغّل:

```powershell
cd A:\cyber_mirage

# شغّل السكريبت
.\deploy_to_aws.ps1 -EC2_IP "YOUR_EC2_IP" -KeyPath "C:\Keys\cyber-mirage-key.pem"
```

**مثال:**
```powershell
.\deploy_to_aws.ps1 -EC2_IP "13.60.19.225" -KeyPath "C:\Keys\cyber-mirage-key.pem"
```

#### 5. **انتظر 10-15 دقيقة**

السكريبت هيعمل:
- ✅ اختبار الاتصال بالسيرفر
- ✅ ضغط المشروع
- ✅ رفع الملفات
- ✅ تثبيت Docker و Docker Compose
- ✅ إعداد Environment Variables
- ✅ تشغيل كل الـ Services
- ✅ عرض معلومات الدخول

#### 6. **افتح Dashboard!**

بعد ما السكريبت يخلص:
```
http://YOUR_EC2_IP:8501
```

---

## الطريقة 2️⃣: يدوياً خطوة بخطوة

### 1. الاتصال بالسيرفر:

```powershell
# ضبط صلاحيات الـ key
icacls "C:\Keys\cyber-mirage-key.pem" /inheritance:r
icacls "C:\Keys\cyber-mirage-key.pem" /grant:r "%username%:R"

# الاتصال
ssh -i "C:\Keys\cyber-mirage-key.pem" ubuntu@YOUR_EC2_IP
```

### 2. تثبيت Docker:

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

### 3. رفع المشروع:

**من جهازك (PowerShell):**
```powershell
cd A:\cyber_mirage

# ضغط المشروع
tar -czf cyber_mirage.tar.gz --exclude=venv --exclude=__pycache__ --exclude=.git --exclude="*.log" .

# رفع للسيرفر
scp -i "C:\Keys\cyber-mirage-key.pem" cyber_mirage.tar.gz ubuntu@YOUR_EC2_IP:~/
```

**على السيرفر:**
```bash
# فك الضغط
mkdir -p ~/cyber_mirage
tar -xzf cyber_mirage.tar.gz -C ~/cyber_mirage/
cd ~/cyber_mirage
```

### 4. إعداد Environment:

```bash
# نسخ ملف البيئة
cp .env.example .env

# تعديله
nano .env
```

**غيّر هذه القيم:**
```bash
POSTGRES_PASSWORD=ضع_باسورد_قوي_123!
REDIS_PASSWORD=ضع_باسورد_قوي_456!
GRAFANA_PASSWORD=ضع_باسورد_قوي_789!
ENVIRONMENT=production
```

اضغط `Ctrl+X`، ثم `Y`، ثم `Enter`

### 5. تشغيل المشروع:

```bash
# تشغيل Production Mode
docker-compose -f docker-compose.production.yml up -d

# شوف الـ logs
docker-compose -f docker-compose.production.yml logs -f
```

### 6. اختبار:

افتح في المتصفح:
```
http://YOUR_EC2_IP:8501    (Dashboard)
http://YOUR_EC2_IP:3000    (Grafana)
```

---

## 🔍 التحقق من الـ Security Group

**في AWS Console:**
1. EC2 → Security Groups
2. اختر السecurity group بتاعك
3. تأكد من وجود هذه الـ Inbound Rules:

| Port | Source | الوصف |
|------|--------|-------|
| 22 | My IP | SSH |
| 8501 | 0.0.0.0/0 | Dashboard |
| 3000 | 0.0.0.0/0 | Grafana |
| 2222 | 0.0.0.0/0 | SSH Honeypot |
| 2121 | 0.0.0.0/0 | FTP Honeypot |
| 445 | 0.0.0.0/0 | SMB Honeypot |
| 502 | 0.0.0.0/0 | Modbus Honeypot |
| 3307 | 0.0.0.0/0 | MySQL Honeypot |
| 5434 | 0.0.0.0/0 | PostgreSQL Honeypot |
| 8080 | 0.0.0.0/0 | HTTP Honeypot |
| 8443 | 0.0.0.0/0 | HTTPS Honeypot |

---

## 🆘 حل المشاكل

### المشكلة: "Permission denied" عند SSH

**الحل:**
```powershell
icacls "C:\Keys\cyber-mirage-key.pem" /inheritance:r
icacls "C:\Keys\cyber-mirage-key.pem" /grant:r "%username%:R"
```

### المشكلة: "Connection refused"

**الحل:**
1. تأكد إن Instance شغال (Running)
2. تأكد إن Security Group فيه Port 22 من My IP
3. تأكد إن الـ IP صحيح

### المشكلة: Dashboard مش بيفتح

**الحل:**
1. تأكد إن Security Group فيه Port 8501
2. تأكد إن الـ Container شغال:
```bash
docker ps | grep streamlit
```
3. شوف الـ logs:
```bash
docker-compose -f docker-compose.production.yml logs dashboard
```

### المشكلة: Docker out of memory

**الحل:**
```bash
# زود Instance size لـ t2.xlarge أو أكبر
# أو قلل عدد الـ services
docker-compose -f docker-compose.yml up -d  # بدل production
```

---

## 📊 بعد التشغيل

### للمراقبة:
```bash
# حالة الـ containers
docker ps

# استهلاك الموارد
docker stats

# الـ logs
docker-compose -f docker-compose.production.yml logs -f SERVICE_NAME
```

### للصيانة:
```bash
# إعادة تشغيل
docker-compose -f docker-compose.production.yml restart

# إيقاف مؤقت
docker-compose -f docker-compose.production.yml stop

# إيقاف وحذف
docker-compose -f docker-compose.production.yml down
```

### للتحديث:
```bash
git pull
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
```

---

## 💰 التكلفة المتوقعة

**m7i-flex.large (الحالي):**
- ~$80-100/شهر

**البدائل الأرخص:**
- **t2.large**: ~$68/شهر (موصى به)
- **t3.large**: ~$60/شهr (أفضل أداء للسعر)
- **t2.medium**: ~$34/شهر (للتجربة فقط)

**Storage (50GB gp3):** ~$5/شهر

---

## ✅ Checklist النهائي

قبل ما تقول "خلصت":

- [ ] EC2 Instance شغال (Running)
- [ ] Security Group مضبوط بكل الـ Ports
- [ ] SSH يشتغل من جهازك
- [ ] Docker و Docker Compose مثبتين
- [ ] المشروع متحمّل ومفكوك
- [ ] .env file مضبوط
- [ ] Containers شغالة (docker ps)
- [ ] Dashboard يفتح (http://IP:8501)
- [ ] Grafana يفتح (http://IP:3000)
- [ ] Honeypots تستقبل اتصالات

---

## 🎯 المفروض تشوف إيه؟

بعد ما كل شيء يشتغل:

1. **Dashboard (Port 8501):**
   - واجهة Streamlit
   - إحصائيات الهجمات
   - التنبيهات الحية

2. **Grafana (Port 3000):**
   - Username: `admin`
   - Password: اللي حطيته في `GRAFANA_PASSWORD`
   - Dashboards للمراقبة

3. **Honeypots:**
   - SSH (2222), FTP (2121), SMB (445), etc.
   - لازم تستقبل اتصالات من المهاجمين

---

## 🎉 خلصت؟

لو كل شيء شغال:
- Dashboard مفتوح
- Grafana شغال
- Honeypots نشطة

**مبروك! نظامك الآن في الإنتاج! 🎊**

---

## 📞 محتاج مساعدة؟

شوف:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - حل المشاكل الشائعة
- [DEPLOYMENT.md](DEPLOYMENT.md) - دليل التفصيلي الكامل
- [SERVER_STATUS.md](SERVER_STATUS.md) - حالة السيرفر والمراقبة

أو اسأل وأنا هساعدك! 😊
