#!/bin/bash
cd /home/ubuntu/cyber_mirage
echo "=== Docker Compose Config (Honeypots env) ==="
sudo docker compose -f docker-compose.production.yml config 2>/dev/null | sed -n '/  honeypots:/,/healthcheck:/p' | sed -n '/environment:/,/volumes:/p'
