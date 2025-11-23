#!/usr/bin/env python3
"""
🌐 Web Scanner - فحص المواقع والثغرات
أداة حقيقية لفحص الويب مثل nikto
"""
import socket
import time
from datetime import datetime

TARGET = "127.0.0.1"
PORT = 8080

# مسارات شائعة للاختبار
PATHS = [
    "/", "/admin", "/login", "/wp-admin", "/administrator",
    "/phpmyadmin", "/config", "/backup", "/api", "/api/users",
    "/robots.txt", "/.git", "/.env", "/debug", "/test",
    "/upload", "/shell.php", "/cmd.php", "/backdoor.php"
]

# SQL Injection payloads للاختبار
SQL_PAYLOADS = [
    "?id=1' OR '1'='1",
    "?id=1' UNION SELECT * FROM users--",
    "?id=1'; DROP TABLE users--",
    "?user=admin'--"
]

print("=" * 70)
print("🌐 WEB VULNERABILITY SCANNER")
print("=" * 70)
print(f"🎯 Target: http://{TARGET}:{PORT}")
print(f"📋 Paths to scan: {len(PATHS)}")
print(f"💉 SQL payloads: {len(SQL_PAYLOADS)}")
print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)
print()

print("🔍 Scanning common paths...")
print("-" * 70)

found_paths = []

for path in PATHS:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((TARGET, PORT))
        
        # إرسال HTTP request
        request = f"GET {path} HTTP/1.1\r\nHost: {TARGET}\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
        sock.send(request.encode())
        
        # استقبال الرد
        response = sock.recv(4096).decode('utf-8', errors='ignore')
        
        # فحص الرد
        if "200 OK" in response or "301" in response or "302" in response:
            status = "✅ FOUND"
            found_paths.append(path)
        elif "404" in response:
            status = "❌ NOT FOUND"
        elif "403" in response:
            status = "🔒 FORBIDDEN"
        else:
            status = "❓ UNKNOWN"
        
        print(f"{status:15s} {path:30s}", end="")
        
        # محاولة كشف محتوى مثير
        if any(word in response.lower() for word in ['password', 'admin', 'user', 'database']):
            print(" 🚨 INTERESTING!")
        else:
            print()
        
        sock.close()
        time.sleep(0.1)
        
    except Exception as e:
        print(f"❌ ERROR      {path:30s} {str(e)[:20]}")

print()
print("-" * 70)
print("💉 Testing SQL Injection vulnerabilities...")
print("-" * 70)

sql_vulnerable = []

for payload in SQL_PAYLOADS:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((TARGET, PORT))
        
        # إرسال payload
        request = f"GET /login{payload} HTTP/1.1\r\nHost: {TARGET}\r\n\r\n"
        sock.send(request.encode())
        
        response = sock.recv(4096).decode('utf-8', errors='ignore')
        
        # البحث عن علامات SQL injection
        if any(word in response.lower() for word in ['sql', 'syntax error', 'mysql', 'database']):
            print(f"🚨 VULNERABLE: {payload}")
            sql_vulnerable.append(payload)
        else:
            print(f"✅ BLOCKED:    {payload}")
        
        sock.close()
        time.sleep(0.1)
        
    except Exception as e:
        print(f"❌ ERROR:     {payload}")

print()
print("=" * 70)
print("📊 SCAN RESULTS:")
print("=" * 70)
print(f"✅ Paths found: {len(found_paths)}")
if found_paths:
    for path in found_paths[:5]:
        print(f"   • {path}")
    if len(found_paths) > 5:
        print(f"   ... and {len(found_paths) - 5} more")

print()
print(f"🚨 SQL Injection points: {len(sql_vulnerable)}")
if sql_vulnerable:
    for vuln in sql_vulnerable:
        print(f"   • {vuln}")

print()
print("⚠️ WARNING:")
if found_paths or sql_vulnerable:
    print("   • This system responded to your probes")
    print("   • BUT: It might be a HONEYPOT!")
    print("   • All data you see could be FAKE")
    print("   • Your scan is definitely being LOGGED")
    print("   • The real system is hidden elsewhere")
else:
    print("   • System appears secure or not responding")
    print("   • OR: You triggered defensive measures")

print()
print(f"⏰ Finished: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)
