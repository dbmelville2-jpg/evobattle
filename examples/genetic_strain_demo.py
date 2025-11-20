"""
Genetic Strain Evolution Demo

Demonstrates the genetic lineage system:
- Strain-based families instead of teams
- Color-coded creatures by genetic similarity
- Trait inheritance and mutation
- Natural selection and strain extinction
"""

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.trait import Trait
from src.models.ecosystem_traits import EFFICIENT, CURIOUS, FORAGER, AGGRESSIVE
from src.systems.breeding import Breeding
from src.systems.population import PopulationManager
import time


def create_founder_creature(name: str, traits: list, hue: float, strain_id: str) -> Creature:
    """Create a founder creature for a genetic strain."""
    base_stats = Stats(
        max_hp=100,
        attack=15,
        defense=12,
        speed=14
    )
    
    creature_type = CreatureType(
        name="Evolver",
        base_stats=base_stats,
        type_tags=["normal"]
    )
    
    creature = Creature(
        name=name,
        creature_type=creature_type,
        level=1,
        traits=traits,
        hue=hue,
        strain_id=strain_id,
        mature=True  # Start mature for breeding demo
    )
    
    return creature


def main():
    print("=" * 70)
    print("GENETIC STRAIN EVOLUTION DEMO")
    print("=" * 70)
    print()
    print("This demo shows how creatures form genetic strains (families)")
    print("based on shared ancestry and traits.")
    print()
    
    # Initialize systems
    breeding = Breeding(mutation_rate=0.15)  # Higher mutation rate for demo
    population = PopulationManager()
    
    print("Creating founder strains...")
    print()
    
    # Create three founder strains with different colors and traits
    # Red Strain - Aggressive hunters
    red_founder1 = create_founder_creature(
        "RedAlpha",
        [AGGRESSIVE],
        hue=0.0,  # Red
        strain_id="strain_red"
    )
    red_founder2 = create_founder_creature(
        "RedBeta",
        [AGGRESSIVE],
        hue=10.0,  # Slight variation
        strain_id="strain_red"
    )
    
    # Green Strain - Efficient foragers
    green_founder1 = create_founder_creature(
        "GreenAlpha",
        [EFFICIENT, FORAGER],
        hue=120.0,  # Green
        strain_id="strain_green"
    )
    green_founder2 = create_founder_creature(
        "GreenBeta",
        [EFFICIENT],
        hue=130.0,
        strain_id="strain_green"
    )
    
    # Blue Strain - Curious explorers
    blue_founder1 = create_founder_creature(
        "BlueAlpha",
        [CURIOUS],
        hue=240.0,  # Blue
        strain_id="strain_blue"
    )
    blue_founder2 = create_founder_creature(
        "BlueBeta",
        [CURIOUS],
        hue=250.0,
        strain_id="strain_blue"
    )
    
    # Add founders to population
    for creature in [red_founder1, red_founder2, green_founder1, 
                     green_founder2, blue_founder1, blue_founder2]:
        population.spawn_creature(creature, log_event=False)
        rgb = creature.get_display_color()
        print(f"✓ {creature.name:15s} - Strain: {creature.strain_id:12s} "
              f"Hue: {creature.hue:6.1f}° RGB: {rgb}")
        print(f"  Traits: {', '.join(t.base_name() for t in creature.traits)}")
    
    print()
    print("=" * 70)
    print("BREEDING SIMULATION")
    print("=" * 70)
    print()
    
    # Simulate several generations of breeding
    generation = 1
    max_generations = 3
    
    while generation <= max_generations:
        print(f"\n--- Generation {generation} ---")
        
        # Get mature creatures that can breed
        breedable = population.get_mature_creatures()
        
        if len(breedable) < 2:
            print("Not enough creatures to breed!")
            break
        
        # Breed pairs (simulate natural reproduction)
        offspring_count = 0
        bred_pairs = set()
        
        for i, parent1 in enumerate(breedable):
            for parent2 in breedable[i+1:]:
                # Avoid breeding same pair twice
                pair_id = tuple(sorted([parent1.creature_id, parent2.creature_id]))
                if pair_id in bred_pairs:
                    continue
                
                # Breed them
                offspring = breeding.breed(parent1, parent2, birth_time=time.time())
                
                if offspring:
                    # Make offspring immediately mature for demo purposes
                    offspring.mature = True
                    population.spawn_creature(offspring, log_event=False)
                    offspring_count += 1
                    bred_pairs.add(pair_id)
                    
                    # Show inheritance info
                    print(f"\n{parent1.name} + {parent2.name} → {offspring.name}")
                    print(f"  Parent strains: {parent1.strain_id[:8]} + {parent2.strain_id[:8]}")
                    print(f"  Child strain: {offspring.strain_id[:8]}")
                    print(f"  Parent hues: {parent1.hue:.1f}° + {parent2.hue:.1f}°")
                    print(f"  Child hue: {offspring.hue:.1f}° (RGB: {offspring.get_display_color()})")
                    print(f"  Traits: {', '.join(t.base_name() for t in offspring.traits)}")
                    
                    # Check for mutations and report trade-offs
                    parent_trait_names = set(t.base_name() for t in parent1.traits + parent2.traits)
                    child_trait_names = set(t.base_name() for t in offspring.traits)
                    
                    new_traits = child_trait_names - parent_trait_names
                    lost_traits = parent_trait_names - child_trait_names
                    
                    if new_traits:
                        print(f"  🧬 MUTATION: Gained trait(s): {', '.join(new_traits)}")
                    if lost_traits:
                        print(f"  🧬 MUTATION: Lost trait(s): {', '.join(lost_traits)}")
                    
                    # Report per-trait trade-off details when mutated
                    for t in offspring.traits:
                        if t.is_mutated():
                            print(f"  ⚡ MUTATED TRAIT: {t.base_name()} -> mods: str={t.strength_modifier:.3f}, spd={t.speed_modifier:.3f}, def={t.defense_modifier:.3f}")
                    
                    # Check for new strain
                    if (offspring.strain_id != parent1.strain_id and 
                        offspring.strain_id != parent2.strain_id):
                        print(f"  ⭐ NEW STRAIN EMERGED!")
                
                # Limit offspring per generation for demo
                if offspring_count >= 4:
                    break
            
            if offspring_count >= 4:
                break
        
        print(f"\nGeneration {generation} complete: {offspring_count} offspring born")
        generation += 1
    
    print()
    print("=" * 70)
    print("STRAIN STATISTICS")
    print("=" * 70)
    print()
    
    # Get strain statistics
    strain_stats = population.get_strain_statistics()
    
    print(f"Total creatures: {len(population.population)}")
    print(f"Alive creatures: {len(population.get_alive_creatures())}")
    print(f"Number of strains: {len(strain_stats)}")
    print()
    
    # Show dominant strains
    print("DOMINANT STRAINS:")
    dominant = population.get_dominant_strains(top_n=5)
    for i, (strain_id, alive_count) in enumerate(dominant, 1):
        stats = strain_stats[strain_id]
        print(f"{i}. Strain {strain_id[:8]:8s} - "
              f"Alive: {alive_count:2d}, "
              f"Total: {stats['total']:2d}, "
              f"Avg Hue: {stats['avg_hue']:6.1f}°")
    
    print()
    
    # Check for extinct strains
    extinct = population.get_extinct_strains()
    if extinct:
        print(f"EXTINCT STRAINS: {len(extinct)}")
        for strain_id in extinct:
            print(f"  ✝ Strain {strain_id[:8]} - died out")
    else:
        print("No extinct strains yet - all founder strains have living descendants!")
    
    print()
    print("=" * 70)
    print("VISUAL COLOR SPECTRUM")
    print("=" * 70)
    print()
    print("Creatures are colored by their genetic strain (hue):")
    print("Similar colors = genetically related")
    print()
    
    # Show all alive creatures sorted by hue
    alive = sorted(population.get_alive_creatures(), key=lambda c: c.hue)
    for creature in alive:
        # Create visual color representation
        hue_normalized = creature.hue / 360.0
        color_bar = "█" * 20
        
        # Map hue to color name
        if creature.hue < 30 or creature.hue > 330:
            color_name = "RED"
        elif 90 <= creature.hue < 150:
            color_name = "GREEN"
        elif 210 <= creature.hue < 270:
            color_name = "BLUE"
        elif 30 <= creature.hue < 90:
            color_name = "YELLOW"
        elif 150 <= creature.hue < 210:
            color_name = "CYAN"
        else:
            color_name = "PURPLE"
        
        print(f"{creature.name:15s} Hue: {creature.hue:6.1f}° [{color_name:7s}] {color_bar}")
    
    print()
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()
    print("Key Features Demonstrated:")
    print("✓ Creatures form genetic strains (families)")
    print("✓ Color (hue) represents genetic similarity")
    print("✓ Traits are inherited from parents")
    print("✓ Mutations can add/remove/modify traits")
    print("✓ New strains can emerge from major mutations")
    print("✓ Population statistics track strain dominance")
    print("✓ Natural selection enables strain extinction")
    print()


if __name__ == "__main__":
    main()
