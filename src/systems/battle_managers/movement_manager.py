"""
Movement Manager

Handles creature movement, physics, collision avoidance, and spatial updates
for the spatial battle system.

Extracted from battle_spatial.py.
"""

import math
from typing import List, Optional, Any, Set, Tuple

from src.models.spatial import Vector2D, SpatialHashGrid, Arena, SpatialEntity
from src.utils.jit_math import calculate_separation_force_fast
from .environment_manager import EnvironmentManager

class MovementManager:
    """
    Manages movement physics and spatial updates for all creatures.
    
    Responsibilities:
    - Update creature positions based on velocity and forces
    - Handle movement towards targets
    - Calculate and apply separation forces to prevent overlapping
    - Enforce arena boundaries
    - Update spatial grid
    - Apply terrain movement modifiers
    """
    
    def __init__(
        self,
        arena: Arena,
        creature_grid: SpatialHashGrid,
        environment_manager: Optional[EnvironmentManager] = None
    ):
        """
        Initialize the movement manager.
        
        Args:
            arena: Arena for boundary enforcement
            creature_grid: Spatial grid for proximity queries
            environment_manager: Optional manager for terrain effects
        """
        self.arena = arena
        self.creature_grid = creature_grid
        self.environment_manager = environment_manager
        self.buildings = []  # Will be set by battle system
        
    def set_buildings(self, buildings: List[Any]):
        """Update the list of buildings for collision detection."""
        self.buildings = buildings
        
    def update_movement(self, creatures: List[Any], delta_time: float):
        """
        Update movement physics for all creatures.
        
        Args:
            creatures: List of BattleCreature instances
            delta_time: Time elapsed since last update
        """
        for creature in creatures:
            # 1. Update physics (velocity -> position)
            creature.spatial.update(delta_time)
            
            # 2. Handle movement towards target
            # Update movement target if tracking a dynamic entity
            if creature.current_movement_entity:
                creature.current_movement_target = creature.current_movement_entity.position
            
            if creature.current_movement_target:
                # Apply terrain modifier if available
                speed_modifier = 1.0
                if self.environment_manager:
                    speed_modifier = self.environment_manager.get_creature_environmental_adaptation(creature, creature.spatial.position)
                
                # We need to pass speed_modifier to move_towards, but SpatialEntity.move_towards 
                # takes speed (absolute), not a modifier.
                # So we'll adjust the max_speed temporarily or calculate desired speed.
                # Actually, SpatialEntity.move_towards uses max_speed if speed is None.
                # Let's just modify the effective speed.
                effective_speed = creature.spatial.max_speed * speed_modifier
                
                creature.spatial.move_towards(
                    creature.current_movement_target, 
                    speed=effective_speed,
                    delta_time=delta_time,
                    stopping_distance=creature.target_stopping_distance
                )
            
            # 3. Apply separation forces
            self._apply_separation_forces(creature)
                
            # 4. Check barrier collisions and revert if needed
            if self._check_barrier_collision(creature):
                # Revert to previous position and stop movement
                creature.spatial.velocity.x = 0
                creature.spatial.velocity.y = 0
                
            # 5. Enforce boundaries
            self.arena.apply_boundary_repulsion(creature.spatial)
            creature.spatial.position = self.arena.clamp_position(creature.spatial.position)
            
            # 6. Update spatial grid
            self.creature_grid.update(creature, creature.spatial.position)
    
    def _check_barrier_collision(self, creature: Any) -> bool:
        """
        Check if creature is colliding with any barrier building tiles.
        
        Args:
            creature: The BattleCreature to check
            
        Returns:
            True if collision detected, False otherwise
        """
        from src.models.building.building_config import BuildingType
        
        # Only check complete barriers
        for structure in self.buildings:
            if structure.building_type != BuildingType.BARRIER:
                continue
            if not structure.is_complete():
                continue
                
            # Check distance to each tile in the barrier
            for tile_pos in structure.tiles:
                dist_sq = (creature.spatial.position.x - tile_pos.x)**2 + \
                          (creature.spatial.position.y - tile_pos.y)**2
                
                # Collision radius: creature radius + tile size (roughly 2.0 units)
                collision_radius = creature.spatial.radius + 2.0
                if dist_sq < collision_radius * collision_radius:
                    return True
        
        return False

    def _apply_separation_forces(self, creature: Any):
        """
        Calculate and apply separation forces to avoid crowding.
        
        Args:
            creature: The BattleCreature to update
        """
        # Calculate separation forces every 2 frames (performance optimization)
        # Still smooth at 30fps separation updates vs 60fps movement
        creature.separation_update_counter += 1
        if creature.separation_update_counter >= 2:
            creature.separation_update_counter = 0
            
            # Query nearby creatures (using current positions, not cached)
            nearby_for_separation = self.creature_grid.query_radius(
                creature.spatial.position,
                radius=2.5,
                exclude={creature}
            )
            
            # Accumulate separation force components directly
            total_fx = 0.0
            total_fy = 0.0
            for nearby in nearby_for_separation:
                if nearby.is_alive():
                    # Reduce separation strength when engaged in combat with target
                    strength = 0.3 if (creature.combat_engaged and nearby == creature.target) else 1.5
                    
                    # Call JIT function directly for performance
                    fx, fy = calculate_separation_force_fast(
                        creature.spatial.position.x, creature.spatial.position.y,
                        nearby.spatial.position.x, nearby.spatial.position.y,
                        creature.spatial.radius, nearby.spatial.radius,
                        strength
                    )
                    total_fx += fx
                    total_fy += fy
            
            # Apply separation force (only create Vector2D if force is non-zero)
            if total_fx != 0.0 or total_fy != 0.0:
                creature.spatial.velocity.x += total_fx
                creature.spatial.velocity.y += total_fy
                
                # Re-clamp velocity
                vel_mag_sq = creature.spatial.velocity.x ** 2 + creature.spatial.velocity.y ** 2
                max_speed_sq = creature.spatial.max_speed ** 2
                if vel_mag_sq > max_speed_sq:
                    vel_mag = math.sqrt(vel_mag_sq)
                    scale = creature.spatial.max_speed / vel_mag
                    creature.spatial.velocity.x *= scale
                    creature.spatial.velocity.y *= scale
