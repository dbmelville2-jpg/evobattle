"""
Resource Manager

Handles food pellet spawning, collection, growth, and lifecycle
for the spatial battle system.

Extracted from battle_spatial.py.
"""

import random
import math
from typing import List, Optional, Callable, Any, Set

from src.models.spatial import Arena, Vector2D, SpatialHashGrid
from src.models.pellet import Pellet, create_random_pellet, create_pellet_from_creature
from src.models.skills import SkillType
from src.systems.battle_events import BattleEvent, BattleEventType
from .event_manager import EventManager
from ..grass_growth_system import GrassGrowthSystem

class ResourceManager:
    """
    Manages food resources (pellets) in the battle arena.
    
    Responsibilities:
    - Spawn food pellets
    - Handle pellet collection by creatures
    - Manage pellet lifecycle (growth, reproduction, death)
    - Integrate with GrassGrowthSystem
    """
    
    def __init__(
        self, 
        arena: Arena,
        event_manager: EventManager,
        creature_grid: SpatialHashGrid,
        spawn_rate: float = 0.1,
        initial_resources: int = 5,
        enable_growth_system: bool = True
    ):
        """
        Initialize the resource manager.
        
        Args:
            arena: The battle arena
            event_manager: Event manager for emitting events
            creature_grid: Spatial grid for creature proximity queries
            spawn_rate: Number of resources to spawn per second
            initial_resources: Number of resources to spawn at start
            enable_growth_system: Whether to enable the grass growth system
        """
        self.arena = arena
        self.event_manager = event_manager
        self.creature_grid = creature_grid
        self.spawn_rate = spawn_rate
        self.time_since_last_spawn = 0.0
        self._pellet_update_counter = 0
        
        # Grass growth enhancement system
        if enable_growth_system:
            self.grass_growth = GrassGrowthSystem(
                arena_width=arena.width,
                arena_height=arena.height,
                enable_pollination=True,
                enable_nutrient_zones=True,
                enable_growth_pulses=True,
                enable_symbiotic_bonus=True
            )
        else:
            self.grass_growth = None
            
        # Spawn initial resources
        for _ in range(initial_resources):
            self.spawn_random_resource()
            
    def update(self, delta_time: float):
        """
        Update resource state for one frame.
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Spawn resources over time
        self.time_since_last_spawn += delta_time
        if self.spawn_rate > 0:
            spawn_interval = 1.0 / self.spawn_rate
            while self.time_since_last_spawn >= spawn_interval:
                self.spawn_random_resource()
                self.time_since_last_spawn -= spawn_interval
                
        # Update pellet lifecycle
        self._update_pellets(delta_time)
        
        # Update grass growth system
        if self.grass_growth:
            was_pulse_active = self.grass_growth.is_growth_pulse_active()
            self.grass_growth.update(delta_time)
            is_pulse_active = self.grass_growth.is_growth_pulse_active()
            
            # Emit event when growth pulse starts
            if not was_pulse_active and is_pulse_active:
                self.event_manager.emit_event(BattleEvent(
                    event_type=BattleEventType.PELLET_SPAWN,
                    message="Growth pulse! Sunlight and rain boost grass growth!",
                    data={'growth_pulse': True, 'multiplier': self.grass_growth.growth_pulse_multiplier}
                ))

    def spawn_random_resource(self):
        """Spawn a food pellet agent at a random location in the arena."""
        x = random.uniform(0, self.arena.width)
        y = random.uniform(0, self.arena.height)
        pellet = create_random_pellet(x, y)
        self.arena.add_pellet(pellet)
        
    def spawn_pellets_from_creature(self, creature: Any, count: int = 3):
        """
        Spawn pellets when a creature dies.
        
        Args:
            creature: The BattleCreature that died
            count: Number of pellets to spawn from the corpse
        """
        # Calculate nutritional value based on creature's size/stats
        base_nutrition = 30.0 + (creature.creature.stats.max_hp / 10.0)
        
        # Create nutrient zone where creature died (enhances pellet growth)
        if self.grass_growth:
            creature_size = creature.creature.stats.max_hp / 100.0  # Normalize size
            self.grass_growth.on_creature_death(
                x=creature.spatial.position.x,
                y=creature.spatial.position.y,
                creature_size=creature_size
            )
        
        for i in range(count):
            # Spawn pellets near the creature's position
            offset_x = random.uniform(-3, 3)
            offset_y = random.uniform(-3, 3)
            pellet = create_pellet_from_creature(
                x=creature.spatial.position.x + offset_x,
                y=creature.spatial.position.y + offset_y,
                creature_nutritional_value=base_nutrition
            )
            # Clamp position to arena bounds
            pellet.x = max(0, min(self.arena.width, pellet.x))
            pellet.y = max(0, min(self.arena.height, pellet.y))
            self.arena.add_pellet(pellet)

    def check_pellet_collection(self, creature: Any, reward_tracker: Any = None, enhancer: Any = None, building_materials: Optional[List] = None):
        """
        Check if creature is near any pellets and collect them.
        
        Args:
            creature: The BattleCreature to check for pellet collection
            reward_tracker: Optional reward tracker for neural learning
            enhancer: Optional living world enhancer
            building_materials: Optional list to add dropped building materials to
        """
        if not self.arena.resources:
            return
        
        COLLECTION_RADIUS = 1.5  # Distance at which creature can collect pellet
        
        # Apply Foraging skill bonus to collection radius
        foraging_skill = creature.creature.skills.get_skill(SkillType.FORAGING)
        # Bonus: up to +50% radius at max level (1.5 -> 2.25)
        radius_bonus = foraging_skill.get_performance_modifier() - 1.0
        effective_radius = COLLECTION_RADIUS * (1.0 + radius_bonus * 0.5)
        
        # Find nearby pellets
        pellets_to_remove = []
        for resource in self.arena.resources:
            resource_pos = self.arena.get_resource_position(resource)
            dist_sq = (creature.spatial.position.x - resource_pos.x)**2 + \
                      (creature.spatial.position.y - resource_pos.y)**2
            
            if dist_sq <= effective_radius * effective_radius:
                # Creature is close enough to collect
                if isinstance(resource, Pellet):
                    # Check if creature can/will eat this pellet
                    if creature.creature.can_eat_pellet(resource.traits.toxicity, resource.traits.palatability):
                        # Eat the pellet
                        hunger_restored = creature.creature.eat(
                            food_value=int(resource.get_nutritional_value()),
                            food_type="plant",
                            toxicity=resource.traits.toxicity,
                            palatability=resource.traits.palatability
                        )
                        
                        if hunger_restored > 0:
                            # Successfully ate the pellet
                            pellets_to_remove.append(resource)
                            
                            # Gain Foraging XP
                            foraging_skill.use(difficulty=1.0, success=True)
                            
                            # Drop building materials from pellet
                            if building_materials is not None:
                                dropped_materials = resource.get_material_drop()
                                if dropped_materials:
                                    for material in dropped_materials:
                                        building_materials.append(material)
                                        self.event_manager.log(f"{creature.creature.name} found {material.material_type.value} from pellet!")
                            
                            # Neural Learning: Reward for eating
                            if reward_tracker:
                                reward_tracker.apply_reward(creature, 'ate_food')
                            
                            # Notify living world enhancer
                            if enhancer:
                                enhancer.on_pellet_eaten(resource, creature.creature)
        
        # Remove collected pellets
        for pellet in pellets_to_remove:
            self.arena.remove_resource(pellet)

    def _update_pellets(self, delta_time: float):
        """
        Update all pellets (age, reproduce, die).
        
        Args:
            delta_time: Time elapsed since last update
        """
        pellets_to_remove = []
        pellets_to_add = []
        
        self._pellet_update_counter += 1
        should_check_reproduction = (self._pellet_update_counter % 30 == 0)
        
        # Get only Pellet objects (not legacy Vector2D resources)
        for pellet in self.arena.pellets:
            # Age the pellet
            pellet.tick(delta_time)
            
            # Check if pellet died of old age
            if pellet.is_dead():
                pellets_to_remove.append(pellet)
                continue
            
            # Only check reproduction periodically to reduce expensive spatial queries
            if should_check_reproduction:
                # Count nearby pellets for density calculation using spatial grid
                pellet_pos = Vector2D(pellet.x, pellet.y)
                DENSITY_RADIUS = 20.0
                # Use exact distance for density checks
                nearby_pellets = self.arena.spatial_grid.query_radius(
                    pellet_pos,
                    DENSITY_RADIUS,
                    exclude={pellet},
                    exact_distance=True,
                    get_position=lambda p: Vector2D(p.x, p.y) if hasattr(p, 'x') else p
                )
                nearby_count = len(nearby_pellets) + 1  # +1 to include the pellet itself
                
                # Get nearby creatures for symbiotic bonus
                CREATURE_RADIUS = 15.0
                nearby_creatures = self.creature_grid.query_radius(
                    pellet_pos,
                    CREATURE_RADIUS,
                    exact_distance=True
                )
                
                # Calculate growth rate multiplier from grass growth system
                growth_multiplier = 1.0
                if self.grass_growth:
                    growth_multiplier = self.grass_growth.get_growth_rate_multiplier(
                        pellet, 
                        nearby_creatures
                    )
                
                # Attempt reproduction with enhanced growth rate
                CARRYING_CAPACITY = 50  # Max pellets in local area
                
                # Apply growth multiplier by temporarily boosting the pellet's growth rate
                original_growth_rate = pellet.traits.growth_rate
                pellet.traits.growth_rate *= growth_multiplier
                
                # Check reproduction with boosted rate
                can_reproduce = pellet.can_reproduce(nearby_count, CARRYING_CAPACITY)
                
                # Restore original growth rate
                pellet.traits.growth_rate = original_growth_rate
                
                if can_reproduce:
                    offspring = pellet.reproduce(mutation_rate=0.15)
                    # Clamp offspring position to arena bounds
                    offspring.x = max(0, min(self.arena.width, offspring.x))
                    offspring.y = max(0, min(self.arena.height, offspring.y))
                    pellets_to_add.append(offspring)
        
        # Remove dead pellets
        for pellet in pellets_to_remove:
            self.arena.remove_resource(pellet)
        
        # Add new offspring
        for pellet in pellets_to_add:
            self.arena.add_pellet(pellet)
    
    def spawn_cooperative_resource(self):
        """
        Spawn a large resource cluster that encourages cooperative gathering.
        
        Creates multiple pellets in a small area, rewarding creatures that work together.
        """
        # Choose a random location for the resource cluster
        cluster_center = Vector2D(
            random.uniform(10, self.arena.width - 10),
            random.uniform(10, self.arena.height - 10)
        )
        
        # Spawn 3-5 pellets in a cluster
        cluster_size = random.randint(3, 5)
        cluster_radius = 5.0
        
        for _ in range(cluster_size):
            # Offset from center
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, cluster_radius)
            position = Vector2D(
                cluster_center.x + math.cos(angle) * distance,
                cluster_center.y + math.sin(angle) * distance
            )
            position = self.arena.clamp_position(position)
            
            # Create a high-quality pellet at the position
            pellet = create_random_pellet(position.x, position.y, generation=1)
            pellet.traits.palatability = random.uniform(0.7, 1.0)  # High palatability
            pellet.traits.toxicity = random.uniform(0.0, 0.2)  # Low toxicity
            pellet.traits.nutrient_value = random.uniform(25, 35)  # Good nutrients
            
            self.arena.add_pellet(pellet)
        
        self.event_manager.log(f"COOPERATIVE FOOD! Resource cluster of {cluster_size} pellets appeared")
        self.event_manager.emit_event(BattleEvent(
            event_type=BattleEventType.PELLET_SPAWN,
            message=f"Rich food cluster spawned! {cluster_size} high-quality pellets",
            data={'cluster_size': cluster_size, 'position': cluster_center.to_tuple()}
        ))

