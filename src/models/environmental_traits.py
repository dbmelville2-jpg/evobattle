"""
Environmental adaptation traits for creatures.

These traits allow creatures to better survive and thrive in different
environmental conditions (weather, terrain, time of day, hazards).

Integrates with:
- Existing trait system (src/models/trait.py)
- Environment system (src/models/environment.py)
- Ecosystem traits (src/models/ecosystem_traits.py)
- Genetics and breeding (src/systems/breeding.py)
"""

from .trait import Trait

# ===========================
# WEATHER ADAPTATION TRAITS
# ===========================

COLD_BLOODED = Trait(
    name="Cold Blooded",
    description="Performance varies with temperature: faster in heat, slower in cold. +20% speed above 25°C, -20% below 10°C",
    trait_type="environmental",
    rarity="common"
)

WARM_BLOODED = Trait(
    name="Warm Blooded",
    description="Maintains consistent performance in all temperatures. +10% defense, immune to temperature effects",
    trait_type="environmental",
    defense_modifier=1.1,
    rarity="uncommon"
)

THICK_FUR = Trait(
    name="Thick Fur",
    description="Insulated against cold. Reduces hunger in cold weather by 30%, +15% defense",
    trait_type="environmental",
    defense_modifier=1.15,
    rarity="uncommon"
)

HEAT_RESISTANT = Trait(
    name="Heat Resistant",
    description="Thrives in hot conditions. +25% speed in temperatures above 30°C, reduced hunger in heat",
    trait_type="environmental",
    speed_modifier=1.05,
    rarity="uncommon"
)

STORM_WALKER = Trait(
    name="Storm Walker",
    description="Unaffected by stormy weather. Normal movement speed in storms, +10% attack during storms",
    trait_type="environmental",
    strength_modifier=1.05,
    rarity="rare"
)

DROUGHT_SURVIVOR = Trait(
    name="Drought Survivor",
    description="Efficient water usage. 40% slower hunger during droughts, can survive longer without food",
    trait_type="environmental",
    rarity="uncommon"
)

# ===========================
# TERRAIN ADAPTATION TRAITS
# ===========================

AQUATIC = Trait(
    name="Aquatic",
    description="Adapted to water. +100% speed in water terrain, -30% speed on land",
    trait_type="environmental",
    rarity="uncommon"
)

ROCK_CLIMBER = Trait(
    name="Rock Climber",
    description="Expert at rocky terrain. +50% speed on rocky terrain, +20% defense when in rocks",
    trait_type="environmental",
    defense_modifier=1.1,
    rarity="uncommon"
)

FOREST_DWELLER = Trait(
    name="Forest Dweller",
    description="At home in forests. +40% speed in forests, +25% stealth in forest terrain",
    trait_type="environmental",
    speed_modifier=1.05,
    rarity="common"
)

DESERT_ADAPTED = Trait(
    name="Desert Adapted",
    description="Thrives in deserts. +30% speed in desert, 50% reduced hunger in arid conditions",
    trait_type="environmental",
    speed_modifier=1.1,
    rarity="uncommon"
)

MARSH_NAVIGATOR = Trait(
    name="Marsh Navigator",
    description="Navigates marshes easily. +80% speed in marsh terrain, finds more resources in marshes",
    trait_type="environmental",
    rarity="uncommon"
)

ALL_TERRAIN = Trait(
    name="All Terrain",
    description="Versatile movement. No terrain penalties, +5% speed everywhere",
    trait_type="environmental",
    speed_modifier=1.05,
    rarity="rare"
)

# ===========================
# TIME OF DAY TRAITS
# ===========================

NOCTURNAL = Trait(
    name="Nocturnal",
    description="Active at night. +30% stats at night, -15% stats during day, excellent night vision",
    trait_type="environmental",
    rarity="common"
)

DIURNAL = Trait(
    name="Diurnal",
    description="Active during day. +20% stats during day, normal vision, -10% stats at night",
    trait_type="environmental",
    rarity="common"
)

CREPUSCULAR = Trait(
    name="Crepuscular",
    description="Active at dawn/dusk. +25% stats during dawn/dusk, +10% stealth during twilight hours",
    trait_type="environmental",
    rarity="uncommon"
)

TIRELESS = Trait(
    name="Tireless",
    description="Always active. No time-of-day penalties, consistent performance 24/7",
    trait_type="environmental",
    defense_modifier=1.05,
    rarity="rare"
)

# ===========================
# HAZARD RESISTANCE TRAITS
# ===========================

FIRE_PROOF = Trait(
    name="Fire Proof",
    description="Immune to fire hazards. Takes no damage from fire, can walk through flames safely",
    trait_type="environmental",
    defense_modifier=1.1,
    rarity="rare"
)

POISON_RESISTANT = Trait(
    name="Poison Resistant",
    description="Resistant to toxins. 70% reduced damage from poison clouds and toxic environments",
    trait_type="environmental",
    defense_modifier=1.05,
    rarity="uncommon"
)

SURE_FOOTED = Trait(
    name="Sure Footed",
    description="Avoids quicksand and traps. Immune to quicksand, 50% reduced hazard damage",
    trait_type="environmental",
    speed_modifier=1.05,
    rarity="uncommon"
)

THICK_HIDE = Trait(
    name="Thick Hide",
    description="Armored skin. Immune to thorn damage, +20% defense against all hazards",
    trait_type="environmental",
    defense_modifier=1.2,
    rarity="rare"
)

GROUNDED = Trait(
    name="Grounded",
    description="Electrical resistance. 80% reduced damage from electrical hazards",
    trait_type="environmental",
    defense_modifier=1.05,
    rarity="uncommon"
)

HAZARD_SENSE = Trait(
    name="Hazard Sense",
    description="Detects and avoids hazards. AI actively avoids environmental hazards, learns danger zones",
    trait_type="environmental",
    rarity="rare"
)

# ===========================
# ENVIRONMENTAL AWARENESS TRAITS
# ===========================

WEATHER_SENSE = Trait(
    name="Weather Sense",
    description="Predicts weather changes. Can sense incoming weather, optimizes behavior accordingly",
    trait_type="environmental",
    rarity="uncommon"
)

TRACKER = Trait(
    name="Tracker",
    description="Reads the environment. Can identify good resource areas, remembers safe terrain",
    trait_type="environmental",
    speed_modifier=1.05,
    rarity="uncommon"
)

CAMOUFLAGE = Trait(
    name="Camouflage",
    description="Blends with terrain. +40% stealth, harder to detect in matching terrain types",
    trait_type="environmental",
    defense_modifier=1.1,
    rarity="rare"
)

ENVIRONMENTAL_MASTER = Trait(
    name="Environmental Master",
    description="Ultimate adaptation. +15% all stats, benefits from all environmental conditions",
    trait_type="environmental",
    strength_modifier=1.15,
    speed_modifier=1.15,
    defense_modifier=1.15,
    rarity="legendary"
)

# ===========================
# FORAGING & RESOURCE TRAITS
# ===========================

KEEN_FORAGER = Trait(
    name="Keen Forager",
    description="Expert at finding food. Detects pellets from 2x distance, +20% movement speed toward food, assesses pellet quality from afar",
    trait_type="environmental",
    speed_modifier=1.1,
    rarity="uncommon"
)

PICKY_EATER = Trait(
    name="Picky Eater",
    description="Selective diet. Only eats high-quality pellets, gets 30% more nutrition from preferred food, completely avoids toxic pellets",
    trait_type="environmental",
    rarity="common"
)

OPPORTUNISTIC_FEEDER = Trait(
    name="Opportunistic Feeder",
    description="Eats anything. Consumes any pellet regardless of toxicity, 50% reduced toxicity damage, survives on low-quality food",
    trait_type="environmental",
    defense_modifier=1.05,
    rarity="common"
)

FOOD_HOARDER = Trait(
    name="Food Hoarder",
    description="Remembers food sources. Returns to known pellet locations, defends favorite foraging areas, +10% attack when protecting food",
    trait_type="environmental",
    strength_modifier=1.05,
    rarity="rare"
)

# ===========================
# SHELTER & TACTICAL TRAITS
# ===========================

SHELTER_SEEKER = Trait(
    name="Shelter Seeker",
    description="Seeks cover when threatened. Actively finds shelter during storms/danger, +30% defense in forest/rocky terrain",
    trait_type="environmental",
    defense_modifier=1.15,
    rarity="uncommon"
)

EXPOSED_FIGHTER = Trait(
    name="Exposed Fighter",
    description="Prefers open terrain. +20% attack in grass/desert, movement penalty in dense terrain, aggressive in open spaces",
    trait_type="environmental",
    strength_modifier=1.1,
    rarity="uncommon"
)

BURROW_DWELLER = Trait(
    name="Burrow Dweller",
    description="Can hide underground. Gains stealth in marsh/rocky terrain, +25% defense when hiding, escapes danger by burrowing",
    trait_type="environmental",
    defense_modifier=1.15,
    rarity="rare"
)

TERRAIN_TACTICIAN = Trait(
    name="Terrain Tactician",
    description="Strategic positioning. Chooses combat positions based on terrain advantages, uses cover effectively, lures enemies into bad terrain",
    trait_type="environmental",
    speed_modifier=1.1,
    defense_modifier=1.1,
    rarity="rare"
)

# ===========================
# TRAIT COLLECTIONS
# ===========================

WEATHER_ADAPTATION_TRAITS = [
    COLD_BLOODED,
    WARM_BLOODED,
    THICK_FUR,
    HEAT_RESISTANT,
    STORM_WALKER,
    DROUGHT_SURVIVOR,
]

TERRAIN_ADAPTATION_TRAITS = [
    AQUATIC,
    ROCK_CLIMBER,
    FOREST_DWELLER,
    DESERT_ADAPTED,
    MARSH_NAVIGATOR,
    ALL_TERRAIN,
]

TIME_ADAPTATION_TRAITS = [
    NOCTURNAL,
    DIURNAL,
    CREPUSCULAR,
    TIRELESS,
]

HAZARD_RESISTANCE_TRAITS = [
    FIRE_PROOF,
    POISON_RESISTANT,
    SURE_FOOTED,
    THICK_HIDE,
    GROUNDED,
    HAZARD_SENSE,
]

AWARENESS_TRAITS = [
    WEATHER_SENSE,
    TRACKER,
    CAMOUFLAGE,
    ENVIRONMENTAL_MASTER,
]

FORAGING_TRAITS = [
    KEEN_FORAGER,
    PICKY_EATER,
    OPPORTUNISTIC_FEEDER,
    FOOD_HOARDER,
]

TACTICAL_TRAITS = [
    SHELTER_SEEKER,
    EXPOSED_FIGHTER,
    BURROW_DWELLER,
    TERRAIN_TACTICIAN,
]

ALL_ENVIRONMENTAL_TRAITS = (
    WEATHER_ADAPTATION_TRAITS +
    TERRAIN_ADAPTATION_TRAITS +
    TIME_ADAPTATION_TRAITS +
    HAZARD_RESISTANCE_TRAITS +
    AWARENESS_TRAITS +
    FORAGING_TRAITS +
    TACTICAL_TRAITS
)


def get_environmental_trait_by_name(name: str) -> Trait:
    """
    Get an environmental trait by name.
    
    Args:
        name: Name of the trait
        
    Returns:
        The trait if found, or a basic trait if not found
    """
    for trait in ALL_ENVIRONMENTAL_TRAITS:
        if trait.name.lower() == name.lower():
            return trait
    
    # Return a basic trait if not found
    return Trait(name=name, description=f"Custom environmental trait: {name}")


def get_random_environmental_trait():
    """Get a random environmental trait."""
    import random
    return random.choice(ALL_ENVIRONMENTAL_TRAITS)


def get_traits_for_terrain(terrain_type_name: str):
    """
    Get traits that would be beneficial for a specific terrain type.
    
    Args:
        terrain_type_name: Name of terrain type (grass, rocky, water, forest, desert, marsh)
        
    Returns:
        List of beneficial traits for that terrain
    """
    terrain_map = {
        'water': [AQUATIC, SURE_FOOTED],
        'rocky': [ROCK_CLIMBER, SURE_FOOTED, ALL_TERRAIN],
        'forest': [FOREST_DWELLER, CAMOUFLAGE, TRACKER],
        'desert': [DESERT_ADAPTED, HEAT_RESISTANT, DROUGHT_SURVIVOR],
        'marsh': [MARSH_NAVIGATOR, POISON_RESISTANT, AQUATIC],
        'grass': [ALL_TERRAIN, TRACKER],
    }
    return terrain_map.get(terrain_type_name.lower(), [])


def get_traits_for_weather(weather_type_name: str):
    """
    Get traits that would be beneficial for specific weather.
    
    Args:
        weather_type_name: Name of weather type (clear, rainy, stormy, foggy, drought)
        
    Returns:
        List of beneficial traits for that weather
    """
    weather_map = {
        'clear': [DIURNAL, TRACKER],
        'rainy': [AQUATIC, STORM_WALKER],
        'stormy': [STORM_WALKER, THICK_HIDE, GROUNDED],
        'foggy': [NOCTURNAL, TRACKER, WEATHER_SENSE],
        'drought': [DROUGHT_SURVIVOR, DESERT_ADAPTED, HEAT_RESISTANT],
    }
    return weather_map.get(weather_type_name.lower(), [])
