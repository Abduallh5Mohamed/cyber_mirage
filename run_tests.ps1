# 🚀 Run All Tests - Cyber Mirage v5.0
# يشغل كل الاختبارات في أمر واحد

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🎭 Cyber Mirage v5.0 LEGENDARY - Quick Test Runner" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# تفعيل البيئة الافتراضية
Write-Host "⚡ Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  📦 Option 1: Quick Test (2 minutes)" -ForegroundColor Green
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  Tests all modules quickly"
Write-Host ""

Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  🎮 Option 2: Full Demo (3 minutes)" -ForegroundColor Green
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  Shows how everything works"
Write-Host ""

Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  📊 Option 3: Dashboard (Interactive)" -ForegroundColor Green
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  Opens full web dashboard"
Write-Host ""

Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  🧪 Option 4: Individual Tests" -ForegroundColor Green
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  Test specific components"
Write-Host ""

$choice = Read-Host "Choose option (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🧪 Running Quick Test..." -ForegroundColor Cyan
        Write-Host ""
        .\venv\Scripts\python.exe test_all_quick.py
    }
    "2" {
        Write-Host ""
        Write-Host "🎮 Running Full Demo..." -ForegroundColor Cyan
        Write-Host ""
        .\venv\Scripts\python.exe demo_full.py
    }
    "3" {
        Write-Host ""
        Write-Host "📊 Starting Dashboard..." -ForegroundColor Cyan
        Write-Host "   Opening http://localhost:8501 in browser..." -ForegroundColor Yellow
        Write-Host ""
        .\venv\Scripts\streamlit.exe run src/dashboard/streamlit_app.py
    }
    "4" {
        Write-Host ""
        Write-Host "🧪 Individual Component Tests" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Test AI Modules (Neural, Swarm, Quantum, Bio)"
        Write-Host "2. Test NEW Components (OSINT, SDN, Quantum)"
        Write-Host "3. Test Network Tools (ARP, DNS)"
        Write-Host "4. Test Security (Container, Monitor)"
        Write-Host "5. Test Forensics (Logs)"
        Write-Host "6. Test ALL"
        Write-Host ""
        $subChoice = Read-Host "Choose test (1-6)"
        
        Write-Host ""
        switch ($subChoice) {
            "1" {
                Write-Host "🤖 Testing AI Modules..." -ForegroundColor Yellow
                .\venv\Scripts\python.exe -c "from src.ai.neural_deception import NeuralDeception; print('✅ Neural OK')"
                .\venv\Scripts\python.exe -c "from src.ai.swarm_intelligence import SwarmDefense; print('✅ Swarm OK')"
                .\venv\Scripts\python.exe -c "from src.ai.quantum_defense import QuantumDefense; print('✅ Quantum OK')"
                .\venv\Scripts\python.exe -c "from src.ai.bio_inspired import BioInspiredDefense; print('✅ Bio OK')"
            }
            "2" {
                Write-Host "🆕 Testing NEW Components..." -ForegroundColor Yellow
                .\venv\Scripts\python.exe src/intelligence/osint_collector.py
                .\venv\Scripts\python.exe src/network/sdn_controller.py
                .\venv\Scripts\python.exe src/ai/real_quantum.py
            }
            "3" {
                Write-Host "🌐 Testing Network Tools..." -ForegroundColor Yellow
                .\venv\Scripts\python.exe -c "from src.network.arp_spoofing import ARPDeception; print('✅ ARP OK')"
                .\venv\Scripts\python.exe -c "from src.network.dns_deception import DNSDeception; print('✅ DNS OK')"
            }
            "4" {
                Write-Host "🔒 Testing Security..." -ForegroundColor Yellow
                .\venv\Scripts\python.exe -c "from src.security.container_isolation import ContainerIsolation; print('✅ Container OK')"
                .\venv\Scripts\python.exe -c "from src.security.resource_monitor import ResourceMonitor; print('✅ Monitor OK')"
            }
            "5" {
                Write-Host "📜 Testing Forensics..." -ForegroundColor Yellow
                .\venv\Scripts\python.exe -c "from src.forensics.log_collector import LogCollector; print('✅ Logs OK')"
            }
            "6" {
                Write-Host "🧪 Testing ALL Components..." -ForegroundColor Yellow
                .\venv\Scripts\python.exe test_all_quick.py
            }
        }
    }
    default {
        Write-Host ""
        Write-Host "❌ Invalid choice. Running Quick Test by default..." -ForegroundColor Red
        Write-Host ""
        .\venv\Scripts\python.exe test_all_quick.py
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Test Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 What's next?" -ForegroundColor Yellow
Write-Host "   • View test results above"
Write-Host "   • Run dashboard: streamlit run src/dashboard/streamlit_app.py"
Write-Host "   • Read docs: QUICK_TEST.md"
Write-Host ""
