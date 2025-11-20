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
    rarity="uncommon",
    interaction_effects={
        'hunger_depletion_multiplier': 0.6,
        # Negative trade-off: slower peak performance/recovery
        'reduced_peak_performance_duration': 0.9,
        'slower_recovery_from_exertion': True
    }
)

EFFICIENT = Trait(
    name="Efficient",
    description="Uses resources wisely, reducing hunger depletion by 30%",
    trait_type="metabolic",
    rarity="common",
    interaction_effects={
        'hunger_depletion_multiplier': 0.7,
        # Negative trade-off: less explosive energy (lower short-burst output)
        'reduced_burst_output_multiplier': 0.9
    }
)

GLUTTON = Trait(
    name="Glutton",
    description="Burns energy quickly (50% faster hunger), but gains HP bonus when eating",
    trait_type="metabolic",
    strength_modifier=1.1,  # Slight strength boost
    rarity="common",
    interaction_effects={
        'hunger_depletion_multiplier': 1.5,
        'hp_on_eat_bonus_multiplier': 1.0,
        # Negative trade-off: easier to starve and lower endurance
        'starvation_risk_multiplier': 1.4
    }
)

VORACIOUS = Trait(
    name="Voracious",
    description="Ravenous appetite (40% faster hunger), heals more when eating",
    trait_type="metabolic",
    strength_modifier=1.15,
    rarity="uncommon",
    interaction_effects={
        'hunger_depletion_multiplier': 1.4,
        'hp_on_eat_bonus_multiplier': 1.2,
        # Negative trade-off: noisy foraging attracts predators
        'predator_attraction_multiplier': 1.2
    }
)


# ===========================
# BEHAVIORAL TRAITS
# ===========================

FORAGER = Trait(
    name="Forager",
    description="Naturally seeks out and collects resources",
    trait_type="behavioral",
    speed_modifier=1.05,  # Slightly faster for finding food
    rarity="common",
    interaction_effects={
        'resource_detection_multiplier': 1.15,
        # Negative trade-off: more time spent foraging vs other tasks
        'reduced_combat_readiness_multiplier': 0.9
    }
)

GATHERER = Trait(
    name="Gatherer",
    description="Expert at finding and collecting resources",
    trait_type="behavioral",
    speed_modifier=1.1,
    rarity="uncommon",
    interaction_effects={
        'resource_yield_multiplier': 1.25,
        # Negative trade-off: predictable routes make ambush more likely
        'ambush_vulnerability_multiplier': 1.15
    }
)

SCAVENGER = Trait(
    name="Scavenger",
    description="Skilled at finding food in harsh conditions",
    trait_type="behavioral",
    defense_modifier=1.05,  # Hardy scavenger
    rarity="common",
    interaction_effects={
        'corpse_nutrition_bonus': 1.3,
        # Negative trade-off: higher disease/toxin risk
        'disease_risk_multiplier': 1.5,
        'lower_social_acceptance': 0.85
    }
)


# ===========================
# PERSONALITY TRAITS
# ===========================

CURIOUS = Trait(
    name="Curious",
    description="Explores widely, wanders more frequently",
    trait_type="personality",
    speed_modifier=1.1,
    rarity="common",
    interaction_effects={
        'exploration_tendency': 1.2,
        # Negative trade-off: distraction and predation risk
        'distraction_chance': 0.2,
        'predation_risk_multiplier': 1.15
    }
)

LAZY = Trait(
    name="Lazy",
    description="Prefers to stay put, minimal movement",
    trait_type="personality",
    speed_modifier=0.9,
    defense_modifier=1.05,  # Conserves energy
    rarity="common",
    interaction_effects={
        'energy_saving_multiplier': 0.85,
        # Negative trade-off: lower resource discovery
        'resource_detection_penalty': 0.85
    }
)

CAUTIOUS = Trait(
    name="Cautious",
    description="Avoids danger and makes careful decisions",
    trait_type="personality",
    defense_modifier=1.1,
    rarity="common",
    interaction_effects={
        'retreat_threshold_modifier': 1.15,
        # Negative trade-off: slower decision-making and missed opportunities
        'engagement_rate_multiplier': 0.9
    }
)

AGGRESSIVE = Trait(
    name="Aggressive",
    description="Attacks first, seeks combat",
    trait_type="personality",
    strength_modifier=1.15,
    defense_modifier=0.95,
    rarity="common",
    interaction_effects={
        'attack_initiation_bonus': 1.15,
        # Negative trade-off: takes more damage when overcommitting
        'damage_taken_multiplier': 1.12
    }
)

WANDERER = Trait(
    name="Wanderer",
    description="Constantly explores and moves around",
    trait_type="personality",
    speed_modifier=1.15,
    rarity="uncommon",
    interaction_effects={
        'movement_frequency_multiplier': 1.25,
        # Negative trade-off: less likely to defend territory/resources
        'territory_defense_penalty': 0.85
    }
)

EXPLORER = Trait(
    name="Explorer",
    description="Driven to discover new areas",
    trait_type="personality",
    speed_modifier=1.2,
    rarity="rare",
    interaction_effects={
        'discovery_bonus': 1.4,
        # Negative trade-off: increased exposure to unknown hazards
        'unknown_hazard_risk_multiplier': 1.3
    }
)

PERSISTENT = Trait(
    name="Persistent",
    description="Sticks with tasks longer, less easily distracted",
    trait_type="personality",
    defense_modifier=1.05,  # Patience provides resilience
    rarity="common",
    interaction_effects={
        'task_completion_bonus': 1.15,
        # Negative trade-off: slower to adapt to new opportunities
        'adaptability_penalty': 0.9
    }
)

DISTRACTIBLE = Trait(
    name="Distractible",
    description="Easily distracted, switches focus frequently",
    trait_type="personality",
    speed_modifier=1.05,  # Quick to react
    defense_modifier=0.95,  # Less focused defense
    rarity="common",
    interaction_effects={
        'reactivity_bonus': 1.1,
        # Negative trade-off: poor sustained performance
        'sustained_performance_penalty': 0.85
    }
)

TUNNEL_VISION = Trait(
    name="Tunnel Vision",
    description="Extremely focused on current task, ignores distractions",
    trait_type="personality",
    strength_modifier=1.1,  # Single-minded determination
    defense_modifier=0.9,  # Vulnerable to flanking
    rarity="uncommon",
    interaction_effects={
        'focus_bonus': 1.2,
        # Negative trade-off: vulnerability to unexpected threats
        'flanking_vulnerability_multiplier': 1.25
    }
)

OPPORTUNIST = Trait(
    name="Opportunist",
    description="Quickly switches to better opportunities, adaptable",
    trait_type="personality",
    speed_modifier=1.1,
    rarity="uncommon",
    interaction_effects={
        'opportunity_gain_multiplier': 1.15,
        # Negative trade-off: unreliable commitments reduce cooperation
        'cooperation_penalty': 0.85
    }
)

FOCUSED = Trait(
    name="Focused",
    description="Maintains concentration, resistant to distractions",
    trait_type="personality",
    strength_modifier=1.05,
    defense_modifier=1.05,
    rarity="uncommon",
    interaction_effects={
        'concentration_bonus': 1.1,
        # Negative trade-off: reduced situational awareness
        'situational_awareness_penalty': 0.9
    }
)

FICKLE = Trait(
    name="Fickle",
    description="Changes mind frequently, unreliable commitments",
    trait_type="personality",
    speed_modifier=1.08,
    strength_modifier=0.95,
    rarity="common",
    interaction_effects={
        'flexibility_bonus': 1.1,
        # Negative trade-off: poor reliability in cooperative tasks
        'reliability_penalty': 0.75
    }
)


# ===========================
# SURVIVAL TRAITS
# ===========================

HARDY = Trait(
    name="Hardy",
    description="Tough and resilient, survives harsh conditions",
    trait_type="survival",
    defense_modifier=1.2,
    rarity="uncommon",
    interaction_effects={
        'environmental_resistance_multiplier': 1.5,
        # Negative trade-off: slower reproduction or growth
        'growth_rate_penalty': 0.85
    }
)

FRAIL = Trait(
    name="Frail",
    description="Weak constitution, more vulnerable",
    trait_type="survival",
    defense_modifier=0.8,
    strength_modifier=0.9,
    rarity="common",
    interaction_effects={
        'vulnerability_multiplier': 1.3,
        # Negative trade-off already inherent; small speed bonus for being lightweight
        'speed_bonus_if_frail': 1.05
    }
)


# ===========================
# DIETARY TRAITS
# ===========================

HERBIVORE = Trait(
    name="Herbivore",
    description="Only eats plant resources, cannot consume other creatures",
    trait_type="dietary",
    rarity="common",
    interaction_effects={
        'plant_nutrition_preference': True,
        # Negative trade-off: cannot eat meat reduces food options
        'dietary_flexibility_penalty': 0.7
    }
)

CARNIVORE = Trait(
    name="Carnivore",
    description="Only eats other creatures, cannot eat plant resources",
    trait_type="dietary",
    strength_modifier=1.2,  # 20% attack bonus
    rarity="uncommon",
    interaction_effects={
        'meat_nutrition_bonus': 1.25,
        # Negative trade-off: vulnerable if prey scarce
        'starvation_risk_when_prey_scarce': 1.4
    }
)

OMNIVORE = Trait(
    name="Omnivore",
    description="Can eat both plants and meat",
    trait_type="dietary",
    rarity="common",
    interaction_effects={
        'dietary_flexibility_bonus': True,
        # Negative trade-off: slightly less efficient than specialists
        'specialist_efficiency_penalty': 0.95
    }
)

PICKY_EATER = Trait(
    name="Picky Eater",
    description="Only eats high-quality food (palatability >0.6, toxicity <0.2), gets bonus nutrition from quality food, risks starvation if food scarce",
    trait_type="dietary",
    defense_modifier=0.95,  # Slightly weaker due to pickiness
    rarity="uncommon",
    interaction_effects={
        'quality_food_bonus_multiplier': 1.2,
        # Negative trade-off: refusal to eat low-quality food when not desperate
        'starvation_risk_if_low_quality': 1.5
    }
)

INDISCRIMINATE_EATER = Trait(
    name="Indiscriminate Eater",
    description="Eats any food (ignores palatability/toxicity), takes less toxicity damage, but has faster hunger depletion",
    trait_type="dietary",
    defense_modifier=1.05,  # Hardy constitution
    rarity="uncommon",
    interaction_effects={
        'toxicity_resistance_multiplier': 0.5,
        'hunger_depletion_multiplier': 1.3,
        # Negative trade-off: faster hunger depletion
        'increased_food_requirements': True
    }
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
    EXPLORER,
    PERSISTENT,
    DISTRACTIBLE,
    TUNNEL_VISION,
    OPPORTUNIST,
    FOCUSED,
    FICKLE
]

SURVIVAL_TRAITS = [
    HARDY,
    FRAIL
]

DIETARY_TRAITS = [
    HERBIVORE,
    CARNIVORE,
    OMNIVORE,
    PICKY_EATER,
    INDISCRIMINATE_EATER
]

ALL_ECOSYSTEM_TRAITS = (
    METABOLIC_TRAITS +
    BEHAVIORAL_TRAITS +
    PERSONALITY_TRAITS +
    SURVIVAL_TRAITS +
    DIETARY_TRAITS
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


def get_random_dietary_trait():
    """Get a random dietary trait."""
    import random
    return random.choice(DIETARY_TRAITS)
