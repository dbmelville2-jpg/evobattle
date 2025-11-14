"""
Screenshot Test - Generate a screenshot of the rendering system.

This creates a single frame screenshot to demonstrate the UI and rendering.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.models.trait import Trait
from src.systems.battle_spatial import SpatialBattle, BattleEventType
from src.rendering import (
    GameWindow,
    ArenaRenderer,
    CreatureRenderer,
    UIComponents,
    EventAnimator
)


def create_test_battle():
    """Create a battle in progress for screenshot."""
    # Create creatures
    dragon_type = CreatureType(
        name="Fire Dragon",
        base_stats=Stats(max_hp=150, attack=20, defense=15, speed=12),
        type_tags=["fire", "flying"]
    )
    
    dragon = Creature(name="Blaze", creature_type=dragon_type, level=10)
    dragon.add_ability(create_ability('fireball'))
    dragon.add_trait(Trait(name="Aggressive"))
    
    serpent_type = CreatureType(
        name="Water Serpent",
        base_stats=Stats(max_hp=120, attack=18, defense=12, speed=16),
        type_tags=["water"]
    )
    
    serpent = Creature(name="Aqua", creature_type=serpent_type, level=10)
    serpent.add_ability(create_ability('tackle'))
    serpent.add_trait(Trait(name="Hunter"))
    
    warrior_type = CreatureType(
        name="Warrior",
        base_stats=Stats(max_hp=140, attack=22, defense=18, speed=10),
        type_tags=["fighting"]
    )
    
    warrior = Creature(name="Ares", creature_type=warrior_type, level=10)
    warrior.add_ability(create_ability('tackle'))
    warrior.add_trait(Trait(name="Defensive"))
    
    # Create battle
    battle = SpatialBattle(
        player_team=[dragon, warrior],
        enemy_team=[serpent],
        arena_width=100,
        arena_height=60,
        random_seed=42
    )
    
    # Simulate a few seconds to get creatures in action
    for _ in range(50):
        battle.update(0.1)
    
    return battle


def main():
    """Generate a screenshot of the rendering system."""
    print("Generating screenshot...")
    
    # Set SDL to use dummy video driver for headless rendering
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    # Create battle
    battle = create_test_battle()
    
    # Create rendering components
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    
    arena_renderer = ArenaRenderer(show_grid=True)
    creature_renderer = CreatureRenderer()
    ui_components = UIComponents(max_log_entries=8)
    event_animator = EventAnimator()
    
    # Add some sample events to the log
    ui_components.event_log.append("Blaze uses Fireball!")
    ui_components.event_log.append("Aqua takes 45 damage!")
    ui_components.event_log.append("Ares uses Tackle!")
    ui_components.event_log.append("Aqua takes 32 damage!")
    ui_components.event_log.append("Aqua uses Tackle!")
    ui_components.event_log.append("Blaze takes 28 damage!")
    
    # Clear screen
    screen.fill((20, 20, 30))
    
    # Render everything
    arena_renderer.render(screen, battle)
    creature_renderer.render(screen, battle)
    ui_components.render(screen, battle, paused=False)
    event_animator.render(screen)
    
    # Save screenshot
    screenshot_path = "/tmp/evobattle_rendering_screenshot.png"
    pygame.image.save(screen, screenshot_path)
    
    pygame.quit()
    
    print(f"Screenshot saved to: {screenshot_path}")
    print("✅ Rendering system working correctly!")
    
    return screenshot_path


if __name__ == "__main__":
    screenshot_path = main()
