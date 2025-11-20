"""
Simple verification script to test arena boundary clamping.
This bypasses unittest to avoid encoding issues.
"""
import sys
sys.path.insert(0, '.')

from src.models.spatial import Vector2D, Arena
from src.systems.battle_spatial import BattleCreature
from src.models.creature import Creature
from src.models.stats import Stats, StatGrowth
from src.models.creature import CreatureType

def test_boundary_clamping():
    """Verify that creatures stay within arena bounds."""
    arena = Arena(100.0, 100.0)
    
    # Create a test creature
    base_stats = Stats(max_hp=100, attack=10, defense=10, speed=20)
    creature_type = CreatureType("TestType", base_stats, ["normal"], stat_growth=StatGrowth())
    creature = Creature("TestCreature", creature_type)
    battle_creature = BattleCreature(creature, Vector2D(50, 50))
    
    # Test 1: High velocity towards right edge
    battle_creature.spatial.position = Vector2D(95.0, 50.0)
    battle_creature.spatial.velocity = Vector2D(100.0, 0.0)
    battle_creature.spatial.max_speed = 100.0
    
    # Simulate update (what happens in battle_spatial.py)
    delta_time = 0.1
    battle_creature.spatial.update(delta_time)  # Moves position
    arena.apply_boundary_repulsion(battle_creature.spatial)  # Apply soft repulsion
    battle_creature.spatial.position = arena.clamp_position(battle_creature.spatial.position)  # HARD CLAMP
    
    pos = battle_creature.spatial.position
    print(f"Test 1 - High velocity right: Position = ({pos.x:.2f}, {pos.y:.2f})")
    assert pos.x <= 100.0, f"X position {pos.x} exceeds arena width 100.0"
    assert pos.x >= 0.0, f"X position {pos.x} is negative"
    print("✓ Test 1 PASSED: Creature clamped to arena bounds")
    
    # Test 2: High velocity towards left edge
    battle_creature.spatial.position = Vector2D(5.0, 50.0)
    battle_creature.spatial.velocity = Vector2D(-100.0, 0.0)
    
    battle_creature.spatial.update(delta_time)
    arena.apply_boundary_repulsion(battle_creature.spatial)
    battle_creature.spatial.position = arena.clamp_position(battle_creature.spatial.position)
    
    pos = battle_creature.spatial.position
    print(f"Test 2 - High velocity left: Position = ({pos.x:.2f}, {pos.y:.2f})")
    assert pos.x >= 0.0, f"X position {pos.x} is negative"
    assert pos.x <= 100.0, f"X position {pos.x} exceeds arena width"
    print("✓ Test 2 PASSED: Creature clamped to arena bounds")
    
    # Test 3: Diagonal high velocity towards corner
    battle_creature.spatial.position = Vector2D(95.0, 95.0)
    battle_creature.spatial.velocity = Vector2D(100.0, 100.0)
    
    battle_creature.spatial.update(delta_time)
    arena.apply_boundary_repulsion(battle_creature.spatial)
    battle_creature.spatial.position = arena.clamp_position(battle_creature.spatial.position)
    
    pos = battle_creature.spatial.position
    print(f"Test 3 - Diagonal to corner: Position = ({pos.x:.2f}, {pos.y:.2f})")
    assert 0.0 <= pos.x <= 100.0, f"X position {pos.x} out of bounds"
    assert 0.0 <= pos.y <= 100.0, f"Y position {pos.y} out of bounds"
    print("✓ Test 3 PASSED: Creature clamped to arena bounds")
    
    print("\n[SUCCESS] All boundary clamping tests PASSED!")
    print("Creatures will now stay within arena bounds and not escape into UI.")

if __name__ == '__main__':
    try:
        test_boundary_clamping()
    except AssertionError as e:
        print(f"\n[FAILED] Test FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
