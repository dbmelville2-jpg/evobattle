import time
from main import create_unified_battle, create_creature
from src.models.creature import Creature
from src.models.disease import DiseaseType, DISEASE_DEFINITIONS
from src.systems.disease_system import DiseaseSystem
from src.systems.battle_spatial import BattleCreature
from src.models.spatial import Vector2D
import random

def spawn_creature(battle):
    """Helper to spawn a creature manually."""
    creature = create_creature(f"SimBorn_{random.randint(1000,9999)}", level=random.randint(1, 5))
    x = random.uniform(0, battle.arena.width)
    y = random.uniform(0, battle.arena.height)
    position = Vector2D(x, y)
    battle_creature = BattleCreature(creature, position)
    
    # Add to battle lists
    battle._creatures.append(battle_creature)
    battle.creature_grid.insert(battle_creature, position)
    
    # Trigger spawn event
    if hasattr(battle, 'enhancer') and battle.enhancer:
        battle.enhancer.on_battle_start([creature]) # Partial init

def run_long_simulation(duration_seconds=300, time_scale=5.0):
    print(f"=== Starting Long Simulation ({duration_seconds}s, {time_scale}x speed) ===")
    
    # Initialize Battle
    battle = create_unified_battle()
    
    # Setup initial state
    # Ensure we have enough creatures
    while len(battle.creatures) < 50:
        spawn_creature(battle)
        
    # Force an initial outbreak
    patient_zero = battle.creatures[0]
    disease = DISEASE_DEFINITIONS[DiseaseType.PLAGUE]
    battle.disease_system.infect_creature(patient_zero.creature, disease)
    print(f"Outbreak started: {patient_zero.creature.name} infected with {disease.name}")
    
    # Simulation Loop
    start_time = time.time()
    sim_time = 0.0
    step_size = 0.016 # 60 FPS
    
    stats_log_interval = 10.0 # Log every 10 sim seconds
    next_log_time = 10.0
    
    try:
        while time.time() - start_time < duration_seconds:
            # Update battle
            # We simulate faster by running multiple steps per real second if needed,
            # but here we just rely on the loop speed.
            
            # Apply time scale
            dt = step_size * time_scale
            
            battle.update(dt)
            sim_time += dt
            
            # Logging
            if sim_time >= next_log_time:
                alive = sum(1 for c in battle.creatures if c.is_alive())
                infected = sum(1 for c in battle.creatures if c.is_alive() and c.creature.active_infection)
                inf_rate = (infected / alive * 100) if alive > 0 else 0
                
                # Count strains
                strains = set()
                for c in battle.creatures:
                    if c.is_alive() and c.creature.active_infection:
                        strains.add(c.creature.active_infection.disease.disease_id)
                
                print(f"[T={sim_time:.1f}s] Pop: {alive} | Infected: {infected} ({inf_rate:.1f}%) | Active Strains: {len(strains)}")
                
                # Check for extinction
                if alive == 0:
                    print("!!! EXTINCTION EVENT !!!")
                    break
                    
                next_log_time += stats_log_interval
                
                # Keep population up if it drops too low (to test long term evolution, not extinction)
                if alive < 20:
                    spawn_creature(battle)
                
    except KeyboardInterrupt:
        print("Simulation stopped by user.")
        
    print("=== Simulation Complete ===")
    
    # Final Report
    print("\nFinal Stats:")
    alive = sum(1 for c in battle.creatures if c.is_alive())
    print(f"Survivors: {alive}")
    
    # Strain Analysis
    strain_counts = {}
    for c in battle.creatures:
        if c.is_alive() and c.creature.active_infection:
            d = c.creature.active_infection.disease
            name = f"{d.name} (G{d.generation})"
            strain_counts[name] = strain_counts.get(name, 0) + 1
            
    print("\nDominant Strains:")
    for name, count in sorted(strain_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {name}: {count}")

if __name__ == "__main__":
    # Run for 30 real seconds at 10x speed = 300 sim seconds
    run_long_simulation(duration_seconds=30, time_scale=10.0)
