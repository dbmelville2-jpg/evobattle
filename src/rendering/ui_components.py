"""
UI Components - Displays overlays, battle info, and event logs.

Provides HUD elements like battle state, team stats, event feed,
and pause/status indicators.
"""

import pygame
from typing import List, Deque
from collections import deque
from ..systems.battle_spatial import SpatialBattle
from ..systems.battle_events import BattleEvent, BattleEventType
from .scientific_cursor import ScientificCursor, CursorTool


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
    
    def __init__(self, max_log_entries: int = 8, show_pellet_stats: bool = True):
        """
        Initialize UI components.
        
        Args:
            max_log_entries: Maximum number of event log entries to display
            show_pellet_stats: Whether to show pellet statistics panel
        """
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Event log
        self.event_log: Deque[str] = deque(maxlen=max_log_entries)
        self.max_log_entries = max_log_entries
        
        # Display options
        self.show_pellet_stats = show_pellet_stats
        
        # Load tool icons
        self.tool_icons = {}
        self._load_tool_icons()
        
        # Colors
        self.text_color = (255, 255, 255)
        self.panel_bg = (20, 20, 30, 180)
        
        # Text surface cache for performance
        self._text_cache = {}

        # Interactive control button geometry (populated when rendering)
        # Map: button_key -> pygame.Rect
        self._control_button_rects = {}

        # Controls panel sizing - ensure other panels can reserve space
        self.controls_panel_height = 240
        # Debug / interaction state
        self._last_click_info = None
        self._pressed_button = None
        self._pressed_time = 0.0
        # Genetic Strain Panel State
        self.strain_scroll_offset = 0
        # Pellet Panel State
        self.pellet_scroll_offset = 0
        self.pellet_panel_rect = None
        self.selected_strain_id = None
        self.strain_panel_rect = None  # Will be updated in render
        self.strain_item_rects = {}    # Map strain_id -> rect for click detection
        self.strain_panel_mode = "GENETIC" # "GENETIC" or "DISEASE"
        self.strain_panel_mode = "GENETIC" # "GENETIC" or "DISEASE"
        self.strain_tab_rects = {}
        
        # Popup State
        self.popup_scroll_offset = 0
        self._popup_button_rects = {}
        self._popup_content_height = 0
        
        # Dilemma UI State
        self.dilemma_choice_rects = {} # Map choice_index -> rect
        self.ask_advisor_rect = None
        self.advisor_panel_rect = None
        self.advisor_close_rect = None
        self.show_advisor_panel = False
        self.show_ethics_dashboard = False
        
        # Scientific Tools
        self.selected_tool = None # InterventionType value
        self.tool_rects = {}
        
        # Collapsible Panel States (True = Expanded, False = Collapsed)
        self.panel_states = {
            'weather': True,
            'biome': True,
            'genetic': True,
            'stats': True,
            'pellets': True,
            'controls': True,
            'log': True,
            'overseer': True
        }
        self.toggle_buttons = {} # Map panel_name -> rect
    
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
            BattleEventType.CREATURE_BIRTH,
            BattleEventType.CREATURE_DEATH,
            BattleEventType.BATTLE_START,
            BattleEventType.BATTLE_END
        ]:
            self.event_log.append(event.message)

    def handle_event(self, event: pygame.event.Event, battle: SpatialBattle, scientific_cursor: ScientificCursor = None) -> bool:
        """
        Handle UI interaction events.
        
        Args:
            event: Pygame event
            battle: Battle instance
            scientific_cursor: Optional ScientificCursor instance
            
        Returns:
            bool: True if event was handled by UI, False otherwise
        """
        # Ensure rects exist
        if not self._control_button_rects:
             try:
                 self._control_button_rects = self._compute_control_rects()
             except Exception:
                 self._control_button_rects = {}

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEWHEEL:
            # Check for Pellet Panel Scroll
            if self.pellet_panel_rect and self.pellet_panel_rect.collidepoint(mouse_pos):
                self.pellet_scroll_offset = max(0, self.pellet_scroll_offset - event.y * 20)
                return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Ignore scroll wheel button events (4=scroll up, 5=scroll down)
            # These are handled by MOUSEWHEEL event handler
            if event.button in (4, 5):
                return False
            
            # 0. Check Panel Toggle Buttons (Highest Priority for UI)
            if event.button == 1:
                for panel_name, rect in self.toggle_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        self.panel_states[panel_name] = not self.panel_states.get(panel_name, True)
                        return True
            
            # 1. Check Dilemma Popup Interactions (High Priority)
            if hasattr(battle, 'pending_dilemma') and battle.pending_dilemma:
                # Check Advisor Panel Close
                if self.show_advisor_panel and self.advisor_close_rect:
                    if self.advisor_close_rect.collidepoint(mouse_pos):
                        self.show_advisor_panel = False
                        return True
                
                # Check Ask Advisor Button
                if self.ask_advisor_rect and self.ask_advisor_rect.collidepoint(mouse_pos):
                    self.show_advisor_panel = not self.show_advisor_panel
                    return True
                    
                # Check Dilemma Choices (only if advisor panel is closed)
                if not self.show_advisor_panel:
                    for i, rect in self.dilemma_choice_rects.items():
                        if rect.collidepoint(mouse_pos):
                            # Make choice
                            battle.resolve_dilemma(i)
                            self.show_advisor_panel = False # Reset for next time
                            return True
                
                # Block other clicks while dilemma is active
                return True

            # 2. Check Scientific Toolbar clicks
            if self.tool_rects:
                if event.button == 1: # Left click
                    for tool, rect in self.tool_rects.items():
                        if rect.collidepoint(mouse_pos):
                            print(f"Toolbar clicked! Selected {tool}")
                            if scientific_cursor:
                                scientific_cursor.select_tool(tool)
                                # Clear legacy selection just in case
                                self.selected_tool = None
                            else:
                                print("Scientific cursor is None!")
                            return True

            # 3. Check Controls Panel clicks
            for btn_key, rect in self._control_button_rects.items():
                if rect.collidepoint(mouse_pos):
                    self._pressed_button = btn_key
                    self._pressed_time = pygame.time.get_ticks()
                    
                    # Execute action immediately
                    try:
                        if btn_key == 'spawn_rate_plus':
                            new_rate = min(5.0, getattr(battle, 'resource_spawn_rate', 0.0) + 0.1)
                            battle.resource_spawn_rate = new_rate
                            # Update ResourceManager's spawn rate
                            if hasattr(battle, 'resource_manager'):
                                battle.resource_manager.spawn_rate = new_rate
                        elif btn_key == 'spawn_rate_minus':
                            new_rate = max(0.0, getattr(battle, 'resource_spawn_rate', 0.0) - 0.1)
                            battle.resource_spawn_rate = new_rate
                            # Update ResourceManager's spawn rate
                            if hasattr(battle, 'resource_manager'):
                                battle.resource_manager.spawn_rate = new_rate
                        elif btn_key == 'breed_cd_plus':
                            battle.breeding_cooldown = min(30.0, getattr(battle, 'breeding_cooldown', 20.0) + 1.0)
                        elif btn_key == 'breed_cd_minus':
                            battle.breeding_cooldown = max(1.0, getattr(battle, 'breeding_cooldown', 20.0) - 1.0)
                        elif btn_key == 'spawn_now':
                            if hasattr(battle, 'spawn_resource'):
                                battle.spawn_resource()
                            elif hasattr(battle, '_spawn_resource'):
                                battle._spawn_resource()
                        elif btn_key == 'toggle_pellet_stats':
                            self.show_pellet_stats = not self.show_pellet_stats
                        elif btn_key == 'mut_rate_plus':
                            if hasattr(battle, 'breeding_system'):
                                battle.breeding_system.mutation_rate = min(1.0, getattr(battle.breeding_system, 'mutation_rate', 0.1) + 0.05)
                        elif btn_key == 'mut_rate_minus':
                            if hasattr(battle, 'breeding_system'):
                                battle.breeding_system.mutation_rate = max(0.0, getattr(battle.breeding_system, 'mutation_rate', 0.1) - 0.05)
                        elif btn_key == 'force_weather':
                             if battle.environment:
                                battle.environment._change_weather()
                    except Exception as e:
                        print(f"UI Action Error: {e}")
                    return True

            # 4. Check Genetic Strain Panel clicks
            if self.strain_panel_rect and self.strain_panel_rect.collidepoint(mouse_pos):
                # Check Tabs
                for mode, rect in self.strain_tab_rects.items():
                    if rect.collidepoint(mouse_pos):
                        self.strain_panel_mode = mode
                        self.selected_strain_id = None # Reset selection on tab switch
                        self.strain_scroll_offset = 0
                        return True

                # Check individual strain items
                clicked_strain = None
                for strain_id, rect in self.strain_item_rects.items():
                    if rect.collidepoint(mouse_pos):
                        clicked_strain = strain_id
                        break
                
                if clicked_strain:
                    if self.selected_strain_id == clicked_strain:
                        self.selected_strain_id = None # Deselect
                    else:
                        self.selected_strain_id = clicked_strain
                return True
            
            # 4.5 Check Popup Button Clicks
            if self.selected_strain_id and self._popup_button_rects:
                for action, rect in self._popup_button_rects.items():
                    if rect.collidepoint(mouse_pos):
                        try:
                            if action == "cull":
                                battle.cull_strain(self.selected_strain_id)
                            elif action == "boost":
                                battle.boost_strain_fertility(self.selected_strain_id)
                        except Exception as e:
                            print(f"Popup Action Error: {e}")
                        return True

            # If a strain is selected and user clicks anywhere else (and not on popup), close it
            if self.selected_strain_id:
                # Check if click is inside popup
                sw, sh = screen.get_size() if 'screen' in locals() else pygame.display.get_surface().get_size()
                popup_rect = pygame.Rect((sw - 400)//2, (sh - 500)//2, 400, 500)
                if not popup_rect.collidepoint(mouse_pos):
                    self.selected_strain_id = None
                    self.popup_scroll_offset = 0 # Reset scroll
                return True



        elif event.type == pygame.MOUSEBUTTONUP:
            self._pressed_button = None
            
        elif event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if mouse is over strain panel
            if self.strain_panel_rect and self.strain_panel_rect.collidepoint(mouse_pos):
                # Scroll
                self.strain_scroll_offset -= event.y * 20
                self.strain_scroll_offset = max(0, self.strain_scroll_offset)
                return True
                
            # Check if mouse is over popup (if open)
            if self.selected_strain_id:
                # Simple check: center of screen roughly
                sw, sh = pygame.display.get_surface().get_size()
                popup_rect = pygame.Rect((sw - 400)//2, (sh - 500)//2, 400, 500)
                if popup_rect.collidepoint(mouse_pos):
                    self.popup_scroll_offset -= event.y * 20
                    # Clamp scroll (max calculated in render)
                    max_scroll = max(0, self._popup_content_height - 350) # Approx view height
                    self.popup_scroll_offset = max(0, min(self.popup_scroll_offset, max_scroll))
                    return True
        
        return False
    
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
            if len(self._text_cache) > 300:
                # Clear oldest 100 entries (simple cache management)
                keys_to_remove = list(self._text_cache.keys())[:100]
                for key in keys_to_remove:
                    del self._text_cache[key]
            
            self._text_cache[cache_key] = font.render(text, True, color)
        
        return self._text_cache[cache_key]
    
    def render(self, screen: pygame.Surface, battle: SpatialBattle, paused: bool, scientific_cursor: ScientificCursor = None):
        """
        Render all UI components.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle to display info for
            paused: Whether the game is paused
            scientific_cursor: Optional ScientificCursor instance
        """
        # Clear interactive rects at start of render to avoid stale geometry
        self._control_button_rects = {}

        # Weather panel (top left)
        self._render_weather_panel(screen, battle)
        
        # Biome panel (below weather panel)
        self._render_biome_panel(screen, battle)
        
        # Genetic strains panel (left side, below biome panel)
        self._render_genetic_strains_panel(screen, battle)
        
        # World Stats Panel (Right side, below controls)
        self._render_world_stats_panel(screen, battle)
        
        # Pellet statistics panel (if enabled and pellets exist)
        if self.show_pellet_stats and battle.arena.pellets:
            self._render_pellet_stats_panel(screen, battle)
        
        # Controls panel (interactive knobs) - render last so controls are on top
        try:
            self._render_controls_panel(screen, battle)
        except Exception:
            # Never let UI rendering crash the game
            pass

        # Experiment Overseer Control Panel (Right Side)
        # REMOVED: User requested removal of experimental controls
        # if hasattr(battle, 'overseer') and battle.overseer:
        #     try:
        #         self._render_overseer_panel(screen, battle)
        #     except Exception as e:
        #         print(f"Overseer UI Error: {e}")
        #         pass

        # Event log (bottom)
        self._render_event_log(screen)
        
        # Pause indicator
        if paused:
            self._render_pause_indicator(screen)
        
        # Battle end overlay
        if battle.is_over:
            self._render_battle_end(screen, battle)
            
        # Dilemma Popup (High Priority Overlay)
        if hasattr(battle, 'pending_dilemma') and battle.pending_dilemma:
            self.render_dilemma_popup(screen, battle.pending_dilemma)
            
        # Assistant Panel (Overlay)
        if self.show_advisor_panel:
            self.render_assistant_panel(screen, battle)
            
        # Ethics Dashboard (Overlay)
        if self.show_ethics_dashboard:
            self.render_ethics_dashboard(screen, battle)
            
        # Scientific Toolbar (Always visible)
        self.render_scientific_toolbar(screen, battle, scientific_cursor)



    def _load_tool_icons(self):
        """Load tool icons from assets."""
        import os
        assets_dir = "assets/icons"
        
        icon_map = {
            CursorTool.OBSERVE: "observe.png",
            CursorTool.FOOD_DISPENSER: "dispenser.png",
            CursorTool.STIMULATOR: "stimulator.png",
            CursorTool.MARKER: "marker.png",
            CursorTool.SAMPLER: "sampler.png",
            CursorTool.RELOCATOR: "relocator.png",
            CursorTool.BARRIER: "barrier.png",
            CursorTool.PHEROMONE: "pheromone.png",
            CursorTool.ASTEROID: "asteroid.png",
            CursorTool.APEX: "apex.png"
        }
        
        for tool, filename in icon_map.items():
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                try:
                    image = pygame.image.load(path).convert_alpha()
                    image = pygame.transform.scale(image, (32, 32))
                    self.tool_icons[tool] = image
                except Exception:
                    pass

    def render_scientific_toolbar(self, screen: pygame.Surface, battle: SpatialBattle, scientific_cursor: ScientificCursor = None):
        """
        Render the toolbar for scientific intervention tools.
        
        Args:
            screen: Pygame surface
            battle: Battle instance
            scientific_cursor: Optional ScientificCursor instance
        """
        if not scientific_cursor:
            return

        # Toolbar dimensions
        item_size = 40
        padding = 8
        
        # All tools from ScientificCursor
        tools = [
            CursorTool.OBSERVE, CursorTool.FOOD_DISPENSER, CursorTool.STIMULATOR, CursorTool.MARKER, 
            CursorTool.SAMPLER, CursorTool.RELOCATOR, CursorTool.BARRIER, CursorTool.PHEROMONE, 
            CursorTool.ASTEROID, CursorTool.APEX
        ]
        
        width = len(tools) * (item_size + padding) + padding
        height = item_size + 2 * padding
        x = (screen.get_width() - width) // 2
        y = 10 # Top center
        
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (30, 30, 40, 230), bg_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 120), bg_rect, 2, border_radius=10)
        
        # Energy Bar (Horizontal, to the left of toolbar)
        bar_height = 12
        bar_width = 150
        bar_x = x - bar_width - 15
        bar_y = y + (height - bar_height) // 2  # Center vertically with toolbar
        
        # Bar Background
        pygame.draw.rect(screen, (20, 20, 30), (bar_x, bar_y, bar_width, bar_height), border_radius=6)
        pygame.draw.rect(screen, (60, 60, 70), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=6)
        
        # Bar Fill
        fill_pct = scientific_cursor.tool_charge / scientific_cursor.max_charge
        fill_width = int((bar_width - 4) * fill_pct)
        fill_rect = pygame.Rect(bar_x + 2, bar_y + 2, fill_width, bar_height - 4)
        
        # Color based on charge (Blue -> Cyan)
        bar_color = (0, 150 + int(105 * fill_pct), 255)
        pygame.draw.rect(screen, bar_color, fill_rect, border_radius=4)
        
        # Energy text overlay
        energy_text = f"{int(scientific_cursor.tool_charge)}/{int(scientific_cursor.max_charge)}"
        energy_surf = self.small_font.render(energy_text, True, (255, 255, 255))
        text_x = bar_x + (bar_width - energy_surf.get_width()) // 2
        text_y = bar_y + (bar_height - energy_surf.get_height()) // 2
        screen.blit(energy_surf, (text_x, text_y))
        
        # Tools
        self.tool_rects = {}
        curr_x = x + padding
        
        for tool in tools:
            rect = pygame.Rect(curr_x, y + padding, item_size, item_size)
            self.tool_rects[tool] = rect
            
            # Highlight if selected
            is_selected = (scientific_cursor.current_tool == tool)
            
            # Draw button background
            if is_selected:
                pygame.draw.rect(screen, (100, 200, 255), rect, border_radius=5)
                pygame.draw.rect(screen, (50, 100, 150), rect.inflate(-4, -4), border_radius=5)
            else:
                pygame.draw.rect(screen, (60, 60, 70), rect, border_radius=5)
            
            # Draw Icon
            if tool in self.tool_icons:
                icon = self.tool_icons[tool]
                # Center icon
                icon_rect = icon.get_rect(center=rect.center)
                screen.blit(icon, icon_rect)
            else:
                # Fallback: First letter
                letter = tool.value[0].upper()
                txt = self.title_font.render(letter, True, (200, 200, 200))
                screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
            
            # Tooltip on hover
            mouse_pos = pygame.mouse.get_pos()
            if rect.collidepoint(mouse_pos):
                # Tool Name
                name = scientific_cursor.get_tool_name() if is_selected else tool.value.replace("_", " ").title()
                if tool == CursorTool.FOOD_DISPENSER: name = "Food Dispenser"
                
                tooltip = self.small_font.render(name, True, (255, 255, 255))
                
                # Draw tooltip background
                tt_rect = tooltip.get_rect(midtop=(rect.centerx, rect.bottom + 5))
                bg_tt = tt_rect.inflate(10, 6)
                pygame.draw.rect(screen, (20, 20, 30), bg_tt, border_radius=4)
                pygame.draw.rect(screen, (100, 100, 100), bg_tt, 1, border_radius=4)
                
                screen.blit(tooltip, tt_rect)
            
            curr_x += item_size + padding

    def _render_panel_container(self, screen: pygame.Surface, x: int, y: int, width: int, height: int, title: str, panel_name: str) -> bool:
        """
        Render a generic panel container with a title and collapse toggle.
        
        Args:
            screen: Pygame surface
            x, y, width, height: Panel dimensions (height is fully expanded height)
            title: Panel title text
            panel_name: Key for panel_states dict
            
        Returns:
            bool: True if panel is expanded and content should be rendered, False if collapsed
        """
        is_expanded = self.panel_states.get(panel_name, True)
        
        # Header height
        header_h = 28
        
        # Current height depends on state
        current_h = height if is_expanded else header_h
        
        # Background - Solid dark blue-grey for "Clean" look
        bg_rect = pygame.Rect(x, y, width, current_h)
        # Main panel body
        if is_expanded:
            # Body background
            body_rect = pygame.Rect(x, y + header_h, width, current_h - header_h)
            pygame.draw.rect(screen, (25, 25, 35), body_rect, border_bottom_left_radius=8, border_bottom_right_radius=8)
            pygame.draw.rect(screen, (60, 70, 90), body_rect, 1, border_bottom_left_radius=8, border_bottom_right_radius=8)
        
        # Header Background - Slightly lighter/vibrant
        header_rect = pygame.Rect(x, y, width, header_h)
        header_color = (40, 45, 60)
        
        # Rounded corners for top
        pygame.draw.rect(screen, header_color, header_rect, border_top_left_radius=8, border_top_right_radius=8)
        if not is_expanded:
            # Rounded all around if collapsed
            pygame.draw.rect(screen, header_color, header_rect, border_radius=8)
            
        # Header Border
        pygame.draw.rect(screen, (80, 90, 110), header_rect, 1, border_top_left_radius=8, border_top_right_radius=8)
        if not is_expanded:
             pygame.draw.rect(screen, (80, 90, 110), header_rect, 1, border_radius=8)
            
        # Title - White and crisp
        title_surf = self.small_font.render(title.upper(), True, (220, 230, 255))
        # Center title vertically in header
        screen.blit(title_surf, (x + 28, y + (header_h - title_surf.get_height()) // 2 + 1))
        
        # Toggle Button
        toggle_rect = pygame.Rect(x + 6, y + 6, 16, 16)
        self.toggle_buttons[panel_name] = toggle_rect
        
        # Draw toggle icon (triangle)
        center_x = toggle_rect.centerx
        center_y = toggle_rect.centery
        
        # Icon color
        icon_color = (150, 200, 255)
        
        if is_expanded:
            # Down arrow
            points = [(center_x - 4, center_y - 2), (center_x + 4, center_y - 2), (center_x, center_y + 3)]
        else:
            # Right arrow
            points = [(center_x - 2, center_y - 4), (center_x - 2, center_y + 4), (center_x + 3, center_y)]
            
        pygame.draw.polygon(screen, icon_color, points)
        
        return is_expanded

    def _render_weather_panel(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render weather and time information in the top left.
        """
        if not battle.environment:
            return
            
        x, y = 20, 50 # Moved down slightly to clear toolbar
        width, height = 220, 80
        
        if not self._render_panel_container(screen, x, y, width, height, "Environment", "weather"):
            return
            
        # Content Offset
        content_y = y + 30
        content_x = x + 10
        
        # Get data
        env = battle.environment
        weather = env.weather
        day_night = env.day_night
        
        if not weather:
            return
            
        # Weather Type
        w_type = weather.weather_type.value.title()
        w_color = (200, 200, 255)
        if w_type == "Clear": w_color = (255, 255, 200)
        elif w_type == "Rainy": w_color = (150, 150, 255)
        
        type_surf = self._get_cached_text(f"Weather: {w_type}", self.text_font, w_color)
        screen.blit(type_surf, (content_x, content_y))
        
        # Temp & Humidity
        content_y += 22
        temp_text = f"{weather.temperature:.1f}°C | {weather.humidity*100:.0f}% Hum"
        temp_surf = self._get_cached_text(temp_text, self.small_font, self.text_color)
        screen.blit(temp_surf, (content_x, content_y))
        
        # Time
        content_y += 18
        if day_night:
            hour = day_night.get_current_hour()
            time_str = f"{int(hour):02d}:{int((hour%1)*60):02d}"
            time_surf = self._get_cached_text(f"Time: {time_str}", self.small_font, (255, 255, 200))
            screen.blit(time_surf, (content_x, content_y))

    def _render_biome_panel(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render biome information panel below the weather panel.
        """
        if not battle.environment:
            return
            
        # Position in Top Right (aligned with top margin)
        panel_width = 230
        margin_from_edge = 10
        x = screen.get_width() - panel_width - margin_from_edge
        y = 10

        # Increased height for mini-map
        width, height = 220, 220 
        
        if not self._render_panel_container(screen, x, y, width, height, "Biome Data", "biome"):
            return
            
        content_y = y + 30
        content_x = x + 10
        
        # Biome Info
        # Get biome name from environment
        if hasattr(battle.environment, 'biome_name'):
            biome_name = battle.environment.biome_name
        elif hasattr(battle.environment, 'biome_type'):
            biome_name = str(battle.environment.biome_type)
        else:
            biome_name = "Unknown"
            
        name_surf = self._get_cached_text(f"Biome: {biome_name}", self.text_font, (150, 255, 150))
        screen.blit(name_surf, (content_x, content_y))
        
        # Difficulty
        content_y += 25
        if hasattr(battle.environment, 'difficulty_rating'):
            diff = battle.environment.difficulty_rating
        elif hasattr(battle.environment, 'biome_difficulty'):
            diff = battle.environment.biome_difficulty
        else:
            diff = 5.0
            
        diff_surf = self._get_cached_text(f"Difficulty: {diff:.1f}/10", self.small_font, (255, 200, 200))
        screen.blit(diff_surf, (content_x, content_y))
        
        # Resources
        content_y += 20
        res_count = len(battle.arena.resources)
        res_surf = self._get_cached_text(f"Resources: {res_count}", self.small_font, (200, 255, 200))
        screen.blit(res_surf, (content_x, content_y))
        
        # Mini-map
        content_y += 25
        map_size = 140
        map_x = x + (width - map_size) // 2
        map_y = content_y
        
        # Draw map background
        pygame.draw.rect(screen, (0, 0, 0), (map_x, map_y, map_size, map_size))
        pygame.draw.rect(screen, (100, 100, 100), (map_x-1, map_y-1, map_size+2, map_size+2), 1)
        
        if battle.environment.terrain_grid:
            from ..models.environment import TerrainType
            colors = {
                TerrainType.GRASS: (34, 139, 34),
                TerrainType.ROCKY: (128, 128, 128),
                TerrainType.WATER: (65, 105, 225),
                TerrainType.FOREST: (0, 100, 0),
                TerrainType.DESERT: (210, 180, 140),
                TerrainType.MARSH: (47, 79, 79)
            }
            
            # Calculate scale
            arena_w = battle.arena.width
            arena_h = battle.arena.height
            scale_x = map_size / arena_w
            scale_y = map_size / arena_h
            
            cell_size = battle.environment.cell_size
            pixel_w = max(1, int(cell_size * scale_x))
            pixel_h = max(1, int(cell_size * scale_y))
            
            # Draw terrain cells
            for (col, row), cell in battle.environment.terrain_grid.items():
                cx = map_x + int(cell.position.x * scale_x)
                cy = map_y + int(cell.position.y * scale_y)
                
                color = colors.get(cell.terrain_type, (50, 50, 50))
                pygame.draw.rect(screen, color, (cx, cy, pixel_w, pixel_h))
                
            # Draw camera viewport rect
            # We need camera info here, but UI render method usually has access to it?
            # The render signature is: render(self, screen, battle, paused, scientific_cursor=None)
            # It doesn't have camera! We need to pass camera to render if we want this.
            # For now, skip viewport rect or find a way to get it.
            # Actually, we can't easily get camera here without changing signature.
            # Let's skip viewport rect for now to avoid breaking API.
            pass

    def _render_genetic_strains_panel(
        self,
        screen: pygame.Surface,
        battle: SpatialBattle
    ):
        """
        Render a panel showing population by genetic strain OR disease strain.
        
        Positioned in the left margin, below the biome panel.
        """
        panel_width = 230
        
        # Dynamic Y position based on Weather panel only (Biome moved to right)
        weather_expanded = self.panel_states.get('weather', True)
        weather_h = 80 if weather_expanded else 28
        
        margin_from_edge = 10
        panel_y = 50 + weather_h + 10
        
        # Battle feed height is 190, plus 5px margin from bottom
        bottom_margin = 200 
        screen_height = screen.get_height()
        
        # Calculate available height
        available_height = screen_height - panel_y - bottom_margin - 10 # 10px buffer
        panel_height = max(200, available_height) # Minimum 200px
        
        # Position in left margin area
        panel_x = margin_from_edge
        
        # Update panel rect for input handling (used for scrolling)
        # Note: This rect covers the whole area, but we only care if expanded
        self.strain_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        if not self._render_panel_container(screen, panel_x, panel_y, panel_width, panel_height, "Populations", "genetic"):
            # If collapsed, we don't render tabs or content
            # But we should clear interactive rects that might be stale
            self.strain_tab_rects = {}
            self.strain_item_rects = {}
            return
        
        # --- TABS ---
        # Offset content by header height
        header_h = 25
        tab_y = panel_y + header_h + 5
        
        tab_height = 30
        tab_width = panel_width // 4  # Changed to 4 tabs for NEURAL
        
        # Genetic Tab
        gen_tab_rect = pygame.Rect(panel_x, tab_y, tab_width, tab_height)
        self.strain_tab_rects["GENETIC"] = gen_tab_rect
        gen_color = (60, 60, 80) if self.strain_panel_mode == "GENETIC" else (40, 40, 50)
        pygame.draw.rect(screen, gen_color, gen_tab_rect, border_top_left_radius=8)
        
        gen_text = self.small_font.render("GENES", True, (200, 200, 255) if self.strain_panel_mode == "GENETIC" else (150, 150, 150))
        screen.blit(gen_text, (gen_tab_rect.centerx - gen_text.get_width()//2, gen_tab_rect.centery - gen_text.get_height()//2))
        
        # Disease Tab
        dis_tab_rect = pygame.Rect(panel_x + tab_width, tab_y, tab_width, tab_height)
        self.strain_tab_rects["DISEASE"] = dis_tab_rect
        dis_color = (80, 40, 40) if self.strain_panel_mode == "DISEASE" else (50, 30, 30)
        pygame.draw.rect(screen, dis_color, dis_tab_rect)
        
        dis_text = self.small_font.render("VIRUS", True, (255, 150, 150) if self.strain_panel_mode == "DISEASE" else (150, 100, 100))
        screen.blit(dis_text, (dis_tab_rect.centerx - dis_text.get_width()//2, dis_tab_rect.centery - dis_text.get_height()//2))

        # Pellet Tab
        pel_tab_rect = pygame.Rect(panel_x + tab_width * 2, tab_y, tab_width, tab_height)
        self.strain_tab_rects["PELLETS"] = pel_tab_rect
        pel_color = (40, 80, 40) if self.strain_panel_mode == "PELLETS" else (30, 50, 30)
        pygame.draw.rect(screen, pel_color, pel_tab_rect, border_top_right_radius=8)
        
        pel_text = self.small_font.render("FOOD", True, (150, 255, 150) if self.strain_panel_mode == "PELLETS" else (100, 150, 100))
        screen.blit(pel_text, (pel_tab_rect.centerx - pel_text.get_width()//2, pel_tab_rect.centery - pel_text.get_height()//2))
        
        # Neural Tab (NEW)
        neu_tab_rect = pygame.Rect(panel_x + tab_width * 3, tab_y, tab_width, tab_height)
        self.strain_tab_rects["NEURAL"] = neu_tab_rect
        neu_color = (40, 60, 80) if self.strain_panel_mode == "NEURAL" else (30, 40, 50)
        pygame.draw.rect(screen, neu_color, neu_tab_rect, border_top_right_radius=8)
        
        neu_text = self.small_font.render("BRAIN", True, (150, 200, 255) if self.strain_panel_mode == "NEURAL" else (100, 130, 150))
        screen.blit(neu_text, (neu_tab_rect.centerx - neu_text.get_width()//2, neu_tab_rect.centery - neu_text.get_height()//2))
        
        # Highlight active tab bottom
        if self.strain_panel_mode == "GENETIC":
            pygame.draw.line(screen, (100, 100, 255), gen_tab_rect.bottomleft, gen_tab_rect.bottomright, 2)
        elif self.strain_panel_mode == "DISEASE":
            pygame.draw.line(screen, (255, 100, 100), dis_tab_rect.bottomleft, dis_tab_rect.bottomright, 2)
        else:
            pygame.draw.line(screen, (100, 255, 100), pel_tab_rect.bottomleft, pel_tab_rect.bottomright, 2)

        # Content area definition
        content_y_start = tab_y + tab_height + 10
        content_height = panel_height - header_h - 5 - tab_height - 35 # Reserve space for footer
        content_rect = pygame.Rect(panel_x, content_y_start, panel_width, content_height)
        
        # Clip rendering to content area
        original_clip = screen.get_clip()
        screen.set_clip(content_rect)
        
        # Clear item rects for this frame
        self.strain_item_rects = {}
        
        if self.strain_panel_mode == "GENETIC":
            self._render_genetic_list(screen, battle, panel_x, content_y_start, content_height, content_rect)
        elif self.strain_panel_mode == "DISEASE":
            self._render_disease_list(screen, battle, panel_x, content_y_start, content_height, content_rect)
        elif self.strain_panel_mode == "PELLETS":
            self._render_pellet_list(screen, battle, panel_x, content_y_start, content_height, content_rect)
        else:  # NEURAL
            self._render_neural_patterns(screen, battle, panel_x, content_y_start, content_height, content_rect)
            
        # Restore clip
        screen.set_clip(original_clip)
        
        # Footer (Total Count)
        footer_y = panel_y + panel_height - 25
        if self.strain_panel_mode == "GENETIC":
            total_alive = sum(1 for c in battle.creatures if c.is_alive())
            total_text = f"Total Alive: {total_alive}/{len(battle.creatures)}"
            color = (200, 255, 200)
        elif self.strain_panel_mode == "DISEASE":
            infected_count = sum(1 for c in battle.creatures if c.is_alive() and c.creature.active_infection)
            total_text = f"Total Infected: {infected_count}"
            color = (255, 150, 150)
        elif self.strain_panel_mode == "PELLETS":
            total_pellets = len(battle.arena.pellets)
            total_text = f"Total Pellets: {total_pellets}"
            color = (150, 255, 150)
        else:  # NEURAL
            brain_count = sum(1 for c in battle.creatures if c.is_alive() and hasattr(c.creature, 'brain') and c.creature.brain)
            total_text = f"Total Brains: {brain_count}"
            color = (150, 200, 255)
            
        total_surface = self.small_font.render(total_text, True, color)
        screen.blit(total_surface, (panel_x + 10, footer_y))
        
        # Render Details Popup if a strain is selected
        if self.selected_strain_id:
            if self.strain_panel_mode == "GENETIC":
                self._render_strain_details_popup(screen, battle)
            elif self.strain_panel_mode == "DISEASE":
                self._render_disease_details_popup(screen, battle)
            elif self.strain_panel_mode == "PELLETS":
                self._render_pellet_details_popup(screen, battle)
    
    def _render_genetic_list(self, screen, battle, panel_x, content_y_start, content_height, content_rect):
        """Render the list of genetic strains."""
        panel_width = 230
        
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
        
        # Calculate total content height
        item_height = 24
        total_items = len(sorted_strains)
        total_content_height = total_items * item_height
        
        # Clamp scroll offset
        max_scroll = max(0, total_content_height - content_height)
        self.strain_scroll_offset = max(0, min(self.strain_scroll_offset, max_scroll))
        
        current_y = content_y_start - self.strain_scroll_offset
        
        for strain_id, creatures in sorted_strains:
            # Optimization: Skip if completely above or below view
            if current_y + item_height < content_y_start:
                current_y += item_height
                continue
            if current_y > content_y_start + content_height:
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
            
            # Highlight if selected
            is_selected = (strain_id == self.selected_strain_id)
            item_rect = pygame.Rect(panel_x + 5, current_y, panel_width - 10, item_height - 2)
            
            # Store rect for click detection (screen coordinates)
            if content_rect.colliderect(item_rect):
                 self.strain_item_rects[strain_id] = item_rect
            
            if is_selected:
                pygame.draw.rect(screen, (60, 60, 80), item_rect, border_radius=4)
                pygame.draw.rect(screen, strain_color, item_rect, 1, border_radius=4)
            
            # Hover effect
            mouse_pos = pygame.mouse.get_pos()
            if item_rect.collidepoint(mouse_pos):
                 pygame.draw.rect(screen, (50, 50, 60), item_rect, border_radius=4)

            # Draw color indicator
            pygame.draw.circle(
                screen,
                strain_color,
                (panel_x + 20, current_y + item_height//2),
                6
            )
            
            # Strain info
            strain_text = f"Strain {strain_id[:6]}"
            text_color = (255, 255, 200) if is_selected else self.text_color
                
            text_surface = self.small_font.render(strain_text, True, text_color)
            screen.blit(text_surface, (panel_x + 35, current_y + 4))
            
            # Population count
            count_text = f"{alive_count}/{total_count}"
            count_surface = self.small_font.render(count_text, True, (200, 200, 200))
            screen.blit(count_surface, (panel_x + panel_width - 50, current_y + 4))
            
            current_y += item_height

        # Draw Scrollbar if needed
        if total_content_height > content_height:
            self._render_scrollbar(screen, panel_x, panel_width, content_y_start, content_height, total_content_height)

    def _render_disease_list(self, screen, battle, panel_x, content_y_start, content_height, content_rect):
        """Render the list of active disease strains."""
        panel_width = 230
        
        # Group infections by disease ID
        disease_groups = {}
        for creature in battle.creatures:
            if creature.is_alive() and creature.creature.active_infection:
                disease = creature.creature.active_infection.disease
                d_id = disease.disease_id
                if d_id not in disease_groups:
                    disease_groups[d_id] = {
                        'disease': disease,
                        'count': 0
                    }
                disease_groups[d_id]['count'] += 1
        
        # Sort by infected count
        sorted_diseases = sorted(
            disease_groups.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        # Calculate total content height
        item_height = 30 # Taller for disease info
        total_items = len(sorted_diseases)
        total_content_height = total_items * item_height
        
        # Clamp scroll offset
        max_scroll = max(0, total_content_height - content_height)
        self.strain_scroll_offset = max(0, min(self.strain_scroll_offset, max_scroll))
        
        current_y = content_y_start - self.strain_scroll_offset
        
        for d_id, data in sorted_diseases:
            disease = data['disease']
            count = data['count']
            
            # Optimization: Skip if completely above or below view
            if current_y + item_height < content_y_start:
                current_y += item_height
                continue
            if current_y > content_y_start + content_height:
                break
            
            # Highlight if selected
            is_selected = (d_id == self.selected_strain_id)
            item_rect = pygame.Rect(panel_x + 5, current_y, panel_width - 10, item_height - 2)
            
            # Store rect
            if content_rect.colliderect(item_rect):
                 self.strain_item_rects[d_id] = item_rect
            
            # Background
            bg_color = (60, 30, 30) if is_selected else (40, 20, 20)
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=4)
            
            if is_selected:
                pygame.draw.rect(screen, (255, 100, 100), item_rect, 1, border_radius=4)
            
            # Hover effect
            
            # Stats Bar (Virulence/Lethality)
            # Just a visual indicator of how dangerous it is
            danger_score = (disease.transmission_rate * 10) + (disease.mortality_rate * 20) + (disease.hp_drain_rate * 5)
            danger_pct = min(1.0, danger_score / 10.0)
            
            # Hover effect
            mouse_pos = pygame.mouse.get_pos()
            if item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (60, 40, 40), item_rect, border_radius=4)
            
            # Disease Name
            disease_name = disease.name if hasattr(disease, 'name') else f"Disease {d_id[:8]}"
            name_color = (255, 200, 200) if is_selected else (255, 150, 150)
            name_surface = self.small_font.render(disease_name, True, name_color)
            screen.blit(name_surface, (panel_x + 10, current_y + 2))
            
            # Infected count
            count_text = f"{count} infected"
            count_surface = self.small_font.render(count_text, True, (200, 150, 150))
            screen.blit(count_surface, (panel_x + panel_width - 80, current_y + 2))
            
            # Stats Bar (Virulence/Lethality) - visual indicator of danger
            bar_width = 100
            bar_height = 4
            bar_x = panel_x + 10
            bar_y = current_y + 20
            
            pygame.draw.rect(screen, (50, 30, 30), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (255, 50, 50), (bar_x, bar_y, int(bar_width * danger_pct), bar_height))
            
            
            current_y += item_height

        # Draw Scrollbar if needed
        if total_content_height > content_height:
            self._render_scrollbar(screen, panel_x, panel_width, content_y_start, content_height, total_content_height)

    def _render_scrollbar(self, screen, panel_x, panel_width, content_y_start, content_height, total_content_height):
        """Helper to render scrollbar."""
        max_scroll = max(0, total_content_height - content_height)
        scrollbar_width = 6
        scrollbar_height = content_height * (content_height / total_content_height)
        scrollbar_x = panel_x + panel_width - 8
        
        # Calculate scrollbar y position
        scroll_ratio = self.strain_scroll_offset / max_scroll if max_scroll > 0 else 0
        scrollbar_y = content_y_start + scroll_ratio * (content_height - scrollbar_height)
        
        pygame.draw.rect(screen, (60, 60, 70), (scrollbar_x, content_y_start, scrollbar_width, content_height), border_radius=3)
        pygame.draw.rect(screen, (150, 150, 150), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), border_radius=3)

    def _render_pellet_list(self, screen, battle, panel_x, content_y_start, content_height, content_rect):
        """Render the list of pellet strains."""
        panel_width = 230
        
        # Group pellets by strain
        strain_groups = {}
        for pellet in battle.arena.pellets:
            strain_id = getattr(pellet, 'strain_id', 'unknown')
            if strain_id not in strain_groups:
                strain_groups[strain_id] = []
            strain_groups[strain_id].append(pellet)
        
        # Sort by population size
        sorted_strains = sorted(
            strain_groups.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        # Calculate total content height
        item_height = 24
        total_items = len(sorted_strains)
        total_content_height = total_items * item_height
        
        # Clamp scroll offset
        max_scroll = max(0, total_content_height - content_height)
        self.strain_scroll_offset = max(0, min(self.strain_scroll_offset, max_scroll))
        
        current_y = content_y_start - self.strain_scroll_offset
        
        for strain_id, pellets in sorted_strains:
            # Optimization: Skip if completely above or below view
            if current_y + item_height < content_y_start:
                current_y += item_height
                continue
            if current_y > content_y_start + content_height:
                break
                
            count = len(pellets)
            
            # Calculate average stats
            avg_nutrition = sum(p.traits.nutritional_value for p in pellets) / count
            avg_growth = sum(p.traits.growth_rate for p in pellets) / count
            
            # Determine display color (average of pellets)
            r = sum(p.traits.color[0] for p in pellets) // count
            g = sum(p.traits.color[1] for p in pellets) // count
            b = sum(p.traits.color[2] for p in pellets) // count
            strain_color = (r, g, b)
            
            # Highlight if selected
            is_selected = (strain_id == self.selected_strain_id)
            item_rect = pygame.Rect(panel_x + 5, current_y, panel_width - 10, item_height - 2)
            
            # Store rect for click detection
            if content_rect.colliderect(item_rect):
                 self.strain_item_rects[strain_id] = item_rect
            
            if is_selected:
                pygame.draw.rect(screen, (40, 60, 40), item_rect, border_radius=4)
                pygame.draw.rect(screen, strain_color, item_rect, 1, border_radius=4)
            
            # Hover effect
            mouse_pos = pygame.mouse.get_pos()
            if item_rect.collidepoint(mouse_pos):
                 pygame.draw.rect(screen, (30, 50, 30), item_rect, border_radius=4)

            # Draw color indicator
            pygame.draw.circle(
                screen,
                strain_color,
                (panel_x + 15, current_y + item_height//2),
                6
            )
            
            # Draw Text
            # Name based on generation/stats
            gen = pellets[0].generation if pellets else 0
            name = f"Strain G{gen}"
            
            text_surf = self.small_font.render(name, True, (200, 255, 200))
            screen.blit(text_surf, (panel_x + 30, current_y + 4))
            
            # Count
            count_text = f"{count}"
            count_surf = self.small_font.render(count_text, True, (150, 150, 150))
            screen.blit(count_surf, (panel_x + panel_width - 30 - count_surf.get_width(), current_y + 4))
            
            # Nutrition bar (mini)
            bar_width = 40
            bar_height = 4
            bar_x = panel_x + panel_width - 80
            bar_y = current_y + 14
            
            # Nutrition (Green)
            nut_pct = min(1.0, avg_nutrition / 100.0)
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (100, 255, 100), (bar_x, bar_y, bar_width * nut_pct, bar_height))
            
            current_y += item_height
            
        # Draw scrollbar if needed
        if total_content_height > content_height:
            self._render_scrollbar(screen, panel_x, panel_width, content_y_start, content_height, total_content_height)

    def _render_neural_patterns(self, screen, battle, panel_x, content_y_start, content_height, content_rect):
        """Render neural network population statistics."""
        panel_width = 230
        
        # Get brain statistics
        if not hasattr(battle, 'brain_stats'):
            # Brain stats system not initialized
            no_data_text = "Brain stats not initialized"
            surf = self.small_font.render(no_data_text, True, (255, 100, 100))
            screen.blit(surf, (panel_x + 10, content_y_start + 10))
            return
            
        if not battle.brain_stats.last_analysis:
            # No data yet - waiting for first analysis
            no_data_text = "Analyzing brains..."
            surf = self.small_font.render(no_data_text, True, (150, 150, 150))
            screen.blit(surf, (panel_x + 10, content_y_start + 10))
            
            # Show time until next analysis
            time_left = 2.0 - (battle.current_time - battle.last_brain_analysis)
            if time_left > 0:
                time_text = f"Next update in {time_left:.1f}s"
                time_surf = self.small_font.render(time_text, True, (100, 100, 100))
                screen.blit(time_surf, (panel_x + 10, content_y_start + 30))
            return
        
        stats = battle.brain_stats.last_analysis
        
        y = content_y_start
        x = panel_x + 10
        
        # Brain count
        brain_text = f"Brains: {stats['total_brains']}"
        surf = self.small_font.render(brain_text, True, (150, 200, 255))
        screen.blit(surf, (x, y))
        y += 25
        
        # Popular Strategies (bar charts)
        strategies_title = "POPULAR STRATEGIES"
        title_surf = self.small_font.render(strategies_title, True, (100, 150, 255))
        screen.blit(title_surf, (x, y))
        y += 20
        
        for strategy in stats['popular_strategies']:
            action = strategy['action']
            pct = strategy['percentage']
            
            # Action name
            action_surf = self.small_font.render(action, True, (200, 200, 200))
            screen.blit(action_surf, (x, y))
            
            # Bar
            bar_x = x + 60
            bar_width = 120
            bar_height = 10
            
            # Background
            pygame.draw.rect(screen, (30, 30, 40), (bar_x, y + 2, bar_width, bar_height))
            
            # Fill
            fill_width = int(bar_width * pct)
            bar_color = (100, 150, 255)
            if action == 'EAT': bar_color = (100, 255, 100)
            elif action == 'FLEE': bar_color = (255, 200, 100)
            elif action == 'FIGHT': bar_color = (255, 100, 100)
            
            pygame.draw.rect(screen, bar_color, (bar_x, y + 2, fill_width, bar_height))
            
            # Percentage
            pct_text = f"{int(pct*100)}%"
            pct_surf = self.small_font.render(pct_text, True, (150, 150, 150))
            screen.blit(pct_surf, (bar_x + bar_width + 5, y))
            
            y += 18
        
        y += 10
        
        # Brain Statistics
        stats_title = "BRAIN STATS"
        title_surf = self.small_font.render(stats_title, True, (255, 200, 100))
        screen.blit(title_surf, (x, y))
        y += 20
        
        # Learning rate
        lr_text = f"Avg Learning: {stats['avg_learning_rate']:.2f}"
        surf = self.small_font.render(lr_text, True, (200, 200, 200))
        screen.blit(surf, (x, y))
        y += 18
        
        # Diversity
        div_text = f"Diversity: {int(stats['brain_diversity']*100)}%"
        surf = self.small_font.render(div_text, True, (200, 200, 200))
        screen.blit(surf, (x, y))
        y += 18
        
        # Intelligent count
        int_text = f"Intelligent: {stats['intelligent_count']}"
        surf = self.small_font.render(int_text, True, (200, 200, 200))
        screen.blit(surf, (x, y))


    def _render_strain_details_popup(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render detailed information popup for the selected strain.
        
        Shows comprehensive strain statistics, traits, and lineage data.
        """
        if not self.selected_strain_id:
            return
        
        # Find all creatures in this strain
        strain_creatures = [
            c for c in battle.creatures 
            if c.creature.strain_id == self.selected_strain_id
        ]
        
        if not strain_creatures:
            return
        
        # Calculate popup dimensions and position
        popup_width = 400
        popup_height = 500
        popup_x = (screen.get_width() - popup_width) // 2
        popup_y = (screen.get_height() - popup_height) // 2
        
        # Semi-transparent background overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 150), pygame.Rect(0, 0, screen.get_width(), screen.get_height()))
        screen.blit(overlay, (0, 0))
        
        # Popup background
        popup_surface = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        pygame.draw.rect(popup_surface, (20, 25, 35, 250), pygame.Rect(0, 0, popup_width, popup_height), border_radius=12)
        pygame.draw.rect(popup_surface, (100, 150, 200), pygame.Rect(0, 0, popup_width, popup_height), 2, border_radius=12)
        screen.blit(popup_surface, (popup_x, popup_y))
        
        # Calculate strain statistics
        alive = [c for c in strain_creatures if c.is_alive()]
        total = len(strain_creatures)
        mature = [c for c in alive if c.creature.mature]
        
        # Calculate average hue and color
        if alive:
            avg_hue = sum(c.creature.hue for c in alive) / len(alive)
            import colorsys
            rgb = colorsys.hsv_to_rgb(avg_hue / 360.0, 0.8, 0.9)
            strain_color = tuple(int(255 * x) for x in rgb)
        else:
            avg_hue = 0
            strain_color = (100, 100, 100)
        
        # Get generation info
        generations = [c.creature.generation for c in strain_creatures if hasattr(c.creature, 'generation')]
        if generations:
            oldest_gen = min(generations)
            newest_gen = max(generations)
            gen_depth = newest_gen - oldest_gen + 1
        else:
            oldest_gen = newest_gen = gen_depth = 0
        
        # Collect common traits
        all_traits = []
        for c in alive:
            all_traits.extend([t.name for t in c.creature.traits])
        
        from collections import Counter
        common_traits = Counter(all_traits).most_common(5)
        
        # Render content
        x = popup_x + 20
        y = popup_y + 20
        
        # Header with strain color indicator
        header_text = "STRAIN DETAILS"
        header_surf = self._get_cached_text(header_text, self.text_font, (150, 200, 255))
        screen.blit(header_surf, (x + (popup_width - 40 - header_surf.get_width()) // 2, y))
        
        # Draw large color indicator
        pygame.draw.circle(screen, strain_color, (popup_x + popup_width - 40, popup_y + 35), 15)
        pygame.draw.circle(screen, (255, 255, 255), (popup_x + popup_width - 40, popup_y + 35), 15, 2)
        
        y += 40
        
        # Strain ID (shortened)
        strain_id_short = self.selected_strain_id[:8] + "..."
        id_text = f"ID: {strain_id_short}"
        id_surf = self._get_cached_text(id_text, self.small_font, (150, 150, 150))
        screen.blit(id_surf, (x, y))
        y += 25
        
        # Divider
        pygame.draw.line(screen, (80, 100, 120), (x, y), (popup_x + popup_width - 20, y), 1)
        y += 10
        
        # --- Scrollable Content Area ---
        content_rect = pygame.Rect(x, y, popup_width - 40, 350)
        # Clip to content area
        original_clip = screen.get_clip()
        screen.set_clip(content_rect)
        
        # Start drawing content at offset
        content_y = y - self.popup_scroll_offset
        start_y = content_y # To calculate total height later
        
        # Population Statistics
        section_title = "POPULATION"
        title_surf = self._get_cached_text(section_title, self.text_font, (100, 255, 150))
        screen.blit(title_surf, (x, content_y))
        content_y += 25
        
        stats = [
            f"Alive: {len(alive)} / {total}",
            f"Mature: {len(mature)}",
            f"Status: {'THRIVING' if len(alive) > 5 else 'EXTINCT' if len(alive) == 0 else 'ENDANGERED'}"
        ]
        
        for stat in stats:
            stat_surf = self._get_cached_text(stat, self.small_font, (200, 200, 200))
            screen.blit(stat_surf, (x + 10, content_y))
            content_y += 20
        
        content_y += 10
        
        # Lineage Information
        section_title = "LINEAGE"
        title_surf = self._get_cached_text(section_title, self.text_font, (255, 200, 100))
        screen.blit(title_surf, (x, content_y))
        content_y += 25
        
        lineage_stats = [
            f"Generation Depth: {gen_depth}",
            f"Oldest Gen: {oldest_gen}",
            f"Newest Gen: {newest_gen}",
            f"Avg Color Hue: {int(avg_hue)}°"
        ]
        
        for stat in lineage_stats:
            stat_surf = self._get_cached_text(stat, self.small_font, (200, 200, 200))
            screen.blit(stat_surf, (x + 10, content_y))
            content_y += 20
        
        content_y += 10
        
        # Detailed Stats (New)
        if alive:
            section_title = "AVERAGE STATS"
            title_surf = self._get_cached_text(section_title, self.text_font, (100, 200, 255))
            screen.blit(title_surf, (x, content_y))
            content_y += 25
            
            avg_hp = sum(c.creature.stats.max_hp for c in alive) / len(alive)
            avg_speed = sum(c.creature.stats.speed for c in alive) / len(alive)
            avg_size = sum(c.spatial.radius for c in alive) / len(alive)
            avg_attack = sum(c.creature.stats.attack for c in alive) / len(alive)
            
            detailed_stats = [
                f"Max HP: {avg_hp:.1f}",
                f"Speed: {avg_speed:.1f}",
                f"Size: {avg_size:.2f}",
                f"Attack: {avg_attack:.1f}"
            ]
            
            for stat in detailed_stats:
                stat_surf = self._get_cached_text(stat, self.small_font, (200, 200, 200))
                screen.blit(stat_surf, (x + 10, content_y))
                content_y += 20
            
            content_y += 10
        
        # Common Traits
        if common_traits and alive:
            section_title = "COMMON TRAITS"
            title_surf = self._get_cached_text(section_title, self.text_font, (255, 150, 255))
            screen.blit(title_surf, (x, content_y))
            content_y += 25
            
            for trait, count in common_traits:
                pct = int((count / len(alive)) * 100)
                trait_text = f"{trait} ({pct}%)"
                self._draw_text(screen, trait_text, x + 10, content_y, (220, 220, 220))
                content_y += 20
                
        content_y += 20
        
        # Actions Section
        section_title = "ACTIONS"
        title_surf = self._get_cached_text(section_title, self.text_font, (255, 100, 100))
        screen.blit(title_surf, (x, content_y))
        content_y += 30
        
        # Action Buttons
        self._popup_button_rects = {}
        
        # Cull Button
        cull_rect = pygame.Rect(x + 10, content_y, 140, 30)
        # Store rect relative to screen, but check visibility
        if content_rect.colliderect(cull_rect):
            self._popup_button_rects["cull"] = cull_rect
            
            # Draw button
            mouse_pos = pygame.mouse.get_pos()
            color = (150, 50, 50) if cull_rect.collidepoint(mouse_pos) else (100, 30, 30)
            pygame.draw.rect(screen, color, cull_rect, border_radius=5)
            pygame.draw.rect(screen, (200, 50, 50), cull_rect, 1, border_radius=5)
            
            btn_text = self.small_font.render("Cull 50%", True, (255, 200, 200))
            screen.blit(btn_text, (cull_rect.centerx - btn_text.get_width()//2, cull_rect.centery - btn_text.get_height()//2))
            
        # Boost Button
        boost_rect = pygame.Rect(x + 170, content_y, 140, 30)
        if content_rect.colliderect(boost_rect):
            self._popup_button_rects["boost"] = boost_rect
            
            # Draw button
            mouse_pos = pygame.mouse.get_pos()
            color = (50, 150, 50) if boost_rect.collidepoint(mouse_pos) else (30, 100, 30)
            pygame.draw.rect(screen, color, boost_rect, border_radius=5)
            pygame.draw.rect(screen, (50, 200, 50), boost_rect, 1, border_radius=5)
            
            btn_text = self.small_font.render("Boost Fertility", True, (200, 255, 200))
            screen.blit(btn_text, (boost_rect.centerx - btn_text.get_width()//2, boost_rect.centery - btn_text.get_height()//2))
            
        content_y += 40
        
        # Calculate total height for scrolling
        self._popup_content_height = content_y - start_y
        
        # Restore clip
        screen.set_clip(original_clip)
        
        # Draw Scrollbar if needed
        if self._popup_content_height > content_rect.height:
            scrollbar_width = 6
            scrollbar_height = content_rect.height * (content_rect.height / self._popup_content_height)
            scrollbar_x = x + content_rect.width - 8
            
            max_scroll = self._popup_content_height - content_rect.height
            scroll_ratio = self.popup_scroll_offset / max_scroll if max_scroll > 0 else 0
            scrollbar_y = content_rect.y + scroll_ratio * (content_rect.height - scrollbar_height)
            
            pygame.draw.rect(screen, (60, 60, 70), (scrollbar_x, content_rect.y, scrollbar_width, content_rect.height), border_radius=3)
            pygame.draw.rect(screen, (150, 150, 150), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), border_radius=3)
        
        # Close instruction
        close_text = "Click outside to close"
        close_surf = self._get_cached_text(close_text, self.small_font, (150, 150, 150))
        screen.blit(close_surf, (popup_x + (popup_width - close_surf.get_width()) // 2, popup_y + popup_height - 25))

    def _render_disease_details_popup(self, screen: pygame.Surface, battle: SpatialBattle):
        """Render details for selected disease strain."""
        if not self.selected_strain_id:
            return
            
        # Find disease instance (any will do as they share static properties, but we need dynamic ones too)
        # Actually, we need to aggregate stats from all infected creatures
        infected_creatures = [
            c for c in battle.creatures 
            if c.is_alive() and c.creature.active_infection and c.creature.active_infection.disease.disease_id == self.selected_strain_id
        ]
        
        if not infected_creatures:
            return
            
        disease = infected_creatures[0].creature.active_infection.disease
        
        # Calculate popup dimensions
        popup_width = 400
        popup_height = 450
        popup_x = (screen.get_width() - popup_width) // 2
        popup_y = (screen.get_height() - popup_height) // 2
        
        # Draw Popup Background
        self._draw_popup_background(screen, popup_x, popup_y, popup_width, popup_height, (40, 20, 20, 250), (200, 100, 100))
        
        x = popup_x + 20
        y = popup_y + 20
        
        # Title
        title_text = f"Virus: {disease.name}"
        title_surf = self._get_cached_text(title_text, self.title_font, (255, 100, 100))
        screen.blit(title_surf, (x, y))
        y += 40
        
        # Stats Section
        self._draw_section_title(screen, "EPIDEMIOLOGY", x, y, (255, 200, 200))
        y += 25
        
        stats = [
            f"Active Cases: {len(infected_creatures)}",
            f"Generation: {getattr(disease, 'generation', 0)}",
            f"Strain ID: {disease.disease_id[:8]}"
        ]
        
        for stat in stats:
            self._draw_text(screen, stat, x + 10, y, (220, 220, 220))
            y += 20
            
        y += 15
        
        # Traits Section
        self._draw_section_title(screen, "VIRAL TRAITS", x, y, (255, 150, 150))
        y += 25
        
        traits = [
            f"Transmission Rate: {disease.transmission_rate:.2f}",
            f"Virulence (Dmg): {disease.hp_drain_rate:.2f}/sec",
            f"Lethality (Mortality): {disease.mortality_rate:.3f}",
            f"Incubation Period: {disease.incubation_time:.1f}s",
            f"Mutation Chance: {disease.mutation_chance:.2f}"
        ]
        
        for trait in traits:
            self._draw_text(screen, trait, x + 10, y, (220, 220, 220))
            y += 20
            
        y += 15
        
        # Description/Type
        self._draw_section_title(screen, "PATHOLOGY", x, y, (200, 200, 255))
        y += 25
        
        desc = "A rapidly evolving pathogen." # Placeholder
        if disease.name == "Plague":
            desc = "Highly infectious, moderate lethality."
        elif disease.name == "Wasting Sickness":
            desc = "Causes rapid energy loss and starvation."
            
        self._draw_text(screen, desc, x + 10, y, (200, 200, 200))
        
    def _render_pellet_details_popup(self, screen: pygame.Surface, battle: SpatialBattle):
        """Render details for selected pellet strain."""
        if not self.selected_strain_id:
            return
            
        # Find pellets
        strain_pellets = [
            p for p in battle.arena.pellets
            if getattr(p, 'strain_id', None) == self.selected_strain_id
        ]
        
        if not strain_pellets:
            return
            
        # Aggregate stats
        count = len(strain_pellets)
        avg_nut = sum(p.traits.nutritional_value for p in strain_pellets) / count
        avg_growth = sum(p.traits.growth_rate for p in strain_pellets) / count
        avg_tox = sum(p.traits.toxicity for p in strain_pellets) / count
        
        # Color
        r = sum(p.traits.color[0] for p in strain_pellets) // count
        g = sum(p.traits.color[1] for p in strain_pellets) // count
        b = sum(p.traits.color[2] for p in strain_pellets) // count
        strain_color = (r, g, b)
        
        # Popup Setup
        popup_width = 400
        popup_height = 450
        popup_x = (screen.get_width() - popup_width) // 2
        popup_y = (screen.get_height() - popup_height) // 2
        
        self._draw_popup_background(screen, popup_x, popup_y, popup_width, popup_height, (20, 40, 20, 250), (100, 200, 100))
        
        x = popup_x + 20
        y = popup_y + 20
        
        # Title
        gen = strain_pellets[0].generation
        title_text = f"Food Strain G{gen}"
        title_surf = self._get_cached_text(title_text, self.title_font, strain_color)
        screen.blit(title_surf, (x, y))
        y += 40
        
        # Stats
        self._draw_section_title(screen, "POPULATION", x, y, (150, 255, 150))
        y += 25
        
        self._draw_text(screen, f"Total Count: {count}", x + 10, y, (220, 220, 220))
        y += 20
        self._draw_text(screen, f"Strain ID: {self.selected_strain_id[:8]}", x + 10, y, (180, 180, 180))
        y += 25
        
        # Traits
        self._draw_section_title(screen, "NUTRITIONAL PROFILE", x, y, (200, 255, 100))
        y += 25
        
        traits = [
            (f"Energy Value: {avg_nut:.1f}", avg_nut / 100.0, (100, 255, 100)),
            (f"Growth Rate: {avg_growth:.2f}", avg_growth / 2.0, (100, 255, 255)),
            (f"Toxicity: {avg_tox:.2f}", avg_tox / 10.0, (255, 100, 100))
        ]
        
        for text, pct, color in traits:
            self._draw_text(screen, text, x + 10, y, (220, 220, 220))
            
            # Bar
            bar_x = x + 200
            bar_width = 100
            bar_height = 8
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, y + 5, bar_width, bar_height))
            pygame.draw.rect(screen, color, (bar_x, y + 5, bar_width * min(1.0, pct), bar_height))
            
            y += 25

    def _draw_popup_background(self, screen, x, y, w, h, bg_color, border_color):
        """Helper to draw popup background."""
        # Overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 150), pygame.Rect(0, 0, screen.get_width(), screen.get_height()))
        screen.blit(overlay, (0, 0))
        
        # Popup
        popup_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(popup_surface, bg_color, pygame.Rect(0, 0, w, h), border_radius=12)
        pygame.draw.rect(popup_surface, border_color, pygame.Rect(0, 0, w, h), 2, border_radius=12)
        screen.blit(popup_surface, (x, y))
        
        # Close instruction
        close_text = "Click anywhere to close"
        close_surf = self._get_cached_text(close_text, self.small_font, (150, 150, 150))
        screen.blit(close_surf, (x + (w - 40 - close_surf.get_width()) // 2, y + h - 30))

    def _draw_section_title(self, screen, text, x, y, color):
        """Helper to draw section title."""
        surf = self._get_cached_text(text, self.text_font, color)
        screen.blit(surf, (x, y))

    def _draw_text(self, screen, text, x, y, color):
        """Helper to draw simple text."""
        surf = self._get_cached_text(text, self.small_font, color)
        screen.blit(surf, (x, y))
    
    def _render_event_log(self, screen: pygame.Surface):
        """
        Render the event log (Battle Feed) at the bottom left.
        
        Panel is positioned in the bottom left corner, aligned with other panels.
        """
        screen_height = screen.get_height()
        
        # Match dimensions of other left-side panels
        panel_width = 230
        panel_height = 190
        panel_x = 10
        panel_y = screen_height - panel_height - 10
        
        if not self._render_panel_container(screen, panel_x, panel_y, panel_width, panel_height, "Battle Feed", "log"):
            return
            
        # Event messages
        y_offset = 35
        for event_msg in list(self.event_log):
            if y_offset > panel_height - 20:
                break
            
            text_surface = self._get_cached_text(event_msg, self.small_font, self.text_color)
            screen.blit(text_surface, (20, panel_y + y_offset))
            y_offset += 20
    
    def _render_pause_indicator(self, screen: pygame.Surface):
        """Render pause indicator in center of screen."""
        
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
             "I - Inspector",
             "SPACE - Pause",
             "ESC - Menu"
         ]
         
         x = screen.get_width() - 200
         y = screen.get_height() - 90
         
         for i, control in enumerate(controls):
             text_surface = self.small_font.render(control, True, (180, 180, 180))
             screen.blit(text_surface, (x, y + i * 18))
    
    def _render_controls_panel(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render a small interactive control panel in the right margin.

        Provides simple buttons to tweak global battle knobs at runtime:
        - Increase / decrease resource (food) spawn rate
        - Increase / decrease breeding cooldown
        - Spawn a resource immediately
        - Toggle pellet stats panel
        """
        panel_width = 230
        margin_from_edge = 10
        panel_x = screen.get_width() - panel_width - margin_from_edge
        
        # Position below Biome panel (dynamic)
        biome_expanded = self.panel_states.get('biome', True)
        biome_h = 220 if biome_expanded else 28
        
        panel_y = 10 + biome_h + 10

        # Panel background
        panel_height = self.controls_panel_height
        
        if not self._render_panel_container(screen, panel_x, panel_y, panel_width, panel_height, "CONTROLS", "controls"):
            return

        y = panel_y + 36
        x = panel_x + 10

        # Resource spawn rate controls
        spawn_rate = getattr(battle, 'resource_spawn_rate', 0.0)
        sr_text = f"Food Spawn Rate: {spawn_rate:.2f}/s"
        screen.blit(self.small_font.render(sr_text, True, self.text_color), (x, y))

        # Buttons: + and - for spawn rate
        btn_w = 28
        btn_h = 20
        gap = 6
        btn_x = panel_x + panel_width - btn_w - 10
        btn_y = y - 2
        plus_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        minus_rect = pygame.Rect(btn_x - btn_w - gap, btn_y, btn_w, btn_h)

        # Draw pressed state if applicable
        now_color = (60, 60, 60)
        if self._pressed_button == 'spawn_rate_minus':
            pygame.draw.rect(screen, (40, 40, 40), minus_rect)
        else:
            pygame.draw.rect(screen, now_color, minus_rect)

        if self._pressed_button == 'spawn_rate_plus':
            pygame.draw.rect(screen, (40, 40, 40), plus_rect)
        else:
            pygame.draw.rect(screen, now_color, plus_rect)

        screen.blit(self.small_font.render("-", True, (220, 220, 220)), (minus_rect.x + 8, minus_rect.y + 1))
        screen.blit(self.small_font.render("+", True, (220, 220, 220)), (plus_rect.x + 8, plus_rect.y + 1))

        self._control_button_rects['spawn_rate_plus'] = plus_rect
        self._control_button_rects['spawn_rate_minus'] = minus_rect

        y += 28

        # Breeding cooldown controls
        bc = getattr(battle, 'breeding_cooldown', 0.0)
        bc_text = f"Breeding Cooldown: {bc:.1f}s"
        screen.blit(self.small_font.render(bc_text, True, self.text_color), (x, y))

        btn_y = y - 2
        plus_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        minus_rect = pygame.Rect(btn_x - btn_w - gap, btn_y, btn_w, btn_h)
        # Breeding cooldown buttons
        if self._pressed_button == 'breed_cd_minus':
            pygame.draw.rect(screen, (40, 40, 40), minus_rect)
        else:
            pygame.draw.rect(screen, (60, 60, 60), minus_rect)

        if self._pressed_button == 'breed_cd_plus':
            pygame.draw.rect(screen, (40, 40, 40), plus_rect)
        else:
            pygame.draw.rect(screen, (60, 60, 60), plus_rect)

        screen.blit(self.small_font.render("-", True, (220, 220, 220)), (minus_rect.x + 8, minus_rect.y + 1))
        screen.blit(self.small_font.render("+", True, (220, 220, 220)), (plus_rect.x + 8, plus_rect.y + 1))

        self._control_button_rects['breed_cd_plus'] = plus_rect
        self._control_button_rects['breed_cd_minus'] = minus_rect

        y += 30

        # Spawn resource now button
        spawn_rect = pygame.Rect(panel_x + 12, y, panel_width - 24, 26)
        spawn_color = (70, 120, 70)
        if self._pressed_button == 'spawn_now':
            spawn_color = (50, 90, 50)
        pygame.draw.rect(screen, spawn_color, spawn_rect, border_radius=6)
        spawn_label = self.small_font.render("Spawn Food Now", True, (230, 255, 230))
        screen.blit(spawn_label, (spawn_rect.x + 8, spawn_rect.y + 4))
        self._control_button_rects['spawn_now'] = spawn_rect

        y += 34

        # Toggle pellet stats visibility
        toggle_rect = pygame.Rect(panel_x + 12, y, panel_width - 24, 22)
        color = (100, 100, 140) if self.show_pellet_stats else (60, 60, 60)
        if self._pressed_button == 'toggle_pellet_stats':
            draw_color = (80, 80, 120)
        else:
            draw_color = color
        pygame.draw.rect(screen, draw_color, toggle_rect, border_radius=6)
        t_label = "Hide Pellet Stats" if self.show_pellet_stats else "Show Pellet Stats"
        t_surf = self.small_font.render(t_label, True, (230, 230, 230))
        screen.blit(t_surf, (toggle_rect.x + 8, toggle_rect.y + 2))
        self._control_button_rects['toggle_pellet_stats'] = toggle_rect

        y += 30
        
        # Mutation Rate controls
        mut_rate = getattr(battle.breeding_system, 'mutation_rate', 0.1)
        mut_text = f"Mutation Rate: {mut_rate:.2f}"
        screen.blit(self.small_font.render(mut_text, True, self.text_color), (x, y))
        
        btn_y = y - 2
        plus_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        minus_rect = pygame.Rect(btn_x - btn_w - gap, btn_y, btn_w, btn_h)
        
        if self._pressed_button == 'mut_rate_minus':
            pygame.draw.rect(screen, (40, 40, 40), minus_rect)
        else:
            pygame.draw.rect(screen, (60, 60, 60), minus_rect)
            
        if self._pressed_button == 'mut_rate_plus':
            pygame.draw.rect(screen, (40, 40, 40), plus_rect)
        else:
            pygame.draw.rect(screen, (60, 60, 60), plus_rect)
            
        screen.blit(self.small_font.render("-", True, (220, 220, 220)), (minus_rect.x + 8, minus_rect.y + 1))
        screen.blit(self.small_font.render("+", True, (220, 220, 220)), (plus_rect.x + 8, plus_rect.y + 1))
        
        self._control_button_rects['mut_rate_plus'] = plus_rect
        self._control_button_rects['mut_rate_minus'] = minus_rect
        
        y += 34
        
        # Force Weather Change
        weather_rect = pygame.Rect(panel_x + 12, y, panel_width - 24, 26)
        w_color = (70, 70, 120)
        if self._pressed_button == 'force_weather':
            w_color = (50, 50, 90)
        pygame.draw.rect(screen, w_color, weather_rect, border_radius=6)
        w_label = self.small_font.render("Force Weather Change", True, (230, 230, 255))
        screen.blit(w_label, (weather_rect.x + 8, weather_rect.y + 4))
        self._control_button_rects['force_weather'] = weather_rect


    
    def _render_world_stats_panel(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render a panel showing global world statistics.
        
        Positioned in the right margin, below controls and above pellet stats.
        """
        panel_width = 230
        margin_from_edge = 10
        
        # Position below Controls panel (dynamic)
        biome_expanded = self.panel_states.get('biome', True)
        biome_h = 220 if biome_expanded else 28
        
        controls_expanded = self.panel_states.get('controls', True)
        controls_h = self.controls_panel_height if controls_expanded else 28
        
        panel_x = screen.get_width() - panel_width - margin_from_edge
        panel_y = 10 + biome_h + 10 + controls_h + 10
        panel_height = 260
        
        if not self._render_panel_container(screen, panel_x, panel_y, panel_width, panel_height, "World Statistics", "stats"):
            return
            
        y = panel_y + 35
        x = panel_x + 10
        
        # Population Stats
        creatures = battle.creatures
        alive_count = sum(1 for c in creatures if c.is_alive())
        total_count = len(creatures)
        
        pop_text = f"Population: {alive_count} / {total_count}"
        screen.blit(self.small_font.render(pop_text, True, self.text_color), (x, y))
        y += 20
        
        # Infection Stats
        infected_count = sum(1 for c in creatures if c.is_alive() and c.creature.active_infection)
        infection_rate = (infected_count / alive_count * 100) if alive_count > 0 else 0
        
        inf_color = (255, 100, 100) if infection_rate > 20 else (200, 200, 200)
        inf_text = f"Infected: {infected_count} ({infection_rate:.1f}%)"
        screen.blit(self.small_font.render(inf_text, True, inf_color), (x, y))
        y += 20
        
        # Pandemic Alert Level
        if infection_rate > 50:
            alert_text = "⚠ PANDEMIC ALERT ⚠"
            alert_color = (255, 50, 50)
        elif infection_rate > 20:
            alert_text = "⚠ OUTBREAK DETECTED"
            alert_color = (255, 150, 50)
        else:
            alert_text = "Status: Stable"
            alert_color = (100, 255, 100)
            
        screen.blit(self.small_font.render(alert_text, True, alert_color), (x, y))
        y += 30
        
        # Generation Stats
        gens = [c.creature.generation for c in creatures if c.is_alive() and hasattr(c.creature, 'generation')]
        if gens:
            avg_gen = sum(gens) / len(gens)
            max_gen = max(gens)
        else:
            avg_gen = 0
            max_gen = 0
            
        screen.blit(self.small_font.render(f"Avg Generation: {avg_gen:.1f}", True, self.text_color), (x, y))
        y += 20
        screen.blit(self.small_font.render(f"Max Generation: {max_gen}", True, self.text_color), (x, y))
        y += 30
        
        # Extinction Counter (Approximation based on strain groups)
        strain_groups = {}
        for c in creatures:
            sid = c.creature.strain_id
            if sid not in strain_groups:
                strain_groups[sid] = {'total': 0, 'alive': 0}
            strain_groups[sid]['total'] += 1
            if c.is_alive():
                strain_groups[sid]['alive'] += 1
                
        extinct_count = sum(1 for s in strain_groups.values() if s['total'] > 0 and s['alive'] == 0)
        
        screen.blit(self.small_font.render(f"Extinct Strains: {extinct_count}", True, (150, 150, 150)), (x, y))
        y += 20
        
        # Active Strains
        active_strains = sum(1 for s in strain_groups.values() if s['alive'] > 0)
        screen.blit(self.small_font.render(f"Active Strains: {active_strains}", True, (150, 255, 150)), (x, y))
        y += 20
        
        # Births and Deaths
        births = getattr(battle.lifecycle_manager, 'birth_count', 0)
        deaths = getattr(battle.lifecycle_manager, 'death_count', 0)
        screen.blit(self.small_font.render(f"Births: {births}", True, (100, 255, 200)), (x, y))
        y += 20
        screen.blit(self.small_font.render(f"Deaths: {deaths}", True, (255, 150, 150)), (x, y))
        y += 30
        
        # Time Scale
        time_text = f"Sim Time: {battle.current_time:.1f}s"
        screen.blit(self.small_font.render(time_text, True, (150, 200, 255)), (x, y))


    def _render_pellet_stats_panel(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render a panel showing pellet population statistics.
        """
        pellets = battle.arena.pellets
        if not pellets:
            return

        panel_width = 230
        margin_from_edge = 10

        # Position below World Stats panel (dynamic)
        biome_expanded = self.panel_states.get('biome', True)
        biome_h = 220 if biome_expanded else 28
        
        controls_expanded = self.panel_states.get('controls', True)
        controls_h = self.controls_panel_height if controls_expanded else 28
        
        stats_expanded = self.panel_states.get('stats', True)
        stats_h = 260 if stats_expanded else 28
        
        panel_x = screen.get_width() - panel_width - margin_from_edge
        panel_y = 10 + biome_h + 10 + controls_h + 10 + stats_h + 10

        # Calculate available height - extend to bottom of screen minus margin
        available_height = screen.get_height() - panel_y - 10
        panel_height = max(50, available_height)
        
        # Update rect for hit testing
        self.pellet_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        if not self._render_panel_container(screen, panel_x, panel_y, panel_width, panel_height, "Pellet Ecosystem", "pellets"):
            return

        # Content Rendering with Scrolling
        content_x = panel_x + 10
        content_y_start = panel_y + 35
        content_width = panel_width - 20
        content_height = panel_height - 45 # Subtract header and bottom padding
        
        # Create a clipping rect for the content
        clip_rect = pygame.Rect(panel_x, content_y_start, panel_width, content_height)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)
        
        y_offset = content_y_start - self.pellet_scroll_offset
        current_y = y_offset

        # Helper to render text line
        def render_line(text, color=self.text_color):
            nonlocal current_y
            surf = self.small_font.render(text, True, color)
            screen.blit(surf, (content_x, current_y))
            current_y += 22

        # Total count
        render_line(f"Count: {len(pellets)}")

        # Average nutrition
        avg_nutrition = sum(p.get_nutritional_value() for p in pellets) / len(pellets)
        render_line(f"Avg Nutrition: {avg_nutrition:.1f}")

        # Nutrition range
        min_nutrition = min(p.get_nutritional_value() for p in pellets)
        max_nutrition = max(p.get_nutritional_value() for p in pellets)
        render_line(f"Range: {min_nutrition:.0f}-{max_nutrition:.0f}")

        # Max generation
        max_gen = max(p.generation for p in pellets)
        render_line(f"Max Gen: {max_gen}")

        # Average growth rate
        avg_growth = sum(p.traits.growth_rate for p in pellets) / len(pellets)
        render_line(f"Avg Growth: {avg_growth:.3f}")

        # Average toxicity
        avg_toxicity = sum(p.traits.toxicity for p in pellets) / len(pellets)
        render_line(f"Avg Toxicity: {avg_toxicity:.2f}")
        
        # Calculate total content height
        total_content_height = current_y - y_offset
        
        # Restore clip
        screen.set_clip(old_clip)
        
        # Clamp scroll offset
        max_scroll = max(0, total_content_height - content_height)
        self.pellet_scroll_offset = max(0, min(self.pellet_scroll_offset, max_scroll))
        
        # Draw Scrollbar if needed
        if total_content_height > content_height:
            scrollbar_x = panel_x + panel_width - 8
            scrollbar_y = content_y_start
            scrollbar_h = content_height
            
            # Track
            pygame.draw.rect(screen, (30, 30, 40), (scrollbar_x, scrollbar_y, 4, scrollbar_h))
            
            # Thumb
            thumb_h = max(20, (content_height / total_content_height) * scrollbar_h)
            if max_scroll > 0:
                thumb_y = scrollbar_y + (self.pellet_scroll_offset / max_scroll) * (scrollbar_h - thumb_h)
            else:
                thumb_y = scrollbar_y
                
            pygame.draw.rect(screen, (100, 100, 120), (scrollbar_x, thumb_y, 4, thumb_h), border_radius=2)
        

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

    def _compute_control_rects(self, screen: pygame.Surface = None):
        """
        Compute the control button rects deterministically from screen size.
        This allows hit-testing even if rendering didn't populate rects.
        """
        if screen is None:
            screen = pygame.display.get_surface()
        if not screen:
            return {}

        panel_width = 230
        margin_from_edge = 10
        panel_x = screen.get_width() - panel_width - margin_from_edge
        
        # Recalculate Panel Y based on Biome state (default expanded for hit testing if unknown)
        biome_expanded = self.panel_states.get('biome', True)
        biome_h = 220 if biome_expanded else 28
        panel_y = 10 + biome_h + 10

        btn_w = 28
        btn_h = 20
        gap = 6
        btn_x = panel_x + panel_width - btn_w - 10

        rects = {}
        # spawn rate +/-
        rects['spawn_rate_plus'] = pygame.Rect(btn_x, panel_y + 36 - 2, btn_w, btn_h)
        rects['spawn_rate_minus'] = pygame.Rect(btn_x - btn_w - gap, panel_y + 36 - 2, btn_w, btn_h)

        # breeding cooldown +/- (below spawn rate by 28)
        rects['breed_cd_plus'] = pygame.Rect(btn_x, panel_y + 36 + 28 - 2, btn_w, btn_h)
        rects['breed_cd_minus'] = pygame.Rect(btn_x - btn_w - gap, panel_y + 36 + 28 - 2, btn_w, btn_h)

        # spawn now button
        spawn_y = panel_y + 36 + 28 + 30
        rects['spawn_now'] = pygame.Rect(panel_x + 12, spawn_y, panel_width - 24, 26)

        # toggle pellet stats
        toggle_y = spawn_y + 34
        rects['toggle_pellet_stats'] = pygame.Rect(panel_x + 12, toggle_y, panel_width - 24, 22)

        return rects



    def render_dilemma_popup(self, screen: pygame.Surface, dilemma):
        """
        Render the ethical dilemma popup.
        
        Args:
            screen: Pygame surface
            dilemma: The active EthicalDilemma
        """
        # Clear interactive rects
        self.dilemma_choice_rects = {}
        self.ask_advisor_rect = None
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Dim background
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 200), overlay.get_rect())
        screen.blit(overlay, (0, 0))
        
        # Popup dimensions
        popup_width = 600
        popup_height = 500
        popup_x = (screen_width - popup_width) // 2
        popup_y = (screen_height - popup_height) // 2
        
        # Popup background
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(screen, (30, 30, 40), popup_rect, border_radius=12)
        pygame.draw.rect(screen, (100, 150, 255), popup_rect, 2, border_radius=12)
        
        # Title
        title_surf = self._get_cached_text("⚠️ ETHICAL DILEMMA", self.title_font, (255, 200, 100))
        title_rect = title_surf.get_rect(centerx=popup_rect.centerx, top=popup_rect.top + 20)
        screen.blit(title_surf, title_rect)
        
        # Dilemma Name
        name_surf = self._get_cached_text(dilemma.title, self.title_font, (255, 255, 255))
        name_rect = name_surf.get_rect(centerx=popup_rect.centerx, top=title_rect.bottom + 20)
        screen.blit(name_surf, name_rect)
        
        # Description (wrapped)
        desc_y = name_rect.bottom + 20
        words = dilemma.description.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if self.text_font.size(test_line)[0] > popup_width - 60:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        for line in lines:
            line_surf = self._get_cached_text(line, self.text_font, (200, 200, 200))
            line_rect = line_surf.get_rect(centerx=popup_rect.centerx, top=desc_y)
            screen.blit(line_surf, line_rect)
            desc_y += 25
            
        # Choices
        choice_y = desc_y + 30
        mouse_pos = pygame.mouse.get_pos()
        
        for i, choice in enumerate(dilemma.choices):
            choice_rect = pygame.Rect(popup_x + 30, choice_y, popup_width - 60, 60)
            
            # Hover effect
            is_hovered = choice_rect.collidepoint(mouse_pos)
            bg_color = (50, 50, 70) if not is_hovered else (70, 70, 90)
            border_color = (100, 100, 100) if not is_hovered else (150, 200, 255)
            
            pygame.draw.rect(screen, bg_color, choice_rect, border_radius=8)
            pygame.draw.rect(screen, border_color, choice_rect, 1, border_radius=8)
            
            # Choice Text
            text_surf = self._get_cached_text(f"{i+1}. {choice.text}", self.text_font, (255, 255, 255))
            screen.blit(text_surf, (choice_rect.x + 15, choice_rect.y + 10))
            
            # Ethics Impact
            impact_text = f"Welfare:{choice.welfare_impact:+.0f}  Ecosystem:{choice.ecosystem_impact:+.0f}  Integrity:{choice.integrity_impact:+.0f}  Intervention:{choice.intervention_impact:+.0f}"
            impact_surf = self._get_cached_text(impact_text, self.small_font, (150, 150, 150))
            screen.blit(impact_surf, (choice_rect.x + 15, choice_rect.y + 35))
            
            # Store rect for click detection
            self.dilemma_choice_rects[i] = choice_rect
            
            choice_y += 70
            
        # Ask Advisors Button
        advisor_btn_rect = pygame.Rect(popup_x + 30, popup_rect.bottom - 50, 150, 30)
        is_hovered = advisor_btn_rect.collidepoint(mouse_pos)
        bg_color = (40, 60, 80) if not is_hovered else (60, 80, 100)
        
        pygame.draw.rect(screen, bg_color, advisor_btn_rect, border_radius=6)
        pygame.draw.rect(screen, (100, 150, 200), advisor_btn_rect, 1, border_radius=6)
        
        btn_text = self._get_cached_text("Ask Advisors", self.text_font, (200, 220, 255))
        text_rect = btn_text.get_rect(center=advisor_btn_rect.center)
        screen.blit(btn_text, text_rect)
        
        
        
        self.ask_advisor_rect = advisor_btn_rect

    def render_ethics_dashboard(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render the ethics dashboard.
        
        Args:
            screen: Pygame surface
            battle: The spatial battle
        """
        if not self.show_ethics_dashboard:
            return
            
        if not hasattr(battle, 'ethics_system'):
            return
            
        ethics = battle.ethics_system
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Panel dimensions
        panel_width = 400
        panel_height = 350
        panel_x = screen_width - panel_width - 20
        panel_y = 100 # Below top bar
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Shadow
        shadow_rect = panel_rect.copy()
        shadow_rect.move_ip(4, 4)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        # Main bg
        pygame.draw.rect(screen, (20, 25, 30, 240), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 200, 255), panel_rect, 2, border_radius=10)
        
        # Header
        header_text = self._get_cached_text("Ethics Dashboard", self.title_font, (200, 255, 255))
        header_rect = header_text.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 15)
        screen.blit(header_text, header_rect)
        
        # Research Approach
        approach = ethics.get_research_approach()
        approach_surf = self._get_cached_text(f"Approach: {approach}", self.text_font, (255, 255, 200))
        approach_rect = approach_surf.get_rect(centerx=panel_rect.centerx, top=header_rect.bottom + 10)
        screen.blit(approach_surf, approach_rect)
        
        # Scores
        y = approach_rect.bottom + 30
        x_label = panel_x + 30
        x_bar = panel_x + 150
        bar_width = 200
        bar_height = 15
        
        metrics = [
            ("Welfare", ethics.welfare_score, (100, 255, 100)),
            ("Ecosystem", ethics.ecosystem_score, (100, 200, 100)),
            ("Integrity", ethics.integrity_score, (100, 100, 255)),
            ("Intervention", ethics.intervention_score, (255, 150, 100))
        ]
        
        for label, score, color in metrics:
            # Label
            lbl_surf = self._get_cached_text(label, self.text_font, (200, 200, 200))
            screen.blit(lbl_surf, (x_label, y))
            
            # Bar Background
            pygame.draw.rect(screen, (50, 50, 50), (x_bar, y + 4, bar_width, bar_height))
            
            # Bar Fill
            # Scores are -100 to 100 (except intervention 0-100)
            if label == "Intervention":
                fill_pct = score / 100.0
                fill_w = bar_width * fill_pct
                fill_rect = pygame.Rect(x_bar, y + 4, fill_w, bar_height)
            else:
                # Normalize -100..100 to 0..1
                norm_score = (score + 100) / 200.0
                fill_w = bar_width * norm_score
                fill_rect = pygame.Rect(x_bar, y + 4, fill_w, bar_height)
                
                # Center marker
                center_x = x_bar + bar_width / 2
                pygame.draw.line(screen, (150, 150, 150), (center_x, y), (center_x, y + bar_height + 8), 1)
            
            pygame.draw.rect(screen, color, fill_rect)
            
            # Score Text
            score_text = f"{score:+.0f}" if label != "Intervention" else f"{score:.0f}"
            score_surf = self._get_cached_text(score_text, self.small_font, (255, 255, 255))
            screen.blit(score_surf, (x_bar + bar_width + 10, y + 4))
            
            y += 40
            
        # Footer hint
        hint_text = self._get_cached_text("Press 'E' to toggle", self.small_font, (150, 150, 150))
        hint_rect = hint_text.get_rect(centerx=panel_rect.centerx, bottom=panel_rect.bottom - 10)
        screen.blit(hint_text, hint_rect)



    def render_assistant_panel(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render the research assistant panel.
        
        Args:
            screen: Pygame surface
            battle: The spatial battle
        """
        if not self.show_advisor_panel:
            return
            
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Panel dimensions
        panel_width = 500
        panel_height = 400
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.advisor_panel_rect = panel_rect
        
        # Shadow
        shadow_rect = panel_rect.copy()
        shadow_rect.move_ip(4, 4)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        # Main bg
        pygame.draw.rect(screen, (25, 30, 40), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 150, 200), panel_rect, 2, border_radius=10)
        
        # Header
        header_text = self._get_cached_text("Research Assistants", self.title_font, (200, 220, 255))
        header_rect = header_text.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 15)
        screen.blit(header_text, header_rect)
        
        # Close Button
        close_size = 24
        close_rect = pygame.Rect(panel_rect.right - 35, panel_rect.top + 10, close_size, close_size)
        self.advisor_close_rect = close_rect
        
        mouse_pos = pygame.mouse.get_pos()
        is_hover = close_rect.collidepoint(mouse_pos)
        color = (255, 100, 100) if is_hover else (200, 80, 80)
        
        pygame.draw.rect(screen, color, close_rect, border_radius=4)
        x_surf = self._get_cached_text("X", self.small_font, (255, 255, 255))
        x_rect = x_surf.get_rect(center=close_rect.center)
        screen.blit(x_surf, x_rect)
        
        # Content
        content_y = header_rect.bottom + 20
        
        if hasattr(battle, 'assistant_manager') and battle.assistant_manager:
            assistants = battle.assistant_manager.assistants
            
            for assistant in assistants:
                # Assistant Card
                card_rect = pygame.Rect(panel_x + 20, content_y, panel_width - 40, 90)
                pygame.draw.rect(screen, (40, 45, 55), card_rect, border_radius=6)
                pygame.draw.rect(screen, (60, 70, 90), card_rect, 1, border_radius=6)
                
                # Name & Title
                name_surf = self._get_cached_text(assistant.name, self.text_font, (255, 255, 255))
                screen.blit(name_surf, (card_rect.x + 10, card_rect.y + 10))
                
                title_surf = self._get_cached_text(assistant.title, self.small_font, (150, 200, 200))
                screen.blit(title_surf, (card_rect.x + 10, card_rect.y + 32))
                
                # Philosophy Badge
                phil_color = (100, 100, 100)
                if "humane" in assistant.philosophy.value: phil_color = (100, 200, 100)
                elif "pragmatic" in assistant.philosophy.value: phil_color = (100, 150, 255)
                elif "naturalist" in assistant.philosophy.value: phil_color = (200, 180, 100)
                
                phil_surf = self._get_cached_text(assistant.philosophy.value.title(), self.small_font, phil_color)
                screen.blit(phil_surf, (card_rect.right - phil_surf.get_width() - 10, card_rect.y + 10))
                
                # Current Advice / Comment
                # If dilemma is pending, show specific advice
                # Otherwise show general comment
        pygame.draw.rect(screen, (100, 150, 200), advisor_btn_rect, 1, border_radius=6)
        
        btn_text = self._get_cached_text("Ask Advisors", self.text_font, (200, 220, 255))
        text_rect = btn_text.get_rect(center=advisor_btn_rect.center)
        screen.blit(btn_text, text_rect)
        
        
        
        self.ask_advisor_rect = advisor_btn_rect

    def render_ethics_dashboard(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render the ethics dashboard.
        
        Args:
            screen: Pygame surface
            battle: The spatial battle
        """
        if not self.show_ethics_dashboard:
            return
            
        if not hasattr(battle, 'ethics_system'):
            return
            
        ethics = battle.ethics_system
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Panel dimensions
        panel_width = 400
        panel_height = 350
        panel_x = screen_width - panel_width - 20
        panel_y = 100 # Below top bar
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Shadow
        shadow_rect = panel_rect.copy()
        shadow_rect.move_ip(4, 4)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        # Main bg
        pygame.draw.rect(screen, (20, 25, 30, 240), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 200, 255), panel_rect, 2, border_radius=10)
        
        # Header
        header_text = self._get_cached_text("Ethics Dashboard", self.title_font, (200, 255, 255))
        header_rect = header_text.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 15)
        screen.blit(header_text, header_rect)
        
        # Research Approach
        approach = ethics.get_research_approach()
        approach_surf = self._get_cached_text(f"Approach: {approach}", self.text_font, (255, 255, 200))
        approach_rect = approach_surf.get_rect(centerx=panel_rect.centerx, top=header_rect.bottom + 10)
        screen.blit(approach_surf, approach_rect)
        
        # Scores
        y = approach_rect.bottom + 30
        x_label = panel_x + 30
        x_bar = panel_x + 150
        bar_width = 200
        bar_height = 15
        
        metrics = [
            ("Welfare", ethics.welfare_score, (100, 255, 100)),
            ("Ecosystem", ethics.ecosystem_score, (100, 200, 100)),
            ("Integrity", ethics.integrity_score, (100, 100, 255)),
            ("Intervention", ethics.intervention_score, (255, 150, 100))
        ]
        
        for label, score, color in metrics:
            # Label
            lbl_surf = self._get_cached_text(label, self.text_font, (200, 200, 200))
            screen.blit(lbl_surf, (x_label, y))
            
            # Bar Background
            pygame.draw.rect(screen, (50, 50, 50), (x_bar, y + 4, bar_width, bar_height))
            
            # Bar Fill
            # Scores are -100 to 100 (except intervention 0-100)
            if label == "Intervention":
                fill_pct = score / 100.0
                fill_w = bar_width * fill_pct
                fill_rect = pygame.Rect(x_bar, y + 4, fill_w, bar_height)
            else:
                # Normalize -100..100 to 0..1
                norm_score = (score + 100) / 200.0
                fill_w = bar_width * norm_score
                fill_rect = pygame.Rect(x_bar, y + 4, fill_w, bar_height)
                
                # Center marker
                center_x = x_bar + bar_width / 2
                pygame.draw.line(screen, (150, 150, 150), (center_x, y), (center_x, y + bar_height + 8), 1)
            
            pygame.draw.rect(screen, color, fill_rect)
            
            # Score Text
            score_text = f"{score:+.0f}" if label != "Intervention" else f"{score:.0f}"
            score_surf = self._get_cached_text(score_text, self.small_font, (255, 255, 255))
            screen.blit(score_surf, (x_bar + bar_width + 10, y + 4))
            
            y += 40
            
        # Footer hint
        hint_text = self._get_cached_text("Press 'E' to toggle", self.small_font, (150, 150, 150))
        hint_rect = hint_text.get_rect(centerx=panel_rect.centerx, bottom=panel_rect.bottom - 10)
        screen.blit(hint_text, hint_rect)



    def render_assistant_panel(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render the research assistant panel.
        
        Args:
            screen: Pygame surface
            battle: The spatial battle
        """
        if not self.show_advisor_panel:
            return
            
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Panel dimensions
        panel_width = 500
        panel_height = 400
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.advisor_panel_rect = panel_rect
        
        # Shadow
        shadow_rect = panel_rect.copy()
        shadow_rect.move_ip(4, 4)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        # Main bg
        pygame.draw.rect(screen, (25, 30, 40), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 150, 200), panel_rect, 2, border_radius=10)
        
        # Header
        header_text = self._get_cached_text("Research Assistants", self.title_font, (200, 220, 255))
        header_rect = header_text.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 15)
        screen.blit(header_text, header_rect)
        
        # Close Button
        close_size = 24
        close_rect = pygame.Rect(panel_rect.right - 35, panel_rect.top + 10, close_size, close_size)
        self.advisor_close_rect = close_rect
        
        mouse_pos = pygame.mouse.get_pos()
        is_hover = close_rect.collidepoint(mouse_pos)
        color = (255, 100, 100) if is_hover else (200, 80, 80)
        
        pygame.draw.rect(screen, color, close_rect, border_radius=4)
        x_surf = self._get_cached_text("X", self.small_font, (255, 255, 255))
        x_rect = x_surf.get_rect(center=close_rect.center)
        screen.blit(x_surf, x_rect)
        
        # Content
        content_y = header_rect.bottom + 20
        
        if hasattr(battle, 'assistant_manager') and battle.assistant_manager:
            assistants = battle.assistant_manager.assistants
            
            for assistant in assistants:
                # Assistant Card
                card_rect = pygame.Rect(panel_x + 20, content_y, panel_width - 40, 90)
                pygame.draw.rect(screen, (40, 45, 55), card_rect, border_radius=6)
                pygame.draw.rect(screen, (60, 70, 90), card_rect, 1, border_radius=6)
                
                # Name & Title
                name_surf = self._get_cached_text(assistant.name, self.text_font, (255, 255, 255))
                screen.blit(name_surf, (card_rect.x + 10, card_rect.y + 10))
                
                title_surf = self._get_cached_text(assistant.title, self.small_font, (150, 200, 200))
                screen.blit(title_surf, (card_rect.x + 10, card_rect.y + 32))
                
                # Philosophy Badge
                phil_color = (100, 100, 100)
                if "humane" in assistant.philosophy.value: phil_color = (100, 200, 100)
                elif "pragmatic" in assistant.philosophy.value: phil_color = (100, 150, 255)
                elif "naturalist" in assistant.philosophy.value: phil_color = (200, 180, 100)
                
                phil_surf = self._get_cached_text(assistant.philosophy.value.title(), self.small_font, phil_color)
                screen.blit(phil_surf, (card_rect.right - phil_surf.get_width() - 10, card_rect.y + 10))
                
                # Current Advice / Comment
                # If dilemma is pending, show specific advice
                # Otherwise show general comment
                comment = ""
                if hasattr(battle, 'pending_dilemma') and battle.pending_dilemma:
                    comment = assistant.get_advice(battle.pending_dilemma, battle.ethics_system)
                elif hasattr(battle, 'ethics_system'):
                    comment = assistant.get_general_comment(battle.ethics_system)
                print(f"Assistant: {assistant.name}, Comment: {comment}") # Debug logging
                
                # Wrap comment
                words = comment.split(' ')
                lines = []
                current_line = []
                for word in words:
                    current_line.append(word)
                    if self.small_font.size(' '.join(current_line))[0] > card_rect.width - 20:
                        current_line.pop()
                        lines.append(' '.join(current_line))
                        current_line = [word]
                lines.append(' '.join(current_line))
                
                text_y = card_rect.y + 50
                for line in lines[:2]: # Max 2 lines
                    line_surf = self._get_cached_text(line, self.small_font, (200, 200, 200))
                    screen.blit(line_surf, (card_rect.x + 10, text_y))
                    text_y += 16
                
                content_y += 100

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
            speed_text = "PAUSED"
            speed_color = (255, 100, 100)
        else:
            speed_text = f"{simulation_speed}x"
            speed_color = (100, 255, 100)
        speed_surf = self.text_font.render(speed_text, True, speed_color)
        screen.blit(speed_surf, (screen.get_width() - 150, 25))
        
        # Mode indicator
        mode_text = "FEED MODE (Press F to toggle)"
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
            stat_surf = self.text_font.render(stat, True, (200, 200, 200))
            screen.blit(stat_surf, (stats_x, stats_y))
            stats_x += stat_surf.get_width() + 40
        
        # Event log
        log_start_y = stats_y + 50
        
        # Get all events (strings)
        events = list(self.event_log)
        events.reverse()  # Most recent first
        
        # Render events
        event_y = log_start_y
        line_height = 30
        
        for i, event_message in enumerate(events):
            if event_y > screen.get_height() - 50:
                break
            
            # Color code based on keywords in message
            message_lower = event_message.lower()
            if 'born' in message_lower or 'birth' in message_lower:
                color = (100, 255, 100)  # Green
            elif 'died' in message_lower or 'death' in message_lower or 'starved' in message_lower:
                color = (255, 100, 100)  # Red
            elif 'attack' in message_lower or 'damage' in message_lower or 'hit' in message_lower:
                color = (255, 200, 100)  # Orange
            elif 'pellet' in message_lower or 'grass' in message_lower:
                color = (100, 255, 255)  # Cyan
            else:
                color = (200, 200, 200)  # White
            
            # Render event with background
            bg_rect = pygame.Rect(10, event_y, screen.get_width() - 20, line_height - 2)
            bg_color = (30, 30, 40) if i % 2 == 0 else (25, 25, 35)
            pygame.draw.rect(screen, bg_color, bg_rect)
            
            text_surf = self.small_font.render(event_message, True, color)
            screen.blit(text_surf, (15, event_y + 5))
            
            event_y += line_height
        
        # Controls help
        help_text = "Controls: Q/W/R/T/Y = Speed | SPACE = Pause | F = Toggle Mode | ESC = Menu"
        help_surf = self.small_font.render(help_text, True, (100, 100, 120))
        screen.blit(help_surf, ((screen.get_width() - help_surf.get_width()) // 2, screen.get_height() - 25))
