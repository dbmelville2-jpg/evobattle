"""
Attention and Focus System for Agents.

Manages agent attention span, focus, and prioritization of stimuli.
Prevents erratic behavior by enforcing commitment times and priority thresholds.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import time


class StimulusType(Enum):
    """Types of stimuli that can capture agent attention."""
    COMBAT = "combat"           # Fighting enemies
    FORAGING = "foraging"       # Seeking food/resources
    FLEEING = "fleeing"         # Escaping danger
    EXPLORING = "exploring"     # Wandering and curiosity
    SOCIAL = "social"           # Interacting with allies
    HAZARD_AVOIDANCE = "hazard_avoidance"  # Avoiding environmental hazards
    BUILDING = "building"       # Constructing structures
    IDLE = "idle"               # No particular focus


@dataclass
class StimulusPriority:
    """
    Priority configuration for different stimulus types.
    
    Attributes:
        base_priority: Base importance (0-100, higher = more important)
        min_commitment_time: Minimum seconds to stay focused on this stimulus
        distraction_threshold: How much better another stimulus must be to switch (0-1)
    """
    base_priority: float = 50.0
    min_commitment_time: float = 2.0
    distraction_threshold: float = 0.3


class AttentionManager:
    """
    Manages an agent's attention, focus, and stimulus prioritization.
    
    Prevents rapid switching between activities by enforcing commitment times
    and priority thresholds. Traits can modify behavior to create different
    agent personalities (distractible, persistent, tunnel vision, opportunist).
    """
    
    # Default priority configurations for each stimulus type
    DEFAULT_PRIORITIES: Dict[StimulusType, StimulusPriority] = {
        StimulusType.FLEEING: StimulusPriority(
            base_priority=95.0,
            min_commitment_time=1.5,
            distraction_threshold=0.1  # Easy to distract when fleeing if threat passes
        ),
        StimulusType.COMBAT: StimulusPriority(
            base_priority=70.0,
            min_commitment_time=2.5,
            distraction_threshold=0.4  # Harder to distract in combat
        ),
        StimulusType.FORAGING: StimulusPriority(
            base_priority=60.0,
            min_commitment_time=2.0,
            distraction_threshold=0.3
        ),
        StimulusType.HAZARD_AVOIDANCE: StimulusPriority(
            base_priority=85.0,
            min_commitment_time=1.0,
            distraction_threshold=0.2
        ),
        StimulusType.SOCIAL: StimulusPriority(
            base_priority=40.0,
            min_commitment_time=1.5,
            distraction_threshold=0.4
        ),
        StimulusType.EXPLORING: StimulusPriority(
            base_priority=30.0,
            min_commitment_time=3.0,
            distraction_threshold=0.5  # Easy to distract wanderers
        ),
        StimulusType.BUILDING: StimulusPriority(
            base_priority=35.0,  # Lower than foraging (60.0) for non-builders
            min_commitment_time=4.0,
            distraction_threshold=0.3  # Harder to distract when building
        ),
        StimulusType.IDLE: StimulusPriority(
            base_priority=0.0,
            min_commitment_time=0.0,
            distraction_threshold=0.0  # Always willing to do something
        ),
    }
    
    def __init__(
        self,
        trait_modifiers: Optional[Dict[str, float]] = None
    ):
        """
        Initialize attention manager.
        
        Args:
            trait_modifiers: Trait-based modifiers for attention behavior
                - 'persistence': Increases commitment times (0.5-2.0, default 1.0)
                - 'distractibility': Decreases distraction thresholds (0.5-2.0, default 1.0)
                - 'tunnel_vision': Greatly increases commitment, decreases threshold changes
                - 'opportunism': Decreases commitment, increases threshold changes
        """
        self.current_focus: StimulusType = StimulusType.IDLE
        self.focus_start_time: float = 0.0
        self.focus_context: Dict[str, Any] = {}  # Additional context for current focus
        
        # Trait modifiers
        self.trait_modifiers = trait_modifiers or {}
        self.persistence_modifier = self.trait_modifiers.get('persistence', 1.0)
        self.distractibility_modifier = self.trait_modifiers.get('distractibility', 1.0)
        self.building_priority_modifier = self.trait_modifiers.get('building_priority', 0.0)  # Additive modifier
        
        # Apply trait modifiers to default priorities
        self.priorities = self._apply_trait_modifiers(self.DEFAULT_PRIORITIES.copy())
    
    def _apply_trait_modifiers(
        self,
        priorities: Dict[StimulusType, StimulusPriority]
    ) -> Dict[StimulusType, StimulusPriority]:
        """
        Apply trait modifiers to priority configurations.
        
        Args:
            priorities: Base priority configurations
            
        Returns:
            Modified priority configurations based on traits
        """
        modified = {}
        
        for stimulus_type, priority in priorities.items():
            # Create a copy to avoid modifying defaults
            modified_priority = StimulusPriority(
                base_priority=priority.base_priority,
                min_commitment_time=priority.min_commitment_time * self.persistence_modifier,
                distraction_threshold=priority.distraction_threshold / self.distractibility_modifier
            )
            
            # Apply building-specific priority modifier
            if stimulus_type == StimulusType.BUILDING:
                modified_priority.base_priority += self.building_priority_modifier
                # Clamp building priority to reasonable range
                modified_priority.base_priority = max(10.0, min(90.0, modified_priority.base_priority))
            
            # Clamp values to reasonable ranges
            modified_priority.min_commitment_time = max(0.5, min(10.0, modified_priority.min_commitment_time))
            modified_priority.distraction_threshold = max(0.05, min(0.9, modified_priority.distraction_threshold))
            
            modified[stimulus_type] = modified_priority
        
        return modified
    
    def get_current_focus(self) -> StimulusType:
        """Get the current focus/attention state."""
        return self.current_focus
    
    def get_focus_duration(self, current_time: float) -> float:
        """
        Get how long the agent has been focused on current stimulus.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            Duration in seconds
        """
        if self.focus_start_time == 0.0:
            return 0.0
        return current_time - self.focus_start_time
    
    def is_committed(self, current_time: float) -> bool:
        """
        Check if agent is still committed to current focus.
        
        An agent is committed if they haven't met the minimum commitment time yet.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            True if still committed to current focus
        """
        if self.current_focus == StimulusType.IDLE:
            return False
        
        duration = self.get_focus_duration(current_time)
        min_time = self.priorities[self.current_focus].min_commitment_time
        
        return duration < min_time
    
    def calculate_effective_priority(
        self,
        stimulus_type: StimulusType,
        urgency_modifier: float = 1.0,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate effective priority for a stimulus considering context.
        
        Args:
            stimulus_type: Type of stimulus
            urgency_modifier: Urgency multiplier (e.g., 2.0 for critical hunger)
            context: Additional context that may affect priority
            
        Returns:
            Effective priority value (0-100+)
        """
        base = self.priorities[stimulus_type].base_priority
        return base * urgency_modifier
    
    def should_switch_focus(
        self,
        new_stimulus: StimulusType,
        new_priority: float,
        current_time: float
    ) -> bool:
        """
        Determine if agent should switch focus to a new stimulus.
        
        Args:
            new_stimulus: The new stimulus type to consider
            new_priority: Effective priority of the new stimulus
            current_time: Current simulation time
            
        Returns:
            True if should switch focus
        """
        # Always willing to switch from idle
        if self.current_focus == StimulusType.IDLE:
            return True
        
        # Check if still committed to current focus
        if self.is_committed(current_time):
            # Can only switch if new stimulus is MUCH more important
            current_priority = self.calculate_effective_priority(self.current_focus)
            
            # Need significant priority advantage to break commitment
            threshold = self.priorities[self.current_focus].distraction_threshold
            priority_difference = new_priority - current_priority
            
            # Require new stimulus to be threshold% better
            required_advantage = current_priority * threshold
            
            return priority_difference > required_advantage
        
        # Not committed - compare priorities with distraction threshold
        current_priority = self.calculate_effective_priority(self.current_focus)
        threshold = self.priorities[self.current_focus].distraction_threshold
        
        # New stimulus must be threshold% better than current
        required_advantage = current_priority * threshold
        priority_difference = new_priority - current_priority
        
        return priority_difference > required_advantage
    
    def set_focus(
        self,
        new_focus: StimulusType,
        current_time: float,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Set new focus for the agent.
        
        Args:
            new_focus: New stimulus type to focus on
            current_time: Current simulation time
            context: Optional context data for this focus
        """
        self.current_focus = new_focus
        self.focus_start_time = current_time
        self.focus_context = context or {}
    
    def evaluate_and_update_focus(
        self,
        stimuli: Dict[StimulusType, float],
        current_time: float,
        force_reevaluate: bool = False
    ) -> StimulusType:
        """
        Evaluate all available stimuli and update focus if appropriate.
        
        Args:
            stimuli: Dictionary mapping stimulus types to their effective priorities
            current_time: Current simulation time
            force_reevaluate: Force reevaluation even if committed
            
        Returns:
            The current/new focus after evaluation
        """
        if not stimuli:
            return self.current_focus
        
        # Find highest priority stimulus
        best_stimulus = max(stimuli.keys(), key=lambda s: stimuli[s])
        best_priority = stimuli[best_stimulus]
        
        # Decide whether to switch
        should_switch = force_reevaluate or self.should_switch_focus(
            best_stimulus,
            best_priority,
            current_time
        )
        
        if should_switch and best_stimulus != self.current_focus:
            self.set_focus(best_stimulus, current_time)
        
        return self.current_focus
    
    def get_debug_info(self, current_time: float) -> Dict[str, Any]:
        """
        Get debug information about current attention state.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            Dictionary with debug information
        """
        return {
            'current_focus': self.current_focus.value,
            'focus_duration': self.get_focus_duration(current_time),
            'is_committed': self.is_committed(current_time),
            'min_commitment_time': self.priorities[self.current_focus].min_commitment_time,
            'distraction_threshold': self.priorities[self.current_focus].distraction_threshold,
            'persistence_modifier': self.persistence_modifier,
            'distractibility_modifier': self.distractibility_modifier,
            'focus_context': self.focus_context
        }


def create_attention_manager_from_traits(traits: list) -> AttentionManager:
    """
    Create an attention manager configured based on creature traits.
    
    Args:
        traits: List of Trait objects
        
    Returns:
        Configured AttentionManager
    """
    trait_names = [t.name.lower() for t in traits]
    modifiers = {}
    
    # Persistence traits (increase commitment times)
    if 'persistent' in ' '.join(trait_names):
        modifiers['persistence'] = 1.5
    elif 'highly persistent' in ' '.join(trait_names):
        modifiers['persistence'] = 2.0
    elif 'tunnel vision' in ' '.join(trait_names):
        modifiers['persistence'] = 2.5  # Extreme persistence
    elif 'fickle' in ' '.join(trait_names):
        modifiers['persistence'] = 0.7
    
    # Distractibility traits (affect threshold for switching)
    if 'distractible' in ' '.join(trait_names):
        modifiers['distractibility'] = 1.5  # More easily distracted
    elif 'highly distractible' in ' '.join(trait_names):
        modifiers['distractibility'] = 2.0
    elif 'focused' in ' '.join(trait_names):
        modifiers['distractibility'] = 0.6  # Less distractible
    elif 'laser focused' in ' '.join(trait_names):
        modifiers['distractibility'] = 0.4
    
    # Opportunist trait (low commitment, high responsiveness)
    if 'opportunist' in ' '.join(trait_names):
        modifiers['persistence'] = 0.6
        modifiers['distractibility'] = 1.3
    
    # Building trait priority modifiers (additive to base 35.0)
    building_priority_bonus = 0.0
    
    # Positive building traits
    if 'architect' in ' '.join(trait_names):
        building_priority_bonus += 40.0  # 35 + 40 = 75 total
        modifiers['persistence'] = modifiers.get('persistence', 1.0) * 0.8  # Slightly less commitment time
    elif 'builder' in ' '.join(trait_names):
        building_priority_bonus += 25.0  # 35 + 25 = 60 total
        modifiers['persistence'] = modifiers.get('persistence', 1.0) * 0.9
    
    if 'material gatherer' in ' '.join(trait_names):
        building_priority_bonus += 15.0  # 35 + 15 = 50 total
    
    if 'cooperative builder' in ' '.join(trait_names):
        building_priority_bonus += 20.0  # 35 + 20 = 55 total
    
    if 'planner' in ' '.join(trait_names):
        building_priority_bonus += 10.0  # 35 + 10 = 45 total
        modifiers['persistence'] = modifiers.get('persistence', 1.0) * 1.5  # Longer commitment
    
    # Negative building traits (reduce priority)
    if 'lazy' in ' '.join(trait_names):
        building_priority_bonus -= 15.0  # 35 - 15 = 20 total
        modifiers['persistence'] = modifiers.get('persistence', 1.0) * 1.5  # Avoids switching to work
    
    if 'impatient' in ' '.join(trait_names):
        building_priority_bonus -= 10.0  # 35 - 10 = 25 total
        modifiers['persistence'] = modifiers.get('persistence', 1.0) * 0.5  # Won't stick with tasks
    
    if 'aggressive' in ' '.join(trait_names):
        building_priority_bonus -= 10.0  # 35 - 10 = 25 total (prefers combat)
    
    if 'wanderer' in ' '.join(trait_names):
        building_priority_bonus -= 12.0  # 35 - 12 = 23 total (too restless)
    
    # Note: Distractible already handled above, but also reduces building effectiveness
    # through reduced commitment time
    
    if building_priority_bonus != 0.0:
        modifiers['building_priority'] = building_priority_bonus
    
    return AttentionManager(trait_modifiers=modifiers)
