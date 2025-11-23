"""
Resource Usage Monitoring
Monitors CPU, RAM, Network usage during operations
"""

import psutil
import time
import json
from datetime import datetime
from pathlib import Path
import sys
import threading

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ResourceMonitor:
    """Monitor system resource usage"""
    
    def __init__(self, interval=1.0):
        self.interval = interval
        self.monitoring = False
        self.samples = []
        self.start_time = None
    
    def start_monitoring(self):
        """Start resource monitoring in background thread"""
        self.monitoring = True
        self.start_time = time.time()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2)
        print("✅ Resource monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            sample = {
                'timestamp': time.time() - self.start_time,
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_mb': psutil.virtual_memory().used / (1024 * 1024),
                'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                'network_io': psutil.net_io_counters()._asdict()
            }
            self.samples.append(sample)
            time.sleep(self.interval)
    
    def get_statistics(self):
        """Calculate statistics from samples"""
        if not self.samples:
            return None
        
        cpu_values = [s['cpu_percent'] for s in self.samples]
        mem_values = [s['memory_percent'] for s in self.samples]
        mem_mb_values = [s['memory_mb'] for s in self.samples]
        
        stats = {
            'duration': self.samples[-1]['timestamp'],
            'samples': len(self.samples),
            'cpu': {
                'mean': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'mean_percent': sum(mem_values) / len(mem_values),
                'max_percent': max(mem_values),
                'mean_mb': sum(mem_mb_values) / len(mem_mb_values),
                'max_mb': max(mem_mb_values)
            }
        }
        
        # Network statistics
        if self.samples[0]['network_io'] and self.samples[-1]['network_io']:
            net_start = self.samples[0]['network_io']
            net_end = self.samples[-1]['network_io']
            duration = self.samples[-1]['timestamp']
            
            stats['network'] = {
                'bytes_sent': net_end['bytes_sent'] - net_start['bytes_sent'],
                'bytes_recv': net_end['bytes_recv'] - net_start['bytes_recv'],
                'packets_sent': net_end['packets_sent'] - net_start['packets_sent'],
                'packets_recv': net_end['packets_recv'] - net_start['packets_recv'],
                'throughput_sent_mbps': ((net_end['bytes_sent'] - net_start['bytes_sent']) / duration) / (1024 * 1024) * 8,
                'throughput_recv_mbps': ((net_end['bytes_recv'] - net_start['bytes_recv']) / duration) / (1024 * 1024) * 8
            }
        
        return stats
    
    def print_report(self):
        """Print resource usage report"""
        stats = self.get_statistics()
        
        if not stats:
            print("❌ No data collected")
            return
        
        print("\n" + "="*70)
        print("📊 RESOURCE USAGE REPORT")
        print("="*70)
        
        print(f"\n⏱️  Monitoring Duration: {stats['duration']:.1f} seconds")
        print(f"📊 Samples Collected: {stats['samples']}")
        
        print(f"\n💻 CPU Usage:")
        print(f"  📈 Mean: {stats['cpu']['mean']:.1f}%")
        print(f"  🔥 Max: {stats['cpu']['max']:.1f}%")
        print(f"  ❄️  Min: {stats['cpu']['min']:.1f}%")
        
        print(f"\n🧠 Memory Usage:")
        print(f"  📈 Mean: {stats['memory']['mean_percent']:.1f}% ({stats['memory']['mean_mb']:.0f} MB)")
        print(f"  🔥 Max: {stats['memory']['max_percent']:.1f}% ({stats['memory']['max_mb']:.0f} MB)")
        
        if 'network' in stats:
            print(f"\n🌐 Network Usage:")
            print(f"  📤 Sent: {stats['network']['bytes_sent'] / (1024*1024):.2f} MB "
                  f"({stats['network']['packets_sent']:,} packets)")
            print(f"  📥 Received: {stats['network']['bytes_recv'] / (1024*1024):.2f} MB "
                  f"({stats['network']['packets_recv']:,} packets)")
            print(f"  🚀 Throughput: ↑ {stats['network']['throughput_sent_mbps']:.2f} Mbps "
                  f"/ ↓ {stats['network']['throughput_recv_mbps']:.2f} Mbps")
        
        # Performance rating
        print(f"\n🏆 Performance Rating:")
        cpu_ok = stats['cpu']['mean'] < 80
        mem_ok = stats['memory']['mean_percent'] < 80
        
        if cpu_ok and mem_ok:
            print("  ⭐⭐⭐⭐⭐ EXCELLENT - Resources well utilized")
        elif cpu_ok or mem_ok:
            print("  ⭐⭐⭐ GOOD - Some optimization possible")
        else:
            print("  ⭐⭐ NEEDS OPTIMIZATION - High resource usage")
        
        return stats
    
    def save_report(self, stats):
        """Save resource usage report"""
        output_dir = Path(__file__).parent.parent / 'data' / 'benchmarks'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'resource_usage_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'statistics': stats,
                'samples': self.samples
            }, f, indent=2)
        
        print(f"\n💾 Report saved to: {output_file}")


def benchmark_with_monitoring(func, duration=10):
    """
    Run a function while monitoring resources
    
    Args:
        func: Function to benchmark
        duration: How long to run (seconds)
    """
    print("\n" + "="*70)
    print("🎯 BENCHMARKING WITH RESOURCE MONITORING")
    print("="*70)
    
    monitor = ResourceMonitor(interval=0.5)
    monitor.start_monitoring()
    
    try:
        print(f"\n⏱️  Running for {duration} seconds...")
        start = time.time()
        
        while time.time() - start < duration:
            func()
            time.sleep(0.01)
        
        print("✅ Benchmark complete")
    
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    
    finally:
        monitor.stop_monitoring()
        stats = monitor.print_report()
        monitor.save_report(stats)


def demo_workload():
    """Demo workload for testing"""
    import random
    # Simulate some work
    data = [random.random() for _ in range(1000)]
    result = sum(data) / len(data)


if __name__ == "__main__":
    print("\n📊 RESOURCE USAGE MONITOR")
    print("="*70)
    
    print("\nOptions:")
    print("  1. Monitor demo workload (10 seconds)")
    print("  2. Monitor AI components (30 seconds)")
    print("  3. Monitor custom duration")
    
    choice = input("\n👉 Select option (1-3): ").strip()
    
    if choice == '1':
        benchmark_with_monitoring(demo_workload, duration=10)
    
    elif choice == '2':
        def ai_workload():
            try:
                from src.ai.neural_deception import NeuralDeception
                deception = NeuralDeception()
                deception.select_strategy(0.5)
            except:
                demo_workload()
        
        benchmark_with_monitoring(ai_workload, duration=30)
    
    elif choice == '3':
        duration = int(input("Duration (seconds): "))
        benchmark_with_monitoring(demo_workload, duration=duration)
    
    else:
        print("❌ Invalid choice")
