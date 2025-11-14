"""
Lineage model - Tracks fighter ancestry and evolutionary history.
"""


class Lineage:
    """
    Tracks the ancestral lineage and breeding history of fighters.
    
    The lineage system records parent-child relationships, generation numbers,
    and trait inheritance patterns. This allows players to track evolutionary
    progress and strategize breeding decisions.
    
    Attributes:
        fighter_id (str): Unique identifier for the fighter
        generation (int): Generation number (0 for original fighters)
        parent1_id (str): ID of first parent (None if generation 0)
        parent2_id (str): ID of second parent (None if generation 0)
        inherited_traits (list): List of traits inherited from parents
        birth_timestamp (float): When the fighter was created/bred
    """
    
    def __init__(
        self,
        fighter_id,
        generation=0,
        parent1_id=None,
        parent2_id=None,
        inherited_traits=None,
        birth_timestamp=None
    ):
        """
        Initialize a new Lineage record.
        
        Args:
            fighter_id (str): Unique identifier for the fighter
            generation (int): Generation number
            parent1_id (str): ID of first parent
            parent2_id (str): ID of second parent
            inherited_traits (list): List of inherited trait names
            birth_timestamp (float): Creation timestamp
        """
        self.fighter_id = fighter_id
        self.generation = generation
        self.parent1_id = parent1_id
        self.parent2_id = parent2_id
        self.inherited_traits = inherited_traits if inherited_traits is not None else []
        self.birth_timestamp = birth_timestamp
    
    def is_original(self):
        """Check if this fighter is an original (generation 0)."""
        return self.generation == 0 and self.parent1_id is None and self.parent2_id is None
    
    def __repr__(self):
        """String representation of the Lineage."""
        return f"Lineage(fighter_id='{self.fighter_id}', generation={self.generation})"
