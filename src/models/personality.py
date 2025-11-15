"""
Personality System - Traits that affect AI behavior and decision making.

Creatures have unique personalities that influence how they fight, explore,
and interact with others, creating diverse and memorable behaviors.
"""

from typing import Dict, Optional
from dataclasses import dataclass
import random


@dataclass
class PersonalityProfile:
    """
    Defines a creature's personality traits.
    
    Each trait ranges from 0.0 to 1.0 and affects behavior in different ways.
    
    Attributes:
        aggression: High = attacks more, targets strong enemies; Low = defensive
        caution: High = retreats early, plays safe; Low = fights to death
        loyalty: High = protects allies, fights for family; Low = self-preservation
        ambition: High = seeks challenges, gains more XP; Low = avoids risk
        curiosity: High = explores, tries new tactics; Low = sticks to patterns
        pride: High = refuses to retreat, seeks glory; Low = pragmatic
        compassion: High = helps wounded allies; Low = fights independently
    """
    aggression: float = 0.5      # 0 = passive, 1 = very aggressive
    caution: float = 0.5         # 0 = reckless, 1 = very cautious
    loyalty: float = 0.5         # 0 = selfish, 1 = very loyal
    ambition: float = 0.5        # 0 = passive, 1 = very ambitious
    curiosity: float = 0.5       # 0 = routine, 1 = very curious
    pride: float = 0.5           # 0 = humble, 1 = very proud
    compassion: float = 0.5      # 0 = ruthless, 1 = very compassionate
    
    def __post_init__(self):
        """Ensure all values are in valid range."""
        self.aggression = max(0.0, min(1.0, self.aggression))
        self.caution = max(0.0, min(1.0, self.caution))
        self.loyalty = max(0.0, min(1.0, self.loyalty))
        self.ambition = max(0.0, min(1.0, self.ambition))
        self.curiosity = max(0.0, min(1.0, self.curiosity))
        self.pride = max(0.0, min(1.0, self.pride))
        self.compassion = max(0.0, min(1.0, self.compassion))
    
    @staticmethod
    def random() -> 'PersonalityProfile':
        """Generate a random personality."""
        return PersonalityProfile(
            aggression=random.uniform(0.2, 0.8),
            caution=random.uniform(0.2, 0.8),
            loyalty=random.uniform(0.2, 0.8),
            ambition=random.uniform(0.2, 0.8),
            curiosity=random.uniform(0.2, 0.8),
            pride=random.uniform(0.2, 0.8),
            compassion=random.uniform(0.2, 0.8)
        )
    
    @staticmethod
    def inherit(parent1: 'PersonalityProfile', parent2: 'PersonalityProfile', mutation_rate: float = 0.1) -> 'PersonalityProfile':
        """
        Create a child personality by inheriting from two parents.
        
        Args:
            parent1: First parent's personality
            parent2: Second parent's personality
            mutation_rate: Chance of random mutation (0-1)
            
        Returns:
            New personality profile
        """
        def inherit_trait(trait1: float, trait2: float) -> float:
            """Inherit a single trait with potential mutation."""
            # Average of parents with slight random variation
            base = (trait1 + trait2) / 2.0
            
            # Mutation
            if random.random() < mutation_rate:
                base += random.uniform(-0.2, 0.2)
            
            return max(0.0, min(1.0, base))
        
        return PersonalityProfile(
            aggression=inherit_trait(parent1.aggression, parent2.aggression),
            caution=inherit_trait(parent1.caution, parent2.caution),
            loyalty=inherit_trait(parent1.loyalty, parent2.loyalty),
            ambition=inherit_trait(parent1.ambition, parent2.ambition),
            curiosity=inherit_trait(parent1.curiosity, parent2.curiosity),
            pride=inherit_trait(parent1.pride, parent2.pride),
            compassion=inherit_trait(parent1.compassion, parent2.compassion)
        )
    
    def get_combat_style(self) -> str:
        """
        Get a description of this creature's combat style.
        
        Returns:
            Human-readable combat style description
        """
        styles = []
        
        if self.aggression > 0.7:
            styles.append("aggressive")
        elif self.aggression < 0.3:
            styles.append("defensive")
        
        if self.caution > 0.7:
            styles.append("cautious")
        elif self.caution < 0.3:
            styles.append("reckless")
        
        if self.pride > 0.7:
            styles.append("proud")
        elif self.pride < 0.3:
            styles.append("humble")
        
        if self.loyalty > 0.7:
            styles.append("loyal")
        elif self.loyalty < 0.3:
            styles.append("selfish")
        
        if len(styles) == 0:
            return "balanced"
        
        return " and ".join(styles)
    
    def should_retreat(self, hp_percent: float, enemy_count: int) -> bool:
        """
        Determine if creature should retreat based on personality.
        
        Args:
            hp_percent: Current HP as percentage (0-1)
            enemy_count: Number of enemies
            
        Returns:
            True if should retreat
        """
        # Cautious creatures retreat earlier
        # Proud creatures refuse to retreat
        # More enemies makes cautious creatures more likely to retreat
        
        base_threshold = 0.2  # Retreat at 20% HP by default
        
        # Caution raises threshold (retreat earlier)
        threshold = base_threshold + (self.caution * 0.3)
        
        # Pride lowers threshold (retreat later)
        threshold -= self.pride * 0.15
        
        # Multiple enemies affects cautious creatures
        if enemy_count > 1:
            threshold += self.caution * 0.1 * (enemy_count - 1)
        
        return hp_percent < threshold
    
    def get_target_preference(self, enemies: list) -> Optional[int]:
        """
        Choose which enemy to target based on personality.
        
        Args:
            enemies: List of enemy creatures with their stats
            
        Returns:
            Index of preferred target, or None for random selection
        """
        if not enemies:
            return None
        
        # Aggressive creatures target the strongest
        if self.aggression > 0.7:
            # Target highest attack
            return max(range(len(enemies)), key=lambda i: getattr(enemies[i], 'attack', 0))
        
        # Cautious creatures target the weakest
        if self.caution > 0.7:
            # Target lowest HP
            return min(range(len(enemies)), key=lambda i: getattr(enemies[i], 'hp', float('inf')))
        
        # Ambitious creatures target highest level
        if self.ambition > 0.7:
            # Target highest level/power
            return max(range(len(enemies)), key=lambda i: getattr(enemies[i], 'level', 1))
        
        # Default: no preference
        return None
    
    def get_exploration_tendency(self) -> float:
        """
        Get how much this creature likes to explore.
        
        Returns:
            Exploration factor (0-1)
        """
        # Curious and ambitious creatures explore more
        return (self.curiosity + self.ambition) / 2.0
    
    def get_team_fight_bonus(self, has_allies: bool, has_family: bool) -> float:
        """
        Get combat bonus when fighting with allies.
        
        Args:
            has_allies: Whether fighting with allies
            has_family: Whether fighting with family members
            
        Returns:
            Damage multiplier (1.0 = no bonus)
        """
        if not has_allies:
            return 1.0
        
        bonus = 1.0
        
        # Loyal creatures fight better with allies
        if self.loyalty > 0.5:
            bonus += (self.loyalty - 0.5) * 0.2  # Up to +10% with max loyalty
        
        # Extra bonus for family
        if has_family and self.loyalty > 0.5:
            bonus += (self.loyalty - 0.5) * 0.1  # Additional +5% with family
        
        return bonus
    
    def get_revenge_bonus(self, is_revenge: bool) -> float:
        """
        Get combat bonus when fighting for revenge.
        
        Args:
            is_revenge: Whether this is a revenge fight
            
        Returns:
            Damage multiplier (1.0 = no bonus)
        """
        if not is_revenge:
            return 1.0
        
        # Loyal and proud creatures fight harder for revenge
        revenge_factor = (self.loyalty + self.pride) / 2.0
        return 1.0 + revenge_factor * 0.3  # Up to +30% damage
    
    def get_critical_hit_chance_modifier(self) -> float:
        """
        Get modifier to critical hit chance based on personality.
        
        Returns:
            Percentage point modifier (-10 to +10)
        """
        # Aggressive and reckless (low caution) creatures crit more
        return ((self.aggression - 0.5) * 10) + ((0.5 - self.caution) * 5)
    
    def get_dodge_chance_modifier(self) -> float:
        """
        Get modifier to dodge chance based on personality.
        
        Returns:
            Percentage point modifier (-10 to +10)
        """
        # Cautious creatures dodge better
        return (self.caution - 0.5) * 20
    
    def get_description(self) -> str:
        """
        Get a human-readable personality description.
        
        Returns:
            Personality description
        """
        traits = []
        
        if self.aggression > 0.7:
            traits.append("very aggressive")
        elif self.aggression > 0.6:
            traits.append("aggressive")
        elif self.aggression < 0.3:
            traits.append("passive")
        
        if self.caution > 0.7:
            traits.append("very cautious")
        elif self.caution > 0.6:
            traits.append("cautious")
        elif self.caution < 0.3:
            traits.append("reckless")
        
        if self.loyalty > 0.7:
            traits.append("fiercely loyal")
        elif self.loyalty > 0.6:
            traits.append("loyal")
        elif self.loyalty < 0.3:
            traits.append("selfish")
        
        if self.pride > 0.7:
            traits.append("very proud")
        elif self.pride > 0.6:
            traits.append("proud")
        
        if self.curiosity > 0.7:
            traits.append("very curious")
        elif self.curiosity > 0.6:
            traits.append("curious")
        
        if self.compassion > 0.7:
            traits.append("compassionate")
        elif self.compassion < 0.3:
            traits.append("ruthless")
        
        if len(traits) == 0:
            return "balanced personality"
        
        return ", ".join(traits)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'aggression': self.aggression,
            'caution': self.caution,
            'loyalty': self.loyalty,
            'ambition': self.ambition,
            'curiosity': self.curiosity,
            'pride': self.pride,
            'compassion': self.compassion
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'PersonalityProfile':
        """Deserialize from dictionary."""
        return PersonalityProfile(**data)
    
    def __repr__(self):
        return f"Personality({self.get_description()})"
