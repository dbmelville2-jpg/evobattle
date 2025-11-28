# EvoBattle Models - Function Summary

This document provides a comprehensive overview of all functions, classes, and methods in the `src/models` directory.

---

## Table of Contents

- [ability.py](#abilitypy) - Creature abilities and special moves
- [attention.py](#attentionpy) - Attention and focus management
- [behavior.py](#behaviorpy) - Spatial combat behaviors
- [combat_config.py](#combat_configpy) - Combat configuration parameters
- [combat_memory.py](#combat_memorypy) - Combat encounter tracking
- [combat_targeting.py](#combat_targetingpy) - Enhanced targeting system
- [creature.py](#creaturepy) - Core creature model
- [creature_beliefs.py](#creature_beliefspy) - Belief and learning system
- [creature_brain.py](#creature_brainpy) - Neural network decision-making
- [cross_entity_interactions.py](#cross_entity_interactionspy) - Creature-pellet interactions
- [disease.py](#diseasepy) - Disease system
- [ecosystem_traits.py](#ecosystem_traitspy) - Predefined ecosystem traits
- [environment.py](#environmentpy) - Environmental simulation
- [environmental_traits.py](#environmental_traitspy) - Environmental adaptation traits
- [evolution.py](#evolutionpy) - Evolution and transformation system
- [genetics.py](#geneticspy) - Advanced genetics engine
- [history.py](#historypy) - Life event tracking
- [injury_tracker.py](#injury_trackerpy) - Injury and damage tracking
- [interactions.py](#interactionspy) - Social interaction tracking
- [pellet.py](#pelletpy) - Food/resource pellets
- [personality.py](#personalitypy) - Personality system
- [relationships.py](#relationshipspy) - Social bonds and relationships
- [skills.py](#skillspy) - Skill development system
- [spatial.py](#spatialpy) - 2D spatial components
- [stats.py](#statspy) - Statistics and modifiers
- [trait.py](#traitpy) - Trait model

---

## ability.py

### Classes

#### `AbilityType` (Enum)
Types of abilities available to creatures.
- `PHYSICAL`, `SPECIAL`, `STATUS`, `HEALING`, `BUFF`, `DEBUFF`

#### `TargetType` (Enum)
Target types for abilities.
- `SELF`, `ENEMY`, `ALLY`, `ALL_ENEMIES`, `ALL_ALLIES`, `ALL`

#### `AbilityEffect`
Represents an effect that an ability can apply (damage, heal, status, stat modification).

**Methods:**
- `to_dict()` - Serialize effect to dictionary
- `from_dict(data: Dict)` - Deserialize effect from dictionary
- `__repr__()` - String representation

#### `Ability`
Represents a skill or move that a creature can use in battle.

**Methods:**
- `__init__(name, description, ability_type, target_type, power=10, accuracy=100, cooldown=0, energy_cost=0, effects=None, conditions=None)` - Initialize ability
- `can_use(user_stats, user_energy=0)` - Check if ability can currently be used
- `use()` - Use the ability, triggering cooldown
- `tick_cooldown()` - Reduce cooldown by 1 turn
- `reset_cooldown()` - Reset cooldown to 0
- `calculate_damage(user_attack, target_defense)` - Calculate damage dealt
- `copy()` - Create a copy of this ability
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `__repr__()` - String representation

### Functions

- `create_ability(template_name: str)` - Create an ability from a predefined template

---

## attention.py

### Classes

#### `StimulusType` (Enum)
Types of stimuli that can capture agent attention.
- `COMBAT`, `FORAGING`, `FLEEING`, `EXPLORING`, `SOCIAL`, `HAZARD_AVOIDANCE`, `BUILDING`, `IDLE`

#### `StimulusPriority`
Priority configuration for different stimulus types with base priority, commitment time, and distraction threshold.

#### `AttentionManager`
Manages an agent's attention, focus, and stimulus prioritization.

**Methods:**
- `__init__(trait_modifiers=None)` - Initialize attention manager with trait-based modifiers
- `_apply_trait_modifiers(priorities)` - Apply trait modifiers to priority configurations
- `get_current_focus()` - Get the current focus/attention state
- `get_focus_duration(current_time)` - Get how long agent has been focused on current stimulus
- `is_committed(current_time)` - Check if agent is still committed to current focus
- `calculate_effective_priority(stimulus_type, urgency_modifier=1.0, context=None)` - Calculate effective priority for a stimulus
- `should_switch_focus(new_stimulus, new_priority, current_time)` - Determine if agent should switch focus
- `set_focus(new_focus, current_time, context=None)` - Set new focus for the agent
- `evaluate_and_update_focus(stimuli, current_time, force_reevaluate=False)` - Evaluate all stimuli and update focus
- `get_debug_info(current_time)` - Get debug information about attention state

### Functions

- `create_attention_manager_from_traits(traits: list)` - Create an attention manager configured based on creature traits

---

## behavior.py

### Classes

#### `BehaviorType` (Enum)
Types of behaviors creatures can exhibit.
- `AGGRESSIVE`, `DEFENSIVE`, `TERRITORIAL`, `CAUTIOUS`, `RECKLESS`, `SUPPORTIVE`, `WANDERER`, `HUNTER`, `FORAGER`, `BUILDING`

#### `SpatialBehavior`
Controls creature behavior in spatial combat.

**Methods:**
- `__init__(behavior_type=BehaviorType.AGGRESSIVE)` - Initialize behavior
- `get_target(entity, allies, enemies, hazards, resources)` - Determine which enemy to target
- `get_movement_target(entity, target_enemy, allies, enemies, hazards, resources)` - Determine where creature should move
- `should_use_ability(entity, target, ability_range)` - Determine if creature should use an ability

---

## combat_config.py

### Classes

#### `CombatConfig`
Configuration parameters for combat system with tunable targeting, memory, cooperation, and flee behaviors.

**Methods:**
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `create_aggressive_config()` - Create configuration for aggressive, fast-paced combat
- `create_tactical_config()` - Create configuration for tactical, positioning-focused combat
- `create_family_focused_config()` - Create configuration emphasizing family and strain loyalty

---

## combat_memory.py

### Classes

#### `CombatEncounter`
Records a single combat encounter between two creatures.

**Methods:**
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `CombatMemory`
Manages a creature's combat memory and targeting preferences.

**Methods:**
- `__init__(creature_id)` - Initialize combat memory
- `record_attacked_by(attacker_id, damage)` - Record being attacked
- `record_attacked(target_id, damage, killed=False)` - Record attacking another creature
- `record_killed_by(killer_id)` - Record being killed
- `record_fought_alongside(ally_id)` - Record fighting alongside another creature
- `_update_threat_level(creature_id, recent_damage)` - Update threat assessment
- `get_threat_level(creature_id)` - Get assessed threat level
- `get_most_threatening(candidate_ids)` - Get most threatening creature from a list
- `get_recent_attackers(max_age=10.0)` - Get creatures who attacked recently
- `should_prioritize_revenge(target_id)` - Check if should prioritize revenge
- `should_stick_with_target(target_id, min_duration=2.0)` - Check if should stick with current target
- `clear_recent_memory()` - Clear recent attacker memory
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

---

## combat_targeting.py

### Classes

#### `TargetingStrategy` (Enum)
Targeting strategies based on personality and context.
- `NEAREST`, `WEAKEST`, `STRONGEST`, `REVENGE`, `PROTECT_ALLIES`, `OPPORTUNISTIC`, `FAMILY_DEFENDER`, `STRAIN_LOYALIST`

#### `CombatContext`
Context information for combat decisions (allies, enemies, HP, etc.).

#### `TargetScore`
Score for a potential target with breakdown of scoring factors.

#### `CombatTargetingSystem`
Enhanced targeting system that considers multiple factors.

**Methods:**
- `select_target(attacker, potential_targets, context)` - Select the best target
- `_score_target(attacker, target, context)` - Calculate comprehensive score for a target
- `_calculate_relationship_score(attacker, target)` - Calculate score based on relationships
- `_calculate_opportunity_score(attacker, target, context)` - Calculate score based on opportunity
- `_calculate_personality_score(attacker, target, context)` - Calculate personality-based targeting modifier
- `should_flee(creature, context)` - Determine if creature should flee
- `get_flee_direction(creature, enemies)` - Calculate direction to flee from enemies

---

## creature.py

### Classes

#### `HazardMemory`
Tracks a creature's memory of a dangerous location.

#### `SocialMemory`
Tracks a creature's memory of interactions with another creature.

**Methods:**
- `get_familiarity()` - Get familiarity score (0-1)
- `get_trust()` - Get trust score (0-1)
- `get_threat(max_hp)` - Get threat score (0-1)

#### `CreatureType`
Defines a creature type/species with base stats and characteristics.

**Methods:**
- `__init__(name, description, base_stats=None, stat_growth=None, type_tags=None, evolution_stage=0, can_evolve=True)` - Initialize creature type
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `__repr__()` - String representation

#### `Creature`
Represents a creature in the EvoBattle game with full stats, abilities, traits, and systems.

**Methods:**
- `__init__(name, creature_type, level=1, experience=0, stats=None, traits=None, abilities=None, parent_ids=None, hue=None, strain_id=None)` - Initialize creature
- `get_effective_stats()` - Calculate effective stats with all modifiers
- `add_modifier(modifier)` - Add a stat modifier
- `remove_modifier(modifier_name)` - Remove a stat modifier by name
- `tick_modifiers()` - Update all modifiers and remove expired ones
- `add_ability(ability)` - Add an ability
- `remove_ability(ability_name)` - Remove an ability by name
- `get_ability(ability_name)` - Get an ability by name
- `gain_experience(amount)` - Gain experience points
- `level_up()` - Level up the creature
- `take_damage(damage)` - Take damage
- `heal(amount)` - Heal HP
- `is_alive()` - Check if creature is alive
- `update_hunger(delta_time)` - Update hunger system
- `eat(nutritional_value)` - Consume food
- `can_reproduce()` - Check if creature can reproduce
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `__repr__()` - String representation

---

## creature_beliefs.py

### Classes

#### `BeliefType` (Enum)
Types of beliefs creatures can form.
- `FOOD_LOCATION`, `DANGER_ZONE`, `SAFE_AREA`, `ALLY`, `THREAT`, `SHELTER`, `WATER_SOURCE`, `NESTING_SITE`, `BUILDING_LOCATION`, `MATERIAL_SOURCE`, `STRUCTURE_BENEFIT`, `CONSTRUCTION_SKILL`

#### `CreatureBelief`
Represents a single belief a creature holds about the world.

**Methods:**
- `__init__(belief_type, target, confidence=0.5)` - Create a new belief
- `reinforce(amount=0.1)` - Strengthen this belief
- `weaken(amount=0.1)` - Weaken this belief
- `decay(decay_rate=0.01)` - Natural decay over time
- `age()` - Get age of belief in seconds
- `__repr__()` - String representation

#### `CreatureBeliefSystem`
Manages all beliefs for a single creature.

**Methods:**
- `__init__(memory_capacity=20)` - Initialize belief system
- `add_belief(belief)` - Add a new belief or reinforce existing one
- `get_belief(target)` - Get belief about specific target
- `get_beliefs_by_type(belief_type)` - Get all beliefs of a specific type
- `get_strongest_belief(belief_type)` - Get the strongest belief of a type
- `remove_belief(target)` - Remove a specific belief
- `update(dt)` - Update all beliefs (apply decay)
- `clear_beliefs_of_type(belief_type)` - Remove all beliefs of a type
- `get_belief_count()` - Get total number of beliefs
- `get_average_confidence()` - Get average confidence across all beliefs
- `get_summary()` - Get summary statistics

---

## creature_brain.py

### Classes

#### `NeuralBrain`
Lightweight neural network for creature decision-making with social learning.

**Architecture:** 8 inputs → 3 hidden neurons → 6 outputs

**Methods:**
- `create_random()` - Create brain with random weights
- `create_default()` - Create brain with reasonable default weights
- `forward(inputs)` - Forward pass through network
- `decide_action(inputs)` - Make decision based on neural network output
- `decide_social_action(inputs)` - Decide on social action (COOPERATE or AVOID)
- `apply_reward(reward)` - Apply reinforcement learning update
- `copy_from(other, blend_factor=0.1)` - Copy weights from another brain
- `mutate(mutation_rate=0.1)` - Apply random mutations
- `inherit_from_parents(parent1, parent2)` - Inherit brain from parents
- `decay_learning_rate(age)` - Reduce learning rate as creature ages
- `to_dict()` - Serialize for saving
- `from_dict(data)` - Deserialize from saved data

---

## cross_entity_interactions.py

### Classes

#### `CrossEntityInteractions`
Manages interactions between creatures and pellets.

**Methods:**
- `calculate_pellet_preference(creature, pellet)` - Calculate how much a creature prefers a pellet
- `apply_consumption_effects(creature, pellet)` - Apply effects when creature consumes pellet
- `apply_pollination_effect(creature, pellet)` - Calculate pollination boost to pellet reproduction
- `calculate_symbiotic_benefit(creature, nearby_pellets, proximity_range=10.0)` - Calculate benefits from symbiotic relationships
- `check_pellet_avoidance(creature, pellet)` - Check if creature should avoid a pellet

#### `PelletCreatureInteraction`
Handles how pellets affect creatures that consume them.

**Methods:**
- `get_stat_modifiers(pellet)` - Get temporary stat modifiers from consuming a pellet

### Functions

- `find_best_pellet_for_creature(creature, available_pellets, max_distance=None)` - Find the best pellet for a creature to eat

---

## disease.py

### Classes

#### `DiseaseType` (Enum)
Types of diseases available.
- `PLAGUE`, `WASTING`, `PARASITE`, `BLIGHT`, `TOXIN_BLOOM`, `ROT`

#### `InfectionStage` (Enum)
Stages of infection progression.
- `INCUBATING`, `SYMPTOMATIC`, `RECOVERING`, `IMMUNE`

#### `Disease`
Defines the properties of a specific disease.

**Methods:**
- `mutate()` - Create a mutated version of this disease

#### `Infection`
Tracks the state of an active infection in an entity.

**Methods:**
- `update(delta_time)` - Update infection timer
- `get_total_duration(current_time)` - Get total time infected

### Constants

- `DISEASE_DEFINITIONS` - Dictionary of predefined disease definitions

---

## ecosystem_traits.py

Predefined metabolic and personality traits for the ecosystem survival system.

### Trait Constants

**Metabolic Traits:**
- `EFFICIENT_METABOLISM` - Burns energy slowly
- `GLUTTON` - Burns energy quickly but gains HP bonus when eating
- `FORAGER` - Better at finding resources
- `GATHERER` - Expert at collecting resources

**Personality Traits:**
- `LAZY` - Prefers to stay put
- `AGGRESSIVE` - Initiates attacks more often
- `WANDERER` - Constantly explores
- `FOCUSED` - Maintains concentration
- `DISTRACTIBLE` - Easily distracted
- `OPPORTUNISTIC` - Quick to seize opportunities

**Survival Traits:**
- `HARDY` - Resistant to environmental stress
- `FRAIL` - Weak constitution

**Dietary Traits:**
- `CARNIVORE` - Prefers meat
- `OMNIVORE` - Can eat both plants and meat
- `HERBIVORE` - Prefers plants

**Cognitive Traits:**
- `QUICK_LEARNER` - Learns from observation faster
- `SLOW_LEARNER` - Takes longer to learn
- `INNOVATIVE` - Develops unique behaviors
- `ANALYTICAL` - Better memory and decision quality
- `INSTINCTIVE` - Relies on instinct over learning

---

## environment.py

### Classes

#### `WeatherType` (Enum)
Types of weather conditions.
- `CLEAR`, `RAINY`, `STORMY`, `FOGGY`, `DROUGHT`

#### `TerrainType` (Enum)
Types of terrain.
- `GRASS`, `ROCKY`, `WATER`, `FOREST`, `DESERT`, `MARSH`

#### `TimeOfDay` (Enum)
Time of day phases.
- `DAWN`, `DAY`, `DUSK`, `NIGHT`

#### `HazardType` (Enum)
Types of environmental hazards.
- `FIRE`, `POISON_CLOUD`, `QUICKSAND`, `THORNS`, `ELECTRICAL`

#### `WeatherConditions`
Current weather conditions affecting the environment.

**Methods:**
- `get_movement_modifier()` - Calculate movement speed modifier
- `get_hunger_modifier()` - Calculate hunger depletion modifier
- `get_resource_quality_modifier()` - Calculate resource quality modifier

#### `TerrainCell`
Represents a cell in the terrain grid.

**Methods:**
- `get_movement_modifier()` - Get movement speed modifier for terrain
- `get_visibility_modifier()` - Get visibility modifier for terrain
- `get_cover_bonus()` - Get defensive cover bonus

#### `EnvironmentalHazard`
Represents a dangerous environmental feature.

**Methods:**
- `is_active()` - Check if hazard is still active
- `affects_position(position)` - Check if position is affected
- `get_damage_at_position(position)` - Calculate damage at position

#### `DayNightCycle`
Manages the day/night cycle.

**Methods:**
- `__init__(cycle_duration=300.0, start_hour=7.0)` - Initialize cycle
- `get_current_hour()` - Get current hour of day
- `get_time_of_day()` - Get current phase of day
- `get_visibility_modifier()` - Get visibility multiplier
- `get_activity_modifier()` - Get creature activity modifier

#### `Environment`
Manages all environmental systems.

**Methods:**
- `__init__(width, height, enable_weather=True, enable_terrain=True, enable_day_night=True, enable_hazards=True)` - Initialize environment
- `update(delta_time)` - Update all environmental systems
- `get_conditions_at(position)` - Get environmental conditions at position
- `spawn_hazard(hazard_type, position, radius, damage, duration)` - Spawn a new hazard
- `apply_environmental_effects(creature, position, delta_time)` - Apply environmental effects to creature

---

## environmental_traits.py

Environmental adaptation traits for creatures.

### Trait Categories

**Weather Adaptation:**
- `COLD_BLOODED`, `HEAT_RESISTANT`, `STORM_WALKER`, `FOG_ADAPTED`

**Terrain Adaptation:**
- `AQUATIC`, `FOREST_DWELLER`, `DESERT_ADAPTED`, `MARSH_NAVIGATOR`, `ALL_TERRAIN`

**Time Adaptation:**
- `NOCTURNAL`, `DIURNAL`, `CREPUSCULAR`, `TIRELESS`

**Hazard Resistance:**
- `FIRE_PROOF`, `POISON_RESISTANT`, `THICK_HIDE`, `HAZARD_SENSE`

**Awareness:**
- `WEATHER_SENSE`, `TRACKER`, `TERRAIN_READER`, `KEEN_FORAGER`

**Foraging:**
- `PICKY_EATER`, `OPPORTUNISTIC_FEEDER`, `FOOD_HOARDER`

**Tactical:**
- `SHELTER_SEEKER`, `EXPOSED_FIGHTER`, `BURROW_DWELLER`, `TERRAIN_TACTICIAN`

### Functions

- `get_environmental_trait_by_name(name)` - Get an environmental trait by name
- `get_random_environmental_trait()` - Get a random environmental trait
- `get_traits_for_terrain(terrain_type_name)` - Get beneficial traits for specific terrain
- `get_traits_for_weather(weather_type_name)` - Get beneficial traits for specific weather

---

## evolution.py

### Classes

#### `EvolutionPath`
Defines a possible evolution from one creature type to another.

**Methods:**
- `__post_init__()` - Initialize optional fields
- `can_evolve(creature)` - Check if creature meets evolution conditions
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `__repr__()` - String representation

#### `EvolutionSystem`
Manages creature evolution pathways and transformations.

**Methods:**
- `__init__()` - Initialize evolution system
- `register_creature_type(creature_type)` - Register a creature type
- `add_evolution_path(evolution_path)` - Add an evolution path
- `get_available_evolutions(creature)` - Get all evolution paths available to creature
- `can_evolve(creature)` - Check if creature can evolve
- `evolve(creature, evolution_path=None)` - Evolve a creature to its next form
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `__repr__()` - String representation

### Functions

- `create_example_evolution_system()` - Create an example evolution system with predefined types and paths

---

## genetics.py

### Classes

#### `GeneticsEngine`
Enhanced genetics engine for creature breeding with Mendelian genetics.

**Methods:**
- `__init__(mutation_rate=0.1)` - Initialize genetics engine
- `combine_traits(parent1, parent2, generation=0)` - Combine traits from both parents using genetics rules
- `_combine_same_trait(trait1, trait2, generation)` - Combine the same trait from both parents
- `_blend_trait_modifiers(trait1, trait2, blend_factor, generation)` - Blend numerical modifiers of two traits
- `_blend_values(val1, val2, blend_factor)` - Blend two numerical values
- `_blend_interaction_effects(effects1, effects2)` - Blend interaction effects from two traits
- `_blend_rarity(rarity1, rarity2)` - Blend rarity levels
- `_inherit_single_trait(trait, generation)` - Inherit a trait from only one parent
- `_mutate_trait(trait)` - Apply mutation to a trait
- `_modify_trait_nature(trait, generation)` - Modify the fundamental nature of a trait
- `_generate_mutation(generation)` - Generate a completely new trait through mutation
- `combine_stats(parent1, parent2)` - Combine stats from both parents

---

## history.py

### Classes

#### `EventType` (Enum)
Types of life events.
- `BIRTH`, `DEATH`, `BATTLE_START`, `BATTLE_END`, `BATTLE_WIN`, `BATTLE_LOSS`, `ATTACK`, `DAMAGE_TAKEN`, `KILL`, `KILLED_BY`, `OFFSPRING_BORN`, `FIRST_KILL`, `LEGENDARY_MOMENT`, `MILESTONE_REACHED`, `SKILL_MASTERED`, `TRAIT_GAINED`, `TRAIT_LOST`, `EVOLUTION`

#### `LifeEvent`
Represents a single significant event in a creature's life.

**Methods:**
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `KillRecord`
Records a kill made by this creature.

**Methods:**
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `Achievement`
Represents an achievement earned by a creature.

**Methods:**
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `CreatureHistory`
Comprehensive history tracking for a single creature.

**Methods:**
- `__init__(creature_id, creature_name)` - Initialize creature history
- `add_event(event)` - Add an event to history
- `record_battle_start(enemies, location=None)` - Record battle start
- `record_attack(target_id, damage, was_critical=False)` - Record an attack
- `record_damage_taken(attacker_id, damage)` - Record damage received
- `record_kill(victim_id, victim_name, power_differential=1.0, location=None, was_revenge=False)` - Record a kill
- `record_death(killer_id, cause, location=None)` - Record death
- `record_battle_victory()` - Record battle victory
- `record_offspring_born(offspring_id, offspring_name)` - Record offspring birth
- `get_kill_count()` - Get total kills
- `get_death_count()` - Get death count
- `get_most_killed_creature()` - Get creature killed most often
- `get_nemesis()` - Get creature who killed this one most
- `get_recent_events(count=10)` - Get recent events
- `get_events_by_type(event_type)` - Get all events of a type
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

---

## injury_tracker.py

### Classes

#### `DamageType` (Enum)
Types of damage.
- `PHYSICAL`, `SPECIAL`, `STARVATION`, `POISON`, `BURNING`, `ENVIRONMENTAL`

#### `InjuryRecord`
Records a single injury/damage event.

**Methods:**
- `health_percentage_before(max_hp)` - Get health percentage before damage
- `health_percentage_after(max_hp)` - Get health percentage after damage
- `was_near_death(max_hp, threshold=0.1)` - Check if injury brought creature near death
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `AttackerStats`
Statistics for damage received from a specific attacker.

**Methods:**
- `average_damage()` - Calculate average damage per hit
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `InjuryTracker`
Comprehensive injury tracking system for a creature.

**Methods:**
- `__init__(creature_id, max_hp)` - Initialize injury tracker
- `record_injury(attacker_id, attacker_name, damage_type, damage_amount, health_before, health_after, was_critical=False, location=None)` - Record a new injury
- `get_total_damage_received()` - Get total damage from all sources
- `get_damage_by_attacker(attacker_id)` - Get total damage from specific attacker
- `get_most_dangerous_attacker()` - Get attacker who dealt most damage
- `get_recent_injuries(count=10)` - Get most recent injuries
- `get_injuries_by_type(damage_type)` - Get all injuries of a specific type
- `get_critical_hits()` - Get all critical hits received
- `get_near_death_injuries()` - Get all injuries that brought creature near death
- `get_survival_rate()` - Calculate survival rate percentage
- `get_damage_breakdown()` - Get damage breakdown by type
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

---

## interactions.py

### Classes

#### `InteractionType` (Enum)
Types of social interactions.
- `FOOD_COMPETITION`, `MATING_ATTEMPT`, `MATING_SUCCESS`, `TERRITORIAL_DISPLAY`, `FLEE`, `CHASE`, `SOCIAL_OBSERVATION`, `ALLIANCE_FORMED`, `COOPERATION`

#### `InteractionRecord`
Records a single social interaction.

**Methods:**
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `FoodCompetitionRecord`
Records a food competition event.

**Methods:**
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `MatingRecord`
Records a mating event.

**Methods:**
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `PartnerStats`
Statistics for interactions with a specific partner.

**Methods:**
- `mating_success_rate()` - Calculate mating success rate
- `competition_win_rate()` - Calculate food competition win rate
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `InteractionTracker`
Comprehensive interaction tracking system for a creature.

**Methods:**
- `__init__(creature_id, creature_name)` - Initialize interaction tracker
- `record_interaction(interaction_type, target_id, target_name, success, location=None, context=None)` - Record a general interaction
- `record_food_competition(pellet_id, competitors, winner_id, location=None)` - Record food competition
- `record_mating_attempt(partner_id, partner_name, success, offspring_id=None, offspring_name=None, location=None)` - Record mating attempt
- `get_interaction_count(interaction_type=None)` - Get count of interactions
- `get_partner_stats(partner_id)` - Get statistics for a specific partner
- `get_most_frequent_partner()` - Get most frequently interacted partner
- `get_recent_interactions(count=10)` - Get recent interactions
- `get_interaction_summary()` - Get summary of all interactions
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

---

## pellet.py

### Classes

#### `PelletTraits`
Traits that define a pellet's characteristics.

**Methods:**
- `mutate(mutation_rate=0.1)` - Create a mutated copy of these traits
- `to_dict()` - Serialize to dictionary
- `from_dict(data)` - Deserialize from dictionary

#### `Pellet`
Represents a food pellet agent with traits and lifecycle.

**Methods:**
- `__post_init__()` - Initialize history
- `__hash__()` - Make Pellet hashable
- `__eq__(other)` - Compare Pellets by ID
- `tick(delta_time=1.0)` - Update pellet state
- `can_reproduce(local_pellet_count, carrying_capacity=100)` - Check if can reproduce
- `reproduce(mutation_rate=0.15, partner=None)` - Create offspring pellet
- `is_dead()` - Check if pellet has died of old age
- `get_nutritional_value()` - Calculate actual nutritional value
- `get_palatability_score()` - Get palatability score for creature selection
- `get_display_color()` - Get color for rendering
- `get_display_size()` - Get size for rendering
- `get_material_drop()` - Get building materials that drop when consumed
- `to_dict()` - Serialize to dictionary
- `from_dict(data)` - Deserialize from dictionary
- `__repr__()` - String representation

---

## personality.py

### Classes

#### `PersonalityProfile`
Defines a creature's personality traits (aggression, caution, curiosity, loyalty, independence, patience).

**Methods:**
- `__post_init__()` - Ensure all values are in valid range
- `random()` - Generate a random personality
- `inherit(parent1, parent2, mutation_rate=0.1)` - Create child personality by inheriting from parents
- `get_combat_style()` - Get description of combat style
- `should_retreat(hp_percent, enemy_count)` - Determine if should retreat
- `get_target_preference(enemies)` - Choose which enemy to target
- `get_exploration_tendency()` - Get how much creature likes to explore
- `get_team_fight_bonus(has_allies, has_family)` - Get combat bonus when fighting with allies
- `get_revenge_bonus(is_revenge)` - Get combat bonus for revenge fights
- `get_critical_hit_chance_modifier()` - Get modifier to critical hit chance
- `get_dodge_chance_modifier()` - Get modifier to dodge chance
- `get_description()` - Get human-readable personality description
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `__repr__()` - String representation

---

## relationships.py

### Classes

#### `RelationshipType` (Enum)
Types of relationships.
- `PARENT`, `CHILD`, `SIBLING`, `ALLY`, `FRIEND`, `RIVAL`, `RESPECT`, `FEAR`, `REVENGE_TARGET`

#### `RelationshipEvent`
Records an event in a relationship.

**Methods:**
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `Relationship`
Represents a relationship between two creatures.

**Methods:**
- `__init__(creature_id, target_id, relationship_type, strength=0.5, metrics=None)` - Initialize relationship
- `add_event(event_type, description)` - Add event to relationship history
- `record_cooperative_behavior(behavior_type)` - Record cooperative behavior
- `strengthen(amount=0.1)` - Strengthen the relationship
- `weaken(amount=0.1)` - Weaken the relationship
- `decay(elapsed_time)` - Decay relationship strength over time
- `get_combat_modifier(fighting_together)` - Get combat modifier based on relationship
- `get_description()` - Get human-readable description
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `RelationshipManager`
Manages all relationships for a creature.

**Methods:**
- `__init__(creature_id)` - Initialize relationship manager
- `add_relationship(target_id, relationship_type, strength=0.5)` - Add or update relationship
- `get_relationship(target_id)` - Get relationship with target
- `has_relationship(target_id, relationship_type=None)` - Check if relationship exists
- `strengthen_relationship(target_id, amount=0.1)` - Strengthen relationship
- `weaken_relationship(target_id, amount=0.1)` - Weaken relationship
- `get_all_relationships()` - Get all relationships
- `get_relationships_by_type(relationship_type)` - Get all relationships of a type
- `get_family_members()` - Get all family relationships
- `get_allies()` - Get all ally relationships
- `get_rivals()` - Get all rival relationships
- `get_revenge_targets()` - Get all revenge target relationships
- `update_decay()` - Update decay for all relationships
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

---

## skills.py

### Classes

#### `SkillType` (Enum)
Types of skills creatures can develop.
- `MELEE_ATTACK`, `RANGED_ATTACK`, `CRITICAL_STRIKE`, `DODGE`, `BLOCK`, `FORAGING`, `METABOLISM`, `STAMINA`, `LEADERSHIP`, `TEAMWORK`, `INTIMIDATION`

#### `Proficiency` (Enum)
Skill proficiency levels.
- `NOVICE`, `COMPETENT`, `EXPERT`, `MASTER`, `LEGENDARY`

#### `SkillConfig`
Configuration for a skill type.

#### `Skill`
Represents a single skill that a creature can develop.

**Methods:**
- `__init__(skill_type, config=None, level=0, experience=0.0)` - Initialize skill
- `_get_default_config(skill_type)` - Get default configuration
- `use(difficulty=1.0, success=True)` - Use the skill and gain experience
- `decay(elapsed_time)` - Decay skill from lack of use
- `_xp_required_for_level(level)` - Calculate XP required for level
- `get_proficiency()` - Get current proficiency level
- `get_performance_modifier()` - Get performance modifier based on skill level
- `get_success_chance_bonus()` - Get bonus to success chance
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `__repr__()` - String representation

#### `SkillManager`
Manages all skills for a creature.

**Methods:**
- `__init__()` - Initialize skill manager
- `get_skill(skill_type)` - Get a skill, creating if doesn't exist
- `use_skill(skill_type, difficulty=1.0, success=True)` - Use a skill and get performance modifier
- `update_decay()` - Update decay for all skills
- `get_all_skills()` - Get all skills
- `get_skill_level(skill_type)` - Get level of a specific skill
- `get_highest_skills(count=3)` - Get highest level skills
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

---

## spatial.py

### Classes

#### `Vector2D`
2D vector for position and velocity.

**Methods:**
- `__init__(x=0.0, y=0.0)` - Initialize vector
- `__repr__()`, `__add__()`, `__sub__()`, `__mul__()` - Operator overloads
- `__hash__()`, `__eq__()` - Hashable and comparable
- `magnitude()` - Calculate the length of the vector
- `normalized()` - Return a unit vector in the same direction
- `distance_to(other)` - Calculate distance to another vector
- `to_tuple()` - Convert to tuple

#### `SpatialEntity`
Represents an entity with position and movement in 2D space.

**Methods:**
- `__init__(position=None, radius=1.0, max_speed=1.0, acceleration=5.0, damping=0.85)` - Initialize entity
- `update(delta_time)` - Update position based on velocity
- `move_towards(target, speed=None, delta_time=0.016, stopping_distance=0.0)` - Set velocity to move towards target
- `stop()` - Stop all movement
- `distance_to(other)` - Calculate distance to another entity
- `is_colliding(other)` - Check if colliding with another entity
- `is_within_range(other, range_distance)` - Check if entity is within range
- `calculate_separation_force(other, strength=2.0)` - Calculate separation force vector
- `apply_separation_force(other, strength=2.0)` - Apply separation force to avoid collision

#### `Arena`
Represents a 2D battle arena with boundaries.

**Methods:**
- `__init__(width, height)` - Initialize arena
- `is_within_bounds(position)` - Check if position is within arena
- `clamp_to_bounds(position)` - Clamp position to arena boundaries
- `get_random_position()` - Get random position within arena
- `add_hazard(position)` - Add a hazard position
- `is_hazard(position)` - Check if position is a hazard
- `add_entity(entity)` - Add entity to spatial grid
- `remove_entity(entity)` - Remove entity from spatial grid
- `update_entity_position(entity)` - Update entity position in grid
- `get_nearby_entities(position, radius)` - Get entities within radius
- `add_resource(resource)` - Add resource to spatial grid
- `remove_resource(resource)` - Remove resource from grid
- `update_resource_position(resource)` - Update resource position
- `get_nearby_resources(position, radius)` - Get resources within radius

---

## stats.py

### Classes

#### `Stats`
Represents the core statistics of a creature.

**Methods:**
- `__post_init__()` - Ensure HP doesn't exceed max_hp
- `copy()` - Create a deep copy
- `apply_modifier(modifier)` - Apply a stat modifier
- `heal(amount)` - Heal the creature
- `take_damage(amount)` - Apply damage
- `is_alive()` - Check if creature is alive
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `__repr__()` - String representation

#### `StatModifier`
Represents a temporary or permanent modification to creature stats.

**Methods:**
- `is_expired()` - Check if modifier has expired
- `tick()` - Decrease duration by 1 turn
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `__repr__()` - String representation

#### `StatGrowth`
Manages stat growth over levels/generations.

**Methods:**
- `__init__(hp_growth=5.0, attack_growth=2.0, defense_growth=2.0, speed_growth=1.5, special_attack_growth=2.0, special_defense_growth=2.0, growth_curve="medium_fast")` - Initialize growth profile
- `calculate_stats_at_level(base_stats, level)` - Calculate stats at a specific level
- `_get_growth_multiplier(level)` - Get growth multiplier based on curve type
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `__repr__()` - String representation

---

## trait.py

### Classes

#### `TraitProvenance`
Tracks the origin and history of a trait.

**Methods:**
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary

#### `Trait`
Represents a genetic trait that can be inherited by fighters.

**Methods:**
- `__init__(name, description, trait_type, strength_modifier=1.0, defense_modifier=1.0, speed_modifier=1.0, rarity="common", dominance="codominant", provenance=None, interaction_effects=None, mutated=False)` - Initialize trait
- `to_dict()` - Serialize to dictionary
- `from_dict(data: Dict)` - Deserialize from dictionary
- `copy()` - Create a copy of this trait
- `base_name()` - Return canonical trait name without mutation markers
- `normalized_name()` - Return lower-cased canonical name for comparisons
- `mark_mutated(marker='+')` - Mark trait as mutated for display
- `is_mutated()` - Check if trait is marked as mutated
- `__repr__()` - String representation
- `__eq__(other)` - Equality based on canonical base name
- `__hash__()` - Hash consistent with __eq__

---

## Additional Files

### building/ subdirectory
Contains building-related models:
- `building_behavior.py` - Building behavior logic
- `building_config.py` - Building configuration
- `building_material.py` - Building material definitions

### Other Model Files
- `expanded_traits.py` - Extended trait definitions
- `pellet_history.py` - Pellet life history tracking
- `pheromone.py` - Pheromone system
- `relationship_metrics.py` - Relationship metrics and shared history
- `status_effect.py` - Status effect system
- `trait_analytics.py` - Trait analytics and tracking
- `trait_generator.py` - Trait generation utilities
- `weather_terrain_traits.py` - Weather and terrain-specific traits

---

## Summary

The `src/models` directory contains **35+ Python files** with comprehensive systems for:

- **Combat**: Abilities, targeting, memory, configuration
- **Creatures**: Stats, traits, genetics, evolution, skills, personality
- **Environment**: Weather, terrain, hazards, day/night cycles
- **Social Systems**: Relationships, interactions, beliefs, history
- **Resources**: Pellets with traits and evolution
- **Spatial**: 2D positioning, movement, collision detection
- **Tracking**: Injuries, events, achievements, interactions

Each system is designed to create emergent, complex behaviors through the interaction of multiple subsystems.
