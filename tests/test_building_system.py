
import unittest
import time
from src.models.creature import Creature, CreatureType
from src.models.trait import Trait
from src.models.spatial import Vector2D, Arena
from src.models.structure import StructureType, Structure
from src.models.building_material import MaterialType
from src.systems.battle_managers.building_manager import BuildingManager
from src.systems.battle_managers.event_manager import EventManager
from src.systems.battle_spatial import SpatialBattle

class MockEvent:
    def log(self, msg):
        print(f"[LOG] {msg}")

class TestBuildingSystem(unittest.TestCase):
    def setUp(self):
        self.event_manager = EventManager()
        self.arena = Arena(width=100, height=100)
        self.building_manager = BuildingManager(self.event_manager, self.arena)
        
        # Create a creature with Architect trait
        self.creature_type = CreatureType(name="Builder")
        self.creature = Creature(name="Bob", creature_type=self.creature_type)
        
        # Add Architect trait
        architect_trait = Trait(name="Architect", interaction_effects={
            "build_speed_multiplier": 2.0,
            "structure_durability_bonus": 1.5
        })
        self.creature.add_trait(architect_trait)
        
        # Mock spatial wrapper
        class SpatialWrapper:
            def __init__(self, x, y):
                self.position = Vector2D(x, y)
        
        self.creature_wrapper = type('obj', (object,), {
            'creature': self.creature,
            'spatial': SpatialWrapper(50, 50),
            'creature_id': self.creature.creature_id
        })

    def test_material_spawning(self):
        # Update manager to spawn materials
        # Default spawn rate is 0.05 per second (1 every 20s)
        # Force high spawn rate for test
        self.building_manager.config.material_spawn_rate = 10.0
        
        self.building_manager.update(1.0, 0.0)
        
        self.assertTrue(len(self.building_manager.materials) > 0)
        print(f"Spawned {len(self.building_manager.materials)} materials")

    def test_building_lifecycle(self):
        # 1. Spawn materials
        self.building_manager.config.material_spawn_rate = 100.0
        self.building_manager.update(1.0, 0.0)
        
        # Ensure we have materials
        self.assertTrue(len(self.building_manager.materials) > 0)
        
        # 2. Creature should identify need (force need via low HP + rain for Shelter)
        # But identify_building_need is probabilistic or condition based.
        # Let's manually trigger start task for deterministic testing
        
        # Manually start task
        task = self.building_manager.behavior_system.start_building_task(
            self.creature.creature_id,
            StructureType.SHELTER,
            Vector2D(60, 60)
        )
        
        # Also create the structure in manager (as if START_TASK decision was processed)
        structure = Structure(
            structure_id="test_struct",
            structure_type=StructureType.SHELTER,
            position=Vector2D(60, 60),
            tiles=[],
            builder_id=self.creature.creature_id,
            completion=0.0,
            durability=1.0
        )
        self.building_manager.structures.append(structure)
        
        # 3. Update creature building logic
        # Creature is at 50,50. Structure at 60,60.
        # Materials are random.
        
        # Move creature to a material
        # Ensure we have a WOOD material (required for Shelter)
        from src.models.building_material import BuildingMaterial
        import uuid
        material = BuildingMaterial(
            material_id=str(uuid.uuid4()),
            material_type=MaterialType.WOOD,
            position=Vector2D(50, 50),
            quantity=1
        )
        self.building_manager.materials = [material] # Override random materials
        
        self.creature_wrapper.spatial.position = Vector2D(material.position.x, material.position.y)
        
        # Update - should GATHER
        decision = self.building_manager.update_creature_building(self.creature_wrapper, [], 1.0)
        self.assertEqual(decision.action_type, "GATHER")
        
        # Execute GATHER logic (simulated by calling update again or checking side effects)
        # Wait, update_creature_building DOES execute the logic (remove from ground, add to creature)
        # So material should be gone from ground and in creature inventory
        
        self.assertNotIn(material, self.building_manager.materials)
        self.assertIn(material, self.creature.carried_materials)
        
        # 4. Move to build site
        self.creature_wrapper.spatial.position = Vector2D(60, 60)
        
        # Update - should BUILD (deposit)
        decision = self.building_manager.update_creature_building(self.creature_wrapper, [], 1.0)
        self.assertEqual(decision.action_type, "BUILD")
        
        # Material should be gone from inventory
        self.assertNotIn(material, self.creature.carried_materials)
        
        # Task should have material gathered
        self.assertTrue(task.materials_gathered[material.material_type] > 0)
        
        # 5. If all materials gathered, should CONSTRUCT
        # Cheat and fill requirements
        task.materials_gathered = task.materials_needed.copy()
        
        decision = self.building_manager.update_creature_building(self.creature_wrapper, [], 1.0)
        self.assertEqual(decision.action_type, "CONSTRUCT")
        
        # Structure should exist and have progress
        self.assertEqual(len(self.building_manager.structures), 1)
        structure = self.building_manager.structures[0]
        self.assertTrue(structure.completion > 0)
        
        print(f"Structure completion: {structure.completion}")

    def test_decay_and_repair(self):
        # Create a complete structure
        structure = Structure(
            structure_id="test",
            structure_type=StructureType.SHELTER,
            position=Vector2D(55, 55),
            tiles=[],
            builder_id="Bob",
            completion=1.0,
            durability=1.0
        )
        self.building_manager.structures.append(structure)
        
        # 1. Test Decay
        # Force high decay
        self.building_manager.config.base_decay_rate = 60.0 # 100% per minute -> 1.0 per sec
        
        self.building_manager.update(0.5, 0.0) # 0.5 seconds -> 0.5 damage
        
        self.assertTrue(structure.durability < 1.0)
        self.assertTrue(structure.durability > 0.0)
        print(f"Durability after decay: {structure.durability}")
        decayed_durability = structure.durability
        
        # 2. Test Repair
        # Creature is close
        self.creature_wrapper.spatial.position = Vector2D(55, 55)
        
        # Should identify repair need and execute repair
        decision = self.building_manager.update_creature_building(self.creature_wrapper, [], 1.0)
        
        # Should be CONSTRUCT with repair metadata
        self.assertEqual(decision.action_type, "CONSTRUCT")
        self.assertTrue(decision.metadata.get("repair"))
        
        # Durability should have increased from decayed state
        self.assertTrue(structure.durability > decayed_durability)
        print(f"Durability after repair: {structure.durability}")

if __name__ == '__main__':
    unittest.main()
