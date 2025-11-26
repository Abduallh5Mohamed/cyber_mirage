# فتح Grafana للوصول الخارجي - Enable Grafana External Access

## ⚠️ المشكلة الحالية
Grafana يعمل على port 3000 لكن غير متاح من الإنترنت بسبب AWS Security Group

---

## ✅ الحل - Solution

### الطريقة 1: AWS Console (الأسهل - Recommended)

1. **افتح AWS Console:**
   - اذهب إلى: https://console.aws.amazon.com/ec2/
   - Region: eu-north-1 (Stockholm)

2. **اذهب إلى Security Groups:**
   - في القائمة الجانبية اضغط على **Security Groups**
   - ابحث عن Security Group للـ instance (cyber-mirage-sg أو اسم مشابه)
   - أو اضغط على instance `13.53.131.159` ثم Security → Security groups

3. **Edit Inbound Rules:**
   - اختار Security Group
   - اضغط على **Inbound rules**
   - اضغط **Edit inbound rules**
   - اضغط **Add rule**

4. **أضف القاعدة الجديدة:**
   ```
   Type:         Custom TCP
   Protocol:     TCP
   Port range:   3000
   Source:       0.0.0.0/0
   Description:  Grafana Dashboard
   ```

5. **حفظ:**
   - اضغط **Save rules**

6. **اختبار:**
   ```bash
   curl http://13.53.131.159:3000
   ```

---

### الطريقة 2: AWS CLI (للمتقدمين)

```bash
# 1. Get Security Group ID
aws ec2 describe-instances --instance-ids i-YOUR_INSTANCE_ID --region eu-north-1 --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text

# 2. Add Grafana port rule
aws ec2 authorize-security-group-ingress \
    --group-id sg-YOUR_SECURITY_GROUP_ID \
    --protocol tcp \
    --port 3000 \
    --cidr 0.0.0.0/0 \
    --region eu-north-1
```

---

### الطريقة 3: Terraform (إذا كنت تستخدمه)

```hcl
resource "aws_security_group_rule" "grafana" {
  type              = "ingress"
  from_port         = 3000
  to_port           = 3000
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.cyber_mirage.id
  description       = "Grafana Dashboard"
}
```

---

## 🔓 الـ Ports المطلوبة - Required Ports

| Port | Service | Status | Purpose |
|------|---------|--------|---------|
| 22 | SSH | ✅ Open | Server Management |
| 80 | HTTP | ⚠️ Optional | HTTP redirect |
| 443 | HTTPS | ⚠️ Optional | SSL/TLS |
| 2121 | FTP | ✅ Open | Honeypot FTP |
| 2222 | SSH | ✅ Open | Honeypot SSH |
| 2323 | Telnet | ✅ Open | Honeypot Telnet |
| 3000 | Grafana | ❌ **Closed** | **يحتاج فتح** |
| 3307 | MySQL | ✅ Open | Honeypot MySQL |
| 8080 | HTTP | ✅ Open | Honeypot HTTP |
| 8501 | Streamlit | ✅ Open | Dashboard |
| 9090 | Prometheus | ⚠️ Optional | Metrics |

---

## 🔐 Grafana Credentials - بيانات الدخول

### Default Login
```
URL: http://13.53.131.159:3000
Username: admin
Password: [check in docker logs or config]
```

### الحصول على Password من Docker
```bash
ssh -i ~/.ssh/cyber_mirage ubuntu@13.53.131.159
sudo docker logs cyber_mirage_grafana 2>&1 | grep -i password
```

أو من متغير البيئة:
```bash
sudo docker exec cyber_mirage_grafana env | grep GF_SECURITY_ADMIN_PASSWORD
```

---

## ✅ التحقق من الوصول - Verify Access

### Test من خارج AWS
```bash
# Test connection
curl -I http://13.53.131.159:3000

# Expected output:
HTTP/1.1 302 Found
Location: /login
```

### Test Grafana API
```bash
curl http://13.53.131.159:3000/api/health

# Expected:
{
  "commit": "...",
  "database": "ok",
  "version": "10.2.3"
}
```

### افتح في المتصفح
```
http://13.53.131.159:3000
```

يجب أن ترى صفحة تسجيل الدخول لـ Grafana

---

## 📊 Grafana Dashboards المتوفرة

بعد الدخول ستجد:
1. **Cyber Mirage Overview** - نظرة عامة على الهجمات
2. **Attack Timeline** - جدول زمني للهجمات
3. **Threat Intelligence** - معلومات التهديدات
4. **Honeypot Performance** - أداء الـ honeypots
5. **AI Engine Metrics** - مقاييس محرك الذكاء الاصطناعي

---

## 🛡️ Security Hardening (اختياري)

### تقييد الوصول لـ IP معين
إذا كنت تريد الوصول لـ Grafana من IP محدد فقط:

```bash
aws ec2 authorize-security-group-ingress \
    --group-id sg-YOUR_SECURITY_GROUP_ID \
    --protocol tcp \
    --port 3000 \
    --cidr YOUR_IP_ADDRESS/32 \
    --region eu-north-1
```

مثال:
```bash
# Allow only from your IP
--cidr 102.45.67.89/32
```

### تفعيل HTTPS (موصى به للإنتاج)
```bash
# Install Nginx reverse proxy
ssh ubuntu@13.53.131.159
sudo apt install nginx certbot python3-certbot-nginx

# Configure Nginx for Grafana
sudo nano /etc/nginx/sites-available/grafana

# Add config:
server {
    listen 443 ssl;
    server_name grafana.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/grafana.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/grafana.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}

# Get SSL certificate
sudo certbot --nginx -d grafana.yourdomain.com
```

---

## 🔧 Troubleshooting

### Grafana لا يفتح بعد فتح Port
```bash
# Check if Grafana container is running
ssh ubuntu@13.53.131.159
sudo docker ps | grep grafana

# Check Grafana logs
sudo docker logs cyber_mirage_grafana --tail 50

# Restart Grafana
cd /opt/cyber_mirage
sudo docker compose -f docker-compose.production.yml restart grafana
```

### Port 3000 محجوب من الـ Firewall
```bash
# Check UFW
sudo ufw status

# If active, allow port 3000
sudo ufw allow 3000/tcp
```

### Grafana يعمل لكن بطيء
```bash
# Check system resources
ssh ubuntu@13.53.131.159
htop

# Check Grafana memory
sudo docker stats cyber_mirage_grafana
```

---

## 📞 Next Steps

1. ✅ افتح port 3000 في AWS Security Group
2. 🔐 سجل دخول إلى Grafana: http://13.53.131.159:3000
3. 📊 تحقق من الـ dashboards
4. 🔗 اربط Prometheus datasource (يجب أن يكون موجود تلقائياً)
5. 📈 شاهد البيانات real-time

---

## ✅ Success Checklist

- [ ] Port 3000 مفتوح في Security Group
- [ ] Grafana يفتح من المتصفح
- [ ] تم تسجيل الدخول بنجاح
- [ ] Dashboards تعرض بيانات
- [ ] Prometheus datasource متصل
- [ ] Attack data visible في الـ panels

---

**Current Status:**
- ✅ Dashboard (Port 8501) - Working with real data
- ❌ Grafana (Port 3000) - **Needs port opening**
- ✅ Honeypots - Active and capturing attacks
- ✅ AI Engine - Connected to PostgreSQL
- ✅ PostgreSQL - 13 real attacks stored
- ✅ Redis - Threat intelligence operational
