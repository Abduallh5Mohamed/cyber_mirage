#!/bin/bash
set -e
cd /home/ubuntu/cyber_mirage

echo "=== Pull latest ==="
git pull origin main || true

echo "=== Build & restart honeypots ==="
sudo docker compose -f docker-compose.production.yml build --no-cache honeypots || true
sudo docker compose -f docker-compose.production.yml up -d honeypots

sleep 3

echo "=== Honeypots logs (tail) ==="
sudo docker compose -f docker-compose.production.yml logs honeypots --tail=40
