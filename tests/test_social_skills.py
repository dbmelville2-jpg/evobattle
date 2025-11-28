"""
Tests for social skills (Teamwork, Intimidation, Leadership).
"""

import unittest
from unittest.mock import MagicMock
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.skills import SkillType
from src.models.spatial import Vector2D
from src.systems.battle_managers.combat_manager import CombatManager

class TestSocialSkills(unittest.TestCase):
    """Test Teamwork, Intimidation, and Leadership skills."""
    
    def setUp(self):
        """Set up test environment."""
        self.creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        
        # Attacker
        self.attacker = Creature(name="Attacker", creature_type=self.creature_type)
        self.attacker.spatial = MagicMock()
        self.attacker.spatial.position = Vector2D(50, 50)
        self.battle_attacker = MagicMock()
        self.battle_attacker.creature = self.attacker
        self.battle_attacker.spatial = self.attacker.spatial
        
        # Defender
        self.defender = Creature(name="Defender", creature_type=self.creature_type)
        self.defender.spatial = MagicMock()
        self.defender.spatial.position = Vector2D(51, 50)
        self.battle_defender = MagicMock()
        self.battle_defender.creature = self.defender
        self.battle_defender.spatial = self.defender.spatial
        
        # Ally
        self.ally = Creature(name="Ally", creature_type=self.creature_type)
        self.ally.strain_id = self.attacker.strain_id # Same strain
        self.ally.spatial = MagicMock()
        self.ally.spatial.position = Vector2D(49, 50) # Nearby
        self.battle_ally = MagicMock()
        self.battle_ally.creature = self.ally
        self.battle_ally.spatial = self.ally.spatial
        
        self.combat_manager = CombatManager(
            event_manager=MagicMock(),
            combat_config=MagicMock(),
            trait_effects_handler=MagicMock()
        )
        # Mock type effectiveness to always be 1.0
        self.combat_manager.get_type_effectiveness = MagicMock(return_value=1.0)
        # Mock trait_effects to return neutral modifier
        self.combat_manager.trait_effects.get_combat_damage_modifier = MagicMock(return_value=1.0)

    def test_teamwork_bonus(self):
        """Test that Teamwork skill increases damage when allies are near."""
        # Set Teamwork skill
        self.attacker.skills.get_skill(SkillType.TEAMWORK).level = 100
        
        # Create a mock ability
        mock_ability = MagicMock()
        mock_ability.calculate_damage.return_value = 100
        
        # Seed random for deterministic results
        import random
        random.seed(42)
        
        # Case 1: No allies
        damage_solo, _ = self.combat_manager.calculate_damage(
            self.battle_attacker, 
            self.battle_defender, 
            mock_ability, 
            [self.battle_attacker, self.battle_defender]
        )
        
        # Reset seed for same variance
        random.seed(42)
        
        # Case 2: With ally
        damage_team, _ = self.combat_manager.calculate_damage(
            self.battle_attacker, 
            self.battle_defender, 
            mock_ability, 
            [self.battle_attacker, self.battle_defender, self.battle_ally]
        )
        
        # Team damage should be higher
        self.assertGreater(damage_team, damage_solo)
        
    def test_intimidation_effect(self):
        """Test that Intimidation skill can increase damage."""
        # Set Intimidation skill to max (high chance)
        self.attacker.skills.get_skill(SkillType.INTIMIDATION).level = 100
        
        # Mock random to ensure success
        import random
        original_random = random.random
        random.random = MagicMock(return_value=0.0) # Always succeed
        
        # Mock ability
        mock_ability = MagicMock()
        mock_ability.calculate_damage.return_value = 100
        
        try:
            damage_intimidated, _ = self.combat_manager.calculate_damage(
                self.battle_attacker, 
                self.battle_defender, 
                mock_ability, 
                [self.battle_attacker, self.battle_defender]
            )
            
            # Reset skill to 0 to compare
            self.attacker.skills.get_skill(SkillType.INTIMIDATION).level = 0
            damage_normal, _ = self.combat_manager.calculate_damage(
                self.battle_attacker, 
                self.battle_defender, 
                mock_ability, 
                [self.battle_attacker, self.battle_defender]
            )
            
            self.assertGreater(damage_intimidated, damage_normal)
            
        finally:
            random.random = original_random

if __name__ == '__main__':
    unittest.main()
