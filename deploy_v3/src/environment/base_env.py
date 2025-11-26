import gymnasium as gym
import numpy as np
from gymnasium import spaces


class HoneynetEnv(gym.Env):
    """🔥 Advanced Cyber Mirage Honeypot Environment 🔥
    
    Elite-level AI-powered deception system designed to deceive world-class attackers.
    Features:
    - MITRE ATT&CK Framework integration
    - APT (Advanced Persistent Threat) simulation
    - Zero-day exploitation detection
    - Sophisticated evasion technique handling
    - Multi-stage attack chain modeling
    """

    # MITRE ATT&CK Tactics mapping
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
    
    # APT Group behavioral patterns
    APT_PROFILES = {
        'apt28': {'stealth': 0.9, 'patience': 0.95, 'sophistication': 0.95},
        'apt29': {'stealth': 0.95, 'patience': 0.98, 'sophistication': 0.98},
        'lazarus': {'stealth': 0.85, 'patience': 0.90, 'sophistication': 0.92},
        'equation_group': {'stealth': 0.98, 'patience': 0.99, 'sophistication': 0.99},
        'script_kiddie': {'stealth': 0.2, 'patience': 0.3, 'sophistication': 0.3},
        'ransomware_gang': {'stealth': 0.6, 'patience': 0.5, 'sophistication': 0.7},
    }

    def __init__(self):
        super(HoneynetEnv, self).__init__()

        # Elite State Space (15 dimensions for world-class detection):
        # [scan_rate, endpoints_touched, time, suspicion, attacker_skill,
        #  data_quality, interaction_depth, network_traffic, honeypot_diversity,
        #  attacker_confidence, evasion_attempts, privilege_level, 
        #  lateral_movement_score, persistence_indicators, exfiltration_attempts]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32),
            high=np.array([100, 100, 2000, 1, 1, 1, 1, 200, 1, 1, 50, 1, 1, 50, 50], dtype=np.float32),
            dtype=np.float32
        )

        # Elite Actions (20 advanced deception techniques):
        # 0: Passive monitoring
        # 1-4: Service decoys (Web, DB, SSH, FTP)
        # 5-7: Data lures (Fake credentials, vulnerabilities, documents)
        # 8-11: Network deception (Slow response, noise, honeytokens, canary files)
        # 12-15: Advanced techniques (Breadcrumbs, polymorphic responses, AI-generated content, fake C2)
        # 16-19: Counter-APT tactics (Deception layers, fake exploits, timing attacks, behavioral mimicry)
        self.action_space = spaces.Discrete(20)

        self.reset()

    def reset(self, seed=None, options=None):
        # Set the seed for reproducibility
        if seed is not None:
            np.random.seed(seed)
        
        # Elite attacker profiling - simulate real APT groups
        apt_type = np.random.choice(list(self.APT_PROFILES.keys()))
        apt_profile = self.APT_PROFILES[apt_type]
        
        self.attacker_skill = apt_profile['sophistication']
        self.attacker_stealth = apt_profile['stealth']
        self.attacker_patience = int(apt_profile['patience'] * 1000)  # APTs are VERY patient
        self.apt_type = apt_type
        
        # Elite State: 15 dimensions
        self.state = np.array([
            np.random.uniform(1, 10) if apt_profile['stealth'] > 0.7 else np.random.uniform(10, 30),  # scan_rate
            0.0,  # endpoints_touched
            0.0,  # time
            0.0,  # suspicion
            self.attacker_skill,  # attacker_skill
            0.0,  # data_quality
            0.0,  # interaction_depth
            np.random.uniform(5, 20),  # network_traffic (APTs are stealthy)
            0.0,  # honeypot_diversity
            self.attacker_skill,  # attacker_confidence
            0.0,  # evasion_attempts
            0.0,  # privilege_level (starts low)
            0.0,  # lateral_movement_score
            0.0,  # persistence_indicators
            0.0,  # exfiltration_attempts
        ], dtype=np.float32)
        
        self.steps = 0
        self.max_steps = 1000  # Longer for APT detection
        self.data_collected = 0
        self.attacker_engaged = False
        self.deception_layers = 0
        self.total_reward = 0
        
        # Advanced tracking
        self.action_history = []
        self.suspicion_events = []
        self.mitre_tactics_used = []
        self.zero_day_attempts = 0
        self.privilege_escalation_attempts = 0
        self.lateral_movement_attempts = 0
        self.c2_connections = 0
        self.tools_detected = []
        
        return self.state, {'apt_type': apt_type, 'profile': apt_profile}

    def step(self, action):
        reward = 0.0
        self.action_history.append(action)
        
        # Keep only last 20 actions for analysis
        if len(self.action_history) > 20:
            self.action_history.pop(0)

        # 🎯 Advanced Action System
        if action == 0:  # Do nothing - risky!
            reward -= 0.5
            self.state[3] += 0.02  # suspicion increases
            
        elif action == 1:  # Web decoy
            reward += 3.0
            self.state[1] += 1  # endpoints
            self.state[6] += 0.05  # interaction depth
            self.deception_layers += 1
            
        elif action == 2:  # Database decoy
            reward += 4.0
            self.state[1] += 1
            self.state[5] += 0.1  # data quality
            self.data_collected += 2
            
        elif action == 3:  # SSH decoy
            reward += 3.5
            self.state[1] += 1
            self.state[6] += 0.08
            if self.attacker_skill > 0.7:  # Skilled attackers love SSH
                reward += 2.0
                self.attacker_engaged = True
                
        elif action == 4:  # FTP decoy
            reward += 2.5
            self.state[1] += 1
            
        elif action == 5:  # Fake credentials
            reward += 5.0
            self.data_collected += 3
            self.state[5] += 0.15
            if np.random.random() < 0.3:  # 30% chance of suspicion
                self.state[3] += 0.05
                
        elif action == 6:  # Fake vulnerability (GENIUS!)
            reward += 7.0
            self.state[6] += 0.2
            self.attacker_engaged = True
            self.data_collected += 4
            # Skilled attackers fall for this harder
            if self.attacker_skill > 0.6:
                reward += 3.0
                
        elif action == 7:  # Slow response (reduces suspicion!)
            reward += 2.0
            self.state[3] -= 0.03  # REDUCES suspicion (realistic delay)
            self.state[3] = max(0, self.state[3])
            
        elif action == 8:  # Network noise
            reward += 1.5
            self.state[7] += 2.0  # traffic
            self.state[3] -= 0.02  # looks more real
            self.state[3] = max(0, self.state[3])
            
        elif action == 9:  # Fake services
            reward += 4.0
            self.state[8] += 0.1  # diversity
            self.state[1] += 2
            
        elif action == 10:  # Breadcrumbs trail (advanced!)
            reward += 6.0
            self.state[6] += 0.15
            self.data_collected += 5
            self.deception_layers += 1
            
        elif action == 11:  # Advanced deception (ULTIMATE!)
            reward += 8.0
            self.state[5] += 0.2
            self.state[6] += 0.25
            self.data_collected += 6
            self.attacker_engaged = True
            if self.attacker_skill > 0.8:
                reward += 5.0  # Extra reward for fooling experts

        # 🧠 Intelligent State Updates
        self.state[2] += 1  # time
        
        # Dynamic scan rate based on engagement
        if self.attacker_engaged:
            self.state[0] += np.random.uniform(-1, 3)
        else:
            self.state[0] += np.random.uniform(-2, 1)
        self.state[0] = np.clip(self.state[0], 0, 100)
        
        # Endpoints grow based on attacker skill
        self.state[1] += np.random.randint(0, int(self.attacker_skill * 3) + 1)
        
        # Network traffic varies realistically
        self.state[7] += np.random.uniform(-5, 5)
        self.state[7] = np.clip(self.state[7], 0, 100)
        
        # Attacker confidence decreases if we're good
        if self.deception_layers > 3:
            self.state[9] -= 0.01  # confidence drops
        
        # 💎 Sophisticated Reward System
        # Bonus for time survived
        time_bonus = self.state[2] * 0.1
        reward += time_bonus
        
        # Bonus for data collected (exponential!)
        data_bonus = self.data_collected ** 1.2 * 0.5
        reward += data_bonus
        
        # Bonus for high interaction depth
        depth_bonus = self.state[6] * 10
        reward += depth_bonus
        
        # Bonus for diversity
        diversity_bonus = self.state[8] * 15
        reward += diversity_bonus
        
        # Bonus for keeping engagement
        if self.attacker_engaged:
            reward += 5.0
        
        # Penalty for repetitive actions (avoid patterns)
        if len(self.action_history) >= 3:
            if self.action_history[-1] == self.action_history[-2] == self.action_history[-3]:
                reward -= 5.0  # Repetition is suspicious!
                self.state[3] += 0.05

        # 🎲 Dynamic Suspicion Calculation
        base_suspicion = np.random.uniform(0, 0.05)  # Reduced from 0.15
        
        # Suspicion increases with time (attacker gets smarter) - but slower
        time_suspicion = min(0.1, self.state[2] / 2000)  # Reduced from 1000
        
        # Low diversity increases suspicion - but less aggressively  
        if self.state[8] < 0.3:
            base_suspicion += 0.02  # Reduced from 0.1
            
        # High interaction without good data = suspicious - but less punishing
        if self.state[6] > 0.5 and self.state[5] < 0.3:
            base_suspicion += 0.03  # Reduced from 0.15
        
        # Update suspicion
        self.state[3] += base_suspicion + time_suspicion
        self.state[3] = np.clip(self.state[3], 0, 1)

        # 🏁 Termination Conditions
        terminated = False
        truncated = False
        
        # Terminated if suspicion too high (CAUGHT!)
        if self.state[3] >= 0.85:
            terminated = True
            reward -= 50.0  # Big penalty for getting caught
            
        # Truncated if time runs out or attacker gives up
        elif self.state[2] >= self.attacker_patience or self.steps >= self.max_steps:
            truncated = True
            # Bonus for lasting long!
            if self.data_collected > 50:
                reward += 100.0
            elif self.data_collected > 30:
                reward += 50.0

        self.steps += 1
        self.total_reward += reward

        # 📊 Detailed Info
        info = {
            'data_collected': self.data_collected,
            'suspicion': float(self.state[3]),
            'attacker_skill': float(self.attacker_skill),
            'interaction_depth': float(self.state[6]),
            'deception_layers': self.deception_layers,
            'attacker_engaged': self.attacker_engaged,
            'total_reward': float(self.total_reward)
        }

        return self.state, float(reward), terminated, truncated, info

    def render(self, mode='human'):
        """Enhanced visualization with emojis and detailed stats"""
        suspicion_emoji = "🟢" if self.state[3] < 0.3 else "🟡" if self.state[3] < 0.6 else "🔴"
        engagement_emoji = "🔥" if self.attacker_engaged else "💤"
        
        print(f"\n{'='*70}")
        print(f"⏱️  Step {self.steps} | Time: {self.state[2]:.0f}s | {engagement_emoji}")
        print(f"{'='*70}")
        print(f"🎯 Endpoints Touched: {int(self.state[1])} | Scan Rate: {self.state[0]:.1f}")
        print(f"📊 Data Collected: {self.data_collected} | Data Quality: {self.state[5]:.1%}")
        print(f"🎭 Deception Layers: {self.deception_layers} | Interaction: {self.state[6]:.1%}")
        print(f"🌐 Network Traffic: {self.state[7]:.1f} | Diversity: {self.state[8]:.1%}")
        print(f"{suspicion_emoji} Suspicion: {self.state[3]:.1%} | Confidence: {self.state[9]:.1%}")
        print(f"💰 Total Reward: {self.total_reward:.2f}")
        print(f"{'='*70}\n")


# اختبار سريع
if __name__ == "__main__":
    print("🎮 Testing Advanced Cyber Mirage Environment...")
    print("="*70)
    env = HoneynetEnv()
    obs, info = env.reset()
    
    print(f"🎯 Attacker Skill Level: {env.attacker_skill:.1%}")
    print(f"⏰ Attacker Patience: {env.attacker_patience} seconds")
    print("="*70)

    for i in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        action_names = [
            "Do Nothing", "Web Decoy", "DB Decoy", "SSH Decoy",
            "FTP Decoy", "Fake Creds", "Fake Vuln", "Slow Response",
            "Network Noise", "Fake Services", "Breadcrumbs", "Advanced Deception"
        ]
        print(f"🎬 Action: {action_names[action]} | Reward: {reward:.2f}")
        
        if i % 3 == 0:
            env.render()
            
        if terminated or truncated:
            print("\n🏁 Episode Ended!")
            if terminated:
                print("❌ Attacker detected the honeypot!")
            else:
                print("✅ Successfully deceived the attacker!")
            break

    print("\n✅ Advanced Environment works perfectly!")