"""AI Agent package for Cyber Mirage."""

import logging

logger = logging.getLogger(__name__)

from .deception_agent import DeceptionAgent, DeceptionState, ActionType, default_agent

# Try to use advanced PPO agent if available
try:
    from .ppo_agent import PPOAgent, create_ppo_agent
    from .ppo_metrics import PPOMetrics, PPOMetricsCollector, get_metrics_collector
    USE_PPO = True
    logger.info("✅ PPO modules imported successfully")
except ImportError as e:
    USE_PPO = False
    PPOAgent = None
    create_ppo_agent = None
    PPOMetrics = None
    PPOMetricsCollector = None
    get_metrics_collector = None
    logger.warning(f"⚠️ PPO import failed: {e}")

__all__ = [
    "DeceptionAgent",
    "DeceptionState",
    "ActionType",
    "default_agent",
    "PPOAgent",
    "create_ppo_agent",
    "PPOMetrics",
    "PPOMetricsCollector",
    "get_metrics_collector",
    "USE_PPO",
]

