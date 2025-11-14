"""
EvoBattle - Evolution-based Battle Game
Main entry point for running the game demo.
"""

from src.models.fighter import Fighter
from src.models.trait import Trait
from src.models.lineage import Lineage
from src.systems.battle import Battle
from src.systems.breeding import Breeding
from src.systems.betting import Betting
from src.utils.random_generator import RandomGenerator


def main():
    """
    Demo script for running evo battle flow:
    - Generate fighters
    - Simulate battles
    - Breed fighters
    - Display results
    """
    print("=" * 50)
    print("Welcome to EvoBattle!")
    print("Evolution-Based Battle Game - Demo")
    print("=" * 50)
    print()
    
    print("🎮 Initializing game systems...")
    print("  ✓ Fighter models loaded")
    print("  ✓ Trait system loaded")
    print("  ✓ Lineage tracking loaded")
    print("  ✓ Battle system loaded")
    print("  ✓ Breeding system loaded")
    print("  ✓ Betting system loaded")
    print("  ✓ Random generator loaded")
    print()
    
    print("📊 Core systems ready for development!")
    print()
    print("Next steps:")
    print("  1. Implement fighter generation logic")
    print("  2. Create battle simulation mechanics")
    print("  3. Develop breeding and inheritance system")
    print("  4. Add betting functionality")
    print("  5. Build lineage tracking features")
    print()
    print("=" * 50)


if __name__ == "__main__":
    main()
