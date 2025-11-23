"""
AI Performance Benchmarking
Tests the speed and accuracy of all AI components
"""

import time
import numpy as np
import json
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.ai.neural_deception import NeuralDeception
    from src.ai.swarm_intelligence import SwarmIntelligence
    from src.ai.quantum_defense import QuantumDefense
    from src.ai.bio_inspired import BioInspiredSecurity
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Some AI modules not available: {e}")
    MODULES_AVAILABLE = False


class AIPerformanceBenchmark:
    """Benchmark AI component performance"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
    
    def benchmark_neural_deception(self, iterations=1000):
        """Benchmark Neural Deception Engine"""
        print("\n" + "="*70)
        print("🧠 NEURAL DECEPTION ENGINE BENCHMARK")
        print("="*70)
        
        if not MODULES_AVAILABLE:
            print("❌ Modules not available")
            return None
        
        try:
            deception = NeuralDeception()
            
            # Test 1: Strategy Selection Speed
            print("\n📊 Test 1: Strategy Selection Speed")
            times = []
            for i in range(iterations):
                threat_level = np.random.random()
                start = time.perf_counter()
                strategy = deception.select_strategy(threat_level)
                elapsed = time.perf_counter() - start
                times.append(elapsed * 1000)  # Convert to ms
            
            results = {
                'mean': np.mean(times),
                'median': np.median(times),
                'min': np.min(times),
                'max': np.max(times),
                'std': np.std(times),
                'p95': np.percentile(times, 95),
                'p99': np.percentile(times, 99)
            }
            
            print(f"  ✅ Iterations: {iterations}")
            print(f"  📈 Mean Time: {results['mean']:.3f} ms")
            print(f"  📊 Median Time: {results['median']:.3f} ms")
            print(f"  ⚡ Min Time: {results['min']:.3f} ms")
            print(f"  🐌 Max Time: {results['max']:.3f} ms")
            print(f"  📉 Std Dev: {results['std']:.3f} ms")
            print(f"  🎯 95th percentile: {results['p95']:.3f} ms")
            print(f"  🎯 99th percentile: {results['p99']:.3f} ms")
            
            # Throughput
            throughput = 1000 / results['mean']
            print(f"  🚀 Throughput: {throughput:.0f} decisions/sec")
            
            self.results['tests']['neural_deception'] = {
                'strategy_selection': results,
                'throughput': throughput
            }
            
            return results
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def benchmark_swarm_intelligence(self, iterations=100):
        """Benchmark Swarm Intelligence"""
        print("\n" + "="*70)
        print("🐝 SWARM INTELLIGENCE BENCHMARK")
        print("="*70)
        
        if not MODULES_AVAILABLE:
            print("❌ Modules not available")
            return None
        
        try:
            swarm = SwarmIntelligence()
            
            # Test 1: Swarm Coordination Speed
            print("\n📊 Test 1: Swarm Coordination Speed (2,100 agents)")
            times = []
            for i in range(iterations):
                start = time.perf_counter()
                defense = swarm.coordinate_defense()
                elapsed = time.perf_counter() - start
                times.append(elapsed * 1000)
            
            results = {
                'mean': np.mean(times),
                'median': np.median(times),
                'min': np.min(times),
                'max': np.max(times),
                'std': np.std(times),
                'p95': np.percentile(times, 95)
            }
            
            print(f"  ✅ Iterations: {iterations}")
            print(f"  📈 Mean Time: {results['mean']:.2f} ms")
            print(f"  📊 Median Time: {results['median']:.2f} ms")
            print(f"  ⚡ Min Time: {results['min']:.2f} ms")
            print(f"  🐌 Max Time: {results['max']:.2f} ms")
            print(f"  📉 Std Dev: {results['std']:.2f} ms")
            print(f"  🎯 95th percentile: {results['p95']:.2f} ms")
            
            throughput = 1000 / results['mean']
            print(f"  🚀 Throughput: {throughput:.1f} coordinations/sec")
            
            self.results['tests']['swarm_intelligence'] = {
                'coordination': results,
                'throughput': throughput,
                'agents': 2100
            }
            
            return results
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def benchmark_quantum_defense(self, iterations=100):
        """Benchmark Quantum Defense"""
        print("\n" + "="*70)
        print("⚛️  QUANTUM DEFENSE BENCHMARK")
        print("="*70)
        
        if not MODULES_AVAILABLE:
            print("❌ Modules not available")
            return None
        
        try:
            quantum = QuantumDefense()
            
            # Test 1: Quantum State Creation
            print("\n📊 Test 1: Quantum Superposition Creation")
            times = []
            for i in range(iterations):
                start = time.perf_counter()
                state = quantum.create_superposition()
                elapsed = time.perf_counter() - start
                times.append(elapsed * 1000)
            
            results = {
                'mean': np.mean(times),
                'median': np.median(times),
                'min': np.min(times),
                'max': np.max(times)
            }
            
            print(f"  ✅ Iterations: {iterations}")
            print(f"  📈 Mean Time: {results['mean']:.3f} ms")
            print(f"  📊 Median Time: {results['median']:.3f} ms")
            
            self.results['tests']['quantum_defense'] = results
            
            return results
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def benchmark_bio_inspired(self, iterations=100):
        """Benchmark Bio-Inspired Security"""
        print("\n" + "="*70)
        print("🧬 BIO-INSPIRED SECURITY BENCHMARK")
        print("="*70)
        
        if not MODULES_AVAILABLE:
            print("❌ Modules not available")
            return None
        
        try:
            bio = BioInspiredSecurity()
            
            # Test 1: Immune System Detection
            print("\n📊 Test 1: Immune System Threat Detection")
            times = []
            for i in range(iterations):
                antigen = np.random.random(10)
                start = time.perf_counter()
                is_threat = bio.immune_system.detect_threat(antigen)
                elapsed = time.perf_counter() - start
                times.append(elapsed * 1000)
            
            results = {
                'mean': np.mean(times),
                'median': np.median(times),
                'throughput': 1000 / np.mean(times)
            }
            
            print(f"  ✅ Iterations: {iterations}")
            print(f"  📈 Mean Time: {results['mean']:.3f} ms")
            print(f"  🚀 Throughput: {results['throughput']:.0f} checks/sec")
            
            self.results['tests']['bio_inspired'] = results
            
            return results
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def run_all_benchmarks(self):
        """Run all AI benchmarks"""
        print("\n" + "="*70)
        print("🎯 CYBER MIRAGE AI PERFORMANCE BENCHMARK SUITE")
        print("="*70)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 Python: {sys.version.split()[0]}")
        
        start_time = time.time()
        
        # Run all benchmarks
        self.benchmark_neural_deception(iterations=1000)
        self.benchmark_swarm_intelligence(iterations=100)
        self.benchmark_quantum_defense(iterations=100)
        self.benchmark_bio_inspired(iterations=100)
        
        total_time = time.time() - start_time
        
        # Summary
        print("\n" + "="*70)
        print("📊 BENCHMARK SUMMARY")
        print("="*70)
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        print(f"✅ Tests Completed: {len(self.results['tests'])}")
        
        # Save results
        self.save_results()
        
        return self.results
    
    def save_results(self):
        """Save benchmark results to file"""
        output_dir = Path(__file__).parent.parent / 'data' / 'benchmarks'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'ai_benchmark_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    benchmark = AIPerformanceBenchmark()
    benchmark.run_all_benchmarks()
