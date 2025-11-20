"""
Random Trait Generator - Procedurally generates traits for emergent diversity.

This module provides procedural generation of traits that can be injected into
the gene pool through mutations, environmental pressures, or cosmic events.
"""

from typing import Optional, Dict, Any, List
import random
import time
from .trait import Trait, TraitProvenance


# Template components for trait name generation
ADJECTIVES = [
    "Ancient", "Blazing", "Celestial", "Dazzling", "Ethereal",
    "Feral", "Glacial", "Haunted", "Infernal", "Jade",
    "Keen", "Luminous", "Mystic", "Nocturnal", "Obsidian",
    "Primal", "Quantum", "Radiant", "Stellar", "Tempest",
    "Umbral", "Vivid", "Wicked", "Xenial", "Zealous",
    "Acidic", "Brutal", "Crystalline", "Dimensional", "Elastic",
    "Fractal", "Gilded", "Hollow", "Ionic", "Jagged"
]

NOUNS = [
    "Fury", "Grace", "Vigor", "Wisdom", "Instinct",
    "Might", "Spirit", "Focus", "Pulse", "Aura",
    "Resilience", "Swiftness", "Cunning", "Tenacity", "Dominance",
    "Harmony", "Chaos", "Balance", "Resonance", "Adaptation",
    "Evolution", "Mutation", "Synthesis", "Transcendence", "Essence",
    "Power", "Presence", "Force", "Energy", "Catalyst"
]

PHYSICAL_DESCRIPTORS = [
    "Plated", "Scaled", "Horned", "Winged", "Spiked",
    "Armored", "Crystalline", "Barbed", "Fanged", "Clawed"
]

BEHAVIORAL_DESCRIPTORS = [
    "Hunter's", "Defender's", "Wanderer's", "Strategist's", "Berserker's",
    "Sage's", "Trickster's", "Guardian's", "Predator's", "Survivor's"
]

METABOLIC_DESCRIPTORS = [
    "Accelerated", "Regulated", "Adaptive", "Balanced", "Vigorous"
]

ENVIRONMENTAL_DESCRIPTORS = [
    "Adapted", "Resistant", "Native", "Wild", "Natural",
    "Hardy", "Rugged", "Attuned", "Weathered", "Acclimated"
]


class TraitGenerator:
    """
    Procedurally generates random traits for injection into the gene pool.
    
    Generates traits with:
    - Unique names from combinatorial templates
    - Balanced stat modifiers
    - Appropriate categories and rarities
    - Cross-entity interaction effects
    - Proper provenance tracking
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the trait generator.
        
        Args:
            seed: Random seed for reproducible generation (None for random)
        """
        if seed is not None:
            random.seed(seed)
        
        self.generated_traits: List[Trait] = []
        self.trait_name_history: set = set()
    
    def generate_trait(
        self,
        category: Optional[str] = None,
        rarity: Optional[str] = None,
        generation: int = 0,
        source_type: str = 'emergent'
    ) -> Trait:
        """
        Generate a random trait.
        
        Args:
            category: Trait category (None for random choice)
            rarity: Trait rarity (None for random based on probability)
            generation: Generation number when trait appears
            source_type: Provenance source type
            
        Returns:
            A newly generated trait
        """
        # Determine category
        if category is None:
            category = random.choice([
                'physical', 'behavioral', 'metabolic', 
                'ecological', 'offensive', 'defensive', 'utility',
                'environmental'
            ])
        
        # Determine rarity
        if rarity is None:
            rarity = self._random_rarity()
        
        # Generate unique name
        name = self._generate_unique_name(category)
        
        # Generate description
        description = self._generate_description(name, category)
        
        # Generate modifiers based on category and rarity
        modifiers = self._generate_modifiers(category, rarity)
        
        # Generate interaction effects
        interaction_effects = self._generate_interaction_effects(category, rarity)
        
        # Determine dominance
        dominance = self._determine_dominance(rarity)
        
        # Create provenance
        provenance = TraitProvenance(
            source_type=source_type,
            parent_traits=[],
            generation=generation,
            timestamp=time.time(),
            mutation_count=0
        )
        
        # Create trait
        trait = Trait(
            name=name,
            description=description,
            trait_type=category,
            strength_modifier=modifiers['strength'],
            speed_modifier=modifiers['speed'],
            defense_modifier=modifiers['defense'],
            rarity=rarity,
            dominance=dominance,
            provenance=provenance,
            interaction_effects=interaction_effects
        )
        
        self.generated_traits.append(trait)
        self.trait_name_history.add(name)
        
        return trait
    
    def generate_creature_trait(
        self,
        generation: int = 0,
        source_type: str = 'emergent'
    ) -> Trait:
        """
        Generate a trait specifically for creatures.
        
        Args:
            generation: Generation number
            source_type: Provenance source type
            
        Returns:
            A creature-focused trait
        """
        category = random.choice([
            'physical', 'behavioral', 'metabolic', 
            'ecological', 'offensive', 'defensive',
            'environmental'
        ])
        
        return self.generate_trait(
            category=category,
            generation=generation,
            source_type=source_type
        )
    
    def generate_pellet_trait(
        self,
        generation: int = 0,
        source_type: str = 'emergent'
    ) -> Trait:
        """
        Generate a trait specifically for pellets.
        
        Args:
            generation: Generation number
            source_type: Provenance source type
            
        Returns:
            A pellet-focused trait
        """
        # Pellets have different trait categories
        return self.generate_trait(
            category='pellet',
            generation=generation,
            source_type=source_type
        )
    
    def _generate_unique_name(self, category: str) -> str:
        """
        Generate a unique trait name.
        
        Args:
            category: Trait category
            
        Returns:
            A unique trait name
        """
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            # Choose template based on category
            if category in ['physical', 'offensive', 'defensive']:
                descriptor = random.choice(PHYSICAL_DESCRIPTORS)
                noun = random.choice(NOUNS)
                name = f"{descriptor} {noun}"
            elif category == 'behavioral':
                descriptor = random.choice(BEHAVIORAL_DESCRIPTORS)
                noun = random.choice(NOUNS)
                name = f"{descriptor} {noun}"
                descriptor = random.choice(METABOLIC_DESCRIPTORS)
                noun = random.choice(NOUNS)
                name = f"{descriptor} {noun}"
            elif category == 'environmental':
                descriptor = random.choice(ENVIRONMENTAL_DESCRIPTORS)
                noun = random.choice(NOUNS)
                name = f"{descriptor} {noun}"
            else:
                # Generic template
                adjective = random.choice(ADJECTIVES)
                noun = random.choice(NOUNS)
                name = f"{adjective} {noun}"
            
            # Check if name is unique
            if name not in self.trait_name_history:
                return name
            
            attempts += 1
        
        # Fallback: add generation suffix
        base_name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
        suffix = random.randint(1000, 9999)
        return f"{base_name} {suffix}"
    
    def _generate_description(self, name: str, category: str) -> str:
        """
        Generate a description for the trait.
        
        Args:
            name: Trait name
            category: Trait category
            
        Returns:
            Description string
        """
        templates = {
            'physical': [
                f"A physical adaptation granting {name.lower()} to the bearer",
                f"Evolved trait providing enhanced {category} capabilities",
                f"Natural selection produced this unique {category} adaptation"
            ],
            'behavioral': [
                f"Influences behavior through {name.lower()}",
                f"A behavioral pattern that emerged through adaptation",
                f"Instinctive tendency toward {name.lower()}"
            ],
            'metabolic': [
                f"Optimizes energy usage through {name.lower()}",
                f"Metabolic efficiency trait enhancing survival",
                f"Regulates biological processes for improved performance"
            ],
            'ecological': [
                f"Affects interactions with the environment and other entities",
                f"Ecological adaptation for specific niches",
                f"Evolved to thrive in particular ecological conditions"
            ],
            'offensive': [
                f"Enhances combat effectiveness and damage output",
                f"Aggressive trait improving attack capabilities",
                f"Battle-hardened adaptation for combat dominance"
            ],
            'defensive': [
                f"Provides protection and survival advantages",
                f"Defensive adaptation reducing damage taken",
                f"Evolved resilience against threats"
            ],
            'pellet': [
                f"Environmental adaptation for pellet survival",
                f"Special characteristic influencing pellet ecology"
            ],
            'environmental': [
                f"Adaptation to specific environmental conditions",
                f"Survival trait for harsh environments",
                f"Evolved resilience to environmental factors"
            ]
        }
        
        category_templates = templates.get(category, templates['physical'])
        return random.choice(category_templates)
    
    def _generate_modifiers(self, category: str, rarity: str) -> Dict[str, float]:
        """
        Generate stat modifiers based on category and rarity.
        
        Args:
            category: Trait category
            rarity: Trait rarity
            
        Returns:
            Dictionary of stat modifiers
        """
        # Base modifier range based on rarity
        rarity_ranges = {
            'common': (0.95, 1.1),
            'uncommon': (0.9, 1.15),
            'rare': (0.85, 1.25),
            'legendary': (0.7, 1.4)
        }
        
        min_mod, max_mod = rarity_ranges.get(rarity, (0.95, 1.1))
        
        # Category influences which stats are modified
        if category == 'offensive':
            strength = random.uniform(max_mod - 0.1, max_mod)
            speed = random.uniform(1.0, max_mod - 0.1)
            defense = random.uniform(min_mod, 1.0)
        elif category == 'defensive':
            strength = random.uniform(min_mod, 1.0)
            speed = random.uniform(min_mod, 1.0)
            defense = random.uniform(max_mod - 0.1, max_mod)
        elif category == 'physical':
            # Balanced physical traits
            strength = random.uniform(min_mod, max_mod)
            speed = random.uniform(min_mod, max_mod)
            defense = random.uniform(min_mod, max_mod)
        elif category == 'behavioral':
            # Behavioral traits affect speed and slight stat variations
            strength = random.uniform(0.95, 1.05)
            speed = random.uniform(min_mod, max_mod)
            defense = random.uniform(0.95, 1.05)
            # Metabolic traits provide defensive benefits
            strength = random.uniform(0.95, 1.05)
            speed = random.uniform(0.95, 1.05)
            defense = random.uniform(1.0, max_mod)
        elif category == 'environmental':
            # Environmental traits are versatile
            strength = random.uniform(0.95, 1.05)
            speed = random.uniform(0.95, 1.05)
            defense = random.uniform(0.95, 1.05)
        else:
            # Utility/ecological - minimal direct stat impact
            strength = random.uniform(0.98, 1.02)
            speed = random.uniform(0.98, 1.02)
            defense = random.uniform(0.98, 1.02)
        
        return {
            'strength': round(strength, 2),
            'speed': round(speed, 2),
            'defense': round(defense, 2)
        }
    
    def _generate_interaction_effects(
        self,
        category: str,
        rarity: str
    ) -> Dict[str, Any]:
        """
        Generate interaction effects for the trait.
        
        Args:
            category: Trait category
            rarity: Trait rarity
            
        Returns:
            Dictionary of interaction effects
        """
        effects = {}
        
        # Rarer traits have more/stronger effects
        num_effects = {
            'common': 1,
            'uncommon': random.randint(1, 2),
            'rare': random.randint(2, 3),
            'legendary': random.randint(3, 4)
        }.get(rarity, 1)
        
        # Category-specific effect pools
        if category == 'offensive':
            possible_effects = {
                'attack_bonus': random.uniform(0.05, 0.2),
                'critical_hit_chance': random.uniform(1.1, 1.3),
                'damage_multiplier': random.uniform(1.05, 1.15),
                'armor_penetration': random.uniform(0.1, 0.3),
                'bleed_on_hit': random.choice([True, False]),
                'poison_on_hit': random.uniform(0.3, 1.0),
                'lifesteal': random.uniform(0.1, 0.5),
                'execute_bonus': random.uniform(0.5, 1.5),
                'multi_strike': random.randint(2, 3),
                'ambush_predator': random.choice([True, False])
            }
        elif category == 'defensive':
            possible_effects = {
                'damage_reduction': random.uniform(0.05, 0.2),
                'dodge_chance': random.uniform(1.1, 1.3),
                'regeneration_rate': random.uniform(0.01, 0.05),
                'resistance_bonus': random.uniform(0.1, 0.25)
            }
        elif category == 'behavioral':
            possible_effects = {
                'aggression_modifier': random.uniform(-0.3, 0.3),
                'flee_threshold': random.uniform(0.2, 0.7),
                'exploration_range': random.uniform(1.1, 1.5),
                'target_preference': random.choice(['weakest', 'strongest', 'nearest', 'random']),
                'pack_hunter': random.choice([True, False]),
                'loner_strength': random.choice([True, False]),
                'scaredy_cat': random.choice([True, False]),
                'circadian_rhythm': random.choice(['nocturnal', 'diurnal', 'any'])
            }
        elif category == 'metabolic':
            possible_effects = {
                'hunger_rate_modifier': random.uniform(0.7, 1.3),
                'healing_multiplier': random.uniform(1.1, 1.4),
                'energy_efficiency': random.uniform(1.05, 1.25),
                'stamina_bonus': random.uniform(0.1, 0.3)
            }
        elif category == 'ecological':
            possible_effects = {
                'resource_detection': random.uniform(1.2, 1.8),
                'pellet_selectivity': random.uniform(0.8, 1.5),
                'toxin_resistance': random.uniform(0.1, 0.5),
                'symbiotic_bonus': random.uniform(0.05, 0.15)
            }
        elif category == 'environmental':
            possible_effects = {
                'environmental_resistance': random.uniform(0.1, 0.3),
                'terrain_affinity': random.choice(['water', 'rocky', 'forest', 'desert', 'marsh', 'grass']),
                'weather_affinity': random.choice(['clear', 'rainy', 'stormy', 'foggy', 'drought']),
                'hazard_resistance': random.uniform(0.2, 0.5)
            }
        else:
            possible_effects = {
                'special_ability': True,
                'unique_interaction': random.choice(['positive', 'negative', 'variable'])
            }
        
        # Select random effects
        selected = random.sample(
            list(possible_effects.items()),
            min(num_effects, len(possible_effects))
        )
        
        for key, value in selected:
            effects[key] = value
        
        return effects
    
    def _determine_dominance(self, rarity: str) -> str:
        """
        Determine dominance based on rarity and randomness.
        
        Args:
            rarity: Trait rarity
            
        Returns:
            Dominance type
        """
        # Rarer traits tend to be more dominant
        if rarity == 'legendary':
            return random.choice(['dominant'] * 3 + ['codominant'])
        elif rarity == 'rare':
            return random.choice(['dominant'] * 2 + ['codominant', 'recessive'])
        elif rarity == 'uncommon':
            return random.choice(['dominant', 'codominant', 'recessive'])
        else:
            return random.choice(['codominant'] * 2 + ['recessive', 'dominant'])
    
    def _random_rarity(self) -> str:
        """
        Generate a random rarity with weighted probabilities.
        
        Returns:
            Rarity string
        """
        roll = random.random()
        
        if roll < 0.6:
            return 'common'
        elif roll < 0.85:
            return 'uncommon'
        elif roll < 0.97:
            return 'rare'
        else:
            return 'legendary'
    
    def get_generated_traits(self) -> List[Trait]:
        """
        Get list of all generated traits.
        
        Returns:
            List of generated traits
        """
        return self.generated_traits.copy()
    
    def clear_history(self):
        """Clear generation history."""
        self.generated_traits.clear()
        self.trait_name_history.clear()
