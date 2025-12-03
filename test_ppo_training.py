#!/usr/bin/env python3
"""Test PPO training functionality."""

import sys
import os

# Add src to path
sys.path.insert(0, '/app/src')

from ai_agent import USE_PPO, create_ppo_agent
from ai_agent.deception_agent import DeceptionState, ActionType
import time

print(f"🔍 USE_PPO: {USE_PPO}")

if USE_PPO:
    try:
        agent = create_ppo_agent()
        print(f"✅ PPO Agent created: {type(agent).__name__}")
        print(f"   Has policy: {hasattr(agent, 'policy')}")
        print(f"   Has store_transition: {hasattr(agent, 'store_transition')}")
        print(f"   Has update: {hasattr(agent, 'update')}")
        print(f"   Training step: {agent.training_step}")
        
        # Test storing transitions
        print("\n📝 Testing transition storage...")
        state = DeceptionState(
            service="ssh",
            command_count=5,
            data_exfil_attempts=2,
            auth_success=True,
            duration_seconds=120.0,
            last_command="ls -la",
            suspicion_score=0.5
        )
        
        for i in range(5):
            action = ActionType.MAINTAIN
            action_idx = [k for k, v in agent.ACTION_MAP.items() if v == action][0]
            log_prob = -1.5  # Dummy value
            value = 0.8  # Dummy value
            reward = 1.0
            agent.store_transition(state, action, reward, log_prob, value, False)
            print(f"   Stored transition {i+1}")
        
        print(f"\n   Memory size: {len(agent.memory.states)}")
        
        # Test training
        if len(agent.memory.states) >= 32:  # Default batch size
            print("\n🎯 Testing training...")
            initial_step = agent.training_step
            agent.update()
            print(f"   Training step: {initial_step} → {agent.training_step}")
            print("   ✅ Training successful!")
        else:
            print(f"\n⚠️  Need more transitions for training (have {len(agent.memory.states)})")
        
        # Test saving
        print("\n💾 Testing checkpoint save...")
        os.makedirs('/tmp/test_models', exist_ok=True)
        agent.save('/tmp/test_models/test_checkpoint.pt')
        
        if os.path.exists('/tmp/test_models/test_checkpoint.pt'):
            size = os.path.getsize('/tmp/test_models/test_checkpoint.pt')
            print(f"   ✅ Checkpoint saved: {size} bytes")
        else:
            print("   ❌ Checkpoint NOT saved")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ PPO not available")
