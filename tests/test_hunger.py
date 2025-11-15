"""
Unit tests for hunger and survival system.
"""

import unittest
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.trait import Trait
from src.models.ecosystem_traits import HERBIVORE, CARNIVORE, OMNIVORE


class TestHungerSystem(unittest.TestCase):
    """Test cases for hunger system."""
    
    def test_creature_has_hunger(self):
        """Test that creatures are initialized with hunger."""
        creature = Creature(name="TestCreature")
        self.assertEqual(creature.hunger, 100)
        self.assertEqual(creature.max_hunger, 100)
    
    def test_hunger_depletion(self):
        """Test that hunger depletes over time."""
        creature = Creature(name="TestCreature")
        initial_hunger = creature.hunger
        
        # Simulate 10 seconds passing
        creature.tick_hunger(10.0)
        
        # Hunger should decrease (1.0 per second = 10 hunger lost)
        self.assertLess(creature.hunger, initial_hunger)
        self.assertEqual(creature.hunger, 90)
    
    def test_hunger_minimum_zero(self):
        """Test that hunger can't go below 0."""
        creature = Creature(name="TestCreature", hunger=5)
        
        # Deplete more hunger than available
        creature.tick_hunger(10.0)
        
        self.assertEqual(creature.hunger, 0)
    
    def test_efficient_metabolism_trait(self):
        """Test that Efficient Metabolism slows hunger depletion."""
        normal_creature = Creature(name="Normal")
        efficient_creature = Creature(
            name="Efficient",
            traits=[Trait(name="Efficient Metabolism")]
        )
        
        # Tick both creatures
        normal_creature.tick_hunger(10.0)
        efficient_creature.tick_hunger(10.0)
        
        # Efficient creature should have more hunger remaining
        self.assertGreater(efficient_creature.hunger, normal_creature.hunger)
        # Should lose 60% of normal rate (10 * 0.6 = 6 lost, 94 remaining)
        self.assertEqual(efficient_creature.hunger, 94)
    
    def test_glutton_trait(self):
        """Test that Glutton trait increases hunger depletion."""
        normal_creature = Creature(name="Normal")
        glutton_creature = Creature(
            name="Glutton",
            traits=[Trait(name="Glutton")]
        )
        
        # Tick both creatures
        normal_creature.tick_hunger(10.0)
        glutton_creature.tick_hunger(10.0)
        
        # Glutton creature should have less hunger remaining
        self.assertLess(glutton_creature.hunger, normal_creature.hunger)
        # Should lose 150% of normal rate (10 * 1.5 = 15 lost, 85 remaining)
        self.assertEqual(glutton_creature.hunger, 85)
    
    def test_eating_restores_hunger(self):
        """Test that eating food restores hunger."""
        creature = Creature(name="TestCreature", hunger=50)
        
        hunger_restored = creature.eat(40)
        
        self.assertEqual(creature.hunger, 90)
        self.assertEqual(hunger_restored, 40)
    
    def test_eating_caps_at_max_hunger(self):
        """Test that eating can't exceed max hunger."""
        creature = Creature(name="TestCreature", hunger=80)
        
        hunger_restored = creature.eat(40)
        
        self.assertEqual(creature.hunger, 100)
        self.assertEqual(hunger_restored, 20)  # Only restored 20
    
    def test_voracious_trait_healing_bonus(self):
        """Test that Voracious trait provides HP bonus when eating."""
        creature = Creature(
            name="Voracious",
            traits=[Trait(name="Voracious")]
        )
        # Damage the creature first
        creature.stats.take_damage(20)
        initial_hp = creature.stats.hp
        
        creature.eat(40)
        
        # Should have gained some HP (40 / 10 = 4 HP)
        self.assertGreater(creature.stats.hp, initial_hp)
    
    def test_starvation_death(self):
        """Test that creatures die when hunger reaches 0."""
        creature = Creature(name="TestCreature", hunger=5)
        
        self.assertTrue(creature.is_alive())
        
        # Deplete all hunger
        creature.tick_hunger(10.0)
        
        self.assertEqual(creature.hunger, 0)
        self.assertFalse(creature.is_alive())
    
    def test_hunger_serialization(self):
        """Test that hunger is properly serialized."""
        creature = Creature(name="TestCreature", hunger=75, max_hunger=100)
        
        data = creature.to_dict()
        
        self.assertEqual(data['hunger'], 75)
        self.assertEqual(data['max_hunger'], 100)
        
        # Test deserialization
        restored = Creature.from_dict(data)
        self.assertEqual(restored.hunger, 75)
        self.assertEqual(restored.max_hunger, 100)


class TestDietaryTraits(unittest.TestCase):
    """Test cases for dietary traits system."""
    
    def test_herbivore_can_eat_plants(self):
        """Test that herbivores can eat plant resources."""
        herbivore = Creature(
            name="Herbivore",
            traits=[HERBIVORE],
            hunger=50
        )
        
        hunger_restored = herbivore.eat(40, food_type="plant")
        
        self.assertEqual(hunger_restored, 40)
        self.assertEqual(herbivore.hunger, 90)
    
    def test_herbivore_cannot_eat_creatures(self):
        """Test that herbivores cannot eat other creatures."""
        herbivore = Creature(
            name="Herbivore",
            traits=[HERBIVORE],
            hunger=50
        )
        
        hunger_restored = herbivore.eat(50, food_type="creature")
        
        self.assertEqual(hunger_restored, 0)
        self.assertEqual(herbivore.hunger, 50)  # Unchanged
    
    def test_carnivore_can_eat_creatures(self):
        """Test that carnivores can eat other creatures."""
        carnivore = Creature(
            name="Carnivore",
            traits=[CARNIVORE],
            hunger=50
        )
        
        hunger_restored = carnivore.eat(50, food_type="creature")
        
        self.assertEqual(hunger_restored, 50)
        self.assertEqual(carnivore.hunger, 100)
    
    def test_carnivore_cannot_eat_plants(self):
        """Test that carnivores cannot eat plant resources."""
        carnivore = Creature(
            name="Carnivore",
            traits=[CARNIVORE],
            hunger=50
        )
        
        hunger_restored = carnivore.eat(40, food_type="plant")
        
        self.assertEqual(hunger_restored, 0)
        self.assertEqual(carnivore.hunger, 50)  # Unchanged
    
    def test_carnivore_has_attack_bonus(self):
        """Test that carnivores have increased attack stats."""
        normal = Creature(name="Normal", level=5)
        carnivore = Creature(
            name="Carnivore",
            traits=[CARNIVORE],  # Use predefined CARNIVORE trait with 1.2 modifier
            level=5
        )
        
        # Carnivore should have 20% more attack
        self.assertGreater(carnivore.stats.attack, normal.stats.attack)
    
    def test_omnivore_can_eat_plants(self):
        """Test that omnivores can eat plant resources."""
        omnivore = Creature(
            name="Omnivore",
            traits=[OMNIVORE],
            hunger=50
        )
        
        hunger_restored = omnivore.eat(40, food_type="plant")
        
        self.assertEqual(hunger_restored, 40)
        self.assertEqual(omnivore.hunger, 90)
    
    def test_omnivore_can_eat_creatures(self):
        """Test that omnivores can eat other creatures."""
        omnivore = Creature(
            name="Omnivore",
            traits=[OMNIVORE],
            hunger=50
        )
        
        hunger_restored = omnivore.eat(50, food_type="creature")
        
        self.assertEqual(hunger_restored, 50)
        self.assertEqual(omnivore.hunger, 100)
    
    def test_no_dietary_trait_can_eat_both(self):
        """Test that creatures without dietary traits can eat both food types."""
        creature = Creature(name="Normal", hunger=50)
        
        # Can eat plants
        hunger_restored_plant = creature.eat(20, food_type="plant")
        self.assertEqual(hunger_restored_plant, 20)
        self.assertEqual(creature.hunger, 70)
        
        # Can eat creatures
        hunger_restored_creature = creature.eat(25, food_type="creature")
        self.assertEqual(hunger_restored_creature, 25)
        self.assertEqual(creature.hunger, 95)
    
    def test_can_eat_food_type_method_herbivore(self):
        """Test can_eat_food_type method for herbivores."""
        herbivore = Creature(
            name="Herbivore",
            traits=[HERBIVORE]
        )
        
        self.assertTrue(herbivore.can_eat_food_type("plant"))
        self.assertFalse(herbivore.can_eat_food_type("creature"))
    
    def test_can_eat_food_type_method_carnivore(self):
        """Test can_eat_food_type method for carnivores."""
        carnivore = Creature(
            name="Carnivore",
            traits=[CARNIVORE]
        )
        
        self.assertFalse(carnivore.can_eat_food_type("plant"))
        self.assertTrue(carnivore.can_eat_food_type("creature"))
    
    def test_can_eat_food_type_method_omnivore(self):
        """Test can_eat_food_type method for omnivores."""
        omnivore = Creature(
            name="Omnivore",
            traits=[OMNIVORE]
        )
        
        self.assertTrue(omnivore.can_eat_food_type("plant"))
        self.assertTrue(omnivore.can_eat_food_type("creature"))


if __name__ == '__main__':
    unittest.main()
