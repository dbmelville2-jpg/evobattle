"""
Test that trait effects are properly applied in combat.
"""

import unittest
from src.models.creature import Creature
from src.models.trait import Trait
from src.systems.trait_effects_handler import TraitEffectsHandler


class TestTraitEffectsHandler(unittest.TestCase):
    """Test TraitEffectsHandler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = TraitEffectsHandler()
    
    def test_pack_hunter_bonus(self):
        """Test that pack_hunter trait increases damage with allies."""
        # Create creature with pack_hunter trait
        pack_hunter_trait = Trait(
            name="Pack Hunter",
            description="Stronger when fighting with allies",
            trait_type="behavioral",
            interaction_effects={
                'pack_hunter': True,
                'pack_coordination': 1.3
            }
        )
        
        attacker = Creature(name="Pack Hunter")
        attacker.traits = [pack_hunter_trait]
        defender = Creature(name="Defender")
        
        # Test with allies nearby
        modifier_with_allies = self.handler.get_combat_damage_modifier(
            attacker,
            defender,
            allies_nearby=2,
            enemies_nearby=1,
            family_nearby=0
        )
        
        # Should get bonus
        self.assertGreater(modifier_with_allies, 1.0)
        
        # Test without allies
        modifier_alone = self.handler.get_combat_damage_modifier(
            attacker,
            defender,
            allies_nearby=0,
            enemies_nearby=1,
            family_nearby=0
        )
        
        # Should not get bonus when alone
        self.assertEqual(modifier_alone, 1.0)
    
    def test_loner_strength_bonus(self):
        """Test that loner_strength trait increases damage when alone."""
        loner_trait = Trait(
            name="Loner",
            description="Stronger when fighting alone",
            trait_type="behavioral",
            interaction_effects={
                'loner_strength': True,
                'isolation_resilience': 1.3
            }
        )
        
        attacker = Creature(name="Loner")
        attacker.traits = [loner_trait]
        defender = Creature(name="Defender")
        
        # Test when alone
        modifier_alone = self.handler.get_combat_damage_modifier(
            attacker,
            defender,
            allies_nearby=0,
            enemies_nearby=1,
            family_nearby=0
        )
        
        # Should get bonus
        self.assertGreater(modifier_alone, 1.0)
        
        # Test with allies
        modifier_with_allies = self.handler.get_combat_damage_modifier(
            attacker,
            defender,
            allies_nearby=2,
            enemies_nearby=1,
            family_nearby=0
        )
        
        # Should not get bonus with allies
        self.assertEqual(modifier_with_allies, 1.0)
    
    def test_combat_avoidance(self):
        """Test that scaredy_cat and very low hunger cause combat avoidance."""
        scaredy_trait = Trait(
            name="Scaredy Cat",
            description="Avoids combat",
            trait_type="behavioral",
            interaction_effects={
                'scaredy_cat': True
            }
        )
        
        creature = Creature(name="Scaredy Creature")
        creature.traits = [scaredy_trait]
        
        # Should avoid combat with scaredy_cat trait
        should_avoid = self.handler.should_avoid_combat(
            creature,
            hunger_level=0.8,  # Well fed
            allies_nearby=0
        )
        
        self.assertTrue(should_avoid)
        
        # Test cautious creature with very low hunger
        cautious_trait = Trait(
            name="Cautious",
            description="Cautious when low on resources",
            trait_type="behavioral",
            interaction_effects={
                'cautious_behavior': True
            }
        )
        
        cautious_creature = Creature(name="Cautious Creature")
        cautious_creature.traits = [cautious_trait]
        
        # Should avoid when very low hunger
        should_avoid_low = self.handler.should_avoid_combat(
            cautious_creature,
            hunger_level=0.1,  # Very low hunger
            allies_nearby=0
        )
        self.assertTrue(should_avoid_low)
        
        # Should NOT avoid when moderate hunger
        should_not_avoid = self.handler.should_avoid_combat(
            cautious_creature,
            hunger_level=0.5,  # Moderate hunger
            allies_nearby=0
        )
        self.assertFalse(should_not_avoid)
    
    def test_food_sharing_willingness(self):
        """Test food sharing willingness based on traits."""
        social_trait = Trait(
            name="Social",
            description="Shares with allies",
            trait_type="behavioral",
            interaction_effects={
                'sharing_willingness': 0.8
            }
        )
        
        creature = Creature(name="Social Creature")
        creature.traits = [social_trait]
        
        # Test sharing with non-family
        willingness = self.handler.get_food_sharing_willingness(
            creature,
            target_is_family=False
        )
        
        self.assertGreater(willingness, 0.0)
        
        # Test sharing with family (should be higher)
        willingness_family = self.handler.get_food_sharing_willingness(
            creature,
            target_is_family=True
        )
        
        self.assertGreater(willingness_family, willingness)
    
    def test_executioner_bonus(self):
        """Test executioner trait bonus vs low HP targets."""
        executioner_trait = Trait(
            name="Executioner",
            description="Bonus vs low HP enemies",
            trait_type="offensive",
            interaction_effects={
                'execute_threshold': 0.3,
                'execute_damage_bonus': 1.5
            }
        )
        
        attacker = Creature(name="Executioner")
        attacker.traits = [executioner_trait]
        
        # Create low HP defender
        defender = Creature(name="Weak Defender")
        defender.stats.hp = 20
        defender.stats.max_hp = 100  # 20% HP
        
        modifier = self.handler.get_combat_damage_modifier(
            attacker,
            defender,
            allies_nearby=0,
            enemies_nearby=1,
            family_nearby=0
        )
        
        # Should get execute bonus
        self.assertGreater(modifier, 1.0)


if __name__ == '__main__':
    unittest.main()
