#!/bin/bash
cd /home/ubuntu/cyber_mirage
echo "=== Environment Variables ==="
cat .env | grep POSTGRES
echo ""
echo "=== Docker Network ==="
sudo docker network ls
echo ""
echo "=== Dashboard Container Env ==="
sudo docker inspect cyber_mirage_dashboard | grep -A 20 "Env"
