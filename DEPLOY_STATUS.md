# ✅ الملفات اترفعت بنجاح!

## الخطوات اللي حصلت:
1. ✅ رفعت `honeypot_manager.py` (6.4 KB)
2. ✅ رفعت `live_dashboard.py` (11 KB)  
3. ✅ نقلت الملفات لـ `/opt/cyber_mirage/`

---

## ⚠️ المتبقي: إعادة بناء الحاويات

**المشكلة:** PowerShell عندك فيه encoding issue بيخلي الأوامر تفشل.

---

## 🚀 الحل: نفّذ من CMD (مش PowerShell)

### الخطوة 1: افتح CMD
اضغط `Win + R` واكتب `cmd` واضغط Enter

### الخطوة 2: انسخ والصق الأوامر دي (واحد واحد):

```cmd
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 "cd /opt/cyber_mirage && sudo docker compose -f docker-compose.production.yml build honeypots"
```

انتظر حتى ينتهي (حوالي 1-2 دقيقة)...

```cmd
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 "cd /opt/cyber_mirage && sudo docker compose -f docker-compose.production.yml build dashboard"
```

انتظر حتى ينتهي...

```cmd
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 "cd /opt/cyber_mirage && sudo docker compose -f docker-compose.production.yml up -d honeypots dashboard"
```

---

## 🧪 بعد كده اختبر:

### في Ubuntu VM Terminal:
```bash
# هجمة SSH
ssh -p 2222 admin@13.53.131.159

# هجمة HTTP  
curl http://13.53.131.159:8080/test

# شوف logs
ssh ubuntu@13.53.131.159 "sudo docker logs cyber_mirage_honeypots --tail 30"
```

### افتح Dashboard:
```
http://13.53.131.159:8501
```

**المتوقع:**
- ✅ No "SessionInfo" warning
- ✅ Total Attacks يزيد
- ✅ Recent Attacks تظهر
- ✅ Logs تقول: "✅ Logged SSH attack from YOUR_IP to PostgreSQL"

---

## 🔧 أو البديل الأسرع: من Ubuntu VM نفسها

```bash
ssh ubuntu@13.53.131.159
cd /opt/cyber_mirage
sudo docker compose -f docker-compose.production.yml build honeypots dashboard
sudo docker compose -f docker-compose.production.yml up -d honeypots dashboard
sudo docker ps | grep -E 'honeypots|dashboard'
```

---

**عايزني أساعدك في إيه بالضبط دلوقتي؟**
1. تنفيذ الأوامر من CMD؟
2. تنفيذ من Ubuntu VM مباشرة؟
3. طريقة تانية؟
