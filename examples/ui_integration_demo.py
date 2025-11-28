import pygame
import sys
import os
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import GameWindow, ArenaRenderer, UIComponents, create_creature
from src.systems.battle_spatial import SpatialBattle
from src.systems.ethical_dilemmas import EthicalDilemma, DilemmaChoice, DilemmaCategory

def create_test_dilemma():
    return EthicalDilemma(
        id="demo_dilemma",
        category=DilemmaCategory.POPULATION_MANAGEMENT,
        title="Resource Scarcity",
        description="The local food supply is dwindling. Do you intervene to save the starving population, or let natural selection take its course?",
        choices=[
            DilemmaChoice(
                text="Provide Emergency Food",
                welfare_impact=10,
                ecosystem_impact=-5,
                integrity_impact=-5,
                intervention_impact=10,
                outcome_description="Increases resource spawn rate."
            ),
            DilemmaChoice(
                text="Observe Natural Selection",
                welfare_impact=-10,
                ecosystem_impact=5,
                integrity_impact=10,
                intervention_impact=-5,
                outcome_description="Increases mutation rate."
            ),
            DilemmaChoice(
                text="Relocate Vulnerable Creatures",
                welfare_impact=5,
                ecosystem_impact=-2,
                integrity_impact=-2,
                intervention_impact=15,
                outcome_description="Triggers migration event."
            )
        ],
        trigger_condition="manual_trigger"
    )

def main():
    pygame.init()
    window = GameWindow(1280, 800)
    pygame.display.set_caption("EvoBattle - UI Integration Demo")
    
    # Create creatures first
    creatures = []
    for i in range(5):
        creature = create_creature(f"Creature_{i}", level=5)
        creatures.append(creature)

    # Initialize Battle
    battle = SpatialBattle(creatures_or_team1=creatures, arena_width=160.0, arena_height=100.0)
        
    # Initialize Renderer and UI
    arena_renderer = ArenaRenderer()
    ui_components = UIComponents()
    
    # Setup Demo State
    print("=== UI Integration Demo ===")
    print("Controls:")
    print("E: Toggle Ethics Dashboard")
    print("D: Trigger Test Dilemma")
    print("A: Toggle Assistant Panel")
    print("Click Scientific Toolbar to select tools")
    print("Click in Arena to use tools")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Demo Controls & Keyboard Shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Pause logic not fully implemented in demo, but good to have placeholder
                    pass
                elif event.key == pygame.K_d:
                    battle.pending_dilemma = create_test_dilemma()
                    print("Triggered Dilemma!")
                elif event.key == pygame.K_e:
                    ui_components.show_ethics_dashboard = not ui_components.show_ethics_dashboard
                elif event.key == pygame.K_a:
                    ui_components.show_advisor_panel = not ui_components.show_advisor_panel
                
                # Dilemma Keyboard Choices
                if hasattr(battle, 'pending_dilemma') and battle.pending_dilemma:
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        index = event.key - pygame.K_1
                        if 0 <= index < len(battle.pending_dilemma.choices):
                            choice = battle.pending_dilemma.choices[index]
                            print(f"Chose option {index+1} via keyboard")
                            battle.pending_dilemma = None

            # Mouse Interactions
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 1. Dilemma Handling (Highest Priority)
                if hasattr(battle, 'pending_dilemma') and battle.pending_dilemma:
                    # Check choices
                    for i, rect in ui_components.dilemma_choice_rects.items():
                        if rect.collidepoint(mouse_pos):
                            print(f"Chose option {i+1} via click")
                            battle.pending_dilemma = None # Clear dilemma
                            break
                    
                    # Check Advisor Button
                    if ui_components.ask_advisor_rect and ui_components.ask_advisor_rect.collidepoint(mouse_pos):
                        ui_components.show_advisor_panel = not ui_components.show_advisor_panel
                    
                    # Don't process other clicks if dilemma is up
                    if not ui_components.show_advisor_panel:
                        continue

                # 2. Advisor Panel Handling
                if ui_components.show_advisor_panel:
                    if ui_components.advisor_close_rect and ui_components.advisor_close_rect.collidepoint(mouse_pos):
                        ui_components.show_advisor_panel = False
                    continue # Skip other clicks

                # 3. Scientific Toolbar
                tool_clicked = False
                for tool_id, rect in ui_components.tool_rects.items():
                    if rect.collidepoint(mouse_pos):
                        if ui_components.selected_tool == tool_id:
                            ui_components.selected_tool = None 
                        else:
                            ui_components.selected_tool = tool_id
                        tool_clicked = True
                        print(f"Selected tool: {ui_components.selected_tool}")
                        break
                
                if tool_clicked:
                    continue

                # 4. Tool Usage in Arena
                if event.button == 1:
                    if ui_components.selected_tool and hasattr(battle, 'scientific_intervention'):
                        bounds = arena_renderer._get_arena_bounds(window.screen)
                        ax, ay, aw, ah = bounds
                        mx, my = mouse_pos
                        
                        if ax <= mx <= ax + aw and ay <= my <= ay + ah:
                            world_x = (mx - ax) / aw * battle.arena.width
                            world_y = (my - ay) / ah * battle.arena.height
                            print(f"Used {ui_components.selected_tool} at ({world_x:.1f}, {world_y:.1f})")
                        continue
            
            ui_components.handle_event(event, battle)
            
        # Update
        if not (hasattr(battle, 'pending_dilemma') and battle.pending_dilemma):
            battle.update(dt)
            
        # Render
        window.screen.fill((20, 20, 30))
        arena_renderer.render(window.screen, battle)
        ui_components.render(window.screen, battle)
        
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main()
