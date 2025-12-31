# Cyber Mirage Scripts

هذا المجلد يحتوي على سكريبتات مساعدة للنشر والإدارة.

## 📁 الملفات

| الملف | الوصف |
|-------|-------|
| `quick_deploy.sh` | 🚀 نشر سريع على سيرفر Ubuntu جديد |
| `setup_https.sh` | 🔒 إعداد HTTPS مع Nginx و Let's Encrypt |
| `security_harden.sh` | 🔐 تقوية أمان السيرفر |
| `install_service.sh` | 📦 تثبيت systemd service للتشغيل التلقائي |
| `update.sh` | ⬆️ تحديث التطبيق لآخر إصدار |
| `health_check.sh` | 🔍 فحص صحة جميع الخدمات |
| `cyber-mirage.service` | 📄 ملف systemd service |

## 🚀 الاستخدام

### نشر سريع (Quick Deploy)
```bash
# على سيرفر Ubuntu 22.04 جديد
chmod +x quick_deploy.sh
./quick_deploy.sh
```

### إعداد HTTPS
```bash
chmod +x setup_https.sh
./setup_https.sh your-domain.com
```

### تقوية الأمان
```bash
chmod +x security_harden.sh
./security_harden.sh
```

### تثبيت التشغيل التلقائي
```bash
chmod +x install_service.sh
./install_service.sh

# الآن يمكنك استخدام:
sudo systemctl start cyber-mirage
sudo systemctl stop cyber-mirage
sudo systemctl status cyber-mirage
```

### التحديث
```bash
chmod +x update.sh
./update.sh
```

### فحص الصحة
```bash
chmod +x health_check.sh
./health_check.sh
```

## ⚠️ ملاحظات مهمة

1. **قبل التشغيل:** تأكد من تعديل `.env.production` بكلمات سر قوية
2. **HTTPS:** يحتاج domain يشير لـ IP السيرفر
3. **الأمان:** شغّل `security_harden.sh` بعد التأكد من عمل SSH بمفتاح
4. **النسخ الاحتياطي:** الـ `update.sh` يأخذ نسخة احتياطية تلقائياً
