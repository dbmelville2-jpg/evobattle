"""
Random generator utilities for EvoBattle.

Provides utilities for generating random fighters, traits, and names.
"""

import random
from typing import List


class RandomGenerator:
    """
    Utilities for generating random game entities.
    
    Creates random fighters, traits, and names for the game.
    """
    
    # Predefined lists for name generation
    FIRST_NAMES = [
        "Thunder", "Shadow", "Blaze", "Steel", "Storm", "Iron",
        "Lightning", "Dragon", "Phoenix", "Viper", "Wolf", "Tiger",
        "Eagle", "Falcon", "Hawk", "Cobra", "Raptor", "Jaguar"
    ]
    
    LAST_NAMES = [
        "Fist", "Claw", "Strike", "Fury", "Blade", "Hammer",
        "Crusher", "Breaker", "Slayer", "Warrior", "Fighter", "Champion",
        "Hunter", "Destroyer", "Avenger", "Conqueror", "Defender", "Guardian"
    ]
    
    TRAIT_NAMES = [
        "Strength", "Agility", "Endurance", "Intelligence", 
        "Speed", "Defense", "Resilience", "Ferocity",
        "Precision", "Vigor", "Power", "Stamina",
        "Reflexes", "Focus", "Courage", "Tenacity"
    ]
    
    @staticmethod
    def generate_name() -> str:
        """
        Generate a random fighter name.
        
        Returns:
            A random fighter name
        """
        first = random.choice(RandomGenerator.FIRST_NAMES)
        last = random.choice(RandomGenerator.LAST_NAMES)
        return f"{first} {last}"
    
    @staticmethod
    def generate_trait():
        """
        Generate a random trait.
        
        Returns:
            A new Trait with random properties
        """
        from ..models.trait import Trait
        
        name = random.choice(RandomGenerator.TRAIT_NAMES)
        power = random.uniform(5.0, 20.0)
        description = f"A natural {name.lower()} trait"
        
        return Trait(name=name, power=power, description=description)
    
    @staticmethod
    def generate_fighter(name: str = None, num_traits: int = None):
        """
        Generate a random fighter.
        
        Args:
            name: Optional name for the fighter (generates random if None)
            num_traits: Optional number of traits (random 2-5 if None)
            
        Returns:
            A new Fighter with random traits
        """
        from ..models.fighter import Fighter
        
        if name is None:
            name = RandomGenerator.generate_name()
        
        if num_traits is None:
            num_traits = random.randint(2, 5)
        
        traits = [RandomGenerator.generate_trait() for _ in range(num_traits)]
        
        return Fighter(name=name, traits=traits)
    
    @staticmethod
    def generate_fighters(count: int) -> List:
        """
        Generate multiple random fighters.
        
        Args:
            count: Number of fighters to generate
            
        Returns:
            List of Fighter objects
        """
        return [RandomGenerator.generate_fighter() for _ in range(count)]
