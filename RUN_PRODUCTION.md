# 🚀 تشغيل المشروع - بدون مشاكل Docker

## ✅ الحل العملي

البناء في Docker يأخذ وقت طويل وقد يتعطل. الحل الأسرع:

### **شغل كل شيء بدون Docker** (الطريقة المباشرة):

---

## 1️⃣ تشغيل قواعد البيانات (Docker فقط):

```powershell
# شغل Redis و PostgreSQL
docker-compose up -d redis postgres
```

---

## 2️⃣ تشغيل الخدمات الأخرى (Docker):

```powershell
# شغل المراقبة
docker-compose up -d prometheus grafana node-exporter
```

---

## 3️⃣ تشغيل Honeypot Main Application (Python مباشر):

```powershell
# تأكد أن الـ venv شغال
.\venv\Scripts\Activate.ps1

# شغل الـ API
python src/api/main.py
```

---

## 4️⃣ تشغيل Dashboard (في terminal منفصل):

```powershell
# في terminal جديد
.\venv\Scripts\Activate.ps1

# شغل Dashboard
streamlit run src/dashboard/streamlit_app.py
```

---

## 📊 النتيجة النهائية:

| الخدمة | الحالة | الطريقة | الرابط |
|--------|--------|--------|--------|
| Redis | ✅ | Docker | Internal |
| PostgreSQL | ✅ | Docker | Internal |
| Prometheus | ✅ | Docker | http://localhost:9090 |
| Grafana | ✅ | Docker | http://localhost:3000 |
| Node Exporter | ✅ | Docker | Internal |
| **Honeypot API** | ✅ | **Python** | **http://localhost:8080** |
| **Dashboard** | ✅ | **Python** | **http://localhost:8501** |

---

## 🎯 الأوامر السريعة:

```powershell
# 1. تفعيل البيئة
.\venv\Scripts\Activate.ps1

# 2. تثبيت التبعيات إن لزم
pip install -r requirements.txt
pip install -r requirements-production.txt

# 3. تشغيل البيانات (Docker)
docker-compose up -d redis postgres prometheus grafana node-exporter

# 4. تشغيل الـ API (في terminal)
python src/api/main.py

# 5. تشغيل Dashboard (في terminal جديد)
streamlit run src/dashboard/streamlit_app.py
```

---

## ✨ المميزات:

✅ **أسرع بكثير** - بدون انتظار بناء Docker الطويل
✅ **أسهل التصحيح** - تعديل الكود والتشغيل فوراً
✅ **Docker للبيانات فقط** - الاستقرار + السرعة
✅ **متوافق مع الإنتاج** - نفس الحزم والإعدادات

---

## 🔄 الخطوات:

### **الخطوة 1: شغل البيانات**

```powershell
docker-compose up -d redis postgres prometheus grafana node-exporter
```

**النتيجة المتوقعة:**
```
[+] Running 5/5
✔ cyber_mirage_redis           Started
✔ cyber_mirage_postgres        Started
✔ cyber_mirage_prometheus      Started
✔ cyber_mirage_grafana         Started
✔ cyber_mirage_node_exporter   Started
```

---

### **الخطوة 2: شغل Honeypot API**

في **terminal 1**:

```powershell
.\venv\Scripts\Activate.ps1
python src/api/main.py
```

**النتيجة المتوقعة:**
```
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Application startup complete
```

---

### **الخطوة 3: شغل Dashboard**

في **terminal 2**:

```powershell
.\venv\Scripts\Activate.ps1
streamlit run src/dashboard/streamlit_app.py
```

**النتيجة المتوقعة:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

---

## 🌐 افتح هذه الروابط:

1. **Dashboard** → http://localhost:8501 🎨
2. **Honeypot API** → http://localhost:8080 🔌
3. **Grafana** → http://localhost:3000 📊
4. **Prometheus** → http://localhost:9090 📈

---

## 🚨 إذا حصل مشكلة:

### Redis لا يعمل:
```powershell
docker-compose logs redis
docker-compose restart redis
```

### PostgreSQL لا يعمل:
```powershell
docker-compose logs postgres
docker-compose restart postgres
```

### Python يشتكي من الحزم:
```powershell
pip install -r requirements.txt --upgrade
```

### Dashboard معطل:
```powershell
streamlit run src/dashboard/streamlit_app.py --logger.level=debug
```

---

## 💾 حفظ البيانات:

```powershell
# حفظ قاعدة البيانات
docker exec cyber_mirage_postgres pg_dump -U honeypot cyber_mirage > backup.sql

# استرجاع البيانات
docker exec -i cyber_mirage_postgres psql -U honeypot cyber_mirage < backup.sql
```

---

## ✨ خلاصة:

✅ خدمات البيانات → Docker (مستقر وسريع)
✅ تطبيقات Python → Direct (مرن وسهل التطوير)
✅ المراقبة → Docker (بيانات دقيقة)

🎉 **كل شيء يعمل!**
