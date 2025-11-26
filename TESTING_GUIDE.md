# 🎯 دليل الهجوم واختبار النظام Real-Time

## ✅ النظام دلوقتي Real-Time 100%

تم تعديل الصفحتين:
- **👤 Attacker Profiles**: بيانات حقيقية من PostgreSQL مباشرة
- **🤖 AI Analysis**: machine learning حقيقي على البيانات الفعلية

---

## 🚀 كيفية الهجوم واختبار النظام

### الخطوة 1: افتح الداشبورد

```
http://13.53.131.159:8501
```

### الخطوة 2: هاجم SSH Honeypot

افتح terminal جديد وجرب:

```bash
# محاولة 1: كلمة سر خاطئة
ssh root@13.53.131.159 -p 2222
# Password: 123456

# محاولة 2: username مختلف
ssh admin@13.53.131.159 -p 2222
# Password: admin

# محاولة 3: محاولات متعددة
ssh test@13.53.131.159 -p 2222
ssh user@13.53.131.159 -p 2222
ssh ubuntu@13.53.131.159 -p 2222
```

### الخطوة 3: شوف معلوماتك تظهر Live

بعد الهجوم ب 5-10 ثواني:

1. **روح على Dashboard → 👤 Attacker Profiles**
2. **هتلاقي IP بتاعك ظهر في الجدول**
3. **اختار IP بتاعك من القائمة المنسدلة**
4. **هتشوف**:
   - موقعك الجغرافي (Country, City, ISP)
   - عدد المحاولات
   - Threat Score بتاعك
   - Skill Level
   - Timeline كل محاولة
   - أوقات الهجوم
   - الخدمات اللي هاجمتها

5. **روح على Dashboard → 🤖 AI Analysis**
6. **هتشوف**:
   - ML Threat Score بتاعك
   - تصنيف التهديد (Critical/High/Medium/Low)
   - Attack Pattern
   - Anomaly Detection
   - Predictions

---

## 📊 معلومات هتظهر عنك

### في Attacker Profiles:

```
IP: [Your IP]
Country: [Your Country]
City: [Your City]
ISP: [Your ISP]
Skill Level: 🔵 Beginner / 🟡 Intermediate / 🟠 Advanced
Threat Score: [Calculated based on behavior]

Total Attacks: [Number of attempts]
Success Rate: [Percentage]
Data Collected: [Amount]

Most Active Time: [Your attack time]
Attack Frequency: [How often you attack]

Services Targeted:
- SSH: X times
- HTTP: Y times

Timeline:
#1 - 2025-11-26 15:30:22 - SSH - 45s - ❌ Failed
#2 - 2025-11-26 15:31:10 - SSH - 30s - ❌ Failed
```

### في AI Analysis:

```
ML Threat Score: [0-100]
Classification: 🟢 Low / 🟡 Medium / 🟠 High / 🔴 Critical

Attack Pattern:
- Service preference: SSH
- Time pattern: Evening
- Frequency: High

Anomaly Detection:
- Unusual duration: No
- Rapid attacks: Yes (if you did multiple attempts)
- High data: No

Prediction:
- Next likely target: SSH
- Confidence: 85%
```

---

## 🎯 كيف يحسب Threat Score

```python
Base Score = Final Suspicion from AI (0-100)

+ Session Duration:
  > 10 minutes: +15
  > 5 minutes: +10

+ Data Collection:
  > 1MB: +20
  > 100KB: +10

+ Zero-days: +30

+ Steps taken:
  > 50: +15
  > 20: +10

+ Evasion (not detected): +10

Total = min(100, score)
```

### Skill Level Classification:

- **80-100**: 🔴 Elite/APT
- **60-79**: 🟠 Advanced
- **40-59**: 🟡 Intermediate
- **20-39**: 🔵 Beginner
- **0-19**: ⚪ Script Kiddie

---

## 🧪 سيناريوهات الاختبار

### سيناريو 1: هجوم بسيط
```bash
# محاولة واحدة فقط
ssh root@13.53.131.159 -p 2222
```
**النتيجة المتوقعة:**
- Threat Score: ~25
- Skill Level: Script Kiddie
- Classification: Low Threat

### سيناريو 2: هجوم متوسط
```bash
# محاولات متعددة
for i in {1..5}; do
  ssh user$i@13.53.131.159 -p 2222
done
```
**النتيجة المتوقعة:**
- Threat Score: ~40-50
- Skill Level: Intermediate
- Classification: Medium Threat

### سيناريو 3: هجوم متقدم
```bash
# محاولات كثيرة بأوقات مختلفة
# استخدام tools مختلفة
# محاولة services متعددة

# SSH attempts
for i in {1..10}; do
  ssh admin@13.53.131.159 -p 2222
  sleep 5
done

# Web attempts (if web honeypot running)
curl http://13.53.131.159:8080/admin
curl http://13.53.131.159:8080/login
```
**النتيجة المتوقعة:**
- Threat Score: ~60-75
- Skill Level: Advanced
- Classification: High Threat

---

## 📈 Real-Time Updates

النظام يحدث البيانات كل:
- **Database queries**: فوري (كل ما تفتح الصفحة)
- **Auto-refresh**: يمكن تفعيله من الشريط الجانبي (5-60 ثانية)

---

## 🔍 كيف تتأكد النظام Real-Time

### 1. قبل الهجوم:
- افتح Dashboard → Attacker Profiles
- لاحظ عدد المهاجمين الحاليين
- IP بتاعك مش موجود

### 2. أثناء الهجوم:
- اعمل محاولات متعددة
- كل محاولة بتتسجل في database فوراً

### 3. بعد الهجوم:
- ارجع للداشبورد (أو اعمل refresh)
- **IP بتاعك ظهر!**
- كل المعلومات موجودة
- الإحصائيات اتحدثت

---

## 🗺️ Attack Map

الخريطة بتعرض:
- كل الهجمات في آخر 24 ساعة
- موقعك الجغرافي الدقيق (Lat/Lon)
- ISP بتاعك
- نوع الشبكة (Cloud/Residential/ISP)

**IP بتاعك هيظهر كنقطة على الخريطة!**

---

## ⚡ Performance

- **Query Time**: < 100ms
- **Page Load**: < 2 seconds
- **Data Latency**: < 5 seconds
- **Dashboard Refresh**: Instant

---

## 🎓 Tips للحصول على Threat Score عالي

1. **هاجم كتير**: 10+ محاولات
2. **استخدم services مختلفة**: SSH, HTTP, FTP
3. **خد وقتك**: sessions طويلة (5+ دقائق)
4. **جرب passwords كتير**: brute force
5. **استخدم tools متقدمة**: nmap, metasploit

---

## 🔒 ملاحظات أمان

- كل الهجمات في بيئة معزولة (honeypots)
- لا ضرر فعلي على السيستم
- كل البيانات للتحليل فقط
- IP بتاعك بيتسجل للتتبع

---

## 📞 معلومات الوصول

```
Dashboard: http://13.53.131.159:8501

SSH Honeypot: 13.53.131.159:2222
Web Honeypot: 13.53.131.159:8080
FTP Honeypot: 13.53.131.159:2121

Database: PostgreSQL (internal)
Cache: Redis (internal)
```

---

## ✅ Checklist قبل الاختبار

- [ ] الداشبورد شغال: http://13.53.131.159:8501
- [ ] صفحة Attacker Profiles تفتح
- [ ] صفحة AI Analysis تفتح
- [ ] جاهز للهجوم!

---

## 🎯 الهدف النهائي

بعد ما تهاجم، روح على الداشبورد وشوف:

1. ✅ IP بتاعك ظهر في Attacker Profiles
2. ✅ الموقع الجغرافي صح (Country, City, ISP)
3. ✅ عدد المحاولات مظبوط
4. ✅ Threat Score متحسب
5. ✅ Timeline بكل المحاولات
6. ✅ AI Analysis عامل تصنيف
7. ✅ ML Predictions شغالة
8. ✅ Anomaly Detection active

**كل حاجة Real-Time من Database! 🚀**

---

## 🐛 في حالة المشاكل

### المشكلة: IP مش ظاهر
**الحل:**
1. تأكد الهجوم وصل (شوف logs):
   ```bash
   ssh -i cyber-key-new.pem ubuntu@13.53.131.159 "sudo docker logs cyber_mirage_ssh --tail 20"
   ```
2. اعمل refresh للداشبورد (F5)
3. تأكد الـ honeypot شغال

### المشكلة: البيانات قديمة
**الحل:**
- فعّل Auto-refresh من الشريط الجانبي
- اختار interval قصير (5-10 ثواني)

### المشكلة: Threat Score = 0
**الحل:**
- الهجوم مكنش كافي
- جرب محاولات أكتر
- استخدم services مختلفة

---

**جاهز للاختبار! ابدأ الهجوم دلوقتي وشوف معلوماتك تظهر Live! 🎯**
