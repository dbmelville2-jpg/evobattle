"""Test with 30 creatures like the real game"""
import sys
sys.path.insert(0, 'c:\\Users\\dbmel\\main')

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ecosystem_traits import FORAGER, AGGRESSIVE
from src.systems.battle_spatial import SpatialBattle
import random

# Create 30 creatures like the real game
creatures = []
for i in range(30):
    creature_type = CreatureType(base_stats=Stats(max_hp=100, attack=15, defense=10, speed=20))
    creature = Creature(name=f"Creature{i}", creature_type=creature_type, level=5)
    creature.add_trait(random.choice([FORAGER, AGGRESSIVE]))
    creature.hunger = 80
    creature.mature = True
    creatures.append(creature)

battle = SpatialBattle(
    creatures_or_team1=creatures,
    arena_width=200,
    arena_height=200,
    initial_resources=20
)

print(f"Initial: {len([c for c in battle.creatures if c.is_alive()])} alive, {len(battle.arena.resources)} pellets")

# Run for 10 seconds
for i in range(100):
    battle.update(0.1)
    if i % 20 == 0:
        alive = len([c for c in battle.creatures if c.is_alive()])
        avg_hunger = sum(c.creature.hunger for c in battle.creatures if c.is_alive()) / max(1, alive)
        moving = sum(1 for c in battle.creatures if c.is_alive() and c.spatial.velocity.magnitude() > 0.1)
        print(f"t={i*0.1:.1f}s: {alive} alive, avg_hunger={avg_hunger:.1f}, {moving} moving, {len(battle.arena.resources)} pellets")

alive = [c for c in battle.creatures if c.is_alive()]
print(f"\nFinal: {len(alive)} alive")
if alive:
    print(f"Sample creature hunger: {alive[0].creature.hunger:.1f}")
    print(f"Sample creature position: {alive[0].spatial.position.to_tuple()}")
