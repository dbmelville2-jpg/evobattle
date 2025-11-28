"""
Systems package - Game logic for battles and breeding.
"""

from .battle_spatial import SpatialBattle as Battle
from .breeding import Breeding

__all__ = ["Battle", "Breeding"]
