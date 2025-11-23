"""
🧪 اختبار شامل للبيئة الواقعية
يختبر كل أنواع المهاجمين من الأضعف للأقوى
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from environment.ultra_realistic_env import UltraRealisticHoneynetEnv


def test_all_attackers():
    """اختبار كل 16 نوع مهاجم"""
    
    env = UltraRealisticHoneynetEnv()
    results = {}
    
    print("🔥"*40)
    print("🧪 اختبار شامل لكل أنواع المهاجمين")
    print("🔥"*40)
    print()
    
    for attacker_name in env.ATTACKER_PROFILES.keys():
        print(f"\n{'='*80}")
        print(f"🎯 Testing: {attacker_name}")
        print(f"{'='*80}")
        
        # Force specific attacker
        env.current_attacker = attacker_name
        profile = env.ATTACKER_PROFILES[attacker_name]
        
        env.attacker_skill = profile["sophistication"]
        env.attacker_stealth = profile["stealth"]
        env.attacker_persistence = profile["persistence"]
        env.detection_ease = profile["detection_ease"]
        env.attacker_category = profile["category"]
        env.attacker_origin = profile["origin"]
        env.data_rate_range = profile["data_rate"]
        env.mitre_usage_prob = profile["mitre_usage"]
        
        obs, info = env.reset()
        
        print(f"🏷️  Category: {profile['category'].upper()}")
        print(f"💪 Sophistication: {int(profile['sophistication']*100)}%")
        print(f"👻 Stealth: {int(profile['stealth']*100)}%")
        print(f"📊 Detection Ease: {int(profile['detection_ease']*100)}%")
        print(f"🌍 Origin: {profile['origin']}")
        print()
        
        total_reward = 0
        done = False
        step_count = 0
        max_steps = 500
        
        while not done and step_count < max_steps:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            step_count += 1
            done = terminated or truncated
        
        # جمع الإحصائيات
        results[attacker_name] = {
            'category': profile['category'],
            'skill': profile['sophistication'],
            'steps': step_count,
            'total_reward': total_reward,
            'data_collected': obs[2],
            'suspicion': obs[1],
            'mitre_tactics': len(env.detected_mitre_tactics),
            'zero_days': obs[10],
            'lateral': obs[11],
            'c2': obs[12],
            'detected': info['detected']
        }
        
        print(f"✅ Completed!")
        print(f"   Steps: {step_count}")
        print(f"   Detected: {'Yes' if info['detected'] else 'No'}")
        print(f"   Total Reward: {total_reward:.0f}")
        print(f"   Data: {obs[2]:.0f} MB")
        print(f"   Suspicion: {obs[1]:.1f}%")
        print(f"   MITRE Tactics: {len(env.detected_mitre_tactics)}")
        print(f"   Zero-days: {int(obs[10])}")
    
    # تلخيص النتائج
    print("\n" + "="*80)
    print("📊 SUMMARY - كل النتائج")
    print("="*80)
    print()
    
    # تقسيم حسب الفئة
    categories = {
        'beginner': [],
        'intermediate': [],
        'advanced': [],
        'elite': []
    }
    
    for name, data in results.items():
        categories[data['category']].append((name, data))
    
    for category_name in ['beginner', 'intermediate', 'advanced', 'elite']:
        attackers = categories[category_name]
        if not attackers:
            continue
        
        print(f"\n🎯 {category_name.upper()}")
        print("-"*80)
        
        for name, data in attackers:
            emoji = "🟢" if category_name == "beginner" else \
                    "🟡" if category_name == "intermediate" else \
                    "🔴" if category_name == "advanced" else "⚫"
            
            print(f"{emoji} {name:25} | Skill: {int(data['skill']*100):2}% | "
                  f"Steps: {data['steps']:3} | Reward: {data['total_reward']:8.0f} | "
                  f"Data: {data['data_collected']:5.0f}MB | "
                  f"MITRE: {data['mitre_tactics']}")
    
    # متوسطات
    print("\n" + "="*80)
    print("📈 AVERAGES")
    print("="*80)
    
    for category_name, emoji in [('beginner', '🟢'), ('intermediate', '🟡'), 
                                  ('advanced', '🔴'), ('elite', '⚫')]:
        attackers = categories[category_name]
        if not attackers:
            continue
        
        avg_steps = np.mean([d['steps'] for _, d in attackers])
        avg_reward = np.mean([d['total_reward'] for _, d in attackers])
        avg_data = np.mean([d['data_collected'] for _, d in attackers])
        avg_mitre = np.mean([d['mitre_tactics'] for _, d in attackers])
        detected_count = sum([d['detected'] for _, d in attackers])
        detection_rate = (detected_count / len(attackers)) * 100
        
        print(f"\n{emoji} {category_name.upper()}:")
        print(f"   Avg Steps: {avg_steps:.0f}")
        print(f"   Avg Reward: {avg_reward:.0f}")
        print(f"   Avg Data: {avg_data:.0f} MB")
        print(f"   Avg MITRE: {avg_mitre:.1f}")
        print(f"   Detection Rate: {detection_rate:.0f}%")
    
    print("\n" + "🔥"*40)
    print("✅ اختبار كامل - كل الأنواع شغالة!")
    print("🔥"*40)


def quick_demo():
    """عرض سريع لأنواع مختلفة"""
    
    env = UltraRealisticHoneynetEnv()
    
    # اختبار 3 attackers: مبتدئ، متوسط، نخبة
    test_attackers = [
        "SCRIPT_KIDDIE",      # 20% skill
        "RANSOMWARE_GANG",     # 75% skill
        "EQUATION_GROUP"       # 99% skill
    ]
    
    print("🔥"*40)
    print("🚀 عرض سريع: 3 أنواع مختلفة")
    print("🔥"*40)
    print()
    
    for attacker_name in test_attackers:
        print(f"\n{'='*80}")
        print(f"🎯 {attacker_name}")
        print(f"{'='*80}")
        
        # Force attacker
        env.current_attacker = attacker_name
        profile = env.ATTACKER_PROFILES[attacker_name]
        
        env.attacker_skill = profile["sophistication"]
        env.attacker_stealth = profile["stealth"]
        env.attacker_persistence = profile["persistence"]
        env.detection_ease = profile["detection_ease"]
        env.attacker_category = profile["category"]
        env.attacker_origin = profile["origin"]
        env.data_rate_range = profile["data_rate"]
        env.mitre_usage_prob = profile["mitre_usage"]
        
        obs, info = env.reset()
        
        print(f"💪 Skill: {int(profile['sophistication']*100)}%")
        print(f"🌍 Origin: {profile['origin']}")
        print()
        
        total_reward = 0
        done = False
        step_count = 0
        
        while not done and step_count < 100:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            step_count += 1
            done = terminated or truncated
            
            if step_count % 20 == 0 or done:
                print(f"Step {step_count:3} | Suspicion: {obs[1]:5.1f}% | "
                      f"Data: {obs[2]:5.0f}MB | Reward: {total_reward:8.0f}")
        
        print(f"\n{'✅' if info['detected'] else '⚠️ '} Result: "
              f"{'Detected' if info['detected'] else 'Still active'} "
              f"after {step_count} steps")
        print(f"📊 Final: Data={obs[2]:.0f}MB, MITRE={len(env.detected_mitre_tactics)}, "
              f"Zero-days={int(obs[10])}")
    
    print("\n" + "🔥"*40)
    print("✅ عرض سريع انتهى!")
    print("🔥"*40)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "full":
        test_all_attackers()
    else:
        quick_demo()
        print("\n💡 Tip: للاختبار الكامل، استخدم: python test_realistic.py full")
