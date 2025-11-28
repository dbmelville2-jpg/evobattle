"""
Scientific Cursor - Player Interaction System for EvoBattle

This module implements the scientific research tools that replace the "Hand of God"
mechanic from Black & White. Players interact with the simulation using various
scientific instruments rather than divine powers.

Tools available:
- OBSERVE: Inspect creatures and environment (default)
- FOOD_DISPENSER: Reward creatures with food
- STIMULATOR: Apply mild negative stimulus to discourage behavior
- MARKER: Mark areas as safe/danger zones
- SAMPLER: Take genetic samples (future: for analysis)
- RELOCATOR: Move creatures for experiments
- BARRIER: Create temporary walls/obstacles
- PHEROMONE: Create chemical trails to guide creatures
- ASTEROID: Orbital impact (God Tool)
- APEX: Spawn Apex Predator (God Tool)
"""

from enum import Enum
from typing import Optional, Tuple, List, Dict
import pygame
from dataclasses import dataclass


class CursorTool(Enum):
    """Available scientific tools for player interaction"""
    OBSERVE = "observe"
    FOOD_DISPENSER = "dispenser"
    STIMULATOR = "stimulator"
    MARKER = "marker"
    SAMPLER = "sampler"
    RELOCATOR = "relocator"
    BARRIER = "barrier"
    PHEROMONE = "pheromone"
    ASTEROID = "asteroid"
    APEX = "apex"


class MarkerType(Enum):
    """Types of area markers"""
    SAFE = "safe"
    DANGER = "danger"
    FOOD_SOURCE = "food_source"
    SHELTER = "shelter"


@dataclass
class AreaMarker:
    """Represents a marked area in the simulation"""
    position: Tuple[float, float]
    marker_type: MarkerType
    radius: float
    duration: float  # How long marker lasts (-1 for permanent)
    created_at: float
    
    def is_expired(self, current_time: float) -> bool:
        """Check if marker has expired"""
        if self.duration < 0:
            return False
        return (current_time - self.created_at) > self.duration


class ScientificCursor:
    """
    Player's scientific interaction system.
    
    Manages tool selection, resource costs, and tool usage.
    Each tool has a resource cost and recharges over time.
    """
    
    def __init__(self):
        """Initialize scientific cursor system"""
        self.current_tool = CursorTool.OBSERVE
        self.tool_charge = 1000.0  # Resource for using tools
        self.max_charge = 1000.0
        self.recharge_rate = 20.0  # Per second
        
        # Tool costs
        self.tool_costs = {
            CursorTool.OBSERVE: 0,
            CursorTool.FOOD_DISPENSER: 10,
            CursorTool.STIMULATOR: 15,
            CursorTool.MARKER: 5,
            CursorTool.SAMPLER: 8,
            CursorTool.RELOCATOR: 12,
            CursorTool.BARRIER: 20,
            CursorTool.PHEROMONE: 7,
            CursorTool.ASTEROID: 100,
            CursorTool.APEX: 80
        }
        
        # Active markers
        self.markers: List[AreaMarker] = []
        
        # Cursor appearance based on ethics (will be set by ethics system)
        self.ethics_score = 0.0  # -100 to +100
        
        # Relocator state
        self.held_creature = None # Reference to creature being moved
        
    def select_tool(self, tool: CursorTool):
        """Select a new tool"""
        self.current_tool = tool
        self.held_creature = None # Reset held creature on tool switch
        
        
    def can_use_tool(self) -> bool:
        """
        Check if current tool can be used.
        
        Returns:
            True if enough charge available
        """
        cost = self.tool_costs.get(self.current_tool, 0)
        return self.tool_charge >= cost
        
    def use_tool_charge(self) -> bool:
        """
        Consume charge for current tool.
        
        Returns:
            True if charge was consumed, False if not enough charge
        """
        cost = self.tool_costs.get(self.current_tool, 0)
        if self.tool_charge >= cost:
            self.tool_charge -= cost
            return True
        return False
        
    def update(self, dt: float, current_time: float):
        """
        Update cursor system - recharge and update markers.
        
        Args:
            dt: Time delta in seconds
            current_time: Current simulation time
        """
        # Recharge tool energy
        self.tool_charge = min(self.max_charge, self.tool_charge + self.recharge_rate * dt)
        
        # Remove expired markers
        self.markers = [m for m in self.markers if not m.is_expired(current_time)]
        
    def add_marker(self, position: Tuple[float, float], marker_type: MarkerType, 
                   radius: float = 5.0, duration: float = 30.0, current_time: float = 0.0):
        """
        Add an area marker.
        
        Args:
            position: World position (x, y)
            marker_type: Type of marker
            radius: Marker radius
            duration: How long marker lasts in seconds (-1 for permanent)
            current_time: Current simulation time
        """
        marker = AreaMarker(
            position=position,
            marker_type=marker_type,
            radius=radius,
            duration=duration,
            created_at=current_time
        )
        self.markers.append(marker)
        
    def get_markers_at_position(self, position: Tuple[float, float]) -> List[AreaMarker]:
        """
        Get all markers affecting a position.
        
        Args:
            position: World position to check
            
        Returns:
            List of markers affecting this position
        """
        result = []
        px, py = position
        for marker in self.markers:
            mx, my = marker.position
            dist_sq = (px - mx) ** 2 + (py - my) ** 2
            if dist_sq <= marker.radius ** 2:
                result.append(marker)
        return result
        
    def get_cursor_color(self) -> Tuple[int, int, int]:
        """
        Get cursor color based on ethics score.
        
        Returns:
            RGB color tuple
        """
        if self.ethics_score > 50:
            return (100, 200, 255)  # Calm blue - humane research
        elif self.ethics_score > 0:
            return (200, 200, 200)  # Neutral gray
        elif self.ethics_score > -50:
            return (255, 200, 100)  # Warning orange
        else:
            return (255, 50, 50)    # Harsh red - cruel experiments
            
    def get_cursor_size(self) -> int:
        """
        Get cursor size based on current tool.
        
        Returns:
            Cursor radius in pixels
        """
        sizes = {
            CursorTool.OBSERVE: 8,
            CursorTool.FOOD_DISPENSER: 12,
            CursorTool.STIMULATOR: 10,
            CursorTool.MARKER: 15,
            CursorTool.SAMPLER: 8,
            CursorTool.RELOCATOR: 14,
            CursorTool.BARRIER: 20,
            CursorTool.PHEROMONE: 10,
            CursorTool.ASTEROID: 30,
            CursorTool.APEX: 25
        }
        return sizes.get(self.current_tool, 8)
        
    def get_tool_name(self) -> str:
        """Get display name of current tool"""
        names = {
            CursorTool.OBSERVE: "Observe",
            CursorTool.FOOD_DISPENSER: "Food Dispenser",
            CursorTool.STIMULATOR: "Stimulator",
            CursorTool.MARKER: "Area Marker",
            CursorTool.SAMPLER: "Genetic Sampler",
            CursorTool.RELOCATOR: "Relocator",
            CursorTool.BARRIER: "Barrier Creator",
            CursorTool.PHEROMONE: "Pheromone Trail",
            CursorTool.ASTEROID: "Asteroid Strike",
            CursorTool.APEX: "Apex Predator"
        }
        return names.get(self.current_tool, "Unknown")
        
    def get_tool_description(self) -> str:
        """Get description of current tool"""
        descriptions = {
            CursorTool.OBSERVE: "Click to inspect creatures and environment",
            CursorTool.FOOD_DISPENSER: "Click to place food reward (Cost: 10)",
            CursorTool.STIMULATOR: "Click creature to apply mild negative stimulus (Cost: 15)",
            CursorTool.MARKER: "Click to mark area as safe/danger zone (Cost: 5)",
            CursorTool.SAMPLER: "Click creature to take genetic sample (Cost: 8)",
            CursorTool.RELOCATOR: "Click and drag to move creature (Cost: 12)",
            CursorTool.BARRIER: "Click and drag to create temporary barrier (Cost: 20)",
            CursorTool.PHEROMONE: "Click and drag to create chemical trail (Cost: 7)",
            CursorTool.ASTEROID: "DEVASTATING: Orbital impact (Cost: 100)",
            CursorTool.APEX: "DANGEROUS: Spawn Apex Predator (Cost: 80)"
        }
        return descriptions.get(self.current_tool, "")


class CursorRenderer:
    """Renders the scientific cursor and its effects"""
    
    def __init__(self):
        """Initialize cursor renderer"""
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        self.icons = {}
        self.tool_rects = {} # Map tool enum to screen rect
        
        # Load icons (placeholders for now, will be generated)
        self._load_icons()
        
    def _load_icons(self):
        """Load tool icons."""
        import os
        
        # Base path for assets
        # Assuming running from main directory
        assets_dir = "assets/icons"
        
        icon_map = {
            CursorTool.OBSERVE: "observe.png",
            CursorTool.FOOD_DISPENSER: "dispenser.png",
            CursorTool.STIMULATOR: "stimulator.png",
            CursorTool.MARKER: "marker.png",
            CursorTool.SAMPLER: "sampler.png",
            CursorTool.RELOCATOR: "relocator.png",
            CursorTool.BARRIER: "barrier.png",
            CursorTool.PHEROMONE: "pheromone.png",
            CursorTool.ASTEROID: "asteroid.png",
            CursorTool.APEX: "apex.png"
        }
        
        for tool, filename in icon_map.items():
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                try:
                    image = pygame.image.load(path).convert_alpha()
                    # Scale if needed (assuming 64x64, target 32x32)
                    image = pygame.transform.scale(image, (32, 32))
                    setattr(self, f"icon_{tool.value}", image)
                except Exception as e:
                    print(f"Failed to load icon {filename}: {e}")
        
    def render_cursor(self, screen: pygame.Surface, cursor: ScientificCursor, 
                     mouse_pos: Tuple[int, int]):
        """
        Render the scientific cursor at mouse position.
        
        Args:
            screen: Pygame surface to draw on
            cursor: ScientificCursor instance
            mouse_pos: Mouse position (x, y)
        """
        x, y = mouse_pos
        color = cursor.get_cursor_color()
        size = cursor.get_cursor_size()
        
        # Draw cursor circle
        pygame.draw.circle(screen, color, (x, y), size, 2)
        
        # Draw crosshair for precision
        pygame.draw.line(screen, color, (x - size - 3, y), (x - size // 2, y), 1)
        pygame.draw.line(screen, color, (x + size // 2, y), (x + size + 3, y), 1)
        pygame.draw.line(screen, color, (x, y - size - 3), (x, y - size // 2), 1)
        pygame.draw.line(screen, color, (x, y + size // 2), (x, y + size + 3), 1)
        
    def render_tool_ui(self, screen: pygame.Surface, cursor: ScientificCursor):
        """
        Render tool selection UI.
        
        DEPRECATED: Now handled by UIComponents.render_scientific_toolbar
        """
        pass

    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[CursorTool]:
        """
        Handle mouse click on the tool UI.
        
        Args:
            mouse_pos: Mouse position (x, y)
            
        Returns:
            Selected tool if clicked, None otherwise
        """
        for tool, rect in self.tool_rects.items():
            if rect.collidepoint(mouse_pos):
                return tool
        return None
        
    def render_markers(self, screen: pygame.Surface, cursor: ScientificCursor, 
                      camera):
        """
        Render area markers on the arena.
        
        Args:
            screen: Pygame surface to draw on
            cursor: ScientificCursor instance
            camera: Camera instance for coordinate conversion
        """
        marker_colors = {
            MarkerType.SAFE: (100, 255, 100, 80),
            MarkerType.DANGER: (255, 100, 100, 80),
            MarkerType.FOOD_SOURCE: (255, 255, 100, 80),
            MarkerType.SHELTER: (150, 150, 255, 80)
        }
        
        for marker in cursor.markers:
            color = marker_colors.get(marker.marker_type, (200, 200, 200, 80))
            
            # Convert world position to screen position
            from ..models.spatial import Vector2D
            world_pos = Vector2D(marker.position[0], marker.position[1])
            screen_pos = camera.world_to_screen(world_pos)
            
            # Scale radius
            radius_px = int(marker.radius * camera.zoom * 10.0)
            
            # Draw marker
            surface = pygame.Surface((radius_px * 2, radius_px * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (radius_px, radius_px), radius_px)
            screen.blit(surface, (screen_pos[0] - radius_px, screen_pos[1] - radius_px))
