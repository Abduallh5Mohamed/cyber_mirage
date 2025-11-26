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
    """Supported deception actions."""

    MAINTAIN = "maintain_session"
    INJECT_DELAY = "inject_delay"
    SWAP_SERVICE_BANNER = "swap_service_banner"
    PRESENT_LURE = "present_lure"
    DROP_SESSION = "drop_session"


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
        alpha: float = 0.3,
        gamma: float = 0.9,
        epsilon: float = 0.2,
    ) -> None:
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table: Dict[Tuple, Dict[ActionType, float]] = {}
        self.lock = threading.Lock()

    def _ensure_state(self, state_key: Tuple) -> Dict[ActionType, float]:
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0.0 for action in ActionType}
        return self.q_table[state_key]

    def choose_action(self, state: DeceptionState) -> ActionType:
        state_key = state.key()
        with self.lock:
            q_values = self._ensure_state(state_key)
            if random.random() < self.epsilon:
                return random.choice(list(ActionType))
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
        if action == ActionType.INJECT_DELAY:
            return "High command velocity → slowing attacker down"
        if action == ActionType.SWAP_SERVICE_BANNER:
            return "Rotating service persona to avoid fingerprinting"
        if action == ActionType.PRESENT_LURE:
            return "Data exfil attempt detected → presenting lure file"
        if action == ActionType.DROP_SESSION:
            return "Suspicious escape attempt → terminating session"
        return "Baseline observation"

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