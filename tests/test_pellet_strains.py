import unittest
from src.models.pellet import Pellet
import random

class TestPelletStrains(unittest.TestCase):
    def test_strain_initialization(self):
        """Test that pellets are initialized with a strain ID."""
        p = Pellet()
        self.assertIsNotNone(p.strain_id)
        self.assertIsInstance(p.strain_id, str)
        print(f"Initial Strain ID: {p.strain_id}")

    def test_asexual_reproduction_inheritance(self):
        """Test that asexual reproduction inherits strain ID."""
        parent = Pellet()
        # Force low mutation rate to ensure inheritance
        child = parent.reproduce(mutation_rate=0.0)
        
        self.assertEqual(child.strain_id, parent.strain_id)
        print(f"Parent Strain: {parent.strain_id} -> Child Strain: {child.strain_id}")

    def test_sexual_reproduction_inheritance(self):
        """Test that sexual reproduction inherits from one parent."""
        p1 = Pellet()
        p2 = Pellet()
        
        # Force low mutation rate
        child = p1.reproduce(mutation_rate=0.0, partner=p2)
        
        self.assertIn(child.strain_id, [p1.strain_id, p2.strain_id])
        print(f"P1: {p1.strain_id}, P2: {p2.strain_id} -> Child: {child.strain_id}")

    def test_strain_mutation(self):
        """Test that new strains can be created via mutation."""
        parent = Pellet()
        
        # Force high mutation rate to trigger new strain
        # We need to mock random or just run until we get a mutation?
        # The logic uses 0.5 * mutation_rate for asexual new strain.
        # Let's try with mutation_rate=2.0 (100% chance)
        
        # Wait, random.random() < 2.0 * 0.5 = 1.0 is always true.
        child = parent.reproduce(mutation_rate=2.0)
        
        self.assertNotEqual(child.strain_id, parent.strain_id)
        print(f"Parent Strain: {parent.strain_id} -> Mutated Child Strain: {child.strain_id}")

if __name__ == '__main__':
    unittest.main()
