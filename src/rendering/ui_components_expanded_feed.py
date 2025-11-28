"""
UI Components - Displays overlays, battle info, and event logs.

Provides HUD elements like battle state, team stats, event feed,
and pause/status indicators.
"""

import pygame
from typing import List, Deque
from collections import deque
from ..systems.battle_spatial import SpatialBattle, BattleEvent, BattleEventType
from .scientific_cursor import ScientificCursor, CursorTool


class UIComponents:
    """Manages UI overlays and information displays.
    
    Displays battle state, team information, event log,
    and other HUD elements.
    
    Attributes:
        title_font: Font for titles
        font: Regular font for text
        small_font: Smaller font for details
        event_log: Deque of recent battle events
        max_log_entries: Maximum number of log entries to keep
    """
    
    def __init__(self, max_log_entries: int = 8, show_pellet_stats: bool = True):
        """
        Initialize UI components.
        
        Args:
            max_log_entries: Maximum number of event log entries to display
            show_pellet_stats: Whether to show pellet statistics panel
        """
        self.title_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.event_log: Deque[BattleEvent] = deque(maxlen=max_log_entries)
        self.max_log_entries = max_log_entries
        self.show_pellet_stats = show_pellet_stats
        
        # Text cache for performance
        self.text_cache = {}
        
        # Genetic Strains Panel
        self.genetic_scroll_offset = 0
        self.selected_strain_id = None
        self.show_strain_details = False
        self.strain_detail_popup_rect = None
        
        # Disease Strains Panel
        self.show_disease_strains = False  # Toggle between genetic/disease view
        
        # Ethics Dashboard
        self.show_ethics_dashboard = False
        
        # Research Assistant Panel
        self.show_advisor_panel = False
        
        # Scientific Toolbar
        self.tool_rects = {}  # Maps CursorTool to pygame.Rect for click detection
        self.tool_icons = {}  # Maps CursorTool to pygame.Surface (icon image)
        
        # Load tool icons from assets
        self._load_tool_icons()
        
    def add_event_to_log(self, event: BattleEvent):
        """
        Add a battle event to the display log.
        
        Args:
            event: The battle event to log
        """
        self.event_log.append(event)
    
    def handle_event(self, event: pygame.event.Event, battle: SpatialBattle, scientific_cursor: ScientificCursor = None):
        """
        Handle UI interaction events.
        
        Args:
            event: Pygame event
            battle: Battle instance
            scientific_cursor: Optional ScientificCursor instance
            
        Returns:
            bool: True if event was handled by UI, False otherwise
        """
        # Handle toolbar clicks
        if event.type == pygame.MOUSEBUTTONDOWN and scientific_cursor:
            mouse_pos = event.pos
            
            # Check if clicking on toolbar
            for tool, rect in self.tool_rects.items():
                if rect.collidepoint(mouse_pos):
                    scientific_cursor.select_tool(tool)
                    return True
        
        # Handle genetic strains panel scrolling
        if event.type == pygame.MOUSEWHEEL:
            # Check if mouse is over the genetic strains panel
            mouse_pos = pygame.mouse.get_pos()
            # Panel is at x=10, y=420 (approx), width=280, height varies
            panel_rect = pygame.Rect(10, 420, 280, 300)
            if panel_rect.collidepoint(mouse_pos):
                self.genetic_scroll_offset -= event.y * 20
                self.genetic_scroll_offset = max(0, self.genetic_scroll_offset)
                return True
        
        # Handle genetic strain selection
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Ignore scroll wheel button events (4=scroll up, 5=scroll down)
            if event.button in (4, 5):
                return False
            
            mouse_pos = event.pos
            
            # Check if clicking on strain detail popup close button
            if self.show_strain_details and self.strain_detail_popup_rect:
                close_button_rect = pygame.Rect(
                    self.strain_detail_popup_rect.right - 30,
                    self.strain_detail_popup_rect.top + 5,
                    25, 25
                )
                if close_button_rect.collidepoint(mouse_pos):
                    self.show_strain_details = False
                    return True
                
                # If clicking outside popup, close it
                if not self.strain_detail_popup_rect.collidepoint(mouse_pos):
                    self.show_strain_details = False
                    return True
            
            # Check if clicking on a strain in the list
            # This is handled in the render method where we track strain rects
            # For now, we'll just check if we're in the panel area
            panel_rect = pygame.Rect(10, 420, 280, 300)
            if panel_rect.collidepoint(mouse_pos):
                # Strain selection is handled in render where we have strain positions
                return False
        
        return False
    
    def _get_cached_text(self, text: str, font: pygame.font.Font, color: tuple):
        """
        Get a cached text surface or create and cache it.
        
        Args:
            text: Text to render
            font: Font to use (reference via font size)
            color: Text color
            
        Returns:
            Rendered text surface
        """
        # Create cache key
        font_size = font.get_height()
        cache_key = (text, font_size, color)
        
        # Check cache
        if cache_key in self.text_cache:
            return self.text_cache[cache_key]
        
        # Render and cache
        surface = font.render(text, True, color)
        
        # Limit cache size
        if len(self.text_cache) > 1000:
            # Clear oldest half of cache
            keys = list(self.text_cache.keys())
            for key in keys[:500]:
                del self.text_cache[key]
        
        self.text_cache[cache_key] = surface
        return surface
    
    def render(self, screen: pygame.Surface, battle: SpatialBattle, paused: bool, scientific_cursor: ScientificCursor = None):
        """
        Render all UI components.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle to display info for
            paused: Whether the game is paused
            scientific_cursor: Optional ScientificCursor instance
        """
        # Render top bar
        self._render_top_bar(screen, battle, paused)
        
        # Render weather panel (top-left)
        if hasattr(battle, 'environment') and battle.environment:
            self._render_weather_panel(screen, battle)
        
        # Render biome panel (below weather)
        if hasattr(battle, 'environment') and battle.environment:
            self._render_biome_panel(screen, battle)
        
        # Render genetic strains panel (below biome)
        self._render_genetic_strains_panel(screen, battle)
        
        # Render battle feed (right side)
        self._render_battle_feed(screen)
        
        # Render pellet stats (bottom-left)
        if self.show_pellet_stats:
            self._render_pellet_stats(screen, battle)
        
        # Render Scientific Toolbar (top-center)
        if scientific_cursor:
            self.render_scientific_toolbar(screen, battle, scientific_cursor)
        
        # Render Ethics Dashboard (if enabled)
        if self.show_ethics_dashboard and hasattr(battle, 'ethics_system'):
            self.render_ethics_dashboard(screen, battle)
        
        # Render Research Assistant Panel (if enabled)
        if self.show_advisor_panel and hasattr(battle, 'overseer'):
            self.render_assistant_panel(screen, battle)
        
        # Render Dilemma Popup (if present)
        if hasattr(battle, 'pending_dilemma') and battle.pending_dilemma:
            self.render_dilemma_popup(screen, battle.pending_dilemma)
    
    def render_expanded_feed(self, screen: pygame.Surface, battle: SpatialBattle, simulation_speed: float, paused: bool):
        """
        Render expanded battle feed mode - full screen detailed event log.
        
        Args:
            screen: Pygame surface
            battle: Battle instance
            simulation_speed: Current simulation speed multiplier
            paused: Whether simulation is paused
        """
        # Fill background
        screen.fill((15, 15, 20))
        
        # Header
        header_height = 80
        pygame.draw.rect(screen, (25, 25, 35), (0, 0, screen.get_width(), header_height))
        pygame.draw.rect(screen, (60, 60, 80), (0, header_height-2, screen.get_width(), 2))
        
        # Title
        title = self.title_font.render("EXPANDED BATTLE FEED", True, (100, 200, 255))
        screen.blit(title, (20, 20))
        
        # Speed indicator
        if paused:
            speed_text = "⏸ PAUSED"
            speed_color = (255, 100, 100)
        else:
            speed_text = f"⏩ {simulation_speed}x"
            speed_color = (100, 255, 100)
        speed_surf = self.font.render(speed_text, True, speed_color)
        screen.blit(speed_surf, (screen.get_width() - 150, 25))
        
        # Mode indicator
        mode_text = "📊 FEED MODE (Press F to toggle)"
        mode_surf = self.small_font.render(mode_text, True, (150, 150, 150))
        screen.blit(mode_surf, (20, 55))
        
        # Stats summary
        alive_count = len([c for c in battle.creatures if c.is_alive()])
        total_births = getattr(battle, 'birth_count', 0)
        total_deaths = getattr(battle, 'death_count', 0)
        pellet_count = len(battle.arena.resources)
        
        stats_y = header_height + 20
        stats = [
            f"Alive: {alive_count}",
            f"Births: {total_births}",
            f"Deaths: {total_deaths}",
            f"Pellets: {pellet_count}",
            f"Time: {int(getattr(battle, 'current_time', 0))}s"
        ]
        
        stats_x = 20
        for stat in stats:
            stat_surf = self.font.render(stat, True, (200, 200, 200))
            screen.blit(stat_surf, (stats_x, stats_y))
            stats_x += stat_surf.get_width() + 40
        
        # Event log (scrollable)
        log_start_y = stats_y + 50
        log_height = screen.get_height() - log_start_y - 20
        
        # Get all events (last 100)
        events = list(self.event_log)
        events.reverse()  # Most recent first
        
        # Render events
        event_y = log_start_y
        line_height = 30
        
        for i, event in enumerate(events):
            if event_y > screen.get_height() - 20:
                break
            
            # Event type color coding
            if event.event_type == BattleEventType.CREATURE_BIRTH:
                color = (100, 255, 100)  # Green
                icon = "🟢"
            elif event.event_type == BattleEventType.CREATURE_DEATH:
                color = (255, 100, 100)  # Red
                icon = "🔴"
            elif event.event_type == BattleEventType.CREATURE_ATTACK:
                color = (255, 200, 100)  # Orange
                icon = "⚔️"
            elif event.event_type == BattleEventType.PELLET_SPAWN:
                color = (100, 255, 255)  # Cyan
                icon = "🟦"
            else:
                color = (200, 200, 200)  # White
                icon = "⚪"
            
            # Render event
            event_text = f"{icon} {event.message}"
            
            # Add detailed data if available
            if hasattr(event, 'data') and event.data:
                details = []
                if 'parent1' in event.data and 'parent2' in event.data:
                    details.append(f"Parents: {event.data['parent1']} & {event.data['parent2']}")
                if 'traits' in event.data:
                    trait_names = [t if isinstance(t, str) else t for t in event.data['traits'][:3]]
                    details.append(f"Traits: {', '.join(trait_names)}")
                if 'mutations' in event.data and event.data['mutations']:
                    details.append(f"Mutations: {len(event.data['mutations'])}")
                if 'cause' in event.data:
                    details.append(f"Cause: {event.data['cause']}")
                if 'damage' in event.data:
                    details.append(f"Damage: {event.data['damage']}")
                
                if details:
                    event_text += f" | {' | '.join(details)}"
            
            # Render with background
            text_surf = self.small_font.render(event_text, True, color)
            
            # Background rect
            bg_rect = pygame.Rect(10, event_y, screen.get_width() - 20, line_height - 2)
            bg_color = (30, 30, 40) if i % 2 == 0 else (25, 25, 35)
            pygame.draw.rect(screen, bg_color, bg_rect)
            
            # Text
            screen.blit(text_surf, (15, event_y + 5))
            
            event_y += line_height
        
        # Controls help (bottom)
        help_text = "Controls: Q/W/R/T/Y = Speed | SPACE = Pause | F = Toggle Mode | ESC = Menu"
        help_surf = self.small_font.render(help_text, True, (100, 100, 120))
        screen.blit(help_surf, ((screen.get_width() - help_surf.get_width()) // 2, screen.get_height() - 25))
