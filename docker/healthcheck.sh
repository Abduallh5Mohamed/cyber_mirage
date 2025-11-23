#!/bin/bash
# 🏥 Health Check Script for Cyber Mirage Containers
# Used by Docker HEALTHCHECK directive

set -e

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local timeout=${2:-5}
    
    if command -v curl &> /dev/null; then
        curl -f -s -m "$timeout" "$url" > /dev/null
        return $?
    elif command -v wget &> /dev/null; then
        wget -q -T "$timeout" -O /dev/null "$url"
        return $?
    else
        echo "ERROR: Neither curl nor wget found"
        return 1
    fi
}

# Function to check TCP port
check_port() {
    local host=$1
    local port=$2
    local timeout=${3:-3}
    
    if command -v nc &> /dev/null; then
        nc -z -w "$timeout" "$host" "$port"
        return $?
    elif command -v telnet &> /dev/null; then
        timeout "$timeout" telnet "$host" "$port" 2>&1 | grep -q "Connected"
        return $?
    else
        # Fallback to Python
        python3 -c "
import socket
import sys
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout($timeout)
    result = sock.connect_ex(('$host', $port))
    sock.close()
    sys.exit(0 if result == 0 else 1)
except:
    sys.exit(1)
"
        return $?
    fi
}

# Main health check logic
SERVICE_TYPE=${SERVICE_TYPE:-unknown}

case "$SERVICE_TYPE" in
    "ai-engine")
        check_http "http://localhost:8001/health" 10
        ;;
    
    "dashboard")
        check_http "http://localhost:8501/_stcore/health" 5
        ;;
    
    "honeypots")
        check_http "http://localhost:8080/health" 5
        ;;
    
    "redis")
        check_port "localhost" 6379 3
        ;;
    
    "postgres")
        check_port "localhost" 5432 3
        ;;
    
    *)
        echo "ERROR: Unknown service type: $SERVICE_TYPE"
        exit 1
        ;;
esac

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ Health check passed for $SERVICE_TYPE"
else
    echo "❌ Health check failed for $SERVICE_TYPE"
fi

exit $exit_code
