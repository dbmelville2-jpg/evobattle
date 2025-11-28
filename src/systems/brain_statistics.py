"""
Brain Statistics - Analyzes population neural network patterns.

Tracks what strategies are popular, how brains are evolving,
and what the collective population is learning.
"""

from typing import List, Dict, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from ..systems.battle_spatial import BattleCreature


class BrainStatistics:
    """
    Analyzes population brain patterns and learning trends.
    
    Provides insights into what strategies are popular, how behaviors
    are spreading, and how the collective intelligence is evolving.
    """
    
    def __init__(self):
        """Initialize brain statistics tracker."""
        self.last_analysis = None
        self.history = []  # For future trend tracking
        
    def analyze_population(self, creatures: List['BattleCreature']) -> Dict:
        """
        Analyze all creature brains and return statistics.
        
        Args:
            creatures: List of all creatures to analyze
            
        Returns:
            Dictionary with brain statistics
        """
        try:
            # Filter creatures with brains
            creatures_with_brains = [
                c for c in creatures 
                if c.is_alive() and hasattr(c.creature, 'brain') and c.creature.brain is not None
            ]
            
            if not creatures_with_brains:
                stats = self._empty_stats()
                self.last_analysis = stats  # IMPORTANT: Set even when empty!
                return stats
            
            # Collect brain data
            all_weights = []
            all_learning_rates = []
            action_preferences = {'EAT': 0, 'FLEE': 0, 'FIGHT': 0, 'EXPLORE': 0}
            intelligent_count = 0
            
            for creature in creatures_with_brains:
                brain = creature.creature.brain
                
                # Collect weights
                all_weights.append({
                    'hidden': brain.input_weights.copy(),
                    'output': brain.output_weights.copy()
                })
                
                # Collect learning rates
                all_learning_rates.append(brain.learning_rate)
                
                # Count intelligent creatures
                if creature.creature.has_trait("Intelligent"):
                    intelligent_count += 1
                
                # Analyze action preferences based on output weights
                # Higher weights = stronger preference for that action
                output_weights = brain.output_weights
                action_preferences['EAT'] += np.mean(output_weights[:, 0])
                action_preferences['FLEE'] += np.mean(output_weights[:, 1])
                action_preferences['FIGHT'] += np.mean(output_weights[:, 2])
                action_preferences['EXPLORE'] += np.mean(output_weights[:, 3])
            
            # Calculate statistics
            total_creatures = len(creatures_with_brains)
            
            # Normalize action preferences to percentages
            total_preference = sum(action_preferences.values())
            if total_preference > 0:
                for action in action_preferences:
                    action_preferences[action] = action_preferences[action] / total_preference
            
            # Calculate brain diversity (variance in weights)
            brain_diversity = self._calculate_diversity(all_weights)
            
            # Build statistics
            stats = {
                'total_brains': total_creatures,
                'intelligent_count': intelligent_count,
                'avg_learning_rate': np.mean(all_learning_rates) if all_learning_rates else 0.0,
                'brain_diversity': brain_diversity,
                'action_preferences': action_preferences,
                'popular_strategies': self._identify_strategies(action_preferences),
            }
            
            self.last_analysis = stats
            return stats
        except Exception as e:
            # If analysis fails, return empty stats but log the error
            print(f"Brain statistics analysis error: {e}")
            import traceback
            traceback.print_exc()
            stats = self._empty_stats()
            self.last_analysis = stats
            return stats
    
    def _calculate_diversity(self, all_weights: List[Dict]) -> float:
        """
        Calculate how diverse the brains are (0-1, higher = more diverse).
        
        Args:
            all_weights: List of weight dictionaries
            
        Returns:
            Diversity score (0-1)
        """
        if len(all_weights) < 2:
            return 0.0
        
        # Calculate variance in hidden layer weights
        hidden_weights = [w['hidden'].flatten() for w in all_weights]
        hidden_variance = np.var(hidden_weights)
        
        # Normalize to 0-1 range (typical variance is 0-0.5)
        diversity = min(hidden_variance * 2.0, 1.0)
        
        return diversity
    
    def _identify_strategies(self, action_preferences: Dict[str, float]) -> List[Dict]:
        """
        Identify popular strategies based on action preferences.
        
        Args:
            action_preferences: Dictionary of action preferences
            
        Returns:
            List of strategy dictionaries
        """
        strategies = []
        
        # Sort actions by preference
        sorted_actions = sorted(action_preferences.items(), key=lambda x: x[1], reverse=True)
        
        for action, preference in sorted_actions:
            # Create strategy description
            if action == 'EAT':
                description = "Seek food when hungry"
            elif action == 'FLEE':
                description = "Flee from threats"
            elif action == 'FIGHT':
                description = "Fight enemies"
            else:  # EXPLORE
                description = "Explore and wander"
            
            strategies.append({
                'action': action,
                'description': description,
                'percentage': preference,
                'trend': 'stable'  # TODO: Calculate from history
            })
        
        return strategies
    
    def _empty_stats(self) -> Dict:
        """Return empty statistics when no brains available."""
        return {
            'total_brains': 0,
            'intelligent_count': 0,
            'avg_learning_rate': 0.0,
            'brain_diversity': 0.0,
            'action_preferences': {'EAT': 0, 'FLEE': 0, 'FIGHT': 0, 'EXPLORE': 0},
            'popular_strategies': [],
        }
