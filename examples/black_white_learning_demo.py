"""
Black & White Learning System Demo

This demo showcases the new creature learning and scientific interaction systems
inspired by Black & White's innovative mechanics.

Features demonstrated:
1. Creature Belief System - Creatures learn and remember
2. Learning Traits - Quick Learner, Mimic, Stubborn, etc.
3. Scientific Cursor - Research tools for player interaction
4. Research Ethics - Track your scientific approach

Run this demo to see creatures forming beliefs, learning from each other,
and responding to your scientific interventions.
"""

import sys
import random
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, '.')

from src.models.creature_beliefs import (
    CreatureBeliefSystem, CreatureBelief, BeliefType
)
from src.models.ecosystem_traits import (
    QUICK_LEARNER, MIMIC, STUBBORN, INNOVATIVE, FORGETFUL, WISE, INSTINCTIVE
)
from src.systems.research_ethics import (
    ResearchEthicsSystem, ETHICAL_ACTIONS
)
from src.rendering.scientific_cursor import (
    ScientificCursor, CursorTool, MarkerType
)


def demo_belief_system():
    """Demonstrate the creature belief system"""
    print("\n" + "="*70)
    print("CREATURE BELIEF SYSTEM DEMO")
    print("="*70)
    
    # Create a belief system for a creature
    belief_system = CreatureBeliefSystem(memory_capacity=10)
    
    print(f"\nCreated belief system: {belief_system}")
    print(f"Memory capacity: {belief_system.memory_capacity} beliefs")
    
    # Creature discovers food locations
    print("\n--- Creature explores and finds food ---")
    food_locations = [
        ("area_10_20", 0.6),
        ("area_50_30", 0.8),
        ("area_75_60", 0.5)
    ]
    
    for location, confidence in food_locations:
        belief = CreatureBelief(BeliefType.FOOD_LOCATION, location, confidence)
        belief_system.add_belief(belief)
        print(f"  Learned: Food at {location} (confidence: {confidence:.2f})")
    
    # Creature learns about dangers
    print("\n--- Creature encounters dangers ---")
    danger_zones = [
        ("area_90_90", 0.9),  # Very dangerous!
        ("area_40_10", 0.4)   # Somewhat risky
    ]
    
    for location, confidence in danger_zones:
        belief = CreatureBelief(BeliefType.DANGER_ZONE, location, confidence)
        belief_system.add_belief(belief)
        print(f"  Learned: Danger at {location} (confidence: {confidence:.2f})")
    
    # Show strongest beliefs
    print("\n--- Strongest beliefs by type ---")
    for belief_type in [BeliefType.FOOD_LOCATION, BeliefType.DANGER_ZONE]:
        strongest = belief_system.get_strongest_belief(belief_type)
        if strongest:
            print(f"  {belief_type.value}: {strongest.target} (conf: {strongest.confidence:.2f})")
    
    # Reinforce a belief
    print("\n--- Creature finds food again at area_50_30 ---")
    belief_system.get_belief("area_50_30").reinforce(0.15)
    print(f"  Reinforced belief about area_50_30")
    print(f"  New confidence: {belief_system.get_belief('area_50_30').confidence:.2f}")
    
    # Show summary
    print(f"\n{belief_system}")
    summary = belief_system.get_summary()
    print(f"Average confidence: {summary['average_confidence']:.2f}")
    print(f"Beliefs by type: {summary['beliefs_by_type']}")


def demo_learning_traits():
    """Demonstrate learning-related traits"""
    print("\n" + "="*70)
    print("LEARNING TRAITS DEMO")
    print("="*70)
    
    traits = [
        QUICK_LEARNER,
        MIMIC,
        STUBBORN,
        INNOVATIVE,
        FORGETFUL,
        WISE,
        INSTINCTIVE
    ]
    
    print("\nAvailable Learning Traits:\n")
    for trait in traits:
        print(f"  {trait.name} ({trait.rarity})")
        print(f"    {trait.description}")
        
        # Show key effects
        effects = trait.interaction_effects
        if 'learning_rate_multiplier' in effects:
            print(f"    Learning Rate: {effects['learning_rate_multiplier']:.1f}x")
        if 'memory_capacity_multiplier' in effects:
            print(f"    Memory Capacity: {effects['memory_capacity_multiplier']:.1f}x")
        print()
    
    # Simulate different learning rates
    print("\n--- Learning Speed Comparison ---")
    print("Scenario: Three creatures observe a successful foraging behavior\n")
    
    creatures = [
        ("Quick Learner", QUICK_LEARNER, 1.5),
        ("Normal Creature", None, 1.0),
        ("Stubborn Creature", STUBBORN, 0.5)
    ]
    
    for name, trait, learning_rate in creatures:
        base_confidence = 0.3
        learned_confidence = base_confidence * learning_rate
        print(f"  {name}: Learns with {learned_confidence:.2f} confidence")
        if trait:
            print(f"    (Learning rate: {learning_rate:.1f}x from {trait.name} trait)")


def demo_scientific_cursor():
    """Demonstrate the scientific cursor system"""
    print("\n" + "="*70)
    print("SCIENTIFIC CURSOR DEMO")
    print("="*70)
    
    cursor = ScientificCursor()
    
    print(f"\nInitial state: {cursor.get_tool_name()}")
    print(f"Tool charge: {cursor.tool_charge}/{cursor.max_charge}")
    
    # Try different tools
    print("\n--- Available Research Tools ---\n")
    for tool in CursorTool:
        cursor.select_tool(tool)
        cost = cursor.tool_costs[tool]
        print(f"  {cursor.get_tool_name()} (Cost: {cost})")
        print(f"    {cursor.get_tool_description()}")
        print()
    
    # Simulate using tools
    print("\n--- Using Tools ---")
    cursor.select_tool(CursorTool.FOOD_DISPENSER)
    print(f"\nSelected: {cursor.get_tool_name()}")
    print(f"Charge before use: {cursor.tool_charge:.1f}")
    
    if cursor.use_tool_charge():
        print(f"[OK] Dispensed food reward")
        print(f"Charge after use: {cursor.tool_charge:.1f}")
    
    # Add markers
    print("\n--- Placing Area Markers ---")
    cursor.add_marker((25.0, 30.0), MarkerType.SAFE, radius=10.0, duration=30.0)
    cursor.add_marker((75.0, 80.0), MarkerType.DANGER, radius=8.0, duration=60.0)
    
    print(f"Placed {len(cursor.markers)} markers:")
    for marker in cursor.markers:
        print(f"  {marker.marker_type.value} at {marker.position} (radius: {marker.radius})")
    
    # Check position
    test_pos = (27.0, 32.0)
    markers_at_pos = cursor.get_markers_at_position(test_pos)
    print(f"\nMarkers affecting position {test_pos}: {len(markers_at_pos)}")
    for marker in markers_at_pos:
        print(f"  - {marker.marker_type.value}")


def demo_research_ethics():
    """Demonstrate the research ethics system"""
    print("\n" + "="*70)
    print("RESEARCH ETHICS SYSTEM DEMO")
    print("="*70)
    
    ethics = ResearchEthicsSystem()
    
    print(f"\nInitial state: {ethics}")
    print(f"Research approach: {ethics.get_research_approach()}")
    
    # Simulate various research actions
    print("\n--- Simulating Research Session ---\n")
    
    actions = [
        ("reward_food", "creature_001", "Rewarded creature for exploring new area"),
        ("observe_only", None, "Watched creatures interact naturally"),
        ("mark_safe_area", None, "Marked shelter location for creatures"),
        ("heal_creature", "creature_002", "Healed injured creature"),
        ("observe_only", None, "Continued observation"),
        ("reward_food", "creature_003", "Rewarded successful foraging"),
    ]
    
    for action, creature_id, notes in actions:
        impacts = ETHICAL_ACTIONS[action]
        ethics.record_action(
            action=action,
            welfare=impacts["welfare"],
            ecosystem=impacts["ecosystem"],
            integrity=impacts["integrity"],
            intervention=impacts["intervention"],
            target_creature_id=creature_id,
            notes=notes
        )
        print(f"  Action: {action}")
        print(f"    {notes}")
        print(f"    Impact: welfare={impacts['welfare']:+d}, "
              f"ecosystem={impacts['ecosystem']:+d}, "
              f"intervention={impacts['intervention']:+d}")
        print()
    
    # Show final state
    print(f"\n{ethics}")
    print(f"\nResearch Approach: {ethics.get_research_approach()}")
    
    summary = ethics.get_summary()
    print(f"\nStatistics:")
    print(f"  Total interventions: {summary['total_interventions']}")
    print(f"  Positive interventions: {summary['positive_interventions']}")
    print(f"  Creatures helped: {summary['creatures_helped']}")
    
    print(f"\nModifiers affecting simulation:")
    print(f"  Creature trust: {summary['modifiers']['creature_trust']:.2f}x")
    print(f"  Ecosystem stability: {summary['modifiers']['ecosystem_stability']:.2f}x")
    print(f"  Learning rate: {summary['modifiers']['learning_rate']:.2f}x")
    
    # Show what happens with different approaches
    print("\n--- Different Research Approaches ---\n")
    
    approaches = [
        ("Cruel Experimenter", [("apply_stimulus", -5, 0, 0, 2)] * 10),
        ("Benevolent Helper", [("reward_food", 2, 0, 0, 1)] * 10),
        ("Pure Observer", [("observe_only", 0, 0, 5, -1)] * 10),
    ]
    
    for approach_name, actions in approaches:
        test_ethics = ResearchEthicsSystem()
        for action, w, e, i, int_val in actions:
            test_ethics.record_action(action, welfare=w, ecosystem=e, 
                                     integrity=i, intervention=int_val)
        
        print(f"  {approach_name}:")
        print(f"    {test_ethics}")
        print(f"    Approach: {test_ethics.get_research_approach()}")
        print(f"    Learning modifier: {test_ethics.get_learning_rate_modifier():.2f}x")
        print()


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("BLACK & WHITE LEARNING SYSTEM DEMO")
    print("Creature AI, Scientific Tools, and Research Ethics")
    print("="*70)
    
    demo_belief_system()
    demo_learning_traits()
    demo_scientific_cursor()
    demo_research_ethics()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nThese systems are now ready to integrate into the main game!")
    print("\nNext steps:")
    print("  1. Integrate belief system with creature decision-making")
    print("  2. Add scientific cursor to game UI")
    print("  3. Connect ethics system to simulation modifiers")
    print("  4. Implement observational learning between creatures")
    print()


if __name__ == "__main__":
    main()
