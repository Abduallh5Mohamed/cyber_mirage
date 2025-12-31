#!/bin/bash
#═══════════════════════════════════════════════════════════════════════════════
# 🔒 Cyber Mirage - HTTPS Setup with Nginx & Let's Encrypt
# Run after deploying the main application
#═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "\n${GREEN}▶ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Get domain name
# ─────────────────────────────────────────────────────────────────────────────
if [ -z "$1" ]; then
    echo "Usage: ./setup_https.sh your-domain.com"
    echo "Example: ./setup_https.sh cyber-mirage.example.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          🔒 Cyber Mirage - HTTPS Setup                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Domain: $DOMAIN"
echo "Email:  $EMAIL"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Install Nginx
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 1/4: Installing Nginx..."
sudo apt update
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx

# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Install Certbot
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 2/4: Installing Certbot..."
sudo apt install certbot python3-certbot-nginx -y

# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Configure Nginx
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 3/4: Configuring Nginx..."

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/cyber-mirage > /dev/null << EOF
# Cyber Mirage - Nginx Reverse Proxy Configuration

# Rate limiting
limit_req_zone \$binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=dashboard:10m rate=30r/s;

# Upstream servers
upstream dashboard {
    server 127.0.0.1:8501;
    keepalive 32;
}

upstream grafana {
    server 127.0.0.1:3000;
    keepalive 32;
}

upstream prometheus {
    server 127.0.0.1:9090;
    keepalive 32;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN;

    # SSL certificates (will be configured by Certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL settings
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Dashboard (main) - /
    location / {
        limit_req zone=dashboard burst=50 nodelay;
        
        proxy_pass http://dashboard;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Streamlit WebSocket support
        proxy_read_timeout 86400;
        proxy_buffering off;
    }

    # Streamlit internal endpoints
    location /_stcore/ {
        proxy_pass http://dashboard/_stcore/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }

    # Grafana - /grafana/
    location /grafana/ {
        limit_req zone=general burst=20 nodelay;
        
        proxy_pass http://grafana/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Prometheus - /prometheus/ (restricted)
    location /prometheus/ {
        # Restrict to specific IPs only
        # allow YOUR_ADMIN_IP;
        # deny all;
        
        limit_req zone=general burst=10 nodelay;
        
        proxy_pass http://prometheus/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "OK";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/cyber-mirage /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Get SSL Certificate
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 4/4: Obtaining SSL certificate..."

print_warning "Make sure your domain $DOMAIN is pointing to this server's IP!"
echo ""
read -p "Press Enter to continue with SSL certificate request..."

sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL

# Reload Nginx
sudo systemctl reload nginx

# ─────────────────────────────────────────────────────────────────────────────
# Setup auto-renewal
# ─────────────────────────────────────────────────────────────────────────────
print_step "Setting up auto-renewal..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# ─────────────────────────────────────────────────────────────────────────────
# Complete
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ✅ HTTPS SETUP COMPLETE!                                        ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║                                                                  ║"
echo "║  🔒 Dashboard:  https://$DOMAIN                                  ║"
echo "║  📈 Grafana:    https://$DOMAIN/grafana/                         ║"
echo "║  📉 Prometheus: https://$DOMAIN/prometheus/                      ║"
echo "║                                                                  ║"
echo "║  SSL certificate auto-renews every 90 days.                      ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
