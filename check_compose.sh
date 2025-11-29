#!/bin/bash
cd /home/ubuntu/cyber_mirage
echo "=== Checking docker-compose.production.yml ==="
sed -n '/^  dashboard:/,/^  [a-z]/p' docker-compose.production.yml | head -30
