# 🐳 Docker Production Deployment Guide - Cyber Mirage v5.0

## 📋 Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Architecture](#architecture)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Monitoring](#monitoring)
8. [Maintenance](#maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Security](#security)

---

## 🎯 Overview

تم تصميم Cyber Mirage v5.0 للعمل في بيئة Production كاملة باستخدام **Docker Containers**. النظام يشمل:

### المكونات الرئيسية:
```
┌──────────────────────────────────────────────────────────┐
│                 CYBER MIRAGE v5.0 STACK                  │
├──────────────────────────────────────────────────────────┤
│  • AI Engine      - Neural, Swarm, OSINT (3 services)   │
│  • Honeypots      - SSH, FTP, HTTP, DB, ICS (8 ports)   │
│  • Dashboard      - Streamlit real-time monitoring       │
│  • Redis          - Cache & message queue                │
│  • PostgreSQL     - Persistent storage                   │
│  • Prometheus     - Metrics collection                   │
│  • Grafana        - Visualization dashboards             │
│  • Alertmanager   - Alert routing                        │
│  • Node Exporter  - System metrics                       │
│  • cAdvisor       - Container metrics                    │
└──────────────────────────────────────────────────────────┘
```

### الميزات:
- ✅ **Multi-container** architecture
- ✅ **Auto-scaling** capabilities
- ✅ **Health checks** for all services
- ✅ **Resource limits** configured
- ✅ **Security hardened** (non-root users, minimal privileges)
- ✅ **Monitoring** with Prometheus + Grafana
- ✅ **Logging** centralized
- ✅ **Backup** strategies included

---

## 📦 Prerequisites

### System Requirements:

#### Minimum:
```
• CPU:     4 cores
• RAM:     16 GB
• Disk:    50 GB SSD
• OS:      Windows 10/11, Linux, macOS
```

#### Recommended:
```
• CPU:     8+ cores
• RAM:     32 GB
• Disk:    100 GB NVMe SSD
• OS:      Ubuntu 22.04 LTS / Windows Server 2022
• Network: 1 Gbps
```

### Software Requirements:

#### 1. Docker Desktop (Windows/Mac):
```powershell
# Windows (using Chocolatey)
choco install docker-desktop

# Or download from:
https://www.docker.com/products/docker-desktop
```

#### 2. Docker Engine (Linux):
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker-compose --version
```

#### 3. Required Ports:
```
Ensure these ports are available:
• 8501  - Dashboard
• 3000  - Grafana
• 9090  - Prometheus
• 9093  - Alertmanager
• 8001  - Neural Deception
• 8002  - Swarm Intelligence
• 8003  - OSINT Collector
• 2222  - SSH Honeypot
• 2121  - FTP Honeypot
• 8080  - HTTP Honeypot
• 8443  - HTTPS Honeypot
• 3306  - MySQL Honeypot
• 5432  - PostgreSQL Honeypot
• 502   - Modbus (ICS) Honeypot
```

---

## 🚀 Quick Start

### 1️⃣ Clone & Setup:
```powershell
# Navigate to project
cd A:\cyber_mirage

# Create .env file
Copy-Item .env.example .env

# Edit .env with your credentials
notepad .env
```

### 2️⃣ Configure Environment:
Edit `.env` file:
```bash
# Database
POSTGRES_PASSWORD=YourSecurePassword123!
REDIS_PASSWORD=YourRedisPassword123!

# Grafana
GRAFANA_PASSWORD=admin123
GRAFANA_SECRET=your-secret-key-here

# API Keys (optional but recommended)
VIRUSTOTAL_API_KEY=your_key_here
ABUSEIPDB_API_KEY=your_key_here
SHODAN_API_KEY=your_key_here
```

### 3️⃣ Deploy:
```powershell
# Using deployment script
.\deploy_production.ps1 -Action start

# Or manually
docker-compose -f docker-compose.production.yml up -d
```

### 4️⃣ Verify:
```powershell
# Check status
.\deploy_production.ps1 -Action status

# View logs
.\deploy_production.ps1 -Action logs
```

### 5️⃣ Access Services:
```
• Dashboard:    http://localhost:8501
• Grafana:      http://localhost:3000 (admin/admin123)
• Prometheus:   http://localhost:9090
• Alertmanager: http://localhost:9093
```

---

## 🏗️ Architecture

### Service Dependencies:
```
┌─────────────────────────────────────────┐
│            Load Balancer                │
│         (External - Optional)           │
└───────────────┬─────────────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼────┐          ┌───────▼────┐
│Dashboard│          │ Honeypots  │
│(8501)  │          │(Multi-Port)│
└───┬────┘          └──────┬─────┘
    │                      │
    │    ┌─────────────────┤
    │    │                 │
┌───▼────▼───┐      ┌──────▼──────┐
│ AI Engine  │      │   Redis     │
│(8001-8003) │      │   (6379)    │
└─────┬──────┘      └──────┬──────┘
      │                    │
      └────────┬───────────┘
               │
       ┌───────▼─────────┐
       │   PostgreSQL    │
       │     (5432)      │
       └─────────────────┘

Monitoring Stack:
┌──────────────┐    ┌──────────────┐
│ Prometheus   │───▶│   Grafana    │
│   (9090)     │    │   (3000)     │
└──────────────┘    └──────────────┘
       ▲
       │
  ┌────┴────┐
  │ Metrics │
  └─────────┘
```

### Network Topology:
```
cyber_network (172.25.0.0/16)
  ├─ ai-engine      (172.25.0.10)
  ├─ dashboard      (172.25.0.20)
  ├─ honeypots      (172.25.0.30)
  ├─ redis          (172.25.0.40)
  └─ postgres       (172.25.0.50)

monitoring (172.26.0.0/16)
  ├─ prometheus     (172.26.0.10)
  ├─ grafana        (172.26.0.20)
  ├─ alertmanager   (172.26.0.30)
  ├─ node-exporter  (172.26.0.40)
  └─ cadvisor       (172.26.0.50)
```

---

## ⚙️ Configuration

### Docker Compose Files:

#### 1. `docker-compose.production.yml`
- **Purpose:** Production deployment
- **Services:** All 10+ services
- **Features:** 
  - Resource limits
  - Health checks
  - Security hardening
  - Auto-restart policies

#### 2. Environment Variables (`.env`):
```bash
# ═══════════════════════════════════════════
# CYBER MIRAGE v5.0 - Production Configuration
# ═══════════════════════════════════════════

# ───────────────────────────────────────────
# Database Configuration
# ───────────────────────────────────────────
POSTGRES_DB=cyber_mirage
POSTGRES_USER=cybermirage
POSTGRES_PASSWORD=SecurePass123!
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=changeme123

# ───────────────────────────────────────────
# Monitoring
# ───────────────────────────────────────────
GRAFANA_PASSWORD=admin123
GRAFANA_SECRET=your-random-secret-key

# ───────────────────────────────────────────
# API Keys (OSINT)
# ───────────────────────────────────────────
VIRUSTOTAL_API_KEY=your_virustotal_key
ABUSEIPDB_API_KEY=your_abuseipdb_key
SHODAN_API_KEY=your_shodan_key

# ───────────────────────────────────────────
# Application Settings
# ───────────────────────────────────────────
ENVIRONMENT=production
LOG_LEVEL=INFO
AI_MODE=all
HONEYPOT_MODE=production
```

### Dockerfile Configuration:

#### AI Engine (`docker/Dockerfile.ai`):
- Base: Python 3.10-slim
- Multi-stage build
- Non-root user (aiengine:1001)
- Resource-optimized
- AI/ML libraries included

#### Dashboard (`docker/Dockerfile.dashboard`):
- Base: Python 3.10-slim
- Streamlit optimized
- Non-root user (dashboard:1002)
- Health check enabled

#### Honeypots (`docker/Dockerfile.honeypot`):
- Base: Python 3.10-slim
- Network capabilities
- Non-root user (honeypot:1003)
- Multi-port support

---

## 🚢 Deployment

### Deployment Script Usage:

#### Start Stack:
```powershell
.\deploy_production.ps1 -Action start
```
**What it does:**
1. Checks prerequisites (Docker, Docker Compose)
2. Creates `.env` if missing
3. Pulls latest images
4. Starts all services
5. Shows status and access URLs

#### Stop Stack:
```powershell
.\deploy_production.ps1 -Action stop
```
**What it does:**
1. Gracefully stops all containers
2. Preserves volumes (data not lost)

#### Restart Stack:
```powershell
.\deploy_production.ps1 -Action restart
```
**What it does:**
1. Restarts all services
2. No data loss
3. Quick recovery

#### Rebuild Stack:
```powershell
.\deploy_production.ps1 -Action rebuild
```
**What it does:**
1. Stops containers
2. Removes old images
3. Rebuilds from Dockerfiles
4. Starts fresh containers
**Use when:** Code changes, Dockerfile updates

#### View Status:
```powershell
.\deploy_production.ps1 -Action status
```
**Shows:**
- Container names
- Status (Up/Down)
- Ports
- Health status

#### View Logs:
```powershell
# All services
.\deploy_production.ps1 -Action logs

# Specific service
.\deploy_production.ps1 -Action logs -Service ai-engine
.\deploy_production.ps1 -Action logs -Service dashboard
.\deploy_production.ps1 -Action logs -Service honeypots
```

#### Clean Up:
```powershell
.\deploy_production.ps1 -Action clean
```
**⚠️ WARNING:** This removes:
- All containers
- All volumes (data lost!)
- All images
- System cache

---

## 📊 Monitoring

### Prometheus Setup:

#### Access:
```
http://localhost:9090
```

#### Key Metrics:
```promql
# Attack rate
rate(honeypot_attacks_total[5m])

# AI response time
ai_engine_response_time_seconds

# CPU usage
rate(process_cpu_seconds_total[5m])

# Memory usage
process_resident_memory_bytes

# Container health
up{job="honeypots"}
```

#### Targets:
- AI Engine (3 endpoints)
- Honeypots
- Dashboard
- Redis
- PostgreSQL
- System (Node Exporter)
- Containers (cAdvisor)

### Grafana Dashboards:

#### Access:
```
http://localhost:3000
Username: admin
Password: admin123 (from .env)
```

#### Pre-configured Dashboards:
1. **Cyber Mirage Overview**
   - Attack statistics
   - Service health
   - Resource usage

2. **AI Engine Performance**
   - Neural Deception metrics
   - Swarm Intelligence stats
   - OSINT collector activity

3. **Honeypot Activity**
   - Attacks per service
   - Top attackers
   - Attack patterns

4. **System Resources**
   - CPU, Memory, Disk
   - Network traffic
   - Container metrics

#### Create Custom Dashboard:
1. Go to Grafana
2. Click "+" → "Dashboard"
3. Add Panel
4. Select "Prometheus" as datasource
5. Write PromQL query
6. Save dashboard

### Alertmanager:

#### Access:
```
http://localhost:9093
```

#### Configured Alerts:
- 🚨 High attack rate (>100/sec)
- 🚨 Sophisticated attack detected
- 🚨 Service down
- ⚠️ High CPU/Memory usage
- ⚠️ Database issues

#### Email Notifications:
Edit `docker/alertmanager/alertmanager.yml`:
```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'your-email@gmail.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

receivers:
  - name: 'security-team'
    email_configs:
      - to: 'security@your-company.com'
```

---

## 🔧 Maintenance

### Backup Strategy:

#### 1. Database Backup:
```powershell
# PostgreSQL backup
docker exec cyber_mirage_postgres pg_dump -U cybermirage cyber_mirage > backup_$(Get-Date -Format 'yyyyMMdd').sql

# Automated daily backup
$BackupScript = @"
`$date = Get-Date -Format 'yyyyMMdd'
docker exec cyber_mirage_postgres pg_dump -U cybermirage cyber_mirage > "backups/db_`$date.sql"
"@

# Schedule in Task Scheduler
```

#### 2. Volume Backup:
```powershell
# Backup all volumes
docker run --rm -v cyber_mirage_postgres_data:/data -v ${PWD}/backups:/backup alpine tar czf /backup/postgres_data.tar.gz /data
```

#### 3. Configuration Backup:
```powershell
# Backup configs
$files = @(
    "docker-compose.production.yml",
    ".env",
    "docker/prometheus/prometheus.yml",
    "docker/grafana/datasources/datasources.yml"
)
Compress-Archive -Path $files -DestinationPath "config_backup_$(Get-Date -Format 'yyyyMMdd').zip"
```

### Updates:

#### 1. Update Application Code:
```powershell
# Pull latest code
git pull origin main

# Rebuild containers
.\deploy_production.ps1 -Action rebuild
```

#### 2. Update Base Images:
```powershell
# Pull latest images
docker-compose -f docker-compose.production.yml pull

# Restart with new images
docker-compose -f docker-compose.production.yml up -d
```

#### 3. Update Dependencies:
```powershell
# Update requirements.txt
# Then rebuild
.\deploy_production.ps1 -Action rebuild
```

### Scaling:

#### Scale Services:
```powershell
# Scale AI engine to 3 instances
docker-compose -f docker-compose.production.yml up -d --scale ai-engine=3

# Scale honeypots to 5 instances
docker-compose -f docker-compose.production.yml up -d --scale honeypots=5
```

#### Resource Adjustment:
Edit `docker-compose.production.yml`:
```yaml
services:
  ai-engine:
    deploy:
      resources:
        limits:
          cpus: '8.0'      # Increase from 4
          memory: 16G      # Increase from 8G
```

---

## 🔍 Troubleshooting

### Common Issues:

#### 1. Container Won't Start:
```powershell
# Check logs
docker logs cyber_mirage_ai

# Check specific error
.\deploy_production.ps1 -Action logs -Service ai-engine
```

**Solutions:**
- Check .env file
- Verify ports not in use
- Check resource availability
- Review Docker logs

#### 2. Database Connection Failed:
```powershell
# Test PostgreSQL
docker exec -it cyber_mirage_postgres psql -U cybermirage -d cyber_mirage

# Test Redis
docker exec -it cyber_mirage_redis redis-cli ping
```

**Solutions:**
- Verify credentials in .env
- Check network connectivity
- Ensure database is healthy

#### 3. High Memory Usage:
```powershell
# Check container stats
docker stats

# Check specific container
docker stats cyber_mirage_ai
```

**Solutions:**
- Increase Docker memory limit
- Adjust resource limits in docker-compose
- Stop unused services

#### 4. Port Already in Use:
```powershell
# Find what's using port
netstat -ano | findstr :8501

# Kill process
taskkill /PID <PID> /F
```

**Solutions:**
- Change port in docker-compose
- Stop conflicting service
- Use different host port

### Health Checks:

#### Manual Health Check:
```powershell
# AI Engine
curl http://localhost:8001/health

# Dashboard
curl http://localhost:8501/_stcore/health

# Honeypots
curl http://localhost:8080/health
```

#### Container Health Status:
```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Logs Analysis:

#### View Logs:
```powershell
# Last 100 lines
docker logs --tail 100 cyber_mirage_ai

# Follow logs
docker logs -f cyber_mirage_honeypots

# With timestamps
docker logs -t cyber_mirage_dashboard
```

#### Search Logs:
```powershell
# Search for errors
docker logs cyber_mirage_ai 2>&1 | Select-String "ERROR"

# Search for specific attack
docker logs cyber_mirage_honeypots | Select-String "SSH"
```

---

## 🔒 Security

### Security Best Practices:

#### 1. Change Default Passwords:
```bash
# Edit .env
POSTGRES_PASSWORD=VerySecurePassword123!@#
REDIS_PASSWORD=AnotherSecurePass456!@#
GRAFANA_PASSWORD=GrafanaSecure789!@#
```

#### 2. Use Secrets Management:
```powershell
# Docker secrets (Swarm mode)
echo "MySecurePassword" | docker secret create postgres_password -
```

#### 3. Enable TLS:
```yaml
# In docker-compose.production.yml
services:
  honeypots:
    environment:
      - TLS_ENABLED=true
      - TLS_CERT_PATH=/certs/cert.pem
      - TLS_KEY_PATH=/certs/key.pem
    volumes:
      - ./certs:/certs:ro
```

#### 4. Firewall Rules:
```powershell
# Windows Firewall (PowerShell Admin)
New-NetFirewallRule -DisplayName "Cyber Mirage Dashboard" -Direction Inbound -Protocol TCP -LocalPort 8501 -Action Allow
New-NetFirewallRule -DisplayName "Cyber Mirage Grafana" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
```

#### 5. Regular Updates:
```powershell
# Update base images monthly
docker-compose pull
docker-compose up -d

# Update application
git pull
.\deploy_production.ps1 -Action rebuild
```

#### 6. Vulnerability Scanning:
```powershell
# Install Trivy
choco install trivy

# Scan images
trivy image cyber-mirage/ai-engine:latest
trivy image cyber-mirage/dashboard:latest
trivy image cyber-mirage/honeypots:latest
```

#### 7. Network Isolation:
- Use separate networks (cyber_network, monitoring)
- Expose only necessary ports
- Use reverse proxy (nginx, Traefik)

#### 8. Audit Logs:
```powershell
# Enable Docker audit logging
# Add to Docker daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## 📈 Performance Optimization

### Resource Tuning:

#### 1. AI Engine:
```yaml
ai-engine:
  deploy:
    resources:
      limits:
        cpus: '8.0'
        memory: 16G
      reservations:
        cpus: '4.0'
        memory: 8G
```

#### 2. Database:
```yaml
postgres:
  command: >
    postgres
    -c shared_buffers=2GB
    -c effective_cache_size=6GB
    -c maintenance_work_mem=512MB
    -c max_connections=200
```

#### 3. Redis:
```yaml
redis:
  command: >
    redis-server
    --maxmemory 4gb
    --maxmemory-policy allkeys-lru
    --save ""
```

### Monitoring Performance:

#### Check Container Stats:
```powershell
# Real-time stats
docker stats

# Export to CSV
docker stats --no-stream --format "table {{.Container}},{{.CPUPerc}},{{.MemUsage}}" > stats.csv
```

---

## 🎓 Advanced Topics

### Multi-Host Deployment (Docker Swarm):

#### Initialize Swarm:
```bash
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.production.yml cyber-mirage
```

### Kubernetes Deployment:

#### Convert to K8s:
```bash
# Install kompose
choco install kompose

# Convert
kompose convert -f docker-compose.production.yml
```

### CI/CD Integration:

#### GitHub Actions:
```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker images
        run: docker-compose -f docker-compose.production.yml build
      
      - name: Push to registry
        run: |
          docker tag cyber-mirage/ai-engine:latest registry.com/cyber-mirage/ai-engine:${{ github.sha }}
          docker push registry.com/cyber-mirage/ai-engine:${{ github.sha }}
```

---

## 📞 Support

### Getting Help:

#### Check Logs First:
```powershell
.\deploy_production.ps1 -Action logs
```

#### Health Status:
```powershell
.\deploy_production.ps1 -Action status
```

#### Common Commands:
```powershell
# Restart everything
.\deploy_production.ps1 -Action restart

# Rebuild after code changes
.\deploy_production.ps1 -Action rebuild

# Clean slate (WARNING: data loss)
.\deploy_production.ps1 -Action clean
```

---

## 🎉 Success!

إذا وصلت هنا، فأنت جاهز للـ Production! 🚀

### Next Steps:
1. ✅ Monitor dashboard: http://localhost:8501
2. ✅ Check Grafana: http://localhost:3000
3. ✅ Review Prometheus: http://localhost:9090
4. ✅ Test honeypots: SSH to port 2222
5. ✅ Setup alerts in Alertmanager
6. ✅ Configure backups (daily)
7. ✅ Start attack testing from Kali Linux

---

**🎯 Cyber Mirage v5.0 - Production Ready! 🎯**

*Last Updated: October 27, 2025*
