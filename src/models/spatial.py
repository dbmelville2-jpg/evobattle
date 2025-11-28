"""
Spatial components for real-time 2D battle system.

Provides positioning, movement, and collision detection for creatures
in a 2D arena.
"""

import math
from typing import Tuple, Optional, List, Union, TYPE_CHECKING, Dict, Set, TypeVar, Generic
from ..utils.jit_math import calculate_separation_force_fast

if TYPE_CHECKING:
    from .pellet import Pellet

T = TypeVar('T')


class Vector2D:
    """2D vector for position and velocity."""
    __slots__ = ['x', 'y']
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector2D(x={self.x}, y={self.y})"
    
    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __hash__(self) -> int:
        """Make Vector2D hashable for use in sets and dicts."""
        return hash((self.x, self.y))
    
    def __eq__(self, other) -> bool:
        """Compare Vector2D objects for equality."""
        if not isinstance(other, Vector2D):
            return False
        return self.x == other.x and self.y == other.y
    
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
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
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
    __slots__ = ['position', 'velocity', 'radius', 'max_speed', 'acceleration', 'damping']
    
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
        
        # Velocity smoothing for momentum (reduces jitter from AI staggering)
        # Blend 85% old velocity + 15% new velocity for smooth transitions
        smoothing = 0.85
        self.velocity.x = self.velocity.x * smoothing + (self.velocity.x * damping_factor) * (1 - smoothing)
        self.velocity.y = self.velocity.y * smoothing + (self.velocity.y * damping_factor) * (1 - smoothing)
        
        # Update position
        self.position = self.position + (self.velocity * delta_time)
    
    def move_towards(self, target: Vector2D, speed: Optional[float] = None, delta_time: float = 0.016, stopping_distance: float = 0.0):
        """
        Set velocity to move towards a target position with smooth acceleration.
        
        Args:
            target: Target position to move towards
            speed: Movement speed (uses max_speed if None)
            delta_time: Time step for acceleration calculation (default 60fps = 0.016s)
            stopping_distance: Minimum distance to maintain from target (prevents jittering when close)
                              Use negative value to disable stopping/deceleration (for wandering)
        """
        # Calculate distance to target
        distance_to_target = self.position.distance_to(target)
        
        # If stopping_distance is negative, disable all deceleration (for wandering/exploring)
        if stopping_distance < 0:
            # Just move at full speed towards target, no deceleration
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
            return
        
        # If already within stopping distance, slow down instead of continuing to move
        if distance_to_target <= stopping_distance:
            # Apply strong damping to come to a stop quickly
            self.velocity = self.velocity * 0.3
            return
        
        speed = speed or self.max_speed
        direction = (target - self.position).normalized()
        
        # Reduce speed as we approach the stopping distance to enable smooth arrival
        # Use a deceleration zone proportional to max speed for smooth braking
        deceleration_zone = max(3.0, speed * 2.0)  # At least 3 units, or 2x speed
        if distance_to_target < stopping_distance + deceleration_zone:
            # Scale speed based on distance - gradually slow down
            speed_scale = (distance_to_target - stopping_distance) / deceleration_zone
            speed_scale = max(0.05, min(1.0, speed_scale))  # Clamp between 0.05 and 1.0
            speed *= speed_scale
        
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
    


    def calculate_separation_force(self, other: 'SpatialEntity', strength: float = 2.0) -> Vector2D:
        """
        Calculate the separation force vector without applying it.
        
        Args:
            other: The other entity to separate from
            strength: How strong the separation force is
            
        Returns:
            Vector2D representing the force
        """
        fx, fy = calculate_separation_force_fast(
            self.position.x, self.position.y,
            other.position.x, other.position.y,
            self.radius, other.radius,
            strength
        )
        return Vector2D(fx, fy)

    def apply_separation_force(self, other: 'SpatialEntity', strength: float = 2.0):
        """
        Apply a separation force to avoid collision with another entity.
        
        This creates a repulsive force when entities get too close, helping
        them navigate around each other smoothly.
        
        Args:
            other: The other entity to separate from
            strength: How strong the separation force is (higher = stronger push)
        """
        separation_force = self.calculate_separation_force(other, strength)
        
        if separation_force.magnitude() > 0:
            # Apply the force to velocity
            self.velocity = self.velocity + separation_force
            
            # Clamp velocity to max speed
            velocity_magnitude = self.velocity.magnitude()
            if velocity_magnitude > self.max_speed:
                self.velocity = self.velocity.normalized() * self.max_speed


class Arena:
    """
    Represents a 2D battle arena with boundaries.
    
    Attributes:
        width: Arena width
        height: Arena height
        hazards: List of hazard positions
        resources: List of resource positions (Vector2D) or Pellet objects
        pellets: List of Pellet agents (same as resources but typed)
        spatial_grid: Spatial hash grid for efficient proximity queries
    """
    
    def __init__(self, width: float = 100.0, height: float = 100.0, cell_size: Optional[float] = None):
        self.width = width
        self.height = height
        self.hazards: List[Vector2D] = []
        # Support both legacy Vector2D resources and new Pellet agents
        self.resources: List[Union[Vector2D, 'Pellet']] = []
        
        # Spatial hash grid for efficient proximity queries
        # Default cell size is ~10% of smaller dimension, clamped between 5 and 20
        if cell_size is None:
            cell_size = max(5.0, min(20.0, min(width, height) * 0.1))
        self.spatial_grid: SpatialHashGrid[Union[Vector2D, 'Pellet']] = SpatialHashGrid(
            width, height, cell_size
        )
    
    @property
    def pellets(self) -> List['Pellet']:
        """Get only Pellet objects from resources (for type safety)."""
        from .pellet import Pellet
        return [r for r in self.resources if isinstance(r, Pellet)]
    
    def is_within_bounds(self, position: Vector2D) -> bool:
        """Check if a position is within arena bounds."""
        return (0 <= position.x <= self.width and 
                0 <= position.y <= self.height)
    
    def clamp_position(self, position: Vector2D) -> Vector2D:
        """Clamp a position to be within arena bounds."""
        x = max(0, min(self.width, position.x))
        y = max(0, min(self.height, position.y))
        return Vector2D(x, y)
    
    def apply_boundary_repulsion(self, entity: 'SpatialEntity', margin: float = 2.0, strength: float = 1.0):
        """
        Apply a repulsion force to keep entities away from arena boundaries.
        
        This creates a gentle push away from walls to prevent creatures from
        getting stuck at boundaries.
        
        Args:
            entity: The spatial entity to apply repulsion to
            margin: Distance from boundary where repulsion starts
            strength: How strong the repulsion force is
        """
        repulsion = Vector2D(0, 0)
        
        # Check distance to each boundary
        left_dist = entity.position.x
        right_dist = self.width - entity.position.x
        top_dist = entity.position.y
        bottom_dist = self.height - entity.position.y
        
        # Apply repulsion from left boundary
        if left_dist < margin:
            force = ((margin - left_dist) / margin) * strength
            repulsion.x += force
        
        # Apply repulsion from right boundary
        if right_dist < margin:
            force = ((margin - right_dist) / margin) * strength
            repulsion.x -= force
        
        # Apply repulsion from top boundary
        if top_dist < margin:
            force = ((margin - top_dist) / margin) * strength
            repulsion.y += force
        
        # Apply repulsion from bottom boundary
        if bottom_dist < margin:
            force = ((margin - bottom_dist) / margin) * strength
            repulsion.y -= force
        
        # Apply the repulsion to entity's velocity
        if repulsion.magnitude() > 0:
            entity.velocity = entity.velocity + repulsion
            
            # Clamp velocity to max speed
            velocity_magnitude = entity.velocity.magnitude()
            if velocity_magnitude > entity.max_speed:
                entity.velocity = entity.velocity.normalized() * entity.max_speed
    
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
    
    def add_resource(self, resource: Union[Vector2D, 'Pellet']):
        """
        Add a resource at the specified position.
        
        Args:
            resource: Either a Vector2D position or a Pellet object
        """
        self.resources.append(resource)
        # Add to spatial grid
        position = self.get_resource_position(resource)
        self.spatial_grid.insert(resource, position)
    
    def add_pellet(self, pellet: 'Pellet'):
        """
        Add a Pellet agent to the arena.
        
        Args:
            pellet: Pellet object to add
        """
        self.resources.append(pellet)
        # Add to spatial grid
        position = Vector2D(pellet.x, pellet.y)
        self.spatial_grid.insert(pellet, position)
    
    def remove_resource(self, resource: Union[Vector2D, 'Pellet']) -> bool:
        """
        Remove a resource from the arena.
        
        Args:
            resource: Resource to remove
            
        Returns:
            True if resource was found and removed
        """
        try:
            self.resources.remove(resource)
            # Remove from spatial grid
            self.spatial_grid.remove(resource)
            return True
        except ValueError:
            return False
    
    def get_resource_position(self, resource: Union[Vector2D, 'Pellet']) -> Vector2D:
        """
        Get position of a resource (handles both Vector2D and Pellet).
        
        Args:
            resource: Resource object
            
        Returns:
            Vector2D position
        """
        if isinstance(resource, Vector2D):
            return resource
        else:
            # It's a Pellet, get its position
            return Vector2D(resource.x, resource.y)
    
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
    
    def get_nearest_resource(self, position: Vector2D) -> Optional[Tuple[Union[Vector2D, 'Pellet'], float]]:
        """
        Find the nearest resource to a position using spatial hash grid.
        
        Returns:
            Tuple of (resource, distance) or None if no resources
        """
        if not self.resources:
            return None
        
        # Use spatial grid for efficient nearest neighbor search
        result = self.spatial_grid.query_nearest(
            position,
            get_position=self.get_resource_position
        )
        return result
    
    def query_resources_in_radius(
        self,
        position: Vector2D,
        radius: float,
        exclude: Optional[Set[Union[Vector2D, 'Pellet']]] = None
    ) -> List[Union[Vector2D, 'Pellet']]:
        """
        Find all resources within a radius using spatial hash grid.
        
        Args:
            position: Center position to search from
            radius: Search radius
            exclude: Optional set of resources to exclude
            
        Returns:
            List of resources within the radius
        """
        return self.spatial_grid.query_radius(position, radius, exclude)
    
    def update_resource_position(self, resource: Union[Vector2D, 'Pellet']):
        """
        Update a resource's position in the spatial grid.
        
        This should be called when a resource moves (e.g., pellet movement).
        
        Args:
            resource: Resource to update
        """
        position = self.get_resource_position(resource)
        self.spatial_grid.update(resource, position)


class SpatialHashGrid(Generic[T]):
    """
    Spatial hash grid for efficient proximity queries.
    
    Divides 2D space into a grid of cells. Each cell contains entities
    within that region, enabling O(1) cell lookup and O(k) queries where
    k is the number of entities in nearby cells (typically k << n).
    
    This replaces O(n²) all-pairs checks with O(n) broad-phase partitioning.
    
    Attributes:
        cell_size: Size of each grid cell
        width: Total grid width
        height: Total grid height
        grid: Dictionary mapping (cell_hash) to set of entities
    """
    
    # Large prime or multiplier for hashing coordinates into a single integer
    # Assumes grid width < 1,000,000 cells
    HASH_MULTIPLIER = 1000000
    
    def __init__(self, width: float, height: float, cell_size: float = 10.0):
        """
        Initialize spatial hash grid.
        
        Args:
            width: Total width of the spatial area
            height: Total height of the spatial area
            cell_size: Size of each grid cell (smaller = more precise, larger = faster)
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        # Use integer keys for faster hashing than tuples
        self.grid: Dict[int, Set[T]] = {}
        # Cache for entity positions to detect movement
        self._entity_cells: Dict[T, int] = {}
    
    def _get_cell_hash(self, position: Vector2D) -> int:
        """
        Convert world position to grid cell hash.
        
        Args:
            position: World position
            
        Returns:
            Integer hash of the cell coordinates
        """
        cell_x = int(position.x / self.cell_size)
        cell_y = int(position.y / self.cell_size)
        return cell_x + cell_y * self.HASH_MULTIPLIER
    
    def clear(self):
        """Clear all entities from the grid."""
        self.grid.clear()
        self._entity_cells.clear()
    
    def insert(self, entity: T, position: Vector2D):
        """
        Insert an entity at the given position.
        
        Args:
            entity: Entity to insert
            position: World position of the entity
        """
        cell_hash = self._get_cell_hash(position)
        
        # Remove from old cell if entity already exists
        if entity in self._entity_cells:
            old_hash = self._entity_cells[entity]
            if old_hash != cell_hash and old_hash in self.grid:
                self.grid[old_hash].discard(entity)
        
        # Add to new cell
        if cell_hash not in self.grid:
            self.grid[cell_hash] = set()
        self.grid[cell_hash].add(entity)
        self._entity_cells[entity] = cell_hash
    
    def remove(self, entity: T):
        """
        Remove an entity from the grid.
        
        Args:
            entity: Entity to remove
        """
        if entity in self._entity_cells:
            cell_hash = self._entity_cells[entity]
            if cell_hash in self.grid:
                self.grid[cell_hash].discard(entity)
                if not self.grid[cell_hash]:
                    del self.grid[cell_hash]
            del self._entity_cells[entity]
    
    def update(self, entity: T, position: Vector2D):
        """
        Update an entity's position in the grid.
        
        This is more efficient than remove + insert if the entity
        stays in the same cell.
        
        Args:
            entity: Entity to update
            position: New world position
        """
        # t0 = time.time()
        new_hash = self._get_cell_hash(position)
        
        if entity in self._entity_cells:
            old_hash = self._entity_cells[entity]
            if old_hash == new_hash:
                # Still in same cell, no update needed
                return
            
            # Remove from old cell
            if old_hash in self.grid:
                self.grid[old_hash].discard(entity)
                if not self.grid[old_hash]:
                    del self.grid[old_hash]
        
        # Add to new cell
        if new_hash not in self.grid:
            self.grid[new_hash] = set()
        self.grid[new_hash].add(entity)
        self._entity_cells[entity] = new_hash
        # t1 = time.time()
        # if (t1 - t0) * 1000 > 1.0:
        #     print(f"Slow grid update: {(t1-t0)*1000:.2f}ms")
    
    def query_radius(
        self,
        position: Vector2D,
        radius: float,
        exclude: Optional[Set[T]] = None,
        exact_distance: bool = False,
        get_position: Optional[callable] = None
    ) -> List[T]:
        """
        Find all entities within a radius of a position.
        
        Args:
            position: Center position to search from
            radius: Search radius
            exclude: Optional set of entities to exclude from results
            exact_distance: If True, filter by exact distance (slower but more accurate)
            get_position: Function to get position from entity (required if exact_distance=True)
            
        Returns:
            List of entities within the radius (or bounding box if exact_distance=False)
        """
        exclude = exclude or set()
        results = []
        seen = set()  # Track entities we've already added
        
        # Calculate which cells to check (bounding box around radius)
        min_cell_x = int((position.x - radius) / self.cell_size)
        max_cell_x = int((position.x + radius) / self.cell_size)
        min_cell_y = int((position.y - radius) / self.cell_size)
        max_cell_y = int((position.y + radius) / self.cell_size)
        
        # Check each cell in the bounding box
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                cell_hash = cell_x + cell_y * self.HASH_MULTIPLIER
                if cell_hash in self.grid:
                    for entity in self.grid[cell_hash]:
                        if entity not in exclude and entity not in seen:
                            # Optionally filter by exact distance
                            if exact_distance:
                                # Get entity position
                                if get_position:
                                    entity_pos = get_position(entity)
                                elif hasattr(entity, 'position'):
                                    entity_pos = entity.position
                                elif hasattr(entity, 'spatial'):
                                    entity_pos = entity.spatial.position
                                elif isinstance(entity, Vector2D):
                                    entity_pos = entity
                                else:
                                    continue
                                
                                # Inline distance check for performance
                                dx = position.x - entity_pos.x
                                dy = position.y - entity_pos.y
                                if dx*dx + dy*dy <= radius * radius:
                                    results.append(entity)
                                    seen.add(entity)
                            else:
                                results.append(entity)
                                seen.add(entity)

        
        return results
    
    def query_nearest(
        self,
        position: Vector2D,
        max_distance: float = float('inf'),
        exclude: Optional[Set[T]] = None,
        get_position: Optional[callable] = None
    ) -> Optional[Tuple[T, float]]:
        """
        Find the nearest entity to a position.
        
        Args:
            position: Position to search from
            max_distance: Maximum search distance
            exclude: Optional set of entities to exclude
            get_position: Function to get position from entity (if not SpatialEntity)
            
        Returns:
            Tuple of (nearest_entity, distance) or None
        """
        exclude = exclude or set()
        
        # Start with cells near the position and expand outward
        search_radius = min(max_distance, self.cell_size * 2)
        max_search_radius = max_distance
        
        nearest_entity = None
        nearest_distance = float('inf')
        
        while search_radius <= max_search_radius:
            candidates = self.query_radius(position, search_radius, exclude)
            
            for entity in candidates:
                # Get entity position
                if get_position:
                    entity_pos = get_position(entity)
                elif hasattr(entity, 'position'):
                    entity_pos = entity.position
                elif hasattr(entity, 'spatial'):
                    entity_pos = entity.spatial.position
                else:
                    continue
                
                distance = position.distance_to(entity_pos)
                if distance < nearest_distance and distance <= max_distance:
                    nearest_distance = distance
                    nearest_entity = entity
            
            # If we found something, we can stop
            if nearest_entity is not None:
                break
            
            # Expand search radius
            if search_radius >= max_search_radius:
                break
            search_radius = min(search_radius * 2, max_search_radius)
        
        if nearest_entity is not None:
            return (nearest_entity, nearest_distance)
        return None
    
    def query_count_in_radius(
        self,
        position: Vector2D,
        radius: float,
        exclude: Optional[Set[T]] = None
    ) -> int:
        """
        Count entities within a radius (optimized for density checks).
        
        Args:
            position: Center position
            radius: Search radius
            exclude: Optional set of entities to exclude
            
        Returns:
            Count of entities within radius
        """
        return len(self.query_radius(position, radius, exclude))
    
    def get_all_entities(self) -> List[T]:
        """
        Get all entities in the grid.
        
        Returns:
            List of all entities
        """
        entities = []
        for cell_entities in self.grid.values():
            entities.extend(cell_entities)
        return entities
