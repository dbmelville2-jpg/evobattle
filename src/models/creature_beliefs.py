"""
Creature Belief System - Adaptive Learning for EvoBattle

This module implements a cognitive layer for creatures, allowing them to form
beliefs about their environment based on experience, observation, and player
intervention. Inspired by Black & White's creature AI learning system.

Creatures develop beliefs about:
- Food locations (where to find resources)
- Danger zones (areas to avoid)
- Safe areas (protected locations)
- Allies (friendly creatures)
- Threats (dangerous creatures)

Beliefs have confidence levels that strengthen with reinforcement and decay
over time if not reinforced. Creatures have limited memory capacity.
"""

from typing import Dict, Optional, List
from enum import Enum
import time


class BeliefType(Enum):
    """Types of beliefs creatures can form"""
    FOOD_LOCATION = "food_location"
    DANGER_ZONE = "danger_zone"
    SAFE_AREA = "safe_area"
    ALLY = "ally"
    THREAT = "threat"
    SHELTER = "shelter"
    WATER_SOURCE = "water_source"
    NESTING_SITE = "nesting_site"
    # Building-related beliefs
    BUILDING_LOCATION = "building_location"      # Good place to build
    MATERIAL_SOURCE = "material_source"          # Where to find materials
    STRUCTURE_BENEFIT = "structure_benefit"      # Structure is useful
    CONSTRUCTION_SKILL = "construction_skill"    # Confidence in building ability


class CreatureBelief:
    """
    Represents a single belief a creature holds about the world.
    
    Beliefs are learned through experience and can be reinforced or decay.
    Each belief has a confidence level (0.0-1.0) that affects how strongly
    the creature acts on it.
    
    Attributes:
        belief_type: Category of belief (food, danger, etc.)
        target: Identifier for what the belief is about (e.g., "area_50_30")
        confidence: Strength of belief (0.0-1.0)
        last_reinforced: Timestamp of last reinforcement
        creation_time: When belief was first formed
        reinforcement_count: Number of times belief was reinforced
    """
    
    def __init__(self, belief_type: BeliefType, target: str, confidence: float = 0.5):
        """
        Create a new belief.
        
        Args:
            belief_type: Type of belief being formed
            target: What the belief is about (location, creature ID, etc.)
            confidence: Initial confidence level (0.0-1.0)
        """
        self.belief_type = belief_type
        self.target = target
        self.confidence = max(0.0, min(1.0, confidence))
        self.last_reinforced = time.time()
        self.creation_time = time.time()
        self.reinforcement_count = 0
        
    def reinforce(self, amount: float = 0.1):
        """
        Strengthen this belief through positive reinforcement.
        
        Args:
            amount: How much to increase confidence (default 0.1)
        """
        self.confidence = min(1.0, self.confidence + amount)
        self.last_reinforced = time.time()
        self.reinforcement_count += 1
        
    def weaken(self, amount: float = 0.1):
        """
        Weaken this belief through negative experience.
        
        Args:
            amount: How much to decrease confidence (default 0.1)
        """
        self.confidence = max(0.0, self.confidence - amount)
        self.last_reinforced = time.time()
        
    def decay(self, decay_rate: float = 0.01):
        """
        Natural decay of belief over time if not reinforced.
        
        Args:
            decay_rate: Rate of confidence decay per second
        """
        time_since_reinforcement = time.time() - self.last_reinforced
        decay_amount = decay_rate * time_since_reinforcement
        self.confidence = max(0.0, self.confidence - decay_amount)
        
    def age(self) -> float:
        """Get age of belief in seconds"""
        return time.time() - self.creation_time
        
    def __repr__(self):
        return f"Belief({self.belief_type.value}, {self.target}, conf={self.confidence:.2f})"


class CreatureBeliefSystem:
    """
    Manages all beliefs for a single creature.
    
    This system handles:
    - Adding new beliefs (with memory capacity limits)
    - Reinforcing existing beliefs
    - Belief decay over time
    - Querying beliefs for decision-making
    - Removing weak or outdated beliefs
    
    Creatures have limited memory capacity - when full, the weakest beliefs
    are forgotten to make room for new ones.
    """
    
    def __init__(self, memory_capacity: int = 20):
        """
        Initialize belief system.
        
        Args:
            memory_capacity: Maximum number of beliefs creature can hold
        """
        self.beliefs: Dict[str, CreatureBelief] = {}
        self.memory_capacity = memory_capacity
        self.decay_rate = 0.001  # Beliefs decay slowly if not reinforced
        
    def add_belief(self, belief: CreatureBelief) -> bool:
        """
        Add a new belief or reinforce existing one.
        
        If belief about same target exists, it's reinforced instead.
        If at capacity, weakest belief is removed.
        
        Args:
            belief: Belief to add
            
        Returns:
            True if belief was added, False if capacity reached and belief too weak
        """
        # Check if belief about this target already exists
        if belief.target in self.beliefs:
            # Reinforce existing belief
            self.beliefs[belief.target].reinforce(0.15)
            return True
            
        # Check memory capacity
        if len(self.beliefs) >= self.memory_capacity:
            # Find weakest belief
            weakest_target = min(self.beliefs.keys(), 
                               key=lambda t: self.beliefs[t].confidence)
            weakest_confidence = self.beliefs[weakest_target].confidence
            
            # Only replace if new belief is stronger
            if belief.confidence > weakest_confidence:
                del self.beliefs[weakest_target]
            else:
                return False
                
        # Add new belief
        self.beliefs[belief.target] = belief
        return True
        
    def get_belief(self, target: str) -> Optional[CreatureBelief]:
        """
        Get belief about specific target.
        
        Args:
            target: Target identifier
            
        Returns:
            Belief if exists, None otherwise
        """
        return self.beliefs.get(target)
        
    def get_beliefs_by_type(self, belief_type: BeliefType) -> List[CreatureBelief]:
        """
        Get all beliefs of a specific type.
        
        Args:
            belief_type: Type of beliefs to retrieve
            
        Returns:
            List of matching beliefs, sorted by confidence (highest first)
        """
        matching = [b for b in self.beliefs.values() if b.belief_type == belief_type]
        return sorted(matching, key=lambda b: b.confidence, reverse=True)
        
    def get_strongest_belief(self, belief_type: BeliefType) -> Optional[CreatureBelief]:
        """
        Get the strongest belief of a specific type.
        
        Args:
            belief_type: Type of belief to find
            
        Returns:
            Strongest belief of that type, or None if none exist
        """
        beliefs = self.get_beliefs_by_type(belief_type)
        return beliefs[0] if beliefs else None
        
    def remove_belief(self, target: str) -> bool:
        """
        Remove a specific belief.
        
        Args:
            target: Target identifier
            
        Returns:
            True if belief was removed, False if didn't exist
        """
        if target in self.beliefs:
            del self.beliefs[target]
            return True
        return False
        
    def update(self, dt: float):
        """
        Update all beliefs - apply decay and remove very weak beliefs.
        
        Args:
            dt: Time delta in seconds
        """
        # Apply decay to all beliefs
        for belief in list(self.beliefs.values()):
            belief.decay(self.decay_rate * dt)
            
        # Remove beliefs that have decayed to near-zero confidence
        to_remove = [target for target, belief in self.beliefs.items() 
                    if belief.confidence < 0.05]
        for target in to_remove:
            del self.beliefs[target]
            
    def clear_beliefs_of_type(self, belief_type: BeliefType):
        """
        Remove all beliefs of a specific type.
        
        Args:
            belief_type: Type of beliefs to clear
        """
        to_remove = [target for target, belief in self.beliefs.items() 
                    if belief.belief_type == belief_type]
        for target in to_remove:
            del self.beliefs[target]
            
    def get_belief_count(self) -> int:
        """Get total number of beliefs"""
        return len(self.beliefs)
        
    def get_average_confidence(self) -> float:
        """Get average confidence across all beliefs"""
        if not self.beliefs:
            return 0.0
        return sum(b.confidence for b in self.beliefs.values()) / len(self.beliefs)
        
    def get_summary(self) -> Dict:
        """
        Get summary statistics about belief system.
        
        Returns:
            Dictionary with belief statistics
        """
        return {
            "total_beliefs": len(self.beliefs),
            "capacity": self.memory_capacity,
            "average_confidence": self.get_average_confidence(),
            "beliefs_by_type": {
                bt.value: len(self.get_beliefs_by_type(bt))
                for bt in BeliefType
            }
        }
        
    def __repr__(self):
        return f"BeliefSystem({len(self.beliefs)}/{self.memory_capacity} beliefs, avg_conf={self.get_average_confidence():.2f})"
