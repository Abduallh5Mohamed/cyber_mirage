"""AI Agent package for Cyber Mirage."""

from .deception_agent import DeceptionAgent, DeceptionState, ActionType, default_agent

# Try to use advanced PPO agent if available
try:
    from .ppo_agent import PPOAgent, create_ppo_agent
    from .ppo_metrics import PPOMetrics, PPOMetricsCollector, get_metrics_collector
    USE_PPO = True
except ImportError:
    USE_PPO = False
    PPOAgent = None
    create_ppo_agent = None
    PPOMetrics = None
    PPOMetricsCollector = None
    get_metrics_collector = None

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

