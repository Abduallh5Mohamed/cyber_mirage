#!/bin/bash
#═══════════════════════════════════════════════════════════════════════════════
# ⬆️ Cyber Mirage - Update Script
# Updates the application to the latest version
#═══════════════════════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "\n${GREEN}▶ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          ⬆️  Cyber Mirage - Update Script                        ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

cd /home/ubuntu/cyber_mirage

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Backup before update
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 1/4: Creating backup before update..."

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker exec cyber_mirage_postgres pg_dump -U cybermirage cyber_mirage > $BACKUP_DIR/pre_update_db_$DATE.sql 2>/dev/null || true
gzip $BACKUP_DIR/pre_update_db_$DATE.sql 2>/dev/null || true

# Backup .env.production
cp .env.production $BACKUP_DIR/.env.production_$DATE

echo "Backup created: $BACKUP_DIR/"

# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Pull latest code
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 2/4: Pulling latest code from GitHub..."

# Stash any local changes
git stash

# Pull latest
git pull origin main

# Restore .env.production (in case it was changed)
cp $BACKUP_DIR/.env.production_$DATE .env.production

# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Rebuild containers
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 3/4: Rebuilding containers..."

docker-compose -f docker-compose.production.yml build --no-cache

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Restart services
# ─────────────────────────────────────────────────────────────────────────────
print_step "Step 4/4: Restarting services..."

docker-compose -f docker-compose.production.yml up -d

# Wait for services to start
sleep 10

# Check status
docker ps --format "table {{.Names}}\t{{.Status}}"

# ─────────────────────────────────────────────────────────────────────────────
# Complete
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ✅ UPDATE COMPLETE!                                             ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║                                                                  ║"
echo "║  Backup location: $BACKUP_DIR/                                   ║"
echo "║                                                                  ║"
echo "║  If something went wrong, restore with:                          ║"
echo "║  docker-compose -f docker-compose.production.yml down            ║"
echo "║  git checkout <previous-commit>                                  ║"
echo "║  docker-compose -f docker-compose.production.yml up -d --build   ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
