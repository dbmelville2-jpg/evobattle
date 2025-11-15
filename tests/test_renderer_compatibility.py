"""
Unit tests for renderer compatibility with SpatialBattle.

Tests that the team-based SpatialBattle provides the necessary API
for renderers that expect individual-based creature access.
"""

import unittest
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

try:
    import pygame
    pygame.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from src.systems.battle_spatial import SpatialBattle
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats


class TestRendererCompatibility(unittest.TestCase):
    """Test cases for renderer compatibility with SpatialBattle."""
    
    def setUp(self):
        """Set up test fixtures."""
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        self.team1 = [
            Creature(name="Player1", creature_type=warrior_type),
            Creature(name="Player2", creature_type=warrior_type)
        ]
        
        self.team2 = [
            Creature(name="Enemy1", creature_type=warrior_type),
            Creature(name="Enemy2", creature_type=warrior_type),
            Creature(name="Enemy3", creature_type=warrior_type)
        ]
    
    def test_creatures_property_exists(self):
        """Test that SpatialBattle has a creatures property."""
        battle = SpatialBattle(
            self.team1,
            self.team2,
            arena_width=100,
            arena_height=100
        )
        
        # Should not raise AttributeError
        self.assertTrue(hasattr(battle, 'creatures'))
    
    def test_creatures_property_returns_all_creatures(self):
        """Test that creatures property returns all creatures from both teams."""
        battle = SpatialBattle(
            self.team1,
            self.team2,
            arena_width=100,
            arena_height=100
        )
        
        # Should return all creatures
        all_creatures = battle.creatures
        self.assertEqual(len(all_creatures), 5)  # 2 + 3
        
        # Should contain both teams
        self.assertEqual(len(battle.player_creatures), 2)
        self.assertEqual(len(battle.enemy_creatures), 3)
    
    def test_creatures_property_is_iterable(self):
        """Test that creatures property can be iterated over."""
        battle = SpatialBattle(
            self.team1,
            self.team2,
            arena_width=100,
            arena_height=100
        )
        
        # Should be able to iterate
        count = 0
        for creature in battle.creatures:
            count += 1
            self.assertTrue(creature.is_alive())
        
        self.assertEqual(count, 5)
    
    def test_renderer_access_pattern(self):
        """Test the typical renderer access pattern."""
        battle = SpatialBattle(
            self.team1,
            self.team2,
            arena_width=100,
            arena_height=100
        )
        
        # Simulate what creature_renderer.py does (line 60)
        alive_creatures = []
        for creature in battle.creatures:
            if creature.is_alive():
                alive_creatures.append(creature)
        
        self.assertEqual(len(alive_creatures), 5)
    
    @unittest.skipUnless(PYGAME_AVAILABLE, "pygame not installed")
    def test_creature_renderer_integration(self):
        """Test that CreatureRenderer can render without errors."""
        from src.rendering.creature_renderer import CreatureRenderer
        
        battle = SpatialBattle(
            self.team1,
            self.team2,
            arena_width=100,
            arena_height=100
        )
        
        renderer = CreatureRenderer()
        screen = pygame.Surface((800, 600))
        
        # Should not raise AttributeError
        try:
            renderer.render(screen, battle)
        except AttributeError as e:
            self.fail(f"CreatureRenderer raised AttributeError: {e}")
    
    @unittest.skipUnless(PYGAME_AVAILABLE, "pygame not installed")
    def test_ui_components_helper_methods(self):
        """Test that UIComponents helper methods work."""
        from src.rendering.ui_components import UIComponents
        
        battle = SpatialBattle(
            self.team1,
            self.team2,
            arena_width=100,
            arena_height=100
        )
        
        ui = UIComponents()
        screen = pygame.Surface((1200, 800))
        
        # Test helper methods
        try:
            ui.draw_battle_timer(screen, battle.current_time, (600, 30))
            ui.draw_population_status(screen, 5, 5, (100, 30))
        except AttributeError as e:
            self.fail(f"UIComponents helper method raised AttributeError: {e}")


if __name__ == '__main__':
    unittest.main()
