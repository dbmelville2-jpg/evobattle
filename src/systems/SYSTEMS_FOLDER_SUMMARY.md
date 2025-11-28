# Systems Folder Summary
> **Location:** `src/systems/`
> **Purpose:** Contains the core logic engines and simulation systems for EvoBattle.

This document provides a detailed summary of the files located in the `src/systems` directory. These files implement the various mechanics of the simulation, from the main battle loop to specific subsystems like disease, breeding, and environmental interactions.

---

## Core Engine

### `battle_spatial.py`
**Role:** The central engine for the real-time simulation.
*   **Responsibilities:**
    *   Initializes all other managers and systems.
    *   Runs the main game loop (`update` method).
    *   Coordinates the interaction between different systems (e.g., triggering breeding checks, updating physics).
    *   Manages the high-level state of the battle (start, end, pause).
*   **Key Interactions:** Acts as the hub, connecting `MovementManager`, `CombatManager`, `ResourceManager`, etc.

### `battle_spatial_helpers.py`
**Role:** Utility functions for the spatial battle system.
*   **Responsibilities:**
    *   Provides helper methods for spatial calculations or common tasks used by `battle_spatial.py` to keep the main file cleaner.

---

## Simulation Subsystems

### `living_world.py`
**Role:** Enhances the simulation with deep social and behavioral mechanics.
*   **Responsibilities:**
    *   **Social State:** Tracks relationships (Parent, Child, Ally, Rival).
    *   **Food Sharing:** Logic for creatures sharing food with allies/offspring.
    *   **Cooperative Combat:** Logic for allies joining fights.
    *   **Personality:** Influences target selection and retreat logic based on traits.

### `disease_system.py`
**Role:** Simulates the spread and effects of diseases.
*   **Responsibilities:**
    *   **Outbreaks:** Triggers disease outbreaks based on population density or random events.
    *   **Transmission:** Handles disease spread between creatures and pellets.
    *   **Progression:** Manages infection stages (Incubating -> Symptomatic -> Recovering -> Immune).
    *   **Effects:** Applies stat penalties and damage to infected creatures.

### `breeding.py`
**Role:** Manages creature reproduction.
*   **Responsibilities:**
    *   **Genetics:** Combines traits from two parents using dominant/recessive mechanics.
    *   **Mutation:** Introduces random genetic mutations.
    *   **Inheritance:** Calculates inherited stats and potential skill/memory transfer.

### `grass_growth_system.py`
**Role:** Simulates dynamic plant growth.
*   **Responsibilities:**
    *   **Pollination:** Creatures spread seeds as they move.
    *   **Nutrient Zones:** Areas where creatures died promote faster growth.
    *   **Growth Pulses:** Periodic environmental events that boost growth.
    *   **Symbiosis:** Herbivores passively boost nearby plant growth.

### `biome_generator.py`
**Role:** Generates diverse environments.
*   **Responsibilities:**
    *   Creates different biome types (Grassland, Desert, Forest, Marsh, Rocky Highlands).
    *   Configures terrain, weather, resources, and hazards for each biome.
    *   Supports mixed biomes and multi-region arenas.

---

## Learning & Evolution

### `neural_observational_learning.py`
**Role:** Implements "memetic" evolution for neural networks.
*   **Responsibilities:**
    *   Allows `Intelligent` creatures to copy brain weights from successful neighbors.
    *   Accelerates the spread of successful strategies through the population.

### `observational_learning.py`
**Role:** General observational learning system.
*   **Responsibilities:**
    *   Creatures form beliefs by watching others (e.g., seeing someone eat -> belief "food is there").
    *   Handles observation range and line-of-sight checks.

### `learned_behavior_inheritance.py`
**Role:** Passes learned knowledge to offspring.
*   **Responsibilities:**
    *   Transfers "beliefs" from parents to children as "instincts".
    *   Allows successful behaviors to be inherited alongside genetics.

### `trait_injection.py`
**Role:** Procedurally introduces new traits into the gene pool.
*   **Responsibilities:**
    *   Injects new traits during breeding or cosmic events.
    *   Responds to environmental pressure (e.g., starvation -> inject metabolic trait).
    *   Maintains genetic diversity.

### `trait_effects_handler.py`
**Role:** Applies complex trait logic.
*   **Responsibilities:**
    *   Calculates modifiers for combat, movement, and behavior based on active traits.
    *   Handles conditional effects (e.g., "Pack Hunter" bonus only when allies are near).

### `mutation.py`
**Role:** Handles low-level genetic mutation logic.
*   **Responsibilities:**
    *   Provides functions for randomizing stats and traits during breeding.

---

## Player Interaction & Research

### `scientific_intervention.py`
**Role:** Implements player tools for guiding evolution.
*   **Responsibilities:**
    *   Provides tools like "Reward", "Discourage", "Mark Area".
    *   Allows the player to influence creature beliefs and behaviors directly.

### `experiment_overseer_system.py`
**Role:** Meta-game system for "The Overseer".
*   **Responsibilities:**
    *   Tracks "Bio-Data" currency earned from observing events.
    *   Unlocks and executes "Protocols" (powers) like "Induce Mutation" or "Dispense Nutrients".

### `research_ethics.py`
**Role:** Tracks the moral alignment of the player's research.
*   **Responsibilities:**
    *   Monitors player actions (e.g., helping vs. harming creatures).
    *   Calculates scores for Welfare, Ecosystem Health, and Research Integrity.
    *   Determines the player's "Research Approach" (e.g., "Benevolent Interventionist").

### `research_assistants.py`
**Role:** (Likely) Manages automated research tasks or helpers.
*   *Note: Needs verification of specific implementation.*

---

## Analytics & Logging

### `event_logger.py`
**Role:** Comprehensive logging system.
*   **Responsibilities:**
    *   Tracks all significant game events (births, deaths, combat, foraging, building, disease, breeding)
    *   Generates real-time console output with timestamps
    *   Creates session log files for post-game analysis
    *   Produces end-of-session summary reports
    *   Captures detailed event context (killer, cause of death, parents, strain info, etc.)
    *   Handles Unicode encoding for Windows compatibility
*   **Event Categories:**
    *   **Births**: Creature spawns with parent and strain information
    *   **Deaths**: Cause of death, killer, age at death
    *   **Combat**: Attack events, damage dealt, kills
    *   **Foraging**: Food collection, starvation warnings
    *   **Building**: Construction progress, building completion
    *   **Disease**: Infection events, disease deaths, outbreaks
    *   **Breeding**: Reproduction events, offspring details
*   **Output Formats:**
    *   Console: `[timestamp] category: message`
    *   File: JSON-formatted events with full details
    *   Summary: Statistics on births, deaths, kills, food collected, buildings completed, session duration

### `brain_statistics.py`
**Role:** Analyzes the population's neural networks.
*   **Responsibilities:**
    *   Calculates statistics on brain diversity, learning rates, and action preferences.
    *   Identifies popular strategies emerging in the population.

### `reward_tracker.py`
**Role:** Tracks creature success for learning systems.
*   **Responsibilities:**
    *   Monitors which creatures are "successful" (eating, killing, surviving).
    *   Used by observational learning to identify role models.

### `terrain_affinity_tracker.py`
**Role:** Tracks how well creatures adapt to terrain.
*   **Responsibilities:**
    *   Monitors creature performance on different terrain types.
    *   Likely used for analytics or unlocking terrain-specific traits.

### `battle_events.py`
**Role:** Defines event types.
*   **Responsibilities:**
    *   Contains `BattleEvent` class and `BattleEventType` enums used by the `EventManager`.

### `betting.py`
**Role:** (Legacy/Side Feature) Betting system.
*   **Responsibilities:**
    *   Allows placing bets on battle outcomes (likely from an older version or specific game mode).

---

## Managers Directory (`src/systems/battle_managers/`)
This directory contains specialized modules that were refactored out of the main `battle_spatial.py` to improve maintainability.

### Manager Architecture

The battle system uses a modular manager architecture where each manager handles a specific domain of responsibility. All managers are coordinated by `SpatialBattle` which orchestrates their update cycles.

**Manager Responsibilities:**

*   **`ai_manager.py`**: Handles decision-making logic (Neural vs. Heuristic)
    - Routes creatures to appropriate AI system (neural brain or attention system)
    - Manages AI update batching and staggering (1/4 creatures per frame)
    - Prioritizes intelligent creatures for every-frame updates
    - Coordinates decision execution

*   **`building_manager.py`**: Manages construction, material spawning, and building decay
    - Spawns building materials periodically (wood, stone, plant fiber, organic)
    - Tracks all active buildings and construction tasks
    - Handles material carrying and deposits by creatures
    - Manages building decay and durability
    - Applies building passive effects (HP regen, breeding bonus, etc.)
    - Coordinates multi-creature construction efforts

*   **`combat_manager.py`**: Handles attacks, damage calculation, and cooldowns
    - Processes attack attempts and range checks
    - Calculates damage with all modifiers (traits, skills, context)
    - Manages attack cooldowns
    - Applies combat effects and status conditions
    - Tracks skill progression (Teamwork, Intimidation, Leadership)
    - Records injuries and combat history

*   **`cooperative_resources.py`**: Logic for resources that require cooperation to harvest
    - Manages resources requiring multiple creatures
    - Coordinates group harvesting efforts
    - Tracks contribution and distributes rewards
    - Handles resource depletion and respawning

*   **`environment_manager.py`**: Manages weather, terrain, and hazards
    - Updates weather conditions and day/night cycle
    - Manages terrain effects on movement and behavior
    - Handles environmental hazards (fire, poison, quicksand, etc.)
    - Applies environmental damage to creatures
    - Tracks hazard duration and area of effect

*   **`event_manager.py`**: Central event bus for decoupling systems
    - Publishes events to all subscribers
    - Manages event callbacks and listeners
    - Provides decoupled communication between systems
    - Enables modular feature integration

*   **`lifecycle_manager.py`**: Handles births, deaths, and population control
    - Processes creature births and establishes relationships
    - Handles creature deaths and cleanup
    - Manages population limits and strain tracking
    - Triggers death-related events (revenge relationships, etc.)
    - Maintains population statistics

*   **`movement_manager.py`**: Handles physics, collision, and position updates
    - Updates creature positions based on velocity
    - Applies physics and collision detection
    - Manages separation forces to prevent overlap
    - Handles boundary clamping
    - Updates spatial grid for efficient neighbor queries
    - Applies terrain movement modifiers

*   **`neural_manager.py`**: Manages neural network updates and learning
    - Updates neural networks for intelligent creatures
    - Applies learning rewards based on outcomes
    - Handles observational learning (copying successful neighbors)
    - Manages brain inheritance during breeding
    - Tracks learning rates and decay

*   **`resource_manager.py`**: Manages pellet spawning, grass growth, and collection
    - Spawns food pellets (resources)
    - Handles pellet reproduction and evolution
    - Manages grass growth system (nutrient zones, pollination, growth pulses)
    - Processes pellet collection by creatures
    - Tracks pellet populations and strains

**Benefits of Manager Architecture:**
- ✅ Separation of concerns - each manager has a single responsibility
- ✅ Easier testing and debugging - isolated components
- ✅ Modular feature toggling - systems can be enabled/disabled independently
- ✅ Clearer code organization - reduced file complexity
- ✅ Improved performance - optimized update cycles per manager
- ✅ Better maintainability - changes isolated to specific managers
