"""
Game Window - Main Pygame window and game loop manager.

Handles Pygame initialization, the main game loop, and coordinates
all rendering components for the battle visualization.
"""

import pygame
from typing import Optional, Callable, List
from ..systems.battle_spatial import SpatialBattle, BattleEvent


class GameWindow:
    """
    Main game window that manages the Pygame display and game loop.
    
    Coordinates between the battle system and all rendering components
    to display the real-time spatial battle.
    
    Attributes:
        width: Window width in pixels
        height: Window height in pixels
        fps: Target frames per second
        title: Window title
        screen: Pygame display surface
        clock: Pygame clock for frame timing
        running: Whether the game loop is active
        paused: Whether the game is paused
    """
    
    def __init__(
        self,
        width: int = 1200,
        height: int = 800,
        fps: int = 30,
        title: str = "EvoBattle - Spatial Combat Arena"
    ):
        """
        Initialize the game window.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            fps: Target frames per second (default 30 for better performance)
            title: Window title
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        
        # Pygame initialization
        pygame.init()
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        
        # State
        self.running = False
        self.paused = False
        self.battle: Optional[SpatialBattle] = None
        
        # Colors
        self.bg_color = (20, 20, 30)
        
        # Event callbacks
        self._input_callbacks: List[Callable[[pygame.event.Event], None]] = []
        
        # Performance monitoring
        self.show_fps = True
        self._fps_font = pygame.font.Font(None, 24)
        self._frame_times = []
        self._max_frame_samples = 30
    
    def set_fps(self, fps: int):
        """
        Set the target FPS at runtime.
        
        Args:
            fps: Target frames per second
        """
        self.fps = max(10, min(120, fps))  # Clamp between 10 and 120
    
    def toggle_fps_display(self):
        """Toggle the FPS counter display."""
        self.show_fps = not self.show_fps
    
    def _render_fps(self, screen: pygame.Surface, actual_fps: float):
        """
        Render FPS counter overlay.
        
        Args:
            screen: Pygame surface to draw on
            actual_fps: Current measured FPS
        """
        if not self.show_fps:
            return
        
        # Determine color based on performance
        if actual_fps >= self.fps * 0.9:
            color = (100, 255, 100)  # Green - good
        elif actual_fps >= self.fps * 0.7:
            color = (255, 255, 100)  # Yellow - okay
        else:
            color = (255, 100, 100)  # Red - poor
        
        fps_text = f"FPS: {actual_fps:.1f} / {self.fps}"
        fps_surface = self._fps_font.render(fps_text, True, color)
        
        # Position in top-right corner
        fps_rect = fps_surface.get_rect(topright=(screen.get_width() - 10, 10))
        
        # Semi-transparent background
        bg_rect = fps_rect.inflate(10, 6)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 180), pygame.Rect(0, 0, bg_rect.width, bg_rect.height), border_radius=5)
        screen.blit(bg_surface, bg_rect.topleft)
        
        screen.blit(fps_surface, fps_rect)
    
    def set_battle(self, battle: SpatialBattle):
        """
        Set the battle to visualize.
        
        Args:
            battle: The spatial battle instance to render
        """
        self.battle = battle
    
    def add_input_callback(self, callback: Callable[[pygame.event.Event], None]):
        """
        Add a callback for handling input events.
        
        Args:
            callback: Function to call with pygame events
        """
        self._input_callbacks.append(callback)
        try:
            print(f"Input callback registered. Total callbacks: {len(self._input_callbacks)}")
        except Exception:
            pass
    
    def handle_events(self):
        """Process Pygame events (input, window events, etc.)."""
        for event in pygame.event.get():
            # Debug: log mouse events to verify they arrive
            try:
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    pos = getattr(event, 'pos', None)
                    print(f"Mouse event: {event.type} pos={pos} callbacks={len(self._input_callbacks)}")
            except Exception:
                pass
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_F3:
                    self.toggle_fps_display()
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    # Decrease FPS
                    self.set_fps(self.fps - 5)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    # Increase FPS (using = key which is + without shift)
                    self.set_fps(self.fps + 5)
            
            # Call custom input callbacks
            for callback in self._input_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in input callback: {e}")
    
    def clear_screen(self):
        """Clear the screen with the background color."""
        self.screen.fill(self.bg_color)
    
    def update_display(self):
        """Flip the display buffer to show the rendered frame."""
        pygame.display.flip()
        actual_dt = self.clock.tick(self.fps)
        
        # Track frame times for FPS calculation
        if len(self._frame_times) >= self._max_frame_samples:
            self._frame_times.pop(0)
        self._frame_times.append(actual_dt)
    
    def get_actual_fps(self) -> float:
        """
        Get the actual measured FPS.
        
        Returns:
            Current FPS based on recent frame times
        """
        if not self._frame_times:
            return 0.0
        
        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        if avg_frame_time > 0:
            return 1000.0 / avg_frame_time
        return 0.0
    
    def run(
        self,
        battle: SpatialBattle,
        arena_renderer,
        creature_renderer,
        ui_components,
        event_animator
    ):
        """
        Run the main game loop.
        
        Args:
            battle: The spatial battle to visualize
            arena_renderer: ArenaRenderer instance
            creature_renderer: CreatureRenderer instance
            ui_components: UIComponents instance
            event_animator: EventAnimator instance
        """
        self.battle = battle
        self.running = True
        
        # Calculate delta time for smooth updates
        last_time = pygame.time.get_ticks()
        
        # Register UI input handler if available
        try:
            # Prefer method name 'handle_event'
            if hasattr(ui_components, 'handle_event'):
                def _ui_callback(event):
                    try:
                        ui_components.handle_event(event, battle)
                    except Exception as e:
                        print(f"UIComponents.handle_event error: {e}")
                self.add_input_callback(_ui_callback)
                _registered_ui_callback = _ui_callback
            else:
                _registered_ui_callback = None
        except Exception:
            _registered_ui_callback = None
            
        while self.running and not battle.is_over:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            # Update battle (if not paused)
            if not self.paused:
                battle.update(delta_time)
            
            # Clear screen
            self.clear_screen()
            
            # Render everything first so interactive UI geometry (button rects) exists
            arena_renderer.render(self.screen, battle)
            creature_renderer.render(self.screen, battle)
            ui_components.render(self.screen, battle, self.paused)
            event_animator.update(delta_time)
            event_animator.render(self.screen)
            
            # Handle input after UI has been rendered so control rects are populated
            self.handle_events()
            
            # Render FPS counter
            self._render_fps(self.screen, self.get_actual_fps())
            
            # Update display
            self.update_display()
        
        # Show final state for a moment
        if battle.is_over:
            pygame.time.wait(2000)
        
        # Unregister UI callback if we registered one
        try:
            if '_registered_ui_callback' in locals() and _registered_ui_callback:
                try:
                    self._input_callbacks.remove(_registered_ui_callback)
                except Exception:
                    pass
        except Exception:
            pass
    
    def quit(self):
        """Clean up and quit Pygame."""
        pygame.quit()
    
    def get_screen_pos_from_world(
        self,
        world_x: float,
        world_y: float,
        arena_width: float,
        arena_height: float
    ) -> tuple:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_x: X coordinate in world space
            world_y: Y coordinate in world space
            arena_width: Width of the arena in world units
            arena_height: Height of the arena in world units
            
        Returns:
            (screen_x, screen_y) tuple
        """
        # Reserve space for UI panels (top, bottom, and sides)
        # Left margin for GENETIC STRAINS panel
        ui_margin_left = 250
        # Right margin for CREATURES and PELLET ECOSYSTEM panels
        ui_margin_right = 250
        # Top margin for header/title
        ui_margin_top = 80
        # Bottom margin for Battle Feed
        ui_margin_bottom = 200
        
        arena_screen_width = self.width - ui_margin_left - ui_margin_right
        arena_screen_height = self.height - ui_margin_top - ui_margin_bottom
        
        screen_x = ui_margin_left + (world_x / arena_width) * arena_screen_width
        screen_y = ui_margin_top + (world_y / arena_height) * arena_screen_height
        
        return (int(screen_x), int(screen_y))
    
    def get_arena_bounds(self) -> tuple:
        """
        Get the screen bounds for the arena rendering area.
        
        Arena is positioned in the center with margins for UI panels:
        - Left: GENETIC STRAINS panel (250px)
        - Right: CREATURES + PELLET ECOSYSTEM panels (250px)
        - Top: Header/title (80px)
        - Bottom: Battle Feed (200px)
        
        Returns:
            (x, y, width, height) tuple
        """
        # Left margin for GENETIC STRAINS panel
        ui_margin_left = 250
        # Right margin for CREATURES and PELLET ECOSYSTEM panels
        ui_margin_right = 250
        # Top margin for header/title
        ui_margin_top = 80
        # Bottom margin for Battle Feed
        ui_margin_bottom = 200
        
        x = ui_margin_left
        y = ui_margin_top
        width = self.width - ui_margin_left - ui_margin_right
        height = self.height - ui_margin_top - ui_margin_bottom
        
        return (x, y, width, height)
