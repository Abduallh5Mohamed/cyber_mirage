# 🚀 Docker Commands - جميع الأوامر في مكان واحد

## 📋 الأوامر الأساسية

### تشغيل

| الأمر | الشرح |
|------|-------|
| `docker-compose up -d redis postgres prometheus grafana node-exporter` | شغّل جميع الخدمات |
| `docker-compose up -d redis` | شغّل Redis فقط |
| `docker-compose up -d postgres` | شغّل PostgreSQL فقط |
| `docker-compose up -d prometheus grafana` | شغّل Prometheus و Grafana |
| `docker-compose up` | شغّل بدون `-d` لمتابعة السجلات |

### إيقاف

| الأمر | الشرح |
|------|-------|
| `docker-compose down` | أوقف جميع الخدمات |
| `docker-compose stop` | أوقف جميع الخدمات (بدون حذف) |
| `docker-compose stop redis` | أوقف Redis فقط |
| `docker-compose down -v` | أوقف وحذف البيانات |

### مراقبة

| الأمر | الشرح |
|------|-------|
| `docker ps` | عرض الحاويات الشغالة |
| `docker ps -a` | عرض جميع الحاويات |
| `docker stats` | مراقبة استهلاك الموارد |
| `docker-compose logs -f` | عرض السجلات الحية |
| `docker-compose logs -f redis` | سجلات Redis الحية |
| `docker-compose logs --tail=50` | آخر 50 سطر |

### إعادة تشغيل

| الأمر | الشرح |
|------|-------|
| `docker-compose restart` | أعد تشغيل جميع الخدمات |
| `docker-compose restart redis` | أعد تشغيل Redis فقط |
| `docker-compose up -d --force-recreate` | أعد الإنشاء والتشغيل |

---

## 🔧 الأوامر المتقدمة

### الدخول والاختبار

```powershell
# اختبار Redis
docker exec -it cyber_mirage_redis redis-cli ping

# اختبار PostgreSQL
docker exec -it cyber_mirage_postgres pg_isready -U honeypot

# الاتصال بـ PostgreSQL
docker exec -it cyber_mirage_postgres psql -U honeypot -d cyber_mirage

# الاتصال بـ Redis
docker exec -it cyber_mirage_redis redis-cli -a changeme
```

### عرض المعلومات

```powershell
# معلومات Docker
docker info

# معلومات الصور
docker images

# معلومات الأحجام
docker ps -s

# معلومات الشبكات
docker network ls

# معلومات الـ Volumes
docker volume ls
```

### البناء والحذف

```powershell
# بناء صورة جديدة
docker-compose build --no-cache

# بناء خدمة محددة
docker-compose build redis

# حذف صورة
docker image rm cyber-mirage:latest

# حذف حاوية
docker rm cyber_mirage_redis

# حذف كل شيء
docker system prune -a
```

---

## 💾 النسخ الاحتياطي والاستعادة

### PostgreSQL

```powershell
# نسخ احتياطي
docker exec cyber_mirage_postgres pg_dump -U honeypot cyber_mirage > backup.sql

# استعادة
docker exec -i cyber_mirage_postgres psql -U honeypot cyber_mirage < backup.sql

# نسخ ملف كامل
docker exec -t cyber_mirage_postgres pg_dump -U honeypot -Fc cyber_mirage > backup.dump
```

### Redis

```powershell
# حفظ البيانات
docker exec cyber_mirage_redis redis-cli -a changeme BGSAVE

# عرض البيانات
docker exec -it cyber_mirage_redis redis-cli -a changeme KEYS *

# حذف البيانات
docker exec cyber_mirage_redis redis-cli -a changeme FLUSHALL
```

### Grafana

```powershell
# نسخ احتياطي
docker cp cyber_mirage_grafana:/var/lib/grafana ./grafana_backup

# استعادة
docker cp ./grafana_backup cyber_mirage_grafana:/var/lib/grafana
```

---

## 🔍 البحث والفحص

### السجلات

```powershell
# جميع السجلات
docker-compose logs

# سجلات محددة
docker-compose logs redis postgres

# بدون الألوان
docker-compose logs --no-color

# متابعة الأخطاء
docker-compose logs | Select-String "error|ERROR|exception"
```

### الفحص

```powershell
# فحص صحة الحاوية
docker exec -it cyber_mirage_postgres pg_isready

# فحص الاتصال
docker exec cyber_mirage_postgres psql -U honeypot -d cyber_mirage -c "SELECT 1"

# فحص الإصدار
docker exec cyber_mirage_postgres postgres --version
```

---

## 🌐 إدارة الشبكة

```powershell
# عرض الشبكات
docker network ls

# معلومات شبكة
docker network inspect cyber_mirage_honeypot_network

# اتصال حاوية بشبكة
docker network connect cyber_mirage_honeypot_network container_name

# فصل حاوية عن شبكة
docker network disconnect cyber_mirage_honeypot_network container_name
```

---

## 📦 إدارة البيانات (Volumes)

```powershell
# عرض الـ Volumes
docker volume ls

# معلومات Volume
docker volume inspect cyber_mirage_redis_data

# حذف Volume
docker volume rm cyber_mirage_redis_data

# حذف جميع الـ Volumes غير المستخدمة
docker volume prune
```

---

## 🐛 استكشاف الأخطاء

### المشكلة: الخدمة تتوقف فوراً

```powershell
# 1. شوف السجلات
docker-compose logs redis

# 2. تحقق من الصورة
docker images | Select-String redis

# 3. احذف وأعد
docker-compose down -v
docker-compose up -d
```

### المشكلة: الـ Port مشغول

```powershell
# 1. شوف العملية
Get-Process | Where-Object {$_.Port -eq 3000}

# 2. أو استخدم
netstat -ano | findstr :3000

# 3. اقتل العملية
Stop-Process -Id [PID] -Force
```

### المشكلة: استهلاك عالي للموارد

```powershell
# 1. شوف الاستهلاك
docker stats

# 2. احذف الـ Cache
docker system prune

# 3. أعد التشغيل
docker-compose restart
```

---

## ⚙️ الأوامر المتقدمة جداً

### الدخول للـ Container

```powershell
# Shell العام
docker exec -it cyber_mirage_redis /bin/sh

# Bash
docker exec -it cyber_mirage_postgres /bin/bash

# تشغيل أمر
docker exec cyber_mirage_redis redis-cli INFO
```

### نقل الملفات

```powershell
# نسخ من Container
docker cp cyber_mirage_postgres:/var/lib/postgresql/data ./data

# نسخ إلى Container
docker cp ./data cyber_mirage_postgres:/var/lib/postgresql/
```

### معلومات النظام

```powershell
# عرض المعالج
docker exec cyber_mirage_postgres grep -c ^processor /proc/cpuinfo

# عرض الذاكرة
docker exec cyber_mirage_postgres free -h

# عرض استخدام القرص
docker exec cyber_mirage_postgres df -h
```

---

## 🎯 أوامر سريعة للنسخ والعجن

```powershell
# تشغيل سريع
docker-compose up -d redis postgres prometheus grafana node-exporter

# إيقاف سريع
docker-compose down

# حالة سريعة
docker ps

# سجلات سريعة
docker-compose logs -f

# نظيف سريع
docker system prune

# نسخة احتياطية سريعة
docker exec cyber_mirage_postgres pg_dump -U honeypot cyber_mirage > backup_$(Get-Date -Format "yyyy-MM-dd_HHmmss").sql
```

---

## 📊 ملخص الأوامر الأساسية

```powershell
# 1️⃣ الإعداد والتشغيل
cd A:\cyber_mirage
docker-compose up -d redis postgres prometheus grafana node-exporter

# 2️⃣ التحقق
docker ps

# 3️⃣ المراقبة
docker-compose logs -f

# 4️⃣ الإيقاف
docker-compose down
```

---

## 🎓 الموارد التعليمية

اقرأ هذه الملفات للمزيد:
- `DOCKER_HOW_TO_USE.md` - شرح مفصل
- `DOCKER_VIDEO_TUTORIAL.md` - شرح خطوة بخطوة
- `DOCKER_MANUAL_SETUP.md` - إعدادات يدوية
- `RUN_PRODUCTION.md` - تشغيل الإنتاج

---

## ✨ نصائح ذهبية

1. ✅ استخدم دائماً `docker-compose` بدل `docker`
2. ✅ احفظ البيانات قبل الحذف
3. ✅ راقب السجلات للأخطاء
4. ✅ استخدم `-f` للمتابعة الحية
5. ✅ استخدم `--tail=50` لآخر السجلات فقط

---

## 🚀 استمتع بـ Docker!

**تذكر:** Docker هو أداة قوية جداً! استخدمها بحذر!

```
docker ps  # ابدأ من هنا! 🐳
```
