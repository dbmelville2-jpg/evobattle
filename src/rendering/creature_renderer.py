"""
Creature Renderer - Renders creatures as sprites or shapes.

Displays creatures at their positions with visual indicators for
team, health, and status. Now features a stylized "Clean & Vibrant" look.
"""

import pygame
import math
import time
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
        radius: int = 12 # Increased from 10 for better visibility
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
    
    def render(self, screen: pygame.Surface, battle: SpatialBattle, camera):
        """
        Render all creatures in the battle.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle containing creatures
            camera: Camera instance for coordinate transformation
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
                self._render_creature(screen, creature, battle, camera, lod_level, mouse_pos)
    
    def _render_creature(
        self,
        screen: pygame.Surface,
        creature: BattleCreature,
        battle: SpatialBattle,
        camera,
        lod_level: int = 0,
        mouse_pos: tuple = (0, 0)
    ):
        """Render a single creature."""
        
        # Calculate world position with optional offsets (e.g. lunge)
        world_pos = Vector2D(creature.spatial.position.x, creature.spatial.position.y)
        
        # Attack Lunge Animation
        if creature.combat_engaged and creature.target and creature.target.is_alive():
            # Simple lunge: if attacking (we don't have exact attack frame, so we use combat_engaged + periodic lunge)
            # For a "gamey" feel, let's lunge periodically
            lunge_cycle = (time.time() * 2) % 1.0 # 2 lunges per second
            if lunge_cycle < 0.2: # Quick forward motion
                direction = (creature.target.spatial.position - creature.spatial.position).normalized()
                lunge_dist = 5.0 # World units
                world_pos += direction * (lunge_dist * (lunge_cycle / 0.2))
            elif lunge_cycle < 0.4: # Return
                direction = (creature.target.spatial.position - creature.spatial.position).normalized()
                lunge_dist = 5.0
                world_pos += direction * (lunge_dist * (1.0 - (lunge_cycle - 0.2) / 0.2))
        
        # Get screen position
        screen_pos = camera.world_to_screen(world_pos)
        
        # Scale radius by zoom
        # Idle breathing animation
        breath = (math.sin(time.time() * 3) + 1) * 0.1 # 0.0 to 0.2
        base_radius_anim = self.radius * (1.0 + breath)
        
        radius = int(base_radius_anim * camera.zoom)
        radius = max(4, min(40, radius))  # Clamp size (slightly larger max)
        
        # Use HSV color from creature
        color = creature.creature.get_display_color()
        
        # Hit Flash (White)
        # We need to know if creature was just hit. 
        # Ideally, BattleCreature would track "last_hit_time".
        # Since we don't have that easily without modifying the model, we'll skip the flash logic here
        # OR we can check health drop? No, that's stateful.
        # Let's rely on the EventAnimator for damage numbers, and maybe add a flash effect there?
        # Actually, we can check if health < max_health and maybe pulse red?
        # For now, let's stick to the disease tint logic which is already here.
        
        # Apply disease tint if infected
        if hasattr(creature.creature, 'active_infection') and creature.creature.active_infection:
            infection = creature.creature.active_infection
            # Flash color if symptomatic
            if infection.stage.name == 'SYMPTOMATIC':
                flash = (math.sin(time.time() * 10) + 1) / 2
                tint = infection.disease.color_tint
                # Blend base color with tint
                color = tuple(
                    int(c * (1 - flash * 0.7) + tint[i] * (flash * 0.7))
                    for i, c in enumerate(color)
                )
            else:
                # Slight tint for incubating/recovering
                tint = infection.disease.color_tint
                color = tuple(
                    int(c * 0.7 + tint[i] * 0.3)
                    for i, c in enumerate(color)
                )
        
        # Calculate outline
        # Thicker, darker outline for "sticker" look
        outline_color = (20, 20, 20) # Almost black
        outline_width = max(2, int(3 * camera.zoom)) # Scale outline slightly
        
        # Draw creature body (circle)
        pygame.draw.circle(screen, outline_color, screen_pos, radius + outline_width) # Outline
        pygame.draw.circle(screen, color, screen_pos, radius) # Body
        
        # Inner highlight/shading for 3D feel
        highlight_pos = (screen_pos[0] - radius//3, screen_pos[1] - radius//3)
        highlight_radius = radius // 3
        if highlight_radius > 1:
             pygame.draw.circle(screen, (255, 255, 255, 100), highlight_pos, highlight_radius)
        
        # Check for hover (override LOD)
        # Simple distance check for hover
        dx = screen_pos[0] - mouse_pos[0]
        dy = screen_pos[1] - mouse_pos[1]
        is_hovered = (dx*dx + dy*dy) < (radius + 5)**2
        
        # Render carrying indicator
        self._render_creature_carrying_materials(screen, creature, screen_pos[0], screen_pos[1])
        
        # Force high detail if hovered or selected (if we had selection)
        if is_hovered:
            lod_level = 0
            # Draw selection bracket/highlight
            pygame.draw.circle(screen, (255, 255, 255), screen_pos, radius + outline_width + 2, 2)
        
        # Draw direction indicator (velocity) - Skip in LOD 2
        if lod_level < 2 and creature.spatial.velocity.magnitude() > 0.1:
            vel_norm = creature.spatial.velocity.normalized()
            end_x = screen_pos[0] + vel_norm.x * (radius + 8)
            end_y = screen_pos[1] + vel_norm.y * (radius + 8)
            pygame.draw.line(
                screen,
                outline_color,
                screen_pos,
                (int(end_x), int(end_y)),
                max(2, int(3 * camera.zoom))
            )
        
        # Draw HP bar above creature - Simplified in LOD 1, Skip in LOD 2
        if lod_level < 2:
            self._draw_hp_bar(screen, creature, screen_pos, radius, simplified=(lod_level == 1))
        
        # Draw hunger bar below HP bar - Skip in LOD 1+
        if lod_level < 1:
            self._draw_hunger_bar(screen, creature, screen_pos, radius)
        
        # Draw energy bar (if applicable) - Skip in LOD 1+
        if lod_level < 1 and hasattr(creature.creature, 'energy') and creature.creature.energy < creature.creature.max_energy:
            self._draw_energy_bar(screen, creature, screen_pos, radius)
        
        # Draw creature name below - Skip in LOD 1+
        if lod_level < 1:
            self._draw_name(screen, creature, screen_pos, radius)
        
        # Draw combat engagement indicator - Simplified in LOD 2 (just color, no pulse ring)
        if creature.combat_engaged:
            if lod_level < 2:
                # Draw a pulsing ring around creatures in active combat
                pulse = (math.sin(time.time() * 10) + 1) / 2  # Faster pulse for combat
                ring_radius = radius + 8 + int(pulse * 4)
                ring_color = (255, 50, 50) # Red alert
                pygame.draw.circle(screen, ring_color, screen_pos, ring_radius, 2)
        
        # Draw target line if creature has a target - Skip in LOD 2
        if lod_level < 2 and creature.target and creature.target.is_alive():
            target_screen_pos = camera.world_to_screen(creature.target.spatial.position)
            # Draw line to target - red if engaged, yellow if approaching
            line_color = (255, 100, 100) if creature.combat_engaged else (255, 255, 100)
            line_width = 2 if creature.combat_engaged else 1
            
            # Dashed line effect for style? Or just simple line.
            # Simple line is cleaner.
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
        radius: int,
        simplified: bool = False
    ):
        """Draw HP bar above the creature."""
        bar_width = 40 if not simplified else 30
        bar_height = 6 if not simplified else 4
        bar_x = screen_pos[0] - bar_width // 2
        bar_y = screen_pos[1] - radius - (15 if not simplified else 8)
        
        # Background (darker gray for contrast)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        
        # HP fill
        hp_percent = creature.creature.stats.hp / creature.creature.stats.max_hp
        fill_width = int(bar_width * hp_percent)
        
        # Color based on HP percentage - Vibrant colors
        if hp_percent > 0.6:
            hp_color = (50, 255, 100) # Bright Green
        elif hp_percent > 0.3:
            hp_color = (255, 220, 50) # Bright Yellow
        else:
            hp_color = (255, 50, 50) # Bright Red
        
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(screen, hp_color, fill_rect)
        
        # Border (Black for style)
        pygame.draw.rect(screen, (0, 0, 0), bg_rect, 1)
        
        # HP text (skip in simplified mode)
        if not simplified:
            hp_text = f"{int(creature.creature.stats.hp)}" # Just current HP for cleaner look
            text_surface = self._get_cached_text(hp_text, self.stat_font, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen_pos[0], bar_y - 8))
            
            # Shadow for text
            shadow_surface = self._get_cached_text(hp_text, self.stat_font, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(screen_pos[0] + 1, bar_y - 7))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)
    
    def _draw_hunger_bar(
        self,
        screen: pygame.Surface,
        creature: BattleCreature,
        screen_pos: tuple,
        radius: int
    ):
        """Draw hunger bar below HP bar."""
        bar_width = 40
        bar_height = 4
        bar_x = screen_pos[0] - bar_width // 2
        bar_y = screen_pos[1] - radius - 8
        
        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        
        # Hunger fill
        hunger_percent = creature.creature.hunger / creature.creature.max_hunger
        fill_width = int(bar_width * hunger_percent)
        
        # Color based on hunger percentage
        if hunger_percent > 0.6:
            hunger_color = (255, 200, 50)  # Golden
        elif hunger_percent > 0.3:
            hunger_color = (255, 150, 0)  # Orange
        else:
            hunger_color = (200, 50, 50)  # Red
        
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(screen, hunger_color, fill_rect)
        
        # Border
        pygame.draw.rect(screen, (0, 0, 0), bg_rect, 1)
    
    def _draw_energy_bar(
        self,
        screen: pygame.Surface,
        creature: BattleCreature,
        screen_pos: tuple,
        radius: int
    ):
        """Draw energy bar below hunger bar."""
        bar_width = 40
        bar_height = 3
        bar_x = screen_pos[0] - bar_width // 2
        bar_y = screen_pos[1] - radius - 4  # Below hunger bar
        
        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (40, 40, 60), bg_rect)
        
        # Energy fill
        energy_percent = creature.creature.energy / creature.creature.max_energy
        fill_width = int(bar_width * energy_percent)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(screen, (100, 200, 255), fill_rect) # Cyan-ish
        
        # Border
        pygame.draw.rect(screen, (0, 0, 0), bg_rect, 1)
    
    def _draw_name(
        self,
        screen: pygame.Surface,
        creature: BattleCreature,
        screen_pos: tuple,
        radius: int
    ):
        """Draw creature name below the creature."""
        name_text = f"{creature.creature.name} (Lv.{creature.creature.level})"
        text_surface = self._get_cached_text(name_text, self.name_font, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_pos[0], screen_pos[1] + radius + 12))
        
        # Draw shadow
        shadow_surface = self._get_cached_text(name_text, self.name_font, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(screen_pos[0] + 1, screen_pos[1] + radius + 13))
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
    
    def _render_creature_carrying_materials(self, screen: pygame.Surface, creature: BattleCreature, screen_x: int, screen_y: int):
        """
        Show indicator if creature is carrying materials.
        
        Args:
            screen: Pygame surface
            creature: BattleCreature instance
            screen_x, screen_y: Screen coordinates
        """
        if not hasattr(creature.creature, 'carried_materials'):
            return
        
        if not creature.creature.carried_materials:
            return
        
        # Draw small icon above creature
        icon_size = 6
        icon_y = screen_y - 20
        
        for i, material in enumerate(creature.creature.carried_materials[:3]):  # Max 3 shown
            from ..models.building.building_material import get_material_color
            color = get_material_color(material.material_type)
            
            icon_x = screen_x - icon_size + i * (icon_size + 2)
            pygame.draw.rect(
                screen,
                color,
                (icon_x, icon_y, icon_size, icon_size)
            )
            
            # Draw border
            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (icon_x, icon_y, icon_size, icon_size),
                1
            )
