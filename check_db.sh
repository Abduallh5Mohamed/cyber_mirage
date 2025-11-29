#!/bin/bash
cd /home/ubuntu/cyber_mirage
sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U cybermirage -d cyber_mirage << EOF
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
EOF
