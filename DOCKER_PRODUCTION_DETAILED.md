# 🐳 Docker Production - شرح تفصيلي كامل

## 🎯 إيه Docker Production؟

```
Docker Development = للتطوير والاختبار
Docker Production = للاستخدام الفعلي والآمن
```

---

## 📋 الفرق الأساسي

| الميزة | Development | Production |
|--------|------------|-----------|
| **الأداء** | سريع للتطوير | محسّن للسرعة |
| **الأمان** | بسيط | قوي جداً |
| **الموارد** | محدود | غير محدود |
| **السجلات** | مفصلة | آمنة |
| **الإعادة** | لا تلقائي | تلقائي دائماً |
| **النسخ الاحتياطية** | لا توجد | موجودة |

---

## 🔧 الخطوة 1: أنشئ `docker-compose.production.yml`

### الملف الكامل:

```yaml
# docker-compose.production.yml

version: '3.8'

services:
  # ============================
  # 🔴 Redis - Cache System
  # ============================
  redis:
    image: redis:7-alpine
    container_name: cyber_mirage_redis_prod
    restart: always
    
    # الأوامر
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --appendonly yes
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
    
    # الموارد
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    
    # التخزين
    volumes:
      - redis_data:/data
      - ./logs/redis:/var/log/redis
    
    # الشبكة
    networks:
      - cyber_net
    
    # صحة النظام
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
    
    # متغيرات البيئة
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    
    # الأمان
    security_opt:
      - no-new-privileges:true
    
    # السجلات
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ============================
  # 🟦 PostgreSQL - Database
  # ============================
  postgres:
    image: postgres:15-alpine
    container_name: cyber_mirage_postgres_prod
    restart: always
    
    # متغيرات البيئة
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - PGDATA=/var/lib/postgresql/data/pgdata
      - POSTGRES_INITDB_ARGS=-c log_min_duration_statement=1000
    
    # الموارد
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    
    # التخزين
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
      - ./logs/postgres:/var/log/postgresql
    
    # الشبكة
    networks:
      - cyber_net
    
    # صحة النظام
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
    
    # الأمان
    security_opt:
      - no-new-privileges:true
    
    # السجلات
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"

  # ============================
  # 🟡 Prometheus - Monitoring
  # ============================
  prometheus:
    image: prom/prometheus:latest
    container_name: cyber_mirage_prometheus_prod
    restart: always
    
    # الأوامر
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=90d'
      - '--storage.tsdb.retention.size=10GB'
    
    # الموارد
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    
    # التخزين
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./docker/prometheus/alerts.yml:/etc/prometheus/alerts.yml:ro
      - prometheus_data:/prometheus
      - ./logs/prometheus:/prometheus/logs
    
    # الشبكة
    networks:
      - monitoring_net
    
    # المنافذ
    ports:
      - "9090:9090"
    
    # الأمان
    security_opt:
      - no-new-privileges:true
    
    # السجلات
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ============================
  # 🟩 Grafana - Dashboard
  # ============================
  grafana:
    image: grafana/grafana:latest
    container_name: cyber_mirage_grafana_prod
    restart: always
    
    # متغيرات البيئة
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER}
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SECURITY_DISABLE_BRUTE_FORCE_LOGIN_PROTECTION=false
    
    # الموارد
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    
    # التخزين
    volumes:
      - grafana_data:/var/lib/grafana
      - ./docker/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./docker/grafana/datasources:/etc/grafana/provisioning/datasources:ro
      - ./logs/grafana:/var/log/grafana
    
    # الشبكة
    networks:
      - monitoring_net
    
    # المنافذ
    ports:
      - "3000:3000"
    
    # التبعيات
    depends_on:
      - prometheus
    
    # الأمان
    security_opt:
      - no-new-privileges:true
    
    # السجلات
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ============================
  # 🟪 Node Exporter - Metrics
  # ============================
  node-exporter:
    image: prom/node-exporter:latest
    container_name: cyber_mirage_node_exporter_prod
    restart: always
    
    # الأوامر
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
      - '--collector.textfile.directory=/etc/node_exporter/textfile_collector'
    
    # الموارد
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.1'
          memory: 256M
    
    # التخزين
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    
    # الشبكة
    networks:
      - monitoring_net
    
    # الأمان
    security_opt:
      - no-new-privileges:true
    
    # السجلات
    logging:
      driver: "json-file"
      options:
        max-size: "5m"
        max-file: "2"

  # ============================
  # 🟢 Honeypot API - Main App
  # ============================
  api:
    build:
      context: .
      dockerfile: Dockerfile.production
    container_name: cyber_mirage_api_prod
    restart: always
    
    # متغيرات البيئة
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - API_PORT=8080
      - WORKERS=4
    
    # الموارد
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    
    # التخزين
    volumes:
      - ./data:/app/data
      - ./logs/api:/app/logs
      - ./config:/app/config:ro
    
    # الشبكة
    networks:
      - cyber_net
      - monitoring_net
    
    # المنافذ
    ports:
      - "8080:8080"
    
    # التبعيات
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    
    # صحة النظام
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # الأمان
    security_opt:
      - no-new-privileges:true
    
    # السجلات
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "10"

# ============================
# 🌐 الشبكات
# ============================
networks:
  cyber_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
    
  monitoring_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16

# ============================
# 💾 التخزين (Volumes)
# ============================
volumes:
  redis_data:
    driver: local
  
  postgres_data:
    driver: local
  
  prometheus_data:
    driver: local
  
  grafana_data:
    driver: local
```

---

## 🔐 الخطوة 2: أنشئ ملف `.env` للـ Production

### الملف `.env.production`:

```bash
# 🔐 Security Credentials
REDIS_PASSWORD=your_very_strong_password_here_min_16_chars
DB_PASSWORD=your_very_strong_database_password_here_min_16_chars
GRAFANA_PASSWORD=your_very_strong_grafana_password_here_min_16_chars

# 📊 Database Configuration
DB_NAME=cyber_mirage_production
DB_USER=admin
DB_PORT=5432

# 👤 Grafana Configuration
GRAFANA_USER=admin

# 🔧 API Configuration
API_PORT=8080
LOG_LEVEL=INFO
ENVIRONMENT=production

# 📈 Performance
REDIS_MAXMEMORY=2gb
POSTGRES_MAX_CONNECTIONS=100
```

---

## 📝 الخطوة 3: أنشئ `Dockerfile.production`

### الملف `Dockerfile.production`:

```dockerfile
# Build stage
FROM python:3.10-slim as builder

WORKDIR /build

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-production.txt /build/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /build/requirements.txt && \
    pip install --no-cache-dir -r /build/requirements-production.txt

# Production stage
FROM python:3.10-slim

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash appuser

WORKDIR /app

# System dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data && chown -R appuser:appuser /app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    ENVIRONMENT=production

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application with gunicorn
CMD ["gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "src.api.main:app"]
```

---

## 📋 الخطوة 4: أنشئ ملف إعدادات Prometheus

### الملف `docker/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'cyber-mirage-production'

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - "/etc/prometheus/alerts.yml"

scrape_configs:
  # Prometheus نفسه
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  # PostgreSQL
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  # Honeypot API
  - job_name: 'honeypot-api'
    static_configs:
      - targets: ['api:8080']
    metrics_path: '/metrics'
```

---

## 🎨 الخطوة 5: إعدادات Grafana

### الملف `docker/grafana/datasources/prometheus.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
    editable: true
```

---

## 🚀 الخطوة 6: كيفية التشغيل

### 1. انسخ الملفات:

```powershell
# انسخ .env.production إلى .env.production
Copy-Item .env.example .env.production

# عدّل كلمات المرور
notepad .env.production
```

### 2. أنشئ الملفات الضرورية:

```powershell
# أنشئ مجلدات Docker
mkdir -p docker/prometheus
mkdir -p docker/grafana/dashboards
mkdir -p docker/grafana/datasources

# أنشئ ملفات الإعدادات
# (انسخ المحتوى من الأعلى)
```

### 3. اختبر البناء:

```powershell
# اختبر بناء الصورة
docker build -f Dockerfile.production -t cyber-mirage:production .
```

### 4. شغّل الإنتاج:

```powershell
# استخدم ملف production
docker-compose -f docker-compose.production.yml up -d
```

### 5. تحقق من الحالة:

```powershell
# عرض الحاويات
docker ps

# عرض السجلات
docker-compose -f docker-compose.production.yml logs -f

# اختبر الاتصال
docker-compose -f docker-compose.production.yml exec api curl http://localhost:8080/health
```

---

## 🔒 ميزات الأمان

```yaml
✅ عدم استخدام صلاحيات root
✅ كلمات مرور قوية
✅ صحة تلقائية
✅ إعادة تشغيل تلقائية
✅ سجلات آمنة
✅ حدود الموارد
✅ شبكات منعزلة
```

---

## 📊 المراقبة

```powershell
# عرض الموارد
docker stats

# عرض السجلات في الوقت الفعلي
docker-compose -f docker-compose.production.yml logs -f api

# اختبر الصحة
docker-compose -f docker-compose.production.yml exec api curl http://localhost:8080/health
```

---

## 🛑 الإيقاف الآمن

```powershell
# إيقاف جميع الخدمات
docker-compose -f docker-compose.production.yml down

# مع الاحتفاظ بالبيانات
# (Volumes لا تُحذف)
```

---

## 📈 الأداء

```
CPU:        محدود ضمن الحدود المعرّفة
Memory:     محدود ضمن الحدود المعرّفة
Storage:    Prometheus محدود 90 يوم/10GB
Logs:       محدودة حجماً وعدداً
```

---

## ✅ الخلاصة

```
1. أنشئ docker-compose.production.yml
2. أنشئ Dockerfile.production
3. أعد ملفات الإعدادات
4. اختبر البناء
5. شغّل الخدمات
6. راقب الأداء
7. احتفظ بالنسخ الاحتياطية

كل شيء آمن واحترافي! 🎉
```
