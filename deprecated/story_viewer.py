"""
Story Viewer - UI component for displaying battle story summaries.

This module provides a Pygame-based UI for viewing AI-generated battle stories,
with options for tone selection and story export.
"""

import pygame
from typing import Optional, List, Callable
from enum import Enum
import os

from ..systems.battle_story_summarizer import StoryTone


class StoryViewerAction(Enum):
    """Actions that can be triggered from the story viewer."""
    CLOSE = "close"
    EXPORT_TXT = "export_txt"
    EXPORT_MD = "export_md"
    CHANGE_TONE = "change_tone"
    REGENERATE = "regenerate"


class StoryViewer:
    """
    UI component for displaying battle stories with export options.
    
    Shows AI-generated battle narratives in a scrollable text panel with
    controls for tone selection, regeneration, and export.
    """
    
    def __init__(
        self,
        width: int = 600,
        height: int = 500,
        font_size: int = 18
    ):
        """
        Initialize the story viewer.
        
        Args:
            width: Width of the viewer panel
            height: Height of the viewer panel
            font_size: Font size for story text
        """
        self.width = width
        self.height = height
        self.font_size = font_size
        
        # Initialize fonts
        try:
            self.title_font = pygame.font.Font(None, 32)
            self.text_font = pygame.font.Font(None, font_size)
            self.button_font = pygame.font.Font(None, 24)
        except:
            self.title_font = pygame.font.SysFont('Arial', 32)
            self.text_font = pygame.font.SysFont('Arial', font_size)
            self.button_font = pygame.font.SysFont('Arial', 24)
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.text_color = (240, 240, 240)
        self.title_color = (255, 215, 0)
        self.button_color = (60, 60, 80)
        self.button_hover_color = (80, 80, 100)
        self.button_text_color = (255, 255, 255)
        self.border_color = (100, 100, 120)
        
        # Story content
        self.story_text: str = ""
        self.wrapped_lines: List[str] = []
        self.scroll_offset: int = 0
        self.max_scroll: int = 0
        
        # Current tone
        self.current_tone = StoryTone.DRAMATIC
        
        # Button definitions
        self.buttons = {
            'close': {'rect': None, 'text': 'Close', 'action': StoryViewerAction.CLOSE},
            'export_txt': {'rect': None, 'text': 'Export TXT', 'action': StoryViewerAction.EXPORT_TXT},
            'export_md': {'rect': None, 'text': 'Export MD', 'action': StoryViewerAction.EXPORT_MD},
            'regenerate': {'rect': None, 'text': 'Regenerate', 'action': StoryViewerAction.REGENERATE},
        }
        
        # Tone selector buttons
        self.tone_buttons = {}
        for tone in StoryTone:
            self.tone_buttons[tone.value] = {
                'rect': None,
                'text': tone.value.capitalize(),
                'tone': tone
            }
        
        self.hovered_button: Optional[str] = None
        self.hovered_tone: Optional[str] = None
    
    def set_story(self, story: str, tone: StoryTone = StoryTone.DRAMATIC):
        """
        Set the story to display.
        
        Args:
            story: Story text to display
            tone: Current tone of the story
        """
        self.story_text = story
        self.current_tone = tone
        self.scroll_offset = 0
        self._wrap_text()
    
    def _wrap_text(self):
        """Wrap story text to fit the display width."""
        self.wrapped_lines = []
        
        if not self.story_text:
            return
        
        # Available width for text (with padding)
        text_width = self.width - 40
        
        # Split into paragraphs
        paragraphs = self.story_text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                self.wrapped_lines.append('')
                continue
            
            # Wrap each paragraph
            words = paragraph.split(' ')
            current_line = ''
            
            for word in words:
                test_line = f"{current_line} {word}".strip()
                text_surface = self.text_font.render(test_line, True, self.text_color)
                
                if text_surface.get_width() <= text_width:
                    current_line = test_line
                else:
                    if current_line:
                        self.wrapped_lines.append(current_line)
                    current_line = word
            
            if current_line:
                self.wrapped_lines.append(current_line)
        
        # Calculate max scroll
        line_height = self.text_font.get_linesize()
        text_area_height = self.height - 200  # Reserve space for title and buttons
        visible_lines = text_area_height // line_height
        self.max_scroll = max(0, len(self.wrapped_lines) - visible_lines)
    
    def _create_button_rects(self, x_offset: int, y_offset: int):
        """Create rectangles for all buttons based on viewer position."""
        # Action buttons at bottom
        button_y = y_offset + self.height - 60
        button_spacing = 10
        button_width = 120
        button_height = 40
        
        x = x_offset + 20
        for key in ['regenerate', 'export_txt', 'export_md', 'close']:
            self.buttons[key]['rect'] = pygame.Rect(x, button_y, button_width, button_height)
            x += button_width + button_spacing
        
        # Tone selector buttons
        tone_button_y = y_offset + 60
        tone_button_width = 100
        tone_button_height = 30
        tone_x = x_offset + 20
        
        for tone_key in self.tone_buttons:
            self.tone_buttons[tone_key]['rect'] = pygame.Rect(
                tone_x, tone_button_y, tone_button_width, tone_button_height
            )
            tone_x += tone_button_width + 5
    
    def handle_event(self, event: pygame.event.Event, x_offset: int, y_offset: int) -> Optional[tuple]:
        """
        Handle pygame events for the story viewer.
        
        Args:
            event: Pygame event
            x_offset: X position of viewer on screen
            y_offset: Y position of viewer on screen
            
        Returns:
            Tuple of (action, data) if action triggered, None otherwise
        """
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            
            # Check button hover
            self.hovered_button = None
            for key, btn in self.buttons.items():
                if btn['rect'] and btn['rect'].collidepoint(mouse_pos):
                    self.hovered_button = key
                    break
            
            # Check tone button hover
            self.hovered_tone = None
            for tone_key, btn in self.tone_buttons.items():
                if btn['rect'] and btn['rect'].collidepoint(mouse_pos):
                    self.hovered_tone = tone_key
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check action buttons
                for key, btn in self.buttons.items():
                    if btn['rect'] and btn['rect'].collidepoint(mouse_pos):
                        return (btn['action'], None)
                
                # Check tone buttons
                for tone_key, btn in self.tone_buttons.items():
                    if btn['rect'] and btn['rect'].collidepoint(mouse_pos):
                        return (StoryViewerAction.CHANGE_TONE, btn['tone'])
            
            elif event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            
            elif event.button == 5:  # Scroll down
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return (StoryViewerAction.CLOSE, None)
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)
            elif event.key == pygame.K_PAGEUP:
                self.scroll_offset = max(0, self.scroll_offset - 5)
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 5)
        
        return None
    
    def draw(self, surface: pygame.Surface, x: int, y: int):
        """
        Draw the story viewer on the surface.
        
        Args:
            surface: Pygame surface to draw on
            x: X position of viewer
            y: Y position of viewer
        """
        # Create button rectangles
        self._create_button_rects(x, y)
        
        # Draw background panel
        panel_rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, panel_rect)
        pygame.draw.rect(surface, self.border_color, panel_rect, 3)
        
        # Draw title
        title_surface = self.title_font.render('Battle Story', True, self.title_color)
        title_x = x + (self.width - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, y + 10))
        
        # Draw tone selector label
        tone_label = self.button_font.render('Tone:', True, self.text_color)
        surface.blit(tone_label, (x + 20, y + 45))
        
        # Draw tone selector buttons
        for tone_key, btn in self.tone_buttons.items():
            if btn['rect']:
                is_selected = btn['tone'] == self.current_tone
                is_hovered = tone_key == self.hovered_tone
                
                # Button background
                button_color = self.button_hover_color if is_hovered else self.button_color
                if is_selected:
                    button_color = (100, 150, 100)  # Green for selected
                
                pygame.draw.rect(surface, button_color, btn['rect'])
                pygame.draw.rect(surface, self.border_color, btn['rect'], 2)
                
                # Button text
                text_surface = self.button_font.render(btn['text'], True, self.button_text_color)
                text_x = btn['rect'].centerx - text_surface.get_width() // 2
                text_y = btn['rect'].centery - text_surface.get_height() // 2
                surface.blit(text_surface, (text_x, text_y))
        
        # Draw story text area
        text_area_y = y + 100
        text_area_height = self.height - 200
        
        # Clip to text area
        clip_rect = pygame.Rect(x + 20, text_area_y, self.width - 40, text_area_height)
        surface.set_clip(clip_rect)
        
        # Draw wrapped text lines
        line_height = self.text_font.get_linesize()
        current_y = text_area_y
        
        for i, line in enumerate(self.wrapped_lines):
            if i < self.scroll_offset:
                continue
            
            if current_y > text_area_y + text_area_height:
                break
            
            text_surface = self.text_font.render(line, True, self.text_color)
            surface.blit(text_surface, (x + 20, current_y))
            current_y += line_height
        
        # Reset clip
        surface.set_clip(None)
        
        # Draw scroll indicator
        if self.max_scroll > 0:
            scroll_text = f"[{self.scroll_offset + 1}/{self.max_scroll + 1}] Use scroll wheel or arrow keys"
            scroll_surface = self.text_font.render(scroll_text, True, (150, 150, 150))
            surface.blit(scroll_surface, (x + 20, y + self.height - 90))
        
        # Draw action buttons
        for key, btn in self.buttons.items():
            if btn['rect']:
                # Button background
                is_hovered = key == self.hovered_button
                button_color = self.button_hover_color if is_hovered else self.button_color
                
                pygame.draw.rect(surface, button_color, btn['rect'])
                pygame.draw.rect(surface, self.border_color, btn['rect'], 2)
                
                # Button text
                text_surface = self.button_font.render(btn['text'], True, self.button_text_color)
                text_x = btn['rect'].centerx - text_surface.get_width() // 2
                text_y = btn['rect'].centery - text_surface.get_height() // 2
                surface.blit(text_surface, (text_x, text_y))
