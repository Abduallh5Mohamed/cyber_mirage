"""
🔥 ULTRA REALISTIC Training Script
يدرّب الموديل على 16 نوع مهاجم من Script Kiddie لـ Equation Group
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from environment.ultra_realistic_env import UltraRealisticHoneynetEnv
import numpy as np


def make_env():
    """إنشاء البيئة"""
    def _init():
        return UltraRealisticHoneynetEnv()
    return _init


def train_ultra_realistic_model():
    """
    تدريب موديل على البيئة الواقعية جداً
    
    Features:
    - 16 نوع مهاجم (Script Kiddie → Equation Group)
    - توزيع واقعي (40% beginners, 35% intermediate, 25% advanced/elite)
    - نظام مكافآت متقدم
    - Detection thresholds متدرجة
    """
    
    print("🔥"*40)
    print("🚀 بدء تدريب ULTRA REALISTIC MODEL")
    print("🔥"*40)
    print()
    
    # إنشاء المسارات
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    models_dir = os.path.join(project_root, "data", "models")
    logs_dir = os.path.join(project_root, "data", "logs", "ultra_realistic")
    
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    
    print(f"📁 Models: {models_dir}")
    print(f"📊 Logs: {logs_dir}")
    print()
    
    # إنشاء البيئة
    print("🏗️  إنشاء البيئة...")
    env = DummyVecEnv([make_env()])
    
    # Hyperparameters محسّنة للواقعية العالية
    print("⚙️  Hyperparameters:")
    hyperparams = {
        "learning_rate": 1.5e-4,      # أقل شوية للاستقرار
        "n_steps": 8192,               # steps أكثر لـ episodes طويلة
        "batch_size": 256,             # batch أكبر
        "n_epochs": 15,                # epochs أكثر
        "gamma": 0.998,                # discount factor عالي (long-term)
        "gae_lambda": 0.96,
        "clip_range": 0.25,
        "ent_coef": 0.005,             # exploration أقل
        "vf_coef": 0.6,
        "max_grad_norm": 0.7,
        "policy_kwargs": dict(
            net_arch=[512, 512, 256, 128]  # شبكة عميقة جداً
        ),
        "verbose": 1,
        "tensorboard_log": logs_dir
    }
    
    for key, value in hyperparams.items():
        if key != "policy_kwargs":
            print(f"   {key}: {value}")
        else:
            print(f"   net_arch: {value['net_arch']}")
    print()
    
    # إنشاء الموديل
    print("🤖 إنشاء PPO Model...")
    model = PPO(
        "MlpPolicy",
        env,
        **hyperparams
    )
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=25000,
        save_path=models_dir,
        name_prefix="ultra_realistic_checkpoint"
    )
    
    # Training
    total_timesteps = 750000  # 750K timesteps للتعامل مع كل الأنواع
    
    print(f"🎯 Training for {total_timesteps:,} timesteps...")
    print(f"⏱️  Expected time: ~30-45 minutes")
    print()
    print("📊 يتم تدريب الموديل على:")
    print("   🟢 40% Beginners    (Script kiddies, Defacers, Phishing)")
    print("   🟡 35% Intermediate (Botnets, Ransomware, Insiders, Financial)")
    print("   🔴 15% Advanced     (APT1, APT32, APT34)")
    print("   ⚫ 10% Elite        (Sandworm, Lazarus, APT28, APT29, Equation)")
    print()
    print("="*80)
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=checkpoint_callback,
            tb_log_name="ultra_realistic_ppo"
        )
        
        # حفظ الموديل النهائي
        final_model_path = os.path.join(models_dir, "ppo_ultra_realistic_final")
        model.save(final_model_path)
        
        print()
        print("="*80)
        print("✅ التدريب انتهى بنجاح!")
        print(f"💾 الموديل محفوظ في: {final_model_path}.zip")
        print()
        
        # اختبار سريع
        print("🧪 اختبار سريع على 5 episodes...")
        test_quick_performance(model, env)
        
        print()
        print("🔥"*40)
        print("🎉 ULTRA REALISTIC MODEL جاهز!")
        print("🔥"*40)
        print()
        print("📝 الخطوات التالية:")
        print("   1. python src/training/test_realistic.py full    - اختبار شامل")
        print("   2. tensorboard --logdir data/logs/ultra_realistic - عرض الإحصائيات")
        print("   3. Integration مع الفريق (7 weeks)")
        
    except KeyboardInterrupt:
        print("\n⚠️  تم إيقاف التدريب!")
        print("💾 حفظ الموديل الحالي...")
        interrupted_path = os.path.join(models_dir, "ppo_ultra_realistic_interrupted")
        model.save(interrupted_path)
        print(f"✅ محفوظ في: {interrupted_path}.zip")


def test_quick_performance(model, env):
    """اختبار سريع على 5 episodes"""
    
    results = []
    
    for episode in range(5):
        obs = env.reset()
        done = False
        episode_reward = 0
        steps = 0
        
        while not done and steps < 500:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            episode_reward += reward[0]
            steps += 1
        
        results.append({
            'episode': episode + 1,
            'reward': episode_reward,
            'steps': steps
        })
        
        print(f"   Episode {episode+1}: Reward={episode_reward:.0f}, Steps={steps}")
    
    avg_reward = np.mean([r['reward'] for r in results])
    avg_steps = np.mean([r['steps'] for r in results])
    
    print(f"\n   📊 Average: Reward={avg_reward:.0f}, Steps={avg_steps:.0f}")


if __name__ == "__main__":
    train_ultra_realistic_model()
