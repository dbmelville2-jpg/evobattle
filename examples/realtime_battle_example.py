"""
Real-Time Battle Example - Watch turn-based battles in real-time!

This example demonstrates the turn-based battle system with visual feedback
and animated battles that you can watch unfold step by step.

Note: This uses the turn-based battle system for demonstration.
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.models.trait import Trait
from src.systems.battle_turnbased_backup import Battle, BattleEvent, BattleEventType


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_health_bar(creature: Creature, width: int = 30):
    """Print a visual health bar for a creature."""
    hp_percent = creature.stats.hp / creature.stats.max_hp
    filled = int(width * hp_percent)
    empty = width - filled
    
    # Color codes
    if hp_percent > 0.6:
        color = '\033[92m'  # Green
    elif hp_percent > 0.3:
        color = '\033[93m'  # Yellow
    else:
        color = '\033[91m'  # Red
    
    reset = '\033[0m'
    
    bar = f"{color}{'█' * filled}{reset}{'░' * empty}"
    hp_text = f"{creature.stats.hp}/{creature.stats.max_hp}"
    
    return f"{bar} {hp_text}"


def display_battle_state(battle: Battle, last_event: str = ""):
    """Display the current battle state visually."""
    clear_screen()
    
    player = battle.state.get_active_player()
    enemy = battle.state.get_active_enemy()
    
    print("=" * 70)
    print("⚔️  EVOBATTLE - REAL-TIME COMBAT ARENA  ⚔️".center(70))
    print("=" * 70)
    print()
    
    # Player side
    if player:
        print(f"🔵 {player.name} (Lv.{player.level})".ljust(35))
        print(f"   Type: {', '.join(player.creature_type.type_tags)}")
        print(f"   HP: {print_health_bar(player)}")
        print(f"   ATK: {player.stats.attack} | DEF: {player.stats.defense} | SPD: {player.stats.speed}")
    
    print()
    print(" " * 30 + "VS")
    print()
    
    # Enemy side
    if enemy:
        print(f"🔴 {enemy.name} (Lv.{enemy.level})".ljust(35))
        print(f"   Type: {', '.join(enemy.creature_type.type_tags)}")
        print(f"   HP: {print_health_bar(enemy)}")
        print(f"   ATK: {enemy.stats.attack} | DEF: {enemy.stats.defense} | SPD: {enemy.stats.speed}")
    
    print()
    print("-" * 70)
    
    # Last event
    if last_event:
        print(f"📢 {last_event}")
    
    print("-" * 70)
    print(f"Turn: {battle.state.current_turn} | Phase: {battle.state.phase.value}")
    print()


def animate_event(event: BattleEvent):
    """Animate a battle event with visual effects."""
    
    # Event-specific animations
    if event.event_type == BattleEventType.ABILITY_USE:
        print(f"\n💥 {event.message}")
        time.sleep(0.8)
        
    elif event.event_type == BattleEventType.DAMAGE_DEALT:
        print(f"\n💢 {event.message}")
        # Visual damage effect
        print("   " + "💥 " * min(5, event.value // 10))
        time.sleep(1.0)
        
    elif event.event_type == BattleEventType.CRITICAL_HIT:
        print(f"\n⚡ {event.message} ⚡")
        time.sleep(0.6)
        
    elif event.event_type == BattleEventType.SUPER_EFFECTIVE:
        print(f"\n🔥 {event.message}")
        time.sleep(0.6)
        
    elif event.event_type == BattleEventType.NOT_EFFECTIVE:
        print(f"\n🛡️  {event.message}")
        time.sleep(0.6)
        
    elif event.event_type == BattleEventType.MISS:
        print(f"\n💨 {event.message}")
        time.sleep(0.8)
        
    elif event.event_type == BattleEventType.HEALING:
        print(f"\n💚 {event.message}")
        time.sleep(0.8)
        
    elif event.event_type == BattleEventType.CREATURE_FAINT:
        print(f"\n💀 {event.message}")
        time.sleep(1.5)
        
    elif event.event_type == BattleEventType.TURN_START:
        print(f"\n🔔 Turn {event.data.get('turn_number', '?')} begins!")
        time.sleep(0.5)


def real_time_battle_example():
    """Run a real-time battle that you can watch!"""
    
    # Create fire dragon
    dragon_type = CreatureType(
        name="Fire Dragon",
        description="A powerful dragon that breathes fire",
        base_stats=Stats(max_hp=120, attack=18, defense=12, speed=14),
        stat_growth=StatGrowth(hp_growth=12.0, attack_growth=2.5),
        type_tags=["fire", "flying"],
        evolution_stage=2
    )
    
    dragon = Creature(
        name="Blaze",
        creature_type=dragon_type,
        level=10
    )
    dragon.add_ability(create_ability('tackle'))
    dragon.add_ability(create_ability('fireball'))
    
    # Create water serpent
    serpent_type = CreatureType(
        name="Water Serpent",
        description="A swift serpent that controls water",
        base_stats=Stats(max_hp=100, attack=16, defense=14, speed=18),
        stat_growth=StatGrowth(hp_growth=10.0, attack_growth=2.0, speed_growth=2.5),
        type_tags=["water"],
        evolution_stage=2
    )
    
    serpent = Creature(
        name="Aqua",
        creature_type=serpent_type,
        level=10
    )
    serpent.add_ability(create_ability('tackle'))
    serpent.add_ability(create_ability('quick_strike'))
    
    # Create battle
    battle = Battle([dragon], [serpent], random_seed=42)
    
    # Event handler for real-time updates
    last_event_message = ""
    
    def on_battle_event(event: BattleEvent):
        nonlocal last_event_message
        last_event_message = event.message
        
        # Display updated state
        display_battle_state(battle, last_event_message)
        
        # Animate the event
        animate_event(event)
    
    # Register event callback
    battle.add_event_callback(on_battle_event)
    
    # Welcome screen
    clear_screen()
    print("=" * 70)
    print("⚔️  EVOBATTLE - REAL-TIME COMBAT ARENA  ⚔️".center(70))
    print("=" * 70)
    print()
    print("Get ready to watch an epic battle!")
    print()
    print(f"🔵 {dragon.name} (Fire Dragon) vs 🔴 {serpent.name} (Water Serpent)")
    print()
    input("Press Enter to start the battle...")
    
    # Start battle
    battle.start_battle()
    
    # Execute battle turn by turn
    while not battle.state.is_battle_over():
        # Small pause between turns
        time.sleep(1.0)
        
        # Execute one turn
        battle.execute_turn()
    
    # Show final result
    winner_side = battle.state.get_winner()
    if winner_side == 'player':
        winner = dragon
        winner_emoji = "🔵"
    else:
        winner = serpent
        winner_emoji = "🔴"
    
    print("\n" + "=" * 70)
    print(f"{winner_emoji} VICTORY! {winner.name} WINS! {winner_emoji}".center(70))
    print("=" * 70)
    print(f"\nRemaining HP: {winner.stats.hp}/{winner.stats.max_hp}")
    print(f"Total Turns: {battle.state.current_turn}")
    print()


def quick_battle_example():
    """Run a faster-paced battle demonstration."""
    
    print("=" * 70)
    print("QUICK BATTLE MODE".center(70))
    print("=" * 70)
    print()
    
    # Create simple creatures
    warrior_type = CreatureType(
        name="Warrior",
        base_stats=Stats(max_hp=100, attack=15, defense=12, speed=10),
        type_tags=["fighter"]
    )
    
    mage_type = CreatureType(
        name="Mage",
        base_stats=Stats(max_hp=80, attack=20, defense=8, speed=15),
        type_tags=["psychic"]
    )
    
    warrior = Creature(name="Ares", creature_type=warrior_type, level=5)
    warrior.add_ability(create_ability('tackle'))
    warrior.add_ability(create_ability('power_up'))
    
    mage = Creature(name="Mystic", creature_type=mage_type, level=5)
    mage.add_ability(create_ability('fireball'))
    
    battle = Battle([warrior], [mage])
    
    # Simple event handler
    def on_event(event: BattleEvent):
        # Only show key events
        if event.event_type in [
            BattleEventType.ABILITY_USE,
            BattleEventType.DAMAGE_DEALT,
            BattleEventType.CRITICAL_HIT,
            BattleEventType.CREATURE_FAINT
        ]:
            print(f"  {event.message}")
            time.sleep(0.3)
    
    battle.add_event_callback(on_event)
    
    print(f"⚔️  {warrior.name} vs {mage.name}\n")
    
    # Run battle with step-by-step execution
    battle.start_battle()
    
    turn = 0
    while not battle.state.is_battle_over():
        turn += 1
        print(f"\n--- Turn {turn} ---")
        battle.execute_turn()
        time.sleep(0.5)
    
    winner_side = battle.state.get_winner()
    winner = warrior if winner_side == 'player' else mage
    
    print(f"\n🏆 {winner.name} wins!")
    print()


def event_log_example():
    """Show all events that occurred during a battle."""
    
    print("=" * 70)
    print("EVENT LOG EXAMPLE".center(70))
    print("=" * 70)
    print()
    
    # Create creatures
    creature1_type = CreatureType(
        name="Type A",
        base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12),
        type_tags=["normal"]
    )
    
    creature1 = Creature(name="Alpha", creature_type=creature1_type, level=5)
    creature1.add_ability(create_ability('tackle'))
    
    creature2 = Creature(name="Beta", creature_type=creature1_type, level=5)
    creature2.add_ability(create_ability('tackle'))
    
    battle = Battle([creature1], [creature2], random_seed=123)
    
    # Run battle (instant)
    winner = battle.simulate()
    
    print(f"Battle complete! Winner: {winner.name}\n")
    print("Event Timeline:")
    print("-" * 70)
    
    # Display all events
    for i, event in enumerate(battle.state.events, 1):
        timestamp = f"[Event {i:2d}]"
        event_type = event.event_type.value.replace('_', ' ').title()
        
        print(f"{timestamp} {event_type:20s} - {event.message}")
    
    print("-" * 70)
    print(f"\nTotal Events: {len(battle.state.events)}")
    print()


if __name__ == "__main__":
    print("\nEVOBATTLE - Real-Time Combat System")
    print("=" * 70)
    print()
    print("Choose a demo:")
    print("1. Full Real-Time Battle (with animations)")
    print("2. Quick Battle Mode")
    print("3. Event Log Example")
    print("4. Run All Examples")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        real_time_battle_example()
    elif choice == "2":
        quick_battle_example()
    elif choice == "3":
        event_log_example()
    elif choice == "4":
        print("\n" + "=" * 70)
        print("RUNNING ALL EXAMPLES")
        print("=" * 70 + "\n")
        
        input("Press Enter to start Full Real-Time Battle...")
        real_time_battle_example()
        
        input("\n\nPress Enter for Quick Battle Mode...")
        quick_battle_example()
        
        input("\n\nPress Enter for Event Log Example...")
        event_log_example()
        
        print("\n✅ All examples completed!")
    else:
        print("Invalid choice. Running default (Full Real-Time Battle)...")
        real_time_battle_example()
