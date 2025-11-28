"""
Research Ethics System - Track Player's Scientific Approach

This module implements an ethics tracking system that monitors how the player
interacts with creatures and the ecosystem. Inspired by Black & White's moral
alignment system, but themed around scientific research ethics.

The system tracks:
- Creature Welfare: How well creatures are treated
- Ecosystem Health: Environmental impact of interventions
- Research Integrity: Scientific honesty and methodology
- Intervention Level: How much the player interferes vs observes

Ethics scores affect simulation behavior, visual feedback, and unlock
different research capabilities.
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
import time


class EthicsMetric(Enum):
    """Categories of ethical measurement"""
    CREATURE_WELFARE = "welfare"
    ECOSYSTEM_HEALTH = "ecosystem"
    RESEARCH_INTEGRITY = "integrity"
    INTERVENTION_LEVEL = "intervention"


@dataclass
class EthicalEvent:
    """Record of an ethical decision"""
    action: str
    timestamp: float
    welfare_impact: float
    ecosystem_impact: float
    integrity_impact: float
    intervention_impact: float
    target_creature_id: Optional[str] = None
    notes: str = ""


class ResearchEthicsSystem:
    """
    Tracks and manages player's research ethics.
    
    Scores range from -100 to +100 for welfare, ecosystem, and integrity.
    Intervention ranges from 0 (hands-off) to 100 (heavy intervention).
    
    Ethics scores affect:
    - Creature behavior (stress, trust, learning)
    - Ecosystem dynamics (stability, diversity)
    - Visual feedback (lab environment, cursor appearance)
    - Available research tools and capabilities
    """
    
    def __init__(self):
        """Initialize ethics tracking system"""
        # Core ethics scores
        self.welfare_score = 0.0      # -100 to +100
        self.ecosystem_score = 0.0    # -100 to +100
        self.integrity_score = 0.0    # -100 to +100
        self.intervention_score = 0.0  # 0 to 100
        
        # Event history
        self.ethical_events: List[EthicalEvent] = []
        
        # Statistics
        self.total_interventions = 0
        self.positive_interventions = 0
        self.negative_interventions = 0
        self.creatures_helped = set()
        self.creatures_harmed = set()
        
    def record_action(self, action: str, welfare: float = 0.0, ecosystem: float = 0.0,
                     integrity: float = 0.0, intervention: float = 0.0,
                     target_creature_id: Optional[str] = None, notes: str = ""):
        """
        Record an ethical decision and update scores.
        
        Args:
            action: Name of action taken
            welfare: Impact on creature welfare (-100 to +100)
            ecosystem: Impact on ecosystem health (-100 to +100)
            integrity: Impact on research integrity (-100 to +100)
            intervention: Intervention level increase (0 to 100)
            target_creature_id: ID of affected creature (if any)
            notes: Additional context
        """
        # Update scores
        self.welfare_score += welfare
        self.ecosystem_score += ecosystem
        self.integrity_score += integrity
        self.intervention_score += intervention
        
        # Clamp scores to valid ranges
        self.welfare_score = max(-100, min(100, self.welfare_score))
        self.ecosystem_score = max(-100, min(100, self.ecosystem_score))
        self.integrity_score = max(-100, min(100, self.integrity_score))
        self.intervention_score = max(0, min(100, self.intervention_score))
        
        # Track statistics
        self.total_interventions += 1
        if welfare > 0 or ecosystem > 0:
            self.positive_interventions += 1
        elif welfare < 0 or ecosystem < 0:
            self.negative_interventions += 1
            
        if target_creature_id:
            if welfare > 0:
                self.creatures_helped.add(target_creature_id)
            elif welfare < 0:
                self.creatures_harmed.add(target_creature_id)
        
        # Record event
        event = EthicalEvent(
            action=action,
            timestamp=time.time(),
            welfare_impact=welfare,
            ecosystem_impact=ecosystem,
            integrity_impact=integrity,
            intervention_impact=intervention,
            target_creature_id=target_creature_id,
            notes=notes
        )
        self.ethical_events.append(event)
        
    def get_overall_ethics(self) -> float:
        """
        Get overall ethics score.
        
        Returns:
            Average of welfare, ecosystem, and integrity scores (-100 to +100)
        """
        return (self.welfare_score + self.ecosystem_score + self.integrity_score) / 3.0
        
    def get_research_approach(self) -> str:
        """
        Get description of research approach based on scores.
        
        Returns:
            String describing research philosophy
        """
        overall = self.get_overall_ethics()
        intervention = self.intervention_score
        
        if overall > 50 and intervention < 30:
            return "Ethical Observer"
        elif overall > 50 and intervention > 70:
            return "Benevolent Interventionist"
        elif overall > 20 and intervention < 50:
            return "Balanced Researcher"
        elif overall < -50 and intervention > 70:
            return "Aggressive Experimenter"
        elif overall < -50:
            return "Detached Observer"
        elif intervention > 80:
            return "Micromanager"
        elif intervention < 20:
            return "Hands-Off Naturalist"
        else:
            return "Pragmatic Scientist"
            
    def get_creature_trust_modifier(self) -> float:
        """
        Get modifier for creature trust/stress based on welfare score.
        
        Returns:
            Multiplier for creature stress/trust (0.5 to 1.5)
        """
        # High welfare = low stress, low welfare = high stress
        return 1.0 - (self.welfare_score / 200.0)
        
    def get_ecosystem_stability_modifier(self) -> float:
        """
        Get modifier for ecosystem stability based on ecosystem score.
        
        Returns:
            Multiplier for ecosystem stability (0.6 to 1.4)
        """
        return 1.0 + (self.ecosystem_score / 250.0)
        
    def get_learning_rate_modifier(self) -> float:
        """
        Get modifier for creature learning based on intervention level.
        
        High intervention = creatures become dependent, learn less
        Low intervention = creatures are self-sufficient, learn more
        
        Returns:
            Multiplier for learning rate (0.7 to 1.3)
        """
        return 1.3 - (self.intervention_score / 200.0)
        
    def get_simulation_modifiers(self) -> Dict[str, float]:
        """
        Get all simulation modifiers in one call.
        
        Returns:
            Dictionary with all active modifiers
        """
        return {
            "creature_trust": self.get_creature_trust_modifier(),
            "ecosystem_stability": self.get_ecosystem_stability_modifier(),
            "learning_rate": self.get_learning_rate_modifier(),
            "welfare_score": self.welfare_score,
            "ecosystem_score": self.ecosystem_score,
            "integrity_score": self.integrity_score,
            "intervention_score": self.intervention_score
        }
        
    def get_summary(self) -> Dict:
        """
        Get summary of ethics system state.
        
        Returns:
            Dictionary with all ethics metrics and statistics
        """
        return {
            "welfare_score": self.welfare_score,
            "ecosystem_score": self.ecosystem_score,
            "integrity_score": self.integrity_score,
            "intervention_score": self.intervention_score,
            "overall_ethics": self.get_overall_ethics(),
            "research_approach": self.get_research_approach(),
            "total_interventions": self.total_interventions,
            "positive_interventions": self.positive_interventions,
            "negative_interventions": self.negative_interventions,
            "creatures_helped": len(self.creatures_helped),
            "creatures_harmed": len(self.creatures_harmed),
            "modifiers": {
                "creature_trust": self.get_creature_trust_modifier(),
                "ecosystem_stability": self.get_ecosystem_stability_modifier(),
                "learning_rate": self.get_learning_rate_modifier()
            }
        }
        
    def __repr__(self):
        return (f"Ethics(welfare={self.welfare_score:.1f}, "
                f"ecosystem={self.ecosystem_score:.1f}, "
                f"intervention={self.intervention_score:.1f}, "
                f"approach={self.get_research_approach()})")


# Predefined ethical actions with their impacts
ETHICAL_ACTIONS = {
    "reward_food": {
        "welfare": 2,
        "ecosystem": 0,
        "integrity": 0,
        "intervention": 1
    },
    "apply_stimulus": {
        "welfare": -5,
        "ecosystem": 0,
        "integrity": 0,
        "intervention": 2
    },
    "relocate_creature": {
        "welfare": -2,
        "ecosystem": -1,
        "integrity": -1,
        "intervention": 3
    },
    "let_creature_starve": {
        "welfare": -10,
        "ecosystem": 0,
        "integrity": 2,  # Observing natural selection
        "intervention": -2
    },
    "introduce_predator": {
        "welfare": -5,
        "ecosystem": -5,
        "integrity": 0,
        "intervention": 10
    },
    "remove_hazard": {
        "welfare": 5,
        "ecosystem": 3,
        "integrity": -2,  # Interfering with natural environment
        "intervention": 5
    },
    "provide_shelter": {
        "welfare": 8,
        "ecosystem": 2,
        "integrity": -3,
        "intervention": 7
    },
    "observe_only": {
        "welfare": 0,
        "ecosystem": 0,
        "integrity": 5,
        "intervention": -1
    },
    "genetic_modification": {
        "welfare": -3,
        "ecosystem": -8,
        "integrity": -10,
        "intervention": 15
    },
    "natural_breeding": {
        "welfare": 3,
        "ecosystem": 5,
        "integrity": 8,
        "intervention": -2
    },
    "force_breeding": {
        "welfare": -8,
        "ecosystem": -3,
        "integrity": -5,
        "intervention": 12
    },
    "heal_creature": {
        "welfare": 6,
        "ecosystem": 0,
        "integrity": -1,
        "intervention": 4
    },
    "euthanize_suffering": {
        "welfare": 3,  # Ending suffering
        "ecosystem": 0,
        "integrity": 2,
        "intervention": 8
    },
    "expand_habitat": {
        "welfare": 10,
        "ecosystem": 5,
        "integrity": -5,
        "intervention": 15
    },
    "reduce_resources": {
        "welfare": -8,
        "ecosystem": -3,
        "integrity": 3,
        "intervention": 8
    },
    "mark_safe_area": {
        "welfare": 4,
        "ecosystem": 1,
        "integrity": -1,
        "intervention": 3
    },
    "mark_danger_area": {
        "welfare": 5,
        "ecosystem": 2,
        "integrity": 0,
        "intervention": 2
    }
}
