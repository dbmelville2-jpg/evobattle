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
        self.selected_strain_id = None
        self.strain_panel_rect = None  # Will be updated in render
        self.strain_item_rects = {}    # Map strain_id -> rect for click detection
    
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

    def handle_event(self, event: pygame.event.Event, battle: SpatialBattle):
        """
        Handle input events for UI interaction.
        
        Args:
            event: Pygame event
            battle: The spatial battle instance
        """
        # Ensure rects exist
        if not self._control_button_rects:
             try:
                 self._control_button_rects = self._compute_control_rects()
             except Exception:
                 self._control_button_rects = {}

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check controls panel buttons
            for btn_key, rect in self._control_button_rects.items():
                if rect.collidepoint(mouse_pos):
                    self._pressed_button = btn_key
                    self._pressed_time = pygame.time.get_ticks()
                    
                    # Execute action immediately
                    try:
                        if btn_key == 'spawn_rate_plus':
                            battle.resource_spawn_rate = min(5.0, getattr(battle, 'resource_spawn_rate', 0.0) + 0.1)
                        elif btn_key == 'spawn_rate_minus':
                            battle.resource_spawn_rate = max(0.0, getattr(battle, 'resource_spawn_rate', 0.0) - 0.1)
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
                    return

            # Check Genetic Strain Panel clicks
            if self.strain_panel_rect and self.strain_panel_rect.collidepoint(mouse_pos):
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
                return
            
            # If a strain is selected and user clicks anywhere else, close the popup
            if self.selected_strain_id:
                self.selected_strain_id = None
                return

            # Check Overseer Panel clicks
            if hasattr(self, 'overseer_btn_rects') and battle.overseer:
                from ..systems.experiment_overseer_system import ProtocolType
                for p_value, rect in self.overseer_btn_rects.items():
                    if rect.collidepoint(mouse_pos):
                        # Execute protocol
                        # Convert string value back to enum if needed, or just pass value if system handles it
                        # The system expects ProtocolType enum
                        try:
                            p_type = ProtocolType(p_value)
                            # For targeted protocols, we might need a targeting mode
                            # For now, let's just execute non-targeted ones or random target
                            # Ideally, we enter a "targeting mode"
                            
                            if p_type in [ProtocolType.DISPENSE_NUTRIENTS, ProtocolType.NEURAL_SHOCK, ProtocolType.GENETIC_BOOST, ProtocolType.INDUCE_MUTATION, ProtocolType.SAMPLE_COLLECTION]:
                                # If it requires a target, we should probably set a "targeting" state
                                # But for simplicity in this iteration, let's try to execute
                                # If it needs a target and none provided, the system might fail or pick random
                                # Let's implement a simple "click to target" flow later if needed
                                # For now, pass the mouse position for area effects
                                
                                # Convert screen pos to world pos
                                # We need the arena renderer for this... which we don't have here easily
                                # But we can approximate or just let the system handle "random" if None
                                
                                # Actually, for targeted skills, we should probably select the protocol first, then click the target
                                # But let's just try to execute it. If it's "Dispense Nutrients", it works.
                                # If it's "Neural Shock", it needs a target.
                                
                                # Let's just execute it. The system handles defaults.
                                battle.overseer.execute_protocol(p_type)
                        except Exception as e:
                            print(f"Protocol Error: {e}")
                        return

        elif event.type == pygame.MOUSEBUTTONUP:
            self._pressed_button = None
            
        elif event.type == pygame.MOUSEWHEEL:
            # Check if mouse is over strain panel
            mouse_pos = pygame.mouse.get_pos()
            
            if self.strain_panel_rect and self.strain_panel_rect.collidepoint(mouse_pos):
                # Scroll
                self.strain_scroll_offset -= event.y * 20
                self.strain_scroll_offset = max(0, self.strain_scroll_offset)
    
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
    
    def render(self, screen: pygame.Surface, battle: SpatialBattle, paused: bool = False):
        """
        Render all UI components.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle to display info for
            paused: Whether the game is paused
        """
        # Clear interactive rects at start of render to avoid stale geometry
        self._control_button_rects = {}

        # Top bar - Battle title and time
        self._render_top_bar(screen, battle)
        
        # Weather panel (top left)
        self._render_weather_panel(screen, battle)
        
        # Biome panel (below weather panel)
        self._render_biome_panel(screen, battle)
        
        # Genetic strains panel (left side, below biome panel)
        self._render_genetic_strains_panel(screen, battle)
        
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
        if hasattr(battle, 'overseer') and battle.overseer:
            try:
                self._render_overseer_panel(screen, battle)
            except Exception as e:
                print(f"Overseer UI Error: {e}")
                pass

        # Event log (bottom)
        self._render_event_log(screen)
        
        # Pause indicator
        if paused:
            self._render_pause_indicator(screen)
        
        # Battle end overlay
        if battle.is_over:
            self._render_battle_end(screen, battle)
    
    def _render_top_bar(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render the top information bar.
        
        Displays title, time, and ecosystem stats (Food count, Births, Deaths).
        """
        screen_width = screen.get_width()
        
        # Semi-transparent background
        bar_rect = pygame.Rect(0, 0, screen_width, 80)
        bar_surface = pygame.Surface((screen_width, 80), pygame.SRCALPHA)
        pygame.draw.rect(bar_surface, self.panel_bg, bar_rect)
        screen.blit(bar_surface, (0, 0))
        
        # Title
        title_text = "EvoBattle - Spatial Combat Arena"
        title_surface = self._get_cached_text(title_text, self.title_font, self.text_color)
        title_rect = title_surface.get_rect(center=(screen_width // 2, 25))
        screen.blit(title_surface, title_rect)
        
        # Controls hint (centered below title)
        controls_text = "Click creatures to inspect! | I: Inspector | SPACE: Pause | ESC: Menu"
        controls_surface = self._get_cached_text(controls_text, self.small_font, (180, 180, 180))
        controls_rect = controls_surface.get_rect(center=(screen_width // 2, 55))
        screen.blit(controls_surface, controls_rect)
        
        # Ecosystem stats in top right
        # Count pellets (food)
        food_count = len(battle.arena.pellets) if hasattr(battle.arena, 'pellets') else 0
        
        # Count births and deaths from battle events
        births = sum(1 for e in battle.events if hasattr(e, 'event_type') and 
                     str(e.event_type) in ['CREATURE_BIRTH', 'BattleEventType.CREATURE_BIRTH'])
        deaths = sum(1 for e in battle.events if hasattr(e, 'event_type') and 
                     str(e.event_type) in ['CREATURE_DEATH', 'BattleEventType.CREATURE_DEATH', 
                                            'CREATURE_FAINT', 'BattleEventType.CREATURE_FAINT'])
        
        # Display stats on the right side
        stats_x = screen_width - 180
        stats_y = 15
        
        food_text = f"Food: {food_count}"
        food_surface = self._get_cached_text(food_text, self.text_font, (150, 255, 150))
        screen.blit(food_surface, (stats_x, stats_y))
        
        births_text = f"Births: {births}"
        births_surface = self._get_cached_text(births_text, self.text_font, (100, 255, 255))
        screen.blit(births_surface, (stats_x, stats_y + 22))
        
        deaths_text = f"Deaths: {deaths}"
        deaths_surface = self._get_cached_text(deaths_text, self.text_font, (255, 150, 150))
        screen.blit(deaths_surface, (stats_x, stats_y + 44))

    def _render_weather_panel(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render weather and time information in the top left.
        
        Displays:
        - Weather Type
        - Temperature & Humidity
        - Time of Day
        """
        if not battle.environment:
            return
            
        # Position in top left (over the top bar background)
        x = 20
        y = 15
        
        # Get data
        env = battle.environment
        weather = env.weather
        day_night = env.day_night
        
        if not weather:
            return
            
        # Weather Type
        w_type = weather.weather_type.value.title()
        # Color based on weather
        w_color = (200, 200, 255)
        if w_type == "Clear": w_color = (255, 255, 200)
        elif w_type == "Rainy": w_color = (150, 150, 255)
        elif w_type == "Stormy": w_color = (100, 100, 200)
        elif w_type == "Drought": w_color = (255, 200, 150)
        elif w_type == "Foggy": w_color = (200, 200, 200)
        
        # Draw Weather Type
        type_surf = self._get_cached_text(f"Weather: {w_type}", self.text_font, w_color)
        screen.blit(type_surf, (x, y))
        
        # Temperature & Humidity
        y += 22
        temp_text = f"Temp: {weather.temperature:.1f}°C"
        temp_surf = self._get_cached_text(temp_text, self.small_font, self.text_color)
        screen.blit(temp_surf, (x, y))
        
        # Humidity
        hum_text = f"Humidity: {weather.humidity*100:.0f}%"
        hum_surf = self._get_cached_text(hum_text, self.small_font, self.text_color)
        screen.blit(hum_surf, (x + 100, y))
        
        # Time of Day
        y += 18
        if day_night:
            time_phase = day_night.get_time_of_day().value.title()
            hour = day_night.get_current_hour()
            time_str = f"{int(hour):02d}:{int((hour%1)*60):02d}"
            
            time_text = f"Time: {time_str} ({time_phase})"
            time_surf = self._get_cached_text(time_text, self.small_font, (255, 255, 200))
            screen.blit(time_surf, (x, y))

    def _render_biome_panel(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render biome information panel below the weather panel.
        
        Displays:
        - Biome Name (or Region Name if multi-biome)
        - Difficulty Rating
        - Biome Description
        - Mini-map of regions
        """
        if not battle.environment:
            return
            
        env = battle.environment
        
        # Position below weather panel
        panel_x = 20
        panel_y = 100
        panel_width = 220
        panel_height = 180  # Increased height for map
        
        # Background for the whole panel area
        # pygame.draw.rect(screen, (30, 30, 40, 180), (panel_x - 5, panel_y - 5, panel_width + 10, panel_height + 10), border_radius=5)
        
        # Determine what to show (Global biome or specific region)
        biome_name = env.biome_name
        description = env.biome_description
        difficulty = env.biome_difficulty
        is_region_hovered = False
        
        # Mini-map area
        map_size = 80
        map_x = panel_x
        map_y = panel_y + 75
        map_rect = pygame.Rect(map_x, map_y, map_size, map_size)
        
        # Check for region hover in multi-biome setup via mini-map
        mouse_pos = pygame.mouse.get_pos()
        mx, my = mouse_pos
        
        hovered_region = None
        
        # Draw Mini-map
        pygame.draw.rect(screen, (0, 0, 0), map_rect)  # Map background
        pygame.draw.rect(screen, (100, 100, 100), map_rect, 1)  # Map border
        
        if hasattr(env, 'biome_regions') and env.biome_regions:
            # Draw regions
            for region in env.biome_regions:
                # Scale region bounds to map size
                # Region bounds are in world coordinates (0 to env.width)
                # Map is map_size x map_size
                
                rx = map_x + (region.bounds[0] / env.width) * map_size
                ry = map_y + (region.bounds[1] / env.height) * map_size
                rw = (region.bounds[2] / env.width) * map_size
                rh = (region.bounds[3] / env.height) * map_size
                
                region_rect = pygame.Rect(rx, ry, rw, rh)
                
                # Color based on biome type
                b_type = region.biome_type.value
                color = (100, 100, 100)
                if b_type == "grassland": color = (100, 200, 100)
                elif b_type == "forest": color = (34, 139, 34)
                elif b_type == "desert": color = (238, 214, 175)
                elif b_type == "marsh": color = (47, 79, 79)
                elif b_type == "rocky_highlands": color = (139, 69, 19)
                
                pygame.draw.rect(screen, color, region_rect)
                pygame.draw.rect(screen, (50, 50, 50), region_rect, 1) # Grid lines
                
                # Check hover
                if region_rect.collidepoint(mx, my):
                    hovered_region = region
                    # Highlight
                    pygame.draw.rect(screen, (255, 255, 255), region_rect, 2)
        else:
            # Single biome - fill map
            color = (100, 100, 100)
            # Try to guess color from name if simple biome
            b_name = env.biome_name.lower()
            if "grass" in b_name: color = (100, 200, 100)
            elif "forest" in b_name: color = (34, 139, 34)
            elif "desert" in b_name: color = (238, 214, 175)
            elif "marsh" in b_name: color = (47, 79, 79)
            elif "rocky" in b_name: color = (139, 69, 19)
            
            pygame.draw.rect(screen, color, map_rect)
            
            if map_rect.collidepoint(mx, my):
                pygame.draw.rect(screen, (255, 255, 255), map_rect, 2)

        # Update info if hovering a region
        if hovered_region:
            biome_name = hovered_region.biome_config.name
            description = hovered_region.biome_config.description
            difficulty = hovered_region.biome_config.difficulty
            is_region_hovered = True
            
        # Render Text Info
        
        # Color based on difficulty
        if difficulty <= 2:
            biome_color = (150, 255, 150)  # Green - easy
        elif difficulty <= 3:
            biome_color = (255, 255, 150)  # Yellow - medium
        else:
            biome_color = (255, 150, 150)  # Red - hard
            
        if is_region_hovered:
            # Add a highlight effect for region info text area
            # pygame.draw.rect(screen, (40, 40, 50), (panel_x-5, panel_y-5, 220, 75), 0, 5)
            pass
        
        # Name
        name_surf = self._get_cached_text(f"{biome_name}", self.text_font, biome_color)
        screen.blit(name_surf, (panel_x, panel_y))
        
        # Difficulty rating with stars
        y_text = panel_y + 22
        diff_text = f"Difficulty: "
        diff_surf = self._get_cached_text(diff_text, self.small_font, self.text_color)
        screen.blit(diff_surf, (panel_x, y_text))
        
        # Draw stars
        star_x = panel_x + diff_surf.get_width() + 2
        for i in range(5):
            if i < difficulty:
                star_color = (255, 200, 50)  # Filled star
            else:
                star_color = (80, 80, 80)  # Empty star
            star_surf = self._get_cached_text("★", self.small_font, star_color)
            screen.blit(star_surf, (star_x + i * 14, y_text))
        
        # Description (truncated if too long)
        y_text += 18
        if description and len(description) > 60:
            description = description[:57] + "..."
        
        # Wrap description text
        words = description.split(' ')
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if self.small_font.size(test_line)[0] > panel_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines[:2]): # Show max 2 lines
            desc_surf = self._get_cached_text(line, self.small_font, (180, 180, 180))
            screen.blit(desc_surf, (panel_x, y_text + i * 14))

        # Map Label
        map_label = self._get_cached_text("Region Map", self.small_font, (150, 150, 150))
        screen.blit(map_label, (map_x, map_y - 14))
    
    def _render_genetic_strains_panel(
        self,
        screen: pygame.Surface,
        battle: SpatialBattle
    ):
        """
        Render a genetic family panel showing population by strain.
        
        Positioned in the left margin, below the biome panel.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle
        """
        panel_width = 230
        
        # Dynamic height calculation
        margin_from_edge = 10
        panel_y = 300  # Start below biome panel
        
        # Battle feed height is 190, plus 5px margin from bottom
        bottom_margin = 200 
        screen_height = screen.get_height()
        
        # Calculate available height
        available_height = screen_height - panel_y - bottom_margin - 10 # 10px buffer
        panel_height = max(200, available_height) # Minimum 200px
        
        # Position in left margin area
        panel_x = margin_from_edge
        
        # Update panel rect for input handling
        self.strain_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
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
        header_text = "GENETIC STRAINS"
        header_surface = self._get_cached_text(header_text, self.text_font, self.text_color)
        header_rect = header_surface.get_rect(centerx=panel_width // 2, top=10)
        screen.blit(header_surface, (panel_x + header_rect.x, panel_y + header_rect.y))
        
        # Content area definition
        content_y_start = panel_y + 40
        content_height = panel_height - 50 # Reserve space for header and footer
        content_rect = pygame.Rect(panel_x, content_y_start, panel_width, content_height)
        
        # Clip rendering to content area
        original_clip = screen.get_clip()
        screen.set_clip(content_rect)
        
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
        
        # Clear item rects for this frame
        self.strain_item_rects = {}
        
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
            # Only store if visible
            if content_rect.colliderect(item_rect):
                 self.strain_item_rects[strain_id] = item_rect
            
            if is_selected:
                pygame.draw.rect(screen, (60, 60, 80), item_rect, border_radius=4)
                pygame.draw.rect(screen, strain_color, item_rect, 1, border_radius=4)
            
            # Hover effect (optional, requires mouse pos)
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
            if is_selected:
                text_color = (255, 255, 200)
            else:
                text_color = self.text_color
                
            text_surface = self.small_font.render(strain_text, True, text_color)
            screen.blit(text_surface, (panel_x + 35, current_y + 4))
            
            # Population count
            count_text = f"{alive_count}/{total_count}"
            count_surface = self.small_font.render(count_text, True, (200, 200, 200))
            screen.blit(count_surface, (panel_x + panel_width - 50, current_y + 4))
            
            current_y += item_height
            
        # Restore clip
        screen.set_clip(original_clip)
        
        # Draw Scrollbar if needed
        if total_content_height > content_height:
            scrollbar_width = 6
            scrollbar_height = content_height * (content_height / total_content_height)
            scrollbar_x = panel_x + panel_width - 8
            
            # Calculate scrollbar y position
            scroll_ratio = self.strain_scroll_offset / max_scroll
            scrollbar_y = content_y_start + scroll_ratio * (content_height - scrollbar_height)
            
            pygame.draw.rect(screen, (60, 60, 70), (scrollbar_x, content_y_start, scrollbar_width, content_height), border_radius=3)
            pygame.draw.rect(screen, (150, 150, 150), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), border_radius=3)

        # Total alive count footer
        footer_y = panel_y + panel_height - 25
        total_alive = sum(1 for c in battle.creatures if c.is_alive())
        total_text = f"Total Alive: {total_alive}/{len(battle.creatures)}"
        total_surface = self.small_font.render(total_text, True, (200, 255, 200))
        screen.blit(total_surface, (panel_x + 10, footer_y))
        
        # Render Details Popup if a strain is selected
        if self.selected_strain_id:
            self._render_strain_details_popup(screen, battle)
    
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
        y += 15
        
        # Population Statistics
        section_title = "POPULATION"
        title_surf = self._get_cached_text(section_title, self.text_font, (100, 255, 150))
        screen.blit(title_surf, (x, y))
        y += 25
        
        stats = [
            f"Alive: {len(alive)} / {total}",
            f"Mature: {len(mature)}",
            f"Status: {'THRIVING' if len(alive) > 5 else 'EXTINCT' if len(alive) == 0 else 'ENDANGERED'}"
        ]
        
        for stat in stats:
            stat_surf = self._get_cached_text(stat, self.small_font, (200, 200, 200))
            screen.blit(stat_surf, (x + 10, y))
            y += 20
        
        y += 10
        
        # Lineage Information
        section_title = "LINEAGE"
        title_surf = self._get_cached_text(section_title, self.text_font, (255, 200, 100))
        screen.blit(title_surf, (x, y))
        y += 25
        
        lineage_stats = [
            f"Generation Depth: {gen_depth}",
            f"Oldest Gen: {oldest_gen}",
            f"Newest Gen: {newest_gen}",
            f"Avg Color Hue: {int(avg_hue)}°"
        ]
        
        for stat in lineage_stats:
            stat_surf = self._get_cached_text(stat, self.small_font, (200, 200, 200))
            screen.blit(stat_surf, (x + 10, y))
            y += 20
        
        y += 10
        
        # Common Traits
        if common_traits and alive:
            section_title = "COMMON TRAITS"
            title_surf = self._get_cached_text(section_title, self.text_font, (255, 150, 255))
            screen.blit(title_surf, (x, y))
            y += 25
            
            for trait, count in common_traits:
                pct = int((count / len(alive)) * 100)
                trait_text = f"• {trait}"
                trait_surf = self._get_cached_text(trait_text, self.small_font, (220, 220, 220))
                screen.blit(trait_surf, (x + 10, y))
                
                # Percentage bar
                bar_x = x + 250
                bar_y = y + 5
                bar_width = 100
                bar_height = 10
                
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(screen, (100, 200, 255), (bar_x, bar_y, bar_width * (pct / 100), bar_height))
                
                pct_text = f"{pct}%"
                pct_surf = self._get_cached_text(pct_text, self.small_font, (150, 150, 150))
                screen.blit(pct_surf, (bar_x + bar_width + 10, y))
                
                y += 22
        
        # Close instruction
        y = popup_y + popup_height - 40
        close_text = "Click anywhere to close"
        close_surf = self._get_cached_text(close_text, self.small_font, (150, 150, 150))
        screen.blit(close_surf, (x + (popup_width - 40 - close_surf.get_width()) // 2, y))
    
    def _render_event_log(self, screen: pygame.Surface):
        """
        Render the event log (Battle Feed) at the bottom.
        
        Panel is positioned in the bottom margin (200px reserved area).
        """
        screen_width = screen.get_width()
        panel_height = 190
        panel_y = screen.get_height() - panel_height - 5  # 5px from bottom edge
        
        # Panel background
        panel_surface = pygame.Surface((screen_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface,
            self.panel_bg,
            pygame.Rect(0, 0, screen_width, panel_height)
        )
        screen.blit(panel_surface, (0, panel_y))
        
        # Title
        title_surface = self._get_cached_text("Battle Feed", self.text_font, (200, 200, 255))
        screen.blit(title_surface, (20, panel_y + 10))
        
        # Event messages
        y_offset = 40
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
        # Anchor at the top of the right margin
        panel_y = 120

        # Panel background
        panel_height = self.controls_panel_height
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface,
            (20, 20, 30, 220),
            pygame.Rect(0, 0, panel_width, panel_height),
            border_radius=8
        )
        screen.blit(panel_surface, (panel_x, panel_y))

        # Header
        header_text = "CONTROLS"
        header_surface = self.text_font.render(header_text, True, (200, 200, 255))
        screen.blit(header_surface, (panel_x + 10, panel_y + 8))

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


    
    def _render_pellet_stats_panel(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render a panel showing pellet population statistics.
        
        Panel is positioned in the right margin below the CREATURES panel.
        Sized to fit above the Battle Feed panel.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle containing pellets
        """
        pellets = battle.arena.pellets
        if not pellets:
            return

        panel_width = 230
        margin_from_edge = 10

        # Position in right margin area, below the creatures panel
        panel_x = screen.get_width() - panel_width - margin_from_edge
        panel_y = 660  # Below creatures panel (90 + 550 + 20 spacing)

        # Calculate available height before Battle Feed starts
        # Battle Feed starts at screen_height - 195
        battle_feed_top = screen.get_height() - 195
        available_height = battle_feed_top - panel_y - 10  # 10px gap
        panel_height = min(180, max(50, available_height))  # Ensure minimum 50px height

        # Skip rendering if panel would be too small to be useful
        if panel_height < 50:
            return

        # Panel background with increased opacity for better text visibility
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        # Use higher opacity background (230 instead of 180) for better text contrast
        pygame.draw.rect(
            panel_surface,
            (20, 20, 30, 230),
            pygame.Rect(0, 0, panel_width, panel_height),
            border_radius=8
        )
        screen.blit(panel_surface, (panel_x, panel_y))

        # Header
        header_text = "PELLET ECOSYSTEM"
        header_surface = self.text_font.render(header_text, True, (150, 255, 150))
        header_rect = header_surface.get_rect(centerx=panel_width // 2, top=10)
        screen.blit(header_surface, (panel_x + header_rect.x, panel_y + header_rect.y))

        y_offset = 40

        # Total count
        count_text = f"Count: {len(pellets)}"
        count_surface = self.small_font.render(count_text, True, self.text_color)
        screen.blit(count_surface, (panel_x + 10, panel_y + y_offset))
        y_offset += 22

        # Average nutrition
        avg_nutrition = sum(p.get_nutritional_value() for p in pellets) / len(pellets)
        nutrition_text = f"Avg Nutrition: {avg_nutrition:.1f}"
        nutrition_surface = self.small_font.render(nutrition_text, True, self.text_color)
        screen.blit(nutrition_surface, (panel_x + 10, panel_y + y_offset))
        y_offset += 22

        # Nutrition range
        min_nutrition = min(p.get_nutritional_value() for p in pellets)
        max_nutrition = max(p.get_nutritional_value() for p in pellets)
        range_text = f"Range: {min_nutrition:.0f}-{max_nutrition:.0f}"
        range_surface = self.small_font.render(range_text, True, self.text_color)
        screen.blit(range_surface, (panel_x + 10, panel_y + y_offset))
        y_offset += 22

        # Max generation
        max_gen = max(p.generation for p in pellets)
        gen_text = f"Max Gen: {max_gen}"
        gen_surface = self.small_font.render(gen_text, True, self.text_color)
        screen.blit(gen_surface, (panel_x + 10, panel_y + y_offset))
        y_offset += 22

        # Average growth rate
        avg_growth = sum(p.traits.growth_rate for p in pellets) / len(pellets)
        growth_text = f"Avg Growth: {avg_growth:.3f}"
        growth_surface = self.small_font.render(growth_text, True, self.text_color)
        screen.blit(growth_surface, (panel_x + 10, panel_y + y_offset))
        y_offset += 22

        # Average toxicity
        avg_toxicity = sum(p.traits.toxicity for p in pellets) / len(pellets)
        toxicity_text = f"Avg Toxicity: {avg_toxicity:.2f}"
        toxicity_surface = self.small_font.render(toxicity_text, True, self.text_color)
        screen.blit(toxicity_surface, (panel_x + 10, panel_y + y_offset))
        

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
        panel_y = 120

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

    def _render_overseer_panel(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render the Experiment Overseer Control Panel.
        
        Displays Bio-Data and Protocol buttons.
        Positioned on the right side of the screen.
        """
        overseer = battle.overseer
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Position at bottom center of screen
        panel_width = 600
        panel_height = 120
        panel_x = (screen_width - panel_width) // 2
        panel_y = screen_height - panel_height - 10
        
        # Panel Background (Sci-Fi Style)
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Main background
        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(s, (10, 20, 30, 220), s.get_rect(), border_radius=10)
        pygame.draw.rect(s, (0, 255, 255), s.get_rect(), 1, border_radius=10)  # Cyan border
        screen.blit(s, (panel_x, panel_y))
        
        # Header: Bio-Data
        header_y = panel_y + 15
        title_text = "EXPERIMENT CONTROLS"
        title_surf = self._get_cached_text(title_text, self.text_font, (0, 255, 255))
        screen.blit(title_surf, (panel_x + (panel_width - title_surf.get_width()) // 2, header_y))
        
        # Bio-Data Gauge
        data_y = header_y + 30
        data_text = f"BIO-DATA: {int(overseer.bio_data)}/{int(overseer.max_bio_data)}"
        data_surf = self._get_cached_text(data_text, self.text_font, (255, 255, 255))
        screen.blit(data_surf, (panel_x + 20, data_y))
        
        # Bar
        bar_x = panel_x + 20
        bar_y = data_y + 25
        bar_w = panel_width - 40
        bar_h = 10
        
        pct = overseer.bio_data / overseer.max_bio_data
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, (0, 255, 255), (bar_x, bar_y, bar_w * pct, bar_h))
        
        # Protocols - Horizontal layout
        btn_start_x = panel_x + 10
        btn_y = bar_y + 20
        btn_width = 110
        btn_height = 35
        btn_margin = 8
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Ensure we have rects for input handling
        if not hasattr(self, 'overseer_btn_rects'):
            self.overseer_btn_rects = {}
            
        self.overseer_btn_rects = {} # Reset for this frame
        
        btn_x = btn_start_x
        for p_type, protocol in overseer.protocols.items():
            btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
            self.overseer_btn_rects[p_type.value] = btn_rect
            
            # Determine state
            is_hover = btn_rect.collidepoint(mouse_pos)
            can_afford = overseer.bio_data >= protocol.cost
            on_cooldown = protocol.current_cooldown > 0
            
            # Colors
            if on_cooldown:
                bg_color = (50, 30, 30)
                border_color = (100, 50, 50)
                text_color = (150, 100, 100)
            elif not can_afford:
                bg_color = (30, 30, 30)
                border_color = (80, 80, 80)
                text_color = (100, 100, 100)
            elif is_hover:
                bg_color = (0, 60, 60)
                border_color = (0, 255, 255)
                text_color = (255, 255, 255)
            else:
                bg_color = (0, 40, 40)
                border_color = (0, 150, 150)
                text_color = (200, 255, 255)
                
            # Draw Button
            pygame.draw.rect(screen, bg_color, btn_rect, border_radius=5)
            pygame.draw.rect(screen, border_color, btn_rect, 1, border_radius=5)
            
            # Text - compact layout
            name_surf = self._get_cached_text(protocol.name, self.small_font, text_color)
            screen.blit(name_surf, (btn_rect.x + 5, btn_rect.y + 3))
            
            cost_text = f"{protocol.cost}"
            cost_surf = self._get_cached_text(cost_text, self.small_font, text_color)
            screen.blit(cost_surf, (btn_rect.x + 5, btn_rect.y + 18))
            
            # Cooldown overlay or status
            if on_cooldown:
                cd_text = f"{protocol.current_cooldown:.1f}s"
                cd_surf = self._get_cached_text(cd_text, self.small_font, (255, 100, 100))
                screen.blit(cd_surf, (btn_rect.right - cd_surf.get_width() - 5, btn_rect.y + 18))
            else:
                # Description on hover (tooltip style)
                if is_hover:
                    # Render tooltip below or to the side
                    pass
            
            btn_x += btn_width + btn_margin
