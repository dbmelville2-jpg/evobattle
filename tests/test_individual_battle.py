"""
Unit tests for individual-based battle system.
"""

import unittest
from src.systems.battle import SpatialBattle, BattleCreature, BattleEventType
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.spatial import Vector2D


class TestIndividualBattle(unittest.TestCase):
    """Test cases for individual-based (non-team) battles."""
    
    def setUp(self):
        """Set up test fixtures."""
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        self.creatures = [
            Creature(name="Fighter1", creature_type=warrior_type, hue=0),
            Creature(name="Fighter2", creature_type=warrior_type, hue=120),
            Creature(name="Fighter3", creature_type=warrior_type, hue=240)
        ]
    
    def test_battle_initialization(self):
        """Test creating an individual-based battle."""
        battle = SpatialBattle(self.creatures, arena_width=100, arena_height=100)
        
        self.assertEqual(len(battle.creatures), 3)
        self.assertFalse(battle.is_over)
    
    def test_battle_spawning(self):
        """Test that creatures spawn in arena."""
        battle = SpatialBattle(self.creatures, arena_width=100, arena_height=100)
        
        for battle_creature in battle.creatures:
            # Check creature has position
            self.assertIsNotNone(battle_creature.spatial.position)
            # Check creature is within arena
            self.assertGreaterEqual(battle_creature.spatial.position.x, 0)
            self.assertLessEqual(battle_creature.spatial.position.x, 100)
            self.assertGreaterEqual(battle_creature.spatial.position.y, 0)
            self.assertLessEqual(battle_creature.spatial.position.y, 100)
    
    def test_battle_no_teams(self):
        """Test that creatures work without team assignments."""
        battle = SpatialBattle(self.creatures, arena_width=100, arena_height=100)
        
        # Battle should work without team concept
        self.assertEqual(len(battle.creatures), 3)
        
        # All creatures should be in the flat list
        for battle_creature in battle.creatures:
            self.assertIsNotNone(battle_creature.creature)
    
    def test_battle_hsv_colors(self):
        """Test that creatures use HSV colors."""
        battle = SpatialBattle(self.creatures, arena_width=100, arena_height=100)
        
        for battle_creature in battle.creatures:
            # Check creature can generate display color
            color = battle_creature.creature.get_display_color()
            self.assertEqual(len(color), 3)
            self.assertTrue(all(0 <= c <= 255 for c in color))
    
    def test_battle_update(self):
        """Test battle update mechanics."""
        battle = SpatialBattle(self.creatures, arena_width=100, arena_height=100)
        
        # Update battle
        battle.update(0.1)
        
        # Check time advanced
        self.assertGreater(battle.current_time, 0)
    
    def test_battle_ends_with_one_survivor(self):
        """Test battle ends when only one creature remains."""
        battle = SpatialBattle(self.creatures, arena_width=100, arena_height=100)
        
        # Kill two creatures
        battle.creatures[1].creature.stats.hp = 0
        battle.creatures[2].creature.stats.hp = 0
        
        # Update battle
        battle.update(0.1)
        
        # Battle should end
        self.assertTrue(battle.is_over)
    
    def test_battle_simulate(self):
        """Test battle simulation."""
        battle = SpatialBattle(self.creatures, arena_width=100, arena_height=100)
        
        # Simulate battle
        winner = battle.simulate(duration=5.0, time_step=0.1)
        
        # Should have a result (winner or None)
        self.assertIsInstance(winner, (Creature, type(None)))
    
    def test_get_all_creatures(self):
        """Test getting all creatures."""
        battle = SpatialBattle(self.creatures, arena_width=100, arena_height=100)
        
        all_creatures = battle.get_all_creatures()
        self.assertEqual(len(all_creatures), 3)
    
    def test_state_snapshot(self):
        """Test state snapshot for visualization."""
        battle = SpatialBattle(self.creatures, arena_width=100, arena_height=100)
        
        snapshot = battle.get_state_snapshot()
        
        self.assertIn('creatures', snapshot)
        self.assertEqual(len(snapshot['creatures']), 3)
        self.assertIn('time', snapshot)
        self.assertIn('is_over', snapshot)
        
        # Check creature data includes color
        for creature_data in snapshot['creatures']:
            self.assertIn('color', creature_data)
            self.assertIn('name', creature_data)
            self.assertIn('hp', creature_data)
            self.assertIn('position', creature_data)


class TestBattleCreature(unittest.TestCase):
    """Test cases for BattleCreature wrapper."""
    
    def test_battle_creature_no_team(self):
        """Test BattleCreature without team."""
        creature = Creature(name="Test")
        position = Vector2D(50, 50)
        
        battle_creature = BattleCreature(creature, position)
        
        self.assertEqual(battle_creature.creature.name, "Test")
        self.assertEqual(battle_creature.spatial.position.x, 50)
        self.assertEqual(battle_creature.spatial.position.y, 50)
        # Battle creatures now work without team attribute
        self.assertIsNotNone(battle_creature.creature)


if __name__ == '__main__':
    unittest.main()
