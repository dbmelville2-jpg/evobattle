import unittest
from unittest.mock import MagicMock, patch
import math

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.spatial import Vector2D
from src.models.ability import Ability, AbilityType
from src.systems.battle_spatial import SpatialBattle, BattleCreature
from src.systems.battle_managers.combat_manager import CombatManager

class TestSpatialBattle(unittest.TestCase):
    def setUp(self):
        # Create basic creature types
        self.type_a = CreatureType("TypeA", Stats(max_hp=100, attack=10, defense=5, speed=10))
        self.type_b = CreatureType("TypeB", Stats(max_hp=100, attack=10, defense=5, speed=10))
        
        self.creature1 = Creature("C1", self.type_a)
        self.creature2 = Creature("C2", self.type_b)
        
        # Add abilities
        self.creature1.abilities = [Ability("Attack", power=10, accuracy=100, cooldown=0)]
        self.creature2.abilities = [Ability("Attack", power=10, accuracy=100, cooldown=0)]
        
        self.battle = SpatialBattle([self.creature1, self.creature2], arena_width=100, arena_height=100)
        
        # Get battle creatures
        self.bc1 = self.battle.creatures[0]
        self.bc2 = self.battle.creatures[1]
        
        # Position them close to each other
        self.bc1.spatial.position = Vector2D(50, 50)
        self.bc2.spatial.position = Vector2D(52, 50) # Distance 2.0
        
        # Update spatial grid
        self.battle.creature_grid.update(self.bc1, self.bc1.spatial.position)
        self.battle.creature_grid.update(self.bc2, self.bc2.spatial.position)

    def test_initialization(self):
        self.assertIsInstance(self.battle.combat_manager, CombatManager)
        self.assertEqual(len(self.battle.creatures), 2)

    def test_combat_execution(self):
        # Force target
        self.bc1.target = self.bc2
        
        # Initial HP
        initial_hp = self.bc2.creature.stats.hp
        
        # Update battle to trigger combat
        # We need to ensure can_attack returns true
        self.bc1.last_attack_time = -10
        
        # Run update
        self.battle.update(0.1)
        
        # Check if damage was dealt
        self.assertLess(self.bc2.creature.stats.hp, initial_hp)
        
    def test_death_handling(self):
        # Set HP to low
        self.bc2.creature.stats.hp = 1
        self.bc1.target = self.bc2
        self.bc1.last_attack_time = -10
        
        # Run update
        self.battle.update(0.1)
        
        # Check if dead
        self.assertFalse(self.bc2.is_alive())
        # Check active creatures
        self.assertNotIn(self.bc2, self.battle.active_creatures)

if __name__ == '__main__':
    unittest.main()
