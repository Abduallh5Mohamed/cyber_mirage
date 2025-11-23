# ⚡ AWS Quick Commands - أوامر سريعة

## 🎯 الخطوات المختصرة

### 1️⃣ سجّل حساب AWS
https://aws.amazon.com/free/

### 2️⃣ أضف SSH Key في AWS Console
```
EC2 → Key Pairs → Import key pair
Name: cyber-mirage-key
Public key: (الصق المفتاح من C:\Users\abdua\.ssh\cyber_mirage.pub)
```

### 3️⃣ أنشئ Security Group
```
EC2 → Security Groups → Create security group
Name: cyber-mirage-sg

Inbound Rules:
- SSH (22) من 0.0.0.0/0
- Custom TCP (2222) من 0.0.0.0/0
- Custom TCP (8080) من 0.0.0.0/0
- Custom TCP (2121) من 0.0.0.0/0
- Custom TCP (3306) من 0.0.0.0/0
- Custom TCP (8501) من 0.0.0.0/0
```

### 4️⃣ أطلق EC2 Instance
```
EC2 → Launch Instance
Name: cyber-mirage
AMI: Ubuntu 22.04 LTS (Free tier eligible)
Instance type: t2.micro
Key pair: cyber-mirage-key
Security group: cyber-mirage-sg
Storage: 30 GB gp3
→ Launch
```

### 5️⃣ من جهازك - ارفع الملفات
```powershell
# احصل على IP من AWS Console
$IP = "YOUR_EC2_PUBLIC_IP"

# ارفع ZIP
scp -i C:\Users\abdua\.ssh\cyber_mirage A:\cyber_mirage\cyber_mirage_deploy.zip ubuntu@${IP}:/home/ubuntu/

# اتصل بالسيرفر
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@${IP}
```

### 6️⃣ على السيرفر - تثبيت وتشغيل
```bash
# فك الضغط
sudo apt update
sudo apt install -y unzip
unzip cyber_mirage_deploy.zip -d /opt/cyber_mirage
cd /opt/cyber_mirage

# شغّل السكريبت التلقائي
chmod +x deploy_auto.sh
sudo bash deploy_auto.sh

# انتظر 5-10 دقائق...

# تحقق من الخدمات
docker compose -f docker-compose.production.yml ps

# شاهد اللوجات
docker compose -f docker-compose.production.yml logs -f
```

### 7️⃣ افتح Dashboard
```
http://YOUR_EC2_PUBLIC_IP:8501
```

### 8️⃣ اختبر الهجوم
```powershell
# من جهازك
nmap -sV YOUR_EC2_PUBLIC_IP
ssh root@YOUR_EC2_PUBLIC_IP -p 2222
curl http://YOUR_EC2_PUBLIC_IP:8080
```

---

## 🔑 معلومات مهمة

**SSH للإدارة:**
```bash
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@YOUR_EC2_PUBLIC_IP
```

**كلمات السر (على السيرفر):**
```bash
cat /root/cyber_mirage_credentials.txt
```

**أوامر Docker:**
```bash
cd /opt/cyber_mirage

# حالة الخدمات
docker compose -f docker-compose.production.yml ps

# إعادة تشغيل
docker compose -f docker-compose.production.yml restart

# إيقاف
docker compose -f docker-compose.production.yml down

# تشغيل
docker compose -f docker-compose.production.yml up -d

# اللوجات
docker compose -f docker-compose.production.yml logs -f honeypots

# استخدام الموارد
docker stats
```

---

## 💰 مراقبة التكاليف

```
AWS Console → Billing → Free Tier

تحقق من:
- EC2: 750 ساعة/شهر (متبقي)
- Storage: 30 GB (متبقي)
- Data Transfer: 15 GB out/شهر (متبقي)
```

**ضع Alert:**
```
Billing → Budgets → Create budget
Budget amount: $5
Alert at: 80%
Email: abduallhshadow@gmail.com
```

---

## 🚨 حل سريع للمشاكل

**Dashboard لا يفتح:**
```bash
# تحقق من Security Group يسمح بـ 8501
# تحقق من الخدمة
docker compose logs dashboard
docker compose restart dashboard
```

**SSH لا يعمل:**
```bash
# تأكد username = ubuntu (ليس root)
# تأكد Security Group يسمح بـ 22
# تأكد من المفتاح الصحيح
```

**Out of Memory:**
```bash
# 1GB RAM قليل - قلل الخدمات أو upgrade
# لكن upgrade = ليس مجاني!
```

---

## ✅ Done!

Dashboard: `http://YOUR_EC2_PUBLIC_IP:8501`  
Honeypots: Ports 2222, 8080, 2121, 3306  
SSH Admin: Port 22 (ubuntu user)

🎉 **استمتع بالهجمات!**
