"""
Load Testing - Stress Test with High Volume Attacks
Tests system performance under heavy load (10K+ concurrent attacks)
"""

import asyncio
import aiohttp
import time
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class LoadTester:
    """High-volume concurrent attack simulator"""
    
    def __init__(self, base_url='http://localhost:8080'):
        self.base_url = base_url
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': []
        }
    
    async def simulate_single_attack(self, session, attack_id, attack_type='web'):
        """Simulate a single attack"""
        try:
            start = time.perf_counter()
            
            if attack_type == 'web':
                # Web attack (SQL injection)
                async with session.get(
                    f"{self.base_url}/login",
                    params={'username': f"admin' OR '1'='1", 'password': 'test'},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    status = response.status
                    elapsed = time.perf_counter() - start
                    return {
                        'id': attack_id,
                        'type': attack_type,
                        'status': status,
                        'time': elapsed * 1000,  # ms
                        'success': True
                    }
            
            elif attack_type == 'scan':
                # Port scan simulation
                async with session.get(
                    f"{self.base_url}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    status = response.status
                    elapsed = time.perf_counter() - start
                    return {
                        'id': attack_id,
                        'type': attack_type,
                        'status': status,
                        'time': elapsed * 1000,
                        'success': True
                    }
        
        except asyncio.TimeoutError:
            elapsed = time.perf_counter() - start
            return {
                'id': attack_id,
                'type': attack_type,
                'error': 'timeout',
                'time': elapsed * 1000,
                'success': False
            }
        except Exception as e:
            elapsed = time.perf_counter() - start
            return {
                'id': attack_id,
                'type': attack_type,
                'error': str(e),
                'time': elapsed * 1000,
                'success': False
            }
    
    async def run_load_test(self, num_attacks=1000, attack_type='web', batch_size=100):
        """
        Run load test with specified number of attacks
        
        Args:
            num_attacks: Total number of attacks to simulate
            attack_type: Type of attack ('web', 'scan')
            batch_size: Number of concurrent requests per batch
        """
        print("\n" + "="*70)
        print(f"🔥 LOAD TEST - {attack_type.upper()} ATTACKS")
        print("="*70)
        print(f"📊 Total Attacks: {num_attacks:,}")
        print(f"⚡ Batch Size: {batch_size}")
        print(f"🎯 Target: {self.base_url}")
        print("="*70)
        
        # Create connector with connection pooling
        connector = aiohttp.TCPConnector(
            limit=batch_size,
            limit_per_host=batch_size,
            ttl_dns_cache=300
        )
        
        results = []
        start_time = time.time()
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Process in batches to avoid overwhelming the system
            for batch_start in range(0, num_attacks, batch_size):
                batch_end = min(batch_start + batch_size, num_attacks)
                batch_num = batch_start // batch_size + 1
                total_batches = (num_attacks + batch_size - 1) // batch_size
                
                print(f"\n⏳ Processing batch {batch_num}/{total_batches} "
                      f"(attacks {batch_start+1}-{batch_end})...", end='', flush=True)
                
                # Create tasks for this batch
                tasks = [
                    self.simulate_single_attack(session, i, attack_type)
                    for i in range(batch_start, batch_end)
                ]
                
                # Run batch
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                results.extend([r for r in batch_results if not isinstance(r, Exception)])
                
                print(f" ✅ Done")
        
        total_time = time.time() - start_time
        
        # Analyze results
        self.analyze_results(results, total_time, num_attacks, attack_type)
        
        return results
    
    def analyze_results(self, results, total_time, num_attacks, attack_type):
        """Analyze and display load test results"""
        
        print("\n" + "="*70)
        print("📊 LOAD TEST RESULTS")
        print("="*70)
        
        # Basic stats
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        print(f"\n📈 Overall Statistics:")
        print(f"  ✅ Total Attacks Sent: {num_attacks:,}")
        print(f"  ✅ Successful: {len(successful):,} ({len(successful)/num_attacks*100:.1f}%)")
        print(f"  ❌ Failed: {len(failed):,} ({len(failed)/num_attacks*100:.1f}%)")
        print(f"  ⏱️  Total Duration: {total_time:.2f} seconds")
        print(f"  🚀 Throughput: {num_attacks/total_time:.2f} attacks/sec")
        
        # Response time statistics
        if successful:
            times = [r['time'] for r in successful]
            print(f"\n⚡ Response Time Statistics:")
            print(f"  📊 Mean: {np.mean(times):.2f} ms")
            print(f"  📊 Median: {np.median(times):.2f} ms")
            print(f"  ⚡ Min: {np.min(times):.2f} ms")
            print(f"  🐌 Max: {np.max(times):.2f} ms")
            print(f"  📉 Std Dev: {np.std(times):.2f} ms")
            print(f"  🎯 95th percentile: {np.percentile(times, 95):.2f} ms")
            print(f"  🎯 99th percentile: {np.percentile(times, 99):.2f} ms")
        
        # Error analysis
        if failed:
            print(f"\n❌ Error Analysis:")
            error_types = {}
            for r in failed:
                error = r.get('error', 'unknown')
                error_types[error] = error_types.get(error, 0) + 1
            
            for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {error}: {count} ({count/len(failed)*100:.1f}%)")
        
        # Performance rating
        print(f"\n🏆 Performance Rating:")
        throughput = num_attacks / total_time
        success_rate = len(successful) / num_attacks * 100
        
        if throughput > 1000 and success_rate > 95:
            rating = "⭐⭐⭐⭐⭐ EXCELLENT"
        elif throughput > 500 and success_rate > 90:
            rating = "⭐⭐⭐⭐ VERY GOOD"
        elif throughput > 200 and success_rate > 80:
            rating = "⭐⭐⭐ GOOD"
        elif throughput > 100 and success_rate > 70:
            rating = "⭐⭐ FAIR"
        else:
            rating = "⭐ NEEDS IMPROVEMENT"
        
        print(f"  {rating}")
        print(f"  • Throughput: {throughput:.0f} attacks/sec")
        print(f"  • Success Rate: {success_rate:.1f}%")
        
        # Save results
        self.save_results({
            'attack_type': attack_type,
            'total_attacks': num_attacks,
            'successful': len(successful),
            'failed': len(failed),
            'duration': total_time,
            'throughput': throughput,
            'success_rate': success_rate,
            'response_times': {
                'mean': float(np.mean(times)) if successful else 0,
                'median': float(np.median(times)) if successful else 0,
                'p95': float(np.percentile(times, 95)) if successful else 0,
                'p99': float(np.percentile(times, 99)) if successful else 0
            }
        })
    
    def save_results(self, summary):
        """Save load test results"""
        output_dir = Path(__file__).parent.parent / 'data' / 'benchmarks'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'load_test_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")


async def main():
    """Run load tests"""
    tester = LoadTester()
    
    print("\n" + "="*70)
    print("🎯 CYBER MIRAGE LOAD TESTING SUITE")
    print("="*70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test scenarios
    scenarios = [
        {'name': 'Light Load', 'attacks': 100, 'batch': 10},
        {'name': 'Medium Load', 'attacks': 1000, 'batch': 50},
        {'name': 'Heavy Load', 'attacks': 5000, 'batch': 100},
        {'name': 'Extreme Load', 'attacks': 10000, 'batch': 200},
    ]
    
    print("\n📋 Available Test Scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"  {i}. {scenario['name']}: {scenario['attacks']:,} attacks "
              f"(batch size: {scenario['batch']})")
    print("  5. Custom")
    print("  0. Run all scenarios")
    
    try:
        choice = input("\n👉 Select scenario (0-5): ").strip()
        
        if choice == '0':
            # Run all scenarios
            for scenario in scenarios:
                await tester.run_load_test(
                    num_attacks=scenario['attacks'],
                    attack_type='web',
                    batch_size=scenario['batch']
                )
                await asyncio.sleep(2)  # Cool down between tests
        
        elif choice in ['1', '2', '3', '4']:
            scenario = scenarios[int(choice) - 1]
            await tester.run_load_test(
                num_attacks=scenario['attacks'],
                attack_type='web',
                batch_size=scenario['batch']
            )
        
        elif choice == '5':
            num_attacks = int(input("Number of attacks: "))
            batch_size = int(input("Batch size: "))
            await tester.run_load_test(
                num_attacks=num_attacks,
                attack_type='web',
                batch_size=batch_size
            )
        
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("\n⚠️  WARNING: This will generate high traffic!")
    print("⚠️  Make sure Cyber Mirage is running: .\\start_defense.ps1")
    print("⚠️  Press Ctrl+C to stop at any time\n")
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm in ['yes', 'y']:
        asyncio.run(main())
    else:
        print("❌ Cancelled")
