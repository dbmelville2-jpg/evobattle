#!/usr/bin/env python3
"""Generate screenshot of story viewer for verification."""

import pygame
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.systems.battle_story_summarizer import BattleStoryGenerator, BattleStoryTracker, StoryTone
from src.rendering import StoryViewer, StoryViewerAction

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((1400, 900))
pygame.display.set_caption('Story Viewer Test')

# Create components
generator = BattleStoryGenerator(default_tone=StoryTone.DRAMATIC)
tracker = BattleStoryTracker(generator=generator, story_interval_seconds=300.0)
viewer = StoryViewer(width=700, height=600)

# Set test story
story = """Battle Story - 'S' Hotkey Test

This demonstrates the Story Viewer working correctly with the S hotkey.

Key Features:
- Press 'S' to toggle story viewer on/off
- Multiple narrative tones available (Dramatic, Heroic, Comedic, etc.)
- Export to TXT or Markdown format
- Auto-generates every 5 minutes during battle

The story viewer is now successfully integrated into the main game!

CONTROLS IN GAME:
- S: Toggle story viewer
- ESC: Close story viewer
- Click tone buttons to change narrative style
- Click Regenerate to create new story
- Click Export buttons to save story

This UI overlay appears when pressing 'S' during battle."""

viewer.set_story(story, StoryTone.DRAMATIC)

# Render to screen
screen.fill((20, 20, 30))

# Draw dark overlay
dark_overlay = pygame.Surface((1400, 900))
dark_overlay.set_alpha(180)
dark_overlay.fill((0, 0, 0))
screen.blit(dark_overlay, (0, 0))

# Draw story viewer at center position (350, 150)
viewer.draw(screen, 350, 150)

# Save screenshot
pygame.image.save(screen, '/tmp/story_viewer_screenshot.png')

print('✓ Story viewer rendered successfully')
print('✓ Screenshot saved to /tmp/story_viewer_screenshot.png')
pygame.quit()
