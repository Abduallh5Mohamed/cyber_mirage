#!/bin/bash
cd /home/ubuntu/cyber_mirage
echo "=== Docker Compose Config (Dashboard section) ==="
sudo docker compose -f docker-compose.production.yml config 2>/dev/null | sed -n '/^  dashboard:/,/^  [a-z]/p' | head -40
