"""
Creature Renderer - Renders creatures as sprites or shapes.

Displays creatures at their positions with visual indicators for
team, health, and status.
"""

import pygame
import math
from functools import lru_cache
from ..systems.battle_spatial import SpatialBattle, BattleCreature
from ..models.spatial import Vector2D


class CreatureRenderer:
    """
    Renders creatures in the battle arena.
    
    Renders creatures as colored circles using HSV colors from the creature
    (based on lineage/strain). Can be extended to use sprite sheets.
    
    Attributes:
        radius: Base radius for creature rendering
    """
    
    def __init__(
        self,
        radius: int = 10
    ):
        """
        Initialize the creature renderer.
        
        Args:
            radius: Base radius for creature circles
        """
        self.radius = radius
        
        # Font for creature names
        pygame.font.init()
        self.name_font = pygame.font.Font(None, 20)
        self.stat_font = pygame.font.Font(None, 16)
        
        # Text surface cache for performance
        self._text_cache = {}
    
    def render(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render all creatures in the battle.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle containing creatures
        """
        # Determine LOD level based on creature count
        creature_count = len(battle.creatures)
        lod_level = 0  # High detail
        
        if creature_count > 100:
            lod_level = 2  # Low detail (circles only)
        elif creature_count > 40:
            lod_level = 1  # Medium detail (simplified bars)
            
        # Get mouse position for hover details
        mouse_pos = pygame.mouse.get_pos()
        
        # Render all creatures
        for creature in battle.creatures:
            if creature.is_alive():
                self._render_creature(screen, creature, battle, lod_level, mouse_pos)
    
    def _render_creature(
        self,
        screen: pygame.Surface,
        creature: BattleCreature,
        battle: SpatialBattle,
        lod_level: int = 0,
        mouse_pos: tuple = (0, 0)
    ):
        """Render a single creature."""
        # Get screen position
        screen_pos = self._world_to_screen(
            creature.spatial.position,
            screen,
            battle.arena
        )
        
        # Use HSV color from creature
        color = creature.creature.get_display_color()
        # Calculate outline as slightly brighter version
        outline_color = tuple(min(255, c + 40) for c in color)
        
        # Draw creature body (circle)
        pygame.draw.circle(screen, color, screen_pos, self.radius)
        pygame.draw.circle(screen, outline_color, screen_pos, self.radius, 2)
        
        # Check for hover (override LOD)
        # Simple distance check for hover
        dx = screen_pos[0] - mouse_pos[0]
        dy = screen_pos[1] - mouse_pos[1]
        is_hovered = (dx*dx + dy*dy) < (self.radius + 5)**2
        
        # Force high detail if hovered or selected (if we had selection)
        if is_hovered:
            lod_level = 0
        
        # Draw direction indicator (velocity) - Skip in LOD 2
        if lod_level < 2 and creature.spatial.velocity.magnitude() > 0.1:
            vel_norm = creature.spatial.velocity.normalized()
            end_x = screen_pos[0] + vel_norm.x * (self.radius + 10)
            end_y = screen_pos[1] + vel_norm.y * (self.radius + 10)
            pygame.draw.line(
                screen,
                outline_color,
                screen_pos,
                (int(end_x), int(end_y)),
                3
            )
        
        # Draw HP bar above creature - Simplified in LOD 1, Skip in LOD 2
        if lod_level < 2:
            self._draw_hp_bar(screen, creature, screen_pos, simplified=(lod_level == 1))
        
        # Draw hunger bar below HP bar - Skip in LOD 1+
        if lod_level < 1:
            self._draw_hunger_bar(screen, creature, screen_pos)
        
        # Draw energy bar (if applicable) - Skip in LOD 1+
        if lod_level < 1 and hasattr(creature.creature, 'energy') and creature.creature.energy < creature.creature.max_energy:
            self._draw_energy_bar(screen, creature, screen_pos)
        
        # Draw creature name below - Skip in LOD 1+
        if lod_level < 1:
            self._draw_name(screen, creature, screen_pos)
        
        # Draw combat engagement indicator - Simplified in LOD 2 (just color, no pulse ring)
        if creature.combat_engaged:
            if lod_level < 2:
                # Draw a pulsing ring around creatures in active combat
                import time
                pulse = (math.sin(time.time() * 5) + 1) / 2  # Pulse between 0 and 1
                ring_radius = self.radius + 5 + int(pulse * 3)
                ring_color = (255, 100, 100) if creature.combat_engaged else (255, 255, 100)
                pygame.draw.circle(screen, ring_color, screen_pos, ring_radius, 2)
        
        # Draw target line if creature has a target - Skip in LOD 2
        if lod_level < 2 and creature.target and creature.target.is_alive():
            target_screen_pos = self._world_to_screen(
                creature.target.spatial.position,
                screen,
                battle.arena
            )
            # Draw line to target - red if engaged, yellow if approaching
            line_color = (255, 100, 100) if creature.combat_engaged else (255, 255, 100)
            line_width = 2 if creature.combat_engaged else 1
            pygame.draw.line(
                screen,
                line_color,
                screen_pos,
                target_screen_pos,
                line_width
            )
    
    def _draw_hp_bar(
        self,
        screen: pygame.Surface,
        creature: BattleCreature,
        screen_pos: tuple,
        simplified: bool = False
    ):
        """Draw HP bar above the creature."""
        bar_width = 40 if not simplified else 30
        bar_height = 6 if not simplified else 4
        bar_x = screen_pos[0] - bar_width // 2
        bar_y = screen_pos[1] - self.radius - (15 if not simplified else 8)
        
        # Background (gray)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (60, 60, 60), bg_rect)
        
        # HP fill
        hp_percent = creature.creature.stats.hp / creature.creature.stats.max_hp
        fill_width = int(bar_width * hp_percent)
        
        # Color based on HP percentage
        if hp_percent > 0.6:
            hp_color = (100, 255, 100)
        elif hp_percent > 0.3:
            hp_color = (255, 255, 100)
        else:
            hp_color = (255, 100, 100)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(screen, hp_color, fill_rect)
        
        # Border
        pygame.draw.rect(screen, (200, 200, 200), bg_rect, 1)
        
        # HP text (skip in simplified mode)
        if not simplified:
            hp_text = f"{int(creature.creature.stats.hp)}/{int(creature.creature.stats.max_hp)}"
            text_surface = self._get_cached_text(hp_text, self.stat_font, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen_pos[0], bar_y - 8))
            screen.blit(text_surface, text_rect)
    
    def _draw_hunger_bar(
        self,
        screen: pygame.Surface,
        creature: BattleCreature,
        screen_pos: tuple
    ):
        """Draw hunger bar below HP bar."""
        bar_width = 40
        bar_height = 4
        bar_x = screen_pos[0] - bar_width // 2
        bar_y = screen_pos[1] - self.radius - 8
        
        # Background (dark gray)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        
        # Hunger fill
        hunger_percent = creature.creature.hunger / creature.creature.max_hunger
        fill_width = int(bar_width * hunger_percent)
        
        # Color based on hunger percentage
        if hunger_percent > 0.6:
            hunger_color = (216, 186, 67)  # Golden/yellow (well fed)
        elif hunger_percent > 0.3:
            hunger_color = (255, 165, 0)  # Orange (getting hungry)
        else:
            hunger_color = (200, 50, 50)  # Red (starving)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(screen, hunger_color, fill_rect)
        
        # Border
        pygame.draw.rect(screen, (150, 150, 150), bg_rect, 1)
    
    def _draw_energy_bar(
        self,
        screen: pygame.Surface,
        creature: BattleCreature,
        screen_pos: tuple
    ):
        """Draw energy bar below hunger bar."""
        bar_width = 40
        bar_height = 3
        bar_x = screen_pos[0] - bar_width // 2
        bar_y = screen_pos[1] - self.radius - 4  # Below hunger bar
        
        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (40, 40, 60), bg_rect)
        
        # Energy fill
        energy_percent = creature.creature.energy / creature.creature.max_energy
        fill_width = int(bar_width * energy_percent)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(screen, (100, 150, 255), fill_rect)
        
        # Border
        pygame.draw.rect(screen, (150, 150, 200), bg_rect, 1)
    
    def _draw_name(
        self,
        screen: pygame.Surface,
        creature: BattleCreature,
        screen_pos: tuple
    ):
        """Draw creature name below the creature."""
        name_text = f"{creature.creature.name} (Lv.{creature.creature.level})"
        text_surface = self._get_cached_text(name_text, self.name_font, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_pos[0], screen_pos[1] + self.radius + 12))
        
        # Draw shadow
        shadow_surface = self._get_cached_text(name_text, self.name_font, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(screen_pos[0] + 1, screen_pos[1] + self.radius + 13))
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw text
        screen.blit(text_surface, text_rect)
    
    def _get_cached_text(self, text: str, font: pygame.font.Font, color: tuple) -> pygame.Surface:
        """
        Get a cached text surface or create and cache it.
        
        Args:
            text: Text to render
            font: Font to use (reference via font size)
            color: Text color
            
        Returns:
            Rendered text surface
        """
        # Create cache key from text, font size, and color
        font_size = font.get_height()
        cache_key = (text, font_size, color)
        
        if cache_key not in self._text_cache:
            # Limit cache size to prevent memory issues
            if len(self._text_cache) > 200:
                # Clear oldest 50 entries (simple cache management)
                keys_to_remove = list(self._text_cache.keys())[:50]
                for key in keys_to_remove:
                    del self._text_cache[key]
            
            self._text_cache[cache_key] = font.render(text, True, color)
        
        return self._text_cache[cache_key]
    
    def _world_to_screen(
        self,
        world_pos: Vector2D,
        screen: pygame.Surface,
        arena
    ) -> tuple:
        """
        Convert world coordinates to screen coordinates.
        
        Uses margins that match arena_renderer.py to ensure creatures
        are rendered within the visible arena bounds, not under UI panels.
        """
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Margins match arena_renderer.py for consistency
        # Left margin for GENETIC STRAINS panel
        ui_margin_left = 250
        # Right margin for CREATURES and PELLET ECOSYSTEM panels
        ui_margin_right = 250
        # Top margin for header/title
        ui_margin_top = 80
        # Bottom margin for Battle Feed
        ui_margin_bottom = 200
        
        arena_width = screen_width - ui_margin_left - ui_margin_right
        arena_height = screen_height - ui_margin_top - ui_margin_bottom
        
        screen_x = ui_margin_left + (world_pos.x / arena.width) * arena_width
        screen_y = ui_margin_top + (world_pos.y / arena.height) * arena_height
        
        return (int(screen_x), int(screen_y))
