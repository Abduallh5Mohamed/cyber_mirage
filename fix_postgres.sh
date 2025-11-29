#!/bin/bash
cd /home/ubuntu/cyber_mirage

# Get the current password from postgres container
CURRENT_PASS=$(sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U postgres -c "SELECT usename FROM pg_user WHERE usename='cybermirage';" 2>/dev/null | grep cybermirage)

if [ -z "$CURRENT_PASS" ]; then
    echo "User cybermirage not found, checking postgres user..."
    # Try to connect with postgres user
    sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U postgres -c "ALTER USER cybermirage WITH PASSWORD 'ChangeThisToSecurePassword123!';"
    echo "Password updated for cybermirage user"
else
    echo "User cybermirage exists"
fi
