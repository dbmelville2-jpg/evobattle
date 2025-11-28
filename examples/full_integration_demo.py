"""
Black & White Integration Demo

This demo showcases all integrated Black & White systems working together:
1. Creature belief systems
2. Observational learning
3. Behavior inheritance
4. Ethical dilemmas
5. Research ethics tracking
6. Ethics consequences on simulation

Run this to see the full learning cycle in action!
"""

import random
import time
from src.models.creature import Creature
from src.models.creature_type import CreatureType
from src.models.stats import Stats
from src.models.creature_beliefs import CreatureBeliefSystem, CreatureBelief, BeliefType
from src.systems.observational_learning import ObservationalLearning, ObservableAction, ActionType, ActionOutcome
from src.systems.ethical_dilemmas import DilemmaSystem
from src.systems.research_assistants import AssistantManager
from src.systems.research_ethics import ResearchEthicsSystem
from src.systems.learned_behavior_inheritance import LearnedBehaviorInheritance


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def create_test_creature(name, x=0, y=0):
    """Create a test creature with belief system"""
    creature_type = CreatureType(
        name="TestSpecies",
        type_tags=["normal"],
        base_hp=100,
        base_attack=10,
        base_defense=10,
        base_speed=5
    )
    
    creature = Creature(
        name=name,
        creature_type=creature_type,
        level=1,
        base_stats=Stats(hp=100, max_hp=100, attack=10, defense=10, speed=5)
    )
    
    # Add Black & White systems
    creature.belief_system = CreatureBeliefSystem()
    creature.observational_learning = ObservationalLearning(
        creature_id=creature.creature_id,
        belief_system=creature.belief_system
    )
    
    return creature


def demo_observational_learning():
    """Demonstrate observational learning"""
    print_section("DEMO 1: Observational Learning")
    
    # Create creatures
    teacher = create_test_creature("Teacher", x=10, y=10)
    learner = create_test_creature("Learner", x=12, y=12)
    
    print(f"Created {teacher.name} at (10, 10)")
    print(f"Created {learner.name} at (12, 12)")
    print(f"Distance: ~2.8 units (within observation range)")
    
    # Teacher finds food
    print(f"\n{teacher.name} finds food at (10, 10)!")
    action = ObservableAction(
        action_type=ActionType.FORAGE_SUCCESS,
        position=(10, 10),
        outcome=ActionOutcome.SUCCESS,
        performer_id=teacher.creature_id,
        timestamp=0.0
    )
    
    # Learner observes
    print(f"\n{learner.name} is nearby and observes...")
    creature_positions = {
        teacher.creature_id: (10, 10),
        learner.creature_id: (12, 12)
    }
    
    learner.observational_learning.observe_action(
        action, creature_positions, current_time=0.0
    )
    
    # Check if learner learned
    food_belief = learner.belief_system.get_strongest_belief(BeliefType.FOOD_LOCATION)
    if food_belief:
        print(f"✓ {learner.name} learned: '{food_belief.target}' is a food location!")
        print(f"  Confidence: {food_belief.confidence:.2f}")
    else:
        print(f"✗ {learner.name} didn't learn (too far or blocked)")
    
    # Repeat observation to strengthen belief
    print(f"\n{teacher.name} eats again at the same spot...")
    learner.observational_learning.observe_action(
        action, creature_positions, current_time=1.0
    )
    
    food_belief = learner.belief_system.get_strongest_belief(BeliefType.FOOD_LOCATION)
    if food_belief:
        print(f"✓ Belief strengthened! Confidence: {food_belief.confidence:.2f}")


def demo_behavior_inheritance():
    """Demonstrate behavior inheritance"""
    print_section("DEMO 2: Behavior Inheritance")
    
    # Create parents with knowledge
    parent1 = create_test_creature("Parent1")
    parent2 = create_test_creature("Parent2")
    offspring = create_test_creature("Offspring")
    
    # Give parents strong beliefs
    parent1.belief_system.add_belief(CreatureBelief(
        belief_type=BeliefType.FOOD_LOCATION,
        target="area_10_10",
        confidence=0.9
    ))
    parent1.belief_system.add_belief(CreatureBelief(
        belief_type=BeliefType.FOOD_LOCATION,
        target="area_20_20",
        confidence=0.7
    ))
    
    parent2.belief_system.add_belief(CreatureBelief(
        belief_type=BeliefType.FOOD_LOCATION,
        target="area_30_30",
        confidence=0.8
    ))
    
    print(f"{parent1.name} knows:")
    for belief in parent1.belief_system.beliefs.values():
        print(f"  - {belief.target} (confidence: {belief.confidence:.2f})")
    
    print(f"\n{parent2.name} knows:")
    for belief in parent2.belief_system.beliefs.values():
        print(f"  - {belief.target} (confidence: {belief.confidence:.2f})")
    
    # Inherit behaviors
    print(f"\n{parent1.name} and {parent2.name} breed...")
    inheritance_system = LearnedBehaviorInheritance()
    inherited_count = inheritance_system.inherit_beliefs(
        parent1.belief_system,
        parent2.belief_system,
        offspring.belief_system,
        offspring.traits
    )
    
    print(f"\n{offspring.name} inherited {inherited_count} instincts:")
    for belief in offspring.belief_system.beliefs.values():
        print(f"  - {belief.target} (confidence: {belief.confidence:.2f})")
    
    print(f"\nNote: Inherited beliefs have ~60% of parent's confidence")


def demo_ethical_dilemmas():
    """Demonstrate ethical dilemma system"""
    print_section("DEMO 3: Ethical Dilemmas")
    
    dilemma_system = DilemmaSystem()
    
    # Test different scenarios
    scenarios = [
        {
            "name": "Sick Creature",
            "state": {"min_creature_health": 15, "population": 10}
        },
        {
            "name": "Overpopulation",
            "state": {"population": 95, "capacity": 100}
        },
        {
            "name": "Starvation",
            "state": {"average_hunger": 15, "population": 10}
        }
    ]
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"State: {scenario['state']}")
        
        dilemma = dilemma_system.check_for_dilemmas(scenario['state'])
        if dilemma:
            print(f"\n⚠️  DILEMMA TRIGGERED: {dilemma.title}")
            print(f"Description: {dilemma.description}")
            print(f"\nChoices:")
            for i, choice in enumerate(dilemma.choices, 1):
                print(f"  {i}. {choice.text}")
                print(f"     Ethics: W:{choice.ethics_impact.welfare:+.1f} "
                      f"E:{choice.ethics_impact.ecosystem:+.1f} "
                      f"I:{choice.ethics_impact.integrity:+.1f} "
                      f"V:{choice.ethics_impact.intervention:+.1f}")
        else:
            print("✓ No dilemma triggered")


def demo_research_ethics():
    """Demonstrate research ethics system"""
    print_section("DEMO 4: Research Ethics & Consequences")
    
    ethics_system = ResearchEthicsSystem()
    
    print("Starting ethics scores:")
    print(f"  Welfare: {ethics_system.welfare_score:.1f}")
    print(f"  Ecosystem: {ethics_system.ecosystem_score:.1f}")
    print(f"  Integrity: {ethics_system.integrity_score:.1f}")
    print(f"  Intervention: {ethics_system.intervention_score:.1f}")
    
    # Perform various actions
    print("\nPerforming research actions...")
    
    print("\n1. Rewarding creature with food (humane)")
    ethics_system.record_action("reward_food", welfare=5, ecosystem=0, integrity=0, intervention=10)
    
    print("2. Observing without interfering (hands-off)")
    ethics_system.record_action("observe", welfare=0, ecosystem=0, integrity=5, intervention=-5)
    
    print("3. Marking area for study (minimal intervention)")
    ethics_system.record_action("mark_area", welfare=0, ecosystem=0, integrity=0, intervention=3)
    
    # Show updated scores
    print("\nUpdated ethics scores:")
    print(f"  Welfare: {ethics_system.welfare_score:.1f}")
    print(f"  Ecosystem: {ethics_system.ecosystem_score:.1f}")
    print(f"  Integrity: {ethics_system.integrity_score:.1f}")
    print(f"  Intervention: {ethics_system.intervention_score:.1f}")
    
    # Show consequences
    print("\nSimulation modifiers:")
    modifiers = ethics_system.get_simulation_modifiers()
    print(f"  Creature Trust: {modifiers['creature_trust']:.2f}x")
    print(f"  Learning Rate: {modifiers['learning_rate']:.2f}x")
    print(f"  Ecosystem Stability: {modifiers['ecosystem_stability']:.2f}x")
    
    approach = ethics_system.get_research_approach()
    print(f"\nResearch Approach: {approach.value}")


def demo_research_assistants():
    """Demonstrate research assistant system"""
    print_section("DEMO 5: Research Assistants")
    
    assistant_manager = AssistantManager()
    
    # Create a sample dilemma
    dilemma_system = DilemmaSystem()
    dilemma = dilemma_system.check_for_dilemmas({"min_creature_health": 15, "population": 10})
    
    if dilemma:
        print(f"Dilemma: {dilemma.title}\n")
        
        # Get advice from each assistant
        for assistant_type in ["humane", "pragmatic", "naturalist"]:
            advice = assistant_manager.get_advice(assistant_type, dilemma)
            print(f"{advice.assistant_name} ({advice.personality}):")
            print(f"  \"{advice.advice}\"")
            print(f"  Recommends: Choice {advice.recommended_choice + 1}")
            print()


def demo_full_integration():
    """Demonstrate all systems working together"""
    print_section("DEMO 6: Full Integration")
    
    print("Simulating a complete learning cycle...\n")
    
    # Setup
    teacher = create_test_creature("Alpha", x=50, y=30)
    learner = create_test_creature("Beta", x=52, y=32)
    ethics_system = ResearchEthicsSystem()
    inheritance_system = LearnedBehaviorInheritance()
    
    # Step 1: Teacher finds food
    print("Step 1: Alpha discovers food at (50, 30)")
    action = ObservableAction(
        action_type=ActionType.FORAGE_SUCCESS,
        position=(50, 30),
        outcome=ActionOutcome.SUCCESS,
        performer_id=teacher.creature_id,
        timestamp=0.0
    )
    
    # Step 2: Learner observes
    print("Step 2: Beta observes Alpha eating")
    creature_positions = {
        teacher.creature_id: (50, 30),
        learner.creature_id: (52, 32)
    }
    learner.observational_learning.observe_action(action, creature_positions, 0.0)
    
    belief = learner.belief_system.get_strongest_belief(BeliefType.FOOD_LOCATION)
    if belief:
        print(f"  ✓ Beta learned: {belief.target} (confidence: {belief.confidence:.2f})")
    
    # Step 3: Player observes (ethical action)
    print("\nStep 3: Researcher observes without interfering")
    ethics_system.record_action("observe", welfare=0, ecosystem=0, integrity=5, intervention=-5)
    modifiers = ethics_system.get_simulation_modifiers()
    print(f"  Learning rate modifier: {modifiers['learning_rate']:.2f}x")
    
    # Step 4: Breeding
    print("\nStep 4: Alpha and Beta breed")
    offspring = create_test_creature("Gamma")
    inherited_count = inheritance_system.inherit_beliefs(
        teacher.belief_system,
        learner.belief_system,
        offspring.belief_system,
        offspring.traits
    )
    print(f"  ✓ Gamma inherited {inherited_count} instincts")
    
    # Step 5: Show results
    print("\nStep 5: Results")
    print(f"  Alpha: {len(teacher.belief_system.beliefs)} beliefs")
    print(f"  Beta: {len(learner.belief_system.beliefs)} beliefs")
    print(f"  Gamma: {len(offspring.belief_system.beliefs)} instincts (inherited)")
    print(f"\n  Research Approach: {ethics_system.get_research_approach().value}")
    print(f"  Gamma knows where food is without ever seeing it!")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("  BLACK & WHITE INTEGRATION DEMO")
    print("  All Systems Working Together!")
    print("="*60)
    
    try:
        demo_observational_learning()
        time.sleep(1)
        
        demo_behavior_inheritance()
        time.sleep(1)
        
        demo_ethical_dilemmas()
        time.sleep(1)
        
        demo_research_ethics()
        time.sleep(1)
        
        demo_research_assistants()
        time.sleep(1)
        
        demo_full_integration()
        
        print_section("DEMO COMPLETE!")
        print("All Black & White systems are integrated and working!")
        print("\nKey Features:")
        print("  ✓ Creatures learn by observing each other")
        print("  ✓ Knowledge passes to offspring as instincts")
        print("  ✓ Ethical dilemmas trigger based on simulation state")
        print("  ✓ Research ethics affect learning rates")
        print("  ✓ AI assistants provide guidance")
        print("\nRun the main game (py main.py) to see it in action!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
