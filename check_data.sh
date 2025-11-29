#!/bin/bash
cd /home/ubuntu/cyber_mirage
sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U cybermirage -d cyber_mirage << EOF
SELECT 'attack_sessions' as table_name, COUNT(*) as row_count FROM attack_sessions
UNION ALL
SELECT 'attack_statistics', COUNT(*) FROM attack_statistics
UNION ALL
SELECT 'deception_events', COUNT(*) FROM deception_events
UNION ALL
SELECT 'agent_decisions', COUNT(*) FROM agent_decisions;
EOF
