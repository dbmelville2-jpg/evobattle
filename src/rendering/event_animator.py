"""
Event Animator - Handles visual effects and animations for battle events.

Displays floating damage numbers, hit effects, and other visual feedback
for battle events.
"""

import pygame
import math
from typing import List, Dict
from ..systems.battle_spatial import BattleEvent, BattleEventType
from ..models.spatial import Vector2D


class AnimatedEffect:
    """
    Represents a temporary visual effect.
    
    Attributes:
        position: Screen position
        text: Text to display (for damage numbers, etc.)
        color: Effect color
        lifetime: Total lifetime in seconds
        age: Current age in seconds
        velocity: Movement velocity
    """
    
    def __init__(
        self,
        position: tuple,
        text: str = "",
        color: tuple = (255, 255, 255),
        lifetime: float = 1.0,
        velocity: tuple = (0, -30)
    ):
        self.position = list(position)
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.velocity = list(velocity)
        self.font = pygame.font.Font(None, 24)
    
    def update(self, delta_time: float):
        """Update effect animation."""
        self.age += delta_time
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time
    
    def is_expired(self) -> bool:
        """Check if effect should be removed."""
        return self.age >= self.lifetime
    
    def render(self, screen: pygame.Surface):
        """Render the effect."""
        if self.is_expired():
            return
        
        # Calculate alpha based on lifetime
        alpha = int(255 * (1.0 - self.age / self.lifetime))
        alpha = max(0, min(255, alpha))
        
        if self.text:
            # Render text with fade out
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(alpha)
            
            # Add shadow
            shadow_surface = self.font.render(self.text, True, (0, 0, 0))
            shadow_surface.set_alpha(alpha // 2)
            
            text_rect = text_surface.get_rect(center=(int(self.position[0]), int(self.position[1])))
            shadow_rect = shadow_surface.get_rect(center=(int(self.position[0]) + 2, int(self.position[1]) + 2))
            
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)


class EventAnimator:
    """
    Manages visual effects and animations for battle events.
    
    Subscribes to battle events and creates visual effects like
    damage numbers, hit flashes, and ability animations.
    
    Attributes:
        effects: List of active animated effects
    """
    
    def __init__(self):
        """Initialize the event animator."""
        self.effects: List[AnimatedEffect] = []
        
        # Store recent events for animation purposes
        self.pending_events: List[BattleEvent] = []
    
    def add_battle_event(self, event: BattleEvent):
        """
        Process a battle event and create appropriate visual effects.
        
        Args:
            event: The battle event to animate
        """
        self.pending_events.append(event)
    
    def on_battle_event(self, event: BattleEvent):
        """
        Callback method for battle events (alias for add_battle_event).
        
        This method can be used directly as a callback for battle.add_event_callback().
        
        Args:
            event: The battle event to animate
        """
        self.add_battle_event(event)
    
    def process_events(self, screen: pygame.Surface, battle):
        """
        Process pending events and create effects.
        
        Args:
            screen: Pygame surface for coordinate conversion
            battle: Battle instance for world-to-screen conversion
        """
        for event in self.pending_events:
            self._create_effect_for_event(event, screen, battle)
        
        self.pending_events.clear()
    
    def _create_effect_for_event(self, event: BattleEvent, screen: pygame.Surface, battle):
        """Create visual effect for a specific event."""
        if event.event_type == BattleEventType.DAMAGE_DEALT and event.target:
            # Create floating damage number
            screen_pos = self._world_to_screen(
                event.target.spatial.position,
                screen,
                battle.arena
            )
            
            damage_text = f"-{event.value}"
            self.effects.append(
                AnimatedEffect(
                    position=screen_pos,
                    text=damage_text,
                    color=(255, 100, 100),
                    lifetime=1.5,
                    velocity=(0, -50)
                )
            )
        
        elif event.event_type == BattleEventType.HEALING and event.actor:
            # Create floating heal number
            screen_pos = self._world_to_screen(
                event.actor.spatial.position,
                screen,
                battle.arena
            )
            
            heal_text = f"+{event.value}"
            self.effects.append(
                AnimatedEffect(
                    position=screen_pos,
                    text=heal_text,
                    color=(100, 255, 100),
                    lifetime=1.5,
                    velocity=(0, -50)
                )
            )
        
        elif event.event_type == BattleEventType.CRITICAL_HIT:
            # Create "CRIT!" text if we have target info
            if event.target:
                screen_pos = self._world_to_screen(
                    event.target.spatial.position,
                    screen,
                    battle.arena
                )
                
                self.effects.append(
                    AnimatedEffect(
                        position=(screen_pos[0] + 30, screen_pos[1] - 20),
                        text="CRIT!",
                        color=(255, 255, 100),
                        lifetime=1.0,
                        velocity=(20, -30)
                    )
                )
        
        elif event.event_type == BattleEventType.MISS:
            # Create "MISS" text
            if event.target:
                screen_pos = self._world_to_screen(
                    event.target.spatial.position,
                    screen,
                    battle.arena
                )
                
                self.effects.append(
                    AnimatedEffect(
                        position=screen_pos,
                        text="MISS",
                        color=(150, 150, 150),
                        lifetime=1.0,
                        velocity=(0, -30)
                    )
                )
        
        elif event.event_type == BattleEventType.SUPER_EFFECTIVE:
            # Create "Super Effective!" text
            if event.target:
                screen_pos = self._world_to_screen(
                    event.target.spatial.position,
                    screen,
                    battle.arena
                )
                
                self.effects.append(
                    AnimatedEffect(
                        position=(screen_pos[0], screen_pos[1] - 30),
                        text="Super Effective!",
                        color=(255, 200, 50),
                        lifetime=1.2,
                        velocity=(0, -40)
                    )
                )
        
        elif event.event_type == BattleEventType.CREATURE_FAINT:
            # Create faint effect
            if event.target:
                screen_pos = self._world_to_screen(
                    event.target.spatial.position,
                    screen,
                    battle.arena
                )
                
                self.effects.append(
                    AnimatedEffect(
                        position=screen_pos,
                        text="FAINTED",
                        color=(200, 200, 200),
                        lifetime=2.0,
                        velocity=(0, -20)
                    )
                )
    
    def update(self, delta_time: float):
        """
        Update all active effects.
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Update all effects
        for effect in self.effects:
            effect.update(delta_time)
        
        # Remove expired effects
        self.effects = [e for e in self.effects if not e.is_expired()]
    
    def render(self, screen: pygame.Surface, battle=None):
        """
        Render all active effects.
        
        Args:
            screen: Pygame surface to draw on
            battle: Optional battle instance (for consistency with other renderers)
        """
        for effect in self.effects:
            effect.render(screen)
    
    def clear(self):
        """Clear all effects and pending events."""
        self.effects.clear()
        self.pending_events.clear()
    
    def _world_to_screen(
        self,
        world_pos: Vector2D,
        screen: pygame.Surface,
        arena
    ) -> tuple:
        """Convert world coordinates to screen coordinates."""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        ui_margin_top = 100
        ui_margin_side = 50
        ui_margin_bottom = 150
        
        arena_width = screen_width - (ui_margin_side * 2)
        arena_height = screen_height - ui_margin_top - ui_margin_bottom
        
        screen_x = ui_margin_side + (world_pos.x / arena.width) * arena_width
        screen_y = ui_margin_top + (world_pos.y / arena.height) * arena_height
        
        return (int(screen_x), int(screen_y))
