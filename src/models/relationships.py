"""
Relationship System - Social bonds between creatures.

Tracks family bonds, rivalries, alliances, and other relationships that
affect behavior and create emergent narratives.
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import time


class RelationshipType(Enum):
    """Types of relationships between creatures."""
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    ALLY = "ally"
    RIVAL = "rival"
    RESPECT = "respect"
    FEAR = "fear"
    REVENGE_TARGET = "revenge_target"  # This creature killed my family


@dataclass
class RelationshipEvent:
    """
    Records an event in a relationship.
    
    Attributes:
        timestamp: When the event occurred
        event_type: Type of event (e.g., "fought_together", "killed_family")
        description: Human-readable description
    """
    timestamp: float
    event_type: str
    description: str
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'description': self.description
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'RelationshipEvent':
        """Deserialize from dictionary."""
        return RelationshipEvent(**data)


class Relationship:
    """
    Represents a relationship between two creatures.
    
    Relationships have types, strength, and history.
    """
    
    def __init__(
        self,
        creature_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        strength: float = 0.5
    ):
        """
        Initialize a relationship.
        
        Args:
            creature_id: ID of the creature who has this relationship
            target_id: ID of the target creature
            relationship_type: Type of relationship
            strength: Relationship strength (0-1)
        """
        self.creature_id = creature_id
        self.target_id = target_id
        self.relationship_type = relationship_type
        self.strength = max(0.0, min(1.0, strength))
        self.formed_time: float = time.time()
        self.last_interaction: float = time.time()
        self.events: List[RelationshipEvent] = []
    
    def add_event(self, event_type: str, description: str):
        """
        Add an event to the relationship history.
        
        Args:
            event_type: Type of event
            description: Description of what happened
        """
        event = RelationshipEvent(
            timestamp=time.time(),
            event_type=event_type,
            description=description
        )
        self.events.append(event)
        self.last_interaction = time.time()
    
    def strengthen(self, amount: float = 0.1):
        """
        Strengthen the relationship.
        
        Args:
            amount: How much to strengthen (0-1)
        """
        self.strength = min(1.0, self.strength + amount)
        self.last_interaction = time.time()
    
    def weaken(self, amount: float = 0.1):
        """
        Weaken the relationship.
        
        Args:
            amount: How much to weaken (0-1)
        """
        self.strength = max(0.0, self.strength - amount)
        self.last_interaction = time.time()
    
    def decay(self, elapsed_time: float):
        """
        Decay relationship strength over time.
        
        Non-family relationships decay if not maintained.
        
        Args:
            elapsed_time: Time since last interaction in seconds
        """
        # Family bonds don't decay
        if self.relationship_type in [RelationshipType.PARENT, RelationshipType.CHILD, RelationshipType.SIBLING]:
            return
        
        # Other relationships decay slowly
        decay_rate = 0.0001  # Very slow decay
        self.strength = max(0.0, self.strength - decay_rate * elapsed_time)
    
    def get_combat_modifier(self, fighting_together: bool) -> float:
        """
        Get combat modifier based on relationship.
        
        Args:
            fighting_together: True if fighting together, False if against each other
            
        Returns:
            Damage multiplier (1.0 = no modifier)
        """
        modifier = 1.0
        
        if fighting_together:
            # Allies and family fight better together
            if self.relationship_type in [RelationshipType.ALLY, RelationshipType.PARENT, 
                                         RelationshipType.CHILD, RelationshipType.SIBLING]:
                modifier += self.strength * 0.2  # Up to +20% damage
        else:
            # Revenge targets and rivals make you fight harder
            if self.relationship_type == RelationshipType.REVENGE_TARGET:
                modifier += self.strength * 0.3  # Up to +30% damage for revenge
            elif self.relationship_type == RelationshipType.RIVAL:
                modifier += self.strength * 0.15  # Up to +15% damage vs rivals
            
            # Fear makes you fight worse against that target
            elif self.relationship_type == RelationshipType.FEAR:
                modifier -= self.strength * 0.2  # Up to -20% damage when scared
        
        return modifier
    
    def get_description(self) -> str:
        """
        Get human-readable description of relationship.
        
        Returns:
            Relationship description
        """
        strength_desc = "strong" if self.strength > 0.7 else "moderate" if self.strength > 0.4 else "weak"
        return f"{strength_desc} {self.relationship_type.value}"
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'creature_id': self.creature_id,
            'target_id': self.target_id,
            'relationship_type': self.relationship_type.value,
            'strength': self.strength,
            'formed_time': self.formed_time,
            'last_interaction': self.last_interaction,
            'events': [e.to_dict() for e in self.events]
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Relationship':
        """Deserialize from dictionary."""
        rel = Relationship(
            creature_id=data['creature_id'],
            target_id=data['target_id'],
            relationship_type=RelationshipType(data['relationship_type']),
            strength=data['strength']
        )
        rel.formed_time = data['formed_time']
        rel.last_interaction = data['last_interaction']
        rel.events = [RelationshipEvent.from_dict(e) for e in data['events']]
        return rel


class RelationshipManager:
    """
    Manages all relationships for a creature.
    
    Handles relationship formation, updates, and queries.
    """
    
    def __init__(self, creature_id: str):
        """
        Initialize relationship manager.
        
        Args:
            creature_id: ID of the creature who owns these relationships
        """
        self.creature_id = creature_id
        self.relationships: Dict[str, Relationship] = {}
    
    def add_relationship(
        self,
        target_id: str,
        relationship_type: RelationshipType,
        strength: float = 0.5
    ) -> Relationship:
        """
        Add or update a relationship.
        
        Args:
            target_id: ID of the target creature
            relationship_type: Type of relationship
            strength: Initial strength
            
        Returns:
            The relationship instance
        """
        if target_id in self.relationships:
            # Update existing relationship
            rel = self.relationships[target_id]
            rel.relationship_type = relationship_type
            rel.strength = strength
        else:
            # Create new relationship
            rel = Relationship(self.creature_id, target_id, relationship_type, strength)
            self.relationships[target_id] = rel
        
        return rel
    
    def get_relationship(self, target_id: str) -> Optional[Relationship]:
        """
        Get relationship with a specific creature.
        
        Args:
            target_id: ID of the target creature
            
        Returns:
            Relationship if it exists, None otherwise
        """
        return self.relationships.get(target_id)
    
    def has_relationship(self, target_id: str, relationship_type: Optional[RelationshipType] = None) -> bool:
        """
        Check if a relationship exists.
        
        Args:
            target_id: ID of the target creature
            relationship_type: Optional specific type to check for
            
        Returns:
            True if relationship exists (and matches type if specified)
        """
        if target_id not in self.relationships:
            return False
        
        if relationship_type is None:
            return True
        
        return self.relationships[target_id].relationship_type == relationship_type
    
    def record_fought_together(self, ally_id: str):
        """
        Record fighting together with an ally.
        
        Args:
            ally_id: ID of the ally
        """
        rel = self.get_relationship(ally_id)
        if rel:
            rel.strengthen(0.05)
            rel.add_event("fought_together", "Fought alongside in battle")
        else:
            # Create ally relationship
            rel = self.add_relationship(ally_id, RelationshipType.ALLY, strength=0.3)
            rel.add_event("fought_together", "First time fighting together")
    
    def record_family_killed(self, killer_id: str, family_member_name: str):
        """
        Record that a family member was killed.
        
        Args:
            killer_id: ID of the killer
            family_member_name: Name of the family member
        """
        # Create or upgrade to revenge target
        rel = self.add_relationship(killer_id, RelationshipType.REVENGE_TARGET, strength=1.0)
        rel.add_event("killed_family", f"Killed {family_member_name}")
    
    def record_revenge_completed(self, target_id: str):
        """
        Record that revenge was completed against a target.
        
        Args:
            target_id: ID of the revenge target
        """
        rel = self.get_relationship(target_id)
        if rel and rel.relationship_type == RelationshipType.REVENGE_TARGET:
            rel.add_event("revenge_completed", "Revenge has been achieved")
            # Convert to rival with weaker bond
            rel.relationship_type = RelationshipType.RIVAL
            rel.strength = 0.5
    
    def record_lost_to(self, enemy_id: str):
        """
        Record losing a fight to an enemy.
        
        Args:
            enemy_id: ID of the enemy who won
        """
        rel = self.get_relationship(enemy_id)
        if rel:
            if rel.relationship_type == RelationshipType.FEAR:
                rel.strengthen(0.1)
            else:
                # May develop fear or respect
                if rel.strength > 0.5:
                    rel.relationship_type = RelationshipType.RESPECT
                else:
                    rel.relationship_type = RelationshipType.FEAR
            rel.add_event("lost_fight", "Lost a battle")
        else:
            # First loss - create fear/respect relationship
            rel = self.add_relationship(enemy_id, RelationshipType.FEAR, strength=0.4)
            rel.add_event("lost_fight", "Lost first battle against this opponent")
    
    def record_defeated(self, enemy_id: str):
        """
        Record defeating an enemy.
        
        Args:
            enemy_id: ID of the defeated enemy
        """
        rel = self.get_relationship(enemy_id)
        if rel:
            # If we had fear, reduce it
            if rel.relationship_type == RelationshipType.FEAR:
                rel.weaken(0.2)
                if rel.strength < 0.3:
                    # No longer fear them, maybe respect
                    rel.relationship_type = RelationshipType.RESPECT
            rel.add_event("won_fight", "Won a battle")
        else:
            # First victory - might create rivalry
            rel = self.add_relationship(enemy_id, RelationshipType.RIVAL, strength=0.3)
            rel.add_event("won_fight", "Won first battle against this opponent")
    
    def get_family(self) -> List[Relationship]:
        """
        Get all family relationships.
        
        Returns:
            List of family relationships
        """
        return [
            rel for rel in self.relationships.values()
            if rel.relationship_type in [RelationshipType.PARENT, RelationshipType.CHILD, RelationshipType.SIBLING]
        ]
    
    def get_allies(self) -> List[Relationship]:
        """
        Get all ally relationships.
        
        Returns:
            List of ally relationships
        """
        return [
            rel for rel in self.relationships.values()
            if rel.relationship_type == RelationshipType.ALLY
        ]
    
    def get_enemies(self) -> List[Relationship]:
        """
        Get all enemy relationships (rivals, revenge targets).
        
        Returns:
            List of enemy relationships
        """
        return [
            rel for rel in self.relationships.values()
            if rel.relationship_type in [RelationshipType.RIVAL, RelationshipType.REVENGE_TARGET]
        ]
    
    def get_revenge_targets(self) -> List[Relationship]:
        """
        Get all revenge targets.
        
        Returns:
            List of revenge target relationships
        """
        return [
            rel for rel in self.relationships.values()
            if rel.relationship_type == RelationshipType.REVENGE_TARGET
        ]
    
    def update_decay(self):
        """Update decay for all relationships."""
        current_time = time.time()
        for rel in self.relationships.values():
            elapsed = current_time - rel.last_interaction
            rel.decay(elapsed)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'creature_id': self.creature_id,
            'relationships': {
                target_id: rel.to_dict()
                for target_id, rel in self.relationships.items()
            }
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'RelationshipManager':
        """Deserialize from dictionary."""
        manager = RelationshipManager(data['creature_id'])
        for target_id, rel_data in data['relationships'].items():
            rel = Relationship.from_dict(rel_data)
            manager.relationships[target_id] = rel
        return manager
