#!/bin/bash
#═══════════════════════════════════════════════════════════════════════════════
# 🔍 Cyber Mirage - Health Check Script
# Checks all services and reports status
#═══════════════════════════════════════════════════════════════════════════════

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

OK="${GREEN}✓${NC}"
FAIL="${RED}✗${NC}"
WARN="${YELLOW}⚠${NC}"

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          🔍 Cyber Mirage - Health Check                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Docker Service Status
# ─────────────────────────────────────────────────────────────────────────────
echo "📦 Docker Containers:"
echo "─────────────────────────────────────────────────────────────────────"

check_container() {
    local name=$1
    local status=$(docker inspect -f '{{.State.Status}}' $name 2>/dev/null)
    local health=$(docker inspect -f '{{.State.Health.Status}}' $name 2>/dev/null)
    
    if [ "$status" == "running" ]; then
        if [ "$health" == "healthy" ] || [ "$health" == "" ]; then
            echo -e "  $OK $name: ${GREEN}Running${NC}"
        elif [ "$health" == "unhealthy" ]; then
            echo -e "  $FAIL $name: ${RED}Unhealthy${NC}"
        else
            echo -e "  $WARN $name: ${YELLOW}$health${NC}"
        fi
    else
        echo -e "  $FAIL $name: ${RED}Not Running${NC}"
    fi
}

check_container cyber_mirage_dashboard
check_container cyber_mirage_honeypots
check_container cyber_mirage_ai
check_container cyber_mirage_postgres
check_container cyber_mirage_redis
check_container cyber_mirage_prometheus
check_container cyber_mirage_grafana
check_container cyber_mirage_alertmanager

# ─────────────────────────────────────────────────────────────────────────────
# Port Connectivity
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "🔌 Port Connectivity:"
echo "─────────────────────────────────────────────────────────────────────"

check_port() {
    local port=$1
    local name=$2
    if nc -z localhost $port 2>/dev/null; then
        echo -e "  $OK Port $port ($name): ${GREEN}Open${NC}"
    else
        echo -e "  $FAIL Port $port ($name): ${RED}Closed${NC}"
    fi
}

check_port 8501 "Dashboard"
check_port 3000 "Grafana"
check_port 9090 "Prometheus"
check_port 2222 "SSH Honeypot"
check_port 2121 "FTP Honeypot"
check_port 8080 "HTTP Honeypot"

# ─────────────────────────────────────────────────────────────────────────────
# Database Status
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "🗄️  Database Status:"
echo "─────────────────────────────────────────────────────────────────────"

# PostgreSQL
PG_READY=$(docker exec cyber_mirage_postgres pg_isready -U cybermirage -d cyber_mirage 2>/dev/null)
if echo "$PG_READY" | grep -q "accepting"; then
    echo -e "  $OK PostgreSQL: ${GREEN}Ready${NC}"
    
    # Get attack count
    ATTACK_COUNT=$(docker exec cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -t -c "SELECT COUNT(*) FROM attack_sessions;" 2>/dev/null | tr -d ' ')
    echo -e "  📊 Total attacks logged: $ATTACK_COUNT"
else
    echo -e "  $FAIL PostgreSQL: ${RED}Not Ready${NC}"
fi

# Redis
REDIS_PING=$(docker exec cyber_mirage_redis redis-cli ping 2>/dev/null)
if [ "$REDIS_PING" == "PONG" ]; then
    echo -e "  $OK Redis: ${GREEN}Ready${NC}"
else
    echo -e "  $FAIL Redis: ${RED}Not Ready${NC}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# System Resources
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "💻 System Resources:"
echo "─────────────────────────────────────────────────────────────────────"

# CPU
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
echo "  CPU Usage: $CPU_USAGE%"

# Memory
MEM_INFO=$(free -h | grep Mem)
MEM_USED=$(echo $MEM_INFO | awk '{print $3}')
MEM_TOTAL=$(echo $MEM_INFO | awk '{print $2}')
echo "  Memory: $MEM_USED / $MEM_TOTAL"

# Disk
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')
DISK_AVAIL=$(df -h / | awk 'NR==2 {print $4}')
echo "  Disk Usage: $DISK_USAGE (Available: $DISK_AVAIL)"

# ─────────────────────────────────────────────────────────────────────────────
# Recent Activity
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "📈 Recent Activity (last 24h):"
echo "─────────────────────────────────────────────────────────────────────"

RECENT_ATTACKS=$(docker exec cyber_mirage_postgres psql -U cybermirage -d cyber_mirage -t -c "SELECT COUNT(*) FROM attack_sessions WHERE created_at > NOW() - INTERVAL '24 hours';" 2>/dev/null | tr -d ' ')
echo "  Attacks in last 24h: ${RECENT_ATTACKS:-0}"

echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo "Health check completed at $(date)"
