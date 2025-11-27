"""
📦 Data Pipeline Package
Cyber Mirage - Role 7: Data Pipeline & Orchestration

Provides message queue, event streaming, and data orchestration.
"""

from .message_queue import (
    MessageQueueManager,
    Message,
    StreamName,
    MessagePriority,
    ConsumerGroup,
    get_queue
)

__all__ = [
    'MessageQueueManager',
    'Message',
    'StreamName',
    'MessagePriority',
    'ConsumerGroup',
    'get_queue'
]
