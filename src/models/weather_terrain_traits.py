"""
Weather and Terrain Trait Definitions

Centralized definitions for weather-responsive and terrain-adaptive traits.
These traits create deeper ecosystem interactions by responding to environmental conditions.
"""

from src.models.trait import Trait
from src.models.environment import TerrainType, WeatherType
from typing import Dict, Any


# Weather-Responsive Traits
WEATHER_TRAITS = {
    "Storm Dancer": {
        "description": "Thrives in stormy weather, gaining speed and power from lightning",
        "trait_type": "weather_adaptive",
        "strength_modifier": 1.0,
        "speed_modifier": 1.1,
        "defense_modifier": 1.0,
        "rarity": "rare",
        "interaction_effects": {
            "storm_dancer": True,
            "storm_speed_bonus": 1.4,  # 40% speed boost in storms
            "storm_damage_bonus": 1.2,  # 20% damage boost in storms
        }
    },
    
    "Rain Harvester": {
        "description": "Extracts extra nutrition from food during rainy weather",
        "trait_type": "weather_adaptive",
        "strength_modifier": 1.0,
        "speed_modifier": 1.0,
        "defense_modifier": 1.0,
        "rarity": "uncommon",
        "interaction_effects": {
            "rain_harvester": True,
            "rain_nutrition_bonus": 1.5,  # 50% more nutrition in rain
            "rain_hunger_reduction": 0.9,  # 10% slower hunger in rain
        }
    },
    
    "Drought Survivor": {
        "description": "Adapted to arid conditions, requires less food in drought",
        "trait_type": "weather_adaptive",
        "strength_modifier": 1.0,
        "speed_modifier": 1.0,
        "defense_modifier": 1.1,
        "rarity": "uncommon",
        "interaction_effects": {
            "drought_survivor": True,
            "drought_hunger_reduction": 0.7,  # 30% slower hunger in drought
            "desert_speed_bonus": 1.2,  # 20% speed in desert terrain
        }
    },
    
    "Fog Walker": {
        "description": "Uses fog for stealth, harder to detect in low visibility",
        "trait_type": "weather_adaptive",
        "strength_modifier": 1.0,
        "speed_modifier": 1.1,
        "defense_modifier": 1.0,
        "rarity": "rare",
        "interaction_effects": {
            "fog_walker": True,
            "fog_stealth_bonus": 0.5,  # 50% harder to detect in fog
            "fog_evasion_bonus": 1.3,  # 30% better dodge in fog
        }
    },
    
    "Lightning Rod": {
        "description": "Absorbs electrical energy from storms, converting hazard damage to power",
        "trait_type": "weather_adaptive",
        "strength_modifier": 1.1,
        "speed_modifier": 1.0,
        "defense_modifier": 1.0,
        "rarity": "legendary",
        "interaction_effects": {
            "lightning_rod": True,
            "absorb_electrical_hazards": True,
            "electrical_damage_to_energy": 0.8,  # Convert 80% of electrical damage to HP
            "storm_attraction": True,  # Becomes visible beacon in storms
        }
    },
}


# Terrain-Adaptive Traits
TERRAIN_TRAITS = {
    "Forest Dweller": {
        "description": "Evolved for forest life, gains stealth and cover bonuses in woods",
        "trait_type": "terrain_adaptive",
        "strength_modifier": 1.0,
        "speed_modifier": 0.95,
        "defense_modifier": 1.1,
        "rarity": "common",
        "interaction_effects": {
            "terrain_affinity": "forest",
            "forest_stealth_bonus": 0.3,  # 30% harder to detect in forest
            "forest_cover_bonus": 0.2,  # 20% damage reduction in forest
            "forest_movement_bonus": 1.2,  # Negate forest movement penalty
        }
    },
    
    "Desert Runner": {
        "description": "Built for speed in open terrain, excels in desert conditions",
        "trait_type": "terrain_adaptive",
        "strength_modifier": 0.95,
        "speed_modifier": 1.15,
        "defense_modifier": 0.95,
        "rarity": "common",
        "interaction_effects": {
            "terrain_affinity": "desert",
            "desert_speed_bonus": 1.3,  # 30% speed boost in desert
            "heat_resistance": 0.7,  # 30% less hunger in hot weather
            "desert_stamina": 1.2,  # 20% more energy in desert
        }
    },
    
    "Marsh Wader": {
        "description": "Adapted to swamps, immune to toxins and moves freely in marshes",
        "trait_type": "terrain_adaptive",
        "strength_modifier": 1.0,
        "speed_modifier": 0.9,
        "defense_modifier": 1.1,
        "rarity": "uncommon",
        "interaction_effects": {
            "terrain_affinity": "marsh",
            "marsh_movement_bonus": 2.0,  # Negate marsh movement penalty
            "toxin_immunity": 0.8,  # 80% resistance to toxic pellets
            "marsh_resource_bonus": 1.3,  # 30% better at finding food in marsh
        }
    },
    
    "Rock Climber": {
        "description": "Sure-footed on rocky terrain, gains defensive bonuses on highlands",
        "trait_type": "terrain_adaptive",
        "strength_modifier": 1.1,
        "speed_modifier": 0.95,
        "defense_modifier": 1.15,
        "rarity": "uncommon",
        "interaction_effects": {
            "terrain_affinity": "rocky",
            "rocky_movement_bonus": 1.4,  # Negate rocky movement penalty
            "rocky_defense_bonus": 1.2,  # 20% more defense on rocky terrain
            "fall_resistance": True,  # Immune to fall damage (if implemented)
        }
    },
    
    "Amphibious": {
        "description": "Equally at home in water and on land",
        "trait_type": "terrain_adaptive",
        "strength_modifier": 1.0,
        "speed_modifier": 1.0,
        "defense_modifier": 1.0,
        "rarity": "rare",
        "interaction_effects": {
            "terrain_affinity": "water",
            "water_movement_bonus": 3.0,  # Normal speed in water
            "water_breathing": True,  # Can stay in water indefinitely
            "amphibious": True,  # No penalties in any terrain
        }
    },
}


# Environmental Synergy Traits
SYNERGY_TRAITS = {
    "Toxin Farmer": {
        "description": "Can cultivate toxic pellets in marsh environments",
        "trait_type": "environmental_synergy",
        "strength_modifier": 1.0,
        "speed_modifier": 1.0,
        "defense_modifier": 1.0,
        "rarity": "legendary",
        "interaction_effects": {
            "toxin_farmer": True,
            "toxic_pellet_spawn_chance": 0.3,  # 30% chance to spawn toxic pellet after eating
            "marsh_synergy": True,  # Requires marsh terrain
            "rain_synergy": True,  # Enhanced by rain
        }
    },
    
    "Illusionist": {
        "description": "Creates mirages in desert heat to confuse enemies",
        "trait_type": "environmental_synergy",
        "strength_modifier": 0.9,
        "speed_modifier": 1.1,
        "defense_modifier": 1.0,
        "rarity": "legendary",
        "interaction_effects": {
            "illusionist": True,
            "desert_synergy": True,  # Requires desert terrain
            "drought_synergy": True,  # Enhanced by drought
            "decoy_spawn_chance": 0.2,  # 20% chance to create fake pellet
            "evasion_bonus": 1.4,  # 40% better dodge in desert + drought
        }
    },
    
    "Gardener": {
        "description": "Cultivates symbiotic relationship with pellets",
        "trait_type": "environmental_synergy",
        "strength_modifier": 1.0,
        "speed_modifier": 0.95,
        "defense_modifier": 1.0,
        "rarity": "rare",
        "interaction_effects": {
            "gardener": True,
            "pollination_bonus": 1.5,  # Pellets reproduce 50% faster when nearby
            "symbiotic_nutrition": 1.3,  # 30% more nutrition from pollinator pellets
            "hp_regen_near_pellets": 0.5,  # Slow HP regen when near pellets
        }
    },
    
    "Nocturnal": {
        "description": "Thrives in darkness, gains bonuses at night",
        "trait_type": "environmental_synergy",
        "strength_modifier": 1.0,
        "speed_modifier": 1.0,
        "defense_modifier": 1.0,
        "rarity": "uncommon",
        "interaction_effects": {
            "nocturnal": True,
            "night_damage_bonus": 1.3,  # 30% more damage at night
            "night_speed_bonus": 1.2,  # 20% more speed at night
            "day_penalty": 0.8,  # 20% penalty during day
            "bioluminescent_vision": True,  # Can see bioluminescent pellets
        }
    },
}


def create_weather_trait(trait_name: str) -> Trait:
    """
    Create a weather-responsive trait instance.
    
    Args:
        trait_name: Name of the trait from WEATHER_TRAITS
        
    Returns:
        Trait instance with weather-responsive effects
    """
    if trait_name not in WEATHER_TRAITS:
        raise ValueError(f"Unknown weather trait: {trait_name}")
    
    config = WEATHER_TRAITS[trait_name]
    return Trait(
        name=trait_name,
        description=config["description"],
        trait_type=config["trait_type"],
        strength_modifier=config["strength_modifier"],
        speed_modifier=config["speed_modifier"],
        defense_modifier=config["defense_modifier"],
        rarity=config["rarity"],
        interaction_effects=config["interaction_effects"]
    )


def create_terrain_trait(trait_name: str) -> Trait:
    """
    Create a terrain-adaptive trait instance.
    
    Args:
        trait_name: Name of the trait from TERRAIN_TRAITS
        
    Returns:
        Trait instance with terrain-adaptive effects
    """
    if trait_name not in TERRAIN_TRAITS:
        raise ValueError(f"Unknown terrain trait: {trait_name}")
    
    config = TERRAIN_TRAITS[trait_name]
    return Trait(
        name=trait_name,
        description=config["description"],
        trait_type=config["trait_type"],
        strength_modifier=config["strength_modifier"],
        speed_modifier=config["speed_modifier"],
        defense_modifier=config["defense_modifier"],
        rarity=config["rarity"],
        interaction_effects=config["interaction_effects"]
    )


def create_synergy_trait(trait_name: str) -> Trait:
    """
    Create an environmental synergy trait instance.
    
    Args:
        trait_name: Name of the trait from SYNERGY_TRAITS
        
    Returns:
        Trait instance with environmental synergy effects
    """
    if trait_name not in SYNERGY_TRAITS:
        raise ValueError(f"Unknown synergy trait: {trait_name}")
    
    config = SYNERGY_TRAITS[trait_name]
    return Trait(
        name=trait_name,
        description=config["description"],
        trait_type=config["trait_type"],
        strength_modifier=config["strength_modifier"],
        speed_modifier=config["speed_modifier"],
        defense_modifier=config["defense_modifier"],
        rarity=config["rarity"],
        interaction_effects=config["interaction_effects"]
    )


def get_all_environmental_traits() -> Dict[str, Dict[str, Any]]:
    """
    Get all environmental trait definitions.
    
    Returns:
        Dictionary of all weather, terrain, and synergy traits
    """
    return {
        **WEATHER_TRAITS,
        **TERRAIN_TRAITS,
        **SYNERGY_TRAITS
    }
