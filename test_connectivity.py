#!/usr/bin/env python3
"""Quick connectivity test"""
import socket
import sys

TARGET = "192.168.1.3"
PORTS = [8501, 8080, 2222, 2121, 3306]

print("🧪 Testing Cyber Mirage connectivity...")
print(f"Target: {TARGET}\n")

for port in PORTS:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((TARGET, port))
    
    if result == 0:
        print(f"✅ Port {port:5d} - OPEN")
    else:
        print(f"❌ Port {port:5d} - CLOSED")
    
    sock.close()

print("\n✅ Test complete!")
