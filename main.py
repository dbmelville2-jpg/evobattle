"""
EvoBattle - Evolution-based Battle Game
Main entry point for running the unified game with all features.

Combines in one cohesive experience:
- Living World with creature inspector, personalities, skills, and histories
- Pellet Evolution with visual traits and generation tracking
- Ecosystem Survival with hunger, foraging, and population dynamics

PERFORMANCE OPTIMIZATIONS:
This game uses several optimizations for smooth 60 FPS with large populations:

1. SPATIAL HASH GRID (Issue #14):
   - SpatialBattle uses SpatialHashGrid for O(k) proximity queries
   - Replaces O(n²) brute-force targeting and collision detection
   - Enables stable performance with 80+ creatures and 100+ pellets
   - Grid is automatically managed by battle system (insert/update/remove)

2. RENDERING OPTIMIZATIONS (Issue #15):
   - Grid Caching: Arena grid lines cached as surface, redrawn only on resize
   - Text Caching: Creature/UI text surfaces cached (200-300 entry limit)
   - Effect Pooling: AnimatedEffect objects reused instead of created/destroyed
   - Combined impact: ~200% performance improvement for large battles

3. RUNTIME PERFORMANCE CONTROLS:
   Keyboard shortcuts for performance tuning:
   - F3: Toggle FPS counter display
   - +/=: Increase target FPS by 5 (clamped 10-120)
   - -: Decrease target FPS by 5 (clamped 10-120)
   - Default: 30 FPS for broad hardware compatibility
   
For more details, see:
- SPATIAL_OPTIMIZATION.md - Spatial hash grid documentation
- RENDERING_DOCUMENTATION.md - Rendering system and optimization details
"""

import pygame
import random
import sys
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.models.trait import Trait
from src.models.ecosystem_traits import (
    AGGRESSIVE, CAUTIOUS, FORAGER, EFFICIENT_METABOLISM,
    CURIOUS, GLUTTON, VORACIOUS, WANDERER, PICKY_EATER, INDISCRIMINATE_EATER
)
from src.systems.battle_spatial import SpatialBattle
from src.systems.living_world import LivingWorldBattleEnhancer
from src.rendering import (
    GameWindow, ArenaRenderer, CreatureRenderer, PelletRenderer,
    UIComponents, EventAnimator, CreatureInspector, PauseMenu,
    PauseMenuAction, PostGameSummary, StoryViewer, StoryViewerAction
)
from src.systems.battle_story_summarizer import (
    BattleStoryGenerator, BattleStoryTracker, StoryTone
)
from src.utils.name_generator import NameGenerator

# New imports to wire the TraitInjection system
from src.models.trait_analytics import TraitAnalytics
except Exception:
    # Fallback minimal implementation if module not present
    class TraitAnalytics:
        def __init__(self, *args, **kwargs):
            pass

try:
from src.systems.trait_injection import TraitInjectionSystem, InjectionConfig
from src.systems.breeding import Breeding


def create_creature(name: str, level: int = 5, traits: list = None) -> Creature:
    """
    Create a creature with full ecosystem, living world, and pellet features.
    
    This unified creature supports:
    - Living world: personalities, skills, history, relationships
    - Ecosystem: hunger, foraging, breeding
    - Combat: stats, abilities, tactics
    """
    if traits is None:
        # Mix of combat and ecosystem traits
        trait_pool = [AGGRESSIVE, CAUTIOUS, FORAGER, EFFICIENT_METABOLISM, 
                      CURIOUS, WANDERER]
        traits = random.sample(trait_pool, k=2)
    
    base_stats = Stats(
        max_hp=80 + level * 10,
        attack=12 + level * 2,
        defense=10 + level * 2,
        speed=15 + level
    )
    
    creature_type = CreatureType(
        name="Creature",
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
    
    # Add abilities
    creature.add_ability(create_ability('tackle'))
    ability = create_ability('quick_strike')
    if ability:
        creature.add_ability(ability)
    
    # Initialize ecosystem features
    if hasattr(creature, "mature"):
        creature.mature = True  # Ready to breed
    
    if hasattr(creature, "hunger"):
        creature.hunger = getattr(creature, "max_hunger", 100)
    
    if hasattr(creature, "stats"):
        creature.stats.hp = getattr(creature.stats, "max_hp", creature.stats.hp)
    
    if hasattr(creature, "hue"):
        creature.hue = random.uniform(0, 360)  # For family colors
    
    return creature


def create_unified_battle():
    """
    Create a unified battle with all features enabled:
    - Living world (personalities, skills, history)
    - Pellet evolution (trait-based pellets that reproduce)
    - Ecosystem survival (hunger, foraging, breeding)
    
    PERFORMANCE NOTE:
    Uses SpatialBattle which employs SpatialHashGrid for optimized:
    - Creature targeting: O(k) instead of O(n²)
    - Breeding proximity checks: O(n) instead of O(n²)
    - Resource queries: O(k) instead of O(n²)
    where k is the number of entities in nearby grid cells (typically 5-10)
    
    See SPATIAL_OPTIMIZATION.md for technical details.
    """
    print("\n=== Creating Unified EvoBattle World ===")
    
    # Generate unique creature names
    name_gen = NameGenerator()
    num_creatures = 30 # starting creatures
    creature_names = name_gen.generate_batch(num_creatures)
    
    creatures = []
    for i, name in enumerate(creature_names):
        level = random.randint(3, 6)
        creature = create_creature(name, level=level)
        creatures.append(creature)
    
    print(f"\nCreated {len(creatures)} creatures (sample):")
    for c in creatures[:5]:
        trait_names = [t.name for t in c.traits]
        print(f"  {c.name}: {', '.join(trait_names)} (lvl {c.level})")
        print(f"    Personality: {c.personality.get_description()}")
    if len(creatures) > 5:
        print(f"  ... and {len(creatures) - 5} more")
    
    # Create battle with balanced settings for all features
    # NOTE: SpatialBattle automatically creates and manages SpatialHashGrid
    # for creatures and resources (via Arena). No manual grid management needed.
    battle = SpatialBattle(
        creatures,
        arena_width=120.0,
        arena_height=100.0,
        resource_spawn_rate=0.001,  # Reduced from 0.15 to 0.06 for better balance
        initial_resources=40  # Starting pellets
    )
    
    # Enable living world features
    enhancer = LivingWorldBattleEnhancer(battle)
    battle.enhancer = enhancer
    enhancer.on_battle_start(creatures)
    
    print("\n=== All Features Enabled ===")
    print("  ✓ Living World: Personalities, skills, history, relationships")
    print("  ✓ Pellet Evolution: Visual traits, generation tracking, reproduction")
    print("  ✓ Ecosystem: Hunger, foraging, breeding, population dynamics")
    print("  ✓ Combat: Spatial battles with abilities and tactics")
    print("  ✓ Optimizations: Spatial hash grid, rendering cache, effect pooling")
    
    return battle


def run_battle_loop(window, battle, injection=None, trait_pool=None):
    """
    Run the main unified battle game loop with all features.
    
    Features include:
    - Living world: Creature inspector, personalities, skills, history
    - Pellet evolution: Visual trait rendering, generation tracking
    - Ecosystem: Hunger bars, population stats, breeding
    - Combat: Spatial battles, abilities, event animations
    
    PERFORMANCE OPTIMIZATIONS APPLIED:
    1. ArenaRenderer: Grid caching enabled (cached surface reused each frame)
    2. CreatureRenderer: Text surface caching (200 entry limit)
    3. UIComponents: Text surface caching (300 entry limit)
    4. EventAnimator: Effect object pooling (50 object pool)
    5. GameWindow: Default 30 FPS target (adjustable at runtime)
    
    RUNTIME CONTROLS:
    - Click creatures: Inspect history and stats
    - I: Toggle creature inspector
    - SPACE: Pause/Resume
    - ESC: Pause Menu
    - F3: Toggle FPS counter
    - +/=: Increase FPS by 5
    - -: Decrease FPS by 5
    
    Args:
        window: Game window
        battle: Spatial battle instance with all features enabled
        injection: optional TraitInjectionSystem instance
        trait_pool: optional list to collect injected traits
    """
    # Create all renderers with optimized settings
    # Grid rendering OFF by default for best performance (can toggle with show_grid=True)
    # When enabled, grid is automatically cached for minimal overhead
    arena_renderer = ArenaRenderer(show_grid=False)
    creature_renderer = CreatureRenderer()  # Text caching enabled by default
    pellet_renderer = PelletRenderer(base_radius=6, show_generation=True)
    ui_components = UIComponents(max_log_entries=10, show_pellet_stats=True)  # Text caching enabled
    event_animator = EventAnimator()  # Effect pooling enabled by default
    creature_inspector = CreatureInspector()
    pause_menu = PauseMenu()
    post_game_summary = PostGameSummary()
    story_viewer = StoryViewer(width=700, height=600)
    font = pygame.font.Font(None, 24)
    
    # Initialize story generation system
    story_generator = BattleStoryGenerator(default_tone=StoryTone.DRAMATIC)
    story_tracker = BattleStoryTracker(
        generator=story_generator,
        story_interval_seconds=300.0  # 5 minutes for production
    )
    story_tracker.start_tracking()
    
    # Connect pellet renderer to arena renderer
    arena_renderer.pellet_renderer = pellet_renderer
    
    # Subscribe to battle events
    battle.add_event_callback(ui_components.add_event_to_log)
    battle.add_event_callback(event_animator.on_battle_event)
    
    # Add story event callback
    def on_battle_event(event):
        story_tracker.generator.add_event(event)
    battle.add_event_callback(on_battle_event)
    
    # Game state
    clock = pygame.time.Clock()
    running = True
    paused = False
    selected_battle_creature = None
    show_summary = False
    show_story = False
    current_story = "Battle in progress... Story will be generated after 5 minutes of combat.\n\nPress 'S' to view this panel again at any time."
    current_tone = StoryTone.DRAMATIC
    last_story_notification = 0.0

    # Track generation by births for injection checks
    last_birth_count = getattr(battle, 'birth_count', 0)
    current_generation = 0

    # Pressure-check timer (run evaluate_population_pressure once per second)
    last_pressure_check = -1.0

    # Set initial story in viewer
    story_viewer.set_story(current_story, current_tone)
    
    print("\n=== Battle Started ===")
    print("Controls:")
    print("  Click on creatures to inspect their history and stats")
    print("  I: Toggle creature inspector")
    print("  S: View battle story")
    print("  SPACE: Pause/Resume")
    print("  ESC: Pause Menu")
    print("  R: Restart (from pause menu)")
    print("  F3: Toggle FPS counter")
    print("  +/=: Increase FPS | -: Decrease FPS")
    print("\nWatch creatures develop skills, pellets evolve, and populations grow!")
    print("All performance optimizations active (spatial grid, caching, pooling)")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Pause menu handling
            if pause_menu.visible:
                action = pause_menu.handle_input(event)
                if action == PauseMenuAction.RESUME:
                    paused = False
                elif action == PauseMenuAction.RESTART:
                    return True  # Restart
                elif action == PauseMenuAction.QUIT:
                    return False
                continue
            
            # Post-game summary handling
            if show_summary:
                action = post_game_summary.handle_input(event)
                if action == 'menu' or action == 'replay':
                    return True  # Restart
                elif action == 'export':
                    filepath = post_game_summary.export_stats()
                    print(f"Stats exported to: {filepath}")
                continue
            
            # Story viewer handling
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
                continue
            
            # Inspector handling
            if creature_inspector.handle_mouse_event(event, window.screen):
                continue
            
            # Regular input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_story:
                        show_story = False
                    elif creature_inspector.visible and not creature_inspector.is_pinned:
                        creature_inspector.hide()
                    else:
                        pause_menu.show()
                        paused = True
                elif event.key == pygame.K_SPACE:
                    if not pause_menu.visible and not show_story:
                        paused = not paused
                elif event.key == pygame.K_s:
                    show_story = not show_story
                    if show_story:
                        # Update story when opening viewer
                        story_viewer.set_story(current_story, current_tone)
                elif event.key == pygame.K_i:
                    creature_inspector.toggle_visibility()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    clicked_creature = get_creature_at_position(
                        mouse_pos, battle, arena_renderer, window
                    )
                    if clicked_creature:
                        selected_battle_creature = clicked_creature
                        creature_inspector.select_creature(clicked_creature.creature)
                        print(f"\nSelected: {clicked_creature.creature.name}")
            
            elif event.type == pygame.MOUSEWHEEL:
                creature_inspector.handle_scroll(-event.y)
        
        # Update battle
        if not paused and not show_story and not battle.is_over:
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

            # === Trait injection periodic checks ===
            try:
                # Track births as a proxy for generation
                birth_count = getattr(battle, 'birth_count', 0)
                if birth_count != last_birth_count:
                    # Increment generation when births occurred
                    current_generation += (birth_count - last_birth_count)
                    last_birth_count = birth_count

                    if injection:
                        new_traits = injection.check_cosmic_event(current_generation)
                        for t in new_traits:
                            print(f"[COSMIC EVENT] new trait available: {t.name}")
                            if trait_pool is not None:
                                try:
                                    trait_pool.append(t)
                                except Exception as e:
                                    print(f"Warning: failed to append trait to trait_pool: {e}")

                # Evaluate population pressure once per second
                if injection and battle.current_time - last_pressure_check >= 1.0:
                    last_pressure_check = battle.current_time

                    alive_bcs = [bc for bc in battle.creatures if bc.is_alive()]
                    pop_size = len(alive_bcs)
                    starvation_count = sum(1 for bc in alive_bcs if getattr(bc.creature, 'hunger', 100) < 10)

                    if pop_size > 0:
                        # Compute average normalized health (hp / max_hp)
                        avg_health_norm = sum(
                            (bc.creature.stats.hp / max(1, getattr(bc.creature.stats, 'max_hp', 1)))
                            for bc in alive_bcs
                        ) / pop_size
                    else:
                        avg_health_norm = 0.0

                    pressure_trait = injection.evaluate_population_pressure(
                        pop_size, starvation_count, avg_health_norm, current_generation
                    )
                    if pressure_trait:
                        print(f"[PRESSURE INJECTION] applying {pressure_trait.name} to survivors")
                        survivors = [bc.creature for bc in alive_bcs]
                        for c in survivors:
                            try:
                                c.add_trait(pressure_trait.copy())
                            except Exception as e:
                                print(f"Warning: failed to add pressure trait: {e}")
            except Exception as e:
                # Don't let injection issues crash the game loop
                print(f"Trait injection error: {e}")

        # Update animations
        creature_inspector.update(dt)
        event_animator.update(dt)
        event_animator.process_events(window.screen, battle)
        
        # Render
        window.screen.fill((20, 20, 30))
        
        if show_story:
            # Draw dimmed battle background
            arena_renderer.render(window.screen, battle)
            pellet_renderer.render(window.screen, battle)
            creature_renderer.render(window.screen, battle)
            
            # Darken the background
            dark_overlay = pygame.Surface((window.width, window.height))
            dark_overlay.set_alpha(180)
            dark_overlay.fill((0, 0, 0))
            window.screen.blit(dark_overlay, (0, 0))
            
            # Draw story viewer
            story_viewer.draw(window.screen, 350, 150)
        
        else:
            # Render arena
            arena_renderer.render(window.screen, battle)
            
            # Render pellets with evolution tracking
            pellet_renderer.render(window.screen, battle)
            
            # Render creatures
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
            event_animator.render(window.screen)
            
            # Render main UI (includes battle timer, population, pellet stats, event log)
            ui_components.render(window.screen, battle, paused)
            
            # Render creature inspector
            creature_inspector.render(window.screen)
            
            # Draw story notification if recently generated
            if not paused and battle.current_time - last_story_notification < 5.0:
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
                pygame.draw.rect(window.screen, (30, 30, 40), bg_rect)
                pygame.draw.rect(window.screen, (255, 215, 0), bg_rect, 2)
                window.screen.blit(notification_text, (x, y))
        
        # Render pause menu
        pause_menu.render(window.screen)
        
        # Render post-game summary
        if show_summary:
            post_game_summary.render(window.screen)
        
        # Instructions overlay
        if not pause_menu.visible and not show_summary and not creature_inspector.visible and not show_story:
            instruction_text = font.render(
                "Click creatures! | I: Inspector | S: Story | SPACE: Pause | ESC: Menu",
                True,
                (255, 255, 100)
            )
            text_rect = instruction_text.get_rect(center=(window.width // 2, 50))
            
            bg_rect = text_rect.inflate(20, 10)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            window.screen.blit(bg_surface, bg_rect.topleft)
            window.screen.blit(instruction_text, text_rect)
        
        # Pause indicator
        if paused and not pause_menu.visible:
            pause_font = pygame.font.Font(None, 48)
            pause_text = pause_font.render("PAUSED", True, (255, 255, 100))
            text_rect = pause_text.get_rect(center=(window.width // 2, window.height // 2))
            
            s = pygame.Surface((text_rect.width + 40, text_rect.height + 20))
            s.set_alpha(200)
            s.fill((30, 30, 40))
            window.screen.blit(s, (text_rect.x - 20, text_rect.y - 10))
            window.screen.blit(pause_text, text_rect)
        
        # Show post-game summary when battle ends
        if battle.is_over and not show_summary and not pause_menu.visible:
            post_game_summary.show(battle)
            show_summary = True
        
        pygame.display.flip()
    
    return False


def get_creature_at_position(mouse_pos, battle, arena_renderer, window):
    """
    Find creature at mouse position for UI click handling.
    
    NOTE: This uses simple iteration because:
    1. It's a UI event handler, not a performance-critical game loop operation
    2. Only runs on mouse click (infrequent), not every frame
    3. The number of alive creatures is typically small (< 20)
    4. Adding spatial grid query would be overkill for this use case
    
    For game logic operations (targeting, breeding, collision), SpatialBattle
    uses SpatialHashGrid for O(k) proximity queries instead of O(n) iteration.
    """
    click_radius = 25
    
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


def main():
    """
    Main entry point for EvoBattle - Unified living world simulator.
    
    PERFORMANCE CONFIGURATION:
    - GameWindow defaults to 30 FPS (broad hardware compatibility)
    - ArenaRenderer grid rendering disabled by default (enable with show_grid=True)
    - All caching and pooling optimizations enabled automatically
    - Runtime FPS adjustment available via keyboard (+/- keys)
    
    For performance tuning, modify settings in run_battle_loop():
    - ArenaRenderer(show_grid=False): Toggle grid visualization
    - GameWindow(fps=30): Adjust target frame rate (10-120)
    - UIComponents(max_log_entries=10): Control event log size
    
    See RENDERING_DOCUMENTATION.md for detailed performance recommendations.
    """
    print("=" * 70)
    print("EvoBattle - Evolution-Based Living World Simulator")
    print("=" * 70)
    print("\nInitializing game systems...")
    
    # Initialize Pygame
    pygame.init()
    
    # Create window with default performance settings
    # Default: 30 FPS for broad hardware compatibility
    # Adjustable at runtime with +/- keys (clamped 10-120)
    # Larger window (1600x900) to accommodate side panels without overlapping arena
    window = GameWindow(
        width=1600,
        height=900,
        title="EvoBattle - Living World Simulator"
        # fps parameter defaults to 30 in GameWindow.__init__
    )

    # === Trait injection wiring (global for this run) ===
    trait_pool = []
    analytics = TraitAnalytics()
    injection = TraitInjectionSystem(
        config=InjectionConfig(injection_enabled=True),
        analytics=analytics,
        seed=None
    )

    def on_trait_injected(trait, reason):
        # quick visible notification in console
        try:
            name = trait.name
        except Exception:
            name = str(trait)
        print(f"[TRAIT INJECTED] {name} reason={reason}")
        # optional: add to a global trait pool for the game to use
        try:
            trait_pool.append(trait)
        except Exception as e:
            print(f"Warning: failed to append trait to trait_pool: {e}")

    injection.register_injection_callback(on_trait_injected)
    # ==================================================
    
    print("✓ All systems ready!")
    print("✓ Performance optimizations: Spatial grid, caching, effect pooling")
    
    # Main game loop - restart on request
    while True:
        # Create unified battle with all features
        battle = create_unified_battle()

        # Wire injection into breeding so breeding-based injections run
        try:
            battle.breeding_system = Breeding(injection_system=injection)
        except Exception:
            try:
                battle.breeding_system = Breeding(mutation_rate=0.1, trait_inheritance_chance=0.8, injection_system=injection)
            except Exception as e:
                print(f"Warning: could not replace battle.breeding_system with injection-enabled Breeding: {e}")
        
        # Run the game; pass injection and trait_pool so run_battle_loop can use them
        restart = run_battle_loop(window, battle, injection=injection, trait_pool=trait_pool)
        
        if not restart:
            break
        
        print("\n" + "=" * 70)
        print("Restarting simulation...")
        print("=" * 70)
    
    # Cleanup
    pygame.quit()
    print("\n" + "=" * 70)
    print("Thank you for playing EvoBattle!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
        pygame.quit()
        sys.exit(0)
