"""
Direct test for pellet material drop functionality.
"""
from src.models.pellet import Pellet
from src.models.building_material import MaterialType

print("Testing pellet material drop...")

# Create a large pellet (higher drop chance)
pellet = Pellet(x=100, y=100)
pellet.traits.size = 2.0  # Max size for 60% drop chance

# Test material drops
drops_count = 0
total_tests = 100

for i in range(total_tests):
    materials = pellet.get_material_drop()
    if materials:
        drops_count += 1
        print(f"Test {i+1}: Dropped {len(materials)} materials - {[m.material_type.name for m in materials]}")

print(f"\nResults: {drops_count}/{total_tests} pellets dropped materials ({drops_count/total_tests*100:.1f}%)")
print(f"Expected: ~60% for size 2.0 pellet")

if drops_count > 0:
    print("\nSUCCESS: Material drop system is working!")
else:
    print("\nFAILURE: No materials dropped")
