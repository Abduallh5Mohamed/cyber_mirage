#!/usr/bin/env python3
"""
🔍 Port Scanner - اكتشف المنافذ المفتوحة
أداة حقيقية لفحص المنافذ مثل nmap
"""
import socket
import sys
from datetime import datetime

TARGET = "127.0.0.1"  # غيّره إلى IP الهدف
PORTS = [21, 22, 23, 80, 443, 2121, 2222, 3306, 8080, 8501]

print("=" * 70)
print("🔍 PORT SCANNER - أداة فحص المنافذ")
print("=" * 70)
print(f"🎯 Target: {TARGET}")
print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)
print()

open_ports = []

for port in PORTS:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((TARGET, port))
    
    if result == 0:
        print(f"✅ Port {port:5d} - OPEN 🟢")
        open_ports.append(port)
        
        # محاولة معرفة نوع الخدمة
        try:
            sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = sock.recv(100).decode('utf-8', errors='ignore').strip()
            if banner:
                print(f"   └─ Service: {banner[:50]}")
        except:
            pass
    else:
        print(f"❌ Port {port:5d} - CLOSED")
    
    sock.close()

print()
print("=" * 70)
print("📊 SCAN RESULTS:")
print("=" * 70)
print(f"✅ Open ports found: {len(open_ports)}")
if open_ports:
    print(f"🎯 Open ports: {', '.join(map(str, open_ports))}")
    print()
    print("⚠️ WARNING: These might be HONEYPOTS!")
    print("   The system may be logging your scan right now...")
else:
    print("❌ No open ports found")
print()
print(f"⏰ Finished: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)
