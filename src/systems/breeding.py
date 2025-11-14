"""
Breeding system - Handles creature reproduction and trait inheritance.
"""

import random
from typing import List, Optional
import time

from ..models.creature import Creature
from ..models.trait import Trait
from ..models.stats import Stats


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
        trait_inheritance_chance: float = 0.8
    ):
        """
        Initialize the Breeding system.
        
        Args:
            mutation_rate: Base mutation probability
            trait_inheritance_chance: Probability of inheriting each parent trait
        """
        self.mutation_rate = mutation_rate
        self.trait_inheritance_chance = trait_inheritance_chance
        self.trait_inheritance_rules = {}
    
    def breed(
        self,
        parent1: Creature,
        parent2: Creature,
        birth_time: Optional[float] = None
    ) -> Optional[Creature]:
        """
        Breed two creatures to create offspring.
        
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
        
        # Calculate inherited traits
        inherited_traits = self.calculate_inherited_traits(parent1, parent2)
        
        # Inherit stats (average of parents with some variation)
        child_stats = self._inherit_stats(parent1, parent2)
        
        # Calculate child hue (average with mutation)
        child_hue = (parent1.hue + parent2.hue) / 2.0
        child_hue += random.uniform(-15, 15)  # Mutation range
        child_hue = child_hue % 360  # Wrap around
        
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
            hue=child_hue
        )
        
        return offspring
    
    def calculate_inherited_traits(
        self,
        parent1: Creature,
        parent2: Creature
    ) -> List[Trait]:
        """
        Determine which traits the offspring inherits.
        
        Each parent trait has a chance (default 70-90%) to be inherited.
        Mutations may modify inherited traits.
        
        Args:
            parent1: First parent creature
            parent2: Second parent creature
            
        Returns:
            list: Traits to be given to the offspring
        """
        inherited = []
        
        # Combine parent traits
        all_parent_traits = parent1.traits + parent2.traits
        
        # Process each unique trait
        trait_names = set()
        for trait in all_parent_traits:
            # Avoid duplicates
            if trait.name in trait_names:
                continue
            
            # Check inheritance chance (70-90%)
            inheritance_roll = random.uniform(0.7, 0.9)
            if random.random() < inheritance_roll:
                # Inherit the trait
                new_trait = trait  # Could copy if Trait had a copy method
                
                # Apply potential mutation
                if random.random() < self.mutation_rate:
                    new_trait = self.apply_mutation(new_trait)
                
                inherited.append(new_trait)
                trait_names.add(trait.name)
        
        return inherited
    
    def _inherit_stats(self, parent1: Creature, parent2: Creature) -> Stats:
        """
        Calculate inherited stats from parents.
        
        Takes average of parent stats with small random variation.
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Stats for offspring
        """
        p1_stats = parent1.base_stats
        p2_stats = parent2.base_stats
        
        # Average stats with small variation
        avg_hp = (p1_stats.max_hp + p2_stats.max_hp) // 2
        avg_attack = (p1_stats.attack + p2_stats.attack) // 2
        avg_defense = (p1_stats.defense + p2_stats.defense) // 2
        avg_speed = (p1_stats.speed + p2_stats.speed) // 2
        
        # Apply small random variation (-10% to +10%)
        variation = 0.1
        hp = int(avg_hp * random.uniform(1 - variation, 1 + variation))
        attack = int(avg_attack * random.uniform(1 - variation, 1 + variation))
        defense = int(avg_defense * random.uniform(1 - variation, 1 + variation))
        speed = int(avg_speed * random.uniform(1 - variation, 1 + variation))
        
        # Ensure minimum values
        hp = max(10, hp)
        attack = max(1, attack)
        defense = max(1, defense)
        speed = max(1, speed)
        
        return Stats(max_hp=hp, attack=attack, defense=defense, speed=speed)
    
    def apply_mutation(self, trait: Trait) -> Trait:
        """
        Apply random mutation to a trait.
        
        Currently creates a new trait with slightly modified stats.
        In a more complete implementation, this could:
        - Modify trait modifiers
        - Change trait type
        - Create entirely new traits
        
        Args:
            trait: The trait to potentially mutate
            
        Returns:
            The mutated trait (or original if no significant mutation)
        """
        # Apply small modifier changes
        mutation_strength = 0.1  # 10% change
        
        new_strength = trait.strength_modifier * random.uniform(1 - mutation_strength, 1 + mutation_strength)
        new_defense = trait.defense_modifier * random.uniform(1 - mutation_strength, 1 + mutation_strength)
        new_speed = trait.speed_modifier * random.uniform(1 - mutation_strength, 1 + mutation_strength)
        
        # Create mutated trait
        mutated = Trait(
            name=f"{trait.name}+",  # Mark as mutated
            description=f"Mutated {trait.description}",
            trait_type=trait.trait_type,
            strength_modifier=new_strength,
            defense_modifier=new_defense,
            speed_modifier=new_speed,
            rarity=trait.rarity
        )
        
        return mutated
    
    def __repr__(self):
        """String representation of the Breeding system."""
        return f"Breeding(mutation_rate={self.mutation_rate}, inheritance={self.trait_inheritance_chance})"

