import time
import random
from src.models.creature import Creature, CreatureType
from src.models.disease import Disease, DiseaseType, Infection, InfectionStage, DISEASE_DEFINITIONS
from src.systems.disease_system import DiseaseSystem
from src.models.creature import Creature
from src.models.disease import Disease, DiseaseType, Infection, InfectionStage, DISEASE_DEFINITIONS
from src.systems.disease_system import DiseaseSystem
from src.models.spatial import Vector2D

# Mock Spatial Component
class MockSpatial:
    def __init__(self, x, y):
        self.position = Vector2D(x, y)

def test_disease_evolution():
    print("=== Testing Disease Evolution & Immunity ===")
    
    # Setup
    system = DiseaseSystem()
    
    # Create a patient zero
    c1 = Creature(name="Patient Zero")
    # Manually attach spatial mock since Creature doesn't have it by default
    c1.spatial = MockSpatial(100, 100)
    
    # Create a target
    c2 = Creature(name="Target")
    c2.spatial = MockSpatial(105, 105) # Within contagion radius
    
    # Infect patient zero with a mutable disease
    base_disease = DISEASE_DEFINITIONS[DiseaseType.PLAGUE]
    base_disease.mutation_chance = 1.0 # Force mutation for test
    base_disease.transmission_rate = 1.0 # Force transmission for test
    
    system.infect_creature(c1, base_disease)
    print(f"Infected {c1.name} with {base_disease.name} (Gen {base_disease.generation})")
    
    # Force transmission
    # We need to wrap creatures in a mock object if the system expects BattleCreature
    class MockBattleCreature:
        def __init__(self, creature):
            self.creature = creature
            self.spatial = creature.spatial
        def is_alive(self):
            return True
            
    bc1 = MockBattleCreature(c1)
    bc2 = MockBattleCreature(c2)
    
    # Simulate update to trigger transmission
    print("Simulating transmission...")
    system._handle_transmission(1.0, [bc1, bc2], [])
    
    # Check if target got infected
    if c2.active_infection:
        inf = c2.active_infection
        dis = inf.disease
        print(f"SUCCESS: Target infected with {dis.name}")
        print(f"  - Generation: {dis.generation}")
        print(f"  - Parent ID: {dis.parent_id}")
        print(f"  - Transmission Rate: {dis.transmission_rate:.3f} (Base: {base_disease.transmission_rate})")
        
        if dis.generation > base_disease.generation:
            print("  -> Mutation CONFIRMED")
        else:
            print("  -> Mutation FAILED")
    else:
        print("FAILURE: Transmission did not occur")

    # Test Immunity
    print("\n=== Testing Immunity ===")
    c3 = Creature(name="Immune Target")
    c3.spatial = MockSpatial(105, 105)
    c3.base_immunity = 1.0 # 100% immunity
    bc3 = MockBattleCreature(c3)
    
    print(f"Attempting to infect {c3.name} (Immunity: {c3.base_immunity})...")
    system._handle_transmission(1.0, [bc1, bc3], [])
    
    if c3.active_infection:
        print("FAILURE: Immune target was infected!")
    else:
        print("SUCCESS: Immune target resisted infection")
        
    # Test Acquired Immunity
    print("\n=== Testing Acquired Immunity ===")
    c4 = Creature(name="Recovered Target")
    c4.spatial = MockSpatial(105, 105)
    # Grant immunity to specific strain
    c4.immune_memory[base_disease.disease_id] = 1.0
    bc4 = MockBattleCreature(c4)
    
    print(f"Attempting to infect {c4.name} (Acquired Immunity to {base_disease.disease_id})...")
    system._handle_transmission(1.0, [bc1, bc4], [])
    
    if c4.active_infection:
        print("FAILURE: Recovered target was infected!")
    else:
        print("SUCCESS: Recovered target resisted infection")

if __name__ == "__main__":
    test_disease_evolution()
