# 🚀 Cyber Mirage - AWS Deployment Guide

## Prerequisites

- AWS Account with EC2 access
- Security Group configured (see below)
- SSH key pair (.pem file)
- Domain name (optional, for HTTPS)

---

## 📋 Quick Start (5 Minutes)

### 1. Launch EC2 Instance

**Recommended Configuration:**
- **AMI:** Ubuntu 22.04 LTS
- **Instance Type:** `t2.large` (2 vCPU, 8GB RAM) or `t2.xlarge` for production
- **Storage:** 50GB GP3 SSD
- **Security Group:** See configuration below

### 2. Configure Security Group

**Inbound Rules** (ALL confirmed working ✅):

| Port | Protocol | Source | Description |
|------|----------|--------|-------------|
| 22 | TCP | Your IP | SSH Management |
| 80 | TCP | 0.0.0.0/0 | HTTP (optional redirect) |
| 445 | TCP | 0.0.0.0/0 | SMB Honeypot |
| 502 | TCP | 0.0.0.0/0 | Modbus Honeypot |
| 1025 | TCP | 0.0.0.0/0 | Custom Honeypot |
| 2121 | TCP | 0.0.0.0/0 | FTP Honeypot |
| 2222 | TCP | 0.0.0.0/0 | SSH Honeypot |
| 3000 | TCP | 0.0.0.0/0 | Grafana Dashboard |
| 3307 | TCP | 0.0.0.0/0 | MySQL Honeypot |
| 5434 | TCP | 0.0.0.0/0 | PostgreSQL Honeypot |
| 8080 | TCP | 0.0.0.0/0 | HTTP Honeypot |
| 8443 | TCP | 0.0.0.0/0 | HTTPS Honeypot |
| 8501 | TCP | 0.0.0.0/0 | **Streamlit Dashboard** (Main UI) |
| 9090 | TCP | Your IP | Prometheus (restrict!) |

### 3. Connect to Instance

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### 4. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

### 5. Clone & Configure Project

```bash
# Clone repository
git clone https://github.com/Abduallh5Mohamed/cyber_mirage.git
cd cyber_mirage

# Create production environment file
cp .env.example .env.production

# Edit environment variables
nano .env.production
```

**Required Environment Variables:**

```bash
# Database Passwords (CHANGE THESE!)
POSTGRES_PASSWORD=YourSecurePassword123!
REDIS_PASSWORD=YourRedisPassword456!
GRAFANA_PASSWORD=YourGrafanaPassword789!

# API Keys (Optional but recommended)
VIRUSTOTAL_API_KEY=your_virustotal_key_here
ABUSEIPDB_API_KEY=your_abuseipdb_key_here
SHODAN_API_KEY=your_shodan_key_here

# Environment
ENVIRONMENT=production
```

### 6. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose -f docker-compose.production.yml up -d --build

# Check status
docker ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

---

## ✅ Verification

### Check All Services Are Running

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Expected Output:**
```
NAMES                          STATUS           PORTS
cyber_mirage_dashboard         Up 2 minutes     0.0.0.0:8501->8501/tcp
cyber_mirage_honeypots         Up 2 minutes     Multiple ports...
cyber_mirage_ai                Up 2 minutes     0.0.0.0:8001->8001/tcp
cyber_mirage_postgres          Up 2 minutes     127.0.0.1:5433->5432/tcp
cyber_mirage_redis             Up 2 minutes     127.0.0.1:6379->6379/tcp
cyber_mirage_prometheus        Up 2 minutes     0.0.0.0:9090->9090/tcp
cyber_mirage_grafana           Up 2 minutes     0.0.0.0:3000->3000/tcp
```

### Access Dashboards

1. **Streamlit Dashboard (Main UI):**  
   `http://YOUR_EC2_IP:8501/`  
   ✅ **This is your primary interface!**

2. **Grafana:**  
   `http://YOUR_EC2_IP:3000/`  
   Login: `admin` / `YourGrafanaPassword789!`

3. **Prometheus:**  
   `http://YOUR_EC2_IP:9090/`  
   ⚠️ Restrict this to admin IPs only!

### Test Honeypots

```bash
# Test SSH honeypot
nc YOUR_EC2_IP 2222

# Test FTP honeypot
nc YOUR_EC2_IP 2121

# Test HTTP honeypot
curl http://YOUR_EC2_IP:8080/
```

---

## 🔧 Management Commands

### View Logs

```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f honeypots
docker-compose -f docker-compose.production.yml logs -f ai-engine
docker-compose -f docker-compose.production.yml logs -f dashboard
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose.production.yml restart

# Restart specific service
docker-compose -f docker-compose.production.yml restart honeypots
```

### Stop/Start

```bash
# Stop all
docker-compose -f docker-compose.production.yml down

# Start all
docker-compose -f docker-compose.production.yml up -d
```

### Database Access

```bash
# PostgreSQL
docker exec -it cyber_mirage_postgres psql -U cybermirage -d cyber_mirage

# Redis
docker exec -it cyber_mirage_redis redis-cli -a changeme123
```

---

## 📊 Monitoring

### Check Database Connections

```sql
-- Inside PostgreSQL
SELECT COUNT(*) FROM attack_sessions;
SELECT COUNT(*) FROM agent_decisions;
SELECT COUNT(*) FROM deception_events;
```

### Check System Resources

```bash
# CPU/Memory usage
docker stats

# Disk usage
df -h
du -sh cyber_mirage/
```

---

## 🔒 Security Hardening

### 1. Change Default Passwords

```bash
# Update .env.production with strong passwords
nano .env.production

# Restart services
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d
```

### 2. Restrict Prometheus Access

Edit Security Group to allow Prometheus (9090) only from your IP.

### 3. Enable HTTPS (Optional)

```bash
# Install certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure reverse proxy (Nginx)
sudo apt install nginx
# ... configure Nginx to proxy 80/443 → 8501
```

### 4. Setup Automatic Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec cyber_mirage_postgres pg_dump -U cybermirage cyber_mirage > $BACKUP_DIR/db_$DATE.sql

# Backup volumes
sudo tar -czf $BACKUP_DIR/volumes_$DATE.tar.gz /var/lib/docker/volumes/

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l ; echo "0 2 * * * /home/ubuntu/cyber_mirage/backup.sh") | crontab -
```

---

## 🐛 Troubleshooting

### Dashboard Not Loading?

```bash
# Check dashboard logs
docker logs cyber_mirage_dashboard

# Restart dashboard
docker restart cyber_mirage_dashboard

# Check if port 8501 is open
sudo netstat -tulpn | grep 8501
```

### Database Connection Failed?

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs cyber_mirage_postgres

# Verify password in .env.production
cat .env.production | grep POSTGRES_PASSWORD
```

### No Attacks Showing?

```bash
# Check honeypots are listening
docker logs cyber_mirage_honeypots

# Verify ports are open
sudo netstat -tulpn | grep -E '2222|2121|8080'

# Check database has data
docker exec -it cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -c "SELECT COUNT(*) FROM attack_sessions;"
```

---

## 📈 Scaling

### Increase Resources

```bash
# Stop instance
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Change instance type
aws ec2 modify-instance-attribute --instance-id i-1234567890abcdef0 --instance-type t2.xlarge

# Start instance
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

### Add More Honeypots

Edit `docker-compose.production.yml` to add more honeypot instances or increase resource limits.

---

## ✅ Production Checklist

- [ ] Strong passwords in `.env.production`
- [ ] Security Group properly configured
- [ ] All services running (`docker ps`)
- [ ] Dashboard accessible at `:8501`
- [ ] Grafana accessible at `:3000`
- [ ] Database has data (`SELECT COUNT(*)`)
- [ ] Automatic backups configured
- [ ] Monitoring alerts setup
- [ ] SSL certificate (optional)
- [ ] Restricted Prometheus access

---

**🎉 Congratulations! Cyber Mirage is now running in production on AWS!**

**Main Dashboard:** `http://YOUR_EC2_IP:8501/`
