"""
Environment Manager

Handles weather, terrain, hazards, and environmental effects
for the spatial battle system.

Extracted from battle_spatial.py.
"""

import random
from typing import Optional, List, Any

from src.models.spatial import Vector2D
from src.models.environment import Environment, EnvironmentalHazard, HazardType, WeatherType, TimeOfDay
from src.systems.battle_events import BattleEvent, BattleEventType
from .event_manager import EventManager

class EnvironmentManager:
    """
    Manages the battle environment.
    
    Responsibilities:
    - Update weather and time of day
    - Manage terrain and biomes
    - Handle environmental hazards
    - Calculate environmental effects on creatures
    """
    
    def __init__(
        self,
        event_manager: EventManager,
        width: float,
        height: float,
        enable_environment: bool = False,
        environment: Optional[Environment] = None,
        biome_type: Optional[str] = None,
        random_seed: Optional[int] = None
    ):
        """
        Initialize the environment manager.
        
        Args:
            event_manager: Event manager for emitting events
            width: Arena width
            height: Arena height
            enable_environment: Whether to enable environmental simulation
            environment: Existing environment instance (optional)
            biome_type: Type of biome to generate (optional)
            random_seed: Seed for random generation
        """
        self.event_manager = event_manager
        self.width = width
        self.height = height
        
        # Hazard management
        self.hazard_interval: float = 45.0
        self.last_hazard_time: float = 0.0
        
        # Initialize environment
        self.environment = self._initialize_environment(
            enable_environment, environment, biome_type, random_seed
        )
        
    def _initialize_environment(
        self,
        enable_environment: bool,
        environment: Optional[Environment],
        biome_type: Optional[str],
        random_seed: Optional[int]
    ) -> Optional[Environment]:
        """Initialize the environment based on configuration."""
        if biome_type and environment is None:
            # Generate biome-based environment
            from src.systems.biome_generator import BiomeGenerator, BiomeType
            
            generator = BiomeGenerator(seed=random_seed)
            
            # Parse biome type
            if biome_type.lower() == 'random':
                import random as rand
                # 20% chance for multi-biome
                if rand.random() < 0.2:
                    biome_enum = 'multi'
                else:
                    biome_enum = rand.choice(list(BiomeType))
            elif biome_type.lower() == 'multi':
                biome_enum = 'multi'
            else:
                try:
                    biome_enum = BiomeType(biome_type.lower())
                except ValueError:
                    # Default to grassland if invalid
                    biome_enum = BiomeType.GRASSLAND
            
            if biome_enum == 'multi':
                # Generate multi-biome environment
                return generator.generate_multi_biome(self.width, self.height)
            else:
                # Generate single biome environment
                return generator.generate_biome(biome_enum, self.width, self.height)
            
        elif enable_environment or environment is not None:
            return environment if environment else Environment(
                width=self.width,
                height=self.height,
                enable_weather=True,
                enable_day_night=True
            )
        else:
            return None

    def update(self, delta_time: float):
        """
        Update environment state for one frame.
        
        Args:
            delta_time: Time elapsed since last update
        """
        if self.environment:
            self.environment.update(delta_time)

    def get_creature_environmental_adaptation(self, creature: Any, position: Vector2D) -> float:
        """
        Calculate creature's environmental adaptation modifier based on traits.
        
        Args:
            creature: The BattleCreature
            position: Current position
            
        Returns:
            Movement speed modifier (0.5 to 2.0)
        """
        if not self.environment:
            return 1.0
        
        modifier = 1.0
        trait_names = [t.name.lower() for t in creature.creature.traits]
        
        # Get terrain type
        terrain = self.environment.get_terrain_at(position)
        if terrain:
            terrain_name = terrain.terrain_type.name.lower()
            
            # Terrain-specific adaptations
            if 'aquatic' in ' '.join(trait_names) and 'water' in terrain_name:
                modifier *= 2.0  # Double speed in water
            elif 'aquatic' in ' '.join(trait_names):
                modifier *= 0.7  # Slower on land
            
            if 'rock climber' in ' '.join(trait_names) and 'rocky' in terrain_name:
                modifier *= 1.5
            
            if 'forest dweller' in ' '.join(trait_names) and 'forest' in terrain_name:
                modifier *= 1.4
            
            if 'desert adapted' in ' '.join(trait_names) and 'desert' in terrain_name:
                modifier *= 1.3
            
            if 'marsh navigator' in ' '.join(trait_names) and 'marsh' in terrain_name:
                modifier *= 1.8
            
            if 'all terrain' in ' '.join(trait_names):
                modifier *= 1.05  # Small bonus everywhere
        
        # Weather adaptations
        if self.environment.weather:
            temp = self.environment.weather.temperature
            
            if 'cold blooded' in ' '.join(trait_names):
                if temp > 25:
                    modifier *= 1.2
                elif temp < 10:
                    modifier *= 0.8
            
            if 'heat resistant' in ' '.join(trait_names) and temp > 30:
                modifier *= 1.25
            
            if 'storm walker' in ' '.join(trait_names):
                if self.environment.weather.weather_type == WeatherType.STORMY:
                    modifier *= 1.1
        
        # Time of day adaptations
        if self.environment.day_night:
            time_of_day = self.environment.day_night.get_time_of_day()
            
            if 'nocturnal' in ' '.join(trait_names):
                if time_of_day == TimeOfDay.NIGHT:
                    modifier *= 1.3
                elif time_of_day == TimeOfDay.DAY:
                    modifier *= 0.85
            
            if 'diurnal' in ' '.join(trait_names):
                if time_of_day == TimeOfDay.DAY:
                    modifier *= 1.2
                elif time_of_day == TimeOfDay.NIGHT:
                    modifier *= 0.9
            
            if 'crepuscular' in ' '.join(trait_names):
                if time_of_day in (TimeOfDay.DAWN, TimeOfDay.DUSK):
                    modifier *= 1.25
        
        return max(0.5, min(2.0, modifier))

    def calculate_hazard_damage(self, creature: Any, base_damage: float) -> float:
        """
        Calculate actual hazard damage after applying trait resistances.
        
        Args:
            creature: The BattleCreature taking damage
            base_damage: Base environmental damage
            
        Returns:
            Actual damage after resistance modifiers
        """
        damage = base_damage
        trait_names = [t.name.lower() for t in creature.creature.traits]
        
        # Check for hazard resistance traits
        if 'tough skin' in ' '.join(trait_names):
            damage *= 0.8
        
        if 'extremophile' in ' '.join(trait_names):
            damage *= 0.5
            
        if 'adaptive' in ' '.join(trait_names):
            damage *= 0.9
            
        return damage
    
    def trigger_hazard(self, alive_creatures: List[Any], arena: Any, event_manager: Any, current_time: float):
        """
        Trigger a random environmental hazard that affects all creatures.
        
        Hazards encourage creatures to work together or find safe zones.
        
        Args:
            alive_creatures: List of all alive creatures
            arena: The battle arena (for resource manipulation)
            event_manager: Event manager for emitting events
            current_time: Current simulation time
        """
        if not alive_creatures:
            return
        
        hazard_types = ['storm', 'heat_wave', 'resource_scarcity']
        hazard = random.choice(hazard_types)
        
        if hazard == 'storm':
            # Storm damages all creatures slightly, encouraging them to seek shelter together
            damage = random.randint(3, 8)
            safe_zone = Vector2D(
                random.uniform(self.width * 0.2, self.width * 0.8),
                random.uniform(self.height * 0.2, self.height * 0.8)
            )
            safe_radius = min(self.width, self.height) * 0.15
            
            affected_count = 0
            for creature in alive_creatures:
                distance_to_safe = creature.spatial.position.distance_to(safe_zone)
                if distance_to_safe > safe_radius:
                    # Creature takes damage from storm
                    actual_damage = creature.creature.stats.take_damage(damage)
                    if actual_damage > 0:
                        affected_count += 1
            
            event_manager.log(f"⚡ STORM! {affected_count} creatures caught outside safe zone took {damage} damage")
            event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.HAZARD_DAMAGE,
                message=f"Storm hits the arena! {affected_count} creatures damaged",
                data={'hazard_type': 'storm', 'damage': damage, 'affected': affected_count}
            ))
        
        elif hazard == 'heat_wave':
            # Heat wave increases hunger depletion temporarily
            event_manager.log(f"🔥 HEAT WAVE! All creatures' hunger depletes faster")
            event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.HAZARD_DAMAGE,
                message="Heat wave strikes! Hunger increases faster",
                data={'hazard_type': 'heat_wave', 'duration': 10.0}
            ))
            # Temporarily increase hunger depletion for all creatures
            for creature in alive_creatures:
                # Reduce hunger by extra amount
                creature.creature.hunger = max(0, creature.creature.hunger - 5)
        
        elif hazard == 'resource_scarcity':
            # Remove some resources, encouraging cooperation in foraging
            resources_before = len(arena.resources)
            if resources_before > 0:
                remove_count = max(1, resources_before // 3)
                for _ in range(remove_count):
                    if arena.resources:
                        arena.resources.pop()
                
                event_manager.log(f"🌾 RESOURCE SCARCITY! {remove_count} food sources disappeared")
                event_manager.emit_event(BattleEvent(
                    event_type=BattleEventType.HAZARD_DAMAGE,
                    message=f"Resource scarcity! {remove_count} food sources vanish",
                    data={'hazard_type': 'resource_scarcity', 'removed': remove_count}
                ))

