"""
Example usage of EvoBattle core game models.

This script demonstrates the key features of the core models:
- Creating creatures with types and stats
- Adding abilities and traits
- Leveling up and stat growth
- Evolution system
- Breeding and genetics
- Serialization and persistence
"""

import json
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatModifier, StatGrowth
from src.models.ability import Ability, AbilityType, create_ability
from src.models.trait import Trait
from src.models.evolution import EvolutionPath, EvolutionSystem, GeneticsSystem


def print_separator(title=""):
    """Print a visual separator."""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print("-" * 60)


def example_1_creature_creation():
    """Example 1: Creating creatures with types and abilities."""
    print_separator("Example 1: Creature Creation")
    
    # Define a creature type
    warrior_type = CreatureType(
        name="Warrior",
        description="A strong melee fighter",
        base_stats=Stats(max_hp=120, hp=120, attack=15, defense=12, speed=10),
        stat_growth=StatGrowth(
            hp_growth=12.0,
            attack_growth=2.5,
            defense_growth=2.0,
            speed_growth=1.5,
            growth_curve="medium_fast"
        ),
        type_tags=["fighter", "melee"],
        evolution_stage=0
    )
    
    # Create a creature
    fighter = Creature(
        name="Ares",
        creature_type=warrior_type,
        level=1
    )
    
    # Add abilities
    fighter.add_ability(create_ability('tackle'))
    fighter.add_ability(create_ability('power_up'))
    
    # Add a trait
    fighter.add_trait(Trait(
        name="Battle Hardened",
        description="Experienced in combat",
        trait_type="offensive",
        strength_modifier=1.15,
        defense_modifier=1.10,
        rarity="uncommon"
    ))
    
    print(f"Created: {fighter}")
    print(f"Type: {fighter.creature_type.name}")
    print(f"Stats: {fighter.stats}")
    print(f"Abilities: {[a.name for a in fighter.abilities]}")
    print(f"Traits: {[t.name for t in fighter.traits]}")
    
    return fighter


def example_2_stat_modifiers_and_buffs():
    """Example 2: Using stat modifiers and buffs."""
    print_separator("Example 2: Stat Modifiers and Buffs")
    
    fighter = Creature(name="TestFighter", level=5)
    
    print(f"Base stats: Attack={fighter.stats.attack}, Defense={fighter.stats.defense}")
    
    # Apply a temporary buff
    buff = StatModifier(
        name="Battle Fury",
        duration=3,
        attack_multiplier=1.5,
        attack_bonus=5,
        defense_multiplier=0.9  # Trade defense for attack
    )
    
    fighter.add_modifier(buff)
    print(f"After buff: Attack={fighter.stats.attack}, Defense={fighter.stats.defense}")
    print(f"Active modifiers: {[m.name for m in fighter.active_modifiers]}")
    
    # Simulate turns passing
    print("\nSimulating 3 turns...")
    for turn in range(1, 4):
        fighter.tick_modifiers()
        print(f"  Turn {turn}: Buff duration={buff.duration}, Active modifiers={len(fighter.active_modifiers)}")
    
    print(f"After buff expires: Attack={fighter.stats.attack}, Defense={fighter.stats.defense}")


def example_3_leveling_and_experience():
    """Example 3: Leveling up and stat growth."""
    print_separator("Example 3: Leveling and Experience")
    
    creature = Creature(name="Learner", level=1)
    
    print(f"Starting at level {creature.level}")
    print(f"Stats: {creature.stats}")
    print(f"XP needed for next level: {creature.experience_for_next_level()}")
    
    # Gain experience
    print("\nGaining experience...")
    for i in range(1, 4):
        xp_gained = 40
        leveled = creature.gain_experience(xp_gained)
        print(f"  Gained {xp_gained} XP. Current XP: {creature.experience}")
        if leveled:
            print(f"  ⭐ LEVEL UP! Now level {creature.level}")
            print(f"  New stats: {creature.stats}")


def example_4_abilities_and_combat():
    """Example 4: Using abilities in simulated combat."""
    print_separator("Example 4: Abilities and Combat")
    
    # Create attacker and defender
    attacker = Creature(name="Attacker", level=5)
    attacker.add_ability(create_ability('tackle'))
    attacker.add_ability(create_ability('fireball'))
    
    defender = Creature(name="Defender", level=5)
    
    print(f"Attacker: {attacker.stats}")
    print(f"Defender: {defender.stats}")
    print()
    
    # Simulate using abilities
    for ability in attacker.abilities:
        print(f"Using ability: {ability.name}")
        print(f"  Type: {ability.ability_type.value}, Power: {ability.power}")
        
        if ability.can_use(attacker.stats, attacker.energy):
            ability.use()
            damage = ability.calculate_damage(attacker.stats.attack, defender.stats.defense)
            actual_damage = defender.stats.take_damage(damage)
            attacker.energy -= ability.energy_cost
            
            print(f"  ✓ Hit! Dealt {actual_damage} damage")
            print(f"  Defender HP: {defender.stats.hp}/{defender.stats.max_hp}")
            print(f"  Attacker energy: {attacker.energy}/{attacker.max_energy}")
            
            if ability.cooldown > 0:
                print(f"  Cooldown: {ability.current_cooldown} turns")
        else:
            print(f"  ✗ Cannot use (insufficient energy or on cooldown)")
        print()


def example_5_evolution_system():
    """Example 5: Evolution system."""
    print_separator("Example 5: Evolution System")
    
    # Set up evolution system
    system = EvolutionSystem()
    
    # Define creature types
    newborn_type = CreatureType(
        name="Newborn",
        base_stats=Stats(max_hp=80, hp=80, attack=8, defense=8, speed=10),
        stat_growth=StatGrowth(hp_growth=10.0, attack_growth=2.0),
        evolution_stage=0,
        can_evolve=True
    )
    
    warrior_type = CreatureType(
        name="Warrior",
        base_stats=Stats(max_hp=120, hp=120, attack=15, defense=12, speed=8),
        stat_growth=StatGrowth(hp_growth=15.0, attack_growth=3.0),
        evolution_stage=1,
        can_evolve=True
    )
    
    speedster_type = CreatureType(
        name="Speedster",
        base_stats=Stats(max_hp=100, hp=100, attack=12, defense=8, speed=18),
        stat_growth=StatGrowth(hp_growth=12.0, attack_growth=2.5, speed_growth=3.0),
        evolution_stage=1,
        can_evolve=True
    )
    
    # Register types
    system.register_creature_type(newborn_type)
    system.register_creature_type(warrior_type)
    system.register_creature_type(speedster_type)
    
    # Add evolution paths
    system.add_evolution_path(EvolutionPath(
        from_type="Newborn",
        to_type="Warrior",
        min_level=10
    ))
    system.add_evolution_path(EvolutionPath(
        from_type="Newborn",
        to_type="Speedster",
        min_level=10
    ))
    
    # Create a creature
    creature = Creature(name="Hatchling", creature_type=newborn_type, level=1)
    print(f"Created: {creature}")
    print(f"Type: {creature.creature_type.name} (Stage {creature.creature_type.evolution_stage})")
    
    # Level up to evolution threshold
    print("\nLeveling up to evolution threshold...")
    while creature.level < 10:
        creature.level_up()
    
    print(f"Now level {creature.level}")
    print(f"Stats: {creature.stats}")
    
    # Check for available evolutions
    if system.can_evolve(creature):
        available = system.get_available_evolutions(creature)
        print(f"\nAvailable evolutions: {[p.to_type for p in available]}")
        
        # Evolve to first available form
        success, message = system.evolve(creature, available[0])
        print(f"\n{message}")
        print(f"New type: {creature.creature_type.name} (Stage {creature.creature_type.evolution_stage})")
        print(f"New stats: {creature.stats}")
    else:
        print("\nNo evolution available yet")


def example_6_breeding_and_genetics():
    """Example 6: Breeding and genetics."""
    print_separator("Example 6: Breeding and Genetics")
    
    # Create parent creatures
    parent1 = Creature(name="Father", level=10)
    parent1.add_trait(Trait(
        name="Mighty",
        trait_type="offensive",
        strength_modifier=1.3,
        rarity="rare"
    ))
    parent1.add_trait(Trait(
        name="Tough",
        trait_type="defensive",
        defense_modifier=1.2,
        rarity="uncommon"
    ))
    
    parent2 = Creature(name="Mother", level=10)
    parent2.add_trait(Trait(
        name="Swift",
        trait_type="utility",
        speed_modifier=1.4,
        rarity="rare"
    ))
    parent2.add_trait(Trait(
        name="Resilient",
        trait_type="defensive",
        defense_modifier=1.15,
        rarity="common"
    ))
    
    print(f"Parent 1: {parent1.name}")
    print(f"  Stats: {parent1.base_stats}")
    print(f"  Traits: {[t.name for t in parent1.traits]}")
    
    print(f"\nParent 2: {parent2.name}")
    print(f"  Stats: {parent2.base_stats}")
    print(f"  Traits: {[t.name for t in parent2.traits]}")
    
    # Breed offspring
    genetics = GeneticsSystem(mutation_rate=0.15)
    offspring = genetics.breed(parent1, parent2, "Offspring")
    
    print(f"\nOffspring: {offspring.name}")
    print(f"  Stats: {offspring.base_stats}")
    print(f"  Inherited {len(offspring.traits)} traits:")
    for trait in offspring.traits:
        print(f"    - {trait.name} ({trait.rarity})")
        if "Mutated" in trait.name:
            print(f"      ⚡ MUTATED!")


def example_7_serialization():
    """Example 7: Saving and loading creatures."""
    print_separator("Example 7: Serialization")
    
    # Create a complex creature
    creature = Creature(name="Serializable", level=5, experience=250)
    creature.add_ability(create_ability('tackle'))
    creature.add_ability(create_ability('fireball'))
    creature.add_trait(Trait(name="Quick", speed_modifier=1.2))
    creature.add_modifier(StatModifier(
        name="Temporary Buff",
        duration=5,
        attack_multiplier=1.3
    ))
    
    print(f"Original creature: {creature}")
    print(f"  Level: {creature.level}, XP: {creature.experience}")
    print(f"  Abilities: {len(creature.abilities)}")
    print(f"  Traits: {len(creature.traits)}")
    print(f"  Active modifiers: {len(creature.active_modifiers)}")
    
    # Serialize to dictionary
    creature_data = creature.to_dict()
    
    # Convert to JSON string
    json_str = json.dumps(creature_data, indent=2)
    print(f"\nSerialized to JSON ({len(json_str)} characters)")
    
    # Deserialize back
    restored_data = json.loads(json_str)
    restored_creature = Creature.from_dict(restored_data)
    
    print(f"\nRestored creature: {restored_creature}")
    print(f"  Level: {restored_creature.level}, XP: {restored_creature.experience}")
    print(f"  Abilities: {len(restored_creature.abilities)}")
    print(f"  Traits: {len(restored_creature.traits)}")
    print(f"  Active modifiers: {len(restored_creature.active_modifiers)}")
    print(f"  IDs match: {creature.creature_id == restored_creature.creature_id}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("  EvoBattle Core Models - Example Usage")
    print("=" * 60)
    
    try:
        example_1_creature_creation()
        example_2_stat_modifiers_and_buffs()
        example_3_leveling_and_experience()
        example_4_abilities_and_combat()
        example_5_evolution_system()
        example_6_breeding_and_genetics()
        example_7_serialization()
        
        print_separator()
        print("\n✓ All examples completed successfully!")
        print("\nFor more information, see MODELS_DOCUMENTATION.md")
        print()
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
