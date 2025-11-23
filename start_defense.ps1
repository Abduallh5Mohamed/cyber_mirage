# 🎯 Start Cyber Mirage Defense
# Run this script to start all components

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🎭 Starting Cyber Mirage Defense System" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "⚡ Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Start Dashboard in background
Write-Host "📊 Starting Dashboard..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\python.exe -m streamlit run src/dashboard/streamlit_app.py"
Start-Sleep -Seconds 3

# Start Environment
Write-Host "🌐 Starting Honeypot Environment..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\python.exe src/environment/base_env.py"
Start-Sleep -Seconds 2

# Start Monitoring
Write-Host "📡 Starting Log Monitoring..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Get-Content data\logs\*.log -Wait -Tail 20"

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ All Systems Started!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Dashboard: http://localhost:8501" -ForegroundColor Cyan
Write-Host "📊 Your IP: 192.168.1.3" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Ready for attack testing!" -ForegroundColor Yellow
Write-Host ""
