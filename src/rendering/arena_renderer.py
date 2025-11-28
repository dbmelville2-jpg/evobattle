"""
Arena Renderer - Renders the 2D battle arena.

Draws the arena boundaries, grid, and any hazards or resources.
"""

import pygame
import os
from ..systems.battle_spatial import SpatialBattle
from ..models.spatial import Vector2D
from ..models.pellet import Pellet


class ArenaRenderer:
    """
    Renders the 2D battle arena including boundaries and grid.
    
    Attributes:
        grid_color: Color for the grid lines
        border_color: Color for the arena border
        hazard_color: Color for hazards
        resource_color: Color for resources
        show_grid: Whether to show the grid
    """
    
    def __init__(
        self,
        grid_color: tuple = (40, 40, 50),
        border_color: tuple = (100, 100, 120),
        hazard_color: tuple = (200, 50, 50),
        resource_color: tuple = (50, 200, 100),
        show_grid: bool = False,
        pellet_renderer = None,
        building_renderer = None
    ):
        """
        Initialize the arena renderer.
        
        Args:
            grid_color: RGB color for grid lines
            border_color: RGB color for arena border
            hazard_color: RGB color for hazards
            resource_color: RGB color for resources (for simple Vector2D resources)
            show_grid: Whether to display the grid (default False for performance)
            pellet_renderer: Optional PelletRenderer for detailed pellet rendering
            building_renderer: Optional BuildingRenderer for building/structure rendering
        """
        self.grid_color = grid_color
        self.border_color = border_color
        self.hazard_color = hazard_color
        self.resource_color = resource_color
        self.show_grid = show_grid
        self.pellet_renderer = pellet_renderer
        self.building_renderer = building_renderer
        
        # Background colors
        self.bg_color = (30, 30, 40)
        self.player_side_tint = (30, 40, 50)
        self.enemy_side_tint = (50, 40, 40)
        
        # Grid cache for performance
        self._cached_grid_surface = None
        self._cached_grid_bounds = None
        
        # Terrain cache
        self._cached_terrain_surface = None
        self._cached_terrain_bounds = None
        
        # Assets
        self.terrain_images = {}
        self.weather_images = {}
        self._load_assets()
        
        # Weather animation state
        self.weather_offset = 0.0
        
    def _load_assets(self):
        """Load terrain and weather assets."""
        # Base path for assets
        base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets')
        
        # Load terrain images
        terrain_path = os.path.join(base_path, 'terrain')
        terrain_files = {
            'grass': 'grass.png',
            'desert': 'desert.png',
            'forest': 'forest.png',
            'marsh': 'marsh.png',
            'rocky': 'rocky.png',
            'water': 'water.png'
        }
        
        for terrain_type, filename in terrain_files.items():
            try:
                path = os.path.join(terrain_path, filename)
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    self.terrain_images[terrain_type] = img
            except Exception as e:
                print(f"Failed to load terrain image {filename}: {e}")
                
        # Load weather images
        weather_path = os.path.join(base_path, 'weather')
        weather_files = {
            'rainy': 'rain.png',
            'stormy': 'storm.png',
            'foggy': 'fog.png',
            'clear': 'sun.png'
        }
        
        for weather_type, filename in weather_files.items():
            try:
                path = os.path.join(weather_path, filename)
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    self.weather_images[weather_type] = img
            except Exception as e:
                print(f"Failed to load weather image {filename}: {e}")


    def render(
        self,
        screen: pygame.Surface,
        battle: SpatialBattle,
        camera=None,
        selected_creature_id: str = None,
        hovered_creature_id: str = None,
        show_debug: bool = False
    ):
        """
        Render the arena and all its contents.
        
        Args:
            screen: Pygame surface to draw on
            battle: Battle state
            camera: Camera instance for view transformation
            selected_creature_id: ID of currently selected creature
            hovered_creature_id: ID of currently hovered creature
            show_debug: Whether to show debug visuals
        """
        # If no camera provided, create a dummy one (fallback)
        if camera is None:
            return
            
        # 1. Draw Background / Terrain
        self._render_terrain(screen, battle, camera)
        
        # 2. Draw Grid (optional)
        if self.show_grid:
            self._render_grid(screen, battle.arena.width, battle.arena.height, camera)
            
        # 3. Draw Hazards
        if battle.environment and battle.environment.hazards:
            for hazard in battle.environment.hazards:
                self._render_hazard(screen, hazard, camera)
                
        # 4. Draw Resources (Pellets)
        # Use specialized pellet renderer if available
        if self.pellet_renderer:
            self.pellet_renderer.render(screen, battle.arena.resources, camera)
        else:
            # Fallback rendering
            for pellet in battle.arena.resources:
                self._render_resource(screen, pellet, camera)
    
        # 5. Draw Creatures
        # Filter visible creatures first, then sort
        # This avoids sorting thousands of off-screen creatures
        screen_w, screen_h = screen.get_size()
        top_left_world = camera.screen_to_world((0, 0))
        bottom_right_world = camera.screen_to_world((screen_w, screen_h))
        
        # Add generous buffer for creatures (radius + UI elements)
        c_buffer = 50.0
        min_cx = top_left_world.x - c_buffer
        max_cx = bottom_right_world.x + c_buffer
        min_cy = top_left_world.y - c_buffer
        max_cy = bottom_right_world.y + c_buffer
        
        visible_creatures = []
        for c in battle.creatures:
            if not c.is_alive():
                continue
            
            # Simple bounding box check
            pos = c.spatial.position
            if min_cx <= pos.x <= max_cx and min_cy <= pos.y <= max_cy:
                visible_creatures.append(c)
                
        # Sort only visible creatures by Y position for proper depth/overlap
        sorted_creatures = sorted(
            visible_creatures,
            key=lambda c: c.spatial.position.y
        )
        
        for creature in sorted_creatures:
            is_selected = (creature.creature.creature_id == selected_creature_id)
            is_hovered = (creature.creature.creature_id == hovered_creature_id)
            
            self._render_creature(
                screen, 
                creature, 
                camera,
                is_selected, 
                is_hovered,
                show_debug
            )
            
        # 6. Draw Weather Overlay
        if battle.environment and battle.environment.weather:
            self._render_weather(screen, battle.environment.weather, camera)
            
        # 7. Draw Arena Border
        self._render_border(screen, battle.arena.width, battle.arena.height, camera)
        
        # 8. Draw Structures & Materials
        if self.building_renderer:
            if hasattr(battle, 'structures'):
                self.building_renderer.render_buildings(screen, battle.buildings, battle.arena, camera)
                
            if hasattr(battle, 'materials'):
                self.building_renderer.render_materials(screen, battle.materials, battle.arena, camera)

    def _render_terrain(self, screen: pygame.Surface, battle: SpatialBattle, camera):
        """Render the terrain background."""
        # Fill background
        screen.fill(self.bg_color)
        
        # If we have a biome map, render it
        if hasattr(battle.arena, 'biome_map') and battle.arena.biome_map:
            # This would be optimized to only draw visible tiles
            # For now, simple implementation
            pass
            
        if not battle.environment or not battle.environment.terrain_grid:
            # Fallback to simple rect if no terrain grid
            top_left = camera.world_to_screen(Vector2D(0, 0))
            bottom_right = camera.world_to_screen(Vector2D(battle.arena.width, battle.arena.height))
            rect_width = bottom_right[0] - top_left[0]
            rect_height = bottom_right[1] - top_left[1]
            pygame.draw.rect(screen, (30, 35, 40), (top_left[0], top_left[1], rect_width, rect_height))
            return

        # Calculate visible range to optimize rendering
        # Get world coordinates of screen corners
        screen_w, screen_h = screen.get_size()
        top_left_world = camera.screen_to_world((0, 0))
        bottom_right_world = camera.screen_to_world((screen_w, screen_h))
        
        # Add buffer
        buffer = 20.0
        min_x = top_left_world.x - buffer
        max_x = bottom_right_world.x + buffer
        min_y = top_left_world.y - buffer
        max_y = bottom_right_world.y + buffer
        
        cell_size = battle.environment.cell_size
        
        # Render visible cells
        for (col, row), cell in battle.environment.terrain_grid.items():
            # Check if cell is within visible range
            cell_x = cell.position.x
            cell_y = cell.position.y
            
            if not (min_x <= cell_x <= max_x and min_y <= cell_y <= max_y):
                continue
                
            # Calculate screen position and size
            # Cell position is center, so top-left is offset
            tl_world = Vector2D(cell_x - cell_size/2, cell_y - cell_size/2)
            br_world = Vector2D(cell_x + cell_size/2, cell_y + cell_size/2)
            
            tl_screen = camera.world_to_screen(tl_world)
            br_screen = camera.world_to_screen(br_world)
            
            width = int(br_screen[0] - tl_screen[0]) + 1 # +1 to avoid gaps
            height = int(br_screen[1] - tl_screen[1]) + 1
            
            if width <= 0 or height <= 0:
                continue
                
            # Draw terrain
            if cell.terrain_type.value in self.terrain_images: # Use .value for string key
                 # Try string key first (loaded as strings)
                img = self.terrain_images[cell.terrain_type.value]
                scaled_img = pygame.transform.scale(img, (width, height))
                screen.blit(scaled_img, tl_screen)
            elif cell.terrain_type in self.terrain_images: # Try enum key
                img = self.terrain_images[cell.terrain_type]
                scaled_img = pygame.transform.scale(img, (width, height))
                screen.blit(scaled_img, tl_screen)
            else:
                # Fallback colors
                from ..models.environment import TerrainType
                colors = {
                    TerrainType.GRASS: (34, 139, 34),
                    TerrainType.ROCKY: (128, 128, 128),
                    TerrainType.WATER: (65, 105, 225),
                    TerrainType.FOREST: (0, 100, 0),
                    TerrainType.DESERT: (210, 180, 140),
                    TerrainType.MARSH: (47, 79, 79)
                }
                color = colors.get(cell.terrain_type, (50, 50, 50))
                pygame.draw.rect(screen, color, (tl_screen[0], tl_screen[1], width, height))

    def _render_grid(self, screen: pygame.Surface, width: float, height: float, camera):
        """Render the grid lines."""
        # Grid spacing in world units
        grid_spacing = 10.0
        
        # Vertical lines
        for x in range(0, int(width) + 1, int(grid_spacing)):
            start_pos = camera.world_to_screen(Vector2D(x, 0))
            end_pos = camera.world_to_screen(Vector2D(x, height))
            pygame.draw.line(screen, self.grid_color, start_pos, end_pos, 1)
            
        # Horizontal lines
        for y in range(0, int(height) + 1, int(grid_spacing)):
            start_pos = camera.world_to_screen(Vector2D(0, y))
            end_pos = camera.world_to_screen(Vector2D(width, y))
            pygame.draw.line(screen, self.grid_color, start_pos, end_pos, 1)

    def _render_border(self, screen: pygame.Surface, width: float, height: float, camera):
        """Render the arena border."""
        top_left = camera.world_to_screen(Vector2D(0, 0))
        top_right = camera.world_to_screen(Vector2D(width, 0))
        bottom_right = camera.world_to_screen(Vector2D(width, height))
        bottom_left = camera.world_to_screen(Vector2D(0, height))
        
        # Draw border lines
        pygame.draw.line(screen, self.border_color, top_left, top_right, 2)
        pygame.draw.line(screen, self.border_color, top_right, bottom_right, 2)
        pygame.draw.line(screen, self.border_color, bottom_right, bottom_left, 2)
        pygame.draw.line(screen, self.border_color, bottom_left, top_left, 2)

    def _render_creature(
        self, 
        screen: pygame.Surface, 
        creature, 
        camera,
        is_selected: bool, 
        is_hovered: bool,
        show_debug: bool
    ):
        """Render a single creature."""
        # Convert position to screen coords
        screen_pos = camera.world_to_screen(creature.spatial.position)
        
        # Calculate radius in screen pixels
        # creature.spatial.radius is typically 0.5-2.0 units
        # With zoom ~0.4 and base scale 10px/unit, this gives us 2-8px radius
        # But we want creatures to be visible, so use a minimum base size
        base_size = 14  # Base pixel size for creatures (increased from 8)
        radius_px = int(base_size * camera.zoom * creature.spatial.radius)
        radius_px = max(3, min(20, radius_px))  # Clamp between 3-20px
        
        # Color based on hue
        color = pygame.Color(0)
        color.hsva = (creature.creature.hue, 80, 80, 100)
        
        # Draw creature body
        pygame.draw.circle(screen, color, screen_pos, radius_px)
        
        # Selection/Hover highlight
        if is_selected:
            pygame.draw.circle(screen, (255, 255, 255), screen_pos, radius_px + 2, 2)
        elif is_hovered:
            pygame.draw.circle(screen, (200, 200, 200), screen_pos, radius_px + 1, 1)
            
        # Health bar
        self._render_health_bar(screen, creature, screen_pos, radius_px)
        
        # Debug info
        if show_debug:
            # Draw velocity vector
            end_pos = (
                screen_pos[0] + creature.spatial.velocity.x * 10 * camera.zoom,
                screen_pos[1] + creature.spatial.velocity.y * 10 * camera.zoom
            )
            pygame.draw.line(screen, (0, 255, 0), screen_pos, end_pos, 1)
            
            # Draw target line
            if creature.target:
                target_pos = camera.world_to_screen(creature.target.spatial.position)
                pygame.draw.line(screen, (255, 0, 0), screen_pos, target_pos, 1)

    def _render_health_bar(self, screen: pygame.Surface, creature, screen_pos, radius_px):
        """Render health bar above creature."""
        width = radius_px * 2.5
        height = max(3, radius_px * 0.4)
        x = screen_pos[0] - width / 2
        y = screen_pos[1] - radius_px - height - 2
        
        hp_pct = creature.creature.stats.hp / max(1, creature.creature.stats.max_hp)
        hp_pct = max(0.0, min(1.0, hp_pct))
        
        # Background
        pygame.draw.rect(screen, (50, 0, 0), (x, y, width, height))
        
        # Health
        hp_color = (0, 255, 0)
        if hp_pct < 0.5: hp_color = (255, 255, 0)
        if hp_pct < 0.2: hp_color = (255, 0, 0)
        
        pygame.draw.rect(screen, hp_color, (x, y, width * hp_pct, height))

    def _render_hazard(self, screen: pygame.Surface, hazard, camera):
        """Render an environmental hazard."""
        screen_pos = camera.world_to_screen(hazard.position)
        
        # Use base size approach like creatures, scale hazard radius appropriately
        # Hazards in world units are typically 10-50, normalize to reasonable pixel sizes
        base_size = 15  # Base pixel size for hazards (slightly larger than creatures)
        radius_px = int(base_size * camera.zoom * (hazard.radius / 10.0))  # Normalize world units
        radius_px = max(5, min(40, radius_px))  # Clamp to reasonable size
        
        # Draw hazard area (transparent)
        surface = pygame.Surface((radius_px * 2, radius_px * 2), pygame.SRCALPHA)
        color = (*self.hazard_color, 100)  # Add alpha
        pygame.draw.circle(surface, color, (radius_px, radius_px), radius_px)
        screen.blit(surface, (screen_pos[0] - radius_px, screen_pos[1] - radius_px))

    def _render_resource(self, screen: pygame.Surface, pellet, camera):
        """Render a resource pellet (fallback)."""
        screen_pos = camera.world_to_screen(pellet.position)
        radius_px = int(0.5 * camera.zoom * 10.0)  # Fixed size for now
        
        pygame.draw.circle(screen, self.resource_color, screen_pos, radius_px)

    def _render_weather(self, screen: pygame.Surface, weather, camera):
        """Render weather effects."""
        if not weather or not weather.weather_type:
            return
            
        # Update animation
        self.weather_offset += 0.5
        if self.weather_offset > 100:
            self.weather_offset = 0
            
        # Get weather image
        if weather.weather_type in self.weather_images:
            img = self.weather_images[weather.weather_type]
            
            # Scale to cover screen
            screen_w, screen_h = screen.get_size()
            scaled_img = pygame.transform.scale(img, (screen_w, screen_h))
            
            # Apply alpha based on intensity
            # Rain/Storm/Fog intensity affects opacity
            alpha = 100 # Base alpha
            
            from ..models.environment import WeatherType
            if weather.weather_type == WeatherType.RAINY:
                alpha = int(100 * weather.precipitation)
            elif weather.weather_type == WeatherType.STORMY:
                alpha = int(150 * weather.precipitation)
            elif weather.weather_type == WeatherType.FOGGY:
                alpha = int(200 * (1.0 - weather.visibility))
                
            scaled_img.set_alpha(alpha)
            screen.blit(scaled_img, (0, 0))
            
            # For rain/storm, maybe draw a second layer with offset for movement
            if weather.weather_type in [WeatherType.RAINY, WeatherType.STORMY]:
                offset_y = int(self.weather_offset * 5) % screen_h
                screen.blit(scaled_img, (0, offset_y - screen_h))
                screen.blit(scaled_img, (0, offset_y))
