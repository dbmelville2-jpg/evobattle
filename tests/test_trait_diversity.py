import unittest
from src.models.genetics import GeneticsEngine
from src.models.creature import Creature, CreatureType
from src.models.trait import Trait
from src.models.stats import Stats
from src.models.expanded_traits import (
    AGGRESSIVE_TRAIT, TIMID_TRAIT, BOLD_TRAIT, CAUTIOUS_TRAIT,
    SOCIAL_TRAIT, SOLITARY_TRAIT, BERSERKER_TRAIT, EXECUTIONER_TRAIT,
    ARMORED_TRAIT, SWIFT_TRAIT, NOCTURNAL_TRAIT, DIURNAL_TRAIT
)
import random

class TestTraitDiversity(unittest.TestCase):
    def setUp(self):
        self.genetics = GeneticsEngine(mutation_rate=0.1)
        self.base_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )

    def test_trait_cap(self):
        """Test that the hard cap on traits is enforced."""
        parent1 = Creature(name="P1", creature_type=self.base_type, mature=True)
        parent2 = Creature(name="P2", creature_type=self.base_type, mature=True)
        
        # Add many traits to parents
        for i in range(10):
            parent1.add_trait(Trait(name=f"Trait1_{i}", trait_type="physical"))
            parent2.add_trait(Trait(name=f"Trait2_{i}", trait_type="physical"))
            
        # Breed
        offspring_traits = self.genetics.combine_traits(parent1, parent2)
        
        # Check cap
        self.assertLessEqual(len(offspring_traits), self.genetics.MAX_TRAITS)

    def test_trait_modification(self):
        """Test that traits can be modified/flipped."""
        # Force high mutation rate for this test
        self.genetics.mutation_rate = 1.0
        
        parent1 = Creature(name="P1", creature_type=self.base_type, mature=True)
        parent2 = Creature(name="P2", creature_type=self.base_type, mature=True)
        
        # Add specific traits that have modification pathways
        parent1.add_trait(AGGRESSIVE_TRAIT.copy())
        parent2.add_trait(TIMID_TRAIT.copy())
        
        modified_count = 0
        for _ in range(50):
            traits = self.genetics.combine_traits(parent1, parent2)
            for trait in traits:
                if trait.provenance.source_type == 'modified':
                    modified_count += 1
                    # Verify description update
                    self.assertIn("Evolved from", trait.description)
                    
        self.assertGreater(modified_count, 0, "Should have triggered some trait modifications")

    def test_new_traits_existence(self):
        """Verify new traits are defined and have correct effects."""
        self.assertIn('night_vision', NOCTURNAL_TRAIT.interaction_effects)
        self.assertIn('sunlight_affinity', DIURNAL_TRAIT.interaction_effects)
        
        # Check modified existing traits
        self.assertIn('scaredy_cat', TIMID_TRAIT.interaction_effects)
        self.assertIn('pack_hunter', SOCIAL_TRAIT.interaction_effects)
        self.assertIn('loner_strength', SOLITARY_TRAIT.interaction_effects)

    def test_trait_loss_soft_cap(self):
        """Test that traits are lost more frequently above soft cap."""
        parent1 = Creature(name="P1", creature_type=self.base_type, mature=True)
        parent2 = Creature(name="P2", creature_type=self.base_type, mature=True)
        
        # Add traits above soft cap (5) but below hard cap (8)
        traits_to_add = [
            AGGRESSIVE_TRAIT, TIMID_TRAIT, BOLD_TRAIT, CAUTIOUS_TRAIT,
            SOCIAL_TRAIT, SOLITARY_TRAIT, ARMORED_TRAIT
        ]
        for t in traits_to_add:
            parent1.add_trait(t.copy())
            parent2.add_trait(t.copy())
            
        # Breed many times and check average trait count
        total_traits = 0
        iterations = 50
        for _ in range(iterations):
            traits = self.genetics.combine_traits(parent1, parent2)
            total_traits += len(traits)
            
        avg_traits = total_traits / iterations
        # Should be less than the input count (7) due to soft cap loss
        self.assertLess(avg_traits, 7.0)

    def test_environmental_traits(self):
        """Verify environmental traits can be generated and have correct effects."""
        from src.models.trait_generator import TraitGenerator
        generator = TraitGenerator()
        
        # Generate environmental traits
        env_traits = []
        for _ in range(20):
            trait = generator.generate_trait(category='environmental')
            env_traits.append(trait)
            
        self.assertTrue(len(env_traits) > 0)
        
        # Check for specific effects
        has_terrain_affinity = False
        has_weather_affinity = False
        
        for trait in env_traits:
            self.assertEqual(trait.trait_type, 'environmental')
            if 'terrain_affinity' in trait.interaction_effects:
                has_terrain_affinity = True
            if 'weather_affinity' in trait.interaction_effects:
                has_weather_affinity = True
                
        self.assertTrue(has_terrain_affinity, "Should generate traits with terrain affinity")
        self.assertTrue(has_weather_affinity, "Should generate traits with weather affinity")

    def test_environmental_traits_integration(self):
        """Verify environmental traits are in the global list."""
        from src.models.expanded_traits import ALL_CREATURE_TRAITS
        from src.models.environmental_traits import FOREST_DWELLER
        
        # Check if specific environmental traits are present by name
        trait_names = [t.name for t in ALL_CREATURE_TRAITS]
        self.assertIn("Forest Dweller", trait_names)
        self.assertIn("Nocturnal", trait_names)
        self.assertIn("Aquatic", trait_names)

if __name__ == '__main__':
    unittest.main()
