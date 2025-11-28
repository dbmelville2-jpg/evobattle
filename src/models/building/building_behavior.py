"""
Building Behavior System - AI for Creature Construction

This module implements the AI logic for creatures to:
- Identify building needs (shelter, food storage, etc.)
- Select appropriate building types
- Find suitable build locations
- Gather and transport materials
- Construct buildings tile by tile

Integrates with the belief/learning system so creatures can learn
building behaviors and pass them to offspring.
"""

from enum import Enum
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
import random
import math

from .building_config import (
    Building, BuildingType, BuildingBlueprint, 
    get_blueprint, BUILDING_BLUEPRINTS
)
from .building_material import (
    BuildingMaterial, MaterialType, get_material_weight
)
from src.models.spatial import Vector2D
from src.models.creature_beliefs import CreatureBeliefSystem, CreatureBelief, BeliefType


class BuildingNeed(Enum):
    """Types of building needs creatures can identify"""
    SHELTER = "shelter"           # Need protection from weather
    FOOD_STORAGE = "food_storage" # Need to preserve food
    BREEDING = "breeding"         # Need safe place to breed
    DEFENSE = "defense"           # Need protection from threats
    VISION = "vision"             # Need better awareness
    TERRITORY = "territory"       # Need to mark territory
    SOCIAL = "social"             # Need gathering place
    SUSTENANCE = "sustenance"     # Need sustainable food


@dataclass
class BuildingTask:
    """
    Represents an active building task for a creature.
    
    Tracks the current state of construction.
    """
    Building_type: BuildingType
    target_position: Vector2D
    blueprint: BuildingBlueprint
    materials_needed: Dict[MaterialType, int]
    materials_gathered: Dict[MaterialType, int]
    construction_progress: float = 0.0
    started: bool = False
    
    def is_materials_complete(self) -> bool:
        """Check if all materials have been gathered"""
        for mat_type, needed in self.materials_needed.items():
            gathered = self.materials_gathered.get(mat_type, 0)
            if gathered < needed:
                return False
        return True
    
    def get_next_material_needed(self) -> Optional[MaterialType]:
        """Get the next material type that needs to be gathered"""
        for mat_type, needed in self.materials_needed.items():
            gathered = self.materials_gathered.get(mat_type, 0)
            if gathered < needed:
                return mat_type
        return None



@dataclass
class BuildingDecision:
    """Result of a building behavior update"""
    action_type: str  # "NONE", "MOVE", "GATHER", "BUILD", "START_TASK", "CONSTRUCT"
    target_position: Optional[Vector2D] = None
    target_entity: Optional[object] = None
    metadata: Optional[Dict] = None


class BuildingBehaviorSystem:
    """
    Manages building behavior AI for creatures.
    
    This system determines when creatures should build, what they should
    build, and coordinates the construction process.
    """
    
    def __init__(self):
        """Initialize building behavior system"""
        self.active_tasks: Dict[str, BuildingTask] = {}  # creature_id -> task
        self.material_detection_range = 150.0  # Base range to detect materials (increased for 200x200 arena)
        
    def identify_building_need(self, creature, environment, nearby_Buildings: List[Building]) -> Optional[BuildingNeed]:
        """
        Determine if creature has a building need.
        
        Args:
            creature: The creature to evaluate
            environment: Current environment state
            nearby_Buildings: Buildings near the creature
            
        Returns:
            BuildingNeed if creature should build, None otherwise
        """
        # Check various conditions to determine need
        
        # Need shelter if HP is low or weather is harsh (relaxed from 50% to 80%)
        if hasattr(environment, 'weather'):
            if creature.stats.hp < creature.stats.max_hp * 0.8:  # Relaxed from 0.5
                if environment.weather.weather_type.value in ['storm', 'rain']:
                    return BuildingNeed.SHELTER
        
        # Random chance for comfort shelter (2%)
        if random.random() < 0.02:
            return BuildingNeed.SHELTER
        
        # Need food storage if moderately well-fed (relaxed from 80 to 60)
        if hasattr(creature, 'hunger'):
            if creature.hunger > 60:  # Relaxed from 80
                # Check if we already have a cache nearby
                has_cache = any(s.building_type == BuildingType.FOOD_CACHE 
                              for s in nearby_Buildings)
                if not has_cache:
                    return BuildingNeed.FOOD_STORAGE
        
        # Need breeding nest if ready to breed
        if hasattr(creature, 'can_breed') and creature.can_breed():
            # Check if no nest nearby
            has_nest = any(s.building_type == BuildingType.NEST 
                          for s in nearby_Buildings if s.is_complete())
            if not has_nest:
                return BuildingNeed.BREEDING
        
        # Need defense if threatened
        if hasattr(creature, 'threat_level'):
            if creature.threat_level > 0.5:
                return BuildingNeed.DEFENSE
        
        # Increased chance for social/territory needs (5% from 1%)
        if random.random() < 0.05:  # Increased from 0.01
            return random.choice([BuildingNeed.SOCIAL, BuildingNeed.TERRITORY])
        
        return None
    
    def select_Building_type(self, need: BuildingNeed, creature_traits: List) -> BuildingType:
        """
        Choose appropriate building type for a need.
        
        Args:
            need: The building need
            creature_traits: Creature's traits (affects choices)
            
        Returns:
            BuildingType to build
        """
        # Map needs to building types
        need_to_Building = {
            BuildingNeed.SHELTER: BuildingType.SHELTER,
            BuildingNeed.FOOD_STORAGE: BuildingType.FOOD_CACHE,
            BuildingNeed.BREEDING: BuildingType.NEST,
            BuildingNeed.DEFENSE: BuildingType.BARRIER,
            BuildingNeed.VISION: BuildingType.WATCHTOWER,
            BuildingNeed.TERRITORY: BuildingType.TERRITORY_MARKER,
            BuildingNeed.SOCIAL: BuildingType.SHRINE,
            BuildingNeed.SUSTENANCE: BuildingType.GARDEN
        }
        
        base_Building = need_to_Building.get(need, BuildingType.SHELTER)
        
        # Innovator trait might choose different/combined Buildings
        has_innovator = any(getattr(t, 'name', '') == 'Innovator' for t in creature_traits)
        if has_innovator and random.random() < 0.2:
            # 20% chance to choose alternative building type
            alternatives = list(BUILDING_BLUEPRINTS.keys())
            return random.choice(alternatives)
        
        return base_Building
    
    def find_build_location(self, creature_position: Vector2D, 
                           Building_type: BuildingType,
                           arena_bounds: Tuple[float, float, float, float],
                           existing_Buildings: List[Building]) -> Optional[Vector2D]:
        """
        Find suitable location to build Building.
        
        Creatures can build wherever they want, as long as it's not too close
        to other Buildings and within arena bounds.
        
        Args:
            creature_position: Current creature position
            Building_type: Type of building to build
            arena_bounds: (min_x, min_y, max_x, max_y)
            existing_Buildings: Already built buildings
            
        Returns:
            Vector2D position or None if no suitable location
        """
        blueprint = get_blueprint(Building_type)
        footprint = blueprint.get_footprint_size()
        
        # Minimum distance to keep from other buildings (prevent overcrowding)
        min_distance_from_Buildings = 15.0  # Reduced from 20 to allow closer building
        max_attempts = 30  # Increased attempts to find a good spot
        
        for _ in range(max_attempts):
            # Build near creature's current position
            # Allow building in a wider area around the creature
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(5, 25)  # Closer to creature (was 10-30)
            
            x = creature_position.x + distance * math.cos(angle)
            y = creature_position.y + distance * math.sin(angle)
            
            # Check bounds - make sure building fits in arena
            margin = max(footprint[0], footprint[1]) * 2  # Give some margin
            if x < arena_bounds[0] + margin or x > arena_bounds[2] - margin:
                continue
            if y < arena_bounds[1] + margin or y > arena_bounds[3] - margin:
                continue
            
            # Check distance from other buildings to prevent overcrowding
            pos = Vector2D(x, y)
            too_close = False
            for Building in existing_Buildings:
                dist = math.sqrt((pos.x - Building.position.x)**2 + 
                               (pos.y - Building.position.y)**2)
                if dist < min_distance_from_Buildings:
                    too_close = True
                    break
            
            if not too_close:
                return pos
        
        # If we couldn't find a spot after many attempts, just build right where creature is
        # as long as it's in bounds
        if (arena_bounds[0] + margin < creature_position.x < arena_bounds[2] - margin and
            arena_bounds[1] + margin < creature_position.y < arena_bounds[3] - margin):
            return Vector2D(creature_position.x, creature_position.y)
        
        return None
    
    def find_nearest_material(self, creature_position: Vector2D,
                             material_type: MaterialType,
                             available_materials: List[BuildingMaterial],
                             creature_traits: List = None) -> Optional[BuildingMaterial]:
        """
        Find nearest material of specified type.
        
        Args:
            creature_position: Creature's position
            material_type: Type of material needed
            available_materials: Materials on the ground
            creature_traits: Creature's traits (affects detection range)
            
        Returns:
            Nearest BuildingMaterial or None
        """
        # Adjust detection range based on traits
        detection_range = 50.0  # Default reduced range
        if creature_traits:
            # Check for Builder trait
            has_builder = any(getattr(t, 'name', '') == 'Builder' for t in creature_traits)
            if has_builder:
                detection_range = 150.0  # Extended range for builders
        
        nearest = None
        nearest_dist = float('inf')
        
        for material in available_materials:
            # Skip if wrong type or already carried
            if material.material_type != material_type:
                continue
            if material.is_carried():
                continue
            
            # Calculate distance
            dist = math.sqrt((creature_position.x - material.position.x)**2 +
                           (creature_position.y - material.position.y)**2)
            
            # Check if within detection range
            if dist > detection_range:
                continue
            
            if dist < nearest_dist:
                nearest = material
                nearest_dist = dist
        
        return nearest
    
    
    def calculate_building_urgency(
        self, 
        creature_traits: List,
        has_active_task: bool,
        materials_nearby: int,
        strain_building_exists: bool
    ) -> float:
        """
        Calculate building urgency multiplier based on context.
        
        Args:
            creature_traits: Creature's traits
            has_active_task: Whether creature has an active building task
            materials_nearby: Number of materials available nearby
            strain_building_exists: Whether there's an incomplete strain building
            
        Returns:
            Urgency multiplier (0.5-3.0)
        """
        # Base urgency
        urgency = 1.0
        
        # Trait-based urgency
        has_architect = any(getattr(t, 'name', '') == "Architect" for t in creature_traits)
        has_builder = any(getattr(t, 'name', '') == "Builder" for t in creature_traits)
        has_material_gatherer = any(getattr(t, 'name', '') == "Material Gatherer" for t in creature_traits)
        
        if has_architect:
            urgency *= 2.0  # Architects are very motivated
        elif has_builder:
            urgency *= 1.5  # Builders are motivated
        elif has_material_gatherer:
            urgency *= 1.2  # Material gatherers somewhat motivated
        else:
            urgency *= 0.5  # Others are less motivated
        
        # Context-based urgency
        if has_active_task:
            urgency *= 1.3  # Committed to current task
        
        if materials_nearby > 0:
            urgency *= 1.2  # Materials available
        
        if strain_building_exists:
            urgency *= 1.15  # Help your strain
        
        return urgency
    
    def find_strain_building(self, creature_strain_id: Optional[str], 
                            creature_position: Vector2D,
                            existing_buildings: List[Building]) -> Optional[Building]:
        """
        Find the nearest incomplete building started by the same genetic strain.
        
        Args:
            creature_strain_id: The creature's genetic strain ID
            creature_position: Creature's current position
            existing_buildings: List of all buildings
            
        Returns:
            Nearest incomplete building from same strain, or None
        """
        if not creature_strain_id:
            return None
        
        nearest = None
        nearest_dist = float('inf')
        
        for building in existing_buildings:
            # Skip completed buildings
            if building.is_complete():
                continue
            
            # Check if same strain
            if building.builder_strain_id != creature_strain_id:
                continue
            
            # Calculate distance
            dist = math.sqrt((creature_position.x - building.position.x)**2 +
                           (creature_position.y - building.position.y)**2)
            
            if dist < nearest_dist:
                nearest = building
                nearest_dist = dist
        
        return nearest
    
    def can_carry_material(self, creature_traits: List, current_carry_count: int) -> bool:
        """
        Check if creature can carry more materials.
        
        Args:
            creature_traits: Creature's traits
            current_carry_count: How many materials currently carrying
            
        Returns:
            True if can carry more
        """
        base_capacity = 1
        
        # Material Gatherer trait increases capacity
        for trait in creature_traits:
            if getattr(trait, 'name', '') == 'Material Gatherer':
                effects = getattr(trait, 'interaction_effects', {})
                multiplier = effects.get('carry_capacity_multiplier', 1.0)
                base_capacity = int(base_capacity * multiplier)
                break
        
        return current_carry_count < base_capacity
    
    def get_build_speed_multiplier(self, creature_traits: List, is_cooperating: bool = False) -> float:
        """
        Calculate build speed multiplier based on traits.
        
        Args:
            creature_traits: Creature's traits
            is_cooperating: Whether building with others
            
        Returns:
            Speed multiplier (1.0 = normal)
        """
        multiplier = 0.3  # Default: Non-specialized creatures build very slowly (30% speed)
        
        for trait in creature_traits:
            trait_name = getattr(trait, 'name', '')
            effects = getattr(trait, 'interaction_effects', {})
            
            if trait_name == 'Architect':
                # Architects ignore the penalty and get their bonus
                multiplier = 1.0 * effects.get('build_speed_multiplier', 1.0)
            
            elif trait_name == 'Builder':
                 # Builders also ignore penalty
                 multiplier = 1.0 * effects.get('build_speed_multiplier', 1.0)
            
            elif trait_name == 'Cooperative Builder' and is_cooperating:
                multiplier *= effects.get('cooperative_speed_bonus', 1.0)
            
            elif trait_name == 'Planner':
                # Planner has delay at start but not ongoing penalty
                pass
        
        return multiplier
    
    def get_Building_durability_multiplier(self, creature_traits: List) -> float:
        """
        Calculate building durability multiplier based on traits.
        
        Args:
            creature_traits: Creature's traits
            
        Returns:
            Durability multiplier (1.0 = normal)
        """
        multiplier = 1.0
        
        for trait in creature_traits:
            if getattr(trait, 'name', '') == 'Architect':
                effects = getattr(trait, 'interaction_effects', {})
                multiplier *= effects.get('Building_durability_bonus', 1.0)
                break
        
        return multiplier
    
    def update_building_task(self, creature_id: str, dt: float) -> Optional[BuildingTask]:
        """
        Update active building task progress.
        
        Args:
            creature_id: ID of creature
            dt: Time delta
            
        Returns:
            Completed task if finished, None otherwise
        """
        if creature_id not in self.active_tasks:
            return None
        
        task = self.active_tasks[creature_id]
        
        # Can only build if materials are complete
        if not task.is_materials_complete():
            return None
        
        # Progress construction
        task.construction_progress += dt
        
        # Check if complete
        if task.construction_progress >= task.blueprint.build_time:
            del self.active_tasks[creature_id]
            return task
        
        return None
    
    def cancel_building_task(self, creature_id: str):
        """Cancel active building task"""
        if creature_id in self.active_tasks:
            del self.active_tasks[creature_id]
    
    def get_active_task(self, creature_id: str) -> Optional[BuildingTask]:
        """Get creature's active building task"""
        return self.active_tasks.get(creature_id)
    
    def start_building_task(self, creature_id: str, Building_type: BuildingType, location: Vector2D) -> BuildingTask:
        """
        Start a new building task for a creature.
        
        Args:
            creature_id: ID of the creature
            Building_type: Type of building to build
            location: Where to build the building
            
        Returns:
            The newly created BuildingTask
        """
        blueprint = get_blueprint(Building_type)
        
        # Initialize materials needed and gathered dictionaries
        materials_needed = dict(blueprint.required_materials)
        materials_gathered = {mat_type: 0 for mat_type in materials_needed.keys()}
        
        # Create the task
        task = BuildingTask(
            Building_type=Building_type,
            target_position=location,
            blueprint=blueprint,
            materials_needed=materials_needed,
            materials_gathered=materials_gathered,
            construction_progress=0.0,
            started=False
        )
        
        # Register it
        self.active_tasks[creature_id] = task
        return task

    def deposit_material(self, creature_id: str, material_type: MaterialType) -> bool:
        """
        Deposit a material into the active task.
        
        Args:
            creature_id: ID of creature
            material_type: Type of material being deposited
            
        Returns:
            True if successful, False if no task or material not needed
        """
        task = self.active_tasks.get(creature_id)
        if not task:
            return False
            
        needed = task.materials_needed.get(material_type, 0)
        gathered = task.materials_gathered.get(material_type, 0)
        
        if gathered < needed:
            task.materials_gathered[material_type] = gathered + 1
            return True
            
        return False

    def identify_repair_need(self, creature, nearby_Buildings: List[Building]) -> Optional[Building]:
        """
        Identify if any nearby Building needs repair.
        
        Args:
            creature: The creature to evaluate
            nearby_Buildings: Buildings near the creature
            
        Returns:
            Building to repair or None
        """
        # Only Architects or Builders care about repair
        has_repair_trait = any(t.name in ["Architect", "Builder"] for t in creature.traits)
        if not has_repair_trait:
            return None
            
        # Find damaged buildings
        damaged = [s for s in nearby_Buildings if s.is_damaged() and not s.is_destroyed()]
        if not damaged:
            return None
            
        # Sort by damage (most damaged first)
        damaged.sort(key=lambda s: s.durability)
        
        # Return the most damaged one within reasonable range
        # For now just the first one, assuming nearby_Buildings are already spatially relevant
        return damaged[0]

    def update_creature_building(self, creature, creature_position: Vector2D, environment, nearby_Buildings: List[Building], 
                               available_materials: List[BuildingMaterial], arena_bounds: Tuple[float, float, float, float]) -> BuildingDecision:
        """
        Main update loop for creature building behavior.
        
        Args:
            creature: The creature model
            creature_position: Current position
            environment: Environment state
            nearby_Buildings: List of nearby buildings
            available_materials: List of materials on ground
            arena_bounds: Arena boundaries
            
        Returns:
            BuildingDecision indicating what the creature wants to do
        """
        creature_id = creature.creature_id
        
        # Allow all creatures to build, but non-Architects will be much slower
        # (Handled in get_build_speed_multiplier)
            
        task = self.get_active_task(creature_id)
        
        # 0. Check for emergency repairs (high priority for Architects)
        repair_target = self.identify_repair_need(creature, nearby_Buildings)
        if repair_target:
            # If we are already building something else, maybe pause? 
            # For simplicity, finish current task first unless it's just starting.
            if not task or not task.started:
                # Go repair
                dist = math.sqrt((creature_position.x - repair_target.position.x)**2 + (creature_position.y - repair_target.position.y)**2)
                if dist < 5.0:
                    return BuildingDecision("CONSTRUCT", target_position=repair_target.position, metadata={"repair": True})
                else:
                    return BuildingDecision("MOVE", target_position=repair_target.position)

        # 1. If no task, check if we should start one
        if not task:
            # Only start building if there are materials available to use
            # This prevents startup spam where everyone tries to build instantly
            if not available_materials and not getattr(creature, 'carried_materials', []):
                # DEBUG: Log why not starting
                # if random.random() < 0.01:  # Log 1% of the time to avoid spam
                #     print(f"DEBUG: {creature.name} - No materials available, not starting building task")
                return BuildingDecision("NONE")
            
            # COOPERATIVE BUILDING: Check if there's an incomplete building from our strain first
            creature_strain_id = getattr(creature, 'strain_id', None)
            strain_building = self.find_strain_building(creature_strain_id, creature_position, nearby_Buildings)
            
            if strain_building:
                # Found an incomplete building from our strain - help complete it!
                # Start a task to work on this existing building
                self.start_building_task(creature_id, strain_building.building_type, strain_building.position)
                return BuildingDecision("START_TASK", target_position=strain_building.position, 
                                      metadata={"Building_type": strain_building.building_type.value, "cooperative": True})
                
            need = self.identify_building_need(creature, environment, nearby_Buildings)
            if need:
                Building_type = self.select_Building_type(need, creature.traits)
                location = self.find_build_location(creature_position, Building_type, arena_bounds, nearby_Buildings)
                
                if location:
                    # Start task
                    self.start_building_task(creature_id, Building_type, location)
                    # print(f"DEBUG: {creature.name} starting building task for {Building_type.value} at {location}")
                    return BuildingDecision("START_TASK", target_position=location, metadata={"Building_type": Building_type.value})
                else:
                    pass
                    # if random.random() < 0.01:
                    #     print(f"DEBUG: {creature.name} - Could not find build location")
            else:
                pass
                # if random.random() < 0.001:  # Very rare log
                #     print(f"DEBUG: {creature.name} - No building need identified")
            
            return BuildingDecision("NONE")
            
        # 2. If task exists, execute next step
        
        # Check if the building we're working on is already complete
        # Find the building at the task location
        for building in nearby_Buildings:
            dist_sq = (building.position.x - task.target_position.x)**2 + (building.position.y - task.target_position.y)**2
            if dist_sq < 25.0:  # Same tolerance as BUILD
                if building.is_complete():
                    # Building is done! Cancel task
                    self.cancel_task(creature_id)
                    return BuildingDecision("NONE")
                break
        
        # Check if we need materials
        needed_material_type = task.get_next_material_needed()
        
        if needed_material_type:
            # We need materials. Do we have them carried?
            # Check creature's carried materials
            carried = [m for m in creature.carried_materials if m.material_type == needed_material_type]
            
            if carried:
                # We have the material, go to build site
                dist = math.sqrt((creature_position.x - task.target_position.x)**2 + (creature_position.y - task.target_position.y)**2)
                if dist < 5.0: # Build range
                    return BuildingDecision("BUILD", target_position=task.target_position, target_entity=carried[0])
                else:
                    return BuildingDecision("MOVE", target_position=task.target_position)
            else:
                # We need to find and gather material
                creature_traits = getattr(creature, 'traits', [])
                material = self.find_nearest_material(creature_position, needed_material_type, available_materials, creature_traits)
                if material:
                    dist = math.sqrt((creature_position.x - material.position.x)**2 + (creature_position.y - material.position.y)**2)
                    if dist < 2.0: # Gather range
                        return BuildingDecision("GATHER", target_position=material.position, target_entity=material)
                    else:
                        return BuildingDecision("MOVE", target_position=material.position)
                else:
                    # No material found... cancel task? or wander?
                    # if random.random() < 0.01:
                    #     print(f"DEBUG: {creature.name} - Looking for {needed_material_type.value} but can't find any (available: {len(available_materials)})")
                    return BuildingDecision("NONE") # Wander/Explore
        
        # If we have all materials, continue building (progress bar)
        # This state implies we are at the site and just need to work
        dist = math.sqrt((creature_position.x - task.target_position.x)**2 + (creature_position.y - task.target_position.y)**2)
        if dist < 5.0:
             return BuildingDecision("CONSTRUCT", target_position=task.target_position)
        else:
             return BuildingDecision("MOVE", target_position=task.target_position)

    def get_build_speed_multiplier(self, traits: List[Any]) -> float:
        """Calculate build speed multiplier from traits."""
        multiplier = 1.0
        for trait in traits:
            if hasattr(trait, 'interaction_effects'):
                effects = trait.interaction_effects
                if effects.get('build_speed_multiplier'):
                    multiplier *= effects['build_speed_multiplier']
                if effects.get('construction_speed_bonus'):
                    multiplier *= (1.0 + effects['construction_speed_bonus'])
        return multiplier

