"""
Predefined metabolic and personality traits for the ecosystem survival system.

These traits affect hunger depletion, foraging behavior, and movement patterns.
"""

from .trait import Trait


# ===========================
# METABOLIC TRAITS
# ===========================

EFFICIENT_METABOLISM = Trait(
    name="Efficient Metabolism",
    description="Burns energy slowly, reducing hunger depletion by 40%",
    trait_type="metabolic",
    rarity="uncommon"
)

EFFICIENT = Trait(
    name="Efficient",
    description="Uses resources wisely, reducing hunger depletion by 30%",
    trait_type="metabolic",
    rarity="common"
)

GLUTTON = Trait(
    name="Glutton",
    description="Burns energy quickly (50% faster hunger), but gains HP bonus when eating",
    trait_type="metabolic",
    strength_modifier=1.1,  # Slight strength boost
    rarity="common"
)

VORACIOUS = Trait(
    name="Voracious",
    description="Ravenous appetite (40% faster hunger), heals more when eating",
    trait_type="metabolic",
    strength_modifier=1.15,
    rarity="uncommon"
)


# ===========================
# BEHAVIORAL TRAITS
# ===========================

FORAGER = Trait(
    name="Forager",
    description="Naturally seeks out and collects resources",
    trait_type="behavioral",
    speed_modifier=1.05,  # Slightly faster for finding food
    rarity="common"
)

GATHERER = Trait(
    name="Gatherer",
    description="Expert at finding and collecting resources",
    trait_type="behavioral",
    speed_modifier=1.1,
    rarity="uncommon"
)

SCAVENGER = Trait(
    name="Scavenger",
    description="Skilled at finding food in harsh conditions",
    trait_type="behavioral",
    defense_modifier=1.05,  # Hardy scavenger
    rarity="common"
)


# ===========================
# PERSONALITY TRAITS
# ===========================

CURIOUS = Trait(
    name="Curious",
    description="Explores widely, wanders more frequently",
    trait_type="personality",
    speed_modifier=1.1,
    rarity="common"
)

LAZY = Trait(
    name="Lazy",
    description="Prefers to stay put, minimal movement",
    trait_type="personality",
    speed_modifier=0.9,
    defense_modifier=1.05,  # Conserves energy
    rarity="common"
)

CAUTIOUS = Trait(
    name="Cautious",
    description="Avoids danger and makes careful decisions",
    trait_type="personality",
    defense_modifier=1.1,
    rarity="common"
)

AGGRESSIVE = Trait(
    name="Aggressive",
    description="Attacks first, seeks combat",
    trait_type="personality",
    strength_modifier=1.15,
    defense_modifier=0.95,
    rarity="common"
)

WANDERER = Trait(
    name="Wanderer",
    description="Constantly explores and moves around",
    trait_type="personality",
    speed_modifier=1.15,
    rarity="uncommon"
)

EXPLORER = Trait(
    name="Explorer",
    description="Driven to discover new areas",
    trait_type="personality",
    speed_modifier=1.2,
    rarity="rare"
)


# ===========================
# SURVIVAL TRAITS
# ===========================

HARDY = Trait(
    name="Hardy",
    description="Tough and resilient, survives harsh conditions",
    trait_type="survival",
    defense_modifier=1.2,
    rarity="uncommon"
)

FRAIL = Trait(
    name="Frail",
    description="Weak constitution, more vulnerable",
    trait_type="survival",
    defense_modifier=0.8,
    strength_modifier=0.9,
    rarity="common"
)


# ===========================
# TRAIT COLLECTIONS
# ===========================

METABOLIC_TRAITS = [
    EFFICIENT_METABOLISM,
    EFFICIENT,
    GLUTTON,
    VORACIOUS
]

BEHAVIORAL_TRAITS = [
    FORAGER,
    GATHERER,
    SCAVENGER
]

PERSONALITY_TRAITS = [
    CURIOUS,
    LAZY,
    CAUTIOUS,
    AGGRESSIVE,
    WANDERER,
    EXPLORER
]

SURVIVAL_TRAITS = [
    HARDY,
    FRAIL
]

ALL_ECOSYSTEM_TRAITS = (
    METABOLIC_TRAITS +
    BEHAVIORAL_TRAITS +
    PERSONALITY_TRAITS +
    SURVIVAL_TRAITS
)


def get_trait_by_name(name: str) -> Trait:
    """
    Get a predefined trait by name.
    
    Args:
        name: Name of the trait
        
    Returns:
        The trait if found, or a basic trait if not found
    """
    for trait in ALL_ECOSYSTEM_TRAITS:
        if trait.name.lower() == name.lower():
            return trait
    
    # Return a basic trait if not found
    return Trait(name=name, description=f"Custom trait: {name}")


def get_random_metabolic_trait():
    """Get a random metabolic trait."""
    import random
    return random.choice(METABOLIC_TRAITS)


def get_random_behavioral_trait():
    """Get a random behavioral trait."""
    import random
    return random.choice(BEHAVIORAL_TRAITS)


def get_random_personality_trait():
    """Get a random personality trait."""
    import random
    return random.choice(PERSONALITY_TRAITS)
