from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
from enum import Enum
from .building_material import MaterialType
from src.models.spatial import Vector2D


class BuildingType(Enum):
    """Types of buildings creatures can build"""
    SHELTER = "shelter"              # Protection from weather/predators
    FOOD_CACHE = "food_cache"        # Food storage
    NEST = "nest"                    # Breeding bonus
    WATCHTOWER = "watchtower"        # Increased vision
    BARRIER = "barrier"              # Defensive wall
    SHRINE = "shrine"                # Social gathering/cooperation
    GARDEN = "garden"                # Pellet growth boost
    BRIDGE = "bridge"                # Cross difficult terrain
    TRAP = "trap"                    # Capture prey/pellets
    TERRITORY_MARKER = "territory_marker"  # Claim area


@dataclass
class BuildingBlueprint:
    """
    Blueprint defining how to build a building.
    
    Contains the pattern, materials needed, and effects of a building type.
    """
    building_type: BuildingType
    required_materials: Dict[MaterialType, int]
    pattern: List[Tuple[int, int]]  # Relative tile positions (x, y)
    build_time: float  # Base time in seconds to complete construction
    effects: Dict[str, Any]  # Effects provided when building is active
    description: str
    
    # New attributes for enhanced system
    decay_rate: float = 0.0003  # Base durability loss per second
    weather_resistance: Dict[str, float] = field(default_factory=dict) # Multiplier for weather damage (lower is better)
    effect_radius: float = 20.0 # Range for building effects
    
    def get_total_material_count(self) -> int:
        """Get total number of materials needed"""
        return sum(self.required_materials.values())
    
    def get_footprint_size(self) -> Tuple[int, int]:
        """Get the width and height of the building's footprint"""
        if not self.pattern:
            return (1, 1)
        xs = [p[0] for p in self.pattern]
        ys = [p[1] for p in self.pattern]
        return (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)


@dataclass
class Building:
    """
    An actual building instance built in the arena.
    
    Tracks construction progress, durability, and active effects.
    """
    building_id: str
    building_type: BuildingType
    position: Vector2D  # Center position
    tiles: List[Vector2D]  # Actual occupied tiles
    builder_id: str  # Creature that built it
    builder_strain_id: Optional[str] = None  # Genetic strain that started this building
    completion: float = 0.0  # 0.0 to 1.0
    durability: float = 1.0  # 0.0 to 1.0
    effects_active: bool = False
    age: float = 0.0  # Time since completion
    materials_placed: Dict[MaterialType, int] = field(default_factory=dict)
    
    # New attributes
    last_maintenance_time: float = 0.0
    
    def is_complete(self) -> bool:
        """Check if building is fully built"""
        return self.completion >= 1.0
    
    def is_damaged(self) -> bool:
        """Check if building needs repair"""
        return self.durability < 0.7  # Increased threshold for maintenance
    
    def is_destroyed(self) -> bool:
        """Check if building is destroyed"""
        return self.durability <= 0.0
    
    def activate(self):
        """Activate building effects (called when construction completes)"""
        if self.is_complete() and not self.is_destroyed():
            self.effects_active = True
    
    def deactivate(self):
        """Deactivate building effects"""
        self.effects_active = False
    
    def damage(self, amount: float):
        """Apply damage to building"""
        self.durability = max(0.0, self.durability - amount)
        if self.is_destroyed():
            self.deactivate()
    
    def repair(self, amount: float):
        """Repair building"""
        self.durability = min(1.0, self.durability + amount)
        if self.is_complete() and not self.is_destroyed():
            self.activate()
            
    def __repr__(self):
        status = "complete" if self.is_complete() else f"{self.completion*100:.0f}%"
        return f"Building({self.building_type.value}, {status}, durability={self.durability:.2f})"


# Building Blueprints - Define all buildable buildings
BUILDING_BLUEPRINTS: Dict[BuildingType, BuildingBlueprint] = {
    BuildingType.SHELTER: BuildingBlueprint(
        building_type=BuildingType.SHELTER,
        required_materials={
            MaterialType.WOOD: 4,
            MaterialType.PLANT_FIBER: 2
        },
        pattern=[
            (0, 0), (1, 0), (2, 0),
            (0, 1),         (2, 1),  # Opening on right
            (0, 2), (1, 2), (2, 2)
        ],
        build_time=30.0,
        effects={
            'hp_regen_bonus': 0.2,  # +20% HP regeneration
            'weather_protection': True,
            'rest_quality_bonus': 0.3
        },
        description="A basic shelter providing protection from weather and enhanced rest"
    ),
    
    BuildingType.FOOD_CACHE: BuildingBlueprint(
        building_type=BuildingType.FOOD_CACHE,
        required_materials={
            MaterialType.STONE: 3,
            MaterialType.WOOD: 2
        },
        pattern=[
            (0, 0), (1, 0),
            (0, 1), (1, 1)
        ],
        build_time=20.0,
        effects={
            'storage_capacity': 5,  # Can store 5 pellets
            'food_decay_reduction': 0.5,  # 50% slower decay
            'preservation': True
        },
        description="Storage area that preserves food and reduces decay"
    ),
    
    BuildingType.NEST: BuildingBlueprint(
        building_type=BuildingType.NEST,
        required_materials={
            MaterialType.PLANT_FIBER: 6,
            MaterialType.ORGANIC: 2
        },
        pattern=[
            (0, 0), (1, 0),
            (0, 1), (1, 1)
        ],
        build_time=25.0,
        effects={
            'breeding_success_bonus': 0.3,  # +30% breeding success
            'safe_spawn': True,
            'offspring_health_bonus': 0.15
        },
        description="A nest that increases breeding success and offspring health"
    ),
    
    BuildingType.WATCHTOWER: BuildingBlueprint(
        building_type=BuildingType.WATCHTOWER,
        required_materials={
            MaterialType.WOOD: 8,
            MaterialType.STONE: 4
        },
        pattern=[
            (0, 0), (1, 0),
                    (1, 1),  # Tower top
            (0, 2), (1, 2)
        ],
        build_time=40.0,
        effects={
            'vision_range_bonus': 0.5,  # +50% vision range
            'predator_detection': True,
            'threat_awareness_bonus': 0.4
        },
        description="Elevated building providing enhanced vision and early warning"
    ),
    
    BuildingType.BARRIER: BuildingBlueprint(
        building_type=BuildingType.BARRIER,
        required_materials={
            MaterialType.WOOD: 6,
            MaterialType.STONE: 3
        },
        pattern=[
            (0, 0), (1, 0), (2, 0), (3, 0)
        ],
        build_time=35.0,
        effects={
            'blocks_movement': True,
            'defensive_bonus': 0.25,
            'territory_control': True
        },
        description="Defensive wall that blocks movement and provides cover"
    ),
    
    BuildingType.SHRINE: BuildingBlueprint(
        building_type=BuildingType.SHRINE,
        required_materials={
            MaterialType.STONE: 10,
            MaterialType.ORGANIC: 5
        },
        pattern=[
                    (1, 0),
            (0, 1), (1, 1), (2, 1),
                    (1, 2)
        ],
        build_time=50.0,
        effects={
            'cooperation_radius_bonus': 0.2,  # +20% cooperation range
            'social_gathering': True,
            'belief_reinforcement': 0.15,
            'morale_bonus': 0.1
        },
        description="Sacred building that enhances cooperation and social bonds"
    ),
    
    BuildingType.GARDEN: BuildingBlueprint(
        building_type=BuildingType.GARDEN,
        required_materials={
            MaterialType.ORGANIC: 4,
            MaterialType.PLANT_FIBER: 3
        },
        pattern=[
            (0, 0), (1, 0), (2, 0),
            (0, 1), (1, 1), (2, 1),
            (0, 2), (1, 2), (2, 2)
        ],
        build_time=30.0,
        effects={
            'pellet_spawn_rate_bonus': 1.0,  # +100% pellet spawn in area
            'pellet_quality_bonus': 0.2,
            'sustainable_food': True
        },
        description="Cultivated area that encourages pellet growth"
    ),
    
    BuildingType.BRIDGE: BuildingBlueprint(
        building_type=BuildingType.BRIDGE,
        required_materials={
            MaterialType.WOOD: 10,
            MaterialType.PLANT_FIBER: 4
        },
        pattern=[
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0)
        ],
        build_time=45.0,
        effects={
            'terrain_crossing': True,
            'movement_speed_bonus': 0.1,
            'access_expansion': True
        },
        description="Crosses difficult terrain like water or hazards"
    ),
    
    BuildingType.TRAP: BuildingBlueprint(
        building_type=BuildingType.TRAP,
        required_materials={
            MaterialType.WOOD: 5,
            MaterialType.PLANT_FIBER: 3
        },
        pattern=[
            (0, 0), (1, 0),
            (0, 1), (1, 1)
        ],
        build_time=25.0,
        effects={
            'capture_chance': 0.3,  # 30% chance to capture prey
            'pellet_collection': True,
            'requires_intelligence': True
        },
        description="Captures prey or collects pellets automatically"
    ),
    
    BuildingType.TERRITORY_MARKER: BuildingBlueprint(
        building_type=BuildingType.TERRITORY_MARKER,
        required_materials={
            MaterialType.STONE: 3,
            MaterialType.ORGANIC: 2
        },
        pattern=[
            (0, 0)
        ],
        build_time=15.0,
        effects={
            'territory_claim': True,
            'rival_deterrent': 0.2,
            'confidence_bonus': 0.1
        },
        description="Marks claimed territory and deters rivals"
    )
}


def get_blueprint(building_type: BuildingType) -> BuildingBlueprint:
    """Get the blueprint for a building type"""
    return BUILDING_BLUEPRINTS[building_type]


def get_all_building_types() -> List[BuildingType]:
    """Get list of all buildable building types"""
    return list(BUILDING_BLUEPRINTS.keys())


@dataclass
class BuildingConfig:
    """Configuration for the building system."""
    
    # Decay settings
    base_decay_rate: float = 0.02  # 2% per minute (approx 0.00033 per second)
    weather_decay_multiplier: Dict[str, float] = field(default_factory=lambda: {
        'rainy': 1.5,
        'stormy': 2.5,
        'clear': 1.0,
        'foggy': 1.1
    })
    
    # Material spawning (Balanced rate)
    material_spawn_rate: float = 0.5  # Materials per second (0.5 = 1 every 2 seconds)
    material_types_weights: Dict[MaterialType, float] = field(default_factory=lambda: {
        MaterialType.WOOD: 0.4,
        MaterialType.STONE: 0.2,
        MaterialType.PLANT_FIBER: 0.3,
        MaterialType.ORGANIC: 0.1
    })
    
    # Building behavior
    building_enabled: bool = True
    require_architect_trait: bool = False  # If True, only Architects can build
    cooperative_building: bool = True
    
    # Visual settings
    building_base_size: int = 60  # Base pixel size for building tiles
    show_construction_ghost: bool = True
    show_material_piles: bool = True
