"""
Creature History & Life Event Tracking System.

This module provides comprehensive tracking of every significant event in a
creature's lifetime, creating rich narratives and memorable moments.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
import time


class EventType(Enum):
    """Types of life events that can occur."""
    # Birth & Death
    BIRTH = "birth"
    DEATH = "death"
    
    # Combat Events
    BATTLE_START = "battle_start"
    BATTLE_END = "battle_end"
    BATTLE_WIN = "battle_win"
    BATTLE_LOSS = "battle_loss"
    ATTACK = "attack"
    CRITICAL_HIT = "critical_hit"
    KILL = "kill"
    REVENGE_KILL = "revenge_kill"
    DAMAGE_TAKEN = "damage_taken"
    DODGE = "dodge"
    
    # Survival Events
    FOOD_CONSUMED = "food_consumed"
    STARVATION = "starvation"
    NEAR_DEATH = "near_death"
    RECOVERY = "recovery"
    
    # Social Events
    OFFSPRING_BORN = "offspring_born"
    PARENT_DIED = "parent_died"
    SIBLING_DIED = "sibling_died"
    ALLIANCE_FORMED = "alliance_formed"
    RIVALRY_FORMED = "rivalry_formed"
    
    # Achievements
    FIRST_KILL = "first_kill"
    LEGENDARY_MOMENT = "legendary_moment"
    MILESTONE_REACHED = "milestone_reached"
    SKILL_MASTERED = "skill_mastered"
    
    # Evolution
    TRAIT_GAINED = "trait_gained"
    TRAIT_LOST = "trait_lost"
    EVOLUTION = "evolution"


@dataclass
class LifeEvent:
    """
    Represents a single significant event in a creature's life.
    
    Attributes:
        event_type: Type of event that occurred
        timestamp: When the event occurred (simulation time)
        description: Human-readable description
        entities_involved: IDs of other creatures involved
        location: Optional (x, y) coordinates where event occurred
        context: Additional event-specific data
        significance: How notable this event is (0-1, higher = more significant)
    """
    event_type: EventType
    timestamp: float
    description: str
    entities_involved: List[str] = field(default_factory=list)
    location: Optional[tuple] = None
    context: Dict[str, Any] = field(default_factory=dict)
    significance: float = 0.5
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp,
            'description': self.description,
            'entities_involved': self.entities_involved,
            'location': self.location,
            'context': self.context,
            'significance': self.significance
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'LifeEvent':
        """Deserialize from dictionary."""
        data_copy = data.copy()
        data_copy['event_type'] = EventType(data_copy['event_type'])
        return LifeEvent(**data_copy)


@dataclass
class KillRecord:
    """
    Records a kill made by this creature.
    
    Attributes:
        victim_id: ID of the creature that was killed
        victim_name: Name of the victim
        timestamp: When the kill occurred
        location: Where the kill occurred
        power_differential: Victim's power / Killer's power
        was_revenge: Whether this was a revenge kill
    """
    victim_id: str
    victim_name: str
    timestamp: float
    location: Optional[tuple] = None
    power_differential: float = 1.0
    was_revenge: bool = False
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'victim_id': self.victim_id,
            'victim_name': self.victim_name,
            'timestamp': self.timestamp,
            'location': self.location,
            'power_differential': self.power_differential,
            'was_revenge': self.was_revenge
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'KillRecord':
        """Deserialize from dictionary."""
        return KillRecord(**data)


@dataclass
class Achievement:
    """
    Represents an achievement earned by a creature.
    
    Attributes:
        name: Achievement name
        description: What was achieved
        timestamp: When it was earned
        rarity: How rare this achievement is (0-1)
    """
    name: str
    description: str
    timestamp: float
    rarity: float = 0.5
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'timestamp': self.timestamp,
            'rarity': self.rarity
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Achievement':
        """Deserialize from dictionary."""
        return Achievement(**data)


class CreatureHistory:
    """
    Comprehensive history tracking for a single creature.
    
    Tracks all significant events, statistics, and achievements throughout
    a creature's lifetime to create memorable narratives.
    """
    
    def __init__(self, creature_id: str, creature_name: str):
        """
        Initialize creature history.
        
        Args:
            creature_id: Unique identifier for the creature
            creature_name: Name of the creature
        """
        self.creature_id = creature_id
        self.creature_name = creature_name
        
        # Lifecycle
        self.birth_time: float = time.time()
        self.death_time: Optional[float] = None
        self.cause_of_death: Optional[str] = None
        
        # Battle Statistics
        self.battles_fought: int = 0
        self.battles_won: int = 0
        self.total_damage_dealt: float = 0.0
        self.total_damage_received: float = 0.0
        self.kills: List[KillRecord] = []
        self.deaths: int = 0
        
        # Survival Statistics
        self.food_consumed: int = 0
        self.times_starved: int = 0
        self.near_death_experiences: int = 0
        
        # Social Statistics
        self.offspring_count: int = 0
        self.times_bred: int = 0
        
        # Event Log
        self.events: List[LifeEvent] = []
        self.legendary_moments: List[LifeEvent] = []
        
        # Achievements
        self.achievements: List[Achievement] = []
        
        # Titles earned
        self.titles: List[str] = []
    
    def add_event(self, event: LifeEvent):
        """
        Add an event to the creature's history.
        
        Args:
            event: The event to record
        """
        self.events.append(event)
        
        # Track legendary moments separately
        if event.significance >= 0.8:
            self.legendary_moments.append(event)
    
    def record_battle_start(self, enemies: List[str], location: Optional[tuple] = None):
        """Record the start of a battle."""
        event = LifeEvent(
            event_type=EventType.BATTLE_START,
            timestamp=time.time(),
            description=f"{self.creature_name} entered battle against {len(enemies)} opponent(s)",
            entities_involved=enemies,
            location=location,
            significance=0.3
        )
        self.add_event(event)
        self.battles_fought += 1
    
    def record_attack(self, target_id: str, damage: float, was_critical: bool = False):
        """Record an attack."""
        event_type = EventType.CRITICAL_HIT if was_critical else EventType.ATTACK
        significance = 0.6 if was_critical else 0.2
        
        event = LifeEvent(
            event_type=event_type,
            timestamp=time.time(),
            description=f"{self.creature_name} {'critically struck' if was_critical else 'attacked'} for {damage:.1f} damage",
            entities_involved=[target_id],
            context={'damage': damage},
            significance=significance
        )
        self.add_event(event)
        self.total_damage_dealt += damage
    
    def record_damage_taken(self, attacker_id: str, damage: float):
        """Record damage received."""
        event = LifeEvent(
            event_type=EventType.DAMAGE_TAKEN,
            timestamp=time.time(),
            description=f"{self.creature_name} took {damage:.1f} damage",
            entities_involved=[attacker_id],
            context={'damage': damage},
            significance=0.2
        )
        self.add_event(event)
        self.total_damage_received += damage
    
    def record_kill(
        self,
        victim_id: str,
        victim_name: str,
        power_differential: float = 1.0,
        location: Optional[tuple] = None,
        was_revenge: bool = False
    ):
        """
        Record a kill made by this creature.
        
        Args:
            victim_id: ID of the killed creature
            victim_name: Name of the killed creature
            power_differential: Victim power / Killer power (>1 = underdog victory)
            location: Where the kill occurred
            was_revenge: Whether this was revenge for a family member
        """
        kill_record = KillRecord(
            victim_id=victim_id,
            victim_name=victim_name,
            timestamp=time.time(),
            location=location,
            power_differential=power_differential,
            was_revenge=was_revenge
        )
        self.kills.append(kill_record)
        
        # Determine significance
        significance = 0.7
        if was_revenge:
            significance = 0.9
        elif power_differential > 2.0:
            significance = 0.95  # Giant slayer!
        elif power_differential > 1.5:
            significance = 0.8
        
        event_type = EventType.REVENGE_KILL if was_revenge else EventType.KILL
        description = f"{self.creature_name} defeated {victim_name}"
        if was_revenge:
            description += " (REVENGE!)"
        elif power_differential > 1.5:
            description += f" (underdog victory, {power_differential:.1f}x power difference!)"
        
        event = LifeEvent(
            event_type=event_type,
            timestamp=time.time(),
            description=description,
            entities_involved=[victim_id],
            location=location,
            context={
                'victim_name': victim_name,
                'power_differential': power_differential,
                'was_revenge': was_revenge
            },
            significance=significance
        )
        self.add_event(event)
        
        # Check for first kill achievement
        if len(self.kills) == 1:
            self.add_achievement(Achievement(
                name="First Blood",
                description=f"First kill: {victim_name}",
                timestamp=time.time(),
                rarity=0.3
            ))
        
        # Check for giant slayer achievement
        if power_differential > 2.0:
            self.add_achievement(Achievement(
                name="Giant Slayer",
                description=f"Defeated {victim_name} with {power_differential:.1f}x power difference",
                timestamp=time.time(),
                rarity=0.8
            ))
    
    def record_death(self, killer_id: Optional[str], cause: str, location: Optional[tuple] = None):
        """Record the death of this creature."""
        self.death_time = time.time()
        self.cause_of_death = cause
        self.deaths += 1
        
        event = LifeEvent(
            event_type=EventType.DEATH,
            timestamp=self.death_time,
            description=f"{self.creature_name} died: {cause}",
            entities_involved=[killer_id] if killer_id else [],
            location=location,
            significance=1.0  # Death is always significant
        )
        self.add_event(event)
    
    def record_battle_victory(self):
        """Record a battle victory."""
        self.battles_won += 1
        event = LifeEvent(
            event_type=EventType.BATTLE_WIN,
            timestamp=time.time(),
            description=f"{self.creature_name} won the battle",
            significance=0.6
        )
        self.add_event(event)
    
    def record_offspring_born(self, offspring_id: str, offspring_name: str):
        """Record the birth of an offspring."""
        self.offspring_count += 1
        self.times_bred += 1
        
        event = LifeEvent(
            event_type=EventType.OFFSPRING_BORN,
            timestamp=time.time(),
            description=f"{self.creature_name} had offspring: {offspring_name}",
            entities_involved=[offspring_id],
            significance=0.7
        )
        self.add_event(event)
    
    def add_achievement(self, achievement: Achievement):
        """Add an achievement to this creature's record."""
        self.achievements.append(achievement)
        
        event = LifeEvent(
            event_type=EventType.MILESTONE_REACHED,
            timestamp=achievement.timestamp,
            description=f"Achievement unlocked: {achievement.name}",
            significance=achievement.rarity
        )
        self.add_event(event)
    
    def add_title(self, title: str):
        """Add a title to this creature."""
        if title not in self.titles:
            self.titles.append(title)
    
    def get_win_rate(self) -> float:
        """Calculate win rate."""
        if self.battles_fought == 0:
            return 0.0
        return self.battles_won / self.battles_fought
    
    def get_kill_death_ratio(self) -> float:
        """Calculate K/D ratio."""
        if self.deaths == 0:
            return float(len(self.kills)) if len(self.kills) > 0 else 0.0
        return len(self.kills) / self.deaths
    
    def get_lifetime(self) -> float:
        """Get the creature's lifetime in seconds."""
        end_time = self.death_time if self.death_time else time.time()
        return end_time - self.birth_time
    
    def get_recent_events(self, count: int = 10) -> List[LifeEvent]:
        """Get the most recent events."""
        return sorted(self.events, key=lambda e: e.timestamp, reverse=True)[:count]
    
    def get_events_by_type(self, event_type: EventType) -> List[LifeEvent]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'creature_id': self.creature_id,
            'creature_name': self.creature_name,
            'birth_time': self.birth_time,
            'death_time': self.death_time,
            'cause_of_death': self.cause_of_death,
            'battles_fought': self.battles_fought,
            'battles_won': self.battles_won,
            'total_damage_dealt': self.total_damage_dealt,
            'total_damage_received': self.total_damage_received,
            'kills': [k.to_dict() for k in self.kills],
            'deaths': self.deaths,
            'food_consumed': self.food_consumed,
            'times_starved': self.times_starved,
            'near_death_experiences': self.near_death_experiences,
            'offspring_count': self.offspring_count,
            'times_bred': self.times_bred,
            'events': [e.to_dict() for e in self.events],
            'legendary_moments': [e.to_dict() for e in self.legendary_moments],
            'achievements': [a.to_dict() for a in self.achievements],
            'titles': self.titles
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'CreatureHistory':
        """Deserialize from dictionary."""
        history = CreatureHistory(data['creature_id'], data['creature_name'])
        history.birth_time = data['birth_time']
        history.death_time = data.get('death_time')
        history.cause_of_death = data.get('cause_of_death')
        history.battles_fought = data['battles_fought']
        history.battles_won = data['battles_won']
        history.total_damage_dealt = data['total_damage_dealt']
        history.total_damage_received = data['total_damage_received']
        history.kills = [KillRecord.from_dict(k) for k in data['kills']]
        history.deaths = data['deaths']
        history.food_consumed = data['food_consumed']
        history.times_starved = data['times_starved']
        history.near_death_experiences = data['near_death_experiences']
        history.offspring_count = data['offspring_count']
        history.times_bred = data['times_bred']
        history.events = [LifeEvent.from_dict(e) for e in data['events']]
        history.legendary_moments = [LifeEvent.from_dict(e) for e in data['legendary_moments']]
        history.achievements = [Achievement.from_dict(a) for a in data['achievements']]
        history.titles = data['titles']
        return history
