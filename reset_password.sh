#!/bin/bash
cd /home/ubuntu/cyber_mirage

echo "=== Resetting PostgreSQL password ==="
# Connect as postgres (no password needed for first connection)
sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U postgres -d postgres << EOF
ALTER USER cybermirage WITH PASSWORD 'ChangeThisToSecurePassword123!';
\q
EOF

echo "Password reset complete"
