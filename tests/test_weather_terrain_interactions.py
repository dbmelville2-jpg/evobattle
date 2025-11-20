"""
Unit tests for weather and terrain interaction systems.

Tests weather-responsive traits, terrain affinity tracking, and environmental synergies.
"""

import unittest
from src.models.trait import Trait
from src.models.creature import Creature
from src.models.stats import Stats
from src.models.weather_terrain_traits import (
    create_weather_trait, create_terrain_trait, create_synergy_trait,
    WEATHER_TRAITS, TERRAIN_TRAITS, SYNERGY_TRAITS
)
from src.systems.trait_effects_handler import TraitEffectsHandler
from src.systems.terrain_affinity_tracker import TerrainAffinityTracker
from src.models.environment import WeatherType, TerrainType, TimeOfDay, HazardType


class TestWeatherTraits(unittest.TestCase):
    """Test weather-responsive trait creation and effects."""
    
    def test_create_storm_dancer(self):
        """Test creating Storm Dancer trait."""
        trait = create_weather_trait("Storm Dancer")
        self.assertEqual(trait.name, "Storm Dancer")
        self.assertTrue(trait.interaction_effects.get('storm_dancer'))
        self.assertGreater(trait.interaction_effects.get('storm_speed_bonus'), 1.0)
    
    def test_create_rain_harvester(self):
        """Test creating Rain Harvester trait."""
        trait = create_weather_trait("Rain Harvester")
        self.assertEqual(trait.name, "Rain Harvester")
        self.assertTrue(trait.interaction_effects.get('rain_harvester'))
        self.assertGreater(trait.interaction_effects.get('rain_nutrition_bonus'), 1.0)
    
    def test_create_lightning_rod(self):
        """Test creating Lightning Rod trait."""
        trait = create_weather_trait("Lightning Rod")
        self.assertEqual(trait.name, "Lightning Rod")
        self.assertTrue(trait.interaction_effects.get('lightning_rod'))
        self.assertTrue(trait.interaction_effects.get('absorb_electrical_hazards'))
    
    def test_invalid_weather_trait(self):
        """Test creating invalid weather trait raises error."""
        with self.assertRaises(ValueError):
            create_weather_trait("Nonexistent Trait")


class TestTerrainTraits(unittest.TestCase):
    """Test terrain-adaptive trait creation and effects."""
    
    def test_create_forest_dweller(self):
        """Test creating Forest Dweller trait."""
        trait = create_terrain_trait("Forest Dweller")
        self.assertEqual(trait.name, "Forest Dweller")
        self.assertEqual(trait.interaction_effects.get('terrain_affinity'), 'forest')
        self.assertGreater(trait.interaction_effects.get('forest_stealth_bonus'), 0.0)
    
    def test_create_desert_runner(self):
        """Test creating Desert Runner trait."""
        trait = create_terrain_trait("Desert Runner")
        self.assertEqual(trait.name, "Desert Runner")
        self.assertEqual(trait.interaction_effects.get('terrain_affinity'), 'desert')
        self.assertGreater(trait.interaction_effects.get('desert_speed_bonus'), 1.0)
    
    def test_create_amphibious(self):
        """Test creating Amphibious trait."""
        trait = create_terrain_trait("Amphibious")
        self.assertEqual(trait.name, "Amphibious")
        self.assertTrue(trait.interaction_effects.get('amphibious'))


class TestWeatherBonuses(unittest.TestCase):
    """Test weather bonus calculations."""
    
    def setUp(self):
        """Set up test creatures and handler."""
        self.handler = TraitEffectsHandler()
        
        # Create creature with Storm Dancer trait
        storm_trait = create_weather_trait("Storm Dancer")
        self.storm_creature = Creature(name="Storm Dancer", traits=[storm_trait])
        
        # Create creature with Rain Harvester trait
        rain_trait = create_weather_trait("Rain Harvester")
        self.rain_creature = Creature(name="Rain Harvester", traits=[rain_trait])
    
    def test_storm_dancer_speed_boost(self):
        """Test Storm Dancer gets speed boost in storms."""
        bonus = self.handler.get_weather_bonus(
            self.storm_creature,
            WeatherType.STORMY,
            'speed'
        )
        self.assertGreater(bonus, 1.0)
        self.assertAlmostEqual(bonus, 1.4, places=1)
    
    def test_storm_dancer_damage_boost(self):
        """Test Storm Dancer gets damage boost in storms."""
        bonus = self.handler.get_weather_bonus(
            self.storm_creature,
            WeatherType.STORMY,
            'damage'
        )
        self.assertGreater(bonus, 1.0)
        self.assertAlmostEqual(bonus, 1.2, places=1)
    
    def test_storm_dancer_no_bonus_in_clear(self):
        """Test Storm Dancer gets no bonus in clear weather."""
        bonus = self.handler.get_weather_bonus(
            self.storm_creature,
            WeatherType.CLEAR,
            'speed'
        )
        self.assertEqual(bonus, 1.0)
    
    def test_rain_harvester_nutrition_boost(self):
        """Test Rain Harvester gets nutrition boost in rain."""
        bonus = self.handler.get_weather_bonus(
            self.rain_creature,
            WeatherType.RAINY,
            'nutrition'
        )
        self.assertGreater(bonus, 1.0)
        self.assertAlmostEqual(bonus, 1.5, places=1)


class TestTerrainBonuses(unittest.TestCase):
    """Test terrain bonus calculations."""
    
    def setUp(self):
        """Set up test creatures and handler."""
        self.handler = TraitEffectsHandler()
        
        # Create creature with Forest Dweller trait
        forest_trait = create_terrain_trait("Forest Dweller")
        self.forest_creature = Creature(name="Forest Dweller", traits=[forest_trait])
        
        # Create creature with Desert Runner trait
        desert_trait = create_terrain_trait("Desert Runner")
        self.desert_creature = Creature(name="Desert Runner", traits=[desert_trait])
    
    def test_forest_dweller_stealth_bonus(self):
        """Test Forest Dweller gets stealth bonus in forest."""
        bonus = self.handler.get_terrain_bonus(
            self.forest_creature,
            TerrainType.FOREST,
            'stealth'
        )
        self.assertGreater(bonus, 1.0)
    
    def test_forest_dweller_no_bonus_in_desert(self):
        """Test Forest Dweller gets no bonus in desert."""
        bonus = self.handler.get_terrain_bonus(
            self.forest_creature,
            TerrainType.DESERT,
            'stealth'
        )
        self.assertEqual(bonus, 1.0)
    
    def test_desert_runner_speed_boost(self):
        """Test Desert Runner gets speed boost in desert."""
        bonus = self.handler.get_terrain_bonus(
            self.desert_creature,
            TerrainType.DESERT,
            'speed'
        )
        self.assertGreater(bonus, 1.0)
        self.assertAlmostEqual(bonus, 1.3, places=1)


class TestHazardAbsorption(unittest.TestCase):
    """Test hazard absorption mechanics."""
    
    def setUp(self):
        """Set up test creatures and handler."""
        self.handler = TraitEffectsHandler()
        
        # Create creature with Lightning Rod trait
        lightning_trait = create_weather_trait("Lightning Rod")
        self.lightning_creature = Creature(name="Lightning Rod", traits=[lightning_trait])
        
        # Create normal creature
        self.normal_creature = Creature(name="Normal", traits=[])
    
    def test_lightning_rod_absorbs_electrical(self):
        """Test Lightning Rod absorbs electrical hazards."""
        should_absorb = self.handler.should_absorb_hazard(
            self.lightning_creature,
            HazardType.ELECTRICAL
        )
        self.assertTrue(should_absorb)
    
    def test_normal_creature_no_absorption(self):
        """Test normal creature doesn't absorb hazards."""
        should_absorb = self.handler.should_absorb_hazard(
            self.normal_creature,
            HazardType.ELECTRICAL
        )
        self.assertFalse(should_absorb)
    
    def test_lightning_rod_absorption_rate(self):
        """Test Lightning Rod has correct absorption rate."""
        rate = self.handler.get_hazard_absorption_rate(
            self.lightning_creature,
            HazardType.ELECTRICAL
        )
        self.assertGreater(rate, 0.0)
        self.assertLessEqual(rate, 1.0)


class TestTerrainAffinityTracker(unittest.TestCase):
    """Test terrain affinity tracking system."""
    
    def setUp(self):
        """Set up tracker."""
        self.tracker = TerrainAffinityTracker()
    
    def test_track_terrain_time(self):
        """Test tracking time in terrain."""
        self.tracker.update("creature1", TerrainType.FOREST, 10.0)
        self.tracker.update("creature1", TerrainType.FOREST, 25.0)
        
        total = self.tracker.get_total_time("creature1")
        self.assertEqual(total, 35.0)
    
    def test_get_preferred_terrain(self):
        """Test getting preferred terrain."""
        # Spend time in multiple terrains
        self.tracker.update("creature1", TerrainType.FOREST, 50.0)
        self.tracker.update("creature1", TerrainType.DESERT, 10.0)
        
        preferred = self.tracker.get_preferred_terrain("creature1")
        self.assertEqual(preferred, TerrainType.FOREST)
    
    def test_no_preference_insufficient_time(self):
        """Test no preference with insufficient time."""
        self.tracker.update("creature1", TerrainType.FOREST, 5.0)
        
        preferred = self.tracker.get_preferred_terrain("creature1")
        self.assertIsNone(preferred)
    
    def test_terrain_bonus(self):
        """Test terrain bonus calculation."""
        # Establish preference
        self.tracker.update("creature1", TerrainType.FOREST, 50.0)
        
        # In preferred terrain
        bonus = self.tracker.get_terrain_bonus("creature1", TerrainType.FOREST)
        self.assertGreater(bonus, 1.0)
        
        # Not in preferred terrain
        bonus = self.tracker.get_terrain_bonus("creature1", TerrainType.DESERT)
        self.assertEqual(bonus, 1.0)
    
    def test_terrain_distribution(self):
        """Test terrain distribution calculation."""
        self.tracker.update("creature1", TerrainType.FOREST, 30.0)
        self.tracker.update("creature1", TerrainType.DESERT, 20.0)
        self.tracker.update("creature1", TerrainType.MARSH, 50.0)
        
        dist = self.tracker.get_terrain_distribution("creature1")
        
        self.assertAlmostEqual(dist[TerrainType.FOREST], 0.3, places=1)
        self.assertAlmostEqual(dist[TerrainType.DESERT], 0.2, places=1)
        self.assertAlmostEqual(dist[TerrainType.MARSH], 0.5, places=1)
    
    def test_inherit_preference_same_parents(self):
        """Test offspring inherits preference from parents."""
        # Both parents prefer forest
        self.tracker.update("parent1", TerrainType.FOREST, 50.0)
        self.tracker.update("parent2", TerrainType.FOREST, 50.0)
        
        # Offspring inherits
        self.tracker.inherit_preference("offspring", "parent1", "parent2")
        
        # Offspring should have forest preference
        preferred = self.tracker.get_preferred_terrain("offspring")
        self.assertEqual(preferred, TerrainType.FOREST)
    
    def test_remove_creature(self):
        """Test removing creature data."""
        self.tracker.update("creature1", TerrainType.FOREST, 50.0)
        self.tracker.remove_creature("creature1")
        
        total = self.tracker.get_total_time("creature1")
        self.assertEqual(total, 0.0)
    
    def test_serialization(self):
        """Test tracker serialization."""
        self.tracker.update("creature1", TerrainType.FOREST, 50.0)
        self.tracker.update("creature2", TerrainType.DESERT, 30.0)
        
        # Serialize
        data = self.tracker.to_dict()
        
        # Deserialize
        new_tracker = TerrainAffinityTracker.from_dict(data)
        
        # Verify data preserved
        self.assertEqual(
            new_tracker.get_total_time("creature1"),
            50.0
        )
        self.assertEqual(
            new_tracker.get_preferred_terrain("creature2"),
            TerrainType.DESERT
        )


class TestEnvironmentalSynergies(unittest.TestCase):
    """Test environmental synergy bonuses."""
    
    def setUp(self):
        """Set up test creatures and handler."""
        self.handler = TraitEffectsHandler()
        
        # Create creature with Nocturnal trait
        nocturnal_trait = create_synergy_trait("Nocturnal")
        self.nocturnal_creature = Creature(name="Nocturnal", traits=[nocturnal_trait])
    
    def test_nocturnal_night_bonus(self):
        """Test Nocturnal gets bonus at night."""
        bonus = self.handler.get_environmental_synergy_bonus(
            self.nocturnal_creature,
            WeatherType.CLEAR,
            TerrainType.GRASS,
            TimeOfDay.NIGHT
        )
        self.assertGreater(bonus, 1.0)
    
    def test_nocturnal_day_penalty(self):
        """Test Nocturnal gets penalty during day."""
        bonus = self.handler.get_environmental_synergy_bonus(
            self.nocturnal_creature,
            WeatherType.CLEAR,
            TerrainType.GRASS,
            TimeOfDay.DAY
        )
        self.assertLess(bonus, 1.0)


if __name__ == '__main__':
    unittest.main()
