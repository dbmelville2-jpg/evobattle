"""
Building System Package

Contains all building-related models and logic:
- Building definitions and blueprints
- Building materials
- Building configuration
- Building behavior and AI
"""

from .building_config import (
    Building, BuildingType, BuildingBlueprint, 
    get_blueprint, get_all_building_types, BUILDING_BLUEPRINTS,
    BuildingConfig
)
from .building_material import (
    BuildingMaterial, MaterialType, create_random_material, get_material_color
)
from .building_behavior import (
    BuildingBehaviorSystem, BuildingDecision, BuildingTask, BuildingNeed
)

__all__ = [
    'Building',
    'BuildingType', 
    'BuildingBlueprint',
    'get_blueprint',
    'get_all_building_types',
    'BUILDING_BLUEPRINTS',
    'BuildingMaterial',
    'MaterialType',
    'create_random_material',
    'get_material_color',
    'BuildingConfig',
    'BuildingBehaviorSystem',
    'BuildingDecision',
    'BuildingTask',
    'BuildingNeed'
]
