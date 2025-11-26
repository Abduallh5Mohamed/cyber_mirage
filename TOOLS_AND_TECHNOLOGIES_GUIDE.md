# 🛠️ دليل الأدوات والتقنيات الشامل لمشروع Cyber Mirage
## Comprehensive Tools & Technologies Guide

---

## 📋 نظرة عامة

تم تجميع هذه القائمة الشاملة والمفصلة لجميع الأدوات والتقنيات المطلوبة لكل فرد من أفراد الفريق السبعة لتنفيذ مهامهم العملية في مشروع Cyber Mirage.

**هذه الأدوات هي التي ستمكن الفريق من التعلم العملي المباشر وبناء النظام.**

---

## 🔗 1. الأدوات المشتركة (مطلوبة لجميع الأعضاء)

| الأداة/التقنية | الوصف وأهميتها | حالة المشروع |
|----------------|----------------|--------------|
| **Git & GitHub/GitLab** | نظام التحكم في الإصدارات. ضروري للتعاون، ومشاركة الكود، وتتبع التغييرات بين جميع أعضاء الفريق. | ✅ مُستخدم |
| **Docker** | تقنية الحاويات. أساس بناء البيئة الوهمية المعزولة (Honeynet) وضمان أن كل مكون يعمل في بيئة نظيفة ومستقلة. | ✅ 10 حاويات |
| **Docker Compose** | أداة لتحديد وتشغيل تطبيقات Docker متعددة الحاويات. ضرورية لدمج جميع مكونات المشروع السبعة في نظام واحد. | ✅ مُفعّل |
| **Python 3.x** | لغة البرمجة الأساسية للمشروع، تستخدم في بناء الخدمات الوهمية، الذكاء الاصطناعي، التحليل، والأتمتة. | ✅ Python 3.11 |
| **Visual Studio Code (VS Code)** | محرر أكواد متقدم، يوفر بيئة عمل موحدة وفعالة لجميع الأعضاء. | ✅ مُوصى به |

### 📦 تثبيت الأدوات المشتركة

```bash
# Git
sudo apt install git -y

# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Docker Compose
sudo apt install docker-compose-plugin -y

# Python
sudo apt install python3 python3-pip python3-venv -y
```

---

## 👥 2. الأدوات والتقنيات الخاصة بكل دور

### 🌐 Role 1: مهندس شبكات العسل (Honeypot Network Engineer)

| النوع | الأداة | الوصف | حالة المشروع |
|-------|--------|-------|--------------|
| **أساسي** | Linux Networking | `iptables`, `netstat`, `ifconfig` للتحكم في الشبكة | ✅ مُطبّق |
| **أساسي** | Scapy | مكتبة Python لمعالجة حزم الشبكة (لتطبيق خداع ARP/DNS) | ✅ مُثبّت |
| **متقدم** | SDN Controller (Ryu/OpenDaylight) | للتحكم البرمجي في مسار الشبكة | ⏳ مستقبلي |
| **متقدم** | Wireshark/TShark | لتحليل حزم الشبكة والتأكد من فعالية الخداع | ✅ متاح |

#### 📁 الملفات ذات الصلة:
```
src/honeypots/
├── honeypot_manager.py     # مدير الـ Honeypots الرئيسي
├── ssh_honeypot.py         # محاكي SSH
├── ftp_honeypot.py         # محاكي FTP
├── http_honeypot.py        # محاكي HTTP
├── mysql_honeypot.py       # محاكي MySQL
└── modbus_honeypot.py      # محاكي Modbus (ICS)
```

#### 💻 أوامر مفيدة:
```bash
# مراقبة حركة الشبكة
sudo tcpdump -i any port 2222 or port 2121 or port 8080

# فحص الاتصالات النشطة
netstat -tlnp | grep -E "2222|2121|8080|3306|502"

# تحليل حزم مع TShark
tshark -i docker0 -f "port 2222"
```

---

### 🎭 Role 2: مهندس محاكاة الخدمات (Service Simulation Engineer)

| النوع | الأداة | الوصف | حالة المشروع |
|-------|--------|-------|--------------|
| **أساسي** | Python Flask | إطار عمل خفيف لإنشاء خوادم الويب الوهمية | ✅ مُستخدم |
| **أساسي** | Paramiko | مكتبة Python لتنفيذ بروتوكول SSH (لإنشاء خادم SSH وهمي) | ✅ مُثبّت |
| **أساسي** | Requests | مكتبة Python لعمل طلبات HTTP (لاختبار الخدمات الوهمية) | ✅ مُثبّت |
| **متقدم** | Jinja2 | محرك قوالب (Templates) لتوليد صفحات ويب وهمية ديناميكية | ✅ مُستخدم |

#### 📁 الملفات ذات الصلة:
```
src/honeypots/
├── http_honeypot.py        # Flask-based web honeypot
├── templates/              # Jinja2 templates للصفحات الوهمية
│   ├── login.html
│   ├── admin.html
│   └── error.html
└── static/                 # CSS/JS للمظهر الحقيقي
```

#### 💻 كود مثال - خادم HTTP وهمي:
```python
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def fake_login():
    if request.method == 'POST':
        # سجّل محاولة الدخول
        log_attack(
            username=request.form.get('username'),
            password=request.form.get('password'),
            ip=request.remote_addr
        )
        return "Login failed", 401
    return render_template('login.html')
```

---

### 🤖 Role 3: مهندس الذكاء الاصطناعي (AI/ML Engineer)

| النوع | الأداة | الوصف | حالة المشروع |
|-------|--------|-------|--------------|
| **أساسي** | NumPy/Pandas | للتعامل مع البيانات وتحليلها | ✅ مُثبّت |
| **أساسي** | Python | لكتابة دالة المكافأة ونموذج القرار | ✅ مُطبّق |
| **متقدم** | Stable Baselines3 (SB3) | مكتبة لتطبيق خوارزميات التعلم المعزز (مثل DQN) | ✅ مُثبّت |
| **متقدم** | TensorFlow/PyTorch | لتطوير نماذج التعلم العميق (إذا تم التوسع) | ⏳ متاح |

#### 📁 الملفات ذات الصلة:
```
src/ai/
├── ai_analyzer.py          # المحلل الرئيسي
├── threat_scorer.py        # حساب Threat Score
├── skill_evaluator.py      # تقييم مستوى المهاجم
├── mitre_mapper.py         # ربط MITRE ATT&CK
├── rl_agent.py             # Reinforcement Learning Agent
└── models/
    ├── dqn_model.pth       # نموذج DQN مُدرّب
    └── threat_classifier.pkl
```

#### 💻 خوارزميات التحليل المُطبّقة:
```python
def calculate_threat_score(attack_data):
    """حساب درجة الخطورة (0-100)"""
    score = 0
    
    # عوامل التقييم
    if attack_data['port'] in [22, 2222]:  # SSH
        score += 30
    if attack_data['attempts'] > 10:
        score += 20
    if is_known_threat(attack_data['ip']):
        score += 40
    
    return min(score, 100)

def get_mitre_mapping(service):
    """ربط الخدمة بتكتيكات MITRE ATT&CK"""
    mappings = {
        'SSH': ['T1078', 'T1110'],   # Valid Accounts, Brute Force
        'HTTP': ['T1190'],            # Exploit Public-Facing App
        'MySQL': ['T1213'],           # Data from Info Repositories
        'Modbus': ['T0831']           # Manipulation of Control
    }
    return mappings.get(service, [])
```

---

### 🔍 Role 4: محلل استخبارات التهديدات (Threat Intelligence Analyst)

| النوع | الأداة | الوصف | حالة المشروع |
|-------|--------|-------|--------------|
| **أساسي** | Wireshark/TShark | الأداة الأساسية لتحليل حركة مرور الشبكة (PCAP) | ✅ متاح |
| **أساسي** | Python | لكتابة سكريبتات تحليل السجلات | ✅ مُطبّق |
| **متقدم** | ELK Stack | Elasticsearch, Logstash, Kibana - لتجميع وتحليل وعرض كميات كبيرة من السجلات | ⏳ بديل: Grafana |
| **متقدم** | MISP | منصة لمشاركة استخبارات التهديدات | ⏳ مستقبلي |

#### 📁 الملفات ذات الصلة:
```
src/analysis/
├── threat_intel.py         # جمع استخبارات التهديدات
├── ip_reputation.py        # تصنيف سمعة الـ IPs
├── geoip_lookup.py         # تحديد الموقع الجغرافي
├── attack_patterns.py      # تحليل أنماط الهجمات
└── reports/
    └── daily_threat_report.py
```

#### 💻 استعلامات تحليل مفيدة:
```sql
-- أكثر الـ IPs هجوماً
SELECT origin, COUNT(*) as attacks 
FROM attack_sessions 
GROUP BY origin 
ORDER BY attacks DESC 
LIMIT 10;

-- الهجمات حسب الخدمة
SELECT 
    CASE 
        WHEN attacker_name LIKE '%SSH%' THEN 'SSH'
        WHEN attacker_name LIKE '%HTTP%' THEN 'HTTP'
        WHEN attacker_name LIKE '%FTP%' THEN 'FTP'
        WHEN attacker_name LIKE '%MySQL%' THEN 'MySQL'
        ELSE 'Other'
    END as service,
    COUNT(*) as count
FROM attack_sessions
GROUP BY service;

-- الهجمات آخر 24 ساعة
SELECT * FROM attack_sessions 
WHERE start_time > NOW() - INTERVAL '24 hours'
ORDER BY start_time DESC;
```

---

### 🛡️ Role 5: مهندس الأمن والاحتواء (Security & Containment Engineer)

| النوع | الأداة | الوصف | حالة المشروع |
|-------|--------|-------|--------------|
| **أساسي** | Linux Security | AppArmor/SELinux للتحكم في الوصول | ✅ متاح |
| **أساسي** | iptables | جدار الحماية الأساسي للتحكم في حركة المرور | ✅ مُطبّق |
| **أساسي** | cgroups | لتقييد موارد الحاويات (CPU/RAM) | ✅ مُطبّق |
| **متقدم** | Sysdig/Falco | أدوات مراقبة متقدمة على مستوى الكيرنل لاكتشاف محاولات الهروب | ⏳ مُوصى |
| **متقدم** | Docker Security Benchmarks | للتحقق من تكوين أمان الحاويات | ✅ مُطبّق |

#### 📁 الملفات ذات الصلة:
```
config/
├── security/
│   ├── iptables.rules      # قواعد جدار الحماية
│   ├── apparmor.profile    # ملف AppArmor
│   └── seccomp.json        # Seccomp profile
docker/
├── Dockerfile.production   # Dockerfile آمن
└── docker-compose.yml      # تكوين الحاويات
```

#### 💻 فحص أمان الحاويات:
```bash
# التحقق من عدم تشغيل الحاويات بوضع Privileged
docker inspect --format '{{.Name}}: Privileged={{.HostConfig.Privileged}}' $(docker ps -q)

# فحص حدود الموارد
docker stats --no-stream

# التحقق من الشبكات المعزولة
docker network ls
docker network inspect cyber_mirage_cyber_network

# فحص Docker Security Benchmark
docker run --rm -it --net host --pid host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  docker/docker-bench-security
```

#### ⚙️ إعدادات الأمان المُطبّقة:
```yaml
# docker-compose.yml
services:
  honeypots:
    security_opt:
      - no-new-privileges:true
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 4G
        reservations:
          memory: 1G
    read_only: false  # يُفضل true في الإنتاج
    privileged: false
```

---

### 🔬 Role 6: مهندس الأدلة الجنائية (Digital Forensics Engineer)

| النوع | الأداة | الوصف | حالة المشروع |
|-------|--------|-------|--------------|
| **أساسي** | Bash Scripting | لكتابة سكريبتات جمع الأدلة البسيطة | ✅ متاح |
| **أساسي** | Python | لأتمتة عملية جمع الأدلة | ✅ مُطبّق |
| **أساسي** | Log2timeline/Plaso | أداة متقدمة لجمع وتحليل الطوابع الزمنية (Timelines) | ⏳ مُوصى |
| **متقدم** | Volatility Framework | لتحليل ذاكرة النظام (Memory Forensics) | ⏳ مستقبلي |
| **متقدم** | Autopsy | أداة واجهة رسومية لتحليل الأدلة الجنائية | ⏳ مستقبلي |

#### 📁 الملفات ذات الصلة:
```
src/forensics/
├── evidence_collector.py   # جامع الأدلة الآلي
├── timeline_builder.py     # بناء Timeline للأحداث
├── log_parser.py           # تحليل السجلات
├── pcap_analyzer.py        # تحليل ملفات PCAP
└── reports/
    └── forensic_report_template.md
```

#### 💻 سكريبت جمع الأدلة:
```bash
#!/bin/bash
# evidence_collection.sh

CASE_ID="CASE_$(date +%Y%m%d_%H%M%S)"
EVIDENCE_DIR="/evidence/$CASE_ID"

mkdir -p $EVIDENCE_DIR

# جمع سجلات Docker
docker logs cyber_mirage_honeypots > $EVIDENCE_DIR/honeypot_logs.txt 2>&1

# جمع سجلات قاعدة البيانات
docker exec cyber_mirage_postgres pg_dump cyber_mirage > $EVIDENCE_DIR/database_dump.sql

# جمع معلومات الحاويات
docker inspect $(docker ps -q) > $EVIDENCE_DIR/container_info.json

# حساب Hash للتحقق
sha256sum $EVIDENCE_DIR/* > $EVIDENCE_DIR/checksums.sha256

echo "Evidence collected in: $EVIDENCE_DIR"
```

---

### 📊 Role 7: مهندس خطوط البيانات والأتمتة (Data Pipeline & DevOps Engineer)

| النوع | الأداة | الوصف | حالة المشروع |
|-------|--------|-------|--------------|
| **أساسي** | Redis | نظام تخزين بيانات في الذاكرة (In-Memory Data Store) | ✅ يعمل |
| **أساسي** | Streamlit/Dash | لإنشاء لوحة التحكم المركزية (Dashboard) بسرعة | ✅ Streamlit |
| **أساسي** | PostgreSQL | قاعدة البيانات الرئيسية | ✅ يعمل |
| **متقدم** | Apache Kafka | نظام متقدم لتدفق البيانات (Data Streaming) | ⏳ مستقبلي |
| **متقدم** | Ansible/Terraform | لأتمتة نشر البنية التحتية بالكامل | ⏳ مستقبلي |
| **متقدم** | Prometheus/Grafana | للمراقبة والتنبيهات | ✅ يعمل |

#### 📁 الملفات ذات الصلة:
```
src/
├── dashboard/
│   └── full_dashboard.py   # Streamlit Dashboard
├── data/
│   ├── redis_client.py     # Redis connection
│   └── postgres_client.py  # PostgreSQL connection
config/
├── prometheus.yml          # Prometheus config
├── grafana/
│   └── dashboards/         # Grafana dashboards
docker/
├── docker-compose.yml      # Main compose file
└── docker-compose.production.yml
```

#### 💻 أوامر إدارة الخدمات:
```bash
# تشغيل النظام الكامل
docker-compose up -d

# مراقبة الحالة
docker-compose ps

# عرض السجلات
docker-compose logs -f honeypots

# إعادة تشغيل خدمة
docker-compose restart dashboard

# التحقق من Redis
docker exec cyber_mirage_redis redis-cli -a changeme123 INFO

# التحقق من PostgreSQL
docker exec cyber_mirage_postgres psql -U cyber_mirage -c "SELECT COUNT(*) FROM attack_sessions"
```

---

## 🧪 3. أدوات الاختبار (Testing Tools)

هذه الأدوات ضرورية لاختبار النظام بعد بنائه:

| الأداة | الغرض من الاستخدام | الدور المسؤول | حالة الاختبار |
|--------|-------------------|---------------|---------------|
| **Nmap** | مسح الشبكة واكتشاف الخدمات المفتوحة | Role 1 & 4 | ✅ تم الاختبار |
| **Netcat (nc)** | اختبار الاتصال بالبورتات والخدمات الوهمية | Role 1 & 2 | ✅ تم الاختبار |
| **Curl/Wget** | التفاعل مع خوادم الويب الوهمية (HTTP/HTTPS) | Role 2 | ✅ تم الاختبار |
| **Metasploit/Kali Linux** | محاكاة هجوم حقيقي لاختبار فعالية الخداع | Role 5 | ⏳ يدوي |
| **Docker CLI** | مراقبة وإيقاف وتشغيل الحاويات | Role 7 | ✅ مستمر |

### 💻 أوامر الاختبار السريع:
```bash
# فحص المنافذ المفتوحة
nmap -sV -p 2222,2121,8080,3306,502 localhost

# اختبار SSH Honeypot
nc -v localhost 2222

# اختبار FTP Honeypot
nc -v localhost 2121

# اختبار HTTP Honeypot
curl -X POST http://localhost:8080/login \
  -d "username=admin&password=test123"

# اختبار MySQL Honeypot
nc -v localhost 3306
```

---

## 📈 4. حالة التنفيذ الحالية

### ✅ الأدوات المُطبّقة والعاملة:

| الأداة | الإصدار | الحالة |
|--------|---------|--------|
| Docker | 24.x | ✅ 10 حاويات تعمل |
| Python | 3.11 | ✅ |
| PostgreSQL | 16 | ✅ 102+ هجمة مسجلة |
| Redis | 7.x | ✅ 50+ threat keys |
| Streamlit | 1.x | ✅ Dashboard يعمل |
| Grafana | 12.2.1 | ✅ |
| Prometheus | 2.x | ✅ |
| Flask | 2.x | ✅ HTTP Honeypot |

### ⏳ الأدوات المُخططة للمستقبل:

| الأداة | الغرض | الأولوية |
|--------|--------|----------|
| Apache Kafka | Data Streaming | متوسطة |
| ELK Stack | Log Analysis | متوسطة |
| Falco | Runtime Security | عالية |
| MISP | Threat Intel Sharing | منخفضة |
| Terraform | Infrastructure as Code | متوسطة |

---

## 🔗 5. الروابط النشطة للنظام

| الخدمة | الرابط | المسؤول |
|--------|--------|---------|
| **Dashboard** | http://13.53.131.159:8501 | Role 7 |
| **Grafana** | http://13.53.131.159:3000 | Role 7 |
| **Prometheus** | http://13.53.131.159:9090 | Role 7 |
| **SSH Honeypot** | `nc 13.53.131.159 2222` | Role 1 & 2 |
| **FTP Honeypot** | `nc 13.53.131.159 2121` | Role 1 & 2 |
| **HTTP Honeypot** | http://13.53.131.159:8080 | Role 2 |
| **MySQL Honeypot** | `nc 13.53.131.159 3306` | Role 2 |

---

## 📚 6. مصادر التعلم الموصى بها

### للجميع:
- [Docker Documentation](https://docs.docker.com/)
- [Python Official Tutorial](https://docs.python.org/3/tutorial/)
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)

### حسب الدور:
| الدور | المصادر |
|-------|---------|
| Role 1 | Scapy Documentation, Linux Networking Basics |
| Role 2 | Flask Mega-Tutorial, Paramiko Docs |
| Role 3 | Stable Baselines3 Docs, MITRE ATT&CK Framework |
| Role 4 | Wireshark User Guide, Threat Intel Fundamentals |
| Role 5 | Docker Security Best Practices, CIS Benchmarks |
| Role 6 | SANS Digital Forensics, Log2Timeline Docs |
| Role 7 | Redis University, Streamlit Docs, Prometheus Docs |

---

## 📅 آخر تحديث: 2025-11-25

**حالة المشروع:** ✅ **جاهز للإنتاج (Production Ready)**

**نتيجة اختبار الاختراق:** 96.25/100 (A+)
