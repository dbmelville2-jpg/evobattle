"""
Learned Behavior Inheritance - Passing Knowledge Across Generations

This module implements the inheritance of learned behaviors from parents to
offspring. This is a key Black & White mechanic - creatures pass down their
knowledge as "instincts" to their children.

This creates behavioral evolution alongside genetic evolution, allowing
successful strategies to propagate through populations.
"""

import random
from typing import List, Optional

from src.models.creature_beliefs import CreatureBeliefSystem, CreatureBelief, BeliefType


class LearnedBehaviorInheritance:
    """
    Manages the transfer of learned beliefs from parents to offspring.
    
    When creatures breed, their strongest beliefs are passed to the child
    as "instincts" - beliefs with reduced confidence that represent innate
    knowledge rather than learned experience.
    """
    
    def __init__(self):
        """Initialize behavior inheritance system"""
        self.inheritance_strength = 0.6  # Inherited beliefs are 60% as strong
        self.mutation_chance = 0.15  # 15% chance for random instinct
        self.max_inherited_beliefs = 6  # Max beliefs to inherit (3 from each parent)
        
    def inherit_beliefs(self, parent1_beliefs: CreatureBeliefSystem,
                       parent2_beliefs: CreatureBeliefSystem,
                       child_beliefs: CreatureBeliefSystem,
                       child_traits: Optional[List] = None) -> int:
        """
        Transfer learned behaviors from parents to child.
        
        Args:
            parent1_beliefs: First parent's belief system
            parent2_beliefs: Second parent's belief system
            child_beliefs: Child's belief system (to populate)
            child_traits: Optional list of child's traits (affects inheritance)
            
        Returns:
            Number of beliefs inherited
        """
        inherited_count = 0
        
        # Get strongest beliefs from each parent
        parent1_top = self._get_top_beliefs(parent1_beliefs, count=3)
        parent2_top = self._get_top_beliefs(parent2_beliefs, count=3)
        
        # Apply trait modifiers
        inheritance_modifier = self._get_trait_modifier(child_traits)
        
        # Transfer beliefs from parent 1
        for belief in parent1_top:
            inherited_belief = self._create_inherited_belief(
                belief, 
                inheritance_modifier
            )
            if inherited_belief:
                child_beliefs.add_belief(inherited_belief)
                inherited_count += 1
                
        # Transfer beliefs from parent 2
        for belief in parent2_top:
            inherited_belief = self._create_inherited_belief(
                belief,
                inheritance_modifier
            )
            if inherited_belief:
                child_beliefs.add_belief(inherited_belief)
                inherited_count += 1
                
        # Chance for mutation - random instinct
        if random.random() < self.mutation_chance:
            random_belief = self._create_random_instinct()
            if random_belief:
                child_beliefs.add_belief(random_belief)
                inherited_count += 1
                
        return inherited_count
        
    def _get_top_beliefs(self, belief_system: CreatureBeliefSystem, 
                        count: int = 3) -> List[CreatureBelief]:
        """
        Get the strongest beliefs from a belief system.
        
        Args:
            belief_system: Belief system to query
            count: Number of beliefs to get
            
        Returns:
            List of strongest beliefs
        """
        all_beliefs = list(belief_system.beliefs.values())
        
        # Sort by confidence (highest first)
        all_beliefs.sort(key=lambda b: b.confidence, reverse=True)
        
        # Return top N
        return all_beliefs[:count]
        
    def _create_inherited_belief(self, parent_belief: CreatureBelief,
                                trait_modifier: float) -> Optional[CreatureBelief]:
        """
        Create an inherited belief from a parent's belief.
        
        Args:
            parent_belief: Parent's belief to inherit
            trait_modifier: Modifier from child's traits
            
        Returns:
            New belief for child, or None if inheritance fails
        """
        # Calculate inherited confidence
        inherited_confidence = parent_belief.confidence * self.inheritance_strength * trait_modifier
        
        # Only inherit if confidence is meaningful
        if inherited_confidence < 0.2:
            return None
            
        # Create new belief (copy of parent's)
        return CreatureBelief(
            belief_type=parent_belief.belief_type,
            target=parent_belief.target,
            confidence=min(1.0, inherited_confidence)
        )
        
    def _get_trait_modifier(self, traits: Optional[List]) -> float:
        """
        Get inheritance modifier based on child's traits.
        
        Args:
            traits: List of child's traits
            
        Returns:
            Modifier (typically 0.5 to 1.5)
        """
        if not traits:
            return 1.0
            
        modifier = 1.0
        
        for trait in traits:
            effects = getattr(trait, 'interaction_effects', {})
            
            # STUBBORN: Retains inherited beliefs better
            if 'memory_capacity_multiplier' in effects:
                if effects['memory_capacity_multiplier'] > 1.0:
                    modifier *= 1.2
                    
            # FORGETFUL: Loses some inherited beliefs
            if 'memory_capacity_multiplier' in effects:
                if effects['memory_capacity_multiplier'] < 1.0:
                    modifier *= 0.8
                    
            # INNOVATIVE: More likely to develop unique interpretations
            if 'unique_behavior_chance' in effects:
                modifier *= 0.9  # Slightly less reliant on parents
                
            # INSTINCTIVE: Strong innate behaviors
            if 'innate_behavior_strength' in effects:
                modifier *= 1.3
                
        return modifier
        
    def _create_random_instinct(self) -> Optional[CreatureBelief]:
        """
        Create a random instinct (mutation).
        
        Returns:
            Random belief, or None
        """
        # Random belief type
        belief_types = list(BeliefType)
        belief_type = random.choice(belief_types)
        
        # Random location (simplified - would use actual arena bounds in practice)
        x = random.randint(10, 90)
        y = random.randint(10, 90)
        target = f"area_{x}_{y}"
        
        # Moderate confidence for random instincts
        confidence = random.uniform(0.3, 0.6)
        
        return CreatureBelief(
            belief_type=belief_type,
            target=target,
            confidence=confidence
        )
        
    def get_inheritance_preview(self, parent1_beliefs: CreatureBeliefSystem,
                               parent2_beliefs: CreatureBeliefSystem,
                               child_traits: Optional[List] = None) -> dict:
        """
        Preview what beliefs a child would inherit.
        
        Useful for UI display or debugging.
        
        Args:
            parent1_beliefs: First parent's beliefs
            parent2_beliefs: Second parent's beliefs
            child_traits: Optional child traits
            
        Returns:
            Dictionary with preview information
        """
        parent1_top = self._get_top_beliefs(parent1_beliefs, count=3)
        parent2_top = self._get_top_beliefs(parent2_beliefs, count=3)
        trait_modifier = self._get_trait_modifier(child_traits)
        
        preview = {
            "from_parent1": [],
            "from_parent2": [],
            "trait_modifier": trait_modifier,
            "mutation_chance": self.mutation_chance
        }
        
        for belief in parent1_top:
            inherited_conf = belief.confidence * self.inheritance_strength * trait_modifier
            if inherited_conf >= 0.2:
                preview["from_parent1"].append({
                    "type": belief.belief_type.value,
                    "target": belief.target,
                    "original_confidence": belief.confidence,
                    "inherited_confidence": min(1.0, inherited_conf)
                })
                
        for belief in parent2_top:
            inherited_conf = belief.confidence * self.inheritance_strength * trait_modifier
            if inherited_conf >= 0.2:
                preview["from_parent2"].append({
                    "type": belief.belief_type.value,
                    "target": belief.target,
                    "original_confidence": belief.confidence,
                    "inherited_confidence": min(1.0, inherited_conf)
                })
                
        return preview
        
    def __repr__(self):
        return (f"LearnedBehaviorInheritance(strength={self.inheritance_strength:.2f}, "
                f"mutation={self.mutation_chance:.2f})")
