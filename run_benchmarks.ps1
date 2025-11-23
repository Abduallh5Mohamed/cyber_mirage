# Cyber Mirage Benchmarking Suite Runner
# Runs all performance tests

Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("="*69) -ForegroundColor Cyan
Write-Host " 📊 CYBER MIRAGE - BENCHMARK SUITE" -ForegroundColor Yellow
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("="*69) -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not activated" -ForegroundColor Yellow
    Write-Host "Activating venv..." -ForegroundColor Cyan
    & ".\venv\Scripts\Activate.ps1"
    if (-not $?) {
        Write-Host "❌ Failed to activate venv" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Green
Write-Host ""

# Check dependencies
Write-Host "🔍 Checking dependencies..." -ForegroundColor Cyan

$required_packages = @("numpy", "psutil", "aiohttp")
$missing_packages = @()

foreach ($package in $required_packages) {
    $check = & python -c "import $package" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missing_packages += $package
    }
}

if ($missing_packages.Count -gt 0) {
    Write-Host "⚠️  Missing packages: $($missing_packages -join ', ')" -ForegroundColor Yellow
    Write-Host "Installing missing packages..." -ForegroundColor Cyan
    
    foreach ($package in $missing_packages) {
        Write-Host "  Installing $package..." -ForegroundColor Gray
        & pip install $package --quiet
        if (-not $?) {
            Write-Host "  ❌ Failed to install $package" -ForegroundColor Red
        } else {
            Write-Host "  ✅ Installed $package" -ForegroundColor Green
        }
    }
}

Write-Host "✅ All dependencies available" -ForegroundColor Green
Write-Host ""

# Menu
Write-Host "📋 Available Benchmark Tests:" -ForegroundColor Yellow
Write-Host "  1. AI Performance Benchmark (2-3 minutes)" -ForegroundColor White
Write-Host "     - Tests: Neural, Swarm, Quantum, Bio-Inspired" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Resource Usage Monitor (Custom duration)" -ForegroundColor White
Write-Host "     - Monitors: CPU, Memory, Network, Disk" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Load Testing (Requires server running)" -ForegroundColor White
Write-Host "     - Tests: 100 to 10,000 concurrent attacks" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Complete Suite (All benchmarks)" -ForegroundColor White
Write-Host "     - Runs all tests and generates report" -ForegroundColor Gray
Write-Host ""
Write-Host "  5. Quick Test (AI Performance only - 1 minute)" -ForegroundColor White
Write-Host "     - Fast performance check" -ForegroundColor Gray
Write-Host ""
Write-Host "  0. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "👉 Select option (0-5)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🧠 Running AI Performance Benchmark..." -ForegroundColor Cyan
        Write-Host ""
        & python benchmarks/ai_performance.py
    }
    
    "2" {
        Write-Host ""
        Write-Host "💻 Running Resource Usage Monitor..." -ForegroundColor Cyan
        Write-Host ""
        & python benchmarks/resource_usage.py
    }
    
    "3" {
        Write-Host ""
        Write-Host "⚠️  Make sure Cyber Mirage is running!" -ForegroundColor Yellow
        Write-Host "   Run in another terminal: .\start_defense.ps1" -ForegroundColor Gray
        Write-Host ""
        $confirm = Read-Host "Is the server running? (yes/no)"
        
        if ($confirm -eq "yes" -or $confirm -eq "y") {
            Write-Host ""
            Write-Host "🔥 Running Load Testing..." -ForegroundColor Cyan
            Write-Host ""
            & python benchmarks/load_testing.py
        } else {
            Write-Host "❌ Cancelled - Start server first" -ForegroundColor Red
        }
    }
    
    "4" {
        Write-Host ""
        Write-Host "🎯 Running Complete Benchmark Suite..." -ForegroundColor Cyan
        Write-Host "⏱️  This will take 2-5 minutes" -ForegroundColor Yellow
        Write-Host ""
        & python benchmarks/run_all_benchmarks.py
    }
    
    "5" {
        Write-Host ""
        Write-Host "⚡ Running Quick AI Performance Test..." -ForegroundColor Cyan
        Write-Host ""
        & python -c @"
from benchmarks.ai_performance import AIPerformanceBenchmark
bench = AIPerformanceBenchmark()
bench.benchmark_neural_deception(iterations=100)
print('\n✅ Quick test complete!')
"@
    }
    
    "0" {
        Write-Host ""
        Write-Host "👋 Goodbye!" -ForegroundColor Cyan
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("="*69) -ForegroundColor Cyan
Write-Host " ✅ BENCHMARK COMPLETE" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("="*69) -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Results saved to: data/benchmarks/" -ForegroundColor Cyan
Write-Host ""
