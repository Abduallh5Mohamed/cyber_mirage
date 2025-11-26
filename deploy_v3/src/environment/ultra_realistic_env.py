"""
🔥🔥 ULTRA REALISTIC Cyber Mirage Environment 🔥🔥
مصمم لكل أنواع الهجمات من البسيطة للمعقدة جداً

Features:
- 16 نوع مهاجم (من Script Kiddie للـ Equation Group)
- توزيع واقعي (60% مبتدئين، 25% متوسط، 15% محترفين)
- MITRE ATT&CK Framework (11 tactics)
- Real-world attack simulations
- Zero-day, APT, Ransomware, Insider threats
"""

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class UltraRealisticHoneynetEnv(gym.Env):
    """البيئة الأكثر واقعية لكل أنواع الهجمات السيبرانية"""

    # MITRE ATT&CK Tactics (11 tactics)
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
    
    # 16 نوع مهاجم حقيقي (من الأضعف للأقوى)
    ATTACKER_PROFILES = {
        # ========== 1-5: المبتدئين (Very Easy) ==========
        "SCRIPT_KIDDIE": {
            "sophistication": 0.20, "stealth": 0.15, "persistence": 0.10,
            "origin": "Script Kiddie", "category": "beginner",
            "description": "Automated tools (Metasploit, SQLmap, Nmap)",
            "attacks": ["Port scan", "SQL injection", "Default passwords", "Public exploits"],
            "detection_ease": 0.95, "data_rate": (1, 5), "mitre_usage": 0.2
        },
        "WEB_DEFACER": {
            "sophistication": 0.30, "stealth": 0.25, "persistence": 0.20,
            "origin": "Defacement Groups", "category": "beginner",
            "description": "Website defacement, simple web attacks",
            "attacks": ["XSS", "CSRF", "Directory traversal", "File upload"],
            "detection_ease": 0.90, "data_rate": (2, 8), "mitre_usage": 0.3
        },
        "PHISHING_OPERATOR": {
            "sophistication": 0.35, "stealth": 0.30, "persistence": 0.25,
            "origin": "Phishing Campaigns", "category": "beginner",
            "description": "Mass phishing emails, credential harvesting",
            "attacks": ["Credential phishing", "Attachment malware", "Link spoofing"],
            "detection_ease": 0.88, "data_rate": (3, 10), "mitre_usage": 0.35
        },
        
        # ========== 6-10: المستوى المتوسط (Intermediate) ==========
        "BOTNET_OPERATOR": {
            "sophistication": 0.50, "stealth": 0.45, "persistence": 0.55,
            "origin": "Botnet/DDoS", "category": "intermediate",
            "description": "IoT botnets (Mirai), DDoS attacks",
            "attacks": ["Mirai variants", "DDoS", "Brute force", "IoT exploitation"],
            "detection_ease": 0.80, "data_rate": (5, 15), "mitre_usage": 0.45
        },
        "CRYPTOJACKER": {
            "sophistication": 0.55, "stealth": 0.65, "persistence": 0.75,
            "origin": "Cryptominers", "category": "intermediate",
            "description": "Silent cryptocurrency mining",
            "attacks": ["XMRig", "Browser mining", "Container escape", "Cloud abuse"],
            "detection_ease": 0.60, "data_rate": (4, 12), "mitre_usage": 0.50
        },
        "INSIDER_THREAT": {
            "sophistication": 0.60, "stealth": 0.80, "persistence": 0.70,
            "origin": "Malicious Insider", "category": "intermediate",
            "description": "Legitimate access abuse, data theft",
            "attacks": ["Data exfil", "Privilege abuse", "Credential theft", "Sabotage"],
            "detection_ease": 0.55, "data_rate": (10, 25), "mitre_usage": 0.55
        },
        "RANSOMWARE_GANG": {
            "sophistication": 0.75, "stealth": 0.60, "persistence": 0.70,
            "origin": "Ransomware (REvil, LockBit, BlackCat)", "category": "intermediate",
            "description": "Double extortion ransomware",
            "attacks": ["Ransomware", "Data leak", "RDP attacks", "Kerberoasting"],
            "detection_ease": 0.65, "data_rate": (15, 30), "mitre_usage": 0.65
        },
        "FINANCIALLY_MOTIVATED": {
            "sophistication": 0.78, "stealth": 0.75, "persistence": 0.78,
            "origin": "FIN7/FIN8/Carbanak", "category": "intermediate",
            "description": "Banking trojans, ATM jackpotting",
            "attacks": ["Carbanak", "ATM malware", "SWIFT attacks", "POS malware"],
            "detection_ease": 0.50, "data_rate": (12, 28), "mitre_usage": 0.70
        },
        
        # ========== 11-16: المحترفين والنخبة (Advanced & Elite) ==========
        "APT1_COMMENT_CREW": {
            "sophistication": 0.83, "stealth": 0.78, "persistence": 0.88,
            "origin": "China (PLA Unit 61398)", "category": "advanced",
            "description": "Massive IP theft, custom RATs",
            "attacks": ["Custom malware", "RATs", "Spear phishing", "Long-term access"],
            "detection_ease": 0.40, "data_rate": (18, 35), "mitre_usage": 0.80
        },
        "APT34_OILRIG": {
            "sophistication": 0.82, "stealth": 0.75, "persistence": 0.80,
            "origin": "Iran (MOIS)", "category": "advanced",
            "description": "Middle East energy sector targeting",
            "attacks": ["DNS tunneling", "PowerShell", "Web shells", "Credential dumping"],
            "detection_ease": 0.45, "data_rate": (15, 32), "mitre_usage": 0.78
        },
        "APT32_OCEAN_LOTUS": {
            "sophistication": 0.88, "stealth": 0.82, "persistence": 0.85,
            "origin": "Vietnam (APT32)", "category": "advanced",
            "description": "Southeast Asia espionage",
            "attacks": ["Spear phishing", "Cobalt Strike", "Living off land", "Backdoors"],
            "detection_ease": 0.38, "data_rate": (20, 40), "mitre_usage": 0.83
        },
        "SANDWORM": {
            "sophistication": 0.90, "stealth": 0.85, "persistence": 0.87,
            "origin": "Russia (GRU Unit 74455)", "category": "elite",
            "description": "Infrastructure attacks (NotPetya, Industroyer)",
            "attacks": ["ICS malware", "Wiper attacks", "Supply chain", "Infrastructure"],
            "detection_ease": 0.30, "data_rate": (22, 45), "mitre_usage": 0.88
        },
        "LAZARUS_GROUP": {
            "sophistication": 0.93, "stealth": 0.88, "persistence": 0.91,
            "origin": "North Korea (RGB)", "category": "elite",
            "description": "WannaCry, SWIFT heists, crypto theft",
            "attacks": ["Zero-day", "Watering hole", "Crypto theft", "Destructive malware"],
            "detection_ease": 0.25, "data_rate": (25, 50), "mitre_usage": 0.90
        },
        "APT28_FANCY_BEAR": {
            "sophistication": 0.95, "stealth": 0.85, "persistence": 0.90,
            "origin": "Russia (GRU Unit 26165)", "category": "elite",
            "description": "Military intelligence operations",
            "attacks": ["Spear phishing", "Credential harvesting", "DNC hack", "Election interference"],
            "detection_ease": 0.22, "data_rate": (28, 55), "mitre_usage": 0.92
        },
        "APT29_COZY_BEAR": {
            "sophistication": 0.98, "stealth": 0.95, "persistence": 0.93,
            "origin": "Russia (SVR)", "category": "elite",
            "description": "SolarWinds supply chain attack",
            "attacks": ["Supply chain", "Cloud infrastructure", "Long-term espionage", "Stealth persistence"],
            "detection_ease": 0.15, "data_rate": (30, 60), "mitre_usage": 0.95
        },
        "EQUATION_GROUP": {
            "sophistication": 0.99, "stealth": 0.98, "persistence": 0.96,
            "origin": "USA (NSA TAO)", "category": "elite",
            "description": "Most advanced: firmware, BIOS rootkits",
            "attacks": ["EternalBlue", "DoublePulsar", "Firmware implants", "BIOS persistence"],
            "detection_ease": 0.08, "data_rate": (35, 70), "mitre_usage": 0.98
        }
    }

    def __init__(self):
        super(UltraRealisticHoneynetEnv, self).__init__()

        # State Space: 15 dimensions
        # [Time, Suspicion, Data, Attacker_engaged, Attacker_skill,
        #  Honeypot_layer1, Honeypot_layer2, Activity_rate, Deception_level,
        #  Attacker_confidence, Zero_days, Lateral_movement, C2_detected,
        #  Privilege_escalation, Evasion_techniques]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32),
            high=np.array([1000, 100, 5000, 1, 1, 1, 1, 500, 1, 1, 100, 1, 1, 100, 100], dtype=np.float32),
            dtype=np.float32
        )

        # 20 Elite Deception Actions
        self.action_space = spaces.Discrete(20)
        self.reset()

    def reset(self, seed=None, options=None):
        if seed is not None:
            np.random.seed(seed)
        
        # اختيار نوع المهاجم بتوزيع واقعي
        attacker_types = list(self.ATTACKER_PROFILES.keys())
        
        # Realistic distribution: 40% beginners, 35% intermediate, 25% advanced/elite
        weights = []
        for attacker_name in attacker_types:
            profile = self.ATTACKER_PROFILES[attacker_name]
            category = profile["category"]
            if category == "beginner":
                weights.append(0.40)  # 40% مبتدئين
            elif category == "intermediate":
                weights.append(0.35)  # 35% متوسطين
            else:  # advanced or elite
                weights.append(0.25)  # 25% محترفين/نخبة
        
        # Normalize weights
        weights = np.array(weights) / sum(weights)
        self.current_attacker = np.random.choice(attacker_types, p=weights)
        profile = self.ATTACKER_PROFILES[self.current_attacker]
        
        # Set attacker characteristics
        self.attacker_skill = profile["sophistication"]
        self.attacker_stealth = profile["stealth"]
        self.attacker_persistence = profile["persistence"]
        self.detection_ease = profile["detection_ease"]
        self.attacker_category = profile["category"]
        self.attacker_origin = profile["origin"]
        self.data_rate_range = profile["data_rate"]
        self.mitre_usage_prob = profile["mitre_usage"]
        
        # Initial state
        self.state = np.zeros(15, dtype=np.float32)
        self.state[0] = 0  # Time
        self.state[1] = np.random.uniform(0.01, 0.05)  # Initial suspicion
        self.state[4] = self.attacker_skill  # Attacker skill
        self.state[7] = np.random.uniform(5, 15)  # Activity rate
        self.state[9] = self.attacker_skill  # Attacker confidence
        
        self.steps = 0
        self.max_steps = 1000
        self.detected_mitre_tactics = set()
        self.detected = False
        
        return self.state, {
            'attacker': self.current_attacker,
            'skill': self.attacker_skill,
            'category': self.attacker_category,
            'origin': self.attacker_origin
        }

    def step(self, action):
        self.steps += 1
        self.state[0] += 1  # Increment time
        
        # ========== 1. حساب الاشتباه (Suspicion) بطريقة واقعية ==========
        base_suspicion = 0.015 + np.random.uniform(0, 0.025)
        
        # تصنيف الأفعال حسب مدى خطورتها
        passive_actions = [0, 1, 5, 6, 7]  # Basic services, lures
        moderate_actions = [2, 8, 9, 10]    # SSH, network deception
        aggressive_actions = [3, 4, 11, 12, 13, 14]  # FTP, honeytokens, AI
        counter_apt_actions = [15, 16, 17, 18, 19]  # Advanced APT counter

        # حساب زيادة الاشتباه بناءً على نوع الفعل
        if action in passive_actions:
            suspicion_increase = self.detection_ease * 0.025
        elif action in moderate_actions:
            suspicion_increase = self.detection_ease * 0.050
        elif action in aggressive_actions:
            suspicion_increase = self.detection_ease * 0.080
        elif action in counter_apt_actions:
            suspicion_increase = self.detection_ease * 0.120
        else:
            suspicion_increase = self.detection_ease * 0.060
        
        # المهاجمون الأذكياء يتحركون أبطأ (تخفيض الاشتباه)
        stealth_reduction = self.attacker_stealth * 0.6
        final_suspicion = suspicion_increase * (1 - stealth_reduction)
        
        self.state[1] += final_suspicion  # Update suspicion
        self.state[1] = min(self.state[1], 100.0)  # Cap at 100%
        
        # ========== 2. جمع البيانات (Data Collection) ==========
        min_data, max_data = self.data_rate_range
        data_collected = np.random.randint(min_data, max_data + 1)
        self.state[2] += data_collected
        
        # ========== 3. كشف MITRE Tactics ==========
        if np.random.random() < self.mitre_usage_prob:
            tactics = list(self.MITRE_TACTICS.keys())
            detected_tactic = np.random.choice(tactics)
            self.detected_mitre_tactics.add(detected_tactic)
        
        # ========== 4. كشف التقنيات المتقدمة ==========
        # Zero-day exploitation (فقط المحترفين والنخبة)
        if self.attacker_skill > 0.80:
            zero_day_chance = (self.attacker_skill - 0.80) * 0.60
            if np.random.random() < zero_day_chance:
                self.state[10] += 1
        
        # Lateral movement (بعد 30 خطوة على الأقل)
        if self.state[0] > 30 and self.attacker_skill > 0.55:
            lateral_chance = (self.attacker_persistence - 0.40) * 0.35
            if np.random.random() < lateral_chance:
                self.state[11] = 1
        
        # C2 Communications
        if self.attacker_skill > 0.50:
            c2_chance = (self.attacker_skill - 0.50) * 0.40
            if np.random.random() < c2_chance:
                self.state[12] = 1
        
        # Privilege Escalation
        if self.state[0] > 20 and self.attacker_skill > 0.45:
            priv_esc_chance = self.attacker_skill * 0.30
            if np.random.random() < priv_esc_chance:
                self.state[13] = 1
        
        # Evasion Techniques (المحترفين والنخبة فقط)
        if self.attacker_skill > 0.75:
            evasion_chance = (self.attacker_skill - 0.75) * 0.50
            if np.random.random() < evasion_chance:
                self.state[14] = 1
        
        # ========== 5. حساب المكافآت (Rewards) ==========
        reward = 0.0
        terminated = False
        
        # 5.1 Engagement Reward (إبقاء المهاجم مشغولاً)
        if not terminated:
            # المبتدئين: مكافأة قليلة (2-5)
            # المتوسطين: مكافأة متوسطة (5-10)
            # المحترفين: مكافأة عالية (10-20)
            # النخبة: مكافأة ضخمة (20-30)
            if self.attacker_category == "beginner":
                engagement_reward = 2.0 + (self.attacker_skill * 15.0)
            elif self.attacker_category == "intermediate":
                engagement_reward = 5.0 + (self.attacker_skill * 25.0)
            elif self.attacker_category == "advanced":
                engagement_reward = 10.0 + (self.attacker_skill * 35.0)
            else:  # elite
                engagement_reward = 20.0 + (self.attacker_skill * 50.0)
            
            reward += engagement_reward
        
        # 5.2 Intelligence Collection Reward
        if data_collected > 0:
            intel_multiplier = 1.0 + (self.attacker_skill * 4.0)  # 1.0-5.0x
            intel_reward = data_collected * intel_multiplier
            reward += intel_reward
        
        # 5.3 MITRE Tactics Detection Reward
        mitre_count = len(self.detected_mitre_tactics)
        if mitre_count > 0:
            # كل tactic = 30-100 نقطة (يزيد مع مهارة المهاجم)
            mitre_reward = mitre_count * 30.0 * (1 + self.attacker_skill * 3)
            reward += mitre_reward
        
        # 5.4 Advanced Technique Detection Rewards
        # Zero-days (أغلى شيء!)
        if self.state[10] > 0:
            zero_day_reward = self.state[10] * 200.0 * (1 + self.attacker_skill * 4)
            reward += zero_day_reward
        
        # Lateral Movement
        if self.state[11] == 1:
            lateral_reward = 150.0 * (1 + self.attacker_skill * 2.5)
            reward += lateral_reward
        
        # C2 Infrastructure
        if self.state[12] == 1:
            c2_reward = 180.0 * (1 + self.attacker_skill * 3)
            reward += c2_reward
        
        # Privilege Escalation
        if self.state[13] == 1:
            priv_esc_reward = 140.0 * (1 + self.attacker_skill * 2)
            reward += priv_esc_reward
        
        # Evasion Techniques
        if self.state[14] == 1:
            evasion_reward = 170.0 * (1 + self.attacker_skill * 2.5)
            reward += evasion_reward
        
        # 5.5 Time-based Rewards (مكافآت التوقيت)
        if terminated:
            # كشف مبكر جداً = سيء جداً
            if self.state[0] < 15:
                reward -= 300.0
            # كشف مبكر = سيء
            elif self.state[0] < 40:
                reward -= 100.0
            # كشف مثالي (40-120 steps)
            elif self.state[0] < 120:
                ideal_bonus = 200.0 * (1 + self.attacker_skill * 3)
                reward += ideal_bonus
            # كشف متأخر (120-250 steps) - ممتاز!
            elif self.state[0] < 250:
                late_bonus = 400.0 * (1 + self.attacker_skill * 5)
                reward += late_bonus
            # Long-term engagement (250+ steps) - أسطوري!
            else:
                epic_bonus = 800.0 * (1 + self.attacker_skill * 8)
                reward += epic_bonus
        
        # 5.6 Data Milestone Rewards
        if self.state[2] > 1000:
            reward += 500.0
        elif self.state[2] > 500:
            reward += 250.0
        elif self.state[2] > 200:
            reward += 120.0
        elif self.state[2] > 100:
            reward += 60.0
        
        # 5.7 Comprehensive Intelligence Bonus
        intel_score = 0
        if self.state[10] > 0: intel_score += 1  # Zero-days
        if self.state[11] == 1: intel_score += 1  # Lateral
        if self.state[12] == 1: intel_score += 1  # C2
        if self.state[13] == 1: intel_score += 1  # Priv Esc
        if self.state[14] == 1: intel_score += 1  # Evasion
        if mitre_count >= 5: intel_score += 1
        
        if intel_score >= 4:
            comprehensive_bonus = 600.0 * (1 + self.attacker_skill * 4)
            reward += comprehensive_bonus
        
        # ========== 6. شرط الإنهاء (Termination) ==========
        # المبتدئين: يُكشفون بسرعة (50-65% suspicion)
        # المتوسطين: 65-80%
        # المحترفين: 80-92%
        # النخبة: 92-99%
        
        if self.attacker_category == "beginner":
            detection_threshold = 50.0 + (self.attacker_stealth * 15.0)
        elif self.attacker_category == "intermediate":
            detection_threshold = 65.0 + (self.attacker_stealth * 15.0)
        elif self.attacker_category == "advanced":
            detection_threshold = 80.0 + (self.attacker_stealth * 12.0)
        else:  # elite
            detection_threshold = 92.0 + (self.attacker_stealth * 7.0)
        
        if self.state[1] >= detection_threshold:
            terminated = True
            self.detected = True
        
        # Max steps
        if self.steps >= self.max_steps:
            terminated = True
        
        truncated = False
        
        info = {
            'attacker': self.current_attacker,
            'category': self.attacker_category,
            'skill': self.attacker_skill,
            'data_collected': self.state[2],
            'suspicion': self.state[1],
            'mitre_tactics': len(self.detected_mitre_tactics),
            'zero_days': self.state[10],
            'detected': self.detected,
            'steps': self.steps
        }
        
        return self.state, float(reward), terminated, truncated, info


# ========== Testing Code ==========
if __name__ == "__main__":
    print("🔥🔥 Testing ULTRA REALISTIC Cyber Mirage Environment...")
    print("="*80)
    
    env = UltraRealisticHoneynetEnv()
    obs, info = env.reset()
    
    print(f"🎯 Attacker: {info['attacker']}")
    print(f"🏷️  Category: {info['category'].upper()}")
    print(f"🌍 Origin: {info['origin']}")
    print(f"💪 Sophistication: {int(info['skill']*100)}%")
    print(f"📊 Detection Ease: {int(env.detection_ease*100)}%")
    print("="*80)
    print()
    
    total_reward = 0
    done = False
    step_count = 0
    
    while not done and step_count < 20:
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        step_count += 1
        done = terminated or truncated
        
        if step_count % 5 == 0 or done:
            print("="*80)
            print(f"🔥 {info['attacker']} ({info['category'].upper()}) | Skill: {int(info['skill']*100)}%")
            print("="*80)
            print(f"⏱️  Step {step_count} | Time: {int(obs[0])}s | Data: {int(obs[2])} MB")
            print(f"📊 MITRE Tactics: {info['mitre_tactics']} | 🔴 Suspicion: {obs[1]:.1f}%")
            print(f"🎯 Zero-Days: {int(obs[10])} | Lateral: {int(obs[11])} | C2: {int(obs[12])}")
            print(f"💰 Step Reward: {reward:.2f} | Total: {total_reward:.2f}")
            print("="*80)
            print()
    
    print()
    print("🏁 Episode Ended!")
    if info['detected']:
        print("✅ Attacker detected successfully!")
    else:
        print("⚠️  Attacker still active (max steps reached)")
    
    print(f"\n📊 Final Intelligence:")
    print(f"   • Total Data: {int(obs[2])} MB")
    print(f"   • MITRE Tactics: {info['mitre_tactics']}")
    print(f"   • Zero-Days: {int(obs[10])}")
    print(f"   • Lateral Movement: {'Yes' if obs[11] == 1 else 'No'}")
    print(f"   • C2 Detected: {'Yes' if obs[12] == 1 else 'No'}")
    print(f"   • Total Reward: {total_reward:.2f}")
    print()
    print("✅ ULTRA REALISTIC Environment ready!")
    print("🌍 من Script Kiddies لـ Equation Group - كلهم جاهزين!")
