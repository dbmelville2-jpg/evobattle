"""
Visual verification script for 'S' hotkey story viewer functionality.
This script simulates the game loop and tests the 'S' key behavior.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src.systems.battle_story_summarizer import BattleStoryGenerator, BattleStoryTracker, StoryTone
from src.rendering import StoryViewer, StoryViewerAction

# Initialize Pygame
pygame.init()

# Create window
screen = pygame.display.set_mode((1400, 900))
pygame.display.set_caption("Story Viewer 'S' Hotkey Test")

# Initialize story system (as in main.py)
story_generator = BattleStoryGenerator(default_tone=StoryTone.DRAMATIC)
story_tracker = BattleStoryTracker(
    generator=story_generator,
    story_interval_seconds=300.0
)
story_tracker.start_tracking()

# Create story viewer
story_viewer = StoryViewer(width=700, height=600)

# Initial story
current_story = """Battle Story Test

This is a test story to verify the 'S' hotkey functionality works correctly.

INSTRUCTIONS:
1. Press 'S' to toggle this story viewer on/off
2. Press ESC to close the story viewer
3. Click tone buttons to change narrative style
4. Click 'Regenerate' to create a new story
5. Click 'Export TXT' or 'Export MD' to save
6. Press 'Q' to quit this test

The story viewer should appear centered on the screen with a dark background overlay.

If you can read this, the 'S' hotkey is working!"""

current_tone = StoryTone.DRAMATIC
story_viewer.set_story(current_story, current_tone)

# Game state
show_story = False
running = True
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

print("\n" + "="*70)
print("Story Viewer 'S' Hotkey Test")
print("="*70)
print("\nControls:")
print("  S: Toggle story viewer")
print("  ESC: Close story viewer")
print("  Q: Quit test")
print("\nPress 'S' to test the story viewer hotkey!")
print("="*70 + "\n")

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Story viewer handling (as in main.py)
        if show_story:
            result = story_viewer.handle_event(event, 350, 150)
            if result:
                action, data = result
                
                if action == StoryViewerAction.CLOSE:
                    show_story = False
                    print("✓ Story viewer closed via Close button")
                
                elif action == StoryViewerAction.CHANGE_TONE:
                    current_tone = data
                    print(f"✓ Tone changed to: {current_tone.value}")
                    current_story = f"Story with {current_tone.value} tone.\n\nThis demonstrates tone changing works!"
                    story_viewer.set_story(current_story, current_tone)
                
                elif action == StoryViewerAction.REGENERATE:
                    print("✓ Story regenerated")
                    current_story = "Regenerated story!\n\nThis demonstrates regeneration works!"
                    story_viewer.set_story(current_story, current_tone)
                
                elif action == StoryViewerAction.EXPORT_TXT:
                    print("✓ Story export to TXT requested")
                
                elif action == StoryViewerAction.EXPORT_MD:
                    print("✓ Story export to MD requested")
        
        # Regular input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
                print("\n✓ Test completed - quitting")
            
            elif event.key == pygame.K_ESCAPE:
                if show_story:
                    show_story = False
                    print("✓ Story viewer closed via ESC key")
            
            elif event.key == pygame.K_s:
                show_story = not show_story
                if show_story:
                    print("✓ Story viewer opened via 'S' key")
                    story_viewer.set_story(current_story, current_tone)
                else:
                    print("✓ Story viewer closed via 'S' key")
    
    # Render
    screen.fill((20, 20, 30))
    
    if show_story:
        # Draw dark overlay
        dark_overlay = pygame.Surface((1400, 900))
        dark_overlay.set_alpha(180)
        dark_overlay.fill((0, 0, 0))
        screen.blit(dark_overlay, (0, 0))
        
        # Draw story viewer
        story_viewer.draw(screen, 350, 150)
    else:
        # Draw instructions
        title = font.render("Story Viewer 'S' Hotkey Test", True, (255, 255, 100))
        instruction1 = font.render("Press 'S' to open the story viewer", True, (200, 200, 200))
        instruction2 = font.render("Press 'Q' to quit this test", True, (200, 200, 200))
        
        screen.blit(title, (400, 300))
        screen.blit(instruction1, (400, 400))
        screen.blit(instruction2, (400, 450))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\n✓ All story viewer hotkey tests completed successfully!")
