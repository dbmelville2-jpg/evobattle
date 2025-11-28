# EvoBattle Game Models Documentation

This document provides a comprehensive overview of the core data models and systems in EvoBattle.

## 1. Core Entities

### Creature (`src/models/creature.py`)
The central agent in the simulation.
- **Attributes**:
  - `stats`: Core statistics (HP, Energy, Speed, etc.) managed by `Stats` class.
  - `traits`: List of `Trait` objects defining genetic characteristics.
  - `skills`: `SkillManager` handling learned abilities (e.g., Fighting, Foraging).
  - `brain`: `NeuralBrain` for decision making.
  - `history`: `CreatureHistory` tracking lifecycle events.
  - `personality`: `PersonalityProfile` influencing behavioral tendencies.
  - `relationships`: `RelationshipManager` tracking social bonds.
  - `memory`: Systems for tracking hazards (`HazardMemory`) and social interactions (`SocialMemory`).

### Pellet (`src/models/pellet.py`)
The primary food source and a living entity with its own evolutionary path.
- **Attributes**:
  - `traits`: `PelletTraits` defining nutritional value, toxicity, growth rate, etc.
  - `history`: `PelletLifeHistory` tracking its lifecycle.
  - `strain_id`: Identifies the genetic lineage of the pellet.
- **Key Behaviors**:
  - `reproduce()`: Creates offspring with mutated traits.
  - `get_nutritional_value()`: Returns energy provided when eaten.

## 2. Environmental System (`src/models/environment.py`)

### Environment
Manages the physical world state.
- **Components**:
  - `WeatherConditions`: Current weather (Clear, Rain, Storm, Fog) affecting visibility and movement.
  - `TerrainGrid`: Grid of `TerrainCell`s (Grass, Rock, Water, Sand) affecting movement and resources.
  - `DayNightCycle`: Tracks time of day, influencing visibility and creature behavior.
  - `Hazards`: Active `EnvironmentalHazard`s (Fire, Poison Cloud, etc.).

### Traits (`src/models/environmental_traits.py`, `weather_terrain_traits.py`)
- **Environmental Traits**: Adaptations like `Aquatic`, `Nocturnal`, `Cold Blooded`.
- **Weather/Terrain Traits**: Specific bonuses for conditions, e.g., `Storm Dancer` (buffs in storms), `Forest Dweller`.

## 3. Trait System

### Ecosystem Traits (`src/models/ecosystem_traits.py`)
Predefined traits categorized by function:
- **Metabolic**: `Efficient Metabolism`, `High Energy`.
- **Behavioral**: `Aggressive`, `Timid`, `Social`.
- **Dietary**: `Carnivore`, `Herbivore`.

### Expanded Traits (`src/models/expanded_traits.py`)
Advanced traits for specialized roles:
- **Combat**: `Berserker`, `Assassin`, `Armored`.
- **Ecological**: `Scavenger`, `Parasite`.
- **Pellet Traits**: `Toxic Defense`, `Nutritious`.

### Trait Generator (`src/models/trait_generator.py`)
Procedural generation system for creating new, unique traits with randomized names and effects.

### Trait Analytics (`src/models/trait_analytics.py`)
System for tracking trait performance:
- Records discovery of new traits.
- Tracks spread and survival rates of traits in the population.

## 4. History & Logging (`src/models/history.py`, `pellet_history.py`)

### CreatureHistory
Tracks a creature's life story:
- **Events**: Birth, Battles, Kills, Reproduction, Death.
- **Stats**: Battles fought, damage dealt, offspring count.
- **Achievements**: Special milestones reached.

### PelletLifeHistory
Tracks pellet lifecycle:
- **Events**: Spawn, Reproduction, Being Eaten, Natural Death.
- **Stats**: Times targeted vs. times eaten (palatability metrics).

## 5. Building System (`src/models/building/`)

### Building (`building_config.py`)
Constructible structures in the world.
- **Types**: `Shelter`, `Nest`, `Food Cache`, `Watchtower`, `Barrier`, etc.
- **Attributes**: `durability`, `completion` (0-100%), `builder_id`.
- **Blueprints**: Define required materials, build time, and passive effects (e.g., `hp_regen_bonus` for Shelters).

### Building Material (`building_material.py`)
Resources used for construction.
- **Types**: `Wood`, `Stone`, `Plant Fiber`, `Organic`.
- **Properties**: Weight (affects carry speed), Durability contribution, Rarity.

### Building Behavior (`building_behavior.py`)
AI logic for construction:
- **Needs**: Identifying what to build (Shelter for safety, Nest for breeding).
- **Tasks**: `BuildingTask` tracks progress of gathering materials and constructing.
- **Cooperation**: Logic for multiple creatures contributing to the same building.
