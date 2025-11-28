"""
Evolution system for creatures.

Manages evolution paths, genetics, and trait inheritance.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
import random

from .creature import Creature, CreatureType
from .stats import Stats, StatGrowth
from .trait import Trait


@dataclass
class EvolutionPath:
    """
    Defines a possible evolution from one creature type to another.
    
    Attributes:
        from_type (str): Name of the creature type that can evolve
        to_type (str): Name of the evolved form
        min_level (int): Minimum level required
        required_traits (List[str]): Traits that must be present
        conditions (Dict): Other conditions (e.g., time of day, item held)
    """
    from_type: str
    to_type: str
    min_level: int = 10
    required_traits: Optional[List[str]] = None
    conditions: Optional[Dict] = None
    
    def __post_init__(self):
        """Initialize optional fields."""
        if self.required_traits is None:
            self.required_traits = []
        if self.conditions is None:
            self.conditions = {}
    
    def can_evolve(self, creature: Creature) -> bool:
        """
        Check if a creature meets the conditions for this evolution.
        
        Args:
            creature: The creature to check
            
        Returns:
            True if creature can evolve via this path
        """
        # Check type match
        if creature.creature_type.name != self.from_type:
            return False
        
        # Check level requirement
        if creature.level < self.min_level:
            return False
        
        # Check required traits
        for trait_name in self.required_traits:
            if not creature.has_trait(trait_name):
                return False
        
        # Check other conditions
        # (In a full implementation, this would check things like items, time, etc.)
        
        return True
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'from_type': self.from_type,
            'to_type': self.to_type,
            'min_level': self.min_level,
            'required_traits': self.required_traits,
            'conditions': self.conditions
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'EvolutionPath':
        """Deserialize from dictionary."""
        return EvolutionPath(**data)
    
    def __repr__(self):
        """String representation."""
        return f"EvolutionPath({self.from_type} -> {self.to_type} @ Lv{self.min_level})"

# ==============================================================================
# NOTE: GeneticsSystem has been removed (was deprecated)
# ==============================================================================
# Use GeneticsEngine from src.models.genetics instead, or use the Breeding
# system from src.systems.breeding for high-level breeding operations.
# ==============================================================================


class EvolutionSystem:
    """
    Manages creature evolution pathways and transformations.
    
    Tracks available evolution paths and handles the evolution process
    when conditions are met.
    """
    
    def __init__(self):
        """Initialize the evolution system."""
        self.evolution_paths: List[EvolutionPath] = []
        self.creature_types: Dict[str, CreatureType] = {}
    
    def register_creature_type(self, creature_type: CreatureType):
        """
        Register a creature type with the system.
        
        Args:
            creature_type: The creature type to register
        """
        self.creature_types[creature_type.name] = creature_type
    
    def add_evolution_path(self, evolution_path: EvolutionPath):
        """
        Add an evolution path to the system.
        
        Args:
            evolution_path: The evolution path to add
        """
        self.evolution_paths.append(evolution_path)
    
    def get_available_evolutions(self, creature: Creature) -> List[EvolutionPath]:
        """
        Get all evolution paths available to a creature.
        
        Args:
            creature: The creature to check
            
        Returns:
            List of available evolution paths
        """
        available = []
        for path in self.evolution_paths:
            if path.can_evolve(creature):
                available.append(path)
        return available
    
    def can_evolve(self, creature: Creature) -> bool:
        """
        Check if a creature can evolve.
        
        Args:
            creature: The creature to check
            
        Returns:
            True if at least one evolution path is available
        """
        return len(self.get_available_evolutions(creature)) > 0
    
    def evolve(
        self,
        creature: Creature,
        evolution_path: Optional[EvolutionPath] = None
    ) -> Tuple[bool, str]:
        """
        Evolve a creature to its next form.
        
        Args:
            creature: The creature to evolve
            evolution_path: Specific path to use (auto-select if None)
            
        Returns:
            Tuple of (success, message)
        """
        # Get available paths if none specified
        if evolution_path is None:
            available = self.get_available_evolutions(creature)
            if not available:
                return False, "No evolution paths available"
            evolution_path = available[0]  # Use first available
        
        # Check if path is valid for this creature
        if not evolution_path.can_evolve(creature):
            return False, "Evolution conditions not met"
        
        # Get the target type
        target_type_name = evolution_path.to_type
        if target_type_name not in self.creature_types:
            return False, f"Target type '{target_type_name}' not found"
        
        target_type = self.creature_types[target_type_name]
        
        # Perform evolution
        old_name = creature.creature_type.name
        creature.creature_type = target_type
        
        # Recalculate stats for evolved form
        creature.base_stats = target_type.stat_growth.calculate_stats_at_level(
            target_type.base_stats,
            creature.level
        )
        creature.stats = creature.get_effective_stats()
        
        # Fully heal on evolution
        creature.stats.hp = creature.stats.max_hp
        creature.energy = creature.max_energy
        
        return True, f"Evolved from {old_name} to {target_type.name}!"
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'evolution_paths': [path.to_dict() for path in self.evolution_paths],
            'creature_types': {
                name: ctype.to_dict() 
                for name, ctype in self.creature_types.items()
            }
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'EvolutionSystem':
        """Deserialize from dictionary."""
        system = EvolutionSystem()
        
        # Restore creature types
        for name, ctype_data in data.get('creature_types', {}).items():
            system.creature_types[name] = CreatureType.from_dict(ctype_data)
        
        # Restore evolution paths
        for path_data in data.get('evolution_paths', []):
            system.evolution_paths.append(EvolutionPath.from_dict(path_data))
        
        return system
    
    def __repr__(self):
        """String representation."""
        return f"EvolutionSystem(paths={len(self.evolution_paths)}, types={len(self.creature_types)})"


# Example evolution setup
def create_example_evolution_system() -> EvolutionSystem:
    """
    Create an example evolution system with some predefined types and paths.
    
    Returns:
        EvolutionSystem with example data
    """
    system = EvolutionSystem()
    
    # Define base creature type
    base_type = CreatureType(
        name="Newborn",
        description="A newly hatched creature",
        base_stats=Stats(max_hp=80, hp=80, attack=8, defense=8, speed=10),
        stat_growth=StatGrowth(
            hp_growth=12.0,
            attack_growth=2.0,
            defense_growth=2.0,
            speed_growth=1.5
        ),
        type_tags=["normal"],
        evolution_stage=0
    )
    
    # Define evolved forms
    warrior_type = CreatureType(
        name="Warrior",
        description="A creature that evolved focusing on strength",
        base_stats=Stats(max_hp=100, hp=100, attack=15, defense=12, speed=8),
        stat_growth=StatGrowth(
            hp_growth=15.0,
            attack_growth=3.5,
            defense_growth=2.5,
            speed_growth=1.0
        ),
        type_tags=["normal", "fighter"],
        evolution_stage=1
    )
    
    speedster_type = CreatureType(
        name="Speedster",
        description="A creature that evolved focusing on speed",
        base_stats=Stats(max_hp=90, hp=90, attack=12, defense=8, speed=18),
        stat_growth=StatGrowth(
            hp_growth=12.0,
            attack_growth=2.5,
            defense_growth=1.5,
            speed_growth=3.0
        ),
        type_tags=["normal", "swift"],
        evolution_stage=1
    )
    
    # Register types
    system.register_creature_type(base_type)
    system.register_creature_type(warrior_type)
    system.register_creature_type(speedster_type)
    
    # Define evolution paths
    system.add_evolution_path(EvolutionPath(
        from_type="Newborn",
        to_type="Warrior",
        min_level=10,
        conditions={'evolution_type': 'strength'}
    ))
    
    system.add_evolution_path(EvolutionPath(
        from_type="Newborn",
        to_type="Speedster",
        min_level=10,
        conditions={'evolution_type': 'speed'}
    ))
    
    return system
