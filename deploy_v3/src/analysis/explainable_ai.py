"""
🔬 Explainable AI (XAI) - Understand Model Decisions
SHAP values, attention visualization, feature importance
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import torch
import torch.nn.functional as F


class ExplainableAI:
    """
    Explain model predictions using various techniques
    """
    
    def __init__(self, model, env):
        self.model = model
        self.env = env
        self.feature_names = self._get_feature_names()
    
    def _get_feature_names(self) -> List[str]:
        """Get human-readable feature names"""
        return [
            "Time Step",
            "Suspicion Level",
            "Data Collected",
            "False Trails",
            "Honeytokens",
            "Decoy Services",
            "Fake Vulnerabilities",
            "Network Behavior",
            "File System Activity",
            "Process Monitoring",
            "Zero-Days Used",
            "Attacker Skill",
            "Detection Risk",
            "Data Collection Rate",
            "Persistence Score"
        ]
    
    def explain_action(self, obs: np.ndarray) -> Dict:
        """
        Explain why the model chose a specific action
        """
        # Get model prediction
        action, _ = self.model.predict(obs, deterministic=True)
        
        # Get action probabilities
        with torch.no_grad():
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0)
            
            # Get policy network output
            features = self.model.policy.extract_features(obs_tensor)
            action_logits = self.model.policy.action_net(features)
            action_probs = F.softmax(action_logits, dim=-1).numpy()[0]
        
        # Calculate feature importance (gradient-based)
        obs_tensor.requires_grad = True
        features = self.model.policy.extract_features(obs_tensor)
        action_logits = self.model.policy.action_net(features)
        
        # Get gradient for chosen action
        action_logits[0, action].backward()
        feature_importance = torch.abs(obs_tensor.grad[0]).numpy()
        
        # Normalize importance
        feature_importance = feature_importance / (feature_importance.sum() + 1e-8)
        
        return {
            'chosen_action': int(action),
            'action_probabilities': {
                f'action_{i}': float(prob) 
                for i, prob in enumerate(action_probs)
            },
            'feature_importance': {
                name: float(importance)
                for name, importance in zip(self.feature_names, feature_importance)
            },
            'top_features': sorted(
                zip(self.feature_names, feature_importance),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def visualize_decision(self, obs: np.ndarray, save_path: str = None):
        """
        Create visualization of model decision
        """
        explanation = self.explain_action(obs)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('🔬 Model Decision Explanation', fontsize=16, fontweight='bold')
        
        # 1. Feature Importance
        ax1 = axes[0, 0]
        importance = explanation['feature_importance']
        features = list(importance.keys())
        values = list(importance.values())
        
        colors = ['#ef4444' if v > 0.1 else '#3b82f6' for v in values]
        ax1.barh(features, values, color=colors)
        ax1.set_xlabel('Importance Score')
        ax1.set_title('Feature Importance')
        ax1.grid(axis='x', alpha=0.3)
        
        # 2. Action Probabilities
        ax2 = axes[0, 1]
        action_probs = explanation['action_probabilities']
        actions = list(action_probs.keys())
        probs = list(action_probs.values())
        
        colors = ['#10b981' if i == explanation['chosen_action'] else '#6b7280' 
                  for i in range(len(probs))]
        ax2.bar(range(len(actions)), probs, color=colors)
        ax2.set_xlabel('Action')
        ax2.set_ylabel('Probability')
        ax2.set_title('Action Probabilities (Green = Chosen)')
        ax2.set_xticks(range(0, len(actions), 5))
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Top Features
        ax3 = axes[1, 0]
        top_features = explanation['top_features']
        top_names = [f[0] for f in top_features]
        top_values = [f[1] for f in top_features]
        
        ax3.barh(top_names, top_values, color='#f59e0b')
        ax3.set_xlabel('Importance')
        ax3.set_title('Top 5 Influential Features')
        ax3.grid(axis='x', alpha=0.3)
        
        # 4. Observation State
        ax4 = axes[1, 1]
        normalized_obs = (obs - obs.min()) / (obs.max() - obs.min() + 1e-8)
        
        im = ax4.imshow(normalized_obs.reshape(-1, 1), cmap='viridis', aspect='auto')
        ax4.set_yticks(range(len(self.feature_names)))
        ax4.set_yticklabels(self.feature_names)
        ax4.set_xticks([])
        ax4.set_title('Current State (Normalized)')
        plt.colorbar(im, ax=ax4)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ Saved visualization to {save_path}")
        
        return fig
    
    def analyze_episode(self, n_steps: int = 100) -> Dict:
        """
        Analyze full episode and track decision patterns
        """
        obs, info = self.env.reset()
        
        episode_data = {
            'actions': [],
            'rewards': [],
            'feature_importance_history': [],
            'suspicion_history': [],
            'data_collected_history': []
        }
        
        for step in range(n_steps):
            # Get explanation
            explanation = self.explain_action(obs)
            
            # Take action
            action = explanation['chosen_action']
            obs, reward, terminated, truncated, info = self.env.step(action)
            
            # Record data
            episode_data['actions'].append(action)
            episode_data['rewards'].append(reward)
            episode_data['feature_importance_history'].append(
                explanation['feature_importance']
            )
            episode_data['suspicion_history'].append(obs[1])
            episode_data['data_collected_history'].append(obs[2])
            
            if terminated or truncated:
                break
        
        return episode_data
    
    def plot_episode_analysis(self, episode_data: Dict, save_path: str = None):
        """
        Visualize episode analysis
        """
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        fig.suptitle('📊 Episode Analysis', fontsize=16, fontweight='bold')
        
        steps = range(len(episode_data['actions']))
        
        # 1. Rewards over time
        ax1 = axes[0]
        ax1.plot(steps, episode_data['rewards'], marker='o', linewidth=2)
        ax1.set_xlabel('Step')
        ax1.set_ylabel('Reward')
        ax1.set_title('Rewards Over Time')
        ax1.grid(alpha=0.3)
        ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        
        # 2. Suspicion and Data Collection
        ax2 = axes[1]
        ax2_twin = ax2.twinx()
        
        ax2.plot(steps, episode_data['suspicion_history'], 
                label='Suspicion', color='#ef4444', linewidth=2)
        ax2_twin.plot(steps, episode_data['data_collected_history'], 
                     label='Data Collected', color='#10b981', linewidth=2)
        
        ax2.set_xlabel('Step')
        ax2.set_ylabel('Suspicion Level', color='#ef4444')
        ax2_twin.set_ylabel('Data Collected (MB)', color='#10b981')
        ax2.set_title('Suspicion vs Data Collection')
        ax2.grid(alpha=0.3)
        
        # 3. Feature importance heatmap
        ax3 = axes[2]
        
        # Create heatmap data
        importance_matrix = []
        for hist in episode_data['feature_importance_history']:
            importance_matrix.append(list(hist.values()))
        
        importance_matrix = np.array(importance_matrix).T
        
        im = ax3.imshow(importance_matrix, aspect='auto', cmap='YlOrRd')
        ax3.set_xlabel('Step')
        ax3.set_ylabel('Feature')
        ax3.set_yticks(range(len(self.feature_names)))
        ax3.set_yticklabels(self.feature_names)
        ax3.set_title('Feature Importance Over Time')
        plt.colorbar(im, ax=ax3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ Saved episode analysis to {save_path}")
        
        return fig


# Example usage
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from environment.comprehensive_env import ComprehensiveHoneynetEnv
    from stable_baselines3 import PPO
    
    print("🔬 Explainable AI Demo")
    print("="*50)
    
    # Load environment and model
    env = ComprehensiveHoneynetEnv()
    
    # Check if model exists
    model_path = "data/models/ppo_comprehensive_final.zip"
    if os.path.exists(model_path):
        print(f"📂 Loading model from {model_path}")
        model = PPO.load(model_path, env=env)
        
        # Create explainer
        xai = ExplainableAI(model, env)
        
        # Reset environment
        obs, info = env.reset()
        
        print(f"\n🎯 Attacker: {info['attacker']}")
        print(f"💪 Skill: {info['skill']*100:.0f}%")
        print(f"🌍 Origin: {info['origin']}")
        
        # Explain decision
        print("\n📊 Explaining first action...")
        explanation = xai.explain_action(obs)
        
        print(f"\n✅ Chosen Action: {explanation['chosen_action']}")
        print(f"\n🔝 Top 5 Influential Features:")
        for name, importance in explanation['top_features']:
            print(f"  - {name}: {importance:.4f}")
        
        # Visualize
        print("\n🎨 Creating visualization...")
        xai.visualize_decision(obs, save_path="data/logs/decision_explanation.png")
        
        # Analyze episode
        print("\n📈 Analyzing full episode...")
        episode_data = xai.analyze_episode(n_steps=50)
        xai.plot_episode_analysis(episode_data, save_path="data/logs/episode_analysis.png")
        
        print("\n✅ XAI analysis complete!")
        
    else:
        print(f"⚠️  Model not found at {model_path}")
        print("Train a model first using train.py")
