"""
Pygame Rendering Demo - Visual real-time battle with Pygame.

This example demonstrates the full rendering system with Pygame,
showing creatures fighting in a 2D arena with animations and UI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.models.trait import Trait
from src.systems.battle_spatial import SpatialBattle
from src.rendering import (
    GameWindow,
    ArenaRenderer,
    CreatureRenderer,
    UIComponents,
    EventAnimator
)


def create_demo_battle():
    """Create a demo battle with interesting creatures."""
    # Create fire dragon with aggressive trait
    dragon_type = CreatureType(
        name="Fire Dragon",
        description="A powerful dragon that breathes fire",
        base_stats=Stats(max_hp=150, attack=20, defense=15, speed=12),
        stat_growth=StatGrowth(hp_growth=15.0, attack_growth=2.5),
        type_tags=["fire", "flying"],
        evolution_stage=2
    )
    
    dragon = Creature(name="Blaze", creature_type=dragon_type, level=10)
    dragon.add_ability(create_ability('fireball'))
    dragon.add_ability(create_ability('tackle'))
    dragon.add_trait(Trait(name="Aggressive", strength_modifier=1.2))
    
    # Create water serpent with hunter trait
    serpent_type = CreatureType(
        name="Water Serpent",
        description="A swift serpent that controls water",
        base_stats=Stats(max_hp=120, attack=18, defense=12, speed=16),
        stat_growth=StatGrowth(hp_growth=12.0, attack_growth=2.0, speed_growth=2.0),
        type_tags=["water"],
        evolution_stage=2
    )
    
    serpent = Creature(name="Aqua", creature_type=serpent_type, level=10)
    serpent.add_ability(create_ability('tackle'))
    serpent.add_ability(create_ability('quick_strike'))
    serpent.add_trait(Trait(name="Hunter", speed_modifier=1.15))
    
    # Create a warrior
    warrior_type = CreatureType(
        name="Warrior",
        description="A strong melee fighter",
        base_stats=Stats(max_hp=140, attack=22, defense=18, speed=10),
        stat_growth=StatGrowth(hp_growth=14.0, attack_growth=2.8),
        type_tags=["fighting"],
        evolution_stage=1
    )
    
    warrior = Creature(name="Ares", creature_type=warrior_type, level=10)
    warrior.add_ability(create_ability('tackle'))
    warrior.add_ability(create_ability('power_up'))
    warrior.add_trait(Trait(name="Defensive", defense_modifier=1.2))
    
    # Create battle with 2v1
    battle = SpatialBattle(
        player_team=[dragon, warrior],
        enemy_team=[serpent],
        arena_width=100,
        arena_height=60,
        random_seed=42
    )
    
    return battle


def main():
    """Main function to run the Pygame rendering demo."""
    print("=" * 70)
    print("EvoBattle - Pygame Rendering Demo".center(70))
    print("=" * 70)
    print()
    print("Watch creatures battle in real-time with full visual rendering!")
    print()
    print("Controls:")
    print("  SPACE - Pause/Resume")
    print("  ESC   - Exit")
    print()
    input("Press Enter to start the battle...")
    
    # Create battle
    battle = create_demo_battle()
    
    # Create rendering components
    window = GameWindow(width=1200, height=800, fps=60)
    arena_renderer = ArenaRenderer(show_grid=True)
    creature_renderer = CreatureRenderer()
    ui_components = UIComponents(max_log_entries=8)
    event_animator = EventAnimator()
    
    # Connect battle events to UI and animator
    def on_battle_event(event):
        ui_components.add_event_to_log(event)
        event_animator.add_battle_event(event)
    
    battle.add_event_callback(on_battle_event)
    
    # Process events in the main loop (we'll handle this in the run loop)
    # We need to modify the run loop to process animator events
    
    # Run the game
    try:
        window.running = True
        last_time = 0
        
        import pygame
        pygame.init()
        last_time = pygame.time.get_ticks()
        
        while window.running and not battle.is_over:
            # Handle input
            window.handle_events()
            
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0
            last_time = current_time
            
            # Update battle (if not paused)
            if not window.paused:
                battle.update(delta_time)
            
            # Process animator events
            event_animator.process_events(window.screen, battle)
            
            # Clear screen
            window.clear_screen()
            
            # Render everything
            arena_renderer.render(window.screen, battle)
            creature_renderer.render(window.screen, battle)
            ui_components.render(window.screen, battle, window.paused)
            event_animator.update(delta_time)
            event_animator.render(window.screen)
            
            # Update display
            window.update_display()
        
        # Show final state for a moment
        if battle.is_over:
            import time
            time.sleep(3)
    
    finally:
        window.quit()
        print("\nBattle ended!")
        print(f"Duration: {battle.current_time:.1f} seconds")
        print(f"Total events: {len(battle.events)}")
        
        # Show battle log
        print("\nBattle Log:")
        print("-" * 70)
        for log in battle.get_battle_log()[:20]:  # Show first 20 entries
            print(f"  {log}")


if __name__ == "__main__":
    main()
