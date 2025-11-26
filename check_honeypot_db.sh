#!/bin/bash
# Check Honeypot Database Status

echo "==================================="
echo "Checking PostgreSQL Attack Records"
echo "==================================="

ssh -i ~/.ssh/cyber_mirage ubuntu@13.53.131.159 << 'ENDSSH'

echo ""
echo "[1] Checking attack_sessions table count:"
sudo docker exec cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -t -c "SELECT COUNT(*) FROM attack_sessions;"

echo ""
echo "[2] Checking recent attacks:"
sudo docker exec cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -c "SELECT id, attacker_name, origin, start_time FROM attack_sessions ORDER BY start_time DESC LIMIT 5;"

echo ""
echo "[3] Checking honeypot environment variables:"
sudo docker exec cyber_mirage_honeypots env | grep -E "POSTGRES|DATABASE"

echo ""
echo "[4] Testing PostgreSQL connection from honeypots:"
sudo docker exec cyber_mirage_honeypots ping -c 2 postgres || echo "Cannot reach postgres container"

echo ""
echo "[5] Checking if honeypots can connect to PostgreSQL:"
sudo docker exec cyber_mirage_honeypots python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='postgres',
        database='cyber_mirage',
        user='cybermirage',
        password='changeme123'
    )
    print('✅ PostgreSQL connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
"

ENDSSH
