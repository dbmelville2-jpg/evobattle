"""
Spatial components for real-time 2D battle system.

Provides positioning, movement, and collision detection for creatures
in a 2D arena.
"""

import math
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class Vector2D:
    """2D vector for position and velocity."""
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def magnitude(self) -> float:
        """Calculate the length of the vector."""
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalized(self) -> 'Vector2D':
        """Return a unit vector in the same direction."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)
    
    def distance_to(self, other: 'Vector2D') -> float:
        """Calculate distance to another vector."""
        return (self - other).magnitude()
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple."""
        return (self.x, self.y)


class SpatialEntity:
    """
    Represents an entity with position and movement in 2D space.
    
    Attributes:
        position: Current position (x, y)
        velocity: Current velocity vector
        radius: Collision radius
        max_speed: Maximum movement speed
    """
    
    def __init__(
        self,
        position: Optional[Vector2D] = None,
        radius: float = 1.0,
        max_speed: float = 1.0,
        acceleration: float = 5.0,
        damping: float = 0.85
    ):
        self.position = position or Vector2D(0, 0)
        self.velocity = Vector2D(0, 0)
        self.radius = radius
        self.max_speed = max_speed
        self.acceleration = acceleration  # How quickly velocity changes
        self.damping = damping  # Velocity decay per second (0.85 = lose 15% per second)
    
    def update(self, delta_time: float):
        """
        Update position based on velocity with damping.
        
        Args:
            delta_time: Time elapsed since last update (seconds)
        """
        # Apply damping to velocity (exponential decay)
        damping_factor = self.damping ** delta_time
        self.velocity = self.velocity * damping_factor
        
        # Update position
        self.position = self.position + (self.velocity * delta_time)
    
    def move_towards(self, target: Vector2D, speed: Optional[float] = None, delta_time: float = 0.016):
        """
        Set velocity to move towards a target position with smooth acceleration.
        
        Args:
            target: Target position to move towards
            speed: Movement speed (uses max_speed if None)
            delta_time: Time step for acceleration calculation (default 60fps = 0.016s)
        """
        speed = speed or self.max_speed
        direction = (target - self.position).normalized()
        desired_velocity = direction * speed
        
        # Smoothly accelerate towards desired velocity
        velocity_change = (desired_velocity - self.velocity) * self.acceleration * delta_time
        self.velocity = self.velocity + velocity_change
        
        # Clamp velocity to max speed
        velocity_magnitude = self.velocity.magnitude()
        if velocity_magnitude > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed
    
    def stop(self):
        """Stop all movement."""
        self.velocity = Vector2D(0, 0)
    
    def distance_to(self, other: 'SpatialEntity') -> float:
        """Calculate distance to another entity."""
        return self.position.distance_to(other.position)
    
    def is_colliding(self, other: 'SpatialEntity') -> bool:
        """Check if colliding with another entity."""
        distance = self.distance_to(other)
        return distance < (self.radius + other.radius)
    
    def is_within_range(self, other: 'SpatialEntity', range_distance: float) -> bool:
        """Check if another entity is within a specific range."""
        return self.distance_to(other) <= range_distance


class Arena:
    """
    Represents a 2D battle arena with boundaries.
    
    Attributes:
        width: Arena width
        height: Arena height
        hazards: List of hazard positions
        resources: List of resource positions
    """
    
    def __init__(self, width: float = 100.0, height: float = 100.0):
        self.width = width
        self.height = height
        self.hazards: List[Vector2D] = []
        self.resources: List[Vector2D] = []
    
    def is_within_bounds(self, position: Vector2D) -> bool:
        """Check if a position is within arena bounds."""
        return (0 <= position.x <= self.width and 
                0 <= position.y <= self.height)
    
    def clamp_position(self, position: Vector2D) -> Vector2D:
        """Clamp a position to be within arena bounds."""
        x = max(0, min(self.width, position.x))
        y = max(0, min(self.height, position.y))
        return Vector2D(x, y)
    
    def get_random_position(self) -> Vector2D:
        """Get a random position within the arena."""
        import random
        return Vector2D(
            random.uniform(0, self.width),
            random.uniform(0, self.height)
        )
    
    def add_hazard(self, position: Vector2D):
        """Add a hazard at the specified position."""
        self.hazards.append(position)
    
    def add_resource(self, position: Vector2D):
        """Add a resource at the specified position."""
        self.resources.append(position)
    
    def get_nearest_hazard(self, position: Vector2D) -> Optional[Tuple[Vector2D, float]]:
        """
        Find the nearest hazard to a position.
        
        Returns:
            Tuple of (hazard_position, distance) or None if no hazards
        """
        if not self.hazards:
            return None
        
        nearest = min(self.hazards, key=lambda h: position.distance_to(h))
        return (nearest, position.distance_to(nearest))
    
    def get_nearest_resource(self, position: Vector2D) -> Optional[Tuple[Vector2D, float]]:
        """
        Find the nearest resource to a position.
        
        Returns:
            Tuple of (resource_position, distance) or None if no resources
        """
        if not self.resources:
            return None
        
        nearest = min(self.resources, key=lambda r: position.distance_to(r))
        return (nearest, position.distance_to(nearest))
