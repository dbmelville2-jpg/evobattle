"""
Models package - Data models for fighters, traits, and lineage tracking.

This package provides the core game models for EvoBattle:
- Creature system with stats, abilities, and evolution
- Stats and modifiers for buffs/debuffs
- Ability system for skills and moves
- Evolution and genetics systems
- Environmental simulation (weather, terrain, hazards, day/night)
- Legacy Fighter, Trait, and Lineage models
"""

# Core game models
from .stats import Stats, StatModifier, StatGrowth
from .ability import Ability, AbilityType, TargetType, AbilityEffect, create_ability
from .creature import Creature, CreatureType
from .evolution import EvolutionPath, EvolutionSystem, create_example_evolution_system
from .pellet import Pellet, PelletTraits, create_random_pellet, create_pellet_from_creature

# Environmental simulation
from .environment import (
    Environment, WeatherConditions, WeatherType, TerrainType, TerrainCell,
    TimeOfDay, DayNightCycle, HazardType, EnvironmentalHazard
)

__all__ = [
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
    "create_example_evolution_system",
    # Pellet system
    "Pellet",
    "PelletTraits",
    "create_random_pellet",
    "create_pellet_from_creature",
    # Environmental system
    "Environment",
    "WeatherConditions",
    "WeatherType",
    "TerrainType",
    "TerrainCell",
    "TimeOfDay",
    "DayNightCycle",
    "HazardType",
    "EnvironmentalHazard",
]
