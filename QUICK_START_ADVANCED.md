# 🚀 دليل سريع للمكونات المتقدمة
## Quick Start Guide for Advanced Components

---

## 📋 المحتويات

1. [🔍 OSINT Collector](#1-osint-collector)
2. [🌐 SDN Controller](#2-sdn-controller)
3. [⚛️ Real Quantum](#3-real-quantum)

---

## 1. 🔍 OSINT Collector
### جمع استخبارات من 5 مصادر مجانية!

### ✅ Setup (5 دقائق)

```bash
# 1. لا تحتاج تنصيب شيء! المكتبات موجودة في requirements.txt
pip install requests

# 2. سجل للحصول على API keys مجانية:
```

**المصادر المجانية:**
- ✅ **VirusTotal** (500 requests/day) - أفضل لفحص الملفات
  - https://www.virustotal.com/gui/join-us
  
- ✅ **AbuseIPDB** (1000 checks/day) - أفضل لفحص IPs
  - https://www.abuseipdb.com/register
  
- ✅ **AlienVault OTX** (Unlimited! 🎉) - أفضل للـ threat intelligence
  - https://otx.alienvault.com/
  
- ⚠️ **GreyNoise** (50 queries/day) - كشف الـ scanners
  - https://www.greynoise.io/
  
- 💰 **Shodan** (100 results/month) - بحث عن أجهزة
  - https://account.shodan.io/

### 🔑 تعيين API Keys

**Windows PowerShell:**
```powershell
$env:VIRUSTOTAL_API_KEY = "your_key_here"
$env:ABUSEIPDB_API_KEY = "your_key_here"
$env:ALIENVAULT_API_KEY = "your_key_here"
```

**Linux/macOS:**
```bash
export VIRUSTOTAL_API_KEY="your_key_here"
export ABUSEIPDB_API_KEY="your_key_here"
export ALIENVAULT_API_KEY="your_key_here"
```

### 🎯 الاستخدام

```python
from src.intelligence.osint_collector import OSINTCollector

# إنشاء Collector
collector = OSINTCollector()

# فحص IP
intel = collector.check_ip('185.220.101.45')

print(f"IP: {intel.ip}")
print(f"Reputation: {intel.reputation_score}/100")
print(f"Malicious: {intel.is_malicious}")
print(f"Country: {intel.country}")
print(f"Sources: {intel.sources}")
```

### 🧪 تجربة بدون API Keys

```python
from src.intelligence.osint_collector import MockOSINTCollector

# استخدام بيانات تجريبية
collector = MockOSINTCollector()
intel = collector.check_ip('185.220.101.45')
```

### 💡 نصائح

1. **ابدأ بـ AlienVault** - Unlimited و مجاني!
2. **AbuseIPDB** ممتاز لـ IPs المشبوهة
3. **VirusTotal** لفحص الملفات والروابط
4. حافظ على API keys سرية
5. راقب الـ rate limits

---

## 2. 🌐 SDN Controller
### ثلاث خيارات - اختر اللي يناسبك!

### Option A: 🎯 Ryu Controller (موصى به)

**المميزات:**
- ✅ OpenFlow 1.3 كامل
- ✅ يشتغل مع switches حقيقية
- ✅ تحليل متقدم للحزم
- ✅ سهل نسبياً

**التنصيب:**
```bash
pip install ryu
```

**التشغيل:**
```bash
# شغل الـ controller
ryu-manager src/network/sdn_controller.py
```

**الوظائف:**
- مراقبة جميع الحزم في الشبكة
- كشف Port Scanning و SYN floods
- إعادة توجيه المهاجمين للـ Honeypots تلقائياً
- حظر IPs خطرة

**إعدادات:**
```python
# في الكود
self.honeypot_ips = ['10.0.0.100', '10.0.0.101']
self.honeypot_port = 99  # Port على الـ Switch
```

### Option B: 🚀 OpenDaylight (متقدم)

**المميزات:**
- ✅ معيار صناعي
- ✅ REST API
- ✅ Multi-vendor support
- ⚠️ Setup معقد

**التنصيب:**
```bash
# تحميل OpenDaylight
wget https://nexus.opendaylight.org/content/repositories/opendaylight.release/org/opendaylight/integration/opendaylight/0.16.2/opendaylight-0.16.2.zip

# فك الضغط وتشغيل
unzip opendaylight-0.16.2.zip
cd opendaylight-0.16.2
./bin/karaf
```

**استخدام REST API:**
```python
import requests

# إضافة Flow
flow = {
    "priority": 100,
    "match": {"ipv4-source": "192.168.1.100"},
    "actions": [{"output-action": {"output-node-connector": "2"}}]
}

requests.put(
    "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/table/0/flow/1",
    json=flow,
    auth=('admin', 'admin')
)
```

### Option C: 🎓 Simplified SDN (للتعلم)

**المميزات:**
- ✅ بدون dependencies خارجية
- ✅ سهل الفهم
- ✅ للتجريب السريع
- ⚠️ وظائف محدودة

**الاستخدام:**
```python
from src.network.sdn_controller import SimplifiedSDN

sdn = SimplifiedSDN()

# قرار التوجيه
decision = sdn.route_packet('192.168.1.100', '8.8.8.8')
# Returns: 'FORWARD', 'HONEYPOT', or 'DROP'

# حظر IP
sdn.block_ip('45.142.120.50')
```

**التجربة:**
```bash
python src/network/sdn_controller.py
```

### 💡 أي واحد تختار؟

| الاستخدام | الخيار الموصى به |
|-----------|------------------|
| 🎓 التعلم والفهم | Simplified SDN |
| 🚀 Production | Ryu Controller |
| 🏢 Enterprise | OpenDaylight |
| 🧪 Testing | Simplified SDN |

---

## 3. ⚛️ Real Quantum Computer
### استخدم كمبيوتر كمي حقيقي من IBM!

### 🌐 التسجيل (مجاني!)

1. سجل في IBM Quantum:
   - https://quantum-computing.ibm.com/

2. احصل على API Token:
   - Dashboard → Account → API Token

3. اشترك في Free Plan:
   - ✅ 10 دقائق/شهر على أجهزة حقيقية
   - ✅ 127-qubit machines
   - ✅ Runtime service

### 🔧 التنصيب

```bash
pip install qiskit qiskit-ibm-runtime qiskit-aer
```

### 🔑 تعيين API Token

**Windows:**
```powershell
$env:IBM_QUANTUM_TOKEN = "your_token_from_ibm"
```

**Linux/macOS:**
```bash
export IBM_QUANTUM_TOKEN="your_token_from_ibm"
```

### 🎯 الاستخدام

**Mode 1: Real Quantum Computer 🔥**
```python
from src.ai.real_quantum import RealQuantumDefense

# اتصل بجهاز حقيقي
quantum = RealQuantumDefense(use_simulator=False)

# توليد مفتاح عشوائي TRUE RANDOM
key = quantum.generate_quantum_key(256)
print(f"Quantum Key: {key}")

# اختيار استراتيجية دفاع
strategy = quantum.quantum_random_defense(threat_level=0.85)
print(f"Strategy: {strategy}")

# مزامنة أنظمة بالتشابك الكمي
sync_codes = quantum.quantum_entanglement_sync(num_systems=3)
print(f"Synced: {sync_codes}")
```

**Mode 2: Simulator (للتجريب)**
```python
# لا يحتاج API token
quantum = RealQuantumDefense(use_simulator=True)

# نفس الوظائف بدون استهلاك الـ free tier
key = quantum.generate_quantum_key(256)
```

### 🎓 الوظائف المتاحة

```python
# 1. توليد مفاتيح عشوائية حقيقية
key = quantum.generate_quantum_key(key_length=256)
# يستخدم: Hadamard gates + Quantum measurement

# 2. اختيار استراتيجيات دفاع
strategy = quantum.quantum_random_defense(threat_level=0.7)
# الاستراتيجيات: REDIRECT_HONEYPOT, BLOCK_IMMEDIATELY, 
#                 MONITOR_CLOSELY, DEPLOY_DECOY, إلخ...

# 3. مزامنة أنظمة
sync_codes = quantum.quantum_entanglement_sync(num_systems=4)
# يستخدم: Bell States (CNOT gates)

# 4. أرقام عشوائية
number = quantum.quantum_random_number(min_val=1, max_val=100)

# 5. حالة الجهاز
status = quantum.get_backend_status()
print(f"Device: {status['name']}")
print(f"Qubits: {status['qubits']}")

# 6. إحصائيات
stats = quantum.get_stats()
```

### 💡 متى تستخدم الجهاز الحقيقي؟

**استخدم Real Quantum في:**
- ✅ توليد مفاتيح تشفير
- ✅ اختيارات عشوائية مهمة
- ✅ مزامنة أنظمة حساسة

**استخدم Simulator في:**
- ✅ التطوير والتجريب
- ✅ Unit tests
- ✅ Demos

### ⚠️ ملاحظات مهمة

1. **Free Tier محدود:** 10 دقائق/شهر
2. **الانتظار:** قد تنتظر في queue
3. **Noise:** الأجهزة الحقيقية فيها noise
4. **Transpilation:** الكود يتحول تلقائياً للجهاز

### 🎯 مثال عملي

```python
from src.ai.real_quantum import RealQuantumDefense
import time

# اتصل بالجهاز
quantum = RealQuantumDefense(use_simulator=False)

# حالة الجهاز
status = quantum.get_backend_status()
print(f"Connected to: {status['name']}")
print(f"Queue: {status['pending_jobs']} jobs")

# ولد 5 مفاتيح
keys = []
for i in range(5):
    key = quantum.generate_quantum_key(128)
    keys.append(key)
    print(f"Key {i+1}: {key[:32]}...")
    time.sleep(1)  # لتجنب rate limiting

# اختر استراتيجيات
threats = [0.2, 0.5, 0.8, 0.95]
for threat in threats:
    strategy = quantum.quantum_random_defense(threat)
    print(f"Threat {threat:.2f} → {strategy}")

# إحصائيات
stats = quantum.get_stats()
print(f"\nTotal quantum operations: {stats['quantum_operations']}")
print(f"Keys generated: {stats['keys_generated']}")
```

---

## 🎯 Integration مع النظام الرئيسي

### دمج OSINT مع Threat Intelligence

```python
from src.intelligence.osint_collector import OSINTCollector
from src.ai.neural_deception import NeuralDeception

osint = OSINTCollector()
neural = NeuralDeception()

# فحص IP
intel = osint.check_ip(attacker_ip)

# تحديث AI بناءً على OSINT
if intel.is_malicious:
    neural.update_threat_level(intel.reputation_score / 100)
```

### دمج SDN مع Deception

```python
from src.network.sdn_controller import SimplifiedSDN
from src.deception.honeypot_manager import HoneypotManager

sdn = SimplifiedSDN()
honeypots = HoneypotManager()

# عند كشف مهاجم
if sdn.route_packet(src_ip, dst_ip) == 'HONEYPOT':
    honeypots.redirect_attacker(src_ip)
```

### دمج Quantum مع AI

```python
from src.ai.real_quantum import RealQuantumDefense
from src.ai.swarm_intelligence import SwarmIntelligence

quantum = RealQuantumDefense(use_simulator=True)
swarm = SwarmIntelligence()

# استخدام عشوائية كمية في القرارات
strategy = quantum.quantum_random_defense(threat_level=0.75)

if strategy == 'SWARM_DEFENSE':
    swarm.coordinate_defense()
```

---

## 📊 مراقبة الأداء

### OSINT Stats

```python
collector = OSINTCollector()

# بعد عدة فحوصات
cache = collector.get_cached_intelligence()
print(f"Cached IPs: {len(cache)}")

for ip, intel in cache.items():
    if intel.is_malicious:
        print(f"🚨 {ip}: {intel.reputation_score}/100")
```

### SDN Stats

```python
from src.network.sdn_controller import SimplifiedSDN

sdn = SimplifiedSDN()

# الإحصائيات متاحة في logs
# يتم طباعتها تلقائياً كل 30 ثانية
```

### Quantum Stats

```python
quantum = RealQuantumDefense()

stats = quantum.get_stats()
print(f"Operations: {stats['quantum_operations']}")
print(f"Keys: {stats['keys_generated']}")
print(f"Decisions: {stats['decisions_made']}")
print(f"Entanglements: {stats['entanglements_created']}")
```

---

## 🐛 Troubleshooting

### OSINT Issues

**Problem:** "Rate limit exceeded"
```python
# Solution: استخدم source واحد أو انتظر
import time
time.sleep(60)  # انتظر دقيقة
```

**Problem:** "No API keys configured"
```python
# Solution: استخدم Mock للتجريب
from src.intelligence.osint_collector import MockOSINTCollector
collector = MockOSINTCollector()
```

### SDN Issues

**Problem:** "Module 'ryu' not found"
```bash
# Solution: نصب Ryu
pip install ryu
```

**Problem:** "No switches connected"
```bash
# Solution: استخدم Mininet للتجريب
sudo mn --controller=remote,ip=127.0.0.1
```

### Quantum Issues

**Problem:** "Job queue too long"
```python
# Solution: استخدم simulator أو انتظر
quantum = RealQuantumDefense(use_simulator=True)
```

**Problem:** "API token invalid"
```bash
# Solution: تحقق من التوكن
echo $IBM_QUANTUM_TOKEN  # Linux
echo $env:IBM_QUANTUM_TOKEN  # Windows
```

---

## 📚 موارد إضافية

### OSINT
- VirusTotal API Docs: https://developers.virustotal.com/
- AbuseIPDB API Docs: https://docs.abuseipdb.com/
- AlienVault OTX API: https://otx.alienvault.com/api

### SDN
- Ryu Documentation: https://ryu.readthedocs.io/
- OpenFlow Spec: https://opennetworking.org/
- Mininet Tutorial: http://mininet.org/walkthrough/

### Quantum
- IBM Quantum: https://quantum-computing.ibm.com/
- Qiskit Textbook: https://qiskit.org/textbook/
- Quantum Algorithms: https://quantum-computing.ibm.com/composer/docs/

---

## ✅ Checklist

### OSINT Setup
- [ ] سجلت في VirusTotal
- [ ] سجلت في AbuseIPDB
- [ ] سجلت في AlienVault OTX
- [ ] حفظت API keys في environment variables
- [ ] جربت `python src/intelligence/osint_collector.py`

### SDN Setup
- [ ] اخترت Option (Ryu, OpenDaylight, أو Simplified)
- [ ] نصبت المكتبات المطلوبة
- [ ] جربت Demo
- [ ] عدلت Honeypot IPs في الكود

### Quantum Setup
- [ ] سجلت في IBM Quantum
- [ ] حصلت على API token
- [ ] نصبت Qiskit
- [ ] جربت Simulator mode
- [ ] جربت Real quantum (optional)

---

## 🎉 خلصت!

دلوقتي عندك 3 مكونات متقدمة جاهزة:
1. ✅ **OSINT Collector** - استخبارات من 5 مصادر
2. ✅ **SDN Controller** - تحكم ذكي في الشبكة
3. ✅ **Real Quantum** - قوة كمية حقيقية

### Next Steps:
1. جرب كل مكون بشكل منفصل
2. ادمجهم مع النظام الرئيسي
3. راقب الأداء
4. طور حسب احتياجاتك

**للدعم:**
- راجع `DEPLOYMENT_GUIDE.md` للإعداد الكامل
- راجع `ADVANCED_IMPLEMENTATION.md` للتفاصيل الفنية
- شغل Dashboard: `streamlit run src/dashboard/streamlit_app.py`

**🚀 Cyber Mirage v5.0 LEGENDARY - Now 95% Complete!**
