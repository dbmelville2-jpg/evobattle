"""
Quick example to demonstrate biome visualization.

Run this to see the biome info panel in action!
"""
import sys
sys.path.insert(0, 'src')

import pygame
from models.creature import Creature
from models.stats import Stats
from models.trait import Trait
from systems.battle_spatial import SpatialBattle
from rendering.ui_components import UIComponents
from rendering.creature_renderer import CreatureRenderer

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((1600, 1000))
pygame.display.set_caption("Biome Visualization Demo")
clock = pygame.time.Clock()

# Create some test creatures
creatures = []
for i in range(6):
    creature = Creature(
        name=f"Creature{i+1}",
        stats=Stats(max_hp=100, hp=100, attack=15, defense=10, speed=20),
        traits=[Trait(name="Forager", description="Seeks food", trait_type="behavioral")]
    )
    creatures.append(creature)

# Create battles with different biomes
biomes = ['grassland', 'desert', 'forest', 'marsh', 'rocky_highlands', 'mixed']
current_biome_idx = 0

def create_battle_with_biome(biome_type):
    return SpatialBattle(
        creatures_or_team1=creatures,
        arena_width=100,
        arena_height=100,
        biome_type=biome_type,
        initial_resources=15
    )

battle = create_battle_with_biome(biomes[current_biome_idx])

# Create renderers
ui = UIComponents()
creature_renderer = CreatureRenderer()

# Main loop
running = True
paused = False
font = pygame.font.Font(None, 36)

print("=" * 60)
print("BIOME VISUALIZATION DEMO")
print("=" * 60)
print("\nControls:")
print("  SPACE - Pause/Resume")
print("  B - Switch to next biome")
print("  ESC - Quit")
print("\nCurrent biome:", biomes[current_biome_idx])
print("=" * 60)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_b:
                # Switch to next biome
                current_biome_idx = (current_biome_idx + 1) % len(biomes)
                battle = create_battle_with_biome(biomes[current_biome_idx])
                print(f"\nSwitched to biome: {biomes[current_biome_idx]}")
                if battle.environment:
                    print(f"  Name: {battle.environment.biome_name}")
                    print(f"  Difficulty: {battle.environment.biome_difficulty}/5")
                    print(f"  Description: {battle.environment.biome_description}")
    
    # Update battle
    if not paused and not battle.is_over:
        battle.update(1/60)
    
    # Render
    screen.fill((20, 25, 30))
    
    # Render arena background
    arena_rect = pygame.Rect(250, 100, 1100, 700)
    pygame.draw.rect(screen, (30, 35, 40), arena_rect)
    
    # Render creatures
    creature_renderer.render(screen, battle, arena_rect)
    
    # Render UI (includes biome panel!)
    ui.render(screen, battle, paused)
    
    # Instructions
    instructions = [
        "Press B to switch biomes",
        "Press SPACE to pause",
        f"Current: {biomes[current_biome_idx]}"
    ]
    y = screen.get_height() - 220
    for instruction in instructions:
        text_surf = font.render(instruction, True, (200, 200, 255))
        screen.blit(text_surf, (screen.get_width() // 2 - text_surf.get_width() // 2, y))
        y += 40
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\nDemo complete!")
