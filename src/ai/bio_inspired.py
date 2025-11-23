"""
🧬 Bio-Inspired Security - أمن مستوحى من الطبيعة
الجهاز المناعي، التطور، الجينات!
"""

import numpy as np
from typing import List, Dict, Tuple
import random


class ArtificialImmuneSystem:
    """
    الجهاز المناعي الاصطناعي
    مثل جهازك المناعي - يتعلم ويتذكر التهديدات!
    """
    
    def __init__(self):
        self.antibodies = []  # خلايا مناعية
        self.memory_cells = []  # خلايا ذاكرة
        self.pathogens_database = []  # قاعدة مسببات الأمراض
    
    def generate_antibodies(self, n: int = 100):
        """
        توليد أجسام مضادة عشوائية
        """
        print(f"🧬 Generating {n} antibodies...")
        
        for i in range(n):
            antibody = {
                'id': i,
                'pattern': np.random.uniform(0, 1, 20),  # Pattern recognition
                'specificity': np.random.uniform(0.5, 1.0),
                'lifespan': random.randint(50, 200),
                'clone_count': 0
            }
            self.antibodies.append(antibody)
        
        print(f"✅ {len(self.antibodies)} antibodies ready!")
    
    def detect_pathogen(self, threat: np.ndarray) -> Dict:
        """
        كشف تهديد (مسبب مرض)
        """
        print(f"\n🦠 Pathogen detected! Analyzing...")
        
        best_match = None
        best_affinity = 0
        
        # Find antibody with best match (affinity)
        for antibody in self.antibodies:
            affinity = self._calculate_affinity(antibody['pattern'], threat)
            
            if affinity > best_affinity:
                best_affinity = affinity
                best_match = antibody
        
        if best_affinity > 0.7:
            print(f"✅ RECOGNIZED! Affinity: {best_affinity:.2%}")
            print(f"   Antibody #{best_match['id']} matched!")
            
            # Clonal selection - نسخ الخلية الناجحة
            self._clonal_selection(best_match, best_affinity)
            
            # Create memory cell
            self._create_memory_cell(best_match, threat)
            
            return {
                'detected': True,
                'antibody': best_match,
                'affinity': best_affinity,
                'response': 'immediate'
            }
        else:
            print(f"⚠️ UNKNOWN PATHOGEN! Affinity: {best_affinity:.2%}")
            print(f"   Generating new antibodies...")
            
            # Generate new antibodies targeting this threat
            self._generate_specific_antibodies(threat)
            
            return {
                'detected': False,
                'affinity': best_affinity,
                'response': 'learning'
            }
    
    def _calculate_affinity(self, antibody_pattern: np.ndarray, threat: np.ndarray) -> float:
        """حساب التقارب بين الجسم المضاد والتهديد"""
        # Euclidean distance (inverse)
        distance = np.linalg.norm(antibody_pattern - threat)
        affinity = 1 / (1 + distance)
        return affinity
    
    def _clonal_selection(self, antibody: Dict, affinity: float):
        """
        الانتقاء النسيلي - نسخ الخلايا الناجحة
        """
        n_clones = int(affinity * 10)  # More clones for better match
        
        print(f"   🧬 Cloning antibody #{antibody['id']} → {n_clones} clones")
        
        for _ in range(n_clones):
            clone = antibody.copy()
            clone['id'] = len(self.antibodies)
            
            # Hypermutation - طفرات عشوائية للتحسين
            clone['pattern'] = antibody['pattern'] + np.random.normal(0, 0.1, 20)
            
            self.antibodies.append(clone)
        
        antibody['clone_count'] += n_clones
    
    def _create_memory_cell(self, antibody: Dict, pathogen: np.ndarray):
        """
        خلق خلية ذاكرة - للاستجابة السريعة مستقبلاً
        """
        memory = {
            'antibody_pattern': antibody['pattern'].copy(),
            'pathogen_signature': pathogen.copy(),
            'date_created': 'now',
            'activation_count': 0
        }
        
        self.memory_cells.append(memory)
        print(f"   💾 Memory cell created! Total memory: {len(self.memory_cells)}")
    
    def _generate_specific_antibodies(self, threat: np.ndarray, n: int = 20):
        """توليد أجسام مضادة خاصة بالتهديد"""
        for i in range(n):
            antibody = {
                'id': len(self.antibodies),
                'pattern': threat + np.random.normal(0, 0.2, 20),
                'specificity': 0.8,
                'lifespan': 100,
                'clone_count': 0
            }
            self.antibodies.append(antibody)
    
    def check_memory(self, threat: np.ndarray) -> bool:
        """
        فحص خلايا الذاكرة - استجابة سريعة للتهديدات المعروفة
        """
        for memory in self.memory_cells:
            affinity = self._calculate_affinity(memory['antibody_pattern'], threat)
            
            if affinity > 0.8:
                print(f"⚡ MEMORY RESPONSE! Known threat detected!")
                print(f"   Immediate immune response activated!")
                memory['activation_count'] += 1
                return True
        
        return False


class GeneticAlgorithmDefense:
    """
    خوارزمية جينية للدفاع
    التطور والانتخاب الطبيعي!
    """
    
    def __init__(self, population_size: int = 100):
        self.population_size = population_size
        self.population = []
        self.generation = 0
    
    def initialize_population(self):
        """تهيئة الجيل الأول"""
        print(f"🧬 Initializing population ({self.population_size} individuals)...")
        
        for i in range(self.population_size):
            individual = {
                'id': i,
                'genes': np.random.uniform(0, 1, 30),  # Defense parameters
                'fitness': 0,
                'age': 0
            }
            self.population.append(individual)
        
        print(f"✅ Generation 0 created!")
    
    def evolve(self, threat_environment: Dict, n_generations: int = 50):
        """
        تطوير الدفاع عبر الأجيال
        """
        print(f"\n🧬 Starting evolution ({n_generations} generations)...")
        
        for gen in range(n_generations):
            self.generation = gen
            
            # 1. Evaluate fitness
            for individual in self.population:
                individual['fitness'] = self._evaluate_fitness(individual, threat_environment)
            
            # 2. Selection - البقاء للأصلح
            self.population.sort(key=lambda x: x['fitness'], reverse=True)
            survivors = self.population[:self.population_size // 2]
            
            # 3. Crossover - التزاوج
            offspring = []
            while len(offspring) < self.population_size // 2:
                parent1 = random.choice(survivors)
                parent2 = random.choice(survivors)
                child = self._crossover(parent1, parent2)
                offspring.append(child)
            
            # 4. Mutation - الطفرة
            for child in offspring:
                if random.random() < 0.2:  # 20% mutation rate
                    self._mutate(child)
            
            # 5. New generation
            self.population = survivors + offspring
            
            if gen % 10 == 0:
                best_fitness = self.population[0]['fitness']
                print(f"   Generation {gen}: Best fitness = {best_fitness:.4f}")
        
        print(f"\n✅ Evolution complete!")
        print(f"   Best individual fitness: {self.population[0]['fitness']:.4f}")
        
        return self.population[0]  # Return fittest
    
    def _evaluate_fitness(self, individual: Dict, environment: Dict) -> float:
        """تقييم اللياقة - مدى جودة الدفاع"""
        genes = individual['genes']
        
        # Simplified fitness function
        detection_rate = np.mean(genes[:10])
        response_speed = np.mean(genes[10:20])
        false_positive_rate = 1 - np.mean(genes[20:])
        
        fitness = (detection_rate * 0.5 + 
                  response_speed * 0.3 + 
                  false_positive_rate * 0.2)
        
        return fitness
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """التزاوج - دمج جينات الوالدين"""
        crossover_point = random.randint(1, 29)
        
        child_genes = np.concatenate([
            parent1['genes'][:crossover_point],
            parent2['genes'][crossover_point:]
        ])
        
        child = {
            'id': len(self.population),
            'genes': child_genes,
            'fitness': 0,
            'age': 0
        }
        
        return child
    
    def _mutate(self, individual: Dict):
        """الطفرة - تغيير عشوائي في الجينات"""
        mutation_point = random.randint(0, 29)
        individual['genes'][mutation_point] = random.uniform(0, 1)


class NeuralDarwinism:
    """
    الداروينية العصبية
    الشبكات العصبية تتطور وتتنافس!
    """
    
    def __init__(self, n_networks: int = 50):
        self.n_networks = n_networks
        self.networks = []
    
    def create_network_population(self):
        """خلق مجموعة من الشبكات العصبية"""
        print(f"🧠 Creating {self.n_networks} neural networks...")
        
        for i in range(self.n_networks):
            network = {
                'id': i,
                'layers': [20, random.randint(10, 50), random.randint(5, 20), 3],
                'activation': random.choice(['relu', 'sigmoid', 'tanh']),
                'performance': 0,
                'survival_rate': 1.0
            }
            self.networks.append(network)
        
        print(f"✅ Neural population created!")
    
    def compete(self, n_rounds: int = 30):
        """
        المنافسة - الشبكات تتنافس على البقاء
        """
        print(f"\n⚔️ Neural competition ({n_rounds} rounds)...")
        
        for round_num in range(n_rounds):
            # Evaluate each network
            for network in self.networks:
                performance = random.uniform(0.5, 1.0)  # Simulated
                network['performance'] = performance
            
            # Sort by performance
            self.networks.sort(key=lambda x: x['performance'], reverse=True)
            
            # Kill bottom 30%
            survivors = self.networks[:int(self.n_networks * 0.7)]
            
            # Breed top performers
            new_networks = []
            for _ in range(self.n_networks - len(survivors)):
                parent = random.choice(survivors[:10])
                child = self._breed_network(parent)
                new_networks.append(child)
            
            self.networks = survivors + new_networks
            
            if round_num % 10 == 0:
                print(f"   Round {round_num}: Best performance = {self.networks[0]['performance']:.4f}")
        
        print(f"\n✅ Neural Darwinism complete!")
        print(f"   Champion network: {self.networks[0]['id']}")
        
        return self.networks[0]
    
    def _breed_network(self, parent: Dict) -> Dict:
        """تكاثر الشبكة - مع طفرات"""
        child = parent.copy()
        child['id'] = len(self.networks) + random.randint(1000, 9999)
        
        # Mutate layers
        if random.random() < 0.3:
            layer_idx = random.randint(1, len(child['layers']) - 2)
            child['layers'][layer_idx] = random.randint(5, 50)
        
        # Mutate activation
        if random.random() < 0.2:
            child['activation'] = random.choice(['relu', 'sigmoid', 'tanh', 'leaky_relu'])
        
        return child


# Demo
if __name__ == "__main__":
    print("🧬 BIO-INSPIRED SECURITY - DEMO")
    print("="*80)
    
    # 1. Artificial Immune System
    print("\n1️⃣ Artificial Immune System")
    ais = ArtificialImmuneSystem()
    ais.generate_antibodies(n=100)
    
    # Simulate threats
    threat1 = np.random.uniform(0, 1, 20)
    response1 = ais.detect_pathogen(threat1)
    
    # Same threat again - should have memory!
    print("\n🔁 Same threat again...")
    is_known = ais.check_memory(threat1)
    
    # 2. Genetic Algorithm Defense
    print("\n" + "="*80)
    print("2️⃣ Genetic Algorithm Defense")
    ga = GeneticAlgorithmDefense(population_size=100)
    ga.initialize_population()
    
    threat_env = {'type': 'apt', 'sophistication': 0.9}
    best_defense = ga.evolve(threat_env, n_generations=30)
    
    print(f"\n🏆 Best Defense Configuration:")
    print(f"   Genes (first 5): {best_defense['genes'][:5]}")
    print(f"   Fitness: {best_defense['fitness']:.4f}")
    
    # 3. Neural Darwinism
    print("\n" + "="*80)
    print("3️⃣ Neural Darwinism")
    darwin = NeuralDarwinism(n_networks=50)
    darwin.create_network_population()
    
    champion = darwin.compete(n_rounds=30)
    
    print(f"\n🏆 Champion Network:")
    print(f"   ID: {champion['id']}")
    print(f"   Architecture: {champion['layers']}")
    print(f"   Activation: {champion['activation']}")
    print(f"   Performance: {champion['performance']:.4f}")
    
    print("\n🧬 BIO-INSPIRED SECURITY IS AMAZING! 🌟")
