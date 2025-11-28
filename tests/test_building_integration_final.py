
import sys
import os
import pygame
import random
from src.systems.battle_spatial import SpatialBattle
from src.models.creature import Creature
from src.models.pellet import Pellet, PelletTraits
from src.models.building_material import MaterialType
from src.models.structure import StructureType
from src.models.spatial import Vector2D

# Setup
pygame.init()
pygame.display.set_mode((800, 600))

# Add a creature
print("Creating creature...")
creature = Creature()
creature.name = "Builder Bob"
# Give traits to help building
from src.models.ecosystem_traits import Trait
builder_trait = Trait(name="Architect", description="Builds faster", trait_type="behavioral")
builder_trait.interaction_effects = {'build_speed_multiplier': 2.0}
creature.traits.append(builder_trait)

print("Initializing SpatialBattle...")
battle = SpatialBattle(creatures_or_team1=[creature], arena_width=800, arena_height=600)
battle_creature = battle._creatures[0]

# Add a pellet that drops materials
print("Adding pellet...")
pellet = Pellet(x=400, y=305)
pellet.traits.nutritional_value = 50
pellet.traits.size = 1.5 # Large pellet
battle.arena.add_pellet(pellet)

print("Simulating updates...")
# Simulate enough frames for:
# 1. Creature to eat pellet (needs hunger)
battle_creature.creature.hunger = 10 # Starving (low hunger = hungry)
battle_creature.creature.max_hunger = 100

# Position creature right next to pellet
battle_creature.spatial.position.x = 400
battle_creature.spatial.position.y = 300

print(f"Creature position: ({battle_creature.spatial.position.x}, {battle_creature.spatial.position.y})")
print(f"Pellet position: (400, 305)")
print(f"Creature hunger: {battle_creature.creature.hunger}/{battle_creature.creature.max_hunger}")

# Run loop
materials_dropped = False
structure_started = False
structure_completed = False

for i in range(500):
    battle.update(0.1)
    
    # Check if pellet was eaten
    if i == 0:
        initial_pellet_count = len(battle.arena.resources)
        print(f"Initial pellets: {initial_pellet_count}")
    
    if i % 50 == 0:
        current_pellet_count = len(battle.arena.resources)
        print(f"Frame {i}: Pellets: {current_pellet_count}, Materials: {len(battle.materials)}, Hunger: {battle_creature.creature.hunger}")
    
    # Check materials
    if not materials_dropped and battle.materials:
        print(f"Frame {i}: Materials dropped! Count: {len(battle.materials)}")
        materials_dropped = True
        # Force start building task if not started (AI might be slow)
        if not battle.building_system.get_active_task(creature.creature_id):
            print("Forcing start of building task...")
            # Find material
            mat = battle.materials[0]
            # Start task
            battle.building_system.start_building_task(
                creature.creature_id,
                StructureType.SHELTER,
                Vector2D(450, 300)
            )
    
    # Check task
    task = battle.building_system.get_active_task(creature.creature_id)
    if task and not structure_started:
        print(f"Frame {i}: Building task active: {task.structure_type.name}")
        structure_started = True
        
    # Check structure completion
    if battle.structures and not structure_completed:
        print(f"Frame {i}: Structure completed! Type: {battle.structures[0].structure_type.name}")
        structure_completed = True
        break

if structure_completed:
    print("SUCCESS: Building cycle complete!")
else:
    print("FAILURE: Building cycle incomplete.")
    if not materials_dropped:
        print("- Materials never dropped.")
    elif not structure_started:
        print("- Task never started.")
    elif not structure_completed:
        print("- Structure never completed.")

pygame.quit()
