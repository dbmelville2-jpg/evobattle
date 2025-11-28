"""
AI Manager

Handles creature decision making, target selection, and behavior updates
for the spatial battle system.

Extracted from battle_spatial.py.
"""

from typing import List, Optional, Any, Dict

from src.models.spatial import Vector2D
from src.models.attention import StimulusType
from .combat_manager import CombatManager
from .neural_manager import NeuralManager
from .lifecycle_manager import LifecycleManager
from .movement_manager import MovementManager
from .resource_manager import ResourceManager
from src.models.spatial import Arena

class AIManager:
    """
    Manages AI logic for creatures.
    
    Responsibilities:
    - Update creature behavior state
    - Handle target selection
    - Coordinate between Neural Manager and standard behavior
    - Execute high-level decisions (fight, flee, eat)
    """
    
    def __init__(
        self,
        combat_manager: CombatManager,
        neural_manager: NeuralManager,
        lifecycle_manager: LifecycleManager,
        movement_manager: MovementManager,
        resource_manager: ResourceManager,
        arena: Arena,
        combat_config: Any
    ):
        """
        Initialize the AI manager.
        
        Args:
            combat_manager: For executing attacks
            neural_manager: For neural network decisions
            lifecycle_manager: For handling deaths
            movement_manager: For movement targets
            resource_manager: For finding food
            arena: For boundary checks and random wandering
            combat_config: Combat configuration
        """
        self.combat_manager = combat_manager
        self.neural_manager = neural_manager
        self.lifecycle_manager = lifecycle_manager
        self.movement_manager = movement_manager
        self.resource_manager = resource_manager
        self.arena = arena
        self.combat_config = combat_config
        self.building_manager = None

    def set_building_manager(self, building_manager: Any):
        """Set the building manager reference."""
        self.building_manager = building_manager

    def update_ai(self, creatures: List[Any], all_active_creatures: List[Any], delta_time: float, current_time: float):
        """
        Update AI logic for a list of creatures.
        
        Args:
            creatures: List of creatures to update
            all_active_creatures: All currently active creatures (for context)
            delta_time: Time elapsed
            current_time: Current simulation time
        """
        for creature in creatures:
            if creature.is_alive():
                self._update_creature_logic(creature, all_active_creatures, delta_time, current_time)

    def _update_creature_logic(self, creature: Any, all_alive: List[Any], delta_time: float, current_time: float):
        """
        Update AI logic for a single creature.
        
        Args:
            creature: Creature to update
            all_alive: List of all alive creatures (for context)
            delta_time: Time elapsed
            current_time: Current simulation time
        """
        # 1. Update internal state (cooldowns, etc.)
        creature.last_retarget_time += delta_time
        creature.last_friendship_check += delta_time
        
        # 2. Determine behavior if needed
        if not creature.behavior:
            creature.behavior = creature._determine_behavior()
            
        # 3. Execute Neural Network if intelligent
        if creature.creature.has_trait("Intelligent"):
            self.neural_manager.update_brains([creature], all_alive, delta_time, current_time)
            # Note: update_brains currently doesn't return an action, it's a placeholder.
            # In a real implementation, it would get an action and execute it.
            # For now, we'll fall back to standard behavior if no neural action is taken.
            
        # 4. Standard Behavior Logic
        
        # Building Logic (High Priority if Architect/Builder)
        building_active = False
        if self.building_manager:
            building_active = self._handle_building(creature, all_alive, delta_time, current_time)
            
        if building_active:
            return  # Building takes precedence if active decision made
        
        # For now, just ensure they have a target if aggressive
        if creature.behavior.behavior_type.name == "AGGRESSIVE":
            if not creature.target or not creature.target.is_alive():
                # Simple retargeting
                if creature.last_retarget_time > creature.min_retarget_time:
                    creature.last_retarget_time = 0
                    # Find nearest enemy
                    nearest = None
                    min_dist = float('inf')
                    for other in all_alive:
                        if other != creature and not self._is_ally(creature, other):
                            dist = creature.spatial.distance_to(other.spatial)
                            if dist < min_dist:
                                min_dist = dist
                                nearest = other
                    creature.target = nearest
        
        elif creature.behavior.behavior_type.name == "FORAGER":
            self._handle_foraging(creature, current_time)
            
        elif creature.behavior.behavior_type.name == "WANDERER":
            self._handle_wandering(creature, current_time)
            
        # Fallback: If hungry and not fighting, try to forage regardless of behavior
        if creature.creature.hunger < 50 and not creature.combat_engaged and not creature.target:
             self._handle_foraging(creature, current_time)
             
        # Fallback: If idle, wander
        if not creature.target and not creature.current_movement_target:
            self._handle_wandering(creature, current_time)
        
        # 5. Execute Combat
        if creature.target and creature.target.is_alive():
            # Set focus for UI
            creature.attention.set_focus(StimulusType.COMBAT, current_time)
            
            # Move towards target handled by movement_manager
            # We set the movement entity here, and MovementManager will use it in its update loop
            creature.current_movement_entity = creature.target.spatial
            
            # Attack if in range
            dist = creature.spatial.distance_to(creature.target.spatial)
            if dist <= self.combat_config.base_attack_range_melee:
                if creature.can_attack(current_time):
                    died = self.combat_manager.attempt_attack(creature, creature.target, current_time, all_alive)
                    if died:
                        self.lifecycle_manager.handle_death(creature.target, all_alive, killer=creature, cause="combat")

    def _handle_building(self, creature: Any, all_alive: List[Any], delta_time: float, current_time: float) -> bool:
        """
        Handle building behavior using attention-based priority.
        
        Returns:
            True if building action taken (overrides other behaviors)
        """
        # Get building decision with urgency
        decision = self.building_manager.update_creature_building(creature, all_alive, delta_time)
        
        if not decision or decision.action_type == "NONE":
            return False
        
        # Calculate building priority using attention system
        urgency = decision.metadata.get('urgency', 1.0) if decision.metadata else 1.0
        building_priority = creature.attention.calculate_effective_priority(
            StimulusType.BUILDING,
            urgency_modifier=urgency
        )
        
        # Check if building should win attention (only if not already building)
        if creature.attention.current_focus != StimulusType.BUILDING:
            current_focus = creature.attention.current_focus
            
            # Always allow building if idle or exploring (low priority activities)
            if current_focus in [StimulusType.IDLE, StimulusType.EXPLORING]:
                # Let building happen if creature wants to build
                pass
            else:
                # For other activities, check if building wins attention
                if not creature.attention.should_switch_focus(StimulusType.BUILDING, building_priority, current_time):
                    return False  # Building doesn't win attention
            
        # Execute decision
        if decision.action_type in ["MOVE", "GATHER", "BUILD", "CONSTRUCT"]:
            creature.current_movement_target = decision.target_position
            
            if decision.target_entity:
                # If target is an entity (material), track it
                # But movement manager expects spatial entity
                if hasattr(decision.target_entity, 'position'): # Material
                     # Create a dummy spatial object or just use position
                     creature.current_movement_entity = None # Use static target for now to avoid complexity
                else:
                     creature.current_movement_entity = None
            else:
                creature.current_movement_entity = None
                
            # Set stopping distance based on action
            if decision.action_type == "GATHER":
                creature.target_stopping_distance = 0.5
                creature.attention.set_focus(StimulusType.FORAGING, current_time) # Reusing foraging focus for gathering
            elif decision.action_type in ["BUILD", "CONSTRUCT"]:
                creature.target_stopping_distance = 2.0
                creature.attention.set_focus(StimulusType.BUILDING, current_time)
            else:
                creature.target_stopping_distance = 1.0
                
            return True
            
        return False

    def _is_ally(self, creature1: Any, creature2: Any) -> bool:
        """Check if two creatures are allies."""
        # Simple check for now
        if hasattr(creature1.creature, 'genome_id') and hasattr(creature2.creature, 'genome_id'):
             return creature1.creature.genome_id == creature2.creature.genome_id
        return False

    def _handle_foraging(self, creature: Any, current_time: float):
        """Handle foraging behavior (finding food)."""
        # Don't retarget too often
        if current_time - creature.last_retarget_time < 1.0:
            return
            
        # Find nearest pellet
        # We need access to pellets. ResourceManager has them in self.arena.resources
        # But we should use a spatial query for efficiency if possible.
        # For now, linear search is okay if not too many pellets, but spatial is better.
        
        nearest_pellet = None
        min_dist_sq = float('inf')
        
        # Access pellets directly from arena (via resource manager reference if needed, or direct arena)
        # ResourceManager stores them in arena.resources (mixed list) or arena.pellets (if separated)
        # Let's assume arena.pellets is available or filter resources.
        
        # Optimization: Use spatial grid if available in arena, otherwise linear
        # The arena has a spatial_grid for resources? No, usually separate.
        # Let's use linear search for now as it's robust.
        
        for resource in self.arena.resources:
            # Check if it's a pellet (has nutritional value)
            if hasattr(resource, 'get_nutritional_value'):
                # Check distance
                dx = resource.x - creature.spatial.position.x
                dy = resource.y - creature.spatial.position.y
                dist_sq = dx*dx + dy*dy
                
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    nearest_pellet = resource
        
        if nearest_pellet:
            creature.current_movement_target = Vector2D(nearest_pellet.x, nearest_pellet.y)
            creature.current_movement_entity = None # Static target
            creature.target_stopping_distance = 0.5
            creature.last_retarget_time = current_time
            creature.attention.set_focus(StimulusType.FORAGING, current_time)

    def _handle_wandering(self, creature: Any, current_time: float):
        """Handle wandering behavior (random movement)."""
        # Change direction every few seconds or if reached target
        if not creature.current_movement_target or \
           (creature.spatial.position.distance_to(creature.current_movement_target) < 2.0) or \
           (current_time - creature.last_retarget_time > 5.0):
            
            import random
            # Pick a random point in the arena
            x = random.uniform(0, self.arena.width)
            y = random.uniform(0, self.arena.height)
            
            creature.current_movement_target = Vector2D(x, y)
            creature.current_movement_entity = None
            creature.target_stopping_distance = 0.0
            creature.last_retarget_time = current_time
            creature.attention.set_focus(StimulusType.EXPLORING, current_time)
