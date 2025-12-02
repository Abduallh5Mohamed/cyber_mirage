"""PPO Agent Metrics and Monitoring for Dashboard Integration."""
import json
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PPOMetrics:
    """Real-time metrics for PPO agent performance."""
    training_step: int = 0
    total_episodes: int = 0
    avg_reward: float = 0.0
    avg_episode_length: float = 0.0
    actor_loss: float = 0.0
    critic_loss: float = 0.0
    entropy: float = 0.0
    policy_version: int = 1
    last_update: str = ""
    
    # Action distribution
    action_counts: Dict[str, int] = None
    
    # Recent performance
    recent_rewards: List[float] = None
    recent_decisions: int = 0
    
    # Model info
    model_path: Optional[str] = None
    device: str = "cpu"
    
    def __post_init__(self):
        if self.action_counts is None:
            self.action_counts = {
                "maintain_session": 0,
                "inject_delay": 0,
                "swap_service_banner": 0,
                "present_lure": 0,
                "drop_session": 0
            }
        if self.recent_rewards is None:
            self.recent_rewards = []
        if not self.last_update:
            self.last_update = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['last_update'] = self.last_update
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PPOMetrics':
        """Create from dictionary."""
        return cls(**data)


class PPOMetricsCollector:
    """Collects and aggregates PPO metrics for monitoring."""
    
    def __init__(self):
        self.metrics = PPOMetrics()
        self.episode_rewards = []
        self.episode_lengths = []
        self.decision_history = []
        
    def update_training_metrics(self, actor_loss: float, critic_loss: float, 
                               entropy: float, training_step: int):
        """Update training metrics after PPO update."""
        self.metrics.actor_loss = actor_loss
        self.metrics.critic_loss = critic_loss
        self.metrics.entropy = entropy
        self.metrics.training_step = training_step
        self.metrics.policy_version += 1
        self.metrics.last_update = datetime.now().isoformat()
        
        logger.info(f"📊 PPO Metrics Updated: step={training_step}, "
                   f"actor_loss={actor_loss:.4f}, critic_loss={critic_loss:.4f}")
    
    def record_episode(self, total_reward: float, episode_length: int):
        """Record completed episode."""
        self.episode_rewards.append(total_reward)
        self.episode_lengths.append(episode_length)
        self.metrics.total_episodes += 1
        
        # Keep last 100 episodes
        if len(self.episode_rewards) > 100:
            self.episode_rewards.pop(0)
            self.episode_lengths.pop(0)
        
        # Update averages
        if self.episode_rewards:
            self.metrics.avg_reward = sum(self.episode_rewards) / len(self.episode_rewards)
            self.metrics.avg_episode_length = sum(self.episode_lengths) / len(self.episode_lengths)
    
    def record_decision(self, action: str, reward: float):
        """Record individual decision."""
        if action in self.metrics.action_counts:
            self.metrics.action_counts[action] += 1
        
        self.metrics.recent_rewards.append(reward)
        if len(self.metrics.recent_rewards) > 100:
            self.metrics.recent_rewards.pop(0)
        
        self.metrics.recent_decisions += 1
        self.decision_history.append({
            'action': action,
            'reward': reward,
            'timestamp': time.time()
        })
        
        # Keep last 1000 decisions
        if len(self.decision_history) > 1000:
            self.decision_history.pop(0)
    
    def get_action_distribution(self) -> Dict[str, float]:
        """Get normalized action distribution."""
        total = sum(self.metrics.action_counts.values())
        if total == 0:
            return {k: 0.0 for k in self.metrics.action_counts.keys()}
        return {k: v / total for k, v in self.metrics.action_counts.items()}
    
    def get_recent_performance(self) -> Dict:
        """Get recent performance statistics."""
        if not self.metrics.recent_rewards:
            return {
                'avg_reward': 0.0,
                'max_reward': 0.0,
                'min_reward': 0.0,
                'reward_std': 0.0
            }
        
        import numpy as np
        rewards = np.array(self.metrics.recent_rewards)
        return {
            'avg_reward': float(rewards.mean()),
            'max_reward': float(rewards.max()),
            'min_reward': float(rewards.min()),
            'reward_std': float(rewards.std())
        }
    
    def get_metrics_summary(self) -> Dict:
        """Get comprehensive metrics summary."""
        return {
            'training': {
                'training_step': self.metrics.training_step,
                'policy_version': self.metrics.policy_version,
                'actor_loss': self.metrics.actor_loss,
                'critic_loss': self.metrics.critic_loss,
                'entropy': self.metrics.entropy,
            },
            'performance': {
                'total_episodes': self.metrics.total_episodes,
                'avg_reward': self.metrics.avg_reward,
                'avg_episode_length': self.metrics.avg_episode_length,
                'recent_decisions': self.metrics.recent_decisions,
            },
            'actions': {
                'distribution': self.get_action_distribution(),
                'counts': self.metrics.action_counts,
            },
            'recent': self.get_recent_performance(),
            'model': {
                'device': self.metrics.device,
                'model_path': self.metrics.model_path,
                'last_update': self.metrics.last_update,
            }
        }
    
    def save_metrics(self, path: str):
        """Save metrics to file."""
        try:
            with open(path, 'w') as f:
                json.dump(self.get_metrics_summary(), f, indent=2)
            logger.info(f"💾 Metrics saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def load_metrics(self, path: str):
        """Load metrics from file."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Restore metrics
            if 'training' in data:
                self.metrics.training_step = data['training']['training_step']
                self.metrics.policy_version = data['training']['policy_version']
                self.metrics.actor_loss = data['training']['actor_loss']
                self.metrics.critic_loss = data['training']['critic_loss']
                self.metrics.entropy = data['training']['entropy']
            
            if 'performance' in data:
                self.metrics.total_episodes = data['performance']['total_episodes']
                self.metrics.avg_reward = data['performance']['avg_reward']
                self.metrics.avg_episode_length = data['performance']['avg_episode_length']
            
            if 'actions' in data and 'counts' in data['actions']:
                self.metrics.action_counts = data['actions']['counts']
            
            logger.info(f"✅ Metrics loaded from {path}")
        except Exception as e:
            logger.warning(f"Could not load metrics: {e}")


# Global metrics collector instance
_global_collector = None


def get_metrics_collector() -> PPOMetricsCollector:
    """Get or create global metrics collector."""
    global _global_collector
    if _global_collector is None:
        _global_collector = PPOMetricsCollector()
    return _global_collector
