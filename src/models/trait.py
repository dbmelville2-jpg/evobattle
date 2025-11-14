"""
Trait model - Represents inheritable characteristics and abilities.
"""


class Trait:
    """
    Represents a genetic trait that can be inherited by fighters.
    
    Traits modify fighter attributes or provide special abilities during
    battles. They can be passed down through breeding and may mutate or
    combine in offspring.
    
    Attributes:
        name (str): The trait's name
        description (str): What the trait does
        trait_type (str): Category of trait (offensive, defensive, utility, etc.)
        strength_modifier (float): Multiplier for strength stat
        speed_modifier (float): Multiplier for speed stat
        defense_modifier (float): Multiplier for defense stat
        rarity (str): How rare the trait is (common, uncommon, rare, legendary)
    """
    
    def __init__(
        self,
        name="Basic Trait",
        description="A basic trait",
        trait_type="neutral",
        strength_modifier=1.0,
        speed_modifier=1.0,
        defense_modifier=1.0,
        rarity="common"
    ):
        """
        Initialize a new Trait.
        
        Args:
            name (str): The trait's name
            description (str): Description of what the trait does
            trait_type (str): Category of the trait
            strength_modifier (float): Strength stat multiplier
            speed_modifier (float): Speed stat multiplier
            defense_modifier (float): Defense stat multiplier
            rarity (str): Rarity level of the trait
        """
        self.name = name
        self.description = description
        self.trait_type = trait_type
        self.strength_modifier = strength_modifier
        self.speed_modifier = speed_modifier
        self.defense_modifier = defense_modifier
        self.rarity = rarity
    
    def __repr__(self):
        """String representation of the Trait."""
        return f"Trait(name='{self.name}', type='{self.trait_type}', rarity='{self.rarity}')"
