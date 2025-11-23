# 📝 Production Deployment Guide

## 🚀 Quick Start (Docker)

### 1. Install Docker & Docker Compose
```bash
# Windows
choco install docker-desktop

# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### 2. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit with your values
nano .env
```

Required environment variables:
```env
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_secure_password
GRAFANA_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_encryption_key
ALLOWED_ORIGINS=https://yourdomain.com
```

### 3. Build & Run
```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f honeypot
```

### 4. Access Services
- **API**: http://localhost:8080
- **Grafana**: http://localhost:3000 (admin / your_password)
- **Prometheus**: http://localhost:9090

---

## 🧪 Run Tests

```bash
# All tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# Unit tests only
pytest tests/test_comprehensive_env.py -v

# Performance tests
pytest tests/test_comprehensive_env.py::TestPerformance -v

# Open coverage report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
```

Target: **80%+ code coverage**

---

## ☸️ Kubernetes Deployment

### 1. Prerequisites
- Kubernetes cluster (GKE, EKS, AKS)
- kubectl configured
- Docker registry (DockerHub, GCR, ECR)

### 2. Build & Push Image
```bash
# Build
docker build -t your-registry/cyber-mirage:v1.0.0 .

# Push
docker push your-registry/cyber-mirage:v1.0.0
```

### 3. Create Namespace & Secrets
```bash
# Create namespace
kubectl create namespace honeypot

# Create secrets
kubectl create secret generic cyber-mirage-secrets \
  --from-literal=postgres-user=honeypot \
  --from-literal=postgres-password=your_password \
  -n honeypot
```

### 4. Deploy
```bash
# Apply configurations
kubectl apply -f k8s/deployment.yml -n honeypot

# Check status
kubectl get pods -n honeypot
kubectl get svc -n honeypot

# View logs
kubectl logs -f deployment/cyber-mirage -n honeypot
```

### 5. Scale
```bash
# Manual scaling
kubectl scale deployment cyber-mirage --replicas=5 -n honeypot

# Auto-scaling (HPA already configured)
kubectl get hpa -n honeypot
```

---

## 🔒 Security Checklist

### Before Production:

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY and ENCRYPTION_KEY
- [ ] Configure CORS properly (not `*`)
- [ ] Enable HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Run security audit: `bandit -r src/`
- [ ] Scan Docker images: `trivy image cyber-mirage:latest`
- [ ] Enable rate limiting
- [ ] Configure API authentication
- [ ] Set up backup strategy
- [ ] Enable audit logging
- [ ] Harden containers (non-root user)
- [ ] Use secrets management (Vault, AWS Secrets Manager)

### Security Commands:
```bash
# Security scan
pip install bandit safety
bandit -r src/ -f json -o security-report.json
safety check

# Docker scan
trivy image cyber-mirage:latest

# SSL/TLS setup (Let's Encrypt)
certbot --nginx -d yourdomain.com
```

---

## 📊 Monitoring & Alerts

### Grafana Dashboards
1. Open http://localhost:3000
2. Login (admin / your_password)
3. Import dashboards:
   - System Metrics (Node Exporter)
   - Application Metrics (Honeypot)
   - Attack Statistics

### Prometheus Queries
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(errors_total[5m])

# Attack detection rate
rate(attacks_detected_total[1h])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Alerting (Add to Prometheus)
```yaml
groups:
  - name: cyber_mirage_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 10
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
        for: 5m
        annotations:
          summary: "Memory usage above 90%"
```

---

## 🔄 CI/CD Pipeline

GitHub Actions pipeline includes:

1. **Code Quality**
   - Black (formatting)
   - Pylint (linting)
   - MyPy (type checking)
   - Flake8 (style)

2. **Testing**
   - Unit tests
   - Integration tests
   - Performance tests
   - Coverage report (Codecov)

3. **Security**
   - Trivy (vulnerability scan)
   - Bandit (security issues)
   - Safety (dependency check)

4. **Build**
   - Docker image build
   - Multi-architecture support
   - Image scanning

5. **Deploy**
   - Kubernetes deployment
   - Rolling updates
   - Health checks

### Trigger Pipeline:
```bash
# Push to main
git push origin main

# Create release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## 📈 Performance Tuning

### Application Level:
```python
# Increase workers (src/api/main.py)
uvicorn.run("main:app", workers=8, host="0.0.0.0", port=8080)

# Enable caching
@lru_cache(maxsize=1000)
def expensive_operation():
    pass
```

### Docker Level:
```yaml
# docker-compose.yml
resources:
  limits:
    cpus: '2'
    memory: 4G
  reservations:
    cpus: '1'
    memory: 2G
```

### Kubernetes Level:
```yaml
# k8s/deployment.yml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

---

## 🔧 Troubleshooting

### Common Issues:

**1. Container fails to start**
```bash
# Check logs
docker-compose logs honeypot

# Check health
docker-compose exec honeypot curl http://localhost:8080/health
```

**2. Database connection failed**
```bash
# Check postgres
docker-compose exec postgres pg_isready

# Check credentials
docker-compose exec honeypot env | grep POSTGRES
```

**3. High memory usage**
```bash
# Check stats
docker stats

# Restart service
docker-compose restart honeypot
```

**4. Tests failing**
```bash
# Clear cache
pytest --cache-clear

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

---

## 📞 Support & Maintenance

### Backup Strategy:
```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U honeypot cyber_mirage > backup.sql

# Backup volumes
docker run --rm -v cyber_mirage_postgres_data:/data -v $(pwd):/backup ubuntu tar cvf /backup/postgres_backup.tar /data
```

### Update Strategy:
```bash
# Pull latest
git pull origin main

# Rebuild
docker-compose build --no-cache

# Rolling update
docker-compose up -d --no-deps honeypot
```

### Health Monitoring:
```bash
# API health
curl http://localhost:8080/health

# Metrics
curl http://localhost:8080/metrics

# System health
docker-compose exec honeypot python -c "import torch; print(torch.cuda.is_available())"
```

---

## 🎯 Production Checklist

Before going live:

**Infrastructure**
- [ ] Load balancer configured
- [ ] SSL/TLS certificates installed
- [ ] CDN configured (if needed)
- [ ] Backup system in place
- [ ] Monitoring dashboards set up
- [ ] Alert rules configured
- [ ] Log aggregation working

**Security**
- [ ] All secrets rotated
- [ ] Firewall rules applied
- [ ] DDoS protection enabled
- [ ] Rate limiting active
- [ ] Security headers added
- [ ] Penetration testing done

**Performance**
- [ ] Load testing completed
- [ ] Auto-scaling configured
- [ ] Caching enabled
- [ ] Database indexed
- [ ] CDN configured

**Operations**
- [ ] Runbooks created
- [ ] On-call rotation set
- [ ] Incident response plan
- [ ] Documentation updated
- [ ] Team trained

---

## 📚 Additional Resources

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Prometheus Monitoring](https://prometheus.io/docs/practices/naming/)
- [FastAPI Production](https://fastapi.tiangolo.com/deployment/)

---

**🎉 You're ready for production!**
