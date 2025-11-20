"""
Canonical mutation helpers for EvoBattle.
Provides trade-off mutation behavior used by breeding and evolution.
"""
from typing import Tuple
import random
import time
from src.models.trait import Trait, TraitProvenance


def apply_tradeoff_mutation(trait: Trait, mutation_strength: float = 0.1, force_tradeoff: bool = True) -> Trait:
    """
    Return a new Trait instance mutated from the given trait.

    Behavior:
    - Copies the input trait into a new Trait
    - Chooses one numeric modifier to increase and another to decrease
      by amounts proportional to mutation_strength.
    - Sets mutated=True on the returned trait and appends a '+' marker to the name
      for display purposes.
    - Updates provenance.mutation_count and provenance.source_type.
    - Updates description to indicate the trade-off performed.

    Args:
        trait: Trait to mutate (original is not modified)
        mutation_strength: Fractional amount to change (e.g., 0.1 = 10%)
        force_tradeoff: If True, always perform both increase and decrease; otherwise
                        may perform only one-sided mutations sometimes.

    Returns:
        A new Trait instance representing the mutated trait.
    """
    # Create a shallow copy via constructor to avoid mutating original
    # Keep provenance updated: increment generation/mutation_count
    prov_ts = trait.provenance.timestamp if (trait.provenance and getattr(trait.provenance, 'timestamp', None)) else time.time()
    new_trait = Trait(
        name=trait.name,
        description=trait.description,
        trait_type=trait.trait_type,
        strength_modifier=trait.strength_modifier,
        speed_modifier=trait.speed_modifier,
        defense_modifier=trait.defense_modifier,
        rarity=trait.rarity,
        dominance=trait.dominance,
        provenance=TraitProvenance(
            source_type='mutated',
            parent_traits=[trait.base_name()],
            generation=(trait.provenance.generation + 1) if trait.provenance else 1,
            timestamp=prov_ts,
            mutation_count=(trait.provenance.mutation_count + 1) if trait.provenance else 1
        ),
        interaction_effects=trait.interaction_effects.copy() if trait.interaction_effects else {},
        mutated=True
    )

    # Select modifiers to adjust
    modifiers = ['strength_modifier', 'speed_modifier', 'defense_modifier']

    # Pick increase and decrease targets
    inc, dec = random.sample(modifiers, 2)

    # Calculate delta based on current value and mutation_strength
    def apply_delta(name: str, delta_frac: float, increase: bool):
        val = getattr(new_trait, name, 1.0)
        # Prevent negative or zero values by clamping
        if val is None:
            val = 1.0
        delta = val * delta_frac
        if not increase:
            new_val = max(0.01, val - delta)
        else:
            new_val = val + delta
        setattr(new_trait, name, new_val)
        return val, new_val

    # Determine actual fractional changes (allow some randomness)
    frac_inc = mutation_strength * (1.0 + (random.random() - 0.5) * 0.5)
    frac_dec = mutation_strength * (1.0 + (random.random() - 0.5) * 0.5)

    old_inc, new_inc = apply_delta(inc, frac_inc, True)
    old_dec, new_dec = apply_delta(dec, frac_dec, False)

    # Optionally sometimes only do a single-sided mutation (no tradeoff)
    if not force_tradeoff and random.random() < 0.2:
        # Revert decrease and only increase
        setattr(new_trait, dec, old_dec)
        new_dec = old_dec

    # Use Trait.mark_mutated() to normalize marker spacing
    new_trait.mark_mutated('+')

    # Update description with mutation details
    inc_stat = inc.replace('_modifier', '').capitalize()
    dec_stat = dec.replace('_modifier', '').capitalize()
    new_trait.description = (
        f"{trait.description} (Mutated: +{inc_stat} {new_inc - old_inc:.3f}, "
        f"-{dec_stat} {old_dec - new_dec:.3f})"
    )

    return new_trait
