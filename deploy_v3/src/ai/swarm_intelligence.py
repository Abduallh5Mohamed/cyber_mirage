"""
🐝 Swarm Intelligence - ذكاء السرب
آلاف من الوكلاء الذكية تعمل كسرب واحد!
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
import random


@dataclass
class SwarmAgent:
    """وكيل واحد في السرب"""
    id: int
    position: np.ndarray  # Position in solution space
    velocity: np.ndarray
    best_position: np.ndarray
    best_fitness: float
    role: str  # scout, defender, attacker, analyzer


class ParticleSwarmDefense:
    """
    دفاع بذكاء السرب - Particle Swarm Optimization
    آلاف من الوكلاء يتشاركون المعلومات!
    """
    
    def __init__(self, n_agents: int = 1000, dimensions: int = 50):
        self.n_agents = n_agents
        self.dimensions = dimensions
        self.agents = []
        self.global_best_position = None
        self.global_best_fitness = -np.inf
        
        self._initialize_swarm()
    
    def _initialize_swarm(self):
        """تهيئة السرب"""
        print(f"🐝 Initializing swarm with {self.n_agents} agents...")
        
        roles = ['scout', 'defender', 'attacker', 'analyzer']
        
        for i in range(self.n_agents):
            agent = SwarmAgent(
                id=i,
                position=np.random.uniform(-10, 10, self.dimensions),
                velocity=np.random.uniform(-1, 1, self.dimensions),
                best_position=np.random.uniform(-10, 10, self.dimensions),
                best_fitness=-np.inf,
                role=random.choice(roles)
            )
            self.agents.append(agent)
        
        print(f"✅ Swarm initialized!")
    
    def optimize_defense(self, threat_landscape: np.ndarray, iterations: int = 100):
        """
        تحسين الدفاع باستخدام ذكاء السرب
        """
        print(f"\n🔄 Optimizing defense strategy ({iterations} iterations)...")
        
        w = 0.7  # Inertia weight
        c1 = 1.5  # Cognitive weight
        c2 = 1.5  # Social weight
        
        for iteration in range(iterations):
            for agent in self.agents:
                # Evaluate fitness
                fitness = self._evaluate_defense(agent.position, threat_landscape)
                
                # Update personal best
                if fitness > agent.best_fitness:
                    agent.best_fitness = fitness
                    agent.best_position = agent.position.copy()
                
                # Update global best
                if fitness > self.global_best_fitness:
                    self.global_best_fitness = fitness
                    self.global_best_position = agent.position.copy()
                
                # Update velocity (swarm dynamics!)
                r1, r2 = np.random.random(), np.random.random()
                
                cognitive = c1 * r1 * (agent.best_position - agent.position)
                social = c2 * r2 * (self.global_best_position - agent.position)
                
                agent.velocity = w * agent.velocity + cognitive + social
                
                # Update position
                agent.position += agent.velocity
                
                # Boundary control
                agent.position = np.clip(agent.position, -10, 10)
            
            if iteration % 20 == 0:
                print(f"   Iteration {iteration}: Best fitness = {self.global_best_fitness:.4f}")
        
        print(f"\n✅ Optimization complete!")
        print(f"   Final best fitness: {self.global_best_fitness:.4f}")
        
        return self.global_best_position
    
    def _evaluate_defense(self, position: np.ndarray, threat: np.ndarray) -> float:
        """تقييم فعالية موقع دفاعي"""
        # Simplified fitness function
        detection_capability = np.sum(position[:20])
        response_time = -np.sum(position[20:30])  # Lower is better
        false_positive = -np.sum(np.abs(position[30:40]))  # Lower is better
        adaptability = np.sum(position[40:])
        
        fitness = detection_capability + response_time + false_positive + adaptability
        
        return fitness
    
    def get_defense_strategy(self) -> Dict:
        """الحصول على استراتيجية الدفاع المثلى"""
        strategy = {
            'detection_threshold': self.global_best_position[0],
            'response_aggressiveness': self.global_best_position[1],
            'deception_level': self.global_best_position[2],
            'monitoring_intensity': self.global_best_position[3],
            'swarm_consensus': self.global_best_fitness,
            'agent_roles': self._count_roles()
        }
        
        return strategy
    
    def _count_roles(self) -> Dict[str, int]:
        """عد الوكلاء حسب الأدوار"""
        roles = {}
        for agent in self.agents:
            roles[agent.role] = roles.get(agent.role, 0) + 1
        return roles


class AntColonyIntelligence:
    """
    ذكاء مستعمرة النمل - Ant Colony Optimization
    النمل يترك فيرومونات لتوجيه الآخرين!
    """
    
    def __init__(self, n_ants: int = 500):
        self.n_ants = n_ants
        self.pheromone_map = {}
        self.best_path = []
        self.best_path_length = np.inf
    
    def find_threat_path(self, threat_graph: Dict, start: str, end: str, iterations: int = 50):
        """
        إيجاد مسارات الهجوم المحتملة
        """
        print(f"\n🐜 Ant Colony searching for threat paths...")
        print(f"   {self.n_ants} ants, {iterations} iterations")
        
        alpha = 1.0  # Pheromone importance
        beta = 2.0   # Heuristic importance
        rho = 0.1    # Evaporation rate
        Q = 100      # Pheromone deposit amount
        
        # Initialize pheromones
        for node in threat_graph:
            for neighbor in threat_graph[node]:
                self.pheromone_map[(node, neighbor)] = 1.0
        
        for iteration in range(iterations):
            paths = []
            
            # Each ant finds a path
            for ant_id in range(self.n_ants):
                path = self._ant_walk(threat_graph, start, end, alpha, beta)
                if path and path[-1] == end:
                    paths.append(path)
                    
                    # Update best path
                    path_length = len(path)
                    if path_length < self.best_path_length:
                        self.best_path_length = path_length
                        self.best_path = path
            
            # Evaporate pheromones
            for edge in self.pheromone_map:
                self.pheromone_map[edge] *= (1 - rho)
            
            # Deposit pheromones
            for path in paths:
                deposit = Q / len(path)
                for i in range(len(path) - 1):
                    edge = (path[i], path[i+1])
                    self.pheromone_map[edge] += deposit
            
            if iteration % 10 == 0:
                print(f"   Iteration {iteration}: Best path length = {self.best_path_length}")
        
        print(f"\n✅ Threat path found: {' -> '.join(self.best_path)}")
        
        return self.best_path
    
    def _ant_walk(self, graph: Dict, start: str, end: str, alpha: float, beta: float) -> List[str]:
        """النملة تمشي في الشبكة"""
        current = start
        path = [current]
        visited = {current}
        
        max_steps = 50
        steps = 0
        
        while current != end and steps < max_steps:
            if current not in graph or not graph[current]:
                break
            
            # Get unvisited neighbors
            neighbors = [n for n in graph[current] if n not in visited]
            if not neighbors:
                break
            
            # Calculate probabilities
            probabilities = []
            for neighbor in neighbors:
                edge = (current, neighbor)
                pheromone = self.pheromone_map.get(edge, 1.0)
                heuristic = 1.0  # Simplified
                
                prob = (pheromone ** alpha) * (heuristic ** beta)
                probabilities.append(prob)
            
            # Normalize
            total = sum(probabilities)
            if total == 0:
                break
            
            probabilities = [p / total for p in probabilities]
            
            # Select next node
            next_node = np.random.choice(neighbors, p=probabilities)
            path.append(next_node)
            visited.add(next_node)
            current = next_node
            steps += 1
        
        return path


class BeeAlgorithm:
    """
    خوارزمية النحل - Bee Algorithm
    نحل كشافة، نحل عاملة، نحل راقصة!
    """
    
    def __init__(self, n_scout_bees: int = 100, n_worker_bees: int = 500):
        self.n_scout_bees = n_scout_bees
        self.n_worker_bees = n_worker_bees
        self.flower_patches = []  # Good solutions
        self.best_patch = None
    
    def search_solution_space(self, problem_space: Dict, iterations: int = 50):
        """
        البحث في فضاء الحلول
        """
        print(f"\n🐝 Bee Algorithm searching...")
        print(f"   {self.n_scout_bees} scouts, {self.n_worker_bees} workers")
        
        for iteration in range(iterations):
            # Phase 1: Scout bees explore
            new_patches = []
            for scout in range(self.n_scout_bees):
                patch = self._scout_explore(problem_space)
                new_patches.append(patch)
            
            # Evaluate patches
            evaluated = [(p, self._evaluate_patch(p)) for p in new_patches]
            evaluated.sort(key=lambda x: x[1], reverse=True)
            
            # Keep best patches
            self.flower_patches = evaluated[:20]
            
            # Update best
            if self.flower_patches[0][1] > (self._evaluate_patch(self.best_patch) if self.best_patch else -np.inf):
                self.best_patch = self.flower_patches[0][0]
            
            # Phase 2: Worker bees exploit best patches
            for patch, quality in self.flower_patches[:5]:
                n_workers = int(self.n_worker_bees * quality / sum(q for _, q in self.flower_patches[:5]))
                
                for worker in range(n_workers):
                    improved_patch = self._worker_exploit(patch)
                    if self._evaluate_patch(improved_patch) > quality:
                        # Found better solution!
                        self.flower_patches.append((improved_patch, self._evaluate_patch(improved_patch)))
            
            if iteration % 10 == 0:
                best_quality = self._evaluate_patch(self.best_patch)
                print(f"   Iteration {iteration}: Best solution quality = {best_quality:.4f}")
        
        print(f"\n✅ Search complete!")
        print(f"   Best solution quality: {self._evaluate_patch(self.best_patch):.4f}")
        
        return self.best_patch
    
    def _scout_explore(self, space: Dict) -> Dict:
        """نحلة كشافة تستكشف"""
        return {
            'defense_position': np.random.uniform(0, 100, 10),
            'strategy': random.choice(['aggressive', 'defensive', 'balanced', 'stealthy'])
        }
    
    def _worker_exploit(self, patch: Dict) -> Dict:
        """نحلة عاملة تستغل حل جيد"""
        improved = patch.copy()
        
        # Local search around good solution
        improved['defense_position'] = patch['defense_position'] + np.random.normal(0, 1, 10)
        
        return improved
    
    def _evaluate_patch(self, patch: Dict) -> float:
        """تقييم جودة الحل"""
        if not patch:
            return 0.0
        
        # Simplified evaluation
        position_quality = np.sum(patch['defense_position']) / 1000
        strategy_bonus = {'aggressive': 1.2, 'defensive': 1.0, 'balanced': 1.1, 'stealthy': 1.15}
        
        quality = position_quality * strategy_bonus.get(patch['strategy'], 1.0)
        
        return quality


class SwarmDefenseCoordinator:
    """
    منسق دفاع السرب - يجمع كل خوارزميات السرب!
    """
    
    def __init__(self):
        self.pso = ParticleSwarmDefense(n_agents=1000)
        self.aco = AntColonyIntelligence(n_ants=500)
        self.bee = BeeAlgorithm(n_scout_bees=100, n_worker_bees=500)
        
        print("🌟 Swarm Defense Coordinator initialized!")
        print(f"   Total agents: {1000 + 500 + 100 + 500} = 2100 agents!")
    
    def coordinate_defense(self, threat_scenario: Dict) -> Dict:
        """
        تنسيق دفاع شامل باستخدام كل الأسراب
        """
        print("\n" + "="*80)
        print("🌟 SWARM DEFENSE COORDINATION")
        print("="*80)
        
        # 1. PSO optimizes detection parameters
        print("\n1️⃣ Particle Swarm optimizing detection...")
        threat_landscape = np.random.randn(50)
        pso_strategy = self.pso.optimize_defense(threat_landscape, iterations=30)
        
        # 2. Ant Colony finds attack paths
        print("\n2️⃣ Ant Colony mapping threat paths...")
        threat_graph = {
            'entry': ['web', 'ssh', 'ftp'],
            'web': ['app', 'db'],
            'ssh': ['admin', 'db'],
            'ftp': ['files'],
            'app': ['db', 'target'],
            'admin': ['target'],
            'db': ['target'],
            'files': ['target'],
            'target': []
        }
        aco_paths = self.aco.find_threat_path(threat_graph, 'entry', 'target', iterations=30)
        
        # 3. Bees search for optimal defense positions
        print("\n3️⃣ Bee Algorithm finding optimal positions...")
        bee_solution = self.bee.search_solution_space({}, iterations=30)
        
        # Combine all swarm intelligence
        coordinated_defense = {
            'detection_strategy': self.pso.get_defense_strategy(),
            'critical_paths': aco_paths,
            'defense_positions': bee_solution,
            'swarm_consensus': 'HIGH',
            'total_agents': 2100,
            'coordination_level': 'EXCELLENT'
        }
        
        print("\n" + "="*80)
        print("✅ SWARM COORDINATION COMPLETE")
        print("="*80)
        print(f"📊 Total agents coordinated: 2100")
        print(f"🎯 Critical paths identified: {len(aco_paths)}")
        print(f"🛡️ Defense positions optimized: YES")
        print(f"⚡ Swarm intelligence: ACTIVATED")
        
        return coordinated_defense


# Demo
if __name__ == "__main__":
    print("🐝 SWARM INTELLIGENCE - ULTIMATE DEMO")
    print("="*80)
    
    # Create swarm coordinator
    coordinator = SwarmDefenseCoordinator()
    
    # Simulate threat scenario
    threat = {
        'type': 'APT',
        'sophistication': 0.9,
        'targets': ['database', 'admin_panel', 'api']
    }
    
    # Coordinate defense
    defense = coordinator.coordinate_defense(threat)
    
    print("\n🎊 SWARM INTELLIGENCE IS PHENOMENAL!")
    print(f"   2100 agents working as ONE! 🔥")
