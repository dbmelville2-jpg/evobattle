
import sys
import os
import time
import random
from typing import List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.systems.battle_spatial import SpatialBattle, BattleCreature
from src.models.creature import Creature
from src.models.stats import Stats
from src.models.spatial import Vector2D

def run_combat_debug():
    print("Initializing combat debug...")
    
    # Create two teams of creatures
    team1 = []
    team2 = []
    
    # Team 1: Aggressive
    for i in range(10):
        stats = Stats(hp=100, max_hp=100, attack=20, defense=10, speed=10)
        creature = Creature(name=f"Ally_{i}", base_stats=stats)
        # Add aggressive trait
        from src.models.trait import Trait
        creature.traits.append(Trait(name="Aggressive", description="Attacks enemies"))
        team1.append(creature)
        
    # Team 2: Dummy targets
    for i in range(5):
        stats = Stats(hp=500, max_hp=500, attack=5, defense=5, speed=5)
        creature = Creature(name=f"Enemy_{i}", base_stats=stats)
        team2.append(creature)
    
    # Initialize battle
    battle = SpatialBattle(
        creatures_or_team1=team1 + team2,
        arena_width=100,
        arena_height=100
    )
    
    # Position them close to each other
    for bc in battle._creatures:
        if "Ally" in bc.creature.name:
            bc.spatial.position = Vector2D(40 + random.uniform(-5, 5), 50 + random.uniform(-5, 5))
        else:
            bc.spatial.position = Vector2D(60 + random.uniform(-2, 2), 50 + random.uniform(-2, 2))
            
    print("Starting simulation...")
    
    total_attacks = 0
    frames = 200
    
    for i in range(frames):
        battle.update(0.016)  # 60 FPS
        
        # Count attacks (check events)
        new_attacks = len([e for e in battle.events if e.event_type.value == "ability_use" and e.timestamp > time.time() - 0.02])
        total_attacks += new_attacks
        
        # Log positions and states every 20 frames
        if i % 20 == 0:
            engaged_count = len([c for c in battle._creatures if c.combat_engaged])
            avg_dist = 0
            ally_count = 0
            for c in battle._creatures:
                if "Ally" in c.creature.name and c.target:
                    avg_dist += c.spatial.distance_to(c.target.spatial)
                    ally_count += 1
            
            if ally_count > 0:
                avg_dist /= ally_count
                
            print(f"Frame {i}: Engaged={engaged_count}, AvgDistToTarget={avg_dist:.2f}, Attacks={total_attacks}")
            
    print(f"Simulation finished. Total attacks: {total_attacks}")
    
    # Print last 20 battle log entries
    print("\n=== Last 20 Battle Log Entries ===")
    for entry in battle.battle_log[-20:]:
        print(entry)

if __name__ == "__main__":
    run_combat_debug()
