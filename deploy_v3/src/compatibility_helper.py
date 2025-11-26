"""
🔧 Compatibility Helper - adds missing method names
"""

def add_compatibility_methods():
    """Add alias methods to classes for better usability"""
    
    from src.ai.swarm_intelligence import SwarmDefenseCoordinator
    from src.ai.quantum_defense import QuantumDefenseSystem
    from src.ai.bio_inspired import ArtificialImmuneSystem
    
    # Add missing methods as aliases
    SwarmDefenseCoordinator.coordinate_agents = lambda self, state: self.update_swarm(state)
    QuantumDefenseSystem.apply_defense = lambda self, state: self.apply_quantum_defense(state)
    ArtificialImmuneSystem.defend = lambda self, state: self.generate_antibodies(state)
    
    return True
