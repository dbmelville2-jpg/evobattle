"""
Population Management System - Tracks population dynamics, births, deaths, and analytics.

Provides infrastructure for managing creature populations in an ecosystem,
tracking lifecycle events, and gathering analytics for the genetic lineage system.
"""

from typing import List, Dict, Optional, Any
from enum import Enum
import time
import json

from ..models.creature import Creature


class EventType(Enum):
    """Types of population events."""
    BIRTH = 'birth'
    DEATH = 'death'
    BREEDING = 'breeding'
    MATURITY = 'maturity'
    STARVATION = 'starvation'
    COMBAT = 'combat'


class PopulationEvent:
    """
    Represents a single population event.
    
    Attributes:
        event_type: Type of event
        creature_id: ID of the creature involved
        timestamp: When the event occurred
        details: Additional event-specific data
    """
    
    def __init__(
        self,
        event_type: EventType,
        creature_id: str,
        timestamp: Optional[float] = None,
        details: Optional[Dict] = None
    ):
        """
        Initialize a population event.
        
        Args:
            event_type: Type of event
            creature_id: ID of creature involved
            timestamp: When event occurred (current time if None)
            details: Additional event data
        """
        self.event_type = event_type
        self.creature_id = creature_id
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.details = details or {}
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'event_type': self.event_type.value,
            'creature_id': self.creature_id,
            'timestamp': self.timestamp,
            'details': self.details
        }
    
    def __repr__(self):
        return f"PopulationEvent({self.event_type.value}, creature={self.creature_id})"


class EventLogger:
    """
    Logs population events for analysis and replay.
    
    Attributes:
        events: List of all logged events
    """
    
    def __init__(self):
        """Initialize the event logger."""
        self.events: List[PopulationEvent] = []
    
    def log(
        self,
        event_type: EventType,
        creature: Creature,
        details: Optional[Dict] = None
    ):
        """
        Log a population event.
        
        Args:
            event_type: Type of event
            creature: Creature involved in the event
            details: Additional event data (e.g., parents, cause of death)
        """
        event = PopulationEvent(event_type, creature.creature_id, details=details)
        self.events.append(event)
    
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        creature_id: Optional[str] = None
    ) -> List[PopulationEvent]:
        """
        Get filtered events.
        
        Args:
            event_type: Filter by event type (None = all)
            creature_id: Filter by creature ID (None = all)
            
        Returns:
            Filtered list of events
        """
        filtered = self.events
        
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        if creature_id:
            filtered = [e for e in filtered if e.creature_id == creature_id]
        
        return filtered
    
    def clear(self):
        """Clear all logged events."""
        self.events.clear()
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'events': [e.to_dict() for e in self.events]
        }


class PopulationAnalytics:
    """
    Tracks and analyzes population metrics over time.
    
    Attributes:
        history: List of population snapshots over time
    """
    
    def __init__(self):
        """Initialize the analytics tracker."""
        self.history: List[Dict] = []
    
    def record_tick(self, pop_manager: 'PopulationManager'):
        """
        Record current population state.
        
        Args:
            pop_manager: PopulationManager to snapshot
        """
        snapshot = {
            'timestamp': time.time(),
            'population': len(pop_manager.population),
            'births': pop_manager.births,
            'deaths': pop_manager.deaths,
            'alive': len([c for c in pop_manager.population if c.is_alive()]),
            'mature': len([c for c in pop_manager.population if c.mature and c.is_alive()])
        }
        self.history.append(snapshot)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics.
        
        Returns:
            Dictionary of population statistics
        """
        if not self.history:
            return {}
        
        current = self.history[-1]
        
        return {
            'current_population': current['population'],
            'total_births': current['births'],
            'total_deaths': current['deaths'],
            'alive_creatures': current['alive'],
            'mature_creatures': current['mature'],
            'total_snapshots': len(self.history)
        }
    
    def clear(self):
        """Clear history."""
        self.history.clear()
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'history': self.history
        }


class PopulationManager:
    """
    Manages population of creatures in an ecosystem.
    
    Tracks births, deaths, and provides population analytics.
    Works with individual creatures rather than teams.
    
    Attributes:
        population: List of all creatures (alive and dead)
        births: Total number of births
        deaths: Total number of deaths
        event_logger: Logger for population events
        analytics: Analytics tracker
    """
    
    def __init__(self):
        """Initialize the population manager."""
        self.population: List[Creature] = []
        self.births: int = 0
        self.deaths: int = 0
        self.event_logger = EventLogger()
        self.analytics = PopulationAnalytics()
    
    def spawn_creature(
        self,
        creature: Creature,
        log_event: bool = True
    ) -> Creature:
        """
        Add a new creature to the population.
        
        Args:
            creature: Creature to add
            log_event: Whether to log the birth event
            
        Returns:
            The added creature
        """
        self.population.append(creature)
        self.births += 1
        
        if log_event:
            details = {}
            if creature.parent_ids:
                details['parents'] = creature.parent_ids
            self.event_logger.log(EventType.BIRTH, creature, details)
        
        return creature
    
    def remove_creature(
        self,
        creature: Creature,
        cause: str = "unknown",
        log_event: bool = True
    ):
        """
        Mark a creature as dead (doesn't remove from population list).
        
        Args:
            creature: Creature to remove
            cause: Cause of death
            log_event: Whether to log the death event
        """
        self.deaths += 1
        
        if log_event:
            # Determine event type based on cause
            if 'starv' in cause.lower():
                event_type = EventType.STARVATION
            elif 'combat' in cause.lower() or 'battle' in cause.lower():
                event_type = EventType.COMBAT
            else:
                event_type = EventType.DEATH
            
            self.event_logger.log(event_type, creature, {'cause': cause})
    
    def get_alive_creatures(self) -> List[Creature]:
        """
        Get all currently alive creatures.
        
        Returns:
            List of alive creatures
        """
        return [c for c in self.population if c.is_alive()]
    
    def get_mature_creatures(self) -> List[Creature]:
        """
        Get all mature, alive creatures that can breed.
        
        Returns:
            List of breedable creatures
        """
        return [c for c in self.population if c.can_breed()]
    
    def update(self, delta_time: float):
        """
        Update all creatures in population.
        
        Args:
            delta_time: Time elapsed since last update
        """
        for creature in self.get_alive_creatures():
            # Update age
            creature.tick_age(delta_time)
            
            # Check for maturity events
            if creature.mature and creature.age == delta_time:
                # Just became mature
                self.event_logger.log(EventType.MATURITY, creature)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'population': [c.to_dict() for c in self.population],
            'births': self.births,
            'deaths': self.deaths,
            'events': self.event_logger.to_dict(),
            'analytics': self.analytics.to_dict()
        }
    
    def __repr__(self):
        alive = len(self.get_alive_creatures())
        return f"PopulationManager(total={len(self.population)}, alive={alive}, births={self.births}, deaths={self.deaths})"


class EcosystemConfig:
    """
    Configuration for ecosystem simulation parameters.
    
    Attributes:
        max_population: Maximum population size
        breeding_cooldown: Time between breeding attempts
        maturity_age: Age when creatures reach maturity
        trait_inheritance_chance: Probability of inheriting each trait
        mutation_rate: Probability of trait mutation
    """
    
    def __init__(
        self,
        max_population: int = 50,
        breeding_cooldown: float = 30.0,
        maturity_age: float = 20.0,
        trait_inheritance_chance: float = 0.8,
        mutation_rate: float = 0.1
    ):
        """
        Initialize ecosystem configuration.
        
        Args:
            max_population: Maximum population size
            breeding_cooldown: Seconds between breeding attempts
            maturity_age: Age in seconds when creatures mature
            trait_inheritance_chance: 0-1 probability of trait inheritance
            mutation_rate: 0-1 probability of mutation
        """
        self.max_population = max_population
        self.breeding_cooldown = breeding_cooldown
        self.maturity_age = maturity_age
        self.trait_inheritance_chance = trait_inheritance_chance
        self.mutation_rate = mutation_rate
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'max_population': self.max_population,
            'breeding_cooldown': self.breeding_cooldown,
            'maturity_age': self.maturity_age,
            'trait_inheritance_chance': self.trait_inheritance_chance,
            'mutation_rate': self.mutation_rate
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'EcosystemConfig':
        """Deserialize from dictionary."""
        return EcosystemConfig(**data)
    
    def save_to_file(self, filepath: str):
        """Save configuration to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @staticmethod
    def load_from_file(filepath: str) -> 'EcosystemConfig':
        """Load configuration from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return EcosystemConfig.from_dict(data)
    
    def __repr__(self):
        return f"EcosystemConfig(max_pop={self.max_population}, maturity={self.maturity_age}s)"
