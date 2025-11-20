"""
EvoBattle - Evolution-based Battle Game
Main entry point for running the unified game with all features.
"""

import pygame
import random
import sys
from typing import List, Optional

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
        trait_pool = [AGGRESSIVE, CAUTIOUS, FORAGER, EFFICIENT_METABOLISM, CURIOUS, WANDERER]
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
        arena_width=160.0,
        arena_height=100.0,
        biome_type='random',
        enable_environment=True
    )

    # Create and attach enhancer
    enhancer = LivingWorldBattleEnhancer(battle)
    battle.enhancer = enhancer
    
    # Initialize battle start
    enhancer.on_battle_start(creatures)

    print("\n=== All Features Enabled ===")
    return battle


def get_creature_at_position(mouse_pos, battle, arena_renderer, window):
    """
    Find the creature at the given mouse position for selection.
    
    Uses a circular click radius to detect creatures near the mouse cursor.
    Converts screen coordinates to world coordinates for accurate detection.
    
    Args:
        mouse_pos: Tuple of (x, y) screen coordinates from pygame mouse event
        battle: SpatialBattle instance containing creatures
        arena_renderer: ArenaRenderer for coordinate conversion
        window: GameWindow for screen dimensions
    
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


def run_battle_loop(window, battle, injection: Optional[TraitInjectionSystem] = None, trait_pool: Optional[List[Trait]] = None) -> bool:
    """
    Run the main game loop for the battle simulation.
    
    This is the core game loop that handles:
    - User input (keyboard and mouse)
    - Battle simulation updates
    - Rendering (creatures, pellets, UI, animations)
    - Event handling (combat, reproduction, story generation)
    - Trait injection based on population pressure
    - Pause/resume functionality
    - Post-game summary
    
    Game Controls:
    - SPACE: Pause/Resume simulation
    - ESC: Open pause menu
    - S: View AI-generated battle story
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
        
    Story Generation:
        AI-generated battle narratives are created every 5 minutes,
        providing dramatic, comedic, or epic summaries of events.
    """
    arena_renderer = ArenaRenderer(show_grid=False)
    creature_renderer = CreatureRenderer()
    pellet_renderer = PelletRenderer(base_radius=6, show_generation=True)
    ui_components = UIComponents(max_log_entries=10, show_pellet_stats=True)
    event_animator = EventAnimator()
    creature_inspector = CreatureInspector()
    pause_menu = PauseMenu()
    post_game_summary = PostGameSummary()
    story_viewer = StoryViewer(width=700, height=600)
    font = pygame.font.Font(None, 24)

    story_generator = BattleStoryGenerator(default_tone=StoryTone.DRAMATIC)
    story_tracker = BattleStoryTracker(generator=story_generator, story_interval_seconds=300.0)
    try:
        story_tracker.start_tracking()
    except Exception:
        pass

    arena_renderer.pellet_renderer = pellet_renderer

    try:
        battle.add_event_callback(ui_components.add_event_to_log)
        battle.add_event_callback(event_animator.on_battle_event)
    except Exception:
        pass

    def on_battle_event(event):
        try:
            story_tracker.generator.add_event(event)
        except Exception:
            pass
    try:
        battle.add_event_callback(on_battle_event)
    except Exception:
        pass

    clock = pygame.time.Clock()
    running = True
    paused = False
    selected_battle_creature = None
    show_summary = False
    show_story = False
    current_story = "Battle in progress... Story will be generated after 5 minutes of combat.\n\nPress 'S' to view this panel again at any time."
    current_tone = StoryTone.DRAMATIC
    last_story_notification = 0.0

    last_birth_count = getattr(battle, 'birth_count', 0)
    current_generation = 0
    last_pressure_check = -1.0

    try:
        story_viewer.set_story(current_story, current_tone)
    except Exception:
        pass

    print("\n=== Battle Started ===")

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

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

            if show_story:
                try:
                    result = story_viewer.handle_event(event, 350, 150)
                except Exception:
                    result = None
                if result:
                    action, data = result
                    if action == StoryViewerAction.CLOSE:
                        show_story = False
                    elif action == StoryViewerAction.CHANGE_TONE:
                        current_tone = data
                        try:
                            current_story = story_tracker.generator.generate_story(tone=current_tone)
                            story_viewer.set_story(current_story, current_tone)
                        except Exception:
                            pass
                    elif action == StoryViewerAction.REGENERATE:
                        try:
                            current_story = story_tracker.generator.generate_story(tone=current_tone)
                            story_viewer.set_story(current_story, current_tone)
                        except Exception:
                            pass
                    elif action == StoryViewerAction.EXPORT_TXT:
                        try:
                            filepath = "battle_story.txt"
                            story_tracker.generator.export_story(current_story, filepath, 'txt')
                        except Exception:
                            pass
                    elif action == StoryViewerAction.EXPORT_MD:
                        try:
                            filepath = "battle_story.md"
                            story_tracker.generator.export_story(current_story, filepath, 'md')
                        except Exception:
                            pass
                continue

            if creature_inspector.handle_mouse_event(event, window.screen):
                continue

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
                        try:
                            story_viewer.set_story(current_story, current_tone)
                        except Exception:
                            pass
                elif event.key == pygame.K_i:
                    creature_inspector.toggle_visibility()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    clicked_creature = get_creature_at_position(mouse_pos, battle, arena_renderer, window)
                    if clicked_creature:
                        selected_battle_creature = clicked_creature
                        creature_inspector.select_creature(clicked_creature.creature)
                        print(f"\nSelected: {clicked_creature.creature.name}")

            elif event.type == pygame.MOUSEWHEEL:
                creature_inspector.handle_scroll(-event.y)
            
            # Handle UI component interactions (buttons, etc)
            ui_components.handle_event(event, battle)

        if not paused and not show_story and not getattr(battle, 'is_over', False):
            try:
                battle.update(dt)
            except Exception:
                pass

            try:
                for log in battle.get_battle_log():
                    if log not in getattr(story_tracker.generator, 'battle_logs', []):
                        story_tracker.generator.add_log(log)
            except Exception:
                pass

            try:
                if story_tracker.should_generate_story():
                    current_story = story_tracker.generate_and_store_story(tone=current_tone)
                    story_viewer.set_story(current_story, current_tone)
                    last_story_notification = getattr(battle, 'current_time', 0.0)
            except Exception:
                pass

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
        try:
            event_animator.process_events(window.screen, battle)
        except Exception:
            pass

        window.screen.fill((20, 20, 30))

        try:
            if show_story:
                arena_renderer.render(window.screen, battle)
                pellet_renderer.render(window.screen, battle)
                creature_renderer.render(window.screen, battle)

                dark_overlay = pygame.Surface((window.width, window.height))
                dark_overlay.set_alpha(180)
                dark_overlay.fill((0, 0, 0))
                window.screen.blit(dark_overlay, (0, 0))

                story_viewer.draw(window.screen, 350, 150)
            else:
                arena_renderer.render(window.screen, battle)
                pellet_renderer.render(window.screen, battle)
                creature_renderer.render(window.screen, battle)

                if selected_battle_creature and selected_battle_creature.is_alive():
                    screen_pos = arena_renderer.world_to_screen(
                        selected_battle_creature.spatial.position,
                        window.screen,
                        battle.arena
                    )
                    pygame.draw.circle(window.screen, (255, 255, 0), (int(screen_pos[0]), int(screen_pos[1])), 30, 3)

                event_animator.render(window.screen)
                ui_components.render(window.screen, battle, paused)
                creature_inspector.render(window.screen)

                if not paused and getattr(battle, 'current_time', 0.0) - last_story_notification < 5.0:
                    notification_font = pygame.font.Font(None, 36)
                    notification_text = notification_font.render(
                        "New Story Available! Press 'S' to view",
                        True,
                        (255, 215, 0)
                    )
                    x = (window.width - notification_text.get_width()) // 2
                    y = 50
                    bg_rect = notification_text.get_rect(topleft=(x-10, y-5))
                    bg_rect.width += 20
                    bg_rect.height += 10
                    pygame.draw.rect(window.screen, (30, 30, 40), bg_rect)
                    pygame.draw.rect(window.screen, (255, 215, 0), bg_rect, 2)
                    window.screen.blit(notification_text, (x, y))
        except Exception:
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

        if not pause_menu.visible and not show_summary and not creature_inspector.visible and not show_story:
            try:
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
            except Exception:
                pass

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
