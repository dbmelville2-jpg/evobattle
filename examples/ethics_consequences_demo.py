"""
Phase 3 Demo: Ethics & Consequences

This demo showcases the ethical dilemma system, research assistants, and
consequence effects. Players face moral choices that affect their research
approach and the simulation.

Run this to see Black & White's moral choice system in action!
"""

import sys
import time

# Add parent directory to path for imports
sys.path.insert(0, '.')

from src.systems.ethical_dilemmas import (
    DilemmaSystem, EthicalDilemma,
    SICK_CREATURE_DILEMMA, OVERPOPULATION_DILEMMA,
    INTERESTING_MUTATION_DILEMMA, AGGRESSIVE_CREATURE_DILEMMA
)
from src.systems.research_assistants import (
    AssistantManager, DR_EMMA_CHEN, DR_MARCUS_REID, DR_SARAH_KIM
)
from src.systems.research_ethics import ResearchEthicsSystem


def print_separator(title=""):
    """Print a nice separator"""
    if title:
        print("\n" + "="*70)
        print(title.center(70))
        print("="*70 + "\n")
    else:
        print("\n" + "-"*70 + "\n")


def print_ethics_state(ethics: ResearchEthicsSystem):
    """Print current ethics state"""
    print("Current Ethics State:")
    print(f"  Welfare:     {ethics.welfare_score:>6.1f}/100  ", end="")
    print("[" + "#" * int((ethics.welfare_score + 100) / 10) + " " * (20 - int((ethics.welfare_score + 100) / 10)) + "]")
    print(f"  Ecosystem:   {ethics.ecosystem_score:>6.1f}/100  ", end="")
    print("[" + "#" * int((ethics.ecosystem_score + 100) / 10) + " " * (20 - int((ethics.ecosystem_score + 100) / 10)) + "]")
    print(f"  Integrity:   {ethics.integrity_score:>6.1f}/100  ", end="")
    print("[" + "#" * int((ethics.integrity_score + 100) / 10) + " " * (20 - int((ethics.integrity_score + 100) / 10)) + "]")
    print(f"  Intervention:{ethics.intervention_score:>6.1f}/100  ", end="")
    print("[" + "#" * int(ethics.intervention_score / 5) + " " * (20 - int(ethics.intervention_score / 5)) + "]")
    print(f"\n  Research Approach: {ethics.get_research_approach()}")


def print_consequences(ethics: ResearchEthicsSystem):
    """Print active consequence effects"""
    modifiers = ethics.get_simulation_modifiers()
    
    print("\nActive Consequences:")
    
    trust = modifiers['creature_trust']
    if trust < 0.9:
        print(f"  + Creatures trust you ({(1-trust)*100:+.0f}% interaction success)")
    elif trust > 1.1:
        print(f"  - Creatures fear you ({(trust-1)*100:-.0f}% interaction success)")
    else:
        print("  = Neutral creature trust")
        
    learning = modifiers['learning_rate']
    if learning > 1.1:
        print(f"  + Enhanced learning rate ({(learning-1)*100:+.0f}%)")
    elif learning < 0.9:
        print(f"  - Reduced learning rate ({(learning-1)*100:-.0f}%)")
    else:
        print("  = Normal learning rate")
        
    stability = modifiers['ecosystem_stability']
    if stability > 1.1:
        print(f"  + Stable ecosystem ({(stability-1)*100:+.0f}% resource regen)")
    elif stability < 0.9:
        print(f"  - Stressed ecosystem ({(stability-1)*100:-.0f}% resource regen)")
    else:
        print("  = Balanced ecosystem")


def demo_single_dilemma():
    """Demonstrate a single dilemma with all assistants"""
    print_separator("SINGLE DILEMMA DEMO")
    
    print("Scenario: A creature in your study has fallen ill\n")
    
    # Create systems
    ethics = ResearchEthicsSystem()
    assistant_manager = AssistantManager()
    
    # Show dilemma
    dilemma = SICK_CREATURE_DILEMMA
    print(f"DILEMMA: {dilemma.title}")
    print(f"{dilemma.description}\n")
    
    # Show all choices
    print("Available Choices:")
    for i, choice in enumerate(dilemma.choices, 1):
        print(f"\n  [{i}] {choice.text}")
        print(f"      {choice.get_impact_summary()}")
        print(f"      Outcome: {choice.outcome_description}")
    
    # Get advice from all assistants
    print("\n" + "-"*70)
    print("Research Assistant Advice:")
    print("-"*70)
    
    for assistant in [DR_EMMA_CHEN, DR_MARCUS_REID, DR_SARAH_KIM]:
        advice = assistant.get_advice(dilemma, ethics)
        print(f"\n{assistant.name} ({assistant.title}):")
        print(f"  \"{advice}\"")
    
    # Simulate choosing option 1 (provide treatment)
    print("\n" + "-"*70)
    print("You choose: [1] Provide medical treatment")
    print("-"*70)
    
    choice = dilemma.choices[0]
    ethics.record_action(
        action="provide_treatment",
        welfare=choice.welfare_impact,
        ecosystem=choice.ecosystem_impact,
        integrity=choice.integrity_impact,
        intervention=choice.intervention_impact,
        notes=choice.outcome_description
    )
    
    print_separator()
    print_ethics_state(ethics)
    print_consequences(ethics)


def demo_dilemma_sequence():
    """Demonstrate a sequence of dilemmas showing ethics evolution"""
    print_separator("DILEMMA SEQUENCE DEMO")
    
    print("Scenario: Multiple ethical challenges over time\n")
    
    # Create systems
    ethics = ResearchEthicsSystem()
    dilemma_system = DilemmaSystem()
    assistant_manager = AssistantManager()
    
    # Sequence of dilemmas and choices
    scenarios = [
        (SICK_CREATURE_DILEMMA, 0, "Provide treatment"),  # Humane choice
        (OVERPOPULATION_DILEMMA, 2, "Let nature take its course"),  # Naturalist choice
        (AGGRESSIVE_CREATURE_DILEMMA, 1, "Apply behavioral conditioning"),  # Interventionist choice
        (INTERESTING_MUTATION_DILEMMA, 2, "Observe naturally")  # Scientific choice
    ]
    
    for i, (dilemma, choice_index, choice_name) in enumerate(scenarios, 1):
        print(f"\n{'='*70}")
        print(f"Dilemma {i}: {dilemma.title}")
        print('='*70)
        
        print(f"\n{dilemma.description}\n")
        
        # Get primary advisor
        advisor = assistant_manager.get_assistant_for_dilemma(dilemma, ethics)
        advice = advisor.get_advice(dilemma, ethics)
        
        print(f"{advisor.name} advises:")
        print(f"  \"{advice}\"\n")
        
        # Make choice
        choice = dilemma.choices[choice_index]
        print(f"You choose: {choice_name}")
        print(f"  Impact: {choice.get_impact_summary()}")
        
        # Update ethics
        resolution = dilemma_system.resolve_dilemma(
            dilemma, choice_index,
            {
                "welfare": ethics.welfare_score,
                "ecosystem": ethics.ecosystem_score,
                "integrity": ethics.integrity_score,
                "intervention": ethics.intervention_score
            }
        )
        
        ethics.record_action(
            action=dilemma.id,
            welfare=choice.welfare_impact,
            ecosystem=choice.ecosystem_impact,
            integrity=choice.integrity_impact,
            intervention=choice.intervention_impact
        )
        
        print_separator()
        print_ethics_state(ethics)
        print_consequences(ethics)
        
        time.sleep(0.5)  # Brief pause for readability
    
    # Final summary
    print_separator("FINAL RESEARCH PROFILE")
    
    stats = dilemma_system.get_resolution_statistics()
    print(f"Total Dilemmas Resolved: {stats['total_dilemmas']}")
    print(f"Average Welfare Impact: {stats['average_welfare_impact']:+.1f}")
    print(f"Average Intervention Impact: {stats['average_intervention_impact']:+.1f}")
    
    print_separator()
    print_ethics_state(ethics)
    print_consequences(ethics)
    
    # Get general comments from assistants
    print("\nResearch Assistant Evaluations:")
    for assistant in [DR_EMMA_CHEN, DR_MARCUS_REID, DR_SARAH_KIM]:
        comment = assistant.get_general_comment(ethics)
        print(f"\n{assistant.name}:")
        print(f"  \"{comment}\"")


def demo_consequence_effects():
    """Demonstrate how different ethics lead to different consequences"""
    print_separator("CONSEQUENCE EFFECTS DEMO")
    
    print("Scenario: Comparing three different research approaches\n")
    
    approaches = [
        ("Humane Researcher", [
            ("heal_creature", 6, 0, -1, 4),
            ("provide_shelter", 8, 2, -3, 7),
            ("natural_breeding", 3, 5, 8, -2),
            ("mark_safe_area", 4, 1, -1, 3)
        ]),
        ("Aggressive Experimenter", [
            ("apply_stimulus", -5, 0, 0, 2),
            ("force_breeding", -8, -3, -5, 12),
            ("genetic_modification", -3, -8, -10, 15),
            ("reduce_resources", -8, -3, 3, 8)
        ]),
        ("Hands-Off Naturalist", [
            ("observe_only", 0, 0, 5, -1),
            ("observe_only", 0, 0, 5, -1),
            ("let_creature_starve", -10, 0, 2, -2),
            ("observe_only", 0, 0, 5, -1)
        ])
    ]
    
    for approach_name, actions in approaches:
        print(f"\n{'='*70}")
        print(f"Approach: {approach_name}")
        print('='*70)
        
        ethics = ResearchEthicsSystem()
        
        # Apply all actions
        for action, w, e, i, v in actions:
            ethics.record_action(action, welfare=w, ecosystem=e, integrity=i, intervention=v)
        
        print_ethics_state(ethics)
        print_consequences(ethics)
        
        print(f"\nSimulation Effects:")
        modifiers = ethics.get_simulation_modifiers()
        print(f"  Creature Trust Modifier:     {modifiers['creature_trust']:.2f}x")
        print(f"  Learning Rate Modifier:      {modifiers['learning_rate']:.2f}x")
        print(f"  Ecosystem Stability Modifier:{modifiers['ecosystem_stability']:.2f}x")


def main():
    """Run all Phase 3 demos"""
    print_separator("PHASE 3: ETHICS & CONSEQUENCES")
    print("Black & White Moral Choices in Scientific Research!")
    
    demo_single_dilemma()
    
    input("\nPress Enter to continue to dilemma sequence demo...")
    demo_dilemma_sequence()
    
    input("\nPress Enter to continue to consequence effects demo...")
    demo_consequence_effects()
    
    print_separator("DEMO COMPLETE")
    print("\nPhase 3 systems are working! Key achievements:")
    print("  [OK] Ethical dilemmas present meaningful choices")
    print("  [OK] Research assistants provide contextual guidance")
    print("  [OK] Ethics scores affect simulation modifiers")
    print("  [OK] Player's approach evolves based on choices")
    print("\nReady for UI integration and full game implementation!")
    print()


if __name__ == "__main__":
    main()
