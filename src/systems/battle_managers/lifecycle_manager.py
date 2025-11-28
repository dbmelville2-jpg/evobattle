"""
Lifecycle Manager

Handles creature birth, death, breeding, and population management
for the spatial battle system.

Extracted from battle_spatial.py.
"""

import random
import math
from typing import List, Optional, Any, Tuple, Dict, Callable

from src.models.spatial import Vector2D, SpatialHashGrid, Arena
from src.models.creature import Creature
from src.models.relationships import RelationshipType
from src.systems.battle_events import BattleEvent, BattleEventType
from src.systems.breeding import Breeding
from .event_manager import EventManager
from .resource_manager import ResourceManager

# Forward declaration for type hinting
# We can't import BattleCreature directly due to circular imports if BattleCreature is in battle_spatial
# But BattleCreature is defined in battle_spatial.py, so we need to be careful.
# Ideally BattleCreature should be in its own file.
# For now, we'll use Any for BattleCreature in type hints or import if possible.
# Actually BattleCreature is in battle_spatial.py.
# We should probably extract BattleCreature to its own file eventually, but for now we will assume it is passed as Any or we import it if it was moved.
# Wait, BattleCreature IS in battle_spatial.py.
# So I cannot import it here without circular dependency if battle_spatial imports LifecycleManager.
# I will use Any for BattleCreature for now.

class LifecycleManager:
    """
    Manages creature lifecycle events.
    
    Responsibilities:
    - Spawn initial population
    - Handle creature deaths
    - Manage breeding and birth
    - Track population statistics
    - Check for battle end conditions
    """
    
    def __init__(
        self,
        event_manager: EventManager,
        resource_manager: ResourceManager,
        arena: Arena,
        creature_grid: SpatialHashGrid,
        breeding_system: Optional[Breeding] = None,
        enhancer: Any = None,
        reward_tracker: Any = None
    ):
        """
        Initialize the lifecycle manager.
        
        Args:
            event_manager: Event manager for emitting events
            resource_manager: Resource manager for spawning pellets on death
            arena: Arena for position clamping
            creature_grid: Spatial grid for proximity queries
            breeding_system: System for handling genetics and breeding
            enhancer: Living world enhancer (optional)
            reward_tracker: Neural reward tracker (optional)
        """
        self.event_manager = event_manager
        self.resource_manager = resource_manager
        self.arena = arena
        self.creature_grid = creature_grid
        self.breeding_system = breeding_system or Breeding()
        self.enhancer = enhancer
        self.reward_tracker = reward_tracker
        
        self.death_count: int = 0
        self.birth_count: int = 0
        
    def spawn_population(
        self,
        creatures: List[Creature],
        battle_creature_class: Any
    ) -> List[Any]:
        """
        Spawn a population of creatures distributed throughout the arena.
        
        Args:
            creatures: List of creature models to spawn
            battle_creature_class: Class to instantiate (BattleCreature)
            
        Returns:
            List of spawned BattleCreature instances
        """
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
            
            battle_creature = battle_creature_class(creature, position)
            spawned.append(battle_creature)
            
            # Add to spatial grid
            self.creature_grid.insert(battle_creature, battle_creature.spatial.position)
            
            self.event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.CREATURE_SPAWN,
                actor=battle_creature,
                message=f"{creature.name} spawned at ({x:.1f}, {y:.1f})",
                data={'position': position.to_tuple()}
            ))
        
        return spawned
    
    def update_lifecycle(self, creatures: List[Any], delta_time: float, environment_manager: Any = None):
        """
        Update hunger, age, and check for starvation deaths.
        
        Args:
            creatures: List of BattleCreature instances
            delta_time: Time elapsed since last update
            environment_manager: Optional environment manager for hunger modifiers
        """
        for creature in creatures:
            if not creature.is_alive():
                continue
                
            # Apply environmental hunger modifier
            hunger_delta = delta_time
            if environment_manager and environment_manager.environment and environment_manager.environment.weather:
                hunger_delta *= environment_manager.environment.weather.get_hunger_modifier()
            
            # Tick hunger and age
            creature.creature.tick_hunger(hunger_delta)
            creature.creature.tick_age(delta_time)
            
            # Process status effects (poison, burning, etc.)
            creature.creature.tick_modifiers()
            
            # Check for starvation death
            if creature.creature.hunger <= 0:
                self.handle_death(creature, creatures, killer=None, cause="starvation")

    def handle_death(
        self,
        creature: Any,
        active_creatures: List[Any],
        killer: Optional[Any] = None,
        cause: str = "unknown"
    ):
        """
        Handle creature death, including removal, logging, and events.
        
        Args:
            creature: The dying BattleCreature
            active_creatures: List of currently active creatures (will be modified)
            killer: The killer BattleCreature (optional)
            cause: Cause of death
        """
        # Neural Learning: Apply death penalty
        if self.reward_tracker:
            self.reward_tracker.apply_reward(creature, 'died')
        
        # Ensure HP is 0
        creature.creature.stats.hp = 0
        
        # Remove from active list
        if creature in active_creatures:
            active_creatures.remove(creature)
            self.death_count += 1
            
            # Remove from spatial grid
            self.creature_grid.remove(creature)
            
            # Log and Event
            message = f"{creature.creature.name} died from {cause}!"
            if killer:
                message = f"{creature.creature.name} was killed by {killer.creature.name}!"
                
            self.event_manager.log(message)
            self.event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.CREATURE_DEATH,
                target=creature,
                actor=killer,
                message=message,
                data={'cause': cause, 'killer_id': killer.creature.creature_id if killer else None}
            ))
            
            # Handle specific death mechanics
            if cause == "starvation":
                 self.resource_manager.spawn_pellets_from_creature(creature)
            elif killer:
                # Combat death
                creature.creature.combat_memory.record_killed_by(killer.creature.creature_id)
                
                # Record kill in battle history
                if hasattr(killer.creature, 'history'):
                    # Calculate power differential (victim power / killer power)
                    victim_power = creature.creature.stats.attack + creature.creature.stats.defense
                    killer_power = killer.creature.stats.attack + killer.creature.stats.defense
                    power_diff = victim_power / max(1, killer_power)
                    
                    killer.creature.history.record_kill(
                        victim_id=creature.creature.creature_id,
                        victim_name=creature.creature.name,
                        power_differential=power_diff,
                        location=(creature.spatial.position.x, creature.spatial.position.y),
                        was_revenge=False  # TODO: Check if this was a revenge kill
                    )
                
                # Record death in victim's history
                if hasattr(creature.creature, 'history'):
                    creature.creature.history.record_death(
                        killer_id=killer.creature.creature_id,
                        cause=f"killed by {killer.creature.name}",
                        location=(creature.spatial.position.x, creature.spatial.position.y)
                    )
                
                self._handle_revenge_relationships(killer, creature, active_creatures)
                
                # Neural Learning: Reward killer
                if self.reward_tracker:
                    self.reward_tracker.apply_reward(killer, 'killed_enemy')
                
                # Record kill for living world
                if self.enhancer:
                    location = (creature.spatial.position.x, creature.spatial.position.y)
                    if hasattr(self.enhancer, 'on_creature_killed'):
                        self.enhancer.on_creature_killed(killer.creature, creature.creature, location)
                    else:
                        self.enhancer.on_creature_death(creature.creature, location, killer.creature)
                
                # Spawn pellets from defeated creature
                self.resource_manager.spawn_pellets_from_creature(creature, count=2)
                
                # Allow nearby carnivores/omnivores to consume the corpse
                self._handle_corpse_consumption(creature, killer)

    def _handle_revenge_relationships(
        self,
        killer: Any,
        victim: Any,
        all_creatures: List[Any]
    ):
        """
        Handle relationship updates when a creature is killed.
        Family members of the victim will seek revenge on the killer.
        """
        # Find family members of the victim
        victim_family = victim.creature.relationships.get_family()
        
        for family_rel in victim_family:
            family_id = family_rel.target_id
            
            # Find the family member in the battle
            for creature in all_creatures:
                if creature.creature.creature_id == family_id and creature.is_alive():
                    # Record that killer killed their family member
                    creature.creature.relationships.record_family_killed(
                        killer.creature.creature_id,
                        victim.creature.name
                    )
                    break

    def _handle_corpse_consumption(self, corpse: Any, killer: Any):
        """
        Allow nearby carnivores/omnivores to consume a defeated creature.
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
                self.event_manager.log(f"{consumer.creature.name} consumed {corpse.creature.name}'s corpse and restored {hunger_restored} hunger!")
                self.event_manager.emit_event(BattleEvent(
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

    def check_breeding(
        self,
        alive_creatures: List[Any],
        current_time: float,
        battle_creature_class: Any,
        all_creatures_list: List[Any]
    ):
        """
        Check for breeding opportunities among creatures.
        
        Args:
            alive_creatures: List of all currently alive creatures
            current_time: Current simulation time
            battle_creature_class: Class to instantiate for offspring
            all_creatures_list: Main list of all creatures (to append offspring)
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
                    birth_time=current_time
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
                    battle_offspring = battle_creature_class(offspring, spawn_pos)
                    all_creatures_list.append(battle_offspring)
                    alive_creatures.append(battle_offspring)
                    
                    # Add offspring to spatial grid
                    self.creature_grid.insert(battle_offspring, battle_offspring.spatial.position)
                    
                    # Create family relationships
                    # Parent 1 -> Child
                    creature1.creature.relationships.add_relationship(
                        offspring.creature_id,
                        RelationshipType.CHILD,
                        strength=1.0
                    )
                    # Parent 2 -> Child
                    creature2.creature.relationships.add_relationship(
                        offspring.creature_id,
                        RelationshipType.CHILD,
                        strength=1.0
                    )
                    # Child -> Parent 1
                    offspring.relationships.add_relationship(
                        creature1.creature.creature_id,
                        RelationshipType.PARENT,
                        strength=1.0
                    )
                    # Child -> Parent 2
                    offspring.relationships.add_relationship(
                        creature2.creature.creature_id,
                        RelationshipType.PARENT,
                        strength=1.0
                    )
                    
                    self.birth_count += 1
                    
                    self.event_manager.log(f"BIRTH! {creature1.creature.name} and {creature2.creature.name} had offspring: {offspring.name}")
                    self.event_manager.emit_event(BattleEvent(
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

    def check_battle_end(self, alive_creatures: List[Any]) -> bool:
        """
        Check if the battle should end and emit events if so.
        
        Returns:
            True if battle is over
        """
        # This logic was originally in _end_battle, but that was called when population collapsed.
        # We need to determine WHEN to call this.
        # In the original code, it was called when len(alive_creatures) <= 1 (or 0)
        # But usually battles run for a duration.
        
        # Let's just provide a method to handle the end of battle reporting
        
        # Record battle end for living world
        if self.enhancer:
            survivors = [bc.creature for bc in alive_creatures]
            self.enhancer.on_battle_end(survivors)
        
        if len(alive_creatures) == 1:
            self.event_manager.log(f"\n=== Battle End - Last survivor: {alive_creatures[0].creature.name} ===")
            self.event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.BATTLE_END,
                message=f"Battle ended - {alive_creatures[0].creature.name} is the last survivor!",
                data={'survivors': 1, 'last_creature': alive_creatures[0].creature.name}
            ))
        elif len(alive_creatures) > 1:
            self.event_manager.log(f"\n=== Battle End - {len(alive_creatures)} survivors remain ===")
            self.event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.BATTLE_END,
                message=f"Battle ended - {len(alive_creatures)} survivors remain",
                data={'survivors': len(alive_creatures)}
            ))
        else:
            self.event_manager.log(f"\n=== Battle End - Total extinction ===")
            self.event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.BATTLE_END,
                message=f"Battle ended - population extinct",
                data={'survivors': 0}
            ))
            
        return True
