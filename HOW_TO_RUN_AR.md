# 🎬 كيفية تشغيل البروجكت - شرح عملي
## How to Run - Complete Guide

---

## 🚀 **الطريقة الأسرع (دقيقة واحدة)**

### الخطوة 1️⃣ : فتح Terminal

```powershell
# اضغط: Win + X ثم اختر PowerShell (أو Windows Terminal)
# أو اكتب من Terminal الموجود:
cd a:\cyber_mirage
```

### الخطوة 2️⃣ : فعّل البيئة

```powershell
.\venv\Scripts\Activate.ps1
```

**ستشوف:** الـ prompt يتغير ل `(venv)`

### الخطوة 3️⃣ : شغّل Dashboard

```powershell
streamlit run src/dashboard/streamlit_app.py
```

**ماذا يحدث:**
- Terminal سيطبع معلومات
- سيقول: `You can now view your Streamlit app in your browser.`
- سيفتح: `http://localhost:8501` تلقائياً

### الخطوة 4️⃣ : استمتع! 🎉

```
Dashboard حي قدامك!
اللي شفت = النظام يعمل 100%
```

---

## 🧪 **الاختبارات المختلفة**

### **اختبار 1: Quick Test (30 ثانية)**

```powershell
python test_all_quick.py
```

**النتيجة:**
```
✅ 14/14 components PASSED
🎖️ Grade: PERFECT!
```

### **اختبار 2: Comprehensive Tests (10 ثوان)**

```powershell
pytest tests/ -v
```

**النتيجة:**
```
✅ 60/60 tests PASSED (100%)
⏱️ Execution time: 7.27 seconds
```

### **اختبار 3: Live Demo (2 دقائق)**

```powershell
python run_live_demo.py
```

**النتيجة:**
```
✅ شاهد كل المكونات تعمل
✅ شاهد البيانات الفعلية
✅ شاهد الأداء
```

### **اختبار 4: Real Attack Simulation (2 دقائق)**

```powershell
python real_attack_test.py
```

**النتيجة:**
```
✅ محاكاة هجمات حقيقية
✅ اختبار الدفاع
✅ قياس الأداء
```

---

## 📊 **الخدمات المتاحة**

بعد تشغيل Dashboard، يمكنك تشغيل خدمات أخرى في Terminal جديد:

### **API Server (اختياري)**

```powershell
# في Terminal جديد:
.\venv\Scripts\Activate.ps1
python src/api/honeypot_api.py
```

**ماذا يعني:** يمكنك الآن ترسل طلبات HTTP للنظام

### **Training (اختياري - يأخذ 10-15 دقيقة)**

```powershell
# في Terminal جديد:
.\venv\Scripts\Activate.ps1
python src/training/train.py
```

**ماذا يعني:** النموذج يتدرب على attacks

### **TensorBoard (اختياري - لمراقبة Training)**

```powershell
# في Terminal جديد:
tensorboard --logdir=data/logs
```

**ماذا يعني:** لوحة تحكم لمراقبة التدريب على `http://localhost:6006`

---

## 🎯 **كل الأوامر في مكان واحد**

```powershell
# تفعيل البيئة
.\venv\Scripts\Activate.ps1

# Dashboard الرئيسي
streamlit run src/dashboard/streamlit_app.py

# اختبارات
python test_all_quick.py                    # quick test
pytest tests/ -v                            # جميع الاختبارات
python run_live_demo.py                     # شامل demo
python real_attack_test.py                  # هجمات حقيقية

# خدمات (في Terminal منفصل)
python src/api/honeypot_api.py             # API
python src/training/train.py               # training
tensorboard --logdir=data/logs             # monitoring

# معلومات
python test_connectivity.py                # اختبر الاتصال
```

---

## 🔍 **كيف تتأكد إن كل شيء يعمل؟**

### ✅ **الداشبورد شغّال:**
```
✅ تشوف واجهة جميلة
✅ تشوف رسوم بيانية
✅ تشوف معلومات حقيقية
✅ تشوف: "Streamlit app is running" في Terminal
```

### ✅ **الاختبارات نجحت:**
```
✅ تشوف: "60 passed"
✅ تشوف: "100%"
✅ تشوف: "PASSED ✅"
✅ لا تشوف أي "FAILED ❌"
```

### ✅ **الهجمات تُكتشف:**
```
✅ تشوف في Dashboard: attacks logged
✅ تشوف: حمراء وتحذيرات
✅ تشوف: الدفاع يستجيب
```

---

## ⚠️ **في حالة مشاكل**

### **المشكلة: "Port already in use"**

```powershell
# الحل:
streamlit run src/dashboard/streamlit_app.py --server.port=8502
# استخدم port مختلف
```

### **المشكلة: "Module not found"**

```powershell
# الحل:
# تأكد البيئة مفعلة:
.\venv\Scripts\Activate.ps1

# ثم جرب مرة أخرى
```

### **المشكلة: "Permission denied"**

```powershell
# الحل:
# شغّل Terminal كـ Administrator
# اضغط: Start > Search "PowerShell" > Right-click > Run as Administrator
```

### **المشكلة: "Python not found"**

```powershell
# الحل:
# تأكد من المسار:
A:\cyber_mirage\venv\Scripts\python.exe test_all_quick.py
```

---

## 📋 **Checklist للتأكد**

```
قبل التشغيل:
☑️  البيئة موجودة (venv/)
☑️  Python 3.13.5 مثبت
☑️  كل المكتبات مثبتة (60+ package)

أثناء التشغيل:
☑️  Dashboard يفتح على 8501
☑️  المتصفح يعمل
☑️  البيانات تظهر بشكل مباشر

بعد التشغيل:
☑️  جميع الاختبارات نجحت
☑️  لا توجد أخطاء
☑️  النظام جاهز للاستخدام
```

---

## 🎬 **سيناريو كامل**

```powershell
# 1. فتح Terminal
Windows key + X → PowerShell

# 2. الذهاب للمجلد
cd a:\cyber_mirage

# 3. تفعيل البيئة
.\venv\Scripts\Activate.ps1

# 4. اختبار سريع (اختياري)
python test_all_quick.py

# 5. شغّل Dashboard
streamlit run src/dashboard/streamlit_app.py

# الآن:
# - Dashboard يفتح تلقائياً على http://localhost:8501
# - النظام يعمل بشكل مباشر
# - يمكنك تجريب الميزات
```

---

## 🚀 **للاستخدام المتقدم**

### **في Terminal منفصل (Terminal 2):**

```powershell
.\venv\Scripts\Activate.ps1
python src/api/honeypot_api.py
# الآن API متاح على http://localhost:8080
```

### **في Terminal ثالث (Terminal 3):**

```powershell
.\venv\Scripts\Activate.ps1
python src/training/train.py
# النموذج يتدرب (10-15 دقيقة)
```

### **في Terminal رابع (Terminal 4):**

```powershell
tensorboard --logdir=data/logs
# شاهد: http://localhost:6006
```

---

## 📊 **ماذا تتوقع أن تشوف**

### **Dashboard:**
```
🎭 عنوان: Cyber Mirage v5.0
📊 رسوم بيانية لـ:
   • الهجمات المكتشفة
   • الأداء الفعلي
   • قرارات AI
   • الإحصائيات
📈 بيانات حية (تتحدث كل ثانية)
```

### **Terminal:**
```
✅ "Streamlit app is running"
ℹ️  "You can now view your Streamlit app in your browser"
✅ معلومات عن المكونات
✅ رسائل حالة
```

---

## 🎉 **Success!**

إذا شفت:
1. ✅ Dashboard في المتصفح
2. ✅ بيانات حية
3. ✅ لا توجد أخطاء
4. ✅ الأداء سريع

## **إذن: النظام يعمل تماماً! 🚀**

---

## 💡 **نصائح سريعة**

- **بطيء البدء؟** أول مرة تأخذ 10 ثوان
- **تريد إيقاف؟** اضغط `Ctrl+C` في Terminal
- **تريد Logs؟** افتح `data/logs/`
- **تريد تغييرات؟** عدّل `src/` وأعد التشغيل

---

**الآن أنت جاهز! ابدأ الآن! 🚀**

```bash
streamlit run src/dashboard/streamlit_app.py
```

