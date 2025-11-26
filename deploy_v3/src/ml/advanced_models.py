"""
🧠 Advanced ML Features - Ensemble Models & Transfer Learning
"""

import numpy as np
from stable_baselines3 import PPO, A2C, SAC
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
import torch
import torch.nn as nn
from typing import List, Dict, Tuple
import os


class EnsembleModel:
    """
    Ensemble of multiple RL models for better performance
    Combines predictions from PPO, A2C, and SAC
    """
    
    def __init__(self, env, models_dir: str = "data/models/ensemble"):
        self.env = env
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
        self.models = {}
        self.weights = {}
    
    def train_ensemble(self, timesteps: int = 1_000_000):
        """Train multiple models"""
        print("🔥 Training Ensemble Models...")
        
        # PPO - Best for discrete actions
        print("\n1️⃣ Training PPO...")
        self.models['ppo'] = PPO(
            "MlpPolicy",
            self.env,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            verbose=1,
            tensorboard_log="data/logs/ensemble_ppo"
        )
        self.models['ppo'].learn(total_timesteps=timesteps)
        self.models['ppo'].save(f"{self.models_dir}/ppo_model")
        
        # A2C - Faster training
        print("\n2️⃣ Training A2C...")
        self.models['a2c'] = A2C(
            "MlpPolicy",
            self.env,
            learning_rate=7e-4,
            n_steps=5,
            gamma=0.99,
            gae_lambda=1.0,
            ent_coef=0.01,
            verbose=1,
            tensorboard_log="data/logs/ensemble_a2c"
        )
        self.models['a2c'].learn(total_timesteps=timesteps // 2)
        self.models['a2c'].save(f"{self.models_dir}/a2c_model")
        
        print("\n✅ Ensemble training complete!")
    
    def load_ensemble(self):
        """Load pre-trained ensemble"""
        print("📂 Loading ensemble models...")
        
        if os.path.exists(f"{self.models_dir}/ppo_model.zip"):
            self.models['ppo'] = PPO.load(f"{self.models_dir}/ppo_model", env=self.env)
            print("✅ PPO loaded")
        
        if os.path.exists(f"{self.models_dir}/a2c_model.zip"):
            self.models['a2c'] = A2C.load(f"{self.models_dir}/a2c_model", env=self.env)
            print("✅ A2C loaded")
        
        # Initialize weights (can be learned)
        self.weights = {
            'ppo': 0.6,  # PPO gets most weight
            'a2c': 0.4
        }
    
    def predict(self, obs, deterministic: bool = True):
        """
        Ensemble prediction - weighted voting
        """
        if not self.models:
            raise ValueError("No models loaded. Call load_ensemble() first.")
        
        predictions = {}
        
        for name, model in self.models.items():
            action, _ = model.predict(obs, deterministic=deterministic)
            predictions[name] = action
        
        # Weighted voting
        action_votes = {}
        for name, action in predictions.items():
            if isinstance(action, np.ndarray):
                action = action.item()
            
            weight = self.weights.get(name, 1.0)
            action_votes[action] = action_votes.get(action, 0) + weight
        
        # Return action with highest weighted vote
        best_action = max(action_votes.items(), key=lambda x: x[1])[0]
        return best_action, None
    
    def evaluate(self, n_episodes: int = 10) -> Dict[str, float]:
        """Evaluate each model in ensemble"""
        results = {}
        
        for name, model in self.models.items():
            episode_rewards = []
            
            for _ in range(n_episodes):
                obs, _ = self.env.reset()
                done = False
                total_reward = 0
                
                while not done:
                    action, _ = model.predict(obs, deterministic=True)
                    obs, reward, terminated, truncated, _ = self.env.step(action)
                    total_reward += reward
                    done = terminated or truncated
                
                episode_rewards.append(total_reward)
            
            results[name] = {
                'mean_reward': np.mean(episode_rewards),
                'std_reward': np.std(episode_rewards)
            }
        
        return results


class TransferLearningModel:
    """
    Transfer learning from base environment to comprehensive environment
    """
    
    def __init__(self, source_model_path: str, target_env):
        self.source_model_path = source_model_path
        self.target_env = target_env
        self.model = None
    
    def load_and_adapt(self):
        """Load source model and adapt to target environment"""
        print("🔄 Loading source model...")
        
        # Load base model
        base_model = PPO.load(self.source_model_path)
        
        # Create new model with same architecture but new environment
        print("🎯 Adapting to new environment...")
        self.model = PPO(
            "MlpPolicy",
            self.target_env,
            learning_rate=1e-4,  # Lower LR for fine-tuning
            policy_kwargs=dict(
                net_arch=dict(pi=[512, 512, 256, 128], vf=[512, 512, 256, 128])
            ),
            verbose=1
        )
        
        # Copy weights from base model (where dimensions match)
        try:
            source_params = base_model.policy.state_dict()
            target_params = self.model.policy.state_dict()
            
            # Copy matching layers
            for key in target_params.keys():
                if key in source_params and source_params[key].shape == target_params[key].shape:
                    target_params[key] = source_params[key]
                    print(f"✅ Transferred: {key}")
            
            self.model.policy.load_state_dict(target_params)
            print("✅ Transfer learning complete!")
            
        except Exception as e:
            print(f"⚠️ Partial transfer: {e}")
    
    def fine_tune(self, timesteps: int = 500_000):
        """Fine-tune on target environment"""
        print("🎓 Fine-tuning model...")
        
        self.model.learn(
            total_timesteps=timesteps,
            callback=CheckpointCallback(
                save_freq=50000,
                save_path="data/models/transfer/",
                name_prefix="finetuned"
            )
        )
        
        print("✅ Fine-tuning complete!")


class CurriculumLearning:
    """
    Curriculum learning - train on increasingly difficult attackers
    """
    
    def __init__(self, env):
        self.env = env
        self.stages = [
            {'name': 'Easy', 'max_skill': 0.3, 'timesteps': 200_000},
            {'name': 'Medium', 'max_skill': 0.6, 'timesteps': 300_000},
            {'name': 'Hard', 'max_skill': 0.8, 'timesteps': 300_000},
            {'name': 'Expert', 'max_skill': 1.0, 'timesteps': 200_000}
        ]
        self.model = None
    
    def train_curriculum(self):
        """Train with curriculum learning"""
        print("📚 Starting Curriculum Learning...")
        
        self.model = PPO(
            "MlpPolicy",
            self.env,
            policy_kwargs=dict(
                net_arch=dict(pi=[512, 512, 256, 128], vf=[512, 512, 256, 128])
            ),
            learning_rate=3e-4,
            verbose=1
        )
        
        for stage in self.stages:
            print(f"\n{'='*50}")
            print(f"📖 Stage: {stage['name']} (Max Skill: {stage['max_skill']*100}%)")
            print(f"{'='*50}")
            
            # Filter attackers by skill level
            self._set_difficulty(stage['max_skill'])
            
            # Train
            self.model.learn(
                total_timesteps=stage['timesteps'],
                reset_num_timesteps=False  # Continue training
            )
            
            # Save checkpoint
            self.model.save(f"data/models/curriculum/stage_{stage['name'].lower()}")
            print(f"✅ Stage {stage['name']} complete!")
        
        print("\n🎓 Curriculum Learning Complete!")
        self.model.save("data/models/curriculum/final_model")
    
    def _set_difficulty(self, max_skill: float):
        """Filter attackers by difficulty"""
        # Filter ATTACKER_PROFILES in environment
        original_profiles = self.env.ATTACKER_PROFILES.copy()
        filtered_profiles = {
            name: profile 
            for name, profile in original_profiles.items()
            if profile['skill'] <= max_skill
        }
        self.env.ATTACKER_PROFILES = filtered_profiles
        self.env._calculate_weights()


class AdvancedFeatureExtractor(nn.Module):
    """
    Custom feature extractor with attention mechanism
    """
    
    def __init__(self, observation_dim: int):
        super().__init__()
        
        # Attention layer
        self.attention = nn.MultiheadAttention(
            embed_dim=observation_dim,
            num_heads=4,
            batch_first=True
        )
        
        # Feature layers
        self.features = nn.Sequential(
            nn.Linear(observation_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64)
        )
    
    def forward(self, x):
        # Add batch dimension for attention
        x_unsqueezed = x.unsqueeze(1)
        
        # Apply attention
        attn_output, _ = self.attention(x_unsqueezed, x_unsqueezed, x_unsqueezed)
        attn_output = attn_output.squeeze(1)
        
        # Extract features
        features = self.features(attn_output)
        
        return features


# Example usage
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from environment.comprehensive_env import ComprehensiveHoneynetEnv
    
    print("🧠 Advanced ML Features Demo")
    print("="*50)
    
    # Create environment
    env = ComprehensiveHoneynetEnv()
    
    # 1. Ensemble Learning
    print("\n1️⃣ Ensemble Learning")
    ensemble = EnsembleModel(env)
    # ensemble.train_ensemble(timesteps=100_000)  # Uncomment to train
    
    # 2. Transfer Learning
    print("\n2️⃣ Transfer Learning")
    if os.path.exists("data/models/ppo_honeypot_final.zip"):
        transfer = TransferLearningModel(
            "data/models/ppo_honeypot_final.zip",
            env
        )
        # transfer.load_and_adapt()
        # transfer.fine_tune(timesteps=100_000)
    
    # 3. Curriculum Learning
    print("\n3️⃣ Curriculum Learning")
    curriculum = CurriculumLearning(env)
    # curriculum.train_curriculum()  # Uncomment to train
    
    print("\n✅ All advanced features available!")
