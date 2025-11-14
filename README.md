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
- [Agent Coordination Guide](AGENT_COORDINATION.md) - Team standards, interface contracts, and integration goals
- [Integration Checklist](INTEGRATION_CHECKLIST.md) - Track implementation progress and integration milestones
- [Project Architect Vision](https://github.com/dbmelville2-jpg/evobattle/issues/2) - Overall project leadership and vision

### Running Examples

```bash
# Battle system examples
python3 examples/battle_system_example.py

# Core models examples
python3 examples/core_models_example.py
```

### Running Tests

```bash
# Run all tests
python3 -m unittest discover tests -v

# Run specific test suites
python3 -m unittest tests.test_battle -v
python3 -m unittest tests.test_status_effect -v
python3 -m unittest tests.test_creature -v
```

## Setup Instructions
1. Clone the repository: `git clone https://github.com/dbmelville2-jpg/evobattle`
2. Navigate into the project directory: `cd evobattle`
3. Install dependencies: `pip install -r requirements.txt`