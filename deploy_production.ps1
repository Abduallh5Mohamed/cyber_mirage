# 🚀 Production Deployment Script for Cyber Mirage v5.0
# PowerShell script to deploy complete Docker stack

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "rebuild", "status", "logs", "clean")]
    [string]$Action = "start",
    
    [Parameter(Mandatory=$false)]
    [string]$Service = "all"
)

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🐳 CYBER MIRAGE v5.0 - Production Deployment" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ──────────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────────

function Show-Status {
    Write-Host "📊 Container Status:" -ForegroundColor Yellow
    docker-compose -f docker-compose.production.yml ps
    Write-Host ""
}

function Show-Logs {
    param([string]$ServiceName)
    
    if ($ServiceName -eq "all") {
        Write-Host "📜 Showing logs for all services..." -ForegroundColor Yellow
        docker-compose -f docker-compose.production.yml logs --tail=50 -f
    } else {
        Write-Host "📜 Showing logs for $ServiceName..." -ForegroundColor Yellow
        docker-compose -f docker-compose.production.yml logs --tail=50 -f $ServiceName
    }
}

function Start-Stack {
    Write-Host "🚀 Starting Cyber Mirage production stack..." -ForegroundColor Green
    
    # Check if .env file exists
    if (-not (Test-Path ".env")) {
        Write-Host "⚠️  Creating .env file from .env.example..." -ForegroundColor Yellow
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Host "✅ .env file created. Please update with your actual credentials!" -ForegroundColor Yellow
            Write-Host ""
        }
    }
    
    # Pull latest images
    Write-Host "📥 Pulling latest images..." -ForegroundColor Cyan
    docker-compose -f docker-compose.production.yml pull
    
    # Start services
    Write-Host "🔧 Starting services..." -ForegroundColor Cyan
    docker-compose -f docker-compose.production.yml up -d
    
    Write-Host ""
    Write-Host "✅ Stack started successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Show status
    Show-Status
    
    # Show access URLs
    Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
    Write-Host "   • Dashboard:    http://localhost:8501" -ForegroundColor White
    Write-Host "   • Grafana:      http://localhost:3000 (admin/admin123)" -ForegroundColor White
    Write-Host "   • Prometheus:   http://localhost:9090" -ForegroundColor White
    Write-Host "   • Alertmanager: http://localhost:9093" -ForegroundColor White
    Write-Host ""
}

function Stop-Stack {
    Write-Host "🛑 Stopping Cyber Mirage stack..." -ForegroundColor Yellow
    docker-compose -f docker-compose.production.yml down
    Write-Host "✅ Stack stopped!" -ForegroundColor Green
    Write-Host ""
}

function Restart-Stack {
    Write-Host "🔄 Restarting Cyber Mirage stack..." -ForegroundColor Yellow
    docker-compose -f docker-compose.production.yml restart
    Write-Host "✅ Stack restarted!" -ForegroundColor Green
    Show-Status
}

function Rebuild-Stack {
    Write-Host "🏗️  Rebuilding containers..." -ForegroundColor Yellow
    
    Write-Host "1️⃣ Stopping existing containers..." -ForegroundColor Cyan
    docker-compose -f docker-compose.production.yml down
    
    Write-Host "2️⃣ Removing old images..." -ForegroundColor Cyan
    docker-compose -f docker-compose.production.yml rm -f
    
    Write-Host "3️⃣ Building new images..." -ForegroundColor Cyan
    docker-compose -f docker-compose.production.yml build --no-cache
    
    Write-Host "4️⃣ Starting services..." -ForegroundColor Cyan
    docker-compose -f docker-compose.production.yml up -d
    
    Write-Host ""
    Write-Host "✅ Rebuild complete!" -ForegroundColor Green
    Show-Status
}

function Clean-Stack {
    Write-Host "🧹 Cleaning up Docker resources..." -ForegroundColor Yellow
    
    $confirm = Read-Host "⚠️  This will remove all containers, volumes, and images. Continue? (y/N)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Host "Stopping and removing containers..." -ForegroundColor Cyan
        docker-compose -f docker-compose.production.yml down -v
        
        Write-Host "Removing images..." -ForegroundColor Cyan
        docker images "cyber-mirage/*" -q | ForEach-Object { docker rmi $_ -f }
        
        Write-Host "Pruning system..." -ForegroundColor Cyan
        docker system prune -a -f
        
        Write-Host "✅ Cleanup complete!" -ForegroundColor Green
    } else {
        Write-Host "❌ Cleanup cancelled." -ForegroundColor Yellow
    }
    Write-Host ""
}

# ──────────────────────────────────────────────────────────
# Pre-flight Checks
# ──────────────────────────────────────────────────────────

function Test-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Cyan
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker not found! Please install Docker Desktop." -ForegroundColor Red
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Host "✅ Docker Compose: $composeVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker Compose not found!" -ForegroundColor Red
        exit 1
    }
    
    # Check if Docker daemon is running
    try {
        docker ps | Out-Null
        Write-Host "✅ Docker daemon is running" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker daemon is not running! Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
}

# ──────────────────────────────────────────────────────────
# Main Execution
# ──────────────────────────────────────────────────────────

# Run pre-flight checks
Test-Prerequisites

# Execute action
switch ($Action.ToLower()) {
    "start" {
        Start-Stack
    }
    "stop" {
        Stop-Stack
    }
    "restart" {
        Restart-Stack
    }
    "rebuild" {
        Rebuild-Stack
    }
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs -ServiceName $Service
    }
    "clean" {
        Clean-Stack
    }
    default {
        Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
        Write-Host ""
        Write-Host "Usage: .\deploy_production.ps1 [-Action <action>] [-Service <service>]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Actions:" -ForegroundColor Cyan
        Write-Host "  start    - Start the production stack" -ForegroundColor White
        Write-Host "  stop     - Stop the production stack" -ForegroundColor White
        Write-Host "  restart  - Restart the production stack" -ForegroundColor White
        Write-Host "  rebuild  - Rebuild and restart all containers" -ForegroundColor White
        Write-Host "  status   - Show container status" -ForegroundColor White
        Write-Host "  logs     - Show logs (use -Service to filter)" -ForegroundColor White
        Write-Host "  clean    - Clean up all resources (WARNING: destructive)" -ForegroundColor White
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Cyan
        Write-Host "  .\deploy_production.ps1 -Action start" -ForegroundColor White
        Write-Host "  .\deploy_production.ps1 -Action logs -Service ai-engine" -ForegroundColor White
        Write-Host "  .\deploy_production.ps1 -Action rebuild" -ForegroundColor White
        Write-Host ""
    }
}
