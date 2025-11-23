# 🚀 **دليل التشغيل السريع - Production Deployment**

> بتاريخ: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

---

## ⚡ **التشغيل بـ 5 خطوات فقط:**

### **الخطوة 1: تحديث كلمات المرور** 
```powershell
# افتح الملف في محرر النصوص
notepad A:\cyber_mirage\.env.production

# غيّر هذه القيم على الأقل:
# - POSTGRES_PASSWORD
# - REDIS_PASSWORD
# - GRAFANA_PASSWORD
```

### **الخطوة 2: انتقل للمجلد الرئيسي**
```powershell
cd A:\cyber_mirage
```

### **الخطوة 3: بناء الصور**
```powershell
docker-compose -f docker-compose.production.yml build
```

### **الخطوة 4: تشغيل الخدمات**
```powershell
docker-compose -f docker-compose.production.yml up -d
```

### **الخطوة 5: التحقق من الحالة**
```powershell
docker-compose -f docker-compose.production.yml ps
```

---

## 🌐 **الخدمات المتاحة بعد التشغيل:**

| الخدمة | الرابط | المنفذ |
|--------|---------|---------|
| 🏠 **Grafana Dashboard** | http://localhost:3000 | 3000 |
| 📊 **Prometheus** | http://localhost:9090 | 9090 |
| 🚨 **Alertmanager** | http://localhost:9093 | 9093 |
| 📈 **API Metrics** | http://localhost:8080/metrics | 8080 |
| 💾 **PostgreSQL** | localhost:5433 | 5433 |
| 🔴 **Redis** | localhost:6379 | 6379 |

---

## 🔐 **بيانات الدخول:**

```
Grafana:
- Username: admin
- Password: (من .env.production - GRAFANA_PASSWORD)

PostgreSQL:
- Username: cybermirage
- Password: (من .env.production - POSTGRES_PASSWORD)

Redis:
- No username
- Password: (من .env.production - REDIS_PASSWORD)
```

---

## 📝 **الملفات المهمة:**

| الملف | الوصف |
|------|--------|
| `.env.production` | **يجب تحديثه** - المتغيرات الحساسة |
| `Dockerfile.production` | بناء صورة Docker optimized |
| `docker-compose.production.yml` | تعريف جميع الخدمات |
| `docker/prometheus/prometheus.yml` | إعدادات جمع المقاييس |
| `docker/prometheus/alerts.yml` | قواعل التنبيهات |

---

## 🛠️ **أوامر مفيدة:**

```powershell
# عرض السجلات
docker-compose -f docker-compose.production.yml logs -f

# عرض سجلات خدمة معينة
docker-compose -f docker-compose.production.yml logs -f prometheus

# إيقاف جميع الخدمات
docker-compose -f docker-compose.production.yml down

# حذف السجلات والبيانات
docker-compose -f docker-compose.production.yml down -v

# إعادة تشغيل خدمة معينة
docker-compose -f docker-compose.production.yml restart prometheus

# دخول container
docker exec -it cyber_mirage_postgres bash

# عرض استهلاك الموارد
docker stats
```

---

## ✅ **قائمة التحقق قبل الإنتاج:**

- [ ] تم تحديث `.env.production` بكلمات مرور قوية
- [ ] تم عمل backup للبيانات الموجودة
- [ ] تم فحص الموارد المتاحة (CPU, RAM, Disk)
- [ ] تم اختبار connectivity للـ external services
- [ ] تم إعداد firewall rules إذا لزم الأمر
- [ ] تم إعداد monitoring وتنبيهات
- [ ] تم توثيق أي تكوينات مخصصة
- [ ] تم عمل test run قبل production

---

## 🚨 **في حالة المشاكل:**

```powershell
# 1. تحقق من الأخطاء
docker-compose -f docker-compose.production.yml logs

# 2. أوقف الخدمات
docker-compose -f docker-compose.production.yml down

# 3. احذف الـ volumes إذا لزم الأمر (تحذير: سيفقد البيانات!)
docker-compose -f docker-compose.production.yml down -v

# 4. أعد بناء الصور
docker-compose -f docker-compose.production.yml build --no-cache

# 5. شغّل مجددًا
docker-compose -f docker-compose.production.yml up -d
```

---

## 📞 **الدعم:**

تم إنشاء هذه الملفات بواسطة **GitHub Copilot**

جميع الملفات الضرورية موجودة في:
- `/docker-compose.production.yml`
- `/Dockerfile.production`
- `/.env.production`
- `/docker/prometheus/*`
- `/docker/grafana/*`
- `/docker/alertmanager/*`
- `/docker/postgres/*`

---

**آخر تحديث:** $(Get-Date)

**الحالة:** ✅ جاهز للإنتاج
