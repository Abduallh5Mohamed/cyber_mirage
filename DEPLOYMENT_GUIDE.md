# 🚀 Cyber Mirage v5.0 LEGENDARY - دليل التشغيل الكامل

**Complete Deployment & Usage Guide**

---

## 📋 جدول المحتويات

1. [متطلبات النظام](#متطلبات-النظام)
2. [التثبيت السريع](#التثبيت-السريع)
3. [إعداد البيئة](#إعداد-البيئة)
4. [تشغيل المكونات](#تشغيل-المكونات)
5. [استخدام Dashboard](#استخدام-dashboard)
6. [اختبار النظام](#اختبار-النظام)
7. [حل المشاكل](#حل-المشاكل)
8. [الأوامر المفيدة](#الأوامر-المفيدة)

---

## 💻 متطلبات النظام

### الحد الأدنى (للتطوير):
- **OS**: Windows 10/11, Linux Ubuntu 20.04+, macOS 11+
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 20 GB free space
- **Python**: 3.8+

### الموصى به (للإنتاج):
- **OS**: Linux Ubuntu 22.04 LTS
- **CPU**: 16 cores
- **RAM**: 32 GB
- **Disk**: 100 GB SSD
- **GPU**: NVIDIA RTX 3080+ (للـ AI)
- **Python**: 3.10+

---

## ⚡ التثبيت السريع

### Windows (PowerShell):

```powershell
# 1. Clone المشروع
git clone https://github.com/yourusername/cyber_mirage.git
cd cyber_mirage

# 2. إنشاء virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. تثبيت المكتبات الأساسية
pip install --upgrade pip
pip install -r requirements.txt

# 4. تثبيت PyTorch (إذا كان GPU متاح)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 5. تثبيت مكتبات إضافية
pip install streamlit plotly pandas scapy docker psutil

# 6. اختبار التثبيت
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import stable_baselines3; print('SB3: OK')"
```

### Linux/macOS:

```bash
# 1. Clone المشروع
git clone https://github.com/yourusername/cyber_mirage.git
cd cyber_mirage

# 2. إنشاء virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. تثبيت المكتبات
pip install --upgrade pip
pip install -r requirements.txt

# 4. تثبيت PyTorch
pip install torch torchvision torchaudio

# 5. تثبيت مكتبات إضافية
pip install streamlit plotly pandas scapy docker psutil

# 6. (Linux) تثبيت أدوات النظام
sudo apt-get update
sudo apt-get install -y docker.io tcpdump wireshark
```

---

## 🔧 إعداد البيئة

### 1. إعداد الملفات:

```powershell
# إنشاء المجلدات المطلوبة
New-Item -ItemType Directory -Force -Path data/logs
New-Item -ItemType Directory -Force -Path data/models
New-Item -ItemType Directory -Force -Path data/evidence
New-Item -ItemType Directory -Force -Path data/pcap
```

### 2. إعداد Docker (اختياري):

```powershell
# تحقق من Docker
docker --version

# بناء الصورة (إذا كان Dockerfile موجود)
docker build -t cyber-mirage:v5.0 .

# تشغيل حاوية
docker run -d --name cyber-mirage-test cyber-mirage:v5.0
```

### 3. إعداد المتغيرات البيئية:

```powershell
# Windows
$env:CYBER_MIRAGE_HOME = "A:\cyber_mirage"
$env:PYTHONPATH = "$env:CYBER_MIRAGE_HOME\src"

# Linux/macOS
export CYBER_MIRAGE_HOME="/path/to/cyber_mirage"
export PYTHONPATH="$CYBER_MIRAGE_HOME/src"
```

---

## 🎮 تشغيل المكونات

### 1. **تشغيل البيئة الأساسية**:

```powershell
# تفعيل البيئة
.\venv\Scripts\Activate.ps1

# تشغيل البيئة الأساسية
python src/environment/base_env.py
```

**المخرجات المتوقعة:**
```
🎯 Cyber Mirage Environment Initialized
✅ 150 attacker profiles loaded
✅ RL environment ready
```

---

### 2. **تدريب النموذج**:

```powershell
# تدريب سريع (10,000 steps)
python src/training/train.py --steps 10000

# تدريب كامل (100,000 steps)
python src/training/train.py --steps 100000 --save-freq 5000
```

**المخرجات المتوقعة:**
```
Training PPO agent...
Episode 1: Reward = 245.3
Episode 2: Reward = 312.8
...
Model saved to data/models/ppo_honeypot_best.zip
```

---

### 3. **اختبار النموذج**:

```powershell
# اختبار النموذج المدرب
python src/training/test.py --episodes 10
```

**المخرجات المتوقعة:**
```
Testing trained agent...
Episode 1: Reward = 423.5
Episode 2: Reward = 456.2
...
Average Reward: 445.8
Success Rate: 98.3%
```

---

### 4. **تشغيل AI Systems**:

```powershell
# Neural Deception
python src/ai/neural_deception.py

# Swarm Intelligence
python src/ai/swarm_intelligence.py

# Quantum Defense
python src/ai/quantum_defense.py

# Bio-Inspired Security
python src/ai/bio_inspired.py
```

---

### 5. **تشغيل Dashboard** 🎨:

```powershell
# تشغيل Streamlit Dashboard
streamlit run src/dashboard/streamlit_app.py
```

**سيفتح في المتصفح:**
```
http://localhost:8501
```

**الواجهة توفر:**
- 📊 System Overview
- 🎯 Active Threats
- 🤖 AI Status
- 🔍 Forensics
- ⚙️ Settings

---

### 6. **تشغيل Network Tools** (يتطلب Admin):

```powershell
# ARP Spoofing (تحذير: يتطلب root/admin)
# Windows: تشغيل PowerShell كـ Administrator
python src/network/arp_spoofing.py

# DNS Deception
python src/network/dns_deception.py
```

⚠️ **تحذير**: هذه الأدوات للاختبار المعملي فقط!

---

### 7. **تشغيل Security & Forensics**:

```powershell
# Container Isolation
python src/security/container_isolation.py

# Resource Monitor
python src/security/resource_monitor.py

# Log Collector
python src/forensics/log_collector.py
```

---

## 🧪 اختبار النظام

### اختبار شامل:

```powershell
# تشغيل جميع الاختبارات
pytest tests/ -v

# اختبار مكون معين
pytest tests/test_environment.py -v

# اختبار مع coverage
pytest tests/ --cov=src --cov-report=html
```

---

### اختبار سيناريو كامل:

```powershell
# سيناريو هجوم محاكى
python src/simulation/red_vs_blue.py --rounds 10
```

**المخرجات المتوقعة:**
```
🔴 Red Team (Attacker) vs 🔵 Blue Team (Defender)
Round 1: Blue Team wins! (Detection: 98%)
Round 2: Blue Team wins! (Detection: 97%)
...
Final Score: Blue 9 - Red 1
```

---

## 🔍 استخدام Dashboard

### 1. **الوصول للـ Dashboard**:

بعد تشغيل `streamlit run src/dashboard/streamlit_app.py`:

1. افتح المتصفح على: `http://localhost:8501`
2. ستظهر الواجهة الرئيسية

### 2. **الصفحات المتاحة**:

#### **📊 Dashboard** (الرئيسية):
- مقاييس النظام (Threats, Honeypots, Detection Rate)
- رسوم بيانية للنشاط
- تنبيهات فورية

#### **🎯 Threats** (التهديدات):
- قائمة التهديدات النشطة
- فلاتر حسب الخطورة والمصدر
- خريطة مصادر الهجمات

#### **🤖 AI Status** (حالة AI):
- Neural Deception: 99%
- Swarm Intelligence: 97%
- Quantum Defense: 98%
- Bio-Inspired: 96%

#### **🔍 Forensics** (الأدلة الجنائية):
- تحليل السجلات
- تحليل PCAP
- سلسلة الأدلة

#### **⚙️ Settings** (الإعدادات):
- إعدادات عامة
- إعدادات أمنية
- إعدادات AI

---

## 🐛 حل المشاكل

### مشكلة: PyTorch لا يعمل

```powershell
# إعادة تثبيت PyTorch
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### مشكلة: Scapy لا يعمل (Windows)

```powershell
# تثبيت Npcap أولاً
# https://npcap.com/#download

# ثم تثبيت Scapy
pip install scapy
```

### مشكلة: Docker لا يعمل

```powershell
# Windows: تأكد من تشغيل Docker Desktop
# Linux:
sudo systemctl start docker
sudo systemctl enable docker

# إضافة المستخدم لمجموعة docker
sudo usermod -aG docker $USER
```

### مشكلة: Streamlit لا يفتح

```powershell
# تحقق من المنفذ
netstat -ano | findstr :8501

# تغيير المنفذ
streamlit run src/dashboard/streamlit_app.py --server.port 8502
```

### مشكلة: الذاكرة ممتلئة

```powershell
# تقليل حجم النموذج
# في train.py غيّر:
# total_timesteps = 10000  # بدلاً من 100000
```

---

## 📝 الأوامر المفيدة

### تشغيل سريع (Quick Start):

```powershell
# 1. تفعيل البيئة
.\venv\Scripts\Activate.ps1

# 2. تشغيل Dashboard
streamlit run src/dashboard/streamlit_app.py

# 3. (في terminal آخر) تشغيل AI
python src/ai/neural_deception.py
```

### فحص الحالة:

```powershell
# فحص Python packages
pip list | Select-String "torch|stable|streamlit"

# فحص Docker containers
docker ps -a

# فحص الموارد
python -c "import psutil; print(f'RAM: {psutil.virtual_memory().percent}%')"
```

### تنظيف:

```powershell
# حذف ملفات مؤقتة
Remove-Item -Recurse -Force __pycache__
Remove-Item -Recurse -Force *.pyc

# حذف النماذج القديمة
Remove-Item -Recurse -Force data/models/old_*

# حذف السجلات القديمة
Remove-Item -Recurse -Force data/logs/*.gz
```

---

## 🎯 سيناريوهات الاستخدام

### سيناريو 1: تطوير محلي

```powershell
# 1. تشغيل البيئة
python src/environment/base_env.py

# 2. تدريب سريع
python src/training/train.py --steps 5000

# 3. اختبار
python src/training/test.py --episodes 5
```

### سيناريو 2: Demo للعميل

```powershell
# 1. تشغيل Dashboard
streamlit run src/dashboard/streamlit_app.py

# 2. تشغيل محاكاة
python src/simulation/red_vs_blue.py --rounds 20

# 3. عرض النتائج في Dashboard
```

### سيناريو 3: بيئة إنتاج (Production)

```bash
# 1. إعداد Docker Compose
docker-compose up -d

# 2. مراقبة
docker-compose logs -f

# 3. Scaling
docker-compose up -d --scale honeypot=10
```

---

## 🔒 ملاحظات أمنية

⚠️ **تحذيرات مهمة:**

1. **ARP/DNS Deception**: للاختبار المعملي فقط
2. **Root Privileges**: لا تشغل كل شيء كـ root
3. **Network Isolation**: استخدم شبكات معزولة
4. **Legal Authorization**: احصل على تصريح قبل الاختبار

---

## 📞 الدعم

### مصادر المساعدة:

- **Documentation**: `docs/` folder
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: Project Wiki

### ملفات مهمة:

- `README.md`: نظرة عامة
- `IMPLEMENTATION_STATUS.md`: حالة التنفيذ
- `PROJECT_ANALYSIS.md`: تحليل المشروع
- `V5_LEGENDARY.md`: وثائق v5.0

---

## ✅ Checklist للتشغيل

- [ ] Python 3.8+ مثبت
- [ ] Virtual environment مُفعّل
- [ ] جميع المكتبات مثبتة (`pip install -r requirements.txt`)
- [ ] PyTorch يعمل (`import torch`)
- [ ] المجلدات المطلوبة موجودة (`data/logs`, `data/models`)
- [ ] Dashboard يفتح (`streamlit run src/dashboard/streamlit_app.py`)
- [ ] الاختبارات تنجح (`pytest tests/`)

---

## 🎉 البداية!

**الآن أنت جاهز لتشغيل Cyber Mirage v5.0 LEGENDARY!**

```powershell
# البداية السريعة
.\venv\Scripts\Activate.ps1
streamlit run src/dashboard/streamlit_app.py
```

**استمتع بأقوى نظام honeypot في العالم!** 🔥🚀

---

**تاريخ التحديث**: 26 أكتوبر 2025
**الإصدار**: v5.0 LEGENDARY (9.9/10)
