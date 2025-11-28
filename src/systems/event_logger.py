"""
Game Event Logger - Tracks and reports all significant game events.

Provides comprehensive logging of creature lifecycle, combat, foraging,
building, and social interactions for observation and analysis.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import os


class EventCategory(Enum):
    """Categories of game events."""
    LIFECYCLE = "Lifecycle"
    COMBAT = "Combat"
    FORAGING = "Foraging"
    BUILDING = "Building"
    SOCIAL = "Social"
    LEARNING = "Learning"
    ENVIRONMENT = "Environment"


@dataclass
class GameEvent:
    """Represents a single game event."""
    timestamp: float  # Game time
    category: EventCategory
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Format event as readable string."""
        time_str = f"[{self.timestamp:>7.1f}s]"
        category_str = f"[{self.category.value:>11}]"
        return f"{time_str} {category_str} {self.message}"


class EventLogger:
    """
    Comprehensive game event logger.
    
    Tracks all significant game events and provides real-time logging
    and end-of-session summaries.
    """
    
    def __init__(self, log_to_console: bool = True, log_to_file: bool = True,
                 log_file_path: Optional[str] = None):
        """
        Initialize the event logger.
        
        Args:
            log_to_console: Whether to print events to console
            log_to_file: Whether to save events to file
            log_file_path: Path to log file (auto-generated if None)
        """
        self.log_to_console = log_to_console
        self.log_to_file = log_to_file
        self.events: List[GameEvent] = []
        
        # Statistics tracking
        self.stats = {
            'births': 0,
            'deaths': 0,
            'kills': {},  # creature_id -> kill count
            'damage_dealt': {},  # creature_id -> total damage
            'pellets_collected': {},  # creature_id -> pellet count
            'materials_gathered': {},  # creature_id -> material count
            'buildings_completed': 0,
            'abilities_used': 0,
            'social_interactions': 0,
        }
        
        # Death causes tracking
        self.death_causes = {}
        
        # Strain tracking
        self.strain_stats = {}  # strain_id -> stats dict
        
        # Setup log file
        if self.log_to_file:
            if log_file_path is None:
                # Create logs directory if it doesn't exist
                os.makedirs('logs', exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file_path = f'logs/game_events_{timestamp}.log'
            
            self.log_file_path = log_file_path
            self.log_file = open(log_file_path, 'w', encoding='utf-8')
            self._write_header()
    
    def _write_header(self):
        """Write header to log file."""
        if self.log_to_file:
            header = "=" * 80 + "\n"
            header += "EVOBATTLE GAME EVENT LOG\n"
            header += f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += "=" * 80 + "\n\n"
            self.log_file.write(header)
            self.log_file.flush()
    
    def log_event(self, category: EventCategory, message: str, 
                  timestamp: float, details: Optional[Dict[str, Any]] = None):
        """
        Log a game event.
        
        Args:
            category: Event category
            message: Human-readable event description
            timestamp: Game time when event occurred
            details: Additional event details
        """
        event = GameEvent(
            timestamp=timestamp,
            category=category,
            message=message,
            details=details or {}
        )
        
        self.events.append(event)
        
        # Output to console (disabled to avoid Unicode issues on Windows)
        # if self.log_to_console:
        #     print(event)
        
        # Output to file
        if self.log_to_file:
            self.log_file.write(str(event) + "\n")
            self.log_file.flush()
    
    # Lifecycle Events
    
    def log_birth(self, creature_id: str, strain_name: str, parent_ids: List[str],
                  timestamp: float, position: tuple):
        """Log creature birth."""
        parent_str = f"parents: {', '.join(parent_ids)}" if parent_ids else "initial spawn"
        message = f"BIRTH: {creature_id} ({strain_name}) born ({parent_str})"
        
        self.log_event(EventCategory.LIFECYCLE, message, timestamp, {
            'creature_id': creature_id,
            'strain': strain_name,
            'parents': parent_ids,
            'position': position
        })
        
        self.stats['births'] += 1
        self._update_strain_stat(strain_name, 'births', 1)
    
    def log_death(self, creature_id: str, strain_name: str, cause: str,
                  timestamp: float, age: float, kills: int = 0, 
                  pellets_collected: int = 0):
        """Log creature death."""
        message = f"DEATH: {creature_id} ({strain_name}) died - {cause} (age: {age:.1f}s, kills: {kills})"
        
        self.log_event(EventCategory.LIFECYCLE, message, timestamp, {
            'creature_id': creature_id,
            'strain': strain_name,
            'cause': cause,
            'age': age,
            'kills': kills,
            'pellets_collected': pellets_collected
        })
        
        self.stats['deaths'] += 1
        self.death_causes[cause] = self.death_causes.get(cause, 0) + 1
        self._update_strain_stat(strain_name, 'deaths', 1)
    
    # Combat Events
    
    def log_attack(self, attacker_id: str, attacker_strain: str,
                   target_id: str, target_strain: str,
                   damage: float, timestamp: float, ability: Optional[str] = None):
        """Log combat attack."""
        ability_str = f" using {ability}" if ability else ""
        message = f"ATTACK: {attacker_id} attacked {target_id} for {damage:.1f} damage{ability_str}"
        
        self.log_event(EventCategory.COMBAT, message, timestamp, {
            'attacker_id': attacker_id,
            'attacker_strain': attacker_strain,
            'target_id': target_id,
            'target_strain': target_strain,
            'damage': damage,
            'ability': ability
        })
        
        # Track damage dealt
        if attacker_id not in self.stats['damage_dealt']:
            self.stats['damage_dealt'][attacker_id] = 0
        self.stats['damage_dealt'][attacker_id] += damage
        
        if ability:
            self.stats['abilities_used'] += 1
    
    def log_kill(self, killer_id: str, killer_strain: str,
                 victim_id: str, victim_strain: str, timestamp: float):
        """Log creature kill."""
        message = f"KILL: {killer_id} ({killer_strain}) killed {victim_id} ({victim_strain})"
        
        self.log_event(EventCategory.COMBAT, message, timestamp, {
            'killer_id': killer_id,
            'killer_strain': killer_strain,
            'victim_id': victim_id,
            'victim_strain': victim_strain
        })
        
        # Track kills
        if killer_id not in self.stats['kills']:
            self.stats['kills'][killer_id] = 0
        self.stats['kills'][killer_id] += 1
    
    # Foraging Events
    
    def log_pellet_spawn(self, pellet_type: str, position: tuple, 
                        value: float, timestamp: float):
        """Log pellet spawning."""
        message = f"🌟 {pellet_type} pellet spawned (value: {value:.1f})"
        
        self.log_event(EventCategory.FORAGING, message, timestamp, {
            'pellet_type': pellet_type,
            'position': position,
            'value': value
        })
    
    def log_pellet_collection(self, creature_id: str, strain_name: str,
                             pellet_type: str, nutrition: float, timestamp: float):
        """Log pellet collection."""
        message = f"FORAGE: {creature_id} collected {pellet_type} pellet (+{nutrition:.1f} nutrition)"
        
        self.log_event(EventCategory.FORAGING, message, timestamp, {
            'creature_id': creature_id,
            'strain': strain_name,
            'pellet_type': pellet_type,
            'nutrition': nutrition
        })
        
        # Track pellet collection
        if creature_id not in self.stats['pellets_collected']:
            self.stats['pellets_collected'][creature_id] = 0
        self.stats['pellets_collected'][creature_id] += 1
    
    # Building Events
    
    def log_material_gather(self, creature_id: str, strain_name: str,
                           material_type: str, timestamp: float):
        """Log material gathering."""
        message = f"🪵 {creature_id} gathered {material_type}"
        
        self.log_event(EventCategory.BUILDING, message, timestamp, {
            'creature_id': creature_id,
            'strain': strain_name,
            'material_type': material_type
        })
        
        # Track material gathering
        if creature_id not in self.stats['materials_gathered']:
            self.stats['materials_gathered'][creature_id] = 0
        self.stats['materials_gathered'][creature_id] += 1
    
    def log_building_progress(self, building_id: str, building_type: str,
                             progress: float, timestamp: float):
        """Log building construction progress."""
        message = f"🏗️  Building {building_id} ({building_type}) at {progress:.0%}"
        
        self.log_event(EventCategory.BUILDING, message, timestamp, {
            'building_id': building_id,
            'building_type': building_type,
            'progress': progress
        })
    
    def log_building_complete(self, building_id: str, building_type: str,
                            timestamp: float):
        """Log building completion."""
        message = f"🏛️  Building {building_id} ({building_type}) completed!"
        
        self.log_event(EventCategory.BUILDING, message, timestamp, {
            'building_id': building_id,
            'building_type': building_type
        })
        
        self.stats['buildings_completed'] += 1
    
    # Social Events
    
    def log_social_interaction(self, creature_id: str, interaction_type: str,
                              target_id: Optional[str], timestamp: float,
                              effect: str):
        """Log social interaction."""
        target_str = f" with {target_id}" if target_id else ""
        message = f"🤝 {creature_id} {interaction_type}{target_str} - {effect}"
        
        self.log_event(EventCategory.SOCIAL, message, timestamp, {
            'creature_id': creature_id,
            'interaction_type': interaction_type,
            'target_id': target_id,
            'effect': effect
        })
        
        self.stats['social_interactions'] += 1
    
    # Learning Events
    
    def log_learning(self, creature_id: str, strain_name: str,
                    learning_type: str, knowledge: str, timestamp: float):
        """Log learning event."""
        message = f"🧠 {creature_id} learned: {knowledge} ({learning_type})"
        
        self.log_event(EventCategory.LEARNING, message, timestamp, {
            'creature_id': creature_id,
            'strain': strain_name,
            'learning_type': learning_type,
            'knowledge': knowledge
        })
    
    # Helper methods
    
    def _update_strain_stat(self, strain_name: str, stat_name: str, value: float):
        """Update strain-specific statistics."""
        if strain_name not in self.strain_stats:
            self.strain_stats[strain_name] = {}
        
        if stat_name not in self.strain_stats[strain_name]:
            self.strain_stats[strain_name][stat_name] = 0
        
        self.strain_stats[strain_name][stat_name] += value
    
    def generate_summary(self, final_timestamp: float) -> str:
        """
        Generate end-of-session summary.
        
        Args:
            final_timestamp: Final game time
            
        Returns:
            Formatted summary string
        """
        summary = "\n" + "=" * 80 + "\n"
        summary += "GAME SESSION SUMMARY\n"
        summary += "=" * 80 + "\n\n"
        
        summary += f"Session Duration: {final_timestamp:.1f} seconds\n"
        summary += f"Total Events: {len(self.events)}\n\n"
        
        # Lifecycle stats
        summary += "LIFECYCLE:\n"
        summary += f"  Births: {self.stats['births']}\n"
        summary += f"  Deaths: {self.stats['deaths']}\n"
        
        if self.death_causes:
            summary += "  Death Causes:\n"
            for cause, count in sorted(self.death_causes.items(), 
                                      key=lambda x: x[1], reverse=True):
                summary += f"    - {cause}: {count}\n"
        summary += "\n"
        
        # Combat stats
        summary += "COMBAT:\n"
        summary += f"  Total Kills: {sum(self.stats['kills'].values())}\n"
        summary += f"  Abilities Used: {self.stats['abilities_used']}\n"
        
        if self.stats['kills']:
            top_killers = sorted(self.stats['kills'].items(), 
                               key=lambda x: x[1], reverse=True)[:5]
            summary += "  Top Killers:\n"
            for creature_id, kills in top_killers:
                summary += f"    - {creature_id}: {kills} kills\n"
        summary += "\n"
        
        # Foraging stats
        summary += "FORAGING:\n"
        total_pellets = sum(self.stats['pellets_collected'].values())
        summary += f"  Total Pellets Collected: {total_pellets}\n"
        
        if self.stats['pellets_collected']:
            top_foragers = sorted(self.stats['pellets_collected'].items(),
                                key=lambda x: x[1], reverse=True)[:5]
            summary += "  Top Foragers:\n"
            for creature_id, count in top_foragers:
                summary += f"    - {creature_id}: {count} pellets\n"
        summary += "\n"
        
        # Building stats
        summary += "BUILDING:\n"
        summary += f"  Buildings Completed: {self.stats['buildings_completed']}\n"
        total_materials = sum(self.stats['materials_gathered'].values())
        summary += f"  Total Materials Gathered: {total_materials}\n\n"
        
        # Social stats
        summary += "SOCIAL:\n"
        summary += f"  Social Interactions: {self.stats['social_interactions']}\n\n"
        
        # Strain stats
        if self.strain_stats:
            summary += "STRAIN STATISTICS:\n"
            for strain, stats in self.strain_stats.items():
                summary += f"  {strain}:\n"
                for stat_name, value in stats.items():
                    summary += f"    - {stat_name}: {value}\n"
            summary += "\n"
        
        summary += "=" * 80 + "\n"
        
        return summary
    
    def close(self, final_timestamp: float):
        """
        Close the logger and write summary.
        
        Args:
            final_timestamp: Final game time
        """
        summary = self.generate_summary(final_timestamp)
        
        if self.log_to_console:
            print(summary)
        
        if self.log_to_file:
            self.log_file.write("\n" + summary)
            self.log_file.close()
            print(f"\nEvent log saved to: {self.log_file_path}")
