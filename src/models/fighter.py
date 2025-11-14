"""
Fighter model for EvoBattle.

Represents a fighter in the evolution battle game with traits and stats.
"""

from typing import List, Optional


class Fighter:
    """
    Represents a fighter in the EvoBattle game.
    
    A fighter has traits that determine their combat effectiveness,
    and participates in battles to pass on their traits to offspring.
    """
    
    def __init__(self, name: str, traits: Optional[List] = None, parent1_id: Optional[str] = None, 
                 parent2_id: Optional[str] = None):
        """
        Initialize a Fighter.
        
        Args:
            name: The fighter's name
            traits: List of Trait objects
            parent1_id: ID of first parent (None for first generation)
            parent2_id: ID of second parent (None for first generation)
        """
        self.id = self._generate_id()
        self.name = name
        self.traits = traits if traits else []
        self.parent1_id = parent1_id
        self.parent2_id = parent2_id
        self.wins = 0
        self.losses = 0
        self.generation = 0
        
        # Calculate generation based on parents
        if parent1_id or parent2_id:
            # Will be set properly when parents are available
            self.generation = 1
    
    def _generate_id(self) -> str:
        """Generate a unique ID for the fighter."""
        import uuid
        return str(uuid.uuid4())
    
    def calculate_power(self) -> float:
        """
        Calculate the fighter's total power based on their traits.
        
        Returns:
            Total power score
        """
        if not self.traits:
            return 0.0
        return sum(trait.power for trait in self.traits)
    
    def add_trait(self, trait) -> None:
        """Add a trait to the fighter."""
        self.traits.append(trait)
    
    def record_win(self) -> None:
        """Record a win for this fighter."""
        self.wins += 1
    
    def record_loss(self) -> None:
        """Record a loss for this fighter."""
        self.losses += 1
    
    def __repr__(self) -> str:
        """String representation of the fighter."""
        return f"Fighter(name='{self.name}', power={self.calculate_power():.2f}, wins={self.wins}, losses={self.losses})"
