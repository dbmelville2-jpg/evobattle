"""
Creature Inspector UI - Display detailed creature information on click.

Shows comprehensive creature details including history, skills, personality,
relationships, and achievements in an interactive panel.
"""

import pygame
import os
from typing import Optional, List, Tuple
from ..models.creature import Creature
from ..models.history import EventType
from ..models.skills import SkillType
from ..models.relationships import RelationshipType
from ..models.attention import StimulusType
from ..utils.preferences import get_preferences


class CreatureInspector:
    """
    Interactive UI panel for inspecting creature details.
    
    Displays:
    - Basic stats and status
    - Personality traits
    - Skill proficiency
    - Battle history and statistics
    - Achievements and titles
    - Relationships
    - Recent event timeline
    """
    
    def __init__(self):
        """Initialize the creature inspector."""
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 28)
        self.header_font = pygame.font.Font(None, 22)
        self.text_font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 16)
        # store small font size for icon scaling
        self.small_font_size = self.small_font.get_height() or 16
        
        # Colors
        self.bg_color = (30, 30, 40, 230)
        self.header_color = (50, 50, 70)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 150, 255)
        self.stat_color = (150, 200, 255)
        self.warning_color = (255, 150, 100)
        self.success_color = (100, 255, 150)
        
        # Load optional raster icon assets (PNG/JPG) from assets/icons/
        self.icon_surfaces = {}
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            icons_dir = os.path.join(project_root, 'assets', 'icons')
            if os.path.isdir(icons_dir):
                for fname in os.listdir(icons_dir):
                    name, ext = os.path.splitext(fname)
                    key = name.lower()
                    if ext.lower() in ('.png', '.jpg', '.jpeg'):
                        path = os.path.join(icons_dir, fname)
                        try:
                            surf = pygame.image.load(path)

                            # Prefer to preserve whatever alpha the loaded image has.
                            # Only call convert_alpha() when a display surface exists (safe), otherwise
                            # keep the raw loaded Surface to avoid losing alpha (convert() can strip it).
                            try:
                                if pygame.display.get_init() and pygame.display.get_surface() is not None:
                                    try:
                                        surf = surf.convert_alpha()
                                    except Exception:
                                        # keep original surface if conversion fails
                                        pass
                            except Exception:
                                pass

                            # Store a couple normalized keys so lookups are forgiving (underscores/dashes)
                            normalized_keys = {key, key.replace('_', ''), key.replace('-', '')}

                            if os.getenv('DEBUG_CREATURE_INSPECTOR_SYMBOLS'):
                                print(f"Loaded icon: {fname} -> keys: {sorted(normalized_keys)}")

                            for nk in normalized_keys:
                                # avoid overwriting an existing better key
                                if nk not in self.icon_surfaces:
                                    self.icon_surfaces[nk] = surf
                        except Exception as e:
                            if os.getenv('DEBUG_CREATURE_INSPECTOR_SYMBOLS'):
                                print(f"Failed loading icon {fname}: {e}")
                            # Continue loading other icons even if one fails
                            continue
        except Exception:
            self.icon_surfaces = {}
        
        # State
        self.selected_creature: Optional[Creature] = None
        self.visible = False
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Panel dimensions (percentage of screen)
        self.panel_width_pct = 0.35  # 35% of screen width
        self.panel_height_pct = 0.85  # 85% of screen height
        self.margin = 20
        self.line_height = 20
        self.section_spacing = 15
        
        # Expanded hover area (pixels around panel to keep it visible)
        self.hover_padding = 30  # 30px padding around panel
        
        # Load preferences
        prefs = get_preferences()
        
        # Position and pinning
        self.is_pinned = prefs.get('inspector.pinned', False)
        self.position = prefs.get('inspector.position', None)  # Will be set on first render
        self.auto_hide_timeout = 3.0  # seconds
        self.auto_hide_timer = 0.0
    
        # Drag state
        self.dragging = False
        self.drag_offset = (0, 0)
        self.title_bar_rect = None
        
        # Animation
        self.alpha = 255 if self.visible else 0
        self.target_alpha = 255 if self.visible else 0
        self.animation_speed = 800  # alpha units per second
    
    def _render_symbol(self, surface: pygame.Surface, key_or_symbol: str, x: int, y: int, base_font: pygame.font.Font, color: Tuple[int, int, int, int]=None):
        """Render an icon image if available, otherwise draw text/symbol.
        Returns (w,h) of drawn area.
        """
        if color is None:
            color = self.text_color

        # If a loaded icon exists for this key, blit it scaled to small_font_size
        try:
            lookup = (key_or_symbol or '').lower()

            if os.getenv('DEBUG_CREATURE_INSPECTOR_SYMBOLS'):
                print(f"_render_symbol lookup: '{lookup}' (orig: '{key_or_symbol}')")

            if lookup in self.icon_surfaces:
                img = self.icon_surfaces[lookup]
                if os.getenv('DEBUG_CREATURE_INSPECTOR_SYMBOLS'):
                    try:
                        print(f"  Found surface for '{lookup}': size={img.get_size()} flags={img.get_flags()} alpha={img.get_alpha()}")
                    except Exception:
                        pass
                size = max(8, getattr(self, 'small_font_size', 16))
                # scale keeping aspect
                try:
                    img_s = pygame.transform.smoothscale(img, (size, size))
                except Exception:
                    img_s = pygame.transform.scale(img, (size, size))
                surface.blit(img_s, (x, y))
                return img_s.get_width(), img_s.get_height()
            else:
                if os.getenv('DEBUG_CREATURE_INSPECTOR_SYMBOLS'):
                    print(f"  No surface for '{lookup}'. Available keys: {sorted(list(self.icon_surfaces.keys()))[:20]}")
        except Exception as e:
            if os.getenv('DEBUG_CREATURE_INSPECTOR_SYMBOLS'):
                print(f"_render_symbol error for '{key_or_symbol}': {e}")
            pass

        # Fallback to text rendering
        use_color = color
        if isinstance(color, (list, tuple)) and len(color) == 4:
            use_color = color[:3]
        try:
            rendered = base_font.render(key_or_symbol, True, use_color)
            surface.blit(rendered, (x, y))
            return rendered.get_width(), rendered.get_height()
        except Exception:
            return 0, 0
    
    def select_creature(self, creature: Optional[Creature]):
        """
        Select a creature to inspect.
        
        Args:
            creature: The creature to inspect, or None to deselect
        """
        self.selected_creature = creature
        if creature is not None:
            self.show()
        self.scroll_offset = 0
    
    def show(self):
        """Show the inspector panel with animation."""
        self.visible = True
        self.target_alpha = 255
        self.auto_hide_timer = 0.0
    
    def hide(self):
        """Hide the inspector panel with animation."""
        self.visible = False
        self.target_alpha = 0
    
    def toggle_visibility(self):
        """Toggle inspector visibility."""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def toggle_pin(self):
        """Toggle pinned state."""
        self.is_pinned = not self.is_pinned
        prefs = get_preferences()
        prefs.set('inspector.pinned', self.is_pinned)
        if self.is_pinned:
            self.auto_hide_timer = 0.0
    
    def update(self, dt: float):
        """
        Update inspector state (animations, auto-hide, etc.).
        
        Args:
            dt: Delta time in seconds
        """
        # Update alpha animation
        if self.alpha < self.target_alpha:
            self.alpha = min(self.target_alpha, self.alpha + self.animation_speed * dt)
        elif self.alpha > self.target_alpha:
            self.alpha = max(self.target_alpha, self.alpha - self.animation_speed * dt)
        
        # Auto-hide logic (if not pinned and visible)
        if self.visible and not self.is_pinned and self.auto_hide_timeout > 0:
            # Check if mouse is hovering over the panel (with expanded hover area)
            if self._is_mouse_over_panel():
                self.auto_hide_timer = 0.0
            else:
                self.auto_hide_timer += dt
                if self.auto_hide_timer >= self.auto_hide_timeout:
                    self.hide()
    
    def _is_mouse_over_panel(self) -> bool:
        """
        Check if mouse is over the inspector panel or within the expanded hover area.
        
        Returns:
            True if mouse is over panel (with padding), False otherwise
        """
        if not self.visible or self.position is None:
            return False
        
        # Get current screen to calculate dimensions
        try:
            screen = pygame.display.get_surface()
            if screen is None:
                return False
            
            screen_width, screen_height = screen.get_size()
            panel_width = int(screen_width * self.panel_width_pct)
            panel_height = int(screen_height * self.panel_height_pct)
            
            panel_x, panel_y = self.position
            
            # Create expanded rect with hover padding
            hover_rect = pygame.Rect(
                panel_x - self.hover_padding,
                panel_y - self.hover_padding,
                panel_width + (self.hover_padding * 2),
                panel_height + (self.hover_padding * 2)
            )
            
            mouse_pos = pygame.mouse.get_pos()
            return hover_rect.collidepoint(mouse_pos)
        except:
            return False
    
    def handle_scroll(self, direction: int):
        """
        Handle scroll input.
        
        Args:
            direction: -1 for up, 1 for down
        """
        scroll_speed = 20
        self.scroll_offset = max(0, min(self.max_scroll, 
                                       self.scroll_offset + direction * scroll_speed))
        # Reset auto-hide timer on interaction
        if self.visible:
            self.auto_hide_timer = 0.0
    
    def handle_mouse_event(self, event: pygame.event.Event, screen: pygame.Surface) -> bool:
        """
        Handle mouse events for dragging and interaction.
        
        Args:
            event: Pygame event
            screen: Screen surface (for bounds checking)
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible or self.alpha < 10:
            return False
        
        screen_width, screen_height = screen.get_size()
        panel_width = int(screen_width * self.panel_width_pct)
        panel_height = int(screen_height * self.panel_height_pct)
        
        # Set default position if not set
        if self.position is None:
            self.position = (screen_width - panel_width - 20, (screen_height - panel_height) // 2)
        
        panel_x, panel_y = self.position
        
        # Title bar for dragging
        title_bar_height = 35
        self.title_bar_rect = pygame.Rect(panel_x, panel_y, panel_width, title_bar_height)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check pin button click FIRST (before title bar, since it's inside the title bar)
            pin_button_rect = pygame.Rect(panel_x + panel_width - 60, panel_y + 5, 25, 25)
            if pin_button_rect.collidepoint(mouse_pos):
                self.toggle_pin()
                return True
            
            # Check close button click FIRST (before title bar, since it's inside the title bar)
            close_button_rect = pygame.Rect(panel_x + panel_width - 30, panel_y + 5, 25, 25)
            if close_button_rect.collidepoint(mouse_pos):
                self.hide()
                return True
            
            # Check title bar for dragging (only if buttons weren't clicked)
            if self.title_bar_rect.collidepoint(mouse_pos):
                self.dragging = True
                self.drag_offset = (mouse_pos[0] - panel_x, mouse_pos[1] - panel_y)
                self.auto_hide_timer = 0.0
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                # Saved position
                prefs = get_preferences()
                prefs.set('inspector.position', self.position)
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_pos = pygame.mouse.get_pos()
                new_x = mouse_pos[0] - self.drag_offset[0]
                new_y = mouse_pos[1] - self.drag_offset[1]
                
                # Keep within screen bounds
                new_x = max(0, min(new_x, screen_width - panel_width))
                new_y = max(0, min(new_y, screen_height - panel_height))
                
                self.position = (new_x, new_y)
                return True
            
            # Check if mouse is over panel with expanded hover area (reset auto-hide)
            hover_rect = pygame.Rect(
                panel_x - self.hover_padding,
                panel_y - self.hover_padding,
                panel_width + (self.hover_padding * 2),
                panel_height + (self.hover_padding * 2)
            )
            if hover_rect.collidepoint(pygame.mouse.get_pos()):
                self.auto_hide_timer = 0.0
        
        return False
    
    def _ensure_icons_converted(self):
        """
        Convert loaded icon surfaces with convert_alpha() once a display surface exists.
        This handles the case where the inspector was instantiated before the pygame display
        was initialized so images were loaded but not converted for the display format.
        """
        try:
            if not (pygame.display.get_init() and pygame.display.get_surface() is not None):
                return
            for key, surf in list(self.icon_surfaces.items()):
                try:
                    # if surf already has same format this will be cheap; otherwise convert_alpha() makes blitting correct
                    conv = surf.convert_alpha()
                    self.icon_surfaces[key] = conv
                except Exception:
                    # ignore failures and keep the original surface
                    pass
        except Exception:
            pass

    def render(self, screen: pygame.Surface):
        """
        Render the inspector panel.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Ensure icons are converted to the display format (if needed)
        self._ensure_icons_converted()
        # Don't render if completely invisible
        if self.alpha < 1:
            return
        
        if not self.selected_creature:
            return
        
        # Handle both Creature and BattleCreature objects
        # If it's a BattleCreature, extract the Creature for display
        battle_creature = None
        if hasattr(self.selected_creature, 'creature'):
            # It's a BattleCreature wrapper
            battle_creature = self.selected_creature
            creature = self.selected_creature.creature
        else:
            # It's a plain Creature
            creature = self.selected_creature
        
        screen_width, screen_height = screen.get_size()
        
        # Calculate panel dimensions
        panel_width = int(screen_width * self.panel_width_pct)
        panel_height = int(screen_height * self.panel_height_pct)
        
        # Set default position if not set
        if self.position is None:
            self.position = (screen_width - panel_width - 20, (screen_height - panel_height) // 2)
        
        panel_x, panel_y = self.position
        
        # Create panel surface with transparency based on alpha
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # Apply alpha to background
        bg_color = (*self.bg_color[:3], int(self.bg_color[3] * self.alpha / 255))
        panel.fill(bg_color)
        
        # Draw border with alpha
        border_color = (*self.highlight_color, int(255 * self.alpha / 255))
        pygame.draw.rect(panel, border_color, panel.get_rect(), 2)
        
        # Draw title bar (for dragging)
        title_bar_height = 35
        title_bar_color = (*self.header_color, int(200 * self.alpha / 255))
        title_bar_rect = pygame.Rect(0, 0, panel_width, title_bar_height)
        pygame.draw.rect(panel, title_bar_color, title_bar_rect)
        
        # Title bar text
        title_bar_text = self.text_font.render(
            f"Inspector: {creature.name}",
            True,
            (*self.text_color, int(255 * self.alpha / 255))
        )
        panel.blit(title_bar_text, (10, 8))
        
        # Pin button (use loaded icon if available)
        pin_x = panel_width - 60
        pin_y = 5
        pin_size = 25
        pin_color = self.success_color if self.is_pinned else (150, 150, 150)
        pin_key = 'pin' if self.is_pinned else 'circle'
        
        # Check if mouse is hovering over pin button
        mouse_pos = pygame.mouse.get_pos()
        pin_button_rect = pygame.Rect(panel_x + pin_x, panel_y + pin_y, pin_size, pin_size)
        pin_hovered = pin_button_rect.collidepoint(mouse_pos) if self.visible else False
        
        # Draw pin button background with hover effect
        pin_bg_alpha = 150 if pin_hovered else 100
        pin_bg_color = (*pin_color, int(pin_bg_alpha * self.alpha / 255))
        pygame.draw.circle(panel, pin_bg_color, (pin_x + pin_size // 2, pin_y + pin_size // 2), pin_size // 2)
        if pin_hovered:
            # Draw border on hover
            pygame.draw.circle(panel, (*pin_color, int(255 * self.alpha / 255)), 
                             (pin_x + pin_size // 2, pin_y + pin_size // 2), pin_size // 2, 2)
        self._render_symbol(panel, pin_key, pin_x + 3, pin_y + 3, self.text_font, (*pin_color, int(255 * self.alpha / 255)))
        
        # Close button with enhanced visuals
        close_x = panel_width - 30
        close_y = 5
        close_size = 25
        
        # Check if mouse is hovering over close button
        close_button_rect = pygame.Rect(panel_x + close_x, panel_y + close_y, close_size, close_size)
        close_hovered = close_button_rect.collidepoint(mouse_pos) if self.visible else False
        
        # Draw close button background with hover effect
        close_bg_alpha = 180 if close_hovered else 120
        close_bg_color = (*self.warning_color, int(close_bg_alpha * self.alpha / 255))
        pygame.draw.circle(panel, close_bg_color, (close_x + close_size // 2, close_y + close_size // 2), close_size // 2)
        if close_hovered:
            # Draw brighter border on hover
            pygame.draw.circle(panel, (255, 200, 200, int(255 * self.alpha / 255)), 
                             (close_x + close_size // 2, close_y + close_size // 2), close_size // 2, 2)
        
        # Draw X symbol
        x_color = (255, 255, 255, int(255 * self.alpha / 255))
        x_offset = 7
        x_size = 11
        # Top-left to bottom-right
        pygame.draw.line(panel, x_color, 
                        (close_x + x_offset, close_y + x_offset),
                        (close_x + x_offset + x_size, close_y + x_offset + x_size), 2)
        # Top-right to bottom-left
        pygame.draw.line(panel, x_color,
                        (close_x + x_offset + x_size, close_y + x_offset),
                        (close_x + x_offset, close_y + x_offset + x_size), 2)
        
        # Render content with scrolling
        content_surface = self._render_content(creature, panel_width, battle_creature)
        
        # Calculate max scroll
        self.max_scroll = max(0, content_surface.get_height() - panel_height + title_bar_height + 10)
        
        # Create a clipping area for content
        content_y = title_bar_height
        content_height = panel_height - title_bar_height
        
        # Set clipping rect to prevent content from drawing outside the content area
        clip_rect = pygame.Rect(0, content_y, panel_width, content_height)
        panel.set_clip(clip_rect)
        
        # Blit scrolled content
        panel.blit(content_surface, (0, content_y - self.scroll_offset))
        
        # Clear clipping rect
        panel.set_clip(None)
        
        # Draw scroll indicators if needed
        if self.max_scroll > 0:
            indicator_color = (*self.highlight_color, int(255 * self.alpha / 255))
            if self.scroll_offset > 0:
                # Up arrow
                pygame.draw.polygon(panel, indicator_color, [
                    (panel_width - 20, content_y + 15),
                    (panel_width - 10, content_y + 25),
                    (panel_width - 30, content_y + 25)
                ])
            if self.scroll_offset < self.max_scroll:
                # Down arrow
                pygame.draw.polygon(panel, indicator_color, [
                    (panel_width - 20, panel_height - 15),
                    (panel_width - 10, panel_height - 25),
                    (panel_width - 30, panel_height - 25)
                ])
        
        # Draw to screen
        screen.blit(panel, (panel_x, panel_y))
        
        # Draw control hints below panel
        hint_y = panel_y + panel_height + 5
        hints = [
            "I - Toggle  •  Click title to drag",
            f"{'📌 Pinned' if self.is_pinned else 'Auto-hide in ' + str(max(0, int(self.auto_hide_timeout - self.auto_hide_timer))) + 's'}"
        ]
        
        for i, hint in enumerate(hints):
            hint_text = self.small_font.render(
                hint,
                True,
                (200, 200, 200, int(200 * self.alpha / 255))
            )
            screen.blit(hint_text, (panel_x + 10, hint_y + i * 18))
    
    def _render_content(self, creature: Creature, panel_width: int, battle_creature=None) -> pygame.Surface:
        """
        Render all content for the inspector panel.
        
        Args:
            creature: The creature to display
            panel_width: Width of the panel
            battle_creature: Optional BattleCreature wrapper for accessing attention system
            
        Returns:
            Surface with all content rendered
        """
        # Estimate height (will create larger surface if needed)
        estimated_height = 2000
        content = pygame.Surface((panel_width, estimated_height), pygame.SRCALPHA)
        
        y = self.margin
        x_margin = self.margin
        content_width = panel_width - (2 * x_margin)
        
        # Title - Creature Name
        title = self.title_font.render(creature.name, True, self.highlight_color)
        content.blit(title, (x_margin, y))
        y += title.get_height() + 5
        
        # Subtitle - Level and Type
        subtitle = self.text_font.render(
            f"Level {creature.level} {creature.creature_type.name}",
            True, self.text_color
        )
        content.blit(subtitle, (x_margin, y))
        y += subtitle.get_height() + self.section_spacing
        
        # === Current Focus ===
        # Get attention system from battle_creature if available
        attention = None
        if battle_creature and hasattr(battle_creature, 'attention'):
            attention = battle_creature.attention
        elif hasattr(creature, 'attention'):
            attention = creature.attention
        
        if attention and hasattr(attention, 'current_focus'):
            current_focus = attention.current_focus
            focus_text = f"Focus: {current_focus.value.upper()}"
            
            # Color code the focus
            focus_color = self.text_color
            if current_focus == StimulusType.COMBAT:
                focus_color = (255, 100, 100) # Red
            elif current_focus == StimulusType.FORAGING:
                focus_color = (100, 255, 100) # Green
            elif current_focus == StimulusType.FLEEING:
                focus_color = (255, 200, 50) # Orange
            elif current_focus == StimulusType.HAZARD_AVOIDANCE:
                focus_color = (255, 150, 50) # Orange-red
            elif current_focus == StimulusType.SOCIAL:
                focus_color = (255, 100, 255) # Pink
            elif current_focus == StimulusType.EXPLORING:
                focus_color = (100, 200, 255) # Blue
                
            focus_surf = self.text_font.render(focus_text, True, focus_color)
            content.blit(focus_surf, (x_margin, y))
            y += focus_surf.get_height() + self.section_spacing
        
        # === Stats Section ===
        y = self._render_section_header(content, "Stats", x_margin, y)
        
        hp_pct = (creature.stats.hp / creature.stats.max_hp * 100) if creature.stats.max_hp > 0 else 0
        hp_color = self.success_color if hp_pct > 70 else self.warning_color if hp_pct > 30 else (255, 50, 50)
        
        stats_lines = [
            f"HP: {creature.stats.hp:.0f}/{creature.stats.max_hp} ({hp_pct:.0f}%)",
            f"Attack: {creature.stats.attack}  Defense: {creature.stats.defense}",
            f"Speed: {creature.stats.speed}  Energy: {creature.energy}/{creature.max_energy}"
        ]
        
        for i, line in enumerate(stats_lines):
            color = hp_color if i == 0 else self.stat_color
            text = self.text_font.render(line, True, color)
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        y += self.section_spacing
        
        # === Health & Injuries Section ===
        y = self._render_section_header(content, "Health & Injuries", x_margin, y)
        
        # === Disease Status ===
        if hasattr(creature, 'active_infection') and creature.active_infection:
            infection = creature.active_infection
            disease = infection.disease
            
            # Disease Name
            name_text = self.text_font.render(f"⚠ Infected: {disease.name}", True, (255, 100, 100))
            content.blit(name_text, (x_margin + 10, y))
            y += self.line_height
            
            # Stage
            stage_text = self.small_font.render(f"Stage: {infection.stage.name}", True, (255, 150, 150))
            content.blit(stage_text, (x_margin + 20, y))
            y += self.line_height
            
            # Effects
            if infection.stage.name == 'SYMPTOMATIC':
                effects = []
                if disease.hp_drain_rate > 0:
                    effects.append(f"HP Drain: -{disease.hp_drain_rate}/s")
                if disease.stat_penalty > 0:
                    effects.append(f"Stats: -{int(disease.stat_penalty * 100)}%")
                    
                if effects:
                    effect_str = ", ".join(effects)
                    effect_text = self.small_font.render(effect_str, True, (255, 100, 100))
                    content.blit(effect_text, (x_margin + 20, y))
                    y += self.line_height
            
            y += 5  # Spacing
            
        tracker = creature.injury_tracker
        
        # Overall injury statistics
        total_damage = tracker.get_total_damage_received()
        near_deaths = tracker.near_death_count
        criticals = tracker.critical_hits_received
        survival_rate = tracker.get_survival_rate()
        
        injury_stats = [
            f"Total Damage Taken: {total_damage:.0f}",
            f"Near-Death Experiences: {near_deaths}",
            f"Critical Hits Taken: {criticals}",
            f"Survival Rate: {survival_rate:.1f}%"
        ]
        
        for line in injury_stats:
            color = self.warning_color if "Near-Death" in line or "Critical" in line else self.stat_color
            text = self.text_font.render(line, True, color)
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        # Most dangerous attacker
        most_dangerous = tracker.get_most_dangerous_attacker()
        if most_dangerous:
            danger_line = f"Most Dangerous Foe: {most_dangerous.attacker_name} ({most_dangerous.total_damage:.0f} dmg)"
            danger_text = self.small_font.render(danger_line, True, self.warning_color)
            content.blit(danger_text, (x_margin + 10, y))
            y += self.line_height
        
        # Recent injuries
        recent_injuries = tracker.get_recent_injuries(3)
        if recent_injuries:
            recent_header = self.small_font.render("Recent Injuries:", True, self.text_color)
            content.blit(recent_header, (x_margin + 10, y))
            y += self.line_height
            
            for injury in recent_injuries:
                hp_after_pct = injury.health_percentage_after(tracker.max_hp)
                crit_mark = " [CRIT]" if injury.was_critical else ""
                injury_line = f"  • {injury.damage_amount:.0f} dmg from {injury.attacker_name}{crit_mark} → {hp_after_pct:.0f}% HP"
                injury_color = (255, 100, 100) if injury.was_critical else (200, 150, 150)
                injury_text = self.small_font.render(injury_line, True, injury_color)
                content.blit(injury_text, (x_margin + 15, y))
                y += self.line_height - 2
        
        y += self.section_spacing
        
        # === Personality Section ===
        y = self._render_section_header(content, "Personality", x_margin, y)
        
        personality_text = creature.personality.get_description()
        y = self._render_wrapped_text(content, personality_text, x_margin + 10, y, 
                                       content_width - 20, self.text_font, self.text_color)
        
        combat_style = f"Combat Style: {creature.personality.get_combat_style()}"
        style_text = self.small_font.render(combat_style, True, self.stat_color)
        content.blit(style_text, (x_margin + 10, y))
        y += self.line_height + self.section_spacing
        
        # === Traits Section ===
        y = self._render_section_header(content, "Genetic Traits", x_margin, y)
        
        if creature.traits:
            for trait in creature.traits[:8]:  # Show up to 8 traits
                # Trait name with rarity indicator
                rarity_colors = {
                    'common': (200, 200, 200),
                    'uncommon': (100, 200, 100),
                    'rare': (100, 150, 255),
                    'legendary': (255, 215, 0)
                }
                trait_color = rarity_colors.get(trait.rarity, self.text_color)

                # Draw a small colored square for rarity instead of a unicode marker
                square_size = 10
                square_x = x_margin + 10
                square_y = y + max(0, (self.line_height - square_size) // 2)
                try:
                    pygame.draw.rect(content, trait_color, pygame.Rect(square_x, square_y, square_size, square_size))
                except Exception:
                    # fallback: no-op if draw fails
                    pass

                # Trait name
                name_x = square_x + square_size + 6
                name_surf = self.text_font.render(trait.name, True, trait_color)
                content.blit(name_surf, (name_x, y))
                y += name_surf.get_height() + 2

                # Provenance / source (if available)
                if hasattr(trait, 'provenance') and trait.provenance:
                    prov_text = f"{trait.provenance.source_type.title()}"
                    if getattr(trait.provenance, 'generation', 0) > 0:
                        prov_text += f" (Gen {trait.provenance.generation})"
                    prov_render = self.small_font.render(prov_text, True, (150, 150, 150))
                    content.blit(prov_render, (name_x, y))
                    y += self.line_height - 2

                # Numeric modifiers: show positive/negative effects (e.g. +15% attack)
                try:
                    mods = []
                    # strength
                    if hasattr(trait, 'strength_modifier') and trait.strength_modifier is not None:
                        delta = (float(trait.strength_modifier) - 1.0) * 100.0
                        if abs(delta) >= 0.5:
                            mods.append((f"Atk {delta:+.0f}%", delta))
                    # speed
                    if hasattr(trait, 'speed_modifier') and trait.speed_modifier is not None:
                        delta = (float(trait.speed_modifier) - 1.0) * 100.0
                        if abs(delta) >= 0.5:
                            mods.append((f"Spd {delta:+.0f}%", delta))
                    # defense
                    if hasattr(trait, 'defense_modifier') and trait.defense_modifier is not None:
                        delta = (float(trait.defense_modifier) - 1.0) * 100.0
                        if abs(delta) >= 0.5:
                            mods.append((f"Def {delta:+.0f}%", delta))

                    if mods:
                        # Render modifiers inline as small labels
                        mod_x = name_x
                        for mod_text, mod_val in mods:
                            mod_color = (100, 255, 150) if mod_val > 0 else (255, 150, 100)
                            mod_surf = self.small_font.render(mod_text, True, mod_color)
                            content.blit(mod_surf, (mod_x, y))
                            mod_x += mod_surf.get_width() + 8
                        y += self.line_height - 2
                except Exception:
                    pass

                # Full trait description (wrapped)
                desc = trait.description if hasattr(trait, 'description') and trait.description else ''
                if desc:
                    wrap_x = name_x
                    wrap_width = content_width - (wrap_x - x_margin) - 10
                    y = self._render_wrapped_text(content, desc, wrap_x, y, wrap_width, self.small_font, (200, 200, 200))
                    y += 4
        else:
            text = self.small_font.render("No special traits", True, (150, 150, 150))
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        y += self.section_spacing
        
        # === Skills Section ===
        y = self._render_section_header(content, "Skills", x_margin, y)
        
        top_skills = creature.skills.get_highest_skills(5)
        if top_skills:
            for skill_type, level in top_skills:
                skill = creature.skills.get_skill(skill_type)
                prof = skill.get_proficiency().value
                skill_line = f"{skill.config.name}: Lv.{level} ({prof})"
                
                # Color based on proficiency
                if level >= 80:
                    color = (255, 215, 0)  # Gold for legendary
                elif level >= 60:
                    color = (200, 100, 255)  # Purple for master
                elif level >= 40:
                    color = (100, 200, 255)  # Blue for expert
                else:
                    color = self.text_color
                
                text = self.text_font.render(skill_line, True, color)
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
        else:
            text = self.small_font.render("No skills developed yet", True, (150, 150, 150))
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        y += self.section_spacing
        
        # === Battle History Section ===
        y = self._render_section_header(content, "Battle Record", x_margin, y)
        
        history = creature.history
        win_rate = history.get_win_rate() * 100
        
        history_lines = [
            f"Battles: {history.battles_fought} ({history.battles_won}W-{history.battles_fought - history.battles_won}L)",
            f"Win Rate: {win_rate:.1f}%",
            f"Kills: {len(history.kills)}  Deaths: {history.deaths}",
            f"Damage: {history.total_damage_dealt:.0f} dealt, {history.total_damage_received:.0f} taken"
        ]
        
        for line in history_lines:
            text = self.text_font.render(line, True, self.stat_color)
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        if history.deaths > 0:
            kd = history.get_kill_death_ratio()
            kd_text = self.text_font.render(f"K/D Ratio: {kd:.2f}", True, self.stat_color)
            content.blit(kd_text, (x_margin + 10, y))
            y += self.line_height
        
        y += self.section_spacing
        
        # === Achievements Section ===
        if history.achievements:
            y = self._render_section_header(content, "Achievements", x_margin, y)
            
            for achievement in history.achievements[:5]:  # Show top 5
                # Star rating based on rarity
                stars = "⭐" * int(achievement.rarity * 5)
                ach_text = f"{stars} {achievement.name}"
                text = self.text_font.render(ach_text, True, (255, 215, 0))
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
                
                # Description
                desc = self.small_font.render(achievement.description, True, (200, 200, 200))
                content.blit(desc, (x_margin + 20, y))
                y += self.line_height
            
            y += self.section_spacing
        
        # === Titles Section ===
        if history.titles:
            y = self._render_section_header(content, "Titles", x_margin, y)
            
            titles_str = ", ".join(history.titles)
            y = self._render_wrapped_text(content, titles_str, x_margin + 10, y,
                                         content_width - 20, self.text_font, (255, 215, 0))
            y += self.section_spacing
        
        # === Relationships Section ===
        allies = creature.relationships.get_allies()
        enemies = creature.relationships.get_enemies()
        family = creature.relationships.get_family()
        
        if allies or enemies or family:
            y = self._render_section_header(content, "Relationships", x_margin, y)
            
            # Display social traits first
            social_desc = f"Traits: {creature.social_traits.get_description()}"
            trait_text = self.small_font.render(social_desc, True, self.stat_color)
            content.blit(trait_text, (x_margin + 10, y))
            y += self.line_height + 3
            
            if family:
                text = self.text_font.render(f"Family: {len(family)}", True, self.success_color)
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
                # Show first family member with metrics
                if len(family) > 0:
                    rel = family[0]
                    coop = rel.metrics.get_cooperation_score() if rel.metrics else 0
                    detail = self.small_font.render(
                        f"  • {rel.relationship_type.value} (Coop: {coop:.2f})",
                        True, (200, 200, 200)
                    )
                    content.blit(detail, (x_margin + 15, y))
                    y += self.line_height - 2
            
            if allies:
                text = self.text_font.render(f"Allies: {len(allies)}", True, (100, 200, 255))
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
            
            if enemies:
                text = self.text_font.render(f"Rivals/Enemies: {len(enemies)}", True, (255, 100, 100))
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
            
            # Show revenge targets specifically
            revenge_targets = creature.relationships.get_revenge_targets()
            if revenge_targets:
                text = self.text_font.render(f"Revenge Targets: {len(revenge_targets)}", True, (255, 50, 50))
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
            
            y += self.section_spacing
        
        # === Social Interactions Section ===
        y = self._render_section_header(content, "Social Interactions", x_margin, y)
        
        interactions = creature.interaction_tracker
        summary = interactions.get_interaction_summary()
        
        interaction_stats = [
            f"Total Interactions: {summary['total_interactions']}",
            f"Food Competitions: {summary['food_competitions']} ({summary['food_competitions_won']}W)",
            f"Mating Attempts: {summary['mating_attempts']} ({summary['successful_matings']} success)",
        ]
        
        for line in interaction_stats:
            text = self.text_font.render(line, True, self.stat_color)
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        # Win rates
        food_win_rate = interactions.get_food_competition_win_rate() * 100
        mating_success_rate = interactions.get_mating_success_rate() * 100
        
        win_rate_line = f"Competition Win Rate: {food_win_rate:.1f}%"
        win_text = self.small_font.render(win_rate_line, True, self.success_color if food_win_rate > 50 else self.warning_color)
        content.blit(win_text, (x_margin + 10, y))
        y += self.line_height
        
        if summary['mating_attempts'] > 0:
            mating_line = f"Mating Success Rate: {mating_success_rate:.1f}%"
            mating_text = self.small_font.render(mating_line, True, self.success_color if mating_success_rate > 50 else self.warning_color)
            content.blit(mating_text, (x_margin + 10, y))
            y += self.line_height
        
        # Most frequent partner
        frequent_partner = interactions.get_most_frequent_partner()
        if frequent_partner:
            partner_line = f"Most Frequent Interaction: {frequent_partner.partner_name}"
            partner_text = self.small_font.render(partner_line, True, self.highlight_color)
            content.blit(partner_text, (x_margin + 10, y))
            y += self.line_height
        
        y += self.section_spacing
        
        # === Recent Events Section ===
        y = self._render_section_header(content, "Recent Events", x_margin, y)
        
        recent_events = history.get_recent_events(8)
        if recent_events:
            for event in recent_events:
                # Event type indicator (use loaded icon if available)
                event_icon_key_or_symbol = self._get_event_icon(event.event_type)
                self._render_symbol(content, event_icon_key_or_symbol, x_margin + 10, y, self.small_font, self.highlight_color)
                
                # Event description
                desc = self.small_font.render(event.description[:50], True, self.text_color)
                content.blit(desc, (x_margin + 30, y))
                y += self.line_height
        else:
            text = self.small_font.render("No events recorded", True, (150, 150, 150))
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        y += self.margin
        
        # Crop content to actual used height
        actual_content = pygame.Surface((panel_width, y), pygame.SRCALPHA)
        actual_content.blit(content, (0, 0))
        
        return actual_content
    
    def _render_section_header(self, surface: pygame.Surface, title: str, x: int, y: int) -> int:
        """
        Render a section header.
        
        Args:
            surface: Surface to draw on
            title: Header title
            x: X position
            y: Y Position
            
        Returns:
            New Y position after header
        """
        # Draw header background
        header_rect = pygame.Rect(x, y, surface.get_width() - 2 * x, 25)
        pygame.draw.rect(surface, self.header_color, header_rect)
        
        # Draw header text
        text = self.header_font.render(title, True, self.text_color)
        surface.blit(text, (x + 5, y + 3))
        
        return y + 30
    
    def _render_wrapped_text(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        max_width: int,
        font: pygame.font.Font,
        color: tuple
    ) -> int:
        """
        Render text with word wrapping.
        
        Args:
            surface: Surface to draw on
            text: Text to render
            x: X position
            y: Starting Y position
            max_width: Maximum width before wrapping
            font: Font to use
            color: Text color
            
        Returns:
            Final Y position after text
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines:
            line_surface = font.render(line, True, color)
            surface.blit(line_surface, (x, y))
            y += self.line_height
        
        return y
    
    def _get_event_icon(self, event_type: EventType) -> str:
        """
        Get an icon key for an event type. Prefer raster icon keys (PNG) if available.
        Returns a key that `_render_symbol` will look up. Falls back to a simple ASCII marker
        to avoid relying on system emoji fonts which often render as empty squares.
        """
        # common ascii/text fallbacks
        ascii_fallbacks = {
            EventType.BIRTH: "(birth)",
            EventType.DEATH: "(death)",
            EventType.BATTLE_START: "(battle)",
            EventType.BATTLE_WIN: "(win)",
            EventType.BATTLE_LOSS: "(loss)",
            EventType.ATTACK: "(attack)",
            EventType.CRITICAL_HIT: "(crit)",
            EventType.KILL: "(kill)",
            EventType.REVENGE_KILL: "(revenge)",
            EventType.OFFSPRING_BORN: "(offspring)",
            EventType.FIRST_KILL: "(first)",
            EventType.MILESTONE_REACHED: "(milestone)",
        }

        key = event_type.name.lower()
        # Try several normalized variants so filename matching is forgiving
        candidates = [key, key.replace('_', ''), key.replace('_', '-'), key.replace('-', ''), key.replace('-', '_')]
        for c in candidates:
            if c in self.icon_surfaces:
                return c

        # Event-specific preferred names (try these before general fallbacks)
        event_preferred = {
            EventType.BATTLE_START: ['battle_start', 'battle', 'battle-start', 'battlestart', 'attack'],
            EventType.BATTLE_WIN: ['battle_win', 'win', 'trophy', 'star'],
            EventType.BATTLE_LOSS: ['battle_loss', 'loss', 'heart', 'brokenheart'],
            EventType.ATTACK: ['attack', 'strike', 'slash'],
            EventType.CRITICAL_HIT: ['critical_hit', 'critical', 'crit', 'explode'],
            EventType.KILL: ['kill', 'skull', 'dagger'],
            EventType.REVENGE_KILL: ['revenge_kill', 'revenge', 'skull'],
            EventType.BIRTH: ['birth', 'offspring', 'baby'],
            EventType.OFFSPRING_BORN: ['offspring_born', 'offspring', 'baby'],
            EventType.DEATH: ['death', 'skull'],
            EventType.FIRST_KILL: ['first_kill', 'first', 'milestone'],
            EventType.MILESTONE_REACHED: ['milestone', 'star', 'trophy']
        }

        prefs = event_preferred.get(event_type, [])
        for alt in prefs:
            alt_norms = [alt, alt.replace('_', ''), alt.replace('-', ''), alt.replace('-', '_')]
            for a in alt_norms:
                if a in self.icon_surfaces:
                    return a

        # Also try some obvious general semantic names (ordered to avoid choosing 'birth' for battle)
        semantic_alts = [
            'battle', 'win', 'loss', 'attack', 'critical', 'kill', 'revenge', 'offspring', 'first', 'milestone',
            'star', 'family', 'pin', 'circle', 'diamond', 'dna', 'birth', 'death'
        ]
        for alt in semantic_alts:
            if alt in self.icon_surfaces:
                return alt

        # No raster icon available — return a short ascii fallback
        return ascii_fallbacks.get(event_type, "•")
