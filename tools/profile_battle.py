import cProfile
import pstats
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.getcwd()))

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.systems.battle_spatial import SpatialBattle

def profile_battle():
    print("Initializing Battle...")
    creature_type = CreatureType(
        name="TestType",
        base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10),
        stat_growth=StatGrowth()
    )
    # 200 creatures
    creatures = [Creature(name=f"c{i}", creature_type=creature_type, level=5) for i in range(200)]
    
    battle = SpatialBattle(creatures, arena_width=500, arena_height=500)
    
    # Warmup
    print("Warming up...")
    for _ in range(10):
        battle.update(0.1)
        
    print("Profiling 100 frames...")
    profiler = cProfile.Profile()
    profiler.enable()
    
    for _ in range(100):
        battle.update(0.016)
        
    profiler.disable()
    
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(20) # Top 20 cumulative time
    
    print("\n--- Top functions by self time (CPU heavy) ---")
    stats.sort_stats('tottime')
    stats.print_stats(20)

if __name__ == "__main__":
    profile_battle()
