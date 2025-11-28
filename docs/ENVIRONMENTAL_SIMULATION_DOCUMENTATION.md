# Environmental Simulation System Documentation

## Overview

The Environmental Simulation System adds deep environmental interactions to the Evolution Battle Game. Weather, terrain, day/night cycles, and environmental hazards dynamically affect creature behavior, survival, and combat effectiveness.

## Table of Contents

1. [Features](#features)
2. [Core Components](#core-components)
3. [Environmental Traits](#environmental-traits)
4. [Integration](#integration)
5. [Usage Examples](#usage-examples)
6. [API Reference](#api-reference)

## Features

### Weather System
Dynamic weather patterns that affect gameplay:
- **5 Weather Types**: Clear, Rainy, Stormy, Foggy, Drought
- **Environmental Parameters**:
  - Temperature (-20°C to 50°C)
  - Humidity (0% to 100%)
  - Precipitation intensity
  - Wind speed
  - Visibility

**Effects:**
- Movement speed modification (0.5x to 1.2x)
- Hunger depletion rate (0.8x to 1.4x)
- Resource quality (0.6x to 1.3x)

### Terrain System
6 distinct terrain types with unique properties:

| Terrain | Movement | Visibility | Cover | Resource Richness |
|---------|----------|------------|-------|-------------------|
| Grass   | 1.0x     | 1.0x       | 0%    | 1.0x              |
| Rocky   | 0.7x     | 0.8x       | 20%   | 0.8x              |
| Water   | 0.3x     | 1.0x       | 0%    | 1.0x              |
| Forest  | 0.8x     | 0.4x       | 30%   | 1.2x              |
| Desert  | 1.3x     | 1.0x       | 0%    | 0.6x              |
| Marsh   | 0.5x     | 0.7x       | 10%   | 1.3x              |

### Day/Night Cycle
Realistic time progression affecting gameplay:

| Time of Day | Hours   | Visibility | Activity |
|-------------|---------|------------|----------|
| Dawn        | 5-7     | 0.6x       | 0.8x     |
| Day         | 7-17    | 1.0x       | 1.0x     |
| Dusk        | 17-19   | 0.6x       | 0.9x     |
| Night       | 19-5    | 0.3x       | 0.5x     |

**Configurable:** Real-world time maps to game time (default: 5 minutes = 24 hours)

### Environmental Hazards
Dangerous zones that creatures must avoid or endure:

| Hazard Type      | Effect                           |
|------------------|----------------------------------|
| Fire             | Direct damage over time          |
| Poison Cloud     | Gradual health reduction         |
| Quicksand        | Severe movement penalty + damage |
| Thorns           | Contact damage                   |
| Electrical       | Random damage spikes             |

**Properties:**
- Position and radius (area of effect)
- Damage per second
- Duration (temporary or permanent)
- Distance-based damage falloff

## Core Components

### Environment Class

Main environmental simulation manager:

```python
from src.models.environment import Environment

env = Environment(
    width=100.0,
    height=100.0,
    cell_size=10.0,
    enable_weather=True,
    enable_day_night=True,
    day_night_cycle_duration=300.0  # 5 minutes = 24 hours
)
```

**Key Methods:**
- `update(delta_time)` - Update environmental systems
- `get_terrain_at(position)` - Get terrain at position
- `get_combined_movement_modifier(position)` - Get total movement modifier
- `get_combined_visibility(position)` - Get total visibility
- `get_resource_quality_at(position)` - Get resource quality modifier
- `get_defensive_cover(position)` - Get defensive cover bonus
- `add_hazard(hazard)` - Add environmental hazard
- `get_total_hazard_damage(position)` - Calculate hazard damage at position

### WeatherConditions

Represents current weather state:

```python
from src.models.environment import WeatherConditions, WeatherType

weather = WeatherConditions(
    weather_type=WeatherType.RAINY,
    temperature=18.0,
    humidity=0.8,
    precipitation=0.5
)

# Get modifiers
movement_mod = weather.get_movement_modifier()  # 0.9x in rain
hunger_mod = weather.get_hunger_modifier()      # 1.0x
quality_mod = weather.get_resource_quality_modifier()  # 1.15x in rain
```

### TerrainCell

Represents a grid cell with terrain properties:

```python
from src.models.environment import TerrainCell, TerrainType
from src.models.spatial import Vector2D

cell = TerrainCell(
    terrain_type=TerrainType.FOREST,
    position=Vector2D(50, 50),
    resource_richness=1.2
)

movement = cell.get_movement_modifier()    # 0.8x in forest
visibility = cell.get_visibility_modifier()  # 0.4x in forest
cover = cell.get_cover_bonus()             # 0.3 (30% defense bonus)
```

### DayNightCycle

Manages time progression:

```python
from src.models.environment import DayNightCycle

cycle = DayNightCycle(
    cycle_duration=300.0,  # 5 minutes = 24 hours
    start_hour=7.0         # Start at 7 AM
)

current_hour = cycle.get_current_hour()       # 0.0 to 24.0
time_of_day = cycle.get_time_of_day()        # DAWN, DAY, DUSK, or NIGHT
visibility = cycle.get_visibility_modifier()  # 0.3 to 1.0
activity = cycle.get_activity_modifier()      # 0.5 to 1.2
```

### EnvironmentalHazard

Dangerous environmental feature:

```python
from src.models.environment import EnvironmentalHazard, HazardType
from src.models.spatial import Vector2D

hazard = EnvironmentalHazard(
    hazard_type=HazardType.FIRE,
    position=Vector2D(75, 75),
    radius=15.0,
    damage=5.0,
    duration=-1  # -1 = permanent
)

is_active = hazard.is_active()
affects = hazard.affects_position(Vector2D(80, 80))
damage = hazard.get_damage_at_position(Vector2D(80, 80))
```

## Environmental Traits

28 environmental adaptation traits that creatures can have:

### Weather Adaptation Traits
- **Cold Blooded** - Performance varies with temperature
- **Warm Blooded** - Immune to temperature effects (+10% defense)
- **Thick Fur** - Reduced hunger in cold, +15% defense
- **Heat Resistant** - +25% speed in hot conditions
- **Storm Walker** - Unaffected by storms, +10% attack in storms
- **Drought Survivor** - 40% slower hunger during droughts

### Terrain Adaptation Traits
- **Aquatic** - +100% speed in water, -30% on land
- **Rock Climber** - +50% speed on rocky terrain, +20% defense
- **Forest Dweller** - +40% speed in forests, +25% stealth
- **Desert Adapted** - +30% speed in desert, 50% reduced hunger
- **Marsh Navigator** - +80% speed in marsh
- **All Terrain** - No terrain penalties, +5% speed everywhere

### Time of Day Traits
- **Nocturnal** - +30% stats at night, -15% during day
- **Diurnal** - +20% stats during day, -10% at night
- **Crepuscular** - +25% stats at dawn/dusk
- **Tireless** - No time-of-day penalties

### Hazard Resistance Traits
- **Fire Proof** - Immune to fire damage (+10% defense)
- **Poison Resistant** - 70% reduced poison damage
- **Sure Footed** - Immune to quicksand
- **Thick Hide** - Immune to thorns, +20% defense
- **Grounded** - 80% reduced electrical damage
- **Hazard Sense** - AI actively avoids hazards

### Environmental Awareness Traits
- **Weather Sense** - Predicts weather changes
- **Tracker** - Identifies good resource areas
- **Camouflage** - +40% stealth, harder to detect
- **Environmental Master** - +15% all stats, benefits from all conditions (legendary)

## Integration

### Battle System Integration

Enable environmental simulation in battles:

```python
from src.systems.battle_spatial import SpatialBattle
from src.models.environment import Environment

# Option 1: Enable with defaults
battle = SpatialBattle(
    creatures,
    arena_width=100.0,
    arena_height=100.0,
    enable_environment=True
)

# Option 2: Provide custom environment
env = Environment(width=100.0, height=100.0)
battle = SpatialBattle(
    creatures,
    environment=env
)
```

**Integration Points:**
1. **Movement Speed**: `environment.get_combined_movement_modifier(position)` applied to creature movement
2. **Hunger**: `weather.get_hunger_modifier()` applied to hunger depletion
3. **Resources**: `environment.get_resource_quality_at(position)` modifies spawned food quality
4. **Hazards**: `environment.get_total_hazard_damage(position)` applies damage each update
5. **Traits**: Creature traits modify environmental effects

### Creature Trait Integration

Creatures with environmental traits get automatic bonuses:

```python
from src.models.creature import Creature
from src.models.trait import Trait

# Create creature with aquatic trait
creature = Creature(...)
creature.traits.append(Trait(
    name="Aquatic",
    description="Fast in water",
    trait_type="environmental"
))

# In battle, creature automatically gets:
# - 2x speed in water terrain
# - 0.7x speed on land terrain
```

### Genetics System Integration

Environmental traits can be inherited:

```python
from src.models.environmental_traits import ALL_ENVIRONMENTAL_TRAITS
from src.systems.breeding import Breeding

breeding = Breeding()

# Environmental traits are inherited like any other trait
offspring = breeding.breed(parent1, parent2)
# offspring may inherit parent environmental traits
```

## Usage Examples

### Basic Environmental Battle

```python
from src.systems.battle_spatial import SpatialBattle
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats

# Create creatures
creature_type = CreatureType(
    name="Survivor",
    base_stats=Stats(max_hp=100, attack=12, defense=10, speed=15)
)
creatures = [Creature(name=f"C{i}", creature_type=creature_type, level=1) for i in range(10)]

# Create battle with environment
battle = SpatialBattle(
    creatures,
    arena_width=100.0,
    arena_height=100.0,
    enable_environment=True,
    initial_resources=20
)

# Run simulation
while not battle.is_over:
    battle.update(1.0)  # Update 1 second
```

### Custom Environment Setup

```python
from src.models.environment import Environment, WeatherType, EnvironmentalHazard, HazardType
from src.models.spatial import Vector2D

# Create custom environment
env = Environment(width=100.0, height=100.0)

# Set weather
env.weather.weather_type = WeatherType.STORMY
env.weather.temperature = 5.0  # Cold storm
env.weather.precipitation = 0.8

# Add hazards
env.add_hazard(EnvironmentalHazard(
    hazard_type=HazardType.FIRE,
    position=Vector2D(50, 50),
    radius=20.0,
    damage=10.0
))

# Use in battle
battle = SpatialBattle(creatures, environment=env)
```

### Creatures with Environmental Adaptations

```python
from src.models.environmental_traits import AQUATIC, FIRE_PROOF, NOCTURNAL

# Create specialized creatures
aquatic_creature = Creature(...)
aquatic_creature.traits.append(AQUATIC)

fire_resistant_creature = Creature(...)
fire_resistant_creature.traits.append(FIRE_PROOF)

night_hunter = Creature(...)
night_hunter.traits.append(NOCTURNAL)

# These creatures will automatically benefit from their traits
```

### Monitoring Environmental State

```python
# Check environment state
env_data = battle.environment.to_dict()
print(f"Weather: {env_data['weather']['type']}")
print(f"Temperature: {env_data['weather']['temperature']}°C")
print(f"Time: {env_data['time_of_day']}")

# Check specific location
position = Vector2D(50, 50)
terrain = battle.environment.get_terrain_at(position)
print(f"Terrain: {terrain.terrain_type.value}")
print(f"Movement modifier: {battle.environment.get_combined_movement_modifier(position):.2f}x")
print(f"Visibility: {battle.environment.get_combined_visibility(position):.0%}")
```

## API Reference

### Environment

```python
Environment(
    width: float = 100.0,
    height: float = 100.0,
    cell_size: float = 10.0,
    enable_weather: bool = True,
    enable_day_night: bool = True,
    day_night_cycle_duration: float = 300.0
)
```

**Attributes:**
- `weather: WeatherConditions` - Current weather state
- `day_night: DayNightCycle` - Day/night cycle manager
- `hazards: List[EnvironmentalHazard]` - Active hazards
- `terrain_grid: Dict[Tuple[int, int], TerrainCell]` - Terrain cells

**Methods:**
- `update(delta_time: float)` - Update all environmental systems
- `get_terrain_at(position: Vector2D) -> Optional[TerrainCell]`
- `get_combined_movement_modifier(position: Vector2D) -> float`
- `get_combined_visibility(position: Vector2D) -> float`
- `get_resource_quality_at(position: Vector2D) -> float`
- `get_defensive_cover(position: Vector2D) -> float`
- `add_hazard(hazard: EnvironmentalHazard)`
- `get_hazards_at(position: Vector2D) -> List[EnvironmentalHazard]`
- `get_total_hazard_damage(position: Vector2D) -> float`
- `to_dict() -> dict` - Serialize state

### WeatherConditions

```python
WeatherConditions(
    weather_type: WeatherType = WeatherType.CLEAR,
    temperature: float = 20.0,
    humidity: float = 0.5,
    precipitation: float = 0.0,
    wind_speed: float = 0.0,
    visibility: float = 1.0
)
```

**Methods:**
- `get_movement_modifier() -> float` - Returns 0.5 to 1.2
- `get_hunger_modifier() -> float` - Returns 0.8 to 1.4
- `get_resource_quality_modifier() -> float` - Returns 0.6 to 1.3

### TerrainCell

```python
TerrainCell(
    terrain_type: TerrainType,
    position: Vector2D,
    resource_richness: float = 1.0,
    danger_level: float = 0.0
)
```

**Methods:**
- `get_movement_modifier() -> float` - Returns 0.3 to 1.3
- `get_visibility_modifier() -> float` - Returns 0.4 to 1.0
- `get_cover_bonus() -> float` - Returns 0.0 to 0.3

### DayNightCycle

```python
DayNightCycle(
    cycle_duration: float = 300.0,
    start_hour: float = 7.0
)
```

**Methods:**
- `get_current_hour() -> float` - Returns 0.0 to 24.0
- `get_time_of_day() -> TimeOfDay` - Returns DAWN, DAY, DUSK, or NIGHT
- `get_visibility_modifier() -> float` - Returns 0.3 to 1.0
- `get_activity_modifier() -> float` - Returns 0.5 to 1.2

### EnvironmentalHazard

```python
EnvironmentalHazard(
    hazard_type: HazardType,
    position: Vector2D,
    radius: float = 5.0,
    damage: float = 5.0,
    duration: float = -1.0
)
```

**Methods:**
- `is_active() -> bool`
- `affects_position(position: Vector2D) -> bool`
- `get_damage_at_position(position: Vector2D) -> float`

## Performance Considerations

The environmental system is optimized for performance:

1. **Terrain Grid**: Uses spatial hash grid for O(1) terrain lookups
2. **Weather Updates**: Only recalculates periodically (every 60 seconds by default)
3. **Hazard Cleanup**: Expired hazards are automatically removed
4. **Modifier Caching**: Environmental modifiers are calculated once per update

**Typical Overhead:**
- Small battles (10-50 creatures): <1% performance impact
- Medium battles (50-200 creatures): <3% performance impact
- Large battles (200+ creatures): <5% performance impact

## See Also

- [Battle System Documentation](BATTLE_SYSTEM_DOCUMENTATION.md)
- [Living World Documentation](LIVING_WORLD_DOCUMENTATION.md)
- [Ecosystem Documentation](ECOSYSTEM_DOCUMENTATION.md)
- [Genetics System Documentation](GENETICS_SYSTEM_DOCUMENTATION.md)
- [Example: Environmental Demo](../examples/environmental_demo.py)
