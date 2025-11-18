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

from src.models.attention import StimulusType
from src.models.behavior import BehaviorType
from typing import List, Optional, Dict, Callable, Tuple, Any
from enum import Enum
from functools import lru_cache
import random
import time
import math

from ..models.creature import Creature
from ..models.ability import Ability, AbilityType, TargetType
from ..models.status_effect import StatusEffect, StatusEffectType
from ..models.stats import StatModifier
from ..models.spatial import Vector2D, SpatialEntity, Arena
from ..models.behavior import SpatialBehavior, BehaviorType
from ..models.pellet import Pellet, create_random_pellet, create_pellet_from_creature
from ..models.combat_config import CombatConfig
from ..models.combat_targeting import CombatTargetingSystem, CombatContext, TargetingStrategy
from ..models.relationships import RelationshipType
from ..models.injury_tracker import DamageType
from ..models.environment import Environment, EnvironmentalHazard, HazardType
from ..models.attention import AttentionManager, StimulusType, create_attention_manager_from_traits
from .breeding import Breeding
from .grass_growth_system import GrassGrowthSystem
from src.models.relationship_metrics import CooperativeBehaviorSystem, DecisionContext


class BattleEventType(Enum):
    """Types of battle events for animation/visualization."""
    BATTLE_START = "battle_start"
    CREATURE_SPAWN = "creature_spawn"
    CREATURE_MOVE = "creature_move"
    ABILITY_USE = "ability_use"
    DAMAGE_DEALT = "damage_dealt"
    HEALING = "healing"
    STATUS_APPLIED = "status_applied"
    MISS = "miss"
    CRITICAL_HIT = "critical_hit"
    SUPER_EFFECTIVE = "super_effective"
    NOT_EFFECTIVE = "not_effective"
    CREATURE_FAINT = "creature_faint"
    HAZARD_DAMAGE = "hazard_damage"
    RESOURCE_COLLECTED = "resource_collected"
    CREATURE_BIRTH = "creature_birth"
    CREATURE_DEATH = "creature_death"
    CREATURE_CONSUMED = "creature_consumed"
    BATTLE_END = "battle_end"
    # Pellet lifecycle events
    PELLET_SPAWN = "pellet_spawn"
    PELLET_REPRODUCE = "pellet_reproduce"
    PELLET_CONSUMED = "pellet_consumed"
    PELLET_DEATH = "pellet_death"
    # Attention/focus events
    ATTENTION_CHANGE = "attention_change"


class BattleEvent:
    """
    Represents a single event in battle for animation/visualization.
    """
    
    def __init__(
        self,
        event_type: BattleEventType,
        actor: Optional['BattleCreature'] = None,
        target: Optional['BattleCreature'] = None,
        ability: Optional[Ability] = None,
        value: Optional[int] = None,
        message: str = "",
        data: Optional[Dict] = None
    ):
        self.event_type = event_type
        self.actor = actor
        self.target = target
        self.ability = ability
        self.value = value
        self.message = message
        self.data = data or {}
        self.timestamp = time.time()
    
    def __repr__(self):
        return f"BattleEvent({self.event_type.value}: {self.message})"


class BattleCreature:
    """
    Wrapper for Creature with spatial properties and behavior.
    
    Combines creature stats/abilities with 2D positioning and AI behavior.
    """
    
    def __init__(
        self,
        creature: Creature,
        position: Vector2D
    ):
        self.creature = creature
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
        self.last_behavior_state: str = "combat"  # Track if seeking food vs combat (start in combat mode)
        
        # Combat engagement state to prevent circling
        self.combat_engaged: bool = False  # True when actively fighting a target
        self.combat_engagement_range: float = 6.0  # Distance to enter combat engagement
    
    def __hash__(self):
        """Make BattleCreature hashable based on creature ID."""
        return hash(self.creature.creature_id)
    
    def __eq__(self, other):
        """Compare BattleCreatures by their creature ID."""
        if not isinstance(other, BattleCreature):
            return False
        return self.creature.creature_id == other.creature.creature_id
    
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
        enable_environment: bool = False
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
        """
        # Handle backward compatibility - detect old two-team API
        if team2_or_none is not None:
            # Old API: two teams passed separately
            all_creatures = creatures_or_team1 + team2_or_none
        else:
            # New API: single list of creatures
            all_creatures = creatures_or_team1
        
        # Combat configuration
        self.combat_config = combat_config if combat_config else CombatConfig()
        
        # Environmental simulation
        if enable_environment or environment is not None:
            self.environment = environment if environment else Environment(
                width=arena_width,
                height=arena_height,
                enable_weather=True,
                enable_day_night=True
            )
        else:
            self.environment = None
        
        self.arena = Arena(arena_width, arena_height)
        self.battle_log: List[str] = []
        self.events: List[BattleEvent] = []
        self._event_callbacks: List[Callable[[BattleEvent], None]] = []
        self.current_time: float = 0.0
        self.is_over: bool = False
        self.resource_spawn_rate = resource_spawn_rate
        self.time_since_last_resource_spawn: float = 0.0
        
        # Spatial hash grid for creature proximity queries
        from ..models.spatial import SpatialHashGrid
        cell_size = max(5.0, min(20.0, min(arena_width, arena_height) * 0.1))
        self.creature_grid: SpatialHashGrid['BattleCreature'] = SpatialHashGrid(
            arena_width, arena_height, cell_size
        )
        
        # Living world enhancer for deep simulation
        self.enhancer = living_world_enhancer
        
        # Breeding system and population statistics
        self.breeding_system = Breeding(mutation_rate=0.1, trait_inheritance_chance=0.8)
        self.birth_count: int = 0
        self.death_count: int = 0
        self.breeding_cooldown: float = 20.0  # Increased from 5.0 to 20.0 seconds for population control
        self.last_breeding_check: float = 0.0
        
        # Environmental hazards and cooperative activities
        self.hazard_interval: float = 45.0  # Hazard every 45 seconds
        self.last_hazard_time: float = 0.0
        self.cooperative_spawn_interval: float = 30.0  # Spawn group resources every 30 seconds
        self.last_cooperative_spawn: float = 0.0
        
        # Performance optimization: Cache ally relationships
        # Key: (creature_id1, creature_id2), Value: is_ally bool
        self._ally_cache: Dict[Tuple[str, str], bool] = {}
        self._ally_cache_update_counter = 0
        
        # Grass growth enhancement system
        self.grass_growth = GrassGrowthSystem(
            arena_width=arena_width,
            arena_height=arena_height,
            enable_pollination=True,
            enable_nutrient_zones=True,
            enable_growth_pulses=True,
            enable_symbiotic_bonus=True
        )
        
        if random_seed is not None:
            random.seed(random_seed)
        
        # Spawn initial resources
        for _ in range(initial_resources):
            self._spawn_resource()
        
        # Spawn creatures distributed throughout the arena
        self._creatures = self._spawn_population(all_creatures)
        
        self._log(f"Battle started: {len(all_creatures)} creatures in {arena_width}x{arena_height} arena")
    
    def _spawn_population(
        self,
        creatures: List[Creature]
    ) -> List[BattleCreature]:
        """Spawn a population of creatures distributed throughout the arena."""
        spawned = []
        
        # Distribute creatures across the arena in a grid pattern
        num_creatures = len(creatures)
        grid_cols = max(2, int(math.sqrt(num_creatures * 2)))
        grid_rows = (num_creatures + grid_cols - 1) // grid_cols
        
        cell_width = self.arena.width / grid_cols
        cell_height = self.arena.height / grid_rows
        
        for i, creature in enumerate(creatures):
            # Calculate grid position
            col = i % grid_cols
            row = i // grid_cols
            
            # Add some randomness within the cell
            x = (col + 0.3 + random.random() * 0.4) * cell_width
            y = (row + 0.3 + random.random() * 0.4) * cell_height
            position = Vector2D(x, y)
            
            battle_creature = BattleCreature(creature, position)
            spawned.append(battle_creature)
            
            # Add to spatial grid
            self.creature_grid.insert(battle_creature, battle_creature.spatial.position)
            
            self._emit_event(BattleEvent(
                event_type=BattleEventType.CREATURE_SPAWN,
                actor=battle_creature,
                message=f"{creature.name} spawned at ({x:.1f}, {y:.1f})",
                data={'position': position.to_tuple()}
            ))
        
        return spawned
    
    def add_event_callback(self, callback: Callable[[BattleEvent], None]):
        """Register a callback function for battle events."""
        self._event_callbacks.append(callback)
    
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
        self.events.append(event)
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                self._log(f"Error in event callback: {e}")
    
    def _log(self, message: str):
        """Add a message to the battle log."""
        self.battle_log.append(message)
    
    def _spawn_resource(self):
        """Spawn a food pellet agent at a random location in the arena."""
        resource_pos = self.arena.get_random_position()
        # Create a Pellet agent instead of simple Vector2D
        pellet = create_random_pellet(x=resource_pos.x, y=resource_pos.y)
        
        # Apply environmental quality modifiers
        if self.environment:
            quality_modifier = self.environment.get_resource_quality_at(resource_pos)
            # Adjust nutritional value based on environment
            pellet.traits.nutritional_value *= quality_modifier
        
        self.arena.add_pellet(pellet)
    
    def update(self, delta_time: float):
        """
        Update battle state for one frame.
        
        Args:
            delta_time: Time elapsed since last update (seconds)
        """
        if self.is_over:
            return
        
        self.current_time += delta_time
        
        # Update environmental simulation
        if self.environment:
            self.environment.update(delta_time)
        
        # Spawn resources over time
        self.time_since_last_resource_spawn += delta_time
        if self.resource_spawn_rate > 0:
            spawn_interval = 1.0 / self.resource_spawn_rate
            while self.time_since_last_resource_spawn >= spawn_interval:
                self._spawn_resource()
                self.time_since_last_resource_spawn -= spawn_interval
        
        # Update all creatures
        alive_creatures = [c for c in self._creatures if c.is_alive()]
        
        # Check if population has collapsed (all dead or too few to continue)
        if len(alive_creatures) <= 1:
            self._end_battle()
            return
        
        # Tick hunger and age for all alive creatures
        for creature in alive_creatures:
            # Apply environmental hunger modifier
            hunger_delta = delta_time
            if self.environment and self.environment.weather:
                hunger_delta *= self.environment.weather.get_hunger_modifier()
            
            creature.creature.tick_hunger(hunger_delta)
            creature.creature.tick_age(delta_time)
            
            # Apply environmental hazard damage
            if self.environment:
                hazard_damage = self.environment.get_total_hazard_damage(creature.spatial.position)
                if hazard_damage > 0:
                    # Apply hazard damage with trait resistance
                    actual_damage = self._calculate_hazard_damage(creature, hazard_damage)
                    creature.creature.stats.hp = max(0, creature.creature.stats.hp - actual_damage)
                    if actual_damage > 0:
                        self._log(f"{creature.creature.name} takes {actual_damage:.1f} environmental damage!")
            
            # Check if creature starved - kill it if hunger depleted
            if creature.creature.hunger <= 0 and creature.is_alive():
                # Kill the creature by setting HP to 0
                creature.creature.stats.hp = 0
                self.death_count += 1
                self._log(f"{creature.creature.name} starved to death!")
                # Remove from spatial grid
                self.creature_grid.remove(creature)
                # Spawn pellets from starved creature
                self._spawn_pellets_from_creature(creature)
                self._emit_event(BattleEvent(
                    event_type=BattleEventType.CREATURE_DEATH,
                    target=creature,
                    message=f"{creature.creature.name} starved to death!"
                ))
        
        # Update pellet lifecycle (age, reproduce, die)
        self._update_pellets(delta_time)
        
        # Update grass growth system and emit events
        was_pulse_active = self.grass_growth.is_growth_pulse_active()
        self.grass_growth.update(delta_time)
        is_pulse_active = self.grass_growth.is_growth_pulse_active()
        
        # Emit event when growth pulse starts
        if not was_pulse_active and is_pulse_active:
            self._emit_event(BattleEvent(
                event_type=BattleEventType.PELLET_SPAWN,
                message="Growth pulse! Sunlight and rain boost grass growth!",
                data={'growth_pulse': True, 'multiplier': self.grass_growth.growth_pulse_multiplier}
            ))
        
        # Update each creature
        for creature in alive_creatures:
            if creature.is_alive():  # Re-check after hunger tick
                self._update_creature(creature, alive_creatures, delta_time)
        
        # Check for breeding opportunities (periodically)
        if self.current_time - self.last_breeding_check >= self.breeding_cooldown:
            self._check_breeding(alive_creatures)
            self.last_breeding_check = self.current_time
        
        # Trigger environmental hazards periodically
        if self.current_time - self.last_hazard_time >= self.hazard_interval:
            self._trigger_environmental_hazard(alive_creatures)
            self.last_hazard_time = self.current_time
        
        # Spawn cooperative group resources
        if self.current_time - self.last_cooperative_spawn >= self.cooperative_spawn_interval:
            self._spawn_cooperative_resource()
            self.last_cooperative_spawn = self.current_time
        
        # Process status effects
        for creature in alive_creatures:
            self._process_status_effects(creature)
    
    def _update_creature(
        self,
        creature: BattleCreature,
        all_alive: List[BattleCreature],
        delta_time: float
    ):
        """Update a single creature's AI, movement, and combat using attention system."""
        # Get other creatures as potential targets/allies
        other_creatures = [c for c in all_alive if c != creature]
        
        # Convert to spatial entities for behavior system
        other_entities = [c.spatial for c in other_creatures]
        
        # === ATTENTION SYSTEM: Evaluate all stimuli and determine focus ===
        
        # Calculate priority for each stimulus type
        stimuli_priorities = {}
        
        # 1. FORAGING - Priority based on hunger level
        if len(self.arena.resources) > 0:
            hunger_urgency = 1.0
            if creature.creature.hunger < 20:  # Critical hunger
                hunger_urgency = 3.0
            elif creature.creature.hunger < 35:  # High hunger
                hunger_urgency = 2.0
            elif creature.creature.hunger < 60:  # Moderate hunger
                hunger_urgency = 1.3
            else:  # Low hunger
                hunger_urgency = 0.5
            
            stimuli_priorities[StimulusType.FORAGING] = creature.attention.calculate_effective_priority(
                StimulusType.FORAGING,
                urgency_modifier=hunger_urgency
            )
        
        # 2. FLEEING - Priority based on health and threats
        hp_percent = creature.creature.stats.hp / max(1, creature.creature.stats.max_hp)
        nearby_enemies = self._get_enemies(creature, other_creatures, self.combat_config.close_combat_range * 2)
        nearby_allies = self._get_allies(creature, other_creatures, self.combat_config.support_range)
        
        if hp_percent < 0.3 or len(nearby_enemies) > len(nearby_allies) + 2:
            flee_urgency = 1.0
            if hp_percent < 0.15:  # Critical health
                flee_urgency = 3.0
            elif hp_percent < 0.25:  # Low health
                flee_urgency = 2.0
            
            # Increase urgency if outnumbered
            if len(nearby_enemies) > len(nearby_allies) + 2:
                flee_urgency *= 1.5
            
            stimuli_priorities[StimulusType.FLEEING] = creature.attention.calculate_effective_priority(
                StimulusType.FLEEING,
                urgency_modifier=flee_urgency
            )
        
        # 3. COMBAT - Priority based on nearby enemies and personality
        potential_targets = self.creature_grid.query_radius(
            creature.spatial.position,
            self.combat_config.max_chase_distance,
            exclude={creature}
        )
        
        # Filter out allies and self
        enemies = [t for t in potential_targets if t != creature and not self._is_ally(creature, t)]
        
        if enemies:
            combat_urgency = 1.0
            
            # Check for revenge targets
            has_revenge_target = False
            for enemy in enemies:
                if creature.creature.relationships.has_relationship(
                    enemy.creature.creature_id,
                    RelationshipType.REVENGE_TARGET
                ):
                    has_revenge_target = True
                    combat_urgency *= 1.5
                    break
            
            # Check for injured family nearby (protection instinct)
            for ally in nearby_allies:
                if creature.creature.relationships.has_relationship(
                    ally.creature.creature_id,
                    RelationshipType.PARENT
                ) or creature.creature.relationships.has_relationship(
                    ally.creature.creature_id,
                    RelationshipType.CHILD
                ):
                    ally_hp_percent = ally.creature.stats.hp / max(1, ally.creature.stats.max_hp)
                    if ally_hp_percent < 0.4:
                        combat_urgency *= 1.8
                        break
            
            stimuli_priorities[StimulusType.COMBAT] = creature.attention.calculate_effective_priority(
                StimulusType.COMBAT,
                urgency_modifier=combat_urgency
            )
        
        # 4. HAZARD AVOIDANCE - Priority based on environmental hazards
        if self.environment and self.environment.hazards:
            nearest_hazard_dist = float('inf')
            for hazard in self.environment.hazards:
                dist = creature.spatial.position.distance_to(hazard.position)
                if dist < nearest_hazard_dist:
                    nearest_hazard_dist = dist
            
            # High priority if close to hazard
            if nearest_hazard_dist < 10.0:
                hazard_urgency = max(1.0, (10.0 - nearest_hazard_dist) / 5.0)
                stimuli_priorities[StimulusType.HAZARD_AVOIDANCE] = creature.attention.calculate_effective_priority(
                    StimulusType.HAZARD_AVOIDANCE,
                    urgency_modifier=hazard_urgency
                )
        
        # 5. EXPLORING - Default low priority
        if not stimuli_priorities or all(p < 30 for p in stimuli_priorities.values()):
            stimuli_priorities[StimulusType.EXPLORING] = creature.attention.calculate_effective_priority(
                StimulusType.EXPLORING
            )
        
        # Track previous focus to detect changes
        previous_focus = creature.attention.get_current_focus()
        
        # Update focus based on stimulus evaluation
        current_focus = creature.attention.evaluate_and_update_focus(
            stimuli_priorities,
            self.current_time
        )
        
        # Emit event if focus changed
        if current_focus != previous_focus:
            debug_info = creature.attention.get_debug_info(self.current_time)
            self._emit_event(BattleEvent(
                event_type=BattleEventType.ATTENTION_CHANGE,
                actor=creature,
                message=f"{creature.creature.name} switched focus: {previous_focus.value} → {current_focus.value}",
                data={
                    'previous_focus': previous_focus.value,
                    'new_focus': current_focus.value,
                    'attention_debug': debug_info
                }
            ))
        
        # === ACT BASED ON CURRENT FOCUS ===
        movement_target = None
        
        if current_focus == StimulusType.FORAGING:
            # Override behavior to seek best available food
            # Filter resources by whether creature will eat them
            acceptable_resources = []
            for r in self.arena.resources:
                if isinstance(r, Pellet):
                    if creature.creature.can_eat_pellet(r.traits.toxicity, r.traits.palatability):
                        acceptable_resources.append(r)
                else:
                    acceptable_resources.append(r)  # Legacy resources always acceptable
            
            if acceptable_resources:
                # Choose best food by quality (prefer high palatability, low toxicity)
                def food_score(resource) -> float:
                    """Calculate food desirability score (higher = better)."""
                    distance = creature.spatial.position.distance_to(
                        self.arena.get_resource_position(resource)
                    )
                    if isinstance(resource, Pellet):
                        # Higher palatability and lower toxicity = better
                        quality = resource.traits.palatability - resource.traits.toxicity
                        # Balance quality with distance
                        return quality * 10.0 - distance * 0.5
                    else:
                        # Legacy resource - neutral quality
                        return 5.0 - distance * 0.5
                
                nearest_resource = max(acceptable_resources, key=food_score)
                movement_target = self.arena.get_resource_position(nearest_resource)
            else:
                # No acceptable food, seek any food in desperation
                if self.arena.resources:
                    nearest_resource = min(
                        self.arena.resources,
                        key=lambda r: creature.spatial.position.distance_to(self.arena.get_resource_position(r))
                    )
                    movement_target = self.arena.get_resource_position(nearest_resource)
        
        elif current_focus == StimulusType.FLEEING:
            # Flee from nearby threats
            if nearby_enemies:
                flee_dir = CombatTargetingSystem.get_flee_direction(creature, nearby_enemies)
                if flee_dir:
                    flee_distance = 20.0
                    movement_target = Vector2D(
                        creature.spatial.position.x + flee_dir[0] * flee_distance,
                        creature.spatial.position.y + flee_dir[1] * flee_distance
                    )
        
        elif current_focus == StimulusType.COMBAT:
            # Combat targeting - only retarget if not committed to current target
            should_retarget = False
            
            if not creature.target or not creature.target.is_alive():
                should_retarget = True
            elif not creature.attention.is_committed(self.current_time):
                # Not committed - can consider retargeting
                if self.current_time - creature.last_retarget_time >= self.combat_config.retarget_check_interval:
                    # Periodic retarget check
                    if creature.target:
                        current_distance = creature.spatial.distance_to(creature.target.spatial)
                        if current_distance > self.combat_config.max_chase_distance:
                            # Current target too far - must retarget
                            should_retarget = True
            
            if should_retarget:
                # Build combat context for targeting decisions
                hp_percent = creature.creature.stats.hp / max(1, creature.creature.stats.max_hp)
                
                # Find nearby allies and enemies
                nearby_allies_list = self._get_allies(creature, other_creatures, self.combat_config.support_range)
                nearby_enemies_list = self._get_enemies(creature, other_creatures, self.combat_config.support_range)
                
                # Check for injured allies
                has_injured_allies = any(
                    ally.creature.stats.hp / max(1, ally.creature.stats.max_hp) < self.combat_config.protect_ally_hp_threshold
                    for ally in nearby_allies_list
                )
                
                # Check for family nearby
                has_family_nearby = any(
                    creature.creature.relationships.has_relationship(
                        ally.creature.creature_id,
                        RelationshipType.PARENT
                    ) or creature.creature.relationships.has_relationship(
                        ally.creature.creature_id,
                        RelationshipType.CHILD
                    ) or creature.creature.relationships.has_relationship(
                        ally.creature.creature_id,
                        RelationshipType.SIBLING
                    )
                    for ally in nearby_allies_list
                )
                
                context = CombatContext(
                    nearby_allies=len(nearby_allies_list),
                    nearby_enemies=len(nearby_enemies_list),
                    self_hp_percent=hp_percent,
                    is_outnumbered=(len(nearby_enemies_list) > len(nearby_allies_list) + 1),
                    has_injured_allies=has_injured_allies,
                    has_family_nearby=has_family_nearby
                )
                
                # Use enhanced targeting system - get all potential targets within range
                potential_targets = self.creature_grid.query_radius(
                    creature.spatial.position,
                    self.combat_config.max_chase_distance,
                    exclude={creature}
                )

                # DEBUG: log what the spatial query returned
                try:
                    candidate_info = ", ".join(f"{t.creature.name}[id={id(t)}]" for t in potential_targets)
                except Exception:
                    candidate_info = str([id(t) for t in potential_targets])
                if self.DEBUG:
                    self._log(f"[debug:potential_targets] attacker={creature.creature.name}[id={id(creature)}] -> {candidate_info}")

                # If the query accidentally returned the attacker, log it explicitly
                for t in potential_targets:
                    if t == creature and self.DEBUG:
                        self._log(f"[debug:potential_targets:self_in_list] attacker returned in own query: {creature.creature.name} id={id(creature)}")

                # Filter out allies (don't target family or friends) and self
                filtered_targets = []
                for target in potential_targets:
                    # Safety check: Never include self
                    if target == creature:
                        continue  # Skip self
                    # Check if ally based on relationships
                    if self._is_ally(creature, target):
                        continue  # Skip allies
                    filtered_targets.append(target)

                # DEBUG: log filtered target list
                try:
                    filtered_info = ", ".join(f"{t.creature.name}[id={id(t)}]" for t in filtered_targets)
                except Exception:
                    filtered_info = str([id(t) for t in filtered_targets])
                if self.DEBUG:
                    self._log(f"[debug:filtered_targets] attacker={creature.creature.name}[id={id(creature)}] -> {filtered_info}")

                # Ensure selected_target is defined even if no filtered targets found
                selected_target = None

                # Select best target using new system
                if filtered_targets:
                    selected_target = CombatTargetingSystem.select_target(
                        creature,
                        filtered_targets,
                        context
                    )

                # DEBUG: log selected target (if any)
                try:
                    sel_name = selected_target.creature.name if selected_target else None
                    sel_id = id(selected_target) if selected_target else None
                except Exception:
                    sel_name = None
                    sel_id = None
                if self.DEBUG:
                    self._log(f"[debug:selected_target] attacker={creature.creature.name}[id={id(creature)}] selected={sel_name} id={sel_id}")

                # Determine new target (none if invalid or self)
                new_target = selected_target if (selected_target and selected_target != creature) else None

                # Only update if the target actually changed
                if creature.target is not new_target:
                    creature.target = new_target
                    creature.last_retarget_time = self.current_time

                # If we cleared the target, try relationship-driven fallbacks (3 → 2 → 1),
                # then finally fall back to attention-priorities / exploring.
                if creature.target is None:
                    try:
                        # Ensure attention exists
                        if not getattr(creature, "attention", None):
                            creature.attention = create_attention_manager_from_traits(
                                getattr(creature.creature, "traits", []) or []
                            )

                        # -----------------------------------------------------------------
                        # 3) Try: Join an ally's fight using CooperativeBehaviorSystem
                        # -----------------------------------------------------------------
                        from src.models.relationship_metrics import (
                            CooperativeBehaviorSystem,
                            DecisionContext,
                            AgentTraits,
                            AgentSocialState,
                            RelationshipMetrics
                        )

                        coop = CooperativeBehaviorSystem()
                        joined = False

                        for ally in nearby_allies_list:
                            # ally is a BattleCreature; check if they're actively fighting
                            if ally.target and ally.target.is_alive():
                                rel = creature.creature.relationships.get_relationship(ally.creature.creature_id)
                                metrics = rel.metrics if rel else RelationshipMetrics()

                                # Build minimal trait/state inputs (fall back to defaults if not present)
                                actor_traits = getattr(creature.creature, "social_traits", None) or AgentTraits()
                                target_traits = getattr(ally.creature, "social_traits", None) or AgentTraits()

                                actor_state = AgentSocialState(
                                    current_pack=[],
                                    current_alpha=None,
                                    hunger_level=max(0.0, min(1.0, getattr(creature.creature, "hunger", 1.0) / max(1, getattr(creature.creature, "max_hunger", 1)))),
                                    health_level=max(0.0, min(1.0, creature.creature.stats.hp / max(1, creature.creature.stats.max_hp))),
                                    in_combat=False,
                                    threatened=False
                                )
                                target_state = AgentSocialState(
                                    current_pack=[],
                                    current_alpha=None,
                                    hunger_level=max(0.0, min(1.0, getattr(ally.creature, "hunger", 1.0) / max(1, getattr(ally.creature, "max_hunger", 1)))),
                                    health_level=max(0.0, min(1.0, ally.creature.stats.hp / max(1, ally.creature.stats.max_hp))),
                                    in_combat=True,
                                    threatened=True
                                )

                                ctx = DecisionContext(
                                    actor_id=creature.creature.creature_id,
                                    target_id=ally.target.creature.creature_id,
                                    actor_traits=actor_traits,
                                    target_traits=target_traits,
                                    metrics=metrics,
                                    actor_state=actor_state,
                                    target_state=target_state
                                )

                                # threat_level heuristics could be refined; use 0.5 as neutral baseline
                                should_join, commitment = coop.evaluate_join_fight(ctx, threat_level=0.5)
                                if should_join:
                                    creature.attention.set_focus(StimulusType.COMBAT, self.current_time)
                                    creature.target = ally.target
                                    creature.last_retarget_time = self.current_time
                                    joined = True
                                    if rel:
                                        # record cooperative behavior for relationship metrics
                                        rel.record_cooperative_behavior("joined_fight")
                                    break

                        if joined:
                            # We set a target by joining an ally's fight — skip other fallbacks
                            pass
                        else:
                            # -----------------------------------------------------------------
                            # 2) Try: Protect injured family / close kin
                            # -----------------------------------------------------------------
                            protected = False
                            for ally in nearby_allies_list:
                                if not ally.is_alive():
                                    continue
                                rel = creature.creature.relationships.get_relationship(ally.creature.creature_id)
                                if not rel:
                                    continue
                                if rel.relationship_type in (
                                    RelationshipType.PARENT,
                                    RelationshipType.CHILD,
                                    RelationshipType.SIBLING
                                ):
                                    ally_hp_percent = ally.creature.stats.hp / max(1, ally.creature.stats.max_hp)
                                    # If family member is injured, prioritize defending them
                                    if ally_hp_percent < 0.5:
                                        # Prefer to target the ally's attacker if known
                                        if ally.target and ally.target.is_alive():
                                            creature.attention.set_focus(StimulusType.COMBAT, self.current_time)
                                            creature.target = ally.target
                                            creature.last_retarget_time = self.current_time
                                            protected = True
                                            break
                                        else:
                                            # Otherwise pick the nearest enemy in the local enemy list
                                            if nearby_enemies_list:
                                                # choose nearest enemy to the ally
                                                nearest_enemy = min(
                                                    nearby_enemies_list,
                                                    key=lambda e: ally.spatial.distance_to(e.spatial)
                                                )
                                                creature.attention.set_focus(StimulusType.COMBAT, self.current_time)
                                                creature.target = nearest_enemy
                                                creature.last_retarget_time = self.current_time
                                                protected = True
                                                break
                            if protected:
                                pass
                            else:
                                # -----------------------------------------------------------------
                                # 1) Try: Revenge priority (seek revenge targets)
                                # -----------------------------------------------------------------
                                revenge_found = False
                                # RelationshipManager convenience helpers may exist; do explicit check
                                for other in all_alive:
                                    if other == creature or not other.is_alive():
                                        continue
                                    if creature.creature.relationships.has_relationship(
                                        other.creature.creature_id,
                                        RelationshipType.REVENGE_TARGET
                                    ):
                                        creature.attention.set_focus(StimulusType.COMBAT, self.current_time)
                                        creature.target = other
                                        creature.last_retarget_time = self.current_time
                                        revenge_found = True
                                        break

                                if revenge_found:
                                    pass
                                else:
                                    # -----------------------------------------------------------------
                                    # Final fallback: use attention priorities (trait-modified) to pick a non-IDLE focus
                                    # -----------------------------------------------------------------
                                    current_focus = creature.attention.get_current_focus()
                                    if current_focus and current_focus != StimulusType.IDLE:
                                        creature.attention.set_focus(current_focus, self.current_time)
                                    else:
                                        priorities = getattr(creature.attention, "priorities", None)
                                        if priorities:
                                            # exclude IDLE when choosing best fallback
                                            non_idle = {k: v for k, v in priorities.items() if k != StimulusType.IDLE}
                                            if non_idle:
                                                best = max(non_idle.items(), key=lambda kv: kv[1].base_priority)[0]
                                            else:
                                                best = StimulusType.EXPLORING
                                            creature.attention.set_focus(best, self.current_time)
                                        else:
                                            # ultimate fallback to wandering behavior
                                            if not getattr(creature.behavior, "behavior_type", None):
                                                creature.behavior.behavior_type = BehaviorType.WANDERER
                                            creature.attention.set_focus(StimulusType.EXPLORING, self.current_time)
                    except Exception:
                        # Defensive: don't crash the battle loop if something's missing
                        pass

                # Trait-driven fallback (minimal)
                if not selected_target:
                    # Forager: go to nearest resource
                    if creature.creature.has_trait("Forager"):
                        nearest = self.arena.get_nearest_resource(creature.spatial.position)
                        if nearest:
                            resource, _dist = nearest
                            creature.target = None
                            creature.attention.set_focus(StimulusType.FORAGING, self.current_time)
                            movement_target = self.arena.get_resource_position(resource)

                    # Restful: rest in place (don't seek combat)
                    if creature.creature.has_trait("Restful"):
                        creature.target = None
                        creature.attention.set_focus(StimulusType.IDLE, self.current_time)
                        movement_target = creature.spatial.position

                    # Social: go towards nearest friendly
                    if creature.creature.has_trait("Social"):
                        ally = self._find_nearest_ally(creature)
                        if ally:
                            creature.target = None
                            creature.attention.set_focus(StimulusType.SOCIAL, self.current_time)
                            movement_target = ally.spatial.position

                    # Patroller / Playful fallback to exploring/wanderer behavior
                    if creature.creature.has_trait("Patroller") or creature.creature.has_trait("Playful"):
                        creature.attention.set_focus(StimulusType.EXPLORING, self.current_time)
                        creature.target = None
                        # let behavior.get_movement_target handle the rest

            # Move towards target
            if creature.target and creature.target.is_alive():
                movement_target = creature.target.spatial.position
        
        elif current_focus == StimulusType.HAZARD_AVOIDANCE:
            # Move away from nearest hazard
            if self.environment and self.environment.hazards:
                nearest_hazard = min(
                    self.environment.hazards,
                    key=lambda h: creature.spatial.position.distance_to(h.position)
                )
                away_vector = creature.spatial.position - nearest_hazard.position
                movement_target = creature.spatial.position + away_vector.normalized() * 15.0
        
        elif current_focus == StimulusType.EXPLORING:
            # Random exploration using behavior system
            resource_positions = [self.arena.get_resource_position(r) for r in self.arena.resources]
            movement_target = creature.behavior.get_movement_target(
                creature.spatial,
                None,  # No target in exploration mode
                [],
                other_entities,
                self.arena.hazards,
                resource_positions
            )
        
        else:  # IDLE or unknown
            # Use default behavior
            resource_positions = [self.arena.get_resource_position(r) for r in self.arena.resources]
            movement_target = creature.behavior.get_movement_target(
                creature.spatial,
                creature.target.spatial if creature.target else None,
                [],
                other_entities,
                self.arena.hazards,
                resource_positions
            )
        
        # Move towards target with smooth acceleration
        old_pos = (creature.spatial.position.x, creature.spatial.position.y)
        if movement_target:
            # Apply environmental movement modifiers
            movement_speed_modifier = 1.0
            if self.environment:
                movement_speed_modifier = self.environment.get_combined_movement_modifier(
                    creature.spatial.position
                )
                # Apply trait-based environmental adaptations
                movement_speed_modifier *= self._get_creature_environmental_adaptation(
                    creature, creature.spatial.position
                )
            
            # Temporarily adjust max speed for this movement
            original_max_speed = creature.spatial.max_speed
            creature.spatial.max_speed *= movement_speed_modifier
            
            # Determine stopping distance based on target type
            # When moving towards another creature (combat or fleeing), maintain distance to prevent overlap
            # When moving towards resources or wandering, allow getting very close
            stopping_distance = 0.0
            if creature.target and creature.target.is_alive():
                # Moving towards enemy - stop at sum of radii to prevent constant overlap/separation
                # Add small buffer for attack range
                stopping_distance = creature.spatial.radius + creature.target.spatial.radius + 0.5
            
            creature.spatial.move_towards(movement_target, delta_time=delta_time, stopping_distance=stopping_distance)
            
            # Check if creature is engaged in combat with target
            # Combat engagement reduces separation to allow melee attacks
            if creature.target and creature.target.is_alive():
                distance_to_target = creature.spatial.distance_to(creature.target.spatial)
                creature.combat_engaged = distance_to_target <= creature.combat_engagement_range
            else:
                creature.combat_engaged = False
            
            # Apply collision avoidance - check nearby creatures and apply separation forces
            # Use spatial grid for efficient proximity queries
            nearby_creatures = self.creature_grid.query_radius(
                creature.spatial.position,
                radius=2.5,  # Check creatures within 2.5 units
                exclude={creature}
            )
            
            # Apply separation force for each nearby creature
            # Reduce separation when combat engaged to allow attacks
            for nearby in nearby_creatures:
                if nearby.is_alive():
                    # If combat engaged with this specific target, greatly reduce separation
                    if creature.combat_engaged and nearby == creature.target:
                        # Minimal separation for combat target to allow attack
                        creature.spatial.apply_separation_force(nearby.spatial, strength=0.3)
                    else:
                        # Normal separation for other creatures
                        creature.spatial.apply_separation_force(nearby.spatial, strength=1.5)
                        
                        # Form friendships during peaceful proximity (not in combat with each other)
                        # Only process friendships occasionally to avoid overhead
                        if hasattr(creature, 'last_friendship_check'):
                            time_since_check = self.current_time - creature.last_friendship_check
                        else:
                            creature.last_friendship_check = 0
                            time_since_check = 999  # Force first check
                        
                        if time_since_check >= 2.0:  # Check every 2 seconds (increased frequency)
                            creature.last_friendship_check = self.current_time
                            # Don't form friendship if they're actively targeting each other
                            actively_fighting = (creature.target == nearby or nearby.target == creature)
                            if not actively_fighting and not self._is_ally(creature, nearby):
                                # Higher chance of forming friendship when near peacefully
                                if random.random() < 0.25:  # 25% chance per check (increased from 15%)
                                    creature.creature.relationships.record_positive_interaction(
                                        nearby.creature.creature_id,
                                        "peaceful_proximity"
                                    )
            
            # Apply boundary repulsion to prevent getting stuck on walls
            self.arena.apply_boundary_repulsion(creature.spatial, margin=3.0, strength=1.2)
            
            # Clamp velocity to max speed after all forces applied
            # This prevents separation/boundary forces from creating excessive velocity
            velocity_magnitude = creature.spatial.velocity.magnitude()
            if velocity_magnitude > creature.spatial.max_speed:
                creature.spatial.velocity = creature.spatial.velocity.normalized() * creature.spatial.max_speed
            
            # Restore original max speed
            if self.environment:
                creature.spatial.max_speed = original_max_speed
            
            creature.spatial.update(delta_time)
            
            # Keep within bounds
            creature.spatial.position = self.arena.clamp_position(creature.spatial.position)
            
            # Update spatial grid with new position
            self.creature_grid.update(creature, creature.spatial.position)
            
            new_pos = (creature.spatial.position.x, creature.spatial.position.y)
            if old_pos != new_pos:
                self._emit_event(BattleEvent(
                    event_type=BattleEventType.CREATURE_MOVE,
                    actor=creature,
                    message=f"{creature.creature.name} moved to ({new_pos[0]:.1f}, {new_pos[1]:.1f})",
                    data={'old_position': old_pos, 'new_position': new_pos}
                ))
        
        # Check for resource collection
        resources_to_remove = []
        for resource in self.arena.resources:
            # Get resource position (works for both Vector2D and Pellet)
            resource_pos = self.arena.get_resource_position(resource)
            distance = creature.spatial.position.distance_to(resource_pos)
            
            # Try pollination when creature is near pellet (before eating)
            if isinstance(resource, Pellet) and distance < 5.0:
                pollinated_pellet = self.grass_growth.try_pollination(
                    creature, resource, self.current_time
                )
                if pollinated_pellet:
                    # Add the new pollinated pellet to arena
                    self.arena.add_pellet(pollinated_pellet)
                    self._emit_event(BattleEvent(
                        event_type=BattleEventType.PELLET_SPAWN,
                        actor=creature,
                        message=f"{creature.creature.name} pollinated grass! Seeds spread.",
                        data={'pollination': True, 'position': (pollinated_pellet.x, pollinated_pellet.y)}
                    ))
            
            if distance < 2.0:  # Collection range
                # Check if creature can eat plant resources (herbivore or omnivore)
                if creature.creature.can_eat_food_type("plant"):
                    # Get nutritional value and quality (Pellet or default)
                    if isinstance(resource, Pellet):
                        # Check if creature will eat this pellet based on quality
                        if not creature.creature.can_eat_pellet(
                            resource.traits.toxicity,
                            resource.traits.palatability
                        ):
                            continue  # Skip this pellet, try next one
                        
                        food_value = int(resource.get_nutritional_value())
                        toxicity = resource.traits.toxicity
                        palatability = resource.traits.palatability
                    else:
                        # Legacy Vector2D resources
                        food_value = 40
                        toxicity = 0.0
                        palatability = 0.5
                    
                    # Eat the resource with quality parameters
                    hunger_restored = creature.creature.eat(
                        food_value,
                        food_type="plant",
                        toxicity=toxicity,
                        palatability=palatability
                    )
                    if hunger_restored > 0:
                        resources_to_remove.append(resource)
                        
                        # Build message with quality info
                        quality_msg = ""
                        if isinstance(resource, Pellet):
                            if toxicity > 0.3:
                                quality_msg = " (toxic!)"
                            elif palatability < 0.4:
                                quality_msg = " (unpalatable)"
                            elif palatability > 0.7:
                                quality_msg = " (tasty!)"
                        
                        self._log(f"{creature.creature.name} ate food{quality_msg} and restored {hunger_restored} hunger!")
                        self._emit_event(BattleEvent(
                            event_type=BattleEventType.RESOURCE_COLLECTED,
                            actor=creature,
                            message=f"{creature.creature.name} ate food{quality_msg}! Hunger: {creature.creature.hunger}/{creature.creature.max_hunger}",
                            data={
                                'resource_position': resource_pos.to_tuple(),
                                'hunger_restored': hunger_restored,
                                'current_hunger': creature.creature.hunger,
                                'toxicity': toxicity,
                                'palatability': palatability
                            }
                        ))
                        break  # Only collect one resource per update
        
        # Remove collected resources
        for resource in resources_to_remove:
            self.arena.resources.remove(resource)
        
        # Attempt combat
        if creature.target and creature.can_attack(self.current_time):
            self._attempt_attack(creature, creature.target)
    
    def _is_ally(self, creature: BattleCreature, other: BattleCreature) -> bool:
        """
        Determine if two creatures are allies (cached for performance).
        
        Allies include:
        - Family members (parent, child, sibling)
        - Explicit ally relationships
        - Friends
        - Same strain (if config enables strain cooperation)
        
        Args:
            creature: First creature
            other: Second creature
            
        Returns:
            True if they are allies
        """
        # Use cache for performance (relationships don't change during battle)
        cache_key = (creature.creature.creature_id, other.creature.creature_id)
        
        if cache_key in self._ally_cache:
            return self._ally_cache[cache_key]
        
        # Check family relationships
        if creature.creature.relationships.has_relationship(
            other.creature.creature_id,
            RelationshipType.PARENT
        ):
            self._ally_cache[cache_key] = True
            return True
        
        if creature.creature.relationships.has_relationship(
            other.creature.creature_id,
            RelationshipType.CHILD
        ):
            self._ally_cache[cache_key] = True
            return True
        
        if creature.creature.relationships.has_relationship(
            other.creature.creature_id,
            RelationshipType.SIBLING
        ):
            self._ally_cache[cache_key] = True
            return True
        
        # Check explicit ally relationship
        if creature.creature.relationships.has_relationship(
            other.creature.creature_id,
            RelationshipType.ALLY
        ):
            self._ally_cache[cache_key] = True
            return True
        
        # Check friend relationship
        if creature.creature.relationships.has_relationship(
            other.creature.creature_id,
            RelationshipType.FRIEND
        ):
            self._ally_cache[cache_key] = True
            return True
        
        # Check strain cooperation (if enabled)
        if self.combat_config.same_strain_avoid_combat:
            if creature.creature.strain_id == other.creature.strain_id:
                self._ally_cache[cache_key] = True
                return True
        
        self._ally_cache[cache_key] = False
        return False
    
    def _get_allies(
        self,
        creature: BattleCreature,
        all_creatures: List[BattleCreature],
        max_distance: float
    ) -> List[BattleCreature]:
        """
        Get all allies within range.
        
        Args:
            creature: The creature to find allies for
            all_creatures: All creatures to check
            max_distance: Maximum distance to consider
            
        Returns:
            List of allied creatures within range
        """
        allies = []
        
        for other in all_creatures:
            if other == creature:
                continue
            
            if not other.is_alive():
                continue
            
            # Check if ally
            if self._is_ally(creature, other):
                # Check distance
                distance = creature.spatial.distance_to(other.spatial)
                if distance <= max_distance:
                    allies.append(other)
        
        return allies
    
    def _get_enemies(
        self,
        creature: BattleCreature,
        all_creatures: List[BattleCreature],
        max_distance: float
    ) -> List[BattleCreature]:
        """
        Get all enemies within range.
        
        Args:
            creature: The creature to find enemies for
            all_creatures: All creatures to check
            max_distance: Maximum distance to consider
            
        Returns:
            List of enemy creatures within range
        """
        enemies = []
        
        for other in all_creatures:
            if other == creature:
                continue
            
            if not other.is_alive():
                continue
            
            # Not an ally = enemy
            if not self._is_ally(creature, other):
                # Check distance
                distance = creature.spatial.distance_to(other.spatial)
                if distance <= max_distance:
                    enemies.append(other)
        
        return enemies

    # Add this helper to the SpatialBattle class (near other helpers like _get_allies/_get_enemies)
    def _find_nearest_ally(self, creature: BattleCreature, max_distance: float = 50.0) -> Optional[BattleCreature]:
        """
        Return the nearest allied BattleCreature within max_distance, or None.
        Minimal helper used by trait-driven fallback.
        """
        allies = self._get_allies(creature, self._creatures, max_distance)
        if not allies:
            return None
        return min(allies, key=lambda a: creature.spatial.distance_to(a.spatial))
    
    def _attempt_attack(self, attacker: BattleCreature, defender: BattleCreature):
        """Attempt an attack from attacker to defender."""
        # Safety check: Never attack self
        if attacker == defender:
            return
        
        # Choose ability
        usable_abilities = [
            a for a in attacker.creature.abilities
            if a is not None and a.can_use(attacker.creature.stats, attacker.creature.energy)
        ]
        
        if usable_abilities:
            ability = max(usable_abilities, key=lambda a: a.power)
        else:
            # Basic attack
            ability = Ability(name="Basic Attack", power=10, accuracy=100)
        
        # Check range - use config values with improved defaults
        # Attack ranges should be larger than separation force threshold (2.5) to allow attacks
        attack_range = self.combat_config.base_attack_range_melee  # Default 3.0
        if ability.ability_type == AbilityType.PHYSICAL:
            attack_range = self.combat_config.base_attack_range_melee  # 3.0 - melee range
        elif ability.ability_type == AbilityType.SPECIAL:
            attack_range = self.combat_config.base_attack_range_ranged  # 8.0 - ranged attack
        
        distance = attacker.spatial.distance_to(defender.spatial)
        
        if distance > attack_range:
            return  # Too far to attack
        
        # Execute attack
        self._execute_ability(attacker, defender, ability)
        attacker.last_attack_time = self.current_time
    
    def _execute_ability(
        self,
        attacker: BattleCreature,
        defender: BattleCreature,
        ability: Ability
    ):
        """Execute an ability from attacker to defender (reuses turn-based damage logic)."""
        self._log(f"{attacker.creature.name} uses {ability.name}!")
        self._emit_event(BattleEvent(
            event_type=BattleEventType.ABILITY_USE,
            actor=attacker,
            target=defender,
            ability=ability,
            message=f"{attacker.creature.name} uses {ability.name}!",
            data={'distance': attacker.spatial.distance_to(defender.spatial)}
        ))
        
        # Use ability
        ability.use()
        attacker.creature.energy = max(0, attacker.creature.energy - ability.energy_cost)
        
        # Check accuracy with dodge modifier
        hit = self._check_accuracy(ability.accuracy)
        
        # Apply living world dodge chance
        if hit and self.enhancer:
            dodge_chance = self.enhancer.calculate_dodge_chance_modifier(defender.creature)
            # Convert percentage to probability (0-100 -> 0.0-1.0)
            if random.random() < (dodge_chance / 100.0):
                hit = False
        
        if not hit:
            self._log(f"{ability.name} missed!")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.MISS,
                actor=attacker,
                target=defender,
                ability=ability,
                message=f"{ability.name} missed!"
            ))
            # Record miss for living world
            if self.enhancer:
                self.enhancer.on_attack_made(
                    attacker.creature,
                    defender.creature,
                    damage=0,
                    was_critical=False,
                    hit=False
                )
            return
        
        # Apply damage or effects
        if ability.ability_type in [AbilityType.PHYSICAL, AbilityType.SPECIAL]:
            damage, was_critical = self._calculate_damage(attacker.creature, defender.creature, ability)
            
            # Apply relationship-based damage modifiers
            damage = self._apply_relationship_damage_modifier(attacker, defender, damage)
            
            was_alive_before_damage = defender.is_alive()
            health_before = defender.creature.stats.hp
            actual_damage = defender.creature.stats.take_damage(damage)
            health_after = defender.creature.stats.hp
            self._log(f"{defender.creature.name} takes {actual_damage} damage! (HP: {defender.creature.stats.hp}/{defender.creature.stats.max_hp})")
            
            # Record injury for inspector stats
            damage_type = DamageType.PHYSICAL if ability.ability_type == AbilityType.PHYSICAL else DamageType.SPECIAL
            defender.creature.injury_tracker.record_injury(
                attacker_id=attacker.creature.creature_id,
                attacker_name=attacker.creature.name,
                damage_type=damage_type,
                damage_amount=actual_damage,
                health_before=health_before,
                health_after=health_after,
                was_critical=was_critical,
                location=(defender.spatial.position.x, defender.spatial.position.y)
            )
            
            # Record combat memory for both creatures
            attacker.creature.combat_memory.record_attacked(
                defender.creature.creature_id,
                actual_damage,
                killed=(was_alive_before_damage and not defender.is_alive())
            )
            defender.creature.combat_memory.record_attacked_by(
                attacker.creature.creature_id,
                actual_damage
            )
            
            # Record attack for living world
            if self.enhancer:
                self.enhancer.on_attack_made(
                    attacker.creature,
                    defender.creature,
                    actual_damage,
                    was_critical,
                    hit=True
                )
            
            self._emit_event(BattleEvent(
                event_type=BattleEventType.DAMAGE_DEALT,
                actor=attacker,
                target=defender,
                ability=ability,
                value=actual_damage,
                message=f"{defender.creature.name} takes {actual_damage} damage!",
                data={'remaining_hp': defender.creature.stats.hp, 'max_hp': defender.creature.stats.max_hp}
            ))
            
            # Only count death if creature was alive before this attack
            if was_alive_before_damage and not defender.is_alive():
                self.death_count += 1
                
                # Record kill in combat memory
                defender.creature.combat_memory.record_killed_by(attacker.creature.creature_id)
                
                # Update relationships - family members seek revenge
                self._handle_revenge_relationships(attacker, defender)
                
                # Remove from spatial grid
                self.creature_grid.remove(defender)
                
                # Record kill for living world
                if self.enhancer:
                    location = (defender.spatial.position.x, defender.spatial.position.y)
                    self.enhancer.on_creature_killed(
                        attacker.creature,
                        defender.creature,
                        location
                    )
                
                self._emit_event(BattleEvent(
                    event_type=BattleEventType.CREATURE_DEATH,
                    target=defender,
                    message=f"{defender.creature.name} was defeated!"
                ))
                
                # Spawn pellets from defeated creature (unless consumed)
                self._spawn_pellets_from_creature(defender, count=2)
                
                # Allow nearby carnivores/omnivores to consume the corpse
                self._handle_corpse_consumption(defender, attacker)
        
        elif ability.ability_type == AbilityType.HEALING:
            heal_amount = ability.power
            actual_heal = attacker.creature.stats.heal(heal_amount)
            self._log(f"{attacker.creature.name} heals {actual_heal} HP!")
            
            self._emit_event(BattleEvent(
                event_type=BattleEventType.HEALING,
                actor=attacker,
                value=actual_heal,
                message=f"{attacker.creature.name} heals {actual_heal} HP!"
            ))
    
    def _calculate_damage(
        self,
        attacker: Creature,
        defender: Creature,
        ability: Ability
    ) -> Tuple[int, bool]:
        """
        Calculate damage (reuses turn-based formula).
        
        Returns:
            Tuple of (damage, was_critical)
        """
        base_damage = ability.calculate_damage(
            attacker.stats.attack,
            defender.stats.defense
        )
        
        # Type effectiveness
        effectiveness = self._get_type_effectiveness(attacker, defender)
        damage = int(base_damage * effectiveness)
        
        if effectiveness > 1.0:
            self._log("It's super effective!")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.SUPER_EFFECTIVE,
                message="It's super effective!",
                data={'effectiveness': effectiveness}
            ))
        elif effectiveness < 1.0 and effectiveness > 0:
            self._log("It's not very effective...")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.NOT_EFFECTIVE,
                message="It's not very effective...",
                data={'effectiveness': effectiveness}
            ))
        
        # Random variance
        damage = int(damage * random.uniform(0.85, 1.0))
        
        # Critical hit with living world modifiers
        crit_chance = 0.0625  # Base 6.25% chance
        if self.enhancer:
            crit_chance += self.enhancer.calculate_critical_chance_modifier(attacker)
        
        is_critical = random.random() < crit_chance
        if is_critical:
            damage = int(damage * 1.5)
            self._log("Critical hit!")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.CRITICAL_HIT,
                message="Critical hit!"
            ))
        
        # Apply living world damage modifiers
        if self.enhancer:
            damage = self.enhancer.calculate_damage_modifier(
                attacker,
                defender,
                damage,
                is_critical
            )
        
        return max(1, int(damage)), is_critical
    
    def _get_type_effectiveness(
        self,
        attacker: Creature,
        defender: Creature
    ) -> float:
        """Calculate type effectiveness multiplier."""
        if not attacker.creature_type.type_tags:
            return 1.0
        
        attacker_type = attacker.creature_type.type_tags[0]
        effectiveness = 1.0
        
        if attacker_type in self.TYPE_EFFECTIVENESS:
            for defender_type in defender.creature_type.type_tags:
                if defender_type in self.TYPE_EFFECTIVENESS[attacker_type]:
                    effectiveness *= self.TYPE_EFFECTIVENESS[attacker_type][defender_type]
        
        return effectiveness
    
    def _check_accuracy(self, accuracy: int) -> bool:
        """Check if an ability hits."""
        return random.randint(1, 100) <= accuracy
    
    def _apply_relationship_damage_modifier(
        self,
        attacker: BattleCreature,
        defender: BattleCreature,
        base_damage: int
    ) -> int:
        """
        Apply damage modifiers based on relationships and combat context.
        
        Args:
            attacker: The attacking creature
            defender: The defending creature
            base_damage: Base damage before modifiers
            
        Returns:
            Modified damage
        """
        modifier = 1.0
        
        # Check for revenge bonus
        relationship = attacker.creature.relationships.get_relationship(
            defender.creature.creature_id
        )
        if relationship:
            if relationship.relationship_type == RelationshipType.REVENGE_TARGET:
                modifier += self.combat_config.revenge_damage_bonus
            elif relationship.relationship_type == RelationshipType.RIVAL:
                modifier += self.combat_config.rival_damage_bonus
            
            # Get combat modifier from relationship
            combat_mod = relationship.get_combat_modifier(fighting_together=False)
            modifier *= combat_mod
        
        # Check for ally support bonus (nearby allies boost damage)
        allies_nearby = self._get_allies(attacker, self._creatures, self.combat_config.support_range)
        if len(allies_nearby) >= self.combat_config.gang_up_threshold:
            # Gang-up bonus
            gang_bonus = 1.0 + (len(allies_nearby) * self.combat_config.gang_up_damage_bonus)
            modifier *= gang_bonus
        elif len(allies_nearby) > 0:
            # Basic ally support
            modifier += self.combat_config.ally_support_bonus
        
        # Check for family protection bonus (protecting injured family)
        for ally in allies_nearby:
            if attacker.creature.relationships.has_relationship(
                ally.creature.creature_id,
                RelationshipType.PARENT
            ) or attacker.creature.relationships.has_relationship(
                ally.creature.creature_id,
                RelationshipType.CHILD
            ) or attacker.creature.relationships.has_relationship(
                ally.creature.creature_id,
                RelationshipType.SIBLING
            ):
                # Check if family member is injured
                family_hp_percent = ally.creature.stats.hp / max(1, ally.creature.stats.max_hp)
                if family_hp_percent < self.combat_config.protect_ally_hp_threshold:
                    # Fighting to protect injured family
                    modifier += self.combat_config.family_protection_bonus
                    break
        
        return int(base_damage * modifier)
    
    def _handle_revenge_relationships(
        self,
        killer: BattleCreature,
        victim: BattleCreature
    ):
        """
        Handle relationship updates when a creature is killed.
        
        Family members of the victim will seek revenge on the killer.
        
        Args:
            killer: The creature who killed
            victim: The creature who was killed
        """
        # Find family members of the victim
        victim_family = victim.creature.relationships.get_family()
        
        for family_rel in victim_family:
            family_id = family_rel.target_id
            
            # Find the family member in the battle
            for creature in self._creatures:
                if creature.creature.creature_id == family_id and creature.is_alive():
                    # Record that killer killed their family member
                    creature.creature.relationships.record_family_killed(
                        killer.creature.creature_id,
                        victim.creature.name
                    )
                    break

    
    def _handle_corpse_consumption(self, corpse: BattleCreature, killer: BattleCreature):
        """
        Allow nearby carnivores/omnivores to consume a defeated creature.
        
        Args:
            corpse: The defeated creature
            killer: The creature that defeated the corpse
        """
        # Define consumption radius
        CONSUMPTION_RADIUS = 5.0
        CORPSE_FOOD_VALUE = 50  # Creatures provide more food than pellets
        
        # Find nearby creatures that can eat creatures (carnivores and omnivores)
        potential_consumers = []
        
        # Prioritize the killer
        if killer.creature.can_eat_food_type("creature"):
            potential_consumers.append(killer)
        
        # Use spatial grid to find other nearby creatures
        nearby_creatures = self.creature_grid.query_radius(
            corpse.spatial.position,
            CONSUMPTION_RADIUS,
            exclude={killer, corpse}
        )
        
        # Filter for those that can eat creatures
        for creature in nearby_creatures:
            if creature.is_alive() and creature.creature.can_eat_food_type("creature"):
                potential_consumers.append(creature)
        
        # Allow one creature to consume the corpse
        if potential_consumers:
            consumer = potential_consumers[0]  # First one gets it
            hunger_restored = consumer.creature.eat(CORPSE_FOOD_VALUE, food_type="creature")
            
            if hunger_restored > 0:
                self._log(f"{consumer.creature.name} consumed {corpse.creature.name}'s corpse and restored {hunger_restored} hunger!")
                self._emit_event(BattleEvent(
                    event_type=BattleEventType.CREATURE_CONSUMED,
                    actor=consumer,
                    target=corpse,
                    value=hunger_restored,
                    message=f"{consumer.creature.name} consumed {corpse.creature.name}! Hunger: {consumer.creature.hunger}/{consumer.creature.max_hunger}",
                    data={
                        'hunger_restored': hunger_restored,
                        'current_hunger': consumer.creature.hunger,
                        'corpse_name': corpse.creature.name
                    }
                ))
    
    def _spawn_pellets_from_creature(self, creature: BattleCreature, count: int = 3):
        """
        Spawn pellets when a creature dies.
        
        Args:
            creature: The creature that died
            count: Number of pellets to spawn from the corpse
        """
        # Calculate nutritional value based on creature's size/stats
        base_nutrition = 30.0 + (creature.creature.stats.max_hp / 10.0)
        
        # Create nutrient zone where creature died (enhances pellet growth)
        creature_size = creature.creature.stats.max_hp / 100.0  # Normalize size
        self.grass_growth.on_creature_death(
            x=creature.spatial.position.x,
            y=creature.spatial.position.y,
            creature_size=creature_size
        )
        
        for i in range(count):
            # Spawn pellets near the creature's position
            offset_x = random.uniform(-3, 3)
            offset_y = random.uniform(-3, 3)
            pellet = create_pellet_from_creature(
                x=creature.spatial.position.x + offset_x,
                y=creature.spatial.position.y + offset_y,
                creature_nutritional_value=base_nutrition
            )
            # Clamp position to arena bounds
            pellet.x = max(0, min(self.arena.width, pellet.x))
            pellet.y = max(0, min(self.arena.height, pellet.y))
            self.arena.add_pellet(pellet)
    
    def _update_pellets(self, delta_time: float):
        """
        Update all pellets (age, reproduce, die).
        
        Args:
            delta_time: Time elapsed since last update
        """
        pellets_to_remove = []
        pellets_to_add = []
        
        # Optimization: Only do density checks every N updates to reduce spatial queries
        # At 60 FPS, checking every 30 frames = ~twice per second
        if not hasattr(self, '_pellet_update_counter'):
            self._pellet_update_counter = 0
        
        self._pellet_update_counter += 1
        should_check_reproduction = (self._pellet_update_counter % 30 == 0)
        
        # Get only Pellet objects (not legacy Vector2D resources)
        for pellet in self.arena.pellets:
            # Age the pellet
            pellet.tick(delta_time)
            
            # Check if pellet died of old age
            if pellet.is_dead():
                pellets_to_remove.append(pellet)
                continue
            
            # Only check reproduction periodically to reduce expensive spatial queries
            if should_check_reproduction:
                # Count nearby pellets for density calculation using spatial grid
                pellet_pos = Vector2D(pellet.x, pellet.y)
                DENSITY_RADIUS = 20.0
                # Use exact distance for density checks
                nearby_pellets = self.arena.spatial_grid.query_radius(
                    pellet_pos,
                    DENSITY_RADIUS,
                    exclude={pellet},
                    exact_distance=True,
                    get_position=lambda p: Vector2D(p.x, p.y) if hasattr(p, 'x') else p
                )
                nearby_count = len(nearby_pellets) + 1  # +1 to include the pellet itself
                
                # Get nearby creatures for symbiotic bonus
                CREATURE_RADIUS = 15.0
                nearby_creatures = self.creature_grid.query_radius(
                    pellet_pos,
                    CREATURE_RADIUS,
                    exact_distance=True
                )
                
                # Calculate growth rate multiplier from grass growth system
                growth_multiplier = self.grass_growth.get_growth_rate_multiplier(
                    pellet, 
                    nearby_creatures
                )
                
                # Attempt reproduction with enhanced growth rate
                CARRYING_CAPACITY = 50  # Max pellets in local area
                
                # Apply growth multiplier by temporarily boosting the pellet's growth rate
                original_growth_rate = pellet.traits.growth_rate
                pellet.traits.growth_rate *= growth_multiplier
                
                # Check reproduction with boosted rate
                can_reproduce = pellet.can_reproduce(nearby_count, CARRYING_CAPACITY)
                
                # Restore original growth rate
                pellet.traits.growth_rate = original_growth_rate
                
                if can_reproduce:
                    offspring = pellet.reproduce(mutation_rate=0.15)
                    # Clamp offspring position to arena bounds
                    offspring.x = max(0, min(self.arena.width, offspring.x))
                    offspring.y = max(0, min(self.arena.height, offspring.y))
                    pellets_to_add.append(offspring)
        
        # Remove dead pellets
        for pellet in pellets_to_remove:
            self.arena.remove_resource(pellet)
        
        # Add new offspring
        for pellet in pellets_to_add:
            self.arena.add_pellet(pellet)
    
    def _process_status_effects(self, creature: BattleCreature):
        """Process status effects (simplified for spatial combat)."""
        # Status effects would be processed here
        # For now, just tick creature modifiers
        creature.creature.tick_modifiers()
    
    def _check_breeding(self, alive_creatures: List[BattleCreature]):
        """
        Check for breeding opportunities among creatures.
        
        Args:
            alive_creatures: List of all currently alive creatures
        """
        # Only attempt breeding if population is not at critical levels
        if len(alive_creatures) < 2:
            return
        
        # Find potential breeding pairs (creatures close to each other)
        # Breeding range scales with arena size (20% of smaller dimension)
        breeding_range = min(self.arena.width, self.arena.height) * 0.3
        
        # Track which creatures have already bred this check
        bred_this_cycle = set()
        
        for creature1 in alive_creatures:
            # Skip if creature cannot breed or already bred this cycle
            if not creature1.creature.can_breed() or creature1 in bred_this_cycle:
                continue
            
            # Use spatial grid to find nearby potential mates
            nearby_creatures = self.creature_grid.query_radius(
                creature1.spatial.position,
                breeding_range,
                exclude={creature1}
            )
            
            # Check nearby creatures for breeding
            for creature2 in nearby_creatures:
                # Skip if second creature cannot breed or already bred
                if not creature2.creature.can_breed() or creature2 in bred_this_cycle:
                    continue
                
                # Attempt breeding
                offspring = self.breeding_system.breed(
                    creature1.creature,
                    creature2.creature,
                    birth_time=self.current_time
                )
                
                if offspring:
                    # Mark both parents as having bred this cycle
                    bred_this_cycle.add(creature1)
                    bred_this_cycle.add(creature2)
                    
                    # Record breeding for living world
                    if self.enhancer:
                        self.enhancer.on_breeding(
                            creature1.creature,
                            creature2.creature,
                            offspring
                        )
                    
                    # Spawn offspring near parents
                    spawn_pos = Vector2D(
                        (creature1.spatial.position.x + creature2.spatial.position.x) / 2,
                        (creature1.spatial.position.y + creature2.spatial.position.y) / 2
                    )
                    # Add small random offset
                    spawn_pos.x += random.uniform(-3, 3)
                    spawn_pos.y += random.uniform(-3, 3)
                    spawn_pos = self.arena.clamp_position(spawn_pos)
                    
                    # Create battle creature and add to population
                    battle_offspring = BattleCreature(offspring, spawn_pos)
                    self._creatures.append(battle_offspring)
                    
                    # Add offspring to spatial grid
                    self.creature_grid.insert(battle_offspring, battle_offspring.spatial.position)
                    
                    self.birth_count += 1
                    
                    self._log(f"BIRTH! {creature1.creature.name} and {creature2.creature.name} had offspring: {offspring.name}")
                    self._emit_event(BattleEvent(
                        event_type=BattleEventType.CREATURE_BIRTH,
                        actor=battle_offspring,
                        message=f"{offspring.name} was born! Parents: {creature1.creature.name} & {creature2.creature.name}",
                        data={
                            'parent1': creature1.creature.name,
                            'parent2': creature2.creature.name,
                            'position': spawn_pos.to_tuple(),
                            'hue': offspring.hue,
                            'strain_id': offspring.strain_id
                        }
                    ))
                    
                    # Only one offspring per pair per check
                    break
    
    def _get_creature_environmental_adaptation(self, creature: BattleCreature, position: Vector2D) -> float:
        """
        Calculate creature's environmental adaptation modifier based on traits.
        
        Args:
            creature: The creature
            position: Current position
            
        Returns:
            Movement speed modifier (0.5 to 2.0)
        """
        if not self.environment:
            return 1.0
        
        modifier = 1.0
        trait_names = [t.name.lower() for t in creature.creature.traits]
        
        # Get terrain type
        terrain = self.environment.get_terrain_at(position)
        if terrain:
            terrain_name = terrain.terrain_type.name.lower()
            
            # Terrain-specific adaptations
            if 'aquatic' in ' '.join(trait_names) and 'water' in terrain_name:
                modifier *= 2.0  # Double speed in water
            elif 'aquatic' in ' '.join(trait_names):
                modifier *= 0.7  # Slower on land
            
            if 'rock climber' in ' '.join(trait_names) and 'rocky' in terrain_name:
                modifier *= 1.5
            
            if 'forest dweller' in ' '.join(trait_names) and 'forest' in terrain_name:
                modifier *= 1.4
            
            if 'desert adapted' in ' '.join(trait_names) and 'desert' in terrain_name:
                modifier *= 1.3
            
            if 'marsh navigator' in ' '.join(trait_names) and 'marsh' in terrain_name:
                modifier *= 1.8
            
            if 'all terrain' in ' '.join(trait_names):
                modifier *= 1.05  # Small bonus everywhere
        
        # Weather adaptations
        if self.environment.weather:
            temp = self.environment.weather.temperature
            
            if 'cold blooded' in ' '.join(trait_names):
                if temp > 25:
                    modifier *= 1.2
                elif temp < 10:
                    modifier *= 0.8
            
            if 'heat resistant' in ' '.join(trait_names) and temp > 30:
                modifier *= 1.25
            
            if 'storm walker' in ' '.join(trait_names):
                from ..models.environment import WeatherType
                if self.environment.weather.weather_type == WeatherType.STORMY:
                    modifier *= 1.1
        
        # Time of day adaptations
        if self.environment.day_night:
            from ..models.environment import TimeOfDay
            time_of_day = self.environment.day_night.get_time_of_day()
            
            if 'nocturnal' in ' '.join(trait_names):
                if time_of_day == TimeOfDay.NIGHT:
                    modifier *= 1.3
                elif time_of_day == TimeOfDay.DAY:
                    modifier *= 0.85
            
            if 'diurnal' in ' '.join(trait_names):
                if time_of_day == TimeOfDay.DAY:
                    modifier *= 1.2
                elif time_of_day == TimeOfDay.NIGHT:
                    modifier *= 0.9
            
            if 'crepuscular' in ' '.join(trait_names):
                if time_of_day in (TimeOfDay.DAWN, TimeOfDay.DUSK):
                    modifier *= 1.25
        
        return max(0.5, min(2.0, modifier))
    
    def _calculate_hazard_damage(self, creature: BattleCreature, base_damage: float) -> float:
        """
        Calculate actual hazard damage after applying trait resistances.
        
        Args:
            creature: The creature taking damage
            base_damage: Base environmental damage
            
        Returns:
            Actual damage after resistance modifiers
        """
        damage = base_damage
        trait_names = [t.name.lower() for t in creature.creature.traits]
        
        # Check for hazard resistance traits
        if 'fire proof' in ' '.join(trait_names) or 'fire resistant' in ' '.join(trait_names):
            damage *= 0.0  # Immune to fire
        elif 'heat resistant' in ' '.join(trait_names):
            damage *= 0.5  # Half damage from heat-based hazards
        
        if 'poison resistant' in ' '.join(trait_names):
            damage *= 0.3  # 70% reduction from poison
        
        if 'thick hide' in ' '.join(trait_names):
            damage *= 0.8  # 20% reduction from all hazards
        
        if 'grounded' in ' '.join(trait_names):
            damage *= 0.2  # 80% reduction from electrical
        
        return damage
    
    def _trigger_environmental_hazard(self, alive_creatures: List[BattleCreature]):
        """
        Trigger a random environmental hazard that affects all creatures.
        
        Hazards encourage creatures to work together or find safe zones.
        """
        if not alive_creatures:
            return
        
        hazard_types = ['storm', 'heat_wave', 'resource_scarcity']
        hazard = random.choice(hazard_types)
        
        if hazard == 'storm':
            # Storm damages all creatures slightly, encouraging them to seek shelter together
            damage = random.randint(3, 8)
            safe_zone = Vector2D(
                random.uniform(self.arena.width * 0.2, self.arena.width * 0.8),
                random.uniform(self.arena.height * 0.2, self.arena.height * 0.8)
            )
            safe_radius = min(self.arena.width, self.arena.height) * 0.15
            
            affected_count = 0
            for creature in alive_creatures:
                distance_to_safe = creature.spatial.position.distance_to(safe_zone)
                if distance_to_safe > safe_radius:
                    # Creature takes damage from storm
                    actual_damage = creature.creature.stats.take_damage(damage)
                    if actual_damage > 0:
                        affected_count += 1
            
            self._log(f"⚡ STORM! {affected_count} creatures caught outside safe zone took {damage} damage")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.HAZARD_DAMAGE,
                message=f"Storm hits the arena! {affected_count} creatures damaged",
                data={'hazard_type': 'storm', 'damage': damage, 'affected': affected_count}
            ))
        
        elif hazard == 'heat_wave':
            # Heat wave increases hunger depletion temporarily
            self._log(f"🔥 HEAT WAVE! All creatures' hunger depletes faster")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.HAZARD_DAMAGE,
                message="Heat wave strikes! Hunger increases faster",
                data={'hazard_type': 'heat_wave', 'duration': 10.0}
            ))
            # Temporarily increase hunger depletion for all creatures
            for creature in alive_creatures:
                # Reduce hunger by extra amount
                creature.creature.hunger = max(0, creature.creature.hunger - 5)
        
        elif hazard == 'resource_scarcity':
            # Remove some resources, encouraging cooperation in foraging
            resources_before = len(self.arena.resources)
            if resources_before > 0:
                remove_count = max(1, resources_before // 3)
                for _ in range(remove_count):
                    if self.arena.resources:
                        self.arena.resources.pop()
                
                self._log(f"🌾 RESOURCE SCARCITY! {remove_count} food sources disappeared")
                self._emit_event(BattleEvent(
                    event_type=BattleEventType.HAZARD_DAMAGE,
                    message=f"Resource scarcity! {remove_count} food sources vanish",
                    data={'hazard_type': 'resource_scarcity', 'removed': remove_count}
                ))
    
    def _spawn_cooperative_resource(self):
        """
        Spawn a large resource cluster that encourages cooperative gathering.
        
        Creates multiple pellets in a small area, rewarding creatures that work together.
        """
        # Choose a random location for the resource cluster
        cluster_center = Vector2D(
            random.uniform(10, self.arena.width - 10),
            random.uniform(10, self.arena.height - 10)
        )
        
        # Spawn 3-5 pellets in a cluster
        cluster_size = random.randint(3, 5)
        cluster_radius = 5.0
        
        for _ in range(cluster_size):
            # Offset from center
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, cluster_radius)
            position = Vector2D(
                cluster_center.x + math.cos(angle) * distance,
                cluster_center.y + math.sin(angle) * distance
            )
            position = self.arena.clamp_position(position)
            
            # Create a high-quality pellet at the position
            pellet = create_random_pellet(position.x, position.y, generation=1)
            pellet.traits.palatability = random.uniform(0.7, 1.0)  # High palatability
            pellet.traits.toxicity = random.uniform(0.0, 0.2)  # Low toxicity
            pellet.traits.nutrient_value = random.uniform(25, 35)  # Good nutrients
            
            self.arena.add_pellet(pellet)
        
        self._log(f"🍎 COOPERATIVE FOOD! Resource cluster of {cluster_size} pellets appeared")
        self._emit_event(BattleEvent(
            event_type=BattleEventType.PELLET_SPAWN,
            message=f"Rich food cluster spawned! {cluster_size} high-quality pellets",
            data={'cluster_size': cluster_size, 'position': cluster_center.to_tuple()}
        ))
    
    
    def _end_battle(self):
        """End the battle when population has collapsed."""
        self.is_over = True
        
        alive_creatures = [c for c in self._creatures if c.is_alive()]
        
        # Record battle end for living world
        if self.enhancer:
            survivors = [bc.creature for bc in alive_creatures]
            self.enhancer.on_battle_end(survivors)
        
        if len(alive_creatures) == 1:
            self._log(f"\n=== Battle End - Last survivor: {alive_creatures[0].creature.name} ===")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.BATTLE_END,
                message=f"Battle ended - {alive_creatures[0].creature.name} is the last survivor!",
                data={'survivors': 1, 'last_creature': alive_creatures[0].creature.name}
            ))
        elif len(alive_creatures) > 1:
            self._log(f"\n=== Battle End - {len(alive_creatures)} survivors remain ===")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.BATTLE_END,
                message=f"Battle ended - {len(alive_creatures)} survivors remain",
                data={'survivors': len(alive_creatures)}
            ))
        else:
            self._log(f"\n=== Battle End - Total extinction ===")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.BATTLE_END,
                message=f"Battle ended - population extinct",
                data={'survivors': 0}
            ))
    
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
    
    def get_battle_log(self) -> List[str]:
        """Get the complete battle log."""
        return self.battle_log
    
    def get_state_snapshot(self) -> Dict:
        """Get current state snapshot for visualization."""
        return {
            'time': self.current_time,
            'is_over': self.is_over,
            'creatures': [
                {
                    'name': c.creature.name,
                    'hp': c.creature.stats.hp,
                    'max_hp': c.creature.stats.max_hp,
                    'hunger': c.creature.hunger,
                    'max_hunger': c.creature.max_hunger,
                    'position': c.spatial.position.to_tuple(),
                    'velocity': c.spatial.velocity.to_tuple(),
                    'alive': c.is_alive()
                }
                for c in self._creatures
            ],
            'resources': [r.to_tuple() for r in self.arena.resources]
        }


# Backwards compatibility alias
Battle = SpatialBattle
