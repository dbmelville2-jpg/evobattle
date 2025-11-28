# EvoBattle Systems - Function Summary

This document provides a comprehensive overview of all functions, classes, and methods in the `src/systems` directory.

---

## Table of Contents

- [battle_events.py](#battle_eventspy) - Battle event definitions
- [battle_spatial.py](#battle_spatialpy) - Main spatial battle system
- [battle_spatial_helpers.py](#battle_spatial_helperspy) - Helper functions
- [biome_generator.py](#biome_generatorpy) - Biome generation
- [brain_statistics.py](#brain_statisticspy) - Neural brain analytics
- [breeding.py](#breedingpy) - Creature reproduction system
- [disease_system.py](#disease_systempy) - Disease management
- [ethical_dilemmas.py](#ethical_dilemmaspy) - Ethical gameplay scenarios
- [event_logger.py](#event_loggerpy) - Game event logging
- [grass_growth_system.py](#grass_growth_systempy) - Grass/pellet growth
- [learned_behavior_inheritance.py](#learned_behavior_inheritancepy) - Behavior learning
- [living_world.py](#living_worldpy) - Living world simulation
- [mutation.py](#mutationpy) - Mutation utilities
- [neural_observational_learning.py](#neural_observational_learningpy) - Neural learning
- [observational_learning.py](#observational_learningpy) - Observational learning
- [population.py](#populationpy) - Population management
- [research_assistants.py](#research_assistantspy) - Research AI assistants
- [research_ethics.py](#research_ethicspy) - Research ethics system
- [reward_tracker.py](#reward_trackerpy) - Reward tracking
- [scientific_intervention.py](#scientific_interventionpy) - Scientific interventions
- [terrain_affinity_tracker.py](#terrain_affinity_trackerpy) - Terrain preferences
- [trait_effects_handler.py](#trait_effects_handlerpy) - Trait effect application
- [trait_injection.py](#trait_injectionpy) - Trait injection system
- [battle_managers/](#battle_managers) - Battle subsystem managers

---

## battle_events.py

### Classes

#### `BattleEventType` (Enum)
Types of battle events for animation/visualization.

**Values:**
- `BATTLE_START`, `CREATURE_SPAWN`, `CREATURE_MOVE`, `ABILITY_USE`
- `DAMAGE_DEALT`, `HEALING`, `STATUS_APPLIED`, `MISS`, `CRITICAL_HIT`
- `SUPER_EFFECTIVE`, `NOT_EFFECTIVE`, `CREATURE_FAINT`, `HAZARD_DAMAGE`
- `RESOURCE_COLLECTED`, `CREATURE_BIRTH`, `CREATURE_DEATH`, `CREATURE_CONSUMED`
- `BATTLE_END`, `PELLET_SPAWN`, `PELLET_REPRODUCE`, `PELLET_CONSUMED`, `PELLET_DEATH`
- `ATTENTION_CHANGE`

#### `BattleEvent`
Represents a single event in battle for animation/visualization.

**Methods:**
- `__init__(event_type, actor=None, target=None, ability=None, value=None, message="", data=None)` - Initialize battle event
- `__repr__()` - String representation

---

## battle_spatial.py

### Classes

#### `BattleCreature`
Wrapper for Creature with spatial properties and behavior.

**Methods:**
- `__init__(creature, position)` - Initialize battle creature with spatial properties
- `__eq__(other)` - Compare BattleCreatures by creature ID
- `__hash__()` - Make hashable
- `_determine_behavior()` - Determine behavior based on creature traits
- `is_alive()` - Check if creature is still alive
- `get_attention_debug_info(current_time)` - Get debug information about attention state
- `can_attack(current_time)` - Check if creature can attack based on cooldown

#### `SpatialBattle`
Manages real-time spatial combat in a 2D arena.

**Methods:**
- `__init__(creatures, arena_width=200, arena_height=200, combat_config=None, environment=None, enable_environment=False, biome_type=None)` - Initialize spatial battle
- `creatures` (property) - Get list of all creatures (alive and dead)
- `events` (property) - Get list of battle events
- `update(delta_time)` - Update battle state for one frame
- `_end_battle()` - End the battle when population has collapsed
- `simulate(duration=60.0, time_step=0.1)` - Simulate entire battle for a duration
- `_get_neural_inputs(creature, all_alive)` - Gather sensory inputs for neural network
- `_execute_neural_action(creature, action, all_alive)` - Execute neural network decision
- `_log(message)` - Internal logging helper
- `_emit_event(event)` - Internal event emission helper
- `add_event_callback(callback)` - Register a callback for battle events
- `get_battle_log()` - Get the complete battle log
- `get_state_snapshot()` - Get current state snapshot for visualization

---

## breeding.py

### Classes

#### `Breeding`
Manages creature breeding and genetic trait inheritance.

**Methods:**
- `__init__(mutation_rate=0.1, trait_inheritance_chance=0.8, injection_system=None)` - Initialize breeding system
- `breed(parent1, parent2, birth_time=None)` - Breed two creatures to create offspring
- `__repr__()` - String representation

---

## disease_system.py

### Classes

#### `DiseaseSystem`
Manages the lifecycle of diseases in the simulation.

**Methods:**
- `__init__()` - Initialize the disease system
- `update(delta_time, current_time, creatures, resources, arena_width, arena_height)` - Main update loop
- `_check_outbreak_conditions(creatures, resources, width, height)` - Check if conditions are met for spontaneous outbreak
- `_trigger_outbreak(disease_type, population, is_creature)` - Infect a random individual to start outbreak
- `infect_creature(creature, disease)` - Attempt to infect a creature
- `infect_pellet(pellet, disease)` - Attempt to infect a pellet
- `_update_creature_infections(delta_time, creatures, current_time)` - Update state of infected creatures
- `_apply_creature_symptoms(creature, disease, delta_time)` - Apply active disease effects
- `_update_pellet_infections(delta_time, resources, current_time)` - Update state of infected pellets
- `_handle_transmission(delta_time, creatures, resources)` - Handle disease spread between entities

---

## event_logger.py

### Classes

#### `EventCategory` (Enum)
Categories of game events.

**Values:**
- `LIFECYCLE`, `COMBAT`, `FORAGING`, `BUILDING`, `SOCIAL`, `LEARNING`, `ENVIRONMENT`

#### `GameEvent`
Represents a single game event.

**Methods:**
- `__str__()` - Format event as readable string

#### `EventLogger`
Comprehensive game event logger.

**Methods:**
- `__init__(log_to_console=True, log_to_file=True, log_file_path=None)` - Initialize event logger
- `_write_header()` - Write header to log file
- `log_event(category, message, timestamp, details=None)` - Log a game event
- `log_birth(creature_id, strain_name, parent_ids, timestamp, position)` - Log creature birth
- `log_death(creature_id, strain_name, cause, timestamp, age, kills=0, pellets_collected=0)` - Log creature death
- `log_attack(attacker_id, attacker_strain, target_id, target_strain, damage, timestamp, ability=None)` - Log combat attack
- `log_kill(killer_id, killer_strain, victim_id, victim_strain, timestamp)` - Log creature kill
- `log_pellet_spawn(pellet_type, position, value, timestamp)` - Log pellet spawning
- `log_pellet_collection(creature_id, strain_name, pellet_type, nutrition, timestamp)` - Log pellet collection
- `log_material_gather(creature_id, strain_name, material_type, timestamp)` - Log material gathering
- `log_building_progress(building_id, building_type, progress, timestamp)` - Log building construction progress
- `log_building_complete(building_id, building_type, timestamp)` - Log building completion
- `log_social_interaction(creature_id, interaction_type, target_id, timestamp, effect)` - Log social interaction
- `log_learning(creature_id, strain_name, learning_type, knowledge, timestamp)` - Log learning event
- `_update_strain_stat(strain_name, stat_name, value)` - Update strain-specific statistics
- `generate_summary(final_timestamp)` - Generate end-of-session summary
- `close(final_timestamp)` - Close the logger and write summary

---

## population.py

### Classes

#### `EventType` (Enum)
Types of population events.

**Values:**
- `BIRTH`, `DEATH`, `BREEDING`, `MATURITY`, `STARVATION`, `COMBAT`

#### `PopulationEvent`
Represents a single population event.

**Methods:**
- `__init__(event_type, creature_id, timestamp=None, details=None)` - Initialize population event
- `to_dict()` - Serialize to dictionary
- `__repr__()` - String representation

#### `EventLogger`
Logs population events for analysis and replay.

**Methods:**
- `__init__()` - Initialize event logger
- `log(event_type, creature, details=None)` - Log a population event
- `get_events(event_type=None, creature_id=None)` - Get filtered events
- `clear()` - Clear all logged events
- `to_dict()` - Serialize to dictionary

#### `PopulationAnalytics`
Tracks and analyzes population metrics over time.

**Methods:**
- `__init__()` - Initialize analytics tracker
- `record_tick(pop_manager)` - Record current population state
- `get_statistics()` - Get summary statistics
- `clear()` - Clear history
- `to_dict()` - Serialize to dictionary

#### `PopulationManager`
Manages population of creatures in an ecosystem.

**Methods:**
- `__init__()` - Initialize population manager
- `spawn_creature(creature, log_event=True)` - Add a new creature to population
- `remove_creature(creature_id, cause="unknown", log_event=True)` - Remove a creature from population
- `get_creature(creature_id)` - Get creature by ID
- `get_all_creatures()` - Get all creatures
- `get_alive_creatures()` - Get all living creatures
- `get_dead_creatures()` - Get all dead creatures
- `get_population_size()` - Get current population size
- `get_alive_count()` - Get count of living creatures
- `get_strain_count(strain_id)` - Get count of creatures in a strain
- `get_strains()` - Get all unique strain IDs
- `update(delta_time)` - Update all creatures in population
- `to_dict()` - Serialize to dictionary
- `__repr__()` - String representation

---

## trait_effects_handler.py

### Classes

#### `TraitEffectsHandler`
Handles application of trait interaction_effects in combat and behavior.

**Methods:**
- `__init__()` - Initialize trait effects handler
- `get_combat_damage_modifier(attacker, defender, allies_nearby=0, enemies_nearby=0, family_nearby=0)` - Calculate combat damage modifier from all trait effects
- `get_defense_modifier(defender, attacker, allies_nearby=0)` - Calculate defense modifier from trait effects
- `should_avoid_combat(creature, hunger_level, allies_nearby=0)` - Determine if creature should avoid combat based on traits
- `get_movement_speed_modifier(creature, is_fleeing=False, allies_nearby=0)` - Get movement speed modifier from traits
- `get_food_sharing_willingness(creature, target_is_family=False)` - Get willingness to share food (0.0 to 1.0)
- `extract_all_effects(creature)` - Extract all interaction_effects from creature's traits
- `get_weather_bonus(creature, weather_type, stat_type='damage')` - Calculate stat bonus from weather-responsive traits
- `get_terrain_bonus(creature, terrain_type, stat_type='damage')` - Calculate stat bonus from terrain-adaptive traits
- `should_absorb_hazard(creature, hazard_type)` - Check if creature can absorb a specific hazard type
- `get_hazard_absorption_rate(creature, hazard_type)` - Get percentage of hazard damage converted to HP

---

## battle_managers/

The `battle_managers` subdirectory contains specialized managers that handle different aspects of the battle system:

### combat_manager.py

#### `CombatManager`
Manages combat mechanics for the spatial battle system.

**Methods:**
- `__init__(event_manager, combat_config, trait_effects_handler, enhancer=None, event_logger=None)` - Initialize combat manager
- `attempt_attack(attacker, defender, current_time, creatures_list)` - Attempt an attack from attacker to defender
- `execute_ability(attacker, defender, ability, creatures_list)` - Execute an ability from attacker to defender
- `calculate_damage(attacker, defender, ability, creatures_list)` - Calculate damage (returns tuple of damage and was_critical)
- `get_type_effectiveness(attacker, defender)` - Calculate type effectiveness multiplier
- `_check_accuracy(accuracy)` - Check if an ability hits
- `_apply_relationship_damage_modifier(attacker, defender, base_damage, creatures_list)` - Apply damage modifiers based on relationships

### movement_manager.py

#### `MovementManager`
Manages movement physics and spatial updates for all creatures.

**Methods:**
- `__init__(arena, creature_grid, environment_manager=None)` - Initialize movement manager
- `set_buildings(buildings)` - Update the list of buildings for collision detection
- `update_movement(creatures, delta_time)` - Update movement physics for all creatures
- `_check_barrier_collision(creature)` - Check if creature is colliding with any barrier building tiles
- `_apply_separation_forces(creature)` - Calculate and apply separation forces to avoid crowding

### resource_manager.py

#### `ResourceManager`
Manages food resources (pellets) in the battle arena.

**Methods:**
- `__init__(arena, event_manager, creature_grid, spawn_rate=0.1, initial_resources=5, enable_growth_system=True, event_logger=None)` - Initialize resource manager
- `update(delta_time)` - Update resource state for one frame
- `spawn_random_resource()` - Spawn a food pellet agent at random location
- `spawn_pellets_from_creature(creature, count=3)` - Spawn pellets when a creature dies
- `check_pellet_collection(creature, reward_tracker=None, enhancer=None, building_materials=None)` - Check if creature is near any pellets and collect them
- `_update_pellets(delta_time)` - Update all pellets (age, reproduce, die)
- `spawn_cooperative_resource()` - Spawn a large resource cluster that encourages cooperative gathering

### Other Battle Managers

The `battle_managers` subdirectory also contains:

- **ai_manager.py** - AI decision-making and behavior
- **building_manager.py** - Building construction and management
- **cooperative_resources.py** - Cooperative resource gathering
- **environment_manager.py** - Environmental effects and terrain
- **event_manager.py** - Event emission and callbacks
- **lifecycle_manager.py** - Creature lifecycle (birth, death, aging)
- **neural_manager.py** - Neural network decision-making

---

## Additional Systems

### biome_generator.py
Generates biomes with specific environmental characteristics, terrain types, and resource distributions.

### brain_statistics.py
Tracks and analyzes neural brain statistics across the population for research and visualization.

### ethical_dilemmas.py
Presents ethical gameplay scenarios and tracks player choices for narrative and research purposes.

### grass_growth_system.py
Manages grass/pellet growth, reproduction, and spatial distribution using cellular automata-like rules.

### learned_behavior_inheritance.py
Allows offspring to inherit learned behaviors from parents, not just genetic traits.

### living_world.py
Orchestrates the entire living world simulation, coordinating all subsystems.

### mutation.py
Provides mutation utilities for applying tradeoff mutations to traits.

### neural_observational_learning.py
Enables creatures to learn from observing other creatures' neural network decisions.

### observational_learning.py
Implements observational learning where creatures can learn behaviors by watching others.

### research_assistants.py
Provides AI research assistants that can analyze simulation data and provide insights.

### research_ethics.py
Manages research ethics considerations and player consent for data collection.

### reward_tracker.py
Tracks rewards for reinforcement learning in neural networks.

### scientific_intervention.py
Allows scientific interventions in the simulation (trait injection, environmental changes, etc.).

### terrain_affinity_tracker.py
Tracks which creatures prefer which terrain types based on their performance and behavior.

### trait_injection.py
Manages trait injection into the population for research and gameplay purposes.

**Key Class: `TraitInjectionSystem`**

**Methods:**
- `__init__(config=None)` - Initialize trait injection system
- `inject_breeding_trait(parent1, parent2, generation)` - Attempt to inject a trait during breeding
- `inject_random_trait(creature)` - Inject a random trait into a creature
- `should_inject(generation, parent_traits)` - Determine if trait should be injected

---

## Summary

The `src/systems` directory contains **35 Python files** organized into:

### Core Battle Systems
- **Spatial Battle**: Real-time 2D combat with positioning and movement
- **Battle Managers**: Specialized subsystems (combat, movement, resources, AI, lifecycle, etc.)
- **Events**: Battle event tracking and callbacks

### Population & Genetics
- **Breeding**: Genetic trait inheritance with Mendelian genetics
- **Population**: Population tracking, analytics, and lifecycle management
- **Mutation**: Trait mutation utilities

### Environment & Resources
- **Biome Generator**: Procedural biome generation
- **Grass Growth**: Resource growth and distribution
- **Disease System**: Disease outbreaks and transmission
- **Environment Manager**: Weather, terrain, and hazards

### Learning & Intelligence
- **Neural Networks**: Brain-based decision-making
- **Observational Learning**: Learning from watching others
- **Learned Behavior Inheritance**: Passing learned behaviors to offspring
- **Reward Tracking**: Reinforcement learning

### Research & Ethics
- **Event Logger**: Comprehensive game event logging
- **Research Assistants**: AI analysis tools
- **Research Ethics**: Ethical considerations and consent
- **Scientific Intervention**: Controlled experiments

### Trait Systems
- **Trait Effects Handler**: Apply trait effects in combat and behavior
- **Trait Injection**: Inject traits for research purposes
- **Terrain Affinity**: Track terrain preferences

Each system is designed to work together to create a complex, emergent ecosystem where creatures evolve, learn, compete, and cooperate in a dynamic 2D world.
