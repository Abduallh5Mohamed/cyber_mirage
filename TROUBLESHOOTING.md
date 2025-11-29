# 🐛 Troubleshooting Guide - Cyber Mirage

Quick solutions to common issues.

---

## 🚫 Dashboard Issues

### Problem: Dashboard won't load (http://YOUR_IP:8501/)

**Solutions:**

1. **Check dashboard container:**
```bash
docker ps | grep dashboard
docker logs cyber_mirage_dashboard
```

2. **Restart dashboard:**
```bash
docker restart cyber_mirage_dashboard
```

3. **Check port is open:**
```bash
sudo netstat -tulpn | grep 8501
# OR
ss -tulpn | grep 8501
```

4. **Check Security Group (AWS):**
- Port 8501 must allow inbound from 0.0.0.0/0

---

## 🗄️ Database Connection Errors

### Problem: "Database connection failed"

**Solutions:**

1. **Check PostgreSQL is running:**
```bash
docker ps | grep postgres
docker logs cyber_mirage_postgres
```

2. **Verify password matches:**
```bash
# Check .env.production
cat .env.production | grep POSTGRES_PASSWORD

# Try connecting manually
docker exec -it cyber_mirage_postgres psql -U cybermirage -d cyber_mirage
```

3. **Reset PostgreSQL password:**
```bash
docker-compose -f docker-compose.production.yml down
# Edit .env.production with new password
docker-compose -f docker-compose.production.yml up -d
```

---

## 🍯 Honeypots Not Receiving Traffic

### Problem: No attacks showing in dashboard

**Solutions:**

1. **Check honeypots are listening:**
```bash
docker logs cyber_mirage_honeypots
sudo netstat -tulpn | grep -E '2222|2121|8080|445|3307'
```

2. **Test honeypots locally:**
```bash
# SSH honeypot
nc localhost 2222

# FTP honeypot 
nc localhost 2121

# HTTP honeypot
curl http://localhost:8080/
```

3. **Check Security Group allows traffic:**
- Verify ALL honeypot ports are open (2222, 2121, 8080, 445, 3307, 5434, 502, 139, 1025, 8443)

4. **Check database for attacks:**
```sql
docker exec -it cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -c "SELECT COUNT(*) FROM attack_sessions WHERE origin IS NOT NULL;"
```

---

## 🤖 AI Agent Not Making Decisions

### Problem: No AI decisions in database

**Solutions:**

1. **Check AI tables exist:**
```sql
docker exec -it cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -c "\dt"
```

Should show: `agent_decisions`, `deception_events`

2. **Create tables manually:**
```bash
docker exec -it cyber_mirage_honeypots python3 -c "from src.honeypots.honeypot_manager import ensure_ai_tables; ensure_ai_tables()"
```

3. **Check honeypot logs for AI activity:**
```bash
docker logs cyber_mirage_honeypots | grep "AI Decision"
```

---

## 🔴 Redis Connection Issues

### Problem: "Redis connection failed"

**Solutions:**

1. **Check Redis is running:**
```bash
docker ps | grep redis
docker logs cyber_mirage_redis
```

2. **Test Redis connection:**
```bash
docker exec -it cyber_mirage_redis redis-cli -a changeme123 PING
# Should return: PONG
```

3. **Check password:**
```bash
cat .env.production | grep REDIS_PASSWORD
```

---

## 📊 Grafana Login Issues

### Problem: Can't login to Grafana (port 3000)

**Default Credentials:**
- Username: `admin`
- Password: Check `.env.production` for `GRAFANA_PASSWORD`

**Reset Password:**
```bash
docker exec -it cyber_mirage_grafana grafana-cli admin reset-admin-password newpassword123
```

---

## 💾 Disk Space Full

### Problem: "No space left on device"

**Solutions:**

1. **Check disk usage:**
```bash
df -h
du -sh /var/lib/docker/
```

2. **Clean Docker:**
```bash
# Remove unused containers/images
docker system prune -a

# Remove unused volumes
docker volume prune
```

3. **Clean logs:**
```bash
# Truncate Docker logs
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'
```

---

## 🚀 Container Won't Start

### Problem: Container crashes immediately

**Solutions:**

1. **Check logs:**
```bash
docker logs CONTAINER_NAME
```

2. **Check resource limits:**
```bash
docker stats
# Look for OOMKilled
```

3. **Increase memory limits:**
Edit `docker-compose.production.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 4G  # Increase this
```

---

## 🔧 Port Already in Use

### Problem: "port is already allocated"

**Solutions:**

1. **Find what's using the port:**
```bash
sudo lsof -i :8501
# OR
sudo netstat -tulpn | grep 8501
```

2. **Kill the process:**
```bash
sudo kill -9 PID_NUMBER
```

3. **Or change the port:**
Edit `docker-compose.production.yml` to use different ports.

---

## 📡 API Keys Not Working

### Problem: Threat intelligence APIs failing

**Solutions:**

1. **Check keys are set:**
```bash
cat .env.production | grep API_KEY
```

2. **Test keys manually:**
```bash
# AbuseIPDB
curl -G https://api.abuseipdb.com/api/v2/check \
  --data-urlencode "ipAddress=118.25.6.39" \
  -H "Key: YOUR_KEY" \
  -H "Accept: application/json"
```

3. **Use local database fallback:**
The system should work without API keys using local threat database.

---

## 🔄 Services Won't Restart

### Problem: `docker-compose restart` fails

**Solutions:**

1. **Full restart:**
```bash
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d
```

2. **Check for port conflicts:**
```bash
sudo netstat -tulpn | grep -E '8501|3000|9090|5432|6379'
```

3. **Rebuild containers:**
```bash
docker-compose -f docker-compose.production.yml up -d --build --force-recreate
```

---

## 🧹 Complete Reset (Nuclear Option)

**WARNING: This deletes ALL data!**

```bash
# Stop all containers
docker-compose -f docker-compose.production.yml down -v

# Remove all volumes
docker volume rm $(docker volume ls -q | grep cyber_mirage)

# Rebuild everything
docker-compose -f docker-compose.production.yml up -d --build
```

---

## 📞 Still Having Issues?

1. **Check GitHub Issues:** https://github.com/Abduallh5Mohamed/cyber_mirage/issues
2. **Review logs:** `docker-compose -f docker-compose.production.yml logs -f`
3. **System requirements:** Ensure 4GB+ RAM, 20GB+ disk
4. **Network:** Check AWS Security Groups allow all required ports

---

**Common Fixes Summary:**

✅ Restart container: `docker restart CONTAINER_NAME`  
✅ View logs: `docker logs CONTAINER_NAME`  
✅ Rebuild: `docker-compose up -d --build`  
✅ Full reset: `docker-compose down -v && docker-compose up -d`
