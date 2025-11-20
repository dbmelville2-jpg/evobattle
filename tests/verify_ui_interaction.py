
import pygame
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rendering.ui_components import UIComponents
from src.systems.battle_spatial import SpatialBattle
# from src.models.evolution import Creature, Genome # Not needed for mocks

# Mock objects
class MockCreature:
    def __init__(self, strain_id):
        self.creature = type('obj', (object,), {
            'strain_id': strain_id,
            'hue': 0.5,
            'speed': 10,
            'size': 10,
            'sense_radius': 50,
            'generation': 1,
            'traits': []
        })
    
    def is_alive(self):
        return True

class MockBattle:
    def __init__(self):
        self.creatures = []
        self.environment = type('obj', (object,), {
            'weather': None,
            'day_night': None,
            'biome_name': 'Test Biome',
            'biome_description': 'Test',
            'biome_difficulty': 1,
            'biome_regions': []
        })
        self.arena = type('obj', (object,), {'pellets': []})
        self.events = []
        self.is_over = False
        self.current_time = 0
        self.resource_spawn_rate = 1.0
        self.breeding_cooldown = 5.0
        self.breeding_system = type('obj', (object,), {'mutation_rate': 0.1})

def test_ui():
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    
    ui = UIComponents()
    battle = MockBattle()
    
    # Add many strains
    for i in range(20):
        strain_id = f"strain_{i}"
        for _ in range(5):
            battle.creatures.append(MockCreature(strain_id))
            
    # Render loop simulation
    ui.render(screen, battle)
    
    # Test Scroll
    scroll_event = pygame.event.Event(pygame.MOUSEWHEEL, {'y': -1}) # Scroll down
    # Need to set mouse pos to be over the panel
    # We can't easily mock mouse pos for pygame.mouse.get_pos() without display interaction
    # But we can check if the method runs without error
    
    try:
        ui.handle_event(scroll_event, battle)
        print("Scroll event handled (no crash)")
    except Exception as e:
        print(f"Scroll event failed: {e}")
        
    # Test Click
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (30, 350), 'button': 1})
    try:
        ui.handle_event(click_event, battle)
        print("Click event handled (no crash)")
    except Exception as e:
        print(f"Click event failed: {e}")

    print("UI Verification Complete")
    pygame.quit()

if __name__ == "__main__":
    test_ui()
