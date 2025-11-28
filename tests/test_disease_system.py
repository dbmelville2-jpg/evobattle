
import sys
import os
import time
import random
from typing import List

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.creature import Creature, CreatureType
from src.models.pellet import Pellet, create_random_pellet
from src.systems.battle_spatial import SpatialBattle, BattleCreature
from src.models.disease import DiseaseType, InfectionStage
from src.systems.disease_system import DiseaseSystem

def test_disease_system():
    print("=== Testing Disease System ===")
    
    # 1. Setup Battle
    print("\n1. Setting up battle environment...")
    creatures = []
    for i in range(20):  # Enough to trigger density check
        c = Creature(
            creature_id=f"c_{i}",
            level=1
        )
        creatures.append(c)
        
    battle = SpatialBattle(
        creatures_or_team1=creatures,
        arena_width=100.0,
        arena_height=100.0,
        enable_environment=False
    )
    
    # Force DiseaseSystem to be present (should be init in battle)
    if not hasattr(battle, 'disease_system'):
        print("ERROR: DiseaseSystem not initialized in SpatialBattle")
        return
        
    ds = battle.disease_system
    print("DiseaseSystem initialized successfully.")
    
    # 2. Test Outbreak Trigger
    print("\n2. Testing Outbreak Trigger...")
    # Manually trigger for test reliability
    ds._trigger_outbreak(DiseaseType.PLAGUE, battle.creatures, is_creature=True)
    
    infected_count = 0
    patient_zero = None
    for bc in battle.creatures:
        if bc.creature.active_infection:
            infected_count += 1
            patient_zero = bc
            print(f"Infected creature found: {bc.creature.name} with {bc.creature.active_infection.disease.name}")
            
    if infected_count == 0:
        print("FAILURE: No outbreak triggered.")
        return
    else:
        print(f"SUCCESS: Outbreak triggered. {infected_count} infected.")

    # 3. Test Transmission
    print("\n3. Testing Transmission...")
    # Move another creature close to patient zero
    target = None
    for bc in battle.creatures:
        if bc != patient_zero:
            target = bc
            break
            
    if target and patient_zero:
        # Force proximity
        target.spatial.position.x = patient_zero.spatial.position.x + 1.0
        target.spatial.position.y = patient_zero.spatial.position.y
        
        # Run updates for a few seconds
        print("Simulating 5 seconds of contact...")
        for _ in range(50): # 50 ticks of 0.1s
            battle.update(0.1)
            if target.creature.active_infection:
                print(f"Transmission successful! Target infected with {target.creature.active_infection.disease.name}")
                break
                
        if not target.creature.active_infection:
            print("WARNING: Transmission did not occur (chance based).")
        else:
            print("SUCCESS: Transmission verified.")
            
    # 4. Test Disease Progression
    print("\n4. Testing Disease Progression...")
    if patient_zero:
        infection = patient_zero.creature.active_infection
        print(f"Initial Stage: {infection.stage.name}")
        
        # Fast forward incubation
        print(f"Fast forwarding {infection.disease.incubation_time + 1} seconds...")
        battle.update(infection.disease.incubation_time + 1.0)
        
        print(f"Current Stage: {infection.stage.name}")
        if infection.stage == InfectionStage.SYMPTOMATIC:
            print("SUCCESS: Disease progressed to SYMPTOMATIC.")
        else:
            print(f"FAILURE: Disease stage is {infection.stage.name}, expected SYMPTOMATIC.")
            
    # 5. Test Pellet Disease
    print("\n5. Testing Pellet Disease...")
    pellet = battle.arena.resources[0]
    from src.models.disease import DISEASE_DEFINITIONS
    ds.infect_pellet(pellet, list(DISEASE_DEFINITIONS.values())[3]) # Blight
    
    if pellet.active_infection:
        print(f"Pellet infected with {pellet.active_infection.disease.name}")
        print("SUCCESS: Pellet infection verified.")
    else:
        # Manual infection might fail if disease list logic above is wonky, let's use direct lookup
        from src.models.disease import DISEASE_DEFINITIONS
        ds.infect_pellet(pellet, DISEASE_DEFINITIONS[DiseaseType.BLIGHT])
        if pellet.active_infection:
             print(f"Pellet infected with {pellet.active_infection.disease.name}")
             print("SUCCESS: Pellet infection verified.")
        else:
             print("FAILURE: Could not infect pellet.")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_disease_system()
