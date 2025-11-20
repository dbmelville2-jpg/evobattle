"""
Quick test to verify grass growth integration and pellet collection.
"""
import sys
sys.path.insert(0, 'src')

from models.creature import Creature
from models.stats import Stats
from models.trait import Trait
from systems.battle_spatial import SpatialBattle
from models.environment import Environment

# Create test creatures
creature1 = Creature(
    name="Herbivore1",
    stats=Stats(max_hp=100, hp=100, attack=10, defense=10, speed=15),
    traits=[Trait(name="Forager", description="Seeks food", trait_type="behavioral")]
)

creature2 = Creature(
    name="Herbivore2",
    stats=Stats(max_hp=100, hp=100, attack=10, defense=10, speed=15),
    traits=[Trait(name="Forager", description="Seeks food", trait_type="behavioral")]
)

# Create battle with environment
env = Environment(width=100, height=100, enable_weather=True, enable_day_night=True)
battle = SpatialBattle(
    creatures_or_team1=[creature1, creature2],
    arena_width=100,
    arena_height=100,
    initial_resources=10,
    resource_spawn_rate=0.5,
    environment=env,
    enable_environment=True
)

print("=" * 60)
print("GRASS GROWTH INTEGRATION TEST")
print("=" * 60)

# Check grass growth system initialized
print(f"\n✓ Grass growth system initialized: {battle.grass_growth is not None}")
print(f"  - Pollination enabled: {battle.grass_growth.enable_pollination}")
print(f"  - Nutrient zones enabled: {battle.grass_growth.enable_nutrient_zones}")
print(f"  - Growth pulses enabled: {battle.grass_growth.enable_growth_pulses}")
print(f"  - Symbiotic bonus enabled: {battle.grass_growth.enable_symbiotic_bonus}")

# Check initial state
print(f"\n✓ Initial state:")
print(f"  - Creatures: {len(battle.creatures)}")
print(f"  - Pellets: {len(battle.arena.pellets)}")
print(f"  - Total resources: {len(battle.arena.resources)}")

# Run simulation for a few seconds
print(f"\n✓ Running simulation for 5 seconds...")
for i in range(300):  # 5 seconds at 60 FPS
    battle.update(1/60)
    
    # Print status every second
    if i % 60 == 0:
        pellet_count = len(battle.arena.pellets)
        nutrient_zones = battle.grass_growth.get_nutrient_zone_count()
        pulse_active = battle.grass_growth.is_growth_pulse_active()
        
        print(f"  Second {i//60}: Pellets={pellet_count}, Nutrient zones={nutrient_zones}, Growth pulse={'YES' if pulse_active else 'no'}")

# Check final state
print(f"\n✓ Final state:")
print(f"  - Creatures alive: {len([c for c in battle.creatures if c.is_alive()])}")
print(f"  - Pellets: {len(battle.arena.pellets)}")
print(f"  - Nutrient zones: {battle.grass_growth.get_nutrient_zone_count()}")

# Check events
pellet_events = [e for e in battle.events if 'PELLET' in e.event_type.value]
print(f"\n✓ Pellet events:")
print(f"  - Total pellet events: {len(pellet_events)}")
print(f"  - Pellet consumed: {len([e for e in pellet_events if e.event_type.value == 'pellet_consumed'])}")
print(f"  - Pellet reproduce: {len([e for e in pellet_events if e.event_type.value == 'pellet_reproduce'])}")
print(f"  - Pellet spawn: {len([e for e in pellet_events if e.event_type.value == 'pellet_spawn'])}")

print("\n" + "=" * 60)
print("TEST COMPLETE!")
print("=" * 60)
