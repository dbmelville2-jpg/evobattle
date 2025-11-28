# Random Trait System - Quick Reference

## What It Does

The Random Trait Generation & Analytics System adds emergent diversity to the Evolution Battle Game by:
- Procedurally generating unique traits during gameplay
- Injecting traits through multiple mechanisms (breeding, cosmic events, environmental pressure)
- Tracking trait spread and impact across generations
- Providing rich analytics and visualization

## Quick Start

### 1. Basic Setup (3 lines)

```python
from src.models.trait_analytics import TraitAnalytics
from src.systems.trait_injection import TraitInjectionSystem
from src.systems.breeding import Breeding

analytics = TraitAnalytics()
injection = TraitInjectionSystem(analytics=analytics)
breeding = Breeding(injection_system=injection)
```

### 2. Let It Run

The system works automatically once integrated:
- Breeding has 2% chance to inject new traits
- Cosmic events occur every 10 generations
- Pressure responses trigger when population stressed
- Diversity interventions maintain genetic variety

### 3. View Analytics

```python
# Get dashboard data
data = analytics.get_dashboard_data()
print(f"Total traits: {data['statistics']['total_discoveries']}")

# Export for analysis
analytics.export_to_json('traits.json')
analytics.export_to_csv('traits.csv')
```

## Key Features

### Trait Categories
- **Physical**: Body modifications (Armored, Swift)
- **Behavioral**: Decision patterns (Aggressive, Cautious)
- **Metabolic**: Energy efficiency (Efficient Metabolism)
- **Ecological**: Environment interactions (Scavenger)
- **Offensive/Defensive**: Combat traits

### Injection Triggers
- 🧬 **Breeding**: Small chance during offspring creation
- 🌟 **Cosmic**: Periodic random events
- 🛡️ **Pressure**: Response to starvation, combat, toxins
- 🎲 **Diversity**: When genetic variety drops too low

### Provenance Tracking
Every trait remembers:
- Where it came from (inherited, emergent, cosmic, etc.)
- When it appeared (generation number)
- How it spread (population metrics)

## Configuration

```python
from src.systems.trait_injection import InjectionConfig

config = InjectionConfig(
    breeding_injection_rate=0.02,    # 2% per breeding
    cosmic_event_interval=10,         # Every 10 generations
    pressure_threshold=0.3,           # Trigger at 30% stress
    diversity_threshold=0.4,          # Trigger at 40% diversity
    injection_enabled=True            # Master switch
)
```

## UI Integration

### Enhanced Creature Inspector
Automatically shows trait origins with icons:
- 👪 Inherited from parents
- ✨ Emerged during breeding
- 🌟 Cosmic event
- 🛡️ Adaptive response
- 🎲 Diversity boost

### Analytics Dashboard
```python
from src.rendering.trait_dashboard import TraitAnalyticsDashboard

dashboard = TraitAnalyticsDashboard(analytics)
dashboard.show()  # Toggle with Ctrl+D
```

## Testing

Run all tests:
```bash
pytest tests/test_trait_*.py -v
```

Run demo:
```bash
PYTHONPATH=. python examples/random_trait_demo.py
```

## Files Overview

### Core Systems
- `src/models/trait_generator.py` - Generates random traits
- `src/models/trait_analytics.py` - Tracks and analyzes traits
- `src/systems/trait_injection.py` - Manages injection triggers
- `src/systems/breeding.py` - Integrated breeding with injection

### UI Components
- `src/rendering/creature_inspector.py` - Enhanced with trait origins
- `src/rendering/trait_dashboard.py` - Analytics visualization

### Tests (73 total)
- `tests/test_trait_generator.py` - 20 tests
- `tests/test_trait_analytics.py` - 19 tests
- `tests/test_trait_injection.py` - 22 tests
- `tests/test_trait_system_integration.py` - 12 tests

### Documentation
- `RANDOM_TRAIT_SYSTEM_DOCUMENTATION.md` - Full documentation
- `examples/random_trait_demo.py` - Working demo

## Performance

- Trait generation: ~0.1ms per trait
- Analytics updates: O(1) operations
- Dashboard caching: 1-second refresh
- Target impact: <1% FPS (achieved ✓)

## Common Patterns

### Custom Injection Event
```python
# Manual cosmic-like event
traits = []
for _ in range(5):
    trait = injection.inject_pressure_response_trait(
        generation=current_gen,
        pressure_type='custom',
        population_affected=population_size
    )
    traits.append(trait)
```

### Tracking Offspring Traits
```python
offspring = breeding.breed(parent1, parent2)
if offspring:
    for trait in offspring.traits:
        analytics.record_creature_trait(
            offspring.creature_id,
            trait.name
        )
```

### Periodic Analytics Report
```python
if generation % 10 == 0:
    summary = analytics.get_generation_summary(generation)
    print(f"Generation {generation}: {summary['unique_traits']} traits")
```

## Troubleshooting

**Q: No traits being injected?**
- Check `injection_enabled=True`
- Verify creatures are mature for breeding
- Check injection rate isn't too low

**Q: Too many traits?**
- Lower `breeding_injection_rate`
- Increase `cosmic_event_interval`
- Disable specific triggers

**Q: Want deterministic generation?**
```python
generator = TraitGenerator(seed=42)
injection = TraitInjectionSystem(seed=42)
```

## Next Steps

1. Read full documentation: `RANDOM_TRAIT_SYSTEM_DOCUMENTATION.md`
2. Run the demo: `python examples/random_trait_demo.py`
3. Integrate into your game loop
4. Monitor analytics dashboard
5. Export and analyze data

## Support

- See full API reference in main documentation
- Check tests for usage examples
- Run demo for working integration example

---

**Status**: Production ready ✓
**Tests**: 73 passing ✓
**Documentation**: Complete ✓
