"""
Spatial Real-Time Battle Example - Watch creatures fight in 2D space!

Demonstrates the spatial battle system where creatures move around
a 2D arena and fight based on proximity and their traits.
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.models.trait import Trait
from src.systems.battle import SpatialBattle, BattleEventType


def visualize_arena(battle: SpatialBattle, width: int = 60, height: int = 20):
    """Create ASCII visualization of the battle arena."""
    # Create empty arena
    arena = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Add borders
    for x in range(width):
        arena[0][x] = '─'
        arena[height-1][x] = '─'
    for y in range(height):
        arena[y][0] = '│'
        arena[y][width-1] = '│'
    arena[0][0] = '┌'
    arena[0][width-1] = '┐'
    arena[height-1][0] = '└'
    arena[height-1][width-1] = '┘'
    
    # Scale factor
    scale_x = (width - 2) / battle.arena.width
    scale_y = (height - 2) / battle.arena.height
    
    # Add creatures
    for creature in battle.player_creatures:
        if creature.is_alive():
            x = int(creature.spatial.position.x * scale_x) + 1
            y = int(creature.spatial.position.y * scale_y) + 1
            if 0 <= y < height and 0 <= x < width:
                arena[y][x] = '🔵' if len('🔵') == 1 else 'P'
    
    for creature in battle.enemy_creatures:
        if creature.is_alive():
            x = int(creature.spatial.position.x * scale_x) + 1
            y = int(creature.spatial.position.y * scale_y) + 1
            if 0 <= y < height and 0 <= x < width:
                arena[y][x] = '🔴' if len('🔴') == 1 else 'E'
    
    # Convert to string
    return '\n'.join(''.join(row) for row in arena)


def print_battle_state(battle: SpatialBattle):
    """Print current battle state."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=" * 70)
    print("  🎮 SPATIAL REAL-TIME BATTLE 🎮".center(70))
    print("=" * 70)
    print()
    
    # Arena visualization
    print(visualize_arena(battle))
    print()
    
    # Stats
    print("-" * 70)
    print(f"Time: {battle.current_time:.1f}s")
    print()
    
    # Player team
    print("🔵 PLAYER TEAM:")
    for creature in battle.player_creatures:
        if creature.is_alive():
            pos = creature.spatial.position
            hp_percent = creature.creature.stats.hp / creature.creature.stats.max_hp
            hp_bar = '█' * int(20 * hp_percent) + '░' * (20 - int(20 * hp_percent))
            print(f"  {creature.creature.name:12s} HP:[{hp_bar}] {creature.creature.stats.hp:3d}/{creature.creature.stats.max_hp:3d}  Pos:({pos.x:5.1f},{pos.y:5.1f})")
    
    print()
    print("🔴 ENEMY TEAM:")
    for creature in battle.enemy_creatures:
        if creature.is_alive():
            pos = creature.spatial.position
            hp_percent = creature.creature.stats.hp / creature.creature.stats.max_hp
            hp_bar = '█' * int(20 * hp_percent) + '░' * (20 - int(20 * hp_percent))
            print(f"  {creature.creature.name:12s} HP:[{hp_bar}] {creature.creature.stats.hp:3d}/{creature.creature.stats.max_hp:3d}  Pos:({pos.x:5.1f},{pos.y:5.1f})")
    
    print("-" * 70)


def spatial_battle_demo():
    """Run a spatial real-time battle demonstration."""
    
    # Create fire dragon with aggressive trait
    dragon_type = CreatureType(
        name="Fire Dragon",
        base_stats=Stats(max_hp=120, attack=18, defense=12, speed=14),
        stat_growth=StatGrowth(),
        type_tags=["fire"]
    )
    
    dragon = Creature(name="Blaze", creature_type=dragon_type, level=10)
    dragon.add_ability(create_ability('fireball'))
    dragon.add_trait(Trait(name="Aggressive", strength_modifier=1.2))
    
    # Create water serpent with cautious trait
    serpent_type = CreatureType(
        name="Water Serpent",
        base_stats=Stats(max_hp=100, attack=16, defense=14, speed=18),
        stat_growth=StatGrowth(),
        type_tags=["water"]
    )
    
    serpent = Creature(name="Aqua", creature_type=serpent_type, level=10)
    serpent.add_ability(create_ability('tackle'))
    serpent.add_trait(Trait(name="Cautious", speed_modifier=1.1))
    
    # Create battle
    battle = SpatialBattle([dragon], [serpent], arena_width=100, arena_height=60, random_seed=42)
    
    # Event handler
    last_event = ""
    
    def on_event(event):
        nonlocal last_event
        if event.event_type in [BattleEventType.DAMAGE_DEALT, BattleEventType.ABILITY_USE]:
            last_event = event.message
    
    battle.add_event_callback(on_event)
    
    # Welcome
    print("=" * 70)
    print("  🎮 SPATIAL REAL-TIME BATTLE DEMO 🎮".center(70))
    print("=" * 70)
    print()
    print("Watch creatures move and fight in real-time 2D combat!")
    print()
    print(f"🔵 {dragon.name} (Fire, Aggressive) vs 🔴 {serpent.name} (Water, Cautious)")
    print()
    input("Press Enter to start...")
    
    # Run battle with visualization
    time_step = 0.1
    update_interval = 0.5  # Update display every 0.5 seconds
    last_display = 0
    
    while not battle.is_over and battle.current_time < 30.0:
        battle.update(time_step)
        
        # Update display periodically
        if battle.current_time - last_display >= update_interval:
            print_battle_state(battle)
            if last_event:
                print(f"\n📢 {last_event}")
            time.sleep(update_interval)
            last_display = battle.current_time
    
    # Final state
    print_battle_state(battle)
    
    winner = "Player" if any(c.is_alive() for c in battle.player_creatures) else "Enemy"
    print()
    print("=" * 70)
    print(f"  🏆 {winner} WINS! 🏆".center(70))
    print("=" * 70)


def quick_spatial_battle():
    """Quick demonstration of spatial combat."""
    print("=" * 70)
    print("QUICK SPATIAL BATTLE".center(70))
    print("=" * 70)
    print()
    
    # Create creatures
    warrior_type = CreatureType(
        name="Warrior",
        base_stats=Stats(max_hp=100, attack=15, defense=12, speed=10),
        type_tags=["fighter"]
    )
    
    warrior = Creature(name="Ares", creature_type=warrior_type, level=5)
    warrior.add_ability(create_ability('tackle'))
    warrior.add_trait(Trait(name="Reckless"))
    
    mage = Creature(name="Mystic", creature_type=warrior_type, level=5)
    mage.add_ability(create_ability('fireball'))
    mage.add_trait(Trait(name="Defensive"))
    
    # Create battle
    battle = SpatialBattle([warrior], [mage], arena_width=50, arena_height=30)
    
    # Event handler
    def on_event(event):
        if event.event_type == BattleEventType.DAMAGE_DEALT:
            print(f"  💥 {event.target.creature.name} took {event.value} damage!")
        elif event.event_type == BattleEventType.CREATURE_FAINT:
            print(f"  💀 {event.target.creature.name} fainted!")
    
    battle.add_event_callback(on_event)
    
    print(f"⚔️  {warrior.name} (Reckless) vs {mage.name} (Defensive)")
    print(f"    Arena: {battle.arena.width}x{battle.arena.height}")
    print()
    
    # Simulate
    winner = battle.simulate(duration=20.0, time_step=0.1)
    
    print(f"\n🏆 {winner.upper()} wins!")
    print(f"    Battle duration: {battle.current_time:.1f} seconds")
    print(f"    Total events: {len(battle.events)}")


if __name__ == "__main__":
    print("\nSpatial Real-Time Battle System")
    print("=" * 70)
    print()
    print("Choose a demo:")
    print("1. Full Spatial Battle (with visualization)")
    print("2. Quick Battle")
    print()
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == "1":
        spatial_battle_demo()
    elif choice == "2":
        quick_spatial_battle()
    else:
        print("Invalid choice. Running full demo...")
        spatial_battle_demo()
