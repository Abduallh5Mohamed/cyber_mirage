import sys
import os

# إضافة المسار
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from environment.base_env import HoneynetEnv


def train():
    print("🚀 Starting ADVANCED Training...")
    print("="*70)
    
    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    logs_dir = os.path.abspath(os.path.join(project_root, 'data', 'logs'))
    models_dir = os.path.abspath(os.path.join(project_root, 'data', 'models'))
    
    # إنشاء البيئة
    env = HoneynetEnv()
    check_env(env)
    print("✅ Advanced Environment is valid!")
    print(f"📊 State Space: {env.observation_space.shape[0]} dimensions")
    print(f"🎮 Action Space: {env.action_space.n} actions")
    print("="*70)
    
    # إنشاء الموديل بـ hyperparameters محسنة
    print("🤖 Creating ADVANCED PPO model...")
    print("⚙️  Hyperparameters:")
    print("   • Learning Rate: 2e-4")
    print("   • Steps per Update: 4096")
    print("   • Batch Size: 128")
    print("   • Epochs: 15")
    print("   • Gamma (Discount): 0.995")
    print("   • GAE Lambda: 0.98")
    print("   • Clip Range: 0.2")
    print("   • Value Function Coef: 0.5")
    print("   • Entropy Coef: 0.01")
    print("="*70)
    
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=2e-4,          # Optimized learning rate
        n_steps=4096,                # More steps for better sampling
        batch_size=128,              # Larger batch for stability
        n_epochs=15,                 # More epochs for better learning
        gamma=0.995,                 # High discount for long-term rewards
        gae_lambda=0.98,            # GAE for advantage estimation
        clip_range=0.2,              # PPO clipping
        clip_range_vf=None,
        ent_coef=0.01,              # Encourage exploration
        vf_coef=0.5,                # Value function coefficient
        max_grad_norm=0.5,          # Gradient clipping
        verbose=1,
        tensorboard_log=logs_dir,
        policy_kwargs=dict(
            net_arch=[dict(pi=[256, 256, 128], vf=[256, 256, 128])]  # Deeper network!
        )
    )
    
    # التدريب
    print("🎓 Training ADVANCED model... (This takes ~10-15 minutes)")
    print("🔥 Training for 200,000 timesteps!")
    print("="*70)
    model.learn(total_timesteps=200000, progress_bar=True)
    
    # حفظ الموديل
    print("\n💾 Saving ADVANCED model...")
    os.makedirs(models_dir, exist_ok=True)
    model.save(os.path.join(models_dir, "ppo_honeynet_advanced"))
    
    print("✨ ADVANCED Training completed!")
    print("="*70)
    print("📁 Model saved at: data/models/ppo_honeynet_advanced.zip")
    print("📊 TensorBoard logs at: data/logs/")
    print("="*70)
    print("🎯 Next steps:")
    print("   1. View training graphs: tensorboard --logdir=data/logs")
    print("   2. Test the model: python src/training/test.py")
    print("="*70)


if __name__ == "__main__":
    train()