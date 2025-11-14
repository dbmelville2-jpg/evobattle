"""
Arena Renderer - Renders the 2D battle arena.

Draws the arena boundaries, grid, and any hazards or resources.
"""

import pygame
from ..systems.battle_spatial import SpatialBattle
from ..models.spatial import Vector2D


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
        show_grid: bool = True
    ):
        """
        Initialize the arena renderer.
        
        Args:
            grid_color: RGB color for grid lines
            border_color: RGB color for arena border
            hazard_color: RGB color for hazards
            resource_color: RGB color for resources
            show_grid: Whether to display the grid
        """
        self.grid_color = grid_color
        self.border_color = border_color
        self.hazard_color = hazard_color
        self.resource_color = resource_color
        self.show_grid = show_grid
        
        # Background colors
        self.bg_color = (30, 30, 40)
        self.player_side_tint = (30, 40, 50)
        self.enemy_side_tint = (50, 40, 40)
    
    def render(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render the arena.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle containing arena data
        """
        # Get arena bounds on screen
        bounds = self._get_arena_bounds(screen)
        x, y, width, height = bounds
        
        # Draw background with team side tints
        mid_x = x + width // 2
        
        # Player side (left) - blue tint
        player_rect = pygame.Rect(x, y, width // 2, height)
        pygame.draw.rect(screen, self.player_side_tint, player_rect)
        
        # Enemy side (right) - red tint
        enemy_rect = pygame.Rect(mid_x, y, width // 2, height)
        pygame.draw.rect(screen, self.enemy_side_tint, enemy_rect)
        
        # Draw center line
        pygame.draw.line(
            screen,
            (60, 60, 70),
            (mid_x, y),
            (mid_x, y + height),
            2
        )
        
        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid(screen, bounds, battle.arena)
        
        # Draw arena border
        pygame.draw.rect(screen, self.border_color, (x, y, width, height), 3)
        
        # Draw hazards
        for hazard_pos in battle.arena.hazards:
            self._draw_hazard(screen, hazard_pos, bounds, battle.arena)
        
        # Draw resources
        for resource_pos in battle.arena.resources:
            self._draw_resource(screen, resource_pos, bounds, battle.arena)
    
    def _get_arena_bounds(self, screen: pygame.Surface) -> tuple:
        """Get the screen bounds for the arena."""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        ui_margin_top = 100
        ui_margin_side = 50
        ui_margin_bottom = 150
        
        x = ui_margin_side
        y = ui_margin_top
        width = screen_width - (ui_margin_side * 2)
        height = screen_height - ui_margin_top - ui_margin_bottom
        
        return (x, y, width, height)
    
    def _draw_grid(self, screen: pygame.Surface, bounds: tuple, arena):
        """Draw grid lines on the arena."""
        x, y, width, height = bounds
        
        # Draw vertical lines (every 10 units)
        grid_spacing_world = 10.0
        num_vertical_lines = int(arena.width / grid_spacing_world)
        
        for i in range(1, num_vertical_lines):
            world_x = i * grid_spacing_world
            screen_x = x + int((world_x / arena.width) * width)
            pygame.draw.line(
                screen,
                self.grid_color,
                (screen_x, y),
                (screen_x, y + height),
                1
            )
        
        # Draw horizontal lines
        num_horizontal_lines = int(arena.height / grid_spacing_world)
        
        for i in range(1, num_horizontal_lines):
            world_y = i * grid_spacing_world
            screen_y = y + int((world_y / arena.height) * height)
            pygame.draw.line(
                screen,
                self.grid_color,
                (x, screen_y),
                (x + width, screen_y),
                1
            )
    
    def _world_to_screen(
        self,
        world_pos: Vector2D,
        bounds: tuple,
        arena
    ) -> tuple:
        """Convert world coordinates to screen coordinates."""
        x, y, width, height = bounds
        
        screen_x = x + (world_pos.x / arena.width) * width
        screen_y = y + (world_pos.y / arena.height) * height
        
        return (int(screen_x), int(screen_y))
    
    def _draw_hazard(
        self,
        screen: pygame.Surface,
        hazard_pos: Vector2D,
        bounds: tuple,
        arena
    ):
        """Draw a hazard at the specified position."""
        screen_pos = self._world_to_screen(hazard_pos, bounds, arena)
        pygame.draw.circle(screen, self.hazard_color, screen_pos, 8)
        pygame.draw.circle(screen, (255, 100, 100), screen_pos, 8, 2)
    
    def _draw_resource(
        self,
        screen: pygame.Surface,
        resource_pos: Vector2D,
        bounds: tuple,
        arena
    ):
        """Draw a resource/food at the specified position."""
        screen_pos = self._world_to_screen(resource_pos, bounds, arena)
        # Draw food as a circle with a distinctive color
        pygame.draw.circle(screen, (80, 200, 60), screen_pos, 8)  # Green center
        pygame.draw.circle(screen, (120, 255, 100), screen_pos, 8, 2)  # Bright green outline
