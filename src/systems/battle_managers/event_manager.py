"""
Event Manager

Handles event emission, callback management, and battle logging
for the spatial battle system.

Extracted from battle_spatial.py to improve separation of concerns.
"""

from typing import List, Callable
from ..battle_events import BattleEvent


class EventManager:
    """
    Manages battle events and logging.
    
    Responsibilities:
    - Emit battle events to registered callbacks
    - Manage event history with bounded growth
    - Handle battle log messages
    - Provide event/log access for UI and debugging
    """
    
    # Memory management: Max sizes for event/log lists to prevent unbounded growth
    MAX_EVENTS = 1000  # Keep last 1000 events
    MAX_BATTLE_LOG = 500  # Keep last 500 log messages
    
    def __init__(self):
        """Initialize the event manager."""
        self.events: List[BattleEvent] = []
        self.battle_log: List[str] = []
        self._event_callbacks: List[Callable[[BattleEvent], None]] = []
    
    def emit_event(self, event: BattleEvent):
        """
        Emit a battle event to all registered callbacks.
        
        Args:
            event: The battle event to emit
        """
        self.events.append(event)
        
        # Prevent unbounded growth - keep only recent events
        if len(self.events) > self.MAX_EVENTS:
            # Remove oldest events, keeping the most recent MAX_EVENTS
            self.events = self.events[-self.MAX_EVENTS:]
        
        # Notify all callbacks
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.log(f"Error in event callback: {e}")
    
    def add_callback(self, callback: Callable[[BattleEvent], None]):
        """
        Register a callback function for battle events.
        
        Args:
            callback: Function to call when events are emitted
        """
        self._event_callbacks.append(callback)
    
    def log(self, message: str):
        """
        Add a message to the battle log.
        
        Args:
            message: Log message to add
        """
        self.battle_log.append(message)
        
        # Prevent unbounded growth - keep only recent log messages
        if len(self.battle_log) > self.MAX_BATTLE_LOG:
            # Remove oldest messages, keeping the most recent MAX_BATTLE_LOG
            self.battle_log = self.battle_log[-self.MAX_BATTLE_LOG:]
    
    def get_events(self) -> List[BattleEvent]:
        """
        Get all stored events.
        
        Returns:
            List of battle events
        """
        return self.events
    
    def get_battle_log(self) -> List[str]:
        """
        Get the battle log.
        
        Returns:
            List of log messages
        """
        return self.battle_log
    
    def clear_events(self):
        """Clear all stored events."""
        self.events = []
    
    def clear_log(self):
        """Clear the battle log."""
        self.battle_log = []
