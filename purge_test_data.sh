#!/bin/bash
cd /home/ubuntu/cyber_mirage
sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U cybermirage -d cyber_mirage <<'SQL'
BEGIN;
TRUNCATE TABLE attack_actions RESTART IDENTITY;
TRUNCATE TABLE agent_decisions;
TRUNCATE TABLE deception_events;
TRUNCATE TABLE attack_sessions RESTART IDENTITY CASCADE;
COMMIT;
SQL
