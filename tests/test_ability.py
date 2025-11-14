"""
Unit tests for Ability system.
"""

import unittest
from src.models.ability import Ability, AbilityType, TargetType, AbilityEffect, create_ability, PREDEFINED_ABILITIES
from src.models.stats import Stats


class TestAbilityEffect(unittest.TestCase):
    """Test cases for AbilityEffect class."""
    
    def test_effect_initialization(self):
        """Test creating an AbilityEffect."""
        effect = AbilityEffect(
            effect_type="damage",
            value=50,
            multiplier=1.5
        )
        self.assertEqual(effect.effect_type, "damage")
        self.assertEqual(effect.value, 50)
        self.assertEqual(effect.multiplier, 1.5)
    
    def test_effect_serialization(self):
        """Test effect serialization."""
        effect = AbilityEffect(
            effect_type="heal",
            value=30,
            duration=3
        )
        data = effect.to_dict()
        
        self.assertEqual(data['effect_type'], "heal")
        self.assertEqual(data['value'], 30)
        
        restored = AbilityEffect.from_dict(data)
        self.assertEqual(restored.effect_type, "heal")
        self.assertEqual(restored.value, 30)


class TestAbility(unittest.TestCase):
    """Test cases for Ability class."""
    
    def test_ability_initialization(self):
        """Test creating an Ability."""
        ability = Ability(
            name="Fireball",
            description="A ball of fire",
            ability_type=AbilityType.SPECIAL,
            power=60,
            cooldown=2
        )
        self.assertEqual(ability.name, "Fireball")
        self.assertEqual(ability.power, 60)
        self.assertEqual(ability.cooldown, 2)
        self.assertEqual(ability.current_cooldown, 0)
    
    def test_ability_use_and_cooldown(self):
        """Test using ability and cooldown management."""
        ability = Ability(cooldown=3)
        
        self.assertEqual(ability.current_cooldown, 0)
        
        ability.use()
        self.assertEqual(ability.current_cooldown, 3)
        
        ability.tick_cooldown()
        self.assertEqual(ability.current_cooldown, 2)
        
        ability.tick_cooldown()
        ability.tick_cooldown()
        self.assertEqual(ability.current_cooldown, 0)
    
    def test_can_use_cooldown(self):
        """Test can_use with cooldown."""
        stats = Stats(attack=10)
        ability = Ability(cooldown=2)
        
        self.assertTrue(ability.can_use(stats))
        
        ability.use()
        self.assertFalse(ability.can_use(stats))
        
        ability.reset_cooldown()
        self.assertTrue(ability.can_use(stats))
    
    def test_can_use_energy_cost(self):
        """Test can_use with energy requirements."""
        stats = Stats()
        ability = Ability(energy_cost=20)
        
        # Insufficient energy
        self.assertFalse(ability.can_use(stats, user_energy=10))
        
        # Sufficient energy
        self.assertTrue(ability.can_use(stats, user_energy=25))
    
    def test_can_use_conditions(self):
        """Test can_use with stat conditions."""
        low_attack_stats = Stats(attack=5)
        high_attack_stats = Stats(attack=20)
        
        ability = Ability(conditions={'min_attack': 15})
        
        self.assertFalse(ability.can_use(low_attack_stats))
        self.assertTrue(ability.can_use(high_attack_stats))
    
    def test_calculate_damage_physical(self):
        """Test physical damage calculation."""
        ability = Ability(
            ability_type=AbilityType.PHYSICAL,
            power=40
        )
        
        damage = ability.calculate_damage(user_attack=20, target_defense=10)
        self.assertGreater(damage, 0)
        self.assertLessEqual(damage, 60)  # power + attack
    
    def test_calculate_damage_special(self):
        """Test special damage calculation."""
        ability = Ability(
            ability_type=AbilityType.SPECIAL,
            power=50
        )
        
        damage = ability.calculate_damage(user_attack=15, target_defense=10)
        self.assertGreater(damage, 0)
    
    def test_calculate_damage_non_damaging(self):
        """Test non-damaging abilities return 0 damage."""
        ability = Ability(ability_type=AbilityType.HEALING)
        
        damage = ability.calculate_damage(user_attack=20, target_defense=10)
        self.assertEqual(damage, 0)
    
    def test_ability_copy(self):
        """Test creating a copy of an ability."""
        original = Ability(name="Test", power=50, cooldown=2)
        copy = original.copy()
        
        self.assertEqual(copy.name, "Test")
        self.assertEqual(copy.power, 50)
        
        # Ensure it's a separate object
        copy.current_cooldown = 5
        self.assertEqual(original.current_cooldown, 0)
    
    def test_ability_serialization(self):
        """Test ability serialization."""
        ability = Ability(
            name="Thunder",
            ability_type=AbilityType.SPECIAL,
            target_type=TargetType.ENEMY,
            power=70,
            accuracy=85,
            cooldown=3,
            effects=[AbilityEffect(effect_type="damage", value=70)]
        )
        
        data = ability.to_dict()
        self.assertEqual(data['name'], "Thunder")
        self.assertEqual(data['power'], 70)
        self.assertEqual(data['ability_type'], "special")
        
        restored = Ability.from_dict(data)
        self.assertEqual(restored.name, "Thunder")
        self.assertEqual(restored.power, 70)
        self.assertEqual(restored.ability_type, AbilityType.SPECIAL)


class TestPredefinedAbilities(unittest.TestCase):
    """Test cases for predefined abilities."""
    
    def test_predefined_abilities_exist(self):
        """Test that predefined abilities are available."""
        self.assertIn('tackle', PREDEFINED_ABILITIES)
        self.assertIn('fireball', PREDEFINED_ABILITIES)
        self.assertIn('heal', PREDEFINED_ABILITIES)
    
    def test_create_ability_from_template(self):
        """Test creating ability from template."""
        tackle = create_ability('tackle')
        self.assertIsNotNone(tackle)
        self.assertEqual(tackle.name, "Tackle")
        self.assertEqual(tackle.ability_type, AbilityType.PHYSICAL)
    
    def test_create_ability_invalid_template(self):
        """Test creating ability with invalid template."""
        invalid = create_ability('nonexistent')
        self.assertIsNone(invalid)
    
    def test_ability_templates_are_copies(self):
        """Test that created abilities are copies, not references."""
        fireball1 = create_ability('fireball')
        fireball2 = create_ability('fireball')
        
        fireball1.use()
        self.assertNotEqual(fireball1.current_cooldown, fireball2.current_cooldown)


if __name__ == '__main__':
    unittest.main()
