"""
Battle system for EvoBattle.

Handles combat between fighters and determines winners.
"""

import random
from typing import Tuple, Optional


class BattleSystem:
    """
    Manages battles between fighters.
    
    Uses fighter traits and power to determine battle outcomes.
    """
    
    def __init__(self):
        """Initialize the battle system."""
        self.battle_history = []
    
    def simulate_battle(self, fighter1, fighter2) -> Tuple[Optional[object], Optional[object]]:
        """
        Simulate a battle between two fighters.
        
        Args:
            fighter1: First fighter
            fighter2: Second fighter
            
        Returns:
            Tuple of (winner, loser)
        """
        # Calculate powers
        power1 = fighter1.calculate_power()
        power2 = fighter2.calculate_power()
        
        # Add some randomness to make battles more interesting
        power1 *= random.uniform(0.8, 1.2)
        power2 *= random.uniform(0.8, 1.2)
        
        # Determine winner
        if power1 > power2:
            winner, loser = fighter1, fighter2
        elif power2 > power1:
            winner, loser = fighter2, fighter1
        else:
            # In case of tie, random winner
            if random.choice([True, False]):
                winner, loser = fighter1, fighter2
            else:
                winner, loser = fighter2, fighter1
        
        # Record results
        winner.record_win()
        loser.record_loss()
        
        # Save to history
        self.battle_history.append({
            'fighter1': fighter1.name,
            'fighter2': fighter2.name,
            'winner': winner.name,
            'power1': power1,
            'power2': power2
        })
        
        return winner, loser
    
    def get_battle_history(self) -> list:
        """
        Get the history of all battles.
        
        Returns:
            List of battle records
        """
        return self.battle_history
    
    def __repr__(self) -> str:
        """String representation of the battle system."""
        return f"BattleSystem(battles_fought={len(self.battle_history)})"
