import sys
import pygame
import random
import os

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.rendering.game_window import GameWindow
from src.rendering.arena_renderer import ArenaRenderer
from src.rendering.creature_renderer import CreatureRenderer
from src.rendering.ui_components import UIComponents
from src.rendering.event_animator import EventAnimator
from src.systems.battle_spatial import SpatialBattle
from src.models.creature import Creature
from src.systems.biome_generator import BiomeType

def main():
    # Initialize window
    window = GameWindow(title="Biome Graphics Test")
    
    # Create renderers
    arena_renderer = ArenaRenderer(show_grid=True)
    creature_renderer = CreatureRenderer()
    ui_components = UIComponents(window.width, window.height)
    event_animator = EventAnimator()
    
    # Create dummy creatures
    creatures = [Creature(name=f"Creature {i}") for i in range(5)]
    
    # Create battle with a specific biome (e.g., FOREST)
    print("Initializing battle with FOREST biome...")
    battle = SpatialBattle(
        creatures_or_team1=creatures,
        biome_type='forest',
        arena_width=100,
        arena_height=100
    )
    
    # Run game loop
    print("Starting game loop. Press ESC to quit.")
    window.run(
        battle,
        arena_renderer,
        creature_renderer,
        ui_components,
        event_animator
    )
    
    window.quit()

if __name__ == "__main__":
    main()
