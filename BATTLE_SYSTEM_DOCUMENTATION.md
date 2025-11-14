# Battle System Documentation

## Overview

The EvoBattle battle system is a comprehensive turn-based combat engine that manages battles between creature teams. It features:

- **Turn-based Combat**: Speed-based turn order with random tiebreaking
- **Real-Time Execution**: Step-by-step battle execution with event callbacks for visualization
- **Damage Calculation**: Complex formulas including type effectiveness, defense, and random variance
- **Status Effects**: Poison, burn, paralysis, sleep, and more
- **Ability System**: Physical attacks, special abilities, buffs, debuffs, and healing
- **Battle State Management**: Tracks all battle participants, effects, and progress
- **Event System**: Real-time battle events for animations and visual feedback
- **Dual Modes**: Instant simulation OR step-by-step execution for watching battles

## Battle Modes

### Instant Simulation (Classic)
Run an entire battle instantly - perfect for AI vs AI or quick results:

```python
battle = Battle([player], [enemy])
winner = battle.simulate()  # Battle completes instantly
```

### Real-Time Execution (New!)
Watch battles unfold step-by-step with visual feedback:

```python
battle = Battle([player], [enemy])

# Register callback to visualize events
def on_event(event):
    if event.event_type == BattleEventType.DAMAGE_DEALT:
        animate_damage(event.target, event.value)

battle.add_event_callback(on_event)

# Execute battle step-by-step
battle.start_battle()
while not battle.state.is_battle_over():
    time.sleep(0.5)  # Delay to watch
    battle.execute_turn()
```

## Architecture

### Core Components

```
src/systems/battle.py       # Main battle engine with event system
src/models/status_effect.py # Status effect system
src/models/ability.py        # Ability system (existing)
src/models/creature.py       # Creature system (existing)
src/models/stats.py          # Stats system (existing)
```

### Battle Flow

```
START → TURN_SELECTION → ACTION → END_OF_TURN → [repeat] → BATTLE_END
```

1. **START**: Initialize battle state, emit BATTLE_START event
2. **TURN_SELECTION**: Determine action order based on speed
3. **ACTION**: Execute creature actions, emit events for each action
4. **END_OF_TURN**: Process status effects, tick cooldowns, check victory
5. **BATTLE_END**: Award experience, determine winner

## Real-Time Event System

### Battle Events

The battle system emits 14 types of events:

- **BATTLE_START**: Battle begins
- **TURN_START**: New turn starts
- **CREATURE_TURN**: Creature's turn begins
- **ABILITY_USE**: Creature uses an ability
- **DAMAGE_DEALT**: Damage is dealt
- **HEALING**: HP is restored
- **CRITICAL_HIT**: Critical hit occurs
- **SUPER_EFFECTIVE**: Super effective attack
- **NOT_EFFECTIVE**: Not very effective attack
- **MISS**: Attack misses
- **BUFF_APPLIED**: Stat increase applied
- **DEBUFF_APPLIED**: Stat decrease applied
- **STATUS_APPLIED**: Status effect applied
- **CREATURE_FAINT**: Creature faints
- **TURN_END**: Turn ends
- **BATTLE_END**: Battle ends

### Event Structure

```python
class BattleEvent:
    event_type: BattleEventType  # Type of event
    actor: Optional[Creature]     # Creature performing action
    target: Optional[Creature]    # Target of action
    ability: Optional[Ability]    # Ability used (if any)
    value: Optional[int]          # Damage/healing value
    message: str                  # Human-readable message
    data: Dict                    # Additional event data
    timestamp: float              # When event occurred
```

### Using Events for Visualization

```python
def visualize_battle(event):
    """Callback to visualize battle events"""
    
    if event.event_type == BattleEventType.ABILITY_USE:
        print(f"⚡ {event.actor.name} uses {event.ability.name}!")
        play_sound("ability_use.wav")
        
    elif event.event_type == BattleEventType.DAMAGE_DEALT:
        print(f"💥 {event.target.name} takes {event.value} damage!")
        animate_damage_number(event.target, event.value)
        shake_sprite(event.target)
        
    elif event.event_type == BattleEventType.CRITICAL_HIT:
        print("⚡ Critical hit!")
        play_sound("critical.wav")
        flash_screen()
        
    elif event.event_type == BattleEventType.CREATURE_FAINT:
        print(f"💀 {event.target.name} fainted!")
        play_faint_animation(event.target)

battle.add_event_callback(visualize_battle)
```

## Key Classes

### Battle

The main battle engine that orchestrates combat.

```python
from src.systems.battle import Battle, BattleEventType
from src.models.creature import Creature

# Create battle
battle = Battle(
    player_team=[creature1, creature2],
    enemy_team=[creature3, creature4],
    random_seed=42  # Optional: for deterministic battles
)

# Run battle
winner = battle.simulate()

# Access battle log
for log_entry in battle.get_battle_log():
    print(log_entry)

# Access battle state
state = battle.get_state()
print(f"Turn: {state.current_turn}")
print(f"Phase: {state.phase}")
```

**Key Methods:**
- `simulate()`: Run complete battle until one side wins (instant)
- `start_battle()`: Initialize battle for step-by-step execution
- `execute_turn()`: Execute one complete turn (both creatures act)
- `execute_action(creature, ability, target)`: Execute a single action
- `add_event_callback(callback)`: Register callback for battle events
- `get_battle_log()`: Get list of all battle log messages
- `get_state()`: Access current battle state
- `is_ready_for_action()`: Check if battle can continue

**Real-Time Methods:**
```python
# Step-by-step battle execution
battle.start_battle()  # Initialize

while not battle.state.is_battle_over():
    # Option 1: Execute full turn
    battle.execute_turn()
    
    # Option 2: Execute individual actions
    # player_action = choose_action()
    # battle.execute_action(player, ability, target)

# Process final state
winner_side = battle.state.get_winner()
```

### BattleState

Manages the state of an active battle.

**Attributes:**
- `player_team`: List of creatures on player's team
- `enemy_team`: List of creatures on enemy's team
- `current_turn`: Current turn number
- `phase`: Current battle phase
- `status_effects`: Dict mapping creature IDs to active status effects

**Methods:**
- `get_active_player()`: Get current active player creature
- `get_active_enemy()`: Get current active enemy creature
- `is_battle_over()`: Check if battle has ended
- `get_winner()`: Get winner ('player', 'enemy', or None)

### StatusEffect

Represents temporary battle conditions affecting creatures.

```python
from src.models.status_effect import StatusEffect, StatusEffectType, create_status_effect

# Create custom status effect
poison = StatusEffect(
    name="Deadly Poison",
    effect_type=StatusEffectType.POISON,
    duration=5,
    potency=12  # Damage per turn
)

# Or use predefined template
burn = create_status_effect('burn')
sleep = create_status_effect('sleep')
```

**Status Effect Types:**
- `POISON`: Deals damage over time
- `BURN`: Deals damage over time (higher potency)
- `PARALYSIS`: May prevent actions
- `SLEEP`: Prevents all actions
- `FREEZE`: Prevents all actions
- `CONFUSION`: May cause self-damage
- `STUN`: Prevents action for one turn
- `REGEN`: Heals over time
- `SHIELD`: Reduces damage taken

## Battle Mechanics

### Turn Order

Turn order is determined by creature speed with a small random factor:

```python
effective_speed = creature.stats.speed + random.uniform(-1, 1)
```

The creature with higher effective speed acts first. This prevents strict speed tiers while still making speed meaningful.

### Damage Calculation

Damage is calculated using this formula:

```python
# Base damage
base_damage = ability.power + attacker.stats.attack - (defender.stats.defense / divisor)

# Type effectiveness (0.5x, 1.0x, or 2.0x)
damage = base_damage * type_effectiveness

# Random variance (85% - 100%)
damage = damage * random.uniform(0.85, 1.0)

# Critical hit (6.25% chance for 1.5x)
if critical_hit:
    damage = damage * 1.5

# Minimum damage
damage = max(1, damage)
```

**Damage Types:**
- **Physical**: Reduced by defense / 2
- **Special**: Reduced by defense / 4 (less affected by defense)

### Type Effectiveness

Type matchups affect damage multipliers:

```python
TYPE_EFFECTIVENESS = {
    'fire': {'grass': 2.0, 'water': 0.5, 'ice': 2.0},
    'water': {'fire': 2.0, 'grass': 0.5, 'ground': 2.0},
    'grass': {'water': 2.0, 'fire': 0.5, 'ground': 2.0},
    'electric': {'water': 2.0, 'flying': 2.0, 'ground': 0.0},
    'ice': {'grass': 2.0, 'ground': 2.0, 'flying': 2.0, 'fire': 0.5},
    # ... more types
}
```

- **Super Effective**: 2.0x damage
- **Not Very Effective**: 0.5x damage
- **No Effect**: 0.0x damage (immune)
- **Neutral**: 1.0x damage

### Accuracy System

Abilities have an accuracy value (0-100). Each use rolls against accuracy:

```python
hit = random.randint(1, 100) <= ability.accuracy
```

- 100 accuracy: Always hits
- 90 accuracy: 90% hit chance
- 0 accuracy: Always misses

### Status Effects Processing

Status effects are processed at the end of each turn:

1. **Damage/Healing**: Apply damage or healing from status
2. **Duration Tick**: Decrease duration by 1
3. **Expiration**: Remove effects with duration 0
4. **Action Prevention**: Check if creature can act next turn

### Ability System Integration

The battle system integrates with the existing ability system:

**Ability Types:**
- `PHYSICAL`: Standard physical attack
- `SPECIAL`: Special attack (less affected by defense)
- `HEALING`: Restores HP
- `BUFF`: Increases stats temporarily
- `DEBUFF`: Decreases enemy stats
- `STATUS`: Applies status effects

**Cooldown Management:**
- Abilities trigger their cooldown when used
- Cooldowns tick at end of turn
- Creatures cannot use abilities on cooldown

**Energy System:**
- Abilities cost energy to use
- Energy is not restored during battle
- Creatures must manage energy strategically

## Usage Examples

### Example 1: Simple 1v1 Battle

```python
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ability import create_ability
from src.systems.battle import Battle

# Create creatures
warrior_type = CreatureType(
    name="Warrior",
    base_stats=Stats(max_hp=120, attack=15, defense=12, speed=10)
)

player = Creature(name="Hero", creature_type=warrior_type, level=5)
player.add_ability(create_ability('tackle'))
player.add_ability(create_ability('power_up'))

enemy = Creature(name="Foe", creature_type=warrior_type, level=5)
enemy.add_ability(create_ability('tackle'))

# Run battle
battle = Battle([player], [enemy])
winner = battle.simulate()

print(f"Winner: {winner.name}")
```

### Example 2: Type Effectiveness

```python
# Create fire and water types
fire_type = CreatureType(
    name="Fire",
    base_stats=Stats(max_hp=100, attack=15, defense=10),
    type_tags=["fire"]
)

water_type = CreatureType(
    name="Water",
    base_stats=Stats(max_hp=100, attack=15, defense=10),
    type_tags=["water"]
)

fire = Creature(name="Blaze", creature_type=fire_type, level=5)
fire.add_ability(create_ability('fireball'))

water = Creature(name="Aqua", creature_type=water_type, level=5)
water.add_ability(create_ability('tackle'))

# Fire is weak to water
battle = Battle([fire], [water])
winner = battle.simulate()
# Water likely wins due to type advantage
```

### Example 3: Team Battle

```python
# Create multiple creatures
team1 = [creature1, creature2, creature3]
team2 = [creature4, creature5, creature6]

battle = Battle(team1, team2)
winner = battle.simulate()

# Check which creatures survived
survivors = [c for c in team1 + team2 if c.is_alive()]
print(f"Survivors: {[c.name for c in survivors]}")
```

### Example 4: Battle Analysis

```python
battle = Battle([player], [enemy], random_seed=42)
winner = battle.simulate()

# Analyze battle
log = battle.get_battle_log()
state = battle.get_state()

print(f"Total Turns: {state.current_turn}")
print(f"Actions Taken: {len([l for l in log if 'uses' in l])}")
print(f"Critical Hits: {len([l for l in log if 'Critical' in l])}")
print(f"Misses: {len([l for l in log if 'missed' in l])}")
```

### Example 5: Status Effects (Future)

```python
# Note: Status effect application through abilities is planned
# but not yet fully integrated. Current implementation supports
# status effect tracking and processing.

from src.models.status_effect import create_status_effect

# Create status effect
poison = create_status_effect('poison')

# In battle, this would be applied via ability effects
# Future ability with status application:
toxic_ability = Ability(
    name="Toxic",
    ability_type=AbilityType.STATUS,
    power=0,
    effects=[
        AbilityEffect(
            effect_type="status",
            status_effect_name="poison"
        )
    ]
)
```

## Testing

Comprehensive test coverage is provided in:
- `tests/test_battle.py`: 24 tests covering battle mechanics
- `tests/test_status_effect.py`: 10 tests covering status effects

Run tests:
```bash
python3 -m unittest tests.test_battle -v
python3 -m unittest tests.test_status_effect -v
```

## Extension Points

The battle system is designed to be easily extended:

### 1. Adding New Status Effects

```python
# In status_effect.py, add to PREDEFINED_STATUS_EFFECTS
'custom_status': lambda: StatusEffect(
    name="Custom Status",
    effect_type=StatusEffectType.CUSTOM,
    duration=3,
    potency=5
)
```

### 2. Adding New Ability Types

```python
# In ability.py
class AbilityType(Enum):
    # ... existing types
    CUSTOM = "custom"
```

### 3. Custom Damage Formulas

Extend `Battle._calculate_damage()` to support custom damage calculations:

```python
def _calculate_damage(self, attacker, defender, ability):
    # Your custom damage formula
    pass
```

### 4. Weather and Terrain

The `BattleState` already has placeholders for weather and terrain:

```python
state.weather = "rain"  # Boosts water, weakens fire
state.terrain = "grass"  # Boosts grass moves
```

Implement effects in damage calculation or turn processing.

### 5. New Battle Phases

Add custom phases by extending `BattlePhase` enum and adding phase handlers:

```python
class BattlePhase(Enum):
    # ... existing phases
    CUSTOM_PHASE = "custom_phase"

# In Battle class
def _phase_custom(self):
    # Your custom phase logic
    pass
```

## Performance Considerations

- **Deterministic Battles**: Use `random_seed` parameter for reproducible results
- **Battle Logging**: Logging adds minimal overhead but can be disabled if needed
- **Large Teams**: System handles teams of any size, but battles with 10+ creatures may be slow
- **Status Effects**: Each status effect is processed every turn; limit to ~5 active effects per creature

## Future Enhancements

Planned improvements for the battle system:

1. **Weather System**: Rain, sun, sandstorm affecting abilities
2. **Terrain Effects**: Different battle terrains with bonuses
3. **Held Items**: Equipment affecting battle performance
4. **Combo Attacks**: Team-based combination moves
5. **Battle Animations**: Hooks for animation system
6. **Replay System**: Save and replay battles
7. **AI Strategies**: More sophisticated AI decision-making
8. **Status Effect Abilities**: Full integration of status application
9. **Multi-Target Abilities**: Abilities that hit multiple targets
10. **Switch Mechanics**: Switching between team members mid-battle

## Design Patterns

The battle system uses several design patterns:

- **State Pattern**: BattlePhase enum and phase handlers
- **Strategy Pattern**: Different damage calculations per ability type
- **Observer Pattern**: Battle log as event recorder
- **Command Pattern**: BattleAction encapsulates actions
- **Facade Pattern**: Battle class simplifies complex interactions

## API Reference

### Battle Class

**Constructor:**
```python
Battle(player_team: List[Creature], enemy_team: List[Creature], random_seed: Optional[int] = None)
```

**Methods:**
- `simulate() -> Creature`: Run complete battle, returns winner
- `get_battle_log() -> List[str]`: Get all battle events
- `get_state() -> BattleState`: Get current battle state
- `__repr__() -> str`: String representation

**Private Methods:**
- `_log(message: str)`: Add entry to battle log
- `_phase_start()`: Execute battle start phase
- `_process_turn()`: Process a complete battle turn
- `_determine_turn_order(player, enemy) -> List[Creature]`: Calculate turn order
- `_can_act(creature) -> bool`: Check if creature can act
- `_execute_ai_action(attacker, defender)`: Execute AI-controlled action
- `_execute_ability(attacker, defender, ability)`: Execute ability
- `_calculate_damage(attacker, defender, ability) -> int`: Calculate damage
- `_get_type_effectiveness(attacker, defender) -> float`: Get type multiplier
- `_check_accuracy(accuracy: int) -> bool`: Roll for hit/miss
- `_apply_stat_changes(target, ability, is_buff)`: Apply buff/debuff
- `_apply_ability_effects(attacker, defender, ability)`: Apply ability effects
- `_phase_end_of_turn(player, enemy)`: Execute end-of-turn phase
- `_process_status_effects(creature)`: Process status effects
- `_phase_battle_end()`: Execute battle end phase

### BattleState Class

**Constructor:**
```python
BattleState(player_team: List[Creature], enemy_team: List[Creature])
```

**Attributes:**
- `player_team: List[Creature]`
- `enemy_team: List[Creature]`
- `current_turn: int`
- `phase: BattlePhase`
- `weather: Optional[str]`
- `terrain: Optional[str]`
- `status_effects: Dict[str, List[StatusEffect]]`

**Methods:**
- `get_active_player() -> Optional[Creature]`
- `get_active_enemy() -> Optional[Creature]`
- `is_battle_over() -> bool`
- `get_winner() -> Optional[str]`

### StatusEffect Class

**Constructor:**
```python
StatusEffect(
    name: str,
    effect_type: StatusEffectType,
    duration: int = 3,
    potency: int = 0,
    prevents_action: bool = False,
    applied_turn: int = 0
)
```

**Methods:**
- `tick() -> bool`: Process one turn, returns if still active
- `is_active() -> bool`: Check if effect is active
- `get_damage() -> int`: Get damage for this turn
- `get_healing() -> int`: Get healing for this turn
- `prevents_creature_action() -> bool`: Check if prevents action
- `to_dict() -> Dict`: Serialize to dictionary
- `from_dict(data: Dict) -> StatusEffect`: Deserialize from dictionary

**Helper Functions:**
- `create_status_effect(effect_name: str) -> Optional[StatusEffect]`: Create from template

## Integration with Other Systems

### Creature System
- Uses `Creature` stats for damage calculation
- Applies experience gain to winners
- Manages creature HP and status

### Ability System
- Executes creature abilities
- Manages cooldowns and energy costs
- Applies ability effects

### Stats System
- Uses stats for damage/defense calculations
- Applies stat modifiers from buffs/debuffs
- Manages HP changes

### Trait System
- Traits affect creature stats in battle
- Trait modifiers applied to effective stats

## Troubleshooting

**Battle never ends:**
- Check that creatures have valid abilities
- Verify damage is being applied
- Ensure at least minimum damage (1) is dealt

**Type effectiveness not working:**
- Verify creature types have `type_tags`
- Check TYPE_EFFECTIVENESS mapping
- Ensure tags match exactly (case-sensitive)

**Status effects not applying:**
- Status effect application through abilities is partially implemented
- Effects must be manually added to `battle.state.status_effects`
- Full integration planned for future update

**Abilities always miss:**
- Check ability accuracy value
- Verify random seed isn't causing issues
- Test with 100 accuracy ability

## Contributing

When extending the battle system:

1. Add tests for new features
2. Update this documentation
3. Follow existing code patterns
4. Maintain backward compatibility
5. Add examples for new features

## See Also

- [Core Models Documentation](../MODELS_DOCUMENTATION.md)
- [Ability System Documentation](../src/models/ability.py)
- [Battle Examples](../examples/battle_system_example.py)
- [Test Suite](../tests/test_battle.py)
