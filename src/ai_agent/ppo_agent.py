"""Advanced PPO (Proximal Policy Optimization) agent for elite-level deception.

This implements a state-of-the-art deep RL agent using PyTorch for superior
decision-making in cyber deception scenarios. Much more powerful than Q-learning.
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
import logging
import os

from .deception_agent import ActionType, DeceptionState

logger = logging.getLogger(__name__)

# Import metrics collector
try:
    from .ppo_metrics import get_metrics_collector
    METRICS_ENABLED = True
except ImportError:
    METRICS_ENABLED = False
    logger.warning("PPO metrics not available")


@dataclass
class PPOMemory:
    """Experience buffer for PPO training."""
    states: List[np.ndarray]
    actions: List[int]
    rewards: List[float]
    values: List[float]
    log_probs: List[float]
    dones: List[bool]
    
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []
        self.dones = []
    
    def store(self, state, action, reward, value, log_prob, done):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
        self.dones.append(done)
    
    def __len__(self):
        return len(self.states)


class ActorCriticNetwork(nn.Module):
    """Neural network for PPO actor-critic architecture."""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        
        # Shared feature extractor
        self.shared = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        
        # Actor head (policy)
        self.actor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim),
            nn.Softmax(dim=-1)
        )
        
        # Critic head (value function)
        self.critic = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )
    
    def forward(self, state):
        features = self.shared(state)
        action_probs = self.actor(features)
        value = self.critic(features)
        return action_probs, value


class PPOAgent:
    """Elite-level PPO agent for cyber deception."""
    
    # 20 Elite Actions mapping
    ACTION_MAP = {
        0: ActionType.MAINTAIN,
        1: ActionType.DROP_SESSION,
        2: ActionType.THROTTLE_SESSION,
        3: ActionType.REDIRECT_SESSION,
        4: ActionType.INJECT_DELAY,
        5: ActionType.PROGRESSIVE_DELAY,
        6: ActionType.RANDOM_DELAY,
        7: ActionType.SWAP_SERVICE_BANNER,
        8: ActionType.RANDOMIZE_BANNER,
        9: ActionType.MIMIC_VULNERABLE,
        10: ActionType.PRESENT_LURE,
        11: ActionType.DEPLOY_BREADCRUMB,
        12: ActionType.INJECT_FAKE_CREDENTIALS,
        13: ActionType.SIMULATE_VALUABLE_TARGET,
        14: ActionType.CAPTURE_TOOLS,
        15: ActionType.LOG_ENHANCED,
        16: ActionType.FINGERPRINT_ATTACKER,
        17: ActionType.TARPIT,
        18: ActionType.HONEYPOT_UPGRADE,
        19: ActionType.ALERT_AND_TRACK,
    }
    
    def __init__(
        self,
        state_dim: int = 15,
        action_dim: int = 20,
        lr: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_epsilon: float = 0.2,
        entropy_coef: float = 0.01,
        value_coef: float = 0.5,
        max_grad_norm: float = 0.5,
        epochs: int = 10,
        batch_size: int = 64,
    ):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.max_grad_norm = max_grad_norm
        self.epochs = epochs
        self.batch_size = batch_size
        
        # Networks
        self.policy = ActorCriticNetwork(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        
        # Experience buffer
        self.memory = PPOMemory()
        
        # Training stats
        self.episode_rewards = []
        self.training_step = 0
        self.current_episode_reward = 0.0
        self.current_episode_length = 0
        
        # Metrics collector
        if METRICS_ENABLED:
            self.metrics = get_metrics_collector()
            self.metrics.metrics.device = str(self.device)
        else:
            self.metrics = None
        
        # Try to load existing checkpoint if available
        checkpoint_path = '/app/data/models/ppo_checkpoint.pt'
        if os.path.exists(checkpoint_path):
            try:
                self.load(checkpoint_path)
                logger.info(f"✅ Loaded existing checkpoint from {checkpoint_path}")
            except Exception as e:
                logger.warning(f"Could not load checkpoint, starting fresh: {e}")
        else:
            logger.info(f"🆕 No checkpoint found at {checkpoint_path}, starting with fresh model")
        
        logger.info(f"🚀 PPO Agent initialized on {self.device}")
    
    def state_to_tensor(self, state: DeceptionState) -> torch.Tensor:
        """Convert DeceptionState to normalized tensor (15 features)."""
        features = [
            # Service encoding (one-hot for 5 major services)
            1.0 if state.service == "SSH" else 0.0,
            1.0 if state.service == "FTP" else 0.0,
            1.0 if state.service == "HTTP" else 0.0,
            1.0 if state.service == "HTTPS" else 0.0,
            1.0 if state.service in ["MySQL", "PostgreSQL"] else 0.0,
            
            # Core metrics (5 features)
            min(state.command_count / 50.0, 1.0),
            min(state.data_exfil_attempts / 10.0, 1.0),
            1.0 if state.auth_success else 0.0,
            min(state.duration_seconds / 300.0, 1.0),
            min(state.suspicion_score, 1.0),
            
            # Command patterns (4 features)
            1.0 if "download" in state.last_command.lower() else 0.0,
            1.0 if "upload" in state.last_command.lower() else 0.0,
            1.0 if any(x in state.last_command.lower() for x in ["user", "pass"]) else 0.0,
            1.0 if any(x in state.last_command.lower() for x in ["ls", "list", "dir"]) else 0.0,
            
            # Threat indicator (1 feature)
            1.0 if state.data_exfil_attempts > 0 or state.suspicion_score > 0.5 else 0.0,
        ]
        
        return torch.FloatTensor(features).to(self.device)
    
    def choose_action(self, state: DeceptionState) -> Tuple[ActionType, float, float]:
        """Choose action using current policy."""
        state_tensor = self.state_to_tensor(state).unsqueeze(0)
        
        with torch.no_grad():
            action_probs, value = self.policy(state_tensor)
        
        # Sample action from distribution
        dist = torch.distributions.Categorical(action_probs)
        action_idx = dist.sample()
        log_prob = dist.log_prob(action_idx)
        
        action = self.ACTION_MAP[action_idx.item()]
        return action, log_prob.item(), value.item()
    
    def store_transition(self, state: DeceptionState, action: ActionType, reward: float, 
                        log_prob: float, value: float, done: bool = False):
        """Store experience for training."""
        state_tensor = self.state_to_tensor(state).cpu().numpy()
        action_idx = [k for k, v in self.ACTION_MAP.items() if v == action][0]
        
        self.memory.store(state_tensor, action_idx, reward, value, log_prob, done)
        
        # Track episode progress
        self.current_episode_reward += reward
        self.current_episode_length += 1
        
        # Record decision in metrics
        if self.metrics:
            self.metrics.record_decision(action.value, reward)
        
        # Episode ended
        if done:
            if self.metrics:
                self.metrics.record_episode(self.current_episode_reward, self.current_episode_length)
            self.current_episode_reward = 0.0
            self.current_episode_length = 0
    
    def compute_gae(self, rewards: List[float], values: List[float], 
                   dones: List[bool]) -> Tuple[np.ndarray, np.ndarray]:
        """Compute Generalized Advantage Estimation."""
        advantages = []
        gae = 0
        
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[t + 1]
            
            delta = rewards[t] + self.gamma * next_value * (1 - dones[t]) - values[t]
            gae = delta + self.gamma * self.gae_lambda * (1 - dones[t]) * gae
            advantages.insert(0, gae)
        
        advantages = np.array(advantages)
        returns = advantages + np.array(values)
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        return advantages, returns
    
    def update(self):
        """Update policy using PPO algorithm."""
        if len(self.memory) < self.batch_size:
            return
        
        # Compute advantages
        advantages, returns = self.compute_gae(
            self.memory.rewards, 
            self.memory.values, 
            self.memory.dones
        )
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(self.memory.states)).to(self.device)
        actions = torch.LongTensor(self.memory.actions).to(self.device)
        old_log_probs = torch.FloatTensor(self.memory.log_probs).to(self.device)
        advantages_tensor = torch.FloatTensor(advantages).to(self.device)
        returns_tensor = torch.FloatTensor(returns).to(self.device)
        
        # PPO update for multiple epochs
        for _ in range(self.epochs):
            # Get current policy outputs
            action_probs, values = self.policy(states)
            values = values.squeeze()
            
            # Compute log probs for taken actions
            dist = torch.distributions.Categorical(action_probs)
            new_log_probs = dist.log_prob(actions)
            entropy = dist.entropy().mean()
            
            # Compute ratio and clipped surrogate
            ratio = torch.exp(new_log_probs - old_log_probs)
            surr1 = ratio * advantages_tensor
            surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * advantages_tensor
            
            # Losses
            actor_loss = -torch.min(surr1, surr2).mean()
            critic_loss = nn.MSELoss()(values, returns_tensor)
            
            # Total loss
            loss = actor_loss + self.value_coef * critic_loss - self.entropy_coef * entropy
            
            # Optimize
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)
            self.optimizer.step()
        
        self.training_step += 1
        
        # Update metrics
        if self.metrics:
            self.metrics.update_training_metrics(
                actor_loss.item(),
                critic_loss.item(),
                entropy.item(),
                self.training_step
            )
        
        if self.training_step % 10 == 0:
            logger.info(f"📈 PPO training step {self.training_step}: "
                       f"actor_loss={actor_loss.item():.4f}, "
                       f"critic_loss={critic_loss.item():.4f}, "
                       f"entropy={entropy.item():.4f}")
        
        # Clear memory
        self.memory.clear()
    
    def save(self, path: str):
        """Save model checkpoint."""
        torch.save({
            'policy_state_dict': self.policy.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_step': self.training_step,
        }, path)
        
        # Update metrics
        if self.metrics:
            self.metrics.metrics.model_path = path
            # Save metrics alongside model
            metrics_path = path.replace('.pt', '_metrics.json')
            self.metrics.save_metrics(metrics_path)
        
        logger.info(f"💾 PPO model saved to {path}")
    
    def load(self, path: str):
        """Load model checkpoint."""
        if not os.path.exists(path):
            logger.warning(f"⚠️ Checkpoint file not found: {path}")
            return
            
        try:
            checkpoint = torch.load(path, map_location=self.device)
            self.policy.load_state_dict(checkpoint['policy_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.training_step = checkpoint['training_step']
            
            # Load metrics if available
            if self.metrics:
                metrics_path = path.replace('.pt', '_metrics.json')
                if os.path.exists(metrics_path):
                    self.metrics.load_metrics(metrics_path)
            
            logger.info(f"✅ PPO model loaded from {path}")
        except Exception as e:
            logger.warning(f"Could not load PPO model from {path}: {e}")
    
    def compute_reward(self, command: str, auth_success: bool, 
                      data_size: int, session_dropped: bool) -> float:
        """Compute sophisticated reward function."""
        reward = 0.0
        
        # Base engagement reward
        reward += 0.5
        
        # Command-based rewards
        cmd_lower = command.lower()
        if any(x in cmd_lower for x in ["retr", "download", "get"]):
            reward += 2.0  # Data exfil attempt captured!
        elif any(x in cmd_lower for x in ["ls", "list", "dir"]):
            reward += 1.0  # Enumeration
        elif any(x in cmd_lower for x in ["user", "pass", "auth"]):
            reward += 1.5  # Auth attempts
        
        # Auth success bonus (kept them engaged)
        if auth_success:
            reward += 2.5
        
        # Data collection bonus
        if data_size > 100:
            reward += 1.0
        if data_size > 500:
            reward += 2.0
        
        # Penalty for premature drops
        if session_dropped and data_size < 50:
            reward -= 3.0
        
        # Bonus for long engagement
        reward += min(data_size / 1000.0, 2.0)
        
        return reward
    
    def get_reason(self, action: ActionType, state: DeceptionState) -> str:
        """Generate human-readable reason for action."""
        reasons = {
            ActionType.MAINTAIN: f"Session maintained: {state.command_count} commands",
            ActionType.DROP_SESSION: f"Session dropped: {state.data_exfil_attempts} exfil attempts",
            ActionType.THROTTLE_SESSION: f"Throttling: suspicion {state.suspicion_score:.2f}",
            ActionType.REDIRECT_SESSION: f"Redirecting to isolated env",
            ActionType.INJECT_DELAY: f"Delay injected: duration {state.duration_seconds:.0f}s",
            ActionType.PROGRESSIVE_DELAY: f"Progressive delay: {state.command_count} cmds",
            ActionType.RANDOM_DELAY: f"Random delay applied",
            ActionType.SWAP_SERVICE_BANNER: f"Banner swapped: {state.service}",
            ActionType.RANDOMIZE_BANNER: f"Randomized service banner",
            ActionType.MIMIC_VULNERABLE: f"Mimicking vulnerable service",
            ActionType.PRESENT_LURE: f"Lure presented: {state.command_count} cmds",
            ActionType.DEPLOY_BREADCRUMB: f"Breadcrumb deployed",
            ActionType.INJECT_FAKE_CREDENTIALS: f"Fake credentials injected",
            ActionType.SIMULATE_VALUABLE_TARGET: f"Simulating high-value target",
            ActionType.CAPTURE_TOOLS: f"Capturing attacker tools",
            ActionType.LOG_ENHANCED: f"Enhanced logging enabled",
            ActionType.FINGERPRINT_ATTACKER: f"Fingerprinting attacker",
            ActionType.TARPIT: f"Tarpit activated",
            ActionType.HONEYPOT_UPGRADE: f"Upgrading to high-interaction",
            ActionType.ALERT_AND_TRACK: f"Alert sent, tracking attacker",
        }
        return reasons.get(action, f"Action: {action.value}")


def create_ppo_agent() -> PPOAgent:
    """Factory function to create PPO agent."""
    return PPOAgent()
