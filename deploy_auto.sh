#!/bin/bash
#
# 🚀 Cyber Mirage - Auto Deploy Script
# نشر تلقائي كامل على Ubuntu Server
#

set -e  # Exit on error

echo "══════════════════════════════════════════════════════════════════════"
echo "🚀 CYBER MIRAGE - AUTOMATED PRODUCTION DEPLOYMENT"
echo "══════════════════════════════════════════════════════════════════════"
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 1: Check if running as root
# ═══════════════════════════════════════════════════════════════
if [ "$EUID" -ne 0 ]; then 
   echo "❌ Please run as root (use: sudo bash deploy.sh)"
   exit 1
fi

echo "✅ Running as root"
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 2: Update system
# ═══════════════════════════════════════════════════════════════
echo "📦 Step 1/10: Updating system packages..."
apt update -qq
apt upgrade -y -qq
echo "✅ System updated"
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 3: Install Docker
# ═══════════════════════════════════════════════════════════════
echo "🐳 Step 2/10: Installing Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker already installed: $(docker --version)"
else
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "✅ Docker installed: $(docker --version)"
fi
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 4: Install Docker Compose
# ═══════════════════════════════════════════════════════════════
echo "🐙 Step 3/10: Installing Docker Compose..."
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    echo "✅ Docker Compose already installed"
else
    apt install docker-compose-plugin -y -qq
    echo "✅ Docker Compose installed"
fi
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 5: Install additional tools
# ═══════════════════════════════════════════════════════════════
echo "🛠️ Step 4/10: Installing utilities..."
apt install -y -qq curl wget git unzip htop nano
echo "✅ Utilities installed"
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 6: Setup Firewall (UFW)
# ═══════════════════════════════════════════════════════════════
echo "🔒 Step 5/10: Configuring firewall..."
apt install -y ufw

# Allow SSH first (critical!)
ufw allow 22/tcp

# Honeypot ports (public)
ufw allow 2222/tcp comment 'SSH Honeypot'
ufw allow 8080/tcp comment 'HTTP Honeypot'
ufw allow 2121/tcp comment 'FTP Honeypot'
ufw allow 3306/tcp comment 'MySQL Honeypot'

# Dashboard (optional - can be closed later)
ufw allow 8501/tcp comment 'Streamlit Dashboard'

# Enable firewall (non-interactive)
echo "y" | ufw enable

ufw status numbered

echo "✅ Firewall configured"
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 7: Create project directory
# ═══════════════════════════════════════════════════════════════
echo "📁 Step 6/10: Creating project directory..."
PROJECT_DIR="/opt/cyber_mirage"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR
echo "✅ Project directory: $PROJECT_DIR"
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 8: Generate .env.production with random passwords
# ═══════════════════════════════════════════════════════════════
echo "🔐 Step 7/10: Generating secure credentials..."

# Generate random passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
GRAFANA_PASSWORD=$(openssl rand -base64 20 | tr -d "=+/" | cut -c1-16)
GRAFANA_SECRET=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

cat > .env.production << EOF
# ═══════════════════════════════════════════════════════════════
# Cyber Mirage Production Environment Variables
# Generated: $(date)
# ═══════════════════════════════════════════════════════════════

ENVIRONMENT=production

# Database
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_USER=cybermirage
POSTGRES_DB=cyber_mirage
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_HOST=redis
REDIS_PORT=6379

# Grafana
GRAFANA_PASSWORD=$GRAFANA_PASSWORD
GRAFANA_SECRET=$GRAFANA_SECRET

# API Keys (Optional - add your own)
VIRUSTOTAL_API_KEY=
ABUSEIPDB_API_KEY=
SHODAN_API_KEY=

# Logging
LOG_LEVEL=INFO

# Monitoring
PROMETHEUS_RETENTION_DAYS=30
GRAFANA_ALLOW_SIGNUP=false
EOF

chmod 600 .env.production

echo "✅ Credentials generated and saved to .env.production"
echo ""
echo "🔑 IMPORTANT - Save these credentials:"
echo "────────────────────────────────────────────────────────────────"
echo "PostgreSQL Password: $POSTGRES_PASSWORD"
echo "Redis Password: $REDIS_PASSWORD"
echo "Grafana Password: $GRAFANA_PASSWORD"
echo "────────────────────────────────────────────────────────────────"
echo ""

# Save credentials to a secure file
cat > /root/cyber_mirage_credentials.txt << EOF
Cyber Mirage Credentials
Generated: $(date)
═══════════════════════════════════════════════════════════════

PostgreSQL:
  Username: cybermirage
  Password: $POSTGRES_PASSWORD
  Port: 5433 (localhost only)

Redis:
  Password: $REDIS_PASSWORD
  Port: 6379 (localhost only)

Grafana:
  Username: admin
  Password: $GRAFANA_PASSWORD
  URL: http://localhost:3000 (use SSH tunnel)

Dashboard:
  URL: http://$(curl -s ifconfig.me):8501

Honeypots:
  SSH: $(curl -s ifconfig.me):2222
  HTTP: http://$(curl -s ifconfig.me):8080
  FTP: $(curl -s ifconfig.me):2121
  MySQL: $(curl -s ifconfig.me):3306

═══════════════════════════════════════════════════════════════
⚠️ Keep this file secure! Delete after saving elsewhere.
EOF

chmod 600 /root/cyber_mirage_credentials.txt
echo "📝 Credentials also saved to: /root/cyber_mirage_credentials.txt"
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 9: Download/Setup project files
# ═══════════════════════════════════════════════════════════════
echo "📥 Step 8/10: Setting up project files..."

# If files don't exist, create minimal structure
if [ ! -f "docker-compose.production.yml" ]; then
    echo "⚠️ Project files not found. You need to upload them."
    echo ""
    echo "From your local machine, run:"
    echo "  scp -r cyber_mirage/* root@$(curl -s ifconfig.me):$PROJECT_DIR/"
    echo ""
    echo "Or use Git:"
    echo "  git clone <your-repo-url> $PROJECT_DIR"
    echo ""
    read -p "Press Enter after uploading files, or Ctrl+C to exit..."
fi

echo "✅ Project files ready"
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 10: Build and start services
# ═══════════════════════════════════════════════════════════════
echo "🏗️ Step 9/10: Building Docker images..."
echo "⏳ This may take 5-10 minutes..."

if [ -f "docker-compose.production.yml" ]; then
    docker compose -f docker-compose.production.yml build
    echo "✅ Docker images built"
else
    echo "❌ docker-compose.production.yml not found!"
    echo "Please upload project files first."
    exit 1
fi
echo ""

echo "🚀 Step 10/10: Starting all services..."
docker compose -f docker-compose.production.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30

echo ""
echo "✅ Services started!"
echo ""

# ═══════════════════════════════════════════════════════════════
# Final: Display status
# ═══════════════════════════════════════════════════════════════
echo "══════════════════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE!"
echo "══════════════════════════════════════════════════════════════════════"
echo ""

PUBLIC_IP=$(curl -s ifconfig.me)

echo "🌐 Your Cyber Mirage is now ONLINE at:"
echo ""
echo "🎯 Honeypots (for hackers to attack):"
echo "   SSH:   ssh://root@$PUBLIC_IP:2222"
echo "   HTTP:  http://$PUBLIC_IP:8080"
echo "   FTP:   ftp://$PUBLIC_IP:2121"
echo "   MySQL: mysql://$PUBLIC_IP:3306"
echo ""
echo "📊 Dashboard (monitoring):"
echo "   http://$PUBLIC_IP:8501"
echo ""
echo "🔧 Monitoring (via SSH tunnel):"
echo "   Grafana: ssh -L 3000:localhost:3000 root@$PUBLIC_IP"
echo "            then open http://localhost:3000"
echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo "📊 Service Status:"
echo "══════════════════════════════════════════════════════════════════════"
docker compose -f docker-compose.production.yml ps
echo ""

echo "══════════════════════════════════════════════════════════════════════"
echo "📝 Next Steps:"
echo "══════════════════════════════════════════════════════════════════════"
echo "1. Check logs: docker compose -f docker-compose.production.yml logs -f"
echo "2. Open dashboard: http://$PUBLIC_IP:8501"
echo "3. Monitor attacks in real-time"
echo "4. Announce your honeypot to hackers!"
echo ""
echo "🔐 Credentials saved in: /root/cyber_mirage_credentials.txt"
echo ""
echo "⚠️ To announce your honeypot:"
echo "   Post on Twitter: \"New honeypot challenge at $PUBLIC_IP!\""
echo "   Or wait - Shodan will find it automatically in a few days"
echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo "🎉 Happy Hacking (Defense)! 🛡️"
echo "══════════════════════════════════════════════════════════════════════"
