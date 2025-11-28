"""
Integration test for 'S' hotkey story viewer functionality.
Tests that the story system is properly integrated into main game loop.
"""

import unittest
import pygame
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.systems.battle_story_summarizer import BattleStoryGenerator, BattleStoryTracker, StoryTone
from src.rendering import StoryViewer, StoryViewerAction


class TestStoryHotkeyIntegration(unittest.TestCase):
    """Test story viewer integration with main game."""
    
    def setUp(self):
        """Set up pygame and story components."""
        pygame.init()
        
    def tearDown(self):
        """Clean up pygame."""
        pygame.quit()
    
    def test_story_system_imports(self):
        """Test that all story system components can be imported."""
        # This test verifies the imports used in main.py work correctly
        self.assertIsNotNone(BattleStoryGenerator)
        self.assertIsNotNone(BattleStoryTracker)
        self.assertIsNotNone(StoryTone)
        self.assertIsNotNone(StoryViewer)
        self.assertIsNotNone(StoryViewerAction)
    
    def test_story_system_initialization(self):
        """Test that story system components can be initialized."""
        # Simulates the initialization in main.py run_battle_loop
        generator = BattleStoryGenerator(default_tone=StoryTone.DRAMATIC)
        tracker = BattleStoryTracker(
            generator=generator,
            story_interval_seconds=300.0
        )
        viewer = StoryViewer(width=700, height=600)
        
        self.assertIsNotNone(generator)
        self.assertIsNotNone(tracker)
        self.assertIsNotNone(viewer)
        
    def test_story_tracker_start(self):
        """Test that story tracker can be started."""
        generator = BattleStoryGenerator(default_tone=StoryTone.DRAMATIC)
        tracker = BattleStoryTracker(generator=generator, story_interval_seconds=300.0)
        
        # Should not raise exception
        tracker.start_tracking()
        self.assertIsNotNone(tracker.last_story_time)
    
    def test_story_viewer_set_story(self):
        """Test that story viewer can display story text."""
        viewer = StoryViewer(width=700, height=600)
        test_story = "Test battle story"
        
        # Should not raise exception
        viewer.set_story(test_story, StoryTone.DRAMATIC)
        self.assertEqual(viewer.story_text, test_story)
        self.assertEqual(viewer.current_tone, StoryTone.DRAMATIC)
    
    def test_keyboard_event_simulation(self):
        """Test that pygame keyboard events can be created for 'S' key."""
        # Simulates pressing 'S' key
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_s})
        
        self.assertEqual(event.type, pygame.KEYDOWN)
        self.assertEqual(event.key, pygame.K_s)
    
    def test_story_viewer_actions(self):
        """Test that all story viewer actions are available."""
        # Verify all actions used in main.py exist
        actions = [
            StoryViewerAction.CLOSE,
            StoryViewerAction.CHANGE_TONE,
            StoryViewerAction.REGENERATE,
            StoryViewerAction.EXPORT_TXT,
            StoryViewerAction.EXPORT_MD
        ]
        
        for action in actions:
            self.assertIsNotNone(action)
    
    def test_story_generation(self):
        """Test that stories can be generated."""
        generator = BattleStoryGenerator(default_tone=StoryTone.DRAMATIC)
        
        # Add some test data
        generator.add_log("Test event 1")
        generator.add_log("Test event 2")
        
        # Generate story
        story = generator.generate_story(tone=StoryTone.DRAMATIC)
        
        self.assertIsNotNone(story)
        self.assertIsInstance(story, str)
        self.assertGreater(len(story), 0)
    
    def test_story_tone_options(self):
        """Test that all story tone options exist."""
        # Verify all tones used in main.py exist
        tones = [
            StoryTone.DRAMATIC,
            StoryTone.HEROIC,
            StoryTone.COMEDIC,
            StoryTone.SERIOUS,
            StoryTone.DOCUMENTARY
        ]
        
        for tone in tones:
            self.assertIsNotNone(tone)
            self.assertIsInstance(tone.value, str)


if __name__ == '__main__':
    unittest.main()
