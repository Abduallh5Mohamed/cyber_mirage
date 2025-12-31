#!/bin/bash
#═══════════════════════════════════════════════════════════════════════════════
# 🔐 Cyber Mirage - Security Hardening Script
# Run after deploying to harden the server
#═══════════════════════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "\n${GREEN}▶ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          🔐 Cyber Mirage - Security Hardening                    ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Disable SSH Password Authentication
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 1/5: Disabling SSH password authentication..."

sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

sudo systemctl restart sshd

# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Install and Configure Fail2Ban
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 2/5: Installing Fail2Ban..."

sudo apt install fail2ban -y

# Create custom jail configuration
sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5
ignoreip = 127.0.0.1/8

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 24h
EOF

sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Configure UFW Firewall
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 3/5: Configuring UFW firewall..."

# Reset UFW to default
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH (management)
sudo ufw allow 22/tcp comment 'SSH'

# Nginx/HTTPS
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Dashboard
sudo ufw allow 8501/tcp comment 'Streamlit Dashboard'

# Grafana (consider restricting to specific IPs)
sudo ufw allow 3000/tcp comment 'Grafana'

# Honeypot ports
sudo ufw allow 2222/tcp comment 'SSH Honeypot'
sudo ufw allow 2121/tcp comment 'FTP Honeypot'
sudo ufw allow 8080/tcp comment 'HTTP Honeypot'
sudo ufw allow 8443/tcp comment 'HTTPS Honeypot'
sudo ufw allow 3307/tcp comment 'MySQL Honeypot'
sudo ufw allow 5434/tcp comment 'PostgreSQL Honeypot'
sudo ufw allow 502/tcp comment 'Modbus Honeypot'
sudo ufw allow 1025/tcp comment 'Custom Honeypot'
sudo ufw allow 445/tcp comment 'SMB Honeypot'
sudo ufw allow 139/tcp comment 'NetBIOS Honeypot'

# Enable UFW
sudo ufw --force enable

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Secure Shared Memory
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 4/5: Securing shared memory..."

# Add tmpfs mount for shared memory if not exists
if ! grep -q "/run/shm" /etc/fstab; then
    echo "tmpfs /run/shm tmpfs defaults,noexec,nosuid 0 0" | sudo tee -a /etc/fstab
fi

# ─────────────────────────────────────────────────────────────────────────────
# Step 5: Setup Auto-Updates
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 5/5: Setting up automatic security updates..."

sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ✅ SECURITY HARDENING COMPLETE!                                 ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║                                                                  ║"
echo "║  ✓ SSH password authentication disabled                         ║"
echo "║  ✓ Root login disabled                                          ║"
echo "║  ✓ Fail2Ban installed and configured                            ║"
echo "║  ✓ UFW firewall enabled                                         ║"
echo "║  ✓ Automatic security updates enabled                           ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

print_step "UFW Status:"
sudo ufw status numbered

print_step "Fail2Ban Status:"
sudo fail2ban-client status

print_warning "Remember to test SSH access before closing your current session!"
