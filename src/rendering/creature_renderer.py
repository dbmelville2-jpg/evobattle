"""
Creature Renderer - Renders creatures as sprites or shapes.

Displays creatures at their positions with visual indicators for
team, health, and status.
"""

import pygame
import math
from ..systems.battle_spatial import SpatialBattle, BattleCreature
from ..models.spatial import Vector2D


class CreatureRenderer:
    """
    Renders creatures in the battle arena.
    
    Can render creatures as colored circles with team colors,
    or can be extended to use sprite sheets.
    
    Attributes:
        player_color: Base color for player team
        enemy_color: Base color for enemy team
        radius: Base radius for creature rendering
    """
    
    def __init__(
        self,
        player_color: tuple = (80, 120, 255),
        enemy_color: tuple = (255, 100, 100),
        radius: int = 15
    ):
        """
        Initialize the creature renderer.
        
        Args:
            player_color: RGB color for player team creatures
            enemy_color: RGB color for enemy team creatures
            radius: Base radius for creature circles
        """
        self.player_color = player_color
        self.enemy_color = enemy_color
        self.radius = radius
        
        # Font for creature names
        pygame.font.init()
        self.name_font = pygame.font.Font(None, 20)
        self.stat_font = pygame.font.Font(None, 16)
    
    def render(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render all creatures in the battle.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle containing creatures
        """
        # Render all creatures
        all_creatures = battle.player_creatures + battle.enemy_creatures
        
        for creature in all_creatures:
            if creature.is_alive():
                self._render_creature(screen, creature, battle)
    
    def _render_creature(
        self,
        screen: pygame.Surface,
        creature: BattleCreature,
        battle: SpatialBattle
    ):
        """Render a single creature."""
        # Get screen position
        screen_pos = self._world_to_screen(
            creature.spatial.position,
            screen,
            battle.arena
        )
        
        # Determine color based on team
        if creature.team == "player":
            color = self.player_color
            outline_color = (120, 160, 255)
        else:
            color = self.enemy_color
            outline_color = (255, 140, 140)
        
        # Draw creature body (circle)
        pygame.draw.circle(screen, color, screen_pos, self.radius)
        pygame.draw.circle(screen, outline_color, screen_pos, self.radius, 2)
        
        # Draw direction indicator (velocity)
        if creature.spatial.velocity.magnitude() > 0.1:
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
        
        # Draw HP bar above creature
        self._draw_hp_bar(screen, creature, screen_pos)
        
        # Draw hunger bar below HP bar
        self._draw_hunger_bar(screen, creature, screen_pos)
        
        # Draw energy bar (if applicable)
        if hasattr(creature.creature, 'energy') and creature.creature.energy < creature.creature.max_energy:
            self._draw_energy_bar(screen, creature, screen_pos)
        
        # Draw creature name below
        self._draw_name(screen, creature, screen_pos)
        
        # Draw target line if creature has a target
        if creature.target and creature.target.is_alive():
            target_screen_pos = self._world_to_screen(
                creature.target.spatial.position,
                screen,
                battle.arena
            )
            # Draw semi-transparent line to target
            pygame.draw.line(
                screen,
                (*color[:3], 100),  # Semi-transparent
                screen_pos,
                target_screen_pos,
                1
            )
    
    def _draw_hp_bar(
        self,
        screen: pygame.Surface,
        creature: BattleCreature,
        screen_pos: tuple
    ):
        """Draw HP bar above the creature."""
        bar_width = 40
        bar_height = 6
        bar_x = screen_pos[0] - bar_width // 2
        bar_y = screen_pos[1] - self.radius - 15
        
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
        
        # HP text
        hp_text = f"{creature.creature.stats.hp}/{creature.creature.stats.max_hp}"
        text_surface = self.stat_font.render(hp_text, True, (255, 255, 255))
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
        text_surface = self.name_font.render(name_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_pos[0], screen_pos[1] + self.radius + 12))
        
        # Draw shadow
        shadow_surface = self.name_font.render(name_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(screen_pos[0] + 1, screen_pos[1] + self.radius + 13))
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw text
        screen.blit(text_surface, text_rect)
    
    def _world_to_screen(
        self,
        world_pos: Vector2D,
        screen: pygame.Surface,
        arena
    ) -> tuple:
        """Convert world coordinates to screen coordinates."""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        ui_margin_top = 100
        ui_margin_side = 50
        ui_margin_bottom = 150
        
        arena_width = screen_width - (ui_margin_side * 2)
        arena_height = screen_height - ui_margin_top - ui_margin_bottom
        
        screen_x = ui_margin_side + (world_pos.x / arena.width) * arena_width
        screen_y = ui_margin_top + (world_pos.y / arena.height) * arena_height
        
        return (int(screen_x), int(screen_y))
