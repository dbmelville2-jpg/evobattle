"""
Camera System - Handles 2D view transformations.

Provides a camera that can pan and zoom around the game world, converting
between world coordinates and screen coordinates.
"""

import pygame
from typing import Tuple, Optional
from ..models.spatial import Vector2D


class Camera:
    """
    A 2D camera for scrolling and zooming around the game world.
    
    Attributes:
        position (Vector2D): Center position of the camera in world coordinates
        zoom (float): Current zoom level (1.0 = normal, 2.0 = 2x zoom)
        viewport_width (int): Width of the view area in pixels
        viewport_height (int): Height of the view area in pixels
        min_zoom (float): Minimum zoom level
        max_zoom (float): Maximum zoom level
    """
    
    def __init__(
        self,
        viewport_width: int,
        viewport_height: int,
        initial_position: Optional[Vector2D] = None,
        initial_zoom: float = 1.0
    ):
        """
        Initialize the camera.
        
        Args:
            viewport_width: Width of the screen/window
            viewport_height: Height of the screen/window
            initial_position: Starting center position (default: 0,0)
            initial_zoom: Starting zoom level (default: 1.0)
        """
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.position = initial_position or Vector2D(0, 0)
        self.zoom = initial_zoom
        
        # Constraints
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.bounds_min = Vector2D(-50, -50)
        self.bounds_max = Vector2D(250, 250)
        
        # Movement smoothing
        self.target_position = self.position
        self.target_zoom = self.zoom
        self.smooth_speed = 10.0  # Higher = faster smoothing
        
    def update(self, delta_time: float):
        """
        Update camera position and zoom with smoothing.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        # Clamp delta_time to prevent overshoot at very low FPS
        dt = min(delta_time, 0.1)
        
        # Frame-rate independent smoothing using exponential decay
        # factor = 1 - exp(-speed * dt)
        # This ensures we never overshoot the target even with large dt
        import math
        smoothing_factor = 1.0 - math.exp(-self.smooth_speed * dt)
        
        # Smooth movement
        if self.position != self.target_position:
            diff = self.target_position - self.position
            if diff.magnitude() < 0.1:
                self.position = self.target_position
            else:
                self.position = self.position + (diff * smoothing_factor)
                
        # Smooth zoom
        if abs(self.zoom - self.target_zoom) > 0.001:
            self.zoom += (self.target_zoom - self.zoom) * smoothing_factor
            
    def world_to_screen(self, world_pos: Vector2D) -> Tuple[int, int]:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_pos: Position in the game world
            
        Returns:
            (x, y) pixel coordinates on screen
        """
        # 1. Translate world to be relative to camera center
        rel_x = world_pos.x - self.position.x
        rel_y = world_pos.y - self.position.y
        
        # 2. Scale by zoom
        scaled_x = rel_x * self.zoom * 10.0  # Base scale: 10 pixels per unit
        scaled_y = rel_y * self.zoom * 10.0
        
        # 3. Translate to screen center
        screen_x = scaled_x + (self.viewport_width / 2)
        screen_y = scaled_y + (self.viewport_height / 2)
        
        return (int(screen_x), int(screen_y))
        
    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Vector2D:
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_pos: (x, y) pixel coordinates on screen
            
        Returns:
            Vector2D position in the game world
        """
        screen_x, screen_y = screen_pos
        
        # 1. Translate from screen center
        scaled_x = screen_x - (self.viewport_width / 2)
        scaled_y = screen_y - (self.viewport_height / 2)
        
        # 2. Unscale
        rel_x = scaled_x / (self.zoom * 10.0)
        rel_y = scaled_y / (self.zoom * 10.0)
        
        # 3. Translate back to world absolute
        world_x = rel_x + self.position.x
        world_y = rel_y + self.position.y
        
        return Vector2D(world_x, world_y)
        
    def move(self, dx: float, dy: float):
        """
        Move the camera target.
        
        Args:
            dx: Change in X
            dy: Change in Y
        """
        # Adjust movement speed based on zoom (move faster when zoomed out)
        speed_factor = 1.0 / self.zoom
        movement = Vector2D(dx, dy) * speed_factor
        
        new_pos = self.target_position + movement
        self.target_position = self._clamp_position(new_pos)
        
    def set_zoom(self, zoom_level: float, focus_point: Optional[Tuple[int, int]] = None):
        """
        Set the target zoom level.
        
        Args:
            zoom_level: New zoom level
            focus_point: Optional screen point to zoom towards (e.g. mouse cursor)
        """
        old_zoom = self.target_zoom
        new_zoom = max(self.min_zoom, min(self.max_zoom, zoom_level))
        
        if focus_point and old_zoom != new_zoom:
            # Zoom towards the focus point
            # 1. Get world pos of focus point before zoom
            # We use current zoom for calculation to be accurate to current state
            # But we're setting target zoom, so this is an approximation for smooth zooming
            # For perfect zooming towards mouse, we'd need to adjust position immediately
            
            # Simple approach: Just zoom
            pass
            
        self.target_zoom = new_zoom
        
    def _clamp_position(self, pos: Vector2D) -> Vector2D:
        """Keep camera within world bounds."""
        x = max(self.bounds_min.x, min(self.bounds_max.x, pos.x))
        y = max(self.bounds_min.y, min(self.bounds_max.y, pos.y))
        return Vector2D(x, y)
        
    def zoom_in(self, amount: float = 0.1):
        """
        Zoom in by a fixed amount.
        
        Args:
            amount: How much to increase zoom (default: 0.1)
        """
        self.set_zoom(self.target_zoom + amount)
        
    def zoom_out(self, amount: float = 0.1):
        """
        Zoom out by a fixed amount.
        
        Args:
            amount: How much to decrease zoom (default: 0.1)
        """
        self.set_zoom(self.target_zoom - amount)
        
    def pan(self, dx: float, dy: float):
        """
        Pan the camera (alias for move).
        
        Args:
            dx: Change in X
            dy: Change in Y
        """
        self.move(dx, dy)
