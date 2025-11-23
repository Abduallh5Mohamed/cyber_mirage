# 🚀 إنشاء Droplet على DigitalOcean - دليل مصوّر

## الطريقة 1: من الواجهة (الأسهل) ⭐

### الخطوة 1: افتح صفحة إنشاء Droplet
اذهب إلى: **https://cloud.digitalocean.com/droplets/new**

أو من Dashboard:
- اضغط "Create" (الزر الأخضر أعلى اليمين)
- اختر "Droplets"

---

### الخطوة 2: اختر المنطقة (Region)
📍 **اختر منطقة قريبة منك:**

للشرق الأوسط وأوروبا:
- ✅ **Frankfurt, Germany** (fra1) ← موصى به
- ✅ London, UK (lon1)
- ✅ Amsterdam, Netherlands (ams3)

للولايات المتحدة:
- New York (nyc1/nyc3)
- San Francisco (sfo3)

---

### الخطوة 3: اختر نظام التشغيل
🐧 **اختر Ubuntu:**

```
Distribution: Ubuntu
Version: 22.04 (LTS) x64
```

---

### الخطوة 4: اختر حجم الـ Droplet
💰 **الحجم الموصى به:**

```
Plan: Basic
CPU Options: Regular

Size: $12/month
- 2 vCPU
- 4 GB RAM
- 80 GB SSD
- 4 TB Transfer
```

**أو إذا كنت تريد توفير المال:**
```
Size: $6/month
- 1 vCPU
- 2 GB RAM
- 50 GB SSD
- 2 TB Transfer
```
⚠️ لكن 4GB RAM أفضل للأداء

---

### الخطوة 5: أضف SSH Key
🔑 **مهم جداً!**

1. في قسم "Authentication"، اختر **"SSH Key"**
2. اختر المفتاح الذي أضفته: **`cyber_mirage_key`**
3. إذا لم يظهر، اضغط "New SSH Key" والصق:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIET9u8Fp1i55K9VyHHDZG0i5cdSudHUmRGzqiNI1f4bk abduallhshadow@gmail.com
```

⚠️ **لا تختر "Password"** - SSH Key أكثر أماناً!

---

### الخطوة 6: إعدادات إضافية (اختيارية)

**Monitoring** (موصى به):
- ☑️ Enable Monitoring (مجاني!)

**Backups** (اختياري):
- ☐ Weekly Backups (+20% من السعر)

**User data / cloud-init** (اختياري للأتمتة):
يمكنك تخطي هذا الآن، سنستخدم السكريبت اليدوي.

---

### الخطوة 7: اختر اسم للـ Droplet
📝 **Hostname:**
```
cyber-mirage
```

**Tags** (اختياري):
```
cyber-mirage, honeypot, production
```

---

### الخطوة 8: إنشاء الـ Droplet
🎯 اضغط **"Create Droplet"** (الزر الأخضر الكبير في الأسفل)

⏳ **انتظر 1-2 دقيقة...**

---

### الخطوة 9: احصل على الـ IP
✅ بعد الإنشاء، ستظهر لك:

```
cyber-mirage
Status: Active 🟢
IP Address: 134.209.89.123 (مثال)
```

📋 **انسخ الـ IP Address** - ستحتاجه في الخطوة التالية!

---

## الطريقة 2: باستخدام doctl CLI (متقدم)

إذا كان لديك DigitalOcean API Token:

```powershell
# تثبيت doctl
scoop install doctl

# التوثيق
doctl auth init --access-token "YOUR_DO_TOKEN"

# إنشاء الـ Droplet
doctl compute droplet create cyber-mirage `
  --region fra1 `
  --size s-2vcpu-4gb `
  --image ubuntu-22-04-x64 `
  --ssh-keys $(doctl compute ssh-key list --no-header --format ID | Select-Object -First 1) `
  --tag-names cyber-mirage `
  --enable-monitoring `
  --wait

# الحصول على الـ IP
doctl compute droplet list --format ID,Name,PublicIPv4
```

---

## ✅ Checklist

قبل ما تكمل، تأكد:
- ☑️ اخترت Ubuntu 22.04 LTS
- ☑️ اخترت حجم 2 vCPU / 4GB RAM (أو أكبر)
- ☑️ أضفت SSH Key: `cyber_mirage_key`
- ☑️ حصلت على IP Address
- ☑️ الـ Droplet Status: **Active** 🟢

---

## 🎯 بعد الإنشاء

**IP الخاص بك:** `_____________` (اكتبه هنا)

**الخطوة التالية:**
```powershell
# اختبار الاتصال
ssh -i C:\Users\abdua\.ssh\cyber_mirage root@YOUR_DROPLET_IP
```

**إذا نجح الاتصال:**
```
Welcome to Ubuntu 22.04.3 LTS
root@cyber-mirage:~#
```

✅ **الآن أنت جاهز لرفع الملفات!**

---

## 💡 نصائح

🔒 **الأمان:**
- لا تشارك IP الخاص بك علناً حتى تنتهي من الإعداد
- استخدم SSH Keys دائماً، ليس Passwords

💰 **الفوترة:**
- DigitalOcean تحاسب بالساعة
- Droplet بـ $12/شهر = $0.018/ساعة
- يمكنك إيقافه في أي وقت لتوفير المال

📊 **المراقبة:**
- راقب استخدام الـ Bandwidth (4TB included)
- افحص الفواتير يومياً أول أسبوع

---

## 🚨 مشاكل شائعة

**❌ Problem: SSH Connection refused**
```
✅ Solution:
- انتظر 2-3 دقائق بعد الإنشاء
- تأكد من استخدام المفتاح الصحيح
- تأكد من IP صحيح
```

**❌ Problem: Permission denied (publickey)**
```
✅ Solution:
- تأكد من إضافة SSH Key عند الإنشاء
- استخدم: ssh -i C:\Users\abdua\.ssh\cyber_mirage root@IP
```

**❌ Problem: Droplet creation failed**
```
✅ Solution:
- تأكد من وجود رصيد في الحساب
- جرب منطقة (region) أخرى
- تحقق من حد الـ Droplets في حسابك
```

---

## 📞 دعم DigitalOcean

إذا واجهت مشاكل:
- Documentation: https://docs.digitalocean.com
- Support: https://cloud.digitalocean.com/support
- Community: https://www.digitalocean.com/community

---

🎉 **مبروك! الآن لديك سيرفر على الإنترنت!**

**الخطوة التالية:** رفع ملفات المشروع للسيرفر
