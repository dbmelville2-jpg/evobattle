"""Quick diagnostic to check if pellet collection is working"""
import sys
sys.path.insert(0, 'c:\\Users\\dbmel\\main')

from src.systems.battle_spatial import SpatialBattle
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ecosystem_traits import FORAGER

# Create a simple test creature
creature_type = CreatureType(base_stats=Stats(max_hp=100, attack=10, defense=10, speed=20))
creature = Creature(name="TestCreature", creature_type=creature_type, level=5)
creature.add_trait(FORAGER)
creature.hunger = 50  # Moderately hungry
creature.mature = True

# Create battle with just one creature
battle = SpatialBattle(
    creatures_or_team1=[creature],
    arena_width=100,
    arena_height=100,
    initial_resources=10
)

print(f"Initial state:")
print(f"  Creature hunger: {creature.hunger}")
print(f"  Pellets in arena: {len(battle.arena.resources)}")
print(f"  Creature position: {battle.creatures[0].spatial.position.to_tuple()}")

# Run for 10 seconds
for i in range(100):  # 100 frames at 0.1s each = 10 seconds
    battle.update(0.1)
    if i % 10 == 0:
        bc = battle.creatures[0]
        print(f"  t={i*0.1:.1f}s: hunger={bc.creature.hunger:.1f}, pellets={len(battle.arena.resources)}, pos={bc.spatial.position.to_tuple()}")

print(f"\nFinal state:")
print(f"  Creature hunger: {battle.creatures[0].creature.hunger}")
print(f"  Pellets remaining: {len(battle.arena.resources)}")
print(f"  Creature alive: {battle.creatures[0].is_alive()}")
