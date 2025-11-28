"""
Event Animator - Handles visual effects and animations for battle events.

Displays floating damage numbers, hit effects, and other visual feedback
for battle events. Now uses WORLD COORDINATES for all effects to ensure
they stay pinned to the world during camera panning.
"""

import pygame
import math
import random
from typing import List, Dict
from ..systems.battle_spatial import BattleEvent, BattleEventType
from ..models.spatial import Vector2D


class Particle:
    """
    Represents a simple visual particle in WORLD SPACE.
    """
    def __init__(self, position, velocity, color, size, lifetime, shape="circle"):
        self.position = list(position) # World position
        self.velocity = list(velocity) # World velocity
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.age = 0.0
        self.active = True
        self.shape = shape # "circle", "square", "diamond"

    def update(self, delta_time):
        self.age += delta_time
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time
        # Shrink over time
        self.size = max(0, self.size - (self.size / self.lifetime) * delta_time)

    def is_expired(self):
        return self.age >= self.lifetime

    def render(self, screen, camera):
        if self.size <= 0:
            return
            
        # Transform to screen coordinates
        screen_pos = camera.world_to_screen(Vector2D(self.position[0], self.position[1]))
        
        # Scale size by zoom
        scaled_size = max(1, int(self.size * camera.zoom))
        
        if self.shape == "square":
            rect = pygame.Rect(0, 0, scaled_size, scaled_size)
            rect.center = screen_pos
            pygame.draw.rect(screen, self.color, rect)
        elif self.shape == "diamond":
            # Draw a diamond (rotated square)
            half = scaled_size // 2
            points = [
                (screen_pos[0], screen_pos[1] - half),
                (screen_pos[0] + half, screen_pos[1]),
                (screen_pos[0], screen_pos[1] + half),
                (screen_pos[0] - half, screen_pos[1])
            ]
            pygame.draw.polygon(screen, self.color, points)
        else: # circle
            pygame.draw.circle(screen, self.color, screen_pos, scaled_size)


class AnimatedEffect:
    """
    Represents a temporary visual effect in WORLD SPACE.
    
    Attributes:
        position: World position
        text: Text to display (for damage numbers, etc.)
        color: Effect color
        lifetime: Total lifetime in seconds
        age: Current age in seconds
        velocity: Movement velocity in world units
    """
    
    def __init__(
        self,
        position: tuple = (0, 0),
        text: str = "",
        color: tuple = (255, 255, 255),
        lifetime: float = 1.0,
        velocity: tuple = (0, -10) # Slower world velocity
    ):
        self.position = list(position)
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.velocity = list(velocity)
        self.font = pygame.font.Font(None, 24) # Base font size
        self.active = True
        self.scale_anim = True # Enable pop animation
    
    def reset(self, position: tuple, text: str, color: tuple, lifetime: float, velocity: tuple):
        """Reset the effect for reuse (object pooling)."""
        self.position = list(position)
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.velocity = list(velocity)
        self.active = True
    
    def update(self, delta_time: float):
        """Update effect animation."""
        self.age += delta_time
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time
    
    def is_expired(self) -> bool:
        """Check if effect should be removed."""
        return self.age >= self.lifetime
    
    def render(self, screen: pygame.Surface, camera):
        """Render the effect."""
        if self.is_expired():
            return
        
        # Transform to screen coordinates
        screen_pos = camera.world_to_screen(Vector2D(self.position[0], self.position[1]))
        
        # Calculate alpha based on lifetime
        progress = self.age / self.lifetime
        alpha = int(255 * (1.0 - progress))
        alpha = max(0, min(255, alpha))
        
        if self.text:
            # Pop animation: Scale up quickly then settle
            scale = 1.0
            if self.scale_anim:
                if progress < 0.2:
                    scale = 1.0 + (progress / 0.2) * 0.5 # Pop up to 1.5x
                else:
                    scale = 1.5 - ((progress - 0.2) / 0.8) * 0.5 # Settle back to 1.0
            
            # Scale font size by zoom (clamped)
            base_size = 24
            zoomed_size = int(base_size * camera.zoom * scale)
            zoomed_size = max(12, min(48, zoomed_size))
            
            # We can't easily scale the font object every frame efficiently.
            # Instead, we'll render at base size and scale the surface, or use a few cached fonts.
            # For simplicity and "pixel art" feel, let's just use the base font and not scale text size with zoom too much,
            # but we WILL apply the pop animation scale.
            
            # Actually, let's stick to a fixed font size for readability, but apply the pop scale.
            # To do this efficiently, we render then transform.
            
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(alpha)
            
            if scale != 1.0:
                w = text_surface.get_width()
                h = text_surface.get_height()
                text_surface = pygame.transform.scale(text_surface, (int(w * scale), int(h * scale)))
            
            # Add shadow
            shadow_surface = self.font.render(self.text, True, (0, 0, 0))
            shadow_surface.set_alpha(alpha // 2)
            if scale != 1.0:
                w = shadow_surface.get_width()
                h = shadow_surface.get_height()
                shadow_surface = pygame.transform.scale(shadow_surface, (int(w * scale), int(h * scale)))
            
            text_rect = text_surface.get_rect(center=screen_pos)
            shadow_rect = shadow_surface.get_rect(center=(screen_pos[0] + 2, screen_pos[1] + 2))
            
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
        self.particles: List[Particle] = []
        
        # Store recent events for animation purposes
        self.pending_events: List[BattleEvent] = []
        
        # Object pool for AnimatedEffect instances
        self._effect_pool: List[AnimatedEffect] = []
        self._max_pool_size = 50  # Limit pool size to prevent unbounded growth
    
    def _get_effect_from_pool(
        self,
        position: tuple,
        text: str = "",
        color: tuple = (255, 255, 255),
        lifetime: float = 1.0,
        velocity: tuple = (0, -10)
    ) -> AnimatedEffect:
        """
        Get an effect from the pool or create a new one.
        """
        if self._effect_pool:
            effect = self._effect_pool.pop()
            effect.reset(position, text, color, lifetime, velocity)
            return effect
        else:
            return AnimatedEffect(position, text, color, lifetime, velocity)
    
    def _return_effect_to_pool(self, effect: AnimatedEffect):
        """Return an effect to the pool for reuse."""
        if len(self._effect_pool) < self._max_pool_size:
            effect.active = False
            self._effect_pool.append(effect)
    
    def add_battle_event(self, event: BattleEvent):
        """Process a battle event and create appropriate visual effects."""
        self.pending_events.append(event)
    
    def on_battle_event(self, event: BattleEvent):
        """Callback method for battle events."""
        self.add_battle_event(event)
    
    def process_events(self, screen: pygame.Surface, battle, camera):
        """
        Process pending events and create effects.
        """
        for event in self.pending_events:
            self._create_effect_for_event(event, screen, battle, camera)
        
        self.pending_events.clear()
    
    def create_explosion(self, position, color=(255, 100, 50), count=20):
        """Create an explosion effect at WORLD position."""
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(10, 40) # World units speed
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(1, 3) # World units size
            lifetime = random.uniform(0.5, 1.0)
            # Mix of squares and diamonds for style
            shape = random.choice(["square", "diamond"])
            self.particles.append(Particle(position, velocity, color, size, lifetime, shape))

    def create_blood_splatter(self, position, color=(200, 0, 0), count=10):
        """Create a blood splatter effect at WORLD position."""
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(5, 20) # World units
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(0.5, 1.5) # Small particles
            lifetime = random.uniform(0.3, 0.8)
            self.particles.append(Particle(position, velocity, color, size, lifetime, shape="square"))

    def create_eat_crumbs(self, position, color=(150, 255, 150), count=5):
        """Create crumb particles at WORLD position."""
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(2, 10)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(0.5, 1.0)
            lifetime = random.uniform(0.3, 0.6)
            self.particles.append(Particle(position, velocity, color, size, lifetime, shape="square"))

    def _create_effect_for_event(self, event: BattleEvent, screen: pygame.Surface, battle, camera):
        """Create visual effect for a specific event."""
        
        # NOTE: We now use event.target.spatial.position directly (WORLD coordinates)
        # We do NOT convert to screen coordinates here.
        
        if event.event_type == BattleEventType.DAMAGE_DEALT and event.target:
            # Create floating damage number
            world_pos = (event.target.spatial.position.x, event.target.spatial.position.y)
            
            damage_text = f"{int(event.value)}"
            self.effects.append(
                self._get_effect_from_pool(
                    position=world_pos,
                    text=damage_text,
                    color=(255, 255, 255), # White flash for damage
                    lifetime=0.8,
                    velocity=(0, -15) # Float up
                )
            )
            
            # Add Blood Particles
            self.create_blood_splatter(world_pos)
        
        elif event.event_type == BattleEventType.HEALING and event.actor:
            world_pos = (event.actor.spatial.position.x, event.actor.spatial.position.y)
            
            heal_text = f"+{int(event.value)}"
            self.effects.append(
                self._get_effect_from_pool(
                    position=world_pos,
                    text=heal_text,
                    color=(100, 255, 100),
                    lifetime=1.0,
                    velocity=(0, -10)
                )
            )
        
        elif event.event_type == BattleEventType.CRITICAL_HIT:
            if event.target:
                world_pos = (event.target.spatial.position.x, event.target.spatial.position.y)
                
                self.effects.append(
                    self._get_effect_from_pool(
                        position=(world_pos[0], world_pos[1] - 2),
                        text="CRIT!",
                        color=(255, 255, 50), # Bright yellow
                        lifetime=1.0,
                        velocity=(5, -20)
                    )
                )
                self.create_blood_splatter(world_pos, count=20)
        
        elif event.event_type == BattleEventType.MISS:
            if event.target:
                world_pos = (event.target.spatial.position.x, event.target.spatial.position.y)
                
                self.effects.append(
                    self._get_effect_from_pool(
                        position=world_pos,
                        text="MISS",
                        color=(100, 200, 255),
                        lifetime=0.8,
                        velocity=(0, -15)
                    )
                )
        
        elif event.event_type == BattleEventType.ABILITY_USE:
            if event.actor:
                world_pos = (event.actor.spatial.position.x, event.actor.spatial.position.y)
                
                self.effects.append(
                    self._get_effect_from_pool(
                        position=(world_pos[0], world_pos[1] - 3),
                        text=event.ability.name if event.ability else "Attack!",
                        color=(255, 200, 100),
                        lifetime=0.6,
                        velocity=(0, -10)
                    )
                )
                
                if event.ability and event.ability.name == "Orbital Strike":
                    self.create_explosion(world_pos, color=(255, 100, 50), count=50)
        
        elif event.event_type == BattleEventType.CREATURE_FAINT:
            if event.target:
                world_pos = (event.target.spatial.position.x, event.target.spatial.position.y)
                
                # Death "Poof"
                self.create_explosion(world_pos, color=(200, 200, 200), count=15)
                
                self.effects.append(
                    self._get_effect_from_pool(
                        position=world_pos,
                        text="XXX",
                        color=(150, 150, 150),
                        lifetime=1.5,
                        velocity=(0, -5)
                    )
                )
        
        elif event.event_type == BattleEventType.PELLET_CONSUMED:
            if 'position' in event.data:
                pos = event.data['position']
                self.create_eat_crumbs(pos)
        
        elif event.event_type == BattleEventType.PELLET_REPRODUCE:
             if 'position' in event.data:
                pos = event.data['position']
                self.effects.append(
                    self._get_effect_from_pool(
                        position=pos,
                        text="+",
                        color=(100, 255, 100),
                        lifetime=0.5,
                        velocity=(0, -5)
                    )
                )

    def update(self, delta_time: float):
        """Update all active effects."""
        for effect in self.effects:
            effect.update(delta_time)
            
        for particle in self.particles:
            particle.update(delta_time)
        
        # Cleanup
        active_effects = []
        for effect in self.effects:
            if effect.is_expired():
                self._return_effect_to_pool(effect)
            else:
                active_effects.append(effect)
        self.effects = active_effects
        
        self.particles = [p for p in self.particles if not p.is_expired()]
    
    def render(self, screen: pygame.Surface, camera):
        """
        Render all active effects.
        
        Args:
            screen: Pygame surface
            camera: Camera instance for coordinate transformation
        """
        for effect in self.effects:
            effect.render(screen, camera)
            
        for particle in self.particles:
            particle.render(screen, camera)
    
    def clear(self):
        """Clear all effects."""
        self.effects.clear()
        self.particles.clear()
        self.pending_events.clear()
    

