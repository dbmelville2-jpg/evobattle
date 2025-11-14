# Core Game Models Documentation

## Overview

This document describes the core game models implemented for EvoBattle. These models provide the foundation for the gameplay systems including creatures, stats, abilities, evolution, and genetics.

## Architecture

The core models are organized into the following modules:

```
src/models/
├── stats.py          # Stats, StatModifier, StatGrowth
├── ability.py        # Ability, AbilityEffect, AbilityType, TargetType
├── creature.py       # Creature, CreatureType
├── evolution.py      # EvolutionPath, EvolutionSystem, GeneticsSystem
├── trait.py          # Trait (existing)
├── fighter.py        # Fighter (legacy, kept for compatibility)
└── lineage.py        # Lineage (existing)
```

## Core Components

### 1. Stats System (`stats.py`)

#### Stats Class
Manages creature statistics with support for modifiers and damage/healing.

**Key Features:**
- HP tracking with max HP
- Attack, Defense, Speed, Special Attack, Special Defense
- Damage and healing methods
- Serialization support

**Example:**
```python
from src.models.stats import Stats

stats = Stats(max_hp=120, attack=15, defense=12, speed=10)
stats.take_damage(30)  # Apply damage
stats.heal(20)         # Heal creature
print(stats.is_alive())  # Check if alive
```

#### StatModifier Class
Represents temporary or permanent stat modifications (buffs/debuffs).

**Key Features:**
- Multiplicative and additive modifiers
- Duration management
- Automatic expiration

**Example:**
```python
from src.models.stats import StatModifier

buff = StatModifier(
    name="Power Boost",
    duration=3,
    attack_multiplier=1.5,
    attack_bonus=10
)

modified_stats = stats.apply_modifier(buff)
buff.tick()  # Decrease duration
```

#### StatGrowth Class
Defines how stats increase with levels.

**Key Features:**
- Configurable growth rates per stat
- Multiple growth curves (slow, medium, fast)
- Level-based stat calculation

**Example:**
```python
from src.models.stats import StatGrowth

growth = StatGrowth(
    hp_growth=12.0,
    attack_growth=2.5,
    growth_curve="medium_fast"
)

level5_stats = growth.calculate_stats_at_level(base_stats, 5)
```

### 2. Ability System (`ability.py`)

#### Ability Class
Represents skills and moves that creatures can use.

**Key Features:**
- Multiple ability types (Physical, Special, Status, Healing, Buff, Debuff)
- Cooldown management
- Energy cost system
- Activation conditions
- Damage calculation
- Effect system

**Example:**
```python
from src.models.ability import Ability, AbilityType, create_ability

# Create a custom ability
fireball = Ability(
    name="Fireball",
    ability_type=AbilityType.SPECIAL,
    power=60,
    accuracy=90,
    cooldown=2,
    energy_cost=10
)

# Or use a predefined template
tackle = create_ability('tackle')

# Use the ability
if fireball.can_use(user_stats, user_energy=50):
    fireball.use()
    damage = fireball.calculate_damage(user_attack=20, target_defense=15)
```

#### Predefined Abilities
The system includes several predefined abilities:
- `tackle` - Basic physical attack
- `fireball` - Special fire attack with cooldown
- `heal` - Self-healing ability
- `power_up` - Attack buff
- `defense_break` - Defense debuff
- `quick_strike` - Fast attack with speed requirement

### 3. Creature System (`creature.py`)

#### CreatureType Class
Defines a species/type of creature with base characteristics.

**Key Features:**
- Base stats for the type
- Growth profile
- Type tags (e.g., "fire", "water", "flying")
- Evolution stage tracking

**Example:**
```python
from src.models.creature import CreatureType
from src.models.stats import Stats, StatGrowth

dragon_type = CreatureType(
    name="Dragon",
    description="A powerful dragon",
    base_stats=Stats(max_hp=150, attack=20, defense=18),
    stat_growth=StatGrowth(hp_growth=15.0, attack_growth=3.0),
    type_tags=["fire", "flying"],
    evolution_stage=2
)
```

#### Creature Class
The main creature class with full functionality.

**Key Features:**
- Unique ID for each creature
- Level and experience system
- Stats with modifier support
- Abilities and cooldown management
- Trait system integration
- Energy system for abilities
- Serialization for persistence

**Example:**
```python
from src.models.creature import Creature
from src.models.ability import create_ability

# Create a creature
creature = Creature(
    name="Blaze",
    creature_type=dragon_type,
    level=5
)

# Add abilities
creature.add_ability(create_ability('tackle'))
creature.add_ability(create_ability('fireball'))

# Add traits
from src.models.trait import Trait
creature.add_trait(Trait(name="Fire Affinity", strength_modifier=1.2))

# Gain experience and level up
creature.gain_experience(100)

# Apply buffs
from src.models.stats import StatModifier
buff = StatModifier(name="Battle Fury", attack_multiplier=1.5, duration=3)
creature.add_modifier(buff)

# Get effective stats (with all modifiers)
effective_stats = creature.get_effective_stats()
```

### 4. Evolution & Genetics System (`evolution.py`)

#### EvolutionPath Class
Defines an evolution path from one creature type to another.

**Key Features:**
- Level requirements
- Trait requirements
- Custom conditions

**Example:**
```python
from src.models.evolution import EvolutionPath

path = EvolutionPath(
    from_type="Newborn",
    to_type="Warrior",
    min_level=10,
    required_traits=["Strong"],
    conditions={'evolution_type': 'strength'}
)
```

#### EvolutionSystem Class
Manages creature evolution and type transformations.

**Key Features:**
- Multiple evolution paths per type
- Condition checking
- Stat recalculation on evolution
- Full heal on evolution

**Example:**
```python
from src.models.evolution import EvolutionSystem, create_example_evolution_system

# Create and configure system
system = EvolutionSystem()
system.register_creature_type(newborn_type)
system.register_creature_type(warrior_type)
system.add_evolution_path(evolution_path)

# Check and perform evolution
if system.can_evolve(creature):
    success, message = system.evolve(creature)
    print(message)  # "Evolved from Newborn to Warrior!"

# Or use the example system
system = create_example_evolution_system()
```

#### GeneticsSystem Class
Manages breeding and trait inheritance.

**Key Features:**
- Stat inheritance with variation
- Trait inheritance (50% chance per trait)
- Mutation system
- Offspring generation

**Example:**
```python
from src.models.evolution import GeneticsSystem

genetics = GeneticsSystem(mutation_rate=0.1)

offspring = genetics.breed(
    parent1=creature1,
    parent2=creature2,
    offspring_name="Baby Dragon"
)
```

## Integration with Existing Systems

### Fighter Compatibility
The original `Fighter` class remains for backward compatibility. New code should use the `Creature` class which provides more features.

### Trait System
The existing `Trait` class is fully integrated with the new creature system. Traits automatically apply their modifiers to creature stats.

### Lineage System
The existing `Lineage` class can be used alongside the new genetics system to track family trees and breeding history.

## Usage Examples

### Example 1: Creating and Battling Creatures

```python
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability

# Define creature types
warrior_type = CreatureType(
    name="Warrior",
    base_stats=Stats(max_hp=120, attack=15, defense=12, speed=10),
    stat_growth=StatGrowth(hp_growth=12.0, attack_growth=2.5),
    type_tags=["fighter"]
)

# Create creatures
fighter1 = Creature(name="Ares", creature_type=warrior_type, level=5)
fighter2 = Creature(name="Athena", creature_type=warrior_type, level=5)

# Add abilities
fighter1.add_ability(create_ability('tackle'))
fighter1.add_ability(create_ability('power_up'))

# Simulate combat
ability = fighter1.get_ability('tackle')
if ability.can_use(fighter1.stats, fighter1.energy):
    ability.use()
    damage = ability.calculate_damage(fighter1.stats.attack, fighter2.stats.defense)
    fighter2.stats.take_damage(damage)
    print(f"Fighter1 deals {damage} damage!")
```

### Example 2: Evolution Path

```python
from src.models.evolution import create_example_evolution_system

# Get example system with predefined types and paths
system = create_example_evolution_system()

# Create a newborn
newborn_type = system.creature_types["Newborn"]
creature = Creature(name="Hatchling", creature_type=newborn_type, level=1)

# Level up to evolution level
for _ in range(9):
    creature.level_up()

# Evolve
if system.can_evolve(creature):
    available_paths = system.get_available_evolutions(creature)
    print(f"Available evolutions: {[p.to_type for p in available_paths]}")
    
    success, message = system.evolve(creature)
    print(message)
```

### Example 3: Breeding and Genetics

```python
from src.models.evolution import GeneticsSystem
from src.models.trait import Trait

# Create parents with traits
parent1 = Creature(name="Father")
parent1.add_trait(Trait(name="Strong", strength_modifier=1.3))

parent2 = Creature(name="Mother")
parent2.add_trait(Trait(name="Swift", speed_modifier=1.2))

# Breed offspring
genetics = GeneticsSystem(mutation_rate=0.1)
child = genetics.breed(parent1, parent2, "Offspring")

print(f"Child inherited {len(child.traits)} traits")
print(f"Child stats: {child.stats}")
```

### Example 4: Persistence

```python
# Save creature to dictionary
creature_data = creature.to_dict()

# Save to JSON file
import json
with open('creature.json', 'w') as f:
    json.dump(creature_data, f, indent=2)

# Load from JSON file
with open('creature.json', 'r') as f:
    loaded_data = json.load(f)

# Restore creature
from src.models.creature import Creature
restored_creature = Creature.from_dict(loaded_data)
```

## Testing

All core models have comprehensive unit tests located in the `tests/` directory:

- `test_stats.py` - Tests for Stats, StatModifier, StatGrowth
- `test_ability.py` - Tests for Ability system
- `test_creature.py` - Tests for Creature and CreatureType
- `test_evolution.py` - Tests for Evolution and Genetics systems

Run tests with:
```bash
python3 -m unittest discover tests -v
```

## Extension Points

The system is designed to be easily extensible:

1. **New Ability Types**: Add new `AbilityType` enum values
2. **Custom Conditions**: Extend condition checking in `Ability.can_use()`
3. **New Stats**: Add stats to `Stats` class and update modifiers
4. **Evolution Triggers**: Add custom conditions to `EvolutionPath`
5. **Mutation Types**: Extend `GeneticsSystem._mutate_trait()` for different mutations
6. **Growth Curves**: Add new curve types in `StatGrowth._get_growth_multiplier()`

## Design Patterns Used

- **Data Classes**: For simple data structures (Stats, StatModifier, EvolutionPath)
- **Builder Pattern**: For creating complex creatures with many options
- **Strategy Pattern**: For different growth curves and evolution paths
- **Observer Pattern**: Potential for event system (not yet implemented)
- **Serialization**: All models support to_dict/from_dict for persistence

## Future Enhancements

Potential areas for expansion:

1. **Battle System Integration**: Link abilities and stats to battle mechanics
2. **Equipment System**: Items that provide stat modifiers
3. **Status Effects**: Poison, burn, paralysis, etc.
4. **Weather/Terrain**: Environmental effects on abilities
5. **Move Learning**: System for creatures to learn new abilities
6. **Breeding Genetics**: More complex inheritance patterns
7. **Stat IVs/EVs**: Individual values and effort values like Pokemon
8. **Nature/Personality**: Additional stat modifiers based on personality
9. **Forms**: Alternate forms for the same creature type
10. **Mega Evolution**: Temporary powerful transformations
