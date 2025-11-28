"""
Research Assistants System - AI Advisors

This module implements AI research assistants that provide guidance to the
player based on different research philosophies. Each assistant has a unique
personality and approach to ethics.

Inspired by Black & White's conscience system, but with scientific advisors
instead of good/evil angels.
"""

from typing import Optional, List
from enum import Enum

from src.systems.ethical_dilemmas import EthicalDilemma, DilemmaChoice
from src.systems.research_ethics import ResearchEthicsSystem


class AssistantPhilosophy(Enum):
    """Research philosophies of assistants"""
    HUMANE = "humane"          # Prioritize creature welfare
    PRAGMATIC = "pragmatic"    # Balance ethics with progress
    NATURALIST = "naturalist"  # Minimal intervention


class ResearchAssistant:
    """
    An AI advisor that provides guidance based on a research philosophy.
    
    Each assistant has a unique personality and will recommend different
    choices based on their values.
    """
    
    def __init__(self, name: str, title: str, philosophy: AssistantPhilosophy,
                 personality_traits: List[str]):
        """
        Initialize a research assistant.
        
        Args:
            name: Assistant's name
            title: Professional title
            philosophy: Research philosophy
            personality_traits: List of personality descriptors
        """
        self.name = name
        self.title = title
        self.philosophy = philosophy
        self.personality_traits = personality_traits
        self.advice_history: List[str] = []
        
    def get_advice(self, dilemma: EthicalDilemma,
                   ethics_system: Optional[ResearchEthicsSystem] = None) -> str:
        """
        Provide advice for a dilemma based on philosophy.
        
        Args:
            dilemma: The ethical dilemma
            ethics_system: Optional current ethics state
            
        Returns:
            Advice string
        """
        # Get recommended choice based on philosophy
        recommended_index = self._get_recommended_choice(dilemma)
        
        # Generate contextual advice
        advice = self._generate_advice(dilemma, recommended_index, ethics_system)
        
        self.advice_history.append(advice)
        if len(self.advice_history) > 20:
            self.advice_history.pop(0)
            
        return advice
        
    def _get_recommended_choice(self, dilemma: EthicalDilemma) -> int:
        """
        Determine which choice to recommend based on philosophy.
        
        Args:
            dilemma: The dilemma
            
        Returns:
            Index of recommended choice
        """
        if self.philosophy == AssistantPhilosophy.HUMANE:
            # Choose option with highest welfare impact
            return max(range(len(dilemma.choices)),
                      key=lambda i: dilemma.choices[i].welfare_impact)
                      
        elif self.philosophy == AssistantPhilosophy.NATURALIST:
            # Choose option with lowest intervention
            return min(range(len(dilemma.choices)),
                      key=lambda i: dilemma.choices[i].intervention_impact)
                      
        else:  # PRAGMATIC
            # Choose balanced option (highest integrity, moderate intervention)
            return max(range(len(dilemma.choices)),
                      key=lambda i: dilemma.choices[i].integrity_impact)
                      
    def _generate_advice(self, dilemma: EthicalDilemma, 
                        recommended_index: int,
                        ethics_system: Optional[ResearchEthicsSystem]) -> str:
        """
        Generate contextual advice string.
        
        Args:
            dilemma: The dilemma
            recommended_index: Index of recommended choice
            ethics_system: Optional ethics state
            
        Returns:
            Advice string
        """
        choice = dilemma.choices[recommended_index]
        
        if self.philosophy == AssistantPhilosophy.HUMANE:
            return self._generate_humane_advice(dilemma, choice, ethics_system)
        elif self.philosophy == AssistantPhilosophy.NATURALIST:
            return self._generate_naturalist_advice(dilemma, choice, ethics_system)
        else:
            return self._generate_pragmatic_advice(dilemma, choice, ethics_system)
            
    def _generate_humane_advice(self, dilemma: EthicalDilemma,
                               choice: DilemmaChoice,
                               ethics_system: Optional[ResearchEthicsSystem]) -> str:
        """Generate advice from humane perspective"""
        templates = [
            f"Consider the creatures' wellbeing first. I recommend: '{choice.text}'",
            f"These creatures depend on us. We should: '{choice.text}'",
            f"Compassion is key to good research. Try: '{choice.text}'",
            f"Let's minimize suffering here: '{choice.text}'"
        ]
        
        # Add context based on current ethics
        if ethics_system and ethics_system.welfare_score < 30:
            return f"Your welfare score is concerning. Please consider: '{choice.text}'"
        
        import random
        return random.choice(templates)
        
    def _generate_naturalist_advice(self, dilemma: EthicalDilemma,
                                   choice: DilemmaChoice,
                                   ethics_system: Optional[ResearchEthicsSystem]) -> str:
        """Generate advice from naturalist perspective"""
        templates = [
            f"Let nature take its course: '{choice.text}'",
            f"Minimal intervention yields the best data: '{choice.text}'",
            f"We're observers, not gods: '{choice.text}'",
            f"Natural processes should guide us: '{choice.text}'"
        ]
        
        # Add context based on intervention level
        if ethics_system and ethics_system.intervention_score > 70:
            return f"You're intervening too much. Step back: '{choice.text}'"
            
        import random
        return random.choice(templates)
        
    def _generate_pragmatic_advice(self, dilemma: EthicalDilemma,
                                  choice: DilemmaChoice,
                                  ethics_system: Optional[ResearchEthicsSystem]) -> str:
        """Generate advice from pragmatic perspective"""
        templates = [
            f"This is an opportunity to learn: '{choice.text}'",
            f"Balance ethics with scientific progress: '{choice.text}'",
            f"The practical choice here is: '{choice.text}'",
            f"Consider both outcomes and ethics: '{choice.text}'"
        ]
        
        import random
        return random.choice(templates)
        
    def get_general_comment(self, ethics_system: ResearchEthicsSystem) -> str:
        """
        Get a general comment about the player's research approach.
        
        Args:
            ethics_system: Current ethics state
            
        Returns:
            Comment string
        """
        approach = ethics_system.get_research_approach()
        
        if self.philosophy == AssistantPhilosophy.HUMANE:
            if ethics_system.welfare_score > 60:
                return "Your compassionate approach is admirable."
            elif ethics_system.welfare_score < 30:
                return "I'm concerned about creature welfare in your study."
            else:
                return "Try to prioritize the creatures' wellbeing more."
                
        elif self.philosophy == AssistantPhilosophy.NATURALIST:
            if ethics_system.intervention_score < 30:
                return "Excellent restraint. Let nature guide the research."
            elif ethics_system.intervention_score > 70:
                return "You're interfering too much with natural processes."
            else:
                return "Consider stepping back and observing more."
                
        else:  # PRAGMATIC
            if ethics_system.integrity_score > 60:
                return "Your research maintains good scientific standards."
            else:
                return "Focus on maintaining research integrity."
                
    def __repr__(self):
        return f"ResearchAssistant(name='{self.name}', philosophy={self.philosophy.value})"


# ============================================================================
# PREDEFINED ASSISTANTS
# ============================================================================

DR_EMMA_CHEN = ResearchAssistant(
    name="Dr. Emma Chen",
    title="Animal Welfare Specialist",
    philosophy=AssistantPhilosophy.HUMANE,
    personality_traits=["compassionate", "empathetic", "protective"]
)

DR_MARCUS_REID = ResearchAssistant(
    name="Dr. Marcus Reid",
    title="Senior Research Scientist",
    philosophy=AssistantPhilosophy.PRAGMATIC,
    personality_traits=["analytical", "balanced", "methodical"]
)

DR_SARAH_KIM = ResearchAssistant(
    name="Dr. Sarah Kim",
    title="Evolutionary Biologist",
    philosophy=AssistantPhilosophy.NATURALIST,
    personality_traits=["observant", "patient", "non-interventionist"]
)


class AssistantManager:
    """
    Manages all research assistants and determines which one speaks.
    
    Different assistants appear based on context and player's ethics.
    """
    
    def __init__(self):
        """Initialize assistant manager"""
        self.assistants = [DR_EMMA_CHEN, DR_MARCUS_REID, DR_SARAH_KIM]
        self.active_assistant: Optional[ResearchAssistant] = DR_MARCUS_REID  # Default
        
    def get_assistant_for_dilemma(self, dilemma: EthicalDilemma,
                                   ethics_system: ResearchEthicsSystem) -> ResearchAssistant:
        """
        Determine which assistant should speak for this dilemma.
        
        Args:
            dilemma: The dilemma
            ethics_system: Current ethics state
            
        Returns:
            Appropriate assistant
        """
        # Welfare-focused dilemmas -> Dr. Chen
        if "welfare" in dilemma.category.value or "creature" in dilemma.title.lower():
            if ethics_system.welfare_score < 40:
                return DR_EMMA_CHEN  # She appears when welfare is low
                
        # High intervention -> Dr. Kim warns
        if ethics_system.intervention_score > 70:
            return DR_SARAH_KIM
            
        # Default to pragmatic advisor
        return DR_MARCUS_REID
        
    def get_all_advice(self, dilemma: EthicalDilemma,
                      ethics_system: ResearchEthicsSystem) -> List[tuple]:
        """
        Get advice from all assistants.
        
        Args:
            dilemma: The dilemma
            ethics_system: Current ethics state
            
        Returns:
            List of (assistant, advice) tuples
        """
        return [
            (assistant, assistant.get_advice(dilemma, ethics_system))
            for assistant in self.assistants
        ]
        
    def get_primary_advisor(self, ethics_system: ResearchEthicsSystem) -> ResearchAssistant:
        """
        Get the primary advisor based on player's approach.
        
        Args:
            ethics_system: Current ethics state
            
        Returns:
            Primary assistant
        """
        approach = ethics_system.get_research_approach()
        
        if "Humane" in approach or "Compassionate" in approach:
            return DR_EMMA_CHEN
        elif "Naturalist" in approach or "Hands-Off" in approach:
            return DR_SARAH_KIM
        else:
            return DR_MARCUS_REID
            
    def __repr__(self):
        return f"AssistantManager(assistants={len(self.assistants)}, active={self.active_assistant.name if self.active_assistant else 'None'})"
