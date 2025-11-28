# Deep Simulation System Documentation

## Overview

The Deep Simulation System provides comprehensive tracking of creature injuries, social interactions, and pellet lifecycle events. This system makes every creature and pellet have a complete, observable story throughout their existence in the simulation.

## Components

### 1. Injury Tracker (`src/models/injury_tracker.py`)

Tracks detailed damage and injury information for each creature.

#### Features
- **Injury Records**: Every damage event is logged with:
  - Attacker information
  - Damage type (physical, special, starvation, poison, burning, environmental)
  - Damage amount
  - Health before/after
  - Critical hit status
  - Location

- **Attacker Statistics**: Aggregated stats per attacker:
  - Total damage dealt
  - Number of hits
  - Critical hits count
  - Near-death hits
  - First/last encounter timestamps

- **Aggregate Metrics**:
  - Total damage received
  - Near-death experience count (< 10% HP threshold)
  - Critical hits received
  - Starvation damage tracking
  - Damage breakdown by type
  - Survival rate calculation

#### Usage Example
```python
from src.models.creature import Creature
from src.models.injury_tracker import DamageType

creature = Creature(name="Hero")

# Record an injury
creature.injury_tracker.record_injury(
    attacker_id="villain_123",
    attacker_name="Dark Knight",
    damage_type=DamageType.PHYSICAL,
    damage_amount=50.0,
    health_before=100.0,
    health_after=50.0,
    was_critical=True,
    location=(10.0, 20.0)
)

# Query statistics
total_damage = creature.injury_tracker.get_total_damage_received()
near_deaths = creature.injury_tracker.near_death_count
most_dangerous = creature.injury_tracker.get_most_dangerous_attacker()
```

### 2. Interaction Tracker (`src/models/interactions.py`)

Tracks social interactions between creatures.

#### Features
- **Interaction Types**:
  - Food competition
  - Mating attempts/successes
  - Territorial displays
  - Flee/chase behaviors
  - Social observations
  - Alliance formation
  - Cooperation

- **Food Competition**: Track pellet contests with:
  - All competitors
  - Winner
  - Location

- **Mating Records**: Track breeding attempts with:
  - Partner information
  - Success/failure
  - Offspring details

- **Partner Statistics**: Per-partner tracking of:
  - Mating attempts/successes
  - Food competitions and win rate
  - First/last interaction timestamps

#### Usage Example
```python
from src.models.creature import Creature

creature = Creature(name="Alpha")

# Record food competition
creature.interaction_tracker.record_food_competition(
    pellet_id="pellet_456",
    competitors=["creature_1", "creature_2", "creature_3"],
    winner_id="creature_1",
    location=(15.0, 25.0)
)

# Record mating
creature.interaction_tracker.record_mating_attempt(
    partner_id="creature_789",
    partner_name="Beta",
    success=True,
    offspring_id="offspring_123",
    offspring_name="Gamma"
)

# Query statistics
win_rate = creature.interaction_tracker.get_food_competition_win_rate()
mating_rate = creature.interaction_tracker.get_mating_success_rate()
summary = creature.interaction_tracker.get_interaction_summary()
```

### 3. Pellet Life History (`src/models/pellet_history.py`)

Tracks complete lifecycle of each pellet.

#### Features
- **Lifecycle Events**:
  - Spawn
  - Reproduction
  - Mutation
  - Targeting by creatures
  - Avoidance by creatures
  - Consumption
  - Death

- **Creature Targeting**: Per-creature statistics:
  - Times targeted
  - Times avoided
  - Distance traveled to target
  - First/last targeting timestamps

- **Lineage Tracking**:
  - Parent pellet ID
  - Offspring IDs list
  - Generation number

- **Metrics**:
  - Lifetime duration
  - Reproduction count
  - Mutation count
  - Targeting rate (targeted vs avoided)

#### Usage Example
```python
from src.models.pellet import Pellet

pellet = Pellet(x=10.0, y=20.0)

# Record lifecycle events
pellet.history.record_spawn(location=(10.0, 20.0))
pellet.history.record_targeted(
    creature_id="creature_123",
    location=(12.0, 22.0),
    distance=5.0
)
pellet.history.record_reproduction(
    offspring_id="pellet_456",
    location=(11.0, 21.0)
)
pellet.history.record_eaten(
    creature_id="creature_789",
    creature_name="Hungry",
    nutritional_value=25.0
)

# Query statistics
lifetime = pellet.history.get_lifetime()
targeting_rate = pellet.history.get_targeting_rate()
most_interested = pellet.history.get_most_interested_creature()
```

## Integration with Living World System

### Event Handlers

The `LivingWorldBattleEnhancer` class provides event handlers that automatically track events:

#### `on_damage_dealt(attacker, defender, damage, damage_type, was_critical, location)`
Called when damage is dealt. Automatically records injury in defender's tracker.

#### `on_food_competition(pellet_id, competitors, winner, location)`
Called when multiple creatures compete for food. Records competition in all participants' trackers.

#### `on_pellet_targeted(pellet, creature, distance, location)`
Called when a creature targets a pellet. Records targeting in pellet's history.

#### `on_pellet_avoided(pellet, creature, reason, location)`
Called when a creature avoids a pellet. Records avoidance in pellet's history.

#### `on_pellet_eaten(pellet, creature, location)`
Called when a pellet is consumed. Records consumption in pellet's history.

### Integration Example
```python
from src.systems.living_world import LivingWorldBattleEnhancer

enhancer = LivingWorldBattleEnhancer(battle_system)

# These are called automatically during battle
enhancer.on_attack_made(attacker, defender, damage=50, was_critical=True, location=(10, 20))
enhancer.on_food_competition(pellet.pellet_id, [creature1, creature2], creature1, (5, 5))
enhancer.on_pellet_eaten(pellet, creature, (10, 20))
```

## User Interface

### Creature Inspector - Health & Injuries Section

Displays comprehensive injury information:
- Total damage taken
- Near-death experiences count
- Critical hits received
- Survival rate percentage
- Most dangerous attacker
- Recent injury timeline with details

### Creature Inspector - Social Interactions Section

Shows interaction statistics:
- Total interactions count
- Food competition stats and win rate
- Mating attempts and success rate
- Most frequent interaction partner

### Pellet Inspector

Complete pellet information panel:
- **Traits**: Nutritional value, size, growth rate, palatability, toxicity
- **Lifecycle**: Status (alive/dead), age, reproduction count, offspring count
- **Creature Interactions**: Targeting/avoidance statistics, most interested creature
- **Lineage**: Parent and offspring information
- **Recent Events**: Timeline of significant events

### Usage in Game

1. **Viewing Creature Details**: Click on a creature to open the inspector
2. **Scrolling**: Use mouse wheel to scroll through information
3. **Viewing Pellet Details**: Click on a pellet to open pellet inspector
4. **Closing**: Click the ✕ button or press the toggle key

## Performance Considerations

### Event Logging Overhead
- Each event log is approximately <1ms
- Events are stored in memory-efficient lists
- Old events can be pruned after a configurable time period

### Memory Management
- Events use lightweight dataclasses
- Serialization uses efficient dict representation
- Consider implementing event compression for very long simulations

### Optimization Tips
1. **Limit Event History**: Keep only recent N events (e.g., last 1000)
2. **Aggregate Old Data**: Summarize old events into statistics
3. **Lazy Loading**: Load full history only when inspector is opened
4. **Batch Updates**: Update UI less frequently than event recording

## Serialization

All trackers support full serialization:

```python
# Creature with trackers
data = creature.to_dict()
# Includes 'injury_tracker' and 'interaction_tracker' keys

# Restore from dict
restored_creature = Creature.from_dict(data)
# Trackers are fully restored

# Pellet with history
pellet_data = pellet.to_dict()
# Includes 'history' key

restored_pellet = Pellet.from_dict(pellet_data)
# History is fully restored
```

## Testing

The system includes comprehensive unit tests:

### Test Coverage
- `tests/test_injury_tracker.py`: 16 tests covering injury tracking
- `tests/test_interactions.py`: 22 tests covering interaction tracking
- `tests/test_pellet_history.py`: 21 tests covering pellet lifecycle

### Running Tests
```bash
# All deep simulation tests
python -m unittest tests.test_injury_tracker tests.test_interactions tests.test_pellet_history

# Individual test files
python -m unittest tests.test_injury_tracker -v
python -m unittest tests.test_interactions -v
python -m unittest tests.test_pellet_history -v
```

## Future Enhancements

Potential additions not currently implemented:

1. **Machine Learning Integration**: Pattern recognition on interaction data
2. **Export Functionality**: Export history data for external analysis
3. **Replay System**: Replay interesting events or battles
4. **Achievement System**: Detect and reward exceptional behaviors
5. **Ecosystem Health Metrics**: Aggregate statistics across population
6. **Advanced Filtering**: Query system for finding specific events
7. **Data Visualization**: Charts and graphs for statistics
8. **Event Compression**: Efficient storage for very long simulations

## API Reference

### InjuryTracker

```python
class InjuryTracker:
    def record_injury(attacker_id, attacker_name, damage_type, damage_amount, 
                     health_before, health_after, was_critical, location)
    def get_total_damage_received() -> float
    def get_damage_by_attacker(attacker_id: str) -> float
    def get_most_dangerous_attacker() -> Optional[AttackerStats]
    def get_recent_injuries(count: int) -> List[InjuryRecord]
    def get_critical_hits() -> List[InjuryRecord]
    def get_near_death_injuries() -> List[InjuryRecord]
    def get_survival_rate() -> float
    def get_damage_breakdown() -> Dict[str, float]
```

### InteractionTracker

```python
class InteractionTracker:
    def record_interaction(interaction_type, target_id, target_name, success, location, context)
    def record_food_competition(pellet_id, competitors, winner_id, location)
    def record_mating_attempt(partner_id, partner_name, success, offspring_id, offspring_name, location)
    def get_food_competition_win_rate() -> float
    def get_mating_success_rate() -> float
    def get_most_frequent_partner() -> Optional[PartnerStats]
    def get_recent_interactions(count: int) -> List[InteractionRecord]
    def get_interaction_summary() -> Dict[str, int]
```

### PelletLifeHistory

```python
class PelletLifeHistory:
    def record_spawn(location, parent_id)
    def record_reproduction(offspring_id, location)
    def record_mutation(mutation_details)
    def record_targeted(creature_id, location, distance)
    def record_avoided(creature_id, location, reason)
    def record_eaten(creature_id, creature_name, location, nutritional_value)
    def record_death(cause, location)
    def get_lifetime() -> float
    def is_alive() -> bool
    def get_targeting_rate() -> float
    def get_most_interested_creature() -> Optional[CreatureTargetingStats]
    def get_recent_events(count: int) -> List[PelletLifeEvent]
```

## Troubleshooting

### Common Issues

**Issue**: High memory usage with large populations
- **Solution**: Implement event pruning, keep only recent N events

**Issue**: Slow UI rendering with long histories
- **Solution**: Limit displayed events, use pagination

**Issue**: Events not being recorded
- **Solution**: Ensure event handlers are being called from battle/ecosystem systems

**Issue**: Serialization fails
- **Solution**: Check that all custom objects have proper to_dict/from_dict methods

## Contributing

When extending this system:

1. Add new event types to appropriate enum classes
2. Update serialization methods if adding new fields
3. Write unit tests for new functionality
4. Update documentation
5. Consider performance impact of additional tracking
6. Maintain backwards compatibility with saved data

## Credits

Part of the EvoBattle Living World System
Implements Deep Simulation as specified in the agent coordination framework
