"""
Unit tests for foraging behavior and resource system.
"""

import unittest
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.trait import Trait
from src.models.behavior import BehaviorType, SpatialBehavior
from src.models.spatial import Vector2D, SpatialEntity, Arena
from src.systems.battle_spatial import SpatialBattle, BattleCreature


class TestForagingBehavior(unittest.TestCase):
    """Test cases for foraging behavior."""
    
    def test_forager_behavior_type_exists(self):
        """Test that FORAGER behavior type is defined."""
        self.assertTrue(hasattr(BehaviorType, 'FORAGER'))
        self.assertEqual(BehaviorType.FORAGER.value, 'forager')
    
    def test_forager_seeks_resources(self):
        """Test that forager behavior seeks resources."""
        behavior = SpatialBehavior(BehaviorType.FORAGER)
        entity = SpatialEntity(position=Vector2D(10, 10))
        
        resources = [Vector2D(20, 20), Vector2D(5, 5)]
        
        target = behavior.get_movement_target(
            entity,
            target_enemy=None,
            allies=[],
            enemies=[],
            hazards=[],
            resources=resources
        )
        
        # Should target the nearest resource
        self.assertIsNotNone(target)
        self.assertEqual(target, Vector2D(5, 5))
    
    def test_forager_wanders_without_resources(self):
        """Test that forager wanders when no resources available."""
        behavior = SpatialBehavior(BehaviorType.FORAGER)
        entity = SpatialEntity(position=Vector2D(10, 10))
        
        target = behavior.get_movement_target(
            entity,
            target_enemy=None,
            allies=[],
            enemies=[],
            hazards=[],
            resources=[]
        )
        
        # Should have a wander target
        self.assertIsNotNone(target)
    
    def test_forager_trait_determines_behavior(self):
        """Test that Forager trait sets FORAGER behavior."""
        creature = Creature(
            name="Forager",
            traits=[Trait(name="Forager")]
        )
        battle_creature = BattleCreature(creature, Vector2D(10, 10))
        
        self.assertEqual(battle_creature.behavior.behavior_type, BehaviorType.FORAGER)


class TestResourceSystem(unittest.TestCase):
    """Test cases for resource spawning and collection."""
    
    def test_arena_has_resources_list(self):
        """Test that Arena has a resources list."""
        arena = Arena(100, 100)
        self.assertIsInstance(arena.resources, list)
        self.assertEqual(len(arena.resources), 0)
    
    def test_arena_add_resource(self):
        """Test adding resources to arena."""
        arena = Arena(100, 100)
        resource_pos = Vector2D(50, 50)
        
        arena.add_resource(resource_pos)
        
        self.assertEqual(len(arena.resources), 1)
        self.assertEqual(arena.resources[0], resource_pos)
    
    def test_battle_spawns_initial_resources(self):
        """Test that battle spawns initial resources."""
        creature1 = Creature(name="C1")
        creature2 = Creature(name="C2")
        
        battle = SpatialBattle(
            [creature1],
            [creature2],
            initial_resources=5
        )
        
        self.assertEqual(len(battle.arena.resources), 5)
    
    def test_battle_spawns_resources_over_time(self):
        """Test that resources spawn over time."""
        creature1 = Creature(name="C1")
        creature2 = Creature(name="C2")
        
        battle = SpatialBattle(
            [creature1],
            [creature2],
            resource_spawn_rate=1.0,  # 1 per second
            initial_resources=0
        )
        
        initial_count = len(battle.arena.resources)
        
        # Update for 1 second
        battle.update(1.0)
        
        # Should have spawned 1 resource
        self.assertEqual(len(battle.arena.resources), initial_count + 1)
    
    def test_resource_collection(self):
        """Test that creatures can collect resources."""
        creature1 = Creature(name="C1", hunger=50)
        creature2 = Creature(name="C2")
        
        battle = SpatialBattle(
            [creature1],
            [creature2],
            initial_resources=0
        )
        
        # Manually place a resource near player creature
        player_pos = battle.player_creatures[0].spatial.position
        resource_pos = Vector2D(player_pos.x + 1, player_pos.y)
        battle.arena.add_resource(resource_pos)
        
        initial_hunger = battle.player_creatures[0].creature.hunger
        
        # Update battle - creature should move toward and collect resource
        for _ in range(20):  # Multiple updates to allow movement
            battle.update(0.1)
        
        # Resource should be collected and hunger increased
        self.assertEqual(len(battle.arena.resources), 0)
        self.assertGreater(battle.player_creatures[0].creature.hunger, initial_hunger)


class TestHungerDrivenBehavior(unittest.TestCase):
    """Test cases for hunger-driven behavior changes."""
    
    def test_hungry_creatures_seek_food(self):
        """Test that hungry creatures prioritize food over combat."""
        hungry_creature = Creature(name="Hungry", hunger=30)
        enemy_creature = Creature(name="Enemy")
        
        battle = SpatialBattle(
            [hungry_creature],
            [enemy_creature],
            initial_resources=1
        )
        
        # Place resource and enemy at different locations
        player_pos = battle.player_creatures[0].spatial.position
        battle.arena.resources[0] = Vector2D(player_pos.x - 10, player_pos.y)
        
        enemy_pos = battle.enemy_creatures[0].spatial.position
        # Move enemy far away
        battle.enemy_creatures[0].spatial.position = Vector2D(player_pos.x + 50, player_pos.y)
        
        # Update - hungry creature should move toward food, not enemy
        initial_distance_to_food = player_pos.distance_to(battle.arena.resources[0])
        battle.update(0.5)
        
        new_player_pos = battle.player_creatures[0].spatial.position
        new_distance_to_food = new_player_pos.distance_to(battle.arena.resources[0])
        
        # Should be moving toward food
        self.assertLess(new_distance_to_food, initial_distance_to_food)
    
    def test_well_fed_creatures_dont_prioritize_food(self):
        """Test that well-fed creatures don't prioritize food."""
        well_fed_creature = Creature(name="WellFed", hunger=80)
        enemy_creature = Creature(name="Enemy")
        
        battle = SpatialBattle(
            [well_fed_creature],
            [enemy_creature],
            initial_resources=1
        )
        
        # Well-fed creature should not be seeking food urgently
        player = battle.player_creatures[0]
        self.assertGreaterEqual(player.creature.hunger, 40)


if __name__ == '__main__':
    unittest.main()
