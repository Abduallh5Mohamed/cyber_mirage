#!/usr/bin/env python3
"""
🎯 MASTER ATTACK CONTROLLER
شغّل كل الهجمات بترتيب واقعي مثل الهاكر الحقيقي!
"""
import subprocess
import time
import sys
from datetime import datetime

ATTACKS = [
    {
        "name": "Port Scanning",
        "file": "attack_port_scan.py",
        "description": "اكتشاف المنافذ المفتوحة",
        "icon": "🔍"
    },
    {
        "name": "Web Scanning",
        "file": "attack_web_scan.py",
        "description": "فحص المواقع والثغرات",
        "icon": "🌐"
    },
    {
        "name": "SSH Brute Force",
        "file": "attack_ssh_brute.py",
        "description": "تخمين كلمات السر SSH",
        "icon": "🔐"
    },
    {
        "name": "SQL Injection",
        "file": "attack_sql_inject.py",
        "description": "اختبار ثغرات SQL",
        "icon": "💉"
    }
]

def print_banner():
    print("\n" + "🔥" * 35)
    print("         🎯 CYBER ATTACK SIMULATOR 🎯")
    print("         اختبار حقيقي لنظام Cyber Mirage")
    print("🔥" * 35 + "\n")

def print_menu():
    print("=" * 70)
    print("اختر نوع الهجوم:")
    print("=" * 70)
    print()
    for i, attack in enumerate(ATTACKS, 1):
        print(f"{i}. {attack['icon']} {attack['name']:20s} - {attack['description']}")
    print(f"5. 🚀 Run ALL Attacks (Full Penetration Test)")
    print(f"0. ❌ Exit")
    print()
    print("=" * 70)

def run_attack(attack):
    print("\n" + "=" * 70)
    print(f"{attack['icon']} Starting: {attack['name']}")
    print("=" * 70)
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    try:
        # تشغيل ملف الهجوم
        result = subprocess.run(
            [sys.executable, attack['file']],
            capture_output=False,
            text=True
        )
        
        print()
        print("=" * 70)
        print(f"✅ {attack['name']} completed")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error running attack: {e}")
        return False

def run_all_attacks():
    print("\n" + "🚀" * 35)
    print("         FULL PENETRATION TEST STARTING!")
    print("         سيتم تشغيل جميع الهجمات بالترتيب")
    print("🚀" * 35)
    print()
    
    print("⚠️ هذا سيحاكي هجوم هاكر حقيقي:")
    print("   1. اكتشاف المنافذ (Reconnaissance)")
    print("   2. فحص الويب (Enumeration)")
    print("   3. هجوم SSH (Exploitation)")
    print("   4. حقن SQL (Data Extraction)")
    print()
    
    input("اضغط Enter للبدء...")
    
    success_count = 0
    
    for i, attack in enumerate(ATTACKS, 1):
        print(f"\n\n{'#' * 70}")
        print(f"STAGE {i}/{len(ATTACKS)}: {attack['name']}")
        print(f"{'#' * 70}\n")
        
        if run_attack(attack):
            success_count += 1
        
        if i < len(ATTACKS):
            print("\n⏳ Waiting 5 seconds before next attack...")
            for remaining in range(5, 0, -1):
                print(f"   {remaining}...", end="\r")
                time.sleep(1)
            print()
    
    # النتيجة النهائية
    print("\n\n" + "🎊" * 35)
    print("         PENETRATION TEST COMPLETED!")
    print("🎊" * 35)
    print()
    print("=" * 70)
    print("📊 FINAL RESULTS:")
    print("=" * 70)
    print(f"✅ Successful attacks: {success_count}/{len(ATTACKS)}")
    print(f"⏰ Finished at: {datetime.now().strftime('%H:%M:%S')}")
    print()
    print("💡 Now check the Cyber Mirage Dashboard:")
    print("   http://localhost:8501")
    print()
    print("   You should see:")
    print("   ✅ All attacks detected")
    print("   ✅ Honeypots engaged")
    print("   ✅ Your IP flagged")
    print("   ✅ Full attack timeline")
    print("=" * 70)

def main():
    print_banner()
    
    print("🎯 Target System: Cyber Mirage")
    print("📍 Target IP: 127.0.0.1 (localhost)")
    print()
    print("⚠️ DISCLAIMER:")
    print("   • هذا اختبار على نظامك المحلي فقط")
    print("   • لا تستخدم هذه الأدوات على أنظمة حقيقية بدون إذن")
    print("   • كل الهجمات سيتم رصدها وتسجيلها")
    print()
    
    input("اضغط Enter للمتابعة...")
    
    while True:
        print_menu()
        
        try:
            choice = input("اختر رقم الهجوم: ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye!\n")
                break
            elif choice == "5":
                run_all_attacks()
            elif choice in ["1", "2", "3", "4"]:
                idx = int(choice) - 1
                run_attack(ATTACKS[idx])
            else:
                print("\n❌ اختيار غير صحيح!\n")
            
            input("\nاضغط Enter للمتابعة...")
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Attack interrupted by user!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
