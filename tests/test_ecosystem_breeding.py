"""
Test breeding in ecosystem/spatial battle simulations.
"""

import unittest
from src.systems.battle_spatial import SpatialBattle
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ecosystem_traits import FORAGER, EFFICIENT_METABOLISM


class TestEcosystemBreeding(unittest.TestCase):
    """Test cases for breeding in ecosystem simulations."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create creature type
        self.creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
    
    def test_offspring_mature_over_time(self):
        """Test that offspring age and eventually mature."""
        # Create a young creature
        creature = Creature(
            name="YoungCreature",
            creature_type=self.creature_type,
            age=0.0,
            mature=False
        )
        
        # Age should start at 0
        self.assertEqual(creature.age, 0.0)
        self.assertFalse(creature.mature)
        
        # Tick age to near maturity
        creature.tick_age(19.0)
        self.assertFalse(creature.mature)
        
        # Tick age to maturity (default is 20 seconds)
        creature.tick_age(1.5)
        self.assertTrue(creature.mature)
        self.assertGreaterEqual(creature.age, 20.0)
    
    def test_breeding_in_spatial_battle(self):
        """Test that breeding occurs in spatial battle with mature, healthy creatures."""
        # Create multiple mature creatures with good health and hunger
        # More creatures increase the chance that some will be close enough to breed
        creatures = []
        for i in range(4):
            creature = Creature(
                name=f"Founder{i}",
                creature_type=self.creature_type,
                mature=True,
                traits=[FORAGER, EFFICIENT_METABOLISM]
            )
            # Ensure full health and high hunger
            creature.stats.hp = creature.stats.max_hp
            creature.hunger = 100
            creatures.append(creature)
        
        # Create battle with high resource spawn rate
        battle = SpatialBattle(
            creatures,
            arena_width=50.0,
            arena_height=50.0,
            resource_spawn_rate=1.0,
            initial_resources=20
        )
        
        # Track initial population
        initial_population = len(battle.creatures)
        
        # Run simulation for enough time to allow breeding
        # Breeding cooldown is 5 seconds, so run for 30 seconds to get multiple checks
        for _ in range(300):  # 30 seconds at 0.1s per step
            battle.update(0.1)
            if battle.is_over:
                break
        
        # Check that offspring were born
        final_population = len(battle.creatures)
        self.assertGreater(battle.birth_count, 0, "No offspring were born during simulation")
        self.assertGreater(final_population, initial_population, "Population did not increase")
    
    def test_tick_age_called_in_battle_update(self):
        """Test that creatures age during battle updates."""
        # Create two young creatures (battle needs at least 2 to continue)
        creatures = []
        for i in range(2):
            creature = Creature(
                name=f"TestCreature{i}",
                creature_type=self.creature_type,
                age=0.0,
                mature=False,
                hunger=100
            )
            creature.stats.hp = creature.stats.max_hp
            creatures.append(creature)
        
        # Create battle with these creatures
        battle = SpatialBattle(
            creatures,
            arena_width=50.0,
            arena_height=50.0,
            resource_spawn_rate=1.0,
            initial_resources=10
        )
        
        # Update battle for some time
        for _ in range(100):  # 10 seconds at 0.1s per step
            battle.update(0.1)
        
        # Check that creatures aged
        for creature in creatures:
            self.assertGreater(creature.age, 0, "Creature did not age during battle updates")
            self.assertGreater(creature.age, 5.0, "Creature age is too low")
    
    def test_breeding_hunger_threshold(self):
        """Test that breeding only occurs when creatures have sufficient hunger."""
        creature = Creature(
            name="TestCreature",
            creature_type=self.creature_type,
            mature=True
        )
        creature.stats.hp = creature.stats.max_hp
        
        # Test with low hunger
        creature.hunger = 50
        self.assertFalse(creature.can_breed(), "Creature should not breed with low hunger")
        
        # Test with sufficient hunger (threshold is 70)
        creature.hunger = 75
        self.assertTrue(creature.can_breed(), "Creature should breed with sufficient hunger")
        
        # Test at threshold
        creature.hunger = 70
        self.assertFalse(creature.can_breed(), "Creature should not breed at exact threshold")
        
        creature.hunger = 71
        self.assertTrue(creature.can_breed(), "Creature should breed just above threshold")


if __name__ == '__main__':
    unittest.main()
