# 🚀 Cyber Mirage - AWS Console Deployment Guide (خطوة بخطوة)

> **دليل شامل للنشر على AWS من خلال AWS Console بالترتيب**

---

## 📋 جدول المحتويات

1. [إنشاء EC2 Instance](#1-إنشاء-ec2-instance)
2. [إعداد Security Group](#2-إعداد-security-group)
3. [إنشاء Key Pair](#3-إنشاء-key-pair)
4. [الاتصال بالسيرفر](#4-الاتصال-بالسيرفر)
5. [تثبيت Docker](#5-تثبيت-docker)
6. [تحميل المشروع وتشغيله](#6-تحميل-المشروع-وتشغيله)
7. [تأمين السيرفر](#7-تأمين-السيرفر)
8. [إعداد النسخ الاحتياطي](#8-إعداد-النسخ-الاحتياطي)
9. [المراقبة والتنبيهات](#9-المراقبة-والتنبيهات)
10. [الاختبار النهائي](#10-الاختبار-النهائي)

---

## 1. إنشاء EC2 Instance

### الخطوة 1.1: الدخول لـ AWS Console
1. افتح [AWS Console](https://console.aws.amazon.com/)
2. سجل دخول بحسابك
3. من شريط البحث العلوي، اكتب "EC2" واضغط عليها

### الخطوة 1.2: إطلاق Instance جديد
1. اضغط على **"Launch Instance"** (الزر البرتقالي)
2. سيظهر لك صفحة إعدادات الـ Instance

### الخطوة 1.3: تسمية الـ Instance
```
Name: Cyber-Mirage-Production
```

### الخطوة 1.4: اختيار نظام التشغيل (AMI)
1. اختر **Ubuntu**
2. من القائمة المنسدلة اختر: **Ubuntu Server 22.04 LTS (HVM), SSD Volume Type**
3. تأكد أن Architecture هو **64-bit (x86)**

### الخطوة 1.5: اختيار نوع الـ Instance

| الخيار | المواصفات | السعر التقريبي/شهر | مناسب لـ |
|--------|-----------|-------------------|----------|
| `t2.medium` | 2 vCPU, 4GB RAM | ~$34 | تجربة خفيفة |
| `t2.large` ⭐ | 2 vCPU, 8GB RAM | ~$68 | **إنتاج متوسط** |
| `t2.xlarge` | 4 vCPU, 16GB RAM | ~$136 | إنتاج كبير |
| `t3.large` | 2 vCPU, 8GB RAM | ~$60 | بديل أفضل للـ t2 |

> **التوصية:** استخدم `t2.large` أو `t3.large` للإنتاج

### الخطوة 1.6: إنشاء Key Pair (مفتاح SSH)
1. في قسم **Key pair (login)** اضغط على **"Create new key pair"**
2. املأ:
   - **Key pair name:** `cyber-mirage-key`
   - **Key pair type:** RSA
   - **Private key file format:** `.pem` (لـ Linux/Mac) أو `.ppk` (لـ Windows PuTTY)
3. اضغط **"Create key pair"**
4. **مهم جداً:** احفظ الملف في مكان آمن! لن تستطيع تحميله مرة أخرى

### الخطوة 1.7: إعدادات الشبكة (Network settings)
1. اضغط على **"Edit"** في قسم Network settings
2. اترك VPC الافتراضي
3. اختر **Auto-assign public IP:** Enable
4. ستنشئ Security Group في الخطوة التالية

### الخطوة 1.8: إعدادات التخزين (Storage)
1. غيّر حجم الـ Root volume من 8 GB إلى **50 GB**
2. اختر **gp3** (أسرع من gp2)
3. Delete on termination: ✓ (حسب رغبتك)

### الخطوة 1.9: إطلاق الـ Instance
1. راجع الإعدادات
2. اضغط **"Launch Instance"**
3. انتظر حتى يصبح Instance State: **Running**

---

## 2. إعداد Security Group

### الخطوة 2.1: الوصول لـ Security Groups
1. من القائمة الجانبية اليسرى، اختر **"Security Groups"** تحت "Network & Security"
2. أو من صفحة الـ Instance، اضغط على اسم الـ Security Group

### الخطوة 2.2: تعديل Inbound Rules
اضغط على **"Edit inbound rules"** وأضف القواعد التالية:

#### 📊 جدول البورتات الكامل

| Port | Protocol | Source | الوصف |
|------|----------|--------|-------|
| 22 | TCP | My IP | SSH إدارة السيرفر |
| 80 | TCP | 0.0.0.0/0 | HTTP (اختياري) |
| 443 | TCP | 0.0.0.0/0 | HTTPS (اختياري) |
| 445 | TCP | 0.0.0.0/0 | 🍯 SMB Honeypot |
| 139 | TCP | 0.0.0.0/0 | 🍯 NetBIOS Honeypot |
| 502 | TCP | 0.0.0.0/0 | 🍯 Modbus/ICS Honeypot |
| 1025 | TCP | 0.0.0.0/0 | 🍯 Custom Honeypot |
| 2121 | TCP | 0.0.0.0/0 | 🍯 FTP Honeypot |
| 2222 | TCP | 0.0.0.0/0 | 🍯 SSH Honeypot |
| 3000 | TCP | My IP ⚠️ | Grafana Dashboard |
| 3307 | TCP | 0.0.0.0/0 | 🍯 MySQL Honeypot |
| 5434 | TCP | 0.0.0.0/0 | 🍯 PostgreSQL Honeypot |
| 8080 | TCP | 0.0.0.0/0 | 🍯 HTTP Honeypot |
| 8443 | TCP | 0.0.0.0/0 | 🍯 HTTPS Honeypot |
| 8501 | TCP | 0.0.0.0/0 | 📊 **Streamlit Dashboard** |
| 9090 | TCP | My IP ⚠️ | Prometheus (للإدارة فقط) |
| 9093 | TCP | My IP ⚠️ | Alertmanager |

> **🔒 ملاحظة أمنية:**
> - البورتات المميزة بـ 🍯 هي Honeypots - يجب فتحها للعالم لجذب الهجمات
> - البورتات المميزة بـ ⚠️ يجب تقييدها لـ IP محدد
> - **لا تفتح 6379 (Redis) أو 5433 (PostgreSQL) للعالم أبداً!**

### الخطوة 2.3: حفظ القواعد
اضغط **"Save rules"**

---

## 3. إنشاء Key Pair (إن لم تنشئه سابقاً)

### من EC2 Dashboard:
1. اذهب لـ **"Key Pairs"** في القائمة الجانبية
2. اضغط **"Create key pair"**
3. أدخل الاسم: `cyber-mirage-key`
4. اختر `.pem` للـ format
5. اضغط Create

---

## 4. الاتصال بالسيرفر

### الخطوة 4.1: الحصول على IP العام
1. اذهب لـ **Instances**
2. اضغط على الـ Instance
3. انسخ **Public IPv4 address** (مثال: `54.123.45.67`)

### الخطوة 4.2: الاتصال من Windows (PowerShell أو CMD)

```powershell
# انتقل لمجلد المفتاح
cd C:\Users\YourName\Downloads

# أو إذا كان المفتاح في مجلد المشروع
cd a:\cyber_mirage

# الاتصال بالسيرفر
ssh -i "cyber-mirage-key.pem" ubuntu@YOUR_EC2_IP
```

### الخطوة 4.3: الاتصال من Linux/Mac

```bash
# تغيير صلاحيات المفتاح
chmod 400 cyber-mirage-key.pem

# الاتصال
ssh -i "cyber-mirage-key.pem" ubuntu@YOUR_EC2_IP
```

### الخطوة 4.4: الاتصال من VS Code (Remote SSH)
1. ثبت extension: **Remote - SSH**
2. اضغط `Ctrl + Shift + P` واكتب "Remote-SSH: Connect to Host"
3. اختر "Add New SSH Host"
4. أدخل: `ssh -i "C:\path\to\cyber-mirage-key.pem" ubuntu@YOUR_EC2_IP`

---

## 5. تثبيت Docker

### الخطوة 5.1: تحديث النظام
```bash
sudo apt update && sudo apt upgrade -y
```

### الخطوة 5.2: تثبيت Docker
```bash
# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# إضافة المستخدم لمجموعة Docker
sudo usermod -aG docker ubuntu

# تفعيل المجموعة فوراً
newgrp docker
```

### الخطوة 5.3: تثبيت Docker Compose
```bash
# أحدث إصدار من Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# إعطاء صلاحية التنفيذ
sudo chmod +x /usr/local/bin/docker-compose

# التحقق
docker --version
docker-compose --version
```

---

## 6. تحميل المشروع وتشغيله

### الخطوة 6.1: استنساخ المشروع
```bash
git clone https://github.com/Abduallh5Mohamed/cyber_mirage.git
cd cyber_mirage
```

### الخطوة 6.2: إعداد ملف البيئة
```bash
# نسخ ملف البيئة النموذجي
cp .env.example .env.production

# تعديل المتغيرات
nano .env.production
```

### الخطوة 6.3: تعديل كلمات السر ⚠️ مهم جداً!

**في ملف `.env.production` غيّر:**

```bash
# ═══════════════════════════════════════════════════════════
# 🔐 كلمات السر - غيّرها جميعاً!
# ═══════════════════════════════════════════════════════════

# PostgreSQL - يجب أن تكون 16+ حرف مع رموز
POSTGRES_PASSWORD=YourVerySecureDBPassword2024@!#

# Redis
REDIS_PASSWORD=YourSecureRedisPassword456@!#

# Grafana
GRAFANA_PASSWORD=YourGrafanaAdminPass789@!#
GRAFANA_SECRET=RandomSecretKeyForGrafana2024

# ═══════════════════════════════════════════════════════════
# 🔑 API Keys (اختياري لكن مفيد جداً)
# ═══════════════════════════════════════════════════════════
VIRUSTOTAL_API_KEY=your_key_here
ABUSEIPDB_API_KEY=your_key_here
SHODAN_API_KEY=your_key_here
```

> **نصيحة لتوليد كلمات سر قوية:**
> ```bash
> # على السيرفر
> openssl rand -base64 32
> ```

### الخطوة 6.4: بناء وتشغيل الخدمات
```bash
# بناء جميع الـ Docker images
docker-compose -f docker-compose.production.yml build

# تشغيل جميع الخدمات
docker-compose -f docker-compose.production.yml up -d

# مشاهدة الـ logs
docker-compose -f docker-compose.production.yml logs -f
```

### الخطوة 6.5: التحقق من الخدمات
```bash
# عرض حالة جميع الـ containers
docker ps

# عرض بشكل منظم
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**الخدمات المتوقعة:**
```
NAMES                          STATUS           PORTS
cyber_mirage_dashboard         Up 2 minutes     0.0.0.0:8501->8501/tcp
cyber_mirage_honeypots         Up 2 minutes     Multiple ports...
cyber_mirage_ai                Up 2 minutes     0.0.0.0:8001->8001/tcp
cyber_mirage_postgres          Up 2 minutes     127.0.0.1:5433->5432/tcp
cyber_mirage_redis             Up 2 minutes     127.0.0.1:6379->6379/tcp
cyber_mirage_prometheus        Up 2 minutes     0.0.0.0:9090->9090/tcp
cyber_mirage_grafana           Up 2 minutes     0.0.0.0:3000->3000/tcp
```

---

## 7. تأمين السيرفر

### الخطوة 7.1: تعطيل دخول SSH بكلمة سر
```bash
# تعديل إعدادات SSH
sudo nano /etc/ssh/sshd_config

# غيّر هذه الخطوط:
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes

# إعادة تشغيل SSH
sudo systemctl restart sshd
```

### الخطوة 7.2: تثبيت Fail2Ban (حماية من هجمات Brute Force)
```bash
sudo apt install fail2ban -y

# إعداد الحماية
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### الخطوة 7.3: إعداد جدار الحماية UFW (اختياري)
```bash
# تفعيل UFW
sudo ufw allow 22/tcp       # SSH
sudo ufw allow 8501/tcp     # Dashboard
sudo ufw allow 2222/tcp     # SSH Honeypot
sudo ufw allow 2121/tcp     # FTP Honeypot
sudo ufw allow 8080/tcp     # HTTP Honeypot
sudo ufw allow 3000/tcp     # Grafana
# أضف البورتات الباقية حسب الحاجة

sudo ufw enable
```

---

## 8. إعداد النسخ الاحتياطي

### الخطوة 8.1: إنشاء سكريبت النسخ الاحتياطي
```bash
cat > /home/ubuntu/backup.sh << 'EOF'
#!/bin/bash
#═══════════════════════════════════════════════════════════
# Cyber Mirage - Automated Backup Script
#═══════════════════════════════════════════════════════════

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$BACKUP_DIR/backup_$DATE.log"

mkdir -p $BACKUP_DIR

echo "Starting backup at $(date)" >> $LOG_FILE

# 1. Backup PostgreSQL
echo "Backing up PostgreSQL..." >> $LOG_FILE
docker exec cyber_mirage_postgres pg_dump -U cybermirage cyber_mirage > $BACKUP_DIR/db_$DATE.sql 2>> $LOG_FILE

# Compress database backup
gzip $BACKUP_DIR/db_$DATE.sql

# 2. Backup important data volumes
echo "Backing up data volumes..." >> $LOG_FILE
sudo tar -czf $BACKUP_DIR/data_$DATE.tar.gz /home/ubuntu/cyber_mirage/data 2>> $LOG_FILE

# 3. Backup logs (last 7 days)
echo "Backing up logs..." >> $LOG_FILE
sudo tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /home/ubuntu/cyber_mirage/logs 2>> $LOG_FILE

# 4. Cleanup old backups (keep last 7 days)
echo "Cleaning old backups..." >> $LOG_FILE
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.log" -mtime +30 -delete

echo "Backup completed at $(date)" >> $LOG_FILE
echo "Backup size: $(du -sh $BACKUP_DIR | cut -f1)" >> $LOG_FILE
EOF

chmod +x /home/ubuntu/backup.sh
```

### الخطوة 8.2: إعداد النسخ الاحتياطي التلقائي (Cron)
```bash
# فتح crontab
crontab -e

# أضف هذا السطر (نسخ احتياطي يومياً الساعة 2 صباحاً)
0 2 * * * /home/ubuntu/backup.sh >> /home/ubuntu/backups/cron.log 2>&1
```

### الخطوة 8.3: نسخ الـ Backups لـ S3 (اختياري)
```bash
# تثبيت AWS CLI
sudo apt install awscli -y

# إعداد الـ credentials
aws configure
# أدخل Access Key و Secret Key

# إضافة للـ backup script:
aws s3 sync $BACKUP_DIR s3://your-bucket-name/cyber-mirage-backups/
```

---

## 9. المراقبة والتنبيهات

### الخطوة 9.1: الوصول للـ Dashboards

| الخدمة | الرابط | التسجيل |
|--------|--------|---------|
| **Streamlit Dashboard** | `http://YOUR_IP:8501` | لا يحتاج تسجيل |
| **Grafana** | `http://YOUR_IP:3000` | `admin` / (كلمة السر في .env) |
| **Prometheus** | `http://YOUR_IP:9090` | لا يحتاج تسجيل |

### الخطوة 9.2: إعداد Grafana Dashboards
1. افتح Grafana على `http://YOUR_IP:3000`
2. سجل دخول بـ `admin` وكلمة السر
3. اذهب لـ **Dashboards** → **Browse**
4. الـ Dashboards جاهزة ومُعدة مسبقاً

### الخطوة 9.3: إعداد تنبيهات Email (اختياري)
```bash
# تعديل إعدادات Alertmanager
nano docker/alertmanager/alertmanager.yml
```

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'your-email@gmail.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

receivers:
  - name: 'email-alerts'
    email_configs:
      - to: 'security-team@your-company.com'
        send_resolved: true

route:
  receiver: 'email-alerts'
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
```

---

## 10. الاختبار النهائي

### الخطوة 10.1: اختبار الـ Dashboard
```bash
# من جهازك المحلي
curl http://YOUR_EC2_IP:8501
```

أو افتح المتصفح على: `http://YOUR_EC2_IP:8501`

### الخطوة 10.2: اختبار الـ Honeypots
```bash
# اختبار SSH Honeypot
nc YOUR_EC2_IP 2222

# اختبار FTP Honeypot
nc YOUR_EC2_IP 2121

# اختبار HTTP Honeypot
curl http://YOUR_EC2_IP:8080/
```

### الخطوة 10.3: التحقق من تسجيل الهجمات
```bash
# على السيرفر
docker exec -it cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -c "SELECT COUNT(*) FROM attack_sessions;"
```

### الخطوة 10.4: فحص الـ Logs
```bash
# عرض logs الـ honeypots
docker logs cyber_mirage_honeypots --tail 50

# عرض logs الـ AI
docker logs cyber_mirage_ai --tail 50

# عرض logs الـ dashboard
docker logs cyber_mirage_dashboard --tail 50
```

---

## 📋 قائمة التحقق النهائية (Production Checklist)

| المهمة | الحالة |
|--------|--------|
| ✅ EC2 Instance شغال (Running) | [ ] |
| ✅ Security Group مُعدة بشكل صحيح | [ ] |
| ✅ SSH بمفتاح خاص فقط (بدون Password) | [ ] |
| ✅ جميع كلمات السر مُغيرة من الافتراضي | [ ] |
| ✅ Docker و Docker Compose مُثبتين | [ ] |
| ✅ جميع الـ Containers شغالة (docker ps) | [ ] |
| ✅ Dashboard يعمل على البورت 8501 | [ ] |
| ✅ Grafana يعمل على البورت 3000 | [ ] |
| ✅ Honeypots تستقبل الاتصالات | [ ] |
| ✅ قاعدة البيانات تسجل الهجمات | [ ] |
| ✅ النسخ الاحتياطي مُفعل (Cron) | [ ] |
| ✅ Fail2Ban مُفعل | [ ] |
| ✅ المراقبة تعمل (Prometheus/Grafana) | [ ] |

---

## 🔧 أوامر مفيدة للإدارة

### إدارة الخدمات
```bash
# إيقاف جميع الخدمات
docker-compose -f docker-compose.production.yml down

# إعادة تشغيل خدمة معينة
docker-compose -f docker-compose.production.yml restart honeypots

# إعادة بناء خدمة
docker-compose -f docker-compose.production.yml up -d --build dashboard

# عرض استهلاك الموارد
docker stats
```

### إدارة قاعدة البيانات
```bash
# الدخول لـ PostgreSQL
docker exec -it cyber_mirage_postgres psql -U cybermirage -d cyber_mirage

# الدخول لـ Redis
docker exec -it cyber_mirage_redis redis-cli -a YOUR_REDIS_PASSWORD
```

### فحص النظام
```bash
# استخدام الذاكرة والـ CPU
htop

# استخدام التخزين
df -h

# حجم مجلد المشروع
du -sh /home/ubuntu/cyber_mirage/
```

---

## 🆘 استكشاف الأخطاء

### Dashboard لا يعمل؟
```bash
docker logs cyber_mirage_dashboard
docker restart cyber_mirage_dashboard
```

### الـ Database لا يتصل؟
```bash
docker logs cyber_mirage_postgres
# تأكد من كلمة السر في .env.production
```

### الـ Honeypots لا تستقبل هجمات؟
```bash
# تأكد من فتح البورتات في Security Group
# اختبر الاتصال
nc -zv YOUR_IP 2222
nc -zv YOUR_IP 8080
```

---

## 📞 الدعم

إذا واجهت مشاكل:
1. راجع ملف `TROUBLESHOOTING.md`
2. افحص الـ logs: `docker-compose logs -f`
3. تأكد من Security Group
4. تأكد من كلمات السر في `.env.production`

---

**🎉 مبروك! Cyber Mirage الآن يعمل في Production على AWS!**

**Main Dashboard:** `http://YOUR_EC2_IP:8501`
