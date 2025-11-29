#!/bin/bash
set -e
cd /home/ubuntu/cyber_mirage

echo "=== Pulling repo ==="
 git pull origin main || true

echo "=== Compose config (dashboard env) ==="
 sudo docker compose -f docker-compose.production.yml config 2>/dev/null | sed -n '/  dashboard:/,/healthcheck:/p' | sed -n '/environment:/,/volumes:/p' || true

echo "=== Test psql connectivity with known password ==="
 sudo docker compose -f docker-compose.production.yml exec -e PGPASSWORD=ChangeThisToSecurePassword123! -T postgres \
   psql -U cybermirage -d cyber_mirage -c "SELECT current_user, current_database();" || echo "psql test failed"

echo "=== Attempt to reset password explicitly (idempotent) ==="
 sudo docker compose -f docker-compose.production.yml exec -e PGPASSWORD=ChangeThisToSecurePassword123! -T postgres \
   psql -U cybermirage -d cyber_mirage -c "ALTER USER cybermirage WITH PASSWORD 'ChangeThisToSecurePassword123!';" || echo "alter failed"

echo "=== Build & restart dashboard ==="
 sudo docker compose -f docker-compose.production.yml build dashboard || true
 sudo docker compose -f docker-compose.production.yml up -d dashboard

sleep 3

echo "=== Dashboard logs (tail) ==="
 sudo docker compose -f docker-compose.production.yml logs dashboard --tail=30
