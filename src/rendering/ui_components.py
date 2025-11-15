"""
UI Components - Displays overlays, battle info, and event logs.

Provides HUD elements like battle state, team stats, event feed,
and pause/status indicators.
"""

import pygame
from typing import List, Deque
from collections import deque
from ..systems.battle_spatial import SpatialBattle, BattleEvent, BattleEventType


class UIComponents:
    """
    Manages UI overlays and information displays.
    
    Displays battle state, team information, event log,
    and other HUD elements.
    
    Attributes:
        title_font: Font for titles
        text_font: Font for regular text
        small_font: Font for small text
        event_log: Recent battle events to display
        max_log_entries: Maximum number of log entries to keep
    """
    
    def __init__(self, max_log_entries: int = 8):
        """
        Initialize UI components.
        
        Args:
            max_log_entries: Maximum number of event log entries to display
        """
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Event log
        self.event_log: Deque[str] = deque(maxlen=max_log_entries)
        self.max_log_entries = max_log_entries
        
        # Colors
        self.text_color = (255, 255, 255)
        self.panel_bg = (20, 20, 30, 180)
    
    def add_event_to_log(self, event: BattleEvent):
        """
        Add a battle event to the display log.
        
        Args:
            event: The battle event to log
        """
        # Only log certain event types
        if event.event_type in [
            BattleEventType.ABILITY_USE,
            BattleEventType.DAMAGE_DEALT,
            BattleEventType.HEALING,
            BattleEventType.CRITICAL_HIT,
            BattleEventType.CREATURE_FAINT,
            BattleEventType.BATTLE_START,
            BattleEventType.BATTLE_END
        ]:
            self.event_log.append(event.message)
    
    def render(self, screen: pygame.Surface, battle: SpatialBattle, paused: bool = False):
        """
        Render all UI components.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle to display info for
            paused: Whether the game is paused
        """
        # Top bar - Battle title and time
        self._render_top_bar(screen, battle)
        
        # Strain status panels (left and right)
        self._render_strain_panel(screen, battle, is_left=True)
        self._render_strain_panel(screen, battle, is_left=False)
        
        # Event log (bottom)
        self._render_event_log(screen)
        
        # Pause indicator
        if paused:
            self._render_pause_indicator(screen)
        
        # Battle end overlay
        if battle.is_over:
            self._render_battle_end(screen, battle)
        
        # Controls help (bottom right)
        self._render_controls_help(screen)
    
    def _render_top_bar(self, screen: pygame.Surface, battle: SpatialBattle):
        """Render the top information bar."""
        screen_width = screen.get_width()
        
        # Semi-transparent background
        bar_rect = pygame.Rect(0, 0, screen_width, 80)
        bar_surface = pygame.Surface((screen_width, 80), pygame.SRCALPHA)
        pygame.draw.rect(bar_surface, self.panel_bg, bar_rect)
        screen.blit(bar_surface, (0, 0))
        
        # Title
        title_text = "EvoBattle - Spatial Combat Arena"
        title_surface = self.title_font.render(title_text, True, self.text_color)
        title_rect = title_surface.get_rect(center=(screen_width // 2, 25))
        screen.blit(title_surface, title_rect)
        
        # Battle time
        time_text = f"Time: {battle.current_time:.1f}s"
        time_surface = self.text_font.render(time_text, True, self.text_color)
        time_rect = time_surface.get_rect(center=(screen_width // 2, 55))
        screen.blit(time_surface, time_rect)
    
    def _render_strain_panel(
        self,
        screen: pygame.Surface,
        battle: SpatialBattle,
        is_left: bool
    ):
        """
        Render a strain/genetic family panel showing population by strain.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle
            is_left: Whether this is the left panel (True) or right (False)
        """
        panel_width = 220
        panel_height = 300
        margin = 10
        
        if is_left:
            panel_x = margin
        else:
            panel_x = screen.get_width() - panel_width - margin
        
        panel_y = 90
        
        # Panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface,
            self.panel_bg,
            pygame.Rect(0, 0, panel_width, panel_height),
            border_radius=8
        )
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Header
        header_text = "GENETIC STRAINS" if is_left else "CREATURES"
        header_surface = self.text_font.render(header_text, True, self.text_color)
        header_rect = header_surface.get_rect(centerx=panel_width // 2, top=10)
        screen.blit(header_surface, (panel_x + header_rect.x, panel_y + header_rect.y))
        
        y_offset = 40
        
        if is_left:
            # Left panel: Show strain statistics
            # Group creatures by strain
            strain_groups = {}
            for creature in battle.creatures:
                strain_id = creature.creature.strain_id
                if strain_id not in strain_groups:
                    strain_groups[strain_id] = []
                strain_groups[strain_id].append(creature)
            
            # Sort by population size
            sorted_strains = sorted(
                strain_groups.items(),
                key=lambda x: len([c for c in x[1] if c.is_alive()]),
                reverse=True
            )
            
            # Display stats for each strain
            for strain_id, creatures in sorted_strains[:6]:  # Show top 6 strains
                if y_offset > panel_height - 30:
                    break
                
                alive_count = sum(1 for c in creatures if c.is_alive())
                total_count = len(creatures)
                
                # Calculate average hue for strain color
                alive_creatures = [c for c in creatures if c.is_alive()]
                if alive_creatures:
                    avg_hue = sum(c.creature.hue for c in alive_creatures) / len(alive_creatures)
                    import colorsys
                    rgb = colorsys.hsv_to_rgb(avg_hue / 360.0, 0.8, 0.9)
                    strain_color = tuple(int(255 * x) for x in rgb)
                else:
                    strain_color = (100, 100, 100)  # Gray for extinct
                
                # Draw color indicator
                pygame.draw.circle(
                    screen,
                    strain_color,
                    (panel_x + 15, panel_y + y_offset + 6),
                    8
                )
                
                # Strain info
                strain_text = f"Strain {strain_id[:8]}"
                text_surface = self.small_font.render(strain_text, True, self.text_color)
                screen.blit(text_surface, (panel_x + 30, panel_y + y_offset))
                
                # Population count
                count_text = f"{alive_count}/{total_count}"
                count_surface = self.small_font.render(count_text, True, self.text_color)
                screen.blit(count_surface, (panel_x + panel_width - 50, panel_y + y_offset))
                
                y_offset += 22
            
            # Total alive count
            if y_offset < panel_height - 40:
                y_offset += 10
                total_alive = sum(1 for c in battle.creatures if c.is_alive())
                total_text = f"Total Alive: {total_alive}/{len(battle.creatures)}"
                total_surface = self.small_font.render(total_text, True, (200, 255, 200))
                screen.blit(total_surface, (panel_x + 10, panel_y + y_offset))
        
        else:
            # Right panel: Show individual creature stats
            alive_count = sum(1 for c in battle.creatures if c.is_alive())
            
            # Alive count
            alive_text = f"Alive: {alive_count}/{len(battle.creatures)}"
            alive_surface = self.small_font.render(alive_text, True, self.text_color)
            screen.blit(alive_surface, (panel_x + 10, panel_y + y_offset))
            y_offset += 25
            
            # Show alive creatures
            alive_creatures = [c for c in battle.creatures if c.is_alive()][:8]
            
            for creature in alive_creatures:
                if y_offset > panel_height - 30:
                    break
                
                # Use creature's hue color
                creature_color = creature.creature.get_display_color()
                
                # Draw color indicator
                pygame.draw.circle(
                    screen,
                    creature_color,
                    (panel_x + 15, panel_y + y_offset + 6),
                    6
                )
                
                # Creature name
                creature_text = f"{creature.creature.name[:10]}"
                text_surface = self.small_font.render(creature_text, True, self.text_color)
                screen.blit(text_surface, (panel_x + 30, panel_y + y_offset))
                
                # HP bar
                hp_percent = creature.creature.stats.hp / creature.creature.stats.max_hp
                bar_width = 80
                bar_x = panel_x + 130
                bar_y = panel_y + y_offset + 2
                
                # Background
                pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, 10))
                
                # Fill
                if hp_percent > 0.6:
                    hp_color = (100, 255, 100)
                elif hp_percent > 0.3:
                    hp_color = (255, 255, 100)
                else:
                    hp_color = (255, 100, 100)
                
                fill_width = int(bar_width * hp_percent)
                if fill_width > 0:
                    pygame.draw.rect(screen, hp_color, (bar_x, bar_y, fill_width, 10))
                
                # Border
                pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, 10), 1)
                
                y_offset += 22
    
    def _render_event_log(self, screen: pygame.Surface):
        """Render the event log at the bottom."""
        screen_width = screen.get_width()
        panel_height = 130
        panel_y = screen.get_height() - panel_height
        
        # Panel background
        panel_surface = pygame.Surface((screen_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface,
            self.panel_bg,
            pygame.Rect(0, 0, screen_width, panel_height)
        )
        screen.blit(panel_surface, (0, panel_y))
        
        # Title
        title_surface = self.text_font.render("Battle Feed", True, (200, 200, 255))
        screen.blit(title_surface, (20, panel_y + 10))
        
        # Event messages
        y_offset = 40
        for event_msg in list(self.event_log):
            if y_offset > panel_height - 20:
                break
            
            text_surface = self.small_font.render(event_msg, True, self.text_color)
            screen.blit(text_surface, (20, panel_y + y_offset))
            y_offset += 20
    
    def _render_pause_indicator(self, screen: pygame.Surface):
        """Render pause indicator in center of screen."""
        pause_text = "PAUSED"
        pause_surface = self.title_font.render(pause_text, True, (255, 255, 100))
        pause_rect = pause_surface.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2)
        )
        
        # Background
        bg_rect = pause_rect.inflate(40, 20)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 200), pygame.Rect(0, 0, bg_rect.width, bg_rect.height), border_radius=10)
        screen.blit(bg_surface, bg_rect.topleft)
        
        # Text
        screen.blit(pause_surface, pause_rect)
        
        # Instructions
        instruction_text = "Press SPACE to resume"
        instruction_surface = self.small_font.render(instruction_text, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 + 40)
        )
        screen.blit(instruction_surface, instruction_rect)
    
    def _render_battle_end(self, screen: pygame.Surface, battle: SpatialBattle):
        """Render battle end overlay."""
        # Determine survivors
        alive_creatures = [c for c in battle.creatures if c.is_alive()]
        
        if len(alive_creatures) == 1:
            winner_text = f"{alive_creatures[0].creature.name} WINS!"
            winner_color = alive_creatures[0].creature.get_display_color()
        elif len(alive_creatures) > 1:
            winner_text = f"{len(alive_creatures)} SURVIVORS!"
            winner_color = (100, 255, 100)
        else:
            winner_text = "NO SURVIVORS"
            winner_color = (200, 200, 200)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 150), pygame.Rect(0, 0, screen.get_width(), screen.get_height()))
        screen.blit(overlay, (0, 0))
        
        # Winner text
        winner_surface = self.title_font.render(winner_text, True, winner_color)
        winner_rect = winner_surface.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2)
        )
        screen.blit(winner_surface, winner_rect)
        
        # Stats
        duration_text = f"Battle Duration: {battle.current_time:.1f}s"
        duration_surface = self.text_font.render(duration_text, True, self.text_color)
        duration_rect = duration_surface.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 + 50)
        )
        screen.blit(duration_surface, duration_rect)
        
        events_text = f"Total Events: {len(battle.events)}"
        events_surface = self.text_font.render(events_text, True, self.text_color)
        events_rect = events_surface.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 + 80)
        )
        screen.blit(events_surface, events_rect)
    
    def _render_controls_help(self, screen: pygame.Surface):
        """Render controls help in bottom right."""
        controls = [
            "SPACE - Pause/Resume",
            "ESC - Exit"
        ]
        
        x = screen.get_width() - 200
        y = screen.get_height() - 90
        
        for i, control in enumerate(controls):
            text_surface = self.small_font.render(control, True, (180, 180, 180))
            screen.blit(text_surface, (x, y + i * 18))
    
    def draw_battle_timer(self, screen: pygame.Surface, time: float, position: tuple):
        """
        Draw battle timer at the specified position.
        
        Helper method for simple timer display without full UI rendering.
        
        Args:
            screen: Pygame surface to draw on
            time: Current battle time in seconds
            position: (x, y) position for centered timer
        """
        time_text = f"Time: {time:.1f}s"
        time_surface = self.text_font.render(time_text, True, self.text_color)
        time_rect = time_surface.get_rect(center=position)
        screen.blit(time_surface, time_rect)
    
    def draw_population_status(
        self,
        screen: pygame.Surface,
        alive_count: int,
        total_count: int,
        position: tuple
    ):
        """
        Draw population status at the specified position.
        
        Helper method for simple population status display without full UI rendering.
        
        Args:
            screen: Pygame surface to draw on
            alive_count: Number of alive creatures
            total_count: Total number of creatures in population
            position: (x, y) position for centered status
        """
        status_text = f"Population: {alive_count}/{total_count}"
        color = (100, 255, 150)  # Green for population
        status_surface = self.text_font.render(status_text, True, color)
        status_rect = status_surface.get_rect(center=position)
        screen.blit(status_surface, status_rect)
