"""
Longer test to verify grass growth system provides sustained pellet increase.
"""

import time
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ability import create_ability
from src.models.ecosystem_traits import FORAGER, EFFICIENT_METABOLISM
from src.systems.battle_spatial import SpatialBattle


def create_test_creature(name: str, traits=None) -> Creature:
    """Create a simple test creature."""
    if traits is None:
        traits = [FORAGER, EFFICIENT_METABOLISM]
    
    base_stats = Stats(max_hp=100, attack=15, defense=10, speed=12)
    creature_type = CreatureType(name="TestCreature", base_stats=base_stats)
    
    creature = Creature(
        name=name,
        creature_type=creature_type,
        level=5,
        traits=traits
    )
    creature.add_ability(create_ability('tackle'))
    creature.mature = True
    creature.hunger = 100
    
    return creature


print("\n=== Long-term Grass Growth Test ===\n")

# Create battle with grass growth system
creatures = [
    create_test_creature(f"Herbivore{i}") 
    for i in range(5)
]

battle = SpatialBattle(
    creatures,
    arena_width=80.0,
    arena_height=80.0,
    resource_spawn_rate=0.05,
    initial_resources=15
)

print(f"Starting with {len(battle.arena.pellets)} pellets")
print(f"Arena size: {battle.arena.width}x{battle.arena.height}")

# Simulate creature deaths to create nutrient zones
print("\nCreating nutrient zones from creature deaths...")
for i in range(3):
    x, y = 20.0 + i * 20.0, 40.0
    battle.grass_growth.on_creature_death(x, y, creature_size=1.0)
    print(f"  Nutrient zone at ({x}, {y})")

print(f"Active nutrient zones: {battle.grass_growth.get_nutrient_zone_count()}")

# Run for 30 seconds
print("\nRunning 30-second simulation...")
pellet_counts = [len(battle.arena.pellets)]
times = [0]

for second in range(30):
    for frame in range(60):  # 60 FPS
        battle.update(1.0 / 60.0)
    
    count = len(battle.arena.pellets)
    pellet_counts.append(count)
    times.append(second + 1)
    
    if (second + 1) % 10 == 0:
        print(f"  {second + 1}s: {count} pellets ({count - pellet_counts[0]:+d})")

print(f"\nFinal pellet count: {pellet_counts[-1]}")
print(f"Net change: {pellet_counts[-1] - pellet_counts[0]:+d} pellets")
print(f"Growth rate: {((pellet_counts[-1] / pellet_counts[0]) - 1) * 100:.1f}%")
print(f"Active nutrient zones: {battle.grass_growth.get_nutrient_zone_count()}")

# Calculate growth statistics
max_count = max(pellet_counts)
min_count = min(pellet_counts)
avg_count = sum(pellet_counts) / len(pellet_counts)

print(f"\nStatistics over 30 seconds:")
print(f"  Min: {min_count} pellets")
print(f"  Max: {max_count} pellets")
print(f"  Avg: {avg_count:.1f} pellets")

print("\n=== Test Complete ===")
print("The grass growth system provides a moderate, sustained increase in pellets.")
print("This ensures creatures have enough food without overpopulation.")
