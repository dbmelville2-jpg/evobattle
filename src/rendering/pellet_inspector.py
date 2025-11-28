"""
Pellet Inspector UI - Display detailed pellet information on click.

Shows comprehensive pellet details including lifecycle history, targeting statistics,
traits, and lineage information.
"""

import pygame
from typing import Optional


class PelletInspector:
    """
    Interactive UI panel for inspecting pellet details.
    
    Displays:
    - Basic traits and status
    - Lifecycle events timeline
    - Targeting and avoidance statistics
    - Lineage and offspring information
    - Creature interaction details
    """
    
    def __init__(self):
        """Initialize the pellet inspector."""
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 28)
        self.header_font = pygame.font.Font(None, 22)
        self.text_font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 16)
        
        # Colors
        self.bg_color = (40, 30, 40, 230)
        self.header_color = (60, 50, 60)
        self.text_color = (255, 255, 255)
        self.highlight_color = (150, 255, 150)
        self.stat_color = (200, 255, 200)
        self.warning_color = (255, 200, 150)
        
        # State
        self.selected_pellet = None
        self.visible = False
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Panel dimensions (percentage of screen)
        self.panel_width_pct = 0.30
        self.panel_height_pct = 0.75
        self.margin = 15
        self.line_height = 20
        self.section_spacing = 12
        
        # Position
        self.position = None  # Will be set on first render
        
        # Animation
        self.alpha = 255 if self.visible else 0
        self.target_alpha = 255 if self.visible else 0
        self.animation_speed = 800
    
    def select_pellet(self, pellet):
        """
        Select a pellet to inspect.
        
        Args:
            pellet: The pellet to inspect, or None to deselect
        """
        self.selected_pellet = pellet
        if pellet is not None:
            self.show()
        self.scroll_offset = 0
    
    def show(self):
        """Show the inspector panel."""
        self.visible = True
        self.target_alpha = 255
    
    def hide(self):
        """Hide the inspector panel."""
        self.visible = False
        self.target_alpha = 0
    
    def toggle_visibility(self):
        """Toggle inspector visibility."""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def update(self, dt: float):
        """
        Update inspector state (animations).
        
        Args:
            dt: Delta time in seconds
        """
        # Update alpha animation
        if self.alpha < self.target_alpha:
            self.alpha = min(self.target_alpha, self.alpha + self.animation_speed * dt)
        elif self.alpha > self.target_alpha:
            self.alpha = max(self.target_alpha, self.alpha - self.animation_speed * dt)
    
    def handle_scroll(self, direction: int):
        """
        Handle scroll input.
        
        Args:
            direction: -1 for up, 1 for down
        """
        scroll_speed = 20
        self.scroll_offset = max(0, min(self.max_scroll, 
                                       self.scroll_offset + direction * scroll_speed))
    
    def handle_mouse_event(self, event: pygame.event.Event, screen: pygame.Surface) -> bool:
        """
        Handle mouse events.
        
        Args:
            event: Pygame event
            screen: Screen surface
            
        Returns:
            True if event was handled
        """
        if not self.visible or self.alpha < 10:
            return False
        
        screen_width, screen_height = screen.get_size()
        panel_width = int(screen_width * self.panel_width_pct)
        
        if self.position is None:
            self.position = (20, (screen_height - int(screen_height * self.panel_height_pct)) // 2)
        
        panel_x, panel_y = self.position
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            # Close button
            close_button_rect = pygame.Rect(panel_x + panel_width - 30, panel_y + 5, 25, 25)
            if close_button_rect.collidepoint(mouse_pos):
                self.hide()
                return True
        
        return False
    
    def render(self, screen: pygame.Surface):
        """
        Render the inspector panel.
        
        Args:
            screen: Pygame surface to draw on
        """
        if self.alpha < 1:
            return
        
        if not self.selected_pellet:
            return
        
        pellet = self.selected_pellet
        screen_width, screen_height = screen.get_size()
        
        # Calculate panel dimensions
        panel_width = int(screen_width * self.panel_width_pct)
        panel_height = int(screen_height * self.panel_height_pct)
        
        # Set default position (left side)
        if self.position is None:
            self.position = (20, (screen_height - panel_height) // 2)
        
        panel_x, panel_y = self.position
        
        # Create panel surface
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        bg_color = (*self.bg_color[:3], int(self.bg_color[3] * self.alpha / 255))
        panel.fill(bg_color)
        
        # Draw border
        border_color = (*self.highlight_color, int(255 * self.alpha / 255))
        pygame.draw.rect(panel, border_color, panel.get_rect(), 2)
        
        # Title bar
        title_bar_height = 35
        title_bar_color = (*self.header_color, int(200 * self.alpha / 255))
        pygame.draw.rect(panel, title_bar_color, (0, 0, panel_width, title_bar_height))
        
        title_text = self.text_font.render(
            f"Pellet Inspector",
            True,
            (*self.text_color, int(255 * self.alpha / 255))
        )
        panel.blit(title_text, (10, 8))
        
        # Close button
        close_text = self.text_font.render("✕", True, (*self.warning_color, int(255 * self.alpha / 255)))
        panel.blit(close_text, (panel_width - 30, 5))
        
        # Render content
        content_surface = self._render_content(pellet, panel_width)
        
        # Calculate max scroll
        self.max_scroll = max(0, content_surface.get_height() - panel_height + title_bar_height + 10)
        
        # Set clipping rect to prevent content from drawing outside the content area
        content_y = title_bar_height
        content_height = panel_height - title_bar_height
        clip_rect = pygame.Rect(0, content_y, panel_width, content_height)
        panel.set_clip(clip_rect)
        
        # Blit scrolled content
        panel.blit(content_surface, (0, content_y - self.scroll_offset))
        
        # Clear clipping rect
        panel.set_clip(None)
        
        # Draw scroll indicators
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
    
    def _render_content(self, pellet, panel_width: int) -> pygame.Surface:
        """
        Render all content for the inspector panel.
        
        Args:
            pellet: The pellet to display
            panel_width: Width of the panel
            
        Returns:
            Surface with all content rendered
        """
        estimated_height = 1500
        content = pygame.Surface((panel_width, estimated_height), pygame.SRCALPHA)
        
        y = self.margin
        x_margin = self.margin
        
        # === Basic Info ===
        title = self.title_font.render(f"Pellet {pellet.pellet_id[:8]}", True, self.highlight_color)
        content.blit(title, (x_margin, y))
        y += title.get_height() + 5
        
        subtitle = self.text_font.render(
            f"Generation {pellet.generation}",
            True, self.text_color
        )
        content.blit(subtitle, (x_margin, y))
        y += subtitle.get_height() + self.section_spacing
        
        # === Traits Section ===
        y = self._render_section_header(content, "Traits", x_margin, y)
        
        traits = pellet.traits
        trait_lines = [
            f"Nutritional Value: {traits.nutritional_value:.1f}",
            f"Size: {traits.size:.2f}",
            f"Growth Rate: {traits.growth_rate:.3f}",
            f"Palatability: {traits.palatability:.2f}",
            f"Toxicity: {traits.toxicity:.2f}",
            f"Spread Radius: {traits.spread_radius}"
        ]
        
        for line in trait_lines:
            text = self.text_font.render(line, True, self.stat_color)
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        y += self.section_spacing
        
        # === Lifecycle Section ===
        if hasattr(pellet, 'history') and pellet.history:
            y = self._render_section_header(content, "Lifecycle", x_margin, y)
            
            history = pellet.history
            lifetime = history.get_lifetime()
            is_alive = history.is_alive()
            
            lifecycle_lines = [
                f"Status: {'Alive ✓' if is_alive else 'Consumed/Dead ✗'}",
                f"Age: {lifetime:.1f}s",
                f"Times Reproduced: {history.times_reproduced}",
                f"Offspring: {len(history.offspring_ids)}",
                f"Mutations: {history.mutation_count}"
            ]
            
            for line in lifecycle_lines:
                color = self.highlight_color if "Alive" in line else self.text_color
                text = self.text_font.render(line, True, color)
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
            
            if not is_alive:
                death_line = f"Cause: {history.cause_of_death}"
                death_text = self.text_font.render(death_line, True, self.warning_color)
                content.blit(death_text, (x_margin + 10, y))
                y += self.line_height
            
            y += self.section_spacing
            
            # === Targeting Statistics ===
            y = self._render_section_header(content, "Creature Interactions", x_margin, y)
            
            targeting_rate = history.get_targeting_rate() * 100
            
            interaction_lines = [
                f"Times Targeted: {history.total_times_targeted}",
                f"Times Avoided: {history.total_times_avoided}",
                f"Targeting Rate: {targeting_rate:.1f}%"
            ]
            
            for line in interaction_lines:
                text = self.text_font.render(line, True, self.stat_color)
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
            
            # Most interested creature
            most_interested = history.get_most_interested_creature()
            if most_interested:
                interested_line = f"Most Interest: Creature {most_interested.creature_id[:8]}"
                interested_text = self.small_font.render(interested_line, True, self.highlight_color)
                content.blit(interested_text, (x_margin + 10, y))
                y += self.line_height
                
                detail_line = f"  Targeted {most_interested.times_targeted}x, Distance: {most_interested.distance_traveled:.1f}"
                detail_text = self.small_font.render(detail_line, True, (200, 200, 200))
                content.blit(detail_text, (x_margin + 15, y))
                y += self.line_height
            
            y += self.section_spacing
            
            # === Lineage Section ===
            if history.parent_id or history.offspring_ids:
                y = self._render_section_header(content, "Lineage", x_margin, y)
                
                if history.parent_id:
                    parent_line = f"Parent: {history.parent_id[:8]}"
                    parent_text = self.text_font.render(parent_line, True, self.stat_color)
                    content.blit(parent_text, (x_margin + 10, y))
                    y += self.line_height
                
                if history.offspring_ids:
                    offspring_header = f"Offspring ({len(history.offspring_ids)}):"
                    offspring_text = self.text_font.render(offspring_header, True, self.stat_color)
                    content.blit(offspring_text, (x_margin + 10, y))
                    y += self.line_height
                    
                    # Show first 3 offspring
                    for offspring_id in history.offspring_ids[:3]:
                        offspring_line = f"  • {offspring_id[:8]}"
                        off_text = self.small_font.render(offspring_line, True, (200, 200, 200))
                        content.blit(off_text, (x_margin + 15, y))
                        y += self.line_height
                    
                    if len(history.offspring_ids) > 3:
                        more_line = f"  ... and {len(history.offspring_ids) - 3} more"
                        more_text = self.small_font.render(more_line, True, (150, 150, 150))
                        content.blit(more_text, (x_margin + 15, y))
                        y += self.line_height
                
                y += self.section_spacing
            
            # === Recent Events ===
            recent_events = history.get_recent_events(5)
            if recent_events:
                y = self._render_section_header(content, "Recent Events", x_margin, y)
                
                for event in recent_events:
                    # Event type icon
                    icon = self._get_event_icon(event.event_type.value)
                    icon_text = self.small_font.render(icon, True, self.highlight_color)
                    content.blit(icon_text, (x_margin + 10, y))
                    
                    # Event description
                    desc = self.small_font.render(event.description[:45], True, self.text_color)
                    content.blit(desc, (x_margin + 30, y))
                    y += self.line_height
                
                y += self.section_spacing
        
        y += self.margin
        
        # Crop to actual height
        actual_content = pygame.Surface((panel_width, y), pygame.SRCALPHA)
        actual_content.blit(content, (0, 0))
        
        return actual_content
    
    def _render_section_header(self, surface: pygame.Surface, title: str, x: int, y: int) -> int:
        """Render a section header."""
        header = self.header_font.render(title, True, self.highlight_color)
        surface.blit(header, (x, y))
        y += header.get_height() + 5
        
        # Underline
        pygame.draw.line(surface, self.highlight_color, 
                        (x, y), (x + 200, y), 1)
        y += 8
        
        return y
    
    def _get_event_icon(self, event_type: str) -> str:
        """Get icon for event type."""
        icons = {
            'spawn': '🌱',
            'reproduce': '🌿',
            'mutate': '✨',
            'targeted': '🎯',
            'avoided': '👁️',
            'eaten': '🍽️',
            'died': '💀'
        }
        return icons.get(event_type, '•')
