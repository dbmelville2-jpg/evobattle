"""
Systems package - Game logic for battles, breeding, and betting.
"""

from .battle_spatial import SpatialBattle as Battle
from .breeding import Breeding
from .betting import Betting

__all__ = ["Battle", "Breeding", "Betting"]
