#!/bin/bash
cd /home/ubuntu/cyber_mirage
sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U cybermirage -d cyber_mirage << 'EOF'
\pset format aligned
\pset border 1
SELECT 'attack_sessions' AS table_name, COUNT(*) AS rows FROM attack_sessions;
SELECT 'attack_actions' AS table_name, COUNT(*) AS rows FROM attack_actions;
SELECT 'attack_statistics' AS table_name, COUNT(*) AS rows FROM attack_statistics;
SELECT 'deception_events' AS table_name, COUNT(*) AS rows FROM deception_events;
EOF
