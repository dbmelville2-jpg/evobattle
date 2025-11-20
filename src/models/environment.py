"""
Environmental simulation system for Evolution Battle Game.

This module provides weather, terrain, day/night cycles, and environmental hazards
that integrate with existing creature systems (traits, behavior, combat, hunger).

Features:
- Weather system (temperature, humidity, precipitation)
- Terrain types (grass, rocky, water, forest, desert)
- Day/night cycle (affects creature visibility and activity)
- Resource quality variations based on environment
- Environmental hazards that creatures can learn to avoid
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple
import random
import time
import math

from .spatial import Vector2D


class WeatherType(Enum):
    """Types of weather conditions."""
    CLEAR = "clear"
    RAINY = "rainy"
    STORMY = "stormy"
    FOGGY = "foggy"
    DROUGHT = "drought"


class TerrainType(Enum):
    """Types of terrain in the arena."""
    GRASS = "grass"       # Default, no modifiers
    ROCKY = "rocky"       # Slower movement, better hiding
    WATER = "water"       # Very slow movement for non-aquatic
    FOREST = "forest"     # Good cover, affects visibility
    DESERT = "desert"     # Fast movement, poor resources
    MARSH = "marsh"       # Slow movement, rich resources


class TimeOfDay(Enum):
    """Time of day phases."""
    DAWN = "dawn"         # 05:00-07:00
    DAY = "day"           # 07:00-17:00
    DUSK = "dusk"         # 17:00-19:00
    NIGHT = "night"       # 19:00-05:00


class HazardType(Enum):
    """Types of environmental hazards."""
    FIRE = "fire"         # Deals damage over time
    POISON_CLOUD = "poison_cloud"  # Reduces health gradually
    QUICKSAND = "quicksand"        # Slows movement drastically
    THORNS = "thorns"     # Deals damage on contact
    ELECTRICAL = "electrical"      # Random damage spikes


@dataclass
class WeatherConditions:
    """
    Current weather conditions affecting the environment.
    
    Attributes:
        weather_type: Current weather pattern
        temperature: Temperature in Celsius (-20 to 50)
        humidity: Humidity percentage (0.0 to 1.0)
        precipitation: Precipitation intensity (0.0 to 1.0)
        wind_speed: Wind speed (0.0 to 10.0)
        visibility: Visibility multiplier (0.0 to 1.0)
    """
    weather_type: WeatherType = WeatherType.CLEAR
    temperature: float = 20.0  # Celsius
    humidity: float = 0.5
    precipitation: float = 0.0
    wind_speed: float = 0.0
    visibility: float = 1.0
    
    def get_movement_modifier(self) -> float:
        """Calculate movement speed modifier based on weather (0.5 to 1.2)."""
        modifier = 1.0
        
        # Heavy rain/storm slows movement
        if self.weather_type == WeatherType.RAINY:
            modifier *= 0.9
        elif self.weather_type == WeatherType.STORMY:
            modifier *= 0.75
        
        # Wind can speed up or slow down
        modifier *= (1.0 - self.wind_speed * 0.05)
        
        # Extreme temperatures slow movement
        if self.temperature < 0 or self.temperature > 35:
            modifier *= 0.85
        
        return max(0.5, min(1.2, modifier))
    
    def get_hunger_modifier(self) -> float:
        """Calculate hunger depletion modifier based on weather (0.8 to 1.4)."""
        modifier = 1.0
        
        # Cold increases hunger
        if self.temperature < 10:
            modifier += (10 - self.temperature) * 0.02
        # Heat increases hunger
        elif self.temperature > 30:
            modifier += (self.temperature - 30) * 0.015
        
        # Storm increases energy expenditure
        if self.weather_type == WeatherType.STORMY:
            modifier *= 1.1
        
        return max(0.8, min(1.4, modifier))
    
    def get_resource_quality_modifier(self) -> float:
        """Calculate resource quality modifier based on weather (0.6 to 1.3)."""
        modifier = 1.0
        
        # Rain improves plant resources
        if self.weather_type == WeatherType.RAINY:
            modifier *= 1.15
        # Drought hurts resources
        elif self.weather_type == WeatherType.DROUGHT:
            modifier *= 0.7
        
        # Moderate humidity is best
        humidity_factor = 1.0 - abs(0.6 - self.humidity) * 0.5
        modifier *= humidity_factor
        
        return max(0.6, min(1.3, modifier))


@dataclass
class TerrainCell:
    """
    Represents a cell in the terrain grid.
    
    Attributes:
        terrain_type: Type of terrain in this cell
        position: Center position of the cell
        resource_richness: How rich in resources (0.0 to 2.0)
        danger_level: Hazard danger level (0.0 to 1.0)
    """
    terrain_type: TerrainType
    position: Vector2D
    resource_richness: float = 1.0
    danger_level: float = 0.0
    
    def get_movement_modifier(self) -> float:
        """Get movement speed modifier for this terrain (0.3 to 1.3)."""
        modifiers = {
            TerrainType.GRASS: 1.0,
            TerrainType.ROCKY: 0.7,
            TerrainType.WATER: 0.3,
            TerrainType.FOREST: 0.8,
            TerrainType.DESERT: 1.3,
            TerrainType.MARSH: 0.5,
        }
        return modifiers.get(self.terrain_type, 1.0)
    
    def get_visibility_modifier(self) -> float:
        """Get visibility modifier for this terrain (0.4 to 1.0)."""
        modifiers = {
            TerrainType.GRASS: 1.0,
            TerrainType.ROCKY: 0.8,
            TerrainType.WATER: 1.0,
            TerrainType.FOREST: 0.4,
            TerrainType.DESERT: 1.0,
            TerrainType.MARSH: 0.7,
        }
        return modifiers.get(self.terrain_type, 1.0)
    
    def get_cover_bonus(self) -> float:
        """Get defensive cover bonus (0.0 to 0.3)."""
        bonuses = {
            TerrainType.GRASS: 0.0,
            TerrainType.ROCKY: 0.2,
            TerrainType.WATER: 0.0,
            TerrainType.FOREST: 0.3,
            TerrainType.DESERT: 0.0,
            TerrainType.MARSH: 0.1,
        }
        return bonuses.get(self.terrain_type, 0.0)


@dataclass
class EnvironmentalHazard:
    """
    Represents a dangerous environmental feature.
    
    Attributes:
        hazard_type: Type of hazard
        position: Location of the hazard
        radius: Affected radius around position
        damage: Damage per second in hazard
        duration: How long hazard lasts (-1 for permanent)
        created_at: When the hazard was created
    """
    hazard_type: HazardType
    position: Vector2D
    radius: float = 5.0
    damage: float = 5.0
    duration: float = -1.0  # -1 means permanent
    created_at: float = field(default_factory=time.time)
    
    def is_active(self) -> bool:
        """Check if hazard is still active."""
        if self.duration < 0:
            return True
        return (time.time() - self.created_at) < self.duration
    
    def affects_position(self, position: Vector2D) -> bool:
        """Check if a position is affected by this hazard."""
        if not self.is_active():
            return False
        return position.distance_to(self.position) <= self.radius
    
    def get_damage_at_position(self, position: Vector2D) -> float:
        """Calculate damage at a specific position (0.0 to damage)."""
        if not self.affects_position(position):
            return 0.0
        
        distance = position.distance_to(self.position)
        # Damage decreases linearly with distance
        damage_multiplier = 1.0 - (distance / self.radius)
        return self.damage * max(0.0, damage_multiplier)


class DayNightCycle:
    """
    Manages the day/night cycle in the simulation.
    
    Attributes:
        cycle_duration: Real-world seconds for a full 24-hour cycle
        start_time: When the cycle started
        current_hour: Current hour (0-24)
    """
    
    def __init__(self, cycle_duration: float = 300.0, start_hour: float = 7.0):
        """
        Initialize day/night cycle.
        
        Args:
            cycle_duration: How many real seconds = 24 game hours (default 5 minutes)
            start_hour: Starting hour of day (default 7.0 = 7 AM)
        """
        self.cycle_duration = cycle_duration
        self.start_time = time.time()
        self.start_hour = start_hour
    
    def get_current_hour(self) -> float:
        """Get current hour of day (0.0 to 24.0)."""
        elapsed = time.time() - self.start_time
        hours_elapsed = (elapsed / self.cycle_duration) * 24.0
        return (self.start_hour + hours_elapsed) % 24.0
    
    def get_time_of_day(self) -> TimeOfDay:
        """Get current phase of day."""
        hour = self.get_current_hour()
        
        if 5.0 <= hour < 7.0:
            return TimeOfDay.DAWN
        elif 7.0 <= hour < 17.0:
            return TimeOfDay.DAY
        elif 17.0 <= hour < 19.0:
            return TimeOfDay.DUSK
        else:
            return TimeOfDay.NIGHT
    
    def get_visibility_modifier(self) -> float:
        """Get visibility multiplier based on time of day (0.3 to 1.0)."""
        time_of_day = self.get_time_of_day()
        
        modifiers = {
            TimeOfDay.DAWN: 0.6,
            TimeOfDay.DAY: 1.0,
            TimeOfDay.DUSK: 0.6,
            TimeOfDay.NIGHT: 0.3,
        }
        return modifiers.get(time_of_day, 1.0)
    
    def get_activity_modifier(self) -> float:
        """Get creature activity modifier based on time (0.5 to 1.2)."""
        time_of_day = self.get_time_of_day()
        
        # Most creatures are active during day
        modifiers = {
            TimeOfDay.DAWN: 0.8,
            TimeOfDay.DAY: 1.0,
            TimeOfDay.DUSK: 0.9,
            TimeOfDay.NIGHT: 0.5,
        }
        return modifiers.get(time_of_day, 1.0)


class Environment:
    """
    Complete environmental simulation system.
    
    Manages weather, terrain, day/night cycle, and hazards.
    Provides modifiers for creature behavior, combat, and survival.
    """
    
    def __init__(
        self,
        width: float = 100.0,
        height: float = 100.0,
        cell_size: float = 10.0,
        enable_weather: bool = True,
        enable_day_night: bool = True,
        day_night_cycle_duration: float = 300.0
    ):
        """
        Initialize the environment.
        
        Args:
            width: Arena width
            height: Arena height
            cell_size: Size of terrain cells
            enable_weather: Enable weather simulation
            enable_day_night: Enable day/night cycle
            day_night_cycle_duration: Real seconds for full day/night cycle
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        
        # Initialize systems
        self.weather = WeatherConditions() if enable_weather else None
        self.day_night = DayNightCycle(day_night_cycle_duration) if enable_day_night else None
        self.hazards: List[EnvironmentalHazard] = []
        
        # Create terrain grid
        self.terrain_grid: Dict[Tuple[int, int], TerrainCell] = {}
        self._initialize_terrain()
        
        # Biome metadata (set by biome generator)
        self.biome_name: Optional[str] = None
        self.biome_description: Optional[str] = None
        self.biome_difficulty: int = 3
        self.biome_regions: List = []  # List[BiomeRegion] - avoid circular import
        
        # Weather change tracking
        self.last_weather_change = time.time()
        self.weather_change_interval = 60.0  # Change weather every 60 seconds
    
    def _initialize_terrain(self):
        """Initialize terrain grid with varied terrain types."""
        cols = int(self.width / self.cell_size)
        rows = int(self.height / self.cell_size)
        
        for row in range(rows):
            for col in range(cols):
                # Use perlin-noise-like generation for natural terrain
                # For now, use simple random with biases
                center_x = (col + 0.5) * self.cell_size
                center_y = (row + 0.5) * self.cell_size
                
                # Bias towards grass in center, water at edges
                distance_from_center = math.sqrt(
                    (center_x - self.width / 2) ** 2 +
                    (center_y - self.height / 2) ** 2
                )
                max_distance = math.sqrt((self.width / 2) ** 2 + (self.height / 2) ** 2)
                edge_factor = distance_from_center / max_distance
                
                # Terrain selection based on position
                rand = random.random()
                if edge_factor > 0.8 and rand < 0.3:
                    terrain = TerrainType.WATER
                elif edge_factor > 0.6 and rand < 0.2:
                    terrain = TerrainType.ROCKY
                elif rand < 0.15:
                    terrain = TerrainType.FOREST
                elif rand < 0.25:
                    terrain = TerrainType.DESERT
                elif rand < 0.3:
                    terrain = TerrainType.MARSH
                else:
                    terrain = TerrainType.GRASS
                
                # Resource richness varies
                resource_richness = random.uniform(0.5, 1.5)
                if terrain == TerrainType.MARSH:
                    resource_richness *= 1.3  # Marshes are resource-rich
                elif terrain == TerrainType.DESERT:
                    resource_richness *= 0.6  # Deserts are poor
                
                cell = TerrainCell(
                    terrain_type=terrain,
                    position=Vector2D(center_x, center_y),
                    resource_richness=resource_richness,
                    danger_level=0.0
                )
                self.terrain_grid[(col, row)] = cell
    
    def get_terrain_at(self, position: Vector2D) -> Optional[TerrainCell]:
        """Get terrain cell at a position."""
        col = int(position.x / self.cell_size)
        row = int(position.y / self.cell_size)
        return self.terrain_grid.get((col, row))
    
    def get_biome_at_position(self, position: Vector2D):
        """
        Get the biome region at a specific position.
        
        Args:
            position: Position to query
            
        Returns:
            BiomeRegion if multi-biome arena, None otherwise
        """
        if not self.biome_regions:
            return None
        
        for region in self.biome_regions:
            if region.contains_position(position):
                return region
        
        return None
    
    def update(self, delta_time: float):
        """
        Update environmental systems.
        
        Args:
            delta_time: Time since last update in seconds
        """
        # Update weather periodically
        if self.weather and (time.time() - self.last_weather_change) > self.weather_change_interval:
            self._change_weather()
            self.last_weather_change = time.time()
        
        # Remove expired hazards
        self.hazards = [h for h in self.hazards if h.is_active()]
    
    def _change_weather(self):
        """Randomly change weather conditions."""
        if not self.weather:
            return
        
        # 70% chance to stay same, 30% to change
        if random.random() < 0.7:
            return
        
        # Choose new weather
        new_weather = random.choice(list(WeatherType))
        self.weather.weather_type = new_weather
        
        # Update weather parameters based on type
        if new_weather == WeatherType.CLEAR:
            self.weather.precipitation = 0.0
            self.weather.humidity = random.uniform(0.3, 0.6)
            self.weather.visibility = 1.0
            self.weather.wind_speed = random.uniform(0.0, 2.0)
        elif new_weather == WeatherType.RAINY:
            self.weather.precipitation = random.uniform(0.3, 0.7)
            self.weather.humidity = random.uniform(0.7, 0.9)
            self.weather.visibility = random.uniform(0.6, 0.8)
            self.weather.wind_speed = random.uniform(1.0, 4.0)
        elif new_weather == WeatherType.STORMY:
            self.weather.precipitation = random.uniform(0.7, 1.0)
            self.weather.humidity = random.uniform(0.8, 1.0)
            self.weather.visibility = random.uniform(0.3, 0.6)
            self.weather.wind_speed = random.uniform(4.0, 8.0)
        elif new_weather == WeatherType.FOGGY:
            self.weather.precipitation = 0.0
            self.weather.humidity = random.uniform(0.9, 1.0)
            self.weather.visibility = random.uniform(0.2, 0.5)
            self.weather.wind_speed = random.uniform(0.0, 1.0)
        elif new_weather == WeatherType.DROUGHT:
            self.weather.precipitation = 0.0
            self.weather.humidity = random.uniform(0.1, 0.3)
            self.weather.visibility = random.uniform(0.7, 1.0)
            self.weather.wind_speed = random.uniform(2.0, 5.0)
        
        # Temperature varies
        self.weather.temperature = random.uniform(-5, 40)
    
    def add_hazard(self, hazard: EnvironmentalHazard):
        """Add a new environmental hazard."""
        self.hazards.append(hazard)
    
    def get_hazards_at(self, position: Vector2D) -> List[EnvironmentalHazard]:
        """Get all active hazards affecting a position."""
        return [h for h in self.hazards if h.affects_position(position)]
    
    def get_total_hazard_damage(self, position: Vector2D) -> float:
        """Calculate total hazard damage at a position."""
        return sum(h.get_damage_at_position(position) for h in self.hazards)
    
    def get_combined_movement_modifier(self, position: Vector2D) -> float:
        """Get combined movement modifier from weather and terrain (0.15 to 1.56)."""
        modifier = 1.0
        
        # Weather effects
        if self.weather:
            modifier *= self.weather.get_movement_modifier()
        
        # Terrain effects
        terrain = self.get_terrain_at(position)
        if terrain:
            modifier *= terrain.get_movement_modifier()
        
        return modifier
    
    def get_combined_visibility(self, position: Vector2D) -> float:
        """Get combined visibility from weather, terrain, and time (0.06 to 1.0)."""
        visibility = 1.0
        
        # Weather effects
        if self.weather:
            visibility *= self.weather.visibility
        
        # Terrain effects
        terrain = self.get_terrain_at(position)
        if terrain:
            visibility *= terrain.get_visibility_modifier()
        
        # Day/night effects
        if self.day_night:
            visibility *= self.day_night.get_visibility_modifier()
        
        return max(0.0, min(1.0, visibility))
    
    def get_resource_quality_at(self, position: Vector2D) -> float:
        """Get resource quality multiplier at a position (0.3 to 2.6)."""
        quality = 1.0
        
        # Weather effects
        if self.weather:
            quality *= self.weather.get_resource_quality_modifier()
        
        # Terrain effects
        terrain = self.get_terrain_at(position)
        if terrain:
            quality *= terrain.resource_richness
        
        return quality
    
    def get_defensive_cover(self, position: Vector2D) -> float:
        """Get defensive cover bonus at a position (0.0 to 0.3)."""
        terrain = self.get_terrain_at(position)
        if terrain:
            return terrain.get_cover_bonus()
        return 0.0
    
    def to_dict(self) -> dict:
        """Serialize environment state to dictionary."""
        return {
            'weather': {
                'type': self.weather.weather_type.value if self.weather else None,
                'temperature': self.weather.temperature if self.weather else None,
                'humidity': self.weather.humidity if self.weather else None,
                'precipitation': self.weather.precipitation if self.weather else None,
                'visibility': self.weather.visibility if self.weather else None,
            } if self.weather else None,
            'time_of_day': self.day_night.get_time_of_day().value if self.day_night else None,
            'current_hour': self.day_night.get_current_hour() if self.day_night else None,
            'active_hazards': len(self.hazards),
        }
