"""
Pellet Evolution Pygame Demo - Visual ecosystem simulation with evolving pellets.

This demo showcases:
- Pellets with visual traits (color, size)
- Generation markers on evolved pellets
- Pellet reproduction and mutation visualization
- Real-time evolution statistics
- Interactive visualization with pause/resume

Controls:
- SPACE: Pause/Resume
- ESC: Exit
- R: Restart simulation

Potential Future Enhancements:
- Step forward mode (single frame advance)
- Fast-forward mode for accelerated simulation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.creature import Creature
from src.models.trait import Trait
from src.systems.battle_spatial import SpatialBattle
from src.rendering import (
    GameWindow,
    ArenaRenderer,
    CreatureRenderer,
    PelletRenderer,
    UIComponents,
    EventAnimator
)

import pygame


def create_ecosystem_creature(name: str, traits: list) -> Creature:
    """Create a simple creature for the pellet evolution ecosystem."""
    creature = Creature(
        name=name,
        hunger=100,
        traits=traits
    )
    return creature


def create_pellet_evolution_battle(
    num_creatures: int = 6,
    initial_pellets: int = 15,
    arena_width: float = 120.0,
    arena_height: float = 120.0,
    resource_spawn_rate: float = 0.2
):
    """Create a battle focused on pellet evolution dynamics."""
    import random
    
    print("\n=== Creating Pellet Evolution Ecosystem ===")
    
    creatures = []
    
    # Create herbivores (can only eat plants/pellets)
    for i in range(4):
        creature = create_ecosystem_creature(
            name=f"Herbivore-{i+1}",
            traits=[Trait(name="Herbivore")]
        )
        creatures.append(creature)
    
    # Create omnivores (can eat both)
    for i in range(2):
        creature = create_ecosystem_creature(
            name=f"Omnivore-{i+1}",
            traits=[]
        )
        creatures.append(creature)
    
    print(f"\nInitial Population: {num_creatures} creatures")
    print(f"  - 4 Herbivores (plant-eaters only)")
    print(f"  - 2 Omnivores (eat plants and creatures)")
    
    print("\n=== Battle Configuration ===")
    print(f"Arena: {arena_width}x{arena_height}")
    print(f"Initial pellets: {initial_pellets}")
    print(f"Pellet spawn rate: {resource_spawn_rate}/second")
    print("\nWatch pellets evolve through reproduction and mutation!")
    print()
    
    # Create battle with pellet-focused settings
    battle = SpatialBattle(
        creatures,
        arena_width=arena_width,
        arena_height=arena_height,
        resource_spawn_rate=resource_spawn_rate,
        initial_resources=initial_pellets
    )
    
    return battle


def main():
    """Run the pellet evolution visualization."""
    print("=" * 70)
    print("PELLET EVOLUTION DEMO - PYGAME VISUALIZATION")
    print("=" * 70)
    
    # Create battle
    battle = create_pellet_evolution_battle()
    
    # Initialize Pygame and create window
    pygame.init()
    window = GameWindow(
        width=1200,
        height=800,
        title="EvoBattle - Pellet Evolution Demo",
        fps=60
    )
    
    # Create renderers
    arena_renderer = ArenaRenderer(show_grid=True)
    pellet_renderer = PelletRenderer(base_radius=6, show_generation=True)
    creature_renderer = CreatureRenderer(radius=15)
    ui_components = UIComponents(show_pellet_stats=True)
    event_animator = EventAnimator()
    
    # Connect pellet renderer to arena renderer for coordinated rendering
    arena_renderer.pellet_renderer = pellet_renderer
    
    # Register event callback for animations
    def on_battle_event(event):
        ui_components.add_event_to_log(event)
        event_animator.on_battle_event(event)
    
    battle.add_event_callback(on_battle_event)
    
    print("\n" + "=" * 70)
    print("SIMULATION STARTED - Watch pellets evolve!")
    print("=" * 70)
    print("\nControls:")
    print("  SPACE - Pause/Resume")
    print("  ESC   - Exit")
    print("  R     - Restart")
    print("\nPotential Future Enhancements:")
    print("  S     - Step forward (single frame)")
    print("  F     - Fast-forward mode")
    print("  (See docs/future_features.md for implementation details)")
    print()
    
    # Simulation state
    running = True
    paused = False
    clock = pygame.time.Clock()
    
    # Future enhancement: Add step mode and fast-forward mode
    # These features would allow frame-by-frame advancement and accelerated simulation
    # Commented out for now - see docs/future_features.md for implementation plan
    # step_mode = False
    # fast_forward = False
    # fast_forward_multiplier = 5.0
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    print(f"{'Paused' if paused else 'Resumed'}")
                elif event.key == pygame.K_r:
                    print("\n=== Restarting Simulation ===\n")
                    battle = create_pellet_evolution_battle()
                    event_animator.clear()
                    battle.add_event_callback(on_battle_event)
                # Future enhancement: Step and fast-forward controls
                # elif event.key == pygame.K_s:
                #     step_mode = True
                #     paused = False
                # elif event.key == pygame.K_f:
                #     fast_forward = not fast_forward
                #     print(f"Fast-forward: {'ON' if fast_forward else 'OFF'}")
        
        # Update simulation
        if not paused and not battle.is_over:
            dt = clock.get_time() / 1000.0  # Convert to seconds
            # Future enhancement: Apply fast-forward multiplier
            # if fast_forward:
            #     dt *= fast_forward_multiplier
            battle.update(dt)
            
            # Future enhancement: Handle step mode
            # if step_mode:
            #     paused = True
            #     step_mode = False
        
        # Update animations
        event_animator.update(clock.get_time() / 1000.0)
        
        # Clear screen
        window.screen.fill((20, 20, 30))
        
        # Render arena (draws background, grid, simple resources)
        arena_renderer.render(window.screen, battle)
        
        # Render pellets (detailed pellet visualization)
        pellet_renderer.render(window.screen, battle)
        
        # Render creatures
        creature_renderer.render(window.screen, battle)
        
        # Render animations
        event_animator.render(window.screen, battle)
        
        # Render UI (includes pellet stats panel)
        ui_components.render(window.screen, battle, paused)
        
        # Draw pause indicator
        if paused:
            pause_font = pygame.font.Font(None, 48)
            pause_text = pause_font.render("PAUSED", True, (255, 255, 100))
            text_rect = pause_text.get_rect(center=(window.width // 2, window.height // 2))
            
            # Draw semi-transparent background
            s = pygame.Surface((text_rect.width + 40, text_rect.height + 20))
            s.set_alpha(200)
            s.fill((30, 30, 40))
            window.screen.blit(s, (text_rect.x - 20, text_rect.y - 10))
            
            window.screen.blit(pause_text, text_rect)
        
        # Draw battle result if over
        if battle.is_over:
            result_font = pygame.font.Font(None, 56)
            result_text = "POPULATION EXTINCT!"
            color = (200, 200, 100)
            
            text_surface = result_font.render(result_text, True, color)
            text_rect = text_surface.get_rect(center=(window.width // 2, window.height // 2))
            
            # Semi-transparent background
            s = pygame.Surface((text_rect.width + 60, text_rect.height + 40))
            s.set_alpha(220)
            s.fill((20, 20, 30))
            window.screen.blit(s, (text_rect.x - 30, text_rect.y - 20))
            
            window.screen.blit(text_surface, text_rect)
            
            # Draw restart hint
            hint_font = pygame.font.Font(None, 32)
            hint_text = hint_font.render("Press R to restart", True, (200, 200, 200))
            hint_rect = hint_text.get_rect(center=(window.width // 2, window.height // 2 + 60))
            window.screen.blit(hint_text, hint_rect)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    # Cleanup
    pygame.quit()
    
    # Print final statistics
    pellets = battle.arena.pellets
    alive_creatures = [c for c in battle.creatures if c.is_alive()]
    
    print("\n" + "=" * 70)
    print(f"Simulation ended at {battle.current_time:.1f}s")
    print(f"Creatures: {len(alive_creatures)}/{len(battle.creatures)} alive")
    
    if pellets:
        print(f"\nFinal Pellet Statistics:")
        print(f"  Total pellets: {len(pellets)}")
        avg_nutrition = sum(p.get_nutritional_value() for p in pellets) / len(pellets)
        print(f"  Avg nutrition: {avg_nutrition:.1f}")
        max_gen = max(p.generation for p in pellets)
        print(f"  Max generation: {max_gen}")
        evolved_pellets = [p for p in pellets if p.generation > 0]
        print(f"  Evolved pellets: {len(evolved_pellets)}/{len(pellets)}")
    else:
        print("\nNo pellets remaining!")
    
    print("=" * 70)
    print()


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        if 'pygame' in str(e):
            print("\n" + "=" * 70)
            print("ERROR: Pygame is not installed")
            print("=" * 70)
            print("\nTo run this demo, install pygame:")
            print("  pip install pygame")
            print("\nAlternatively, run the text-based demo:")
            print("  python -m examples.pellet_evolution_demo")
            print()
        else:
            raise
