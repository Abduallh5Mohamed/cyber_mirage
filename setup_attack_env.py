#!/usr/bin/env python3
"""
🎯 Setup Real Attack Environment
يجهز بيئة كاملة لاختبار Cyber Mirage ضد هجمات حقيقية

Usage:
    python setup_attack_env.py
"""

import os
import sys
import socket
import subprocess
import json
from datetime import datetime
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════════════╗
║  🎯 Cyber Mirage - Real Attack Environment Setup            ║
╚══════════════════════════════════════════════════════════════╝
""")

# 1. Check system info
print("📊 System Information:")
print("─"*60)

try:
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"✅ Hostname: {hostname}")
    print(f"✅ Local IP: {local_ip}")
except Exception as e:
    print(f"❌ Error getting system info: {e}")
    local_ip = "unknown"

print()

# 2. Check required directories
print("📁 Checking Directories:")
print("─"*60)

required_dirs = [
    "data/logs",
    "data/honeypots",
    "data/forensics",
    "data/attacks",
    "data/iocs"
]

for dir_path in required_dirs:
    full_path = Path(dir_path)
    if full_path.exists():
        print(f"✅ {dir_path} - EXISTS")
    else:
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"🆕 {dir_path} - CREATED")

print()

# 3. Create attack configuration
print("⚙️ Creating Attack Configuration:")
print("─"*60)

config = {
    "environment": {
        "type": "isolated_testing",
        "defender_ip": local_ip,
        "attacker_ip": "CONFIGURE_THIS",
        "network": "192.168.1.0/24"
    },
    "honeypots": {
        "web": {"port": 8080, "enabled": True},
        "ssh": {"port": 2222, "enabled": True},
        "ftp": {"port": 2121, "enabled": True},
        "database": {"port": 3306, "enabled": True}
    },
    "monitoring": {
        "dashboard_port": 8501,
        "logging_level": "DEBUG",
        "real_time": True
    },
    "ai_defense": {
        "enabled": True,
        "models": ["neural", "swarm", "quantum", "bio"],
        "response_time": "< 1 second"
    },
    "created_at": datetime.now().isoformat()
}

config_file = "attack_test_config.json"
with open(config_file, 'w') as f:
    json.dump(config, indent=2, fp=f)

print(f"✅ Config saved to: {config_file}")
print()

# 4. Create startup scripts
print("📝 Creating Startup Scripts:")
print("─"*60)

# PowerShell script for Windows
powershell_script = """# 🎯 Start Cyber Mirage Defense
# Run this script to start all components

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🎭 Starting Cyber Mirage Defense System" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "⚡ Activating virtual environment..." -ForegroundColor Yellow
& .\\venv\\Scripts\\Activate.ps1

# Start Dashboard in background
Write-Host "📊 Starting Dashboard..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\\venv\\Scripts\\python.exe -m streamlit run src/dashboard/streamlit_app.py"
Start-Sleep -Seconds 3

# Start Environment
Write-Host "🌐 Starting Honeypot Environment..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\\venv\\Scripts\\python.exe src/environment/base_env.py"
Start-Sleep -Seconds 2

# Start Monitoring
Write-Host "📡 Starting Log Monitoring..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Get-Content data\\logs\\*.log -Wait -Tail 20"

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ All Systems Started!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Dashboard: http://localhost:8501" -ForegroundColor Cyan
Write-Host "📊 Your IP: """ + local_ip + """" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Ready for attack testing!" -ForegroundColor Yellow
Write-Host ""
"""

with open("start_defense.ps1", 'w', encoding='utf-8') as f:
    f.write(powershell_script)

print("✅ Created: start_defense.ps1")

# Bash script for attacker (Kali Linux)
bash_script = """#!/bin/bash
# 🎯 Automated Attack Script
# Run this from Kali Linux

TARGET_IP=\"""" + local_ip + """\"
LOG_FILE=\"attack_log_$(date +%Y%m%d_%H%M%S).txt\"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🎯 Automated Attack Against Cyber Mirage                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Target: $TARGET_IP"
echo "Log: $LOG_FILE"
echo ""

# Phase 1: Reconnaissance
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 Phase 1: Reconnaissance"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[$(date)] Starting recon..." | tee -a $LOG_FILE
nmap -sV $TARGET_IP | tee -a $LOG_FILE
sleep 5

# Phase 2: Port Scan
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Phase 2: Full Port Scan"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[$(date)] Scanning all ports..." | tee -a $LOG_FILE
nmap -p 1-10000 $TARGET_IP | tee -a $LOG_FILE
sleep 5

# Phase 3: Service Detection
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Phase 3: Service Detection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[$(date)] Detecting services..." | tee -a $LOG_FILE
nmap -sV -sC $TARGET_IP | tee -a $LOG_FILE
sleep 5

# Phase 4: Web Testing
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Phase 4: Web Application Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[$(date)] Testing web services..." | tee -a $LOG_FILE

# Test HTTP
curl -I http://$TARGET_IP:8080 2>&1 | tee -a $LOG_FILE
curl http://$TARGET_IP:8080 2>&1 | tee -a $LOG_FILE

# Simple SQL injection test
curl "http://$TARGET_IP:8080/login?user=admin'--" 2>&1 | tee -a $LOG_FILE
sleep 3

# Phase 5: SSH Testing
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 Phase 5: SSH Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[$(date)] Testing SSH..." | tee -a $LOG_FILE

# Test SSH connection
nc -zv $TARGET_IP 2222 2>&1 | tee -a $LOG_FILE
sleep 2

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Attack Simulation Complete!                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results saved to: $LOG_FILE"
echo "🎯 Check Cyber Mirage Dashboard for detection results"
echo ""
"""

with open("attack_simulation.sh", 'w', encoding='utf-8') as f:
    f.write(bash_script)

print("✅ Created: attack_simulation.sh")
print()

# 5. Create monitoring script
print("📊 Creating Monitoring Script:")
print("─"*60)

monitor_script = """#!/usr/bin/env python3
\"\"\"Real-time Attack Monitor\"\"\"
import time
import json
from pathlib import Path
from datetime import datetime

print("🔍 Monitoring for attacks...")
print("Press Ctrl+C to stop\\n")

log_dir = Path("data/logs")
attacks_seen = set()

try:
    while True:
        # Check for new attack logs
        for log_file in log_dir.glob("attack_*.json"):
            if log_file not in attacks_seen:
                with open(log_file) as f:
                    attack = json.load(f)
                    print(f"🚨 NEW ATTACK DETECTED!")
                    print(f"   Time: {attack.get('timestamp')}")
                    print(f"   IP: {attack.get('source_ip')}")
                    print(f"   Type: {attack.get('attack_type')}")
                    print(f"   Severity: {attack.get('severity')}/10")
                    print()
                    attacks_seen.add(log_file)
        
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\\n👋 Monitoring stopped")
"""

with open("monitor_attacks.py", 'w', encoding='utf-8') as f:
    f.write(monitor_script)

print("✅ Created: monitor_attacks.py")
print()

# 6. Create quick test script
print("🧪 Creating Quick Test Script:")
print("─"*60)

test_script = f"""#!/usr/bin/env python3
\"\"\"Quick connectivity test\"\"\"
import socket
import sys

TARGET = "{local_ip}"
PORTS = [8501, 8080, 2222, 2121, 3306]

print("🧪 Testing Cyber Mirage connectivity...")
print(f"Target: {{TARGET}}\\n")

for port in PORTS:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((TARGET, port))
    
    if result == 0:
        print(f"✅ Port {{port:5d}} - OPEN")
    else:
        print(f"❌ Port {{port:5d}} - CLOSED")
    
    sock.close()

print("\\n✅ Test complete!")
"""

with open("test_connectivity.py", 'w', encoding='utf-8') as f:
    f.write(test_script)

print("✅ Created: test_connectivity.py")
print()

# 7. Create README for attacker
print("📖 Creating Attacker Guide:")
print("─"*60)

attacker_guide = f"""# 🎯 Attacker Setup Guide

## Your Mission
Test Cyber Mirage's defenses by simulating real attacks.

## Target Information
- **IP Address:** {local_ip}
- **Network:** 192.168.1.0/24
- **Ports:** 8080 (HTTP), 2222 (SSH), 2121 (FTP), 3306 (MySQL)

## Quick Start (5 minutes)

### 1. Check Connectivity
```bash
ping {local_ip}
```

### 2. Run Automated Attack
```bash
chmod +x attack_simulation.sh
./attack_simulation.sh
```

### 3. Manual Testing
```bash
# Port scan
nmap -sV {local_ip}

# Web attack
curl http://{local_ip}:8080
sqlmap -u "http://{local_ip}:8080/login" --forms

# SSH bruteforce
hydra -l admin -P passwords.txt ssh://{local_ip}:2222
```

## Tools Needed
- nmap
- curl
- sqlmap
- hydra
- metasploit (optional)

## Expected Behavior
- System should detect you
- You'll be redirected to honeypots
- Your actions will be logged
- Dashboard will show your attacks in real-time

## Results
Check the defender's dashboard at:
http://{local_ip}:8501

Good luck! 🎯
"""

with open("ATTACKER_GUIDE.md", 'w', encoding='utf-8') as f:
    f.write(attacker_guide)

print("✅ Created: ATTACKER_GUIDE.md")
print()

# 8. Final summary
print("╔══════════════════════════════════════════════════════════════╗")
print("║  ✅ Setup Complete!                                          ║")
print("╚══════════════════════════════════════════════════════════════╝")
print()
print("📋 Files Created:")
print("   1. attack_test_config.json    - Configuration")
print("   2. start_defense.ps1           - Start all components")
print("   3. attack_simulation.sh        - Automated attack script")
print("   4. monitor_attacks.py          - Real-time monitoring")
print("   5. test_connectivity.py        - Connectivity test")
print("   6. ATTACKER_GUIDE.md           - Guide for attacker")
print()
print("🎯 Next Steps:")
print("   1. Run: .\\start_defense.ps1")
print("   2. Open dashboard: http://localhost:8501")
print(f"   3. From Kali Linux, attack: {local_ip}")
print("   4. Watch the dashboard for results!")
print()
print("💡 Defender IP:", local_ip)
print("📊 Dashboard: http://localhost:8501")
print()
print("Ready for real attack testing! 🚀")
print()
