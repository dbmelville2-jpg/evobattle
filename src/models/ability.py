"""
Ability model - Represents skills and special moves that creatures can use.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class AbilityType(Enum):
    """Types of abilities available to creatures."""
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"
    HEALING = "healing"
    BUFF = "buff"
    DEBUFF = "debuff"


class TargetType(Enum):
    """Target types for abilities."""
    SELF = "self"
    ENEMY = "enemy"
    ALLY = "ally"
    ALL_ENEMIES = "all_enemies"
    ALL_ALLIES = "all_allies"
    ALL = "all"


@dataclass
class AbilityEffect:
    """
    Represents an effect that an ability can apply.
    
    Effects can deal damage, heal, apply status conditions, or modify stats.
    
    Attributes:
        effect_type (str): Type of effect (damage, heal, stat_change, status)
        value (int): Base value of the effect
        stat_affected (str): Which stat is affected (for stat changes)
        duration (int): How long the effect lasts (for temporary effects)
        multiplier (float): Multiplier based on caster's stats
    """
    effect_type: str = "damage"
    value: int = 0
    stat_affected: Optional[str] = None
    duration: int = 0
    multiplier: float = 1.0
    
    def to_dict(self) -> Dict:
        """Serialize effect to dictionary."""
        return {
            'effect_type': self.effect_type,
            'value': self.value,
            'stat_affected': self.stat_affected,
            'duration': self.duration,
            'multiplier': self.multiplier
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'AbilityEffect':
        """Deserialize effect from dictionary."""
        return AbilityEffect(**data)
    
    def __repr__(self):
        """String representation of AbilityEffect."""
        return f"AbilityEffect(type='{self.effect_type}', value={self.value})"


class Ability:
    """
    Represents a skill or move that a creature can use in battle.
    
    Abilities can deal damage, heal, buff allies, debuff enemies, or apply
    status conditions. They have cooldowns, costs, and activation conditions.
    
    Attributes:
        name (str): Name of the ability
        description (str): What the ability does
        ability_type (AbilityType): Category of ability
        target_type (TargetType): Who can be targeted
        power (int): Base power of the ability
        accuracy (int): Hit chance (0-100)
        cooldown (int): Turns before ability can be used again
        current_cooldown (int): Current cooldown remaining
        energy_cost (int): Energy/mana cost to use ability
        effects (List[AbilityEffect]): Effects applied by this ability
        conditions (Dict): Conditions that must be met to use ability
    """
    
    def __init__(
        self,
        name: str = "Basic Attack",
        description: str = "A basic attack",
        ability_type: AbilityType = AbilityType.PHYSICAL,
        target_type: TargetType = TargetType.ENEMY,
        power: int = 10,
        accuracy: int = 100,
        cooldown: int = 0,
        energy_cost: int = 0,
        effects: Optional[List[AbilityEffect]] = None,
        conditions: Optional[Dict] = None
    ):
        """
        Initialize a new Ability.
        
        Args:
            name: Name of the ability
            description: Description of what it does
            ability_type: Type/category of ability
            target_type: Valid targets for this ability
            power: Base power value
            accuracy: Hit chance percentage
            cooldown: Turns between uses
            energy_cost: Energy required to use
            effects: List of effects this ability applies
            conditions: Conditions for using the ability
        """
        self.name = name
        self.description = description
        self.ability_type = ability_type
        self.target_type = target_type
        self.power = power
        self.accuracy = accuracy
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.energy_cost = energy_cost
        self.effects = effects if effects is not None else []
        self.conditions = conditions if conditions is not None else {}
    
    def can_use(self, user_stats: 'Stats', user_energy: int = 0) -> bool:
        """
        Check if the ability can currently be used.
        
        Args:
            user_stats: Stats of the creature trying to use the ability
            user_energy: Current energy/mana of the user
            
        Returns:
            True if ability can be used, False otherwise
        """
        # Check cooldown
        if self.current_cooldown > 0:
            return False
        
        # Check energy cost
        if user_energy < self.energy_cost:
            return False
        
        # Check HP threshold if specified
        if 'min_hp_percent' in self.conditions:
            min_hp = self.conditions['min_hp_percent']
            hp_percent = (user_stats.hp / user_stats.max_hp) * 100
            if hp_percent < min_hp:
                return False
        
        # Check stat requirements
        if 'min_attack' in self.conditions and user_stats.attack < self.conditions['min_attack']:
            return False
        if 'min_speed' in self.conditions and user_stats.speed < self.conditions['min_speed']:
            return False
        
        return True
    
    def use(self):
        """
        Use the ability, triggering its cooldown.
        """
        self.current_cooldown = self.cooldown
    
    def tick_cooldown(self):
        """
        Reduce cooldown by 1 turn.
        """
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
    def reset_cooldown(self):
        """
        Reset cooldown to 0 (make ability immediately available).
        """
        self.current_cooldown = 0
    
    def calculate_damage(self, user_attack: int, target_defense: int) -> int:
        """
        Calculate damage dealt by this ability.
        
        Args:
            user_attack: Attacker's attack stat
            target_defense: Target's defense stat
            
        Returns:
            Calculated damage value
        """
        if self.ability_type == AbilityType.PHYSICAL:
            # Physical damage formula
            base_damage = self.power + user_attack
            reduced_damage = max(1, base_damage - (target_defense // 2))
            return reduced_damage
        elif self.ability_type == AbilityType.SPECIAL:
            # Special damage formula (less affected by defense)
            base_damage = self.power + user_attack
            reduced_damage = max(1, base_damage - (target_defense // 4))
            return reduced_damage
        else:
            # Non-damaging ability
            return 0
    
    def copy(self) -> 'Ability':
        """Create a copy of this ability."""
        return Ability(
            name=self.name,
            description=self.description,
            ability_type=self.ability_type,
            target_type=self.target_type,
            power=self.power,
            accuracy=self.accuracy,
            cooldown=self.cooldown,
            energy_cost=self.energy_cost,
            effects=[AbilityEffect(**effect.to_dict()) for effect in self.effects],
            conditions=self.conditions.copy()
        )
    
    def to_dict(self) -> Dict:
        """Serialize ability to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'ability_type': self.ability_type.value if isinstance(self.ability_type, AbilityType) else self.ability_type,
            'target_type': self.target_type.value if isinstance(self.target_type, TargetType) else self.target_type,
            'power': self.power,
            'accuracy': self.accuracy,
            'cooldown': self.cooldown,
            'current_cooldown': self.current_cooldown,
            'energy_cost': self.energy_cost,
            'effects': [effect.to_dict() for effect in self.effects],
            'conditions': self.conditions
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Ability':
        """Deserialize ability from dictionary."""
        data_copy = data.copy()
        # Convert string enums back to enum objects
        if 'ability_type' in data_copy and isinstance(data_copy['ability_type'], str):
            data_copy['ability_type'] = AbilityType(data_copy['ability_type'])
        if 'target_type' in data_copy and isinstance(data_copy['target_type'], str):
            data_copy['target_type'] = TargetType(data_copy['target_type'])
        if 'effects' in data_copy:
            data_copy['effects'] = [AbilityEffect.from_dict(e) for e in data_copy['effects']]
        # Remove current_cooldown from initialization (it's set in __init__)
        data_copy.pop('current_cooldown', None)
        return Ability(**data_copy)
    
    def __repr__(self):
        """String representation of Ability."""
        return f"Ability(name='{self.name}', type={self.ability_type.value}, power={self.power})"


# Predefined abilities that can be used as templates
PREDEFINED_ABILITIES = {
    'tackle': Ability(
        name="Tackle",
        description="A basic physical attack",
        ability_type=AbilityType.PHYSICAL,
        power=40,
        accuracy=100,
        cooldown=0
    ),
    'fireball': Ability(
        name="Fireball",
        description="Launch a ball of fire at the enemy",
        ability_type=AbilityType.SPECIAL,
        power=60,
        accuracy=90,
        cooldown=2,
        energy_cost=10,
        effects=[AbilityEffect(effect_type="damage", value=60)]
    ),
    'heal': Ability(
        name="Heal",
        description="Restore HP to self",
        ability_type=AbilityType.HEALING,
        target_type=TargetType.SELF,
        power=50,
        accuracy=100,
        cooldown=3,
        energy_cost=15,
        effects=[AbilityEffect(effect_type="heal", value=50)]
    ),
    'power_up': Ability(
        name="Power Up",
        description="Increase attack power temporarily",
        ability_type=AbilityType.BUFF,
        target_type=TargetType.SELF,
        power=0,
        accuracy=100,
        cooldown=5,
        energy_cost=10,
        effects=[AbilityEffect(
            effect_type="stat_change",
            value=5,
            stat_affected="attack",
            duration=3
        )]
    ),
    'defense_break': Ability(
        name="Defense Break",
        description="Lower enemy's defense",
        ability_type=AbilityType.DEBUFF,
        power=0,
        accuracy=85,
        cooldown=4,
        energy_cost=12,
        effects=[AbilityEffect(
            effect_type="stat_change",
            value=-5,
            stat_affected="defense",
            duration=3
        )]
    ),
    'quick_strike': Ability(
        name="Quick Strike",
        description="A fast attack that goes first",
        ability_type=AbilityType.PHYSICAL,
        power=30,
        accuracy=95,
        cooldown=1,
        conditions={'min_speed': 15}
    )
}


def create_ability(template_name: str) -> Optional[Ability]:
    """
    Create an ability from a predefined template.
    
    Args:
        template_name: Name of the template ability
        
    Returns:
        A copy of the template ability, or None if not found
    """
    template = PREDEFINED_ABILITIES.get(template_name.lower())
    return template.copy() if template else None
