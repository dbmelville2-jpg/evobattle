"""
Breeding system - Handles creature reproduction and trait inheritance.
"""

import random
from typing import List, Optional
import time

from ..models.creature import Creature
from ..models.trait import Trait
from ..models.stats import Stats
from ..models.genetics import GeneticsEngine
from .trait_injection import TraitInjectionSystem, InjectionConfig
from src.systems.mutation import apply_tradeoff_mutation


class Breeding:
    """
    Manages creature breeding and genetic trait inheritance.
    
    The breeding system creates offspring from two parent creatures, combining
    their traits and attributes with potential mutations. It integrates with
    the lineage system to track ancestry.
    
    Attributes:
        mutation_rate (float): Probability of trait mutations (0.0 to 1.0)
        trait_inheritance_chance (float): Probability each trait is inherited (0.0 to 1.0)
        trait_inheritance_rules (dict): Rules for how traits are passed down
    """
    
    def __init__(
        self,
        mutation_rate: float = 0.1,
        trait_inheritance_chance: float = 0.8,
        injection_system: Optional[TraitInjectionSystem] = None
    ):
        """
        Initialize the Breeding system.
        
        Args:
            mutation_rate: Base mutation probability
            trait_inheritance_chance: Probability of inheriting each parent trait
            injection_system: Optional trait injection system for random traits
        """
        self.mutation_rate = mutation_rate
        self.trait_inheritance_chance = trait_inheritance_chance
        self.trait_inheritance_rules = {}
        self.genetics_engine = GeneticsEngine(mutation_rate=mutation_rate)
        self.generation_counter = 0
        self.injection_system = injection_system
    
    def breed(
        self,
        parent1: Creature,
        parent2: Creature,
        birth_time: Optional[float] = None
    ) -> Optional[Creature]:
        """
        Breed two creatures to create offspring.
        
        Uses the enhanced genetics engine to properly combine traits
        from both parents with dominant/recessive gene mechanics.
        
        Args:
            parent1: First parent creature
            parent2: Second parent creature
            birth_time: Birth time for offspring (current time if None)
            
        Returns:
            A new creature offspring, or None if breeding fails
        """
        # Check if both parents can breed
        if not parent1.can_breed() or not parent2.can_breed():
            return None
        
        # Increment generation counter
        self.generation_counter += 1
        
        # Calculate inherited traits using new genetics engine
        inherited_traits = self.genetics_engine.combine_traits(
            parent1,
            parent2,
            generation=self.generation_counter
        )
        
        # Check for random trait injection
        if self.injection_system is not None:
            injected_trait = self.injection_system.inject_breeding_trait(
                parent1,
                parent2,
                self.generation_counter
            )
            if injected_trait is not None:
                inherited_traits.append(injected_trait)
        
        # Inherit stats using genetics engine (blends both parents)
        child_stats = self.genetics_engine.combine_stats(parent1, parent2)
        
        # Calculate child hue (average with mutation)
        child_hue = (parent1.hue + parent2.hue) / 2.0
        child_hue += random.uniform(-15, 15)  # Mutation range
        child_hue = child_hue % 360  # Wrap around
        
        # Determine strain_id (inherit from parent or create new strain on major mutation)
        # If parents are same strain, child inherits it unless major mutation occurs
        if parent1.strain_id == parent2.strain_id:
            # Same strain - small chance of mutation creating new strain
            if random.random() < self.mutation_rate * 0.3:  # 3% chance with default mutation_rate
                child_strain_id = None  # Will create new strain
            else:
                child_strain_id = parent1.strain_id
        else:
            # Different strains - inherit from random parent
            child_strain_id = random.choice([parent1.strain_id, parent2.strain_id])
        
        # Create offspring
        offspring = Creature(
            name=f"{parent1.name[:4]}{parent2.name[:4]}",
            creature_type=parent1.creature_type,  # Inherit type from parent1
            level=1,
            base_stats=child_stats,
            traits=inherited_traits,
            birth_time=birth_time,
            age=0.0,
            mature=False,
            parent_ids=[parent1.creature_id, parent2.creature_id],
            hue=child_hue,
            strain_id=child_strain_id
        )
        
        # Neural Brain Inheritance - Offspring inherit parent brains
        if hasattr(parent1, 'brain') and hasattr(parent2, 'brain'):
            if parent1.brain is not None and parent2.brain is not None:
                # Offspring inherits blended parent brains with mutations
                offspring.brain.inherit_from_parents(parent1.brain, parent2.brain)
        
        return offspring
    

    
    def __repr__(self):
        """String representation of the Breeding system."""
        return f"Breeding(mutation_rate={self.mutation_rate}, inheritance={self.trait_inheritance_chance})"

