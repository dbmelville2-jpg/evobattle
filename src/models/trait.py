"""
Trait model - Represents inheritable characteristics and abilities.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import time


@dataclass
class TraitProvenance:
    """
    Tracks the origin and history of a trait.
    
    Attributes:
        source_type: How the trait was acquired ('inherited', 'mutated', 'emergent')
        parent_traits: Names of parent traits if inherited
        generation: Generation number when trait appeared
        timestamp: When the trait was acquired
        mutation_count: Number of mutations this trait has undergone
    """
    source_type: str = "inherited"
    parent_traits: List[str] = field(default_factory=list)
    generation: int = 0
    timestamp: float = field(default_factory=time.time)
    mutation_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'source_type': self.source_type,
            'parent_traits': self.parent_traits,
            'generation': self.generation,
            'timestamp': self.timestamp,
            'mutation_count': self.mutation_count
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TraitProvenance':
        """Deserialize from dictionary."""
        return TraitProvenance(
            source_type=data.get('source_type', 'inherited'),
            parent_traits=data.get('parent_traits', []),
            generation=data.get('generation', 0),
            timestamp=data.get('timestamp', time.time()),
            mutation_count=data.get('mutation_count', 0)
        )


class Trait:
    """
    Represents a genetic trait that can be inherited by fighters.
    
    Traits modify fighter attributes or provide special abilities during
    battles. They can be passed down through breeding and may mutate or
    combine in offspring.

    Enhanced with:
    - Dominance system (dominant/recessive genes)
    - Expanded trait categories (behavioral, physical, ecological)
    - Trait provenance tracking
    - Cross-entity interaction effects
    """

    def __init__(self,
        name: str = "Basic Trait",
        description: str = "A basic trait",
        trait_type: str = "neutral",
        strength_modifier: float = 1.0,
        speed_modifier: float = 1.0,
        defense_modifier: float = 1.0,
        rarity: str = "common",
        dominance: str = "codominant",
        provenance: Optional[TraitProvenance] = None,
        interaction_effects: Optional[Dict[str, Any]] = None,
        mutated: bool = False
    ):
        """
        Initialize a new Trait.
        
        Args:
            name (str): The trait's name
            description (str): Description of what the trait does
            trait_type (str): Category of the trait
            strength_modifier (float): Strength stat multiplier
            speed_modifier (float): Speed stat multiplier
            defense_modifier (float): Defense stat multiplier
            rarity (str): Rarity level of the trait
            dominance (str): Gene dominance type
            provenance (TraitProvenance): Trait origin tracking
            interaction_effects (Dict): Effects on cross-entity interactions
            mutated (bool): Whether this trait instance is a mutation
        """
        self.name = name
        self.description = description
        self.trait_type = trait_type
        self.strength_modifier = strength_modifier
        self.speed_modifier = speed_modifier
        self.defense_modifier = defense_modifier
        self.rarity = rarity
        self.dominance = dominance
        self.provenance = provenance if provenance else TraitProvenance()
        self.interaction_effects = interaction_effects if interaction_effects else {}
        # metadata flag to indicate trait instance was produced by mutation
        self.mutated = mutated
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'trait_type': self.trait_type,
            'strength_modifier': self.strength_modifier,
            'speed_modifier': self.speed_modifier,
            'defense_modifier': self.defense_modifier,
            'rarity': self.rarity,
            'dominance': self.dominance,
            'provenance': self.provenance.to_dict() if self.provenance else None,
            'interaction_effects': self.interaction_effects,
            'mutated': self.mutated
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Trait':
        """Deserialize from dictionary."""
        provenance = None
        if 'provenance' in data and data.get('provenance'):
            provenance = TraitProvenance.from_dict(data['provenance'])
        
        return Trait(
            name=data.get('name', 'Basic Trait'),
            description=data.get('description', 'A basic trait'),
            trait_type=data.get('trait_type', 'neutral'),
            strength_modifier=data.get('strength_modifier', 1.0),
            speed_modifier=data.get('speed_modifier', 1.0),
            defense_modifier=data.get('defense_modifier', 1.0),
            rarity=data.get('rarity', 'common'),
            dominance=data.get('dominance', 'codominant'),
            provenance=provenance,
            interaction_effects=data.get('interaction_effects', {}),
            mutated=data.get('mutated', False)
        )
    
    def copy(self) -> 'Trait':
        """Create a copy of this trait."""
        return Trait(
            name=self.name,
            description=self.description,
            trait_type=self.trait_type,
            strength_modifier=self.strength_modifier,
            speed_modifier=self.speed_modifier,
            defense_modifier=self.defense_modifier,
            rarity=self.rarity,
            dominance=self.dominance,
            provenance=TraitProvenance(
                source_type=self.provenance.source_type,
                parent_traits=self.provenance.parent_traits.copy(),
                generation=self.provenance.generation,
                timestamp=self.provenance.timestamp,
                mutation_count=self.provenance.mutation_count
            ),
            interaction_effects=self.interaction_effects.copy(),
            mutated=self.mutated
        )
    
    def base_name(self) -> str:
        """
        Return the canonical trait name without mutation display markers.
        Strips trailing plus signs, asterisks, and common " (Mutated)" suffix.
        """
        name = self.name or ""
        name = name.strip()

        # Strip trailing '+' and '*' markers (can be repeated)
        while name.endswith('+') or name.endswith('*'):
            name = name[:-1].rstrip()

        # Strip common "(Mutated)" marker variants
        for suffix in (" (Mutated)", "(Mutated)", " (mutated)", "(mutated)"):
            if name.endswith(suffix):
                name = name[:-len(suffix)].rstrip()

        # Final trim of any leftover marker characters/spaces
        name = name.rstrip(' +*')

        return name
    
    def normalized_name(self) -> str:
        """
        Return a lower-cased, stripped canonical name useful for comparisons.
        """
        return self.base_name().strip().lower()
    
    def mark_mutated(self, marker: str = '+') -> None:
        """
        Mark this trait instance as mutated for display purposes.

        This sets the metadata flag and appends a visual marker to the name
        if not already present. Prefer using the `mutated` flag for logic and
        `base_name()` for comparisons.
        """
        self.mutated = True
        if not marker:
            return

        # Avoid duplicating markers; consider existing trailing spaces/markers
        stripped = self.name.rstrip()
        if stripped.endswith(marker):
            # Already has marker (with or without trailing spaces) -> normalize spacing
            # Ensure single space before marker
            core = stripped[:-len(marker)].rstrip()
            self.name = f"{core} {marker}"
        else:
            # Append single spaced marker
            self.name = f"{stripped} {marker}"
    
    def is_mutated(self) -> bool:
        """Convenience: returns whether this trait instance is marked mutated."""
        return bool(self.mutated)
    
    def __repr__(self):
        """String representation of the Trait including modifiers and mutated flag."""
        mods = f"str={self.strength_modifier}, spd={self.speed_modifier}, def={self.defense_modifier}"
        prov = None
        try:
            prov = f"gen={self.provenance.generation},mut_cnt={self.provenance.mutation_count}"
        except Exception:
            prov = ""
        return (f"Trait(name='{self.name}', base='{self.base_name()}', type='{self.trait_type}', "
                f"rarity='{self.rarity}', dominance='{self.dominance}', mutated={self.mutated}, "
                f"mods=({mods}) {prov})")
    
    def __eq__(self, other: object) -> bool:
        """
        Equality based on canonical base name and core modifiers/mutated flag.
        This keeps identity stable across display-only name markers.
        """
        if not isinstance(other, Trait):
            return NotImplemented
        return (
            self.normalized_name() == other.normalized_name() and
            float(self.strength_modifier) == float(other.strength_modifier) and
            float(self.speed_modifier) == float(other.speed_modifier) and
            float(self.defense_modifier) == float(other.defense_modifier) and
            bool(self.mutated) == bool(other.mutated)
        )
    
    def __hash__(self) -> int:
        """Hash consistent with __eq__."""
        return hash((self.normalized_name(), round(self.strength_modifier, 6),
                     round(self.speed_modifier, 6), round(self.defense_modifier, 6), bool(self.mutated)))
