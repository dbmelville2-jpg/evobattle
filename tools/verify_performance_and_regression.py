import unittest
import time
import sys
import os
import random
import math

# Add project root to path
sys.path.append(os.path.abspath(os.getcwd()))

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.spatial import Vector2D, SpatialHashGrid
from src.systems.battle_spatial import SpatialBattle, BattleCreature
from src.systems.scientific_intervention import ScientificIntervention
from src.rendering.scientific_cursor import CursorTool
from src.utils import jit_math

class TestNumbaIntegration(unittest.TestCase):
    """Verify Numba integration and performance."""
    
    def test_jit_math_speedup(self):
        """Compare JIT math functions against pure Python versions."""
        print("\n--- Numba Performance Check ---")
        
        # Pure Python implementation for comparison
        def py_distance_sq(x1, y1, x2, y2):
            return (x1 - x2)**2 + (y1 - y2)**2
            
        # Test data
        n = 1_000_000
        x1, y1 = 10.0, 10.0
        x2, y2 = 20.0, 20.0
        
        # Benchmark Python
        start = time.time()
        for _ in range(n):
            py_distance_sq(x1, y1, x2, y2)
        py_time = time.time() - start
        
        # Benchmark JIT
        # Warmup
        jit_math.distance_sq(x1, y1, x2, y2)
        
        start = time.time()
        for _ in range(n):
            jit_math.distance_sq(x1, y1, x2, y2)
        jit_time = time.time() - start
        
        print(f"1M distance_sq calls:")
        print(f"  Python: {py_time:.4f}s")
        print(f"  Numba:  {jit_time:.4f}s")
        print(f"  Speedup: {py_time / jit_time:.1f}x")
        
        self.assertLess(jit_time, py_time, "JIT should be faster than Python")

class TestScienceToolbarRegression(unittest.TestCase):
    """Regression tests for Science Toolbar."""
    
    def setUp(self):
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10),
            stat_growth=StatGrowth()
        )
        creatures = [Creature(name=f"c{i}", creature_type=creature_type, level=5) for i in range(5)]
        self.battle = SpatialBattle(creatures, arena_width=100, arena_height=100)
        
    def test_initialization(self):
        """Verify systems are initialized."""
        print("\n--- Science Toolbar Regression Check ---")
        self.assertTrue(hasattr(self.battle, 'intervention_system'), "intervention_system missing")
        self.assertTrue(hasattr(self.battle, 'ethics_system'), "ethics_system missing")
        self.assertIsInstance(self.battle.intervention_system, ScientificIntervention)
        print("Initialization: OK")
        
    def test_tool_usage(self):
        """Verify tool usage logic."""
        # Test Food Dispenser
        pos = (50.0, 50.0)
        success, msg = self.battle.intervention_system.use_tool("nutrient_drop", pos, self.battle)
        print(f"Food Dispenser: {success} ({msg})")
        
        # Should succeed (assuming enough charge/valid conditions, though charge is handled by cursor)
        # The system itself just checks logic. 
        # Note: nutrient_drop might fail if max pellets reached, but usually succeeds.
        
        # Check if pellet was added
        pellet_count = len(self.battle.arena.resources)
        self.assertGreater(pellet_count, 0, "Pellets should exist")
        
    def test_circular_dependency_fix(self):
        """Verify BattleEvent imports work."""
        from src.systems.battle_events import BattleEvent, BattleEventType
        event = BattleEvent(BattleEventType.BATTLE_START, message="Test")
import unittest
import time
import sys
import os
import random
import math

# Add project root to path
sys.path.append(os.path.abspath(os.getcwd()))

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.spatial import Vector2D, SpatialHashGrid
from src.systems.battle_spatial import SpatialBattle, BattleCreature
from src.systems.scientific_intervention import ScientificIntervention
from src.rendering.scientific_cursor import CursorTool
from src.utils import jit_math

class TestNumbaIntegration(unittest.TestCase):
    """Verify Numba integration and performance."""
    
    def test_jit_math_speedup(self):
        """Compare JIT math functions against pure Python versions."""
        print("\n--- Numba Performance Check ---")
        
        # Pure Python implementation for comparison
        def py_distance_sq(x1, y1, x2, y2):
            return (x1 - x2)**2 + (y1 - y2)**2
            
        # Test data
        n = 1_000_000
        x1, y1 = 10.0, 10.0
        x2, y2 = 20.0, 20.0
        
        # Benchmark Python
        start = time.time()
        for _ in range(n):
            py_distance_sq(x1, y1, x2, y2)
        py_time = time.time() - start
        
        # Benchmark JIT
        # Warmup
        jit_math.distance_sq(x1, y1, x2, y2)
        
        start = time.time()
        for _ in range(n):
            jit_math.distance_sq(x1, y1, x2, y2)
        jit_time = time.time() - start
        
        print(f"1M distance_sq calls:")
        print(f"  Python: {py_time:.4f}s")
        print(f"  Numba:  {jit_time:.4f}s")
        print(f"  Speedup: {py_time / jit_time:.1f}x")
        
        self.assertLess(jit_time, py_time, "JIT should be faster than Python")

class TestScienceToolbarRegression(unittest.TestCase):
    """Regression tests for Science Toolbar."""
    
    def setUp(self):
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10),
            stat_growth=StatGrowth()
        )
        creatures = [Creature(name=f"c{i}", creature_type=creature_type, level=5) for i in range(5)]
        self.battle = SpatialBattle(creatures, arena_width=100, arena_height=100)
        
    def test_initialization(self):
        """Verify systems are initialized."""
        print("\n--- Science Toolbar Regression Check ---")
        self.assertTrue(hasattr(self.battle, 'intervention_system'), "intervention_system missing")
        self.assertTrue(hasattr(self.battle, 'ethics_system'), "ethics_system missing")
        self.assertIsInstance(self.battle.intervention_system, ScientificIntervention)
        print("Initialization: OK")
        
    def test_tool_usage(self):
        """Verify tool usage logic."""
        # Test Food Dispenser
        pos = (50.0, 50.0)
        success, msg = self.battle.intervention_system.use_tool("nutrient_drop", pos, self.battle)
        print(f"Food Dispenser: {success} ({msg})")
        
        # Should succeed (assuming enough charge/valid conditions, though charge is handled by cursor)
        # The system itself just checks logic. 
        # Note: nutrient_drop might fail if max pellets reached, but usually succeeds.
        
        # Check if pellet was added
        pellet_count = len(self.battle.arena.resources)
        self.assertGreater(pellet_count, 0, "Pellets should exist")
        
    def test_circular_dependency_fix(self):
        """Verify BattleEvent imports work."""
        from src.systems.battle_events import BattleEvent, BattleEventType
        event = BattleEvent(BattleEventType.BATTLE_START, message="Test")
        self.assertEqual(event.message, "Test")
        print("Circular Dependency Fix: OK")

class TestSpatialPerformance(unittest.TestCase):
    """Performance tests for spatial hash grid."""
    
    def setUp(self):
        self.ctype = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10),
            stat_growth=StatGrowth()
        )

    def test_battle_performance(self):
        print("\n--- Battle Performance Check ---")
        # Stress test with 200 creatures
        count = 200
        creatures = [Creature(name=f"c{i}", creature_type=self.ctype, level=5) for i in range(count)]
        
        battle = SpatialBattle(creatures, arena_width=500, arena_height=500)
        
        # Warmup
        battle.update(0.1)
        
        # Measure
        frames = 60
        start = time.time()
        for _ in range(frames):
            battle.update(0.016)
        duration = time.time() - start
        
        fps = frames / duration
        ms_per_frame = (duration / frames) * 1000
        
        print(f"Battle ({count} creatures):")
        print(f"  FPS: {fps:.1f}")
        print(f"  ms/frame: {ms_per_frame:.2f}ms")
        
        # Target: 30 FPS for 200 creatures is decent for Python
        if fps < 30:
            print("WARNING: Performance below 30 FPS target")
        else:
            print("Performance: OK")
            
    def test_dead_creature_performance(self):
        """Verify performance with many dead creatures (regression check)."""
        print("\n--- Dead Creature Performance Check ---")
        
        # Create battle with 200 alive and 3000 dead creatures
        creatures = [Creature(name=f"c{i}", creature_type=self.ctype, level=5) for i in range(200)]
        battle = SpatialBattle(
            creatures_or_team1=creatures,
            arena_width=200,
            arena_height=200,
            enable_environment=False
        )
        
        # Add 3000 dead creatures
        dead_creatures = []
        for i in range(3000):
            c = Creature(name=f"Dead{i}", creature_type=self.ctype)
            c.stats.hp = 0
            bc = BattleCreature(c, Vector2D(0, 0))
            dead_creatures.append(bc)
            
        # Manually inject them into the battle list (simulating accumulation)
        battle._creatures.extend(dead_creatures)
        
        start_time = time.time()
        frames = 50
        for _ in range(frames):
            battle.update(0.1)
            
        end_time = time.time()
        duration = end_time - start_time
        fps = frames / duration
        
        print(f"Battle (200 alive + 3000 dead):")
        print(f"  FPS: {fps:.1f}")
        print(f"  ms/frame: {(duration/frames)*1000:.2f}ms")
        
        # If iterating over dead creatures is slow, this will fail
        self.assertGreater(fps, 30.0, "FPS with dead creatures should be > 30")

if __name__ == '__main__':
    unittest.main(verbosity=2)
