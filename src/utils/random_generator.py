"""
Random generator utility - Provides random generation functions for game elements.
"""

import random


class RandomGenerator:
    """
    Utility class for generating random game elements.
    
    Provides methods for generating fighters, traits, attributes, and other
    random elements needed throughout the game. Uses a seed for reproducible
    random sequences when needed for testing or replay.
    
    Attributes:
        seed (int): Random seed for reproducibility (None for true random)
        rng (Random): Python random number generator instance
    """
    
    def __init__(self, seed=None):
        """
        Initialize the RandomGenerator.
        
        Args:
            seed (int): Optional seed for reproducible randomness
        """
        self.seed = seed
        self.rng = random.Random(seed)
    
    def generate_stat(self, min_value=5, max_value=20):
        """
        Generate a random stat value.
        
        Args:
            min_value (int): Minimum stat value
            max_value (int): Maximum stat value
            
        Returns:
            int: Random stat value in the specified range
        """
        return self.rng.randint(min_value, max_value)
    
    def generate_name(self, prefix="Fighter"):
        """
        Generate a random name for a fighter.
        
        Args:
            prefix (str): Prefix for the generated name
            
        Returns:
            str: A randomly generated name
        """
        suffix_number = self.rng.randint(1, 9999)
        return f"{prefix}_{suffix_number:04d}"
    
    def select_random_trait(self, trait_pool):
        """
        Select a random trait from a pool of traits.
        
        Args:
            trait_pool (list): List of available traits
            
        Returns:
            A random trait from the pool, or None if pool is empty
        """
        if not trait_pool:
            return None
        return self.rng.choice(trait_pool)
    
    def random_chance(self, probability):
        """
        Determine if a random event occurs based on probability.
        
        Args:
            probability (float): Probability of the event (0.0 to 1.0)
            
        Returns:
            bool: True if event occurs, False otherwise
        """
        return self.rng.random() < probability
    
    def roll_dice(self, sides=6):
        """
        Simulate rolling a die.
        
        Args:
            sides (int): Number of sides on the die
            
        Returns:
            int: Result of the die roll (1 to sides)
        """
        return self.rng.randint(1, sides)
    
    def __repr__(self):
        """String representation of the RandomGenerator."""
        return f"RandomGenerator(seed={self.seed})"
