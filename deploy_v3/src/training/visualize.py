"""
🎨 Advanced Visualization for Cyber Mirage Training Results
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from stable_baselines3 import PPO
from environment.base_env import HoneynetEnv
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict


def visualize_performance():
    """Comprehensive performance visualization"""
    
    print("🎨 Advanced Visualization Suite")
    print("="*70)
    
    # Load model
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    model_path = os.path.abspath(os.path.join(project_root, 'data', 'models', 'ppo_honeynet_advanced.zip'))
    
    if not os.path.exists(model_path):
        print("❌ Advanced model not found. Using regular model...")
        model_path = os.path.abspath(os.path.join(project_root, 'data', 'models', 'ppo_honeynet.zip'))
        if not os.path.exists(model_path):
            print("❌ No model found! Train first.")
            return
    
    model = PPO.load(model_path)
    env = HoneynetEnv()
    
    # Run multiple episodes
    n_episodes = 50
    print(f"🎮 Running {n_episodes} episodes for analysis...")
    
    results = {
        'rewards': [],
        'steps': [],
        'data_collected': [],
        'suspicions': [],
        'attacker_skills': [],
        'interaction_depths': [],
        'success': [],
        'action_frequencies': defaultdict(int)
    }
    
    for ep in range(n_episodes):
        obs, info = env.reset()
        done = False
        total_reward = 0
        steps = 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            total_reward += reward
            steps += 1
            results['action_frequencies'][action] += 1
        
        results['rewards'].append(total_reward)
        results['steps'].append(steps)
        results['data_collected'].append(info['data_collected'])
        results['suspicions'].append(info['suspicion'])
        results['attacker_skills'].append(info['attacker_skill'])
        results['interaction_depths'].append(info['interaction_depth'])
        results['success'].append(1 if truncated and not terminated else 0)
        
        if (ep + 1) % 10 == 0:
            print(f"✅ Completed {ep + 1}/{n_episodes} episodes")
    
    # Create visualization
    print("\n📊 Creating visualizations...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('🔥 Cyber Mirage - Advanced Performance Analysis 🔥', 
                 fontsize=16, fontweight='bold')
    
    # 1. Reward Distribution
    ax = axes[0, 0]
    ax.hist(results['rewards'], bins=20, color='#2ecc71', alpha=0.7, edgecolor='black')
    ax.axvline(np.mean(results['rewards']), color='red', linestyle='--', 
               label=f'Mean: {np.mean(results["rewards"]):.2f}')
    ax.set_xlabel('Total Reward', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('📊 Reward Distribution', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 2. Success Rate by Attacker Skill
    ax = axes[0, 1]
    skill_bins = [0, 0.4, 0.6, 0.8, 1.0]
    skill_labels = ['Novice', 'Intermediate', 'Advanced', 'Expert']
    success_by_skill = {label: [] for label in skill_labels}
    
    for i, skill in enumerate(results['attacker_skills']):
        for j in range(len(skill_bins) - 1):
            if skill_bins[j] <= skill < skill_bins[j + 1]:
                success_by_skill[skill_labels[j]].append(results['success'][i])
                break
    
    success_rates = [np.mean(success_by_skill[label]) * 100 if success_by_skill[label] 
                     else 0 for label in skill_labels]
    colors = ['#3498db', '#9b59b6', '#e74c3c', '#c0392b']
    ax.bar(skill_labels, success_rates, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('🎯 Success Rate by Attacker Skill', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # 3. Data Collected vs Steps
    ax = axes[0, 2]
    scatter = ax.scatter(results['steps'], results['data_collected'], 
                        c=results['rewards'], cmap='plasma', alpha=0.6, s=50)
    ax.set_xlabel('Steps', fontsize=12)
    ax.set_ylabel('Data Collected', fontsize=12)
    ax.set_title('📦 Data Collection Efficiency', fontsize=14, fontweight='bold')
    plt.colorbar(scatter, ax=ax, label='Reward')
    ax.grid(alpha=0.3)
    
    # 4. Action Frequency
    ax = axes[1, 0]
    action_names = [
        "Do Nothing", "Web", "DB", "SSH", "FTP", "Creds",
        "Vuln", "Slow", "Noise", "Services", "Bread", "Adv"
    ]
    actions = list(results['action_frequencies'].keys())
    frequencies = [results['action_frequencies'][a] for a in actions]
    colors_actions = plt.cm.viridis(np.linspace(0, 1, len(actions)))
    ax.barh([action_names[a] for a in actions], frequencies, 
            color=colors_actions, alpha=0.7, edgecolor='black')
    ax.set_xlabel('Frequency', fontsize=12)
    ax.set_title('🎬 Action Usage Distribution', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # 5. Suspicion vs Interaction Depth
    ax = axes[1, 1]
    colors_map = ['green' if s else 'red' for s in results['success']]
    ax.scatter(results['interaction_depths'], results['suspicions'], 
               c=colors_map, alpha=0.6, s=50)
    ax.set_xlabel('Interaction Depth', fontsize=12)
    ax.set_ylabel('Final Suspicion', fontsize=12)
    ax.set_title('🎭 Deception Effectiveness', fontsize=14, fontweight='bold')
    ax.axhline(0.85, color='red', linestyle='--', label='Detection Threshold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 6. Episode Length Distribution
    ax = axes[1, 2]
    ax.hist(results['steps'], bins=20, color='#e67e22', alpha=0.7, edgecolor='black')
    ax.axvline(np.mean(results['steps']), color='red', linestyle='--',
               label=f'Mean: {np.mean(results["steps"]):.1f}')
    ax.set_xlabel('Episode Length (steps)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('⏱️ Engagement Duration', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_dir = os.path.abspath(os.path.join(project_root, 'data'))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'performance_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Visualization saved: {output_path}")
    
    # Print statistics
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE STATISTICS")
    print("="*70)
    print(f"Episodes Analyzed: {n_episodes}")
    print(f"Overall Success Rate: {np.mean(results['success'])*100:.1f}%")
    print(f"Average Reward: {np.mean(results['rewards']):.2f} ± {np.std(results['rewards']):.2f}")
    print(f"Average Steps: {np.mean(results['steps']):.1f} ± {np.std(results['steps']):.1f}")
    print(f"Average Data Collected: {np.mean(results['data_collected']):.1f}")
    print(f"Average Interaction Depth: {np.mean(results['interaction_depths']):.2%}")
    print("="*70)
    print(f"\n🎨 Open: {output_path}")
    
    plt.show()


if __name__ == "__main__":
    visualize_performance()
