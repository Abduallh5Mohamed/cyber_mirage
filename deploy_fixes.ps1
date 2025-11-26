# Deploy Fixed Files to Production (PowerShell)

$SERVER = "ubuntu@13.53.131.159"
$KEY = "C:\Users\abdua\.ssh\cyber_mirage"
$DEST = "/opt/cyber_mirage"

Write-Host "`n===========================================" -ForegroundColor Cyan
Write-Host "Deploying Fixed Honeypots and Dashboard" -ForegroundColor Cyan
Write-Host "===========================================`n" -ForegroundColor Cyan

# Copy honeypot manager
Write-Host "[1/4] Uploading fixed honeypot_manager.py..." -ForegroundColor Yellow
scp -i $KEY a:\cyber_mirage\src\honeypots\honeypot_manager.py ${SERVER}:/home/ubuntu/

# Copy dashboard
Write-Host "[2/4] Uploading fixed live_dashboard.py..." -ForegroundColor Yellow
scp -i $KEY a:\cyber_mirage\src\dashboard\live_dashboard.py ${SERVER}:/home/ubuntu/

# Move files and rebuild
Write-Host "[3/4] Moving files to production directories..." -ForegroundColor Yellow
ssh -i $KEY $SERVER @"
sudo mv /home/ubuntu/honeypot_manager.py /opt/cyber_mirage/src/honeypots/
sudo mv /home/ubuntu/live_dashboard.py /opt/cyber_mirage/src/dashboard/
cd /opt/cyber_mirage
echo '[4/4] Rebuilding containers...'
sudo docker compose -f docker-compose.production.yml build honeypots dashboard
echo 'Restarting services...'
sudo docker compose -f docker-compose.production.yml up -d honeypots dashboard
echo '✅ Deployment complete!'
echo ''
echo 'Waiting 15 seconds for services to start...'
sleep 15
echo 'Checking container status:'
sudo docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'honeypots|dashboard'
"@

Write-Host "`n===========================================" -ForegroundColor Green
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "===========================================`n" -ForegroundColor Green

Write-Host "Now test the system:" -ForegroundColor Yellow
Write-Host "1. Attack from Ubuntu VM:" -ForegroundColor White
Write-Host "   ssh -p 2222 admin@13.53.131.159" -ForegroundColor Gray
Write-Host "   curl http://13.53.131.159:8080/test`n" -ForegroundColor Gray

Write-Host "2. Check Dashboard:" -ForegroundColor White
Write-Host "   http://13.53.131.159:8501`n" -ForegroundColor Gray

Write-Host "3. View logs:" -ForegroundColor White
Write-Host "   ssh -i $KEY $SERVER 'sudo docker logs cyber_mirage_honeypots --tail 20'" -ForegroundColor Gray
