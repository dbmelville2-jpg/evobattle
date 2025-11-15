"""
Spatial Real-Time Battle System - Handles real-time 2D combat.

Creatures move and fight in a 2D arena with positioning, proximity-based
targeting, and continuous time updates. Traits affect behavior, movement,
and combat decisions.
"""

from typing import List, Optional, Dict, Callable, Tuple
from enum import Enum
import random
import time
import math

from ..models.creature import Creature
from ..models.ability import Ability, AbilityType, TargetType
from ..models.status_effect import StatusEffect, StatusEffectType
from ..models.stats import StatModifier
from ..models.spatial import Vector2D, SpatialEntity, Arena
from ..models.behavior import SpatialBehavior, BehaviorType
from .breeding import Breeding


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
    BATTLE_END = "battle_end"


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
            radius=1.0,
            max_speed=creature.stats.speed / 10.0  # Convert speed stat to spatial speed
        )
        self.behavior = self._determine_behavior()
        self.target: Optional['BattleCreature'] = None
        self.ability_cooldowns: Dict[str, float] = {}
        self.last_attack_time: float = 0
        self.attack_cooldown: float = 1.0  # Seconds between attacks
        
        # Target retention to prevent rapid retargeting
        self.target_retention_distance: float = 15.0  # Keep target if within this distance
        self.min_retarget_time: float = 0.5  # Minimum seconds before changing target
        self.last_retarget_time: float = 0.0
        
        # Movement state to prevent jitter
        self.current_movement_target: Optional[Vector2D] = None
        self.last_behavior_state: str = "combat"  # Track if seeking food vs combat (start in combat mode)
    
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
    
    def can_attack(self, current_time: float) -> bool:
        """Check if creature can attack based on cooldown."""
        return current_time - self.last_attack_time >= self.attack_cooldown


class SpatialBattle:
    """
    Manages real-time spatial combat in a 2D arena.
    
    Creatures move, target, and fight based on proximity and traits.
    Uses continuous time updates rather than turns.
    """
    
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
        initial_resources: int = 5
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
        """
        # Handle backward compatibility - detect old two-team API
        if team2_or_none is not None:
            # Old API: two teams passed separately
            all_creatures = creatures_or_team1 + team2_or_none
        else:
            # New API: single list of creatures
            all_creatures = creatures_or_team1
        
        self.arena = Arena(arena_width, arena_height)
        self.battle_log: List[str] = []
        self.events: List[BattleEvent] = []
        self._event_callbacks: List[Callable[[BattleEvent], None]] = []
        self.current_time: float = 0.0
        self.is_over: bool = False
        self.resource_spawn_rate = resource_spawn_rate
        self.time_since_last_resource_spawn: float = 0.0
        
        # Breeding system and population statistics
        self.breeding_system = Breeding(mutation_rate=0.1, trait_inheritance_chance=0.8)
        self.birth_count: int = 0
        self.death_count: int = 0
        self.breeding_cooldown: float = 5.0  # Seconds between breeding attempts
        self.last_breeding_check: float = 0.0
        
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
        """Spawn a food resource at a random location in the arena."""
        resource_pos = self.arena.get_random_position()
        self.arena.add_resource(resource_pos)
    
    def update(self, delta_time: float):
        """
        Update battle state for one frame.
        
        Args:
            delta_time: Time elapsed since last update (seconds)
        """
        if self.is_over:
            return
        
        self.current_time += delta_time
        
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
        
        # Tick hunger for all alive creatures
        for creature in alive_creatures:
            creature.creature.tick_hunger(delta_time)
            # Check if creature starved
            if creature.creature.hunger <= 0 and creature.is_alive():
                self.death_count += 1
                self._log(f"{creature.creature.name} starved to death!")
                self._emit_event(BattleEvent(
                    event_type=BattleEventType.CREATURE_DEATH,
                    target=creature,
                    message=f"{creature.creature.name} starved to death!"
                ))
        
        # Update each creature
        for creature in alive_creatures:
            if creature.is_alive():  # Re-check after hunger tick
                self._update_creature(creature, alive_creatures, delta_time)
        
        # Check for breeding opportunities (periodically)
        if self.current_time - self.last_breeding_check >= self.breeding_cooldown:
            self._check_breeding(alive_creatures)
            self.last_breeding_check = self.current_time
        
        # Process status effects
        for creature in alive_creatures:
            self._process_status_effects(creature)
    
    def _update_creature(
        self,
        creature: BattleCreature,
        all_alive: List[BattleCreature],
        delta_time: float
    ):
        """Update a single creature's AI, movement, and combat."""
        # Get other creatures as potential targets/allies
        other_creatures = [c for c in all_alive if c != creature]
        
        # Convert to spatial entities for behavior system
        other_entities = [c.spatial for c in other_creatures]
        
        # Check if creature is hungry and should prioritize food
        # Use hysteresis to prevent rapid behavior flipping at threshold
        HUNGER_THRESHOLD_LOW = 35  # Start seeking food
        HUNGER_THRESHOLD_HIGH = 50  # Stop seeking food (buffer zone)
        
        current_state = "seeking_food" if creature.last_behavior_state == "seeking_food" else "combat"
        
        if current_state == "combat" and creature.creature.hunger < HUNGER_THRESHOLD_LOW and len(self.arena.resources) > 0:
            # Switch to seeking food
            current_state = "seeking_food"
        elif current_state == "seeking_food" and (creature.creature.hunger >= HUNGER_THRESHOLD_HIGH or len(self.arena.resources) == 0):
            # Switch back to combat
            current_state = "combat"
        
        creature.last_behavior_state = current_state
        seeking_food = (current_state == "seeking_food")
        
        # Determine movement - prioritize food if hungry
        if seeking_food:
            # Override behavior to seek nearest food
            nearest_resource = min(self.arena.resources, key=lambda r: creature.spatial.position.distance_to(r))
            movement_target = nearest_resource
        else:
            # Determine target with hysteresis to prevent rapid retargeting
            should_retarget = False
            
            if not creature.target or not creature.target.is_alive():
                should_retarget = True
            elif self.current_time - creature.last_retarget_time >= creature.min_retarget_time:
                # Check if current target is too far and there's a closer target
                current_distance = creature.spatial.distance_to(creature.target.spatial)
                if current_distance > creature.target_retention_distance:
                    # Look for a closer target
                    if other_creatures:
                        closest_distance = min(creature.spatial.distance_to(c.spatial) for c in other_creatures if c != creature.target)
                        # Only retarget if significantly closer (20% threshold)
                        if closest_distance < current_distance * 0.8:
                            should_retarget = True
            
            if should_retarget:
                target_entity = creature.behavior.get_target(
                    creature.spatial,
                    [],  # No allies in free-for-all
                    other_entities,
                    self.arena.hazards,
                    self.arena.resources
                )
                # Find corresponding BattleCreature
                if target_entity:
                    for other in other_creatures:
                        if other.spatial == target_entity:
                            creature.target = other
                            creature.last_retarget_time = self.current_time
                            break
            
            # Determine movement
            movement_target = creature.behavior.get_movement_target(
                creature.spatial,
                creature.target.spatial if creature.target else None,
                [],  # No allies in free-for-all
                other_entities,
                self.arena.hazards,
                self.arena.resources
            )
        
        # Move towards target with smooth acceleration
        old_pos = (creature.spatial.position.x, creature.spatial.position.y)
        if movement_target:
            creature.spatial.move_towards(movement_target, delta_time=delta_time)
            creature.spatial.update(delta_time)
            
            # Keep within bounds
            creature.spatial.position = self.arena.clamp_position(creature.spatial.position)
            
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
            distance = creature.spatial.position.distance_to(resource)
            if distance < 2.0:  # Collection range
                # Eat the resource
                hunger_restored = creature.creature.eat(40)
                resources_to_remove.append(resource)
                self._log(f"{creature.creature.name} ate food and restored {hunger_restored} hunger!")
                self._emit_event(BattleEvent(
                    event_type=BattleEventType.RESOURCE_COLLECTED,
                    actor=creature,
                    message=f"{creature.creature.name} ate food! Hunger: {creature.creature.hunger}/{creature.creature.max_hunger}",
                    data={
                        'resource_position': resource.to_tuple(),
                        'hunger_restored': hunger_restored,
                        'current_hunger': creature.creature.hunger
                    }
                ))
                break  # Only collect one resource per update
        
        # Remove collected resources
        for resource in resources_to_remove:
            self.arena.resources.remove(resource)
        
        # Attempt combat
        if creature.target and creature.can_attack(self.current_time):
            self._attempt_attack(creature, creature.target)
    
    def _attempt_attack(self, attacker: BattleCreature, defender: BattleCreature):
        """Attempt an attack from attacker to defender."""
        # Choose ability
        usable_abilities = [
            a for a in attacker.creature.abilities
            if a.can_use(attacker.creature.stats, attacker.creature.energy)
        ]
        
        if usable_abilities:
            ability = max(usable_abilities, key=lambda a: a.power)
        else:
            # Basic attack
            ability = Ability(name="Basic Attack", power=10, accuracy=100)
        
        # Check range
        attack_range = 5.0  # Base attack range
        if ability.ability_type == AbilityType.PHYSICAL:
            attack_range = 3.0  # Melee range
        elif ability.ability_type == AbilityType.SPECIAL:
            attack_range = 8.0  # Ranged attack
        
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
        
        # Check accuracy
        if not self._check_accuracy(ability.accuracy):
            self._log(f"{ability.name} missed!")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.MISS,
                actor=attacker,
                target=defender,
                ability=ability,
                message=f"{ability.name} missed!"
            ))
            return
        
        # Apply damage or effects
        if ability.ability_type in [AbilityType.PHYSICAL, AbilityType.SPECIAL]:
            damage = self._calculate_damage(attacker.creature, defender.creature, ability)
            actual_damage = defender.creature.stats.take_damage(damage)
            self._log(f"{defender.creature.name} takes {actual_damage} damage! (HP: {defender.creature.stats.hp}/{defender.creature.stats.max_hp})")
            
            self._emit_event(BattleEvent(
                event_type=BattleEventType.DAMAGE_DEALT,
                actor=attacker,
                target=defender,
                ability=ability,
                value=actual_damage,
                message=f"{defender.creature.name} takes {actual_damage} damage!",
                data={'remaining_hp': defender.creature.stats.hp, 'max_hp': defender.creature.stats.max_hp}
            ))
            
            if not defender.is_alive():
                self.death_count += 1
                self._emit_event(BattleEvent(
                    event_type=BattleEventType.CREATURE_DEATH,
                    target=defender,
                    message=f"{defender.creature.name} was defeated!"
                ))
        
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
    ) -> int:
        """Calculate damage (reuses turn-based formula)."""
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
        
        # Critical hit
        if random.random() < 0.0625:
            damage = int(damage * 1.5)
            self._log("Critical hit!")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.CRITICAL_HIT,
                message="Critical hit!"
            ))
        
        return max(1, damage)
    
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
        breeding_range = 10.0  # Distance within which creatures can breed
        
        for i, creature1 in enumerate(alive_creatures):
            # Skip if creature cannot breed
            if not creature1.creature.can_breed():
                continue
            
            # Check for nearby potential mates
            for creature2 in alive_creatures[i+1:]:
                # Skip if second creature cannot breed
                if not creature2.creature.can_breed():
                    continue
                
                # Check distance
                distance = creature1.spatial.distance_to(creature2.spatial)
                if distance <= breeding_range:
                    # Attempt breeding
                    offspring = self.breeding_system.breed(
                        creature1.creature,
                        creature2.creature,
                        birth_time=self.current_time
                    )
                    
                    if offspring:
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
    
    def _end_battle(self):
        """End the battle when population has collapsed."""
        self.is_over = True
        
        alive_creatures = [c for c in self._creatures if c.is_alive()]
        
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
