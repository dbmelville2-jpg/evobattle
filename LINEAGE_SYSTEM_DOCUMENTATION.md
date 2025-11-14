# Genetic Lineage System Documentation

## Overview

The Genetic Lineage System transforms EvoBattle from a team-based battle game into an evolutionary ecosystem simulator. Creatures form dynamic families/strains based on shared ancestry and hereditary traits, with color serving as a visual indicator of genetic similarity.

## Core Concepts

### Strains (Genetic Families)

A **strain** is a genetic family of creatures that share common ancestry. Instead of being assigned to fixed teams, creatures belong to strains that:

- Form naturally through breeding
- Have visual identity through color (hue)
- Can grow, dominate, or go extinct
- Pass down traits across generations
- Mutate and branch into new strains

### Color as Genetic Marker

Each creature has a **hue** value (0-360°) that represents its genetic lineage:

- **Red** (0-30°): Aggressive hunter strains
- **Yellow** (30-90°): Balanced generalist strains
- **Green** (90-150°): Efficient forager strains
- **Cyan** (150-210°): Mixed hybrid strains
- **Blue** (210-270°): Explorer/curious strains
- **Purple** (270-330°): Rare mutant strains

Similar colors indicate genetic relatedness. When a strain goes extinct, its color disappears from the arena.

### Trait Inheritance and Mutation

Creatures inherit traits from their parents with these mechanics:

1. **Inheritance** (70-90% chance per trait): Most traits pass to offspring
2. **Modification** (10% chance): Trait modifiers change slightly
3. **Addition** (3% chance): New trait appears through mutation
4. **Removal** (5% chance): Trait is lost through mutation
5. **Strain Mutation** (3% chance with different-strain parents): New strain emerges

## Data Models

### Creature.strain_id

Every creature has a `strain_id` attribute (UUID string) that identifies its genetic family:

```python
creature = Creature(
    name="Hunter",
    hue=15.0,  # Reddish color
    strain_id="strain_red_alpha"  # Optional, auto-generated if None
)
```

When `strain_id` is None, a new UUID is generated, creating a founder of a new strain.

### Lineage Model

The `Lineage` model tracks ancestry and strain membership:

```python
lineage = Lineage(
    creature_id="creature_123",
    strain_id="strain_red_alpha",
    generation=2,
    parent1_id="parent_1",
    parent2_id="parent_2",
    inherited_traits=["Aggressive", "Fast"],
    birth_timestamp=1234567890.0
)
```

**Attributes:**
- `creature_id`: Unique creature identifier
- `strain_id`: Genetic strain/family identifier
- `generation`: Generation number (0 = founder)
- `parent1_id`, `parent2_id`: Parent creature IDs
- `inherited_traits`: List of trait names inherited
- `birth_timestamp`: When creature was born

## Breeding System

### Strain Inheritance Rules

When two creatures breed:

1. **Same Strain Parents** (both have `strain_A`):
   - 97% chance: offspring inherits `strain_A`
   - 3% chance: major mutation creates new strain

2. **Different Strain Parents** (`strain_A` + `strain_B`):
   - 50% chance: inherit `strain_A`
   - 50% chance: inherit `strain_B`

### Color/Hue Inheritance

Hue follows this formula:
```python
child_hue = (parent1.hue + parent2.hue) / 2.0
child_hue += random.uniform(-15, 15)  # Mutation range
child_hue = child_hue % 360  # Wrap around
```

This creates gradual color shifts while maintaining family similarity.

### Trait Mutations

The breeding system supports three types of mutations:

#### 1. Trait Modification
Existing traits have 10% of their modifiers changed:
```python
# Original trait
trait = Trait(name="Strong", strength_modifier=1.2)

# After mutation
mutated = Trait(name="Strong+", strength_modifier=1.32)  # +10%
```

#### 2. Trait Addition (3% chance)
A completely new trait is added from the ecosystem trait pool:
```python
# Parents have: ["Aggressive"]
# Offspring gains: ["Aggressive", "Curious"]  # New trait!
```

#### 3. Trait Removal (5% chance)
A parent trait fails to pass to offspring:
```python
# Parents have: ["Aggressive", "Fast"]
# Offspring has: ["Aggressive"]  # Lost "Fast"
```

### Example Breeding Code

```python
from src.systems.breeding import Breeding
from src.models.creature import Creature

breeding = Breeding(mutation_rate=0.1)

parent1 = Creature(name="RedAlpha", hue=0.0, strain_id="strain_red", mature=True)
parent2 = Creature(name="RedBeta", hue=10.0, strain_id="strain_red", mature=True)

offspring = breeding.breed(parent1, parent2)

print(f"Child strain: {offspring.strain_id}")
print(f"Child hue: {offspring.hue}°")
print(f"Traits: {[t.name for t in offspring.traits]}")
```

## Population Management

### PopulationManager Strain Methods

The `PopulationManager` provides comprehensive strain tracking:

#### get_strain_statistics()
Returns detailed stats for each strain:

```python
stats = population.get_strain_statistics()
# Returns: {
#     'strain_red': {
#         'alive': 5,
#         'total': 8,
#         'mature': 3,
#         'extinct': False,
#         'avg_hue': 12.5
#     },
#     'strain_green': {
#         'alive': 0,
#         'total': 3,
#         'mature': 0,
#         'extinct': True,
#         'avg_hue': 125.0
#     }
# }
```

#### get_dominant_strains(top_n=5)
Returns most populous strains:

```python
dominant = population.get_dominant_strains(top_n=3)
# Returns: [
#     ('strain_red', 5),    # 5 alive
#     ('strain_blue', 3),   # 3 alive
#     ('strain_green', 0)   # extinct
# ]
```

#### get_extinct_strains()
Lists strains with no living members:

```python
extinct = population.get_extinct_strains()
# Returns: ['strain_green', 'strain_purple']
```

### Example Population Tracking

```python
from src.systems.population import PopulationManager

pop = PopulationManager()

# Add creatures
for creature in initial_creatures:
    pop.spawn_creature(creature)

# Simulate deaths
for creature in weak_creatures:
    if not creature.is_alive():
        pop.remove_creature(creature, cause="starvation")

# Get statistics
stats = pop.get_strain_statistics()
for strain_id, info in stats.items():
    print(f"Strain {strain_id[:8]}: {info['alive']}/{info['total']} alive")
    if info['extinct']:
        print(f"  ⚠️ EXTINCT")
```

## Rendering and UI

### Strain-Based UI Components

The UI has been updated to show strain information instead of team affiliations:

#### Left Panel: Strain Statistics
Shows genetic families sorted by population:
- Color indicator (circle) showing strain hue
- Strain ID (abbreviated)
- Population count (alive/total)

#### Right Panel: Individual Creatures
Shows living creatures with:
- Color indicator showing individual hue
- Creature name
- HP bar
- Sorted by remaining creatures

### Color Visualization

Creatures are rendered using their hue-based color:

```python
# In creature_renderer.py
color = creature.creature.get_display_color()  # Returns RGB from HSV
pygame.draw.circle(screen, color, position, radius)
```

The `get_display_color()` method converts HSV to RGB:
- **Hue**: Genetic lineage (0-360°)
- **Saturation**: HP ratio (30-100%, low HP = desaturated)
- **Value**: Hunger level (30-100%, starving = dark)

This creates visual feedback where:
- Healthy creatures are vibrant
- Wounded creatures are pale/desaturated
- Starving creatures are dark

## Usage Examples

### Creating a Strain-Based Ecosystem

```python
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.trait import Trait
from src.systems.breeding import Breeding
from src.systems.population import PopulationManager

# Initialize systems
breeding = Breeding(mutation_rate=0.15)
population = PopulationManager()

# Create founder strains
red_strain = Creature(
    name="RedFounder",
    hue=0.0,
    strain_id="strain_red",
    traits=[Trait(name="Aggressive")]
)

green_strain = Creature(
    name="GreenFounder", 
    hue=120.0,
    strain_id="strain_green",
    traits=[Trait(name="Efficient")]
)

# Add to population
population.spawn_creature(red_strain)
population.spawn_creature(green_strain)

# Simulate breeding
for generation in range(5):
    breedable = population.get_mature_creatures()
    
    for i in range(len(breedable) - 1):
        offspring = breeding.breed(breedable[i], breedable[i+1])
        if offspring:
            population.spawn_creature(offspring)

# Analyze results
strain_stats = population.get_strain_statistics()
dominant = population.get_dominant_strains()

print(f"Total strains: {len(strain_stats)}")
print(f"Dominant strain: {dominant[0][0]}")
```

### Tracking Strain Evolution

```python
# Monitor strain changes over time
history = []

for timestep in range(100):
    # Update creatures, handle deaths, breed, etc.
    
    # Record current state
    stats = population.get_strain_statistics()
    history.append({
        'time': timestep,
        'strain_count': len(stats),
        'total_alive': sum(s['alive'] for s in stats.values()),
        'dominant': population.get_dominant_strains(1)[0]
    })

# Analyze evolution
print("Strain Evolution Timeline:")
for record in history[::10]:  # Every 10 timesteps
    print(f"T={record['time']:3d}: {record['strain_count']} strains, "
          f"{record['total_alive']} alive, "
          f"dominant={record['dominant'][0][:8]}")
```

## Integration with Existing Systems

### Battle System
The spatial battle system already uses creature colors:
```python
# In battle_spatial.py
creature_color = battle_creature.creature.get_display_color()
# Automatically uses hue-based color
```

### Foraging System
Creatures with different strains compete for resources:
```python
# Foragers from efficient strains have advantage
if creature.has_trait("Efficient Metabolism"):
    hunger_depletion *= 0.6  # Survive longer
```

### Evolution System
Can track which strains evolve to higher forms:
```python
if evolution_system.can_evolve(creature):
    evolved = evolution_system.evolve_creature(creature)
    # Evolved creature keeps strain_id but gains new traits
```

## Natural Selection Scenarios

### Scenario 1: Efficient Foragers Dominate
- **Initial**: Mixed strains with various metabolic traits
- **Environment**: Limited food resources
- **Outcome**: Strains with "Efficient Metabolism" survive, others starve
- **Visual**: Green hues (efficient) replace red hues (aggressive)

### Scenario 2: Aggressive Hunters Win Battles
- **Initial**: Foragers vs. hunters
- **Environment**: Combat-heavy with abundant food
- **Outcome**: Aggressive strains eliminate peaceful ones
- **Visual**: Red hues dominate, green hues disappear

### Scenario 3: Hybrid Strain Emerges
- **Initial**: Two distinct strains
- **Process**: Cross-breeding creates hybrid with best of both
- **Outcome**: New strain (different color) outcompetes parents
- **Visual**: Cyan hybrid color replaces parent red and green

## Best Practices

### 1. Mutation Rate Tuning
```python
# For stable populations
breeding = Breeding(mutation_rate=0.05)  # Low mutation

# For rapid evolution
breeding = Breeding(mutation_rate=0.20)  # High mutation

# For realistic simulation
breeding = Breeding(mutation_rate=0.10)  # Balanced
```

### 2. Strain Tracking
Always track strain statistics for analysis:
```python
# Record every N timesteps
if timestep % 10 == 0:
    analytics.record_tick(population)
    strain_stats = population.get_strain_statistics()
    save_snapshot(strain_stats)
```

### 3. Preventing Extinction
Maintain minimum population per strain:
```python
strain_stats = population.get_strain_statistics()
for strain_id, stats in strain_stats.items():
    if stats['alive'] < 2 and not stats['extinct']:
        # Spawn rescue creature
        founder = find_founder_by_strain(strain_id)
        new_creature = create_similar_creature(founder)
        population.spawn_creature(new_creature)
```

### 4. Visualizing Evolution
Use hue as primary visual indicator:
```python
# Sort creatures by hue for color-based grouping
sorted_creatures = sorted(
    population.get_alive_creatures(),
    key=lambda c: c.hue
)

# Display color spectrum
for creature in sorted_creatures:
    color = creature.get_display_color()
    display_with_color(creature.name, color)
```

## Testing

The strain system includes comprehensive tests in `tests/test_strain.py`:

- **Strain Inheritance Tests**: Verify parent-to-child strain passing
- **Mutation Tests**: Confirm trait addition/removal/modification
- **Statistics Tests**: Validate population tracking
- **Extinction Tests**: Ensure proper detection of extinct strains
- **Serialization Tests**: Check saving/loading of strain data

Run tests:
```bash
python3 -m unittest tests.test_strain -v
```

## Performance Considerations

### Memory Usage
- Each creature stores one `strain_id` (UUID string)
- Lineage records are lightweight (< 1 KB per creature)
- Strain statistics are computed on-demand

### Optimization Tips
1. **Cache strain statistics**: Don't recompute every frame
   ```python
   self.cached_stats = None
   self.cache_time = 0
   
   def get_stats(self, current_time):
       if current_time - self.cache_time > 1.0:  # 1 second cache
           self.cached_stats = population.get_strain_statistics()
           self.cache_time = current_time
       return self.cached_stats
   ```

2. **Limit UI updates**: Only update strain panel when needed
3. **Batch breeding**: Process multiple breeding events together
4. **Prune history**: Remove old lineage records for dead creatures

## Future Enhancements

Potential additions to the strain system:

1. **Strain Names**: Auto-generate meaningful names based on traits
2. **Family Trees**: Visual lineage tree display
3. **Trait Combinations**: Special effects for specific trait combos
4. **Migration**: Strains moving between different arenas
5. **Symbiosis**: Cooperative relationships between strains
6. **Predator-Prey**: Specific strain interactions
7. **Genetic Distance**: Measure relatedness between strains
8. **Breeding Restrictions**: Prevent breeding between distant strains

## Troubleshooting

### Issue: All creatures same color
**Cause**: All creatures have same strain_id
**Solution**: Create diverse founders with different strain_ids and hues

### Issue: No mutations occurring
**Cause**: Mutation rate too low or not enough generations
**Solution**: Increase `mutation_rate` in Breeding system

### Issue: Strains going extinct too quickly
**Cause**: Population too small or selection pressure too high
**Solution**: Increase initial population or adjust environmental factors

### Issue: UI not showing strain colors
**Cause**: Using old team-based rendering
**Solution**: Use `_render_strain_panel()` in UI components

## Conclusion

The Genetic Lineage System transforms EvoBattle into a dynamic evolutionary simulator where:

- Natural selection drives population changes
- Color visually represents genetic relationships
- Strains compete, mutate, and evolve
- Players observe emergence and extinction of genetic families

This creates emergent gameplay where successful strategies naturally spread through the population while unsuccessful ones die out, all visualized through the color spectrum of the arena.
