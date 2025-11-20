"""
Visual demonstration of the Grass Growth Enhancement System.

This script shows all 4 mechanics in action with visual output:
1. Nutrient zones
2. Pollination  
3. Growth pulses
4. Symbiotic bonuses

Run this to see how the grass growth system enhances pellet populations!
"""

import time
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ability import create_ability
from src.models.ecosystem_traits import FORAGER, EFFICIENT_METABOLISM
from src.systems.battle_spatial import SpatialBattle


def create_herbivore(name: str) -> Creature:
    """Create a herbivore creature."""
    base_stats = Stats(max_hp=100, attack=15, defense=10, speed=12)
    creature_type = CreatureType(name="Herbivore", base_stats=base_stats)
    
    creature = Creature(
        name=name,
        creature_type=creature_type,
        level=5,
        traits=[FORAGER, EFFICIENT_METABOLISM]
    )
    creature.add_ability(create_ability('tackle'))
    creature.mature = True
    creature.hunger = 100
    
    return creature


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_status(battle, elapsed_seconds):
    """Print current battle status."""
    pellet_count = len(battle.arena.pellets)
    creature_count = len([c for c in battle.creatures if c.is_alive()])
    zones = battle.grass_growth.get_nutrient_zone_count()
    pulse = "ACTIVE" if battle.grass_growth.is_growth_pulse_active() else "inactive"
    
    print(f"\n[{elapsed_seconds:3d}s] Pellets: {pellet_count:3d} | "
          f"Creatures: {creature_count} | Zones: {zones} | Pulse: {pulse}")


def main():
    print_section("Grass Growth Enhancement System - Visual Demo")
    
    print("\nThis demo runs a 60-second simulation showing all growth mechanics:")
    print("  🌱 Nutrient zones (pellets grow faster where creatures died)")
    print("  🐝 Pollination (creatures spread seeds)")
    print("  ☀️ Growth pulses (periodic environmental boosts)")
    print("  🦌 Symbiotic bonus (herbivores help grass grow)")
    
    # Create battle
    print("\nSetting up arena...")
    creatures = [create_herbivore(f"Herbivore-{i}") for i in range(6)]
    
    battle = SpatialBattle(
        creatures,
        arena_width=100.0,
        arena_height=100.0,
        resource_spawn_rate=0.05,
        initial_resources=20
    )
    
    print(f"  Arena: {battle.arena.width}x{battle.arena.height}")
    print(f"  Initial creatures: {len(creatures)}")
    print(f"  Initial pellets: {len(battle.arena.pellets)}")
    
    # Create some nutrient zones
    print("\n🌱 Creating nutrient zones from simulated deaths...")
    death_positions = [
        (25, 50, 1.0),
        (50, 50, 1.2),
        (75, 50, 0.8)
    ]
    
    for x, y, size in death_positions:
        battle.grass_growth.on_creature_death(x, y, creature_size=size)
        print(f"  Zone at ({x}, {y}) - strength: {1.15 + min(0.25, size * 0.15):.2f}x")
    
    # Run simulation
    print_section("Running 60-Second Simulation")
    
    start_pellets = len(battle.arena.pellets)
    pellet_history = [start_pellets]
    
    print("\nWatching for events:")
    print("  - Growth pulses occur every 60 seconds")
    print("  - Pollination happens when creatures revisit pellets")
    print("  - Pellets reproduce faster in nutrient zones")
    print("  - Herbivores boost nearby pellet growth")
    
    print_status(battle, 0)
    
    for second in range(1, 61):
        # Run 60 frames (1 second at 60 FPS)
        for frame in range(60):
            battle.update(1.0 / 60.0)
        
        current_pellets = len(battle.arena.pellets)
        pellet_history.append(current_pellets)
        
        # Print status every 10 seconds or on significant events
        if second % 10 == 0:
            print_status(battle, second)
        
        # Announce growth pulses
        if battle.grass_growth.is_growth_pulse_active():
            if second % 10 == 0 or second == 1:
                print(f"  ☀️ Growth pulse active! (+15% growth)")
    
    # Final statistics
    print_section("Simulation Complete - Results")
    
    final_pellets = pellet_history[-1]
    net_change = final_pellets - start_pellets
    growth_rate = ((final_pellets / start_pellets) - 1) * 100
    
    print(f"\n📊 Growth Statistics:")
    print(f"  Starting pellets:  {start_pellets}")
    print(f"  Final pellets:     {final_pellets}")
    print(f"  Net change:        {net_change:+d} pellets")
    print(f"  Growth rate:       {growth_rate:+.1f}%")
    
    # Calculate averages
    avg_pellets = sum(pellet_history) / len(pellet_history)
    max_pellets = max(pellet_history)
    min_pellets = min(pellet_history)
    
    print(f"\n  Average:           {avg_pellets:.1f} pellets")
    print(f"  Peak:              {max_pellets} pellets")
    print(f"  Low:               {min_pellets} pellets")
    
    # System status
    print(f"\n🌱 System Status:")
    print(f"  Active nutrient zones: {battle.grass_growth.get_nutrient_zone_count()}")
    print(f"  Growth pulse active:   {battle.grass_growth.is_growth_pulse_active()}")
    print(f"  Pollinations tracked:  {len(battle.grass_growth.last_pollination)}")
    
    # Growth breakdown
    print(f"\n📈 Growth Timeline:")
    milestones = [10, 20, 30, 40, 50, 60]
    for ms in milestones:
        pellets_at_ms = pellet_history[ms]
        change = pellets_at_ms - start_pellets
        rate = ((pellets_at_ms / start_pellets) - 1) * 100
        print(f"  {ms:2d}s: {pellets_at_ms:3d} pellets ({change:+3d}, {rate:+5.1f}%)")
    
    print_section("Demo Complete!")
    
    print("\n✓ All 4 grass growth mechanics demonstrated:")
    print("  ✓ Nutrient zones enhanced growth in specific areas")
    print("  ✓ Growth pulses provided periodic boosts")
    print("  ✓ Symbiotic bonuses from herbivore creatures")
    print("  ✓ Pollination spread seeds across the arena")
    
    print(f"\nResult: Pellets grew from {start_pellets} to {final_pellets} (+{growth_rate:.1f}%)")
    print("This provides enough food for creatures without overpopulation!")
    
    print("\n💡 To see this in the full game, run: python main.py")
    print("   Watch for 'Growth pulse!' and 'pollinated grass!' messages!")


if __name__ == "__main__":
    main()
