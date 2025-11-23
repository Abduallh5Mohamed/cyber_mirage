#!/usr/bin/env python3
"""
🧪 Quick Test Script - اختبار سريع لكل المكونات
يختبر كل الـ modules في دقيقتين!

Usage:
    python test_all_quick.py
"""

import sys
import os
from datetime import datetime

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("🧪 Cyber Mirage v5.0 LEGENDARY - Quick Test Suite")
print("="*70 + "\n")

test_results = []
total_tests = 0
passed_tests = 0

def test_module(name, import_func):
    """اختبار module واحد"""
    global total_tests, passed_tests
    total_tests += 1
    
    print(f"🔍 Testing {name}...", end=" ")
    try:
        import_func()
        print("✅ PASSED")
        test_results.append(f"✅ {name}")
        passed_tests += 1
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:50]}")
        test_results.append(f"❌ {name}: {str(e)[:50]}")
        return False

print("📦 Testing Core AI Modules...")
print("-" * 70)

# Test 1: Neural Deception
test_module("Neural Deception", lambda: __import__('src.ai.neural_deception', fromlist=['NeuralDeception']))

# Test 2: Swarm Intelligence
test_module("Swarm Intelligence", lambda: __import__('src.ai.swarm_intelligence', fromlist=['SwarmDefense']))

# Test 3: Quantum Defense
test_module("Quantum Defense", lambda: __import__('src.ai.quantum_defense', fromlist=['QuantumDefense']))

# Test 4: Bio-Inspired
test_module("Bio-Inspired Defense", lambda: __import__('src.ai.bio_inspired', fromlist=['BioInspiredDefense']))

print("\n🌐 Testing Network Components...")
print("-" * 70)

# Test 5: ARP Spoofing
test_module("ARP Spoofing", lambda: __import__('src.network.arp_spoofing', fromlist=['ARPDeception']))

# Test 6: DNS Deception
test_module("DNS Deception", lambda: __import__('src.network.dns_deception', fromlist=['DNSDeception']))

# Test 7: SDN Controller
test_module("SDN Controller", lambda: __import__('src.network.sdn_controller', fromlist=['SimplifiedSDN']))

print("\n🔒 Testing Security Components...")
print("-" * 70)

# Test 8: Container Isolation
test_module("Container Isolation", lambda: __import__('src.security.container_isolation', fromlist=['ContainerIsolation']))

# Test 9: Resource Monitor
test_module("Resource Monitor", lambda: __import__('src.security.resource_monitor', fromlist=['ResourceMonitor']))

print("\n🔍 Testing Intelligence Components...")
print("-" * 70)

# Test 10: OSINT Collector
test_module("OSINT Collector", lambda: __import__('src.intelligence.osint_collector', fromlist=['MockOSINTCollector']))

# Test 11: Threat Forecasting
test_module("Threat Forecasting", lambda: __import__('src.prediction.threat_forecasting', fromlist=['ThreatForecaster']))

print("\n📜 Testing Forensics Components...")
print("-" * 70)

# Test 12: Log Collector
test_module("Log Collector", lambda: __import__('src.forensics.log_collector', fromlist=['LogCollector']))

print("\n🚀 Testing Advanced Components...")
print("-" * 70)

# Test 13: Real Quantum
test_module("Real Quantum Computer", lambda: __import__('src.ai.real_quantum', fromlist=['RealQuantumDefense']))

# Test 14: Environment
test_module("Base Environment", lambda: __import__('src.environment.base_env', fromlist=['CyberMirageEnv']))

print("\n" + "="*70)
print("📊 TEST SUMMARY")
print("="*70)

# Print all results
print("\n📋 Detailed Results:")
for result in test_results:
    print(f"  {result}")

# Summary statistics
print(f"\n🎯 Overall Results:")
print(f"   Total Tests: {total_tests}")
print(f"   Passed: {passed_tests} ✅")
print(f"   Failed: {total_tests - passed_tests} ❌")

success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
print(f"   Success Rate: {success_rate:.1f}%")

# Grade
if success_rate == 100:
    grade = "🏆 PERFECT!"
    color = "green"
elif success_rate >= 90:
    grade = "⭐ EXCELLENT!"
    color = "green"
elif success_rate >= 80:
    grade = "✅ GOOD"
    color = "blue"
elif success_rate >= 70:
    grade = "⚠️ ACCEPTABLE"
    color = "yellow"
else:
    grade = "❌ NEEDS WORK"
    color = "red"

print(f"\n🎖️ Grade: {grade}")

# Save results to file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_file = f"test_results_{timestamp}.txt"

with open(report_file, 'w', encoding='utf-8') as f:
    f.write(f"Cyber Mirage v5.0 - Quick Test Results\n")
    f.write(f"Date: {datetime.now()}\n")
    f.write(f"="*70 + "\n\n")
    f.write(f"Total Tests: {total_tests}\n")
    f.write(f"Passed: {passed_tests}\n")
    f.write(f"Failed: {total_tests - passed_tests}\n")
    f.write(f"Success Rate: {success_rate:.1f}%\n")
    f.write(f"Grade: {grade}\n\n")
    f.write(f"Detailed Results:\n")
    f.write("-"*70 + "\n")
    for result in test_results:
        f.write(f"{result}\n")

print(f"\n💾 Report saved to: {report_file}")
print("="*70 + "\n")

# Exit code
sys.exit(0 if passed_tests == total_tests else 1)
