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
        fps: int = 60,
        title: str = "EvoBattle - Spatial Combat Arena"
    ):
        """
        Initialize the game window.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            fps: Target frames per second
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
    
    def handle_events(self):
        """Process Pygame events (input, window events, etc.)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
            
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
        self.clock.tick(self.fps)
    
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
        
        while self.running and not battle.is_over:
            # Handle input
            self.handle_events()
            
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            # Update battle (if not paused)
            if not self.paused:
                battle.update(delta_time)
            
            # Clear screen
            self.clear_screen()
            
            # Render everything
            arena_renderer.render(self.screen, battle)
            creature_renderer.render(self.screen, battle)
            ui_components.render(self.screen, battle, self.paused)
            event_animator.update(delta_time)
            event_animator.render(self.screen)
            
            # Update display
            self.update_display()
        
        # Show final state for a moment
        if battle.is_over:
            pygame.time.wait(2000)
    
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
        # Reserve space for UI (top and sides)
        ui_margin_top = 100
        ui_margin_side = 50
        ui_margin_bottom = 150
        
        arena_screen_width = self.width - (ui_margin_side * 2)
        arena_screen_height = self.height - ui_margin_top - ui_margin_bottom
        
        screen_x = ui_margin_side + (world_x / arena_width) * arena_screen_width
        screen_y = ui_margin_top + (world_y / arena_height) * arena_screen_height
        
        return (int(screen_x), int(screen_y))
    
    def get_arena_bounds(self) -> tuple:
        """
        Get the screen bounds for the arena rendering area.
        
        Returns:
            (x, y, width, height) tuple
        """
        ui_margin_top = 100
        ui_margin_side = 50
        ui_margin_bottom = 150
        
        x = ui_margin_side
        y = ui_margin_top
        width = self.width - (ui_margin_side * 2)
        height = self.height - ui_margin_top - ui_margin_bottom
        
        return (x, y, width, height)
