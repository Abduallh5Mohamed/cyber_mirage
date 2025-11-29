#!/bin/bash
cd /home/ubuntu/cyber_mirage
echo "=== Checking .env file ==="
cat .env | grep -i postgres
echo ""
echo "=== Checking docker-compose.production.yml ==="
grep -A 5 "POSTGRES_PASSWORD" docker-compose.production.yml | head -20
