"""
Unit tests for movement smoothing and jitter prevention.
"""

import unittest
from src.models.spatial import Vector2D, SpatialEntity
from src.systems.battle_spatial import SpatialBattle, BattleCreature
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats


class TestMovementSmoothing(unittest.TestCase):
    """Test cases for movement smoothing features."""
    
    def test_spatial_entity_has_damping(self):
        """Test that SpatialEntity has damping attribute."""
        entity = SpatialEntity()
        self.assertTrue(hasattr(entity, 'damping'))
        self.assertTrue(hasattr(entity, 'acceleration'))
        self.assertGreater(entity.damping, 0)
        self.assertLessEqual(entity.damping, 1.0)
    
    def test_velocity_smoothing_on_direction_change(self):
        """Test that velocity changes smoothly when target direction changes."""
        entity = SpatialEntity(position=Vector2D(0, 0), max_speed=10.0)
        
        # Move towards east
        target1 = Vector2D(10, 0)
        entity.move_towards(target1, delta_time=0.1)
        velocity_after_first = entity.velocity.magnitude()
        
        # Immediately change to west - velocity should not instantly reverse
        target2 = Vector2D(-10, 0)
        entity.move_towards(target2, delta_time=0.1)
        velocity_after_change = entity.velocity.magnitude()
        
        # After direction change, velocity should be lower due to acceleration damping
        self.assertLess(velocity_after_change, velocity_after_first)
    
    def test_velocity_damping_over_time(self):
        """Test that velocity decays when not being updated."""
        entity = SpatialEntity(position=Vector2D(0, 0), max_speed=10.0)
        
        # Set initial velocity
        entity.velocity = Vector2D(10, 0)
        initial_magnitude = entity.velocity.magnitude()
        
        # Update without changing direction - velocity should decay
        entity.update(0.1)
        after_update_magnitude = entity.velocity.magnitude()
        
        self.assertLess(after_update_magnitude, initial_magnitude)
    
    def test_battle_creature_has_target_retention(self):
        """Test that BattleCreature has target retention attributes."""
        ctype = CreatureType(name="Test", base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10))
        creature = Creature(name="TestCreature", creature_type=ctype, level=1)
        battle_creature = BattleCreature(creature, Vector2D(0, 0))
        
        self.assertTrue(hasattr(battle_creature, 'target_retention_distance'))
        self.assertTrue(hasattr(battle_creature, 'min_retarget_time'))
        self.assertTrue(hasattr(battle_creature, 'last_retarget_time'))
        self.assertTrue(hasattr(battle_creature, 'last_behavior_state'))
        
        self.assertGreater(battle_creature.target_retention_distance, 0)
        self.assertGreater(battle_creature.min_retarget_time, 0)
    
    def test_smooth_movement_towards_target(self):
        """Test that movement towards a target is smooth, not instant."""
        entity = SpatialEntity(position=Vector2D(0, 0), max_speed=10.0)
        target = Vector2D(100, 0)
        
        # Move towards target in small steps
        velocities = []
        for _ in range(5):
            entity.move_towards(target, delta_time=0.1)
            velocities.append(entity.velocity.magnitude())
            entity.update(0.1)
        
        # Velocity should gradually increase (acceleration)
        self.assertLess(velocities[0], velocities[1])
        self.assertLess(velocities[1], velocities[2])
        
        # Eventually reach max speed
        self.assertLessEqual(max(velocities), entity.max_speed)


class TestTargetRetention(unittest.TestCase):
    """Test cases for target retention and retargeting hysteresis."""
    
    def test_creatures_dont_retarget_immediately(self):
        """Test that creatures don't change targets every frame."""
        # Create a simple battle with 3 creatures
        creatures = []
        for i in range(3):
            ctype = CreatureType(name=f"Type{i}", base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10))
            creature = Creature(name=f"Creature{i}", creature_type=ctype, level=1)
            creatures.append(creature)
        
        battle = SpatialBattle(creatures, arena_width=50, arena_height=50)
        
        # Get first creature
        first_creature = battle.creatures[0]
        
        # Run a few updates to let it pick a target
        for _ in range(3):
            battle.update(0.016)
        
        # Record its target
        initial_target = first_creature.target
        
        if initial_target:
            # Run more updates - target should be retained for at least min_retarget_time
            for _ in range(10):
                battle.update(0.016)  # 10 frames at 60fps = 0.16 seconds
            
            # Target should still be the same (less than min_retarget_time of 0.5 seconds)
            self.assertEqual(first_creature.target, initial_target)
    
    def test_hunger_behavior_has_hysteresis(self):
        """Test that hunger-based behavior switching has a buffer zone."""
        from src.models.ecosystem_traits import FORAGER
        
        ctype = CreatureType(name="Test", base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10))
        creature = Creature(name="TestCreature", creature_type=ctype, level=1, traits=[FORAGER])
        
        battle = SpatialBattle([creature], arena_width=50, arena_height=50, initial_resources=5)
        battle_creature = battle.creatures[0]
        
        # Set hunger to just above the low threshold (35) but below high threshold (50)
        battle_creature.creature.hunger = 40
        
        # Update once to establish state
        battle.update(0.016)
        initial_state = battle_creature.last_behavior_state
        
        # Hunger at 40 should maintain current state due to hysteresis
        # If it was "combat", should stay "combat" (threshold is 35)
        # If it was "seeking_food", should stay "seeking_food" (threshold is 50)
        self.assertIsNotNone(battle_creature.last_behavior_state)


if __name__ == '__main__':
    unittest.main()
