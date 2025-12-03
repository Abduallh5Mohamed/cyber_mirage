#!/usr/bin/env python3
from src.ai_agent import default_agent, USE_PPO

print(f"USE_PPO: {USE_PPO}")
print(f"Agent type: {type(default_agent).__name__}")
print(f"Has policy: {hasattr(default_agent, 'policy')}")
if hasattr(default_agent, 'policy'):
    print(f"Policy type: {type(default_agent.policy).__name__}")
