"""
Ecosystem Survival Mode Demo

Demonstrates the new survival features:
- Hunger system with metabolic traits
- Resource gathering and foraging behavior
- Trait-driven wandering
- Creatures competing for resources
"""

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.trait import Trait
from src.models.ability import create_ability
from src.systems.battle_spatial import SpatialBattle


def create_ecosystem_creature(name: str, traits: list, level: int = 5) -> Creature:
    """Create a creature for the ecosystem simulation."""
    base_stats = Stats(
        max_hp=80 + (level - 1) * 10,
        attack=12 + (level - 1) * 2,
        defense=10 + (level - 1) * 2,
        speed=15 + (level - 1)
    )
    
    creature_type = CreatureType(
        name=f"{name} Type",
        base_stats=base_stats,
        type_tags=["normal"]
    )
    
    creature = Creature(
        name=name,
        creature_type=creature_type,
        level=level,
        traits=traits
    )
    
    # Add some basic abilities
    creature.add_ability(create_ability('tackle'))
    
    return creature


def main():
    print("=" * 70)
    print("ECOSYSTEM SURVIVAL MODE DEMO")
    print("=" * 70)
    print()
    
    # Create diverse creatures with different traits
    print("Creating ecosystem creatures...")
    print()
    
    # Team 1: Foragers and Efficient creatures
    forager = create_ecosystem_creature(
        "Forager Fox",
        [Trait(name="Forager"), Trait(name="Efficient Metabolism")],
        level=5
    )
    print(f"✓ {forager.name} - Forager + Efficient Metabolism")
    print(f"  Behavior: Seeks resources, slow hunger depletion")
    
    curious_explorer = create_ecosystem_creature(
        "Curious Cat",
        [Trait(name="Curious"), Trait(name="Efficient")],
        level=4
    )
    print(f"✓ {curious_explorer.name} - Curious + Efficient")
    print(f"  Behavior: Wanders and explores, moderate hunger")
    
    glutton = create_ecosystem_creature(
        "Glutton Bear",
        [Trait(name="Glutton")],
        level=6
    )
    print(f"✓ {glutton.name} - Glutton")
    print(f"  Behavior: Fast hunger depletion, HP bonus when eating")
    
    # Team 2: Aggressive and Voracious creatures
    aggressive_hunter = create_ecosystem_creature(
        "Hunter Wolf",
        [Trait(name="Aggressive"), Trait(name="Voracious")],
        level=5
    )
    print(f"✓ {aggressive_hunter.name} - Aggressive + Voracious")
    print(f"  Behavior: Aggressive, fast hunger, heals when eating")
    
    cautious_creature = create_ecosystem_creature(
        "Cautious Rabbit",
        [Trait(name="Cautious")],
        level=4
    )
    print(f"✓ {cautious_creature.name} - Cautious")
    print(f"  Behavior: Avoids conflict, moderate hunger")
    
    wanderer = create_ecosystem_creature(
        "Wanderer Bird",
        [Trait(name="Wanderer"), Trait(name="Efficient Metabolism")],
        level=4
    )
    print(f"✓ {wanderer.name} - Wanderer + Efficient Metabolism")
    print(f"  Behavior: Random exploration, slow hunger")
    
    print()
    print("-" * 70)
    
    # Create battle with resource spawning
    print("\nInitializing ecosystem arena...")
    print(f"Arena size: 100x100")
    print(f"Initial resources: 8 food items")
    print(f"Resource spawn rate: 0.2 per second (1 every 5 seconds)")
    print()
    
    team1 = [forager, curious_explorer, glutton]
    team2 = [aggressive_hunter, cautious_creature, wanderer]
    
    battle = SpatialBattle(
        team1,
        team2,
        arena_width=100.0,
        arena_height=100.0,
        resource_spawn_rate=0.2,  # Spawn resources slowly
        initial_resources=8
    )
    
    print("=" * 70)
    print("SIMULATION START")
    print("=" * 70)
    print()
    
    # Simulate the ecosystem
    time_step = 0.1
    max_time = 60.0  # Run for 60 seconds
    report_interval = 10.0
    next_report = report_interval
    
    print(f"Simulating ecosystem for {max_time} seconds...")
    print(f"Time step: {time_step}s, reporting every {report_interval}s")
    print()
    
    while battle.current_time < max_time and not battle.is_over:
        battle.update(time_step)
        
        # Report status periodically
        if battle.current_time >= next_report:
            print(f"\n--- Time: {battle.current_time:.1f}s ---")
            print(f"Resources available: {len(battle.arena.resources)}")
            
            print("\nTeam 1 Status:")
            for creature in battle.player_creatures:
                if creature.is_alive():
                    status = "ALIVE"
                    hp_pct = (creature.creature.stats.hp / creature.creature.stats.max_hp) * 100
                    hunger_pct = (creature.creature.hunger / creature.creature.max_hunger) * 100
                    print(f"  {creature.creature.name:20s} - {status:8s} | HP: {hp_pct:5.1f}% | Hunger: {hunger_pct:5.1f}%")
                else:
                    print(f"  {creature.creature.name:20s} - FAINTED")
            
            print("\nTeam 2 Status:")
            for creature in battle.enemy_creatures:
                if creature.is_alive():
                    status = "ALIVE"
                    hp_pct = (creature.creature.stats.hp / creature.creature.stats.max_hp) * 100
                    hunger_pct = (creature.creature.hunger / creature.creature.max_hunger) * 100
                    print(f"  {creature.creature.name:20s} - {status:8s} | HP: {hp_pct:5.1f}% | Hunger: {hunger_pct:5.1f}%")
                else:
                    print(f"  {creature.creature.name:20s} - FAINTED")
            
            next_report += report_interval
    
    print()
    print("=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print()
    
    # Final statistics
    alive_team1 = [c for c in battle.player_creatures if c.is_alive()]
    alive_team2 = [c for c in battle.enemy_creatures if c.is_alive()]
    
    print(f"Final Time: {battle.current_time:.1f}s")
    print(f"Resources remaining: {len(battle.arena.resources)}")
    print()
    
    print("Final Status:")
    print(f"  Team 1: {len(alive_team1)}/{len(battle.player_creatures)} survivors")
    print(f"  Team 2: {len(alive_team2)}/{len(battle.enemy_creatures)} survivors")
    print()
    
    if alive_team1 and not alive_team2:
        print("🏆 Team 1 wins!")
    elif alive_team2 and not alive_team1:
        print("🏆 Team 2 wins!")
    elif alive_team1 and alive_team2:
        print("🤝 Both teams survived!")
    else:
        print("💀 All creatures perished!")
    
    print()
    print("=" * 70)
    print("KEY EVENTS FROM BATTLE LOG")
    print("=" * 70)
    
    # Show interesting events
    interesting_events = [
        log for log in battle.battle_log
        if any(keyword in log.lower() for keyword in ['starved', 'ate', 'food', 'fainted'])
    ]
    
    for event in interesting_events[-20:]:  # Show last 20 interesting events
        print(f"  {event}")
    
    print()
    print("=" * 70)
    print()
    print("Ecosystem features demonstrated:")
    print("  ✓ Hunger system with metabolic traits")
    print("  ✓ Resource spawning and collection")
    print("  ✓ Foraging behavior (prioritizing food when hungry)")
    print("  ✓ Trait-driven behavior diversity")
    print("  ✓ Survival mechanics (starvation)")
    print()
    print("Try running with different trait combinations!")
    print()


if __name__ == "__main__":
    main()
