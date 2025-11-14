#!/usr/bin/env python3
"""
EvoBattle Demo Script

Demonstrates the core gameplay flow:
1. Generate random fighters
2. Simulate battles
3. Place bets
4. Breed winners
5. Continue evolution
"""

from src.utils.random_generator import RandomGenerator
from src.systems.battle import BattleSystem
from src.systems.betting import BettingSystem
from src.systems.breeding import BreedingSystem


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 60 + "\n")


def main():
    """
    Main demo function showcasing the EvoBattle game flow.
    """
    print("Welcome to EvoBattle!")
    print("An evolution-based battle game")
    print_separator()
    
    # Initialize game systems
    battle_system = BattleSystem()
    betting_system = BettingSystem()
    breeding_system = BreedingSystem(mutation_rate=0.3)
    
    print("Initializing game systems...")
    print(f"  - {battle_system}")
    print(f"  - {betting_system}")
    print(f"  - {breeding_system}")
    print_separator()
    
    # Generate initial fighters (Generation 0)
    print("Generating initial fighters (Generation 0)...")
    fighters = RandomGenerator.generate_fighters(4)
    
    for i, fighter in enumerate(fighters, 1):
        print(f"  Fighter {i}: {fighter}")
        for trait in fighter.traits:
            print(f"    - {trait}")
    
    print_separator()
    
    # Simulate a battle between first two fighters
    print("BATTLE 1: Setting up battle...")
    fighter1, fighter2 = fighters[0], fighters[1]
    
    print(f"  {fighter1.name} (Power: {fighter1.calculate_power():.2f})")
    print(f"    vs")
    print(f"  {fighter2.name} (Power: {fighter2.calculate_power():.2f})")
    
    # Place some bets
    print("\nPlacing bets...")
    betting_system.place_bet(fighter1.id, "Alice", 100.0)
    betting_system.place_bet(fighter1.id, "Bob", 50.0)
    betting_system.place_bet(fighter2.id, "Charlie", 75.0)
    print(f"  Total pot: ${betting_system.total_pot:.2f}")
    
    # Simulate the battle
    print("\nBattle in progress...")
    winner1, loser1 = battle_system.simulate_battle(fighter1, fighter2)
    
    print(f"  Winner: {winner1.name}!")
    print(f"  {winner1.name}: {winner1.wins} wins, {winner1.losses} losses")
    print(f"  {loser1.name}: {loser1.wins} wins, {loser1.losses} losses")
    
    # Calculate payouts
    payouts = betting_system.calculate_payout(winner1.id)
    print("\nBetting payouts:")
    for bettor, amount in payouts.items():
        print(f"  {bettor} wins: ${amount:.2f}")
    
    betting_system.clear_bets()
    print_separator()
    
    # Simulate second battle
    print("BATTLE 2: Setting up battle...")
    fighter3, fighter4 = fighters[2], fighters[3]
    
    print(f"  {fighter3.name} (Power: {fighter3.calculate_power():.2f})")
    print(f"    vs")
    print(f"  {fighter4.name} (Power: {fighter4.calculate_power():.2f})")
    
    print("\nBattle in progress...")
    winner2, loser2 = battle_system.simulate_battle(fighter3, fighter4)
    
    print(f"  Winner: {winner2.name}!")
    print(f"  {winner2.name}: {winner2.wins} wins, {winner2.losses} losses")
    print(f"  {loser2.name}: {loser2.wins} wins, {loser2.losses} losses")
    
    print_separator()
    
    # Breed the winners to create next generation
    print("BREEDING: Creating next generation...")
    print(f"  Parents: {winner1.name} x {winner2.name}")
    
    offspring = breeding_system.breed(winner1, winner2, "Next Gen Champion")
    
    print(f"\n  Offspring: {offspring}")
    print(f"  Generation: {offspring.generation}")
    print(f"  Inherited traits:")
    for trait in offspring.traits:
        print(f"    - {trait}")
    
    print_separator()
    
    # Display summary
    print("GAME SUMMARY")
    print(f"\nBattles fought: {len(battle_system.get_battle_history())}")
    print(f"Breeding events: {len(breeding_system.get_breeding_history())}")
    print(f"Betting rounds: {len(betting_system.get_betting_history())}")
    
    print("\nAll fighters:")
    all_fighters = fighters + [offspring]
    for fighter in all_fighters:
        print(f"  - {fighter.name}: Gen {fighter.generation}, Power {fighter.calculate_power():.2f}, W/L {fighter.wins}/{fighter.losses}")
    
    print_separator()
    print("Demo complete! The evolution continues...")
    print("\nThis was a demonstration of the core EvoBattle mechanics.")
    print("Future enhancements could include:")
    print("  - Web interface for interactive gameplay")
    print("  - Persistent storage for fighter lineages")
    print("  - Advanced trait combinations and synergies")
    print("  - Tournament brackets")
    print("  - Player accounts and leaderboards")


if __name__ == "__main__":
    main()
