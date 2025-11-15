"""
Battle System Example - Demonstrates the turn-based battle mechanics.

This example shows how to use the turn-based battle system including:
- Creating creatures with abilities
- Simulating battles
- Type effectiveness
- Status effects
- Battle logging

Note: This uses the turn-based battle system for demonstration.
"""

import sys
import os
# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability, Ability, AbilityType
from src.models.trait import Trait
from src.models.status_effect import create_status_effect
from src.systems.battle_turnbased_backup import Battle


def create_fire_dragon():
    """Create a fire dragon creature."""
    dragon_type = CreatureType(
        name="Fire Dragon",
        description="A powerful dragon that breathes fire",
        base_stats=Stats(max_hp=120, attack=18, defense=12, speed=14),
        stat_growth=StatGrowth(hp_growth=12.0, attack_growth=2.5),
        type_tags=["fire", "flying"],
        evolution_stage=2
    )
    
    dragon = Creature(
        name="Blaze",
        creature_type=dragon_type,
        level=10
    )
    
    # Add abilities
    dragon.add_ability(create_ability('tackle'))
    dragon.add_ability(create_ability('fireball'))
    dragon.add_ability(create_ability('power_up'))
    
    # Add traits
    dragon.add_trait(Trait(
        name="Fire Affinity",
        description="Enhanced fire attacks",
        trait_type="offensive",
        strength_modifier=1.2
    ))
    
    return dragon


def create_water_serpent():
    """Create a water serpent creature."""
    serpent_type = CreatureType(
        name="Water Serpent",
        description="A swift serpent that controls water",
        base_stats=Stats(max_hp=100, attack=16, defense=14, speed=18),
        stat_growth=StatGrowth(hp_growth=10.0, attack_growth=2.0, speed_growth=2.5),
        type_tags=["water"],
        evolution_stage=2
    )
    
    serpent = Creature(
        name="Aqua",
        creature_type=serpent_type,
        level=10
    )
    
    # Add abilities
    serpent.add_ability(create_ability('tackle'))
    serpent.add_ability(create_ability('quick_strike'))
    serpent.add_ability(create_ability('defense_break'))
    
    # Add traits
    serpent.add_trait(Trait(
        name="Hydro Body",
        description="Enhanced defense in water",
        trait_type="defensive",
        defense_modifier=1.15
    ))
    
    return serpent


def example_basic_battle():
    """Demonstrate a basic 1v1 battle."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Battle")
    print("=" * 60)
    
    # Create creatures
    dragon = create_fire_dragon()
    serpent = create_water_serpent()
    
    print(f"\nPlayer: {dragon.name} ({dragon.creature_type.name})")
    print(f"  HP: {dragon.stats.hp}/{dragon.stats.max_hp}")
    print(f"  Attack: {dragon.stats.attack}, Defense: {dragon.stats.defense}, Speed: {dragon.stats.speed}")
    print(f"  Abilities: {', '.join(a.name for a in dragon.abilities)}")
    print(f"  Type: {', '.join(dragon.creature_type.type_tags)}")
    
    print(f"\nEnemy: {serpent.name} ({serpent.creature_type.name})")
    print(f"  HP: {serpent.stats.hp}/{serpent.stats.max_hp}")
    print(f"  Attack: {serpent.stats.attack}, Defense: {serpent.stats.defense}, Speed: {serpent.stats.speed}")
    print(f"  Abilities: {', '.join(a.name for a in serpent.abilities)}")
    print(f"  Type: {', '.join(serpent.creature_type.type_tags)}")
    
    # Create and run battle
    battle = Battle([dragon], [serpent], random_seed=42)
    winner = battle.simulate()
    
    # Display results
    print("\n" + "=" * 60)
    print("BATTLE LOG")
    print("=" * 60)
    for log_entry in battle.get_battle_log():
        print(log_entry)
    
    print("\n" + "=" * 60)
    print(f"WINNER: {winner.name}")
    print(f"Remaining HP: {winner.stats.hp}/{winner.stats.max_hp}")
    print("=" * 60)


def example_type_effectiveness():
    """Demonstrate type effectiveness in battle."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Type Effectiveness")
    print("=" * 60)
    
    # Fire vs Water (not effective)
    print("\n--- Fire Dragon vs Water Serpent ---")
    dragon = create_fire_dragon()
    serpent = create_water_serpent()
    
    battle1 = Battle([dragon], [serpent], random_seed=123)
    winner1 = battle1.simulate()
    
    print(f"\nWinner: {winner1.name}")
    print(f"Note: Fire is not very effective against Water!")
    
    # Create grass type
    grass_type = CreatureType(
        name="Grass Warrior",
        base_stats=Stats(max_hp=110, attack=14, defense=16, speed=10),
        type_tags=["grass"]
    )
    grass = Creature(name="Verdant", creature_type=grass_type, level=10)
    grass.add_ability(create_ability('tackle'))
    
    # Fire vs Grass (super effective)
    print("\n--- Fire Dragon vs Grass Warrior ---")
    dragon2 = create_fire_dragon()
    
    battle2 = Battle([dragon2], [grass], random_seed=456)
    winner2 = battle2.simulate()
    
    print(f"\nWinner: {winner2.name}")
    print(f"Note: Fire is super effective against Grass!")


def example_team_battle():
    """Demonstrate team battle with multiple creatures."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Team Battle")
    print("=" * 60)
    
    # Create player team
    dragon = create_fire_dragon()
    
    warrior_type = CreatureType(
        name="Warrior",
        base_stats=Stats(max_hp=130, attack=20, defense=15, speed=12),
        type_tags=["fighter"]
    )
    warrior = Creature(name="Ares", creature_type=warrior_type, level=10)
    warrior.add_ability(create_ability('tackle'))
    warrior.add_ability(create_ability('power_up'))
    
    # Create enemy team
    serpent = create_water_serpent()
    
    mage_type = CreatureType(
        name="Mage",
        base_stats=Stats(max_hp=90, attack=22, defense=10, speed=16),
        type_tags=["psychic"]
    )
    mage = Creature(name="Mystic", creature_type=mage_type, level=10)
    mage.add_ability(create_ability('fireball'))
    mage.add_ability(create_ability('heal'))
    
    print(f"\nPlayer Team: {dragon.name} & {warrior.name}")
    print(f"Enemy Team: {serpent.name} & {mage.name}")
    
    # Run battle
    battle = Battle([dragon, warrior], [serpent, mage], random_seed=789)
    winner = battle.simulate()
    
    print("\n" + "=" * 60)
    print(f"WINNER: {winner.name}")
    print("=" * 60)


def example_abilities_and_effects():
    """Demonstrate different ability types and effects."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 4: Abilities and Effects")
    print("=" * 60)
    
    # Create healer
    healer_type = CreatureType(
        name="Healer",
        base_stats=Stats(max_hp=100, attack=10, defense=12, speed=14),
        type_tags=["normal"]
    )
    healer = Creature(name="Cleric", creature_type=healer_type, level=10)
    healer.add_ability(create_ability('tackle'))
    healer.add_ability(create_ability('heal'))
    
    # Create buffer
    buffer_type = CreatureType(
        name="Buffer",
        base_stats=Stats(max_hp=110, attack=15, defense=10, speed=12),
        type_tags=["normal"]
    )
    buffer = Creature(name="Sage", creature_type=buffer_type, level=10)
    buffer.add_ability(create_ability('power_up'))
    buffer.add_ability(create_ability('defense_break'))
    buffer.add_ability(create_ability('tackle'))
    
    print(f"\n{healer.name} has healing abilities")
    print(f"{buffer.name} has buff/debuff abilities")
    
    # Battle with strategic abilities
    battle = Battle([healer], [buffer], random_seed=101)
    winner = battle.simulate()
    
    # Show key moments from log
    print("\nKey Battle Moments:")
    for log in battle.get_battle_log():
        if 'heal' in log.lower() or 'increased' in log.lower() or 'decreased' in log.lower():
            print(f"  {log}")
    
    print(f"\nWinner: {winner.name}")


def example_battle_statistics():
    """Demonstrate battle statistics and analysis."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 5: Battle Statistics")
    print("=" * 60)
    
    dragon = create_fire_dragon()
    serpent = create_water_serpent()
    
    # Run battle
    battle = Battle([dragon], [serpent], random_seed=2024)
    winner = battle.simulate()
    
    # Analyze battle
    log = battle.get_battle_log()
    
    print("\nBattle Statistics:")
    print(f"  Total Turns: {battle.state.current_turn}")
    print(f"  Total Actions: {len([l for l in log if 'uses' in l])}")
    print(f"  Critical Hits: {len([l for l in log if 'Critical' in l])}")
    print(f"  Super Effective Hits: {len([l for l in log if 'super effective' in l])}")
    print(f"  Misses: {len([l for l in log if 'missed' in l])}")
    
    print(f"\nFinal State:")
    print(f"  Winner: {winner.name}")
    print(f"  Winner HP: {winner.stats.hp}/{winner.stats.max_hp}")
    
    loser = serpent if winner == dragon else dragon
    print(f"  Loser: {loser.name}")
    print(f"  Loser HP: {loser.stats.hp}/{loser.stats.max_hp}")


if __name__ == "__main__":
    # Run all examples
    example_basic_battle()
    example_type_effectiveness()
    example_team_battle()
    example_abilities_and_effects()
    example_battle_statistics()
    
    print("\n\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
