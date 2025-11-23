# 🐳 Docker Manual Setup - الإعداد اليدوي

## الوضع الحالي ✅

### الخدمات الشغالة (5 خدمات):

| الخدمة | الحالة | الرابط | الوصف |
|--------|--------|---------|-------|
| **Redis** | ✅ Healthy | داخلي | قاعدة بيانات سريعة |
| **PostgreSQL** | ✅ Healthy | داخلي | قاعدة بيانات رئيسية |
| **Prometheus** | ✅ Running | http://localhost:9090 | مراقبة الأداء |
| **Grafana** | ✅ Running | http://localhost:3000 | لوحة المراقبة |
| **Node Exporter** | ✅ Running | داخلي | مقاييس النظام |
| **Dashboard** | ✅ Running | http://localhost:8501 | لوحة التحكم الرئيسية |

---

## 🎯 كيفية الاستخدام

### 1️⃣ تشغيل كل الخدمات:

```powershell
# بدء جميع الخدمات
docker-compose up -d redis postgres prometheus grafana node-exporter

# التحقق من الحالة
docker ps
```

### 2️⃣ تشغيل Dashboard:

```powershell
# تشغيل لوحة التحكم
.\venv\Scripts\python.exe -m streamlit run src/dashboard/streamlit_app.py
```

### 3️⃣ إيقاف الخدمات:

```powershell
# إيقاف جميع الخدمات
docker-compose down

# إيقاف مع حذف البيانات
docker-compose down -v
```

---

## 📋 الأوامر المفيدة

### مراقبة الحالة:

```powershell
# عرض الحاويات الشغالة
docker ps

# عرض سجلات خدمة معينة
docker-compose logs -f redis
docker-compose logs -f postgres
docker-compose logs -f prometheus

# التحقق من استهلاك الموارد
docker stats
```

### إعادة التشغيل:

```powershell
# إعادة تشغيل خدمة واحدة
docker-compose restart redis

# إعادة تشغيل كل شيء
docker-compose restart
```

### حذف وإعادة البناء:

```powershell
# حذف كل شيء وإعادة البداية
docker-compose down -v
docker-compose up -d
```

---

## 🔧 استكشاف الأخطاء

### Redis لا يعمل:

```powershell
# التحقق من السجلات
docker-compose logs redis

# إعادة التشغيل
docker-compose restart redis
```

### PostgreSQL لا يعمل:

```powershell
# التحقق من الحالة الصحية
docker exec cyber_mirage_postgres pg_isready -U honeypot

# الاتصال بقاعدة البيانات
docker exec -it cyber_mirage_postgres psql -U honeypot -d cyber_mirage
```

### Prometheus لا يظهر بيانات:

```powershell
# التحقق من التكوين
docker exec cyber_mirage_prometheus cat /etc/prometheus/prometheus.yml

# إعادة تحميل التكوين
docker exec cyber_mirage_prometheus kill -HUP 1
```

---

## 🌐 الروابط المهمة

| الخدمة | الرابط | اسم المستخدم | كلمة المرور |
|--------|---------|--------------|-------------|
| **Dashboard** | http://localhost:8501 | - | - |
| **Grafana** | http://localhost:3000 | admin | admin |
| **Prometheus** | http://localhost:9090 | - | - |

---

## 📊 التحقق من البيانات

### Redis:

```powershell
# الاتصال بـ Redis
docker exec -it cyber_mirage_redis redis-cli -a changeme

# عرض جميع المفاتيح
KEYS *

# الخروج
exit
```

### PostgreSQL:

```powershell
# الاتصال بقاعدة البيانات
docker exec -it cyber_mirage_postgres psql -U honeypot -d cyber_mirage

# عرض الجداول
\dt

# عرض البيانات
SELECT * FROM attacks LIMIT 10;

# الخروج
\q
```

---

## 🎨 تخصيص Grafana

### 1. افتح Grafana:
- اذهب إلى http://localhost:3000
- اسم المستخدم: `admin`
- كلمة المرور: `admin`

### 2. إضافة Data Source:
- اذهب إلى **Configuration** → **Data Sources**
- اختر **Prometheus**
- URL: `http://prometheus:9090`
- احفظ وتحقق

### 3. استيراد Dashboard:
- اذهب إلى **Dashboards** → **Import**
- ارفع ملف من `docker/grafana/dashboards/`

---

## 🔒 الأمان

### تغيير كلمات المرور:

1. **تعديل ملف .env**:
```env
POSTGRES_PASSWORD=كلمة_مرور_قوية_هنا
REDIS_PASSWORD=كلمة_مرور_قوية_هنا
GRAFANA_PASSWORD=كلمة_مرور_قوية_هنا
```

2. **إعادة تشغيل الخدمات**:
```powershell
docker-compose down
docker-compose up -d
```

---

## 📈 مراقبة الأداء

### استخدام Prometheus:

1. افتح http://localhost:9090
2. اكتب استعلام مثل:
   - `container_memory_usage_bytes`
   - `container_cpu_usage_seconds_total`
3. اضغط **Execute** لعرض البيانات

### استخدام Grafana:

1. افتح http://localhost:3000
2. اذهب إلى **Dashboards** → **Browse**
3. اختر dashboard جاهز لعرض المقاييس

---

## ✨ نصائح مهمة

1. **احفظ البيانات دائماً**:
   - لا تستخدم `-v` مع `docker-compose down` إلا إذا كنت تريد حذف كل البيانات

2. **راقب الموارد**:
   - استخدم `docker stats` لمراقبة استهلاك CPU والذاكرة

3. **السجلات مهمة**:
   - استخدم `docker-compose logs` لمتابعة الأخطاء

4. **النسخ الاحتياطي**:
   ```powershell
   # نسخ احتياطي لقاعدة البيانات
   docker exec cyber_mirage_postgres pg_dump -U honeypot cyber_mirage > backup.sql
   ```

---

## 🎯 الخطوات التالية

الآن بعد أن أصبح Docker يعمل:

1. ✅ **اختبر Dashboard**: افتح http://localhost:8501
2. ✅ **راقب الأداء**: افتح http://localhost:9090
3. ✅ **اعرض الإحصائيات**: افتح http://localhost:3000
4. 📝 **تابع السجلات**: استخدم `docker-compose logs -f`

---

## 📞 المساعدة

إذا واجهت أي مشكلة:

1. **تحقق من السجلات**:
   ```powershell
   docker-compose logs -f [service_name]
   ```

2. **تحقق من الحالة**:
   ```powershell
   docker ps -a
   ```

3. **أعد التشغيل**:
   ```powershell
   docker-compose restart
   ```

4. **ابدأ من جديد**:
   ```powershell
   docker-compose down
   docker-compose up -d
   ```
