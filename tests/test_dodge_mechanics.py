"""
Tests for dodge mechanics to ensure balanced miss rates.

This test suite validates the fix for excessive creature miss rates.
"""

import unittest
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.skills import SkillType
from src.models.ability import create_ability
from src.systems.battle_spatial import SpatialBattle
from src.systems.living_world import LivingWorldBattleEnhancer


class TestDodgeMechanics(unittest.TestCase):
    """Test dodge chance calculations and miss rates."""
    
    def setUp(self):
        """Set up test creatures."""
        self.creature_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=150, attack=12, defense=8, speed=10)
        )
    
    def test_dodge_skill_scaling(self):
        """Test that dodge skill scales from 0% to 15%."""
        creature = Creature(name="Test", creature_type=self.creature_type, level=5)
        dodge_skill = creature.skills.get_skill(SkillType.DODGE)
        
        # Level 0 should give 0% dodge
        dodge_skill.level = 0
        self.assertEqual(dodge_skill.get_success_chance_bonus(), 0.0)
        
        # Level 50 should give 7.5% dodge
        dodge_skill.level = 50
        self.assertAlmostEqual(dodge_skill.get_success_chance_bonus(), 7.5, places=1)
        
        # Level 100 should give 15% dodge (not 50% like before the fix)
        dodge_skill.level = 100
        self.assertAlmostEqual(dodge_skill.get_success_chance_bonus(), 15.0, places=1)
    
    def test_personality_dodge_modifier(self):
        """Test that personality provides reasonable dodge modifier."""
        creature = Creature(name="Test", creature_type=self.creature_type, level=5)
        
        # Max caution (1.0) should give +10% dodge
        creature.personality.caution = 1.0
        self.assertAlmostEqual(creature.personality.get_dodge_chance_modifier(), 10.0, places=1)
        
        # Min caution (0.0) should give -10% dodge
        creature.personality.caution = 0.0
        self.assertAlmostEqual(creature.personality.get_dodge_chance_modifier(), -10.0, places=1)
        
        # Mid caution (0.5) should give 0% dodge
        creature.personality.caution = 0.5
        self.assertAlmostEqual(creature.personality.get_dodge_chance_modifier(), 0.0, places=1)
    
    def test_max_dodge_chance(self):
        """Test that maximum combined dodge chance is reasonable (~25%)."""
        creature = Creature(name="Test", creature_type=self.creature_type, level=5)
        
        # Max out dodge skill and caution
        dodge_skill = creature.skills.get_skill(SkillType.DODGE)
        dodge_skill.level = 100
        creature.personality.caution = 1.0
        
        # Calculate total dodge
        total_dodge = dodge_skill.get_success_chance_bonus()
        total_dodge += creature.personality.get_dodge_chance_modifier()
        
        # Should be around 25% (15% skill + 10% personality)
        self.assertLess(total_dodge, 30.0, "Max dodge should be less than 30%")
        self.assertGreater(total_dodge, 20.0, "Max dodge should be greater than 20%")
    
    def test_battle_miss_rates_are_reasonable(self):
        """Test that actual battle miss rates are reasonable."""
        # Create attacker and defender
        attacker = Creature(name="Attacker", creature_type=self.creature_type, level=5)
        attacker.add_ability(create_ability('tackle'))
        
        defender = Creature(name="Defender", creature_type=self.creature_type, level=5)
        defender.add_ability(create_ability('tackle'))
        
        # Give defender max dodge skill
        defender.skills.get_skill(SkillType.DODGE).level = 100
        
        # Run battle
        battle = SpatialBattle([attacker, defender])
        enhancer = LivingWorldBattleEnhancer(battle)
        battle.enhancer = enhancer
        
        for _ in range(200):
            battle.update(0.1)
            if battle.is_over:
                break
        
        # Count misses
        battle_log = battle.get_battle_log()
        miss_count = sum(1 for log in battle_log if "missed" in log.lower())
        hit_count = sum(1 for log in battle_log if "takes" in log.lower() and "damage" in log.lower())
        total_attacks = miss_count + hit_count
        
        if total_attacks > 0:
            miss_rate = (miss_count / total_attacks) * 100
            # Even with max dodge, miss rate should be less than 40%
            self.assertLess(miss_rate, 40.0, f"Miss rate of {miss_rate:.1f}% is too high")


if __name__ == '__main__':
    unittest.main()
