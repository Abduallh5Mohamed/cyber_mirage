"""
🔍 Log Collector - Centralized Logging System
نظام جمع السجلات المركزي

يجمع السجلات من جميع المصادر ويحللها
"""

import logging
import json
import gzip
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import threading
import queue
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogEntry:
    """إدخال سجل"""
    
    def __init__(
        self,
        timestamp: datetime,
        source: str,
        level: str,
        message: str,
        metadata: Dict = None
    ):
        self.timestamp = timestamp
        self.source = source
        self.level = level
        self.message = message
        self.metadata = metadata or {}
        self.entry_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """توليد ID فريد"""
        data = f"{self.timestamp}{self.source}{self.message}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        return {
            'id': self.entry_id,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'level': self.level,
            'message': self.message,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class LogCollector:
    """
    جامع السجلات المركزي
    """
    
    def __init__(self, storage_dir: str = "./data/logs"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_queue = queue.Queue()
        self.running = False
        self.worker_thread = None
        
        self.current_file = None
        self.current_file_size = 0
        self.max_file_size = 10 * 1024 * 1024  # 10 MB
        
        self.stats = {
            'total_logs': 0,
            'logs_by_source': {},
            'logs_by_level': {}
        }
    
    def start(self):
        """بدء جامع السجلات"""
        if self.running:
            logger.warning("Log collector already running")
            return
        
        logger.info("🔍 Starting Log Collector")
        self.running = True
        
        self.worker_thread = threading.Thread(target=self._worker_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def stop(self):
        """إيقاف جامع السجلات"""
        logger.info("🔍 Stopping Log Collector")
        self.running = False
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        
        self._close_current_file()
    
    def collect(self, log_entry: LogEntry):
        """جمع إدخال سجل"""
        self.log_queue.put(log_entry)
    
    def collect_dict(self, log_dict: Dict):
        """جمع سجل من dict"""
        entry = LogEntry(
            timestamp=datetime.fromisoformat(log_dict.get('timestamp', datetime.now().isoformat())),
            source=log_dict.get('source', 'unknown'),
            level=log_dict.get('level', 'INFO'),
            message=log_dict.get('message', ''),
            metadata=log_dict.get('metadata', {})
        )
        self.collect(entry)
    
    def _worker_loop(self):
        """حلقة المعالجة"""
        while self.running:
            try:
                # الحصول على سجل من الطابور
                log_entry = self.log_queue.get(timeout=1)
                
                # كتابة السجل
                self._write_log(log_entry)
                
                # تحديث الإحصائيات
                self._update_stats(log_entry)
                
                self.log_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
    
    def _write_log(self, log_entry: LogEntry):
        """كتابة السجل إلى ملف"""
        try:
            # فتح ملف جديد إذا لزم الأمر
            if self._needs_new_file():
                self._rotate_file()
            
            # كتابة السجل
            if self.current_file:
                line = log_entry.to_json() + '\n'
                self.current_file.write(line)
                self.current_file.flush()
                
                self.current_file_size += len(line)
                
        except Exception as e:
            logger.error(f"Error writing log: {e}")
    
    def _needs_new_file(self) -> bool:
        """التحقق من الحاجة لملف جديد"""
        if not self.current_file:
            return True
        
        if self.current_file_size >= self.max_file_size:
            return True
        
        return False
    
    def _rotate_file(self):
        """تدوير الملفات"""
        self._close_current_file()
        
        # إنشاء اسم ملف جديد
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.storage_dir / f"logs_{timestamp}.jsonl"
        
        self.current_file = open(filename, 'w')
        self.current_file_size = 0
        
        logger.info(f"Created new log file: {filename}")
    
    def _close_current_file(self):
        """إغلاق الملف الحالي"""
        if self.current_file:
            self.current_file.close()
            
            # ضغط الملف
            self._compress_file(self.current_file.name)
            
            self.current_file = None
    
    def _compress_file(self, filename: str):
        """ضغط ملف السجل"""
        try:
            with open(filename, 'rb') as f_in:
                with gzip.open(f"{filename}.gz", 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # حذف الملف الأصلي
            os.remove(filename)
            
            logger.info(f"Compressed log file: {filename}.gz")
            
        except Exception as e:
            logger.error(f"Error compressing file: {e}")
    
    def _update_stats(self, log_entry: LogEntry):
        """تحديث الإحصائيات"""
        self.stats['total_logs'] += 1
        
        # إحصائيات حسب المصدر
        source = log_entry.source
        self.stats['logs_by_source'][source] = \
            self.stats['logs_by_source'].get(source, 0) + 1
        
        # إحصائيات حسب المستوى
        level = log_entry.level
        self.stats['logs_by_level'][level] = \
            self.stats['logs_by_level'].get(level, 0) + 1
    
    def get_stats(self) -> Dict:
        """الحصول على الإحصائيات"""
        return self.stats.copy()
    
    def search_logs(
        self,
        source: Optional[str] = None,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        keyword: Optional[str] = None
    ) -> List[Dict]:
        """
        البحث في السجلات
        """
        results = []
        
        try:
            # البحث في جميع ملفات السجلات
            for log_file in self.storage_dir.glob("logs_*.jsonl*"):
                
                # فك الضغط إذا لزم الأمر
                if log_file.suffix == '.gz':
                    with gzip.open(log_file, 'rt') as f:
                        lines = f.readlines()
                else:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                
                # البحث في السطور
                for line in lines:
                    try:
                        entry = json.loads(line)
                        
                        # تطبيق الفلاتر
                        if source and entry.get('source') != source:
                            continue
                        
                        if level and entry.get('level') != level:
                            continue
                        
                        timestamp = datetime.fromisoformat(entry.get('timestamp'))
                        
                        if start_time and timestamp < start_time:
                            continue
                        
                        if end_time and timestamp > end_time:
                            continue
                        
                        if keyword and keyword.lower() not in entry.get('message', '').lower():
                            continue
                        
                        results.append(entry)
                        
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            logger.error(f"Error searching logs: {e}")
        
        return results


class DockerLogCollector:
    """
    جامع سجلات Docker المتخصص
    """
    
    def __init__(self, log_collector: LogCollector):
        self.log_collector = log_collector
    
    def collect_container_logs(self, container_id: str):
        """جمع سجلات حاوية Docker"""
        try:
            import docker
            client = docker.from_env()
            container = client.containers.get(container_id)
            
            # جمع السجلات
            logs = container.logs(stream=True)
            
            for log_line in logs:
                entry = LogEntry(
                    timestamp=datetime.now(),
                    source=f"docker:{container_id[:12]}",
                    level="INFO",
                    message=log_line.decode('utf-8').strip(),
                    metadata={'container_id': container_id}
                )
                
                self.log_collector.collect(entry)
                
        except Exception as e:
            logger.error(f"Error collecting Docker logs: {e}")


class NetworkLogCollector:
    """
    جامع سجلات الشبكة
    """
    
    def __init__(self, log_collector: LogCollector):
        self.log_collector = log_collector
    
    def collect_network_traffic(self, packet_info: Dict):
        """جمع معلومات حزم الشبكة"""
        entry = LogEntry(
            timestamp=datetime.now(),
            source="network",
            level="INFO",
            message=f"Network packet: {packet_info.get('protocol')} "
                   f"{packet_info.get('src')} -> {packet_info.get('dst')}",
            metadata=packet_info
        )
        
        self.log_collector.collect(entry)


# Demo
if __name__ == "__main__":
    print("🔍 LOG COLLECTOR - DEMO")
    print("="*80)
    
    print("\n1️⃣ Creating Log Collector...")
    collector = LogCollector(storage_dir="./data/logs/demo")
    
    print("\n2️⃣ Starting collector...")
    collector.start()
    
    print("\n3️⃣ Collecting sample logs...")
    
    # سجلات عينة
    for i in range(10):
        entry = LogEntry(
            timestamp=datetime.now(),
            source="honeypot",
            level="INFO" if i % 3 != 0 else "WARNING",
            message=f"Sample log message #{i+1}",
            metadata={'test': True, 'index': i}
        )
        collector.collect(entry)
    
    print(f"   Collected 10 sample logs")
    
    # انتظار المعالجة
    import time
    time.sleep(2)
    
    print("\n4️⃣ Statistics:")
    stats = collector.get_stats()
    print(f"   Total logs: {stats['total_logs']}")
    print(f"   By source: {stats['logs_by_source']}")
    print(f"   By level: {stats['logs_by_level']}")
    
    print("\n5️⃣ Searching logs...")
    results = collector.search_logs(level="WARNING")
    print(f"   Found {len(results)} WARNING logs")
    
    print("\n6️⃣ Stopping collector...")
    collector.stop()
    
    print("\n✅ Demo complete!")
    print(f"   Logs stored in: {collector.storage_dir}")
