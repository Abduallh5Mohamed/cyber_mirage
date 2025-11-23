# 📺 شرح مصور - كيفية تشغيل Docker

## 🎬 الفيديو النصي

---

## المرحلة 1️⃣: الإعداد الأولي

### الخطوة 1: افتح PowerShell

```
❌ لا تستخدم Command Prompt
✅ استخدم PowerShell

الطريقة:
- اضغط: Win + X
- اختر: PowerShell أو Windows PowerShell
```

### الخطوة 2: انتقل للمجلد

```powershell
cd A:\cyber_mirage
```

**النتيجة:**
```
PS A:\cyber_mirage>
```

---

## المرحلة 2️⃣: التشغيل

### الخطوة 3: شغل جميع الخدمات

```powershell
docker-compose up -d redis postgres prometheus grafana node-exporter
```

### ستشوف هذا:

```
time="2025-10-27T21:04:58+03:00" level=warning msg="..."

[+] Running 5/5
 ✔ cyber_mirage_redis           Started
 ✔ cyber_mirage_postgres        Started
 ✔ cyber_mirage_prometheus      Started
 ✔ cyber_mirage_grafana         Started
 ✔ cyber_mirage_node_exporter   Started
```

✅ **كل شيء شغّال!**

---

## المرحلة 3️⃣: التحقق

### الخطوة 4: تأكد من التشغيل

```powershell
docker ps
```

### ستشوف هذا:

```
NAMES                        STATUS
cyber_mirage_redis           Up 3 seconds (healthy)
cyber_mirage_postgres        Up 3 seconds (healthy)
cyber_mirage_prometheus      Up 3 seconds
cyber_mirage_grafana         Up 3 seconds
cyber_mirage_node_exporter   Up 3 seconds
```

✅ **جميع الخدمات شغّالة!**

---

## المرحلة 4️⃣: الدخول للخدمات

### افتح الروابط دي في المتصفح:

#### 1. Grafana (لوحة التحكم)
```
http://localhost:3000

Username: admin
Password: admin
```

#### 2. Prometheus (مراقبة الأداء)
```
http://localhost:9090
```

#### 3. Redis (يعمل في الخلفية)
```
localhost:6379
```

#### 4. PostgreSQL (يعمل في الخلفية)
```
localhost:5432
```

---

## المرحلة 5️⃣: مراقبة السجلات

### لو تبي شوف اللي حصل:

```powershell
# عرض جميع السجلات
docker-compose logs -f

# عرض سجلات Redis فقط
docker-compose logs -f redis

# عرض آخر 50 سطر
docker-compose logs --tail=50
```

### مثال:

```powershell
docker-compose logs -f postgres
```

**ستشوف:**
```
cyber_mirage_postgres | ...server started
cyber_mirage_postgres | ...ready to accept connections
```

---

## المرحلة 6️⃣: الإيقاف

### لو تبي توقف الخدمات:

#### إيقاف بسيط:
```powershell
docker-compose down
```

#### إيقاف مع حذف البيانات:
```powershell
docker-compose down -v
```

---

## 🎯 سيناريوهات عملية

### السيناريو 1: تشغيل Redis فقط

```powershell
# التشغيل
docker-compose up -d redis

# التحقق
docker exec -it cyber_mirage_redis redis-cli ping

# النتيجة المتوقعة
PONG
```

---

### السيناريو 2: فحص قاعدة البيانات

```powershell
# الدخول إلى PostgreSQL
docker exec -it cyber_mirage_postgres psql -U honeypot -d cyber_mirage

# عرض الجداول
\dt

# عرض عدد الصفوف
SELECT COUNT(*) FROM attacks;

# الخروج
\q
```

---

### السيناريو 3: مراقبة استهلاك الموارد

```powershell
# عرض في الوقت الفعلي
docker stats

# أو بدون تحديث
docker stats --no-stream
```

### ستشوف:

```
CONTAINER ID   NAME                       CPU %   MEM USAGE
abc123...      cyber_mirage_redis         0.1%    45.2MiB
def456...      cyber_mirage_postgres      0.2%    120.5MiB
ghi789...      cyber_mirage_grafana       0.3%    98.7MiB
```

---

### السيناريو 4: إعادة تشغيل خدمة

```powershell
# إعادة تشغيل Grafana
docker-compose restart grafana

# ستشوف
cyber_mirage_grafana  Stopping
cyber_mirage_grafana  Stopped
cyber_mirage_grafana  Starting
cyber_mirage_grafana  Started
```

---

## 🚨 ماذا تفعل إذا حصلت مشكلة؟

### المشكلة: الخدمات ما طلعت

```powershell
# اشوف السجلات
docker-compose logs

# إذا فيه error:
docker-compose down -v
docker-compose up -d
```

---

### المشكلة: Port مشغول

```powershell
# لو الـ port 3000 مشغول:
# اقتل البروسيس
Get-Process | Where-Object {$_.Port -eq 3000}

# أو غيّر الـ port في docker-compose.yml
```

---

### المشكلة: بطيء جداً

```powershell
# تأكد من توفر الموارد
docker stats

# احذف البيانات القديمة
docker system prune

# أعد التشغيل
docker-compose down -v
docker-compose up -d
```

---

## 📝 أوامر سريعة للنسخ والعجن

```powershell
# نسخ احتياطي
docker exec cyber_mirage_postgres pg_dump -U honeypot cyber_mirage > backup.sql

# استرجاع
docker exec -i cyber_mirage_postgres psql -U honeypot cyber_mirage < backup.sql

# حذف كل شيء
docker system prune -a

# معلومات النظام
docker info
```

---

## ✅ الخطوات الـ 3 الأساسية فقط

إذا تبي شيء بسيط جداً:

### 1. شغّل
```powershell
docker-compose up -d redis postgres prometheus grafana node-exporter
```

### 2. تحقق
```powershell
docker ps
```

### 3. أوقف
```powershell
docker-compose down
```

**بس! 🎉**

---

## 📞 معلومات مفيدة

### Docker سهل إذا فهمت:

- **Container** = برنامج مستقل
- **Image** = صورة البرنامج
- **Volume** = مجلد البيانات
- **Network** = شبكة الاتصال

### الفكرة البسيطة:

Docker يُشغّل برامج **منعزلة** عن جهازك! 
- كل برنامج بيئة مستقلة
- ما يؤثر على الأخرى
- سهل التثبيت والحذف

---

## 🎓 تعلم أكثر

```powershell
# اقرأ الشرح الكامل
get-content DOCKER_HOW_TO_USE.md

# أو افتح الملفات التوثيقية
- RUN_PRODUCTION.md
- SETUP_COMPLETE.md
- DOCKER_MANUAL_SETUP.md
```

---

## 🎉 انتهينا!

أنت الآن تعرف:
✅ كيفية تشغيل Docker
✅ كيفية التحقق من الخدمات
✅ كيفية مراقبة السجلات
✅ كيفية إيقاف الخدمات
✅ كيفية حل المشاكل البسيطة

**استمتع! 🐳**
