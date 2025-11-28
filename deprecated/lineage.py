"""
Lineage model - Legacy lineage tracking system.

.. deprecated::
    This class is deprecated and kept for backward compatibility only.
    Lineage tracking is now integrated directly into the :class:`Creature` class
    through the following attributes:
    - parent_ids: List of parent creature IDs
    - strain_id: Genetic strain/family identifier
    - generation: Generation number
    - hue: Visual lineage indicator
    
    Use Creature's built-in lineage tracking instead of this separate class.
"""


class Lineage:
    """
    Tracks the ancestral lineage, breeding history, and strain membership of creatures.
    
    The lineage system records parent-child relationships, generation numbers,
    trait inheritance patterns, and strain/family membership. This allows tracking
    evolutionary progress, strain dominance, and genetic diversity.
    
    Attributes:
        creature_id (str): Unique identifier for the creature
        strain_id (str): Genetic strain/family identifier
        generation (int): Generation number (0 for original creatures)
        parent1_id (str): ID of first parent (None if generation 0)
        parent2_id (str): ID of second parent (None if generation 0)
        inherited_traits (list): List of traits inherited from parents
        birth_timestamp (float): When the creature was created/bred
    """
    
    def __init__(
        self,
        creature_id,
        strain_id=None,
        generation=0,
        parent1_id=None,
        parent2_id=None,
        inherited_traits=None,
        birth_timestamp=None
    ):
        """
        Initialize a new Lineage record.
        
        Args:
            creature_id (str): Unique identifier for the creature
            strain_id (str): Genetic strain/family identifier
            generation (int): Generation number
            parent1_id (str): ID of first parent
            parent2_id (str): ID of second parent
            inherited_traits (list): List of inherited trait names
            birth_timestamp (float): Creation timestamp
        """
        self.creature_id = creature_id
        self.strain_id = strain_id
        self.generation = generation
        self.parent1_id = parent1_id
        self.parent2_id = parent2_id
        self.inherited_traits = inherited_traits if inherited_traits is not None else []
        self.birth_timestamp = birth_timestamp
    
    def is_original(self):
        """Check if this creature is an original (generation 0)."""
        return self.generation == 0 and self.parent1_id is None and self.parent2_id is None
    
    def __repr__(self):
        """String representation of the Lineage."""
        return f"Lineage(creature_id='{self.creature_id}', strain_id='{self.strain_id}', generation={self.generation})"
