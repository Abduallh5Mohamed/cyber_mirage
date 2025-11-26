# 📤 رفع ملفات Role 4 إلى السيرفر

## الملفات التي تم إنشاؤها:

```
src/analysis/threat_intel.py      - جمع معلومات التهديدات
src/analysis/ip_reputation.py     - تقييم سمعة IPs
src/analysis/geoip_lookup.py      - البحث الجغرافي
src/analysis/attack_patterns.py   - تحليل أنماط الهجوم
```

## خطوات الرفع:

### 1. الاتصال بالسيرفر:
```bash
ssh -i "PATH_TO_YOUR_KEY.pem" ubuntu@13.53.131.159
```

### 2. إنشاء المجلد المؤقت:
```bash
mkdir -p ~/analysis_module
```

### 3. من جهازك المحلي - رفع الملفات:
```bash
scp -i "PATH_TO_YOUR_KEY.pem" \
    "a:\cyber_mirage\src\analysis\threat_intel.py" \
    "a:\cyber_mirage\src\analysis\ip_reputation.py" \
    "a:\cyber_mirage\src\analysis\geoip_lookup.py" \
    "a:\cyber_mirage\src\analysis\attack_patterns.py" \
    ubuntu@13.53.131.159:~/analysis_module/
```

### 4. على السيرفر - نسخ الملفات:
```bash
sudo cp ~/analysis_module/*.py /opt/cyber_mirage/src/analysis/
sudo chown -R root:root /opt/cyber_mirage/src/analysis/
ls -la /opt/cyber_mirage/src/analysis/
```

### 5. اختبار الملفات:
```bash
docker exec -it cyber_mirage_ai python -c "
from src.analysis.threat_intel import ThreatIntelCollector
from src.analysis.ip_reputation import IPReputationChecker
from src.analysis.geoip_lookup import GeoIPLookup
from src.analysis.attack_patterns import AttackPatternAnalyzer
print('✅ All Role 4 modules imported successfully!')
"
```

## النتيجة المتوقعة:
بعد تنفيذ هذه الخطوات، سيكون Role 4 (Threat Intelligence Analyst) مكتمل 100%!
