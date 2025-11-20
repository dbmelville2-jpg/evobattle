"""Test growth WITHOUT nutrient zones to see baseline."""
import time
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ability import create_ability
from src.models.ecosystem_traits import FORAGER
from src.systems.battle_spatial import SpatialBattle

def create_test_creature(name: str) -> Creature:
    base_stats = Stats(max_hp=100, attack=15, defense=10, speed=12)
    creature_type = CreatureType(name="Test", base_stats=base_stats)
    creature = Creature(name=name, creature_type=creature_type, level=5, traits=[FORAGER])
    creature.add_ability(create_ability('tackle'))
    creature.mature = True
    creature.hunger = 100
    return creature

creatures = [create_test_creature(f"C{i}") for i in range(5)]
battle = SpatialBattle(creatures, arena_width=80.0, arena_height=80.0, resource_spawn_rate=0.05, initial_resources=15)

# Disable nutrient zones for baseline
battle.grass_growth.enable_nutrient_zones = False

print(f"Starting: {len(battle.arena.pellets)} pellets (NO nutrient zones)")

for second in range(30):
    for frame in range(60):
        battle.update(1.0 / 60.0)
    if (second + 1) % 10 == 0:
        print(f"{second + 1}s: {len(battle.arena.pellets)} pellets")

final = len(battle.arena.pellets)
print(f"\nFinal: {final} pellets")
print(f"Growth: {((final / 15) - 1) * 100:.1f}%")
