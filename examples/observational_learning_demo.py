"""
Phase 2 Demo: Observational Learning & Behavior Inheritance

This demo showcases the Black & White-inspired learning mechanics where:
1. Creatures watch and learn from successful peers
2. Players guide learning through scientific intervention
3. Offspring inherit parents' learned behaviors as instincts

Run this to see the "magic" of Black & White come alive!
"""

import sys
import time

# Add parent directory to path for imports
sys.path.insert(0, '.')

from src.models.creature_beliefs import CreatureBeliefSystem, CreatureBelief, BeliefType
from src.models.ecosystem_traits import (
    QUICK_LEARNER, MIMIC, STUBBORN, INNOVATIVE, FORGETFUL, WISE
)
from src.systems.observational_learning import (
    ObservationalLearning, ObservationalLearningManager,
    ObservableAction, ActionType, ActionOutcome
)
from src.systems.scientific_intervention import (
    ScientificIntervention, InterventionType
)
from src.systems.learned_behavior_inheritance import LearnedBehaviorInheritance
from src.systems.research_ethics import ResearchEthicsSystem


def demo_observational_learning():
    """Demonstrate creatures learning by watching each other"""
    print("\n" + "="*70)
    print("OBSERVATIONAL LEARNING DEMO")
    print("="*70)
    
    print("\nScenario: Experienced creature teaches naive creatures where to find food\n")
    
    # Create belief systems for 3 creatures
    experienced_beliefs = CreatureBeliefSystem(memory_capacity=15)
    naive1_beliefs = CreatureBeliefSystem(memory_capacity=10)
    naive2_beliefs = CreatureBeliefSystem(memory_capacity=10)
    
    # Experienced creature already knows food locations
    print("--- Experienced Creature's Knowledge ---")
    food_spots = [(45, 30, 0.9), (67, 12, 0.8), (23, 89, 0.7)]
    for x, y, conf in food_spots:
        belief = CreatureBelief(BeliefType.FOOD_LOCATION, f"area_{x}_{y}", conf)
        experienced_beliefs.add_belief(belief)
        print(f"  Knows food at area_{x}_{y} (confidence: {conf:.2f})")
    
    # Create learning systems
    print("\n--- Creating Learners ---")
    naive1_learning = ObservationalLearning("naive_1", naive1_beliefs)
    naive1_learning.apply_trait_modifiers([QUICK_LEARNER])
    print(f"  Naive 1: {naive1_learning}")
    
    naive2_learning = ObservationalLearning("naive_2", naive2_beliefs)
    naive2_learning.apply_trait_modifiers([MIMIC])
    print(f"  Naive 2 (Mimic): {naive2_learning}")
    
    # Simulate experienced creature foraging successfully
    print("\n--- Experienced Creature Forages ---")
    for x, y, _ in food_spots[:2]:  # First 2 locations
        action = ObservableAction(
            action_type=ActionType.FORAGE_SUCCESS,
            position=(float(x), float(y)),
            outcome=ActionOutcome.SUCCESS,
            performer_id="experienced",
            timestamp=time.time(),
            context="found_food"
        )
        
        print(f"\n  Experienced creature eats at ({x}, {y})")
        
        # Naive creatures observe
        naive1_pos = (x + 8, y + 5)  # Within observation range
        naive2_pos = (x + 12, y + 3)  # Also within range
        
        if naive1_learning.can_observe(naive1_pos, action):
            belief = naive1_learning.observe_action(naive1_pos, action, time.time())
            if belief:
                print(f"    -> Naive 1 learned: {belief.belief_type.value} at {belief.target} "
                      f"(conf: {belief.confidence:.2f})")
                
        if naive2_learning.can_observe(naive2_pos, action):
            belief = naive2_learning.observe_action(naive2_pos, action, time.time())
            if belief:
                print(f"    -> Naive 2 (Mimic) learned: {belief.belief_type.value} at {belief.target} "
                      f"(conf: {belief.confidence:.2f})")
    
    # Show final knowledge
    print("\n--- Final Knowledge State ---")
    print(f"\n  Naive 1: {naive1_beliefs}")
    print(f"    Beliefs: {naive1_beliefs.get_belief_count()}")
    
    print(f"\n  Naive 2 (Mimic): {naive2_beliefs}")
    print(f"    Beliefs: {naive2_beliefs.get_belief_count()}")
    print(f"    (Mimic trait gives 2x observation range and 1.5x imitation success!)")


def demo_scientific_intervention():
    """Demonstrate player guiding creature learning"""
    print("\n" + "="*70)
    print("SCIENTIFIC INTERVENTION DEMO")
    print("="*70)
    
    print("\nScenario: Scientist guides creature exploration with rewards and discouragement\n")
    
    # Create systems
    ethics = ResearchEthicsSystem()
    intervention = ScientificIntervention(ethics_system=ethics)
    creature_beliefs = CreatureBeliefSystem()
    
    print("--- Creature Explores Arena ---")
    
    # Creature explores good area
    print("\n  Creature explores safe grassland at (25, 30)")
    print("  Scientist rewards with food!")
    belief = intervention.reward_behavior(
        creature_id="explorer_1",
        belief_system=creature_beliefs,
        position=(25.0, 30.0),
        behavior="explored_new_area"
    )
    print(f"    -> Creature learned: {belief.belief_type.value} at {belief.target} "
          f"(conf: {belief.confidence:.2f})")
    
    # Creature approaches danger
    print("\n  Creature approaches dangerous cliff at (90, 90)")
    print("  Scientist applies mild stimulus to discourage!")
    belief = intervention.discourage_behavior(
        creature_id="explorer_1",
        belief_system=creature_beliefs,
        position=(90.0, 90.0),
        behavior="entered_danger_zone"
    )
    print(f"    -> Creature learned: {belief.belief_type.value} at {belief.target} "
          f"(conf: {belief.confidence:.2f})")
    
    # Creature finds food
    print("\n  Creature finds food at (45, 60)")
    print("  Scientist rewards successful foraging!")
    belief = intervention.reward_behavior(
        creature_id="explorer_1",
        belief_system=creature_beliefs,
        position=(45.0, 60.0),
        behavior="foraged_successfully"
    )
    print(f"    -> Creature learned: {belief.belief_type.value} at {belief.target} "
          f"(conf: {belief.confidence:.2f})")
    
    # Show results
    print("\n--- Results ---")
    print(f"\n  Creature's Beliefs: {creature_beliefs}")
    summary = creature_beliefs.get_summary()
    print(f"    Total beliefs: {summary['total_beliefs']}")
    print(f"    By type: {summary['beliefs_by_type']}")
    
    print(f"\n  Ethics System: {ethics}")
    print(f"    Research approach: {ethics.get_research_approach()}")
    print(f"    Welfare score: {ethics.welfare_score:.1f}")
    print(f"    Intervention score: {ethics.intervention_score:.1f}")
    
    print(f"\n  Intervention Stats: {intervention}")
    stats = intervention.get_statistics()
    print(f"    Total interventions: {stats['total_interventions']}")
    print(f"    By type: {stats['by_type']}")


def demo_behavior_inheritance():
    """Demonstrate offspring inheriting learned behaviors"""
    print("\n" + "="*70)
    print("LEARNED BEHAVIOR INHERITANCE DEMO")
    print("="*70)
    
    print("\nScenario: Experienced parents pass knowledge to offspring as instincts\n")
    
    # Create parent belief systems
    print("--- Parent 1: Experienced Forager ---")
    parent1_beliefs = CreatureBeliefSystem()
    food_knowledge = [
        (45, 30, 0.9),
        (67, 12, 0.8),
        (23, 89, 0.7),
        (50, 50, 0.6)
    ]
    for x, y, conf in food_knowledge:
        belief = CreatureBelief(BeliefType.FOOD_LOCATION, f"area_{x}_{y}", conf)
        parent1_beliefs.add_belief(belief)
        print(f"  Knows food at area_{x}_{y} (confidence: {conf:.2f})")
    
    print("\n--- Parent 2: Cautious Explorer ---")
    parent2_beliefs = CreatureBeliefSystem()
    danger_knowledge = [
        (90, 90, 0.95),
        (10, 95, 0.85),
        (80, 10, 0.75)
    ]
    safe_knowledge = [
        (25, 30, 0.8),
        (50, 50, 0.7)
    ]
    for x, y, conf in danger_knowledge:
        belief = CreatureBelief(BeliefType.DANGER_ZONE, f"area_{x}_{y}", conf)
        parent2_beliefs.add_belief(belief)
        print(f"  Knows danger at area_{x}_{y} (confidence: {conf:.2f})")
    for x, y, conf in safe_knowledge:
        belief = CreatureBelief(BeliefType.SAFE_AREA, f"area_{x}_{y}", conf)
        parent2_beliefs.add_belief(belief)
        print(f"  Knows safe area at area_{x}_{y} (confidence: {conf:.2f})")
    
    # Create offspring
    print("\n--- Offspring Born ---")
    child_beliefs = CreatureBeliefSystem()
    child_traits = [STUBBORN]  # Stubborn retains inherited beliefs better
    
    # Inherit behaviors
    inheritance_system = LearnedBehaviorInheritance()
    print(f"\nInheritance System: {inheritance_system}")
    print(f"  Inheritance strength: {inheritance_system.inheritance_strength:.2f}")
    print(f"  Mutation chance: {inheritance_system.mutation_chance:.2f}")
    
    # Preview inheritance
    print("\n--- Inheritance Preview ---")
    preview = inheritance_system.get_inheritance_preview(
        parent1_beliefs, parent2_beliefs, child_traits
    )
    print(f"  Trait modifier: {preview['trait_modifier']:.2f}x (STUBBORN bonus!)")
    print(f"\n  From Parent 1 (Forager):")
    for belief_info in preview['from_parent1']:
        print(f"    {belief_info['type']}: {belief_info['target']}")
        print(f"      Original: {belief_info['original_confidence']:.2f} -> "
              f"Inherited: {belief_info['inherited_confidence']:.2f}")
    print(f"\n  From Parent 2 (Explorer):")
    for belief_info in preview['from_parent2']:
        print(f"    {belief_info['type']}: {belief_info['target']}")
        print(f"      Original: {belief_info['original_confidence']:.2f} -> "
              f"Inherited: {belief_info['inherited_confidence']:.2f}")
    
    # Actually inherit
    print("\n--- Performing Inheritance ---")
    inherited_count = inheritance_system.inherit_beliefs(
        parent1_beliefs, parent2_beliefs, child_beliefs, child_traits
    )
    print(f"  Inherited {inherited_count} beliefs!")
    
    # Show child's instincts
    print("\n--- Child's Innate Instincts ---")
    print(f"  {child_beliefs}")
    summary = child_beliefs.get_summary()
    print(f"    Total instincts: {summary['total_beliefs']}")
    print(f"    By type: {summary['beliefs_by_type']}")
    print(f"    Average confidence: {summary['average_confidence']:.2f}")
    
    print("\n  Child is born knowing:")
    for belief in sorted(child_beliefs.beliefs.values(), 
                        key=lambda b: b.confidence, reverse=True):
        print(f"    - {belief.belief_type.value} at {belief.target} "
              f"(confidence: {belief.confidence:.2f})")


def demo_full_learning_cycle():
    """Demonstrate complete learning cycle across generations"""
    print("\n" + "="*70)
    print("FULL LEARNING CYCLE DEMO")
    print("="*70)
    
    print("\nScenario: Complete cycle from observation -> learning -> inheritance\n")
    
    # Generation 1: Learn through observation
    print("--- GENERATION 1: Learning Through Observation ---")
    gen1_beliefs = CreatureBeliefSystem()
    gen1_learning = ObservationalLearning("gen1", gen1_beliefs)
    gen1_learning.apply_trait_modifiers([QUICK_LEARNER])
    
    # Observe successful actions
    actions = [
        (ActionType.FORAGE_SUCCESS, (45, 30)),
        (ActionType.FORAGE_SUCCESS, (45, 30)),  # Repeated observation
        (ActionType.FLEE_DANGER, (90, 90)),
        (ActionType.FIND_SHELTER, (25, 25))
    ]
    
    for action_type, pos in actions:
        action = ObservableAction(
            action_type=action_type,
            position=pos,
            outcome=ActionOutcome.SUCCESS,
            performer_id="teacher",
            timestamp=time.time()
        )
        gen1_learning.observe_action((pos[0] + 5, pos[1] + 5), action, time.time())
    
    print(f"  Gen 1 learned {gen1_beliefs.get_belief_count()} beliefs through observation")
    
    # Generation 2: Inherit from Gen 1
    print("\n--- GENERATION 2: Inheriting Knowledge ---")
    gen2_beliefs = CreatureBeliefSystem()
    inheritance = LearnedBehaviorInheritance()
    
    # Gen 1 breeds with another creature (simplified)
    partner_beliefs = CreatureBeliefSystem()
    partner_beliefs.add_belief(CreatureBelief(BeliefType.SAFE_AREA, "area_30_30", 0.8))
    
    inherited = inheritance.inherit_beliefs(gen1_beliefs, partner_beliefs, gen2_beliefs)
    print(f"  Gen 2 inherited {inherited} beliefs as instincts")
    
    # Gen 2 also learns new things
    print("\n--- GENERATION 2: Learning New Things ---")
    gen2_learning = ObservationalLearning("gen2", gen2_beliefs)
    gen2_learning.apply_trait_modifiers([MIMIC])
    
    new_action = ObservableAction(
        action_type=ActionType.DRINK_WATER,
        position=(60.0, 40.0),
        outcome=ActionOutcome.SUCCESS,
        performer_id="other",
        timestamp=time.time()
    )
    gen2_learning.observe_action((65, 42), new_action, time.time())
    print(f"  Gen 2 now has {gen2_beliefs.get_belief_count()} total beliefs")
    print(f"    (Inherited instincts + newly learned knowledge)")
    
    # Show progression
    print("\n--- Knowledge Progression ---")
    print(f"  Gen 1: {gen1_beliefs.get_belief_count()} beliefs (all learned)")
    print(f"  Gen 2: {gen2_beliefs.get_belief_count()} beliefs (inherited + learned)")
    print("\n  This is behavioral evolution in action!")


def main():
    """Run all Phase 2 demos"""
    print("\n" + "="*70)
    print("PHASE 2: OBSERVATIONAL LEARNING & BEHAVIOR INHERITANCE")
    print("Black & White Mechanics in Action!")
    print("="*70)
    
    demo_observational_learning()
    demo_scientific_intervention()
    demo_behavior_inheritance()
    demo_full_learning_cycle()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nPhase 2 systems are working! Key achievements:")
    print("  [OK] Creatures learn by watching successful peers")
    print("  [OK] Players can guide learning through scientific intervention")
    print("  [OK] Offspring inherit parents' knowledge as instincts")
    print("  [OK] Behavioral evolution happens alongside genetic evolution")
    print("\nReady for integration into the main game!")
    print()


if __name__ == "__main__":
    main()
