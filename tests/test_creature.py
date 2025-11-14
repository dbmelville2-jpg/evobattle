"""
Unit tests for Creature model.
"""

import unittest
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatModifier, StatGrowth
from src.models.ability import Ability, AbilityType
from src.models.trait import Trait


class TestCreatureType(unittest.TestCase):
    """Test cases for CreatureType class."""
    
    def test_creature_type_initialization(self):
        """Test creating a CreatureType."""
        ctype = CreatureType(
            name="Dragon",
            description="A powerful dragon",
            type_tags=["fire", "flying"],
            evolution_stage=2
        )
        self.assertEqual(ctype.name, "Dragon")
        self.assertIn("fire", ctype.type_tags)
        self.assertEqual(ctype.evolution_stage, 2)
    
    def test_creature_type_serialization(self):
        """Test CreatureType serialization."""
        ctype = CreatureType(
            name="Phoenix",
            type_tags=["fire", "bird"]
        )
        data = ctype.to_dict()
        
        self.assertEqual(data['name'], "Phoenix")
        self.assertIn("fire", data['type_tags'])
        
        restored = CreatureType.from_dict(data)
        self.assertEqual(restored.name, "Phoenix")
        self.assertIn("fire", restored.type_tags)


class TestCreature(unittest.TestCase):
    """Test cases for Creature class."""
    
    def test_creature_initialization(self):
        """Test creating a Creature."""
        creature = Creature(name="TestCreature", level=1)
        self.assertEqual(creature.name, "TestCreature")
        self.assertEqual(creature.level, 1)
        self.assertIsNotNone(creature.creature_id)
        self.assertTrue(creature.is_alive())
    
    def test_creature_with_custom_stats(self):
        """Test creating creature with custom stats."""
        custom_stats = Stats(max_hp=200, hp=200, attack=25)
        creature = Creature(name="Strong", base_stats=custom_stats)
        
        self.assertEqual(creature.stats.max_hp, 200)
        self.assertEqual(creature.stats.attack, 25)
    
    def test_add_and_get_ability(self):
        """Test adding and retrieving abilities."""
        creature = Creature(name="Fighter")
        ability = Ability(name="Punch", power=40)
        
        creature.add_ability(ability)
        self.assertEqual(len(creature.abilities), 1)
        
        retrieved = creature.get_ability("Punch")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Punch")
    
    def test_remove_ability(self):
        """Test removing an ability."""
        creature = Creature(name="Mage")
        ability = Ability(name="Fireball")
        
        creature.add_ability(ability)
        self.assertEqual(len(creature.abilities), 1)
        
        removed = creature.remove_ability("Fireball")
        self.assertTrue(removed)
        self.assertEqual(len(creature.abilities), 0)
        
        # Try removing non-existent ability
        removed = creature.remove_ability("Lightning")
        self.assertFalse(removed)
    
    def test_add_trait(self):
        """Test adding traits to creature."""
        creature = Creature(name="Beast")
        trait = Trait(
            name="Strong",
            strength_modifier=1.2,
            defense_modifier=1.1
        )
        
        initial_attack = creature.stats.attack
        creature.add_trait(trait)
        
        # Stats should be recalculated with trait
        self.assertTrue(creature.has_trait("Strong"))
        self.assertEqual(len(creature.traits), 1)
    
    def test_has_trait(self):
        """Test checking for trait presence."""
        creature = Creature(name="Scout")
        trait = Trait(name="Quick")
        
        self.assertFalse(creature.has_trait("Quick"))
        creature.add_trait(trait)
        self.assertTrue(creature.has_trait("Quick"))
    
    def test_add_modifier(self):
        """Test adding stat modifiers."""
        creature = Creature(name="Warrior")
        base_attack = creature.stats.attack
        
        modifier = StatModifier(
            name="Battle Rage",
            duration=3,
            attack_multiplier=1.5
        )
        creature.add_modifier(modifier)
        
        self.assertGreater(creature.stats.attack, base_attack)
        self.assertEqual(len(creature.active_modifiers), 1)
    
    def test_remove_modifier(self):
        """Test removing stat modifiers."""
        creature = Creature(name="Knight")
        modifier = StatModifier(name="Shield Buff", defense_multiplier=1.3)
        
        creature.add_modifier(modifier)
        self.assertEqual(len(creature.active_modifiers), 1)
        
        removed = creature.remove_modifier("Shield Buff")
        self.assertTrue(removed)
        self.assertEqual(len(creature.active_modifiers), 0)
    
    def test_tick_modifiers(self):
        """Test modifier duration management."""
        creature = Creature(name="Mage")
        
        modifier1 = StatModifier(name="Temp Buff", duration=2)
        modifier2 = StatModifier(name="Permanent", duration=-1)
        
        creature.add_modifier(modifier1)
        creature.add_modifier(modifier2)
        
        self.assertEqual(len(creature.active_modifiers), 2)
        
        creature.tick_modifiers()
        self.assertEqual(modifier1.duration, 1)
        
        creature.tick_modifiers()
        # modifier1 should be expired and removed
        self.assertEqual(len(creature.active_modifiers), 1)
        self.assertEqual(creature.active_modifiers[0].name, "Permanent")
    
    def test_get_effective_stats(self):
        """Test calculating effective stats with traits and modifiers."""
        creature = Creature(name="Test")
        base_attack = creature.base_stats.attack
        
        trait = Trait(name="Power", strength_modifier=1.5)
        modifier = StatModifier(name="Buff", attack_bonus=10)
        
        creature.add_trait(trait)
        creature.add_modifier(modifier)
        
        effective = creature.get_effective_stats()
        # Attack should be affected by both trait and modifier
        self.assertGreater(effective.attack, base_attack)
    
    def test_gain_experience(self):
        """Test gaining experience."""
        creature = Creature(name="Learner", level=1)
        
        # Add some XP but not enough to level
        leveled = creature.gain_experience(50)
        self.assertFalse(leveled)
        self.assertEqual(creature.experience, 50)
        self.assertEqual(creature.level, 1)
    
    def test_level_up(self):
        """Test leveling up."""
        creature = Creature(name="Growing", level=1)
        initial_max_hp = creature.stats.max_hp
        
        creature.level_up()
        
        self.assertEqual(creature.level, 2)
        self.assertEqual(creature.experience, 0)
        # Stats should increase with level
        self.assertGreater(creature.stats.max_hp, initial_max_hp)
        # Should be fully healed
        self.assertEqual(creature.stats.hp, creature.stats.max_hp)
    
    def test_level_up_via_experience(self):
        """Test leveling up through experience gain."""
        creature = Creature(name="Fighter", level=1)
        
        # Give enough XP to level up (level 1 needs 100 XP)
        leveled = creature.gain_experience(100)
        
        self.assertTrue(leveled)
        self.assertEqual(creature.level, 2)
    
    def test_is_alive(self):
        """Test alive status checking."""
        creature = Creature(name="Test")
        self.assertTrue(creature.is_alive())
        
        creature.stats.take_damage(creature.stats.max_hp)
        self.assertFalse(creature.is_alive())
    
    def test_rest(self):
        """Test resting to restore energy and HP."""
        creature = Creature(name="Tired", energy=50, max_energy=100)
        creature.stats.take_damage(50)
        
        ability = Ability(name="Attack", cooldown=3)
        ability.use()
        creature.add_ability(ability)
        
        creature.rest()
        
        self.assertEqual(creature.energy, 100)
        self.assertGreater(creature.stats.hp, creature.stats.max_hp // 2)
        # Cooldowns should be reset
        self.assertEqual(creature.abilities[0].current_cooldown, 0)
    
    def test_creature_serialization(self):
        """Test creature serialization and deserialization."""
        creature = Creature(
            name="Serializable",
            level=5,
            experience=250
        )
        creature.add_ability(Ability(name="Tackle", power=40))
        creature.add_trait(Trait(name="Swift", speed_modifier=1.2))
        
        data = creature.to_dict()
        
        self.assertEqual(data['name'], "Serializable")
        self.assertEqual(data['level'], 5)
        self.assertEqual(len(data['abilities']), 1)
        self.assertEqual(len(data['traits']), 1)
        
        restored = Creature.from_dict(data)
        self.assertEqual(restored.name, "Serializable")
        self.assertEqual(restored.level, 5)
        self.assertEqual(len(restored.abilities), 1)
        self.assertEqual(len(restored.traits), 1)
        self.assertEqual(restored.creature_id, creature.creature_id)


if __name__ == '__main__':
    unittest.main()
