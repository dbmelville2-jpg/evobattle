"""
Pellet Renderer - Renders pellets as visual elements with traits.

Displays pellets at their positions with visual indicators for
traits like color, size, generation, toxicity, and nutritional value.
"""

import pygame
import math
from ..systems.battle_spatial import SpatialBattle
from ..models.spatial import Vector2D
from ..models.pellet import Pellet


class PelletRenderer:
    """
    Renders pellets in the battle arena.
    
    Renders pellets as colored circles using their trait-based colors and sizes.
    Shows visual indicators for generation, toxicity, and other properties.
    
    Attributes:
        base_radius: Base radius for pellet rendering
        show_generation: Whether to show generation numbers
        show_stats_on_hover: Whether to show detailed stats on hover
    """
    
    def __init__(
        self,
        base_radius: int = 6,
        show_generation: bool = True,
        show_stats_on_hover: bool = False
    ):
        """
        Initialize the pellet renderer.
        
        Args:
            base_radius: Base radius for pellet circles
            show_generation: Whether to show generation numbers for evolved pellets
            show_stats_on_hover: Whether to show stats tooltip on hover (future)
        """
        self.base_radius = base_radius
        self.show_generation = show_generation
        self.show_stats_on_hover = show_stats_on_hover
        
        # Font for generation numbers
        pygame.font.init()
        self.tiny_font = pygame.font.Font(None, 12)
        self.small_font = pygame.font.Font(None, 16)
    
    def render(self, screen: pygame.Surface, pellets: list, camera, selected_pellet_id: str = None):
        """
        Render all pellets in the battle.
        
        Args:
            screen: Pygame surface to draw on
            pellets: List of pellets to render
            camera: Camera instance for coordinate transformation
            selected_pellet_id: ID of the currently selected pellet
        """
        # Render each pellet
        for pellet in pellets:
            is_selected = (pellet.pellet_id == selected_pellet_id)
            self._render_pellet(screen, pellet, camera, is_selected)
    
    def _render_pellet(
        self,
        screen: pygame.Surface,
        pellet: Pellet,
        camera,
        is_selected: bool = False
    ):
        """Render a single pellet."""
        # Get screen position
        screen_pos = camera.world_to_screen(Vector2D(pellet.x, pellet.y))
        
        # Calculate radius based on size trait
        # Scale radius by zoom
        radius = int(self.base_radius * pellet.get_display_size() * camera.zoom)
        radius = max(2, min(12, radius))  # Clamp size - pellets should be smaller than creatures
        
        # Get color from pellet traits
        color = pellet.get_display_color()
        
        # Apply toxicity visual effect (darken toxic pellets)
        if pellet.traits.toxicity > 0:
            toxicity_factor = 1.0 - (pellet.traits.toxicity * 0.5)  # Up to 50% darker
            color = tuple(int(c * toxicity_factor) for c in color)
            
        # Apply disease tint if infected
        if hasattr(pellet, 'active_infection') and pellet.active_infection:
            infection = pellet.active_infection
            tint = infection.disease.color_tint
            # Blend base color with tint (stronger for pellets)
            color = tuple(
                int(c * 0.5 + tint[i] * 0.5)
                for i, c in enumerate(color)
            )
        
        # Draw pellet body (filled circle)
        pygame.draw.circle(screen, color, screen_pos, radius)
        
        # Draw outline based on generation (brighter for higher generations)
        outline_brightness = min(255, 100 + pellet.generation * 20)
        outline_color = (outline_brightness, outline_brightness, outline_brightness)
        outline_width = 1 + (pellet.generation // 3)  # Thicker outline for evolved pellets
        outline_width = min(outline_width, 3)  # Max 3 pixels
        pygame.draw.circle(screen, outline_color, screen_pos, radius, outline_width)
        
        # Selection highlight
        if is_selected:
            # Draw a bright white ring around the pellet
            highlight_radius = radius + 4
            pygame.draw.circle(screen, (255, 255, 255), screen_pos, highlight_radius, 2)
            # Draw a second thinner ring further out
            pygame.draw.circle(screen, (200, 255, 200), screen_pos, highlight_radius + 3, 1)
        
        # Show generation number for evolved pellets (gen > 0)
        if self.show_generation and pellet.generation > 0:
            # Scale font size with zoom
            font_size = max(10, int(12 * camera.zoom))
            font = pygame.font.Font(None, font_size)
            
            gen_text = str(pellet.generation)
            text_surface = font.render(gen_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=screen_pos)
            
            # Draw small black background for readability
            bg_rect = text_rect.inflate(2, 2)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (0, 0, 0, 150), pygame.Rect(0, 0, bg_rect.width, bg_rect.height))
            screen.blit(bg_surface, bg_rect.topleft)
            
            # Draw generation number
            screen.blit(text_surface, text_rect)
        
        # Visual indicator for high nutrition (glow effect)
        if pellet.get_nutritional_value() > 60:
            glow_color = (*color, 80)  # Semi-transparent glow
            glow_radius = radius + 2  # Fixed 2px glow, independent of zoom
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (screen_pos[0] - glow_radius, screen_pos[1] - glow_radius))
    
    def render_pellet_tooltip(
        self,
        screen: pygame.Surface,
        pellet: Pellet,
        screen_pos: tuple
    ):
        """
        Render a tooltip showing pellet stats (for hover/click interaction).
        
        Args:
            screen: Pygame surface to draw on
            pellet: The pellet to show stats for
            screen_pos: Screen position for tooltip anchor
        """
        # Create tooltip content
        lines = [
            f"Gen: {pellet.generation}",
            f"Nutrition: {pellet.get_nutritional_value():.1f}",
            f"Age: {pellet.age}",
            f"Growth: {pellet.traits.growth_rate:.3f}",
            f"Toxicity: {pellet.traits.toxicity:.2f}"
        ]
        
        # Calculate tooltip size
        padding = 8
        line_height = 16
        max_width = max(self.small_font.size(line)[0] for line in lines)
        tooltip_width = max_width + padding * 2
        tooltip_height = len(lines) * line_height + padding * 2
        
        # Position tooltip (offset to avoid covering pellet)
        tooltip_x = screen_pos[0] + 15
        tooltip_y = screen_pos[1] - tooltip_height // 2
        
        # Keep tooltip on screen
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        if tooltip_x + tooltip_width > screen_width:
            tooltip_x = screen_pos[0] - tooltip_width - 15
        if tooltip_y < 0:
            tooltip_y = 0
        if tooltip_y + tooltip_height > screen_height:
            tooltip_y = screen_height - tooltip_height
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        pygame.draw.rect(
            tooltip_surface,
            (20, 20, 30, 230),
            pygame.Rect(0, 0, tooltip_width, tooltip_height),
            border_radius=5
        )
        pygame.draw.rect(
            tooltip_surface,
            (100, 100, 120),
            pygame.Rect(0, 0, tooltip_width, tooltip_height),
            2,
            border_radius=5
        )
        screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
        
        # Draw tooltip text
        y_offset = padding
        for line in lines:
            text_surface = self.small_font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (tooltip_x + padding, tooltip_y + y_offset))
            y_offset += line_height
