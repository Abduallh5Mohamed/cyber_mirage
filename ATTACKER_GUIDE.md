# 🎯 Attacker Setup Guide

## Your Mission
Test Cyber Mirage's defenses by simulating real attacks.

## Target Information
- **IP Address:** 192.168.1.3
- **Network:** 192.168.1.0/24
- **Ports:** 8080 (HTTP), 2222 (SSH), 2121 (FTP), 3306 (MySQL)

## Quick Start (5 minutes)

### 1. Check Connectivity
```bash
ping 192.168.1.3
```

### 2. Run Automated Attack
```bash
chmod +x attack_simulation.sh
./attack_simulation.sh
```

### 3. Manual Testing
```bash
# Port scan
nmap -sV 192.168.1.3

# Web attack
curl http://192.168.1.3:8080
sqlmap -u "http://192.168.1.3:8080/login" --forms

# SSH bruteforce
hydra -l admin -P passwords.txt ssh://192.168.1.3:2222
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
http://192.168.1.3:8501

Good luck! 🎯
