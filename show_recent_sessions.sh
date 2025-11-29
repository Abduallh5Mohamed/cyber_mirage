#!/bin/bash
cd /home/ubuntu/cyber_mirage
sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U cybermirage -d cyber_mirage <<'SQL'
\pset format aligned
\pset border 1
SELECT attacker_name, origin, start_time FROM attack_sessions ORDER BY start_time DESC LIMIT 5;
SQL
