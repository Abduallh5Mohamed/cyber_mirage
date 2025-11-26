import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from stable_baselines3 import PPO
from environment.base_env import HoneynetEnv
import numpy as np


def test():
    print("🧪 Testing ADVANCED Trained Model...")
    print("="*70)
    
    # Get absolute path to model
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    
    # Try to load advanced model first, fall back to regular
    model_path_advanced = os.path.abspath(os.path.join(project_root, 'data', 'models', 'ppo_honeynet_advanced.zip'))
    model_path_regular = os.path.abspath(os.path.join(project_root, 'data', 'models', 'ppo_honeynet.zip'))
    
    if os.path.exists(model_path_advanced):
        model_path = model_path_advanced
        print("🔥 Loading ADVANCED model...")
    elif os.path.exists(model_path_regular):
        model_path = model_path_regular
        print("📦 Loading regular model...")
    else:
        print("❌ Model not found! Train first.")
        print(f"Looking for: {model_path_advanced}")
        return
    
    model = PPO.load(model_path)
    env = HoneynetEnv()
    
    print(f"✅ Model loaded successfully!")
    print("="*70)
    
    # اختبار 20 episodes بدلاً من 10
    results = []
    data_collected_list = []
    attacker_skills = []
    success_count = 0
    
    for ep in range(20):
        obs, info = env.reset()
        terminated = False
        truncated = False
        total_reward = 0
        steps = 0
        
        print(f"\n🎯 Episode {ep+1}/20")
        print(f"🎲 Attacker Skill: {env.attacker_skill:.1%}")
        attacker_skills.append(env.attacker_skill)
        
        while not (terminated or truncated):
            # استخدام الموديل
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1
            
            if steps % 50 == 0:
                env.render()
        
        results.append(total_reward)
        data_collected_list.append(info['data_collected'])
        
        if truncated and not terminated:
            success_count += 1
            print(f"✅ SUCCESS! Deceived attacker!")
        else:
            print(f"❌ CAUGHT! Attacker detected honeypot!")
            
        print(f"📊 Reward: {total_reward:.2f} | Steps: {steps} | Data: {info['data_collected']}")
    
    # الإحصائيات المحسنة
    print("\n" + "="*70)
    print("📊 ADVANCED RESULTS")
    print("="*70)
    print(f"🎯 Success Rate: {success_count}/20 ({success_count/20*100:.1f}%)")
    print(f"💰 Average Reward: {np.mean(results):.2f} ± {np.std(results):.2f}")
    print(f"🏆 Best Reward: {max(results):.2f}")
    print(f"📉 Worst Reward: {min(results):.2f}")
    print(f"📊 Median Reward: {np.median(results):.2f}")
    print("="*70)
    print(f"📦 Average Data Collected: {np.mean(data_collected_list):.1f}")
    print(f"🏆 Max Data Collected: {max(data_collected_list)}")
    print(f"📊 Total Data Collected: {sum(data_collected_list)}")
    print("="*70)
    print(f"🎲 Average Attacker Skill: {np.mean(attacker_skills):.1%}")
    print(f"🔥 Hardest Attacker: {max(attacker_skills):.1%}")
    print(f"💤 Easiest Attacker: {min(attacker_skills):.1%}")
    print("="*70)
    
    # Performance evaluation
    if success_count >= 15:
        print("🏆 EXCELLENT! World-class honeypot performance!")
    elif success_count >= 12:
        print("🥈 GREAT! Strong deception capabilities!")
    elif success_count >= 10:
        print("🥉 GOOD! Decent performance!")
    else:
        print("⚠️  NEEDS IMPROVEMENT! Consider more training!")
    print("="*70)


if __name__ == "__main__":
    test()