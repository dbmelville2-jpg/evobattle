"""Enhanced diagnostic to trace movement decisions"""
import sys
sys.path.insert(0, 'c:\\Users\\dbmel\\main')

from src.systems.battle_spatial import SpatialBattle
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ecosystem_traits import FORAGER

# Enable debug mode
SpatialBattle.DEBUG = True

# Create a simple test creature
creature_type = CreatureType(base_stats=Stats(max_hp=100, attack=10, defense=10, speed=20))
creature = Creature(name="TestCreature", creature_type=creature_type, level=5)
creature.add_trait(FORAGER)
creature.hunger = 30  # Hungry enough to forage
creature.mature = True

# Create battle with just one creature
battle = SpatialBattle(
    creatures_or_team1=[creature],
    arena_width=100,
    arena_height=100,
    initial_resources=5
)

print(f"Initial state:")
print(f"  Creature hunger: {creature.hunger}")
print(f"  Pellets in arena: {len(battle.arena.resources)}")
bc = battle.creatures[0]
print(f"  Creature position: {bc.spatial.position.to_tuple()}")
print(f"  Has attention: {hasattr(bc, 'attention')}")
if hasattr(bc, 'attention'):
    print(f"  Current focus: {bc.attention.get_current_focus()}")

# Run for 5 seconds
for i in range(50):
    battle.update(0.1)
    if i % 5 == 0:
        bc = battle.creatures[0]
        focus = bc.attention.get_current_focus() if hasattr(bc, 'attention') else "NO_ATTENTION"
        print(f"  t={i*0.1:.1f}s: hunger={bc.creature.hunger:.1f}, focus={focus}, movement_target={bc.current_movement_target}, pos={bc.spatial.position.to_tuple()}")

print(f"\nFinal state:")
print(f"  Creature hunger: {battle.creatures[0].creature.hunger}")
print(f"  Creature alive: {battle.creatures[0].is_alive()}")
