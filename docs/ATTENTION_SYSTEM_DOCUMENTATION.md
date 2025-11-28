# Attention Span and Focus System Documentation

## Overview

The Attention Span and Focus System addresses the issue of agents rapidly switching between tasks and targets without persistence or clear prioritization. This system introduces a comprehensive attention management framework that:

- **Prioritizes all stimuli** across domains (combat, foraging, fleeing, exploring, hazards, social)
- **Enforces commitment times** to prevent rapid switching
- **Uses trait-based modifiers** to create distinct behavioral personalities
- **Provides debug visualization** for tuning and understanding agent behavior

## Problem Solved

### Before the Attention System:
- ❌ Agents switched between targets/behaviors every frame
- ❌ No persistence or commitment to chosen actions
- ❌ Reactionary decision-making without clear priorities
- ❌ "Buzzing" behavior patterns from indecisive oscillation
- ❌ No trait influence on focus or distractibility

### After the Attention System:
- ✅ Agents commit to tasks for configurable minimum times
- ✅ Clear priority hierarchy (fleeing > combat > foraging > exploring)
- ✅ Urgency modifiers amplify priorities (critical hunger, low health)
- ✅ Trait-based personalities affect focus and persistence
- ✅ Smooth, believable behavior patterns
- ✅ Debug events and visualization for tuning

## Architecture

### Core Components

#### 1. `AttentionManager` (`src/models/attention.py`)

The central class that manages agent focus and stimulus evaluation.

```python
from src.models.attention import AttentionManager, StimulusType

# Create an attention manager
manager = AttentionManager()

# Evaluate stimuli and update focus
stimuli = {
    StimulusType.FORAGING: 60.0,  # Moderate hunger
    StimulusType.COMBAT: 70.0,    # Enemy nearby
}
current_focus = manager.evaluate_and_update_focus(stimuli, current_time)
```

**Key Methods:**
- `evaluate_and_update_focus()`: Determines best stimulus and updates focus
- `is_committed()`: Checks if agent is still committed to current focus
- `calculate_effective_priority()`: Computes priority with urgency modifiers
- `should_switch_focus()`: Decides if a new stimulus warrants switching
- `get_debug_info()`: Returns detailed debug information

#### 2. `StimulusType` Enum

Defines all types of stimuli that can capture agent attention:

| Stimulus Type | Base Priority | Default Commitment | Distraction Threshold |
|---------------|---------------|--------------------|-----------------------|
| `FLEEING` | 95.0 | 1.5s | 0.1 (easy to override) |
| `HAZARD_AVOIDANCE` | 85.0 | 1.0s | 0.2 |
| `COMBAT` | 70.0 | 2.5s | 0.4 (harder to distract) |
| `FORAGING` | 60.0 | 2.0s | 0.3 |
| `SOCIAL` | 40.0 | 1.5s | 0.4 |
| `EXPLORING` | 30.0 | 3.0s | 0.5 |
| `IDLE` | 0.0 | 0.0s | 0.0 (always switchable) |

#### 3. `StimulusPriority` Dataclass

Configures behavior for each stimulus type:

```python
@dataclass
class StimulusPriority:
    base_priority: float = 50.0          # Base importance (0-100+)
    min_commitment_time: float = 2.0     # Min seconds to stay focused
    distraction_threshold: float = 0.3   # How easily distracted (0-1)
```

## New Personality Traits

Six new traits affect attention behavior:

### 1. **Persistent**
- **Effect**: 1.5x commitment times (stays on task longer)
- **Rarity**: Common
- **Modifiers**: +5% defense (patience provides resilience)
- **Use Case**: Creatures that finish what they start, reliable workers

### 2. **Distractible**
- **Effect**: 1.5x easier to distract (lower thresholds)
- **Rarity**: Common
- **Modifiers**: +5% speed (quick reactions), -5% defense
- **Use Case**: Reactive, opportunistic creatures

### 3. **Tunnel Vision**
- **Effect**: 2.5x commitment times (extreme focus)
- **Rarity**: Uncommon
- **Modifiers**: +10% strength, -10% defense
- **Use Case**: Single-minded predators, specialists

### 4. **Opportunist**
- **Effect**: 0.6x commitment, 1.3x distraction sensitivity
- **Rarity**: Uncommon
- **Modifiers**: +10% speed
- **Use Case**: Adaptable survivors, scavengers

### 5. **Focused**
- **Effect**: 0.6x distraction threshold (harder to distract)
- **Rarity**: Uncommon
- **Modifiers**: +5% strength, +5% defense
- **Use Case**: Elite warriors, skilled hunters

### 6. **Fickle**
- **Effect**: 0.7x commitment times (unreliable)
- **Rarity**: Common
- **Modifiers**: +8% speed, -5% strength
- **Use Case**: Unpredictable creatures, chaotic behavior

## Integration with Battle System

The attention system is integrated into `BattleCreature` in `battle_spatial.py`:

### Initialization
```python
class BattleCreature:
    def __init__(self, creature: Creature, position: Vector2D):
        # ... other initialization ...
        
        # Create attention manager from creature's traits
        self.attention = create_attention_manager_from_traits(creature.traits)
```

### Decision Loop

The `_update_creature` method now:

1. **Evaluates all stimuli** with urgency modifiers:
   ```python
   stimuli_priorities = {}
   
   # Foraging priority based on hunger
   if creature.creature.hunger < 20:
       hunger_urgency = 3.0  # Critical
   elif creature.creature.hunger < 35:
       hunger_urgency = 2.0  # High
   else:
       hunger_urgency = 1.0  # Normal
   
   stimuli_priorities[StimulusType.FORAGING] = creature.attention.calculate_effective_priority(
       StimulusType.FORAGING,
       urgency_modifier=hunger_urgency
   )
   ```

2. **Updates focus** respecting commitments:
   ```python
   current_focus = creature.attention.evaluate_and_update_focus(
       stimuli_priorities,
       self.current_time
   )
   ```

3. **Acts based on focus** (foraging, combat, fleeing, etc.)

4. **Emits events** for debugging:
   ```python
   if current_focus != previous_focus:
       self._emit_event(BattleEvent(
           event_type=BattleEventType.ATTENTION_CHANGE,
           actor=creature,
           message=f"{creature.creature.name} switched focus: {previous_focus.value} → {current_focus.value}",
           data={'attention_debug': debug_info}
       ))
   ```

## Usage Examples

### Creating Creatures with Attention Traits

```python
from src.models.creature import Creature
from src.models.ecosystem_traits import PERSISTENT, TUNNEL_VISION, OPPORTUNIST

# Persistent creature - sticks with tasks
persistent_fighter = Creature(name="Steadfast Sam")
persistent_fighter.add_trait(PERSISTENT)

# Tunnel vision creature - extreme focus
focused_hunter = Creature(name="Laser Lucy")
focused_hunter.add_trait(TUNNEL_VISION)

# Opportunistic creature - adapts quickly
agile_survivor = Creature(name="Quick Quinn")
agile_survivor.add_trait(OPPORTUNIST)
```

### Monitoring Attention State

```python
# During battle update
battle_creature = battle.creatures[0]

# Get current focus
focus = battle_creature.attention.get_current_focus()
print(f"Current focus: {focus.value}")

# Check if committed
if battle_creature.attention.is_committed(battle.current_time):
    print("Creature is committed to current task")

# Get full debug info
debug = battle_creature.get_attention_debug_info(battle.current_time)
print(f"Focus duration: {debug['focus_duration']:.1f}s")
print(f"Persistence modifier: {debug['persistence_modifier']}")
print(f"Distractibility modifier: {debug['distractibility_modifier']}")
```

### Listening to Attention Change Events

```python
from src.systems.battle_spatial import BattleEventType

def on_attention_change(event):
    if event.event_type == BattleEventType.ATTENTION_CHANGE:
        print(f"{event.actor.creature.name}: {event.data['previous_focus']} → {event.data['new_focus']}")

battle.add_event_callback(on_attention_change)
```

## Tuning and Configuration

### Modifying Default Priorities

```python
from src.models.attention import AttentionManager, StimulusPriority, StimulusType

# Create custom attention manager
manager = AttentionManager()

# Make foraging more important
manager.priorities[StimulusType.FORAGING] = StimulusPriority(
    base_priority=80.0,      # Increased from 60.0
    min_commitment_time=3.0,  # Increased from 2.0
    distraction_threshold=0.2 # Decreased from 0.3 (harder to distract)
)
```

### Custom Trait Modifiers

```python
# Create custom trait modifiers
trait_modifiers = {
    'persistence': 2.0,      # 2x commitment times
    'distractibility': 0.5   # 0.5x distraction (harder to distract)
}

manager = AttentionManager(trait_modifiers=trait_modifiers)
```

## Priority Calculation

Effective priority = Base Priority × Urgency Modifier

### Urgency Examples

**Foraging (based on hunger):**
- Hunger > 60: urgency = 0.5 (low priority)
- Hunger 35-60: urgency = 1.3 (moderate)
- Hunger 20-35: urgency = 2.0 (high)
- Hunger < 20: urgency = 3.0 (critical)

**Fleeing (based on health):**
- HP > 30%: urgency = 1.0 (normal)
- HP 15-30%: urgency = 2.0 (high)
- HP < 15%: urgency = 3.0 (critical)

**Combat (based on threats):**
- Base: urgency = 1.0
- Has revenge target: urgency = 1.5
- Protecting injured family: urgency = 1.8

## Commitment and Switching Logic

### When Can Focus Switch?

An agent will switch focus when:

1. **Not committed** (past minimum commitment time) AND new stimulus is threshold% better, OR
2. **Still committed** BUT new stimulus is significantly better (threshold advantage required)

### Example Calculation

```python
# Agent focused on FORAGING (priority 60, threshold 0.3)
# Has been focused for 1.5s (min commitment 2.0s)

# New COMBAT stimulus appears with priority 70

# Calculate required advantage
required = 60 * 0.3 = 18

# Check if switch should happen
advantage = 70 - 60 = 10

# 10 < 18, so agent stays focused on foraging
# (not enough advantage to break commitment)
```

## Debug Visualization

### Debug Info Fields

```python
debug = creature.get_attention_debug_info(current_time)

{
    'current_focus': 'combat',           # Current stimulus type
    'focus_duration': 3.2,               # How long focused (seconds)
    'is_committed': True,                # Still in commitment period?
    'min_commitment_time': 2.5,          # Min time for this stimulus
    'distraction_threshold': 0.4,        # How hard to distract
    'persistence_modifier': 1.5,         # Trait-based modifier
    'distractibility_modifier': 1.0,     # Trait-based modifier
    'focus_context': {}                  # Extra context data
}
```

### Attention Change Events

```python
{
    'event_type': 'attention_change',
    'actor': <BattleCreature>,
    'message': 'Persistent Pete switched focus: foraging → combat',
    'data': {
        'previous_focus': 'foraging',
        'new_focus': 'combat',
        'attention_debug': {...}  # Full debug info
    }
}
```

## Testing

### Unit Tests (`tests/test_attention.py`)

Tests core attention system functionality:
- ✅ Basic attention switching
- ✅ Commitment time enforcement
- ✅ Trait modifier effects
- ✅ Priority calculation with urgency
- ✅ Debug info generation

### Integration Tests (`tests/test_attention_integration.py`)

Tests integration with battle system:
- ✅ Attention managers created for all creatures
- ✅ Trait modifiers applied correctly
- ✅ Focus changes tracked during battle
- ✅ Different traits produce different behavior patterns

### Demo Script (`examples/attention_demo.py`)

Visual demonstration showing:
- Creatures with different attention traits
- Focus changes over time
- Commitment indicators (✓ when committed)
- Attention change event tracking

Run with: `python examples/attention_demo.py`

## Performance Considerations

The attention system adds minimal overhead:

- **Per-creature**: 1 AttentionManager object (~200 bytes)
- **Per update**: 1-2 focus evaluations (microseconds)
- **Events**: Only emitted on focus change (rare)

Optimizations:
- Commitment check is O(1)
- Priority calculation is O(n) where n = number of active stimuli (typically 2-4)
- No expensive spatial queries in attention logic

## Best Practices

### 1. Choose Appropriate Traits

Match traits to intended behavior:
- **Hunters**: Tunnel Vision or Focused (stay on prey)
- **Gatherers**: Persistent (finish collecting resources)
- **Scouts**: Opportunist (react to discoveries)
- **Unpredictable NPCs**: Fickle or Distractible

### 2. Monitor Attention Changes

Too many changes = creature is indecisive:
```python
# Track changes over time
if len(attention_changes) > 20:
    print("Warning: Too many attention changes, increase commitment times")
```

### 3. Use Urgency Modifiers

Amplify priorities for critical situations:
```python
# Critical hunger should override most things
if hunger < 10:
    urgency = 5.0  # Extreme urgency
```

### 4. Debug with Events

Enable attention change events during development:
```python
battle.add_event_callback(lambda e: 
    print(e.message) if e.event_type == BattleEventType.ATTENTION_CHANGE else None
)
```

## Troubleshooting

### Creatures Never Switch Focus

**Cause**: Commitment times too long or thresholds too high

**Solution**: Reduce commitment times or distraction thresholds:
```python
manager.priorities[StimulusType.COMBAT].min_commitment_time = 1.5  # Reduce from 2.5
manager.priorities[StimulusType.COMBAT].distraction_threshold = 0.2  # Reduce from 0.4
```

### Creatures Switch Too Often

**Cause**: Commitment times too short or thresholds too low

**Solution**: Increase commitment or threshold:
```python
manager.priorities[StimulusType.FORAGING].min_commitment_time = 3.0  # Increase
manager.priorities[StimulusType.FORAGING].distraction_threshold = 0.5  # Increase
```

### Creature Ignores Critical Threats

**Cause**: Threat priority not high enough

**Solution**: Increase urgency modifier for threats:
```python
if hp_percent < 0.2:
    flee_urgency = 5.0  # Much higher urgency
```

## Future Enhancements

Potential future additions:

1. **Memory of past focus**: Remember what was being done before interrupt
2. **Goal stacking**: Return to previous goal after urgent task
3. **Social coordination**: Coordinate focus with nearby allies
4. **Learning**: Adjust priorities based on success/failure
5. **Mood system**: Emotional state affects distractibility
6. **Fatigue**: Longer focus durations reduce effectiveness

## Summary

The Attention Span and Focus System provides:

✅ **Persistent behavior**: Creatures stick with tasks instead of oscillating
✅ **Intelligent prioritization**: Critical needs override less important activities
✅ **Personality diversity**: Traits create distinct behavioral patterns
✅ **Debug visibility**: Easy to monitor and tune agent decisions
✅ **Backward compatibility**: Existing code continues to work

This system transforms agents from reactive automatons into believable entities with focus, determination, and personality-driven decision-making.
