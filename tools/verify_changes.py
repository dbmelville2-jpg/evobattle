
import sys
import os
import pygame
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.getcwd())

# Mock Pygame init
pygame.init()
pygame.font.init()
screen = pygame.Surface((1200, 800))

# Import modules
try:
    from src.rendering.ui_components import UIComponents
    from src.rendering.event_animator import EventAnimator
    from src.rendering.arena_renderer import ArenaRenderer
    from src.systems.scientific_intervention import ScientificIntervention
    from src.systems.battle_spatial import BattleEvent, BattleEventType
    from src.models.spatial import Vector2D
    print("Imports successful.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# Mock Battle
class MockCreature:
    def __init__(self, x, y):
        self.spatial = MagicMock()
        self.spatial.position.x = x
        self.spatial.position.y = y
        self.creature = MagicMock()
        self.creature.name = "TestCreature"
        self.creature.stats.hp = 100
        self.creature.stats.max_hp = 100
    
    def is_alive(self):
        return True

class MockBattle:
    def __init__(self):
        self.creatures = [MockCreature(100, 100), MockCreature(110, 110)]
        self.events = []
        self.arena = MagicMock()
        self.arena.width = 1000
        self.arena.height = 800
        self.arena.pellets = []
        self.resource_spawn_rate = 1.0
        self.breeding_cooldown = 10.0
        self.overseer = None
        self.is_over = False
        self.pending_dilemma = None
        self.assistant_manager = None
        self.ethics_system = MagicMock()
        self.environment = None
        
    def add_event(self, event):
        self.events.append(event)
        print(f"Event added: {event.event_type} - {event.message}")

battle = MockBattle()

# Test EventAnimator
print("\nTesting EventAnimator...")
animator = EventAnimator()
animator.create_explosion((100, 100))
animator.create_blood_splatter((100, 100))
print(f"Particles active: {len(animator.particles)}")
assert len(animator.particles) > 0, "Particles should be created"

# Test ScientificIntervention
print("\nTesting ScientificIntervention...")
intervention = ScientificIntervention(ethics_system=battle.ethics_system)

# Test Asteroid Strike
print("Testing Asteroid Strike...")
success, msg = intervention.use_tool("asteroid_strike", (100, 100), battle)
print(f"Result: {success}, {msg}")
assert success, "Asteroid strike should succeed"
assert len(battle.events) > 0, "Asteroid strike should trigger events"

# Test Monster Drop
print("Testing Monster Drop...")
success, msg = intervention.use_tool("monster_drop", (200, 200), battle)
print(f"Result: {success}, {msg}")
assert success, "Monster drop should succeed"

# Test UIComponents
print("\nTesting UIComponents...")
# Correctly instantiate without screen argument
ui = UIComponents()
# Just call render to see if it crashes
try:
    ui.render(screen, battle)
    print("UI Render successful")
except Exception as e:
    print(f"UI Render failed: {e}")

# Test ArenaRenderer screen_to_world
print("\nTesting ArenaRenderer...")
renderer = ArenaRenderer()
# Mock get_arena_bounds since we don't have a full window
renderer._get_arena_bounds = MagicMock(return_value=(100, 100, 800, 600))
screen_pos = (500, 400) # Center of the mock arena rect (100+400, 100+300)
world_pos = renderer.screen_to_world(screen_pos, screen, battle.arena)
print(f"Screen {screen_pos} -> World {world_pos}")
# Expected: Center of arena (1000x800) -> (500, 400)
assert abs(world_pos.x - 500) < 1.0 and abs(world_pos.y - 400) < 1.0, "screen_to_world calculation incorrect"
print("screen_to_world verification successful")

print("\nVerification Complete.")
