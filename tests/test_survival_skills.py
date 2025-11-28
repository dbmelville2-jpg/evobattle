"""
Tests for survival skills (Foraging and Metabolism).
"""

import unittest
import math
from unittest.mock import MagicMock
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.skills import SkillType
from src.models.pellet import Pellet, PelletTraits
from src.models.spatial import Arena, Vector2D, SpatialHashGrid
from src.systems.battle_managers.resource_manager import ResourceManager
from src.systems.battle_managers.event_manager import EventManager

class TestSurvivalSkills(unittest.TestCase):
    """Test Foraging and Metabolism skills."""
    
    def setUp(self):
        """Set up test environment."""
        self.creature_type = CreatureType(
            name="Survivor",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        self.creature = Creature(name="Test", creature_type=self.creature_type)
        
        # Setup for resource manager tests
        self.arena = Arena(100, 100)
        self.event_manager = EventManager()
        self.creature_grid = SpatialHashGrid(100, 100, 10)
        self.resource_manager = ResourceManager(
            self.arena, 
            self.event_manager, 
            self.creature_grid,
            spawn_rate=0,
            initial_resources=0,
            enable_growth_system=False
        )
        
        # Mock creature spatial
        self.creature.spatial = MagicMock()
        self.creature.spatial.position = Vector2D(50, 50)
        
        # Wrap in a mock BattleCreature as expected by ResourceManager
        self.battle_creature = MagicMock()
        self.battle_creature.creature = self.creature
        self.battle_creature.spatial = self.creature.spatial
        
        # Ensure creature is hungry so it will eat
        self.creature.hunger = 50
    
    def test_metabolism_skill_reduces_hunger_depletion(self):
        """Test that Metabolism skill reduces hunger loss."""
        # Baseline depletion
        self.creature.hunger = 100
        self.creature.tick_hunger(1.0)
        baseline_loss = 100 - self.creature.hunger
        
        # Max out Metabolism skill
        metabolism_skill = self.creature.skills.get_skill(SkillType.METABOLISM)
        metabolism_skill.level = 100
        
        # Test with max skill
        self.creature.hunger = 100
        self.creature.tick_hunger(1.0)
        skilled_loss = 100 - self.creature.hunger
        
        # Should be half the loss (efficiency = 2.0 at level 100)
        self.assertAlmostEqual(skilled_loss, baseline_loss / 2.0, places=2)
    
    def test_foraging_skill_increases_radius(self):
        """Test that Foraging skill allows collecting from further away."""
        # Create a pellet just outside normal range (1.5) but inside skilled range
        # Normal range is 1.5. Max skilled range is 1.5 * 1.5 = 2.25.
        # Let's put a pellet at distance 2.0
        pellet = Pellet(x=52.0, y=50.0) # Distance 2.0
        self.arena.add_pellet(pellet)
        
        # With level 0 skill, should NOT collect
        self.creature.skills.get_skill(SkillType.FORAGING).level = 0
        self.resource_manager.check_pellet_collection(self.battle_creature)
        self.assertEqual(len(self.arena.resources), 1) # Still there
        
        # With level 100 skill, SHOULD collect
        # Level 100 gives +50% radius -> 2.25 range
        self.creature.skills.get_skill(SkillType.FORAGING).level = 100
        self.resource_manager.check_pellet_collection(self.battle_creature)
        self.assertEqual(len(self.arena.resources), 0) # Collected
    
    def test_foraging_skill_gains_xp(self):
        """Test that collecting pellets grants Foraging XP."""
        pellet = Pellet(x=50.0, y=50.0) # Right on top
        self.arena.add_pellet(pellet)
        
        skill = self.creature.skills.get_skill(SkillType.FORAGING)
        initial_xp = skill.experience
        
        self.resource_manager.check_pellet_collection(self.battle_creature)
        
        self.assertGreater(skill.experience, initial_xp)

if __name__ == '__main__':
    unittest.main()
