"""
Pheromone Model - Chemical signals for creature guidance.

Pheromones are temporary environmental markers that can attract or repel creatures.
They decay over time and have a specific type/strength.
"""

from dataclasses import dataclass
from enum import Enum
import time
from typing import Tuple

class PheromoneType(Enum):
    ATTRACT = "attract"  # Pulls creatures towards it
    REPEL = "repel"      # Pushes creatures away
    CONFUSION = "confusion" # Randomizes movement

@dataclass
class Pheromone:
    """
    Represents a chemical signal in the environment.
    """
    position: Tuple[float, float]
    pheromone_type: PheromoneType
    strength: float      # 0.0 to 1.0, affects pull/push force
    radius: float        # Area of effect
    decay_rate: float    # Strength loss per second
    created_at: float
    
    def update(self, dt: float):
        """Update pheromone state (decay)."""
        self.strength -= self.decay_rate * dt
        
    def is_active(self) -> bool:
        """Check if pheromone is still potent enough."""
        return self.strength > 0.01
