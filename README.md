# Evolution Battle Game

## Project Description
This is an evolution-based battle game where players can engage in battles, breed their fighters, and place bets. Every creature has a unique story, personality, and history that makes them memorable.

## Features

### Living World System ✓
Transform battles into emergent narratives where every creature matters:
- **Individual Histories**: Track every attack, kill, achievement, and life event
- **Skill Progression**: Skills improve through use (Melee Attack, Dodge, Critical Strike, etc.)
- **Unique Personalities**: 7 personality traits affect behavior (aggression, caution, loyalty, pride, etc.)
- **Dynamic Relationships**: Family bonds, rivalries, alliances, and revenge arcs
- **Achievement System**: Celebrate exceptional moments (Giant Slayer, First Blood, etc.)
- **Creature Inspector UI**: Click creatures to see their full history and stats
- **Emergent Stories**: Watch legendary creatures rise and dramatic rivalries form

See [Living World Documentation](docs/LIVING_WORLD_DOCUMENTATION.md) for details.

### Battle System ✓
A comprehensive turn-based combat engine featuring:
- Speed-based turn order with random tiebreaking
- Complex damage calculation with type effectiveness
- Status effects (poison, burn, sleep, paralysis, etc.)
- Buff/debuff system for strategic gameplay
- Multiple ability types (physical, special, healing, buff, debuff)
- Complete battle logging for analysis and replay

See [Battle System Documentation](docs/BATTLE_SYSTEM_DOCUMENTATION.md) for details.

### Creature System ✓
Full creature management including:
- Stats and stat modifiers
- Level and experience system
- Ability learning and cooldowns
- Trait system for genetic characteristics
- Evolution paths and breeding mechanics

See [Core Models Documentation](docs/MODELS_DOCUMENTATION.md) for details.

### Ecosystem Survival System ✓
A complete survival ecosystem simulation featuring:
- Hunger system with metabolic traits
- Resource gathering and foraging behavior
- Trait-driven wandering and exploration
- Starvation mechanics
- Dynamic behavior based on hunger levels
- 15+ predefined ecosystem traits (Forager, Efficient Metabolism, Curious, etc.)

See [Ecosystem Documentation](docs/ECOSYSTEM_DOCUMENTATION.md) for details.

### Environmental Simulation System ✓ NEW!
Deep environmental interactions that affect creature survival and behavior:
- **Dynamic Weather**: 5 weather types (clear, rainy, stormy, foggy, drought) affecting movement, hunger, and resources
- **Terrain Types**: 6 distinct terrains (grass, rocky, water, forest, desert, marsh) with unique properties
- **Day/Night Cycle**: 4 time phases (dawn, day, dusk, night) affecting visibility and activity
- **Environmental Hazards**: 5 hazard types (fire, poison, quicksand, thorns, electrical) with area-of-effect damage
- **28 Environmental Traits**: Weather adaptation, terrain specialization, time-of-day activity, hazard resistance
- **Integrated Effects**: Weather impacts hunger (0.8x-1.4x), terrain affects speed (0.3x-1.3x), hazards deal damage
- **Trait-Based Adaptation**: Creatures with environmental traits get bonuses (Aquatic 2x speed in water, Fire Proof immunity, etc.)

See [Environmental Simulation Documentation](docs/ENVIRONMENTAL_SIMULATION_DOCUMENTATION.md) for details.

### Grass Growth Enhancement System ✓
Dynamic pellet (food) growth using simulation-based mechanics:
- **Nutrient Zones**: Pellets grow faster where creatures died (1.05-1.15x boost, lasts 30s)
- **Pollination**: Creatures spread seeds as they move (3% chance on revisit)
- **Growth Pulses**: Periodic environmental boosts (10% boost every 60s for 8s)
- **Symbiotic Bonus**: Herbivores enhance nearby grass growth (up to 8% boost)
- **Spatial Patterns**: Pellets cluster around death sites and herbivore paths
- **Balanced Growth**: 100% increase over 30s with zones vs 40% baseline

See [Grass Growth System Documentation](docs/GRASS_GROWTH_SYSTEM.md) for details.

### Lethal Combat Traits ✓
High-risk, high-reward combat traits that enable dramatic kills and apex predators:
- **10 New Offensive Traits**: Berserker, Executioner, Bloodthirsty, Brutal, Assassin, Apex Predator, Reckless Fury, Toxic, Frenzied, Vampiric
- **Advanced Mechanics**: Bleed, poison, lifesteal, execute, multi-strike, armor penetration
- **Glass Cannon Builds**: High offense with defensive trade-offs
- **Scaling Effects**: Kill streaks, rage mode, fear auras
- **Strategic Depth**: Counter-play and archetype diversity

See [Lethal Combat Traits Documentation](docs/LETHAL_COMBAT_TRAITS_DOCUMENTATION.md) for details.

### Genetic Lineage System ✓
An evolutionary ecosystem where creatures form dynamic genetic families:
- Strain-based families instead of fixed teams
- Color-coded genetic similarity (hue represents lineage)
- Trait inheritance with mutations (add/remove/modify traits)
- Natural selection and strain extinction
- Population analytics tracking dominant/extinct strains
- Visual evolution through color spectrum changes

See [Lineage System Documentation](docs/LINEAGE_SYSTEM_DOCUMENTATION.md) for details.

## Quick Start

## For Developers

### Documentation
- [**📚 Documentation Index**](docs/DOCUMENTATION_INDEX.md) - Complete guide to all documentation
- [**🏗️ Systems Architecture**](SYSTEMS_ARCHITECTURE.md) - **NEW!** Master reference for all systems and interactions
- [Living World](docs/LIVING_WORLD_DOCUMENTATION.md) - Creature histories, skills, personalities
- [Battle System](docs/BATTLE_SYSTEM_DOCUMENTATION.md) - Complete battle system guide
- [Ecosystem](docs/ECOSYSTEM_DOCUMENTATION.md) - Hunger, foraging, and survival
- [Environmental Simulation](docs/ENVIRONMENTAL_SIMULATION_DOCUMENTATION.md) - Weather, terrain, hazards

📁 **Note:** Historical documents are in [docs/archive/](docs/archive/)

### Running Examples

All examples should be run from the project root directory using Python's module syntax:

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

enemy = Creature(name="Foe", creature_type=warrior_type, level=5)
enemy.add_ability(create_ability('tackle'))

# Run battle
battle = Battle([player], [enemy])
winner = battle.simulate()

# Living World demos
python3 -m examples.living_world_demo              # Text-based: See histories and skills
python3 -m examples.interactive_living_world_demo  # Visual: Click creatures to inspect

# Battle system examples
python3 -m examples.battle_system_example

# Core models examples
python3 -m examples.core_models_example

# Spatial battle examples
python3 -m examples.spatial_battle_example

# Ecosystem survival simulation (text-based)
python3 -m examples.ecosystem_survival_demo

# Ecosystem survival with Pygame visualization
python3 -m examples.ecosystem_pygame_demo

# Genetic strain evolution demo (shows lineage system)
python3 -m examples.genetic_strain_demo

# Real-time battle example
python3 -m examples.realtime_battle_example

# Pygame rendering demo
python3 -m examples.pygame_rendering_demo
```

### Pygame Rendering Demo

Watch battles in real-time with full visual rendering:

```bash
# Run the Pygame visualization demo
python3 -m examples.pygame_rendering_demo
```

**Features:**
- Real-time 2D arena visualization
- Creature movement and combat animations
- HP/energy bars and status indicators
- Event log showing battle actions
- Interactive controls (SPACE to pause, ESC to exit)

### Ecosystem Survival Demo

Experience the complete survival ecosystem with hunger and foraging:

```bash
# Run the Ecosystem Survival Pygame demo
python3 -m examples.ecosystem_pygame_demo
```

**Features:**
- Hunger bars showing creature survival status
- Food resources scattered in arena
- Creatures seeking food when hungry
- Diverse metabolic traits affecting behavior
- Real-time survival simulation
- Interactive controls (SPACE to pause, R to restart, ESC to exit)

**Controls:**
- `SPACE` - Pause/Resume battle
- `ESC` - Exit

The rendering system uses an event-driven architecture that subscribes to battle events and creates corresponding visual effects. All rendering components are modular and can be customized or extended.

### Running Tests

```bash
# Run all tests
python3 -m unittest discover tests -v

# Run specific test suites
python3 -m unittest tests.test_battle -v
python3 -m unittest tests.test_status_effect -v
python3 -m unittest tests.test_creature -v
```

## Rendering & Visualization ✓
Real-time Pygame-based visualization system featuring:
- 2D spatial arena with grid and resource locations
- Creature rendering with HP/hunger bars and strain-based colors
- Interactive UI with population panels and battle feed
- Event-driven animations (damage numbers, effects)
- Pause/resume and input handling
- Battle state visualization and survivor display

See the [Pygame Rendering Demo](#pygame-rendering-demo) below for a live visualization example.

![EvoBattle Rendering Screenshot](https://github.com/user-attachments/assets/e876d6cc-186d-4e7c-bdf3-6d89972b03e8)

## Setup Instructions
1. Clone the repository: `git clone https://github.com/dbmelville2-jpg/evobattle`
2. Navigate into the project directory: `cd evobattle`
3. Install dependencies: `pip install -r requirements.txt`
   - Includes: Flask, Python-dotenv, Pygame