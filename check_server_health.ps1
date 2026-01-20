# 🔍 Cyber Mirage - System Status Check Script
# Use this after SSH access is restored

# Colors
$GREEN = "Green"
$RED = "Red"
$YELLOW = "Yellow"
$CYAN = "Cyan"

Write-Host "`n╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Cyber Mirage - Remote System Health Check  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$server = "13.48.194.249"
$key = "C:\Users\abdua\Downloads\cyber-mirage-key.pem"

# Test if SSH is accessible now
Write-Host "[1/6] Testing SSH Connection..." -ForegroundColor Yellow
try {
    $sshTest = ssh -i $key -o ConnectTimeout=10 -o BatchMode=yes ubuntu@$server "echo 'OK'" 2>&1
    if ($sshTest -match "OK") {
        Write-Host "✓ SSH Connection: Success" -ForegroundColor $GREEN
        $canSSH = $true
    } else {
        Write-Host "✗ SSH Connection: Failed - Fix Security Group first" -ForegroundColor $RED
        Write-Host "  Run: a:\cyber_mirage\fix_security_group.ps1" -ForegroundColor $YELLOW
        $canSSH = $false
    }
} catch {
    Write-Host "✗ SSH Connection: Failed" -ForegroundColor $RED
    $canSSH = $false
}

if (-not $canSSH) {
    Write-Host "`n⚠ Cannot proceed without SSH access. Please fix Security Group first.`n" -ForegroundColor $YELLOW
    exit 1
}

# Check Docker containers
Write-Host "`n[2/6] Checking Docker Containers..." -ForegroundColor Yellow
$containers = ssh -i $key ubuntu@$server "docker ps --format 'table {{.Names}}\t{{.Status}}' 2>&1"
Write-Host $containers

# Check running services
Write-Host "`n[3/6] Checking Service Ports..." -ForegroundColor Yellow
$ports = @(8501, 8000, 8001, 8002, 8003, 5000, 9090, 3000, 5601, 9200, 6379, 5432)
foreach ($port in $ports) {
    $result = ssh -i $key ubuntu@$server "timeout 2 bash -c '</dev/tcp/localhost/$port' 2>&1 && echo 'OPEN' || echo 'CLOSED'"
    $status = if ($result -match "OPEN") { "✓" ; $color = $GREEN } else { "✗" ; $color = $RED }
    $serviceName = switch ($port) {
        8501 { "Dashboard (Streamlit)" }
        8000 { "API Server" }
        8001 { "AI Engine - Neural" }
        8002 { "AI Engine - Swarm" }
        8003 { "AI Engine - OSINT" }
        5000 { "Flask App" }
        9090 { "Prometheus" }
        3000 { "Grafana" }
        5601 { "Kibana" }
        9200 { "Elasticsearch" }
        6379 { "Redis" }
        5432 { "PostgreSQL" }
    }
    Write-Host "  $status Port $port`: $serviceName" -ForegroundColor $color
}

# Check disk space
Write-Host "`n[4/6] Checking Disk Space..." -ForegroundColor Yellow
$diskSpace = ssh -i $key ubuntu@$server "df -h / | tail -1 | awk '{print \`$5}'"
Write-Host "  Disk Usage: $diskSpace"

# Check memory
Write-Host "`n[5/6] Checking Memory..." -ForegroundColor Yellow
$memory = ssh -i $key ubuntu@$server "free -h | grep Mem | awk '{print \`$3 \`"/\`" \`$2}'"
Write-Host "  Memory Usage: $memory"

# Check recent logs
Write-Host "`n[6/6] Checking Recent Logs..." -ForegroundColor Yellow
$logs = ssh -i $key ubuntu@$server "docker logs cyber_mirage_dashboard --tail 10 2>&1"
Write-Host $logs

# Summary
Write-Host "`n╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              System Check Complete            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Dashboard URL: http://$server`:8501/" -ForegroundColor $GREEN
Write-Host "SSH Command: ssh -i `"$key`" ubuntu@$server" -ForegroundColor $CYAN
