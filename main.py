"""
EvoBattle - Evolution-based Battle Game
Main entry point for running the unified game with all features.
"""

import pygame
import random
import sys
import traceback
from typing import List, Optional

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.models.trait import Trait
from src.models.ecosystem_traits import (
    AGGRESSIVE, CAUTIOUS, FORAGER, EFFICIENT_METABOLISM,
    CURIOUS, GLUTTON, VORACIOUS, WANDERER, PICKY_EATER, INDISCRIMINATE_EATER,
    INTELLIGENT  # Neural brain learning trait
)
# Black & White systems
from src.models.creature_beliefs import CreatureBeliefSystem
from src.systems.observational_learning import ObservationalLearning
from src.systems.battle_spatial import SpatialBattle
from src.systems.living_world import LivingWorldBattleEnhancer
from src.rendering import (
    GameWindow, ArenaRenderer, CreatureRenderer, PelletRenderer,
    UIComponents, EventAnimator, CreatureInspector, PauseMenu,
    PauseMenuAction, PostGameSummary,
    Camera
)
from src.rendering.scientific_cursor import ScientificCursor, CursorRenderer, CursorTool
from src.controllers import ScientificCursorController
from src.models.spatial import Vector2D
from src.utils.name_generator import NameGenerator

# Optional imports for trait injection & analytics - provide safe fallbacks
try:
    from src.models.trait_analytics import TraitAnalytics
except Exception:
    class TraitAnalytics:
        def __init__(self, *args, **kwargs):
            pass

try:
    from src.systems.trait_injection import TraitInjectionSystem, InjectionConfig
except Exception:
    class InjectionConfig:
        def __init__(self, injection_enabled=False, **kwargs):
            self.injection_enabled = injection_enabled

    class TraitInjectionSystem:
        def __init__(self, config=None, analytics=None, seed=None):
            self.config = config
            self.analytics = analytics
            self._callbacks = []

        def register_injection_callback(self, cb):
            try:
                self._callbacks.append(cb)
            except Exception:
                pass

        def check_cosmic_event(self, generation: int) -> List[Trait]:
            return []

        def evaluate_population_pressure(self, pop_size, starvation_count, avg_health_norm, generation):
            return None

        def add_trait_via_callback(self, trait, reason):
            for cb in self._callbacks:
                try:
                    cb(trait, reason)
                except Exception:
                    pass

try:
    from src.systems.breeding import Breeding
except Exception:
    class Breeding:
        def __init__(self, mutation_rate: float = 0.0, trait_inheritance_chance: float = 0.0, injection_system: Optional[TraitInjectionSystem] = None):
            self.mutation_rate = mutation_rate
            self.trait_inheritance_chance = trait_inheritance_chance
            self.injection_system = injection_system


def create_creature(name: str, level: int = 5, traits: Optional[List[Trait]] = None) -> Creature:
    """
    Create a creature with randomized traits and abilities.
    
    This function creates a fully-initialized creature ready for battle, including:
    - Base stats scaled by level
    - Random traits from the ecosystem trait pool
    - Basic combat abilities (tackle, quick strike)
    - Initialized ecosystem features (maturity, hunger, hue)
    
    Args:
        name: Display name for the creature
        level: Starting level (affects base stats). Default is 5.
        traits: Optional list of traits. If None, 2 random traits are selected.
    
    Returns:
        Fully initialized Creature instance ready for battle
        
    Example:
        >>> creature = create_creature("Warrior", level=10, traits=[AGGRESSIVE, FORAGER])
        >>> print(f"{creature.name} has {creature.stats.max_hp} HP")
    """
    if traits is None:
        trait_pool = [
            AGGRESSIVE, CAUTIOUS, FORAGER, EFFICIENT_METABOLISM, 
            CURIOUS, WANDERER, INTELLIGENT  # Added INTELLIGENT for neural learning
        ]
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
    try:
        creature.add_ability(create_ability('tackle'))
        ability = create_ability('quick_strike')
        if ability:
            creature.add_ability(ability)
    except Exception:
        pass

    # Initialize optional ecosystem features if present
    if hasattr(creature, "mature"):
        creature.mature = True

    if hasattr(creature, "hunger"):
        creature.hunger = getattr(creature, "max_hunger", 100)

    if hasattr(creature, "stats"):
        creature.stats.hp = getattr(creature.stats, "max_hp", creature.stats.hp)

    if hasattr(creature, "hue"):
        creature.hue = random.uniform(0, 360)
    
    # NEW: Add Black & White systems
    # Belief system for learned knowledge
    creature.belief_system = CreatureBeliefSystem()
    
    # Observational learning system
    creature.observational_learning = ObservationalLearning(
        creature_id=creature.creature_id,
        belief_system=creature.belief_system
    )
    creature.observational_learning.apply_trait_modifiers(creature.traits)

    return creature


def create_unified_battle() -> SpatialBattle:
    """
    Create a complete EvoBattle world with all features enabled.
    
    This function sets up a full simulation including:
    - 30 creatures with random names and traits
    - Random biome selection (desert, forest, grassland, etc.)
    - Environmental system (weather, terrain, hazards)
    - Living world enhancer (hunger, reproduction, ecosystem dynamics)
    - Grass growth system (nutrient zones, pollination)
    
    The battle is configured for an engaging gameplay experience with:
    - Arena size: 160x100 units
    - Mixed creature levels (3-6)
    - Random trait distribution
    - Dynamic environment
    
    Returns:
        SpatialBattle instance with all systems initialized and ready to run
        
    Note:
        This function prints initialization details to console, including
        creature names, traits, and personality descriptions.
    """

    name_gen = NameGenerator()
    num_creatures = 30
    creature_names = name_gen.generate_batch(num_creatures)

    creatures = []
    for name in creature_names:
        level = random.randint(3, 6)
        creature = create_creature(name, level=level)
        creatures.append(creature)

    print(f"\nCreated {len(creatures)} creatures (sample):")
    for c in creatures[:5]:
        trait_names = [t.name for t in getattr(c, 'traits', [])]
        personality_desc = "(no personality)"
        if hasattr(c, 'personality'):
            try:
                personality_desc = c.personality.get_description()
            except Exception:
                pass
        print(f"- {c.name} (Lvl {c.level}): {', '.join(trait_names)} | {personality_desc}")

    # Create battle with random biome
    battle = SpatialBattle(
        creatures_or_team1=creatures,
        arena_width=200.0,
        arena_height=200.0,
        biome_type='random',
        enable_environment=True,
        initial_resources=30,  # Start with plenty of food
        resource_spawn_rate=0.5  # Spawn 0.5 pellets per second
    )

    # Create and attach enhancer
    enhancer = LivingWorldBattleEnhancer(battle)
    battle.enhancer = enhancer
    
    # Initialize battle start
    enhancer.on_battle_start(creatures)

    print("\n=== All Features Enabled ===")
    return battle


def get_creature_at_position(mouse_pos, battle, camera):
    """
    Find the creature at the given mouse position for selection.
    
    Uses a circular click radius to detect creatures near the mouse cursor.
    Converts screen coordinates to world coordinates for accurate detection.
    
    Args:
        mouse_pos: Tuple of (x, y) screen coordinates from pygame mouse event
        battle: SpatialBattle instance containing creatures
        camera: Camera instance for coordinate conversion
    
    Returns:
        BattleCreature if one is found within click radius, None otherwise
        
    Note:
        Click radius is set to 25 pixels for easy creature selection.
        Only alive creatures can be selected.
    """
    click_radius = 25
    for bc in battle.creatures:
        if not bc.is_alive():
            continue
        screen_pos = camera.world_to_screen(bc.spatial.position)
        dx = mouse_pos[0] - screen_pos[0]
        dy = mouse_pos[1] - screen_pos[1]
        distance = (dx * dx + dy * dy) ** 0.5
        if distance <= click_radius:
            return bc
    return None


def run_battle_loop(window, battle, injection: Optional[TraitInjectionSystem] = None, trait_pool: Optional[List[Trait]] = None) -> bool:
    """
    Run the main game loop for the battle simulation.
    
    This is the core game loop that handles:
    - User input (keyboard and mouse)
    - Battle simulation updates
    - Rendering (creatures, pellets, UI, animations)
    - Event handling (combat, reproduction)
    - Trait injection based on population pressure
    - Pause/resume functionality
    - Post-game summary
    
    Game Controls:
    - SPACE: Pause/Resume simulation
    - ESC: Open pause menu
    - ESC: Open pause menu
    - I: Toggle creature inspector panel
    - Click creatures: Select and inspect individual creatures
    - Mouse wheel: Scroll in creature inspector
    
    Args:
        window: GameWindow instance for rendering
        battle: SpatialBattle instance to simulate
        injection: Optional TraitInjectionSystem for procedural trait introduction
        trait_pool: Optional list to track available traits (modified in-place)
    
    Returns:
        bool: True if user wants to restart, False if quitting
        
    Game Loop Flow:
    1. Process user input events
    2. Update battle simulation (if not paused)
    3. Update animations and UI
    4. Render all game elements
    5. Check for trait injection opportunities
    6. Generate battle stories at intervals
    7. Display post-game summary when battle ends
    
    Trait Injection:
        The system monitors population health and introduces new traits when:
        - Cosmic events occur (periodic random injection)
        - Population pressure is high (starvation, low health)
        - New generations are born
        

    """
    # Initialize renderers
    from src.rendering.building_renderer import BuildingRenderer
    building_renderer = BuildingRenderer()
    arena_renderer = ArenaRenderer(show_grid=False, building_renderer=building_renderer)
    creature_renderer = CreatureRenderer()
    pellet_renderer = PelletRenderer(base_radius=6, show_generation=True)
    ui_components = UIComponents(max_log_entries=5, show_pellet_stats=True)
    
    # Initialize Camera
    # Use full window dimensions - UI panels will overlay the arena
    viewport_width = window.width
    viewport_height = window.height
    
    # Center camera on the arena (200x200)
    arena_center = Vector2D(100, 100)  # Center of 200x200 arena
    
    # Calculate zoom to fit arena in viewport
    # Arena is 200 units, base scale is 10px/unit
    # So 200 units * 10px/unit * zoom = viewport_width
    # zoom = viewport_width / (200 * 10) = viewport_width / 2000
    initial_zoom = min(viewport_width / 2000, viewport_height / 2000) * 0.9  # 90% to add margin
    
    camera = Camera(viewport_width, viewport_height, initial_position=arena_center, initial_zoom=initial_zoom)
    
    # Initialize Scientific Cursor Controller
    cursor_controller = ScientificCursorController(
        ScientificCursor(),
        CursorRenderer()
    )
    event_animator = EventAnimator()
    creature_inspector = CreatureInspector()
    pause_menu = PauseMenu()
    post_game_summary = PostGameSummary()
    font = pygame.font.Font(None, 24)

    arena_renderer.pellet_renderer = pellet_renderer

    try:
        battle.add_event_callback(ui_components.add_event_to_log)
        battle.add_event_callback(event_animator.on_battle_event)
    except Exception:
        pass



    clock = pygame.time.Clock()
    running = True
    paused = False
    simulation_speed = 1.0  # Speed multiplier: 0.5x, 1x, 2x, 5x, 10x
    expanded_feed_mode = False  # Toggle between arena and expanded feed view
    selected_battle_creature = None
    show_summary = False

    last_birth_count = getattr(battle, 'birth_count', 0)
    current_generation = 0
    last_pressure_check = -1.0

    print("\n=== Battle Started ===")

    # FPS Monitoring
    fps_update_timer = 0.0
    fps_update_interval = 0.5

    while running:
        dt = clock.tick(60) / 1000.0
        
        # Update FPS in title
        fps_update_timer += dt
        if fps_update_timer >= fps_update_interval:
            fps = clock.get_fps()
            alive_count = len([c for c in battle.creatures if c.is_alive()])
            pygame.display.set_caption(f"EvoBattle - FPS: {fps:.1f} | Creatures: {alive_count} | Pellets: {len(battle.arena.resources)}")
            fps_update_timer = 0.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            # Handle UI component interactions first (includes Dilemma, Toolbar, etc.)
            if ui_components.handle_event(event, battle, cursor_controller.cursor):
                continue

            if pause_menu.visible:
                action = pause_menu.handle_input(event)
                if action == PauseMenuAction.RESUME:
                    paused = False
                elif action == PauseMenuAction.RESTART:
                    return True
                elif action == PauseMenuAction.QUIT:
                    return False
                continue

            if show_summary:
                action = post_game_summary.handle_input(event)
                if action in ('menu', 'replay'):
                    return True
                elif action == 'export':
                    try:
                        filepath = post_game_summary.export_stats()
                        print(f"Stats exported to: {filepath}")
                    except Exception:
                        pass
                continue



            # Handle UI Events (including Toolbar)
            # print(f"Event: {event.type}")
            if ui_components.handle_event(event, battle, cursor_controller.cursor):
                print("UI Handled Event")
                continue

            if creature_inspector.handle_mouse_event(event, window.screen):
                continue



            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if creature_inspector.visible and not creature_inspector.is_pinned:
                        creature_inspector.hide()
                    else:
                        pause_menu.show()
                        paused = True
                elif event.key == pygame.K_SPACE:
                    if not pause_menu.visible:
                        paused = not paused

                elif event.key == pygame.K_i:
                    creature_inspector.toggle_visibility()
                elif event.key == pygame.K_e:
                    ui_components.show_ethics_dashboard = not ui_components.show_ethics_dashboard
                elif event.key == pygame.K_a:
                    ui_components.show_advisor_panel = not ui_components.show_advisor_panel
                
                # Simulation Speed Controls
                elif event.key == pygame.K_q:
                    simulation_speed = 0.5
                    print(f"Speed: 0.5x")
                elif event.key == pygame.K_w:
                    simulation_speed = 1.0
                    print(f"Speed: 1x (Normal)")
                elif event.key == pygame.K_r:
                    simulation_speed = 2.0
                    print(f"Speed: 2x")
                elif event.key == pygame.K_t:
                    simulation_speed = 5.0
                    print(f"Speed: 5x")
                elif event.key == pygame.K_y:
                    simulation_speed = 10.0
                    print(f"Speed: 10x")
                
                # Expanded Feed Mode Toggle
                elif event.key == pygame.K_f:
                    expanded_feed_mode = not expanded_feed_mode
                    mode_name = "EXPANDED FEED" if expanded_feed_mode else "ARENA VIEW"
                    print(f"Mode: {mode_name}")
                
                # Scientific Tool Selection
                elif event.key == pygame.K_1:
                    cursor_controller.cursor.select_tool(CursorTool.OBSERVE)
                elif event.key == pygame.K_2:
                    cursor_controller.cursor.select_tool(CursorTool.FOOD_DISPENSER)
                elif event.key == pygame.K_3:
                    cursor_controller.cursor.select_tool(CursorTool.STIMULATOR)
                elif event.key == pygame.K_4:
                    cursor_controller.cursor.select_tool(CursorTool.MARKER)




            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if event.button == 1:
                    # Handle Scientific Cursor Tools via controller
                    if cursor_controller.handle_event(event, battle, camera, get_creature_at_position):
                        continue

                    # Creature Selection
                    clicked_creature = get_creature_at_position(mouse_pos, battle, camera)
                    if clicked_creature:
                        selected_battle_creature = clicked_creature
                        creature_inspector.select_creature(clicked_creature)  # Pass BattleCreature, not just Creature
                        print(f"\nSelected: {clicked_creature.creature.name}")


            elif event.type == pygame.MOUSEWHEEL:
                # Check if mouse is over creature inspector first
                if creature_inspector.visible and creature_inspector._is_mouse_over_panel():
                    # Only scroll the inspector, don't zoom camera
                    creature_inspector.handle_scroll(-event.y)
                else:
                    # Only zoom camera when not over inspector
                    if event.y > 0:
                        camera.zoom_in(0.1)
                    elif event.y < 0:
                        camera.zoom_out(0.1)

        # Update camera (smooth interpolation)
        camera.update(dt)
        
        # Handle camera pan (middle mouse drag) - outside event loop for continuous input
        if pygame.mouse.get_pressed()[1]:  # Middle button
            rel = pygame.mouse.get_rel()
            camera.pan(-rel[0] * 0.5, -rel[1] * 0.5)  # Scale down for smoother control
        else:
            pygame.mouse.get_rel()  # Clear relative movement
        
        if not paused and not getattr(battle, 'is_over', False) and not (hasattr(battle, 'pending_dilemma') and battle.pending_dilemma):
            try:
                # Apply simulation speed multiplier
                adjusted_dt = dt * simulation_speed
                # Debug: Print dt occasionally
                # if random.random() < 0.01:
                #    print(f"Update dt: {adjusted_dt:.4f}")
                battle.update(adjusted_dt)
            except Exception as e:
                print(f"Error in battle.update: {e}")
                traceback.print_exc()
            
            # Auto-resolve dilemmas in expanded feed mode
            if expanded_feed_mode and hasattr(battle, 'pending_dilemma') and battle.pending_dilemma:
                try:
                    import random
                    dilemma = battle.pending_dilemma
                    # Randomly choose one of the available choices
                    if hasattr(dilemma, 'choices') and dilemma.choices:
                        random_choice_index = random.randint(0, len(dilemma.choices) - 1)
                        random_choice = dilemma.choices[random_choice_index]
                        # Resolve the dilemma with the choice index
                        if hasattr(battle, 'resolve_dilemma'):
                            battle.resolve_dilemma(random_choice_index)
                        else:
                            battle.pending_dilemma = None
                        print(f"[AUTO-RESOLVED] Dilemma: {dilemma.title} -> {random_choice.text}")
                except Exception as e:
                    print(f"Error auto-resolving dilemma: {e}")
                    battle.pending_dilemma = None



            # Trait injection checks
            try:
                birth_count = getattr(battle, 'birth_count', 0)
                if birth_count != last_birth_count:
                    current_generation += (birth_count - last_birth_count)
                    last_birth_count = birth_count
                    if injection:
                        try:
                            new_traits = injection.check_cosmic_event(current_generation)
                        except Exception:
                            new_traits = []
                        for t in new_traits:
                            try:
                                print(f"[COSMIC EVENT] new trait available: {getattr(t, 'name', str(t))}")
                                if trait_pool is not None:
                                    trait_pool.append(t)
                            except Exception:
                                pass

                if injection and getattr(battle, 'current_time', 0.0) - last_pressure_check >= 1.0:
                    last_pressure_check = getattr(battle, 'current_time', 0.0)
                    alive_bcs = [bc for bc in battle.creatures if bc.is_alive()]
                    pop_size = len(alive_bcs)
                    starvation_count = sum(1 for bc in alive_bcs if getattr(bc.creature, 'hunger', 100) < 10)

                    if pop_size > 0:
                        avg_health_norm = sum(
                            (bc.creature.stats.hp / max(1, getattr(bc.creature.stats, 'max_hp', 1)))
                            for bc in alive_bcs
                        ) / pop_size
                    else:
                        avg_health_norm = 0.0

                    try:
                        pressure_trait = injection.evaluate_population_pressure(pop_size, starvation_count, avg_health_norm, current_generation)
                    except Exception:
                        pressure_trait = None

                    if pressure_trait:
                        try:
                            print(f"[PRESSURE INJECTION] applying {getattr(pressure_trait, 'name', str(pressure_trait))} to survivors")
                            survivors = [bc.creature for bc in alive_bcs]
                            for c in survivors:
                                try:
                                    c.add_trait(pressure_trait.copy())
                                except Exception:
                                    pass
                        except Exception:
                            pass
            except Exception:
                pass

        creature_inspector.update(dt)
        event_animator.update(dt)
        cursor_controller.update(dt, getattr(battle, 'current_time', 0.0))
        try:
            event_animator.process_events(window.screen, battle, camera)
        except Exception:
            pass

        window.screen.fill((20, 20, 30))

        try:
            if expanded_feed_mode:
                # Expanded Feed Mode - Full screen battle feed
                ui_components.render_expanded_feed(window.screen, battle, simulation_speed, paused)
            else:
                # Normal Arena Mode
                arena_renderer.render(
                    window.screen, 
                    battle, 
                    camera=camera,
                    selected_creature_id=selected_battle_creature.creature.creature_id if selected_battle_creature else None,
                    hovered_creature_id=None,
                    show_debug=False
                )
                
                # Render Scientific Cursor Markers
                cursor_controller.render_markers(window.screen, camera)

                if selected_battle_creature and selected_battle_creature.is_alive():
                    screen_pos = camera.world_to_screen(selected_battle_creature.spatial.position)
                    
                    # Draw selection indicator (e.g. bracket or arrow)
                    # For now, simple circle is handled by render, but maybe we want extra UI here?
                    # Actually, render() already handles selection highlight.
                    # This block might be for something else, let's see context.
                    # It seems it was for drawing a line to target or similar.
                    pass
                    pygame.draw.circle(window.screen, (255, 255, 0), (int(screen_pos[0]), int(screen_pos[1])), 30, 3)

                event_animator.render(window.screen, camera)
                ui_components.render(window.screen, battle, paused, cursor_controller.cursor)
                cursor_controller.render_cursor(window.screen, pygame.mouse.get_pos())
                creature_inspector.render(window.screen)
        except Exception:
            traceback.print_exc()
            pass

        try:
            pause_menu.render(window.screen)
        except Exception:
            pass

        if show_summary:
            try:
                post_game_summary.render(window.screen)
            except Exception:
                pass

        # Instruction text removed - Scientific Toolbar now at top

        if paused and not pause_menu.visible:
            pause_font = pygame.font.Font(None, 48)
            pause_text = pause_font.render("PAUSED", True, (255, 255, 100))
            text_rect = pause_text.get_rect(center=(window.width // 2, window.height // 2))
            s = pygame.Surface((text_rect.width + 40, text_rect.height + 20))
            s.set_alpha(200)
            s.fill((30, 30, 40))
            window.screen.blit(s, (text_rect.x - 20, text_rect.y - 10))
            window.screen.blit(pause_text, text_rect)

        if getattr(battle, 'is_over', False) and not show_summary and not pause_menu.visible:
            try:
                post_game_summary.show(battle)
                show_summary = True
            except Exception:
                pass

        pygame.display.flip()

    return False


def main():
    print("=" * 70)
    print("EvoBattle - Evolution-Based Living World Simulator")
    print("=" * 70)

    pygame.init()

    window = GameWindow(width=1600, height=900, title="EvoBattle - Living World Simulator")

    trait_pool: List[Trait] = []
    analytics = TraitAnalytics()
    injection = TraitInjectionSystem(config=InjectionConfig(injection_enabled=True), analytics=analytics, seed=None)

    def on_trait_injected(trait, reason):
        try:
            name = trait.name
        except Exception:
            name = str(trait)
        print(f"[TRAIT INJECTED] {name} reason={reason}")
        try:
            trait_pool.append(trait)
        except Exception:
            pass

    try:
        injection.register_injection_callback(on_trait_injected)
    except Exception:
        pass

    print("All systems ready!")

    while True:
        battle = create_unified_battle()

        try:
            battle.breeding_system = Breeding(injection_system=injection)
        except Exception:
            try:
                battle.breeding_system = Breeding(mutation_rate=0.1, trait_inheritance_chance=0.8, injection_system=injection)
            except Exception:
                pass

        restart = run_battle_loop(window, battle, injection=injection, trait_pool=trait_pool)
        if not restart:
            break

        print("\n" + "=" * 70)
        print("Restarting simulation...")
        print("=" * 70)

    pygame.quit()
    print("\n" + "=" * 70)
    print("Thank you for playing EvoBattle!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
        try:
            pygame.quit()
        except Exception:
            pass
        sys.exit(0)
