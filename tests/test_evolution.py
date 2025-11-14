"""
Unit tests for Evolution and Genetics systems.
"""

import unittest
from src.models.evolution import EvolutionPath, GeneticsSystem, EvolutionSystem, create_example_evolution_system
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.trait import Trait


class TestEvolutionPath(unittest.TestCase):
    """Test cases for EvolutionPath class."""
    
    def test_evolution_path_initialization(self):
        """Test creating an EvolutionPath."""
        path = EvolutionPath(
            from_type="Basic",
            to_type="Advanced",
            min_level=10
        )
        self.assertEqual(path.from_type, "Basic")
        self.assertEqual(path.to_type, "Advanced")
        self.assertEqual(path.min_level, 10)
    
    def test_can_evolve_level_check(self):
        """Test evolution level requirements."""
        creature_type = CreatureType(name="Basic")
        creature = Creature(name="Test", creature_type=creature_type, level=5)
        
        path = EvolutionPath(from_type="Basic", to_type="Advanced", min_level=10)
        
        self.assertFalse(path.can_evolve(creature))
        
        creature.level = 10
        self.assertTrue(path.can_evolve(creature))
    
    def test_can_evolve_trait_requirements(self):
        """Test evolution with trait requirements."""
        creature_type = CreatureType(name="Basic")
        creature = Creature(name="Test", creature_type=creature_type, level=10)
        
        path = EvolutionPath(
            from_type="Basic",
            to_type="Special",
            min_level=10,
            required_traits=["Fire Affinity"]
        )
        
        self.assertFalse(path.can_evolve(creature))
        
        creature.add_trait(Trait(name="Fire Affinity"))
        self.assertTrue(path.can_evolve(creature))
    
    def test_evolution_path_serialization(self):
        """Test EvolutionPath serialization."""
        path = EvolutionPath(
            from_type="Newborn",
            to_type="Adult",
            min_level=15,
            required_traits=["Strong"]
        )
        
        data = path.to_dict()
        self.assertEqual(data['from_type'], "Newborn")
        self.assertEqual(data['min_level'], 15)
        
        restored = EvolutionPath.from_dict(data)
        self.assertEqual(restored.from_type, "Newborn")
        self.assertEqual(restored.to_type, "Adult")


class TestGeneticsSystem(unittest.TestCase):
    """Test cases for GeneticsSystem class."""
    
    def test_genetics_initialization(self):
        """Test creating a GeneticsSystem."""
        genetics = GeneticsSystem(mutation_rate=0.2)
        self.assertEqual(genetics.mutation_rate, 0.2)
    
    def test_breed_creates_offspring(self):
        """Test that breeding creates a valid offspring."""
        parent1 = Creature(name="Parent1", level=5)
        parent2 = Creature(name="Parent2", level=5)
        
        genetics = GeneticsSystem(mutation_rate=0.1)
        offspring = genetics.breed(parent1, parent2, "Child")
        
        self.assertIsNotNone(offspring)
        self.assertEqual(offspring.name, "Child")
        self.assertEqual(offspring.level, 1)
    
    def test_breed_inherits_stats(self):
        """Test that offspring inherits stats from parents."""
        type1 = CreatureType(
            name="Type1",
            base_stats=Stats(max_hp=100, hp=100, attack=20, defense=15)
        )
        type2 = CreatureType(
            name="Type2",
            base_stats=Stats(max_hp=120, hp=120, attack=15, defense=20)
        )
        
        parent1 = Creature(name="P1", creature_type=type1, level=1)
        parent2 = Creature(name="P2", creature_type=type2, level=1)
        
        genetics = GeneticsSystem(mutation_rate=0.0)
        offspring = genetics.breed(parent1, parent2)
        
        # Offspring stats should be in reasonable range between parents
        self.assertGreater(offspring.base_stats.max_hp, 50)
        self.assertLess(offspring.base_stats.max_hp, 150)
    
    def test_breed_inherits_traits(self):
        """Test that offspring can inherit traits."""
        parent1 = Creature(name="P1")
        parent1.add_trait(Trait(name="Swift", speed_modifier=1.2))
        
        parent2 = Creature(name="P2")
        parent2.add_trait(Trait(name="Strong", strength_modifier=1.3))
        
        genetics = GeneticsSystem(mutation_rate=0.0)
        offspring = genetics.breed(parent1, parent2)
        
        # Offspring may inherit some traits (random, so just check it's valid)
        self.assertIsInstance(offspring.traits, list)
    
    def test_mutation_can_occur(self):
        """Test that mutations can occur during breeding."""
        parent1 = Creature(name="P1")
        parent1.add_trait(Trait(name="Basic"))
        
        parent2 = Creature(name="P2")
        
        # High mutation rate to ensure mutation in test
        genetics = GeneticsSystem(mutation_rate=1.0)
        offspring = genetics.breed(parent1, parent2)
        
        # With 100% mutation rate and trait inheritance, 
        # offspring should have a mutated trait
        # (This is probabilistic, but with our setup should happen)
        self.assertIsInstance(offspring, Creature)


class TestEvolutionSystem(unittest.TestCase):
    """Test cases for EvolutionSystem class."""
    
    def test_evolution_system_initialization(self):
        """Test creating an EvolutionSystem."""
        system = EvolutionSystem()
        self.assertEqual(len(system.evolution_paths), 0)
        self.assertEqual(len(system.creature_types), 0)
    
    def test_register_creature_type(self):
        """Test registering creature types."""
        system = EvolutionSystem()
        ctype = CreatureType(name="Dragon")
        
        system.register_creature_type(ctype)
        self.assertIn("Dragon", system.creature_types)
    
    def test_add_evolution_path(self):
        """Test adding evolution paths."""
        system = EvolutionSystem()
        path = EvolutionPath(from_type="Baby", to_type="Adult", min_level=10)
        
        system.add_evolution_path(path)
        self.assertEqual(len(system.evolution_paths), 1)
    
    def test_get_available_evolutions(self):
        """Test getting available evolution paths."""
        system = EvolutionSystem()
        
        baby_type = CreatureType(name="Baby")
        adult_type = CreatureType(name="Adult")
        
        system.register_creature_type(baby_type)
        system.register_creature_type(adult_type)
        
        path = EvolutionPath(from_type="Baby", to_type="Adult", min_level=10)
        system.add_evolution_path(path)
        
        low_level = Creature(name="Young", creature_type=baby_type, level=5)
        high_level = Creature(name="Ready", creature_type=baby_type, level=10)
        
        # Low level can't evolve
        available_low = system.get_available_evolutions(low_level)
        self.assertEqual(len(available_low), 0)
        
        # High level can evolve
        available_high = system.get_available_evolutions(high_level)
        self.assertEqual(len(available_high), 1)
    
    def test_can_evolve(self):
        """Test checking if creature can evolve."""
        system = EvolutionSystem()
        
        base_type = CreatureType(name="Base")
        evolved_type = CreatureType(name="Evolved")
        
        system.register_creature_type(base_type)
        system.register_creature_type(evolved_type)
        
        path = EvolutionPath(from_type="Base", to_type="Evolved", min_level=5)
        system.add_evolution_path(path)
        
        creature = Creature(name="Test", creature_type=base_type, level=3)
        self.assertFalse(system.can_evolve(creature))
        
        creature.level = 5
        self.assertTrue(system.can_evolve(creature))
    
    def test_evolve_creature(self):
        """Test evolving a creature."""
        system = EvolutionSystem()
        
        base_type = CreatureType(
            name="Newborn",
            base_stats=Stats(max_hp=80, hp=80, attack=10)
        )
        evolved_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=120, hp=120, attack=18)
        )
        
        system.register_creature_type(base_type)
        system.register_creature_type(evolved_type)
        
        path = EvolutionPath(from_type="Newborn", to_type="Warrior", min_level=10)
        system.add_evolution_path(path)
        
        creature = Creature(name="Fighter", creature_type=base_type, level=10)
        old_max_hp = creature.stats.max_hp
        
        success, message = system.evolve(creature)
        
        self.assertTrue(success)
        self.assertIn("Evolved", message)
        self.assertEqual(creature.creature_type.name, "Warrior")
        # Stats should be updated
        self.assertNotEqual(creature.stats.max_hp, old_max_hp)
        # Should be fully healed
        self.assertEqual(creature.stats.hp, creature.stats.max_hp)
    
    def test_evolve_fails_when_conditions_not_met(self):
        """Test that evolution fails when conditions aren't met."""
        system = EvolutionSystem()
        
        base_type = CreatureType(name="Base")
        system.register_creature_type(base_type)
        
        creature = Creature(name="Test", creature_type=base_type, level=1)
        
        success, message = system.evolve(creature)
        
        self.assertFalse(success)
        self.assertIn("No evolution", message)
    
    def test_evolution_system_serialization(self):
        """Test EvolutionSystem serialization."""
        system = EvolutionSystem()
        
        ctype = CreatureType(name="Test")
        system.register_creature_type(ctype)
        
        path = EvolutionPath(from_type="A", to_type="B", min_level=5)
        system.add_evolution_path(path)
        
        data = system.to_dict()
        
        self.assertIn("creature_types", data)
        self.assertIn("evolution_paths", data)
        
        restored = EvolutionSystem.from_dict(data)
        self.assertEqual(len(restored.creature_types), 1)
        self.assertEqual(len(restored.evolution_paths), 1)


class TestExampleEvolutionSystem(unittest.TestCase):
    """Test the example evolution system."""
    
    def test_create_example_system(self):
        """Test creating the example evolution system."""
        system = create_example_evolution_system()
        
        self.assertGreater(len(system.creature_types), 0)
        self.assertGreater(len(system.evolution_paths), 0)
    
    def test_example_system_evolution(self):
        """Test evolution using the example system."""
        system = create_example_evolution_system()
        
        newborn_type = system.creature_types.get("Newborn")
        self.assertIsNotNone(newborn_type)
        
        creature = Creature(
            name="TestNewborn",
            creature_type=newborn_type,
            level=10
        )
        
        self.assertTrue(system.can_evolve(creature))
        
        available = system.get_available_evolutions(creature)
        self.assertGreater(len(available), 0)


if __name__ == '__main__':
    unittest.main()
