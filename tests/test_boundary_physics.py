import unittest
from src.models.spatial import Vector2D, SpatialEntity, Arena
from src.systems.battle_spatial import BattleCreature, SpatialBattle
from src.models.creature import Creature
from src.models.stats import Stats, StatGrowth
from src.models.creature import CreatureType

class TestBoundaryPhysics(unittest.TestCase):
    def setUp(self):
        self.arena_width = 100.0
        self.arena_height = 100.0
        self.arena = Arena(self.arena_width, self.arena_height)
        
        # Create a dummy creature
        base_stats = Stats(max_hp=100, attack=10, defense=10, speed=20)
        creature_type = CreatureType("TestType", base_stats, ["normal"], StatGrowth())
        self.creature = Creature("TestCreature", creature_type)
        self.battle_creature = BattleCreature(self.creature, Vector2D(50, 50))

    def test_boundary_repulsion_softness(self):
        """Test that repulsion alone might not be enough for high speeds."""
        # Place creature near edge
        self.battle_creature.spatial.position = Vector2D(99.0, 50.0)
        # Give high velocity towards outside
        self.battle_creature.spatial.velocity = Vector2D(100.0, 0.0)
        self.battle_creature.spatial.max_speed = 100.0
        
        # Update for 1 second (large step)
        # Note: In real game, steps are smaller, but lag spikes happen.
        # Also, multiple frames of acceleration can push it out.
        
        # Manually apply update logic similar to battle_spatial.py BEFORE fix
        delta_time = 0.1
        self.battle_creature.spatial.update(delta_time)
        self.arena.apply_boundary_repulsion(self.battle_creature.spatial)
        
        # Check if out of bounds
        pos = self.battle_creature.spatial.position
        is_inside = self.arena.is_within_bounds(pos)
        
        # This might pass or fail depending on exact math, but let's see.
        # If it's at 99, vel 100, dt 0.1 -> moves 10 units -> pos 109.
        # Repulsion is applied AFTER movement in the loop?
        # In battle_spatial.py:
        # creature.spatial.update(delta_time)  <-- Moves first!
        # self.arena.apply_boundary_repulsion(creature.spatial) <-- Then repels
        
        # So if it moves out, repulsion changes velocity but doesn't fix position immediately.
        # So it will be out of bounds for at least one frame.
        
        self.assertTrue(pos.x > self.arena_width, "Creature should have moved out of bounds before repulsion could stop it")

    def test_clamping_enforcement(self):
        """Test that clamping keeps creature inside."""
        # This test simulates the FIX logic
        self.battle_creature.spatial.position = Vector2D(99.0, 50.0)
        self.battle_creature.spatial.velocity = Vector2D(100.0, 0.0)
        self.battle_creature.spatial.max_speed = 100.0
        
        delta_time = 0.1
        
        # Logic with fix:
        self.battle_creature.spatial.update(delta_time)
        self.battle_creature.spatial.position = self.arena.clamp_position(self.battle_creature.spatial.position)
        self.arena.apply_boundary_repulsion(self.battle_creature.spatial)
        
        pos = self.battle_creature.spatial.position
        self.assertTrue(self.arena.is_within_bounds(pos), f"Creature at {pos} should be within bounds")
        self.assertLessEqual(pos.x, self.arena_width)

if __name__ == '__main__':
    unittest.main()
