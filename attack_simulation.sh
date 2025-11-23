#!/bin/bash
# 🎯 Automated Attack Script
# Run this from Kali Linux

TARGET_IP="192.168.1.3"
LOG_FILE="attack_log_$(date +%Y%m%d_%H%M%S).txt"

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
