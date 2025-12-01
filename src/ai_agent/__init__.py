"""AI Agent package for Cyber Mirage."""

from .deception_agent import DeceptionAgent, DeceptionState, ActionType, default_agent

# Try to use advanced PPO agent if available
try:
    from .ppo_agent import PPOAgent, create_ppo_agent
    USE_PPO = True
except ImportError:
    USE_PPO = False
    PPOAgent = None
    create_ppo_agent = None

__all__ = [
    "DeceptionAgent",
    "DeceptionState",
    "ActionType",
    "default_agent",
    "PPOAgent",
    "create_ppo_agent",
    "USE_PPO",
]

