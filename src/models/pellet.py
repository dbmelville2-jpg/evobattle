"""
Pellet model - Represents food/resource agents with traits and evolution.

Pellets are living food sources that reproduce, evolve, and interact with creatures.
Each pellet has traits that affect its nutritional value, reproduction, and behavior.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple, List
import random
import uuid
import time
import math
from .pellet_history import PelletLifeHistory
from .disease import Infection


@dataclass
class PelletTraits:
    """
    Traits that define a pellet's characteristics.
    
    Attributes:
        nutritional_value: Energy provided to creatures when eaten (10-100)
        growth_rate: Probability to reproduce per tick (0.0-1.0)
        spread_radius: Distance offspring can spawn from parent (1-10)
        size: Visual size and affects lifespan (0.5-2.0)
        color: RGB color tuple for visual appearance (0-255 each)
        toxicity: Negative food value, reduces hunger restoration (0.0-1.0)
        palatability: Affects creature preference (0.0-1.0, higher = more preferred)
    """
    nutritional_value: float = 25.0  # Reduced from 40.0 to 25.0 for balance
    growth_rate: float = 0.01
    spread_radius: int = 5
    size: float = 1.0
    color: Tuple[int, int, int] = (100, 200, 100)
    toxicity: float = 0.0
    palatability: float = 0.5
    defense: float = 0.0
    
    def mutate(self, mutation_rate: float = 0.1) -> 'PelletTraits':
        """
        Create a mutated copy of these traits.
        
        Args:
            mutation_rate: Probability and magnitude of mutations (0.0-1.0)
            
        Returns:
            New PelletTraits with possible mutations
        """
        def mutate_value(value: float, min_val: float, max_val: float, mutation_strength: float = 0.2) -> float:
            """Mutate a float value within bounds."""
            if random.random() < mutation_rate:
                change = random.gauss(0, mutation_strength) * (max_val - min_val)
                return max(min_val, min(max_val, value + change))
            return value
        
        def mutate_color(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
            """Mutate color slightly."""
            if random.random() < mutation_rate:
                return tuple(
                    max(0, min(255, c + random.randint(-30, 30)))
                    for c in color
                )
            return color
        
        return PelletTraits(
            nutritional_value=mutate_value(self.nutritional_value, 10.0, 100.0),
            growth_rate=mutate_value(self.growth_rate, 0.001, 0.1, 0.15),
            spread_radius=int(mutate_value(float(self.spread_radius), 1.0, 10.0)),
            size=mutate_value(self.size, 0.5, 2.0, 0.15),
            color=mutate_color(self.color),
            toxicity=mutate_value(self.toxicity, 0.0, 0.5, 0.1),
            palatability=mutate_value(self.palatability, 0.1, 1.0, 0.15),
            defense=mutate_value(self.defense, 0.0, 0.5, 0.1)
        )
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            'nutritional_value': self.nutritional_value,
            'growth_rate': self.growth_rate,
            'spread_radius': self.spread_radius,
            'size': self.size,
            'color': self.color,
            'toxicity': self.toxicity,
            'palatability': self.palatability,
            'defense': self.defense
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'PelletTraits':
        """Deserialize from dictionary."""
        return PelletTraits(**data)


@dataclass
class Pellet:
    """
    Represents a food pellet agent with traits and lifecycle.
    
    Pellets are living resources that reproduce, age, and evolve. They provide
    food for creatures and form their own evolving ecosystem.
    
    Attributes:
        pellet_id: Unique identifier
        x: X position in arena
        y: Y position in arena
        traits: PelletTraits defining characteristics
        age: Age in simulation ticks
        max_age: Maximum age before natural death (optional, None = immortal unless eaten)
        born_time: Simulation time when pellet was created
        parent_id: ID of parent pellet (None if initial spawn)
        generation: How many generations from initial pellets
        history: PelletLifeHistory tracking lifecycle events
    """
    pellet_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    x: float = 0.0
    y: float = 0.0
    traits: PelletTraits = field(default_factory=PelletTraits)
    age: int = 0
    max_age: Optional[int] = None
    born_time: float = field(default_factory=time.time)
    parent_id: Optional[str] = None
    generation: int = 0
    history: Optional[PelletLifeHistory] = field(default=None, repr=False)
    active_infection: Optional[Infection] = None
    strain_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Initialize history if not provided."""
        if self.history is None:
            self.history = PelletLifeHistory(self.pellet_id, self.born_time)
    
    def __hash__(self):
        """Make Pellet hashable based on its unique ID."""
        return hash(self.pellet_id)
    
    def __eq__(self, other):
        """Compare Pellets by their unique ID."""
        if not isinstance(other, Pellet):
            return False
        return self.pellet_id == other.pellet_id
    
    def tick(self, delta_time: float = 1.0):
        """
        Update pellet state for one time step.
        
        Args:
            delta_time: Time elapsed since last tick
        """
        self.age += 1
    
    def can_reproduce(self, local_pellet_count: int, carrying_capacity: int = 100) -> bool:
        """
        Check if pellet can reproduce based on growth rate and local density.
        
        Args:
            local_pellet_count: Number of pellets in local area
            carrying_capacity: Maximum pellets in area before reproduction stops
            
        Returns:
            True if reproduction should occur
        """
        # Can't reproduce if at carrying capacity
        if local_pellet_count >= carrying_capacity:
            return False
        
        # Density reduces reproduction probability
        density_factor = 1.0 - (local_pellet_count / carrying_capacity)
        effective_growth_rate = self.traits.growth_rate * density_factor
        
        return random.random() < effective_growth_rate
    
    def reproduce(self, mutation_rate: float = 0.15, partner: Optional['Pellet'] = None) -> 'Pellet':
        """
        Create offspring pellet with inherited and mutated traits.
        
        Supports both asexual (single parent) and sexual (two parents) reproduction.
        
        Args:
            mutation_rate: Probability and magnitude of trait mutations
            partner: Optional second parent for sexual reproduction
            
        Returns:
            New Pellet offspring
        """
        from .genetics import PelletGenetics
        
        # Offspring spawns near parent within spread_radius
        # Use polar coordinates to ensure distance constraint is met
        angle = random.uniform(0, 2 * 3.14159)
        distance = random.uniform(0, self.traits.spread_radius)
        offset_x = distance * math.cos(angle)
        offset_y = distance * math.sin(angle)
        
        # Use genetics engine for trait inheritance
        genetics = PelletGenetics(mutation_rate=mutation_rate)
        offspring_traits = genetics.combine_pellet_traits(self, partner)
        
        # Determine strain ID
        # Strain Compression: Only create new strain if traits are significantly different
        
        # Calculate trait difference
        diff = 0.0
        diff += abs(offspring_traits.nutritional_value - self.traits.nutritional_value) / 10.0 # Normalize roughly
        diff += abs(offspring_traits.growth_rate - self.traits.growth_rate) * 5.0
        diff += abs(offspring_traits.toxicity - self.traits.toxicity) * 2.0
        diff += abs(offspring_traits.defense - self.traits.defense) * 2.0
        
        # Color difference
        c_diff = sum(abs(a - b) for a, b in zip(offspring_traits.color, self.traits.color))
        diff += c_diff / 50.0
        
        strain_threshold = 1.5 # Threshold for declaring a new strain
        
        if partner:
            # Sexual reproduction: chance to start new strain or inherit from one parent
            # If traits are very different from both parents, new strain
            p_diff = 0.0
            p_diff += abs(offspring_traits.nutritional_value - partner.traits.nutritional_value) / 10.0
            # ... (simplified check against partner)
            
            if diff > strain_threshold and random.random() < 0.5:
                 new_strain_id = str(uuid.uuid4())
            else:
                 new_strain_id = random.choice([self.strain_id, partner.strain_id])
        else:
            # Asexual reproduction: inherit strain unless major mutation
            # Only create new strain if difference exceeds threshold AND random chance
            if diff > strain_threshold:
                new_strain_id = str(uuid.uuid4())
            else:
                new_strain_id = self.strain_id
        
        return Pellet(
            x=self.x + offset_x,
            y=self.y + offset_y,
            traits=offspring_traits,
            born_time=time.time(),
            parent_id=self.pellet_id,
            generation=self.generation + 1,
            strain_id=new_strain_id
        )
    
    def is_dead(self) -> bool:
        """
        Check if pellet has died of old age.
        
        Returns:
            True if pellet has exceeded max_age
        """
        if self.max_age is None:
            return False
        return self.age >= self.max_age
    
    def get_nutritional_value(self) -> float:
        """
        Calculate actual nutritional value accounting for toxicity.
        
        Returns:
            Net nutritional value (can be negative if very toxic)
        """
        base_nutrition = self.traits.nutritional_value
        toxicity_penalty = base_nutrition * self.traits.toxicity
        return base_nutrition - toxicity_penalty
    
    def get_palatability_score(self) -> float:
        """
        Get palatability score for creature selection preference.
        
        Higher scores make pellets more likely to be chosen by creatures.
        
        Returns:
            Palatability score (0.0-1.0)
        """
        return self.traits.palatability
    
    def get_display_color(self) -> Tuple[int, int, int]:
        """
        Get color for rendering.
        
        Returns:
            RGB color tuple
        """
        return self.traits.color
    
    def get_display_size(self) -> float:
        """
        Get size for rendering.
        
        Returns:
            Size multiplier for rendering
        """
        return self.traits.size
    
    def get_material_drop(self) -> List['BuildingMaterial']:
        """
        Get building materials that drop when this pellet is consumed.
        
        Larger pellets have a higher chance to drop materials.
        
        Returns:
            List of BuildingMaterial objects (may be empty)
        """
        from .building.building_material import BuildingMaterial, MaterialType
        from .spatial import Vector2D
        import random
        import uuid
        
        materials = []
        
        # Drop chance based on size
        drop_chance = min(0.5, self.traits.size * 0.3)  # 30% for size 1.0, 60% for size 2.0
        
        if random.random() < drop_chance:
            # Randomly choose material type
            material_type = random.choice(list(MaterialType))
            
            # Create material at pellet position (will be offset by caller)
            material = BuildingMaterial(
                material_id=str(uuid.uuid4()),
                material_type=material_type,
                position=Vector2D(self.x, self.y),
                source_id=self.pellet_id
            )
            materials.append(material)
        
        return materials
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for persistence."""
        return {
            'pellet_id': self.pellet_id,
            'x': self.x,
            'y': self.y,
            'traits': self.traits.to_dict(),
            'age': self.age,
            'max_age': self.max_age,
            'born_time': self.born_time,
            'parent_id': self.parent_id,
            'generation': self.generation,
            'history': self.history.to_dict() if self.history else None
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Pellet':
        """Deserialize from dictionary."""
        data_copy = data.copy()
        data_copy['traits'] = PelletTraits.from_dict(data_copy['traits'])
        
        # Restore history if present
        if 'history' in data_copy and data_copy['history'] is not None:
            data_copy['history'] = PelletLifeHistory.from_dict(data_copy['history'])
        
        return Pellet(**data_copy)
    
    def __repr__(self):
        """String representation."""
        return (f"Pellet(id={self.pellet_id[:8]}..., gen={self.generation}, "
                f"nutrition={self.traits.nutritional_value:.1f}, "
                f"age={self.age})")


def create_random_pellet(x: float, y: float, generation: int = 0) -> Pellet:
    """
    Create a pellet with randomized traits.
    
    Args:
        x: X position
        y: Y position
        generation: Generation number
        
    Returns:
        New Pellet with random traits
    """
    traits = PelletTraits(
        nutritional_value=random.uniform(15.0, 35.0),  # Reduced from 20-60 to 15-35
        growth_rate=random.uniform(0.005, 0.03),
        spread_radius=random.randint(3, 8),
        size=random.uniform(0.7, 1.3),
        color=(
            random.randint(80, 180),
            random.randint(150, 255),
            random.randint(80, 180)
        ),
        toxicity=random.uniform(0.0, 0.2),
        palatability=random.uniform(0.3, 0.9)
    )
    
    return Pellet(
        x=x,
        y=y,
        traits=traits,
        generation=generation
    )


def create_pellet_from_creature(x: float, y: float, creature_nutritional_value: float = 50.0) -> Pellet:
    """
    Create pellets when a creature dies, with traits influenced by the creature.
    
    When creatures die, their body becomes food. The pellets have higher nutritional
    value based on the creature's size/stats.
    
    Args:
        x: X position (creature death location)
        y: Y position (creature death location)
        creature_nutritional_value: Nutritional value based on creature stats
        
    Returns:
        New Pellet representing creature remains
    """
    # Creature-based pellets have higher nutrition but don't reproduce well
    traits = PelletTraits(
        nutritional_value=creature_nutritional_value,
        growth_rate=0.0,  # Corpses don't reproduce
        spread_radius=1,
        size=random.uniform(1.2, 1.8),  # Larger than plant pellets
        color=(200, 100, 100),  # Reddish/meat color
        toxicity=random.uniform(0.0, 0.1),  # Slight toxicity as it decays
        palatability=0.7  # Fairly palatable
    )
    
    return Pellet(
        x=x,
        y=y,
        traits=traits,
        max_age=100,  # Corpses decay after 100 ticks
        generation=0
    )
