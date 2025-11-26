"""
🤖 Automated Red Team vs Blue Team Simulation
Self-playing agents that improve each other
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import time


@dataclass
class RedTeamAgent:
    """Attacker agent (Red Team)"""
    name: str
    skill_level: float
    tactics: List[str]
    success_rate: float
    evasion_capability: float


@dataclass
class BlueTeamAgent:
    """Defender agent (Blue Team)"""
    name: str
    detection_rate: float
    response_time: float
    learning_rate: float


class RedVsBlueSimulation:
    """
    Automated adversarial training simulation
    Red team attacks, Blue team defends, both learn
    """
    
    def __init__(self):
        self.red_team = []
        self.blue_team = []
        self.simulation_history = []
        self.round_number = 0
    
    def create_red_team(self):
        """Create Red Team attackers"""
        print("🔴 Creating Red Team...")
        
        self.red_team = [
            RedTeamAgent(
                name="Script Kiddie",
                skill_level=0.2,
                tactics=['scanning', 'basic_exploit'],
                success_rate=0.1,
                evasion_capability=0.1
            ),
            RedTeamAgent(
                name="Intermediate Hacker",
                skill_level=0.5,
                tactics=['reconnaissance', 'social_engineering', 'exploit'],
                success_rate=0.3,
                evasion_capability=0.4
            ),
            RedTeamAgent(
                name="Advanced Persistent Threat",
                skill_level=0.85,
                tactics=['zero_day', 'persistence', 'lateral_movement', 'exfiltration'],
                success_rate=0.6,
                evasion_capability=0.8
            ),
            RedTeamAgent(
                name="Nation-State Actor",
                skill_level=0.95,
                tactics=['supply_chain', 'firmware_implant', 'covert_channel'],
                success_rate=0.8,
                evasion_capability=0.95
            )
        ]
        
        print(f"✅ Created {len(self.red_team)} Red Team agents")
    
    def create_blue_team(self):
        """Create Blue Team defenders"""
        print("🔵 Creating Blue Team...")
        
        self.blue_team = [
            BlueTeamAgent(
                name="Junior Analyst",
                detection_rate=0.3,
                response_time=120,
                learning_rate=0.1
            ),
            BlueTeamAgent(
                name="Security Engineer",
                detection_rate=0.6,
                response_time=60,
                learning_rate=0.05
            ),
            BlueTeamAgent(
                name="Senior Analyst",
                detection_rate=0.8,
                response_time=30,
                learning_rate=0.03
            ),
            BlueTeamAgent(
                name="AI Detection System",
                detection_rate=0.9,
                response_time=5,
                learning_rate=0.02
            )
        ]
        
        print(f"✅ Created {len(self.blue_team)} Blue Team agents")
    
    def run_simulation(self, n_rounds: int = 100):
        """
        Run Red vs Blue simulation
        Each round, Red attacks and Blue defends
        """
        print(f"\n⚔️ Starting Red vs Blue Simulation ({n_rounds} rounds)")
        print("="*80)
        
        for round_num in range(n_rounds):
            self.round_number = round_num + 1
            
            if round_num % 10 == 0:
                print(f"\n🔄 Round {self.round_number}/{n_rounds}")
            
            # Select random attacker and defender
            attacker = np.random.choice(self.red_team)
            defender = np.random.choice(self.blue_team)
            
            # Simulate attack
            result = self._simulate_attack(attacker, defender)
            
            # Record result
            self.simulation_history.append(result)
            
            # Adaptive learning
            self._adaptive_learning(attacker, defender, result)
            
            # Display milestone results
            if (round_num + 1) % 25 == 0:
                self._display_round_stats(round_num + 1)
        
        print("\n✅ Simulation complete!")
        self._display_final_results()
    
    def _simulate_attack(
        self,
        attacker: RedTeamAgent,
        defender: BlueTeamAgent
    ) -> Dict:
        """Simulate single attack"""
        
        # Calculate detection probability
        detection_prob = (
            defender.detection_rate * 
            (1 - attacker.evasion_capability)
        )
        
        # Determine if attack is detected
        detected = np.random.random() < detection_prob
        
        # If detected, calculate response success
        if detected:
            response_success = np.random.random() < 0.8  # 80% successful response
        else:
            response_success = False
        
        # Attack success depends on skill and detection
        attack_successful = (
            not detected and 
            np.random.random() < attacker.success_rate
        )
        
        result = {
            'round': self.round_number,
            'attacker': attacker.name,
            'defender': defender.name,
            'attacker_skill': attacker.skill_level,
            'detected': detected,
            'detection_time': defender.response_time if detected else None,
            'response_successful': response_successful,
            'attack_successful': attack_successful,
            'data_collected': np.random.uniform(10, 1000) if detected else 0
        }
        
        return result
    
    def _adaptive_learning(
        self,
        attacker: RedTeamAgent,
        defender: BlueTeamAgent,
        result: Dict
    ):
        """
        Adaptive learning - agents improve based on results
        """
        
        # Blue team learns from successful detections
        if result['detected']:
            defender.detection_rate = min(
                1.0,
                defender.detection_rate + defender.learning_rate * 0.01
            )
        
        # Red team learns from failures
        if result['detected'] and not result['attack_successful']:
            attacker.evasion_capability = min(
                1.0,
                attacker.evasion_capability + 0.01
            )
        
        # Red team becomes more successful over time
        if result['attack_successful']:
            attacker.success_rate = min(
                0.95,
                attacker.success_rate + 0.005
            )
    
    def _display_round_stats(self, round_num: int):
        """Display statistics for recent rounds"""
        recent = self.simulation_history[-25:]
        
        detection_rate = sum(1 for r in recent if r['detected']) / len(recent) * 100
        attack_success_rate = sum(1 for r in recent if r['attack_successful']) / len(recent) * 100
        
        print(f"  📊 Rounds {round_num-24}-{round_num}:")
        print(f"     Detection Rate: {detection_rate:.1f}%")
        print(f"     Attack Success Rate: {attack_success_rate:.1f}%")
    
    def _display_final_results(self):
        """Display final simulation results"""
        print("\n" + "="*80)
        print("📊 FINAL SIMULATION RESULTS")
        print("="*80)
        
        total_rounds = len(self.simulation_history)
        detected = sum(1 for r in self.simulation_history if r['detected'])
        successful_attacks = sum(1 for r in self.simulation_history if r['attack_successful'])
        
        print(f"\n🎯 Overall Statistics:")
        print(f"   Total Rounds: {total_rounds}")
        print(f"   Detection Rate: {detected/total_rounds*100:.1f}%")
        print(f"   Attack Success Rate: {successful_attacks/total_rounds*100:.1f}%")
        
        # Blue team performance
        print(f"\n🔵 Blue Team Evolution:")
        for defender in self.blue_team:
            print(f"   {defender.name}:")
            print(f"     Detection Rate: {defender.detection_rate*100:.1f}%")
        
        # Red team performance
        print(f"\n🔴 Red Team Evolution:")
        for attacker in self.red_team:
            print(f"   {attacker.name}:")
            print(f"     Success Rate: {attacker.success_rate*100:.1f}%")
            print(f"     Evasion Capability: {attacker.evasion_capability*100:.1f}%")
        
        # Performance by attacker type
        print(f"\n📈 Performance by Attacker Type:")
        for attacker in self.red_team:
            attacker_rounds = [
                r for r in self.simulation_history 
                if r['attacker'] == attacker.name
            ]
            if attacker_rounds:
                detection = sum(1 for r in attacker_rounds if r['detected']) / len(attacker_rounds) * 100
                print(f"   {attacker.name}: {detection:.1f}% detected")
    
    def generate_training_insights(self) -> str:
        """Generate insights from simulation"""
        
        insights = f"""
{'='*80}
🧠 RED VS BLUE SIMULATION INSIGHTS
{'='*80}

📊 Key Findings:

1. Detection Effectiveness:
   - High-skill attackers (APT, Nation-State) have {self._get_detection_rate_for_skill('high'):.1f}% detection rate
   - Low-skill attackers (Script Kiddie) have {self._get_detection_rate_for_skill('low'):.1f}% detection rate
   - AI Detection System most effective with {self.blue_team[-1].detection_rate*100:.1f}% detection rate

2. Attack Evolution:
   - Red team evasion capability improved by {self._calculate_improvement('evasion'):.1f}%
   - Attack success rate increased by {self._calculate_improvement('success'):.1f}%

3. Defense Evolution:
   - Blue team detection improved by {self._calculate_improvement('detection'):.1f}%
   - Response time remained consistent

4. Recommendations:
   ✓ Deploy AI-powered detection for APT-level threats
   ✓ Focus training on detecting evasive techniques
   ✓ Implement behavior-based detection for nation-state actors
   ✓ Maintain adaptive learning for continuous improvement

{'='*80}
"""
        return insights
    
    def _get_detection_rate_for_skill(self, skill_category: str) -> float:
        """Get detection rate for skill category"""
        if skill_category == 'high':
            attackers = [a.name for a in self.red_team if a.skill_level >= 0.8]
        else:
            attackers = [a.name for a in self.red_team if a.skill_level < 0.4]
        
        relevant = [
            r for r in self.simulation_history 
            if r['attacker'] in attackers
        ]
        
        if not relevant:
            return 0.0
        
        return sum(1 for r in relevant if r['detected']) / len(relevant) * 100
    
    def _calculate_improvement(self, metric: str) -> float:
        """Calculate improvement percentage"""
        if not self.simulation_history or len(self.simulation_history) < 20:
            return 0.0
        
        early = self.simulation_history[:20]
        late = self.simulation_history[-20:]
        
        if metric == 'detection':
            early_rate = sum(1 for r in early if r['detected']) / len(early)
            late_rate = sum(1 for r in late if r['detected']) / len(late)
            return (late_rate - early_rate) * 100
        
        elif metric == 'evasion':
            # Approximate from attack success rates
            early_rate = sum(1 for r in early if r['attack_successful']) / len(early)
            late_rate = sum(1 for r in late if r['attack_successful']) / len(late)
            return (late_rate - early_rate) * 100
        
        elif metric == 'success':
            early_rate = sum(1 for r in early if r['attack_successful']) / len(early)
            late_rate = sum(1 for r in late if r['attack_successful']) / len(late)
            return (late_rate - early_rate) * 100
        
        return 0.0


# Example usage
if __name__ == "__main__":
    print("⚔️ Red Team vs Blue Team Simulation")
    print("="*80)
    
    # Create simulation
    sim = RedVsBlueSimulation()
    
    # Create teams
    sim.create_red_team()
    sim.create_blue_team()
    
    # Run simulation
    sim.run_simulation(n_rounds=200)
    
    # Generate insights
    insights = sim.generate_training_insights()
    print(insights)
    
    print("\n✅ Red vs Blue simulation complete!")
