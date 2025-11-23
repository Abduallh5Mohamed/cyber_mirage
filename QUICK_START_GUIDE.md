# 🚀 **البدء السريع - Cyber Mirage**

---

## ✅ **المشروع جاهز الآن!**

جميع الخدمات تعمل وجاهزة للاستخدام 🎉

---

## 🌐 **الوصول السريع للخدمات:**

### **الخدمات الأساسية:**

| الخدمة | الرابط | اسم المستخدم | كلمة المرور |
|--------|---------|----------|----------|
| **Grafana** | http://localhost:3000 | admin | admin |
| **Prometheus** | http://localhost:9090 | - | - |
| **Alertmanager** | http://localhost:9093 | - | - |
| **Honeypot API** | http://localhost:8080/docs | - | - |
| **Streamlit Dashboard** | http://localhost:8501 | - | - |

---

## 📊 **أولاً: استكشف Grafana**

```
1. افتح: http://localhost:3000
2. سجّل دخول: admin / admin
3. استكشف اللوحات المسبقة:
   • System Overview
   • Network Metrics
   • Application Performance
   • Security Alerts
   • Attack Statistics
```

---

## 📈 **ثانياً: تحقق من Prometheus**

```
1. افتح: http://localhost:9090
2. اختبر استعلام:
   • up{job="prometheus"}
   • node_cpu_seconds_total
   • process_resident_memory_bytes
3. عرض Target Status
```

---

## 🚨 **ثالثاً: استكشف Alertmanager**

```
1. افتح: http://localhost:9093
2. اعرض التنبيهات:
   • Active Alerts
   • Rules
   • Silences
3. إدارة الإجراءات
```

---

## 🔌 **رابعاً: اختبر الـ API**

```
1. افتح: http://localhost:8080/docs
2. استكشف Endpoints:
   • GET /health ............... Health check
   • GET /metrics .............. Prometheus metrics
   • POST /api/attack .......... Log attack
   • GET /api/attacks .......... Get attacks
```

---

## 📱 **خامساً: استخدم Dashboard**

```
1. افتح: http://localhost:8501
2. استكشف:
   • Real-time metrics
   • Attack logs
   • System status
   • Performance charts
```

---

## 🛠️ **أوامر مفيدة:**

```powershell
# عرض حالة جميع الخدمات
docker-compose ps

# عرض السجلات لخدمة معينة
docker-compose logs -f [service_name]

# إيقاف جميع الخدمات
docker-compose down

# إعادة تشغيل خدمة
docker-compose restart [service_name]

# دخول container
docker exec -it [container_name] bash

# عرض الموارد المستخدمة
docker stats
```

---

## 📝 **مثال على الاستخدام:**

### **1. لتسجيل هجوم:**
```bash
curl -X POST http://localhost:8080/api/attack \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.100",
    "attack_type": "SSH_BRUTE_FORCE",
    "severity": "high"
  }'
```

### **2. لعرض الهجمات:**
```bash
curl http://localhost:8080/api/attacks
```

### **3. لعرض الصحة:**
```bash
curl http://localhost:8080/health
```

---

## 🔍 **كيفية مراقبة النظام:**

### **في Grafana:**
1. انتقل إلى Dashboards
2. اختر "System Overview"
3. راقب:
   - CPU Usage
   - Memory Usage
   - Network Traffic
   - Disk Space
   - Container Status

### **في Prometheus:**
1. انتقل إلى Graph
2. اختبر استعلام:
   ```
   rate(http_requests_total[5m])
   ```
3. شاهد النتائج بيانياً

### **في Alertmanager:**
1. افتح التنبيهات النشطة
2. شاهد تفاصيل التنبيه
3. اتخذ إجراء

---

## ⚙️ **تكوين إضافي (اختياري):**

### **إضافة بيانات اعتماد Slack:**
```
1. اذهب إلى .env.production
2. أضف SLACK_WEBHOOK_URL
3. أعد تشغيل Alertmanager
```

### **إضافة بيانات اعتماد Email:**
```
1. اذهب إلى .env.production
2. أضف SMTP_* variables
3. أعد تشغيل Alertmanager
```

---

## 🚨 **في حالة المشاكل:**

```powershell
# 1. تحقق من الخدمات
docker-compose ps

# 2. اعرض السجلات
docker-compose logs -f

# 3. أعد تشغيل الخدمة
docker-compose restart [service_name]

# 4. افعل rebuild
docker-compose build [service_name]

# 5. ابدأ من جديد
docker-compose down
docker-compose up -d
```

---

## 📚 **الملفات المرجعية:**

- `PROJECT_FINAL_STATUS.md` - الحالة النهائية
- `README.md` - التفاصيل الكاملة
- `DOCKER_COMMANDS_REFERENCE.md` - أوامر Docker
- `API_DOCUMENTATION.md` - توثيق API

---

## 🎯 **الخطوات التالية:**

1. ✅ استكشف Grafana
2. ✅ راقب Prometheus
3. ✅ اختبر Alertmanager
4. ✅ استخدم API
5. ✅ عدّل التكوينات حسب احتياجاتك

---

## 💡 **نصائح مفيدة:**

- 💡 احفظ كلمات المرور الحالية
- 💡 عمل backup للبيانات بانتظام
- 💡 راقب استهلاك الموارد
- 💡 اقرأ السجلات عند المشاكل
- 💡 استخدم health checks للتحقق

---

**الآن أنت جاهز للبدء!** 🚀

استمتع بـ **Cyber Mirage**! 🎉
