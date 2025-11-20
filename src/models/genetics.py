"""
Advanced genetics system with dominant/recessive genes and trait blending.

This module implements:
- Mendelian genetics with dominant/recessive/codominant traits
- Proper trait combination from both parents
- Trait blending for quantitative traits
- Mutation with provenance tracking
- Cross-generational trait history
"""

from typing import List, Dict, Tuple, Optional, Any
import random
import time
from .trait import Trait, TraitProvenance
from .creature import Creature


class GeneticsEngine:
    """
    Enhanced genetics engine for creature breeding.
    
    Implements proper Mendelian genetics with:
    - Dominant/recessive gene expression
    - Trait blending for numerical modifiers
    - Mutation tracking with provenance
    - Multi-generational inheritance patterns
    """
    
    def __init__(self, mutation_rate: float = 0.1):
        """
        Initialize genetics engine.
        
        Args:
            mutation_rate: Base probability of mutations (0.0-1.0)
        """
        self.mutation_rate = mutation_rate
        self.generation_counter = 0
        self.MAX_TRAITS = 8
        self.SOFT_CAP_TRAITS = 5
    
    def combine_traits(
        self,
        parent1: Creature,
        parent2: Creature,
        generation: int = 0
    ) -> List[Trait]:
        """
        Combine traits from both parents using genetics rules.
        
        This is the core of the genetics system. It:
        1. Groups traits by name from both parents
        2. Applies dominant/recessive rules
        3. Blends quantitative traits (modifiers)
        4. Applies mutations
        5. Tracks provenance
        
        Args:
            parent1: First parent
            parent2: Second parent
            generation: Current generation number
            
        Returns:
            List of inherited traits for offspring
        """
        inherited_traits = []
        
        # Create trait dictionaries by name for both parents
        p1_traits = {t.name: t for t in parent1.traits}
        p2_traits = {t.name: t for t in parent2.traits}
        
        # Get all unique trait names from both parents
        all_trait_names = set(p1_traits.keys()) | set(p2_traits.keys())
        
        # Soft cap check - if parents have many traits, inheritance becomes harder
        total_parent_traits = len(p1_traits) + len(p2_traits)
        avg_traits = total_parent_traits / 2
        
        # Probability to drop a trait increases as we go over the soft cap
        drop_chance_base = 0.0
        if avg_traits > self.SOFT_CAP_TRAITS:
            # 10% chance to drop per trait over cap
            drop_chance_base = (avg_traits - self.SOFT_CAP_TRAITS) * 0.1
            drop_chance_base = min(drop_chance_base, 0.5)  # Cap drop chance at 50%
        
        for trait_name in all_trait_names:
            # Apply drop chance for non-essential traits
            if random.random() < drop_chance_base:
                continue
                
            p1_has = trait_name in p1_traits
            p2_has = trait_name in p2_traits
            
            trait = None
            if p1_has and p2_has:
                # Both parents have this trait - blend or express based on dominance
                trait = self._combine_same_trait(
                    p1_traits[trait_name],
                    p2_traits[trait_name],
                    generation
                )
            elif p1_has or p2_has:
                # Only one parent has this trait
                source_trait = p1_traits[trait_name] if p1_has else p2_traits[trait_name]
                trait = self._inherit_single_trait(source_trait, generation)
            
            if trait:
                # Chance for trait modification (evolutionary shift)
                # Instead of just stats changing, the trait itself changes nature
                if random.random() < self.mutation_rate * 0.2:  # 20% of mutation rate
                    trait = self._modify_trait_nature(trait, generation)
                
                inherited_traits.append(trait)
        
        # Apply mutations - may add new traits
        if random.random() < self.mutation_rate * 0.3:
            new_trait = self._generate_mutation(generation)
            if new_trait and new_trait.name not in all_trait_names:
                inherited_traits.append(new_trait)
        
        # Enforce Hard Cap
        if len(inherited_traits) > self.MAX_TRAITS:
            # Shuffle to randomly drop traits, but prefer keeping newer mutations or higher rarity
            # For now, just random shuffle and slice
            random.shuffle(inherited_traits)
            inherited_traits = inherited_traits[:self.MAX_TRAITS]
            
        return inherited_traits
    
    def _combine_same_trait(
        self,
        trait1: Trait,
        trait2: Trait,
        generation: int
    ) -> Optional[Trait]:
        """
        Combine the same trait from both parents.
        
        Rules:
        - Dominant + Dominant = Always expressed
        - Dominant + Recessive = Dominant expressed
        - Recessive + Recessive = Recessive expressed
        - Codominant + Codominant = Blended expression
        - Codominant + Dominant/Recessive = Partial expression
        
        Args:
            trait1: Trait from parent 1
            trait2: Trait from parent 2
            generation: Current generation
            
        Returns:
            Combined trait or None if not expressed
        """
        # Determine dominance interaction
        dom1 = trait1.dominance
        dom2 = trait2.dominance
        
        # Both dominant - always express
        if dom1 == "dominant" and dom2 == "dominant":
            return self._blend_trait_modifiers(trait1, trait2, 1.0, generation)
        
        # Dominant + Recessive - dominant wins
        elif (dom1 == "dominant" and dom2 == "recessive") or \
             (dom1 == "recessive" and dom2 == "dominant"):
            dominant_trait = trait1 if dom1 == "dominant" else trait2
            # 90% dominant expression, 10% hidden recessive influence
            return self._blend_trait_modifiers(dominant_trait, dominant_trait, 0.95, generation)
        
        # Both recessive - express
        elif dom1 == "recessive" and dom2 == "recessive":
            return self._blend_trait_modifiers(trait1, trait2, 1.0, generation)
        
        # Codominant interactions - blend traits
        elif dom1 == "codominant" or dom2 == "codominant":
            # Codominant means both traits contribute
            if dom1 == "codominant" and dom2 == "codominant":
                # Both codominant - 50/50 blend
                return self._blend_trait_modifiers(trait1, trait2, 1.0, generation)
            else:
                # One codominant, one dominant/recessive - 70/30 blend
                return self._blend_trait_modifiers(trait1, trait2, 0.85, generation)
        
        return None
    
    def _blend_trait_modifiers(
        self,
        trait1: Trait,
        trait2: Trait,
        blend_factor: float,
        generation: int
    ) -> Trait:
        """
        Blend the numerical modifiers of two traits.
        
        Args:
            trait1: First trait
            trait2: Second trait
            blend_factor: How much to blend (1.0 = full blend, 0.5 = partial)
            generation: Current generation
            
        Returns:
            New trait with blended modifiers
        """
        # Calculate blended modifiers
        str_mod = self._blend_values(
            trait1.strength_modifier,
            trait2.strength_modifier,
            blend_factor
        )
        spd_mod = self._blend_values(
            trait1.speed_modifier,
            trait2.speed_modifier,
            blend_factor
        )
        def_mod = self._blend_values(
            trait1.defense_modifier,
            trait2.defense_modifier,
            blend_factor
        )
        
        # Apply potential mutation to modifiers
        if random.random() < self.mutation_rate:
            mutation_strength = 0.05  # 5% variation
            str_mod *= random.uniform(1 - mutation_strength, 1 + mutation_strength)
            spd_mod *= random.uniform(1 - mutation_strength, 1 + mutation_strength)
            def_mod *= random.uniform(1 - mutation_strength, 1 + mutation_strength)
        
        # Blend interaction effects
        blended_effects = self._blend_interaction_effects(
            trait1.interaction_effects,
            trait2.interaction_effects
        )
        
        # Create provenance
        provenance = TraitProvenance(
            source_type='inherited',
            parent_traits=[trait1.name, trait2.name],
            generation=generation,
            timestamp=time.time(),
            mutation_count=0
        )
        
        # Create blended trait
        return Trait(
            name=trait1.name,  # Keep the trait name
            description=f"Inherited from both parents: {trait1.description}",
            trait_type=trait1.trait_type,
            strength_modifier=str_mod,
            speed_modifier=spd_mod,
            defense_modifier=def_mod,
            rarity=self._blend_rarity(trait1.rarity, trait2.rarity),
            dominance=trait1.dominance,  # Keep dominance of first parent
            provenance=provenance,
            interaction_effects=blended_effects
        )
    
    def _blend_values(self, val1: float, val2: float, blend_factor: float) -> float:
        """Blend two numerical values based on blend factor."""
        # blend_factor determines how much blending occurs
        # 1.0 = average, 0.5 = mostly first value
        return val1 * (1 - blend_factor * 0.5) + val2 * (blend_factor * 0.5)
    
    def _blend_interaction_effects(
        self,
        effects1: Dict[str, Any],
        effects2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Blend interaction effects from two traits.
        
        Args:
            effects1: First trait's effects
            effects2: Second trait's effects
            
        Returns:
            Blended effects dictionary
        """
        blended = {}
        all_keys = set(effects1.keys()) | set(effects2.keys())
        
        for key in all_keys:
            val1 = effects1.get(key)
            val2 = effects2.get(key)
            
            if val1 is not None and val2 is not None:
                # Both have this effect
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    # Numerical - average
                    blended[key] = (val1 + val2) / 2
                elif isinstance(val1, bool) and isinstance(val2, bool):
                    # Boolean - OR logic (if either is true, result is true)
                    blended[key] = val1 or val2
                else:
                    # Other types - randomly choose one
                    blended[key] = random.choice([val1, val2])
            elif val1 is not None:
                blended[key] = val1
            elif val2 is not None:
                blended[key] = val2
        
        return blended
    
    def _blend_rarity(self, rarity1: str, rarity2: str) -> str:
        """
        Blend rarity levels.
        
        Args:
            rarity1: First trait rarity
            rarity2: Second trait rarity
            
        Returns:
            Blended rarity string
        """
        rarity_levels = {
            'common': 0,
            'uncommon': 1,
            'rare': 2,
            'legendary': 3
        }
        
        level1 = rarity_levels.get(rarity1, 0)
        level2 = rarity_levels.get(rarity2, 0)
        avg_level = (level1 + level2) // 2
        
        reverse_map = {v: k for k, v in rarity_levels.items()}
        return reverse_map.get(avg_level, 'common')
    
    def _inherit_single_trait(
        self,
        trait: Trait,
        generation: int
    ) -> Optional[Trait]:
        """
        Inherit a trait from only one parent.
        
        Args:
            trait: The trait to inherit
            generation: Current generation
            
        Returns:
            Inherited trait or None if not expressed
        """
        # Recessive traits from single parent have lower inheritance chance
        if trait.dominance == "recessive":
            if random.random() < 0.5:  # 50% chance
                return None
        
        # Create a copy with updated provenance
        new_trait = trait.copy()
        new_trait.provenance = TraitProvenance(
            source_type='inherited',
            parent_traits=[trait.name],
            generation=generation,
            timestamp=time.time(),
            mutation_count=trait.provenance.mutation_count
        )
        
        # Apply potential mutation
        if random.random() < self.mutation_rate:
            new_trait = self._mutate_trait(new_trait)
        
        return new_trait
    
    def _mutate_trait(self, trait: Trait) -> Trait:
        """
        Apply mutation to a trait.
        
        Args:
            trait: Trait to mutate
            
        Returns:
            Mutated trait
        """
        mutation_strength = 0.1  # 10% variation
        
        mutated = trait.copy()
        mutated.strength_modifier *= random.uniform(1 - mutation_strength, 1 + mutation_strength)
        mutated.speed_modifier *= random.uniform(1 - mutation_strength, 1 + mutation_strength)
        mutated.defense_modifier *= random.uniform(1 - mutation_strength, 1 + mutation_strength)
        
        # Update provenance
        mutated.provenance.mutation_count += 1
        mutated.provenance.source_type = 'mutated'
        mutated.name = f"{trait.name}*"  # Mark as mutated
        mutated.description = f"Mutated variant: {trait.description}"
        
        return mutated
    
    def _modify_trait_nature(self, trait: Trait, generation: int) -> Trait:
        """
        Modify the fundamental nature of a trait (evolutionary shift).
        
        This can flip a trait (Aggressive <-> Timid) or shift it to a related
        variant (Aggressive -> Berserker).
        
        Args:
            trait: The trait to modify
            generation: Current generation
            
        Returns:
            Modified trait
        """
        from .expanded_traits import (
            AGGRESSIVE_TRAIT, TIMID_TRAIT, BOLD_TRAIT, CAUTIOUS_TRAIT,
            SOCIAL_TRAIT, SOLITARY_TRAIT, BERSERKER_TRAIT, EXECUTIONER_TRAIT,
            ARMORED_TRAIT, SWIFT_TRAIT
        )
        
        # Define modification pathways
        # key: trait name, value: list of possible evolutions/flips
        pathways = {
            "Aggressive": [TIMID_TRAIT, BERSERKER_TRAIT, BOLD_TRAIT],
            "Timid": [AGGRESSIVE_TRAIT, CAUTIOUS_TRAIT],
            "Bold": [CAUTIOUS_TRAIT, AGGRESSIVE_TRAIT, EXECUTIONER_TRAIT],
            "Cautious": [BOLD_TRAIT, TIMID_TRAIT],
            "Social": [SOLITARY_TRAIT],
            "Solitary": [SOCIAL_TRAIT],
            "Armored": [SWIFT_TRAIT],  # Trade armor for speed
            "Swift": [ARMORED_TRAIT],  # Trade speed for armor
        }
        
        base_name = trait.base_name()
        if base_name in pathways:
            # Pick a new form
            new_template = random.choice(pathways[base_name])
            
            # Create new trait based on template but keeping some history
            new_trait = new_template.copy()
            new_trait.provenance = TraitProvenance(
                source_type='modified',
                parent_traits=[trait.name],
                generation=generation,
                timestamp=time.time(),
                mutation_count=trait.provenance.mutation_count + 1
            )
            new_trait.description = f"Evolved from {trait.name}: {new_template.description}"
            return new_trait
            
        return trait

    def _generate_mutation(self, generation: int) -> Optional[Trait]:
        """
        Generate a completely new trait through mutation.
        
        Args:
            generation: Current generation
            
        Returns:
            New mutated trait or None
        """
        from .expanded_traits import ALL_CREATURE_TRAITS
        
        if not ALL_CREATURE_TRAITS:
            return None
        
        # Select a random trait from the trait library
        base_trait = random.choice(ALL_CREATURE_TRAITS)
        
        # Create a new instance with mutation provenance
        new_trait = base_trait.copy()
        new_trait.provenance = TraitProvenance(
            source_type='emergent',
            parent_traits=[],
            generation=generation,
            timestamp=time.time(),
            mutation_count=0
        )
        new_trait.description = f"Emerged through mutation: {base_trait.description}"
        
        return new_trait
    
    def combine_stats(
        self,
        parent1: Creature,
        parent2: Creature
    ) -> 'Stats':
        """
        Combine stats from both parents.
        
        Uses weighted averaging with random variation and genetic potential.
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Combined stats for offspring
        """
        from .stats import Stats
        
        p1_stats = parent1.base_stats
        p2_stats = parent2.base_stats
        
        def blend_stat(stat1: int, stat2: int) -> int:
            """
            Blend a single stat with genetic variation.
            
            Uses weighted averaging (not pure 50/50) to create variation.
            Adds random genetic potential.
            """
            # Random weight between 0.3 and 0.7 (not always 50/50)
            weight = random.uniform(0.3, 0.7)
            avg = stat1 * weight + stat2 * (1 - weight)
            
            # Add genetic variation (-15% to +15%)
            variation = random.uniform(-0.15, 0.15)
            result = avg * (1 + variation)
            
            # Rare genetic potential boost (5% chance of +20% boost)
            if random.random() < 0.05:
                result *= 1.2
            
            return max(1, int(result))
        
        return Stats(
            max_hp=blend_stat(p1_stats.max_hp, p2_stats.max_hp),
            attack=blend_stat(p1_stats.attack, p2_stats.attack),
            defense=blend_stat(p1_stats.defense, p2_stats.defense),
            speed=blend_stat(p1_stats.speed, p2_stats.speed),
            special_attack=blend_stat(p1_stats.special_attack, p2_stats.special_attack),
            special_defense=blend_stat(p1_stats.special_defense, p2_stats.special_defense)
        )


class PelletGenetics:
    """
    Genetics system for pellet reproduction.
    
    Similar to creature genetics but focused on pellet-specific traits
    like nutrition, growth rate, toxicity, etc.
    """
    
    def __init__(self, mutation_rate: float = 0.15):
        """
        Initialize pellet genetics.
        
        Args:
            mutation_rate: Base mutation rate for pellets (higher than creatures)
        """
        self.mutation_rate = mutation_rate
    
    def combine_pellet_traits(
        self,
        parent1: 'Pellet',
        parent2: Optional['Pellet'] = None
    ) -> 'PelletTraits':
        """
        Combine traits from parent pellet(s).
        
        Pellets can reproduce sexually (2 parents) or asexually (1 parent).
        
        Args:
            parent1: First parent pellet
            parent2: Optional second parent pellet
            
        Returns:
            Combined pellet traits
        """
        from .pellet import PelletTraits
        
        if parent2 is None:
            # Asexual reproduction - inherit with mutation
            return self._asexual_inheritance(parent1)
        else:
            # Sexual reproduction - blend traits
            return self._sexual_inheritance(parent1, parent2)
    
    def _asexual_inheritance(self, parent: 'Pellet') -> 'PelletTraits':
        """Asexual reproduction - clone with mutation."""
        from .pellet import PelletTraits
        
        # Start with parent traits
        traits = parent.traits
        
        # Apply higher mutation rate for asexual reproduction
        return traits.mutate(self.mutation_rate * 1.5)
    
    def _sexual_inheritance(self, parent1: 'Pellet', parent2: 'Pellet') -> 'PelletTraits':
        """Sexual reproduction - blend two parent pellets."""
        from .pellet import PelletTraits
        
        t1 = parent1.traits
        t2 = parent2.traits
        
        # Blend numerical traits
        nutrition = self._blend_pellet_stat(t1.nutritional_value, t2.nutritional_value)
        growth = self._blend_pellet_stat(t1.growth_rate, t2.growth_rate)
        spread = int(self._blend_pellet_stat(float(t1.spread_radius), float(t2.spread_radius)))
        size = self._blend_pellet_stat(t1.size, t2.size)
        toxicity = self._blend_pellet_stat(t1.toxicity, t2.toxicity)
        palatability = self._blend_pellet_stat(t1.palatability, t2.palatability)
        
        # Blend colors
        color = tuple(
            int((t1.color[i] + t2.color[i]) / 2)
            for i in range(3)
        )
        
        # Create offspring traits
        offspring_traits = PelletTraits(
            nutritional_value=nutrition,
            growth_rate=growth,
            spread_radius=spread,
            size=size,
            color=color,
            toxicity=toxicity,
            palatability=palatability
        )
        
        # Apply mutation
        return offspring_traits.mutate(self.mutation_rate)
    
    def _blend_pellet_stat(self, val1: float, val2: float) -> float:
        """Blend two pellet stat values with variation."""
        # Weighted average
        weight = random.uniform(0.3, 0.7)
        avg = val1 * weight + val2 * (1 - weight)
        
        # Add variation
        variation = random.uniform(-0.1, 0.1)
        return avg * (1 + variation)
