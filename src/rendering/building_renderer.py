"""
Building Renderer - Renders buildings and materials.

Handles all rendering for the building system including:
- Building materials on the ground
- Building tiles and construction
"""

import pygame
import os
import random


class BuildingRenderer:
    """
    Renders buildings and building materials.
    
    Attributes:
        material_images: Dictionary of material texture sprites
    """
    
    def __init__(self):
        """Initialize the building renderer and load assets."""
        self.material_images = {}
        self._load_material_assets()
    
    def _load_material_assets(self):
        """Load building material sprite sheet."""
        # Base path for assets
        base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets')
        
        # Load building materials
        structure_path = os.path.join(base_path, 'buildings')
        self.material_images = {}
        try:
            path = os.path.join(structure_path, 'materials.png')
            if os.path.exists(path):
                sheet = pygame.image.load(path).convert_alpha()
                w, h = sheet.get_size()
                hw, hh = w // 2, h // 2
                
                # Assume 2x2 grid: Log, Stone, Fiber, Plank
                self.material_images = {
                    'log': sheet.subsurface(pygame.Rect(0, 0, hw, hh)),
                    'stone': sheet.subsurface(pygame.Rect(hw, 0, hw, hh)),
                    'fiber': sheet.subsurface(pygame.Rect(0, hh, hw, hh)),
                    'plank': sheet.subsurface(pygame.Rect(hw, hh, hw, hh))
                }
        except Exception as e:
            print(f"Failed to load building materials: {e}")
    
    def render_materials(self, screen: pygame.Surface, materials: list, arena, camera):
        """
        Render building materials on the ground.
        
        Args:
            screen: Pygame surface
            materials: List of BuildingMaterial instances
            arena: Arena instance for coordinate conversion
            camera: Camera instance
        """
        from ..models.building.building_material import MaterialType
        
        # Map MaterialType to texture keys in self.material_images
        # Based on _load_material_assets: 'log', 'stone', 'fiber', 'plank'
        type_map = {
            MaterialType.WOOD: 'log',
            MaterialType.STONE: 'stone',
            MaterialType.PLANT_FIBER: 'fiber',
            MaterialType.ORGANIC: 'plank' # Using plank for organic/refined
        }
        
        for material in materials:
            if material.is_carried():
                continue  # Don't render carried materials
            
            # Convert world to screen coordinates
            screen_pos = camera.world_to_screen(material.position)
            screen_x, screen_y = int(screen_pos[0]), int(screen_pos[1])
            
            # Use zoom-dependent size for visibility
            # Base size 16 world units (icon size)
            size = int(16 * camera.zoom)
            
            # Draw a subtle white outline to highlight the material
            # This ensures visibility without looking like a "black circle"
            pygame.draw.circle(
                screen,
                (255, 255, 255, 100),  # White semi-transparent
                (screen_x, screen_y),
                size // 2 + 2,
                1  # Outline only
            )
            
            # Get texture from pre-loaded images
            texture_key = type_map.get(material.material_type)
            texture = self.material_images.get(texture_key)
            
            if texture:
                # Scale icon to current size
                scaled_icon = pygame.transform.scale(texture, (size, size))
                screen.blit(scaled_icon, (screen_x - size//2, screen_y - size//2))
            else:
                # Fallback to colored squares
                from ..models.building.building_material import get_material_color
                color = get_material_color(material.material_type)
                
                # Draw with black outline for better contrast
                pygame.draw.rect(
                    screen, 
                    (0, 0, 0),
                    (screen_x - size//2 - 1, screen_y - size//2 - 1, size + 2, size + 2)
                )
                
                pygame.draw.rect(
                    screen, 
                    color,
                    (screen_x - size//2, screen_y - size//2, size, size)
                )
            
            # Draw quantity if > 1
            if material.quantity > 1:
                font_size = max(12, int(10 * camera.zoom))
                font = pygame.font.Font(None, font_size)
                text = font.render(str(material.quantity), True, (255, 255, 255))
                # Draw text with shadow
                text_shadow = font.render(str(material.quantity), True, (0, 0, 0))
                screen.blit(text_shadow, (screen_x + size//2 + 1, screen_y - size//2 + 1))
                screen.blit(text, (screen_x + size//2, screen_y - size//2))
    
    def render_buildings(self, screen: pygame.Surface, buildings: list, arena, camera):
        """
        Render all buildings in the arena.
        
        Args:
            screen: Pygame surface
            buildings: List of Building instances
            arena: Arena instance
            camera: Camera instance
        """
        for structure in buildings:
            self._render_building(screen, structure, arena, camera)
    
    def _render_building(self, screen: pygame.Surface, structure, arena, camera):
        """
        Render individual building tile-by-tile based on its tiles list.
        Shows simple patterns like squares, crosses, etc.
        """
        from ..models.building.building_config import BuildingType
        
        # Get building color based on type
        colors = {
            BuildingType.SHELTER: (139, 90, 43),      # Brown
            BuildingType.FOOD_CACHE: (60, 100, 180),  # Blue
            BuildingType.NEST: (210, 180, 140),       # Tan
            BuildingType.WATCHTOWER: (101, 67, 33),   # Dark brown
            BuildingType.BARRIER: (70, 70, 75),       # Gray
            BuildingType.SHRINE: (255, 215, 0),       # Gold
            BuildingType.GARDEN: (34, 139, 34),       # Green
            BuildingType.BRIDGE: (160, 82, 45),       # Sienna
            BuildingType.TRAP: (80, 40, 10),          # Dark Wood
            BuildingType.TERRITORY_MARKER: (220, 50, 50) # Red
        }
        
        # Normalize building type if it's a string
        stype = structure.building_type
        if isinstance(stype, str):
            try:
                stype = BuildingType(stype.lower())
            except ValueError:
                stype = structure.building_type
        
        base_color = colors.get(stype, (100, 100, 100))
        
        # Adjust color based on completion/durability
        if structure.is_damaged():
            # Desaturated for damaged buildings
            damage_factor = 1.0 - structure.durability
            gray = 80
            color = tuple(int(c * (1-damage_factor*0.5) + gray * damage_factor*0.5) for c in base_color)
            border_color = (50, 20, 20)
            is_ghost = False
        else:
            color = base_color
            border_color = (20, 20, 20)
            is_ghost = False
        
        # Determine material texture based on type
        texture_key = 'log' # Default
        if stype == BuildingType.SHELTER: texture_key = 'log'
        elif stype == BuildingType.FOOD_CACHE: texture_key = 'stone'
        elif stype == BuildingType.NEST: texture_key = 'fiber'
        elif stype == BuildingType.WATCHTOWER: texture_key = 'plank'
        elif stype == BuildingType.BARRIER: texture_key = 'stone'
        elif stype == BuildingType.SHRINE: texture_key = 'stone'
        elif stype == BuildingType.GARDEN: texture_key = 'fiber'
        elif stype == BuildingType.BRIDGE: texture_key = 'plank'
        elif stype == BuildingType.TRAP: texture_key = 'fiber'
        elif stype == BuildingType.TERRITORY_MARKER: texture_key = 'stone'
        
        texture = self.material_images.get(texture_key)
        
        # Calculate how many tiles to show based on completion
        total_tiles = len(structure.tiles)
        
        # Draw construction site outline if incomplete
        if not structure.is_complete():
            # Draw a dashed or semi-transparent outline of the full footprint
            # For now, just a large rectangle or marker at the position
            screen_pos = camera.world_to_screen(structure.position)
            
            # Get footprint size from blueprint if possible, or estimate
            # Default to a reasonable size
            site_radius = int(20 * camera.zoom)
            
            # Draw "Under Construction" marker (yellow dashed box)
            # rect = pygame.Rect(0, 0, site_radius*2, site_radius*2)
            # rect.center = screen_pos
            # pygame.draw.rect(screen, (255, 255, 0), rect, 1) # Yellow outline removed per user request
            
            # Progress bar (re-enabled for debugging)
            rect = pygame.Rect(0, 0, site_radius*2, site_radius*2)
            rect.center = screen_pos
            bar_w = site_radius * 2
            bar_h = 6
            # Background
            pygame.draw.rect(screen, (50, 50, 50), (rect.left, rect.bottom + 2, bar_w, bar_h))
            # Progress
            pygame.draw.rect(screen, (0, 255, 0), (rect.left, rect.bottom + 2, bar_w * structure.completion, bar_h))

        if total_tiles == 0:
            return  # Nothing to render - skip completely (no progress bar for empty buildings)
        
        tiles_to_show = int(total_tiles * structure.completion)
        tiles_to_show = max(1, min(tiles_to_show, total_tiles))  # At least 1, at most all
        
        # Render each tile
        for i, tile_pos in enumerate(structure.tiles[:tiles_to_show]):
            # Convert tile position to screen coordinates
            screen_pos = camera.world_to_screen(tile_pos)
            screen_x, screen_y = screen_pos
            
            # Calculate tile size in pixels based on ZOOM
            # Use a large world-unit size (e.g. 15.0) so it scales correctly
            tile_size_world = 15.0 
            tile_size_px = int(tile_size_world * camera.zoom)
            tile_size_px = max(10, tile_size_px) # Minimum 10px visibility
            
            if texture:
                # Scale texture
                scaled_tex = pygame.transform.scale(texture, (tile_size_px, tile_size_px))
                
                # Add random rotation based on position (deterministic)
                # Use tile position as seed so it stays consistent
                rng = random.Random(tile_pos.x * 100 + tile_pos.y)
                angle = rng.uniform(-20, 20)
                
                # Rotate
                rotated_tex = pygame.transform.rotate(scaled_tex, angle)
                
                # Center the rotated image
                new_rect = rotated_tex.get_rect(center=(screen_x, screen_y))
                
                screen.blit(rotated_tex, new_rect)
                
            else:
                # Fallback to original rect rendering if no texture
                # Draw the tile as a square
                half_size = tile_size_px // 2
                
                # Draw shadow (scaled offset)
                shadow_offset = max(2, int(2 * camera.zoom))
                pygame.draw.rect(
                    screen,
                    (0, 0, 0, 100),  # Semi-transparent black
                    (screen_x - half_size + shadow_offset, 
                        screen_y - half_size + shadow_offset, 
                        tile_size_px, 
                        tile_size_px)
                )
                
                # Draw tile fill
                pygame.draw.rect(
                    screen,
                    color,
                    (screen_x - half_size, screen_y - half_size, tile_size_px, tile_size_px)
                )
                
                # Draw tile border
                border_width = max(1, int(1 * camera.zoom))
                pygame.draw.rect(
                    screen,
                    border_color,
                    (screen_x - half_size, screen_y - half_size, tile_size_px, tile_size_px),
                    border_width
                )
        
        # Draw label for completed buildings
        if structure.is_complete():
            # Get building name
            building_name = structure.building_type.value.replace('_', ' ').title()
            
            # Get strain color (default to white if no strain)
            label_color = (255, 255, 255)  # Default white
            if hasattr(structure, 'builder_strain_id') and structure.builder_strain_id:
                # Try to get strain color from the strain ID
                # Use a simple hash to generate a consistent color from strain ID
                import hashlib
                hash_val = int(hashlib.md5(structure.builder_strain_id.encode()).hexdigest()[:6], 16)
                # Generate a vibrant color
                hue = (hash_val % 360) / 360.0
                # Convert HSV to RGB (simple conversion for vibrant colors)
                import colorsys
                rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
                label_color = tuple(int(c * 255) for c in rgb)
            
            # Render label text
            font_size = max(14, int(12 * camera.zoom))
            font = pygame.font.Font(None, font_size)
            text_surface = font.render(building_name, True, label_color)
            
            # Position label above the building
            screen_pos = camera.world_to_screen(structure.position)
            label_x = int(screen_pos[0]) - text_surface.get_width() // 2
            label_y = int(screen_pos[1]) - int(30 * camera.zoom)  # Above the building
            
            # Draw text shadow for better visibility
            shadow_surface = font.render(building_name, True, (0, 0, 0))
            screen.blit(shadow_surface, (label_x + 1, label_y + 1))
            screen.blit(text_surface, (label_x, label_y))

