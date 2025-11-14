"""
Trait model for EvoBattle.

Represents inheritable traits that affect a fighter's capabilities.
"""

from typing import Optional


class Trait:
    """
    Represents a trait that a fighter can possess.
    
    Traits are inheritable characteristics that affect a fighter's 
    combat effectiveness and can be passed to offspring.
    """
    
    def __init__(self, name: str, power: float, description: Optional[str] = None):
        """
        Initialize a Trait.
        
        Args:
            name: The trait's name
            power: Power value contributed by this trait
            description: Optional description of the trait
        """
        self.name = name
        self.power = power
        self.description = description or f"A trait called {name}"
    
    def __repr__(self) -> str:
        """String representation of the trait."""
        return f"Trait(name='{self.name}', power={self.power:.2f})"
