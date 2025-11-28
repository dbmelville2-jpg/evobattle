# Grass Growth Enhancement System

## Overview
The Grass Growth Enhancement System adds interesting simulation-based mechanics to pellet (grass/food) reproduction in EvoBattle. Instead of just random spawning, pellets now grow more dynamically based on environmental factors and creature interactions.

## Features

### 1. Nutrient Zones 🌱
**What it does:** When creatures die, they create nutrient-rich zones where pellets grow faster.

**How it works:**
- Each creature death creates a circular nutrient zone
- Zone strength scales with creature size (1.05x to 1.15x growth multiplier)
- Zone radius: 8-12 units (small, localized effect)
- Zones last for 30 seconds before fading
- Multiple zones can overlap for cumulative effects

**Simulation logic:** Dead creatures decompose and enrich the soil, making it better for plant growth.

### 2. Pollination System 🐝
**What it does:** Creatures spread pellet seeds as they move through the arena.

**How it works:**
- When a creature moves near a pellet (within 5 units), it "visits" the pellet
- If the creature revisits a pellet, there's a 3% chance to pollinate
- Pollination creates a new pellet 5-15 units away from the parent
- Each creature can only pollinate once per 5 seconds
- Pollinated pellets inherit parent traits with mutations

**Simulation logic:** Like bees spreading pollen, creatures inadvertently help plants reproduce by carrying seeds on their bodies.

### 3. Growth Pulses ☀️🌧️
**What it does:** Periodic environmental events boost pellet growth (simulating favorable weather).

**How it works:**
- Growth pulses occur every 60 seconds
- Each pulse lasts 8 seconds
- Provides a 10% growth rate boost (1.10x multiplier)
- Announced in the game log: "Growth pulse! Sunlight and rain boost grass growth!"
- Stacks with other bonuses

**Simulation logic:** Periodic rain and sunshine create ideal growing conditions for plants.

### 4. Symbiotic Bonus 🦌
**What it does:** Pellets near herbivore creatures grow faster (symbiotic relationship).

**How it works:**
- Herbivores are detected by traits (Forager, Herbivore, etc.)
- Pellets within 15 units of herbivores get a growth boost
- Bonus scales with number of nearby herbivores (up to 8% boost)
- 1 herbivore: ~5% boost
- 2+ herbivores: 8% boost (cap)

**Simulation logic:** Herbivores provide natural fertilization and seed spreading, helping plants grow.

## Combined Effects

All growth bonuses **multiply together** for powerful synergies:

| Condition | Multiplier |
|-----------|-----------|
| Base (no bonuses) | 1.00x |
| Nutrient zone only | 1.05-1.15x |
| Growth pulse only | 1.10x |
| 2 Herbivores only | 1.08x |
| **All combined** | **~1.31x** |

Example: A pellet in a nutrient zone, during a growth pulse, with 2 nearby herbivores grows at 131% normal rate!

## Performance Impact

The system is optimized for 60 FPS gameplay:

- Nutrient zones: Simple distance checks (O(1) per pellet)
- Growth pulses: Global state, no per-pellet overhead
- Symbiotic bonus: Uses existing spatial grid (O(k) where k is nearby creatures)
- Pollination: Only triggered when creatures are near pellets

**Result:** No measurable performance impact even with 100+ pellets.

## Balance

The system is carefully balanced to provide more pellets without overpopulation:

- **Baseline (no zones, 30s):** +40% growth (15 → 21 pellets)
- **With nutrient zones (30s):** +100% growth (15 → 30 pellets)
- **Long term (60s with zones):** Moderate exponential growth

This ensures:
- ✓ Creatures have enough food
- ✓ Pellets don't overwhelm the arena
- ✓ Natural ebb and flow to the ecosystem
- ✓ Interesting spatial patterns (pellets cluster near death sites)
- ✓ Nutrient zones fade after 30s to prevent permanent hotspots

## Integration

The system is automatically enabled in `SpatialBattle`:

```python
# Grass growth is created automatically
battle = SpatialBattle(
    creatures,
    arena_width=120.0,
    arena_height=100.0,
    resource_spawn_rate=0.06,
    initial_resources=20
)

# Access the system if needed
battle.grass_growth.get_nutrient_zone_count()
battle.grass_growth.is_growth_pulse_active()
```

To disable specific features:

```python
# Manually create with features disabled
from src.systems.grass_growth_system import GrassGrowthSystem

grass_growth = GrassGrowthSystem(
    arena_width=120.0,
    arena_height=100.0,
    enable_pollination=False,  # Disable pollination
    enable_nutrient_zones=True,
    enable_growth_pulses=True,
    enable_symbiotic_bonus=True
)
```

## Events

The system emits battle events for visual feedback:

**Growth Pulse Start:**
```python
BattleEvent(
    event_type=BattleEventType.PELLET_SPAWN,
    message="Growth pulse! Sunlight and rain boost grass growth!",
    data={'growth_pulse': True, 'multiplier': 1.15}
)
```

**Pollination:**
```python
BattleEvent(
    event_type=BattleEventType.PELLET_SPAWN,
    actor=creature,
    message="CreatureName pollinated grass! Seeds spread.",
    data={'pollination': True, 'position': (x, y)}
)
```

## Testing

Run the included test scripts:

```bash
# Quick feature test
python test_grass_growth.py

# Long-term balance test
python test_grass_growth_longterm.py
```

## Design Philosophy

The grass growth system follows these principles:

1. **Simple rules, complex outcomes:** Each mechanic is simple, but they combine to create interesting emergent behavior
2. **Spatial patterns:** Pellets cluster around death sites and herbivore movement paths
3. **Temporal dynamics:** Growth pulses create periods of abundance and scarcity
4. **Ecosystem realism:** All mechanics are based on real ecological relationships
5. **Performance first:** No feature sacrifices the 60 FPS target

## Future Extensions

Potential additions (not implemented):

- Seasonal cycles (longer growth/dormancy periods)
- Pellet competition (neighboring pellets inhibit each other)
- Soil degradation (areas become less fertile over time)
- Weather patterns (predictable vs random pulses)
- Creature-specific pollination (some creatures better pollinators)

## File Structure

```
src/systems/
  ├── grass_growth_system.py    # Core grass growth logic
  └── battle_spatial.py          # Integration with battle system

test_grass_growth.py              # Quick feature test
test_grass_growth_longterm.py     # Long-term balance test
```

## API Reference

### `GrassGrowthSystem`

```python
class GrassGrowthSystem:
    def __init__(
        arena_width: float,
        arena_height: float,
        enable_pollination: bool = True,
        enable_nutrient_zones: bool = True,
        enable_growth_pulses: bool = True,
        enable_symbiotic_bonus: bool = True
    )
    
    def on_creature_death(x: float, y: float, creature_size: float)
    """Create nutrient zone when creature dies"""
    
    def update(delta_time: float)
    """Update system state (pulses, zone expiration)"""
    
    def get_growth_rate_multiplier(
        pellet: Pellet,
        nearby_creatures: Optional[List[BattleCreature]]
    ) -> float
    """Calculate total growth multiplier for pellet"""
    
    def try_pollination(
        creature: BattleCreature,
        pellet: Pellet,
        current_time: float
    ) -> Optional[Pellet]
    """Attempt pollination, returns new pellet if successful"""
    
    def is_growth_pulse_active() -> bool
    """Check if growth pulse is currently active"""
    
    def get_nutrient_zone_count() -> int
    """Get number of active nutrient zones"""
```

### `NutrientZone`

```python
class NutrientZone:
    def __init__(x: float, y: float, strength: float, radius: float)
    
    def is_expired() -> bool
    """Check if zone has expired (> 60s old)"""
    
    def get_growth_multiplier(pellet_x: float, pellet_y: float) -> float
    """Get growth multiplier for pellet at position"""
```

## Troubleshooting

**Pellets not growing fast enough?**
- Check that creatures are dying (creates nutrient zones)
- Verify herbivores are near pellet clusters
- Wait for growth pulses (every 60 seconds)

**Pellets growing too fast?**
- Reduce `growth_pulse_multiplier` in `GrassGrowthSystem.__init__`
- Reduce `strength` in `NutrientZone` creation
- Increase `pollination_cooldown`

**Not seeing pollination?**
- Creatures must revisit pellets (visit, leave, return)
- 3% chance per revisit (may take time to observe)
- Check battle log for "pollinated grass!" messages
