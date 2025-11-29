#!/bin/bash
cd /home/ubuntu/cyber_mirage

# Stop the dashboard to release the connection
sudo docker compose -f docker-compose.production.yml stop dashboard

# Wait a moment
sleep 3

# Reset the password using the postgres container directly
# The password in the .env file is: ChangeThisToSecurePassword123!
# But we need to set it to what PostgreSQL expects

# First, let's check what password PostgreSQL is using
echo "Checking PostgreSQL initialization..."
sudo docker compose -f docker-compose.production.yml exec -T postgres env | grep POSTGRES

# Now update the password
echo "Updating cybermirage password..."
sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U cybermirage -d cyber_mirage -c "SELECT 1;" 2>&1 || true

# If that fails, try with the default password
echo "Trying with default password..."
PGPASSWORD=SecurePass123! sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U cybermirage -d cyber_mirage -c "SELECT 1;" 2>&1 || true
