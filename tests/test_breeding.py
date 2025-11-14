"""
Unit tests for enhanced Breeding system.
"""

import unittest
from src.systems.breeding import Breeding
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.trait import Trait


class TestBreeding(unittest.TestCase):
    """Test cases for Breeding class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.breeding = Breeding(mutation_rate=0.1, trait_inheritance_chance=0.8)
        
        # Create parent creatures
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        self.parent1 = Creature(
            name="Parent1",
            creature_type=warrior_type,
            mature=True,
            hue=120.0
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
            mature=True,
            hue=180.0
        )
        self.parent2.add_trait(Trait(
            name="Fast",
            description="Extra speed",
            trait_type="physical",
            speed_modifier=1.2
        ))
    
    def test_breeding_initialization(self):
        """Test breeding system initialization."""
        self.assertEqual(self.breeding.mutation_rate, 0.1)
        self.assertEqual(self.breeding.trait_inheritance_chance, 0.8)
    
    def test_breed_creates_offspring(self):
        """Test that breeding creates a valid offspring."""
        offspring = self.breeding.breed(self.parent1, self.parent2)
        
        self.assertIsNotNone(offspring)
        self.assertIsInstance(offspring, Creature)
        self.assertEqual(offspring.level, 1)
        self.assertFalse(offspring.mature)
    
    def test_breed_tracks_parents(self):
        """Test that offspring tracks parent IDs."""
        offspring = self.breeding.breed(self.parent1, self.parent2)
        
        self.assertEqual(len(offspring.parent_ids), 2)
        self.assertIn(self.parent1.creature_id, offspring.parent_ids)
        self.assertIn(self.parent2.creature_id, offspring.parent_ids)
    
    def test_breed_inherits_hue(self):
        """Test that offspring inherits hue from parents."""
        offspring = self.breeding.breed(self.parent1, self.parent2)
        
        # Hue should be roughly average of parents (120 + 180)/2 = 150
        # With mutation of -15 to +15, should be in range 135-165
        self.assertGreaterEqual(offspring.hue, 135)
        self.assertLessEqual(offspring.hue, 165)
    
    def test_breed_fails_without_maturity(self):
        """Test that immature creatures cannot breed."""
        self.parent1.mature = False
        offspring = self.breeding.breed(self.parent1, self.parent2)
        
        self.assertIsNone(offspring)
    
    def test_breed_fails_with_low_health(self):
        """Test that unhealthy creatures cannot breed."""
        self.parent1.stats.hp = self.parent1.stats.max_hp * 0.3
        offspring = self.breeding.breed(self.parent1, self.parent2)
        
        self.assertIsNone(offspring)
    
    def test_inherit_stats(self):
        """Test stat inheritance."""
        offspring = self.breeding.breed(self.parent1, self.parent2)
        
        # Stats should be roughly average of parents
        # Parent stats are: max_hp=100, attack=15, defense=10, speed=12
        # With 10% variation, offspring stats should be in reasonable range
        self.assertGreaterEqual(offspring.base_stats.max_hp, 80)
        self.assertLessEqual(offspring.base_stats.max_hp, 120)
        
        self.assertGreaterEqual(offspring.base_stats.attack, 10)
        self.assertLessEqual(offspring.base_stats.attack, 20)
    
    def test_trait_inheritance(self):
        """Test that offspring can inherit traits from parents."""
        # Run multiple breeding attempts to test probabilistic inheritance
        offspring_list = []
        for _ in range(10):
            offspring = self.breeding.breed(self.parent1, self.parent2)
            if offspring:
                offspring_list.append(offspring)
        
        # At least some offspring should have inherited traits
        # (with 70-90% inheritance chance per trait)
        has_traits = any(len(o.traits) > 0 for o in offspring_list)
        self.assertTrue(has_traits)
    
    def test_calculate_inherited_traits(self):
        """Test trait calculation."""
        # This is probabilistic, so we test the method exists and returns a list
        traits = self.breeding.calculate_inherited_traits(self.parent1, self.parent2)
        self.assertIsInstance(traits, list)
    
    def test_apply_mutation(self):
        """Test trait mutation."""
        original_trait = Trait(
            name="TestTrait",
            description="Test",
            trait_type="physical",
            strength_modifier=1.0
        )
        
        mutated = self.breeding.apply_mutation(original_trait)
        
        # Mutated trait should have different modifiers
        # Note: mutation changes stats by ~10%, so check they're different
        self.assertNotEqual(mutated.strength_modifier, 1.0)
        self.assertTrue(mutated.name.endswith('+'))


if __name__ == '__main__':
    unittest.main()
