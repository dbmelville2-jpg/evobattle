"""
Enhanced Combat Targeting System - Context-aware target selection.

Integrates personality, relationships, memory, and spatial context to
make intelligent targeting decisions.
"""

from typing import List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum
import random

if TYPE_CHECKING:
    from ..systems.battle_spatial import BattleCreature


class TargetingStrategy(Enum):
    """Targeting strategies based on personality and context."""
    NEAREST = "nearest"                    # Target closest enemy
    WEAKEST = "weakest"                    # Target lowest HP enemy
    STRONGEST = "strongest"                # Target highest attack enemy
    REVENGE = "revenge"                    # Target recent attackers
    PROTECT_ALLIES = "protect_allies"      # Target enemies attacking allies
    OPPORTUNISTIC = "opportunistic"        # Target best opportunity (injured + close)
    FAMILY_DEFENDER = "family_defender"    # Prioritize defending family
    STRAIN_LOYALIST = "strain_loyalist"    # Prioritize strain members


@dataclass
class CombatContext:
    """
    Context information for combat decisions.
    
    Attributes:
        nearby_allies: Number of allies within support range
        nearby_enemies: Number of enemies within threat range
        self_hp_percent: Our current HP percentage
        is_outnumbered: Whether we're outnumbered
        has_injured_allies: Whether any allies are injured
        has_family_nearby: Whether family members are nearby
    """
    nearby_allies: int = 0
    nearby_enemies: int = 0
    self_hp_percent: float = 1.0
    is_outnumbered: bool = False
    has_injured_allies: bool = False
    has_family_nearby: bool = False


@dataclass
class TargetScore:
    """
    Score for a potential target.
    
    Higher score = higher priority to target.
    """
    target_id: str
    total_score: float
    distance_score: float = 0.0
    threat_score: float = 0.0
    relationship_score: float = 0.0
    opportunity_score: float = 0.0
    personality_score: float = 0.0


class CombatTargetingSystem:
    """
    Enhanced targeting system that considers multiple factors.
    
    Integrates:
    - Spatial proximity (don't chase across map)
    - Combat memory (revenge, threat assessment)
    - Relationships (family, allies, rivals, revenge targets)
    - Personality (aggressive, cautious, loyal, vengeful)
    - Context (outnumbered, injured allies, etc.)
    """
    
    # Turn this to True to re-enable prints for debugging
    DEBUG: bool = False

    # Configuration parameters
    MAX_CHASE_DISTANCE = 30.0        # Don't chase enemies beyond this distance
    CLOSE_RANGE = 10.0               # Enemies within this are "close"
    SUPPORT_RANGE = 20.0             # Allies within this can be supported
    MIN_TARGET_SWITCH_TIME = 2.0     # Min seconds before switching targets
    
    # Scoring weights
    WEIGHT_DISTANCE = 0.3            # How much distance matters
    WEIGHT_THREAT = 0.25             # How much threat level matters
    WEIGHT_RELATIONSHIP = 0.25       # How much relationships matter
    WEIGHT_OPPORTUNITY = 0.2         # How much opportunity (injured, etc.) matters
    
    @staticmethod
    def select_target(
        attacker: 'BattleCreature',
        potential_targets: List['BattleCreature'],
        context: CombatContext
    ) -> Optional['BattleCreature']:
        """
        Select the best target based on all available information.

        Args:
            attacker: The creature selecting a target
            potential_targets: List of possible targets
            context: Current combat context

        Returns:
            Best target to attack, or None if no valid targets
        """
        # Defensive: empty input
        if not potential_targets:
            if CombatTargetingSystem.DEBUG:
                print(f"[Targeting DEBUG] attacker={attacker.creature.name}[id={id(attacker)}] incoming=[] -> no targets")
            return None

        # DEBUG: log incoming list
        try:
            incoming = ", ".join(f"{t.creature.name}[id={id(t)}]" for t in potential_targets)
        except Exception:
            incoming = str([id(t) for t in potential_targets])
        if CombatTargetingSystem.DEBUG:
            print(f"[Targeting DEBUG] attacker={attacker.creature.name}[id={id(attacker)}] incoming=[{incoming}]")

        # Safety check: Remove self from potential targets if somehow present
        before_count = len(potential_targets)
        potential_targets = [t for t in potential_targets if t != attacker]
        after_count = len(potential_targets)
        if before_count != after_count and CombatTargetingSystem.DEBUG:
            print(f"[Targeting DEBUG] attacker={attacker.creature.name}[id={id(attacker)}] removed_self_from_incoming (removed {before_count-after_count})")

        if not potential_targets:
            if CombatTargetingSystem.DEBUG:
                print(f"[Targeting DEBUG] attacker={attacker.creature.name}[id={id(attacker)}] -> no valid targets after self-filter")
            return None

        # Get current target (if any) for stickiness check
        current_target = getattr(attacker, "target", None)

        # Stickiness: prefer current target when combat memory requests it
        try:
            if current_target and current_target in potential_targets:
                cm = getattr(attacker.creature, "combat_memory", None)
                should_stick = False
                if cm and hasattr(cm, "should_stick_with_target"):
                    try:
                        should_stick = cm.should_stick_with_target(
                            current_target.creature.creature_id,
                            getattr(CombatTargetingSystem, "MIN_TARGET_SWITCH_TIME", 1.0)
                        )
                    except Exception:
                        should_stick = False
                if should_stick:
                    if CombatTargetingSystem.DEBUG:
                        print(f"[Targeting DEBUG] attacker={attacker.creature.name}[id={id(attacker)}] sticking with current target {current_target.creature.name}[id={id(current_target)}]")
                    return current_target
        except Exception:
            # Be conservative: continue to scoring if any error
            pass

        # Score all potential targets
        scores: List[TargetScore] = []

        for target in potential_targets:
            score = CombatTargetingSystem._score_target(attacker, target, context)
            if score.total_score > 0:  # Only consider valid targets
                scores.append(score)

        if not scores:
            if CombatTargetingSystem.DEBUG:
                print(f"[Targeting DEBUG] attacker={attacker.creature.name}[id={id(attacker)}] -> no targets after scoring")
            return None

        # Select highest scoring target
        best_score = max(scores, key=lambda s: s.total_score)

        # Find the corresponding target
        best = None
        for target in potential_targets:
            try:
                if target.creature.creature_id == best_score.target_id:
                    best = target
                    break
            except Exception:
                continue

        # DEBUG: log result
        if best:
            try:
                if CombatTargetingSystem.DEBUG:
                    print(f"[Targeting DEBUG] attacker={attacker.creature.name}[id={id(attacker)}] selected={best.creature.name}[id={id(best)}] score={best_score.total_score:.2f}")
            except Exception:
                if CombatTargetingSystem.DEBUG:
                    print(f"[Targeting DEBUG] attacker selected id={id(best)} score={best_score.total_score:.2f}")
        else:
            if CombatTargetingSystem.DEBUG:
                print(f"[Targeting DEBUG] attacker={attacker.creature.name}[id={id(attacker)}] selected=None (no matching id)")

        return best
    
    @staticmethod
    def _score_target(
        attacker: 'BattleCreature',
        target: 'BattleCreature',
        context: CombatContext
    ) -> TargetScore:
        """
        Calculate comprehensive score for a potential target.
        
        Args:
            attacker: The creature evaluating the target
            target: The potential target
            context: Combat context
            
        Returns:
            TargetScore with breakdown of scoring factors
        """
        target_id = target.creature.creature_id
        score = TargetScore(target_id=target_id, total_score=0.0)
        
        # Safety check: Never score self as a valid target
        if attacker == target:
            return score  # Return 0 score
        
        # Distance score (closer = better, beyond max = 0)
        distance = attacker.spatial.distance_to(target.spatial)
        if distance > CombatTargetingSystem.MAX_CHASE_DISTANCE:
            return score  # Too far, don't chase
        
        # Normalize distance (0 = far, 1 = close)
        distance_normalized = 1.0 - (distance / CombatTargetingSystem.MAX_CHASE_DISTANCE)
        score.distance_score = distance_normalized
        
        # Threat score (from combat memory)
        if hasattr(attacker.creature, 'combat_memory'):
            threat = attacker.creature.combat_memory.get_threat_level(target_id)
            score.threat_score = threat
            
            # Bonus for revenge targets
            if attacker.creature.combat_memory.should_prioritize_revenge(target_id):
                score.threat_score += 0.5  # Significant boost
        
        # Relationship score
        score.relationship_score = CombatTargetingSystem._calculate_relationship_score(
            attacker, target
        )
        
        # Opportunity score (injured, isolated, etc.)
        score.opportunity_score = CombatTargetingSystem._calculate_opportunity_score(
            attacker, target, context
        )
        
        # Personality modifiers
        score.personality_score = CombatTargetingSystem._calculate_personality_score(
            attacker, target, context
        )
        
        # Calculate total weighted score
        score.total_score = (
            score.distance_score * CombatTargetingSystem.WEIGHT_DISTANCE +
            score.threat_score * CombatTargetingSystem.WEIGHT_THREAT +
            score.relationship_score * CombatTargetingSystem.WEIGHT_RELATIONSHIP +
            score.opportunity_score * CombatTargetingSystem.WEIGHT_OPPORTUNITY +
            score.personality_score * 0.1  # Personality is a modifier
        )
        
        return score
    
    @staticmethod
    def _calculate_relationship_score(
        attacker: 'BattleCreature',
        target: 'BattleCreature'
    ) -> float:
        """
        Calculate score based on relationships.
        
        Args:
            attacker: The attacking creature
            target: The potential target
            
        Returns:
            Relationship score (higher = higher priority)
        """
        score = 0.0
        
        if not hasattr(attacker.creature, 'relationships'):
            return score
        
        target_id = target.creature.creature_id
        relationship = attacker.creature.relationships.get_relationship(target_id)
        
        if relationship:
            from ..models.relationships import RelationshipType
            
            # Revenge targets are highest priority
            if relationship.relationship_type == RelationshipType.REVENGE_TARGET:
                score += 1.0 * relationship.strength
            
            # Rivals are high priority
            elif relationship.relationship_type == RelationshipType.RIVAL:
                score += 0.7 * relationship.strength
            
            # Fear makes us avoid them
            elif relationship.relationship_type == RelationshipType.FEAR:
                score -= 0.5 * relationship.strength
            
            # Don't target allies or family (negative score)
            elif relationship.relationship_type in [
                RelationshipType.ALLY,
                RelationshipType.FRIEND,
                RelationshipType.PARENT,
                RelationshipType.CHILD,
                RelationshipType.SIBLING
            ]:
                score -= 2.0  # Strong penalty for friendly fire
        
        # Bonus for same strain rivals (genetic competition)
        if attacker.creature.strain_id == target.creature.strain_id:
            # Slight bonus for intra-strain competition (unless family or friends)
            if not relationship or relationship.relationship_type not in [
                RelationshipType.PARENT,
                RelationshipType.CHILD,
                RelationshipType.SIBLING,
                RelationshipType.FRIEND
            ]:
                score += 0.1
        
        return score
    
    @staticmethod
    def _calculate_opportunity_score(
        attacker: 'BattleCreature',
        target: 'BattleCreature',
        context: CombatContext
    ) -> float:
        """
        Calculate score based on opportunity (injured, isolated, etc.).
        
        Args:
            attacker: The attacking creature
            target: The potential target
            context: Combat context
            
        Returns:
            Opportunity score (higher = better opportunity)
        """
        score = 0.0
        
        # Injured targets are easier prey
        target_hp_percent = target.creature.stats.hp / max(1, target.creature.stats.max_hp)
        injury_bonus = 1.0 - target_hp_percent  # More injured = higher score
        score += injury_bonus * 0.5
        
        # Weak creatures are opportune targets
        if attacker.creature.stats.attack > target.creature.stats.defense * 1.5:
            score += 0.3  # We're much stronger
        
        # Carnivore bonus for herbivore targets
        if attacker.creature.has_trait("Carnivore") and target.creature.has_trait("Herbivore"):
            score += 0.4  # Prey preference
        
        return min(1.0, score)
    
    @staticmethod
    def _calculate_personality_score(
        attacker: 'BattleCreature',
        target: 'BattleCreature',
        context: CombatContext
    ) -> float:
        """
        Calculate personality-based targeting modifier.
        
        Args:
            attacker: The attacking creature
            target: The potential target
            context: Combat context
            
        Returns:
            Personality modifier (-1 to +1)
        """
        if not hasattr(attacker.creature, 'personality'):
            return 0.0
        
        personality = attacker.creature.personality
        modifier = 0.0
        
        # Aggressive creatures prefer strong targets
        if personality.aggression > 0.7:
            target_strength = target.creature.stats.attack / max(1, attacker.creature.stats.attack)
            modifier += (target_strength - 0.5) * 0.3
        
        # Cautious creatures prefer weak targets
        if personality.caution > 0.7:
            target_hp_percent = target.creature.stats.hp / max(1, target.creature.stats.max_hp)
            modifier += (1.0 - target_hp_percent) * 0.3
        
        # Loyal creatures protect allies (negative score if allies are threatened)
        if personality.loyalty > 0.6 and context.has_injured_allies:
            # Prefer targets that are attacking our allies
            # This would require additional context we don't have here
            # For now, just general bonus when allies need help
            modifier += 0.2
        
        # Proud creatures don't back down from strong enemies
        if personality.pride > 0.7:
            target_strength = target.creature.stats.attack / max(1, attacker.creature.stats.attack)
            if target_strength > 1.2:  # Stronger enemy
                modifier += 0.3  # Take the challenge
        
        return modifier
    
    @staticmethod
    def should_flee(
        creature: 'BattleCreature',
        context: CombatContext
    ) -> bool:
        """
        Determine if creature should flee from combat.
        
        Args:
            creature: The creature considering fleeing
            context: Combat context
            
        Returns:
            True if should flee
        """
        # Check personality-based retreat
        if hasattr(creature.creature, 'personality'):
            if creature.creature.personality.should_retreat(
                context.self_hp_percent,
                context.nearby_enemies
            ):
                return True
        
        # Default retreat logic (very low HP or heavily outnumbered)
        if context.self_hp_percent < 0.15:  # Critical HP
            return True
        
        if context.is_outnumbered and context.nearby_enemies >= 3:
            # Heavily outnumbered
            if context.self_hp_percent < 0.5:
                return True
        
        return False
    
    @staticmethod
    def get_flee_direction(
        creature: 'BattleCreature',
        enemies: List['BattleCreature']
    ) -> Optional[Tuple[float, float]]:
        """
        Calculate direction to flee from enemies.
        
        Args:
            creature: The fleeing creature
            enemies: List of enemy creatures
            
        Returns:
            (x, y) direction vector to flee, or None if no enemies
        """
        if not enemies:
            return None
        
        # Calculate average enemy position
        avg_x = sum(e.spatial.position.x for e in enemies) / len(enemies)
        avg_y = sum(e.spatial.position.y for e in enemies) / len(enemies)
        
        # Flee in opposite direction
        flee_x = creature.spatial.position.x - avg_x
        flee_y = creature.spatial.position.y - avg_y
        
        # Normalize
        magnitude = (flee_x ** 2 + flee_y ** 2) ** 0.5
        if magnitude > 0:
            flee_x /= magnitude
            flee_y /= magnitude
        
        return (flee_x, flee_y)
