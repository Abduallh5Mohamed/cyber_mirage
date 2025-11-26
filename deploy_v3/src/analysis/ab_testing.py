"""
🧪 A/B Testing Framework for Model Comparison
Compare different models, strategies, and hyperparameters
"""

import numpy as np
from typing import Dict, List, Tuple
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Experiment:
    """Experiment configuration"""
    name: str
    model_path: str
    description: str
    hyperparameters: Dict


class ABTestingFramework:
    """
    A/B testing for comparing different models and strategies
    """
    
    def __init__(self, env):
        self.env = env
        self.experiments = {}
        self.results = {}
    
    def add_experiment(self, experiment: Experiment):
        """Add experiment to compare"""
        self.experiments[experiment.name] = experiment
        print(f"✅ Added experiment: {experiment.name}")
    
    def run_experiment(
        self, 
        experiment_name: str,
        model,
        n_episodes: int = 50,
        verbose: bool = True
    ) -> Dict:
        """
        Run single experiment
        """
        if verbose:
            print(f"\n🧪 Running experiment: {experiment_name}")
            print(f"Episodes: {n_episodes}")
        
        episode_rewards = []
        episode_lengths = []
        detection_rates = []
        data_collected = []
        attacker_skills = []
        
        for episode in range(n_episodes):
            obs, info = self.env.reset()
            done = False
            total_reward = 0
            steps = 0
            
            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = self.env.step(action)
                total_reward += reward
                steps += 1
                done = terminated or truncated
            
            episode_rewards.append(total_reward)
            episode_lengths.append(steps)
            detection_rates.append(1 if info['detected'] else 0)
            data_collected.append(obs[2])
            attacker_skills.append(info['skill'])
            
            if verbose and (episode + 1) % 10 == 0:
                print(f"  Episode {episode + 1}/{n_episodes}: "
                      f"Reward={total_reward:.0f}, Steps={steps}")
        
        results = {
            'experiment_name': experiment_name,
            'n_episodes': n_episodes,
            'episode_rewards': episode_rewards,
            'episode_lengths': episode_lengths,
            'detection_rates': detection_rates,
            'data_collected': data_collected,
            'attacker_skills': attacker_skills,
            'statistics': {
                'mean_reward': np.mean(episode_rewards),
                'std_reward': np.std(episode_rewards),
                'median_reward': np.median(episode_rewards),
                'mean_length': np.mean(episode_lengths),
                'detection_rate': np.mean(detection_rates) * 100,
                'mean_data': np.mean(data_collected),
                'mean_skill': np.mean(attacker_skills) * 100
            }
        }
        
        self.results[experiment_name] = results
        
        if verbose:
            print(f"\n📊 Results for {experiment_name}:")
            print(f"  Mean Reward: {results['statistics']['mean_reward']:.2f} "
                  f"± {results['statistics']['std_reward']:.2f}")
            print(f"  Detection Rate: {results['statistics']['detection_rate']:.1f}%")
            print(f"  Avg Episode Length: {results['statistics']['mean_length']:.0f} steps")
        
        return results
    
    def compare_experiments(self) -> pd.DataFrame:
        """
        Compare all experiments statistically
        """
        if len(self.results) < 2:
            print("⚠️  Need at least 2 experiments to compare")
            return None
        
        print("\n📊 Statistical Comparison")
        print("="*80)
        
        # Create comparison dataframe
        comparison_data = []
        
        for name, results in self.results.items():
            comparison_data.append({
                'Experiment': name,
                'Mean Reward': results['statistics']['mean_reward'],
                'Std Reward': results['statistics']['std_reward'],
                'Detection Rate': results['statistics']['detection_rate'],
                'Avg Length': results['statistics']['mean_length'],
                'Mean Data': results['statistics']['mean_data']
            })
        
        df = pd.DataFrame(comparison_data)
        print(df.to_string(index=False))
        
        # Perform t-tests between experiments
        print("\n🔬 Statistical Tests (t-test p-values):")
        print("-"*80)
        
        experiment_names = list(self.results.keys())
        
        for i, exp1 in enumerate(experiment_names):
            for exp2 in experiment_names[i+1:]:
                rewards1 = self.results[exp1]['episode_rewards']
                rewards2 = self.results[exp2]['episode_rewards']
                
                t_stat, p_value = stats.ttest_ind(rewards1, rewards2)
                
                significant = "✅ SIGNIFICANT" if p_value < 0.05 else "❌ Not significant"
                print(f"{exp1} vs {exp2}:")
                print(f"  p-value: {p_value:.4f} - {significant}")
        
        return df
    
    def visualize_comparison(self, save_path: str = None):
        """
        Create comprehensive visualization of all experiments
        """
        if not self.results:
            print("⚠️  No results to visualize")
            return
        
        n_experiments = len(self.results)
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('🧪 A/B Testing Results', fontsize=16, fontweight='bold')
        
        experiment_names = list(self.results.keys())
        colors = sns.color_palette("husl", n_experiments)
        
        # 1. Mean Reward Comparison
        ax1 = axes[0, 0]
        means = [self.results[exp]['statistics']['mean_reward'] for exp in experiment_names]
        stds = [self.results[exp]['statistics']['std_reward'] for exp in experiment_names]
        
        x_pos = np.arange(len(experiment_names))
        ax1.bar(x_pos, means, yerr=stds, color=colors, alpha=0.7, capsize=10)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(experiment_names, rotation=45, ha='right')
        ax1.set_ylabel('Mean Reward')
        ax1.set_title('Mean Reward Comparison')
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Detection Rate Comparison
        ax2 = axes[0, 1]
        detection_rates = [
            self.results[exp]['statistics']['detection_rate'] 
            for exp in experiment_names
        ]
        ax2.bar(x_pos, detection_rates, color=colors, alpha=0.7)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(experiment_names, rotation=45, ha='right')
        ax2.set_ylabel('Detection Rate (%)')
        ax2.set_title('Detection Rate Comparison')
        ax2.grid(axis='y', alpha=0.3)
        ax2.axhline(y=50, color='r', linestyle='--', alpha=0.5, label='50% baseline')
        ax2.legend()
        
        # 3. Episode Length Comparison
        ax3 = axes[0, 2]
        lengths = [
            self.results[exp]['statistics']['mean_length'] 
            for exp in experiment_names
        ]
        ax3.bar(x_pos, lengths, color=colors, alpha=0.7)
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(experiment_names, rotation=45, ha='right')
        ax3.set_ylabel('Average Steps')
        ax3.set_title('Episode Length Comparison')
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Reward Distribution (Box Plot)
        ax4 = axes[1, 0]
        reward_data = [
            self.results[exp]['episode_rewards'] 
            for exp in experiment_names
        ]
        box = ax4.boxplot(reward_data, labels=experiment_names, patch_artist=True)
        for patch, color in zip(box['boxes'], colors):
            patch.set_facecolor(color)
        ax4.set_xticklabels(experiment_names, rotation=45, ha='right')
        ax4.set_ylabel('Reward Distribution')
        ax4.set_title('Reward Distribution (Box Plot)')
        ax4.grid(axis='y', alpha=0.3)
        
        # 5. Cumulative Rewards
        ax5 = axes[1, 1]
        for i, exp in enumerate(experiment_names):
            rewards = self.results[exp]['episode_rewards']
            cumulative = np.cumsum(rewards)
            ax5.plot(cumulative, label=exp, color=colors[i], linewidth=2)
        ax5.set_xlabel('Episode')
        ax5.set_ylabel('Cumulative Reward')
        ax5.set_title('Cumulative Rewards Over Episodes')
        ax5.legend()
        ax5.grid(alpha=0.3)
        
        # 6. Learning Curves (Moving Average)
        ax6 = axes[1, 2]
        window = 5
        for i, exp in enumerate(experiment_names):
            rewards = self.results[exp]['episode_rewards']
            moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
            ax6.plot(moving_avg, label=exp, color=colors[i], linewidth=2)
        ax6.set_xlabel('Episode')
        ax6.set_ylabel(f'Reward (MA-{window})')
        ax6.set_title('Learning Curves (Moving Average)')
        ax6.legend()
        ax6.grid(alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ Saved visualization to {save_path}")
        
        return fig
    
    def generate_report(self, save_path: str = None) -> str:
        """
        Generate detailed text report
        """
        report = []
        report.append("="*80)
        report.append("🧪 A/B TESTING REPORT")
        report.append("="*80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Experiments: {len(self.results)}")
        report.append("")
        
        # Find best experiment
        best_exp = max(
            self.results.items(),
            key=lambda x: x[1]['statistics']['mean_reward']
        )
        
        report.append("🏆 WINNER:")
        report.append(f"  {best_exp[0]}")
        report.append(f"  Mean Reward: {best_exp[1]['statistics']['mean_reward']:.2f}")
        report.append(f"  Detection Rate: {best_exp[1]['statistics']['detection_rate']:.1f}%")
        report.append("")
        
        # Detailed results for each experiment
        for name, results in self.results.items():
            report.append("-"*80)
            report.append(f"📊 {name}")
            report.append("-"*80)
            
            stats = results['statistics']
            report.append(f"  Mean Reward:     {stats['mean_reward']:.2f} ± {stats['std_reward']:.2f}")
            report.append(f"  Median Reward:   {stats['median_reward']:.2f}")
            report.append(f"  Detection Rate:  {stats['detection_rate']:.1f}%")
            report.append(f"  Avg Episode Len: {stats['mean_length']:.0f} steps")
            report.append(f"  Mean Data:       {stats['mean_data']:.2f} MB")
            report.append(f"  Avg Skill:       {stats['mean_skill']:.1f}%")
            report.append("")
        
        report_text = "\n".join(report)
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"✅ Saved report to {save_path}")
        
        return report_text


# Example usage
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from environment.comprehensive_env import ComprehensiveHoneynetEnv
    from stable_baselines3 import PPO
    
    print("🧪 A/B Testing Framework Demo")
    print("="*80)
    
    # Create environment
    env = ComprehensiveHoneynetEnv()
    
    # Initialize framework
    framework = ABTestingFramework(env)
    
    # Check if models exist
    model_path = "data/models/ppo_comprehensive_final.zip"
    if os.path.exists(model_path):
        print(f"\n📂 Loading model from {model_path}")
        model = PPO.load(model_path, env=env)
        
        # Run experiments
        print("\n🧪 Running experiments...")
        framework.run_experiment("Baseline_Model", model, n_episodes=20)
        
        # Compare results
        df = framework.compare_experiments()
        
        # Visualize
        framework.visualize_comparison(save_path="data/logs/ab_testing_results.png")
        
        # Generate report
        report = framework.generate_report(save_path="data/logs/ab_testing_report.txt")
        print("\n" + report)
        
    else:
        print(f"⚠️  Model not found at {model_path}")
