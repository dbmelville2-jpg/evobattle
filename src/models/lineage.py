"""
Lineage model for EvoBattle.

Tracks the ancestry and breeding history of fighters.
"""

from typing import List, Optional


class Lineage:
    """
    Represents the lineage/ancestry of a fighter.
    
    Tracks the family tree and inheritance of traits through generations.
    """
    
    def __init__(self, fighter_id: str):
        """
        Initialize a Lineage for a fighter.
        
        Args:
            fighter_id: The ID of the fighter this lineage belongs to
        """
        self.fighter_id = fighter_id
        self.ancestors: List[str] = []
        self.descendants: List[str] = []
        self.generation = 0
    
    def add_ancestor(self, ancestor_id: str) -> None:
        """
        Add an ancestor to the lineage.
        
        Args:
            ancestor_id: ID of the ancestor fighter
        """
        if ancestor_id not in self.ancestors:
            self.ancestors.append(ancestor_id)
    
    def add_descendant(self, descendant_id: str) -> None:
        """
        Add a descendant to the lineage.
        
        Args:
            descendant_id: ID of the descendant fighter
        """
        if descendant_id not in self.descendants:
            self.descendants.append(descendant_id)
    
    def get_depth(self) -> int:
        """
        Get the depth of the lineage tree.
        
        Returns:
            Number of generations in the lineage
        """
        return self.generation
    
    def __repr__(self) -> str:
        """String representation of the lineage."""
        return f"Lineage(fighter_id='{self.fighter_id}', generation={self.generation}, ancestors={len(self.ancestors)}, descendants={len(self.descendants)})"
