#!/usr/bin/env python3
"""Real-time Attack Monitor"""
import time
import json
from pathlib import Path
from datetime import datetime

print("🔍 Monitoring for attacks...")
print("Press Ctrl+C to stop\n")

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
    print("\n👋 Monitoring stopped")
