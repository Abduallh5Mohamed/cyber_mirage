#!/bin/bash
# Deploy Fixed Files to Production

SERVER="ubuntu@13.53.131.159"
KEY="~/.ssh/cyber_mirage"
DEST="/opt/cyber_mirage"

echo "==========================================="
echo "Deploying Fixed Honeypots and Dashboard"
echo "==========================================="

# Copy honeypot manager
echo "[1/4] Uploading fixed honeypot_manager.py..."
scp -i $KEY src/honeypots/honeypot_manager.py $SERVER:/home/ubuntu/

# Copy dashboard
echo "[2/4] Uploading fixed live_dashboard.py..."
scp -i $KEY src/dashboard/live_dashboard.py $SERVER:/home/ubuntu/

# Move files and rebuild
echo "[3/4] Moving files to production directories..."
ssh -i $KEY $SERVER << 'ENDSSH'
sudo mv /home/ubuntu/honeypot_manager.py /opt/cyber_mirage/src/honeypots/
sudo mv /home/ubuntu/live_dashboard.py /opt/cyber_mirage/src/dashboard/
cd /opt/cyber_mirage
echo "[4/4] Rebuilding containers..."
sudo docker compose -f docker-compose.production.yml build honeypots dashboard
echo "Restarting services..."
sudo docker compose -f docker-compose.production.yml up -d honeypots dashboard
echo "✅ Deployment complete!"
echo ""
echo "Waiting 15 seconds for services to start..."
sleep 15
echo "Checking container status:"
sudo docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'honeypots|dashboard'
ENDSSH

echo ""
echo "==========================================="
echo "✅ Deployment Complete!"
echo "==========================================="
echo ""
echo "Now test the system:"
echo "1. Attack from Ubuntu VM:"
echo "   ssh -p 2222 admin@13.53.131.159"
echo "   curl http://13.53.131.159:8080/test"
echo ""
echo "2. Check Dashboard:"
echo "   http://13.53.131.159:8501"
echo ""
echo "3. View logs:"
echo "   ssh $SERVER 'sudo docker logs cyber_mirage_honeypots --tail 20'"
