# 🧪 دليل الاختبار الشامل - Cyber Mirage
## كيف تختبر النظام وتتأكد من فعاليته

---

## 📋 **جدول المحتويات**

1. [اختبارات سريعة (5 دقائق)](#quick-tests)
2. [اختبار الـ Dashboard](#dashboard-test)
3. [اختبار Honeypots بالهجمات الحقيقية](#honeypot-attacks)
4. [اختبار AI Engine](#ai-engine-test)
5. [اختبار Monitoring (Prometheus & Grafana)](#monitoring-test)
6. [اختبار قواعد البيانات](#database-test)
7. [اختبار الأداء تحت الضغط](#stress-test)

---

## ⚡ <a name="quick-tests"></a>1. اختبارات سريعة (5 دقائق)

### **التحقق من حالة جميع الخدمات:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
echo '=== Container Health Status ===' && \
sudo docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' --filter name=cyber_mirage
"@
```

**النتيجة المتوقعة:** جميع الحاويات `(healthy)` أو `Up`

---

### **اختبار جميع Endpoints:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
echo '1. Dashboard:' && curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:8501 && \
echo '2. AI Engine Health:' && curl -s http://localhost:8001/health | jq -r '.status' && \
echo '3. AI Engine Metrics:' && curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:8001/metrics && \
echo '4. Prometheus:' && curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:9090/-/ready && \
echo '5. Grafana:' && curl -s http://localhost:3000/api/health | jq -r '.database'
"@
```

**النتيجة المتوقعة:**
- Dashboard: `HTTP 200`
- AI Engine Health: `healthy`
- AI Engine Metrics: `HTTP 200`
- Prometheus: `HTTP 200`
- Grafana: `ok`

---

## 🖥️ <a name="dashboard-test"></a>2. اختبار الـ Dashboard

### **افتح Dashboard في المتصفح:**

```
http://13.53.131.159:8501
```

### **ما يجب أن تراه:**

✅ **واجهة Streamlit** تعمل بدون أخطاء
✅ **صفحة رئيسية** بعنوان "Cyber Mirage"
✅ **إحصائيات** (حتى لو كانت فارغة في البداية)
✅ **لا توجد رسائل خطأ** في أعلى الصفحة

### **اختبار تفاعلي:**

1. جرب تنقل بين التبويبات (Tabs)
2. شاهد إذا كانت الرسوم البيانية تظهر
3. تحقق من أن الصفحة تحدث البيانات تلقائياً

---

## 🎯 <a name="honeypot-attacks"></a>3. اختبار Honeypots بالهجمات الحقيقية

### **A. اختبار SSH Honeypot (المنفذ 2222):**

```powershell
# من جهازك المحلي - محاولة اتصال SSH خاطئة
ssh -p 2222 root@13.53.131.159
# اكتب أي كلمة مرور خاطئة 3 مرات
```

**النتيجة المتوقعة:**
- يسمح لك بالمحاولة
- يسجل محاولاتك الفاشلة
- يجمع بيانات عن هجومك

---

### **B. اختبار HTTP Honeypot (المنفذ 8080):**

```powershell
# اختبار هجوم SQL Injection
curl "http://13.53.131.159:8080/login?username=admin'%20OR%201=1--&password=anything"

# اختبار Directory Traversal
curl "http://13.53.131.159:8080/../../../etc/passwd"

# اختبار XSS
curl "http://13.53.131.159:8080/search?q=<script>alert('XSS')</script>"
```

---

### **C. اختبار MySQL Honeypot (المنفذ 3306):**

```powershell
# محاولة اتصال MySQL خاطئة (يحتاج mysql client)
mysql -h 13.53.131.159 -P 3306 -u root -p
# اكتب كلمة مرور خاطئة
```

أو استخدم Python:

```python
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 "python3 << 'EOF'
import socket
import time

# محاولة اتصال بـ MySQL Honeypot
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 3306))
data = sock.recv(1024)
print(f'MySQL Response: {data[:50]}...')
sock.close()
EOF
"
```

---

### **D. التحقق من تسجيل الهجمات:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
echo '=== Recent Honeypot Logs ===' && \
sudo docker logs cyber_mirage_honeypots --tail 50 | grep -E 'attack|connection|attempt'
"@
```

**النتيجة المتوقعة:** ترى سجلات الاتصالات والمحاولات الفاشلة

---

### **E. فحص البيانات في PostgreSQL:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
sudo docker exec cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -c \
\"SELECT COUNT(*) as total_attacks, \
        COUNT(DISTINCT attacker_name) as unique_attackers \
 FROM attack_sessions;\"
"@
```

---

## 🤖 <a name="ai-engine-test"></a>4. اختبار AI Engine

### **A. التحقق من Metrics:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 "curl -s http://localhost:8001/metrics"
```

**ابحث عن:**
- `ai_engine_attacks_total` - عدد الهجمات المعالجة
- `ai_engine_redis_connected 1` - Redis متصل
- `ai_engine_db_connected 1` - PostgreSQL متصل

---

### **B. إرسال هجوم وهمي للاختبار:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
sudo docker exec cyber_mirage_redis redis-cli -a changeme123 --no-auth-warning lpush attack_queue '{\"source_ip\":\"192.168.1.100\",\"attack_type\":\"brute_force\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}'
"@
```

**ثم تحقق من المعالجة:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
echo '=== AI Engine Logs ===' && \
sudo docker logs cyber_mirage_ai --tail 20 | grep -E 'Processed|attack'
"@
```

**النتيجة المتوقعة:** ترى رسالة `Processed attack from 192.168.1.100`

---

### **C. فحص Redis Threat Intelligence:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
sudo docker exec cyber_mirage_redis redis-cli -a changeme123 --no-auth-warning --raw HGETALL threat:192.168.1.100
"@
```

**النتيجة المتوقعة:** ترى `count` و `last_seen`

---

## 📊 <a name="monitoring-test"></a>5. اختبار Monitoring

### **A. Prometheus - تحقق من Targets:**

افتح في المتصفح:
```
http://13.53.131.159:9090/targets
```

**ابحث عن:**
- ✅ `honeypots` - State: UP
- ✅ `ai-engine` - State: UP
- ✅ `postgres` - State: UP
- ✅ `redis` - State: UP
- ✅ `node-exporter` - State: UP
- ✅ `cadvisor` - State: UP

---

### **B. Prometheus Queries - اختبر البيانات:**

في Prometheus Web UI اذهب لـ Graph واكتب:

```promql
# عدد الحاويات الشغالة
count(up == 1)

# استخدام CPU للحاويات
rate(container_cpu_usage_seconds_total[5m])

# استخدام Memory
container_memory_usage_bytes

# AI Engine attacks
ai_engine_attacks_total

# Redis اتصال
ai_engine_redis_connected
```

---

### **C. Grafana - إنشاء Dashboard:**

1. افتح Grafana:
   ```
   http://13.53.131.159:3000
   ```

2. تسجيل الدخول:
   - Username: `admin`
   - Password: `admin123`

3. إنشاء Dashboard جديد:
   - Click `+` → `Dashboard`
   - Add new panel
   - في Query اكتب:
     ```promql
     ai_engine_attacks_total
     ```

4. جرب Dashboards جاهزة:
   - اذهب لـ Dashboards → Import
   - استخدم Dashboard ID: `1860` (Node Exporter)
   - أو `893` (Docker Dashboard)

---

## 💾 <a name="database-test"></a>6. اختبار قواعد البيانات

### **A. PostgreSQL - فحص الجداول:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
sudo docker exec cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -c '\dt'
"@
```

**النتيجة المتوقعة:** قائمة بجداول `attack_sessions` و `attack_actions`

---

### **B. PostgreSQL - إدراج بيانات اختبار:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
sudo docker exec cyber_mirage_postgres psql -U cybermirage -d cyber_mirage << 'EOSQL'
INSERT INTO attack_sessions (attacker_name, attacker_skill, total_steps, detected, origin)
VALUES ('test_attacker', 0.75, 10, false, 'test');

SELECT * FROM attack_sessions WHERE origin = 'test' LIMIT 1;
EOSQL
"@
```

---

### **C. Redis - فحص البيانات:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
echo '=== Redis Info ===' && \
sudo docker exec cyber_mirage_redis redis-cli -a changeme123 --no-auth-warning INFO stats | grep -E 'total_connections|total_commands'
"@
```

---

## ⚡ <a name="stress-test"></a>7. اختبار الأداء تحت الضغط

### **A. اختبار Stress على HTTP Honeypot:**

```powershell
# من جهازك - استخدم Apache Bench (ab)
# أو استخدم curl في loop

# الطريقة 1: PowerShell Loop
1..100 | ForEach-Object {
    Start-Job -ScriptBlock {
        curl -s "http://13.53.131.159:8080/test?id=$using:_" -o $null
    }
}
Get-Job | Wait-Job | Remove-Job
```

---

### **B. اختبار Concurrent SSH Attacks:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
# إنشاء script اختبار
cat > /tmp/ssh_stress.sh << 'SCRIPT'
#!/bin/bash
for i in {1..50}; do
    (
        sshpass -p 'wrong_password' ssh -o StrictHostKeyChecking=no \
        -o ConnectTimeout=5 -p 2222 root@localhost 2>/dev/null
    ) &
done
wait
SCRIPT

chmod +x /tmp/ssh_stress.sh && \
bash /tmp/ssh_stress.sh
"@
```

---

### **C. مراقبة الأداء أثناء الاختبار:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
echo '=== System Resources ===' && \
sudo docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'
"@
```

---

## 📈 **قياس الفعالية - KPIs**

### **1. معدل التقاط الهجمات:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
echo '=== Attack Capture Rate ===' && \
sudo docker logs cyber_mirage_honeypots --since 1h 2>&1 | grep -c 'connection' && \
echo 'attacks captured in last hour'
"@
```

---

### **2. زمن الاستجابة (Response Time):**

```powershell
# قياس زمن استجابة Dashboard
Measure-Command {
    curl -s http://13.53.131.159:8501 -o $null
}

# قياس زمن استجابة AI Engine
Measure-Command {
    curl -s http://13.53.131.159:8001/health -o $null
}
```

---

### **3. استخدام الموارد (Resource Utilization):**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
echo '=== CPU & Memory Usage ===' && \
sudo docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}'
"@
```

**معايير الأداء الجيد:**
- CPU < 50% في الوضع العادي
- Memory < 70% لكل حاوية
- Response Time < 1s للـ API endpoints

---

### **4. معدل نجاح AI Engine:**

```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
curl -s http://localhost:8001/metrics | grep -E 'ai_engine_(attacks|errors)'
"@
```

**حساب Success Rate:**
```
Success Rate = (attacks_total - errors_total) / attacks_total × 100%
```

---

## 🎬 **سيناريو اختبار كامل (End-to-End Test)**

### **الهدف:** محاكاة هجوم كامل وتتبعه عبر النظام

```powershell
# 1. إرسال هجمات SSH متعددة
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
for i in {1..10}; do
    timeout 2 ssh -o ConnectTimeout=1 -p 2222 root@localhost 2>&1 | head -1
    sleep 1
done
"@

# 2. التحقق من التسجيل في Logs
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
echo '=== Honeypot Logs ===' && \
sudo docker logs cyber_mirage_honeypots --tail 30 | grep -i ssh
"@

# 3. التحقق من معالجة AI Engine
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
echo '=== AI Engine Processing ===' && \
curl -s http://localhost:8001/metrics | grep ai_engine_attacks_total
"@

# 4. التحقق من البيانات في PostgreSQL
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
echo '=== Database Records ===' && \
sudo docker exec cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -c \
'SELECT COUNT(*) FROM attack_sessions WHERE start_time > NOW() - INTERVAL '\''10 minutes'\'';'
"@

# 5. فحص Dashboard
Write-Host "افتح Dashboard وشوف الإحصائيات الجديدة:"
Write-Host "http://13.53.131.159:8501" -ForegroundColor Green

# 6. فحص Grafana Metrics
Write-Host "افتح Grafana وشوف الـ Graphs:"
Write-Host "http://13.53.131.159:3000" -ForegroundColor Green
```

---

## ✅ **Checklist - النظام يعمل بفعالية إذا:**

- [ ] جميع الحاويات `healthy`
- [ ] Dashboard يفتح بدون أخطاء
- [ ] Honeypots تسجل الاتصالات
- [ ] AI Engine يعالج الهجمات (attacks_total يزيد)
- [ ] PostgreSQL يحفظ البيانات
- [ ] Redis يخزن threat intelligence
- [ ] Prometheus يجمع metrics من جميع الخدمات
- [ ] Grafana يعرض البيانات بشكل صحيح
- [ ] Response Time أقل من ثانية
- [ ] CPU Usage أقل من 50%
- [ ] لا توجد أخطاء في logs

---

## 🚨 **في حالة وجود مشاكل:**

### **مشكلة: Dashboard لا يفتح**
```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
sudo docker logs cyber_mirage_dashboard --tail 50
"@
```

### **مشكلة: AI Engine لا يعالج الهجمات**
```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
sudo docker logs cyber_mirage_ai --tail 50
"@
```

### **مشكلة: Honeypots لا تستجيب**
```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
sudo docker logs cyber_mirage_honeypots --tail 50
"@
```

### **إعادة تشغيل خدمة معينة:**
```powershell
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 @"
cd /opt/cyber_mirage && \
sudo docker compose -f docker-compose.production.yml restart <service-name>
"@
```

---

## 📞 **معلومات مهمة:**

- **IP السيرفر:** `13.53.131.159`
- **Dashboard:** http://13.53.131.159:8501
- **Grafana:** http://13.53.131.159:3000 (admin/admin123)
- **Prometheus:** http://13.53.131.159:9090
- **SSH:** `ssh -i key ubuntu@13.53.131.159`

---

**جرب الاختبارات دي وشوف النتايج - لو في أي مشكلة قولي!** 🚀
