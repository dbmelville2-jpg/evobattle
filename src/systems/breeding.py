"""
Breeding system for EvoBattle.

Handles the creation of offspring from parent fighters with trait inheritance.
"""

import random
from typing import List


class BreedingSystem:
    """
    Manages breeding and trait inheritance between fighters.
    
    Creates offspring that inherit traits from parents with some variation.
    """
    
    def __init__(self, mutation_rate: float = 0.2):
        """
        Initialize the breeding system.
        
        Args:
            mutation_rate: Probability of a new random trait appearing (0.0-1.0)
        """
        self.mutation_rate = mutation_rate
        self.breeding_history = []
    
    def breed(self, parent1, parent2, offspring_name: str):
        """
        Create offspring from two parent fighters.
        
        Args:
            parent1: First parent fighter
            parent2: Second parent fighter
            offspring_name: Name for the offspring
            
        Returns:
            New Fighter with inherited traits
        """
        from ..models.fighter import Fighter
        from ..models.trait import Trait
        
        # Inherit traits from both parents
        inherited_traits = []
        
        # Randomly select traits from parent1
        if parent1.traits:
            num_traits_p1 = random.randint(0, len(parent1.traits))
            inherited_traits.extend(random.sample(parent1.traits, num_traits_p1))
        
        # Randomly select traits from parent2
        if parent2.traits:
            num_traits_p2 = random.randint(0, len(parent2.traits))
            inherited_traits.extend(random.sample(parent2.traits, num_traits_p2))
        
        # Chance of mutation (new random trait)
        if random.random() < self.mutation_rate:
            mutation_trait = self._generate_random_trait()
            inherited_traits.append(mutation_trait)
        
        # Create offspring
        offspring = Fighter(
            name=offspring_name,
            traits=inherited_traits,
            parent1_id=parent1.id,
            parent2_id=parent2.id
        )
        
        # Set generation
        offspring.generation = max(parent1.generation, parent2.generation) + 1
        
        # Record breeding
        self.breeding_history.append({
            'parent1': parent1.name,
            'parent2': parent2.name,
            'offspring': offspring.name,
            'generation': offspring.generation
        })
        
        return offspring
    
    def _generate_random_trait(self):
        """
        Generate a random mutation trait.
        
        Returns:
            New Trait with random properties
        """
        from ..models.trait import Trait
        
        trait_names = [
            "Strength", "Agility", "Endurance", "Intelligence", 
            "Speed", "Defense", "Resilience", "Ferocity",
            "Precision", "Vigor"
        ]
        
        name = random.choice(trait_names)
        power = random.uniform(5.0, 20.0)
        
        return Trait(name=name, power=power, description=f"Mutated {name} trait")
    
    def get_breeding_history(self) -> list:
        """
        Get the history of all breeding events.
        
        Returns:
            List of breeding records
        """
        return self.breeding_history
    
    def __repr__(self) -> str:
        """String representation of the breeding system."""
        return f"BreedingSystem(mutation_rate={self.mutation_rate}, breedings={len(self.breeding_history)})"
