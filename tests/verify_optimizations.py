import sys
import os
import time
import pygame

# Add project root to path
sys.path.append(os.path.abspath("c:/Users/dbmel/main"))

from src.systems.battle_spatial import SpatialBattle, BattleCreature
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.rendering.creature_renderer import CreatureRenderer

def test_optimization_stability():
    print("Initializing test...")
    
    # Create dummy creature type
    c_type = CreatureType(
        name="TestType",
        description="Test Type",
        base_stats=Stats(hp=100, max_hp=100, attack=10, defense=5, speed=10)
    )
    
    # Create dummy creatures
    creatures = []
    for i in range(50):
        stats = Stats(hp=100, max_hp=100, attack=10, defense=5, speed=10)
        c = Creature(
            creature_id=f"c{i}", 
            name=f"Creature {i}", 
            creature_type=c_type,
            level=1,
            experience=0,
            base_stats=stats,
            abilities=[],
            traits=[]
        )
        creatures.append(c)
        
    # Initialize battle
    battle = SpatialBattle(creatures_or_team1=creatures, arena_width=1000, arena_height=800)
    print(f"Battle initialized with {len(creatures)} creatures.")
    
    # Initialize renderer
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    renderer = CreatureRenderer()
    
    # Run simulation loop
    print("Running simulation loop...")
    start_time = time.time()
    frames = 0
    
    try:
        for i in range(100):
            # Update battle
            battle.update(0.016)  # Simulate 60 FPS
            
            # Render (headless-ish, but calling the code)
            renderer.render(screen, battle)
            
            frames += 1
            if i % 20 == 0:
                print(f"Frame {i} completed.")
                
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    end_time = time.time()
    duration = end_time - start_time
    fps = frames / duration
    print(f"Simulation finished. {frames} frames in {duration:.2f}s ({fps:.1f} FPS)")
    print("Stability check passed.")
    return True

if __name__ == "__main__":
    success = test_optimization_stability()
    sys.exit(0 if success else 1)
