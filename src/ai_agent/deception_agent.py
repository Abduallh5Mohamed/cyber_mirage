"""AI-driven deception controller (lightweight Q-learning implementation).

This module exposes a DeceptionAgent that can evaluate attacker state, choose
an action, log the decision context, and report rewards. While simplified, it
follows the reinforcement-learning flow described in the Cyber Mirage design:
state -> action -> reward -> update.
"""
from __future__ import annotations

import json
import math
import random
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Optional, Tuple


class ActionType(str, Enum):
    """20 Elite Deception Actions for Advanced Cyber Defense."""
    
    # === Session Control (1-4) ===
    MAINTAIN = "maintain_session"           # Keep session active, observe behavior
    DROP_SESSION = "drop_session"           # Terminate malicious session
    THROTTLE_SESSION = "throttle_session"   # Slow down attacker's actions
    REDIRECT_SESSION = "redirect_session"   # Redirect to isolated environment
    
    # === Delay Tactics (5-7) ===
    INJECT_DELAY = "inject_delay"           # Add artificial latency
    PROGRESSIVE_DELAY = "progressive_delay" # Gradually increase delay
    RANDOM_DELAY = "random_delay"           # Unpredictable response times
    
    # === Banner & Identity Manipulation (8-10) ===
    SWAP_SERVICE_BANNER = "swap_service_banner"     # Change service fingerprint
    RANDOMIZE_BANNER = "randomize_banner"           # Random service identity
    MIMIC_VULNERABLE = "mimic_vulnerable"           # Appear vulnerable
    
    # === Lure & Deception (11-14) ===
    PRESENT_LURE = "present_lure"                   # Show fake valuable data
    DEPLOY_BREADCRUMB = "deploy_breadcrumb"         # Leave false trail
    INJECT_FAKE_CREDENTIALS = "inject_fake_creds"  # Plant fake credentials
    SIMULATE_VALUABLE_TARGET = "simulate_target"    # Appear high-value
    
    # === Active Defense (15-17) ===
    CAPTURE_TOOLS = "capture_tools"         # Capture attacker's tools/malware
    LOG_ENHANCED = "log_enhanced"           # Enhanced forensic logging
    FINGERPRINT_ATTACKER = "fingerprint"    # Collect attacker fingerprints
    
    # === Advanced Tactics (18-20) ===
    TARPIT = "tarpit"                       # Trap in slow connection
    HONEYPOT_UPGRADE = "honeypot_upgrade"   # Switch to higher interaction
    ALERT_AND_TRACK = "alert_track"         # Alert SOC and track attacker


@dataclass(frozen=True)
class DeceptionState:
    """Features that describe the honeypot session state."""

    service: str
    command_count: int
    data_exfil_attempts: int
    auth_success: bool
    duration_seconds: float
    last_command: str
    suspicion_score: float

    def key(self) -> Tuple:
        return (
            self.service,
            min(self.command_count, 50),
            min(self.data_exfil_attempts, 10),
            int(self.auth_success),
            int(self.duration_seconds // 5),
            self._bucket_command(self.last_command),
            round(self.suspicion_score, 1),
        )

    @staticmethod
    def _bucket_command(cmd: str) -> str:
        cmd = (cmd or "").lower()
        if cmd.startswith("retr") or "download" in cmd:
            return "download"
        if cmd.startswith("stor") or "upload" in cmd:
            return "upload"
        if cmd.startswith("user") or cmd.startswith("pass"):
            return "auth"
        if cmd in {"ls", "list", "nlst"}:
            return "listing"
        return "other"


class DeceptionAgent:
    """Simple tabular Q-learning agent for deception decisions."""

    def __init__(
        self,
        alpha: float = 0.4,
        gamma: float = 0.95,
        epsilon: float = 0.35,
        min_epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
    ) -> None:
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.epsilon_decay = epsilon_decay
        self.q_table: Dict[Tuple, Dict[ActionType, float]] = {}
        self.lock = threading.Lock()
        self.decision_count = 0
        self._init_action_biases()

    def _init_action_biases(self) -> None:
        """Initialize positive biases for active deception actions."""
        self.action_biases = {
            # Session Control
            ActionType.MAINTAIN: 0.0,
            ActionType.DROP_SESSION: 1.0,
            ActionType.THROTTLE_SESSION: 1.5,
            ActionType.REDIRECT_SESSION: 2.0,
            # Delay Tactics
            ActionType.INJECT_DELAY: 2.0,
            ActionType.PROGRESSIVE_DELAY: 1.8,
            ActionType.RANDOM_DELAY: 1.5,
            # Banner Manipulation
            ActionType.SWAP_SERVICE_BANNER: 1.5,
            ActionType.RANDOMIZE_BANNER: 1.3,
            ActionType.MIMIC_VULNERABLE: 2.5,
            # Lure & Deception
            ActionType.PRESENT_LURE: 3.0,
            ActionType.DEPLOY_BREADCRUMB: 2.5,
            ActionType.INJECT_FAKE_CREDENTIALS: 2.8,
            ActionType.SIMULATE_VALUABLE_TARGET: 2.2,
            # Active Defense
            ActionType.CAPTURE_TOOLS: 3.5,
            ActionType.LOG_ENHANCED: 1.0,
            ActionType.FINGERPRINT_ATTACKER: 2.0,
            # Advanced Tactics
            ActionType.TARPIT: 2.5,
            ActionType.HONEYPOT_UPGRADE: 2.0,
            ActionType.ALERT_AND_TRACK: 3.0,
        }

    def _ensure_state(self, state_key: Tuple) -> Dict[ActionType, float]:
        if state_key not in self.q_table:
            # Initialize with biases to encourage active actions
            self.q_table[state_key] = {
                action: self.action_biases.get(action, 0.0) 
                for action in ActionType
            }
        return self.q_table[state_key]

    def choose_action(self, state: DeceptionState) -> ActionType:
        state_key = state.key()
        with self.lock:
            q_values = self._ensure_state(state_key)
            self.decision_count += 1
            
            # Decay epsilon over time
            if self.decision_count % 50 == 0:
                self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
            
            # Exploration with bias towards active deception
            if random.random() < self.epsilon:
                # Weighted random: favor active deception actions across 20 types
                weights = [
                    1,   # MAINTAIN
                    2,   # DROP_SESSION
                    2,   # THROTTLE_SESSION
                    3,   # REDIRECT_SESSION
                    3,   # INJECT_DELAY
                    2,   # PROGRESSIVE_DELAY
                    2,   # RANDOM_DELAY
                    2,   # SWAP_SERVICE_BANNER
                    2,   # RANDOMIZE_BANNER
                    3,   # MIMIC_VULNERABLE
                    4,   # PRESENT_LURE
                    3,   # DEPLOY_BREADCRUMB
                    3,   # INJECT_FAKE_CREDENTIALS
                    3,   # SIMULATE_VALUABLE_TARGET
                    4,   # CAPTURE_TOOLS
                    2,   # LOG_ENHANCED
                    3,   # FINGERPRINT_ATTACKER
                    3,   # TARPIT
                    2,   # HONEYPOT_UPGRADE
                    4,   # ALERT_AND_TRACK
                ]
                return random.choices(list(ActionType), weights=weights, k=1)[0]
            
            # Context-aware action selection
            action = self._context_aware_action(state, q_values)
            return action
    
    def _context_aware_action(self, state: DeceptionState, q_values: Dict[ActionType, float]) -> ActionType:
        """Smart action selection based on attack context with 20 elite actions."""
        
        # === Critical Threat: Very high suspicion ===
        if state.suspicion_score > 0.9:
            return ActionType.ALERT_AND_TRACK
        
        if state.suspicion_score > 0.85:
            return ActionType.DROP_SESSION
        
        # === Data Exfiltration Detected ===
        if state.data_exfil_attempts > 2:
            return ActionType.CAPTURE_TOOLS
        
        if state.data_exfil_attempts > 0:
            candidates = [ActionType.PRESENT_LURE, ActionType.INJECT_FAKE_CREDENTIALS, ActionType.DEPLOY_BREADCRUMB]
            return max(candidates, key=lambda a: q_values.get(a, 0))
        
        # === High Suspicion ===
        if state.suspicion_score > 0.6:
            candidates = [ActionType.TARPIT, ActionType.FINGERPRINT_ATTACKER, ActionType.LOG_ENHANCED]
            return max(candidates, key=lambda a: q_values.get(a, 0))
        
        # === Many Commands (Active Attacker) ===
        if state.command_count > 10:
            candidates = [ActionType.PROGRESSIVE_DELAY, ActionType.THROTTLE_SESSION]
            return max(candidates, key=lambda a: q_values.get(a, 0))
        
        if state.command_count > 5:
            candidates = [ActionType.INJECT_DELAY, ActionType.RANDOM_DELAY]
            return max(candidates, key=lambda a: q_values.get(a, 0))
        
        # === Long Session (Engaged Attacker) ===
        if state.duration_seconds > 60:
            return ActionType.HONEYPOT_UPGRADE
        
        if state.duration_seconds > 30:
            candidates = [ActionType.SWAP_SERVICE_BANNER, ActionType.MIMIC_VULNERABLE, ActionType.SIMULATE_VALUABLE_TARGET]
            return max(candidates, key=lambda a: q_values.get(a, 0))
        
        # === Auth Success (Trusted Attacker) ===
        if state.auth_success:
            candidates = [ActionType.PRESENT_LURE, ActionType.DEPLOY_BREADCRUMB, ActionType.SIMULATE_VALUABLE_TARGET]
            return max(candidates, key=lambda a: q_values.get(a, 0))
        
        # === Default: Best Q-value ===
        return max(q_values, key=q_values.get)

    def update(self, state: DeceptionState, action: ActionType, reward: float, next_state: Optional[DeceptionState]) -> None:
        state_key = state.key()
        with self.lock:
            q_values = self._ensure_state(state_key)
            current_q = q_values[action]
            next_max = 0.0
            if next_state is not None:
                next_q_values = self._ensure_state(next_state.key())
                next_max = max(next_q_values.values())
            q_values[action] = current_q + self.alpha * (reward + self.gamma * next_max - current_q)

    def get_reason(self, action: ActionType, state: DeceptionState) -> str:
        """Short textual justification shown on dashboard."""
        reasons = {
            ActionType.MAINTAIN: "Baseline observation - monitoring attacker",
            ActionType.DROP_SESSION: "Suspicious behavior → terminating session",
            ActionType.THROTTLE_SESSION: "Throttling to slow attacker progress",
            ActionType.REDIRECT_SESSION: "Redirecting to isolated environment",
            ActionType.INJECT_DELAY: "High command velocity → slowing attacker",
            ActionType.PROGRESSIVE_DELAY: "Progressively increasing delays",
            ActionType.RANDOM_DELAY: "Random delays to confuse timing analysis",
            ActionType.SWAP_SERVICE_BANNER: "Rotating service persona",
            ActionType.RANDOMIZE_BANNER: "Randomizing service fingerprint",
            ActionType.MIMIC_VULNERABLE: "Appearing vulnerable to lure attacker",
            ActionType.PRESENT_LURE: "Data exfil attempt → presenting lure",
            ActionType.DEPLOY_BREADCRUMB: "Deploying false trail breadcrumbs",
            ActionType.INJECT_FAKE_CREDENTIALS: "Planting fake credentials",
            ActionType.SIMULATE_VALUABLE_TARGET: "Simulating high-value target",
            ActionType.CAPTURE_TOOLS: "Capturing attacker tools/malware",
            ActionType.LOG_ENHANCED: "Enhanced forensic logging enabled",
            ActionType.FINGERPRINT_ATTACKER: "Collecting attacker fingerprints",
            ActionType.TARPIT: "Tarpit activated - trapping attacker",
            ActionType.HONEYPOT_UPGRADE: "Upgrading interaction level",
            ActionType.ALERT_AND_TRACK: "ALERT: Tracking high-threat attacker",
        }
        return reasons.get(action, f"Action: {action.value}")

    def build_decision_payload(self, session_id: str, state: DeceptionState, action: ActionType, reward: float = 0.0) -> Dict:
        return {
            "decision_id": str(uuid.uuid4()),
            "session_id": session_id,
            "state": asdict(state),
            "action": action.value,
            "reason": self.get_reason(action, state),
            "reward": reward,
            "timestamp": time.time(),
        }

    def compute_reward(self, command: str, auth_success: bool, data_collected: float, session_closed: bool) -> float:
        """Heuristic reward shaping to bootstrap RL behaviour."""
        reward = 0.0
        cmd = (command or "").lower()
        if "password" in cmd or auth_success:
            reward += 5.0
        if cmd.startswith("retr") or "download" in cmd:
            reward += 4.0
        if cmd.startswith("stor"):
            reward += 2.0
        if "escape" in cmd or "sudo" in cmd:
            reward -= 6.0
        if session_closed and not auth_success:
            reward -= 2.0
        reward += min(data_collected / 512.0, 3.0)
        return reward


def default_agent() -> DeceptionAgent:
    """Factory used by honeypot manager to get a singleton agent."""
    return DeceptionAgent()