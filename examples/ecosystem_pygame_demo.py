"""
Ecosystem Survival Pygame Demo - Visual ecosystem simulation with hunger and foraging.

This demo showcases:
- Hunger bars on creatures
- Food resources scattered in arena
- Creatures seeking food when hungry
- Different metabolic traits affecting behavior
- Real-time survival simulation

Controls:
- SPACE: Pause/Resume
- ESC: Exit
- R: Restart simulation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.models.ecosystem_traits import (
    FORAGER, EFFICIENT_METABOLISM, CURIOUS, GLUTTON,
    VORACIOUS, AGGRESSIVE, CAUTIOUS, WANDERER
)
from src.systems.battle_spatial import SpatialBattle
from src.rendering import (
    GameWindow,
    ArenaRenderer,
    CreatureRenderer,
    UIComponents,
    EventAnimator
)

import pygame


def create_ecosystem_creature(name: str, traits: list, level: int = 5) -> Creature:
    """Create a creature for the ecosystem simulation."""
    base_stats = Stats(
        max_hp=80 + (level - 1) * 10,
        attack=12 + (level - 1) * 2,
        defense=10 + (level - 1) * 2,
        speed=15 + (level - 1)
    )
    
    creature_type = CreatureType(
        name=f"{name} Type",
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
    
    # Add basic abilities
    creature.add_ability(create_ability('tackle'))
    
    return creature


def create_ecosystem_battle():
    """Create an ecosystem battle simulation."""
    print("\n=== Creating Ecosystem Battle ===")
    
    # Create diverse creatures with ecosystem traits
    team1 = [
        create_ecosystem_creature("Forager Fox", [FORAGER, EFFICIENT_METABOLISM], level=5),
        create_ecosystem_creature("Curious Cat", [CURIOUS], level=4),
        create_ecosystem_creature("Glutton Bear", [GLUTTON], level=6),
    ]
    
    team2 = [
        create_ecosystem_creature("Hunter Wolf", [AGGRESSIVE, VORACIOUS], level=5),
        create_ecosystem_creature("Cautious Rabbit", [CAUTIOUS, EFFICIENT_METABOLISM], level=4),
        create_ecosystem_creature("Wanderer Bird", [WANDERER], level=4),
    ]
    
    print("\nTeam 1 (Left side):")
    for c in team1:
        trait_names = [t.name for t in c.traits]
        print(f"  - {c.name}: {', '.join(trait_names)}")
    
    print("\nTeam 2 (Right side):")
    for c in team2:
        trait_names = [t.name for t in c.traits]
        print(f"  - {c.name}: {', '.join(trait_names)}")
    
    print("\n=== Battle Configuration ===")
    print("Arena: 100x100")
    print("Initial resources: 10 food items")
    print("Resource spawn rate: 0.15/second (1 every ~7 seconds)")
    print("\nWatch the hunger bars (yellow) below HP bars!")
    print("Creatures will seek food when hungry (hunger < 40%)")
    print()
    
    # Create battle with moderate resource spawning
    battle = SpatialBattle(
        team1,
        team2,
        arena_width=100.0,
        arena_height=100.0,
        resource_spawn_rate=0.15,  # Moderate spawn rate
        initial_resources=10
    )
    
    return battle


def main():
    """Run the ecosystem survival visualization."""
    print("=" * 70)
    print("ECOSYSTEM SURVIVAL MODE - PYGAME VISUALIZATION")
    print("=" * 70)
    
    # Create battle
    battle = create_ecosystem_battle()
    
    # Initialize Pygame and create window
    pygame.init()
    window = GameWindow(
        width=1200,
        height=800,
        title="EvoBattle - Ecosystem Survival Mode",
        target_fps=60
    )
    
    # Create renderers
    arena_renderer = ArenaRenderer(show_grid=True)
    creature_renderer = CreatureRenderer(radius=15)
    ui_components = UIComponents()
    event_animator = EventAnimator()
    
    # Register event callback for animations
    battle.add_event_callback(event_animator.on_battle_event)
    
    print("\n" + "=" * 70)
    print("SIMULATION STARTED - Watch creatures hunt and forage!")
    print("=" * 70)
    print("\nControls:")
    print("  SPACE - Pause/Resume")
    print("  ESC   - Exit")
    print("  R     - Restart")
    print()
    
    # Simulation state
    running = True
    paused = False
    clock = pygame.time.Clock()
    
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
                    battle = create_ecosystem_battle()
                    event_animator.clear()
                    battle.add_event_callback(event_animator.on_battle_event)
        
        # Update simulation
        if not paused and not battle.is_over:
            dt = clock.get_time() / 1000.0  # Convert to seconds
            battle.update(dt)
        
        # Update animations
        event_animator.update(clock.get_time() / 1000.0)
        
        # Clear screen
        window.screen.fill((20, 20, 30))
        
        # Render arena
        arena_renderer.render(window.screen, battle)
        
        # Render creatures
        creature_renderer.render(window.screen, battle)
        
        # Render animations
        event_animator.render(window.screen, battle)
        
        # Render UI
        alive_players = [c for c in battle.player_creatures if c.is_alive()]
        alive_enemies = [c for c in battle.enemy_creatures if c.is_alive()]
        
        ui_components.draw_battle_timer(
            window.screen,
            battle.current_time,
            (window.width // 2, 30)
        )
        
        ui_components.draw_team_status(
            window.screen,
            "Team 1",
            len(alive_players),
            len(battle.player_creatures),
            (100, 30)
        )
        
        ui_components.draw_team_status(
            window.screen,
            "Team 2",
            len(alive_enemies),
            len(battle.enemy_creatures),
            (window.width - 100, 30)
        )
        
        # Draw resource count
        font = pygame.font.Font(None, 24)
        resource_text = f"Food: {len(battle.arena.resources)}"
        text_surface = font.render(resource_text, True, (120, 255, 100))
        window.screen.blit(text_surface, (window.width // 2 - 40, 60))
        
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
            if alive_players and not alive_enemies:
                result_text = "TEAM 1 WINS!"
                color = (100, 200, 255)
            elif alive_enemies and not alive_players:
                result_text = "TEAM 2 WINS!"
                color = (255, 100, 100)
            else:
                result_text = "DRAW!"
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
        
        # Draw event log
        recent_events = battle.events[-5:]  # Show last 5 events
        log_y = window.height - 120
        event_font = pygame.font.Font(None, 20)
        
        for i, event in enumerate(recent_events):
            event_text = event_font.render(event.message[:80], True, (200, 200, 200))
            window.screen.blit(event_text, (20, log_y + i * 22))
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    # Cleanup
    pygame.quit()
    print("\n" + "=" * 70)
    print(f"Simulation ended at {battle.current_time:.1f}s")
    print(f"Final survivors: Team 1: {len(alive_players)}, Team 2: {len(alive_enemies)}")
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
            print("  python -m examples.ecosystem_survival_demo")
            print()
        else:
            raise
