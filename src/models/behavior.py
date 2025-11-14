"""
Behavior system for spatial combat.

Defines how creatures behave in the 2D arena based on their traits.
"""

from enum import Enum
from typing import Optional, List
from ..models.spatial import Vector2D, SpatialEntity


class BehaviorType(Enum):
    """Types of behaviors creatures can exhibit."""
    AGGRESSIVE = "aggressive"  # Seeks and attacks enemies
    DEFENSIVE = "defensive"    # Avoids enemies, stays near resources
    TERRITORIAL = "territorial"  # Defends a specific area
    CAUTIOUS = "cautious"      # Avoids hazards and stronger enemies
    RECKLESS = "reckless"      # Ignores hazards, attacks anything
    SUPPORTIVE = "supportive"  # Stays near allies
    WANDERER = "wanderer"      # Moves randomly, explores
    HUNTER = "hunter"          # Targets weakest enemies


class SpatialBehavior:
    """
    Controls creature behavior in spatial combat.
    
    Determines movement decisions, target selection, and reactions
    to the environment based on creature traits.
    """
    
    def __init__(self, behavior_type: BehaviorType = BehaviorType.AGGRESSIVE):
        self.behavior_type = behavior_type
        self.target_position: Optional[Vector2D] = None
        self.home_position: Optional[Vector2D] = None
        self.patrol_radius: float = 10.0
    
    def get_target(
        self,
        entity: SpatialEntity,
        allies: List[SpatialEntity],
        enemies: List[SpatialEntity],
        hazards: List[Vector2D],
        resources: List[Vector2D]
    ) -> Optional[SpatialEntity]:
        """
        Determine which enemy to target based on behavior.
        
        Args:
            entity: The creature making the decision
            allies: List of allied entities
            enemies: List of enemy entities
            hazards: List of hazard positions
            resources: List of resource positions
            
        Returns:
            Target enemy entity or None
        """
        if not enemies:
            return None
        
        if self.behavior_type == BehaviorType.AGGRESSIVE:
            # Target nearest enemy
            return min(enemies, key=lambda e: entity.distance_to(e))
        
        elif self.behavior_type == BehaviorType.HUNTER:
            # Target weakest enemy (we'll need health info for this)
            # For now, target nearest
            return min(enemies, key=lambda e: entity.distance_to(e))
        
        elif self.behavior_type == BehaviorType.CAUTIOUS:
            # Only target nearby enemies, avoid if too many
            nearby_enemies = [e for e in enemies if entity.distance_to(e) < 15.0]
            if len(nearby_enemies) <= 1:
                return min(nearby_enemies, key=lambda e: entity.distance_to(e)) if nearby_enemies else None
            return None
        
        elif self.behavior_type == BehaviorType.DEFENSIVE:
            # Only attack if enemy is very close
            nearest = min(enemies, key=lambda e: entity.distance_to(e))
            if entity.distance_to(nearest) < 5.0:
                return nearest
            return None
        
        elif self.behavior_type == BehaviorType.TERRITORIAL:
            # Attack enemies that enter territory
            if self.home_position:
                for enemy in enemies:
                    if enemy.position.distance_to(self.home_position) < self.patrol_radius:
                        return enemy
            return None
        
        elif self.behavior_type == BehaviorType.RECKLESS:
            # Always target nearest enemy
            return min(enemies, key=lambda e: entity.distance_to(e))
        
        else:
            # Default: target nearest enemy
            return min(enemies, key=lambda e: entity.distance_to(e))
    
    def get_movement_target(
        self,
        entity: SpatialEntity,
        target_enemy: Optional[SpatialEntity],
        allies: List[SpatialEntity],
        enemies: List[SpatialEntity],
        hazards: List[Vector2D],
        resources: List[Vector2D]
    ) -> Optional[Vector2D]:
        """
        Determine where the creature should move.
        
        Args:
            entity: The creature making the decision
            target_enemy: Current combat target (if any)
            allies: List of allied entities
            enemies: List of enemy entities
            hazards: List of hazard positions
            resources: List of resource positions
            
        Returns:
            Target position to move towards or None to stay still
        """
        if self.behavior_type == BehaviorType.AGGRESSIVE:
            if target_enemy:
                return target_enemy.position
            # Move towards nearest enemy
            if enemies:
                nearest = min(enemies, key=lambda e: entity.distance_to(e))
                return nearest.position
        
        elif self.behavior_type == BehaviorType.DEFENSIVE:
            # Move towards nearest resource, away from enemies
            if resources and enemies:
                nearest_resource = min(resources, key=lambda r: entity.position.distance_to(r))
                nearest_enemy = min(enemies, key=lambda e: entity.distance_to(e))
                
                # If enemy is close, move away
                if entity.distance_to(nearest_enemy) < 10.0:
                    # Move in opposite direction
                    away_vector = entity.position - nearest_enemy.position
                    return entity.position + away_vector.normalized() * 5.0
                else:
                    return nearest_resource
        
        elif self.behavior_type == BehaviorType.TERRITORIAL:
            # Stay near home position
            if self.home_position:
                if entity.position.distance_to(self.home_position) > self.patrol_radius:
                    return self.home_position
                # If in territory and enemy nearby, move towards enemy
                if target_enemy and entity.distance_to(target_enemy) < self.patrol_radius:
                    return target_enemy.position
        
        elif self.behavior_type == BehaviorType.CAUTIOUS:
            # Avoid hazards and strong enemies
            if hazards:
                nearest_hazard = min(hazards, key=lambda h: entity.position.distance_to(h))
                if entity.position.distance_to(nearest_hazard) < 8.0:
                    # Move away from hazard
                    away_vector = entity.position - nearest_hazard
                    return entity.position + away_vector.normalized() * 5.0
            
            # Move towards target if safe
            if target_enemy and len([e for e in enemies if entity.distance_to(e) < 15.0]) <= 1:
                return target_enemy.position
        
        elif self.behavior_type == BehaviorType.SUPPORTIVE:
            # Stay near allies
            if allies:
                # Find center of allies
                avg_x = sum(a.position.x for a in allies) / len(allies)
                avg_y = sum(a.position.y for a in allies) / len(allies)
                return Vector2D(avg_x, avg_y)
        
        elif self.behavior_type == BehaviorType.WANDERER:
            # Random exploration
            if not self.target_position or entity.position.distance_to(self.target_position) < 2.0:
                # Set new random target
                import random
                self.target_position = Vector2D(
                    entity.position.x + random.uniform(-20, 20),
                    entity.position.y + random.uniform(-20, 20)
                )
            return self.target_position
        
        elif self.behavior_type == BehaviorType.RECKLESS:
            # Charge at enemies, ignore hazards
            if target_enemy:
                return target_enemy.position
            if enemies:
                return min(enemies, key=lambda e: entity.distance_to(e)).position
        
        return None
    
    def should_use_ability(
        self,
        entity: SpatialEntity,
        target: Optional[SpatialEntity],
        ability_range: float
    ) -> bool:
        """
        Determine if the creature should use an ability.
        
        Args:
            entity: The creature making the decision
            target: Current target
            ability_range: Range of the ability
            
        Returns:
            True if should use ability
        """
        if not target:
            return False
        
        distance = entity.distance_to(target)
        
        if self.behavior_type == BehaviorType.AGGRESSIVE:
            return distance <= ability_range
        
        elif self.behavior_type == BehaviorType.CAUTIOUS:
            # Only use ability if at safe distance
            return ability_range * 0.7 <= distance <= ability_range
        
        elif self.behavior_type == BehaviorType.RECKLESS:
            # Use ability aggressively
            return distance <= ability_range * 1.2
        
        else:
            return distance <= ability_range
