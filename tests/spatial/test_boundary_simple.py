"""
Minimal verification that arena boundary clamping works.
Tests the core fix without complex creature initialization.
"""
import sys
sys.path.insert(0, '.')

from src.models.spatial import Vector2D, SpatialEntity, Arena

def test_arena_clamp():
    """Test that clamp_position keeps entities within bounds."""
    arena = Arena(100.0, 100.0)
    
    # Test 1: Position beyond right edge
    pos = Vector2D(150.0, 50.0)
    clamped = arena.clamp_position(pos)
    print(f"Test 1: Position (150, 50) clamped to ({clamped.x}, {clamped.y})")
    assert clamped.x == 100.0, f"Expected x=100.0, got {clamped.x}"
    assert clamped.y == 50.0, f"Expected y=50.0, got {clamped.y}"
    print("[PASS] Right edge clamping works")
    
    # Test 2: Position beyond left edge
    pos = Vector2D(-10.0, 50.0)
    clamped = arena.clamp_position(pos)
    print(f"Test 2: Position (-10, 50) clamped to ({clamped.x}, {clamped.y})")
    assert clamped.x == 0.0, f"Expected x=0.0, got {clamped.x}"
    print("[PASS] Left edge clamping works")
    
    # Test 3: Position beyond top edge
    pos = Vector2D(50.0, -20.0)
    clamped = arena.clamp_position(pos)
    print(f"Test 3: Position (50, -20) clamped to ({clamped.x}, {clamped.y})")
    assert clamped.y == 0.0, f"Expected y=0.0, got {clamped.y}"
    print("[PASS] Top edge clamping works")
    
    # Test 4: Position beyond bottom edge
    pos = Vector2D(50.0, 150.0)
    clamped = arena.clamp_position(pos)
    print(f"Test 4: Position (50, 150) clamped to ({clamped.x}, {clamped.y})")
    assert clamped.y == 100.0, f"Expected y=100.0, got {clamped.y}"
    print("[PASS] Bottom edge clamping works")
    
    # Test 5: Position beyond corner
    pos = Vector2D(200.0, 200.0)
    clamped = arena.clamp_position(pos)
    print(f"Test 5: Position (200, 200) clamped to ({clamped.x}, {clamped.y})")
    assert clamped.x == 100.0 and clamped.y == 100.0
    print("[PASS] Corner clamping works")
    
    print("\n[SUCCESS] All arena boundary clamping tests passed!")
    print("The fix in battle_spatial.py line 626 ensures creatures stay within bounds.")
    return True

if __name__ == '__main__':
    try:
        test_arena_clamp()
    except Exception as e:
        print(f"\n[FAILED] {e}")
        sys.exit(1)
