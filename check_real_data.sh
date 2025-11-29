#!/bin/bash
cd /home/ubuntu/cyber_mirage
sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U cybermirage -d cyber_mirage << EOF
-- Check attack_sessions data
SELECT 'attack_sessions' as table_name, COUNT(*) as total_rows FROM attack_sessions;

-- Check if there's data with origin
SELECT 'attack_sessions with origin' as check_type, COUNT(*) as count FROM attack_sessions WHERE origin IS NOT NULL;

-- Sample some actual data
SELECT 'Sample attack data:' as info;
SELECT origin, attacker_name, detected, created_at FROM attack_sessions LIMIT 5;

-- Check attack_statistics
SELECT 'attack_statistics' as table_name, COUNT(*) as total_rows FROM attack_statistics;

-- Check deception_events
SELECT 'deception_events' as table_name, COUNT(*) as total_rows FROM deception_events;
EOF
