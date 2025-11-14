# Examples

This directory contains example scripts demonstrating the usage of EvoBattle's core game models.

## Running Examples

To run the examples, use the following command from the project root:

```bash
PYTHONPATH=/path/to/evobattle python3 examples/core_models_example.py
```

Or from the project root:

```bash
PYTHONPATH=. python3 examples/core_models_example.py
```

## Available Examples

### core_models_example.py

Comprehensive demonstration of all core game models including:

1. **Creature Creation** - Creating creatures with types, stats, abilities, and traits
2. **Stat Modifiers** - Applying buffs and debuffs with duration management
3. **Leveling and Experience** - Experience gain and level-up mechanics
4. **Abilities and Combat** - Using abilities in simulated combat scenarios
5. **Evolution System** - Evolving creatures through multiple stages
6. **Breeding and Genetics** - Creating offspring with inherited traits and mutations
7. **Serialization** - Saving and loading creatures to/from JSON

## Documentation

For detailed documentation of the core models, see:
- [MODELS_DOCUMENTATION.md](../MODELS_DOCUMENTATION.md) - Complete API documentation

For running tests:
```bash
python3 -m unittest discover tests -v
```
