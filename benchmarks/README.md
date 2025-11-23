# 📊 Cyber Mirage Benchmarking Suite

Complete performance testing and analysis tools for Cyber Mirage v5.0.

---

## 📋 Available Benchmarks

### 1. **AI Performance Benchmark** 🧠
**File:** `ai_performance.py`

Tests the speed and efficiency of all AI components:
- Neural Deception Engine
- Swarm Intelligence (2,100 agents)
- Quantum Defense
- Bio-Inspired Security

**Usage:**
```powershell
python benchmarks/ai_performance.py
```

**Metrics:**
- Decision time (ms)
- Throughput (decisions/sec)
- Statistical analysis (mean, median, p95, p99)

---

### 2. **Load Testing** 🔥
**File:** `load_testing.py`

Stress test with high-volume concurrent attacks:
- Light Load: 100 attacks
- Medium Load: 1,000 attacks
- Heavy Load: 5,000 attacks
- Extreme Load: 10,000 attacks

**Prerequisites:**
```powershell
# Start Cyber Mirage first
.\start_defense.ps1
```

**Usage:**
```powershell
python benchmarks/load_testing.py
```

**Metrics:**
- Throughput (attacks/sec)
- Success rate
- Response times
- Error analysis

---

### 3. **Resource Usage Monitor** 💻
**File:** `resource_usage.py`

Monitors system resources during operation:
- CPU usage
- Memory usage
- Network throughput
- Disk I/O

**Usage:**
```powershell
python benchmarks/resource_usage.py
```

**Metrics:**
- CPU: mean, max, min
- Memory: usage in MB and %
- Network: throughput in Mbps

---

### 4. **Complete Suite** 🎯
**File:** `run_all_benchmarks.py`

Runs all benchmarks and generates comprehensive report.

**Usage:**
```powershell
python benchmarks/run_all_benchmarks.py
```

**Output:**
- Complete JSON results
- Summary report
- Performance rating
- Optimization recommendations

---

## 🚀 Quick Start

### Run All Benchmarks:
```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Run complete suite
python benchmarks/run_all_benchmarks.py
```

### Run Individual Tests:
```powershell
# AI Performance only
python benchmarks/ai_performance.py

# Resource monitoring only
python benchmarks/resource_usage.py

# Load testing only (requires server running)
.\start_defense.ps1
python benchmarks/load_testing.py
```

---

## 📊 Results

All benchmark results are saved to: `data/benchmarks/`

### Files Created:
- `ai_benchmark_YYYYMMDD_HHMMSS.json` - AI performance results
- `load_test_YYYYMMDD_HHMMSS.json` - Load test results
- `resource_usage_YYYYMMDD_HHMMSS.json` - Resource monitoring results
- `complete_benchmark_YYYYMMDD_HHMMSS.json` - Complete suite results
- `summary_YYYYMMDD_HHMMSS.txt` - Human-readable summary

---

## 🎯 Performance Targets

### AI Components:
| Component | Target | Excellent | Good | Fair |
|-----------|--------|-----------|------|------|
| Neural Deception | >1000/s | >1000/s | >500/s | >200/s |
| Swarm Intelligence | >50/s | >100/s | >50/s | >20/s |
| Quantum Defense | >200/s | >500/s | >200/s | >100/s |

### Load Testing:
| Metric | Target | Excellent | Good | Fair |
|--------|--------|-----------|------|------|
| Throughput | >500/s | >1000/s | >500/s | >200/s |
| Success Rate | >95% | >99% | >95% | >90% |
| Response Time | <100ms | <50ms | <100ms | <200ms |

### Resource Usage:
| Resource | Target | Excellent | Good | Fair |
|----------|--------|-----------|------|------|
| CPU | <80% | <50% | <80% | <90% |
| Memory | <4GB | <2GB | <4GB | <6GB |

---

## 🔧 Dependencies

```bash
# Required
pip install psutil      # Resource monitoring
pip install aiohttp     # Async HTTP for load testing
pip install numpy       # Statistical analysis

# All dependencies
pip install -r requirements.txt
```

---

## 📈 Interpreting Results

### AI Performance:
```
Mean Time < 1ms     → ⭐⭐⭐⭐⭐ Excellent
Mean Time < 5ms     → ⭐⭐⭐⭐ Very Good
Mean Time < 10ms    → ⭐⭐⭐ Good
Mean Time > 10ms    → Needs optimization
```

### Load Testing:
```
Success Rate > 99%  → ⭐⭐⭐⭐⭐ Excellent
Success Rate > 95%  → ⭐⭐⭐⭐ Very Good
Success Rate > 90%  → ⭐⭐⭐ Good
Success Rate < 90%  → Needs improvement
```

### Resource Usage:
```
CPU < 50%           → ⭐⭐⭐⭐⭐ Excellent
CPU < 80%           → ⭐⭐⭐⭐ Very Good
CPU > 80%           → Consider optimization
```

---

## 🐛 Troubleshooting

### Issue: ImportError
```powershell
# Install missing dependencies
pip install -r requirements.txt
```

### Issue: Load test connection errors
```powershell
# Make sure server is running
.\start_defense.ps1

# Check if port 8080 is accessible
curl http://localhost:8080
```

### Issue: High resource usage during tests
```
This is expected! Benchmarks are designed to stress test the system.
Close other applications for more accurate baseline results.
```

---

## 📝 Example Output

### AI Performance:
```
🧠 NEURAL DECEPTION ENGINE BENCHMARK
====================================
Test 1: Strategy Selection Speed
  ✅ Iterations: 1000
  📈 Mean Time: 0.523 ms
  🚀 Throughput: 1912 decisions/sec
  🎯 95th percentile: 0.781 ms
```

### Load Testing:
```
🔥 LOAD TEST RESULTS
====================
📈 Overall Statistics:
  ✅ Total Attacks: 10,000
  ✅ Successful: 9,847 (98.5%)
  🚀 Throughput: 1,234 attacks/sec

⚡ Response Times:
  📊 Mean: 45.2 ms
  🎯 95th percentile: 89.3 ms

🏆 Rating: ⭐⭐⭐⭐⭐ EXCELLENT
```

---

## 🎓 Best Practices

1. **Run benchmarks after code changes** to verify performance
2. **Close unnecessary applications** for accurate baseline
3. **Run multiple times** and average results
4. **Monitor trends over time** to detect regressions
5. **Compare before/after** optimization changes

---

## 📞 Support

- 📖 Full documentation: `../README.md`
- 🐛 Report issues: Create GitHub issue
- 💡 Optimization tips: `../PROJECT_ANALYSIS.md`

---

## ✅ Checklist

Before running benchmarks:
- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Cyber Mirage tested (`python test_all_quick.py`)
- [ ] For load tests: Server running (`.\start_defense.ps1`)
- [ ] Other applications closed (for accurate baseline)

---

**Last Updated:** October 27, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
