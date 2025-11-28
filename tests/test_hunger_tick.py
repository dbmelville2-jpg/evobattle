"""Ultra-detailed diagnostic"""
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
creature.hunger = 100  # Start full
creature.mature = True

# Create battle
battle = SpatialBattle(
    creatures_or_team1=[creature],
    arena_width=100,
    arena_height=100,
    initial_resources=5
)

bc = battle.creatures[0]
print(f"Before update: hunger={bc.creature.hunger}")

# Single update
battle.update(1.0)  # 1 full second

print(f"After 1s update: hunger={bc.creature.hunger}")
print(f"Expected: ~98.0 (100 - 2.0*1.0)")
print(f"Creature ID match: {bc.creature.creature_id == creature.creature_id}")
print(f"Same object: {bc.creature is creature}")
