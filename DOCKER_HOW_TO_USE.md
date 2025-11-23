# 🐳 دليل تشغيل Docker - خطوة بخطوة

## 📊 الوضع الحالي

Docker **شغّال بنجاح** 100%! ✅

### الخدمات اللي شغالة دلوقتي:

```
✓ Redis
✓ PostgreSQL  
✓ Prometheus
✓ Grafana
✓ Node Exporter
```

---

## 🎯 كيفية التشغيل

### **الطريقة الأولى: تشغيل كل الخدمات معاً**

افتح PowerShell وشغل:

```powershell
docker-compose up -d redis postgres prometheus grafana node-exporter
```

**النتيجة:**
```
[+] Running 5/5
 ✔ cyber_mirage_redis
 ✔ cyber_mirage_postgres
 ✔ cyber_mirage_prometheus
 ✔ cyber_mirage_grafana
 ✔ cyber_mirage_node_exporter
```

---

### **الطريقة الثانية: تشغيل خدمة واحدة**

```powershell
# شغل Redis فقط
docker-compose up -d redis

# شغل PostgreSQL فقط
docker-compose up -d postgres

# شغل Grafana فقط
docker-compose up -d grafana
```

---

### **الطريقة الثالثة: تشغيل بدون `-d` (نشوف السجلات)**

```powershell
# شغل وشوف السجلات مباشرة
docker-compose up redis postgres prometheus grafana node-exporter
```

---

## 🛑 كيفية الإيقاف

### إيقاف جميع الخدمات:

```powershell
docker-compose down
```

### إيقاف مع حذف البيانات:

```powershell
docker-compose down -v
```

### إيقاف خدمة واحدة:

```powershell
docker-compose stop redis
docker-compose stop postgres
```

---

## 🔄 إعادة التشغيل

```powershell
# إعادة تشغيل كل الخدمات
docker-compose restart

# إعادة تشغيل خدمة واحدة
docker-compose restart redis
docker-compose restart postgres
```

---

## 📊 مراقبة الحالة

### عرض الحاويات الشغالة:

```powershell
docker ps
```

**النتيجة:**
```
NAMES                        STATUS
cyber_mirage_redis           Up 3 hours
cyber_mirage_postgres        Up 3 hours
cyber_mirage_prometheus      Up 3 hours
cyber_mirage_grafana         Up 3 hours
cyber_mirage_node_exporter   Up 3 hours
```

### عرض جميع الحاويات (شغالة وموقوفة):

```powershell
docker ps -a
```

### عرض استهلاك الموارد:

```powershell
docker stats
```

---

## 📋 عرض السجلات

### عرض السجلات في الوقت الفعلي:

```powershell
# جميع السجلات
docker-compose logs -f

# سجلات Redis فقط
docker-compose logs -f redis

# سجلات PostgreSQL فقط
docker-compose logs -f postgres

# آخر 50 سطر
docker-compose logs --tail=50
```

---

## 🔍 اختبار الخدمات

### اختبار Redis:

```powershell
docker exec -it cyber_mirage_redis redis-cli ping
```

**النتيجة المتوقعة:**
```
PONG
```

### اختبار PostgreSQL:

```powershell
docker exec -it cyber_mirage_postgres pg_isready -U honeypot
```

**النتيجة المتوقعة:**
```
accepting connections
```

### الاتصال بـ PostgreSQL:

```powershell
docker exec -it cyber_mirage_postgres psql -U honeypot -d cyber_mirage
```

---

## 🌐 الوصول إلى الخدمات

| الخدمة | الرابط | الملاحظة |
|--------|--------|---------|
| Grafana | http://localhost:3000 | username: admin, password: admin |
| Prometheus | http://localhost:9090 | بدون تسجيل دخول |
| Redis | localhost:6379 | بدون واجهة ويب |
| PostgreSQL | localhost:5432 | بدون واجهة ويب |

---

## 🚨 استكشاف الأخطاء

### Redis لا يعمل:

```powershell
# شوف السجلات
docker-compose logs redis

# أعد التشغيل
docker-compose restart redis

# احذف وأعد التشغيل
docker-compose down -v
docker-compose up -d redis
```

### PostgreSQL لا يعمل:

```powershell
# شوف السجلات
docker-compose logs postgres

# تحقق من الاتصال
docker exec -it cyber_mirage_postgres pg_isready -U honeypot

# أعد التشغيل
docker-compose restart postgres
```

### Grafana لا يفتح:

```powershell
# تحقق من أن الخدمة شغالة
docker ps | findstr grafana

# شوف السجلات
docker-compose logs grafana

# أعد التشغيل
docker-compose restart grafana
```

---

## 💾 النسخ الاحتياطي

### نسخ احتياطي من قاعدة البيانات:

```powershell
docker exec cyber_mirage_postgres pg_dump -U honeypot cyber_mirage > backup.sql
```

### استرجاع البيانات:

```powershell
docker exec -i cyber_mirage_postgres psql -U honeypot cyber_mirage < backup.sql
```

---

## 🔧 الأوامر المتقدمة

### دخول حاوية مباشرة:

```powershell
# دخول Redis
docker exec -it cyber_mirage_redis bash

# دخول PostgreSQL
docker exec -it cyber_mirage_postgres bash
```

### حذف صورة Docker:

```powershell
docker image rm cyber-mirage:latest
```

### حذف حاوية:

```powershell
docker rm cyber_mirage_redis
```

### بناء صورة جديدة:

```powershell
docker-compose build --no-cache
```

---

## 📈 أداء Docker

### مراقبة استهلاك الموارد في الوقت الفعلي:

```powershell
docker stats --no-stream
```

### عرض حجم الحاويات:

```powershell
docker ps -s
```

---

## 🎯 أوامر سريعة

```powershell
# تشغيل سريع
docker-compose up -d redis postgres prometheus grafana node-exporter

# إيقاف سريع
docker-compose down

# حالة سريعة
docker ps

# سجلات سريعة
docker-compose logs -f

# تنظيف سريع
docker system prune
```

---

## ✨ نصائح مهمة

1. **استخدم `-d`** للتشغيل في الخلفية
2. **استخدم `-f`** مع logs لمتابعة السجلات الحية
3. **احفظ البيانات دائماً** قبل الحذف
4. **راقب استهلاك الموارد** بـ `docker stats`

---

## 🎉 ملخص الأوامر الأساسية

| الغرض | الأمر |
|-------|-------|
| تشغيل | `docker-compose up -d` |
| إيقاف | `docker-compose down` |
| حالة | `docker ps` |
| سجلات | `docker-compose logs -f` |
| إعادة تشغيل | `docker-compose restart` |
| اختبار | `docker exec -it [container] [command]` |

---

## 📞 مساعدة إضافية

للمزيد من المعلومات:
```powershell
docker-compose --help
docker --help
```

**استمتع بـ Docker! 🐳**
