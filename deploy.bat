@echo off
REM Deploy and Rebuild Containers

echo ==========================================
echo Building Honeypots Container...
echo ==========================================
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 "cd /opt/cyber_mirage && sudo docker compose -f docker-compose.production.yml build honeypots"

echo.
echo ==========================================
echo Building Dashboard Container...
echo ==========================================
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 "cd /opt/cyber_mirage && sudo docker compose -f docker-compose.production.yml build dashboard"

echo.
echo ==========================================
echo Restarting Services...
echo ==========================================
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 "cd /opt/cyber_mirage && sudo docker compose -f docker-compose.production.yml up -d honeypots dashboard"

echo.
echo ==========================================
echo Waiting for services to start...
echo ==========================================
timeout /t 15

echo.
echo ==========================================
echo Checking Container Status...
echo ==========================================
ssh -i C:\Users\abdua\.ssh\cyber_mirage ubuntu@13.53.131.159 "sudo docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'honeypots|dashboard'"

echo.
echo ==========================================
echo Deployment Complete!
echo ==========================================
echo.
echo Test now:
echo 1. From Ubuntu VM: ssh -p 2222 admin@13.53.131.159
echo 2. Open Dashboard: http://13.53.131.159:8501
echo 3. Check logs: ssh ubuntu@13.53.131.159 "sudo docker logs cyber_mirage_honeypots --tail 20"
