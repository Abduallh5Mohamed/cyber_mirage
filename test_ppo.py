#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/src')

try:
    import torch
    print(f"✅ PyTorch {torch.__version__} imported successfully")
except Exception as e:
    print(f"❌ PyTorch import failed: {e}")
    sys.exit(1)

try:
    import ai_agent
    print(f"✅ ai_agent module imported successfully")
    print(f"USE_PPO = {ai_agent.USE_PPO}")
    
    if ai_agent.USE_PPO:
        print("✅ PPO is ENABLED")
        try:
            from ai_agent import create_ppo_agent
            agent = create_ppo_agent()
            print(f"✅ PPO agent created successfully: {type(agent)}")
        except Exception as e:
            print(f"❌ PPO agent creation failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ PPO is DISABLED (fallback to Q-Learning)")
        print("Trying direct import:")
        try:
            from ai_agent.ppo_agent import PPOAgent
            print("✅ PPOAgent class import successful")
        except Exception as e:
            print(f"❌ PPOAgent import failed: {e}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"❌ ai_agent import failed: {e}")
    import traceback
    traceback.print_exc()
