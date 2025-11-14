"""
Unit tests for Stats, StatModifier, and StatGrowth models.
"""

import unittest
from src.models.stats import Stats, StatModifier, StatGrowth


class TestStats(unittest.TestCase):
    """Test cases for Stats class."""
    
    def test_stats_initialization(self):
        """Test creating a Stats object with default values."""
        stats = Stats()
        self.assertEqual(stats.hp, 100)
        self.assertEqual(stats.max_hp, 100)
        self.assertEqual(stats.attack, 10)
        self.assertEqual(stats.defense, 10)
        self.assertEqual(stats.speed, 10)
    
    def test_stats_custom_values(self):
        """Test creating Stats with custom values."""
        stats = Stats(max_hp=150, hp=150, attack=20, defense=15, speed=12)
        self.assertEqual(stats.max_hp, 150)
        self.assertEqual(stats.hp, 150)
        self.assertEqual(stats.attack, 20)
    
    def test_stats_hp_cap(self):
        """Test that HP is capped at max_hp during initialization."""
        stats = Stats(max_hp=100, hp=150)
        self.assertEqual(stats.hp, 100)
    
    def test_heal(self):
        """Test healing functionality."""
        stats = Stats(max_hp=100, hp=50)
        healed = stats.heal(30)
        self.assertEqual(healed, 30)
        self.assertEqual(stats.hp, 80)
    
    def test_heal_beyond_max(self):
        """Test that healing doesn't exceed max HP."""
        stats = Stats(max_hp=100, hp=90)
        healed = stats.heal(20)
        self.assertEqual(healed, 10)
        self.assertEqual(stats.hp, 100)
    
    def test_take_damage(self):
        """Test damage application."""
        stats = Stats(max_hp=100, hp=100)
        damage = stats.take_damage(30)
        self.assertEqual(damage, 30)
        self.assertEqual(stats.hp, 70)
    
    def test_take_damage_beyond_zero(self):
        """Test that HP doesn't go below 0."""
        stats = Stats(max_hp=100, hp=20)
        damage = stats.take_damage(30)
        self.assertEqual(damage, 20)
        self.assertEqual(stats.hp, 0)
    
    def test_is_alive(self):
        """Test alive status checking."""
        stats = Stats(max_hp=100, hp=50)
        self.assertTrue(stats.is_alive())
        
        stats.take_damage(50)
        self.assertFalse(stats.is_alive())
    
    def test_copy(self):
        """Test creating a copy of stats."""
        original = Stats(max_hp=100, hp=80, attack=15)
        copy = original.copy()
        
        self.assertEqual(copy.hp, 80)
        self.assertEqual(copy.attack, 15)
        
        # Ensure it's a separate object
        copy.hp = 50
        self.assertEqual(original.hp, 80)
    
    def test_apply_modifier(self):
        """Test applying a stat modifier."""
        stats = Stats(attack=10, defense=10)
        modifier = StatModifier(
            attack_multiplier=1.5,
            attack_bonus=5,
            defense_multiplier=1.0,
            defense_bonus=3
        )
        
        modified = stats.apply_modifier(modifier)
        self.assertEqual(modified.attack, 20)  # (10 * 1.5) + 5
        self.assertEqual(modified.defense, 13)  # (10 * 1.0) + 3
    
    def test_serialization(self):
        """Test to_dict and from_dict."""
        stats = Stats(max_hp=120, hp=100, attack=15, defense=12, speed=14)
        data = stats.to_dict()
        
        self.assertEqual(data['max_hp'], 120)
        self.assertEqual(data['attack'], 15)
        
        restored = Stats.from_dict(data)
        self.assertEqual(restored.hp, 100)
        self.assertEqual(restored.attack, 15)


class TestStatModifier(unittest.TestCase):
    """Test cases for StatModifier class."""
    
    def test_modifier_initialization(self):
        """Test creating a StatModifier."""
        modifier = StatModifier(
            name="Power Boost",
            duration=3,
            attack_multiplier=1.5,
            attack_bonus=10
        )
        self.assertEqual(modifier.name, "Power Boost")
        self.assertEqual(modifier.duration, 3)
        self.assertEqual(modifier.attack_multiplier, 1.5)
    
    def test_modifier_tick(self):
        """Test duration decrease."""
        modifier = StatModifier(duration=3)
        modifier.tick()
        self.assertEqual(modifier.duration, 2)
        modifier.tick()
        self.assertEqual(modifier.duration, 1)
    
    def test_modifier_expiration(self):
        """Test modifier expiration."""
        modifier = StatModifier(duration=1)
        self.assertFalse(modifier.is_expired())
        modifier.tick()
        self.assertTrue(modifier.is_expired())
    
    def test_permanent_modifier(self):
        """Test that permanent modifiers don't expire."""
        modifier = StatModifier(duration=-1)
        modifier.tick()
        self.assertEqual(modifier.duration, -1)
        self.assertFalse(modifier.is_expired())
    
    def test_modifier_serialization(self):
        """Test modifier serialization."""
        modifier = StatModifier(
            name="Test",
            duration=5,
            attack_multiplier=2.0,
            defense_bonus=5
        )
        data = modifier.to_dict()
        
        self.assertEqual(data['name'], "Test")
        self.assertEqual(data['attack_multiplier'], 2.0)
        
        restored = StatModifier.from_dict(data)
        self.assertEqual(restored.name, "Test")
        self.assertEqual(restored.duration, 5)


class TestStatGrowth(unittest.TestCase):
    """Test cases for StatGrowth class."""
    
    def test_growth_initialization(self):
        """Test creating a StatGrowth profile."""
        growth = StatGrowth(
            hp_growth=15.0,
            attack_growth=3.0,
            growth_curve="fast"
        )
        self.assertEqual(growth.hp_growth, 15.0)
        self.assertEqual(growth.attack_growth, 3.0)
        self.assertEqual(growth.growth_curve, "fast")
    
    def test_calculate_stats_at_level(self):
        """Test stat calculation at different levels."""
        base_stats = Stats(max_hp=100, hp=100, attack=10, defense=10, speed=10)
        growth = StatGrowth(
            hp_growth=10.0,
            attack_growth=2.0,
            defense_growth=2.0,
            speed_growth=1.5,
            growth_curve="medium_fast"
        )
        
        # Level 1 should be same as base
        level1_stats = growth.calculate_stats_at_level(base_stats, 1)
        self.assertEqual(level1_stats.max_hp, 100)
        self.assertEqual(level1_stats.attack, 10)
        
        # Level 5 should have increased stats
        level5_stats = growth.calculate_stats_at_level(base_stats, 5)
        self.assertGreater(level5_stats.max_hp, 100)
        self.assertGreater(level5_stats.attack, 10)
    
    def test_growth_curves(self):
        """Test different growth curves."""
        base_stats = Stats(max_hp=100, hp=100, attack=10)
        
        slow_growth = StatGrowth(attack_growth=2.0, growth_curve="slow")
        fast_growth = StatGrowth(attack_growth=2.0, growth_curve="fast")
        
        slow_stats = slow_growth.calculate_stats_at_level(base_stats, 10)
        fast_stats = fast_growth.calculate_stats_at_level(base_stats, 10)
        
        # Fast growth should result in higher stats
        self.assertGreater(fast_stats.attack, slow_stats.attack)
    
    def test_growth_serialization(self):
        """Test growth profile serialization."""
        growth = StatGrowth(
            hp_growth=12.0,
            attack_growth=3.0,
            growth_curve="fast"
        )
        data = growth.to_dict()
        
        self.assertEqual(data['hp_growth'], 12.0)
        self.assertEqual(data['growth_curve'], "fast")
        
        restored = StatGrowth.from_dict(data)
        self.assertEqual(restored.hp_growth, 12.0)
        self.assertEqual(restored.growth_curve, "fast")


if __name__ == '__main__':
    unittest.main()
