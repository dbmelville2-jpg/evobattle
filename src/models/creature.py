"""
Creature model - Enhanced creature system with stats, abilities, and evolution.
"""

from typing import Dict, List, Optional
import uuid
import time
import colorsys
import random
from .stats import Stats, StatModifier, StatGrowth
from .ability import Ability
from .trait import Trait
from .history import CreatureHistory
from .skills import SkillManager
from .personality import PersonalityProfile
from .relationships import RelationshipManager


class CreatureType:
    """
    Defines a creature type/species with base stats and characteristics.
    
    Attributes:
        name (str): Name of the creature type
        description (str): Description of this creature type
        base_stats (Stats): Base stats for this type at level 1
        stat_growth (StatGrowth): How stats grow with levels
        type_tags (List[str]): Tags like "fire", "water", "flying", etc.
        evolution_stage (int): Current evolution stage (0=base, 1=first evolution, etc.)
        can_evolve (bool): Whether this type can evolve further
    """
    
    def __init__(
        self,
        name: str = "Basic Creature",
        description: str = "A basic creature type",
        base_stats: Optional[Stats] = None,
        stat_growth: Optional[StatGrowth] = None,
        type_tags: Optional[List[str]] = None,
        evolution_stage: int = 0,
        can_evolve: bool = True
    ):
        """
        Initialize a CreatureType.
        
        Args:
            name: Name of the creature type
            description: Description
            base_stats: Base stats at level 1
            stat_growth: Growth profile
            type_tags: Type tags for this creature
            evolution_stage: Current evolution stage
            can_evolve: Whether further evolution is possible
        """
        self.name = name
        self.description = description
        self.base_stats = base_stats if base_stats else Stats()
        self.stat_growth = stat_growth if stat_growth else StatGrowth()
        self.type_tags = type_tags if type_tags else []
        self.evolution_stage = evolution_stage
        self.can_evolve = can_evolve
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'base_stats': self.base_stats.to_dict(),
            'stat_growth': self.stat_growth.to_dict(),
            'type_tags': self.type_tags,
            'evolution_stage': self.evolution_stage,
            'can_evolve': self.can_evolve
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'CreatureType':
        """Deserialize from dictionary."""
        data_copy = data.copy()
        if 'base_stats' in data_copy:
            data_copy['base_stats'] = Stats.from_dict(data_copy['base_stats'])
        if 'stat_growth' in data_copy:
            data_copy['stat_growth'] = StatGrowth.from_dict(data_copy['stat_growth'])
        return CreatureType(**data_copy)
    
    def __repr__(self):
        """String representation."""
        return f"CreatureType(name='{self.name}', stage={self.evolution_stage})"


class Creature:
    """
    Represents a creature in the EvoBattle game.
    
    An enhanced version of Fighter with full stats system, abilities,
    type information, experience/leveling, and serialization support.
    
    Attributes:
        creature_id (str): Unique identifier
        name (str): Individual name of this creature
        creature_type (CreatureType): Type/species of creature
        level (int): Current level
        experience (int): Current experience points
        stats (Stats): Current stats
        base_stats (Stats): Base stats without modifiers
        abilities (List[Ability]): Abilities this creature can use
        traits (List[Trait]): Genetic traits affecting the creature
        active_modifiers (List[StatModifier]): Active stat modifiers
        energy (int): Current energy for using abilities
        max_energy (int): Maximum energy
        hunger (int): Current hunger level (0=starving, 100=full)
        max_hunger (int): Maximum hunger level
        birth_time (float): Simulation time when creature was born
        age (float): Current age in simulation time units
        mature (bool): Whether creature has reached maturity
        parent_ids (List[str]): IDs of parent creatures
        hue (float): Base hue for HSV color system (0-360)
        strain_id (str): Genetic strain/family identifier
    """
    
    def __init__(
        self,
        name: str = "Creature",
        creature_type: Optional[CreatureType] = None,
        level: int = 1,
        experience: int = 0,
        creature_id: Optional[str] = None,
        base_stats: Optional[Stats] = None,
        abilities: Optional[List[Ability]] = None,
        traits: Optional[List[Trait]] = None,
        energy: int = 100,
        max_energy: int = 100,
        hunger: int = 100,
        max_hunger: int = 100,
        birth_time: Optional[float] = None,
        age: float = 0.0,
        mature: bool = False,
        parent_ids: Optional[List[str]] = None,
        hue: Optional[float] = None,
        strain_id: Optional[str] = None
    ):
        """
        Initialize a new Creature.
        
        Args:
            name: Individual name
            creature_type: Type/species
            level: Starting level
            experience: Starting XP
            creature_id: Unique ID (auto-generated if None)
            base_stats: Base stats (from type if None)
            abilities: List of abilities
            traits: List of traits
            energy: Starting energy
            max_energy: Maximum energy
            hunger: Starting hunger (0=starving, 100=full)
            max_hunger: Maximum hunger
            birth_time: When creature was born (current time if None)
            age: Current age in simulation time
            mature: Whether creature is mature enough to breed
            parent_ids: List of parent creature IDs
            hue: Base hue for color (0-360, random if None)
            strain_id: Genetic strain/family ID (auto-generated if None)
        """
        self.creature_id = creature_id if creature_id else str(uuid.uuid4())
        self.name = name
        self.creature_type = creature_type if creature_type else CreatureType()
        self.level = level
        self.experience = experience
        
        # Lifecycle attributes
        self.birth_time = birth_time if birth_time is not None else time.time()
        self.age = age
        self.mature = mature
        self.parent_ids = parent_ids if parent_ids else []
        self.hue = hue if hue is not None else random.uniform(0, 360)
        
        # Genetic lineage
        self.strain_id = strain_id if strain_id else str(uuid.uuid4())
        
        # Initialize stats based on type and level
        if base_stats:
            self.base_stats = base_stats
        else:
            self.base_stats = self.creature_type.stat_growth.calculate_stats_at_level(
                self.creature_type.base_stats,
                self.level
            )
        
        self.stats = self.base_stats.copy()
        self.abilities = abilities if abilities else []
        self.traits = traits if traits else []
        self.active_modifiers: List[StatModifier] = []
        self.energy = energy
        self.max_energy = max_energy
        self.hunger = hunger
        self.max_hunger = max_hunger
        
        # Living World Systems
        self.history = CreatureHistory(self.creature_id, self.name)
        self.skills = SkillManager()
        self.personality = PersonalityProfile.random()
        self.relationships = RelationshipManager(self.creature_id)
        
        # Recalculate stats with trait modifiers applied
        if self.traits:
            self.stats = self.get_effective_stats()
    
    def get_effective_stats(self) -> Stats:
        """
        Calculate effective stats with all modifiers applied.
        
        Returns:
            Stats with all active modifiers applied
        """
        effective = self.base_stats.copy()
        
        # Apply trait modifiers
        for trait in self.traits:
            trait_modifier = StatModifier(
                name=f"Trait: {trait.name}",
                duration=-1,
                attack_multiplier=trait.strength_modifier,
                defense_multiplier=trait.defense_modifier,
                speed_multiplier=trait.speed_modifier
            )
            effective = effective.apply_modifier(trait_modifier)
        
        # Apply active modifiers (buffs/debuffs)
        for modifier in self.active_modifiers:
            effective = effective.apply_modifier(modifier)
        
        return effective
    
    def add_modifier(self, modifier: StatModifier):
        """
        Add a stat modifier to the creature.
        
        Args:
            modifier: The modifier to add
        """
        self.active_modifiers.append(modifier)
        self.stats = self.get_effective_stats()
    
    def remove_modifier(self, modifier_name: str) -> bool:
        """
        Remove a stat modifier by name.
        
        Args:
            modifier_name: Name of the modifier to remove
            
        Returns:
            True if modifier was found and removed
        """
        for i, mod in enumerate(self.active_modifiers):
            if mod.name == modifier_name:
                self.active_modifiers.pop(i)
                self.stats = self.get_effective_stats()
                return True
        return False
    
    def tick_modifiers(self):
        """Update all modifiers and remove expired ones."""
        expired = []
        for modifier in self.active_modifiers:
            modifier.tick()
            if modifier.is_expired():
                expired.append(modifier)
        
        for exp_mod in expired:
            self.active_modifiers.remove(exp_mod)
        
        if expired:
            self.stats = self.get_effective_stats()
    
    def add_ability(self, ability: Ability):
        """Add an ability to this creature."""
        if ability is not None:
            self.abilities.append(ability)
    
    def remove_ability(self, ability_name: str) -> bool:
        """
        Remove an ability by name.
        
        Args:
            ability_name: Name of ability to remove
            
        Returns:
            True if ability was found and removed
        """
        for i, ability in enumerate(self.abilities):
            if ability.name == ability_name:
                self.abilities.pop(i)
                return True
        return False
    
    def get_ability(self, ability_name: str) -> Optional[Ability]:
        """
        Get an ability by name.
        
        Args:
            ability_name: Name of the ability
            
        Returns:
            The ability if found, None otherwise
        """
        for ability in self.abilities:
            if ability.name == ability_name:
                return ability
        return None
    
    def add_trait(self, trait: Trait):
        """
        Add a trait to this creature.
        
        Args:
            trait: The trait to add
        """
        self.traits.append(trait)
        self.stats = self.get_effective_stats()
    
    def has_trait(self, trait_name: str) -> bool:
        """
        Check if creature has a specific trait.
        
        Args:
            trait_name: Name of the trait
            
        Returns:
            True if creature has the trait
        """
        return any(trait.name == trait_name for trait in self.traits)
    
    def gain_experience(self, amount: int) -> bool:
        """
        Add experience and check for level up.
        
        Args:
            amount: Amount of XP to add
            
        Returns:
            True if leveled up
        """
        self.experience += amount
        exp_needed = self.experience_for_next_level()
        
        if self.experience >= exp_needed:
            return self.level_up()
        return False
    
    def experience_for_next_level(self) -> int:
        """
        Calculate experience needed for next level.
        
        Returns:
            XP required to reach next level
        """
        # Simple formula: level^2 * 100
        return (self.level ** 2) * 100
    
    def level_up(self) -> bool:
        """
        Level up the creature.
        
        Returns:
            True if level up succeeded
        """
        self.level += 1
        self.experience = 0  # Reset XP for new level
        
        # Recalculate stats for new level
        self.base_stats = self.creature_type.stat_growth.calculate_stats_at_level(
            self.creature_type.base_stats,
            self.level
        )
        self.stats = self.get_effective_stats()
        
        # Restore HP and energy on level up
        self.stats.hp = self.stats.max_hp
        self.energy = self.max_energy
        
        return True
    
    def is_alive(self) -> bool:
        """Check if creature is still alive (HP > 0 and not starved)."""
        return self.stats.is_alive() and self.hunger > 0
    
    def can_breed(self) -> bool:
        """
        Check if creature is eligible for breeding.
        
        Returns:
            True if creature is mature, alive, and in good condition
        """
        return (
            self.mature and 
            self.is_alive() and 
            self.stats.hp > 0.5 * self.stats.max_hp and 
            self.hunger > 70
        )
    
    def tick_age(self, delta_time: float):
        """
        Update creature age and check for maturity.
        
        Args:
            delta_time: Time elapsed since last tick (seconds)
        """
        self.age += delta_time
        
        # Check for maturity (default: 20 seconds of age)
        if not self.mature and self.age >= 20.0:
            self.mature = True
    
    def get_display_color(self) -> tuple:
        """
        Calculate display color using HSV system.
        
        Hue is based on lineage (stored in self.hue),
        Saturation reflects health (HP ratio),
        Value reflects hunger level.
        
        Returns:
            RGB color tuple (r, g, b) with values 0-255
        """
        # Saturation based on HP ratio (0.3 to 1.0 for visibility)
        saturation = 0.3 + 0.7 * (self.stats.hp / self.stats.max_hp)
        
        # Value based on hunger (0.3 to 1.0 for visibility)
        value = 0.3 + 0.7 * (self.hunger / 100.0)
        
        # Convert HSV to RGB
        rgb = colorsys.hsv_to_rgb(self.hue / 360.0, saturation, value)
        return tuple(int(255 * x) for x in rgb)
    
    def rest(self):
        """Restore energy and some HP."""
        self.energy = self.max_energy
        heal_amount = self.stats.max_hp // 4
        self.stats.heal(heal_amount)
        
        # Reset ability cooldowns
        for ability in self.abilities:
            ability.reset_cooldown()
    
    def tick_hunger(self, delta_time: float):
        """
        Deplete hunger over time based on metabolic traits.
        
        Args:
            delta_time: Time elapsed since last tick (seconds)
        """
        # Base hunger depletion rate (1.0 per second means 100 seconds to starve)
        hunger_depletion = 1.0 * delta_time
        
        # Apply metabolic trait modifiers
        if self.has_trait("Efficient Metabolism"):
            hunger_depletion *= 0.6  # 40% slower hunger depletion
        if self.has_trait("Efficient"):
            hunger_depletion *= 0.7  # 30% slower hunger depletion
        if self.has_trait("Glutton"):
            hunger_depletion *= 1.5  # 50% faster hunger depletion
        if self.has_trait("Voracious"):
            hunger_depletion *= 1.4  # 40% faster hunger depletion
        
        # Deplete hunger
        self.hunger = max(0, self.hunger - hunger_depletion)
    
    def eat(self, food_value: int = 40, food_type: str = "plant") -> int:
        """
        Consume food to restore hunger.
        
        Args:
            food_value: Amount of hunger to restore
            food_type: Type of food being consumed ("plant" or "creature")
            
        Returns:
            Actual amount of hunger restored (0 if dietary restrictions prevent eating)
        """
        # Check dietary restrictions
        if food_type == "plant":
            # Carnivores cannot eat plants
            if self.has_trait("Carnivore"):
                return 0
        elif food_type == "creature":
            # Herbivores cannot eat creatures
            if self.has_trait("Herbivore"):
                return 0
        
        old_hunger = self.hunger
        self.hunger = min(self.max_hunger, self.hunger + food_value)
        
        # Some traits may provide bonus HP when eating
        if self.has_trait("Voracious") or self.has_trait("Glutton"):
            # Voracious/Glutton creatures gain a small HP bonus when eating
            hp_bonus = food_value // 10
            self.stats.heal(hp_bonus)
        
        return int(self.hunger - old_hunger)
    
    def can_eat_food_type(self, food_type: str) -> bool:
        """
        Check if creature can eat a specific food type based on dietary traits.
        
        Args:
            food_type: Type of food ("plant" or "creature")
            
        Returns:
            True if creature can eat this food type
        """
        if food_type == "plant":
            # Carnivores cannot eat plants
            return not self.has_trait("Carnivore")
        elif food_type == "creature":
            # Herbivores cannot eat creatures
            return not self.has_trait("Herbivore")
        return True
    
    def to_dict(self) -> Dict:
        """
        Serialize creature to dictionary for persistence.
        
        Returns:
            Dictionary representation
        """
        return {
            'creature_id': self.creature_id,
            'name': self.name,
            'creature_type': self.creature_type.to_dict(),
            'level': self.level,
            'experience': self.experience,
            'base_stats': self.base_stats.to_dict(),
            'abilities': [ability.to_dict() for ability in self.abilities],
            'traits': [
                {
                    'name': trait.name,
                    'description': trait.description,
                    'trait_type': trait.trait_type,
                    'strength_modifier': trait.strength_modifier,
                    'speed_modifier': trait.speed_modifier,
                    'defense_modifier': trait.defense_modifier,
                    'rarity': trait.rarity
                }
                for trait in self.traits
            ],
            'active_modifiers': [mod.to_dict() for mod in self.active_modifiers],
            'energy': self.energy,
            'max_energy': self.max_energy,
            'hunger': self.hunger,
            'max_hunger': self.max_hunger,
            'birth_time': self.birth_time,
            'age': self.age,
            'mature': self.mature,
            'parent_ids': self.parent_ids,
            'hue': self.hue,
            'strain_id': self.strain_id
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Creature':
        """
        Deserialize creature from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            Recreated Creature object
        """
        from .ability import Ability
        
        creature_type = CreatureType.from_dict(data['creature_type'])
        base_stats = Stats.from_dict(data['base_stats'])
        abilities = [Ability.from_dict(a) for a in data.get('abilities', [])]
        traits = [Trait(**t) for t in data.get('traits', [])]
        
        creature = Creature(
            name=data['name'],
            creature_type=creature_type,
            level=data['level'],
            experience=data['experience'],
            creature_id=data['creature_id'],
            base_stats=base_stats,
            abilities=abilities,
            traits=traits,
            energy=data.get('energy', 100),
            max_energy=data.get('max_energy', 100),
            hunger=data.get('hunger', 100),
            max_hunger=data.get('max_hunger', 100),
            birth_time=data.get('birth_time'),
            age=data.get('age', 0.0),
            mature=data.get('mature', False),
            parent_ids=data.get('parent_ids', []),
            hue=data.get('hue'),
            strain_id=data.get('strain_id')
        )
        
        # Restore active modifiers
        for mod_data in data.get('active_modifiers', []):
            creature.active_modifiers.append(StatModifier.from_dict(mod_data))
        
        creature.stats = creature.get_effective_stats()
        return creature
    
    def __repr__(self):
        """String representation of Creature."""
        return (f"Creature(name='{self.name}', type='{self.creature_type.name}', "
                f"level={self.level}, hp={self.stats.hp}/{self.stats.max_hp})")
