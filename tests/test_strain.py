"""
Unit tests for genetic strain/lineage system.
"""

import unittest
import random
from src.systems.breeding import Breeding
from src.systems.population import PopulationManager
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.trait import Trait
from src.models.lineage import Lineage
from src.systems.mutation import apply_tradeoff_mutation


class TestStrainInheritance(unittest.TestCase):
    """Test cases for strain inheritance in breeding."""
    
    def setUp(self):
        """Set up test fixtures."""
        # deterministic tests
        random.seed(42)
        self.breeding = Breeding(mutation_rate=0.1)
        
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        # Create parents with same strain
        self.parent1 = Creature(
            name="Parent1",
            creature_type=warrior_type,
            mature=True,
            hue=120.0,
            strain_id="strain_A"
        )
        
        self.parent2 = Creature(
            name="Parent2",
            creature_type=warrior_type,
            mature=True,
            hue=130.0,
            strain_id="strain_A"
        )
        
        # Create parents with different strains
        self.parent3 = Creature(
            name="Parent3",
            creature_type=warrior_type,
            mature=True,
            hue=180.0,
            strain_id="strain_B"
        )
    
    def test_creature_has_strain_id(self):
        """Test that creatures are created with strain_id."""
        creature = Creature(name="Test", mature=True)
        self.assertIsNotNone(creature.strain_id)
        self.assertIsInstance(creature.strain_id, str)
    
    def test_same_strain_parents_inherit_strain(self):
        """Test that offspring from same strain parents usually inherit the strain."""
        # Run multiple times since there's a small mutation chance
        offspring_strains = []
        random.seed(42)
        for _ in range(10):
            offspring = self.breeding.breed(self.parent1, self.parent2)
            if offspring:
                offspring_strains.append(offspring.strain_id)
        
        # Most should inherit parent strain (with small chance of mutation)
        same_strain_count = sum(1 for s in offspring_strains if s == "strain_A")
        self.assertGreater(same_strain_count, 5)  # At least 50% should inherit
    
    def test_different_strain_parents(self):
        """Test that offspring from different strain parents inherit one parent's strain."""
        offspring = self.breeding.breed(self.parent1, self.parent3)
        
        self.assertIsNotNone(offspring)
        self.assertIsNotNone(offspring.strain_id)
        # Should be one of the parent strains
        self.assertIn(offspring.strain_id, ["strain_A", "strain_B"])
    
    def test_strain_serialization(self):
        """Test that strain_id is properly serialized and deserialized."""
        creature = Creature(
            name="Test",
            mature=True,
            strain_id="test_strain"
        )
        
        # Serialize
        data = creature.to_dict()
        self.assertEqual(data['strain_id'], "test_strain")
        
        # Deserialize
        restored = Creature.from_dict(data)
        self.assertEqual(restored.strain_id, "test_strain")


class TestTraitMutation(unittest.TestCase):
    """Test cases for trait mutation system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # deterministic tests
        random.seed(42)
        self.breeding = Breeding(mutation_rate=0.3)  # Higher rate for testing
        
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        self.parent1 = Creature(
            name="Parent1",
            creature_type=warrior_type,
            mature=True
        )
        self.parent1.add_trait(Trait(
            name="Strong",
            description="Extra strength",
            trait_type="physical",
            strength_modifier=1.2
        ))
        
        self.parent2 = Creature(
            name="Parent2",
            creature_type=warrior_type,
            mature=True
        )
        self.parent2.add_trait(Trait(
            name="Fast",
            description="Extra speed",
            trait_type="physical",
            speed_modifier=1.2
        ))
    
    def test_trait_can_be_lost(self):
        """Test that traits can be lost through mutation."""
        # Breed many times and check if any offspring lose traits
        offspring_list = []
        random.seed(123)
        for _ in range(20):
            offspring = self.breeding.breed(self.parent1, self.parent2)
            if offspring:
                offspring_list.append(offspring)
        
        # At least some offspring should have fewer traits than parents due to loss
        parent_trait_names = {"Strong", "Fast"}
        lost_trait_count = 0
        
        for offspring in offspring_list:
            # Use canonical base_name() so display markers don't affect logic
            offspring_trait_names = {t.base_name() for t in offspring.traits}
            
            missing_traits = parent_trait_names - offspring_trait_names
            if missing_traits:
                lost_trait_count += 1
        
        # With high mutation rate, at least some should lose traits
        self.assertGreater(lost_trait_count, 0)
    
    def test_new_trait_can_be_added(self):
        """Test that new traits can be added through mutation."""
        # Breed many times and check if any offspring gain new traits
        offspring_list = []
        random.seed(222)
        for _ in range(30):
            offspring = self.breeding.breed(self.parent1, self.parent2)
            if offspring:
                offspring_list.append(offspring)
        
        # Check if any offspring have traits not in parents
        parent_trait_names = {"Strong", "Fast"}
        new_trait_count = 0
        
        for offspring in offspring_list:
            for trait in offspring.traits:
                base_name = trait.base_name()
                if base_name not in parent_trait_names:
                    new_trait_count += 1
                    break
        
        # With high mutation rate, at least some should gain new traits
        self.assertGreater(new_trait_count, 0)
    
    def test_generate_new_trait(self):
        """Test the generate_new_trait method."""
        new_trait = self.breeding.generate_new_trait()
        
        # Should return a trait
        self.assertIsInstance(new_trait, Trait)
        self.assertIsNotNone(new_trait.name)
    
    def test_tradeoff_mutation_changes_stats(self):
        """Ensure tradeoff mutation increases one stat and decreases another."""
        t = Trait(name="Balance", strength_modifier=1.0, speed_modifier=1.0, defense_modifier=1.0)
        # deterministic mutation
        random.seed(7)
        mutated = apply_tradeoff_mutation(t, mutation_strength=0.2, force_tradeoff=True)

        # At least one modifier should increase and one should decrease
        inc = 0
        dec = 0
        for attr in ('strength_modifier', 'speed_modifier', 'defense_modifier'):
            orig = getattr(t, attr)
            new = getattr(mutated, attr)
            if new > orig:
                inc += 1
            elif new < orig:
                dec += 1

        self.assertGreater(inc, 0)
        self.assertGreater(dec, 0)


class TestLineageModel(unittest.TestCase):
    """Test cases for enhanced Lineage model."""
    
    def test_lineage_with_strain(self):
        """Test creating lineage with strain_id."""
        lineage = Lineage(
            creature_id="creature_1",
            strain_id="strain_A",
            generation=1,
            parent1_id="parent_1",
            parent2_id="parent_2"
        )
        
        self.assertEqual(lineage.creature_id, "creature_1")
        self.assertEqual(lineage.strain_id, "strain_A")
        self.assertEqual(lineage.generation, 1)
    
    def test_lineage_repr_includes_strain(self):
        """Test that lineage string representation includes strain."""
        lineage = Lineage(
            creature_id="creature_1",
            strain_id="strain_A",
            generation=1
        )
        
        repr_str = repr(lineage)
        self.assertIn("strain_A", repr_str)


class TestStrainStatistics(unittest.TestCase):
    """Test cases for strain statistics in PopulationManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pop_manager = PopulationManager()
        
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        # Create creatures in two strains
        for i in range(3):
            creature = Creature(
                name=f"StrainA_{i}",
                creature_type=warrior_type,
                strain_id="strain_A",
                hue=120.0 + i * 5
            )
            self.pop_manager.spawn_creature(creature, log_event=False)
        
        for i in range(2):
            creature = Creature(
                name=f"StrainB_{i}",
                creature_type=warrior_type,
                strain_id="strain_B",
                hue=240.0 + i * 5
            )
            self.pop_manager.spawn_creature(creature, log_event=False)
    
    def test_get_strain_statistics(self):
        """Test getting statistics per strain."""
        stats = self.pop_manager.get_strain_statistics()
        
        # Should have two strains
        self.assertEqual(len(stats), 2)
        self.assertIn("strain_A", stats)
        self.assertIn("strain_B", stats)
        
        # Check strain A stats
        self.assertEqual(stats["strain_A"]["alive"], 3)
        self.assertEqual(stats["strain_A"]["total"], 3)
        self.assertFalse(stats["strain_A"]["extinct"])
        
        # Check strain B stats
        self.assertEqual(stats["strain_B"]["alive"], 2)
        self.assertEqual(stats["strain_B"]["total"], 2)
        self.assertFalse(stats["strain_B"]["extinct"])
    
    def test_strain_average_hue(self):
        """Test that average hue is calculated for strains."""
        stats = self.pop_manager.get_strain_statistics()
        
        # Strain A should have average hue around 125 (120, 125, 130)
        self.assertAlmostEqual(stats["strain_A"]["avg_hue"], 125.0, delta=1.0)
        
        # Strain B should have average hue around 242.5 (240, 245)
        self.assertAlmostEqual(stats["strain_B"]["avg_hue"], 242.5, delta=1.0)
    
    def test_extinct_strain_detection(self):
        """Test detection of extinct strains."""
        # Kill all creatures in strain B
        for creature in self.pop_manager.population:
            if creature.strain_id == "strain_B":
                creature.stats.hp = 0
        
        stats = self.pop_manager.get_strain_statistics()
        
        # Strain B should be marked extinct
        self.assertTrue(stats["strain_B"]["extinct"])
        self.assertEqual(stats["strain_B"]["alive"], 0)
        
        # Strain A should still be alive
        self.assertFalse(stats["strain_A"]["extinct"])
        self.assertEqual(stats["strain_A"]["alive"], 3)
    
    def test_get_dominant_strains(self):
        """Test getting dominant strains by population."""
        dominant = self.pop_manager.get_dominant_strains(top_n=2)
        
        # Should return list of (strain_id, count) tuples
        self.assertEqual(len(dominant), 2)
        
        # First should be strain_A with 3 members
        self.assertEqual(dominant[0][0], "strain_A")
        self.assertEqual(dominant[0][1], 3)
        
        # Second should be strain_B with 2 members
        self.assertEqual(dominant[1][0], "strain_B")
        self.assertEqual(dominant[1][1], 2)
    
    def test_get_extinct_strains(self):
        """Test getting list of extinct strains."""
        # Initially no extinct strains
        extinct = self.pop_manager.get_extinct_strains()
        self.assertEqual(len(extinct), 0)
        
        # Kill all creatures in strain B
        for creature in self.pop_manager.population:
            if creature.strain_id == "strain_B":
                creature.stats.hp = 0
        
        # Now strain B should be extinct
        extinct = self.pop_manager.get_extinct_strains()
        self.assertEqual(len(extinct), 1)
        self.assertIn("strain_B", extinct)


if __name__ == '__main__':
    unittest.main()
