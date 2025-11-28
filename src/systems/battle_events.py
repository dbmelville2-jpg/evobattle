"""
Battle Events Module

Contains event definitions for the battle system.
Extracted from battle_spatial.py to resolve circular imports.
"""

from enum import Enum
from typing import Optional, Dict, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from .battle_spatial import BattleCreature
    from ..models.ability import Ability

class BattleEventType(Enum):
    """Types of battle events for animation/visualization."""
    BATTLE_START = "battle_start"
    CREATURE_SPAWN = "creature_spawn"
    CREATURE_MOVE = "creature_move"
    ABILITY_USE = "ability_use"
    DAMAGE_DEALT = "damage_dealt"
    HEALING = "healing"
    STATUS_APPLIED = "status_applied"
    MISS = "miss"
    CRITICAL_HIT = "critical_hit"
    SUPER_EFFECTIVE = "super_effective"
    NOT_EFFECTIVE = "not_effective"
    CREATURE_FAINT = "creature_faint"
    HAZARD_DAMAGE = "hazard_damage"
    RESOURCE_COLLECTED = "resource_collected"
    CREATURE_BIRTH = "creature_birth"
    CREATURE_DEATH = "creature_death"
    CREATURE_CONSUMED = "creature_consumed"
    BATTLE_END = "battle_end"
    # Pellet lifecycle events
    PELLET_SPAWN = "pellet_spawn"
    PELLET_REPRODUCE = "pellet_reproduce"
    PELLET_CONSUMED = "pellet_consumed"
    PELLET_DEATH = "pellet_death"
    # Attention/focus events
    ATTENTION_CHANGE = "attention_change"


class BattleEvent:
    """
    Represents a single event in battle for animation/visualization.
    """
    
    def __init__(
        self,
        event_type: BattleEventType,
        actor: Optional['BattleCreature'] = None,
        target: Optional['BattleCreature'] = None,
        ability: Optional['Ability'] = None,
        value: Optional[int] = None,
        message: str = "",
        data: Optional[Dict] = None
    ):
        self.event_type = event_type
        self.actor = actor
        self.target = target
        self.ability = ability
        self.value = value
        self.message = message
        self.data = data or {}
        self.timestamp = time.time()
    
    def __repr__(self):
        return f"BattleEvent({self.event_type.value}: {self.message})"
