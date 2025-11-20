# Code Organization Guide

Welcome to the EvoBattle codebase! This guide will help you understand how the project is structured and where to find specific features.

## Directory Structure

```
evobattle/
├── src/                    # Main source code
│   ├── models/            # Data models and game entities
│   ├── systems/           # Game systems and mechanics
│   ├── rendering/         # Pygame rendering components
│   └── utils/             # Utility functions and helpers
├── tests/                 # Unit and integration tests
│   ├── grass_growth/     # Grass growth system tests
│   ├── spatial/          # Spatial system tests
│   └── ...               # Other test modules
├── examples/              # Example scripts and demos
├── docs/                  # Documentation
├── assets/                # Game assets (images, sounds, etc.)
└── main.py               # Main entry point
```

## Core Modules

### Models (`src/models/`)

**Purpose**: Define the core data structures and entities in the game.

Key files:
- **`creature.py`**: The `Creature` class - represents individual organisms with stats, traits, and abilities
- **`genetics.py`**: `GeneticsEngine` - handles Mendelian genetics with dominant/recessive genes
- **`trait.py`**: `Trait` class - defines creature traits and their effects
- **`pellet.py`**: `Pellet` class - food resources that evolve and reproduce
- **`spatial.py`**: `Vector2D`, `SpatialComponent`, `Arena` - 2D physics and positioning
- **`environment.py`**: `Environment` class - weather, terrain, and environmental hazards
- **`stats.py`**: `Stats` class - creature statistics (HP, attack, defense, speed)
- **`ability.py`**: `Ability` class - special moves creatures can use in combat

**Trait-related files**:
- `ecosystem_traits.py` - Basic ecosystem traits (Forager, Aggressive, etc.)
- `expanded_traits.py` - Advanced combat and social traits
- `environmental_traits.py` - Weather and terrain-responsive traits
- `weather_terrain_traits.py` - Specific environmental adaptation traits
- `trait_generator.py` - Procedural trait generation system
- `trait_analytics.py` - Trait usage tracking and analytics

### Systems (`src/systems/`)

**Purpose**: Implement game mechanics and simulation logic.

Key files:
- **`battle_spatial.py`**: `SpatialBattle` - main real-time battle system with 2D movement
- **`battle_turnbased_backup.py`**: `Battle` - legacy turn-based battle system (still used by some tests)
- **`breeding.py`**: `Breeding` - creature reproduction with genetic inheritance
- **`living_world.py`**: `LivingWorldBattleEnhancer` - adds hunger, reproduction, and ecosystem dynamics
- **`grass_growth_system.py`**: `GrassGrowthSystem` - pellet growth with nutrient zones and pollination
- **`trait_injection.py`**: `TraitInjectionSystem` - procedural trait introduction based on environmental pressure
- **`trait_effects_handler.py`**: `TraitEffectsHandler` - applies trait bonuses in combat
- **`terrain_affinity_tracker.py`**: `TerrainAffinityTracker` - tracks creature terrain preferences
- **`battle_story_summarizer.py`**: `BattleStoryGenerator` - AI-generated battle narratives

### Rendering (`src/rendering/`)

**Purpose**: Pygame-based visualization components.

Key files:
- **`game_window.py`**: `GameWindow` - main game window management
- **`arena_renderer.py`**: `ArenaRenderer` - renders the battle arena with terrain and biomes
- **`creature_renderer.py`**: `CreatureRenderer` - draws creatures with health bars and visual effects
- **`pellet_renderer.py`**: `PelletRenderer` - renders pellets with generation markers
- **`ui_components.py`**: `UIComponents` - HUD, stats panels, battle feed
- **`event_animator.py`**: `EventAnimator` - battle event animations
- **`creature_inspector.py`**: `CreatureInspector` - detailed creature info panel
- **`pause_menu.py`**: `PauseMenu` - in-game pause menu
- **`post_game_summary.py`**: `PostGameSummary` - end-of-battle statistics
- **`story_viewer.py`**: `StoryViewer` - AI-generated story display

### Utilities (`src/utils/`)

**Purpose**: Helper functions and utilities.

Key files:
- **`name_generator.py`**: `NameGenerator` - generates creature names
- **`preferences.py`**: `PreferencesManager` - user preferences and settings

## Key Concepts

### Creature Lifecycle

1. **Creation**: Creatures are created with a `CreatureType`, base stats, and initial traits
2. **Combat**: Creatures fight using abilities, with damage calculated from stats and traits
3. **Feeding**: Creatures consume pellets to satisfy hunger
4. **Reproduction**: Mature creatures with sufficient hunger can breed
5. **Evolution**: Offspring inherit traits through Mendelian genetics with mutations

### Trait System

Traits modify creature behavior and stats:
- **Stat modifiers**: Direct bonuses to HP, attack, defense, speed
- **Interaction effects**: Special behaviors (e.g., Pack Hunter gets bonuses near allies)
- **Environmental responses**: Traits that activate in specific weather/terrain
- **Inheritance**: Traits have dominant/recessive genes that pass to offspring

### Spatial Battle System

The main game loop (`battle_spatial.py`):
1. **Physics update**: Creatures move based on velocity and acceleration
2. **AI decision**: Creatures choose targets and actions
3. **Combat resolution**: Damage is calculated and applied
4. **Feeding**: Creatures eat nearby pellets
5. **Reproduction**: Breeding occurs when conditions are met
6. **Environment**: Weather changes, hazards spawn, pellets grow

### Pellet Ecosystem

Pellets are living resources that:
- **Reproduce**: Create offspring pellets over time
- **Evolve**: Mutations change nutritional value, toxicity, palatability
- **Respond to environment**: Growth rates affected by nutrient zones, weather, nearby creatures
- **Pollinate**: Creatures spread pellet seeds as they move

## Finding Specific Features

### "I want to modify creature stats"
→ `src/models/stats.py` and `src/models/creature.py`

### "I want to add a new trait"
→ `src/models/ecosystem_traits.py` or `src/models/expanded_traits.py`

### "I want to change combat mechanics"
→ `src/systems/battle_spatial.py` (search for `_calculate_damage`)

### "I want to modify the breeding system"
→ `src/systems/breeding.py` and `src/models/genetics.py`

### "I want to change how pellets grow"
→ `src/systems/grass_growth_system.py`

### "I want to modify the UI"
→ `src/rendering/ui_components.py`

### "I want to add a new biome"
→ `src/models/environment.py` (add to `BiomeType` enum)

### "I want to modify weather effects"
→ `src/models/environment.py` and `src/models/environmental_traits.py`

## Running the Game

**Main game**:
```bash
python main.py
```

**Examples**:
```bash
python -m examples.biome_visualization_demo
python -m examples.grass_growth_demo
python -m examples.pellet_evolution_pygame_demo
```

**Tests**:
```bash
python -m pytest tests/
python -m pytest tests/grass_growth/
python -m pytest tests/spatial/
```

## Common Workflows

### Adding a New Trait

1. Define the trait in `src/models/ecosystem_traits.py`:
   ```python
   NIGHT_VISION = Trait(
       name="Night Vision",
       description="Can see better in darkness",
       stat_modifiers={"speed": 1.2},
       interaction_effects={"darkness_bonus": 1.5}
   )
   ```

2. Handle the trait effect in `src/systems/trait_effects_handler.py`:
   ```python
   if "darkness_bonus" in trait.interaction_effects:
       if current_weather == WeatherType.NIGHT:
           multiplier *= trait.interaction_effects["darkness_bonus"]
   ```

3. Add to trait pool in `main.py` or breeding system

### Adding a New Creature Type

1. Define in your script:
   ```python
   from src.models.creature import CreatureType
   from src.models.stats import Stats, StatGrowth
   
   dragon_type = CreatureType(
       name="Dragon",
       base_stats=Stats(max_hp=150, attack=25, defense=20, speed=15),
       stat_growth=StatGrowth(hp_growth=20.0, attack_growth=4.0),
       type_tags=["fire", "flying"]
   )
   ```

2. Create creatures with this type:
   ```python
   dragon = Creature(name="Draco", creature_type=dragon_type, level=5)
   ```

### Debugging

- **Battle logs**: Check `battle.get_battle_log()` for event history
- **Creature state**: Use `creature_inspector` in UI to view detailed stats
- **Enable debug rendering**: Set `show_grid=True` in `ArenaRenderer`
- **Slow down simulation**: Reduce FPS in `GameWindow` or add pauses

## Architecture Patterns

### Event-Driven System

The battle system uses callbacks for events:
```python
def on_battle_event(event):
    print(f"Event: {event.event_type} - {event.message}")

battle.add_event_callback(on_battle_event)
```

### Component-Based Creatures

Creatures are composed of multiple components:
- `Stats`: Health, attack, defense, speed
- `Traits`: Behavioral and stat modifiers
- `Abilities`: Special moves
- `SpatialComponent`: Position and velocity
- `AttentionManager`: AI decision-making

### Genetics Engine

Uses Mendelian genetics:
- Each trait has dominant/recessive genes
- Offspring inherit one gene from each parent
- Mutations can occur during reproduction
- Trait expression follows genetic rules

## Best Practices

1. **Always use type hints**: Makes code self-documenting
2. **Add docstrings**: Especially for public methods
3. **Keep systems decoupled**: Use events/callbacks instead of direct dependencies
4. **Test your changes**: Add unit tests for new features
5. **Follow existing patterns**: Look at similar code before implementing

## Getting Help

- **Documentation**: Check `docs/` directory for detailed system docs
- **Examples**: Run example scripts to see features in action
- **Tests**: Look at test files to understand expected behavior
- **Code search**: Use grep to find where features are implemented

## Contributing

See `CONTRIBUTING.md` for guidelines on:
- Code style
- Testing requirements
- Pull request process
- Documentation standards
