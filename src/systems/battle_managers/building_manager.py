import random
import math
from typing import List, Dict, Optional, Tuple, Any
from src.models.building.building_config import Building, BuildingType, get_blueprint
from src.models.building.building_material import BuildingMaterial, MaterialType, create_random_material
from src.models.building.building_config import BuildingConfig
from src.models.spatial import Vector2D, Arena
from src.models.building.building_behavior import BuildingBehaviorSystem, BuildingDecision
from src.systems.battle_managers.event_manager import EventManager
from src.systems.battle_events import BattleEvent, BattleEventType

class BuildingManager:
    """
    Manages the lifecycle of buildings, material spawning, and building coordination.
    """
    
    def __init__(
        self,
        event_manager: EventManager,
        arena: Arena,
        config: Optional[BuildingConfig] = None
    ):
        self.event_manager = event_manager
        self.arena = arena
        self.config = config if config else BuildingConfig()
        
        # Core state
        self.buildings: List[Building] = []
        self.materials: List[BuildingMaterial] = []
        
        # Sub-systems
        self.behavior_system = BuildingBehaviorSystem()
        
        # Spawning state
        self.time_since_last_spawn = 0.0
        self.current_time = 0.0  # Track current time for material expiration
        
    def update(self, delta_time: float, current_time: float, weather_type: str = "clear"):
        """Main update loop."""
        if not self.config.building_enabled:
            return
        
        # Store current time for material expiration
        self.current_time = current_time
            
        # 1. Update buildings (decay, effects)
        self._update_Buildings(delta_time, weather_type)
        
        # 2. Remove expired materials
        self._remove_expired_materials(current_time)
        
        # 3. Spawn materials
        self._update_material_spawning(delta_time)
        
        # 4. Update active building tasks
        # Note: Creature-specific updates happen in AI loop via update_creature_building
        
    def _update_Buildings(self, delta_time: float, weather_type: str):
        """Update building state, decay, and removal."""
        active_buildings = []
        
        for building in self.buildings:
            # Skip if already destroyed (should be cleaned up, but just in case)
            if building.is_destroyed():
                continue
                
            # Update age
            if building.is_complete():
                building.age += delta_time
                
                # Apply decay
                decay_rate = self.config.base_decay_rate
                
                # Apply weather multiplier
                weather_mult = self.config.weather_decay_multiplier.get(weather_type, 1.0)
                
                # Apply building-specific resistance (from blueprint)
                blueprint = get_blueprint(building.building_type)
                resistance = blueprint.weather_resistance.get(weather_type, 1.0)
                
                # Calculate final decay
                # Convert per-minute rate to per-second
                decay_amount = (decay_rate / 60.0) * weather_mult * resistance * delta_time
                
                building.damage(decay_amount)
                
                if building.is_destroyed():
                    self.event_manager.log(f"Building {building.building_type.value} collapsed from decay!")
                    continue
            
            active_buildings.append(building)
            
        self.buildings = active_buildings

    def _remove_expired_materials(self, current_time: float):
        """Remove materials that have expired."""
        # Filter out expired materials (but keep carried materials)
        active_materials = []
        for material in self.materials:
            if material.is_carried() or not material.is_expired(current_time):
                active_materials.append(material)
        
        self.materials = active_materials

    def _update_material_spawning(self, delta_time: float):
        """Spawn new materials periodically."""
        # Skip if material spawning is disabled
        if self.config.material_spawn_rate <= 0:
            return
            
        self.time_since_last_spawn += delta_time
        
        spawn_interval = 1.0 / self.config.material_spawn_rate
        
        if self.time_since_last_spawn >= spawn_interval:
            self.time_since_last_spawn = 0
            self._spawn_random_material()
            
    def _spawn_random_material(self):
        """Spawn a single random material."""
        # Select type based on weights
        types = list(self.config.material_types_weights.keys())
        weights = list(self.config.material_types_weights.values())
        
        material_type = random.choices(types, weights=weights, k=1)[0]
        
        # Random position
        x = random.uniform(0, self.arena.width)
        y = random.uniform(0, self.arena.height)
        position = Vector2D(x, y)
        
        # Create material
        material = create_random_material(material_type, position, self.current_time)
        self.materials.append(material)
        
    def apply_Building_effects(self, creatures: List[Any]):
        """Apply active building effects to nearby creatures."""
        for building in self.buildings:
            if not building.is_complete() or not building.effects_active:
                continue
                
            blueprint = get_blueprint(building.building_type)
            radius = blueprint.effect_radius
            radius_sq = radius * radius
            
            for creature in creatures:
                if not creature.is_alive():
                    continue
                    
                # Check distance
                dist_sq = (creature.spatial.position.x - building.position.x)**2 + \
                          (creature.spatial.position.y - building.position.y)**2
                          
                if dist_sq <= radius_sq:
                    self._apply_single_Building_effect(building, creature, blueprint.effects)

    def _apply_single_Building_effect(self, building: Building, creature: Any, effects: Dict[str, Any]):
        """Apply specific effects from a building to a creature."""
        # HP Regen (Shelter)
        if 'hp_regen_bonus' in effects:
            regen = effects['hp_regen_bonus'] * 0.016  # Per frame (assuming 60fps)
            creature.creature.stats.hp = min(
                creature.creature.stats.max_hp,
                creature.creature.stats.hp + regen
            )
            
        # Breeding Bonus (Nest)
        if 'breeding_success_bonus' in effects:
            # This is handled in breeding check, but we can mark the creature
            creature.creature.current_building_bonus = effects['breeding_success_bonus']
            
        # Cooperation Bonus (Shrine)
        if 'cooperation_radius_bonus' in effects:
            # Handled in AI logic
            pass

    def update_creature_building(self, creature: Any, all_creatures: List[Any], delta_time: float) -> Optional[BuildingDecision]:
        """
        Coordinate building behavior for a single creature.
        Delegates to BuildingBehaviorSystem but manages global state.
        """
        # Check if creature can build
        if self.config.require_architect_trait:
            has_trait = any(t.name in ["Architect", "Builder"] for t in creature.creature.traits)
            if not has_trait:
                return None
                
        # Get decision from behavior system
        decision = self.behavior_system.update_creature_building(
            creature=creature.creature,
            creature_position=creature.spatial.position,
            environment=None,  # Passed in update loop if needed
            nearby_Buildings=self.buildings,
            available_materials=self.materials,
            arena_bounds=(0, 0, self.arena.width, self.arena.height)
        )
        
        # Handle state changes based on decision
        if decision.action_type == "START_TASK":
            # Check minimum spacing from other buildings before creating
            MIN_BUILDING_SPACING = 20.0
            for building in self.buildings:
                if building.is_destroyed():
                    continue
                
                dist_sq = (building.position.x - decision.target_position.x)**2 + \
                          (building.position.y - decision.target_position.y)**2
                
                if dist_sq < MIN_BUILDING_SPACING * MIN_BUILDING_SPACING:
                    # Too close to existing building - abort this build task
                    return None
            
            # Create new building placeholder
            stype = decision.metadata["Building_type"]
            if isinstance(stype, str):
                try:
                    stype = BuildingType(stype)
                except ValueError:
                    # Fallback or error logging
                    self.event_manager.log(f"Error: Invalid building type {stype}")
                    return decision
                    
            blueprint = get_blueprint(stype)
            
            # Generate tiles from blueprint pattern
            # Scale the pattern so tiles are larger and more visible
            BUILDING_SCALE = 3.0
            tiles = []
            for pattern_offset in blueprint.pattern:
                # Pattern offsets are relative (x, y) tuples
                tile_x = decision.target_position.x + pattern_offset[0] * BUILDING_SCALE
                tile_y = decision.target_position.y + pattern_offset[1] * BUILDING_SCALE
                tiles.append(Vector2D(tile_x, tile_y))
            
            # Create building instance
            import uuid
            # Get creature's strain ID
            creature_strain_id = getattr(creature.creature, 'strain_id', None)
            
            new_building = Building(
                building_id=str(uuid.uuid4()),
                building_type=blueprint.building_type,
                position=decision.target_position,
                tiles=tiles,  # Properly filled with tile positions from pattern
                builder_id=creature.creature.creature_id,
                builder_strain_id=creature_strain_id,  # Track which strain started this
                completion=0.0,
                durability=1.0
            )
            self.buildings.append(new_building)
            
            self.event_manager.log(f"{creature.creature.name} started building {blueprint.building_type.value}")
            
        elif decision.action_type == "GATHER":
            # Handle material pickup logic
            target_material = decision.target_entity
            if target_material and target_material in self.materials:
                # Check distance
                dist = math.sqrt((creature.spatial.position.x - target_material.position.x)**2 + 
                               (creature.spatial.position.y - target_material.position.y)**2)
                
                if dist < 2.0: # Pickup range
                    # Remove from ground
                    self.materials.remove(target_material)
                    
                    # Add to creature
                    target_material.carrier_id = creature.creature.creature_id
                    creature.creature.carried_materials.append(target_material)
                    
                    self.event_manager.log(f"{creature.creature.name} gathered {target_material.material_type.value}")
            
        elif decision.action_type == "BUILD":
            # Deposit material
            target_material = decision.target_entity
            if target_material and target_material in creature.creature.carried_materials:
                # Check distance to build site
                dist = math.sqrt((creature.spatial.position.x - decision.target_position.x)**2 + 
                               (creature.spatial.position.y - decision.target_position.y)**2)
                
                if dist < 5.0: # Deposit range
                    # Remove from creature
                    creature.creature.carried_materials.remove(target_material)
                    target_material.carrier_id = None
                    
                    # Update task
                    success = self.behavior_system.deposit_material(creature.creature.creature_id, target_material.material_type)
                    if success:
                        self.event_manager.log(f"{creature.creature.name} deposited {target_material.material_type.value}")
                        
                        # CRITICAL FIX: Update the building object itself
                        # Find the building at this location
                        for building in self.buildings:
                            dist_sq = (building.position.x - decision.target_position.x)**2 + (building.position.y - decision.target_position.y)**2
                            if dist_sq < 25.0:  # Same tolerance as CONSTRUCT
                                # Don't add materials to completed buildings
                                if building.is_complete():
                                    print(f"DEBUG: Building {building.building_type.value} is already complete, not accepting more materials")
                                    break
                                
                                # Add material to building
                                if target_material.material_type not in building.materials_placed:
                                    building.materials_placed[target_material.material_type] = 0
                                building.materials_placed[target_material.material_type] += 1
                                
                                # Update completion based on materials
                                blueprint = get_blueprint(building.building_type)
                                total_needed = sum(blueprint.required_materials.values())
                                total_placed = sum(building.materials_placed.values())
                                building.completion = min(1.0, total_placed / max(1, total_needed))
                                
                                print(f"DEBUG: Building {building.building_type.value} now at {building.completion*100:.1f}% completion ({total_placed}/{total_needed} materials)")
                                break
            
        elif decision.action_type == "CONSTRUCT":
            # Find the building being built or repaired
            target_pos = decision.target_position
            is_repair = decision.metadata and decision.metadata.get("repair", False)
            
            building_found = False
            for building in self.buildings:
                # Use distance check instead of exact float equality
                dist_sq = (building.position.x - target_pos.x)**2 + (building.position.y - target_pos.y)**2
                
                # DEBUG: Check what we are comparing
                # self.event_manager.log(f"DEBUG: Checking building at {building.position} vs target {target_pos} (dist_sq={dist_sq:.4f})")
                
                if dist_sq < 25.0: # Widen tolerance significantly (was 1.0)
                    building_found = True
                    # Apply construction/repair progress
                    # Base build speed
                    build_speed = 1.0 * delta_time
                    
                    # Trait bonuses
                    multiplier = self.behavior_system.get_build_speed_multiplier(creature.creature.traits)
                    build_speed *= multiplier
                    
                    if is_repair:
                        # Repair logic
                        repair_amount = build_speed * 0.1 
                        building.repair(repair_amount)
                        if building.durability >= 1.0:
                            self.event_manager.log(f"{creature.creature.name} repaired {building.building_type.value}")
                    else:
                        # Construction logic
                        blueprint = get_blueprint(building.building_type)
                        # Ensure build_time is not zero to avoid division by zero
                        build_time = max(1.0, blueprint.build_time)
                        progress_amount = build_speed / build_time
                        
                        old_completion = building.completion
                        building.completion += progress_amount
                        
                        # FORCE LOGGING for debugging
                        # if random.random() < 0.1: # Log 10% of frames to avoid spam but see activity
                        #      self.event_manager.log(f"DEBUG: {creature.creature.name} building. dt={delta_time:.4f}, speed={build_speed:.4f}, prog={building.completion:.4f}")
                        
                        if building.is_complete() and not building.effects_active:
                            building.activate()
                            self.event_manager.log(f"{creature.creature.name} completed {building.building_type.value}!")
                            # Clear the task from behavior system
                            self.behavior_system.cancel_building_task(creature.creature.creature_id)
                    break
            
            if not building_found:
                 pass
                 # self.event_manager.log(f"DEBUG: {creature.creature.name} tried to build but found no building at {target_pos}")
                 # If we tried to construct but couldn't find the building, something is wrong.
                 # Maybe it was destroyed? Cancel the task.
                 self.behavior_system.cancel_building_task(creature.creature.creature_id)
                    
        return decision
