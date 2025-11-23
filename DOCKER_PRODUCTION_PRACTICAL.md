# 🚀 Docker Production - تطبيق عملي خطوة بخطوة

## 📋 الخطوات العملية الفعلية

---

## ✅ الخطوة 1: انسخ ملف الإنتاج

### في PowerShell:

```powershell
# 1. انتقل للمجلد
cd A:\cyber_mirage

# 2. انسخ docker-compose.yml إلى production
Copy-Item docker-compose.yml docker-compose.production.yml

# 3. تحقق من النسخ
ls docker-compose*
```

**النتيجة:**
```
docker-compose.yml             (النسخة الأصلية)
docker-compose.production.yml  (النسخة الجديدة للإنتاج)
```

---

## ✅ الخطوة 2: عدّل `.env`

### أنشئ `.env.production`:

```powershell
# 1. انسخ الملف
Copy-Item .env .env.production

# 2. افتح للتعديل
notepad .env.production
```

### المحتوى المطلوب:

```env
# 🔐 كلمات المرور (قوية جداً!)
POSTGRES_PASSWORD=Cyber@Mirage#Production$2025!SuperSecure123
REDIS_PASSWORD=Redis@Production$2025!SecurePassword456
GRAFANA_PASSWORD=Grafana@Admin$2025!DashboardPassword789

# 📊 قاعدة البيانات
POSTGRES_DB=cyber_mirage_prod
POSTGRES_USER=admin

# 🟡 المراقبة
GRAFANA_USER=admin

# 🔧 الإعدادات
ENVIRONMENT=production
LOG_LEVEL=INFO
API_PORT=8080
```

---

## ✅ الخطوة 3: أنشئ `Dockerfile.production`

### في المجلد الرئيسي، أنشئ ملف `Dockerfile.production`:

```powershell
# استخدم أي محرر نصوص
New-Item -Path "A:\cyber_mirage\Dockerfile.production" -ItemType File
```

### المحتوى:

```dockerfile
# Build Stage
FROM python:3.10-slim as builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ git make libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-production.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-production.txt

# Production Stage
FROM python:3.10-slim

RUN useradd -m -u 1000 -s /bin/bash appuser
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=appuser:appuser . .

RUN mkdir -p /app/logs /app/data && chown -R appuser:appuser /app

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 ENVIRONMENT=production
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "src/api/main.py"]
```

---

## ✅ الخطوة 4: أنشئ مجلدات الإعدادات

### في PowerShell:

```powershell
# أنشئ مجلدات Docker
mkdir -p docker/prometheus
mkdir -p docker/grafana/dashboards
mkdir -p docker/grafana/datasources
mkdir -p logs

# تحقق من الإنشاء
ls docker/
ls logs/
```

---

## ✅ الخطوة 5: أنشئ ملف إعدادات Prometheus

### `docker/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - "/etc/prometheus/alerts.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'api'
    static_configs:
      - targets: ['api:8080']
    metrics_path: '/metrics'
```

### `docker/prometheus/alerts.yml`:

```yaml
groups:
  - name: cyber_mirage_alerts
    rules:
      - alert: HighCPUUsage
        expr: node_cpu_seconds_total > 80
        for: 5m
        annotations:
          summary: "High CPU usage detected"

      - alert: LowDiskSpace
        expr: node_filesystem_free_bytes < 1000000000
        for: 5m
        annotations:
          summary: "Low disk space warning"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        annotations:
          summary: "Service is down"
```

---

## ✅ الخطوة 6: أنشئ ملف Grafana

### `docker/grafana/datasources/prometheus.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
```

---

## ✅ الخطوة 7: عدّل `docker-compose.production.yml`

### استبدل المحتوى بهذا:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: cyber_mirage_redis_prod
    restart: always
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - cyber_net
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  postgres:
    image: postgres:15-alpine
    container_name: cyber_mirage_postgres_prod
    restart: always
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./logs/postgres:/var/log/postgresql
    networks:
      - cyber_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    container_name: cyber_mirage_prometheus_prod
    restart: always
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=90d'
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./docker/prometheus/alerts.yml:/etc/prometheus/alerts.yml:ro
      - prometheus_data:/prometheus
    networks:
      - monitoring_net
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    container_name: cyber_mirage_grafana_prod
    restart: always
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_SECURITY_ADMIN_USER=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./docker/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./docker/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    networks:
      - monitoring_net
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    container_name: cyber_mirage_node_exporter_prod
    restart: always
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    networks:
      - monitoring_net

  api:
    build:
      context: .
      dockerfile: Dockerfile.production
    container_name: cyber_mirage_api_prod
    restart: always
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - REDIS_HOST=redis
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - ./data:/app/data
      - ./logs/api:/app/logs
    networks:
      - cyber_net
      - monitoring_net
    ports:
      - "8080:8080"
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  cyber_net:
    driver: bridge
  monitoring_net:
    driver: bridge

volumes:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:
```

---

## ✅ الخطوة 8: اختبر البناء

### في PowerShell:

```powershell
# 1. اختبر بناء الصورة الأولى
docker build -f Dockerfile.production -t cyber-mirage:production . --progress=plain

# 2. تحقق من الصورة
docker images | Select-String cyber-mirage
```

**النتيجة المتوقعة:**
```
cyber-mirage    production    abc123def456    2.5GB    Few seconds ago
```

---

## ✅ الخطوة 9: شغّل الإنتاج

### في PowerShell:

```powershell
# 1. حمّل المتغيرات من .env.production
$env:DOTENV_FILE = ".env.production"

# 2. شغّل الخدمات
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# 3. تحقق من البدء
Start-Sleep -Seconds 5
docker-compose -f docker-compose.production.yml ps
```

**النتيجة المتوقعة:**
```
NAMES                              STATUS
cyber_mirage_redis_prod            Up 10 seconds (healthy)
cyber_mirage_postgres_prod         Up 10 seconds (healthy)
cyber_mirage_prometheus_prod       Up 5 seconds
cyber_mirage_grafana_prod          Up 5 seconds
cyber_mirage_node_exporter_prod    Up 5 seconds
cyber_mirage_api_prod              Up 5 seconds (healthy)
```

---

## ✅ الخطوة 10: تحقق من الصحة

### في PowerShell:

```powershell
# 1. عرض جميع الخدمات
docker ps

# 2. اختبر الـ API
curl http://localhost:8080/health

# 3. افتح الروابط في المتصفح
Start-Process "http://localhost:8501"  # Dashboard
Start-Process "http://localhost:8080"  # API
Start-Process "http://localhost:3000"  # Grafana
Start-Process "http://localhost:9090"  # Prometheus
```

---

## ✅ الخطوة 11: راقب السجلات

### في PowerShell:

```powershell
# 1. عرض جميع السجلات
docker-compose -f docker-compose.production.yml logs -f

# 2. سجلات خدمة محددة
docker-compose -f docker-compose.production.yml logs -f api

# 3. آخر 100 سطر فقط
docker-compose -f docker-compose.production.yml logs --tail=100 api
```

---

## ✅ الخطوة 12: نسخ احتياطي للبيانات

### في PowerShell:

```powershell
# 1. نسخ احتياطي من PostgreSQL
docker exec cyber_mirage_postgres_prod pg_dump -U admin cyber_mirage_prod > backup_$(Get-Date -Format "yyyy-MM-dd_HHmmss").sql

# 2. نسخ احتياطي من Redis
docker exec cyber_mirage_redis_prod redis-cli -a $env:REDIS_PASSWORD BGSAVE

# 3. نسخ احتياطي من Grafana
docker cp cyber_mirage_grafana_prod:/var/lib/grafana ./grafana_backup_$(Get-Date -Format "yyyy-MM-dd_HHmmss")
```

---

## 🛑 الإيقاف الآمن

### في PowerShell:

```powershell
# 1. إيقاف الخدمات
docker-compose -f docker-compose.production.yml down

# 2. مع حذف البيانات (احذر!)
docker-compose -f docker-compose.production.yml down -v
```

---

## 📊 الأوامر المفيدة

```powershell
# عرض الموارد المستخدمة
docker stats

# عرض حجم الحاويات
docker ps -s

# فحص حاوية محددة
docker inspect cyber_mirage_api_prod

# دخول حاوية
docker exec -it cyber_mirage_api_prod /bin/bash

# نسخ ملف من حاوية
docker cp cyber_mirage_postgres_prod:/var/log/postgresql ./logs
```

---

## ✨ الملخص

```
1. ✅ انسخ docker-compose.yml
2. ✅ عدّل .env
3. ✅ أنشئ Dockerfile.production
4. ✅ أنشئ ملفات الإعدادات
5. ✅ اختبر البناء
6. ✅ شغّل الخدمات
7. ✅ افتح الروابط
8. ✅ راقب السجلات
9. ✅ نسخ احتياطي
10. ✅ استمتع! 🎉
```

---

**الآن عندك Production Docker Setup كامل!** 🚀
