"""
Building Material Model - Resources for Construction

This module defines the materials that creatures can gather and use to build
buildings. Materials are dropped by pellets, found in terrain, or harvested
from the environment.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from src.models.spatial import Vector2D


class MaterialType(Enum):
    """Types of building materials"""
    PLANT_FIBER = "plant_fiber"  # From grass/plant pellets
    WOOD = "wood"                # From forest pellets
    STONE = "stone"              # From rocky terrain
    ORGANIC = "organic"          # From creature remains/decomposition


@dataclass
class BuildingMaterial:
    """
    Represents a building material that can be gathered and used.
    
    Materials can be on the ground, carried by creatures, or stored in buildings.
    
    Attributes:
        material_id: Unique identifier
        material_type: Type of material
        position: Current position in arena
        quantity: Amount of material (stackable)
        carrier_id: ID of creature carrying this material (None if on ground)
        source_id: ID of pellet/entity that dropped this material
    """
    material_id: str
    material_type: MaterialType
    position: Vector2D
    quantity: int = 1
    carrier_id: Optional[str] = None
    source_id: Optional[str] = None
    spawn_time: float = 0.0  # Time when material was spawned
    max_age: float = 120.0  # Materials expire after 2 minutes
    
    def is_carried(self) -> bool:
        """Check if material is being carried by a creature"""
        return self.carrier_id is not None
    
    def is_on_ground(self) -> bool:
        """Check if material is on the ground"""
        return self.carrier_id is None
    
    def is_expired(self, current_time: float) -> bool:
        """Check if material has expired and should be removed"""
        return (current_time - self.spawn_time) > self.max_age
    
    def get_age(self, current_time: float) -> float:
        """Get the current age of the material in seconds"""
        return current_time - self.spawn_time
    
    def __repr__(self):
        status = f"carried by {self.carrier_id}" if self.is_carried() else "on ground"
        return f"Material({self.material_type.value} x{self.quantity}, {status})"


# Material properties for gameplay balance
MATERIAL_PROPERTIES = {
    MaterialType.PLANT_FIBER: {
        "weight": 1,           # How much it slows creature when carried
        "durability": 0.5,     # How long buildings made from it last
        "rarity": 1.0,         # How common it is (1.0 = common, 0.1 = rare)
        "color": (120, 180, 80)  # RGB for rendering
    },
    MaterialType.WOOD: {
        "weight": 2,
        "durability": 1.0,
        "rarity": 0.6,
        "color": (139, 90, 43)
    },
    MaterialType.STONE: {
        "weight": 3,
        "durability": 1.5,
        "rarity": 0.4,
        "color": (128, 128, 128)
    },
    MaterialType.ORGANIC: {
        "weight": 1,
        "durability": 0.3,
        "rarity": 0.7,
        "color": (101, 67, 33)
    }
}


def get_material_weight(material_type: MaterialType) -> int:
    """Get the weight of a material type"""
    return MATERIAL_PROPERTIES[material_type]["weight"]


def get_material_durability(material_type: MaterialType) -> float:
    """Get the durability multiplier of a material type"""
    return MATERIAL_PROPERTIES[material_type]["durability"]


def get_material_rarity(material_type: MaterialType) -> float:
    """Get the rarity of a material type (1.0 = common, 0.1 = very rare)"""
    return MATERIAL_PROPERTIES[material_type]["rarity"]


def get_material_color(material_type: MaterialType) -> tuple:
    """Get the RGB color for rendering a material type"""
    return MATERIAL_PROPERTIES[material_type]["color"]


def create_random_material(material_type: MaterialType, position: Vector2D, spawn_time: float = 0.0) -> BuildingMaterial:
    """
    Create a new material instance at the given position.
    
    Args:
        material_type: Type of material
        position: Location
        spawn_time: Time when material was spawned (for expiration tracking)
        
    Returns:
        New BuildingMaterial instance
    """
    import uuid
    return BuildingMaterial(
        material_id=str(uuid.uuid4()),
        material_type=material_type,
        position=position,
        quantity=1,
        spawn_time=spawn_time
    )
