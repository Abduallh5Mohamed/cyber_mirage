"""
📨 Message Queue Service - Redis Streams Implementation
Cyber Mirage - Role 7: Data Pipeline & Orchestration

Lightweight message queue using Redis Streams for:
- Asynchronous event processing
- Attack event streaming
- AI agent decision pipeline
- Forensics evidence queue
- Alert notifications

Author: Cyber Mirage Team
Version: 1.0.0 - Production
"""

import json
import logging
import time
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class StreamName(Enum):
    """Available message streams"""
    ATTACK_EVENTS = "stream:attacks"
    AI_DECISIONS = "stream:ai_decisions"
    FORENSICS = "stream:forensics"
    ALERTS = "stream:alerts"
    THREAT_INTEL = "stream:threat_intel"
    HONEYPOT_LOGS = "stream:honeypot_logs"
    SYSTEM_EVENTS = "stream:system_events"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class ConsumerGroup(Enum):
    """Consumer groups for stream processing"""
    AI_PROCESSOR = "group:ai_processor"
    FORENSICS_COLLECTOR = "group:forensics"
    ALERT_MANAGER = "group:alerts"
    DASHBOARD_UPDATER = "group:dashboard"
    LOG_ARCHIVER = "group:archiver"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Message:
    """Represents a message in the queue"""
    message_id: str
    stream: str
    payload: Dict[str, Any]
    priority: int
    timestamp: str
    producer_id: str
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_redis(self) -> Dict[str, str]:
        """Convert to Redis-compatible format"""
        return {
            'message_id': self.message_id,
            'payload': json.dumps(self.payload),
            'priority': str(self.priority),
            'timestamp': self.timestamp,
            'producer_id': self.producer_id,
            'retry_count': str(self.retry_count),
            'max_retries': str(self.max_retries)
        }
    
    @classmethod
    def from_redis(cls, message_id: str, stream: str, data: Dict[str, str]) -> 'Message':
        """Create Message from Redis data"""
        return cls(
            message_id=data.get('message_id', message_id),
            stream=stream,
            payload=json.loads(data.get('payload', '{}')),
            priority=int(data.get('priority', 2)),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            producer_id=data.get('producer_id', 'unknown'),
            retry_count=int(data.get('retry_count', 0)),
            max_retries=int(data.get('max_retries', 3))
        )


@dataclass
class StreamStats:
    """Statistics for a stream"""
    stream_name: str
    length: int
    groups: int
    first_entry: Optional[str]
    last_entry: Optional[str]
    pending_messages: int


# =============================================================================
# MESSAGE QUEUE MANAGER
# =============================================================================

class MessageQueueManager:
    """
    Production-grade message queue using Redis Streams
    
    Features:
    - Multiple streams for different event types
    - Consumer groups for distributed processing
    - Message acknowledgment and retry
    - Dead letter queue for failed messages
    - Stream trimming and cleanup
    - Metrics and monitoring
    """
    
    def __init__(
        self,
        redis_host: str = 'redis',
        redis_port: int = 6379,
        redis_password: str = None,
        max_stream_length: int = 100000,
        producer_id: str = None
    ):
        """
        Initialize message queue manager
        
        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_password: Redis password
            max_stream_length: Maximum messages per stream
            producer_id: Unique producer identifier
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.max_stream_length = max_stream_length
        self.producer_id = producer_id or f"producer-{uuid.uuid4().hex[:8]}"
        
        # Redis connection
        self._redis: Optional[redis.Redis] = None
        
        # Message handlers
        self._handlers: Dict[str, List[Callable]] = {}
        
        # Consumer threads
        self._consumers: Dict[str, threading.Thread] = {}
        self._running = False
        
        # Statistics
        self.stats = {
            'messages_published': 0,
            'messages_consumed': 0,
            'messages_failed': 0,
            'messages_retried': 0
        }
        
        logger.info(f"MessageQueueManager initialized with producer_id: {self.producer_id}")
    
    @property
    def redis(self) -> redis.Redis:
        """Get or create Redis connection"""
        if self._redis is None:
            self._redis = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
        return self._redis
    
    def is_connected(self) -> bool:
        """Check Redis connection"""
        try:
            self.redis.ping()
            return True
        except Exception:
            return False
    
    # =========================================================================
    # STREAM MANAGEMENT
    # =========================================================================
    
    def create_stream(self, stream: StreamName) -> bool:
        """Create a stream if it doesn't exist"""
        try:
            # XADD with NOMKSTREAM won't create, so we add a dummy entry
            # Then delete it to ensure stream exists
            self.redis.xadd(stream.value, {'init': 'true'}, maxlen=self.max_stream_length)
            return True
        except Exception as e:
            logger.error(f"Failed to create stream {stream.value}: {e}")
            return False
    
    def create_consumer_group(
        self,
        stream: StreamName,
        group: ConsumerGroup,
        start_from: str = '0'
    ) -> bool:
        """Create a consumer group for a stream"""
        try:
            self.redis.xgroup_create(
                stream.value,
                group.value,
                id=start_from,
                mkstream=True
            )
            logger.info(f"Created consumer group {group.value} for stream {stream.value}")
            return True
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                # Group already exists
                return True
            logger.error(f"Failed to create consumer group: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to create consumer group: {e}")
            return False
    
    def get_stream_info(self, stream: StreamName) -> Optional[StreamStats]:
        """Get stream information"""
        try:
            info = self.redis.xinfo_stream(stream.value)
            groups = self.redis.xinfo_groups(stream.value)
            
            return StreamStats(
                stream_name=stream.value,
                length=info.get('length', 0),
                groups=len(groups),
                first_entry=info.get('first-entry', [None])[0] if info.get('first-entry') else None,
                last_entry=info.get('last-entry', [None])[0] if info.get('last-entry') else None,
                pending_messages=sum(g.get('pending', 0) for g in groups)
            )
        except redis.ResponseError:
            return None
        except Exception as e:
            logger.error(f"Failed to get stream info: {e}")
            return None
    
    def trim_stream(self, stream: StreamName, maxlen: int = None) -> int:
        """Trim stream to maximum length"""
        try:
            maxlen = maxlen or self.max_stream_length
            return self.redis.xtrim(stream.value, maxlen=maxlen, approximate=True)
        except Exception as e:
            logger.error(f"Failed to trim stream: {e}")
            return 0
    
    # =========================================================================
    # MESSAGE PUBLISHING
    # =========================================================================
    
    def publish(
        self,
        stream: StreamName,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> Optional[str]:
        """
        Publish a message to a stream
        
        Args:
            stream: Target stream
            payload: Message payload
            priority: Message priority
        
        Returns:
            Message ID if successful
        """
        try:
            message = Message(
                message_id=str(uuid.uuid4()),
                stream=stream.value,
                payload=payload,
                priority=priority.value,
                timestamp=datetime.now().isoformat(),
                producer_id=self.producer_id
            )
            
            # Add to stream
            redis_id = self.redis.xadd(
                stream.value,
                message.to_redis(),
                maxlen=self.max_stream_length
            )
            
            self.stats['messages_published'] += 1
            logger.debug(f"Published message {message.message_id} to {stream.value}")
            
            return redis_id
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return None
    
    def publish_attack_event(
        self,
        attacker_ip: str,
        service: str,
        action: str,
        details: Dict = None
    ) -> Optional[str]:
        """Publish an attack event"""
        payload = {
            'event_type': 'attack',
            'attacker_ip': attacker_ip,
            'service': service,
            'action': action,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        return self.publish(StreamName.ATTACK_EVENTS, payload, MessagePriority.HIGH)
    
    def publish_ai_decision(
        self,
        session_id: str,
        action: str,
        state: Dict,
        reward: float
    ) -> Optional[str]:
        """Publish an AI decision event"""
        payload = {
            'event_type': 'ai_decision',
            'session_id': session_id,
            'action': action,
            'state': state,
            'reward': reward,
            'timestamp': datetime.now().isoformat()
        }
        return self.publish(StreamName.AI_DECISIONS, payload)
    
    def publish_alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        description: str,
        source: str = None
    ) -> Optional[str]:
        """Publish an alert"""
        priority = MessagePriority.CRITICAL if severity == 'critical' else MessagePriority.HIGH
        payload = {
            'event_type': 'alert',
            'alert_type': alert_type,
            'severity': severity,
            'title': title,
            'description': description,
            'source': source or self.producer_id,
            'timestamp': datetime.now().isoformat()
        }
        return self.publish(StreamName.ALERTS, payload, priority)
    
    def publish_forensics_event(
        self,
        evidence_type: str,
        case_id: str,
        data: Dict
    ) -> Optional[str]:
        """Publish a forensics collection event"""
        payload = {
            'event_type': 'forensics',
            'evidence_type': evidence_type,
            'case_id': case_id,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        return self.publish(StreamName.FORENSICS, payload)
    
    # =========================================================================
    # MESSAGE CONSUMPTION
    # =========================================================================
    
    def consume(
        self,
        stream: StreamName,
        group: ConsumerGroup,
        consumer_name: str,
        count: int = 10,
        block: int = 5000
    ) -> List[Message]:
        """
        Consume messages from a stream
        
        Args:
            stream: Source stream
            group: Consumer group
            consumer_name: Consumer name
            count: Maximum messages to read
            block: Block timeout in milliseconds
        
        Returns:
            List of messages
        """
        try:
            # Ensure group exists
            self.create_consumer_group(stream, group)
            
            # Read new messages
            result = self.redis.xreadgroup(
                group.value,
                consumer_name,
                {stream.value: '>'},
                count=count,
                block=block
            )
            
            messages = []
            if result:
                for stream_name, entries in result:
                    for entry_id, data in entries:
                        message = Message.from_redis(entry_id, stream_name, data)
                        messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to consume messages: {e}")
            return []
    
    def acknowledge(
        self,
        stream: StreamName,
        group: ConsumerGroup,
        message_ids: List[str]
    ) -> int:
        """Acknowledge processed messages"""
        try:
            return self.redis.xack(stream.value, group.value, *message_ids)
        except Exception as e:
            logger.error(f"Failed to acknowledge messages: {e}")
            return 0
    
    def get_pending(
        self,
        stream: StreamName,
        group: ConsumerGroup,
        count: int = 100
    ) -> List[Dict]:
        """Get pending messages for a group"""
        try:
            pending = self.redis.xpending_range(
                stream.value,
                group.value,
                '-',
                '+',
                count=count
            )
            return pending
        except Exception as e:
            logger.error(f"Failed to get pending messages: {e}")
            return []
    
    def claim_pending(
        self,
        stream: StreamName,
        group: ConsumerGroup,
        consumer_name: str,
        min_idle_time: int = 60000,
        count: int = 10
    ) -> List[Message]:
        """Claim pending messages from failed consumers"""
        try:
            # Get pending messages
            pending = self.get_pending(stream, group, count)
            
            if not pending:
                return []
            
            # Filter by idle time
            message_ids = [
                p['message_id'] for p in pending
                if p.get('time_since_delivered', 0) > min_idle_time
            ]
            
            if not message_ids:
                return []
            
            # Claim messages
            result = self.redis.xclaim(
                stream.value,
                group.value,
                consumer_name,
                min_idle_time,
                message_ids
            )
            
            messages = []
            for entry_id, data in result:
                message = Message.from_redis(entry_id, stream.value, data)
                message.retry_count += 1
                messages.append(message)
                self.stats['messages_retried'] += 1
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to claim pending messages: {e}")
            return []
    
    # =========================================================================
    # MESSAGE HANDLERS
    # =========================================================================
    
    def register_handler(
        self,
        stream: StreamName,
        handler: Callable[[Message], bool]
    ):
        """Register a message handler for a stream"""
        if stream.value not in self._handlers:
            self._handlers[stream.value] = []
        self._handlers[stream.value].append(handler)
        logger.info(f"Registered handler for stream {stream.value}")
    
    def _process_message(self, message: Message) -> bool:
        """Process a message using registered handlers"""
        handlers = self._handlers.get(message.stream, [])
        
        if not handlers:
            logger.warning(f"No handlers for stream {message.stream}")
            return True
        
        success = True
        for handler in handlers:
            try:
                if not handler(message):
                    success = False
            except Exception as e:
                logger.error(f"Handler error for message {message.message_id}: {e}")
                success = False
        
        if success:
            self.stats['messages_consumed'] += 1
        else:
            self.stats['messages_failed'] += 1
        
        return success
    
    # =========================================================================
    # CONSUMER WORKERS
    # =========================================================================
    
    def start_consumer(
        self,
        stream: StreamName,
        group: ConsumerGroup,
        consumer_name: str = None
    ):
        """Start a consumer worker thread"""
        consumer_name = consumer_name or f"consumer-{uuid.uuid4().hex[:8]}"
        
        def worker():
            logger.info(f"Consumer {consumer_name} started for {stream.value}")
            
            while self._running:
                try:
                    # Consume messages
                    messages = self.consume(stream, group, consumer_name, count=10, block=5000)
                    
                    for message in messages:
                        success = self._process_message(message)
                        
                        if success:
                            self.acknowledge(stream, group, [message.message_id])
                        elif message.retry_count >= message.max_retries:
                            # Move to dead letter queue
                            self._move_to_dlq(message)
                            self.acknowledge(stream, group, [message.message_id])
                    
                    # Claim stale pending messages
                    stale_messages = self.claim_pending(
                        stream, group, consumer_name,
                        min_idle_time=60000, count=5
                    )
                    
                    for message in stale_messages:
                        if message.retry_count < message.max_retries:
                            self._process_message(message)
                            self.acknowledge(stream, group, [message.message_id])
                        else:
                            self._move_to_dlq(message)
                            self.acknowledge(stream, group, [message.message_id])
                    
                except Exception as e:
                    logger.error(f"Consumer {consumer_name} error: {e}")
                    time.sleep(1)
            
            logger.info(f"Consumer {consumer_name} stopped")
        
        thread = threading.Thread(target=worker, daemon=True)
        self._consumers[consumer_name] = thread
        self._running = True
        thread.start()
        
        return consumer_name
    
    def _move_to_dlq(self, message: Message):
        """Move failed message to dead letter queue"""
        try:
            dlq_payload = {
                'original_stream': message.stream,
                'original_message': message.to_dict(),
                'failed_at': datetime.now().isoformat(),
                'retry_count': message.retry_count
            }
            self.redis.xadd(
                'stream:dead_letter',
                {'payload': json.dumps(dlq_payload)},
                maxlen=10000
            )
            logger.warning(f"Message {message.message_id} moved to DLQ after {message.retry_count} retries")
        except Exception as e:
            logger.error(f"Failed to move message to DLQ: {e}")
    
    def stop_consumers(self):
        """Stop all consumer workers"""
        self._running = False
        for name, thread in self._consumers.items():
            thread.join(timeout=10)
        self._consumers.clear()
        logger.info("All consumers stopped")
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        stats = dict(self.stats)
        
        # Add stream stats
        stream_stats = {}
        for stream in StreamName:
            info = self.get_stream_info(stream)
            if info:
                stream_stats[stream.value] = {
                    'length': info.length,
                    'groups': info.groups,
                    'pending': info.pending_messages
                }
        
        stats['streams'] = stream_stats
        stats['consumers'] = len(self._consumers)
        stats['running'] = self._running
        
        return stats
    
    def flush_stream(self, stream: StreamName) -> bool:
        """Delete all messages from a stream"""
        try:
            self.redis.delete(stream.value)
            logger.info(f"Flushed stream {stream.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to flush stream: {e}")
            return False
    
    def close(self):
        """Close connections and stop consumers"""
        self.stop_consumers()
        if self._redis:
            self._redis.close()
            self._redis = None
        logger.info("MessageQueueManager closed")


# =============================================================================
# EVENT PUBLISHER SINGLETON
# =============================================================================

_queue_instance: Optional[MessageQueueManager] = None


def get_queue(
    redis_host: str = 'redis',
    redis_port: int = 6379,
    redis_password: str = None
) -> MessageQueueManager:
    """Get or create MessageQueueManager singleton"""
    global _queue_instance
    
    if _queue_instance is None:
        _queue_instance = MessageQueueManager(
            redis_host=redis_host,
            redis_port=redis_port,
            redis_password=redis_password
        )
    
    return _queue_instance


# =============================================================================
# MAIN - TESTING
# =============================================================================

if __name__ == "__main__":
    import os
    
    # Get settings from environment
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_password = os.getenv('REDIS_PASSWORD')
    
    # Create queue manager
    queue = MessageQueueManager(
        redis_host=redis_host,
        redis_port=redis_port,
        redis_password=redis_password
    )
    
    if not queue.is_connected():
        print("❌ Redis not connected")
        exit(1)
    
    print("✅ Redis connected")
    
    # Test publishing
    print("\n📨 Publishing test messages...")
    
    # Attack event
    msg_id = queue.publish_attack_event(
        attacker_ip="192.168.1.100",
        service="SSH",
        action="brute_force",
        details={"attempts": 50}
    )
    print(f"  Attack event: {msg_id}")
    
    # AI decision
    msg_id = queue.publish_ai_decision(
        session_id="session-123",
        action="DELAY_RESPONSE",
        state={"command_count": 5},
        reward=0.5
    )
    print(f"  AI decision: {msg_id}")
    
    # Alert
    msg_id = queue.publish_alert(
        alert_type="intrusion",
        severity="high",
        title="Multiple Login Attempts",
        description="50 failed SSH login attempts from 192.168.1.100"
    )
    print(f"  Alert: {msg_id}")
    
    # Get stats
    print("\n📊 Queue Statistics:")
    stats = queue.get_stats()
    print(f"  Messages published: {stats['messages_published']}")
    for stream, info in stats.get('streams', {}).items():
        print(f"  {stream}: {info['length']} messages")
    
    print("\n✅ Message queue test complete!")
