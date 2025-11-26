"""
📊 Resource Monitor - Real-time Container Monitoring
مراقبة موارد الحاويات في الوقت الفعلي

يراقب CPU, Memory, Network, Disk للكشف عن السلوك الشاذ
"""

import docker
import psutil
import time
import threading
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ResourceThresholds:
    """حدود الموارد للإنذار"""
    cpu_percent: float = 80.0
    memory_percent: float = 85.0
    disk_percent: float = 90.0
    network_mbps: float = 100.0
    processes: int = 100


@dataclass
class ResourceMetrics:
    """مقاييس الموارد"""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    network_rx_mb: float = 0.0
    network_tx_mb: float = 0.0
    disk_read_mb: float = 0.0
    disk_write_mb: float = 0.0
    processes: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_mb': self.memory_mb,
            'memory_percent': self.memory_percent,
            'network_rx_mb': self.network_rx_mb,
            'network_tx_mb': self.network_tx_mb,
            'disk_read_mb': self.disk_read_mb,
            'disk_write_mb': self.disk_write_mb,
            'processes': self.processes
        }


class ContainerResourceMonitor:
    """
    مراقب موارد الحاوية
    """
    
    def __init__(self, container_id: str, thresholds: ResourceThresholds = None):
        self.container_id = container_id
        self.thresholds = thresholds or ResourceThresholds()
        
        try:
            self.client = docker.from_env()
            self.container = self.client.containers.get(container_id)
        except Exception as e:
            logger.error(f"Cannot connect to container {container_id}: {e}")
            self.client = None
            self.container = None
        
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_history: List[ResourceMetrics] = []
        self.alerts: List[Dict] = []
    
    def get_current_metrics(self) -> Optional[ResourceMetrics]:
        """
        الحصول على مقاييس الموارد الحالية
        """
        if not self.container:
            return None
        
        try:
            # احصائيات Docker
            stats = self.container.stats(stream=False)
            
            metrics = ResourceMetrics()
            
            # CPU
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            
            if system_delta > 0:
                num_cpus = len(stats['cpu_stats']['cpu_usage'].get('percpu_usage', [0]))
                metrics.cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0
            
            # Memory
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 1)
            
            metrics.memory_mb = memory_usage / (1024 * 1024)
            metrics.memory_percent = (memory_usage / memory_limit) * 100.0
            
            # Network
            networks = stats.get('networks', {})
            for net_name, net_stats in networks.items():
                metrics.network_rx_mb += net_stats.get('rx_bytes', 0) / (1024 * 1024)
                metrics.network_tx_mb += net_stats.get('tx_bytes', 0) / (1024 * 1024)
            
            # Disk I/O
            blkio_stats = stats.get('blkio_stats', {})
            io_service_bytes = blkio_stats.get('io_service_bytes_recursive', [])
            
            for entry in io_service_bytes:
                if entry.get('op') == 'Read':
                    metrics.disk_read_mb = entry.get('value', 0) / (1024 * 1024)
                elif entry.get('op') == 'Write':
                    metrics.disk_write_mb = entry.get('value', 0) / (1024 * 1024)
            
            # Processes
            metrics.processes = stats.get('pids_stats', {}).get('current', 0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return None
    
    def check_thresholds(self, metrics: ResourceMetrics) -> List[str]:
        """
        فحص الحدود وإنشاء التنبيهات
        """
        violations = []
        
        if metrics.cpu_percent > self.thresholds.cpu_percent:
            violations.append(
                f"CPU usage {metrics.cpu_percent:.1f}% exceeds threshold "
                f"{self.thresholds.cpu_percent}%"
            )
        
        if metrics.memory_percent > self.thresholds.memory_percent:
            violations.append(
                f"Memory usage {metrics.memory_percent:.1f}% exceeds threshold "
                f"{self.thresholds.memory_percent}%"
            )
        
        if metrics.processes > self.thresholds.processes:
            violations.append(
                f"Process count {metrics.processes} exceeds threshold "
                f"{self.thresholds.processes}"
            )
        
        return violations
    
    def start_monitoring(self, interval: int = 5):
        """
        بدء المراقبة المستمرة
        """
        if self.monitoring:
            logger.warning("Monitoring already active")
            return
        
        logger.info(f"📊 Starting resource monitoring for {self.container_id}")
        self.monitoring = True
        
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitoring_loop(self, interval: int):
        """
        حلقة المراقبة
        """
        while self.monitoring:
            try:
                metrics = self.get_current_metrics()
                
                if metrics:
                    # حفظ في السجل
                    self.metrics_history.append(metrics)
                    
                    # الاحتفاظ بآخر 1000 قراءة فقط
                    if len(self.metrics_history) > 1000:
                        self.metrics_history = self.metrics_history[-1000:]
                    
                    # فحص الحدود
                    violations = self.check_thresholds(metrics)
                    
                    if violations:
                        alert = {
                            'timestamp': datetime.now().isoformat(),
                            'container_id': self.container_id,
                            'violations': violations,
                            'metrics': metrics.to_dict()
                        }
                        
                        self.alerts.append(alert)
                        
                        for violation in violations:
                            logger.warning(f"⚠️ {violation}")
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def stop_monitoring(self):
        """
        إيقاف المراقبة
        """
        logger.info(f"📊 Stopping resource monitoring for {self.container_id}")
        self.monitoring = False
    
    def get_statistics(self) -> Dict:
        """
        الحصول على إحصائيات ملخصة
        """
        if not self.metrics_history:
            return {}
        
        cpu_values = [m.cpu_percent for m in self.metrics_history]
        mem_values = [m.memory_percent for m in self.metrics_history]
        
        return {
            'container_id': self.container_id,
            'monitoring_duration': len(self.metrics_history) * 5,  # seconds
            'cpu': {
                'current': cpu_values[-1] if cpu_values else 0,
                'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0,
                'min': min(cpu_values) if cpu_values else 0
            },
            'memory': {
                'current': mem_values[-1] if mem_values else 0,
                'average': sum(mem_values) / len(mem_values) if mem_values else 0,
                'max': max(mem_values) if mem_values else 0,
                'min': min(mem_values) if mem_values else 0
            },
            'alerts_count': len(self.alerts),
            'recent_alerts': self.alerts[-5:] if self.alerts else []
        }
    
    def export_metrics(self, filename: str):
        """
        تصدير المقاييس إلى ملف JSON
        """
        try:
            data = {
                'container_id': self.container_id,
                'thresholds': {
                    'cpu_percent': self.thresholds.cpu_percent,
                    'memory_percent': self.thresholds.memory_percent,
                    'processes': self.thresholds.processes
                },
                'metrics': [m.to_dict() for m in self.metrics_history],
                'alerts': self.alerts,
                'statistics': self.get_statistics()
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Metrics exported to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")


class SystemResourceMonitor:
    """
    مراقب موارد النظام الكامل
    """
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
    
    def get_system_metrics(self) -> Dict:
        """
        الحصول على مقاييس النظام
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'cpu_count': psutil.cpu_count(),
                'memory': {
                    'total_gb': memory.total / (1024**3),
                    'used_gb': memory.used / (1024**3),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': disk.total / (1024**3),
                    'used_gb': disk.used / (1024**3),
                    'percent': disk.percent
                },
                'network': {
                    'sent_mb': network.bytes_sent / (1024**2),
                    'recv_mb': network.bytes_recv / (1024**2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}


# Demo
if __name__ == "__main__":
    print("📊 RESOURCE MONITOR - DEMO")
    print("="*80)
    
    print("\n1️⃣ Creating System Monitor...")
    system_monitor = SystemResourceMonitor()
    
    print("\n2️⃣ Getting system metrics...")
    metrics = system_monitor.get_system_metrics()
    
    if metrics:
        print(f"\n   💻 CPU: {metrics['cpu_percent']:.1f}% ({metrics['cpu_count']} cores)")
        print(f"   🧠 Memory: {metrics['memory']['percent']:.1f}% "
              f"({metrics['memory']['used_gb']:.1f}GB / {metrics['memory']['total_gb']:.1f}GB)")
        print(f"   💾 Disk: {metrics['disk']['percent']:.1f}% "
              f"({metrics['disk']['used_gb']:.1f}GB / {metrics['disk']['total_gb']:.1f}GB)")
        print(f"   🌐 Network: ↓{metrics['network']['recv_mb']:.1f}MB ↑{metrics['network']['sent_mb']:.1f}MB")
    
    print("\n3️⃣ Container Monitor Configuration...")
    thresholds = ResourceThresholds(
        cpu_percent=80.0,
        memory_percent=85.0,
        processes=100
    )
    
    print(f"   ⚠️ CPU threshold: {thresholds.cpu_percent}%")
    print(f"   ⚠️ Memory threshold: {thresholds.memory_percent}%")
    print(f"   ⚠️ Process threshold: {thresholds.processes}")
    
    print("\n✅ Demo complete!")
    print("\n📝 Note: Container monitoring requires:")
    print("   - Docker daemon running")
    print("   - Valid container ID")
    print("   - Appropriate permissions")
