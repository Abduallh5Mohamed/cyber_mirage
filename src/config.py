"""
⚙️ Cyber Mirage Configuration File
Advanced settings for training and environment
"""

# 🎮 Environment Configuration
ENV_CONFIG = {
    'max_steps': 500,                    # Maximum steps per episode
    'attacker_skill_range': (0.3, 0.95), # Min and max attacker skill
    'patience_range': (100, 400),        # Attacker patience in seconds
    'detection_threshold': 0.85,         # Suspicion level for detection
    
    # State space dimensions: 10
    # Actions: 12
}

# 🤖 PPO Training Configuration (ADVANCED)
PPO_CONFIG = {
    'learning_rate': 2e-4,
    'n_steps': 4096,
    'batch_size': 128,
    'n_epochs': 15,
    'gamma': 0.995,
    'gae_lambda': 0.98,
    'clip_range': 0.2,
    'clip_range_vf': None,
    'ent_coef': 0.01,
    'vf_coef': 0.5,
    'max_grad_norm': 0.5,
    'policy_kwargs': {
        'net_arch': [dict(pi=[256, 256, 128], vf=[256, 256, 128])]
    }
}

# 🎓 Training Configuration
TRAINING_CONFIG = {
    'total_timesteps': 200000,  # Increase for better results
    'log_interval': 1,
    'save_freq': 10000,
    'eval_freq': 5000,
    'n_eval_episodes': 10,
}

# 🧪 Testing Configuration
TESTING_CONFIG = {
    'n_episodes': 20,
    'render_interval': 50,  # Render every N steps
    'deterministic': True,   # Use deterministic policy
}

# 📊 Reward Configuration (Fine-tuning)
REWARD_CONFIG = {
    # Base action rewards
    'web_decoy': 3.0,
    'db_decoy': 4.0,
    'ssh_decoy': 3.5,
    'ftp_decoy': 2.5,
    'fake_creds': 5.0,
    'fake_vuln': 7.0,
    'slow_response': 2.0,
    'network_noise': 1.5,
    'fake_services': 4.0,
    'breadcrumbs': 6.0,
    'advanced_deception': 8.0,
    
    # Bonus multipliers
    'time_bonus': 0.1,
    'data_bonus_exp': 1.2,
    'data_bonus_mult': 0.5,
    'depth_bonus': 10.0,
    'diversity_bonus': 15.0,
    'engagement_bonus': 5.0,
    
    # Penalties
    'repetition_penalty': -5.0,
    'detection_penalty': -50.0,
    'do_nothing_penalty': -0.5,
    
    # Success bonuses
    'high_data_bonus': 100.0,   # If data > 50
    'medium_data_bonus': 50.0,  # If data > 30
}

# 🎨 Visualization Configuration
VIZ_CONFIG = {
    'figure_size': (18, 12),
    'dpi': 300,
    'style': 'seaborn-v0_8-darkgrid',
    'colors': {
        'primary': '#2ecc71',
        'secondary': '#3498db',
        'danger': '#e74c3c',
        'warning': '#f39c12',
        'success': '#27ae60',
    }
}

# 📁 Path Configuration
PATHS = {
    'logs': 'data/logs',
    'models': 'data/models',
    'visualizations': 'data/visualizations',
}

# 🎯 Advanced Features Toggle
FEATURES = {
    'use_curiosity': False,      # Intrinsic motivation (future)
    'use_multi_agent': False,    # Multi-attacker scenarios (future)
    'use_adaptive_difficulty': True,  # Dynamic attacker skill
    'use_memory': False,         # LSTM policy (future)
}

print("⚙️ Cyber Mirage Configuration Loaded")
print(f"🎮 Environment: {ENV_CONFIG['max_steps']} max steps")
print(f"🤖 Training: {TRAINING_CONFIG['total_timesteps']:,} timesteps")
print(f"🧠 Network: {PPO_CONFIG['policy_kwargs']['net_arch']}")
