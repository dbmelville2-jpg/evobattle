"""
Skill System - Skills that develop through use and experience.

Creatures develop proficiency in various skills through practice, creating
unique combat styles and emergent gameplay.
"""

from typing import Dict, Optional
from enum import Enum
from dataclasses import dataclass
import time
import math


class SkillType(Enum):
    """Types of skills creatures can develop."""
    # Combat Skills
    MELEE_ATTACK = "melee_attack"
    RANGED_ATTACK = "ranged_attack"
    CRITICAL_STRIKE = "critical_strike"
    DODGE = "dodge"
    BLOCK = "block"
    
    # Survival Skills
    FORAGING = "foraging"
    METABOLISM = "metabolism"
    STAMINA = "stamina"
    
    # Social Skills
    LEADERSHIP = "leadership"
    TEAMWORK = "teamwork"
    INTIMIDATION = "intimidation"


class Proficiency(Enum):
    """Skill proficiency levels."""
    NOVICE = "novice"          # 0-19
    COMPETENT = "competent"    # 20-39
    EXPERT = "expert"          # 40-59
    MASTER = "master"          # 60-79
    LEGENDARY = "legendary"    # 80-100


@dataclass
class SkillConfig:
    """Configuration for a skill type."""
    name: str
    description: str
    base_learning_rate: float = 1.0  # XP gained per use
    difficulty_scaling: float = 1.0  # How much difficulty affects XP gain
    max_level: int = 100
    decay_rate: float = 0.001  # XP lost per second of non-use


class Skill:
    """
    Represents a single skill that a creature can develop.
    
    Skills gain experience through use and provide performance bonuses.
    Higher skill levels make actions more effective but also slower to improve.
    """
    
    def __init__(
        self,
        skill_type: SkillType,
        config: Optional[SkillConfig] = None,
        level: int = 0,
        experience: float = 0.0
    ):
        """
        Initialize a skill.
        
        Args:
            skill_type: The type of skill
            config: Skill configuration (uses default if None)
            level: Starting skill level (0-100)
            experience: Starting experience points
        """
        self.skill_type = skill_type
        self.config = config if config else self._get_default_config(skill_type)
        self.level = level
        self.experience = experience
        self.last_used: float = time.time()
        self.total_uses: int = 0
    
    @staticmethod
    def _get_default_config(skill_type: SkillType) -> SkillConfig:
        """Get default configuration for a skill type."""
        configs = {
            SkillType.MELEE_ATTACK: SkillConfig(
                name="Melee Attack",
                description="Proficiency with close-range attacks",
                base_learning_rate=1.0,
                difficulty_scaling=1.5
            ),
            SkillType.RANGED_ATTACK: SkillConfig(
                name="Ranged Attack",
                description="Accuracy with ranged attacks",
                base_learning_rate=1.0,
                difficulty_scaling=1.2
            ),
            SkillType.CRITICAL_STRIKE: SkillConfig(
                name="Critical Strike",
                description="Chance to land devastating hits",
                base_learning_rate=0.5,
                difficulty_scaling=2.0
            ),
            SkillType.DODGE: SkillConfig(
                name="Dodge",
                description="Ability to evade attacks",
                base_learning_rate=1.0,
                difficulty_scaling=1.5
            ),
            SkillType.BLOCK: SkillConfig(
                name="Block",
                description="Reduce damage from attacks",
                base_learning_rate=0.8,
                difficulty_scaling=1.3
            ),
            SkillType.FORAGING: SkillConfig(
                name="Foraging",
                description="Efficiency at finding food",
                base_learning_rate=1.2,
                difficulty_scaling=0.8
            ),
            SkillType.METABOLISM: SkillConfig(
                name="Metabolism",
                description="Efficiency at using food energy",
                base_learning_rate=0.3,
                difficulty_scaling=0.5
            ),
            SkillType.STAMINA: SkillConfig(
                name="Stamina",
                description="Endurance and sustained activity",
                base_learning_rate=0.5,
                difficulty_scaling=1.0
            ),
            SkillType.LEADERSHIP: SkillConfig(
                name="Leadership",
                description="Inspire and coordinate allies",
                base_learning_rate=0.4,
                difficulty_scaling=1.5
            ),
            SkillType.TEAMWORK: SkillConfig(
                name="Teamwork",
                description="Fight effectively with allies",
                base_learning_rate=0.6,
                difficulty_scaling=1.0
            ),
            SkillType.INTIMIDATION: SkillConfig(
                name="Intimidation",
                description="Frighten and demoralize enemies",
                base_learning_rate=0.5,
                difficulty_scaling=1.2
            ),
        }
        return configs.get(skill_type, SkillConfig(name=skill_type.value, description=""))
    
    def use(self, difficulty: float = 1.0, success: bool = True) -> float:
        """
        Use the skill and gain experience.
        
        Args:
            difficulty: How difficult the task was (affects XP gain)
            success: Whether the action succeeded (more XP for success)
            
        Returns:
            Performance modifier (1.0 = baseline, higher = better)
        """
        self.last_used = time.time()
        self.total_uses += 1
        
        # Calculate XP gain
        # Harder tasks and successes give more XP
        # Higher skill levels learn slower (diminishing returns)
        base_xp = self.config.base_learning_rate
        difficulty_bonus = difficulty * self.config.difficulty_scaling
        success_multiplier = 1.0 if success else 0.3
        level_penalty = 1.0 / (1.0 + self.level / 50.0)  # Slower learning at high levels
        
        xp_gain = base_xp * difficulty_bonus * success_multiplier * level_penalty
        self.experience += xp_gain
        
        # Level up if enough experience
        xp_for_next_level = self._xp_required_for_level(self.level + 1)
        if self.experience >= xp_for_next_level and self.level < self.config.max_level:
            self.level += 1
        
        # Return performance modifier
        return self.get_performance_modifier()
    
    def decay(self, elapsed_time: float):
        """
        Decay skill from lack of use.
        
        Args:
            elapsed_time: Time since last use in seconds
        """
        if elapsed_time <= 0:
            return
        
        # Decay experience based on time
        decay_amount = self.config.decay_rate * elapsed_time
        self.experience = max(0, self.experience - decay_amount)
        
        # Potentially decrease level
        xp_for_current_level = self._xp_required_for_level(self.level)
        if self.experience < xp_for_current_level and self.level > 0:
            self.level -= 1
    
    def _xp_required_for_level(self, level: int) -> float:
        """Calculate XP required to reach a given level."""
        # Exponential curve: each level requires more XP
        return 10.0 * (level ** 1.5)
    
    def get_proficiency(self) -> Proficiency:
        """Get current proficiency level."""
        if self.level >= 80:
            return Proficiency.LEGENDARY
        elif self.level >= 60:
            return Proficiency.MASTER
        elif self.level >= 40:
            return Proficiency.EXPERT
        elif self.level >= 20:
            return Proficiency.COMPETENT
        else:
            return Proficiency.NOVICE
    
    def get_performance_modifier(self) -> float:
        """
        Get performance modifier based on skill level.
        
        Returns:
            Multiplier for skill-related actions (1.0 = baseline, 2.0 = double effectiveness)
        """
        # Scale from 1.0 at level 0 to 2.0 at level 100
        return 1.0 + (self.level / 100.0)
    
    def get_success_chance_bonus(self) -> float:
        """
        Get bonus to success chance (e.g., dodge chance, crit chance).
        
        Returns:
            Bonus percentage (0-50%)
        """
        # Scale from 0% at level 0 to 50% at level 100
        return self.level * 0.5
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'skill_type': self.skill_type.value,
            'level': self.level,
            'experience': self.experience,
            'last_used': self.last_used,
            'total_uses': self.total_uses,
            'proficiency': self.get_proficiency().value
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Skill':
        """Deserialize from dictionary."""
        skill = Skill(
            skill_type=SkillType(data['skill_type']),
            level=data['level'],
            experience=data['experience']
        )
        skill.last_used = data['last_used']
        skill.total_uses = data['total_uses']
        return skill
    
    def __repr__(self):
        return f"Skill({self.config.name}, Lv.{self.level}, {self.get_proficiency().value})"


class SkillManager:
    """
    Manages all skills for a creature.
    
    Handles skill progression, decay, and querying.
    """
    
    def __init__(self):
        """Initialize skill manager."""
        self.skills: Dict[SkillType, Skill] = {}
    
    def get_skill(self, skill_type: SkillType) -> Skill:
        """
        Get a skill, creating it if it doesn't exist.
        
        Args:
            skill_type: Type of skill to get
            
        Returns:
            The skill instance
        """
        if skill_type not in self.skills:
            self.skills[skill_type] = Skill(skill_type)
        return self.skills[skill_type]
    
    def use_skill(self, skill_type: SkillType, difficulty: float = 1.0, success: bool = True) -> float:
        """
        Use a skill and get performance modifier.
        
        Args:
            skill_type: Type of skill being used
            difficulty: How difficult the task is
            success: Whether the action succeeded
            
        Returns:
            Performance modifier
        """
        skill = self.get_skill(skill_type)
        return skill.use(difficulty, success)
    
    def update_decay(self):
        """Update decay for all skills based on time since last use."""
        current_time = time.time()
        for skill in self.skills.values():
            elapsed = current_time - skill.last_used
            skill.decay(elapsed)
    
    def get_all_skills(self) -> Dict[SkillType, Skill]:
        """Get all skills."""
        return self.skills.copy()
    
    def get_proficiency_summary(self) -> Dict[str, int]:
        """
        Get summary of skill proficiencies.
        
        Returns:
            Dictionary mapping proficiency levels to count
        """
        summary = {p.value: 0 for p in Proficiency}
        for skill in self.skills.values():
            prof = skill.get_proficiency()
            summary[prof.value] += 1
        return summary
    
    def get_highest_skills(self, count: int = 3) -> list:
        """
        Get the highest level skills.
        
        Args:
            count: Number of top skills to return
            
        Returns:
            List of (skill_type, level) tuples
        """
        sorted_skills = sorted(
            self.skills.items(),
            key=lambda x: x[1].level,
            reverse=True
        )
        return [(st, s.level) for st, s in sorted_skills[:count]]
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            skill_type.value: skill.to_dict()
            for skill_type, skill in self.skills.items()
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'SkillManager':
        """Deserialize from dictionary."""
        manager = SkillManager()
        for skill_type_str, skill_data in data.items():
            skill = Skill.from_dict(skill_data)
            manager.skills[skill.skill_type] = skill
        return manager
