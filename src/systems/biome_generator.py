"""
Biome Generation System

Generates diverse biomes with distinct terrain patterns, weather, resources, and hazards.
Creates varied environments that support different types of life and gameplay strategies.

Biome Types:
- Grassland: Balanced, high pellet density, clear weather
- Desert: Sparse pellets, drought weather, fast movement
- Forest: Dense cover, foggy weather, slow movement, high resources
- Marsh: Very slow movement, rainy weather, toxic pellets, rich resources
- Rocky Highlands: Elevation variation, stormy weather, hazards
- Mixed Biome: Combination of 2-3 terrain types
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from enum import Enum
import random
import math

from ..models.environment import (
    Environment, TerrainType, TerrainCell, WeatherType, 
    WeatherConditions, HazardType, EnvironmentalHazard
)
from ..models.spatial import Vector2D


class BiomeType(Enum):
    """Types of biomes that can be generated."""
    GRASSLAND = "grassland"
    DESERT = "desert"
    FOREST = "forest"
    MARSH = "marsh"
    ROCKY_HIGHLANDS = "rocky_highlands"
    MIXED = "mixed"


@dataclass
class BiomeConfig:
    """
    Configuration for a specific biome type.
    
    Attributes:
        name: Display name of the biome
        description: Description of the biome
        primary_terrain: Main terrain type for this biome
        terrain_distribution: Dict of terrain types to their probability weights
        weather_type: Default weather for this biome
        temperature_range: (min, max) temperature in Celsius
        humidity_range: (min, max) humidity (0.0 to 1.0)
        pellet_density: Multiplier for pellet spawning (0.5 to 2.0)
        pellet_toxicity_bias: Bias toward toxic pellets (-0.5 to 0.5)
        hazard_types: List of hazard types that can spawn
        hazard_frequency: How often hazards spawn (0.0 to 1.0)
        difficulty: Difficulty rating (1-5)
    """
    name: str
    description: str
    primary_terrain: TerrainType
    terrain_distribution: Dict[TerrainType, float]
    weather_type: WeatherType
    temperature_range: Tuple[float, float]
    humidity_range: Tuple[float, float]
    pellet_density: float = 1.0
    pellet_toxicity_bias: float = 0.0
    hazard_types: List[HazardType] = None
    hazard_frequency: float = 0.3
    difficulty: int = 3


@dataclass
class BiomeRegion:
    """
    Represents a spatial region with a specific biome type.
    
    Attributes:
        biome_type: Type of biome in this region
        biome_config: Configuration for this biome
        bounds: (x, y, width, height) defining the region
        center: Center point of the region
    """
    biome_type: BiomeType
    biome_config: BiomeConfig
    bounds: Tuple[float, float, float, float]  # (x, y, width, height)
    center: Vector2D
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is within this region."""
        bx, by, bw, bh = self.bounds
        return bx <= x < (bx + bw) and by <= y < (by + bh)
    
    def contains_position(self, position: Vector2D) -> bool:
        """Check if a position is within this region."""
        return self.contains_point(position.x, position.y)


class BiomeGenerator:
    """
    Generates biomes with varied terrain, weather, and resources.
    
    Uses Perlin-noise-like generation for natural terrain patterns.
    """
    
    # Biome configurations
    BIOME_CONFIGS = {
        BiomeType.GRASSLAND: BiomeConfig(
            name="Grassland",
            description="Balanced plains with abundant food and moderate conditions",
            primary_terrain=TerrainType.GRASS,
            terrain_distribution={
                TerrainType.GRASS: 0.7,
                TerrainType.FOREST: 0.15,
                TerrainType.ROCKY: 0.1,
                TerrainType.WATER: 0.05,
            },
            weather_type=WeatherType.CLEAR,
            temperature_range=(15.0, 25.0),
            humidity_range=(0.4, 0.6),
            pellet_density=1.5,
            pellet_toxicity_bias=0.0,
            hazard_types=[],
            hazard_frequency=0.1,
            difficulty=1
        ),
        
        BiomeType.DESERT: BiomeConfig(
            name="Desert",
            description="Arid wasteland with scarce resources and extreme heat",
            primary_terrain=TerrainType.DESERT,
            terrain_distribution={
                TerrainType.DESERT: 0.8,
                TerrainType.ROCKY: 0.15,
                TerrainType.GRASS: 0.05,
            },
            weather_type=WeatherType.DROUGHT,
            temperature_range=(30.0, 45.0),
            humidity_range=(0.1, 0.3),
            pellet_density=0.5,
            pellet_toxicity_bias=0.1,
            hazard_types=[HazardType.FIRE],
            hazard_frequency=0.4,
            difficulty=4
        ),
        
        BiomeType.FOREST: BiomeConfig(
            name="Forest",
            description="Dense woodland with rich resources and limited visibility",
            primary_terrain=TerrainType.FOREST,
            terrain_distribution={
                TerrainType.FOREST: 0.7,
                TerrainType.GRASS: 0.2,
                TerrainType.WATER: 0.1,
            },
            weather_type=WeatherType.FOGGY,
            temperature_range=(10.0, 20.0),
            humidity_range=(0.6, 0.8),
            pellet_density=1.8,
            pellet_toxicity_bias=-0.1,
            hazard_types=[HazardType.THORNS],
            hazard_frequency=0.3,
            difficulty=2
        ),
        
        BiomeType.MARSH: BiomeConfig(
            name="Marsh",
            description="Swampy wetland with toxic plants and treacherous terrain",
            primary_terrain=TerrainType.MARSH,
            terrain_distribution={
                TerrainType.MARSH: 0.6,
                TerrainType.WATER: 0.25,
                TerrainType.GRASS: 0.15,
            },
            weather_type=WeatherType.RAINY,
            temperature_range=(15.0, 25.0),
            humidity_range=(0.7, 0.9),
            pellet_density=2.0,
            pellet_toxicity_bias=0.3,
            hazard_types=[HazardType.POISON_CLOUD, HazardType.QUICKSAND],
            hazard_frequency=0.5,
            difficulty=4
        ),
        
        BiomeType.ROCKY_HIGHLANDS: BiomeConfig(
            name="Rocky Highlands",
            description="Mountainous terrain with storms and dangerous hazards",
            primary_terrain=TerrainType.ROCKY,
            terrain_distribution={
                TerrainType.ROCKY: 0.7,
                TerrainType.GRASS: 0.2,
                TerrainType.DESERT: 0.1,
            },
            weather_type=WeatherType.STORMY,
            temperature_range=(5.0, 15.0),
            humidity_range=(0.5, 0.7),
            pellet_density=1.0,
            pellet_toxicity_bias=0.0,
            hazard_types=[HazardType.ELECTRICAL, HazardType.QUICKSAND],
            hazard_frequency=0.6,
            difficulty=5
        ),
    }
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the biome generator.
        
        Args:
            seed: Random seed for reproducible generation
        """
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        self.rng = random.Random(self.seed)
    
    def generate_biome(
        self,
        biome_type: BiomeType,
        width: float,
        height: float,
        cell_size: float = 10.0
    ) -> Environment:
        """
        Generate a complete biome environment.
        
        Args:
            biome_type: Type of biome to generate
            width: Width of the environment
            height: Height of the environment
            cell_size: Size of terrain cells
            
        Returns:
            Environment configured for the biome
        """
        if biome_type == BiomeType.MIXED:
            return self._generate_mixed_biome(width, height, cell_size)
        
        config = self.BIOME_CONFIGS[biome_type]
        
        # Create environment with biome-specific weather
        env = Environment(
            width=width,
            height=height,
            cell_size=cell_size,
            enable_weather=True,
            enable_day_night=True
        )
        
        # Set biome metadata
        env.biome_name = config.name
        env.biome_description = config.description
        env.biome_difficulty = config.difficulty
        
        # Generate terrain
        self._generate_terrain(env, config, width, height, cell_size)
        
        # Set weather
        self._set_biome_weather(env, config)
        
        # Place hazards
        if config.hazard_types:
            self._place_hazards(env, config, width, height)
        
        return env
    
    def generate_multi_biome(
        self,
        width: float,
        height: float,
        cell_size: float = 10.0,
        num_regions: int = 4
    ) -> Environment:
        """
        Generate a multi-biome environment with distinct regions.
        
        Creates an arena divided into regions, each with its own biome type.
        Uses quadrant layout for 4 regions.
        
        Args:
            width: Width of the environment
            height: Height of the environment
            cell_size: Size of terrain cells
            num_regions: Number of biome regions (currently only 4 supported)
            
        Returns:
            Environment with multiple biome regions
        """
        # Create base environment
        env = Environment(
            width=width,
            height=height,
            cell_size=cell_size,
            enable_weather=True,
            enable_day_night=True
        )
        
        # Select random biomes for each region (no duplicates)
        available_biomes = [b for b in BiomeType if b != BiomeType.MIXED]
        selected_biomes = self.rng.sample(available_biomes, min(num_regions, len(available_biomes)))
        
        # Create quadrant regions
        half_width = width / 2
        half_height = height / 2
        
        regions = [
            # Northwest quadrant
            BiomeRegion(
                biome_type=selected_biomes[0],
                biome_config=self.BIOME_CONFIGS[selected_biomes[0]],
                bounds=(0, 0, half_width, half_height),
                center=Vector2D(half_width / 2, half_height / 2)
            ),
            # Northeast quadrant
            BiomeRegion(
                biome_type=selected_biomes[1],
                biome_config=self.BIOME_CONFIGS[selected_biomes[1]],
                bounds=(half_width, 0, half_width, half_height),
                center=Vector2D(half_width + half_width / 2, half_height / 2)
            ),
            # Southwest quadrant
            BiomeRegion(
                biome_type=selected_biomes[2] if len(selected_biomes) > 2 else selected_biomes[0],
                biome_config=self.BIOME_CONFIGS[selected_biomes[2] if len(selected_biomes) > 2 else selected_biomes[0]],
                bounds=(0, half_height, half_width, half_height),
                center=Vector2D(half_width / 2, half_height + half_height / 2)
            ),
            # Southeast quadrant
            BiomeRegion(
                biome_type=selected_biomes[3] if len(selected_biomes) > 3 else selected_biomes[1],
                biome_config=self.BIOME_CONFIGS[selected_biomes[3] if len(selected_biomes) > 3 else selected_biomes[1]],
                bounds=(half_width, half_height, half_width, half_height),
                center=Vector2D(half_width + half_width / 2, half_height + half_height / 2)
            ),
        ]
        
        # Store regions in environment
        env.biome_regions = regions
        
        # Set environment metadata
        biome_names = [r.biome_config.name for r in regions]
        env.biome_name = "Multi-Biome Arena"
        env.biome_description = f"Regions: {', '.join(biome_names)}"
        env.biome_difficulty = int(sum(r.biome_config.difficulty for r in regions) / len(regions))
        
        # Generate terrain for each region
        cols = int(width / cell_size)
        rows = int(height / cell_size)
        
        for row in range(rows):
            for col in range(cols):
                center_x = (col + 0.5) * cell_size
                center_y = (row + 0.5) * cell_size
                
                # Find which region this cell belongs to
                region = None
                for r in regions:
                    if r.contains_point(center_x, center_y):
                        region = r
                        break
                
                if not region:
                    continue
                
                # Generate terrain using this region's biome config
                config = region.biome_config
                
                # Select terrain from distribution
                terrain = self._select_terrain_from_distribution(config.terrain_distribution)
                
                # Resource richness varies
                resource_richness = self.rng.uniform(0.5, 1.5)
                if terrain == TerrainType.MARSH:
                    resource_richness *= 1.3
                elif terrain == TerrainType.DESERT:
                    resource_richness *= 0.6
                
                cell = TerrainCell(
                    terrain_type=terrain,
                    position=Vector2D(center_x, center_y),
                    resource_richness=resource_richness,
                    danger_level=0.0
                )
                env.terrain_grid[(col, row)] = cell
        
        # Set weather to average of all regions
        avg_temp = sum(self.rng.uniform(*r.biome_config.temperature_range) for r in regions) / len(regions)
        avg_humidity = sum(self.rng.uniform(*r.biome_config.humidity_range) for r in regions) / len(regions)
        
        # Use most common weather type
        weather_types = [r.biome_config.weather_type for r in regions]
        env.weather = WeatherConditions(
            weather_type=self.rng.choice(weather_types),
            temperature=avg_temp,
            humidity=avg_humidity,
            wind_speed=self.rng.uniform(0.0, 20.0)
        )
        
        # Place hazards for each region
        for region in regions:
            if region.biome_config.hazard_types:
                self._place_regional_hazards(env, region)
        
        return env
    
    def _place_regional_hazards(
        self,
        env: Environment,
        region: BiomeRegion
    ):
        """
        Place hazards within a specific biome region.
        
        Args:
            env: Environment to populate
            region: BiomeRegion to place hazards in
        """
        config = region.biome_config
        if not config.hazard_types:
            return
        
        bx, by, bw, bh = region.bounds
        area = bw * bh
        
        # Number of hazards based on frequency and region area
        base_hazards = int((area / 1000.0) * config.hazard_frequency)
        num_hazards = self.rng.randint(max(1, base_hazards - 1), base_hazards + 1)
        
        for _ in range(num_hazards):
            hazard_type = self.rng.choice(config.hazard_types)
            
            # Random position within region bounds
            x = self.rng.uniform(bx + 5, bx + bw - 5)
            y = self.rng.uniform(by + 5, by + bh - 5)
            
            # Hazard properties
            radius = self.rng.uniform(5.0, 15.0)
            damage = self.rng.uniform(2.0, 8.0)
            duration = self.rng.uniform(30.0, 120.0)
            
            hazard = EnvironmentalHazard(
                hazard_type=hazard_type,
                position=Vector2D(x, y),
                radius=radius,
                damage=damage,
                duration=duration
            )
            
            env.hazards.append(hazard)
    
    def _generate_terrain(
        self,
        env: Environment,
        config: BiomeConfig,
        width: float,
        height: float,
        cell_size: float
    ):
        """
        Generate terrain using Perlin-noise-like patterns.
        
        Args:
            env: Environment to populate
            config: Biome configuration
            width: Environment width
            height: Environment height
            cell_size: Cell size
        """
        cols = int(width / cell_size)
        rows = int(height / cell_size)
        
        # Generate noise map for natural patterns
        noise_map = self._generate_noise_map(cols, rows)
        
        # Convert terrain distribution to cumulative probabilities
        terrain_types = list(config.terrain_distribution.keys())
        weights = list(config.terrain_distribution.values())
        cumulative = []
        total = 0
        for w in weights:
            total += w
            cumulative.append(total)
        
        # Generate terrain cells
        for row in range(rows):
            for col in range(cols):
                center_x = (col + 0.5) * cell_size
                center_y = (row + 0.5) * cell_size
                
                # Use noise value to select terrain type
                noise_value = noise_map[row][col]
                
                # Map noise to terrain type using distribution
                terrain = config.primary_terrain
                for i, threshold in enumerate(cumulative):
                    if noise_value * total < threshold:
                        terrain = terrain_types[i]
                        break
                
                # Add some clustering by checking neighbors
                # (Makes terrain more natural with larger patches)
                if col > 0 and row > 0:
                    neighbor_key = (col - 1, row - 1)
                    if neighbor_key in env.terrain_grid:
                        neighbor_terrain = env.terrain_grid[neighbor_key].terrain_type
                        # 30% chance to match neighbor for clustering
                        if self.rng.random() < 0.3:
                            terrain = neighbor_terrain
                
                # Resource richness varies
                resource_richness = self.rng.uniform(0.5, 1.5)
                if terrain == TerrainType.MARSH:
                    resource_richness *= 1.3
                elif terrain == TerrainType.DESERT:
                    resource_richness *= 0.6
                
                cell = TerrainCell(
                    terrain_type=terrain,
                    position=Vector2D(center_x, center_y),
                    resource_richness=resource_richness,
                    danger_level=0.0
                )
                env.terrain_grid[(col, row)] = cell
    
    def _generate_noise_map(self, cols: int, rows: int) -> List[List[float]]:
        """
        Generate a 2D noise map for terrain variation.
        
        Simple implementation using random values with smoothing.
        
        Args:
            cols: Number of columns
            rows: Number of rows
            
        Returns:
            2D list of noise values (0.0 to 1.0)
        """
        # Generate random base values
        noise = [[self.rng.random() for _ in range(cols)] for _ in range(rows)]
        
        # Smooth with simple averaging (creates more natural patterns)
        smoothed = [[0.0 for _ in range(cols)] for _ in range(rows)]
        for row in range(rows):
            for col in range(cols):
                total = 0.0
                count = 0
                
                # Average with neighbors
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        r, c = row + dr, col + dc
                        if 0 <= r < rows and 0 <= c < cols:
                            total += noise[r][c]
                            count += 1
                
                smoothed[row][col] = total / count
        
        return smoothed
    
    def _set_biome_weather(self, env: Environment, config: BiomeConfig):
        """
        Set weather conditions for the biome.
        
        Args:
            env: Environment to configure
            config: Biome configuration
        """
        temp = self.rng.uniform(*config.temperature_range)
        humidity = self.rng.uniform(*config.humidity_range)
        
        env.weather = WeatherConditions(
            weather_type=config.weather_type,
            temperature=temp,
            humidity=humidity,
            wind_speed=self.rng.uniform(0.0, 20.0)
        )
    
    def _place_hazards(
        self,
        env: Environment,
        config: BiomeConfig,
        width: float,
        height: float
    ):
        """
        Place environmental hazards in the biome.
        
        Args:
            env: Environment to populate
            config: Biome configuration
            width: Environment width
            height: Environment height
        """
        if not config.hazard_types:
            return
        
        # Number of hazards based on frequency and area
        area = width * height
        base_hazards = int((area / 1000.0) * config.hazard_frequency)
        num_hazards = self.rng.randint(max(1, base_hazards - 2), base_hazards + 2)
        
        for _ in range(num_hazards):
            hazard_type = self.rng.choice(config.hazard_types)
            
            # Random position
            x = self.rng.uniform(10, width - 10)
            y = self.rng.uniform(10, height - 10)
            
            # Hazard properties
            radius = self.rng.uniform(5.0, 15.0)
            damage = self.rng.uniform(2.0, 8.0)
            duration = self.rng.uniform(30.0, 120.0)  # 30-120 seconds
            
            hazard = EnvironmentalHazard(
                hazard_type=hazard_type,
                position=Vector2D(x, y),
                radius=radius,
                damage=damage,
                duration=duration
            )
            
            env.hazards.append(hazard)
    
    def _generate_mixed_biome(
        self,
        width: float,
        height: float,
        cell_size: float
    ) -> Environment:
        """
        Generate a mixed biome combining 2-3 biome types.
        
        Args:
            width: Environment width
            height: Environment height
            cell_size: Cell size
            
        Returns:
            Environment with mixed biome features
        """
        # Choose 2-3 biome types to mix
        available_biomes = [b for b in BiomeType if b != BiomeType.MIXED]
        num_biomes = self.rng.randint(2, 3)
        selected_biomes = self.rng.sample(available_biomes, num_biomes)
        
        # Create base environment
        env = Environment(
            width=width,
            height=height,
            cell_size=cell_size,
            enable_weather=True,
            enable_day_night=True
        )
        
        env.biome_name = "Mixed Biome"
        env.biome_description = f"Combination of {', '.join(b.value for b in selected_biomes)}"
        env.biome_difficulty = 3
        
        # Divide arena into regions for each biome
        cols = int(width / cell_size)
        rows = int(height / cell_size)
        
        # Create regions (simple division)
        region_configs = [self.BIOME_CONFIGS[b] for b in selected_biomes]
        
        for row in range(rows):
            for col in range(cols):
                # Determine which region this cell belongs to
                region_idx = (col * len(region_configs)) // cols
                config = region_configs[region_idx]
                
                center_x = (col + 0.5) * cell_size
                center_y = (row + 0.5) * cell_size
                
                # Select terrain from this region's distribution
                terrain = self._select_terrain_from_distribution(config.terrain_distribution)
                
                resource_richness = self.rng.uniform(0.5, 1.5)
                
                cell = TerrainCell(
                    terrain_type=terrain,
                    position=Vector2D(center_x, center_y),
                    resource_richness=resource_richness,
                    danger_level=0.0
                )
                env.terrain_grid[(col, row)] = cell
        
        # Set weather from one of the biomes
        primary_config = region_configs[0]
        self._set_biome_weather(env, primary_config)
        
        # Add hazards from all biomes
        for config in region_configs:
            if config.hazard_types:
                self._place_hazards(env, config, width, height)
        
        return env
    
    def _select_terrain_from_distribution(
        self,
        distribution: Dict[TerrainType, float]
    ) -> TerrainType:
        """
        Select a terrain type based on probability distribution.
        
        Args:
            distribution: Dict of terrain types to probabilities
            
        Returns:
            Selected terrain type
        """
        terrain_types = list(distribution.keys())
        weights = list(distribution.values())
        return self.rng.choices(terrain_types, weights=weights)[0]
    
    def get_pellet_spawn_config(self, biome_type: BiomeType) -> Dict:
        """
        Get pellet spawning configuration for a biome.
        
        Args:
            biome_type: Type of biome
            
        Returns:
            Dict with pellet spawn parameters
        """
        if biome_type == BiomeType.MIXED:
            return {
                'density': 1.2,
                'toxicity_bias': 0.0,
                'initial_count': 15
            }
        
        config = self.BIOME_CONFIGS.get(biome_type)
        if not config:
            return {'density': 1.0, 'toxicity_bias': 0.0, 'initial_count': 10}
        
        return {
            'density': config.pellet_density,
            'toxicity_bias': config.pellet_toxicity_bias,
            'initial_count': int(10 * config.pellet_density)
        }


def create_random_biome(
    width: float = 100.0,
    height: float = 100.0,
    seed: Optional[int] = None
) -> Tuple[Environment, BiomeType]:
    """
    Create a random biome environment.
    
    Args:
        width: Environment width
        height: Environment height
        seed: Random seed
        
    Returns:
        Tuple of (Environment, BiomeType)
    """
    generator = BiomeGenerator(seed)
    biome_type = random.choice(list(BiomeType))
    env = generator.generate_biome(biome_type, width, height)
    return env, biome_type
