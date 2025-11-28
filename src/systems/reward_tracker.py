"""
Reward tracking system for reinforcement learning.

Tracks creature actions and applies rewards/penalties to their neural brains.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..systems.battle_spatial import BattleCreature


class RewardTracker:
    """Tracks events and applies rewards to creature brains."""
    
    # Reward values for different events
    REWARDS = {
        # Positive rewards
        'ate_food': 0.5,
        'avoided_damage': 0.3,
        'killed_enemy': 1.0,
        'found_mate': 0.7,
        'healed': 0.2,
        'escaped_danger': 0.4,
        
        # Negative penalties
        'took_damage': -0.5,
        'lost_food': -0.3,
        'hunger_increased': -0.1,
        'fled_unnecessarily': -0.2,
        'died': -2.0,
        'attacked_ally': -0.8,
    }
    
    def __init__(self):
        """Initialize reward tracker."""
        self.recent_successes = {}  # Track recent successful actions for observational learning
    
    def apply_reward(self, creature: 'BattleCreature', event: str):
        """
        Apply reward for an event.
        
        Args:
            creature: Creature to reward
            event: Event type (key in REWARDS dict)
        """
        if not hasattr(creature.creature, 'brain') or creature.creature.brain is None:
            return
        
        reward = self.REWARDS.get(event, 0.0)
        creature.creature.brain.apply_reward(reward)
        
        # Track successful actions for observational learning
        if reward > 0:
            self.recent_successes[creature.id] = True
        elif reward < -0.5:  # Significant failure
            self.recent_successes[creature.id] = False
    
    def was_recently_successful(self, creature: 'BattleCreature') -> bool:
        """Check if creature was recently successful."""
        return self.recent_successes.get(creature.id, False)
    
    def clear_success_flags(self):
        """Clear success tracking (call each frame)."""
        self.recent_successes.clear()
