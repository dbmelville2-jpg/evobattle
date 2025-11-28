"""
Neural Observational Learning - Smart creatures copy successful brain weights.

This is a simplified observational learning system specifically for the neural
network brain system. Intelligent creatures watch nearby successful creatures
and copy their brain weights.
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..systems.battle_spatial import BattleCreature
    from .reward_tracker import RewardTracker


class NeuralObservationalLearning:
    """
    Manages neural brain copying for Intelligent creatures.
    
    Intelligent creatures watch nearby creatures and copy brain weights
    from those who are successful (recently ate, killed, etc.).
    """
    
    def __init__(self):
        """Initialize neural observational learning system."""
        self.observation_range = 30.0  # Distance creatures can observe from
        self.learning_blend_factor = 0.05  # How much to copy (5%)
        
    def update(self, creatures: List['BattleCreature'], reward_tracker: 'RewardTracker'):
        """
        Update observational learning for all creatures.
        
        Args:
            creatures: All creatures in the battle
            reward_tracker: Reward tracker to check for successful creatures
        """
        # Only process creatures with Intelligent trait
        intelligent_creatures = [
            c for c in creatures 
            if c.is_alive() and c.creature.has_trait("Intelligent")
        ]
        
        if not intelligent_creatures:
            return
        
        # Find successful creatures (those who recently got rewards)
        successful_creatures = [
            c for c in creatures
            if c.is_alive() and reward_tracker.was_recently_successful(c)
        ]
        
        if not successful_creatures:
            return
        
        # Each intelligent creature observes nearby successful creatures
        for observer in intelligent_creatures:
            if not hasattr(observer.creature, 'brain') or observer.creature.brain is None:
                continue
            
            # Find nearby successful creatures
            nearby_successful = []
            for other in successful_creatures:
                if other == observer:
                    continue
                
                if not hasattr(other.creature, 'brain') or other.creature.brain is None:
                    continue
                
                # Check distance
                distance = observer.spatial.distance_to(other.spatial)
                if distance <= self.observation_range:
                    nearby_successful.append(other)
            
            # Learn from the nearest successful creature
            if nearby_successful:
                # Choose the closest one
                nearest = min(nearby_successful, 
                            key=lambda c: observer.spatial.distance_to(c.spatial))
                
                # Copy their brain weights
                observer.creature.brain.copy_from(
                    nearest.creature.brain,
                    blend_factor=self.learning_blend_factor
                )
                
                # Optional: Track that learning occurred (for debugging/stats)
                if not hasattr(observer, 'learning_events'):
                    observer.learning_events = 0
                observer.learning_events += 1
