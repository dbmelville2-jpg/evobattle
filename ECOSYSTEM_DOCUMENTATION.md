# Ecosystem Survival System Documentation

## Overview

The Ecosystem Survival System adds hunger, resource gathering, and trait-driven foraging behavior to EvoBattle's spatial combat system. Creatures must now balance combat with survival - finding food to avoid starvation while competing for resources.

## Features

### 1. Hunger System

Every creature has a **hunger** stat ranging from 0 (starving) to 100 (full):

- **Hunger Depletion**: Hunger depletes continuously at a base rate of 1.0 per second
- **Starvation**: When hunger reaches 0, the creature dies
- **Metabolic Traits**: Certain traits modify hunger depletion rate:
  - `Efficient Metabolism`: -40% hunger depletion
  - `Efficient`: -30% hunger depletion  
  - `Glutton`: +50% hunger depletion
  - `Voracious`: +40% hunger depletion

### 2. Resource System

Food resources spawn in the arena and can be collected by creatures:

- **Initial Resources**: Configurable number of resources at battle start
- **Resource Spawning**: Resources spawn over time at a configurable rate
- **Collection Range**: Creatures collect food within 2.0 units
- **Hunger Restoration**: Each food item restores 40 hunger points
- **HP Bonus**: Creatures with Glutton or Voracious traits gain bonus HP when eating

### 3. Foraging Behavior

New `FORAGER` behavior type added to the behavior system:

- **Priority Food Seeking**: Foragers actively seek nearest food resources
- **Hunger-Driven Behavior**: ALL creatures prioritize food when hunger < 40
- **Trait Recognition**: Creatures with `Forager`, `Gatherer`, or `Scavenger` traits automatically use foraging behavior
- **Wandering**: Foragers wander to search for food when none is visible

### 4. Metabolic Traits

Predefined traits in `src/models/ecosystem_traits.py`:

#### Metabolic Traits
- **Efficient Metabolism**: 40% slower hunger, uncommon
- **Efficient**: 30% slower hunger, common
- **Glutton**: 50% faster hunger, +10% strength, HP bonus when eating, common
- **Voracious**: 40% faster hunger, +15% strength, heals when eating, uncommon

#### Behavioral Traits
- **Forager**: Seeks resources, +5% speed, common
- **Gatherer**: Expert resource finder, +10% speed, uncommon
- **Scavenger**: Hardy food finder, +5% defense, common

#### Personality Traits
- **Curious**: Explores widely, +10% speed, common
- **Wanderer**: Constantly moving, +15% speed, uncommon
- **Explorer**: Driven explorer, +20% speed, rare
- **Lazy**: Minimal movement, -10% speed, +5% defense, common
- **Cautious**: Avoids danger, +10% defense, common
- **Aggressive**: Seeks combat, +15% strength, -5% defense, common

#### Survival Traits
- **Hardy**: Tough and resilient, +20% defense, uncommon
- **Frail**: Vulnerable, -20% defense, -10% strength, common

## API Reference

### Creature Class

#### New Attributes
```python
creature.hunger: int          # Current hunger (0-100)
creature.max_hunger: int      # Maximum hunger (default: 100)
```

#### New Methods
```python
creature.tick_hunger(delta_time: float) -> None
    """Deplete hunger over time based on metabolic traits."""

creature.eat(food_value: int = 40) -> int
    """Consume food to restore hunger. Returns amount restored."""
```

### SpatialBattle Class

#### Constructor Parameters
```python
SpatialBattle(
    creatures: List[Creature],
    arena_width: float = 100.0,
    arena_height: float = 100.0,
    random_seed: Optional[int] = None,
    resource_spawn_rate: float = 0.1,  # Resources per second
    initial_resources: int = 5          # Starting food count
)
```

**Note:** For backward compatibility, you can still pass two lists (old API), but the new API uses a single population list.

### BehaviorType Enum

#### New Behavior
```python
BehaviorType.FORAGER = "forager"  # Prioritizes seeking food/resources
```

## Usage Examples

### Basic Hunger System

```python
from src.models.creature import Creature
from src.models.ecosystem_traits import EFFICIENT_METABOLISM

# Create creature with efficient metabolism
creature = Creature(name="Fox", traits=[EFFICIENT_METABOLISM])

# Simulate 10 seconds
creature.tick_hunger(10.0)
print(f"Hunger: {creature.hunger}/100")  # ~94 (reduced depletion)

# Feed the creature
hunger_restored = creature.eat(40)
print(f"Restored {hunger_restored} hunger")
```

### Ecosystem Battle

```python
from src.models.creature import Creature
from src.models.ecosystem_traits import FORAGER, GLUTTON, CURIOUS
from src.systems.battle_spatial import SpatialBattle

# Create creatures with diverse traits
forager = Creature(name="Forager", traits=[FORAGER])
glutton = Creature(name="Glutton", traits=[GLUTTON])
explorer = Creature(name="Explorer", traits=[CURIOUS])

# Create battle with resources
battle = SpatialBattle(
    [forager, explorer],
    [glutton],
    resource_spawn_rate=0.2,    # 1 food every 5 seconds
    initial_resources=10        # Start with 10 food items
)

# Simulate ecosystem
while not battle.is_over:
    battle.update(0.1)  # 0.1 second time step
```

### Using Predefined Traits

```python
from src.models.ecosystem_traits import (
    EFFICIENT_METABOLISM,
    VORACIOUS,
    FORAGER,
    CURIOUS,
    get_random_metabolic_trait,
    get_trait_by_name
)

# Use predefined traits
creature1 = Creature(name="C1", traits=[EFFICIENT_METABOLISM, FORAGER])

# Get random trait
random_trait = get_random_metabolic_trait()
creature2 = Creature(name="C2", traits=[random_trait])

# Get trait by name
trait = get_trait_by_name("Curious")
creature3 = Creature(name="C3", traits=[trait])
```

## Rendering

### Hunger Bar

The `CreatureRenderer` automatically displays hunger bars:
- **Position**: Below HP bar
- **Color**: 
  - Golden/yellow (> 60% hunger)
  - Orange (30-60% hunger)
  - Red (< 30% hunger)
- **Size**: 40x4 pixels

### Food Resources

The `ArenaRenderer` displays food as:
- **Appearance**: Green circles with bright outline
- **Size**: 8-pixel radius
- **Color**: RGB(80, 200, 60) with RGB(120, 255, 100) outline

## Configuration

### Hunger Depletion Rates

Base rate: 1.0 hunger per second (100 seconds to starve)

Trait modifiers:
- Efficient Metabolism: 0.6x (166 seconds to starve)
- Efficient: 0.7x (142 seconds to starve)
- Glutton: 1.5x (66 seconds to starve)
- Voracious: 1.4x (71 seconds to starve)

### Resource Spawning

Recommended rates:
- **Sparse**: 0.05/second (1 every 20 seconds)
- **Normal**: 0.1/second (1 every 10 seconds)
- **Abundant**: 0.2/second (1 every 5 seconds)

### Collection Parameters

- **Collection Range**: 2.0 units
- **Food Value**: 40 hunger points (restores to full from 60%)
- **HP Bonus** (Voracious/Glutton): food_value / 10 (4 HP per food)

## Testing

### Unit Tests

Run hunger system tests:
```bash
python -m unittest tests.test_hunger
```

Run foraging behavior tests:
```bash
python -m unittest tests.test_foraging
```

### Demo Scripts

Text-based demo:
```bash
python -m examples.ecosystem_survival_demo
```

Pygame visualization (requires pygame):
```bash
python -m examples.ecosystem_pygame_demo
```

## Design Patterns

### Trait-Driven Behavior

The system uses a trait-driven design where creature behavior emerges from trait combinations:

1. **Behavior Determination**: Traits automatically set initial behavior type
2. **Dynamic Switching**: Hunger overrides behavior when critical
3. **Modifier Stacking**: Multiple traits can affect the same stat

Example combinations:
- `FORAGER + EFFICIENT_METABOLISM`: Perfect gatherer, long-lasting
- `AGGRESSIVE + VORACIOUS`: Combat-focused but needs frequent food
- `CURIOUS + WANDERER`: Explorer that covers lots of ground
- `GLUTTON + HARDY`: Survives despite fast hunger depletion

### Event System

The hunger system integrates with the existing event system:

- `BattleEventType.RESOURCE_COLLECTED`: Fired when creature eats food
- `BattleEventType.CREATURE_FAINT`: Includes starvation deaths

## Performance

- **Hunger Tick**: O(n) per frame, where n = number of creatures
- **Resource Spawning**: O(1) per spawn
- **Resource Collection**: O(n*m) where m = number of resources
- **Behavior Update**: O(n) per frame

For large simulations (>100 creatures), consider:
- Reducing resource spawn rate
- Increasing collection range
- Using spatial partitioning for resource queries

## Future Enhancements

Potential additions to the system:

1. **Resource Variety**: Different food types with varying hunger restoration
2. **Spoilage**: Resources that expire after a time limit
3. **Caching**: Creatures can store food for later
4. **Hunting**: Creatures can hunt each other for food
5. **Metabolism Scaling**: Hunger depletion scales with creature size/level
6. **Seasonal Variation**: Resource spawn rates change over time
7. **Territory Control**: Resource-rich areas that can be controlled

## Troubleshooting

### Creatures starving too quickly
- Increase `resource_spawn_rate`
- Increase `initial_resources`
- Give creatures `EFFICIENT_METABOLISM` trait
- Reduce simulation speed (smaller `delta_time`)

### Creatures not seeking food
- Ensure creatures have hunger < 40
- Check that resources exist in arena
- Verify creatures are alive and mobile
- Check behavior type assignment

### Resources not spawning
- Verify `resource_spawn_rate` > 0
- Check that sufficient time has passed
- Ensure arena has valid spawn area

## Contributing

When adding new ecosystem features:

1. Add trait definitions to `ecosystem_traits.py`
2. Update hunger/foraging logic in relevant systems
3. Add unit tests to `test_hunger.py` or `test_foraging.py`
4. Update this documentation
5. Consider rendering/visualization updates

## License

Same as EvoBattle main project.
