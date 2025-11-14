"""
Models package - Data models for fighters, traits, and lineage tracking.

This package provides the core game models for EvoBattle:
- Creature system with stats, abilities, and evolution
- Stats and modifiers for buffs/debuffs
- Ability system for skills and moves
- Evolution and genetics systems
- Legacy Fighter, Trait, and Lineage models
"""

# Legacy models (kept for backward compatibility)
from .fighter import Fighter
from .trait import Trait
from .lineage import Lineage

# Core game models
from .stats import Stats, StatModifier, StatGrowth
from .ability import Ability, AbilityType, TargetType, AbilityEffect, create_ability
from .creature import Creature, CreatureType
from .evolution import EvolutionPath, EvolutionSystem, GeneticsSystem, create_example_evolution_system

__all__ = [
    # Legacy models
    "Fighter",
    "Trait",
    "Lineage",
    # Stats system
    "Stats",
    "StatModifier",
    "StatGrowth",
    # Ability system
    "Ability",
    "AbilityType",
    "TargetType",
    "AbilityEffect",
    "create_ability",
    # Creature system
    "Creature",
    "CreatureType",
    # Evolution system
    "EvolutionPath",
    "EvolutionSystem",
    "GeneticsSystem",
    "create_example_evolution_system",
]
