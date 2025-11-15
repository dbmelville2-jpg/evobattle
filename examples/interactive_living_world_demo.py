"""
Interactive Living World Demo - Pygame visualization with creature inspector.

This demo showcases the living world features with a visual battle where you can:
- Watch creatures fight in real-time
- Click on creatures to see their detailed histories
- See personalities affect behavior
- Watch skills develop through combat
- Track relationships and rivalries forming
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
from src.rendering import GameWindow, ArenaRenderer, CreatureRenderer, UIComponents, EventAnimator
from src.rendering.creature_inspector import CreatureInspector


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
    """Run the interactive living world demo."""
    # Initialize Pygame
    pygame.init()
    
    # Create window
    window = GameWindow(
        width=1400,
        height=900,
        title="Living World Demo - Click Creatures to Inspect"
    )
    
    # Create battle with warriors
    print("\n=== Creating Living World Battle ===")
    warriors = [
        create_warrior("Aragorn", level=5, traits=[AGGRESSIVE]),
        create_warrior("Legolas", level=5, traits=[CAUTIOUS]),
        create_warrior("Gimli", level=4, traits=[AGGRESSIVE]),
        create_warrior("Boromir", level=5, traits=[AGGRESSIVE]),
        create_warrior("Gandalf", level=6, traits=[CAUTIOUS]),
        create_warrior("Frodo", level=3, traits=[CAUTIOUS]),
        create_warrior("Sam", level=4, traits=[AGGRESSIVE]),
        create_warrior("Merry", level=3, traits=[CAUTIOUS]),
    ]
    
    # Show personalities
    print("\nCreated warriors:")
    for w in warriors:
        print(f"  {w.name}: {w.personality.get_description()}")
    
    # Create battle with all warriors in a single population
    # Note: Pass warriors as first positional argument (creatures_or_team1 parameter)
    battle = SpatialBattle(
        warriors,  # All creatures in one population
        arena_width=120.0,
        arena_height=90.0,
        resource_spawn_rate=0.0  # No food in this demo
    )
    
    # Create living world enhancer and connect to battle
    enhancer = LivingWorldBattleEnhancer(battle)
    battle.enhancer = enhancer  # Connect enhancer to battle
    enhancer.on_battle_start(warriors)
    
    # Create renderers
    arena_renderer = ArenaRenderer(show_grid=True)
    
    creature_renderer = CreatureRenderer()
    ui_components = UIComponents(max_log_entries=10)
    event_animator = EventAnimator()
    creature_inspector = CreatureInspector()
    
    # Subscribe to battle events
    battle.add_event_callback(ui_components.add_event_to_log)
    battle.add_event_callback(event_animator.on_battle_event)
    
    # Game state
    paused = False
    clock = pygame.time.Clock()
    running = True
    selected_battle_creature = None
    
    print("\n=== Battle Started ===")
    print("Controls:")
    print("  Click on creatures to inspect their history")
    print("  SPACE: Pause/Resume")
    print("  I: Toggle inspector")
    print("  ESC: Exit")
    print("\nWatch as creatures develop skills, form rivalries, and create stories!")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_i:
                    creature_inspector.toggle_visibility()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if clicked on a creature
                    mouse_pos = pygame.mouse.get_pos()
                    clicked_creature = _get_creature_at_position(
                        mouse_pos,
                        battle,
                        arena_renderer,
                        window
                    )
                    
                    if clicked_creature:
                        selected_battle_creature = clicked_creature
                        creature_inspector.select_creature(clicked_creature.creature)
                        print(f"\nSelected: {clicked_creature.creature.name}")
                        print(f"  Personality: {clicked_creature.creature.personality.get_description()}")
                        print(f"  Battles: {clicked_creature.creature.history.battles_fought}")
                        print(f"  Kills: {len(clicked_creature.creature.history.kills)}")
                        creature_inspector.visible = True
            
            elif event.type == pygame.MOUSEWHEEL:
                # Scroll inspector
                creature_inspector.handle_scroll(-event.y)
        
        # Update battle
        if not paused and not battle.is_over:
            battle.update(dt)
        
        # Process event animations
        event_animator.process_events(window.screen, battle)
        
        # Render
        window.screen.fill((20, 20, 30))
        
        # Render arena and creatures
        arena_renderer.render(window.screen, battle)
        creature_renderer.render(window.screen, battle)
        
        # Highlight selected creature
        if selected_battle_creature and selected_battle_creature.is_alive():
            screen_pos = arena_renderer.world_to_screen(
                selected_battle_creature.spatial.position,
                window.screen,
                battle.arena
            )
            pygame.draw.circle(
                window.screen,
                (255, 255, 0),
                (int(screen_pos[0]), int(screen_pos[1])),
                30,
                3
            )
        
        # Render event animations
        event_animator.update(dt)
        event_animator.render(window.screen)
        
        # Render UI
        ui_components.render(window.screen, battle, paused)
        
        # Render creature inspector
        creature_inspector.render(window.screen)
        
        # Instructions overlay
        if not creature_inspector.visible:
            font = pygame.font.Font(None, 24)
            instruction_text = font.render(
                "Click on creatures to inspect them!",
                True,
                (255, 255, 100)
            )
            text_rect = instruction_text.get_rect(center=(window.width // 2, 50))
            
            # Draw background
            bg_rect = text_rect.inflate(20, 10)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            window.screen.blit(bg_surface, bg_rect.topleft)
            
            window.screen.blit(instruction_text, text_rect)
        
        pygame.display.flip()
        
        # Check if battle ended
        if battle.is_over and not paused:
            pygame.time.wait(3000)
            break
    
    # Show final statistics
    print("\n=== Battle Complete ===")
    print("\nFinal Statistics:")
    
    survivors = [bc for bc in battle.creatures if bc.is_alive()]
    if survivors:
        print(f"\nSurvivors: {len(survivors)}")
        for bc in survivors:
            creature = bc.creature
            print(f"\n{creature.name}:")
            print(f"  HP: {creature.stats.hp:.0f}/{creature.stats.max_hp}")
            print(f"  Battles: {creature.history.battles_fought} ({creature.history.battles_won}W)")
            print(f"  Kills: {len(creature.history.kills)}")
            print(f"  Damage Dealt: {creature.history.total_damage_dealt:.0f}")
            
            # Show top skills
            top_skills = creature.skills.get_highest_skills(3)
            if top_skills:
                print(f"  Top Skills:")
                for skill_type, level in top_skills:
                    skill = creature.skills.get_skill(skill_type)
                    print(f"    - {skill.config.name}: Level {level}")
    
    pygame.quit()
    print("\nDemo complete!")


def _get_creature_at_position(
    mouse_pos: tuple,
    battle,
    arena_renderer: 'ArenaRenderer',
    window: GameWindow
) -> 'BattleCreature':
    """
    Find creature at mouse position.
    
    Args:
        mouse_pos: Mouse (x, y) position
        battle: The spatial battle
        arena_renderer: Arena renderer for coordinate conversion
        window: Game window
        
    Returns:
        BattleCreature if found, None otherwise
    """
    click_radius = 25  # Pixels
    
    for bc in battle.creatures:
        if not bc.is_alive():
            continue
        
        screen_pos = arena_renderer.world_to_screen(
            bc.spatial.position,
            window.screen,
            battle.arena
        )
        dx = mouse_pos[0] - screen_pos[0]
        dy = mouse_pos[1] - screen_pos[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance <= click_radius:
            return bc
    
    return None


if __name__ == "__main__":
    main()
