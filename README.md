# Evolution Battle Game

## Project Description
This is an evolution-based battle game where players can engage in battles, breed their fighters, and place bets.

## Features

### Battle System ✓
A comprehensive turn-based combat engine featuring:
- Speed-based turn order with random tiebreaking
- Complex damage calculation with type effectiveness
- Status effects (poison, burn, sleep, paralysis, etc.)
- Buff/debuff system for strategic gameplay
- Multiple ability types (physical, special, healing, buff, debuff)
- Complete battle logging for analysis and replay

See [Battle System Documentation](BATTLE_SYSTEM_DOCUMENTATION.md) for details.

### Creature System ✓
Full creature management including:
- Stats and stat modifiers
- Level and experience system
- Ability learning and cooldowns
- Trait system for genetic characteristics
- Evolution paths and breeding mechanics

See [Core Models Documentation](MODELS_DOCUMENTATION.md) for details.

### Ecosystem Survival System ✓
A complete survival ecosystem simulation featuring:
- Hunger system with metabolic traits
- Resource gathering and foraging behavior
- Trait-driven wandering and exploration
- Starvation mechanics
- Dynamic behavior based on hunger levels
- 15+ predefined ecosystem traits (Forager, Efficient Metabolism, Curious, etc.)

See [Ecosystem Documentation](ECOSYSTEM_DOCUMENTATION.md) for details.

### Genetic Lineage System ✓
An evolutionary ecosystem where creatures form dynamic genetic families:
- Strain-based families instead of fixed teams
- Color-coded genetic similarity (hue represents lineage)
- Trait inheritance with mutations (add/remove/modify traits)
- Natural selection and strain extinction
- Population analytics tracking dominant/extinct strains
- Visual evolution through color spectrum changes

See [Lineage System Documentation](LINEAGE_SYSTEM_DOCUMENTATION.md) for details.

## Quick Start

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

print(f"Winner: {winner.name}")
for log in battle.get_battle_log():
    print(log)
```

## For Developers

### Agent Coordination
This project is developed by three specialist agents working in coordination:
- **Core Gameplay Engineer** - Implements game mechanics, physics, and player interaction ([Issue #11](https://github.com/dbmelville2-jpg/evobattle/issues/11))
- **Graphics & Rendering Agent** - Handles visual systems, animations, and UI ([Issue #12](https://github.com/dbmelville2-jpg/evobattle/issues/12))
- **Data & Systems Agent** - Manages game state, persistence, and support systems ([Issue #13](https://github.com/dbmelville2-jpg/evobattle/issues/13))

**Important Documentation:**
- [Battle System Documentation](BATTLE_SYSTEM_DOCUMENTATION.md) - Complete battle system guide
- [Core Models Documentation](MODELS_DOCUMENTATION.md) - Creature, stats, and ability systems
- [Ecosystem Documentation](ECOSYSTEM_DOCUMENTATION.md) - Hunger, foraging, and survival mechanics
- [Lineage System Documentation](LINEAGE_SYSTEM_DOCUMENTATION.md) - Genetic strains and evolution
- [Rendering Documentation](RENDERING_DOCUMENTATION.md) - Visual rendering and animation systems
- [Agent Coordination Guide](AGENT_COORDINATION.md) - Team standards, interface contracts, and integration goals
- [Integration Checklist](INTEGRATION_CHECKLIST.md) - Track implementation progress and integration milestones
- [Project Architect Vision](https://github.com/dbmelville2-jpg/evobattle/issues/2) - Overall project leadership and vision

### Running Examples

```bash
# Battle system examples
python3 examples/battle_system_example.py

# Core models examples
python3 examples/core_models_example.py

# Spatial battle examples
python3 examples/spatial_battle_example.py

# Ecosystem survival simulation (text-based)
python3 -m examples.ecosystem_survival_demo

# Ecosystem survival with Pygame visualization
python3 -m examples.ecosystem_pygame_demo

# Genetic strain evolution demo (shows lineage system)
python3 -m examples.genetic_strain_demo
```

### Pygame Rendering Demo

Watch battles in real-time with full visual rendering:

```bash
# Run the Pygame visualization demo
python3 examples/pygame_rendering_demo.py
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
- 2D spatial arena with team-colored zones and grid
- Creature rendering with HP/energy bars and status indicators
- Interactive UI with team panels and battle feed
- Event-driven animations (damage numbers, effects)
- Pause/resume and input handling
- Battle state visualization and winner display

See the [Pygame Rendering Demo](#pygame-rendering-demo) below for a live visualization example.

![EvoBattle Rendering Screenshot](https://github.com/user-attachments/assets/e876d6cc-186d-4e7c-bdf3-6d89972b03e8)

## Setup Instructions
1. Clone the repository: `git clone https://github.com/dbmelville2-jpg/evobattle`
2. Navigate into the project directory: `cd evobattle`
3. Install dependencies: `pip install -r requirements.txt`
   - Includes: Flask, Python-dotenv, Pygame