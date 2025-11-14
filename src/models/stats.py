"""
Stats model - Manages creature statistics and modifiers.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class Stats:
    """
    Represents the core statistics of a creature.
    
    Stats can be modified by buffs, debuffs, traits, and equipment.
    Base stats are the creature's natural values, while effective stats
    include all modifiers.
    
    Attributes:
        hp (int): Health points - creature dies when this reaches 0
        max_hp (int): Maximum health points
        attack (int): Attack power - determines damage dealt
        defense (int): Defense value - reduces damage taken
        speed (int): Speed value - determines turn order and evasion
        special_attack (int): Special attack power for abilities
        special_defense (int): Special defense against abilities
    """
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 10
    speed: int = 10
    special_attack: int = 10
    special_defense: int = 10
    
    def __post_init__(self):
        """Ensure HP doesn't exceed max_hp."""
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    
    def copy(self) -> 'Stats':
        """Create a deep copy of this Stats object."""
        return Stats(
            hp=self.hp,
            max_hp=self.max_hp,
            attack=self.attack,
            defense=self.defense,
            speed=self.speed,
            special_attack=self.special_attack,
            special_defense=self.special_defense
        )
    
    def apply_modifier(self, modifier: 'StatModifier') -> 'Stats':
        """
        Apply a stat modifier to create modified stats.
        
        Args:
            modifier: The StatModifier to apply
            
        Returns:
            New Stats object with modifiers applied
        """
        modified = self.copy()
        modified.attack = int(modified.attack * modifier.attack_multiplier + modifier.attack_bonus)
        modified.defense = int(modified.defense * modifier.defense_multiplier + modifier.defense_bonus)
        modified.speed = int(modified.speed * modifier.speed_multiplier + modifier.speed_bonus)
        modified.special_attack = int(modified.special_attack * modifier.special_attack_multiplier + modifier.special_attack_bonus)
        modified.special_defense = int(modified.special_defense * modifier.special_defense_multiplier + modifier.special_defense_bonus)
        modified.max_hp = int(modified.max_hp * modifier.max_hp_multiplier + modifier.max_hp_bonus)
        # Keep current HP ratio when max_hp changes
        hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 1.0
        modified.hp = int(modified.max_hp * hp_ratio)
        return modified
    
    def heal(self, amount: int) -> int:
        """
        Heal the creature by a specified amount.
        
        Args:
            amount: Amount of HP to restore
            
        Returns:
            Actual amount healed
        """
        old_hp = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        return self.hp - old_hp
    
    def take_damage(self, amount: int) -> int:
        """
        Apply damage to the creature.
        
        Args:
            amount: Amount of damage to apply
            
        Returns:
            Actual damage taken
        """
        old_hp = self.hp
        self.hp = max(0, self.hp - amount)
        return old_hp - self.hp
    
    def is_alive(self) -> bool:
        """Check if the creature is still alive."""
        return self.hp > 0
    
    def to_dict(self) -> Dict:
        """Serialize stats to dictionary."""
        return {
            'hp': self.hp,
            'max_hp': self.max_hp,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'special_attack': self.special_attack,
            'special_defense': self.special_defense
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Stats':
        """Deserialize stats from dictionary."""
        return Stats(**data)
    
    def __repr__(self):
        """String representation of Stats."""
        return (f"Stats(hp={self.hp}/{self.max_hp}, atk={self.attack}, "
                f"def={self.defense}, spd={self.speed})")


@dataclass
class StatModifier:
    """
    Represents a temporary or permanent modification to creature stats.
    
    Modifiers are applied multiplicatively first, then additively.
    Can represent buffs, debuffs, equipment bonuses, or trait effects.
    
    Attributes:
        name (str): Name of the modifier
        duration (int): How many turns the modifier lasts (-1 for permanent)
        attack_multiplier (float): Multiplier for attack stat
        attack_bonus (int): Flat bonus to attack stat
        defense_multiplier (float): Multiplier for defense stat
        defense_bonus (int): Flat bonus to defense stat
        speed_multiplier (float): Multiplier for speed stat
        speed_bonus (int): Flat bonus to speed stat
        special_attack_multiplier (float): Multiplier for special attack
        special_attack_bonus (int): Flat bonus to special attack
        special_defense_multiplier (float): Multiplier for special defense
        special_defense_bonus (int): Flat bonus to special defense
        max_hp_multiplier (float): Multiplier for max HP
        max_hp_bonus (int): Flat bonus to max HP
    """
    name: str = "Modifier"
    duration: int = -1  # -1 means permanent
    attack_multiplier: float = 1.0
    attack_bonus: int = 0
    defense_multiplier: float = 1.0
    defense_bonus: int = 0
    speed_multiplier: float = 1.0
    speed_bonus: int = 0
    special_attack_multiplier: float = 1.0
    special_attack_bonus: int = 0
    special_defense_multiplier: float = 1.0
    special_defense_bonus: int = 0
    max_hp_multiplier: float = 1.0
    max_hp_bonus: int = 0
    
    def is_expired(self) -> bool:
        """Check if this modifier has expired."""
        return self.duration == 0
    
    def tick(self):
        """Decrease duration by 1 turn (if not permanent)."""
        if self.duration > 0:
            self.duration -= 1
    
    def to_dict(self) -> Dict:
        """Serialize modifier to dictionary."""
        return {
            'name': self.name,
            'duration': self.duration,
            'attack_multiplier': self.attack_multiplier,
            'attack_bonus': self.attack_bonus,
            'defense_multiplier': self.defense_multiplier,
            'defense_bonus': self.defense_bonus,
            'speed_multiplier': self.speed_multiplier,
            'speed_bonus': self.speed_bonus,
            'special_attack_multiplier': self.special_attack_multiplier,
            'special_attack_bonus': self.special_attack_bonus,
            'special_defense_multiplier': self.special_defense_multiplier,
            'special_defense_bonus': self.special_defense_bonus,
            'max_hp_multiplier': self.max_hp_multiplier,
            'max_hp_bonus': self.max_hp_bonus
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'StatModifier':
        """Deserialize modifier from dictionary."""
        return StatModifier(**data)
    
    def __repr__(self):
        """String representation of StatModifier."""
        return f"StatModifier(name='{self.name}', duration={self.duration})"


class StatGrowth:
    """
    Manages stat growth over levels/generations.
    
    Defines how a creature's stats increase as it gains experience
    or evolves through generations. Uses growth curves to determine
    stat increases at each level.
    """
    
    def __init__(
        self,
        hp_growth: float = 10.0,
        attack_growth: float = 2.0,
        defense_growth: float = 2.0,
        speed_growth: float = 1.5,
        special_attack_growth: float = 2.0,
        special_defense_growth: float = 2.0,
        growth_curve: str = "medium_fast"
    ):
        """
        Initialize a StatGrowth profile.
        
        Args:
            hp_growth: HP increase per level
            attack_growth: Attack increase per level
            defense_growth: Defense increase per level
            speed_growth: Speed increase per level
            special_attack_growth: Special attack increase per level
            special_defense_growth: Special defense increase per level
            growth_curve: Growth curve type (slow, medium_slow, medium_fast, fast)
        """
        self.hp_growth = hp_growth
        self.attack_growth = attack_growth
        self.defense_growth = defense_growth
        self.speed_growth = speed_growth
        self.special_attack_growth = special_attack_growth
        self.special_defense_growth = special_defense_growth
        self.growth_curve = growth_curve
    
    def calculate_stats_at_level(self, base_stats: Stats, level: int) -> Stats:
        """
        Calculate stats at a specific level.
        
        Args:
            base_stats: Base stats at level 1
            level: Target level
            
        Returns:
            Stats for the specified level
        """
        growth_multiplier = self._get_growth_multiplier(level)
        
        return Stats(
            max_hp=int(base_stats.max_hp + self.hp_growth * (level - 1) * growth_multiplier),
            hp=int(base_stats.max_hp + self.hp_growth * (level - 1) * growth_multiplier),
            attack=int(base_stats.attack + self.attack_growth * (level - 1) * growth_multiplier),
            defense=int(base_stats.defense + self.defense_growth * (level - 1) * growth_multiplier),
            speed=int(base_stats.speed + self.speed_growth * (level - 1) * growth_multiplier),
            special_attack=int(base_stats.special_attack + self.special_attack_growth * (level - 1) * growth_multiplier),
            special_defense=int(base_stats.special_defense + self.special_defense_growth * (level - 1) * growth_multiplier)
        )
    
    def _get_growth_multiplier(self, level: int) -> float:
        """
        Get growth multiplier based on curve type.
        
        Args:
            level: Current level
            
        Returns:
            Multiplier for stat growth
        """
        curves = {
            'slow': 0.8,
            'medium_slow': 0.9,
            'medium_fast': 1.0,
            'fast': 1.2
        }
        return curves.get(self.growth_curve, 1.0)
    
    def to_dict(self) -> Dict:
        """Serialize growth profile to dictionary."""
        return {
            'hp_growth': self.hp_growth,
            'attack_growth': self.attack_growth,
            'defense_growth': self.defense_growth,
            'speed_growth': self.speed_growth,
            'special_attack_growth': self.special_attack_growth,
            'special_defense_growth': self.special_defense_growth,
            'growth_curve': self.growth_curve
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'StatGrowth':
        """Deserialize growth profile from dictionary."""
        return StatGrowth(**data)
    
    def __repr__(self):
        """String representation of StatGrowth."""
        return f"StatGrowth(curve='{self.growth_curve}')"
