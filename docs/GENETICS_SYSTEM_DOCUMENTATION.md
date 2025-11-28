# Enhanced Genetics and Trait System Documentation

## Overview

This document describes the enhanced genetics system with dominant/recessive genes, expanded trait categories, and cross-entity interactions between creatures and pellets.

**NOTE:** For architecture and system boundaries, see [GENETICS_BREEDING_ARCHITECTURE.md](GENETICS_BREEDING_ARCHITECTURE.md)

## System Architecture

The genetics and breeding systems are organized as follows:

- **GeneticsEngine** (`src/models/genetics.py`) - Core Mendelian genetics implementation
- **PelletGenetics** (`src/models/genetics.py`) - Pellet-specific reproduction genetics
- **Breeding** (`src/systems/breeding.py`) - High-level breeding orchestration
- **EvolutionSystem** (`src/models/evolution.py`) - Creature type transformation (separate from breeding)

See [GENETICS_BREEDING_ARCHITECTURE.md](GENETICS_BREEDING_ARCHITECTURE.md) for detailed architecture documentation.

## Key Features

### 1. Enhanced Trait System

#### Trait Provenance
Every trait now tracks its origin and history:
- **Source type**: `inherited`, `mutated`, or `emergent`
- **Parent traits**: Names of traits this came from
- **Generation**: When the trait first appeared
- **Mutation count**: How many times it has mutated

#### Dominance System
Traits can have three dominance levels:
- **Dominant**: Always expressed when present from one parent
- **Recessive**: Only expressed when both parents have it
- **Codominant**: Both traits contribute when one parent has each

### 2. Expanded Trait Categories

#### Behavioral Traits
Affect creature decision-making and personality:
- **Timid**: Flees earlier, reduced aggression
- **Aggressive**: Seeks combat, fights fiercely
- **Curious**: Explores more, finds resources faster
- **Cautious**: Strategic, avoids risks
- **Bold**: Takes risks, never retreats
- **Social**: Better cooperation with family
- **Solitary**: Stronger alone, weaker in groups

#### Physical Traits
Affect stats and physical capabilities:
- **Armored**: Exceptional defense, slower speed
- **Swift**: Incredible speed, higher dodge chance
- **Regenerative**: Slow HP regeneration
- **Venomous**: Attacks inflict poison
- **Camouflaged**: Harder to detect, ambush bonus
- **Keen Senses**: Better threat and food detection
- **Powerful**: Immense strength, critical damage

#### Ecological Traits
Affect environment and entity interactions:
- **Scavenger**: Prefers corpses, bonus nutrition from them
- **Pollinator**: Helps pellets reproduce
- **Parasitic**: Drains life from opponents
- **Symbiotic**: Benefits from pellet proximity
- **Predator**: Hunts creatures effectively
- **Herbivore**: Plant specialist, can't eat meat
- **Omnivore**: Efficient with varied diet
- **Toxin Resistant**: Reduced toxin damage

### 3. Pellet Traits

Pellets can have traits that affect their properties:
- **Highly Nutritious**: Exceptional energy value
- **Toxic Defense**: Contains harmful toxins
- **Fast Growing**: Reproduces quickly
- **Attractive**: Highly palatable to creatures
- **Repellent**: Discourages consumption
- **Medicinal**: Heals creatures that eat it
- **Symbiotic**: Benefits from creature proximity
- **Hardy**: Longer lifespan, environmental resistance

### 4. Advanced Genetics

#### Trait Inheritance
The new genetics engine properly combines traits from both parents:

1. **Both parents have same trait**:
   - Dominant + Dominant → Always expressed
   - Recessive + Recessive → Expressed
   - Dominant + Recessive → Dominant expressed
   - Codominant + Codominant → Blended expression

2. **One parent has trait**:
   - Dominant → 100% inheritance
   - Recessive → 50% inheritance
   - Codominant → Variable inheritance

#### Stat Blending
Stats are no longer pure 50/50 averages:
- Weighted averaging (30-70% range)
- Random genetic variation (-15% to +15%)
- 5% chance of genetic potential boost (+20%)

#### Mutation System
- Base mutation rate configurable (default 10%)
- Trait modification (±10% to modifiers)
- Trait addition (3% chance of new trait)
- Trait removal (5% chance during inheritance)
- All mutations tracked in provenance

### 5. Cross-Entity Interactions

#### Pellet Preference
Creatures evaluate pellets based on their traits:

```python
# Scavenger prefers corpses
scavenger_trait → corpse_pellet = 1.5x preference

# Herbivore prefers green pellets
herbivore_trait → green_pellet = 1.4x preference

# Toxin Resistant can eat toxic pellets
toxin_resistant_trait → toxic_pellet = 1.3x preference
```

#### Consumption Effects
When a creature eats a pellet:

1. **Nutrition Calculation**:
   - Base nutrition from pellet
   - Trait-based multipliers (scavenger, herbivore, omnivore)
   - Special effects tracked

2. **Toxin Damage**:
   - Base damage = toxicity * 20
   - Toxin Resistant reduces by 40%
   - Indiscriminate Eater reduces by 50%

3. **Special Effects**:
   - Scavenger bonus from corpses
   - Herbivore bonus from plants
   - Omnivore efficiency bonus

#### Pollination
Creatures with Pollinator trait boost nearby pellet reproduction:
- Default boost: 1.4x reproduction rate
- Applied when creature is near pellet
- Helps pellet populations thrive

#### Symbiosis
Creatures with Symbiotic trait gain benefits from nearby pellets:
- Stat boost (up to 1.2x with 3+ pellets)
- HP regeneration (0.5 per pellet)
- Energy regeneration

### 6. Pellet Genetics

#### Asexual Reproduction
Single pellet creates offspring:
- Inherits parent traits with mutation
- Higher mutation rate (15% default)

#### Sexual Reproduction
Two pellets create offspring:
- Traits blended from both parents
- Weighted averaging (30-70% range)
- Standard mutation rate (15%)
- Color blending
- All numerical traits combined

## Usage Examples

### Creating Creatures with Traits

```python
from src.models.creature import Creature, CreatureType
from src.models.expanded_traits import AGGRESSIVE_TRAIT, ARMORED_TRAIT
from src.models.stats import Stats

# Create creature type
warrior = CreatureType(
    name="Warrior",
    base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
)

# Create creature with traits
creature = Creature(name="Brutus", creature_type=warrior)
creature.add_trait(AGGRESSIVE_TRAIT.copy())
creature.add_trait(ARMORED_TRAIT.copy())
```

### Breeding with Genetics

```python
from src.systems.breeding import Breeding

# Create breeding system
breeding = Breeding(mutation_rate=0.1)

# Breed two creatures
parent1 = Creature(name="Alpha", creature_type=warrior, mature=True)
parent1.add_trait(AGGRESSIVE_TRAIT.copy())

parent2 = Creature(name="Beta", creature_type=warrior, mature=True)
parent2.add_trait(SWIFT_TRAIT.copy())

# Create offspring
offspring = breeding.breed(parent1, parent2)

# Offspring may have:
# - Aggressive trait (dominant)
# - Swift trait (dominant)
# - Blended stats from both parents
# - Possible mutations
```

### Cross-Entity Interactions

```python
from src.models.cross_entity_interactions import (
    CrossEntityInteractions,
    find_best_pellet_for_creature
)
from src.models.pellet import Pellet, PelletTraits

# Create pellets
normal_pellet = Pellet(x=10, y=10, traits=PelletTraits(
    nutritional_value=30.0,
    toxicity=0.1,
    palatability=0.6
))

toxic_pellet = Pellet(x=20, y=20, traits=PelletTraits(
    nutritional_value=40.0,
    toxicity=0.8,
    palatability=0.3
))

# Create creature with traits
creature = Creature(name="Hunter", creature_type=warrior)
creature.add_trait(SCAVENGER_TRAIT.copy())

# Calculate preferences
interactions = CrossEntityInteractions()
normal_pref = interactions.calculate_pellet_preference(creature, normal_pellet)
toxic_pref = interactions.calculate_pellet_preference(creature, toxic_pellet)

# Find best pellet
available_pellets = [normal_pellet, toxic_pellet]
best = find_best_pellet_for_creature(creature, available_pellets)

# Apply consumption effects
effects = interactions.apply_consumption_effects(creature, best)
print(f"Nutrition gained: {effects['nutrition_gained']}")
print(f"HP change: {effects['hp_change']}")
print(f"Special effects: {effects['special_effects']}")
```

### Pellet Sexual Reproduction

```python
from src.models.pellet import Pellet, PelletTraits

# Create two parent pellets
parent1 = Pellet(x=10, y=10, traits=PelletTraits(
    nutritional_value=50.0,
    growth_rate=0.02,
    toxicity=0.1,
    color=(100, 200, 100)
))

parent2 = Pellet(x=15, y=15, traits=PelletTraits(
    nutritional_value=30.0,
    growth_rate=0.03,
    toxicity=0.05,
    color=(150, 220, 120)
))

# Sexual reproduction
offspring = parent1.reproduce(mutation_rate=0.15, partner=parent2)

# Offspring has:
# - Blended nutritional value (~40, with variation)
# - Blended growth rate (~0.025, with variation)
# - Blended toxicity (~0.075, with variation)
# - Blended color (greenish)
```

## Testing

Comprehensive test coverage includes:

### Genetics Tests (19 tests)
- Trait provenance tracking
- Dominant/recessive gene interactions
- Stat blending (not pure average)
- Multi-generational inheritance
- Mutation tracking
- Pellet genetics (sexual/asexual)

### Cross-Entity Interaction Tests (16 tests)
- Pellet preference calculation
- Trait-based consumption effects
- Scavenger bonus from corpses
- Herbivore preference for plants
- Toxin resistance mechanics
- Pollination effects
- Symbiotic benefits
- Pellet avoidance

### Breeding Tests (10 tests)
- All existing tests still pass
- Integration with genetics engine verified

## Performance

The genetics system has minimal performance impact:
- Trait combination: O(n) where n = number of unique traits
- Stat blending: O(1)
- Cross-entity preference: O(1) per pellet
- Memory: ~200 bytes per trait with provenance

## Future Enhancements

Potential additions:
- **Epistatic traits**: Traits that modify other traits
- **Trait hierarchies**: Parent/child trait relationships
- **Environmental effects**: Traits affected by arena conditions
- **Trait visualization**: UI for viewing inheritance chains
- **Historical tracking**: Full genetic lineage trees
- **Trait libraries**: Procedurally generated traits

## Integration Points

The genetics system integrates with:
- **Breeding System**: Uses GeneticsEngine for trait inheritance
- **Pellet System**: Uses PelletGenetics for reproduction
- **Battle System**: Traits affect combat behavior
- **Creature System**: All trait effects applied
- **Living World**: Provenance tracking for history

## Configuration

Key parameters:
```python
# Breeding system
breeding = Breeding(
    mutation_rate=0.1,  # 10% mutation chance
    trait_inheritance_chance=0.8  # 80% trait inheritance
)

# Genetics engine
genetics = GeneticsEngine(
    mutation_rate=0.1  # 10% mutation chance
)

# Pellet genetics
pellet_genetics = PelletGenetics(
    mutation_rate=0.15  # 15% mutation (higher for pellets)
)
```

## Backward Compatibility

All changes are backward compatible:
- Existing creatures work with new system
- Old save files load correctly
- Default dominance is "codominant"
- Provenance auto-generated for existing traits
- No breaking changes to APIs
