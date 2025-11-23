# 🚀 دليل التشغيل السريع - Cyber Mirage v5.0

## ⚡ التشغيل السريع (5 دقائق)

### 1️⃣ تأكد من البيئة الافتراضية

```powershell
# تفعيل البيئة الافتراضية
.\venv\Scripts\Activate.ps1

# تأكد من المكتبات
.\venv\Scripts\pip.exe list | Select-String "streamlit|scapy|pandas"
```

---

## 🎯 اختبارات سريعة (كل واحد دقيقة!)

### ✅ اختبار 1: AI Modules (Neural, Swarm, Quantum, Bio)

```powershell
# اختبار Neural Deception
.\venv\Scripts\python.exe -c "from src.ai.neural_deception import NeuralDeception; nd = NeuralDeception(); print('✅ Neural Deception: OK')"

# اختبار Swarm Intelligence
.\venv\Scripts\python.exe -c "from src.ai.swarm_intelligence import SwarmDefense; sd = SwarmDefense(); print('✅ Swarm Intelligence: OK')"

# اختبار Quantum Defense
.\venv\Scripts\python.exe -c "from src.ai.quantum_defense import QuantumDefense; qd = QuantumDefense(); print('✅ Quantum Defense: OK')"

# اختبار Bio-Inspired
.\venv\Scripts\python.exe -c "from src.ai.bio_inspired import BioInspiredDefense; bio = BioInspiredDefense(); print('✅ Bio-Inspired: OK')"
```

**النتيجة المتوقعة:** رسالة "OK" لكل module ✅

---

### ✅ اختبار 2: المكونات الجديدة (OSINT, SDN, Quantum)

```powershell
# اختبار OSINT Collector
.\venv\Scripts\python.exe src/intelligence/osint_collector.py

# اختبار SDN Controller
.\venv\Scripts\python.exe src/network/sdn_controller.py

# اختبار Real Quantum
.\venv\Scripts\python.exe src/ai/real_quantum.py
```

**النتيجة المتوقعة:** 
```
✅ OSINT Collector DEMO - PASSED
✅ SDN Controller DEMO - PASSED
✅ Real Quantum DEMO - PASSED
```

---

### ✅ اختبار 3: Network Tools (ARP, DNS)

```powershell
# اختبار ARP Spoofing (بدون صلاحيات admin - demo mode)
.\venv\Scripts\python.exe -c "from src.network.arp_spoofing import ARPDeception; arp = ARPDeception(); print('✅ ARP Deception: OK')"

# اختبار DNS Deception
.\venv\Scripts\python.exe -c "from src.network.dns_deception import DNSDeception; dns = DNSDeception(); print('✅ DNS Deception: OK')"
```

**النتيجة المتوقعة:** رسالة "OK" ✅

---

### ✅ اختبار 4: Security & Forensics

```powershell
# اختبار Container Isolation
.\venv\Scripts\python.exe -c "from src.security.container_isolation import ContainerIsolation; ci = ContainerIsolation(); print('✅ Container Isolation: OK')"

# اختبار Resource Monitor
.\venv\Scripts\python.exe -c "from src.security.resource_monitor import ResourceMonitor; rm = ResourceMonitor(); print('✅ Resource Monitor: OK')"

# اختبار Log Collector
.\venv\Scripts\python.exe -c "from src.forensics.log_collector import LogCollector; lc = LogCollector(); print('✅ Log Collector: OK')"
```

**النتيجة المتوقعة:** كل الـ modules تشتغل ✅

---

### 