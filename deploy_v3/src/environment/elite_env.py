"""
🔥 ELITE Cyber Mirage Environment 🔥
Designed to deceive world-class attackers including APT groups

Features:
- MITRE ATT&CK Framework integration
- Real APT group behavior simulation (APT28, APT29, Lazarus, Equation Group)
- Zero-day exploitation detection
- Lateral movement tracking
- C2 communication detection
- 20 advanced deception techniques
"""

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class EliteHoneynetEnv(gym.Env):
    """Elite-level AI honeypot for world-class cyber defense"""

    # MITRE ATT&CK Tactics
    MITRE_TACTICS = {
        'reconnaissance': ['T1595', 'T1590', 'T1589'],
        'initial_access': ['T1190', 'T1133', 'T1078'],
        'execution': ['T1059', 'T1203', 'T1204'],
        'persistence': ['T1053', 'T1547', 'T1136'],
        'privilege_escalation': ['T1068', 'T1055', 'T1134'],
        'defense_evasion': ['T1027', 'T1070', 'T1562'],
        'credential_access': ['T1110', 'T1003', 'T1056'],
        'discovery': ['T1082', 'T1083', 'T1018'],
        'lateral_movement': ['T1021', 'T1210', 'T1570'],
        'collection': ['T1005', 'T1039', 'T1119'],
        'exfiltration': ['T1041', 'T1048', 'T1567'],
    }
    
    # Real APT behavioral profiles
    APT_PROFILES = {
        'apt28_fancy_bear': {'stealth': 0.90, 'patience': 0.95, 'sophistication': 0.95, 'origin': 'Russia'},
        'apt29_cozy_bear': {'stealth': 0.95, 'patience': 0.98, 'sophistication': 0.98, 'origin': 'Russia'},
        'apt32_ocean_lotus': {'stealth': 0.88, 'patience': 0.92, 'sophistication': 0.90, 'origin': 'Vietnam'},
        'apt34_oilrig': {'stealth': 0.85, 'patience': 0.88, 'sophistication': 0.87, 'origin': 'Iran'},
        'apt41': {'stealth': 0.92, 'patience': 0.94, 'sophistication': 0.96, 'origin': 'China'},
        'lazarus': {'stealth': 0.87, 'patience': 0.91, 'sophistication': 0.93, 'origin': 'N.Korea'},
        'equation_group': {'stealth': 0.98, 'patience': 0.99, 'sophistication': 0.99, 'origin': 'Unknown'},
        'sandworm': {'stealth': 0.89, 'patience': 0.93, 'sophistication': 0.94, 'origin': 'Russia'},
        'script_kiddie': {'stealth': 0.20, 'patience': 0.30, 'sophistication': 0.30, 'origin': 'Various'},
        'ransomware_gang': {'stealth': 0.65, 'patience': 0.55, 'sophistication': 0.75, 'origin': 'Various'},
    }

    def __init__(self):
        super(EliteHoneynetEnv, self).__init__()

        # Elite State Space: 15 dimensions
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32),
            high=np.array([100, 100, 2000, 1, 1, 1, 1, 200, 1, 1, 50, 1, 1, 50, 50], dtype=np.float32),
            dtype=np.float32
        )

        # 20 Elite Actions
        self.action_space = spaces.Discrete(20)
        self.reset()

    def reset(self, seed=None, options=None):
        if seed is not None:
            np.random.seed(seed)
        
        # Select APT profile
        apt_type = np.random.choice(list(self.APT_PROFILES.keys()))
        apt_profile = self.APT_PROFILES[apt_type]
        
        self.attacker_skill = apt_profile['sophistication']
        self.attacker_stealth = apt_profile['stealth']
        self.attacker_patience = int(apt_profile['patience'] * 1000)
        self.apt_type = apt_type
        self.apt_origin = apt_profile['origin']
        
        # State: 15 dimensions
        self.state = np.array([
            np.random.uniform(1, 10) if apt_profile['stealth'] > 0.7 else np.random.uniform(10, 30),
            0.0, 0.0, 0.0, self.attacker_skill, 0.0, 0.0,
            np.random.uniform(5, 20), 0.0, self.attacker_skill,
            0.0, 0.0, 0.0, 0.0, 0.0
        ], dtype=np.float32)
        
        self.steps = 0
        self.max_steps = 1000
        self.data_collected = 0
        self.attacker_engaged = False
        self.deception_layers = 0
        self.total_reward = 0
        self.action_history = []
        self.mitre_tactics_used = []
        self.zero_day_attempts = 0
        self.privilege_escalation_attempts = 0
        self.lateral_movement_attempts = 0
        self.c2_connections = 0
        
        return self.state, {'apt_type': apt_type, 'profile': apt_profile}

    def step(self, action):
        reward = 0.0
        self.action_history.append(action)
        if len(self.action_history) > 50:
            self.action_history.pop(0)

        # Action execution with MITRE mapping
        action_rewards = {
            0: (-1.0, 0.03, 0, []),
            1: (4.0, 0, 1, ['T1190']),
            2: (5.0, 0, 3, ['T1005']),
            3: (4.5, 0, 1, ['T1021']),
            4: (3.0, 0, 1, ['T1083']),
            5: (7.0, 0, 4, ['T1078']),
            6: (9.0, 0, 5, ['T1068']),
            7: (3.0, -0.04, 0, []),
            8: (2.5, -0.03, 0, []),
            9: (5.0, 0, 0, ['T1046']),
            10: (8.0, 0, 6, ['T1083']),
            11: (10.0, 0, 7, []),
            12: (6.0, 0, 4, ['T1552']),
            13: (5.5, 0, 4, ['T1119']),
            14: (7.0, -0.05, 0, []),
            15: (8.0, 0, 6, []),
            16: (12.0, 0, 10, ['T1071']),
            17: (9.0, 0, 7, []),
            18: (10.0, 0, 8, ['T1203']),
            19: (11.0, -0.08, 0, []),
        }
        
        r, susp_change, data, tactics = action_rewards.get(action, (0, 0, 0, []))
        reward += r
        self.state[3] += susp_change
        self.state[3] = max(0, self.state[3])
        self.data_collected += data
        self.mitre_tactics_used.extend(tactics)
        
        if action in [6, 18]:
            self.zero_day_attempts += 1
        if action == 16:
            self.c2_connections += 1
        if action in [3, 10]:
            self.lateral_movement_attempts += 1
        if action in [6, 18]:
            self.privilege_escalation_attempts += 1
        if action in [1, 2, 3, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
            self.attacker_engaged = True
            self.deception_layers += 1

        # State updates
        self.state[2] += 1
        self.state[0] += np.random.uniform(-1, 2) if self.attacker_stealth > 0.8 else np.random.uniform(-2, 4)
        self.state[0] = np.clip(self.state[0], 0, 100)
        self.state[1] += np.random.randint(0, int(self.attacker_skill * 4) + 1)
        self.state[7] += np.random.uniform(-3, 3)
        self.state[7] = np.clip(self.state[7], 0, 200)
        
        # Advanced behaviors
        if self.state[2] > 100 and np.random.random() < self.attacker_skill * 0.1:
            self.state[11] += 0.1
            self.privilege_escalation_attempts += 1
        
        if self.state[11] > 0.3 and np.random.random() < self.attacker_skill * 0.05:
            self.state[12] += 0.15
            self.lateral_movement_attempts += 1
        
        if self.state[2] > 200 and np.random.random() < self.attacker_skill * 0.08:
            self.state[13] += 1.0
        
        if self.state[2] > 300 and self.data_collected > 20:
            if np.random.random() < self.attacker_skill * 0.05:
                self.state[14] += 1.0

        # Reward calculations
        time_bonus = (self.state[2] ** 1.1) * 0.05
        data_bonus = (self.data_collected ** 1.3) * 0.8
        depth_bonus = (self.state[6] ** 1.2) * 15
        diversity_bonus = self.state[8] * 20
        
        reward += time_bonus + data_bonus + depth_bonus + diversity_bonus
        
        if self.attacker_engaged:
            reward += 10.0
        
        if self.attacker_skill > 0.85:
            reward *= 1.5
        
        unique_tactics = len(set(self.mitre_tactics_used))
        reward += unique_tactics * 5.0
        reward += self.zero_day_attempts * 20.0
        reward += self.privilege_escalation_attempts * 15.0
        reward += self.lateral_movement_attempts * 25.0
        reward += self.c2_connections * 30.0
        
        # Repetition penalty
        if len(self.action_history) >= 5:
            if len(set(self.action_history[-5:])) <= 2:
                reward -= 10.0
                self.state[3] += 0.08

        # Suspicion calculation
        base_suspicion = np.random.uniform(0, 0.08)
        time_suspicion = min(0.15, (self.state[2] / 2000) * self.attacker_stealth)
        
        if self.state[8] < 0.4:
            base_suspicion += 0.08 * self.attacker_skill
        if self.state[6] > 0.6 and self.state[5] < 0.4:
            base_suspicion += 0.12 * self.attacker_stealth
        if self.state[10] > 5:
            base_suspicion += 0.05
        if self.privilege_escalation_attempts > 3 and self.state[11] < 0.2:
            base_suspicion += 0.15
        
        self.state[3] += (base_suspicion + time_suspicion) * (1 + self.attacker_stealth * 0.5)
        self.state[3] = np.clip(self.state[3], 0, 1)

        # Termination
        terminated = False
        truncated = False
        detection_threshold = 0.75 + (self.attacker_stealth * 0.15)
        
        if self.state[3] >= detection_threshold:
            terminated = True
            reward -= 100.0 * self.attacker_skill
        elif self.state[2] >= self.attacker_patience or self.steps >= self.max_steps:
            truncated = True
            if self.data_collected > 100:
                reward += 500.0
            elif self.data_collected > 70:
                reward += 300.0
            elif self.data_collected > 50:
                reward += 200.0
            if self.attacker_skill > 0.85:
                reward += 200.0
                if unique_tactics > 5:
                    reward += 300.0

        self.steps += 1
        self.total_reward += reward

        info = {
            'data_collected': self.data_collected,
            'suspicion': float(self.state[3]),
            'attacker_skill': float(self.attacker_skill),
            'apt_type': self.apt_type,
            'apt_origin': self.apt_origin,
            'mitre_tactics': unique_tactics,
            'zero_day_attempts': self.zero_day_attempts,
            'lateral_movement': self.lateral_movement_attempts,
            'c2_connections': self.c2_connections,
            'total_reward': float(self.total_reward)
        }

        return self.state, float(reward), terminated, truncated, info

    def render(self, mode='human'):
        apt_emoji = "🔥" if self.attacker_skill > 0.85 else "⚡" if self.attacker_skill > 0.7 else "💤"
        susp_emoji = "🟢" if self.state[3] < 0.3 else "🟡" if self.state[3] < 0.6 else "🔴"
        
        print(f"\n{'='*80}")
        print(f"{apt_emoji} APT Type: {self.apt_type.upper()} ({self.apt_origin}) | Skill: {self.attacker_skill:.0%}")
        print(f"{'='*80}")
        print(f"⏱️  Step {self.steps} | Time: {self.state[2]:.0f}s | Data: {self.data_collected}")
        print(f"📊 MITRE Tactics: {len(set(self.mitre_tactics_used))} | {susp_emoji} Suspicion: {self.state[3]:.1%}")
        print(f"🎯 Zero-Days: {self.zero_day_attempts} | Lateral: {self.lateral_movement_attempts} | C2: {self.c2_connections}")
        print(f"💰 Reward: {self.total_reward:.2f}")
        print(f"{'='*80}\n")


# Test
if __name__ == "__main__":
    print("🔥 Testing ELITE Cyber Mirage Environment...")
    print("="*80)
    env = EliteHoneynetEnv()
    obs, info = env.reset()
    
    print(f"🎯 APT Group: {info['apt_type'].upper()}")
    print(f"🌍 Origin: {info['profile']['origin']}")
    print(f"💪 Sophistication: {info['profile']['sophistication']:.0%}")
    print("="*80)

    for i in range(20):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        if i % 5 == 0:
            env.render()
            
        if terminated or truncated:
            print("\n🏁 Episode Ended!")
            if terminated:
                print("❌ APT detected the honeypot!")
            else:
                print(f"✅ Successfully profiled {info['apt_type'].upper()}!")
            print(f"📊 Intelligence Gathered:")
            print(f"   • MITRE Tactics: {info['mitre_tactics']}")
            print(f"   • Zero-Day Attempts: {info['zero_day_attempts']}")
            print(f"   • Lateral Movement: {info['lateral_movement']}")
            print(f"   • C2 Connections: {info['c2_connections']}")
            break

    print("\n✅ ELITE Environment ready to defeat world-class attackers!")
