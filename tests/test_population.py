"""
Unit tests for Population Management System.
"""

import unittest
import time
from src.systems.population import (
    EventType, PopulationEvent, EventLogger,
    PopulationAnalytics, PopulationManager, EcosystemConfig
)
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats


class TestPopulationEvent(unittest.TestCase):
    """Test cases for PopulationEvent class."""
    
    def test_event_initialization(self):
        """Test creating a population event."""
        event = PopulationEvent(EventType.BIRTH, "creature_123")
        
        self.assertEqual(event.event_type, EventType.BIRTH)
        self.assertEqual(event.creature_id, "creature_123")
        self.assertIsNotNone(event.timestamp)
        self.assertEqual(event.details, {})
    
    def test_event_with_details(self):
        """Test event with additional details."""
        event = PopulationEvent(
            EventType.BREEDING,
            "creature_456",
            details={'parents': ['p1', 'p2']}
        )
        
        self.assertEqual(event.details['parents'], ['p1', 'p2'])
    
    def test_event_serialization(self):
        """Test event serialization."""
        event = PopulationEvent(EventType.DEATH, "creature_789")
        data = event.to_dict()
        
        self.assertEqual(data['event_type'], 'death')
        self.assertEqual(data['creature_id'], 'creature_789')


class TestEventLogger(unittest.TestCase):
    """Test cases for EventLogger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = EventLogger()
        self.creature = Creature(name="TestCreature")
    
    def test_log_event(self):
        """Test logging an event."""
        self.logger.log(EventType.BIRTH, self.creature)
        
        self.assertEqual(len(self.logger.events), 1)
        self.assertEqual(self.logger.events[0].event_type, EventType.BIRTH)
    
    def test_filter_by_type(self):
        """Test filtering events by type."""
        self.logger.log(EventType.BIRTH, self.creature)
        self.logger.log(EventType.DEATH, self.creature)
        self.logger.log(EventType.BIRTH, self.creature)
        
        birth_events = self.logger.get_events(event_type=EventType.BIRTH)
        self.assertEqual(len(birth_events), 2)
    
    def test_filter_by_creature(self):
        """Test filtering events by creature ID."""
        creature1 = Creature(name="Creature1")
        creature2 = Creature(name="Creature2")
        
        self.logger.log(EventType.BIRTH, creature1)
        self.logger.log(EventType.BIRTH, creature2)
        
        c1_events = self.logger.get_events(creature_id=creature1.creature_id)
        self.assertEqual(len(c1_events), 1)


class TestPopulationAnalytics(unittest.TestCase):
    """Test cases for PopulationAnalytics class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analytics = PopulationAnalytics()
        self.pop_manager = PopulationManager()
    
    def test_record_tick(self):
        """Test recording population snapshots."""
        # Add some creatures
        for i in range(5):
            creature = Creature(name=f"Creature{i}")
            self.pop_manager.spawn_creature(creature, log_event=False)
        
        self.analytics.record_tick(self.pop_manager)
        
        self.assertEqual(len(self.analytics.history), 1)
        self.assertEqual(self.analytics.history[0]['population'], 5)
    
    def test_get_statistics(self):
        """Test getting summary statistics."""
        creature = Creature(name="TestCreature")
        self.pop_manager.spawn_creature(creature, log_event=False)
        
        self.analytics.record_tick(self.pop_manager)
        stats = self.analytics.get_statistics()
        
        self.assertEqual(stats['current_population'], 1)
        self.assertEqual(stats['total_births'], 1)


class TestPopulationManager(unittest.TestCase):
    """Test cases for PopulationManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PopulationManager()
    
    def test_spawn_creature(self):
        """Test spawning a creature."""
        creature = Creature(name="NewCreature")
        self.manager.spawn_creature(creature)
        
        self.assertEqual(len(self.manager.population), 1)
        self.assertEqual(self.manager.births, 1)
    
    def test_remove_creature(self):
        """Test removing a creature."""
        creature = Creature(name="TestCreature")
        self.manager.spawn_creature(creature)
        self.manager.remove_creature(creature, cause="test")
        
        self.assertEqual(self.manager.deaths, 1)
    
    def test_get_alive_creatures(self):
        """Test getting alive creatures."""
        creature1 = Creature(name="Alive")
        creature2 = Creature(name="Dead")
        
        self.manager.spawn_creature(creature1)
        self.manager.spawn_creature(creature2)
        
        # Kill creature2
        creature2.stats.hp = 0
        
        alive = self.manager.get_alive_creatures()
        self.assertEqual(len(alive), 1)
        self.assertEqual(alive[0].name, "Alive")
    
    def test_get_mature_creatures(self):
        """Test getting mature creatures."""
        creature1 = Creature(name="Mature", mature=True)
        creature2 = Creature(name="Juvenile", mature=False)
        
        self.manager.spawn_creature(creature1)
        self.manager.spawn_creature(creature2)
        
        mature = self.manager.get_mature_creatures()
        self.assertEqual(len(mature), 1)
        self.assertEqual(mature[0].name, "Mature")


class TestEcosystemConfig(unittest.TestCase):
    """Test cases for EcosystemConfig class."""
    
    def test_config_initialization(self):
        """Test creating a configuration."""
        config = EcosystemConfig(
            max_population=100,
            breeding_cooldown=60.0,
            maturity_age=30.0
        )
        
        self.assertEqual(config.max_population, 100)
        self.assertEqual(config.breeding_cooldown, 60.0)
        self.assertEqual(config.maturity_age, 30.0)
    
    def test_config_serialization(self):
        """Test config serialization."""
        config = EcosystemConfig()
        data = config.to_dict()
        
        self.assertIn('max_population', data)
        self.assertIn('breeding_cooldown', data)
        
        # Test round-trip
        config2 = EcosystemConfig.from_dict(data)
        self.assertEqual(config.max_population, config2.max_population)


class TestCreatureLifecycle(unittest.TestCase):
    """Test cases for creature lifecycle features."""
    
    def test_creature_has_lifecycle_fields(self):
        """Test creature has new lifecycle fields."""
        creature = Creature(name="TestCreature")
        
        self.assertIsNotNone(creature.birth_time)
        self.assertEqual(creature.age, 0.0)
        self.assertFalse(creature.mature)
        self.assertEqual(creature.parent_ids, [])
        self.assertIsNotNone(creature.hue)
    
    def test_creature_can_breed(self):
        """Test can_breed method."""
        creature = Creature(name="TestCreature", mature=True)
        
        # Should be able to breed when mature, healthy, and well-fed
        self.assertTrue(creature.can_breed())
        
        # Should not breed when immature
        creature.mature = False
        self.assertFalse(creature.can_breed())
        
        # Should not breed when low HP
        creature.mature = True
        creature.stats.hp = creature.stats.max_hp * 0.3
        self.assertFalse(creature.can_breed())
    
    def test_creature_tick_age(self):
        """Test age progression."""
        creature = Creature(name="TestCreature")
        
        # Age should start at 0
        self.assertEqual(creature.age, 0.0)
        
        # Tick age
        creature.tick_age(10.0)
        self.assertEqual(creature.age, 10.0)
        
        # Should not be mature yet
        self.assertFalse(creature.mature)
        
        # Tick to maturity
        creature.tick_age(15.0)
        self.assertTrue(creature.mature)
    
    def test_creature_hsv_color(self):
        """Test HSV color system."""
        creature = Creature(name="TestCreature", hue=180.0)
        
        # Should return RGB tuple
        color = creature.get_display_color()
        self.assertEqual(len(color), 3)
        self.assertTrue(all(0 <= c <= 255 for c in color))
        
        # Color should change with health
        color1 = creature.get_display_color()
        creature.stats.hp = creature.stats.max_hp * 0.5
        color2 = creature.get_display_color()
        self.assertNotEqual(color1, color2)
    
    def test_creature_serialization_with_lifecycle(self):
        """Test serialization includes lifecycle fields."""
        creature = Creature(
            name="TestCreature",
            age=10.0,
            mature=True,
            parent_ids=["parent1", "parent2"],
            hue=120.0
        )
        
        data = creature.to_dict()
        
        self.assertEqual(data['age'], 10.0)
        self.assertTrue(data['mature'])
        self.assertEqual(data['parent_ids'], ["parent1", "parent2"])
        self.assertEqual(data['hue'], 120.0)
        
        # Test deserialization
        creature2 = Creature.from_dict(data)
        self.assertEqual(creature2.age, 10.0)
        self.assertTrue(creature2.mature)
        self.assertEqual(creature2.parent_ids, ["parent1", "parent2"])
        self.assertEqual(creature2.hue, 120.0)


if __name__ == '__main__':
    unittest.main()
