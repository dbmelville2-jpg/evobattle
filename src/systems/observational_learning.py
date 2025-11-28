"""
Observational Learning System - Creatures Learn by Watching

This module implements the core Black & White mechanic where creatures observe
and learn from the successful actions of nearby peers. This creates emergent
social learning and allows knowledge to spread through populations.

Key Features:
- Creatures watch nearby successful actions (eating, fleeing, fighting)
- Learning rate influenced by traits (Mimic, Quick Learner, Stubborn)
- Observation range and line-of-sight checks
- Beliefs formed from repeated observations
- Social learning spreads knowledge through populations
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
from enum import Enum
import math

from src.models.creature_beliefs import CreatureBeliefSystem, CreatureBelief, BeliefType


class ActionType(Enum):
    """Types of observable actions"""
    FORAGE_SUCCESS = "forage_success"
    FLEE_DANGER = "flee_danger"
    COMBAT_VICTORY = "combat_victory"
    FIND_SHELTER = "find_shelter"
    DRINK_WATER = "drink_water"
    REST_SAFELY = "rest_safely"


class ActionOutcome(Enum):
    """Outcome of an action"""
    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"


@dataclass
class ObservableAction:
    """
    Represents an action that can be observed and learned from.
    
    Attributes:
        action_type: Type of action performed
        position: World position where action occurred
        outcome: Whether action was successful
        performer_id: ID of creature who performed action
        timestamp: When action occurred
        context: Additional context (e.g., "found_food", "avoided_predator")
    """
    action_type: ActionType
    position: Tuple[float, float]
    outcome: ActionOutcome
    performer_id: str
    timestamp: float
    context: str = ""


class ObservationalLearning:
    """
    Manages observational learning for a single creature.
    
    Creatures can watch nearby successful actions and form beliefs based on
    what they observe. Learning is influenced by traits and requires the
    observer to be within range and have line-of-sight.
    """
    
    def __init__(self, creature_id: str, belief_system: CreatureBeliefSystem):
        """
        Initialize observational learning for a creature.
        
        Args:
            creature_id: Unique identifier for this creature
            belief_system: Creature's belief system to update
        """
        self.creature_id = creature_id
        self.belief_system = belief_system
        
        # Base learning parameters (modified by traits)
        self.base_observation_range = 15.0
        self.base_learning_rate = 0.3
        
        # Current modifiers (set by traits)
        self.observation_range_multiplier = 1.0
        self.learning_rate_multiplier = 1.0
        self.imitation_success_rate = 1.0
        
        # Track what we've observed recently
        self.recent_observations: List[ObservableAction] = []
        self.max_recent_observations = 20
        
    def apply_trait_modifiers(self, traits: List):
        """
        Apply trait modifiers to learning parameters.
        
        Args:
            traits: List of creature's traits
        """
        for trait in traits:
            effects = getattr(trait, 'interaction_effects', {})
            
            # Observation range modifiers
            if 'observation_range_multiplier' in effects:
                self.observation_range_multiplier *= effects['observation_range_multiplier']
                
            # Learning rate modifiers
            if 'learning_rate_multiplier' in effects:
                self.learning_rate_multiplier *= effects['learning_rate_multiplier']
                
            # Imitation success rate (for Mimic trait)
            if 'imitation_success_rate' in effects:
                self.imitation_success_rate *= effects['imitation_success_rate']
                
    def get_observation_range(self) -> float:
        """
        Get effective observation range.
        
        Returns:
            Observation range in world units
        """
        return self.base_observation_range * self.observation_range_multiplier
        
    def get_learning_rate(self) -> float:
        """
        Get effective learning rate.
        
        Returns:
            Learning rate multiplier (0.0 to 2.0+)
        """
        return self.base_learning_rate * self.learning_rate_multiplier
        
    def can_observe(self, observer_pos: Tuple[float, float], 
                   action: ObservableAction,
                   obstacles: Optional[List[Tuple[float, float]]] = None) -> bool:
        """
        Check if creature can observe an action.
        
        Args:
            observer_pos: Position of observing creature
            action: Action to observe
            obstacles: Optional list of obstacle positions (for line-of-sight)
            
        Returns:
            True if action is observable
        """
        # Don't observe own actions
        if action.performer_id == self.creature_id:
            return False
            
        # Check range
        distance = self._calculate_distance(observer_pos, action.position)
        if distance > self.get_observation_range():
            return False
            
        # Check line-of-sight (simplified - just check if obstacles block)
        if obstacles and self._is_line_blocked(observer_pos, action.position, obstacles):
            return False
            
        return True
        
    def observe_action(self, observer_pos: Tuple[float, float], 
                      action: ObservableAction,
                      current_time: float) -> Optional[CreatureBelief]:
        """
        Process an observed action and potentially form a belief.
        
        Args:
            observer_pos: Position of observing creature
            action: Action being observed
            current_time: Current simulation time
            
        Returns:
            CreatureBelief if one was formed, None otherwise
        """
        # Only learn from successful actions
        if action.outcome != ActionOutcome.SUCCESS:
            return None
            
        # Track observation
        self.recent_observations.append(action)
        if len(self.recent_observations) > self.max_recent_observations:
            self.recent_observations.pop(0)
            
        # Determine what to learn based on action type
        belief = self._create_belief_from_action(action)
        
        if belief:
            # Apply learning rate to confidence
            belief.confidence *= self.get_learning_rate()
            
            # Apply imitation success rate
            belief.confidence *= self.imitation_success_rate
            
            # Clamp confidence
            belief.confidence = min(1.0, max(0.1, belief.confidence))
            
            # Add to belief system
            self.belief_system.add_belief(belief)
            
            return belief
            
        return None
        
    def _create_belief_from_action(self, action: ObservableAction) -> Optional[CreatureBelief]:
        """
        Create appropriate belief based on observed action.
        
        Args:
            action: Observed action
            
        Returns:
            CreatureBelief or None
        """
        if action.action_type == ActionType.FORAGE_SUCCESS:
            # Learn food location
            return CreatureBelief(
                belief_type=BeliefType.FOOD_LOCATION,
                target=f"area_{int(action.position[0])}_{int(action.position[1])}",
                confidence=0.6  # Base confidence for observed foraging
            )
            
        elif action.action_type == ActionType.FLEE_DANGER:
            # Learn danger zone
            return CreatureBelief(
                belief_type=BeliefType.DANGER_ZONE,
                target=f"area_{int(action.position[0])}_{int(action.position[1])}",
                confidence=0.7  # Higher confidence for danger
            )
            
        elif action.action_type == ActionType.FIND_SHELTER:
            # Learn safe area
            return CreatureBelief(
                belief_type=BeliefType.SAFE_AREA,
                target=f"area_{int(action.position[0])}_{int(action.position[1])}",
                confidence=0.5
            )
            
        elif action.action_type == ActionType.DRINK_WATER:
            # Learn water source
            return CreatureBelief(
                belief_type=BeliefType.WATER_SOURCE,
                target=f"area_{int(action.position[0])}_{int(action.position[1])}",
                confidence=0.6
            )
            
        elif action.action_type == ActionType.REST_SAFELY:
            # Learn shelter location
            return CreatureBelief(
                belief_type=BeliefType.SHELTER,
                target=f"area_{int(action.position[0])}_{int(action.position[1])}",
                confidence=0.5
            )
            
        elif action.action_type == ActionType.COMBAT_VICTORY:
            # Learn about ally (successful fighter)
            return CreatureBelief(
                belief_type=BeliefType.ALLY,
                target=action.performer_id,
                confidence=0.4
            )
            
        return None
        
    def get_observation_count(self, action_type: ActionType, 
                             time_window: float = 60.0,
                             current_time: float = 0.0) -> int:
        """
        Count how many times an action type was observed recently.
        
        Args:
            action_type: Type of action to count
            time_window: Time window in seconds
            current_time: Current simulation time
            
        Returns:
            Number of observations
        """
        count = 0
        for obs in self.recent_observations:
            if obs.action_type == action_type:
                if current_time - obs.timestamp <= time_window:
                    count += 1
        return count
        
    def _calculate_distance(self, pos1: Tuple[float, float], 
                           pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two positions"""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return math.sqrt(dx * dx + dy * dy)
        
    def _is_line_blocked(self, start: Tuple[float, float], 
                        end: Tuple[float, float],
                        obstacles: List[Tuple[float, float]],
                        obstacle_radius: float = 2.0) -> bool:
        """
        Check if line-of-sight is blocked by obstacles.
        
        Simplified check: see if any obstacle is close to the line segment.
        
        Args:
            start: Start position
            end: End position
            obstacles: List of obstacle positions
            obstacle_radius: Radius around obstacles that blocks sight
            
        Returns:
            True if line is blocked
        """
        # Simplified: check if any obstacle is within radius of line midpoint
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        for obs_pos in obstacles:
            dist = self._calculate_distance((mid_x, mid_y), obs_pos)
            if dist < obstacle_radius:
                return True
                
        return False
        
    def get_summary(self) -> dict:
        """
        Get summary of learning state.
        
        Returns:
            Dictionary with learning statistics
        """
        return {
            "observation_range": self.get_observation_range(),
            "learning_rate": self.get_learning_rate(),
            "imitation_success_rate": self.imitation_success_rate,
            "recent_observations": len(self.recent_observations),
            "observations_by_type": {
                action_type.value: sum(1 for obs in self.recent_observations 
                                      if obs.action_type == action_type)
                for action_type in ActionType
            }
        }
        
    def __repr__(self):
        return (f"ObservationalLearning(range={self.get_observation_range():.1f}, "
                f"learning_rate={self.get_learning_rate():.2f}, "
                f"observations={len(self.recent_observations)})")


class ObservationalLearningManager:
    """
    Manages observational learning for all creatures in the simulation.
    
    This is the system-level manager that broadcasts observable actions
    to all nearby creatures and processes learning updates.
    """
    
    def __init__(self):
        """Initialize the learning manager"""
        self.learners: Dict[str, ObservationalLearning] = {}
        self.action_history: List[ObservableAction] = []
        self.max_history = 100
        
    def register_learner(self, creature_id: str, 
                        belief_system: CreatureBeliefSystem,
                        traits: List) -> ObservationalLearning:
        """
        Register a creature for observational learning.
        
        Args:
            creature_id: Unique creature identifier
            belief_system: Creature's belief system
            traits: Creature's traits
            
        Returns:
            ObservationalLearning instance for this creature
        """
        learner = ObservationalLearning(creature_id, belief_system)
        learner.apply_trait_modifiers(traits)
        self.learners[creature_id] = learner
        return learner
        
    def unregister_learner(self, creature_id: str):
        """Remove a creature from learning system"""
        if creature_id in self.learners:
            del self.learners[creature_id]
            
    def broadcast_action(self, action: ObservableAction, 
                        creature_positions: Dict[str, Tuple[float, float]],
                        current_time: float,
                        obstacles: Optional[List[Tuple[float, float]]] = None) -> int:
        """
        Broadcast an observable action to all nearby creatures.
        
        Args:
            action: Action to broadcast
            creature_positions: Dict mapping creature IDs to positions
            current_time: Current simulation time
            obstacles: Optional obstacle positions
            
        Returns:
            Number of creatures that observed the action
        """
        # Add to history
        self.action_history.append(action)
        if len(self.action_history) > self.max_history:
            self.action_history.pop(0)
            
        # Broadcast to all learners
        observers = 0
        for creature_id, learner in self.learners.items():
            if creature_id not in creature_positions:
                continue
                
            observer_pos = creature_positions[creature_id]
            
            # Check if creature can observe
            if learner.can_observe(observer_pos, action, obstacles):
                # Process observation
                belief = learner.observe_action(observer_pos, action, current_time)
                if belief:
                    observers += 1
                    
        return observers
        
    def get_statistics(self) -> dict:
        """
        Get system-wide learning statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_learners": len(self.learners),
            "total_actions_recorded": len(self.action_history),
            "average_observation_range": sum(l.get_observation_range() 
                                            for l in self.learners.values()) / max(1, len(self.learners)),
            "average_learning_rate": sum(l.get_learning_rate() 
                                        for l in self.learners.values()) / max(1, len(self.learners))
        }
