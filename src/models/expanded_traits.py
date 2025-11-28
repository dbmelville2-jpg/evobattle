"""
Expanded trait definitions for creatures and pellets.

This module defines a comprehensive trait library with:
- Behavioral traits (timidity, aggression, curiosity)
- Physical traits (defensive adaptations, camouflage, sensory abilities)
- Ecological roles (scavenger, pollinator, parasite)
- Cross-entity interaction effects
"""

from typing import Dict, Any
from .trait import Trait
from .environmental_traits import ALL_ENVIRONMENTAL_TRAITS


# ============================================================================
# BEHAVIORAL TRAITS - Affect creature decision making and personality
# ============================================================================

TIMID_TRAIT = Trait(
    name="Timid",
    description="Avoids confrontation and flees earlier from threats",
    trait_type="behavioral",
    strength_modifier=0.9,
    speed_modifier=1.1,
    defense_modifier=1.0,
    rarity="common",
    dominance="recessive",
    interaction_effects={
        'flee_threshold': 0.6,  # Flee when HP < 60%
        'aggression_penalty': -0.3,
        # Negative trade-off: misses attacking opportunities and may be targeted when fleeing
        'reduced_engagement_time': 0.8,  # spends less time fighting/gathering
        'vulnerability_while_fleeing': 1.15,
        'scaredy_cat': True,  # New behavior: flees very easily
        'panic_speed_boost': 1.3  # Run faster when panicking
    }
)

AGGRESSIVE_TRAIT = Trait(
    name="Aggressive",
    description="Seeks out combat and fights more fiercely",
    trait_type="behavioral",
    strength_modifier=1.2,
    speed_modifier=0.95,
    defense_modifier=0.9,
    rarity="common",
    dominance="dominant",
    interaction_effects={
        'attack_bonus': 0.15,
        'flee_threshold': 0.2,  # Only flee when HP < 20%
        'target_preference': 'strongest',
        # Negative trade-off: takes more damage when overcommitting
        'reckless_exposure': True,
        'damage_taken_multiplier': 1.15
    }
)

CURIOUS_TRAIT = Trait(
    name="Curious",
    description="Explores more and discovers resources faster",
    trait_type="behavioral",
    strength_modifier=1.0,
    speed_modifier=1.05,
    defense_modifier=1.0,
    rarity="common",
    dominance="codominant",
    interaction_effects={
        'exploration_range': 1.3,
        'resource_detection': 1.25,
        # Negative trade-off: more likely to wander into danger or miss objectives
        'distraction_chance': 0.25,
        'predation_risk_multiplier': 1.2
    }
)

CAUTIOUS_TRAIT = Trait(
    name="Cautious",
    description="Careful and strategic, avoids unnecessary risks",
    trait_type="behavioral",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=1.15,
    rarity="uncommon",
    dominance="recessive",
    interaction_effects={
        'retreat_early': True,
        'pellet_selectivity': 1.2,  # More selective about food
        # Negative trade-off: misses out on some resources / opportunities
        'resource_gather_penalty': 0.85,
        'slower_engagement_rate': 0.9
    }
)

BOLD_TRAIT = Trait(
    name="Bold",
    description="Takes risks and fights to the end",
    trait_type="behavioral",
    strength_modifier=1.1,
    speed_modifier=1.05,
    defense_modifier=0.95,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'no_retreat': True,
        'critical_hit_chance': 1.2,
        # Negative trade-off: higher chance to suffer heavy damage
        'overexposure_damage_multiplier': 1.25,
        'injury_risk_increase': True
    }
)

SOCIAL_TRAIT = Trait(
    name="Social",
    description="Cooperates better with family and allies",
    trait_type="behavioral",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=1.0,
    rarity="uncommon",
    dominance="codominant",
    interaction_effects={
        'group_bonus': 1.15,
        'sharing_willingness': 0.8,
        # Negative trade-off: individual resource gain reduced
        'resource_share_penalty': 0.9,
        'vulnerability_when_group_split': 1.1,
        'pack_hunter': True,  # New behavior: bonus when near allies
        'pack_coordination': 1.2
    }
)

SOLITARY_TRAIT = Trait(
    name="Solitary",
    description="Prefers to hunt and fight alone",
    trait_type="behavioral",
    strength_modifier=1.15,
    speed_modifier=1.0,
    defense_modifier=1.05,
    rarity="uncommon",
    dominance="recessive",
    interaction_effects={
        'group_penalty': 0.9,
        'solo_bonus': 1.2,
        # Negative trade-off: lacks group support and suffers against coordinated foes
        'lack_of_support_multiplier': 0.85,
        'reduced_rescue_chance': 0.6,
        'loner_strength': True,  # New behavior: bonus when alone
        'isolation_resilience': 1.3
    }
)

# ============================================================================
# PHYSICAL TRAITS - Affect stats and physical capabilities
# ============================================================================

ARMORED_TRAIT = Trait(
    name="Armored",
    description="Thick hide provides exceptional defense",
    trait_type="physical",
    strength_modifier=0.95,
    speed_modifier=0.85,
    defense_modifier=1.4,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'damage_reduction': 0.25,
        'blunt_resistance': 1.5,
        # Negative trade-off: heavier armor increases stamina costs and reduces agility
        'stamina_drain_multiplier': 1.25,
        'reduced_maneuverability': 0.85
    }
)

SWIFT_TRAIT = Trait(
    name="Swift",
    description="Incredible speed and agility",
    trait_type="physical",
    strength_modifier=0.9,
    speed_modifier=1.5,
    defense_modifier=0.95,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'dodge_chance': 1.4,
        'first_strike': True,
        # Negative trade-off: lighter frame means less impact resistance
        'reduced_armor_effectiveness': 0.8,
        'vulnerability_to_heavy_hits': 1.2
    }
)

REGENERATIVE_TRAIT = Trait(
    name="Regenerative",
    description="Slowly heals over time",
    trait_type="physical",
    strength_modifier=0.95,
    speed_modifier=0.95,
    defense_modifier=1.1,
    rarity="rare",
    dominance="recessive",
    interaction_effects={
        'hp_regen_rate': 0.02,  # 2% HP per tick
        'recovery_speed': 1.5,
        # Negative trade-off: higher metabolic demands
        'food_requirement_multiplier': 1.3,
        'reduced_peak_performance_duration': 0.9
    }
)

VENOMOUS_TRAIT = Trait(
    name="Venomous",
    description="Attacks inflict poison damage over time",
    trait_type="physical",
    strength_modifier=1.1,
    speed_modifier=1.0,
    defense_modifier=0.95,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'poison_on_hit': 0.3,  # 30% chance
        'poison_damage': 5,
        # Negative trade-off: making/holding venom costs energy and slows growth
        'energetic_cost_multiplier': 1.2,
        'reduced_reproduction_rate': 0.85
    }
)

CAMOUFLAGED_TRAIT = Trait(
    name="Camouflaged",
    description="Blends with environment, harder to detect",
    trait_type="physical",
    strength_modifier=1.0,
    speed_modifier=1.05,
    defense_modifier=1.1,
    rarity="uncommon",
    dominance="recessive",
    interaction_effects={
        'detection_range': 0.7,  # Harder to spot
        'ambush_bonus': 1.3,
        # Negative trade-off: reduced sensing of allies and less group awareness
        'reduced_group_awareness': 0.85,
        'vulnerability_in_open_areas': 1.25
    }
)

KEEN_SENSES_TRAIT = Trait(
    name="Keen Senses",
    description="Enhanced vision and hearing detect threats and food",
    trait_type="physical",
    strength_modifier=1.0,
    speed_modifier=1.1,
    defense_modifier=1.0,
    rarity="common",
    dominance="codominant",
    interaction_effects={
        'threat_detection': 1.4,
        'food_detection': 1.5,
        'pellet_quality_sense': True,
        # Negative trade-off: can be overloaded by stimuli
        'sensory_overload_chance': 0.15,
        'stun_chance_from_loud_events': 0.1
    }
)

POWERFUL_TRAIT = Trait(
    name="Powerful",
    description="Immense physical strength",
    trait_type="physical",
    strength_modifier=1.4,
    speed_modifier=0.9,
    defense_modifier=1.05,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'critical_damage': 1.5,
        'knockback': True,
        # Negative trade-off: slower recovery and higher stamina use
        'stamina_recovery_multiplier': 0.8,
        'higher_energy_consumption': 1.3
    }
)

# ============================================================================
# LETHAL COMBAT TRAITS - High-risk, high-reward combat traits
# ============================================================================

BERSERKER_TRAIT = Trait(
    name="Berserker",
    description="Rages when wounded, trading defense for pure carnage",
    trait_type="offensive",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=0.7,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'attack_bonus_below_30_hp': 1.0,  # +100% attack when below 30% HP
        'cannot_retreat': True,
        'rage_threshold': 0.3,
        # Negative trade-off: takes extra damage while berserk
        'damage_taken_while_raging_multiplier': 1.4
    }
)

EXECUTIONER_TRAIT = Trait(
    name="Executioner",
    description="Finishes the weak with ruthless efficiency",
    trait_type="offensive",
    strength_modifier=1.1,
    speed_modifier=1.0,
    defense_modifier=1.0,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'execute_bonus': 1.5,  # +150% damage to targets below 40% HP
        'execute_threshold': 0.4,
        'immune_to_fear': True,
        # Negative trade-off: focused execution style slows recovery between fights
        'post_execute_recovery_penalty': 0.8
    }
)

BLOODTHIRSTY_TRAIT = Trait(
    name="Bloodthirsty",
    description="Damage increases with each kill in battle",
    trait_type="offensive",
    strength_modifier=1.05,
    speed_modifier=1.05,
    defense_modifier=0.95,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'damage_per_kill': 0.15,  # +15% damage per kill
        'max_kill_stacks': 5,
        'resets_on_battle_end': True,
        'targets_injured': True,
        # Negative trade-off: bloodlust reduces carefulness, increasing incoming damage
        'increased_incoming_damage_per_stack': 0.05
    }
)

BRUTAL_TRAIT = Trait(
    name="Brutal",
    description="Ignores armor and causes bleeding wounds",
    trait_type="offensive",
    strength_modifier=1.5,
    speed_modifier=0.95,
    defense_modifier=0.95,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'armor_penetration': 0.5,  # Ignores 50% of target's armor/defense
        'bleed_on_hit': True,
        'bleed_damage': 3,  # Damage over time
        # Negative trade-off: heavy-hitting attacks are slower and easier to avoid
        'attack_speed_penalty': 0.85,
        'predictable_strike_pattern': True
    }
)

ASSASSIN_TRAIT = Trait(
    name="Assassin",
    description="Deadly from the shadows, vulnerable when exposed",
    trait_type="offensive",
    strength_modifier=1.1,
    speed_modifier=1.2,
    defense_modifier=0.7,
    rarity="rare",
    dominance="recessive",
    interaction_effects={
        'ambush_damage': 2.0,  # +200% damage on first strike/ambush
        'counter_vulnerability': 2.0,  # Receives double damage if counter-attacked
        'stealth_movement': True,
        'first_strike': True,
        # Negative trade-off: exposed assassins suffer morale penalties when revealed
        'reveal_penalty_duration': 3,
        'reduced_effectiveness_in_group_fight': 0.7,
        'ambush_predator': True,  # New behavior: bonus on first hit
        'stealth_regen': 1.5  # Regenerate energy faster while hidden
    }
)

APEX_PREDATOR_TRAIT = Trait(
    name="Apex Predator",
    description="Grows stronger with each unique kill, inspiring fear",
    trait_type="offensive",
    strength_modifier=1.1,
    speed_modifier=1.1,
    defense_modifier=1.05,
    rarity="legendary",
    dominance="dominant",
    interaction_effects={
        'stats_per_unique_kill': 0.2,  # +20% stats per unique strain killed
        'fear_aura': True,
        'fear_radius': 50.0,
        'prey_tracking': True,
        # Negative trade-off: high energy demands and reduced reproduction
        'energy_drain_per_kill': 1.2,
        'reduced_reproductive_success': 0.7
    }
)

RECKLESS_FURY_TRAIT = Trait(
    name="Reckless Fury",
    description="Overwhelming offense at the cost of safety",
    trait_type="offensive",
    strength_modifier=1.6,
    speed_modifier=1.1,
    defense_modifier=0.5,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'self_damage_chance': 0.2,  # 20% chance to hurt self on each attack
        'self_damage_amount': 5,
        'cannot_block': True,
        'cannot_parry': True,
        # Negative trade-off: long recovery and high injury likelihood
        'post_combat_debuff_duration': 5,
        'long_term_injury_risk': 0.2
    }
)

TOXIC_TRAIT = Trait(
    name="Toxic",
    description="All attacks inflict stacking poison",
    trait_type="offensive",
    strength_modifier=1.1,
    speed_modifier=1.0,
    defense_modifier=0.9,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'poison_on_hit': 1.0,  # 100% chance to poison
        'poison_damage': 2,  # Damage per tick
        'poison_stacks': 5,  # Max stacks
        'healing_reduction': 0.3,  # Reduced healing received
        # Negative trade-off: poison production can contaminate allies or self
        'friendly_fire_poison_risk': True,
        'detox_energy_cost_multiplier': 1.2
    }
)

FRENZIED_TRAIT = Trait(
    name="Frenzied",
    description="Attacks in rapid succession, forsaking defense",
    trait_type="offensive",
    strength_modifier=1.1,
    speed_modifier=2.5,
    defense_modifier=0.8,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'multi_strike': 3,  # Up to 3 attacks per turn
        'attack_speed_multiplier': 2.5,
        'cannot_use_defensive_abilities': True,
        # Negative trade-off: exhaustion after frenzied activity
        'post_frenzy_exhaustion_multiplier': 0.6,
        'increased_miss_chance_when_exhausted': 0.15
    }
)

VAMPIRIC_TRAIT = Trait(
    name="Vampiric",
    description="Drains life from enemies, converting damage to health",
    trait_type="offensive",
    strength_modifier=1.1,
    speed_modifier=0.95,
    defense_modifier=0.95,
    rarity="rare",
    dominance="recessive",
    interaction_effects={
        'lifesteal': 0.5,  # Heals for 50% of damage dealt
        'overheal_shield': True,
        'overheal_max': 0.3,  # Can overheal up to 30% max HP as shield
        # Negative trade-off: less effective against non-living or shielded targets
        'ineffective_against_shields': True,
        'recovery_dependency_on_damage_dealt': True
    }
)

# ============================================================================
# ECOLOGICAL TRAITS - Affect interactions with environment and other entities
# ============================================================================

SCAVENGER_TRAIT = Trait(
    name="Scavenger",
    description="Prefers eating corpses, gains more nutrition from them",
    trait_type="ecological",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=1.0,
    rarity="uncommon",
    dominance="recessive",
    interaction_effects={
        'corpse_nutrition_bonus': 1.5,
        'corpse_preference': True,
        'toxin_resistance': 1.3,
        # Negative trade-off: higher disease/toxin exposure risk
        'disease_risk_multiplier': 1.6,
        'lower_social_acceptance': 0.8
    }
)

POLLINATOR_TRAIT = Trait(
    name="Pollinator",
    description="Helps pellets reproduce when feeding",
    trait_type="ecological",
    strength_modifier=0.95,
    speed_modifier=1.05,
    defense_modifier=1.0,
    rarity="rare",
    dominance="codominant",
    interaction_effects={
        'pellet_reproduction_boost': 1.4,
        'symbiotic_bonus': True,
        'plant_pellet_preference': True,
        # Negative trade-off: spends more time feeding and is less mobile
        'movement_penalty_while_pollinating': 0.8,
        'exposure_to_predators_while_pollinating': 1.25
    }
)

PARASITE_TRAIT = Trait(
    name="Parasitic",
    description="Drains life from opponents over time",
    trait_type="ecological",
    strength_modifier=0.95,
    speed_modifier=1.0,
    defense_modifier=0.9,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'lifesteal': 0.15,  # Steal 15% of damage as HP
        'attach_on_hit': 0.2,  # 20% chance to attach
        # Negative trade-off: heavy dependence on a host and vulnerability if detached
        'host_dependency': True,
        'vulnerability_when_detached_multiplier': 1.4
    }
)

SYMBIOTIC_TRAIT = Trait(
    name="Symbiotic",
    description="Benefits from proximity to certain pellets",
    trait_type="ecological",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=1.05,
    rarity="rare",
    dominance="codominant",
    interaction_effects={
        'pellet_aura_bonus': 1.2,
        'beneficial_pellets': True,
        'mutual_benefit': True,
        # Negative trade-off: dependence on specific pellet types reduces flexibility
        'dependence_penalty_if_pellet_absent': 0.75,
        'reduced_survivability_in_barren_areas': 0.8
    }
)

PREDATOR_TRAIT = Trait(
    name="Predator",
    description="Hunts other creatures more effectively",
    trait_type="ecological",
    strength_modifier=1.2,
    speed_modifier=1.1,
    defense_modifier=0.95,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'hunt_bonus': 1.3,
        'carnivore': True,
        'track_prey': True,
        # Negative trade-off: more visible/tracked by other predators and human-like forces
        'higher_visibility_multiplier': 1.15,
        'increased_energy_needs': 1.2
    }
)

HERBIVORE_TRAIT = Trait(
    name="Herbivore",
    description="Specialized for plant consumption, cannot eat meat",
    trait_type="ecological",
    strength_modifier=0.95,
    speed_modifier=1.0,
    defense_modifier=1.1,
    rarity="common",
    dominance="recessive",
    interaction_effects={
        'plant_nutrition_bonus': 1.4,
        'cannot_eat_meat': True,
        'plant_pellet_detection': 1.5,
        # Negative trade-off: more attractive to predators and limited diet flexibility
        'predator_targeting_multiplier': 1.25,
        'reduced_diet_flexibility': 0.8
    }
)

OMNIVORE_TRAIT = Trait(
    name="Omnivore",
    description="Can eat both plants and meat efficiently",
    trait_type="ecological",
    strength_modifier=1.05,
    speed_modifier=1.05,
    defense_modifier=1.0,
    rarity="common",
    dominance="codominant",
    interaction_effects={
        'varied_diet_bonus': 1.2,
        'nutrition_efficiency': 1.15,
        # Negative trade-off: less specialized efficiency compared to specialists
        'specialist_efficiency_penalty': 0.95
    }
)

TOXIN_RESISTANT_TRAIT = Trait(
    name="Toxin Resistant",
    description="Reduced damage from toxic food and poisons",
    trait_type="ecological",
    strength_modifier=1.0,
    speed_modifier=0.95,
    defense_modifier=1.15,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'toxin_damage_reduction': 0.6,  # 40% less damage
        'can_eat_toxic': True,
        # Negative trade-off: metabolic cost for maintaining resistance
        'metabolic_cost_multiplier': 1.15,
        'slower_growth_in_clean_environments': 0.9
    }
)

NOCTURNAL_TRAIT = Trait(
    name="Nocturnal",
    description="Active at night, rests during the day",
    trait_type="behavioral",
    strength_modifier=1.05,
    speed_modifier=1.1,
    defense_modifier=1.0,
    rarity="common",
    dominance="codominant",
    interaction_effects={
        'night_vision': True,
        'day_sluggishness': 0.8,
        'night_activity_bonus': 1.2,
        'circadian_rhythm': 'nocturnal'
    }
)

DIURNAL_TRAIT = Trait(
    name="Diurnal",
    description="Active during the day, rests at night",
    trait_type="behavioral",
    strength_modifier=1.05,
    speed_modifier=1.0,
    defense_modifier=1.05,
    rarity="common",
    dominance="codominant",
    interaction_effects={
        'sunlight_affinity': True,
        'night_fear': True,
        'day_activity_bonus': 1.2,
    }
)

# ============================================================================
# IMMUNITY TRAITS - Disease resistance and recovery
# ============================================================================

ROBUST_IMMUNE_TRAIT = Trait(
    name="Robust Immunity",
    description="Strong immune system resists infection",
    trait_type="physical",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=1.0,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'base_immunity_bonus': 0.25,  # +25% base immunity
        'disease_resistance': 1.25,
        # Negative trade-off: high metabolic cost
        'energy_cost_multiplier': 1.1
    }
)

FAST_RECOVERY_TRAIT = Trait(
    name="Fast Recovery",
    description="Recovers from diseases and injuries quickly",
    trait_type="physical",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=1.0,
    rarity="uncommon",
    dominance="recessive",
    interaction_effects={
        'disease_duration_multiplier': 0.7,  # 30% shorter diseases
        'recovery_speed': 1.3,
        # Negative trade-off: requires more food during recovery
        'hunger_rate_while_sick': 1.4
    }
)

CARRIER_TRAIT = Trait(
    name="Asymptomatic Carrier",
    description="Carries diseases without suffering severe symptoms",
    trait_type="physical",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=1.0,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'symptom_suppression': 0.8,  # 80% reduction in symptoms (HP drain/stats)
        'transmission_boost': 1.5,   # Spreads disease more effectively
        'incubation_extension': 2.0, # Stays in incubating stage longer
        # Negative trade-off: social stigma (if detected) and constant energy drain
        'social_distancing_penalty': 0.5,
        'chronic_energy_drain': 0.5
    }
)

# ============================================================================
# PELLET-SPECIFIC TRAITS - New traits for pellet evolution
# ============================================================================

class PelletTrait:
    """
    Trait specific to pellets (food sources).
    Similar to creature Trait but with pellet-specific effects.
    """
    def __init__(
        self,
        name: str,
        description: str,
        trait_type: str,
        nutritional_modifier: float = 1.0,
        growth_modifier: float = 1.0,
        toxicity_modifier: float = 1.0,
        palatability_modifier: float = 1.0,
        rarity: str = "common",
        dominance: str = "codominant",
        interaction_effects: Dict[str, Any] = None
    ):
        self.name = name
        self.description = description
        self.trait_type = trait_type
        self.nutritional_modifier = nutritional_modifier
        self.growth_modifier = growth_modifier
        self.toxicity_modifier = toxicity_modifier
        self.palatability_modifier = palatability_modifier
        self.rarity = rarity
        self.dominance = dominance
        self.interaction_effects = interaction_effects if interaction_effects else {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'trait_type': self.trait_type,
            'nutritional_modifier': self.nutritional_modifier,
            'growth_modifier': self.growth_modifier,
            'toxicity_modifier': self.toxicity_modifier,
            'palatability_modifier': self.palatability_modifier,
            'rarity': self.rarity,
            'dominance': self.dominance,
            'interaction_effects': self.interaction_effects
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PelletTrait':
        """Deserialize from dictionary."""
        return PelletTrait(
            name=data.get('name', 'Basic Pellet Trait'),
            description=data.get('description', ''),
            trait_type=data.get('trait_type', 'neutral'),
            nutritional_modifier=data.get('nutritional_modifier', 1.0),
            growth_modifier=data.get('growth_modifier', 1.0),
            toxicity_modifier=data.get('toxicity_modifier', 1.0),
            palatability_modifier=data.get('palatability_modifier', 1.0),
            rarity=data.get('rarity', 'common'),
            dominance=data.get('dominance', 'codominant'),
            interaction_effects=data.get('interaction_effects', {})
        )


# Pellet trait definitions
NUTRITIOUS_PELLET_TRAIT = PelletTrait(
    name="Highly Nutritious",
    description="Provides exceptional energy to consumers",
    trait_type="beneficial",
    nutritional_modifier=1.5,
    palatability_modifier=1.2,
    rarity="uncommon",
    dominance="recessive"
)

TOXIC_DEFENSE_PELLET_TRAIT = PelletTrait(
    name="Toxic Defense",
    description="Contains toxins that harm creatures without resistance",
    trait_type="defensive",
    toxicity_modifier=2.0,
    palatability_modifier=0.5,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'damage_on_consumption': 10,
        'discourages_predation': True,
        # Negative trade-off: attracts specialized scavengers and decomposers
        'attracts_detritivores': True,
        'reduced_spread_by_consumers': 0.85
    }
)

FAST_GROWING_PELLET_TRAIT = PelletTrait(
    name="Fast Growing",
    description="Reproduces more quickly",
    trait_type="reproductive",
    growth_modifier=1.8,
    nutritional_modifier=0.9,
    rarity="common",
    dominance="dominant",
    interaction_effects={
        # Negative trade-off: lower per-item nutrition due to rapid growth
        'lower_nutrition_per_unit': 0.9
    }
)

ATTRACTIVE_PELLET_TRAIT = PelletTrait(
    name="Attractive",
    description="Highly palatable and sought after by creatures",
    trait_type="beneficial",
    palatability_modifier=1.6,
    rarity="uncommon",
    dominance="codominant",
    interaction_effects={
        'attract_creatures': True,
        'preferred_food': True,
        # Negative trade-off: high predation pressure
        'higher_predation_pressure': 1.4
    }
)

REPELLENT_PELLET_TRAIT = PelletTrait(
    name="Repellent",
    description="Emits chemicals that discourage consumption",
    trait_type="defensive",
    palatability_modifier=0.3,
    toxicity_modifier=1.2,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'repel_creatures': True,
        'avoid_radius': 5.0,
        # Negative trade-off: slower spread and fewer dispersers
        'reduced_dispersal_rate': 0.7
    }
)

MEDICINAL_PELLET_TRAIT = PelletTrait(
    name="Medicinal",
    description="Heals creatures that consume it",
    trait_type="beneficial",
    nutritional_modifier=1.1,
    palatability_modifier=0.8,
    rarity="rare",
    dominance="recessive",
    interaction_effects={
        'heal_on_consumption': 15,
        'cure_poison': True,
        # Negative trade-off: slower reproduction due to energy invested in medicinal compounds
        'reduced_reproduction_rate': 0.8
    }
)

SYMBIOTIC_PELLET_TRAIT = PelletTrait(
    name="Symbiotic",
    description="Benefits from creature proximity, grows near them",
    trait_type="ecological",
    growth_modifier=1.3,
    rarity="rare",
    dominance="codominant",
    interaction_effects={
        'creature_proximity_bonus': 1.4,
        'mutual_benefit': True,
        # Negative trade-off: vulnerable if creatures leave the area
        'decline_if_creatures_absent': 0.6
    }
)

HARDY_PELLET_TRAIT = PelletTrait(
    name="Hardy",
    description="Survives longer and in harsh conditions",
    trait_type="survival",
    growth_modifier=0.9,
    nutritional_modifier=1.1,
    rarity="common",
    dominance="recessive",
    interaction_effects={
        'lifespan_multiplier': 2.0,
        'environmental_resistance': True,
        # Negative trade-off: slower reproduction or spread
        'reduced_spread_rate': 0.7
    }
)

# ============================================================================
# TRAIT COLLECTIONS
# ============================================================================

# All creature traits
ALL_CREATURE_TRAITS = [
    # Behavioral
    TIMID_TRAIT, AGGRESSIVE_TRAIT, CURIOUS_TRAIT, CAUTIOUS_TRAIT, BOLD_TRAIT,
    SOCIAL_TRAIT, SOLITARY_TRAIT,
    # Physical
    ARMORED_TRAIT, SWIFT_TRAIT, REGENERATIVE_TRAIT, VENOMOUS_TRAIT,
    CAMOUFLAGED_TRAIT, KEEN_SENSES_TRAIT, POWERFUL_TRAIT,
    # Lethal Combat
    BERSERKER_TRAIT, EXECUTIONER_TRAIT, BLOODTHIRSTY_TRAIT, BRUTAL_TRAIT,
    ASSASSIN_TRAIT, APEX_PREDATOR_TRAIT, RECKLESS_FURY_TRAIT, TOXIC_TRAIT,
    FRENZIED_TRAIT, VAMPIRIC_TRAIT,
    # Ecological
    SCAVENGER_TRAIT, POLLINATOR_TRAIT, PARASITE_TRAIT, SYMBIOTIC_TRAIT,
    PREDATOR_TRAIT, HERBIVORE_TRAIT, OMNIVORE_TRAIT, TOXIN_RESISTANT_TRAIT
] + list(ALL_ENVIRONMENTAL_TRAITS)

# All pellet traits
ALL_PELLET_TRAITS = [
    NUTRITIOUS_PELLET_TRAIT, TOXIC_DEFENSE_PELLET_TRAIT, FAST_GROWING_PELLET_TRAIT,
    ATTRACTIVE_PELLET_TRAIT, REPELLENT_PELLET_TRAIT, MEDICINAL_PELLET_TRAIT,
    SYMBIOTIC_PELLET_TRAIT, HARDY_PELLET_TRAIT
]

# Traits by category
BEHAVIORAL_TRAITS = [TIMID_TRAIT, AGGRESSIVE_TRAIT, CURIOUS_TRAIT, CAUTIOUS_TRAIT, BOLD_TRAIT, SOCIAL_TRAIT, SOLITARY_TRAIT]
PHYSICAL_TRAITS = [ARMORED_TRAIT, SWIFT_TRAIT, REGENERATIVE_TRAIT, VENOMOUS_TRAIT, CAMOUFLAGED_TRAIT, KEEN_SENSES_TRAIT, POWERFUL_TRAIT]
LETHAL_COMBAT_TRAITS = [BERSERKER_TRAIT, EXECUTIONER_TRAIT, BLOODTHIRSTY_TRAIT, BRUTAL_TRAIT, ASSASSIN_TRAIT, APEX_PREDATOR_TRAIT, RECKLESS_FURY_TRAIT, TOXIC_TRAIT, FRENZIED_TRAIT, VAMPIRIC_TRAIT]
ECOLOGICAL_TRAITS = [SCAVENGER_TRAIT, POLLINATOR_TRAIT, PARASITE_TRAIT, SYMBIOTIC_TRAIT, PREDATOR_TRAIT, HERBIVORE_TRAIT, OMNIVORE_TRAIT, TOXIN_RESISTANT_TRAIT]

# Traits by dominance
DOMINANT_TRAITS = [t for t in ALL_CREATURE_TRAITS if t.dominance == "dominant"]
RECESSIVE_TRAITS = [t for t in ALL_CREATURE_TRAITS if t.dominance == "recessive"]
CODOMINANT_TRAITS = [t for t in ALL_CREATURE_TRAITS if t.dominance == "codominant"]
