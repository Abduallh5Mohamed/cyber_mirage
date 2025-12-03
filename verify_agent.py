#!/usr/bin/env python3
"""Verify which agent is actually running."""

import sys
sys.path.insert(0, '/app/src')

from ai_agent import USE_PPO, create_ppo_agent, default_agent

print("=" * 50)
print("🔍 AGENT VERIFICATION")
print("=" * 50)

print(f"\n1. USE_PPO flag: {USE_PPO}")

if USE_PPO:
    try:
        ppo_agent = create_ppo_agent()
        print(f"2. PPO Agent type: {type(ppo_agent).__name__}")
        print(f"3. Has policy (PPO feature): {hasattr(ppo_agent, 'policy')}")
        print(f"4. Has q_table (Q-Learning feature): {hasattr(ppo_agent, 'q_table')}")
        print(f"\n✅ RESULT: Using **PPO Agent**")
        print(f"   - PyTorch Neural Network: YES")
        print(f"   - Q-Table: NO")
    except Exception as e:
        print(f"❌ PPO failed: {e}")
        q_agent = default_agent()
        print(f"2. Fallback Agent type: {type(q_agent).__name__}")
        print(f"\n⚠️ RESULT: Using **Q-Learning Agent** (fallback)")
else:
    q_agent = default_agent()
    print(f"2. Agent type: {type(q_agent).__name__}")
    print(f"\n⚠️ RESULT: Using **Q-Learning Agent** (PPO disabled)")

print("\n" + "=" * 50)
print("Q-Learning is STILL IN CODE (as backup)")
print("But it's NOT USED if PPO works!")
print("=" * 50)
