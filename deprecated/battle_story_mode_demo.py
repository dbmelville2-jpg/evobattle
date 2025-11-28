"""
Battle Story Mode Demo - AI-powered battle narrative generation.

This demo showcases the battle story summarizer that generates engaging
narratives from battle events. It demonstrates:
- Automatic story generation at time intervals
- Multiple narrative tones (serious, heroic, comedic, dramatic)
- Story viewing in a dedicated UI panel
- Export functionality for sharing stories
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import random
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.models.ecosystem_traits import AGGRESSIVE, CAUTIOUS, FORAGER, EFFICIENT_METABOLISM
from src.models.spatial import Vector2D
from src.systems.battle_spatial import SpatialBattle, BattleCreature
from src.systems.living_world import LivingWorldBattleEnhancer
from src.systems.battle_story_summarizer import (
    BattleStoryGenerator, BattleStoryTracker, StoryTone
)
from src.rendering import (
    GameWindow, ArenaRenderer, CreatureRenderer, UIComponents, EventAnimator,
    StoryViewer, StoryViewerAction, PauseMenu, PauseMenuAction
)


def create_warrior(name: str, level: int = 5, traits: list = None) -> Creature:
    """Create a warrior creature."""
    if traits is None:
        traits = [random.choice([AGGRESSIVE, CAUTIOUS])]
    
    base_stats = Stats(
        max_hp=80 + level * 10,
        attack=12 + level * 2,
        defense=10 + level * 2,
        speed=15 + level
    )
    
    creature_type = CreatureType(
        name="Warrior",
        base_stats=base_stats,
        type_tags=["normal"],
        stat_growth=StatGrowth(hp_growth=10.0, attack_growth=2.0)
    )
    
    creature = Creature(
        name=name,
        creature_type=creature_type,
        level=level,
        traits=traits
    )
    
    creature.add_ability(create_ability('tackle'))
    ability = create_ability('quick_strike')
    if ability:
        creature.add_ability(ability)
    
    return creature


def main():
    """Run the battle story mode demo."""
    # Initialize Pygame
    pygame.init()
    
    # Create window
    window = GameWindow(
        width=1400,
        height=900,
        title="Battle Story Mode Demo - Press 'S' to View Story"
    )
    
    # Create battle with warriors
    print("\n=== Creating Battle with Story Mode ===")
    warriors = [
        create_warrior("Aragorn", level=5, traits=[AGGRESSIVE]),
        create_warrior("Legolas", level=5, traits=[CAUTIOUS]),
        create_warrior("Gimli", level=4, traits=[AGGRESSIVE]),
        create_warrior("Boromir", level=5, traits=[AGGRESSIVE]),
        create_warrior("Gandalf", level=6, traits=[CAUTIOUS]),
        create_warrior("Frodo", level=3, traits=[CAUTIOUS]),
        create_warrior("Sam", level=4, traits=[AGGRESSIVE]),
        create_warrior("Merry", level=3, traits=[CAUTIOUS]),
        create_warrior("Pippin", level=3, traits=[CAUTIOUS]),
        create_warrior("Saruman", level=6, traits=[AGGRESSIVE]),
    ]
    
    # Show personalities
    print("\nCreated warriors:")
    for w in warriors:
        print(f"  {w.name}: {w.personality.get_description()}")
    
    # Create battle with living world enhancer
    living_world = LivingWorldBattleEnhancer(None)
    battle = SpatialBattle(
        warriors,
        arena_width=120.0,
        arena_height=90.0,
        initial_resources=15,
        living_world_enhancer=living_world
    )
    
    # Initialize story generation system
    print("\n=== Initializing Story Generation System ===")
    story_generator = BattleStoryGenerator(default_tone=StoryTone.DRAMATIC)
    
    # Use 30 seconds interval for demo (normally 5 minutes)
    story_tracker = BattleStoryTracker(
        generator=story_generator,
        story_interval_seconds=30.0  # 30 seconds for demo
    )
    story_tracker.start_tracking()
    
    print(f"Story will be generated every {story_tracker.story_interval} seconds")
    print("Press 'S' to view the current story at any time")
    print("In the story viewer:")
    print("  - Click tone buttons to change narrative style")
    print("  - Click 'Regenerate' to create a new story")
    print("  - Click 'Export TXT' or 'Export MD' to save the story")
    print("  - Use scroll wheel or arrow keys to scroll")
    print("  - Press ESC or click 'Close' to return to battle")
    
    # Set up event callback to collect battle events
    def on_battle_event(event):
        story_tracker.generator.add_event(event)
    
    battle.add_event_callback(on_battle_event)
    
    # Initialize renderers
    arena_renderer = ArenaRenderer()
    creature_renderer = CreatureRenderer()
    ui_components = UIComponents()
    event_animator = EventAnimator()
    story_viewer = StoryViewer(width=700, height=600)
    pause_menu = PauseMenu()
    
    # Game state
    running = True
    paused = False
    show_story = False
    clock = pygame.time.Clock()
    dt = 0.0
    last_story_notification = 0.0
    current_story = ""
    current_tone = StoryTone.DRAMATIC
    
    # Generate initial story with placeholder
    current_story = "Battle in progress... Story will be generated after 30 seconds of combat.\n\nPress 'S' to view this panel again at any time."
    story_viewer.set_story(current_story, current_tone)
    
    print("\n=== Battle Started! ===")
    
    # Main game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_story:
                        show_story = False
                    elif paused:
                        paused = False
                    else:
                        paused = True
                
                elif event.key == pygame.K_SPACE:
                    if not show_story:
                        paused = not paused
                
                elif event.key == pygame.K_s:
                    show_story = not show_story
                    if show_story:
                        # Update story when opening viewer
                        story_viewer.set_story(current_story, current_tone)
            
            # Handle story viewer events
            if show_story:
                result = story_viewer.handle_event(event, 350, 150)
                if result:
                    action, data = result
                    
                    if action == StoryViewerAction.CLOSE:
                        show_story = False
                    
                    elif action == StoryViewerAction.CHANGE_TONE:
                        current_tone = data
                        print(f"\nRegenerating story with {current_tone.value} tone...")
                        current_story = story_tracker.generator.generate_story(tone=current_tone)
                        story_viewer.set_story(current_story, current_tone)
                        print("Story regenerated!")
                    
                    elif action == StoryViewerAction.REGENERATE:
                        print(f"\nRegenerating story with {current_tone.value} tone...")
                        current_story = story_tracker.generator.generate_story(tone=current_tone)
                        story_viewer.set_story(current_story, current_tone)
                        print("Story regenerated!")
                    
                    elif action == StoryViewerAction.EXPORT_TXT:
                        filepath = "battle_story.txt"
                        story_tracker.generator.export_story(current_story, filepath, 'txt')
                        print(f"\nStory exported to {filepath}")
                    
                    elif action == StoryViewerAction.EXPORT_MD:
                        filepath = "battle_story.md"
                        story_tracker.generator.export_story(current_story, filepath, 'md')
                        print(f"\nStory exported to {filepath}")
            
            # Handle pause menu events
            elif paused:
                result = pause_menu.handle_event(event, 500, 300)
                if result:
                    if result == PauseMenuAction.RESUME:
                        paused = False
                    elif result == PauseMenuAction.QUIT:
                        running = False
            
            # Handle battle events (animator)
            else:
                event_animator.handle_event(event)
        
        # Update game state
        if not paused and not show_story and not battle.is_over:
            # Update battle
            battle.update(dt)
            
            # Add battle logs to story generator
            for log in battle.get_battle_log():
                if log not in story_tracker.generator.battle_logs:
                    story_tracker.generator.add_log(log)
            
            # Check if it's time to generate a story
            if story_tracker.should_generate_story():
                print(f"\n{'='*70}")
                print(f"  AUTO-GENERATING STORY ({story_tracker.story_interval}s interval)")
                print(f"{'='*70}")
                current_story = story_tracker.generate_and_store_story(tone=current_tone)
                story_viewer.set_story(current_story, current_tone)
                last_story_notification = battle.current_time
                print("\nStory generated! Press 'S' to view it.")
                print(f"Total stories generated: {len(story_tracker.get_all_stories())}")
            
            # Process battle events for animations
            for event in battle.events:
                event_animator.add_event(event)
            battle.events.clear()
            
            # Update animator
            event_animator.update(dt)
        
        # Render
        window.surface.fill((20, 20, 30))
        
        if show_story:
            # Draw dimmed battle background
            arena_renderer.draw(window.surface, battle, opacity=0.3)
            creature_renderer.draw_all(window.surface, battle.battle_creatures, opacity=0.3)
            
            # Draw story viewer
            story_viewer.draw(window.surface, 350, 150)
        
        else:
            # Draw battle
            arena_renderer.draw(window.surface, battle)
            creature_renderer.draw_all(window.surface, battle.battle_creatures)
            
            # Draw animations
            event_animator.draw(window.surface)
            
            # Draw UI
            ui_components.draw_battle_info(window.surface, battle)
            ui_components.draw_controls(
                window.surface,
                ["SPACE: Pause/Resume", "S: View Story", "ESC: Pause Menu"]
            )
            
            # Draw story notification
            if battle.current_time - last_story_notification < 5.0:
                notification_font = pygame.font.Font(None, 36)
                notification_text = notification_font.render(
                    "New Story Available! Press 'S' to view",
                    True,
                    (255, 215, 0)
                )
                x = (window.width - notification_text.get_width()) // 2
                y = 50
                # Draw background
                bg_rect = notification_text.get_rect(topleft=(x-10, y-5))
                bg_rect.width += 20
                bg_rect.height += 10
                pygame.draw.rect(window.surface, (30, 30, 40), bg_rect)
                pygame.draw.rect(window.surface, (255, 215, 0), bg_rect, 2)
                window.surface.blit(notification_text, (x, y))
            
            # Draw pause menu if paused
            if paused:
                pause_menu.draw(window.surface, 500, 300)
        
        # Update display
        window.update()
        dt = clock.tick(60) / 1000.0  # 60 FPS
    
    # Battle ended - generate final story
    if not show_story:
        print(f"\n{'='*70}")
        print("  BATTLE ENDED - GENERATING FINAL STORY")
        print(f"{'='*70}")
        final_story = story_tracker.generate_and_store_story(tone=current_tone)
        print("\n" + final_story)
        print(f"\n{'='*70}")
        print(f"Total stories generated during battle: {len(story_tracker.get_all_stories())}")
        print(f"{'='*70}")
        
        # Export all stories
        story_tracker.export_all_stories('battle_stories', format='txt')
        print(f"\nAll stories exported to 'battle_stories/' directory")
    
    pygame.quit()


if __name__ == "__main__":
    main()
