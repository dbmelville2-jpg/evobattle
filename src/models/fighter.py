"""
Fighter model - Represents a battle fighter with attributes and traits.
"""


class Fighter:
    """
    Represents a fighter in the EvoBattle game.
    
    A fighter has core attributes (health, strength, speed, etc.) and can
    possess various traits that affect battle performance. Fighters can
    participate in battles, breed with other fighters, and evolve over
    generations through the lineage system.
    
    Attributes:
        name (str): The fighter's name
        health (int): Current health points
        strength (int): Base attack power
        speed (int): Determines action order in battle
        defense (int): Damage mitigation capability
        traits (list): List of Trait objects affecting fighter abilities
    """
    
    def __init__(self, name="Fighter", health=100, strength=10, speed=10, defense=10):
        """
        Initialize a new Fighter.
        
        Args:
            name (str): The fighter's name
            health (int): Starting health points
            strength (int): Base attack power
            speed (int): Speed attribute
            defense (int): Defense attribute
        """
        self.name = name
        self.health = health
        self.strength = strength
        self.speed = speed
        self.defense = defense
        self.traits = []
    
    def __repr__(self):
        """String representation of the Fighter."""
        return f"Fighter(name='{self.name}', health={self.health}, strength={self.strength})"
