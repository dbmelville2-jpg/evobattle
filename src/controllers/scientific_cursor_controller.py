"""
Scientific Cursor Controller

Handles event processing, tool usage, and rendering coordination
for the scientific intervention tools.
"""

import time
import pygame
from src.rendering.scientific_cursor import CursorTool
from src.rendering.scientific_cursor import MarkerType


class ScientificCursorController:
    """
    Controller for Scientific Cursor tool system.
    
    Coordinates between the ScientificCursor model, CursorRenderer,
    and the battle system to handle tool selection and usage.
    """
    
    def __init__(self, cursor, cursor_renderer):
        """
        Initialize the controller.
        
        Args:
            cursor: ScientificCursor instance
            cursor_renderer: CursorRenderer instance
        """
        self.cursor = cursor
        self.renderer = cursor_renderer
    
    def handle_event(self, event, battle, camera, get_creature_fn):
        """
        Handle mouse events for tool selection and usage.
        
        Args:
            event: Pygame event
            battle: SpatialBattle instance
            camera: Camera instance for coordinate conversion
            get_creature_fn: Function to get creature at position (mouse_pos, battle, camera)
        
        Returns:
            bool: True if event was handled and should skip further processing
        """
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False
        
        if event.button != 1:  # Only handle left click
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # 1. Check if clicking on toolbar to select tool
        clicked_tool = self.renderer.handle_click(mouse_pos)
        if clicked_tool:
            self.cursor.select_tool(clicked_tool)
            print(f"Selected tool: {clicked_tool.value}")
            return True
        
        # 2. Handle tool usage (if not in OBSERVE mode)
        if self.cursor.current_tool == CursorTool.OBSERVE:
            return False
        
        if not hasattr(battle, 'intervention_system'):
            return False
        
        # Convert screen to world coordinates
        world_pos_vec = camera.screen_to_world(mouse_pos)
        world_pos = (world_pos_vec.x, world_pos_vec.y)
        
        # Check if click is within arena bounds
        if not (0 <= world_pos[0] <= battle.arena.width and 0 <= world_pos[1] <= battle.arena.height):
            return False
        
        # Check if tool has enough charge
        if not self.cursor.can_use_tool():
            print("Not enough charge!")
            return True
        
        # Execute the appropriate tool
        success, message = self._use_tool(world_pos, mouse_pos, battle, camera, get_creature_fn)
        
        if success:
            self.cursor.use_tool_charge()
            print(f"Tool used: {message}")
        else:
            print(f"Tool failed: {message}")
        
        return True
    
    def _use_tool(self, world_pos, mouse_pos, battle, camera, get_creature_fn):
        """
        Execute the currently selected tool.
        
        Args:
            world_pos: World coordinates (x, y)
            mouse_pos: Screen coordinates (x, y)
            battle: SpatialBattle instance
            camera: Camera instance for coordinate conversion
            get_creature_fn: Function to get creature at position
        
        Returns:
            tuple: (success: bool, message: str)
        """
        tool = self.cursor.current_tool
        
        # Map cursor tool to intervention system
        if tool == CursorTool.FOOD_DISPENSER:
            return battle.intervention_system.use_tool("nutrient_drop", world_pos, battle)
        
        elif tool == CursorTool.STIMULATOR:
            return battle.intervention_system.use_tool("neural_shock", world_pos, battle)
        
        elif tool == CursorTool.SAMPLER:
            return battle.intervention_system.use_tool("collect_sample", world_pos, battle)
        
        elif tool == CursorTool.RELOCATOR:
            # Two-step process: Pick up, then Place
            if self.cursor.held_creature:
                # Step 2: Place creature
                success, message = battle.intervention_system.use_tool(
                    "relocate", world_pos, battle, target_id=self.cursor.held_creature
                )
                self.cursor.held_creature = None  # Reset
                return success, message
            else:
                # Step 1: Pick up creature (use camera parameter)
                target = get_creature_fn(mouse_pos, battle, camera)
                if target:
                    self.cursor.held_creature = target.creature.creature_id
                    return True, f"Picked up {target.creature.name}"
                else:
                    return False, "No creature to pick up"
        
        elif tool == CursorTool.ASTEROID:
            return battle.intervention_system.use_tool("asteroid_strike", world_pos, battle)
        
        elif tool == CursorTool.APEX:
            return battle.intervention_system.use_tool("monster_drop", world_pos, battle)
        
        elif tool == CursorTool.BARRIER:
            return battle.intervention_system.create_barrier(world_pos, battle)
        
        elif tool == CursorTool.PHEROMONE:
            return battle.intervention_system.create_pheromone(world_pos, battle)
        
        elif tool == CursorTool.MARKER:
            # Visual marker (default to SAFE area)
            if hasattr(battle, 'creatures'):
                self.cursor.add_marker(world_pos, MarkerType.SAFE, current_time=time.time())
                return True, "Marker placed (Visual only for now)"
            else:
                return False, "Cannot place marker"
        
        return False, f"Unknown tool: {tool}"
    
    def update(self, dt, current_time):
        """
        Update cursor state (charge regeneration, etc.).
        
        Args:
            dt: Delta time in seconds
            current_time: Current game time
        """
        self.cursor.update(dt, current_time)
    
    def render_markers(self, screen, camera):
        """
        Render cursor markers on the screen.
        
        Args:
            screen: Pygame screen surface
            camera: Camera instance for coordinate conversion
        """
        self.renderer.render_markers(screen, self.cursor, camera)
    
    def render_cursor(self, screen, mouse_pos):
        """
        Render cursor at mouse position.
        
        Args:
            screen: Pygame screen surface
            mouse_pos: Mouse position (x, y)
        """
        self.renderer.render_cursor(screen, self.cursor, mouse_pos)
