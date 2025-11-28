# Lethal Combat Traits Documentation

## Overview

This document describes the 10 new high-lethality combat traits added to the Evolution Battle Game. These traits introduce high-risk, high-reward gameplay mechanics that enable dramatic kills, apex predators, and sudden battle reversals.

## Design Philosophy

The lethal combat traits follow these principles:
- **High Risk, High Reward**: Most traits offer significant offensive bonuses but come with defensive penalties or other risks
- **Emergent Narratives**: Enable memorable moments (kill streaks, comebacks, dramatic finishes)
- **Build Diversity**: Support specialized builds (glass cannons, vampires, executioners, berserkers)
- **Dynamic Combat**: Faster, more lethal battles with dramatic swings

## Trait Catalog

### 1. Berserker
```python
BERSERKER_TRAIT = Trait(
    name="Berserker",
    description="Rages when wounded, trading defense for pure carnage"
)
```

**Stats:**
- Strength: 1.0× (normal)
- Speed: 1.0× (normal)
- Defense: 0.7× (vulnerable)
- Rarity: Rare
- Dominance: Dominant

**Effects:**
- `attack_bonus_below_30_hp`: +100% attack when below 30% HP
- `cannot_retreat`: Cannot flee from battle
- `rage_threshold`: 0.3 (triggers at 30% HP)

**Strategy:** 
- High-risk melee fighter that becomes incredibly dangerous when wounded
- Pairs well with regeneration or lifesteal to survive long enough to enrage
- Vulnerable to burst damage and execution abilities

---

### 2. Executioner
```python
EXECUTIONER_TRAIT = Trait(
    name="Executioner",
    description="Finishes the weak with ruthless efficiency"
)
```

**Stats:**
- Strength: 1.1× (boosted)
- Speed: 1.0× (normal)
- Defense: 1.0× (normal)
- Rarity: Rare
- Dominance: Dominant

**Effects:**
- `execute_bonus`: +150% damage to targets below 40% HP
- `execute_threshold`: 0.4 (bonus applies below 40% HP)
- `immune_to_fear`: Cannot be frightened or intimidated

**Strategy:**
- Excellent finisher that ensures wounded enemies don't escape
- Synergizes with allies who soften up targets
- Effective against regenerating or healing enemies

---

### 3. Bloodthirsty
```python
BLOODTHIRSTY_TRAIT = Trait(
    name="Bloodthirsty",
    description="Damage increases with each kill in battle"
)
```

**Stats:**
- Strength: 1.05× (slightly boosted)
- Speed: 1.05× (slightly boosted)
- Defense: 0.95× (slightly reduced)
- Rarity: Rare
- Dominance: Dominant

**Effects:**
- `damage_per_kill`: +15% damage per kill (stacks)
- `max_kill_stacks`: 5 stacks maximum (+75% total)
- `resets_on_battle_end`: Stacks reset after battle
- `targets_injured`: Tends to focus on wounded targets

**Strategy:**
- Snowball champion that grows stronger as battle progresses
- Devastating in prolonged battles with multiple enemies
- Weak at the start, needs to secure first kill to ramp up

---

### 4. Brutal
```python
BRUTAL_TRAIT = Trait(
    name="Brutal",
    description="Ignores armor and causes bleeding wounds"
)
```

**Stats:**
- Strength: 1.5× (very high)
- Speed: 0.95× (slightly reduced)
- Defense: 0.95× (slightly reduced)
- Rarity: Rare
- Dominance: Dominant

**Effects:**
- `armor_penetration`: Ignores 50% of target's armor/defense
- `bleed_on_hit`: All successful hits cause bleeding
- `bleed_damage`: 3 damage per tick

**Strategy:**
- Hard counter to heavily armored opponents
- Damage over time creates pressure even if target escapes
- Very effective against defensive builds

---

### 5. Assassin
```python
ASSASSIN_TRAIT = Trait(
    name="Assassin",
    description="Deadly from the shadows, vulnerable when exposed"
)
```

**Stats:**
- Strength: 1.1× (boosted)
- Speed: 1.2× (high)
- Defense: 0.7× (vulnerable)
- Rarity: Rare
- Dominance: Recessive

**Effects:**
- `ambush_damage`: +200% damage on first strike/ambush
- `counter_vulnerability`: Receives double damage if counter-attacked
- `stealth_movement`: Moves stealthily near enemies
- `first_strike`: Usually attacks first

**Strategy:**
- Glass cannon that excels at eliminating targets quickly
- Extremely vulnerable if first strike fails or gets countered
- Best used with hit-and-run tactics

---

### 6. Apex Predator
```python
APEX_PREDATOR_TRAIT = Trait(
    name="Apex Predator",
    description="Grows stronger with each unique kill, inspiring fear"
)
```

**Stats:**
- Strength: 1.1× (boosted)
- Speed: 1.1× (boosted)
- Defense: 1.05× (slightly boosted)
- Rarity: Legendary
- Dominance: Dominant

**Effects:**
- `stats_per_unique_kill`: +20% all stats per unique strain killed
- `fear_aura`: Nearby enemies occasionally flee
- `fear_radius`: 50.0 units
- `prey_tracking`: Enhanced ability to track and hunt

**Strategy:**
- Ultimate predator that becomes unstoppable over time
- Rewards hunting diverse prey (killing different strains)
- Creates emergent "boss creature" narratives

---

### 7. Reckless Fury
```python
RECKLESS_FURY_TRAIT = Trait(
    name="Reckless Fury",
    description="Overwhelming offense at the cost of safety"
)
```

**Stats:**
- Strength: 1.6× (extremely high)
- Speed: 1.1× (boosted)
- Defense: 0.5× (very vulnerable)
- Rarity: Rare
- Dominance: Dominant

**Effects:**
- `self_damage_chance`: 20% chance to damage self on each attack
- `self_damage_amount`: 5 damage
- `cannot_block`: Cannot use blocking abilities
- `cannot_parry`: Cannot parry attacks

**Strategy:**
- Extreme glass cannon, highest raw damage output
- High risk of self-destruction
- Best in short, decisive battles

---

### 8. Toxic
```python
TOXIC_TRAIT = Trait(
    name="Toxic",
    description="All attacks inflict stacking poison"
)
```

**Stats:**
- Strength: 1.1× (boosted)
- Speed: 1.0× (normal)
- Defense: 0.9× (slightly reduced)
- Rarity: Rare
- Dominance: Dominant

**Effects:**
- `poison_on_hit`: 100% chance to poison on hit
- `poison_damage`: 2 damage per tick
- `poison_stacks`: Maximum 5 stacks (10 damage/tick)
- `healing_reduction`: -30% healing received

**Strategy:**
- Excels in prolonged battles where poison stacks up
- Soft counter to healing/regeneration
- Creates battlefield pressure over time

---

### 9. Frenzied
```python
FRENZIED_TRAIT = Trait(
    name="Frenzied",
    description="Attacks in rapid succession, forsaking defense"
)
```

**Stats:**
- Strength: 1.1× (boosted)
- Speed: 2.5× (extremely fast)
- Defense: 0.8× (reduced)
- Rarity: Rare
- Dominance: Dominant

**Effects:**
- `multi_strike`: Can attack up to 3 times per turn
- `attack_speed_multiplier`: 2.5× attack speed
- `cannot_use_defensive_abilities`: No defensive actions allowed

**Strategy:**
- Burst damage specialist, overwhelms with attack volume
- Vulnerable during opponent's turn
- Best for quick eliminations before taking damage

---

### 10. Vampiric
```python
VAMPIRIC_TRAIT = Trait(
    name="Vampiric",
    description="Drains life from enemies, converting damage to health"
)
```

**Stats:**
- Strength: 1.1× (boosted)
- Speed: 0.95× (slightly reduced)
- Defense: 0.95× (slightly reduced)
- Rarity: Rare
- Dominance: Recessive

**Effects:**
- `lifesteal`: Heals for 50% of all damage dealt
- `overheal_shield`: Can overheal beyond max HP
- `overheal_max`: Shield up to 30% of max HP

**Strategy:**
- Sustain fighter that gets stronger the longer battle lasts
- Countered by anti-heal and burst damage
- Excellent in prolonged battles and 1v1 scenarios

---

## Implementation Details

### File Locations
- **Trait Definitions**: `src/models/expanded_traits.py` (lines 236-390)
- **Trait Collections**: `src/models/expanded_traits.py` (LETHAL_COMBAT_TRAITS list)
- **Generator Support**: `src/models/trait_generator.py` (offensive category effects)
- **Tests**: `tests/test_lethal_combat_traits.py`

### Trait Categories
All lethal traits are categorized as:
- `trait_type="offensive"`

### Integration with Trait System
The lethal combat traits are automatically included in:
- `ALL_CREATURE_TRAITS` - Complete trait pool
- `LETHAL_COMBAT_TRAITS` - Specific lethal trait collection
- Trait generator's offensive category pool

## Usage Examples

### Accessing Lethal Traits
```python
from src.models.expanded_traits import LETHAL_COMBAT_TRAITS, BERSERKER_TRAIT

# Get all lethal traits
print(f"Total lethal traits: {len(LETHAL_COMBAT_TRAITS)}")

# Access specific trait
berserker = BERSERKER_TRAIT
print(f"{berserker.name}: {berserker.description}")
```

### Generating Random Lethal Traits
```python
from src.models.trait_generator import TraitGenerator

generator = TraitGenerator()

# Generate offensive trait with lethal effects
trait = generator.generate_trait(category='offensive', rarity='rare')
print(f"Generated: {trait.name}")
print(f"Effects: {trait.interaction_effects}")
```

### Assigning to Creatures
```python
from src.models.creature import Creature
from src.models.expanded_traits import APEX_PREDATOR_TRAIT

creature = Creature(name="Alpha Hunter")
creature.traits.append(APEX_PREDATOR_TRAIT)

# The trait's effects would be applied during combat
```

## Balance Considerations

### Glass Cannon Traits
These traits have significantly reduced defense (≤0.7×):
- **Berserker**: 0.7× defense
- **Assassin**: 0.7× defense
- **Reckless Fury**: 0.5× defense

### Moderate Risk Traits
These traits have slightly reduced defense (0.8-0.95×):
- **Bloodthirsty**: 0.95× defense
- **Brutal**: 0.95× defense
- **Toxic**: 0.9× defense
- **Frenzied**: 0.8× defense
- **Vampiric**: 0.95× defense

### High Power Traits
These traits have exceptional strength modifiers:
- **Reckless Fury**: 1.6× strength (highest)
- **Brutal**: 1.5× strength

### Legendary Tier
Only one trait is legendary rarity:
- **Apex Predator**: Most powerful long-term scaling

## Gameplay Impact

### Creates Distinct Archetypes
- **Berserker**: Comeback mechanic, dramatic low-HP reversal
- **Executioner**: Finisher, ensures no escapes
- **Bloodthirsty**: Snowball carry, grows with kills
- **Brutal**: Tank buster, counters armor
- **Assassin**: One-shot specialist, high skill cap
- **Apex Predator**: Boss creature, endgame threat
- **Reckless Fury**: All-in aggressor, win or die
- **Toxic**: Attrition fighter, pressure over time
- **Frenzied**: Burst assassin, overwhelming offense
- **Vampiric**: Sustain fighter, outlasts opponents

### Enables Strategic Counterplay
- Anti-heal counters: Toxic, Vampiric
- Burst damage counters: Berserker, regenerators
- Armor counters: Brutal
- Glass cannon counters: Any defensive build vs Assassin, Reckless Fury
- Sustain counters: Executioner, burst damage

### Promotes Build Diversity
Players can now create:
- Pure offense builds (Reckless Fury + Frenzied)
- Sustain builds (Vampiric + Regenerative)
- Finisher builds (Executioner + Bloodthirsty)
- Predator builds (Apex Predator + Predator trait)

## Testing

Run the lethal trait test suite:
```bash
python -m unittest tests.test_lethal_combat_traits -v
```

Test coverage includes:
- All 10 traits properly defined
- Correct stat modifiers and rarities
- Interaction effects present and valid
- Serialization/deserialization
- Integration with trait system
- Balance validation (glass cannon, power levels)

## Future Enhancements

Potential additions to the lethal combat system:
1. **Counter Traits**: Defensive traits that specifically counter lethal builds
   - Fortified (high armor, slow)
   - Hexproof (immune to poison/bleed)
   - Regenerator (counter to DOT effects)
   
2. **Combo Traits**: Traits that synergize with specific lethal traits
   - Blood Pact (boost Vampiric lifesteal)
   - Adrenaline (boost Berserker rage bonus)
   
3. **Combat Effect Handlers**: Implement the actual combat mechanics for:
   - Bleed damage over time
   - Poison stacking
   - Execute threshold checking
   - Multi-strike attack sequences
   - Lifesteal healing
   - Overheal shields

4. **UI Indicators**: Visual feedback for:
   - Rage state (Berserker)
   - Kill streak count (Bloodthirsty)
   - Poison/bleed stacks
   - Fear aura radius (Apex Predator)

## Contributing

When adding new lethal traits:
1. Follow the existing trait structure
2. Add to `LETHAL_COMBAT_TRAITS` collection
3. Include comprehensive `interaction_effects`
4. Add tests to `test_lethal_combat_traits.py`
5. Update this documentation
6. Balance against existing traits

## References

- **Main Trait System**: `TRAIT_SYSTEM_QUICK_REFERENCE.md`
- **Random Generation**: `RANDOM_TRAIT_SYSTEM_DOCUMENTATION.md`
- **Combat System**: `COMBAT_SYSTEM_DOCUMENTATION.md`
- **Issue**: GitHub issue #[issue_number] - Add More Lethal and Deadly Combat Traits

---

**Status**: Implemented ✓  
**Tests**: 20 passing ✓  
**Integration**: Complete ✓  
**Documentation**: Complete ✓
