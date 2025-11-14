"""
Betting system for EvoBattle.

Manages bets placed on fighters and payouts.
"""

from typing import Dict, Optional


class BettingSystem:
    """
    Manages betting on fighters in battles.
    
    Allows placing bets and calculating payouts based on battle outcomes.
    """
    
    def __init__(self):
        """Initialize the betting system."""
        self.bets: Dict[str, list] = {}  # Maps fighter_id to list of bets
        self.total_pot = 0.0
        self.betting_history = []
    
    def place_bet(self, fighter_id: str, bettor_name: str, amount: float) -> bool:
        """
        Place a bet on a fighter.
        
        Args:
            fighter_id: ID of the fighter to bet on
            bettor_name: Name of the person placing the bet
            amount: Amount to bet
            
        Returns:
            True if bet was placed successfully
        """
        if amount <= 0:
            return False
        
        if fighter_id not in self.bets:
            self.bets[fighter_id] = []
        
        bet = {
            'bettor': bettor_name,
            'amount': amount,
            'fighter_id': fighter_id
        }
        
        self.bets[fighter_id].append(bet)
        self.total_pot += amount
        
        return True
    
    def calculate_payout(self, winner_id: str) -> Dict[str, float]:
        """
        Calculate payouts for all bettors after a battle.
        
        Args:
            winner_id: ID of the winning fighter
            
        Returns:
            Dictionary mapping bettor names to their payout amounts
        """
        payouts = {}
        
        if winner_id not in self.bets or not self.bets[winner_id]:
            # No winners, house keeps the pot
            return payouts
        
        # Calculate total amount bet on winner
        winner_bets_total = sum(bet['amount'] for bet in self.bets[winner_id])
        
        # Calculate payout for each bettor on the winning fighter
        for bet in self.bets[winner_id]:
            bettor = bet['bettor']
            bet_amount = bet['amount']
            
            # Proportional share of the total pot
            payout = (bet_amount / winner_bets_total) * self.total_pot
            
            if bettor in payouts:
                payouts[bettor] += payout
            else:
                payouts[bettor] = payout
        
        # Record in history
        self.betting_history.append({
            'winner_id': winner_id,
            'total_pot': self.total_pot,
            'payouts': payouts.copy()
        })
        
        return payouts
    
    def clear_bets(self) -> None:
        """Clear all current bets (for next battle)."""
        self.bets = {}
        self.total_pot = 0.0
    
    def get_betting_history(self) -> list:
        """
        Get the history of all betting rounds.
        
        Returns:
            List of betting records
        """
        return self.betting_history
    
    def __repr__(self) -> str:
        """String representation of the betting system."""
        return f"BettingSystem(total_pot={self.total_pot:.2f}, active_bets={sum(len(bets) for bets in self.bets.values())})"
