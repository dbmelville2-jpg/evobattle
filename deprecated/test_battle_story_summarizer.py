"""
Tests for the Battle Story Summarizer system.
"""

import unittest
import time
import os
import tempfile
from src.systems.battle_story_summarizer import (
    BattleStoryGenerator, BattleStoryTracker, StoryTone, BattleStoryMetrics
)
from src.systems.battle_spatial import BattleEvent, BattleEventType


class MockBattleEvent:
    """Mock battle event for testing."""
    
    def __init__(self, event_type_str, message="", value=None):
        self.event_type = type('EventType', (), {'value': event_type_str})()
        self.message = message
        self.value = value


class TestBattleStoryGenerator(unittest.TestCase):
    """Test cases for BattleStoryGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = BattleStoryGenerator(default_tone=StoryTone.DRAMATIC)
    
    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.default_tone, StoryTone.DRAMATIC)
        self.assertEqual(len(self.generator.collected_events), 0)
        self.assertEqual(len(self.generator.battle_logs), 0)
        self.assertIsNone(self.generator.start_time)
    
    def test_start_collection(self):
        """Test starting event collection."""
        # Add some data
        self.generator.collected_events = [1, 2, 3]
        self.generator.battle_logs = ["log1", "log2"]
        
        # Start collection should reset
        self.generator.start_collection()
        
        self.assertEqual(len(self.generator.collected_events), 0)
        self.assertEqual(len(self.generator.battle_logs), 0)
        self.assertIsNotNone(self.generator.start_time)
    
    def test_add_event(self):
        """Test adding battle events."""
        self.generator.start_collection()
        
        # Add attack event
        event = MockBattleEvent('ability_use', 'Creature attacks')
        self.generator.add_event(event)
        
        self.assertEqual(len(self.generator.collected_events), 1)
        self.assertEqual(self.generator.metrics.total_attacks, 1)
    
    def test_add_damage_event(self):
        """Test adding damage events."""
        self.generator.start_collection()
        
        # Add damage event
        event = MockBattleEvent('damage_dealt', 'Damage dealt', value=50)
        self.generator.add_event(event)
        
        self.assertEqual(self.generator.metrics.total_damage_dealt, 50.0)
    
    def test_add_kill_event(self):
        """Test adding kill events."""
        self.generator.start_collection()
        
        # Add death event
        event = MockBattleEvent('creature_death', 'Creature defeated')
        self.generator.add_event(event)
        
        self.assertEqual(self.generator.metrics.total_kills, 1)
        self.assertIn('Creature defeated', self.generator.metrics.dramatic_events)
    
    def test_add_birth_event(self):
        """Test adding birth events."""
        self.generator.start_collection()
        
        # Add birth event
        event = MockBattleEvent('creature_birth', 'New creature born')
        self.generator.add_event(event)
        
        self.assertEqual(self.generator.metrics.total_births, 1)
        self.assertIn('New creature born', self.generator.metrics.key_moments)
    
    def test_add_log(self):
        """Test adding battle logs."""
        self.generator.start_collection()
        
        self.generator.add_log("Battle started")
        self.generator.add_log("Creature attacks enemy")
        
        self.assertEqual(len(self.generator.battle_logs), 2)
        self.assertIn("Battle started", self.generator.battle_logs)
    
    def test_extract_metrics_from_logs(self):
        """Test metric extraction from logs."""
        self.generator.start_collection()
        
        # Add logs with keywords
        self.generator.add_log("Epic comeback by warrior")
        self.generator.add_log("Betrayal in the arena")
        self.generator.add_log("Last survivor standing")
        
        time.sleep(0.1)  # Small delay to measure duration
        metrics = self.generator._extract_metrics_from_logs()
        
        self.assertGreater(metrics.duration_seconds, 0)
        self.assertTrue(len(metrics.key_moments) > 0)
    
    def test_generate_fallback_story(self):
        """Test story generation using local processing."""
        self.generator.start_collection()
        
        # Add some events and logs
        self.generator.add_event(MockBattleEvent('ability_use', 'Attack'))
        self.generator.add_event(MockBattleEvent('damage_dealt', 'Damage', value=100))
        self.generator.add_event(MockBattleEvent('creature_death', 'Defeated'))
        self.generator.add_log("Battle commenced")
        self.generator.add_log("Fierce combat ensued")
        
        # Generate story
        story = self.generator.generate_story(tone=StoryTone.DRAMATIC)
        
        self.assertIsInstance(story, str)
        self.assertGreater(len(story), 0)
        self.assertIn("Battle Summary", story)
        # Check for key content
        self.assertIn("attacks", story.lower())
        self.assertIn("damage", story.lower())
    
    def test_generate_story_different_tones(self):
        """Test story generation with different tones."""
        self.generator.start_collection()
        
        # Add some events
        for i in range(5):
            self.generator.add_event(MockBattleEvent('ability_use', f'Attack {i}'))
        
        # Test each tone
        for tone in StoryTone:
            story = self.generator.generate_story(tone=tone)
            self.assertIsInstance(story, str)
            self.assertGreater(len(story), 0)
    
    def test_export_story_txt(self):
        """Test exporting story to text file."""
        story = "This is a test battle story."
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_story.txt")
            self.generator.export_story(story, filepath, format='txt')
            
            self.assertTrue(os.path.exists(filepath))
            
            with open(filepath, 'r') as f:
                content = f.read()
                self.assertEqual(content, story)
    
    def test_export_story_markdown(self):
        """Test exporting story to markdown file."""
        story = "This is a test battle story."
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_story.md")
            self.generator.export_story(story, filepath, format='md')
            
            self.assertTrue(os.path.exists(filepath))
            
            with open(filepath, 'r') as f:
                content = f.read()
                self.assertIn("# Battle Story", content)
                self.assertIn(story, content)


class TestBattleStoryTracker(unittest.TestCase):
    """Test cases for BattleStoryTracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = BattleStoryGenerator()
        self.tracker = BattleStoryTracker(
            generator=self.generator,
            story_interval_seconds=1.0  # Short interval for testing
        )
    
    def test_initialization(self):
        """Test tracker initialization."""
        self.assertEqual(self.tracker.story_interval, 1.0)
        self.assertFalse(self.tracker.is_tracking)
        self.assertEqual(len(self.tracker.stories), 0)
    
    def test_start_tracking(self):
        """Test starting tracking."""
        self.tracker.start_tracking()
        
        self.assertTrue(self.tracker.is_tracking)
        self.assertGreater(self.tracker.last_story_time, 0)
    
    def test_stop_tracking(self):
        """Test stopping tracking."""
        self.tracker.start_tracking()
        self.tracker.stop_tracking()
        
        self.assertFalse(self.tracker.is_tracking)
    
    def test_should_generate_story(self):
        """Test story generation timing."""
        # Not tracking yet
        self.assertFalse(self.tracker.should_generate_story())
        
        # Start tracking
        self.tracker.start_tracking()
        self.assertFalse(self.tracker.should_generate_story())
        
        # Wait for interval
        time.sleep(1.1)
        self.assertTrue(self.tracker.should_generate_story())
    
    def test_generate_and_store_story(self):
        """Test generating and storing stories."""
        self.tracker.start_tracking()
        
        # Add some events
        self.generator.add_event(MockBattleEvent('ability_use', 'Attack'))
        self.generator.add_log("Battle started")
        
        # Generate story
        story = self.tracker.generate_and_store_story(tone=StoryTone.HEROIC)
        
        self.assertIsInstance(story, str)
        self.assertEqual(len(self.tracker.stories), 1)
        self.assertEqual(self.tracker.stories[0]['tone'], StoryTone.HEROIC)
    
    def test_get_all_stories(self):
        """Test retrieving all stories."""
        self.tracker.start_tracking()
        
        # Generate multiple stories
        self.tracker.generate_and_store_story(tone=StoryTone.DRAMATIC)
        self.tracker.generate_and_store_story(tone=StoryTone.COMEDIC)
        
        stories = self.tracker.get_all_stories()
        self.assertEqual(len(stories), 2)
    
    def test_export_all_stories(self):
        """Test exporting all stories."""
        self.tracker.start_tracking()
        
        # Generate stories
        self.tracker.generate_and_store_story(tone=StoryTone.DRAMATIC)
        self.tracker.generate_and_store_story(tone=StoryTone.HEROIC)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            self.tracker.export_all_stories(tmpdir, format='txt')
            
            # Check files exist
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "battle_story_1.txt")))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "battle_story_2.txt")))


class TestBattleStoryMetrics(unittest.TestCase):
    """Test cases for BattleStoryMetrics."""
    
    def test_initialization(self):
        """Test metrics initialization."""
        metrics = BattleStoryMetrics()
        
        self.assertEqual(metrics.duration_seconds, 0.0)
        self.assertEqual(metrics.total_attacks, 0)
        self.assertEqual(metrics.total_kills, 0)
        self.assertEqual(metrics.total_births, 0)
        self.assertEqual(len(metrics.key_moments), 0)
        self.assertEqual(len(metrics.mvp_creatures), 0)


if __name__ == '__main__':
    unittest.main()
