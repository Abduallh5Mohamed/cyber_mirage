"""
Run All Benchmarks - Complete Performance Testing Suite
Runs all benchmarks and generates comprehensive report
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path
import json
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.ai_performance import AIPerformanceBenchmark
from benchmarks.resource_usage import ResourceMonitor


class CompleteBenchmarkSuite:
    """Complete benchmark suite runner"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'benchmarks': {}
        }
    
    def run_all(self):
        """Run all benchmarks"""
        print("\n" + "="*70)
        print("🎯 CYBER MIRAGE - COMPLETE BENCHMARK SUITE")
        print("="*70)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 Platform: {sys.platform}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print("="*70)
        
        total_start = time.time()
        
        # 1. AI Performance Benchmarks
        print("\n🧠 PHASE 1: AI PERFORMANCE BENCHMARKS")
        print("-" * 70)
        
        monitor = ResourceMonitor()
        monitor.start_monitoring()
        
        ai_bench = AIPerformanceBenchmark()
        ai_results = ai_bench.run_all_benchmarks()
        self.results['benchmarks']['ai_performance'] = ai_results
        
        monitor.stop_monitoring()
        resource_stats = monitor.get_statistics()
        self.results['benchmarks']['ai_resources'] = resource_stats
        
        # 2. Load Testing (if server is running)
        print("\n🔥 PHASE 2: LOAD TESTING")
        print("-" * 70)
        print("⚠️  Skipping load tests (requires running server)")
        print("💡 Run separately: python benchmarks/load_testing.py")
        
        # Summary
        total_time = time.time() - total_start
        
        print("\n" + "="*70)
        print("🎉 BENCHMARK SUITE COMPLETE")
        print("="*70)
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        self.save_results()
    
    def generate_summary(self):
        """Generate benchmark summary"""
        print("\n" + "="*70)
        print("📊 BENCHMARK SUMMARY")
        print("="*70)
        
        # AI Performance Summary
        if 'ai_performance' in self.results['benchmarks']:
            ai = self.results['benchmarks']['ai_performance']
            
            print("\n🧠 AI Performance:")
            
            if 'neural_deception' in ai.get('tests', {}):
                neural = ai['tests']['neural_deception']
                if 'throughput' in neural:
                    print(f"  • Neural Deception: {neural['throughput']:.0f} decisions/sec")
            
            if 'swarm_intelligence' in ai.get('tests', {}):
                swarm = ai['tests']['swarm_intelligence']
                if 'throughput' in swarm:
                    print(f"  • Swarm Intelligence: {swarm['throughput']:.1f} coordinations/sec "
                          f"({swarm.get('agents', 0)} agents)")
        
        # Resource Usage Summary
        if 'ai_resources' in self.results['benchmarks']:
            res = self.results['benchmarks']['ai_resources']
            
            print("\n💻 Resource Usage:")
            if 'cpu' in res:
                print(f"  • CPU: {res['cpu']['mean']:.1f}% avg, {res['cpu']['max']:.1f}% peak")
            if 'memory' in res:
                print(f"  • Memory: {res['memory']['mean_mb']:.0f} MB avg, "
                      f"{res['memory']['max_mb']:.0f} MB peak")
        
        # Overall Rating
        print("\n🏆 Overall Performance Rating:")
        self.calculate_rating()
    
    def calculate_rating(self):
        """Calculate overall performance rating"""
        score = 0
        max_score = 0
        
        # AI throughput check
        if 'ai_performance' in self.results['benchmarks']:
            ai = self.results['benchmarks']['ai_performance']
            
            if 'neural_deception' in ai.get('tests', {}):
                throughput = ai['tests']['neural_deception'].get('throughput', 0)
                max_score += 100
                if throughput > 1000:
                    score += 100
                elif throughput > 500:
                    score += 80
                elif throughput > 200:
                    score += 60
                else:
                    score += 40
        
        # Resource efficiency check
        if 'ai_resources' in self.results['benchmarks']:
            res = self.results['benchmarks']['ai_resources']
            max_score += 100
            
            cpu_ok = res.get('cpu', {}).get('mean', 100) < 80
            mem_ok = res.get('memory', {}).get('mean_percent', 100) < 80
            
            if cpu_ok and mem_ok:
                score += 100
            elif cpu_ok or mem_ok:
                score += 70
            else:
                score += 40
        
        if max_score > 0:
            percentage = (score / max_score) * 100
            
            if percentage >= 90:
                rating = "⭐⭐⭐⭐⭐ EXCELLENT"
            elif percentage >= 75:
                rating = "⭐⭐⭐⭐ VERY GOOD"
            elif percentage >= 60:
                rating = "⭐⭐⭐ GOOD"
            elif percentage >= 45:
                rating = "⭐⭐ FAIR"
            else:
                rating = "⭐ NEEDS IMPROVEMENT"
            
            print(f"  {rating} ({percentage:.0f}/100)")
        else:
            print("  ⚠️  Insufficient data for rating")
    
    def save_results(self):
        """Save complete benchmark results"""
        output_dir = Path(__file__).parent.parent / 'data' / 'benchmarks'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'complete_benchmark_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Complete results saved to: {output_file}")
        
        # Also save a summary report
        summary_file = output_dir / f'summary_{timestamp}.txt'
        with open(summary_file, 'w') as f:
            f.write("CYBER MIRAGE - BENCHMARK SUMMARY\n")
            f.write("=" * 70 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            
            # Add summary content
            if 'ai_performance' in self.results['benchmarks']:
                f.write("AI Performance:\n")
                ai = self.results['benchmarks']['ai_performance']
                for test_name, test_data in ai.get('tests', {}).items():
                    f.write(f"  • {test_name}: {json.dumps(test_data, indent=4)}\n")
        
        print(f"💾 Summary report saved to: {summary_file}")


if __name__ == "__main__":
    print("\n🎯 CYBER MIRAGE - COMPLETE BENCHMARK SUITE")
    print("="*70)
    print("\n⚠️  WARNING:")
    print("  • This will run comprehensive performance tests")
    print("  • Tests may take 2-5 minutes")
    print("  • System resources will be monitored")
    print("\n💡 TIP: Close unnecessary applications for accurate results")
    
    confirm = input("\nProceed with benchmarks? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        suite = CompleteBenchmarkSuite()
        suite.run_all()
        
        print("\n" + "="*70)
        print("✅ ALL BENCHMARKS COMPLETE!")
        print("="*70)
        print("\n📁 Results saved to: data/benchmarks/")
        print("\n💡 Next steps:")
        print("  1. Review benchmark results")
        print("  2. Run load tests: python benchmarks/load_testing.py")
        print("  3. Optimize based on findings")
        print("  4. Re-run benchmarks after optimization")
    else:
        print("\n❌ Cancelled")
