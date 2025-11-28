"""
Spatial Real-Time Battle System - Handles real-time 2D combat.

Creatures move and fight in a 2D arena with positioning, proximity-based
targeting, and continuous time updates. Traits affect behavior, movement,
and combat decisions.

Enhanced with:
- Combat memory and threat assessment
- Relationship-aware targeting (allies, enemies, family, rivals)
- Personality-driven combat behaviors
- Configurable combat parameters
- Cooperative and vengeful tactics
- Environmental simulation (weather, terrain, day/night, hazards)
"""

from typing import List, Optional, Dict, Callable, Tuple, Any
from enum import Enum
import random
import time
import math

from ..models.creature import Creature
from ..models.skills import SkillType
from ..models.ability import Ability, AbilityType, TargetType
from ..models.status_effect import StatusEffect, StatusEffectType
from ..models.stats import StatModifier
from ..models.spatial import Vector2D, SpatialEntity, Arena
from ..utils.jit_math import distance_sq, calculate_separation_force_fast
from ..models.behavior import SpatialBehavior, BehaviorType
from ..models.pellet import Pellet, create_random_pellet, create_pellet_from_creature
from ..models.combat_config import CombatConfig
from ..models.combat_targeting import CombatTargetingSystem, CombatContext, TargetingStrategy
from ..models.relationships import RelationshipType
from ..models.injury_tracker import DamageType
from ..models.environment import Environment, EnvironmentalHazard, HazardType
from ..models.attention import AttentionManager, StimulusType, create_attention_manager_from_traits
from .breeding import Breeding
from .trait_effects_handler import TraitEffectsHandler
from .disease_system import DiseaseSystem
from src.systems.scientific_intervention import ScientificIntervention
from src.systems.research_ethics import ResearchEthicsSystem
from .reward_tracker import RewardTracker
from .neural_observational_learning import NeuralObservationalLearning
from .brain_statistics import BrainStatistics


from .battle_events import BattleEvent, BattleEventType
from .battle_managers.event_manager import EventManager
from .battle_managers.resource_manager import ResourceManager
from .battle_managers.environment_manager import EnvironmentManager
from .battle_managers.lifecycle_manager import LifecycleManager
from .battle_managers.combat_manager import CombatManager
from .battle_managers.movement_manager import MovementManager
from .battle_managers.neural_manager import NeuralManager
from .battle_managers.ai_manager import AIManager


class BattleCreature:
    """
    Wrapper for Creature with spatial properties and behavior.
    
    Combines creature stats/abilities with 2D positioning and AI behavior.
    """
    __slots__ = ['creature', 'spatial', 'attention', 'target', 'last_attack_time', 
                 'last_retarget_time', 'attack_cooldown', 'target_stopping_distance',
                 'current_movement_target', 'current_movement_entity', 'current_separation_force',
                 'id', 'behavior', 'ability_cooldowns', 'target_retention_distance', 
                 'min_retarget_time', 'last_behavior_state', 'combat_engaged', 'combat_engagement_range',
                 '_cached_allies_count', '_cached_enemies_count', '_cached_family_count',
                 'last_friendship_check', 'separation_update_counter', 'learning_events']

    def __init__(self, creature: Creature, position: Vector2D):
        self.creature = creature
        self.id = creature.creature_id  # Cache ID for faster access
        self.spatial = SpatialEntity(
            position=position,
            radius=0.6,  # Reduced from 1.0 for smaller collision size
            max_speed=creature.stats.speed / 4.0  # Increased from /10.0 to /4.0 for more dynamic combat (2.5x faster)
        )
        
        self.behavior = self._determine_behavior()
        self.target: Optional['BattleCreature'] = None
        self.ability_cooldowns: Dict[str, float] = {}
        self.last_attack_time: float = 0
        self.attack_cooldown: float = 0.5  # Reduced from 1.0 to 0.5 for more dynamic combat
        
        # Attention and focus management
        self.attention = create_attention_manager_from_traits(creature.traits)
        
        # Target retention to prevent rapid retargeting (now managed by attention system)
        self.target_retention_distance: float = 15.0  # Keep target if within this distance
        self.min_retarget_time: float = 0.5  # Minimum seconds before changing target
        self.last_retarget_time: float = 0.0
        
        # Movement state to prevent jitter
        self.current_movement_target: Optional[Vector2D] = None
        self.current_movement_entity: Optional[SpatialEntity] = None  # Track dynamic entity for smooth chasing
        self.target_stopping_distance: float = 0.0
        self.current_separation_force: Vector2D = Vector2D(0, 0)
        self.last_behavior_state: str = "combat"  # Track if seeking food vs combat (start in combat mode)
        
        # Combat engagement state to prevent circling
        self.combat_engaged: bool = False  # True when actively fighting a target
        self.combat_engagement_range: float = 6.0  # Distance to enter combat engagement
        
        # Cached counts for performance
        self._cached_allies_count = 0
        self._cached_enemies_count = 0
        self._cached_family_count = 0
        
        # Friendship check timer
        self.last_friendship_check: float = 0.0
        
        # Performance: Separation force update counter (update every N frames)
        self.separation_update_counter: int = 0
        
        # Neural learning: Track learning events for observational learning
        self.learning_events: int = 0
        
    def __eq__(self, other):
        """Compare BattleCreatures by their creature ID."""
        if other is None:
            return False
        try:
            return self.id == other.id
        except AttributeError:
            return False
            
    def __hash__(self):
        return hash(self.id)
    
    def _determine_behavior(self) -> SpatialBehavior:
        """Determine behavior based on creature traits."""
        # Check traits for behavior hints
        trait_names = [t.name.lower() for t in self.creature.traits]
        
        # Check for foraging/food-seeking traits first
        if any(word in ' '.join(trait_names) for word in ['forager', 'gatherer', 'scavenger']):
            return SpatialBehavior(BehaviorType.FORAGER)
        
        if any(word in ' '.join(trait_names) for word in ['aggressive', 'fierce', 'brutal']):
            return SpatialBehavior(BehaviorType.AGGRESSIVE)
        elif any(word in ' '.join(trait_names) for word in ['defensive', 'cautious', 'careful']):
            return SpatialBehavior(BehaviorType.CAUTIOUS)
        elif any(word in ' '.join(trait_names) for word in ['territorial', 'guardian']):
            behavior = SpatialBehavior(BehaviorType.TERRITORIAL)
            behavior.home_position = self.spatial.position
            return behavior
        elif any(word in ' '.join(trait_names) for word in ['reckless', 'wild', 'chaotic']):
            return SpatialBehavior(BehaviorType.RECKLESS)
        elif any(word in ' '.join(trait_names) for word in ['support', 'healer', 'protective']):
            return SpatialBehavior(BehaviorType.SUPPORTIVE)
        elif any(word in ' '.join(trait_names) for word in ['hunter', 'predator']):
            return SpatialBehavior(BehaviorType.HUNTER)
        elif any(word in ' '.join(trait_names) for word in ['wanderer', 'explorer', 'curious']):
            return SpatialBehavior(BehaviorType.WANDERER)
        else:
            # Default behavior based on stats
            if self.creature.stats.attack > self.creature.stats.defense:
                return SpatialBehavior(BehaviorType.AGGRESSIVE)
            else:
                return SpatialBehavior(BehaviorType.DEFENSIVE)
    
    def is_alive(self) -> bool:
        """Check if creature is still alive."""
        return self.creature.is_alive()
    
    def get_attention_debug_info(self, current_time: float) -> Dict[str, Any]:
        """
        Get debug information about creature's attention state.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            Dictionary with attention debug information
        """
        return self.attention.get_debug_info(current_time)
    
    def can_attack(self, current_time: float) -> bool:
        """Check if creature can attack based on cooldown."""
        return current_time - self.last_attack_time >= self.attack_cooldown


class SpatialBattle:
    """
    Manages real-time spatial combat in a 2D arena.
    
    Creatures move, target, and fight based on proximity and traits.
    Uses continuous time updates rather than turns.
    """

    # Set to True to enable internal debug _log entries that are for development only.
    # Default is False to silence debug noise in normal runs.
    DEBUG: bool = False

    # Type effectiveness chart (reused from turn-based system)
    TYPE_EFFECTIVENESS = {
        'fire': {'grass': 2.0, 'water': 0.5, 'ice': 2.0},
        'water': {'fire': 2.0, 'grass': 0.5, 'ground': 2.0},
        'grass': {'water': 2.0, 'fire': 0.5, 'ground': 2.0},
        'electric': {'water': 2.0, 'flying': 2.0, 'ground': 0.0},
        'ice': {'grass': 2.0, 'ground': 2.0, 'flying': 2.0, 'fire': 0.5},
        'fighting': {'normal': 2.0, 'ice': 2.0, 'flying': 0.5},
        'flying': {'fighting': 2.0, 'grass': 2.0, 'electric': 0.5},
        'psychic': {'fighting': 2.0, 'poison': 2.0},
        'dark': {'psychic': 2.0, 'fighting': 0.5},
        'steel': {'ice': 2.0, 'fairy': 2.0, 'fire': 0.5}
    }
    
    # Memory management: Max sizes for event/log lists to prevent unbounded growth
    MAX_EVENTS = 1000  # Keep last 1000 events
    MAX_BATTLE_LOG = 500  # Keep last 500 log messages
    
    def __init__(
        self,
        creatures_or_team1: List[Creature],
        team2_or_none: Optional[List[Creature]] = None,
        arena_width: float = 100.0,
        arena_height: float = 100.0,
        random_seed: Optional[int] = None,
        resource_spawn_rate: float = 0.1,  # Resources per second
        initial_resources: int = 5,
        living_world_enhancer: Optional['LivingWorldBattleEnhancer'] = None,
        combat_config: Optional[CombatConfig] = None,
        environment: Optional[Environment] = None,
        enable_environment: bool = False,
        biome_type: Optional[str] = None  # New parameter for biome generation
    ):
        """
        Initialize a new spatial battle.
        
        Args:
            creatures_or_team1: Either a list of all creatures (new API) or player team (old API)
            team2_or_none: Enemy team if using old API, None for new API
            arena_width: Width of the battle arena
            arena_height: Height of the battle arena
            random_seed: Optional seed for reproducible randomness
            resource_spawn_rate: Number of resources to spawn per second
            initial_resources: Number of resources to spawn at start
            living_world_enhancer: Optional living world enhancer for deep simulation features
            combat_config: Optional combat configuration (uses defaults if None)
            environment: Optional environment instance (creates default if None and enable_environment=True)
            enable_environment: Enable environmental simulation (weather, terrain, day/night)
            biome_type: Optional biome type ('grassland', 'desert', 'forest', 'marsh', 'rocky_highlands', 'mixed', 'random')
        """
        # Handle backward compatibility - detect old two-team API
        if team2_or_none is not None:
            # Old API: two teams passed separately
            all_creatures = creatures_or_team1 + team2_or_none
        else:
            # New API: single list of creatures
            all_creatures = creatures_or_team1
        
        # Core initialization
        self.arena = Arena(arena_width, arena_height)
        self.event_manager = EventManager()
        self.current_time: float = 0.0
        self.is_over: bool = False
        
        # Combat configuration
        self.combat_config = combat_config if combat_config else CombatConfig()
        
        # Environment Manager handles weather, terrain, hazards
        self.environment_manager = EnvironmentManager(
            event_manager=self.event_manager,
            width=arena_width,
            height=arena_height,
            enable_environment=enable_environment,
            environment=environment,
            biome_type=biome_type,
            random_seed=random_seed
        )
        self.environment = self.environment_manager.environment
        
        # Spatial hash grid for creature proximity queries
        from ..models.spatial import SpatialHashGrid
        # Increased cell size for better performance (fewer cells = faster queries)
        cell_size = max(5.0, min(20.0, min(arena_width, arena_height) * 0.15))
        self.creature_grid: SpatialHashGrid['BattleCreature'] = SpatialHashGrid(
            arena_width, arena_height, cell_size
        )
        
        # Living world enhancer for deep simulation
        self.enhancer = living_world_enhancer
        
        # Breeding system and population statistics
        self.breeding_system = Breeding(mutation_rate=0.1, trait_inheritance_chance=0.8)
        self.breeding_cooldown: float = 20.0  # Increased from 5.0 to 20.0 seconds for population control
        self.last_breeding_check: float = 0.0
        
        # Environmental hazards
        self.hazard_interval: float = 45.0  # Hazard every 45 seconds
        self.last_hazard_time: float = 0.0
        
        # Cooperative resource spawning
        self.cooperative_spawn_interval: float = 30.0  # Spawn cooperative resources every 30 seconds
        self.last_cooperative_spawn: float = 0.0
        
        # Performance optimization: Cache ally relationships
        # Key: (creature_id1, creature_id2), Value: is_ally bool
        self._ally_cache: Dict[Tuple[str, str], bool] = {}
        self._ally_cache_update_counter = 0
        
        # Performance optimization: Staggered AI updates
        # Only update a fraction of creatures' AI each frame
        self.ai_update_interval: int = 4  # Update AI every 4 frames
        self.frame_count: int = 0
        
        # Resource Manager handles pellets and grass growth
        self.resource_manager = ResourceManager(
            arena=self.arena,
            event_manager=self.event_manager,
            creature_grid=self.creature_grid,
            spawn_rate=resource_spawn_rate,
            initial_resources=initial_resources,
            enable_growth_system=True
        )
        # Lifecycle Manager handles birth, death, breeding
        self.lifecycle_manager = LifecycleManager(
            event_manager=self.event_manager,
            resource_manager=self.resource_manager,
            arena=self.arena,
            creature_grid=self.creature_grid,
            breeding_system=self.breeding_system,
            enhancer=self.enhancer if hasattr(self, 'enhancer') else None,
            reward_tracker=None # Will be set later
        )
        
        # Trait effects handler for applying interaction_effects
        self.trait_effects = TraitEffectsHandler()
        
        # Combat Manager handles attacks and damage
        self.combat_manager = CombatManager(
            event_manager=self.event_manager,
            combat_config=self.combat_config,
            trait_effects_handler=self.trait_effects,
            enhancer=self.enhancer if hasattr(self, 'enhancer') else None
        )
        
        # Movement Manager handles physics and positioning
        self.movement_manager = MovementManager(
            arena=self.arena,
            creature_grid=self.creature_grid,
            environment_manager=self.environment_manager
        )
        
        # Expose grass_growth for other systems that might need it (like terrain tracker)
        self.grass_growth = self.resource_manager.grass_growth
        
        # Terrain affinity tracker for ecosystem interactions
        from .terrain_affinity_tracker import TerrainAffinityTracker
        self.terrain_tracker = TerrainAffinityTracker()
        
        if random_seed is not None:
            random.seed(random_seed)
        
        # Spawn creatures distributed throughout the arena
        self._creatures = self.lifecycle_manager.spawn_population(all_creatures, BattleCreature)
        self.active_creatures = list(self._creatures)
        
        # Initialize Experiment Overseer System
        # Import here to avoid circular dependency
        from .experiment_overseer_system import ExperimentOverseer
        self.overseer = ExperimentOverseer(self)
        
        # Initialize Scientific Systems
        self.ethics_system = ResearchEthicsSystem()
        self.intervention_system = ScientificIntervention(self.ethics_system)
        
        # Initialize Disease System
        self.disease_system = DiseaseSystem()
        
        # Neural Manager handles brain updates and learning
        self.neural_manager = NeuralManager(
            event_manager=self.event_manager,
            combat_manager=self.combat_manager,
            resource_manager=self.resource_manager,
            lifecycle_manager=self.lifecycle_manager,
            movement_manager=self.movement_manager,
            arena=self.arena,
            combat_config=self.combat_config
        )
        
        # Expose components for backward compatibility/external access
        self.reward_tracker = self.neural_manager.reward_tracker
        self.neural_learning = self.neural_manager.neural_learning
        self.brain_stats = self.neural_manager.brain_stats
        self.last_brain_analysis = 0.0
        
        # AI Manager handles decision making
        self.ai_manager = AIManager(
            combat_manager=self.combat_manager,
            neural_manager=self.neural_manager,
            lifecycle_manager=self.lifecycle_manager,
            movement_manager=self.movement_manager,
            resource_manager=self.resource_manager,
            arena=self.arena,
            combat_config=self.combat_config
        )
        
        # Building Manager handles structures and materials
        from .battle_managers.building_manager import BuildingManager
        self.building_manager = BuildingManager(
            event_manager=self.event_manager,
            arena=self.arena
        )
        
        # Link Building Manager to AI Manager
        self.ai_manager.set_building_manager(self.building_manager)
        
        self._log(f"Battle started: {len(all_creatures)} creatures in {arena_width}x{arena_height} arena")
    
    @property
    def structures(self) -> List[Any]:
        """Get all structures in the arena."""
        return self.building_manager.buildings
    
    @property
    def buildings(self) -> List[Any]:
        """Get all buildings in the arena."""
        return self.building_manager.buildings
        
    @property
    def materials(self) -> List[Any]:
        """Get all building materials in the arena."""
        return self.building_manager.materials

    

    
    def add_event_callback(self, callback: Callable[[BattleEvent], None]):
        """Register a callback function for battle events."""
        self.event_manager.add_callback(callback)
    
    @property
    def creatures(self) -> List[BattleCreature]:
        """
        Get all creatures in the battle.
        
        Returns:
            List of all BattleCreatures in the population
        """
        return self._creatures
    
    @property
    def player_creatures(self) -> List[BattleCreature]:
        """
        Backward compatibility property for accessing creatures.
        Returns first half of creatures (simulating old "player team").
        
        This property exists for compatibility with old code but will be deprecated.
        Use the 'creatures' property instead.
        """
        # For backward compatibility, split the list in half
        mid = len(self._creatures) // 2
        return self._creatures[:mid] if mid > 0 else self._creatures
    
    @property
    def enemy_creatures(self) -> List[BattleCreature]:
        """
        Backward compatibility property for accessing creatures.
        Returns second half of creatures (simulating old "enemy team").
        
        This property exists for compatibility with old code but will be deprecated.
        Use the 'creatures' property instead.
        """
        # For backward compatibility, split the list in half
        mid = len(self._creatures) // 2
        return self._creatures[mid:] if mid > 0 else []
    
    def _emit_event(self, event: BattleEvent):
        """Emit a battle event to all registered callbacks."""
        self.event_manager.emit_event(event)
    
    def _log(self, message: str):
        """Add a message to the battle log."""
        self.event_manager.log(message)
        
    @property
    def events(self) -> List[BattleEvent]:
        """
        Backward compatibility property for accessing events.
        Delegates to event_manager.events.
        """
        return self.event_manager.events
    

    
    def update(self, delta_time: float):
        """
        Update battle state for one frame.
        
        Args:
            delta_time: Time elapsed since last update (seconds)
        """
        if self.is_over:
            return
        
        t0 = time.time()
        
        self.current_time += delta_time
        
        # Update environmental simulation
        self.environment_manager.update(delta_time)
        
        # Update Building System (Structures, Decay, Spawning)
        weather_type = "clear"
        if self.environment_manager.environment and self.environment_manager.environment.weather:
            weather_type = self.environment_manager.environment.weather.weather_type.value
        self.building_manager.update(delta_time, self.current_time, weather_type)
        
        # Update movement manager with current structures for collision detection
        self.movement_manager.set_buildings(self.building_manager.buildings)
            
        # Update Experiment Overseer
        if hasattr(self, 'overseer') and self.overseer:
            self.overseer.update(delta_time)
        
        # Update resource manager
        self.resource_manager.update(delta_time)
        
        # Update all creatures
        # Use active_creatures to avoid iterating over dead ones
        # Create a copy for iteration since creatures might die and be removed
        current_active_creatures = list(self.active_creatures)
        
        # Check if population has collapsed (all dead)
        if len(current_active_creatures) == 0:
            self._end_battle()
            return
        
        t1 = time.time()
        
        pellet_time = 0
        grid_time = 0
        tick_time = 0
        
        # Tick hunger and age for all alive creatures
        for creature in current_active_creatures:
            tt0 = time.time()
            # Apply environmental hunger modifier
            hunger_delta = delta_time
            if self.environment and self.environment.weather:
                hunger_delta *= self.environment.weather.get_hunger_modifier()
            
            creature.creature.tick_hunger(hunger_delta)
            creature.creature.tick_age(delta_time)
            
            # Update skill decay
            creature.creature.skills.update_decay()
            
            # Leadership Skill: Apply aura to nearby allies
            leadership_skill = creature.creature.skills.get_skill(SkillType.LEADERSHIP)
            if leadership_skill.level > 0:
                # Find allies within range (8.0 units)
                allies_buffed = 0
                creature_pos = creature.spatial.position
                
                # Optimization: Use spatial grid query if possible, but for now iterate active creatures
                # Since we are already inside the loop of active creatures, we need access to the full list
                # We can access self.creatures which is a dict, or self.creature_grid
                
                # Using spatial grid for efficiency
                nearby_entities = self.creature_grid.query_radius(creature_pos, 8.0)
                
                for entity in nearby_entities:
                    # Entity might be BattleCreature or just spatial entity depending on grid storage
                    # In this system, grid stores BattleCreature
                    if entity == creature:
                        continue
                        
                    if hasattr(entity, 'creature') and entity.creature.strain_id == creature.creature.strain_id:
                        # Apply Leadership Buff
                        # Buff strength based on skill level (1.0 to 2.0 multiplier)
                        buff_strength = 1.05 + (leadership_skill.get_performance_modifier() - 1.0) * 0.1
                        
                        # Create a temporary modifier
                        # Note: We need to be careful not to spam modifiers every tick.
                        # Check if already has "Leader's Inspiration"
                        has_buff = False
                        for mod in entity.creature.active_modifiers:
                            if mod.name == "Leader's Inspiration":
                                has_buff = True
                                mod.duration = 1.0 # Refresh duration
                                break
                        
                        if not has_buff:
                            from src.models.stats import StatModifier
                            modifier = StatModifier(
                                name="Leader's Inspiration",
                                duration=1.0, # Short duration, refreshed constantly
                                attack_multiplier=buff_strength,
                                defense_multiplier=buff_strength
                            )
                            entity.creature.add_modifier(modifier)
                            allies_buffed += 1
                
                # Gain Leadership XP if buffing allies (rate limited)
                if allies_buffed > 0 and random.random() < 0.05:
                    leadership_skill.use(difficulty=1.0, success=True)
            
            # Apply environmental hazard damage
            if self.environment:
                hazard_damage = self.environment.get_total_hazard_damage(creature.spatial.position)
                if hazard_damage > 0:
                    # Apply hazard damage with trait resistance
                    actual_damage = self.environment_manager.calculate_hazard_damage(creature, hazard_damage)
                    creature.creature.stats.hp = max(0, creature.creature.stats.hp - actual_damage)
                    if actual_damage > 0:
                        self._log(f"{creature.creature.name} takes {actual_damage:.1f} environmental damage!")
            
            # Check if creature starved - kill it if hunger depleted
            if creature.creature.hunger <= 0:
                self.lifecycle_manager.handle_death(creature, self.active_creatures, cause="starvation")
                continue
                
            # Check if died from hazard
            if not creature.is_alive():
                self.lifecycle_manager.handle_death(creature, self.active_creatures, cause="environmental hazard")
                continue
            tt1 = time.time()
            tick_time += (tt1 - tt0)
            
            # Attempt combat (every frame, not just during AI update)
            if creature.target and creature.target.is_alive() and creature.can_attack(self.current_time):
                died = self.combat_manager.attempt_attack(creature, creature.target, self.current_time, current_active_creatures)
                if died:
                    self.lifecycle_manager.handle_death(creature.target, self.active_creatures, killer=creature, cause="combat")
            
            # Note: Pellet collection moved to Loop 2 after movement
            # Note: Spatial grid update moved to Loop 2 after movement is applied
            tt3 = time.time()
            grid_time += (tt3 - tt1)  # Adjusted timing since we removed pellet check
        
        t2 = time.time()
        
        # Note: Pellet lifecycle and grass growth updated in resource_manager.update()
        
        # Update creature lifecycle (hunger, age, starvation)
        self.lifecycle_manager.update_lifecycle(current_active_creatures, delta_time, self.environment_manager)
        
        # Update disease system (outbreaks, transmission, progression)
        self.disease_system.update(
            delta_time=delta_time,
            current_time=self.current_time,
            creatures=current_active_creatures,
            resources=self.arena.resources,
            arena_width=self.arena.width,
            arena_height=self.arena.height
        )
        
        # Check for breeding opportunities (periodically)
        if self.current_time - self.last_breeding_check >= self.breeding_cooldown:
            self.lifecycle_manager.check_breeding(
                self.active_creatures,  # Pass main list so newborns are added correctly
                self.current_time,
                BattleCreature,
                self._creatures
            )
            self.last_breeding_check = self.current_time
        
        # Update each creature
        # Staggered AI updates: only update logic for a subset of creatures
        # But ALWAYS update physics/movement for smoothness
        self.frame_count += 1
        
        # Process a subset of creatures each frame to distribute load
        # INTELLIGENT creatures get updated every frame for faster reactions
        # Normal creatures use staggered batching (1/4th per frame)
        batch_size = max(1, len(current_active_creatures) // 4)
        start_idx = (int(self.current_time * 60) % 4) * batch_size
        end_idx = start_idx + batch_size
        
        ai_creatures = []
        for i, creature in enumerate(current_active_creatures):
            # Smart creatures (Intelligent trait) update every frame
            if creature.creature.has_trait("Intelligent"):
                ai_creatures.append(creature)
            # Normal creatures use staggered batching
            elif start_idx <= i < end_idx:
                ai_creatures.append(creature)
        
        ai_delta_time = delta_time * 4  # AI thinks in larger time steps
        
        # AI Logic Update Loop
        for creature in ai_creatures:
            if creature.is_alive():
                # Smart creatures use actual delta_time for more responsive thinking
                if creature.creature.has_trait("Intelligent"):
                    self.ai_manager.update_ai([creature], current_active_creatures, delta_time, self.current_time)
                else:
                    self.ai_manager.update_ai([creature], current_active_creatures, ai_delta_time, self.current_time)
        
        # Physics/Movement Update Loop (All creatures)
        self.movement_manager.update_movement(current_active_creatures, delta_time)
        
        # Check for nearby pellets to collect at NEW position (after movement)
        # Note: This was previously inside the loop, now we need to iterate again or move it to MovementManager?
        # MovementManager doesn't know about pellets/ResourceManager.
        # So we should iterate here or add a callback.
        # Iterating again is safer for now to keep managers decoupled.
        for creature in current_active_creatures:
             self.resource_manager.check_pellet_collection(creature, self.reward_tracker, self.enhancer, self.building_manager.materials)
        
        # Neural Observational Learning - Intelligent creatures copy successful behaviors
        self.neural_learning.update(current_active_creatures, self.reward_tracker)
        
        # Brain Statistics Analysis - Update every 2 seconds
        if self.current_time - self.last_brain_analysis >= 2.0:
            self.brain_stats.analyze_population(current_active_creatures)
            self.last_brain_analysis = self.current_time
        
        # Clear success flags for next frame
        self.reward_tracker.clear_success_flags()
        
        # Spawn cooperative group resources periodically
        if self.current_time - self.last_cooperative_spawn >= self.cooperative_spawn_interval:
            self.resource_manager.spawn_cooperative_resource()
            self.last_cooperative_spawn = self.current_time
        
        # Trigger environmental hazards periodically
        if self.current_time - self.last_hazard_time >= self.hazard_interval:
            self.environment_manager.trigger_hazard(
                current_active_creatures,
                self.arena,
                self.event_manager,
                self.current_time
            )
            self.last_hazard_time = self.current_time

    

    
    
    def _end_battle(self):
        """End the battle when population has collapsed."""
        self.is_over = True
        alive_creatures = [c for c in self._creatures if c.is_alive()]
        self.lifecycle_manager.check_battle_end(alive_creatures)
    
    def simulate(self, duration: float = 60.0, time_step: float = 0.1) -> Optional[str]:
        """
        Simulate the entire battle for a duration or until it ends.
        
        Args:
            duration: Maximum battle duration in seconds
            time_step: Time between updates (smaller = more accurate)
            
        Returns:
            None (no longer returns winner as there are no teams)
        """
        self._emit_event(BattleEvent(
            event_type=BattleEventType.BATTLE_START,
            message="Battle begins!",
            data={'duration': duration, 'time_step': time_step}
        ))
        
        elapsed = 0.0
        while elapsed < duration and not self.is_over:
            self.update(time_step)
            elapsed += time_step
        
        if not self.is_over:
            # Timeout - battle continues
            return None
        
        return None
    
    # === NEURAL NETWORK HELPER METHODS ===
    
    def _get_neural_inputs(self, creature: BattleCreature, all_alive: List[BattleCreature]):
        """Gather sensory inputs for neural network (5 inputs)."""
        return self.neural_manager.get_neural_inputs(creature, all_alive)
    
    def _execute_neural_action(self, creature: BattleCreature, action: str, all_alive: List[BattleCreature]):
        """Execute neural network decision."""
        self.neural_manager.execute_neural_action(creature, action, all_alive, self.current_time)
        

        

    
    def get_battle_log(self) -> List[str]:
        """Get the complete battle log."""
        return self.event_manager.get_battle_log()
    
    def get_state_snapshot(self) -> Dict:
        """Get current state snapshot for visualization."""


# Backwards compatibility alias
Battle = SpatialBattle
