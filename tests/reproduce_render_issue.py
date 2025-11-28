
import unittest
from enum import Enum
from src.models.structure import StructureType, Structure
from src.models.spatial import Vector2D

class TestRendererLogic(unittest.TestCase):
    def test_enum_matching(self):
        # Simulate the logic in arena_renderer.py
        
        # 1. Define colors dict using StructureType
        colors = {
            StructureType.SHELTER: (139, 90, 43),
            StructureType.FOOD_CACHE: (100, 100, 110),
        }
        
        # 2. Create a structure with Enum type
        s1 = Structure(
            structure_id="1",
            structure_type=StructureType.SHELTER,
            position=Vector2D(0,0),
            tiles=[],
            builder_id="bob"
        )
        
        # 3. Create a structure with String type (simulating bad data)
        s2 = Structure(
            structure_id="2",
            structure_type="shelter",
            position=Vector2D(0,0),
            tiles=[],
            builder_id="bob"
        )
        
        # 4. Create a structure with Uppercase String type
        s3 = Structure(
            structure_id="3",
            structure_type="SHELTER",
            position=Vector2D(0,0),
            tiles=[],
            builder_id="bob"
        )
        
        def get_color(structure):
            stype = structure.structure_type
            if isinstance(stype, str):
                try:
                    stype = StructureType(stype.lower())
                except ValueError:
                    print(f"Failed to convert {stype}")
                    pass
            
            return colors.get(stype, (100, 100, 100))
            
        # Test s1 (Enum)
        c1 = get_color(s1)
        print(f"s1 color: {c1}")
        self.assertEqual(c1, (139, 90, 43))
        
        # Test s2 (String)
        c2 = get_color(s2)
        print(f"s2 color: {c2}")
        self.assertEqual(c2, (139, 90, 43))
        
        # Test s3 (Uppercase String)
        c3 = get_color(s3)
        print(f"s3 color: {c3}")
        self.assertEqual(c3, (139, 90, 43))

if __name__ == '__main__':
    unittest.main()
