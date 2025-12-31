#!/bin/bash
#═══════════════════════════════════════════════════════════════════════════════
# 📦 Cyber Mirage - Install Systemd Service
# Enables auto-start on boot
#═══════════════════════════════════════════════════════════════════════════════

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          📦 Installing Systemd Service                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

# Copy service file
sudo cp /home/ubuntu/cyber_mirage/scripts/cyber-mirage.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable cyber-mirage

echo ""
echo "✅ Service installed successfully!"
echo ""
echo "Commands:"
echo "  sudo systemctl start cyber-mirage   # Start services"
echo "  sudo systemctl stop cyber-mirage    # Stop services"
echo "  sudo systemctl status cyber-mirage  # Check status"
echo "  sudo systemctl restart cyber-mirage # Restart services"
echo ""
echo "Services will now auto-start on boot!"
