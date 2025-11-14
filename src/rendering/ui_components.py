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
        self.player_team_color = (80, 120, 255)
        self.enemy_team_color = (255, 100, 100)
    
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
        
        # Team status panels (left and right)
        self._render_team_panel(screen, battle, "player", is_left=True)
        self._render_team_panel(screen, battle, "enemy", is_left=False)
        
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
    
    def _render_team_panel(
        self,
        screen: pygame.Surface,
        battle: SpatialBattle,
        team: str,
        is_left: bool
    ):
        """Render a team status panel."""
        panel_width = 220
        panel_height = 200
        margin = 10
        
        if is_left:
            panel_x = margin
            creatures = battle.player_creatures
            team_color = self.player_team_color
            team_name = "PLAYER TEAM"
        else:
            panel_x = screen.get_width() - panel_width - margin
            creatures = battle.enemy_creatures
            team_color = self.enemy_team_color
            team_name = "ENEMY TEAM"
        
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
        
        # Team name header
        header_surface = self.text_font.render(team_name, True, team_color)
        header_rect = header_surface.get_rect(centerx=panel_width // 2, top=10)
        screen.blit(header_surface, (panel_x + header_rect.x, panel_y + header_rect.y))
        
        # Creature stats
        y_offset = 40
        alive_count = sum(1 for c in creatures if c.is_alive())
        
        # Alive count
        alive_text = f"Alive: {alive_count}/{len(creatures)}"
        alive_surface = self.small_font.render(alive_text, True, self.text_color)
        screen.blit(alive_surface, (panel_x + 10, panel_y + y_offset))
        y_offset += 25
        
        # Individual creature stats
        for creature in creatures:
            if y_offset > panel_height - 30:
                break  # Panel full
            
            status = "💚" if creature.is_alive() else "💀"
            creature_text = f"{status} {creature.creature.name[:12]}"
            text_surface = self.small_font.render(creature_text, True, self.text_color)
            screen.blit(text_surface, (panel_x + 10, panel_y + y_offset))
            
            if creature.is_alive():
                # HP bar
                hp_percent = creature.creature.stats.hp / creature.creature.stats.max_hp
                bar_width = 100
                bar_x = panel_x + 120
                bar_y = panel_y + y_offset + 2
                
                # Background
                pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, 12))
                
                # Fill
                if hp_percent > 0.6:
                    hp_color = (100, 255, 100)
                elif hp_percent > 0.3:
                    hp_color = (255, 255, 100)
                else:
                    hp_color = (255, 100, 100)
                
                fill_width = int(bar_width * hp_percent)
                if fill_width > 0:
                    pygame.draw.rect(screen, hp_color, (bar_x, bar_y, fill_width, 12))
                
                # Border
                pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, 12), 1)
            
            y_offset += 25
    
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
        # Determine winner
        alive_players = [c for c in battle.player_creatures if c.is_alive()]
        winner = "PLAYER WINS!" if alive_players else "ENEMY WINS!"
        winner_color = self.player_team_color if alive_players else self.enemy_team_color
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 150), pygame.Rect(0, 0, screen.get_width(), screen.get_height()))
        screen.blit(overlay, (0, 0))
        
        # Winner text
        winner_surface = self.title_font.render(winner, True, winner_color)
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
