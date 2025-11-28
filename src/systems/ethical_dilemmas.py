"""
Ethical Dilemmas System - Research Ethics Choices

This module implements the moral choice system from Black & White, translated
into research ethics. Players face dilemmas during gameplay and must make
choices that affect their research approach and the simulation.

Key Features:
- Present ethical dilemmas with multiple choices
- Each choice has clear ethics impacts
- Dilemmas trigger based on simulation events
- Track dilemma history and player tendencies
"""

from dataclasses import dataclass
from typing import List, Optional, Callable, Dict
from enum import Enum
import time


class DilemmaCategory(Enum):
    """Categories of ethical dilemmas"""
    CREATURE_WELFARE = "creature_welfare"
    RESEARCH_INTEGRITY = "research_integrity"
    ECOSYSTEM_IMPACT = "ecosystem_impact"
    POPULATION_MANAGEMENT = "population_management"


@dataclass
class DilemmaChoice:
    """
    A single choice option in an ethical dilemma.
    
    Attributes:
        text: Display text for the choice
        welfare_impact: Change to welfare score (-100 to +100)
        ecosystem_impact: Change to ecosystem score
        integrity_impact: Change to research integrity score
        intervention_impact: Change to intervention level
        outcome_description: What happens if this choice is made
        outcome_callback: Optional function to execute if chosen
    """
    text: str
    welfare_impact: int
    ecosystem_impact: int
    integrity_impact: int
    intervention_impact: int
    outcome_description: str
    outcome_callback: Optional[Callable] = None
    
    def get_impact_summary(self) -> str:
        """Get formatted summary of ethics impacts"""
        parts = []
        if self.welfare_impact != 0:
            parts.append(f"Welfare: {self.welfare_impact:+d}")
        if self.ecosystem_impact != 0:
            parts.append(f"Ecosystem: {self.ecosystem_impact:+d}")
        if self.integrity_impact != 0:
            parts.append(f"Integrity: {self.integrity_impact:+d}")
        if self.intervention_impact != 0:
            parts.append(f"Intervention: {self.intervention_impact:+d}")
        return "  ".join(parts)


@dataclass
class EthicalDilemma:
    """
    An ethical dilemma presented to the player.
    
    Attributes:
        id: Unique identifier
        category: Type of dilemma
        title: Short title
        description: Full description of the situation
        choices: List of available choices
        trigger_condition: String describing when this triggers
        cooldown_seconds: Minimum time before this can trigger again
    """
    id: str
    category: DilemmaCategory
    title: str
    description: str
    choices: List[DilemmaChoice]
    trigger_condition: str
    cooldown_seconds: float = 300.0  # 5 minutes default
    
    def __repr__(self):
        return f"EthicalDilemma(id='{self.id}', title='{self.title}', choices={len(self.choices)})"


@dataclass
class DilemmaResolution:
    """Record of a resolved dilemma"""
    dilemma_id: str
    choice_index: int
    timestamp: float
    ethics_before: Dict[str, float]
    ethics_after: Dict[str, float]


# ============================================================================
# OUTCOME CALLBACK HELPERS
# ============================================================================

def _heal_sick_creature(battle: 'SpatialBattle'):
    """Heal the weakest creature"""
    weakest = None
    min_hp = float('inf')
    
    for bc in battle.creatures:
        if bc.is_alive() and bc.creature.stats.hp < min_hp:
            min_hp = bc.creature.stats.hp
            weakest = bc
    
    if weakest:
        weakest.creature.stats.hp = min(weakest.creature.stats.max_hp, weakest.creature.stats.hp + 30.0)
        battle._log(f"Healed {weakest.creature.name} (+30 HP)")

def _euthanize_sick_creature(battle: 'SpatialBattle'):
    """Humanely remove the weakest creature"""
    weakest = None
    min_hp = float('inf')
    
    for bc in battle.creatures:
        if bc.is_alive() and bc.creature.stats.hp < min_hp:
            min_hp = bc.creature.stats.hp
            weakest = bc
    
    if weakest:
        weakest.creature.stats.hp = 0
        battle._log(f"Euthanized {weakest.creature.name}")

def _expand_arena(battle: 'SpatialBattle'):
    """Expand the arena to support more creatures"""
    old_width = battle.arena.width
    old_height = battle.arena.height
    battle.arena.width *= 1.3
    battle.arena.height *= 1.3
    battle._log(f"Expanded arena from {old_width:.0f}x{old_height:.0f} to {battle.arena.width:.0f}x{battle.arena.height:.0f}")

def _reduce_food_supply(battle: 'SpatialBattle'):
    """Reduce pellet spawn rate"""
    old_rate = battle.resource_spawn_rate
    battle.resource_spawn_rate *= 0.7
    battle._log(f"Reduced food spawn rate by 30% ({old_rate:.2f} -> {battle.resource_spawn_rate:.2f})")

def _spawn_emergency_food(battle: 'SpatialBattle'):
    """Spawn emergency food pellets"""
    import random
    pellet_count = 20
    for _ in range(pellet_count):
        x = random.uniform(0, battle.arena.width)
        y = random.uniform(0, battle.arena.height)
        battle._spawn_resource_at(x, y)
    battle._log(f"Spawned {pellet_count} emergency food pellets")

def _increase_mutation_rate(battle: 'SpatialBattle'):
    """Increase mutation rate temporarily"""
    if hasattr(battle, 'breeding_system'):
        old_rate = battle.breeding_system.mutation_rate
        battle.breeding_system.mutation_rate = min(1.0, old_rate * 1.5)
        battle._log(f"Increased mutation rate by 50% ({old_rate:.2f} -> {battle.breeding_system.mutation_rate:.2f})")

def _suppress_mutation(battle: 'SpatialBattle'):
    """Suppress mutation temporarily"""
    if hasattr(battle, 'breeding_system'):
        old_rate = battle.breeding_system.mutation_rate
        battle.breeding_system.mutation_rate = max(0.0, old_rate * 0.5)
        battle._log(f"Reduced mutation rate by 50% ({old_rate:.2f} -> {battle.breeding_system.mutation_rate:.2f})")


# ============================================================================
# PREDEFINED DILEMMAS
# ============================================================================

# Creature Welfare Dilemmas
SICK_CREATURE_DILEMMA = EthicalDilemma(
    id="sick_creature_01",
    category=DilemmaCategory.CREATURE_WELFARE,
    title="Sick Creature Detected",
    description="A creature in your study shows signs of severe illness. Its condition is deteriorating rapidly. How do you proceed?",
    choices=[
        DilemmaChoice(
            text="Provide medical treatment",
            welfare_impact=5,
            ecosystem_impact=0,
            integrity_impact=-2,
            intervention_impact=3,
            outcome_description="Creature recovers but this may affect natural selection dynamics.",
            outcome_callback=_heal_sick_creature
        ),
        DilemmaChoice(
            text="Isolate and observe",
            welfare_impact=0,
            ecosystem_impact=0,
            integrity_impact=3,
            intervention_impact=1,
            outcome_description="Document illness progression for scientific understanding."
        ),
        DilemmaChoice(
            text="Euthanize humanely",
            welfare_impact=-3,
            ecosystem_impact=1,
            integrity_impact=1,
            intervention_impact=2,
            outcome_description="Prevent suffering and potential spread to other creatures.",
            outcome_callback=_euthanize_sick_creature
        )
    ],
    trigger_condition="creature_health_below_20_percent"
)

AGGRESSIVE_CREATURE_DILEMMA = EthicalDilemma(
    id="aggressive_creature_01",
    category=DilemmaCategory.CREATURE_WELFARE,
    title="Aggressive Behavior",
    description="A creature has become extremely aggressive, attacking others frequently. It's disrupting the social dynamics of the population.",
    choices=[
        DilemmaChoice(
            text="Relocate to isolated area",
            welfare_impact=2,
            ecosystem_impact=-1,
            integrity_impact=0,
            intervention_impact=4,
            outcome_description="Separate the aggressive creature to protect others."
        ),
        DilemmaChoice(
            text="Apply behavioral conditioning",
            welfare_impact=-2,
            ecosystem_impact=0,
            integrity_impact=-3,
            intervention_impact=5,
            outcome_description="Use stimulus to discourage aggressive behavior."
        ),
        DilemmaChoice(
            text="Allow natural social hierarchy",
            welfare_impact=-1,
            ecosystem_impact=3,
            integrity_impact=4,
            intervention_impact=-3,
            outcome_description="Let the population establish dominance naturally."
        )
    ],
    trigger_condition="creature_attack_count_above_threshold"
)

# Population Management Dilemmas
OVERPOPULATION_DILEMMA = EthicalDilemma(
    id="overpopulation_01",
    category=DilemmaCategory.POPULATION_MANAGEMENT,
    title="Overpopulation Crisis",
    description="The creature population has exceeded sustainable levels. Food scarcity is causing widespread hunger and stress.",
    choices=[
        DilemmaChoice(
            text="Introduce predator species",
            welfare_impact=-5,
            ecosystem_impact=5,
            integrity_impact=0,
            intervention_impact=8,
            outcome_description="Natural population control through predation."
        ),
        DilemmaChoice(
            text="Reduce food supply gradually",
            welfare_impact=-3,
            ecosystem_impact=2,
            integrity_impact=2,
            intervention_impact=3,
            outcome_description="Encourage natural population decline through resource limitation.",
            outcome_callback=_reduce_food_supply
        ),
        DilemmaChoice(
            text="Let nature take its course",
            welfare_impact=-2,
            ecosystem_impact=6,
            integrity_impact=5,
            intervention_impact=-5,
            outcome_description="Allow natural die-off and population regulation."
        ),
        DilemmaChoice(
            text="Expand the habitat",
            welfare_impact=6,
            ecosystem_impact=-2,
            integrity_impact=-3,
            intervention_impact=10,
            outcome_description="Provide more space and resources to support larger population.",
            outcome_callback=_expand_arena
        )
    ],
    trigger_condition="population_above_150_percent_capacity"
)

STARVATION_DILEMMA = EthicalDilemma(
    id="starvation_01",
    category=DilemmaCategory.POPULATION_MANAGEMENT,
    title="Mass Starvation Event",
    description="A significant portion of the population is starving due to resource depletion. Creatures are dying rapidly.",
    choices=[
        DilemmaChoice(
            text="Emergency food distribution",
            welfare_impact=8,
            ecosystem_impact=-3,
            integrity_impact=-4,
            intervention_impact=7,
            outcome_description="Save lives but create dependency on researcher intervention.",
            outcome_callback=_spawn_emergency_food
        ),
        DilemmaChoice(
            text="Provide minimal support",
            welfare_impact=3,
            ecosystem_impact=0,
            integrity_impact=0,
            intervention_impact=3,
            outcome_description="Help the weakest survive while maintaining some natural selection."
        ),
        DilemmaChoice(
            text="Document the event",
            welfare_impact=-5,
            ecosystem_impact=4,
            integrity_impact=6,
            intervention_impact=-6,
            outcome_description="Observe natural population dynamics without interference."
        )
    ],
    trigger_condition="average_hunger_above_80_percent"
)

# Research Integrity Dilemmas
INTERESTING_MUTATION_DILEMMA = EthicalDilemma(
    id="mutation_01",
    category=DilemmaCategory.RESEARCH_INTEGRITY,
    title="Fascinating Mutation Discovered",
    description="A creature has developed a unique mutation with interesting properties. This could be a valuable research opportunity.",
    choices=[
        DilemmaChoice(
            text="Isolate for intensive study",
            welfare_impact=-2,
            ecosystem_impact=-2,
            integrity_impact=-3,
            intervention_impact=6,
            outcome_description="Remove from population to study in controlled conditions."
        ),
        DilemmaChoice(
            text="Encourage breeding",
            welfare_impact=1,
            ecosystem_impact=-1,
            integrity_impact=-4,
            intervention_impact=5,
            outcome_description="Selectively breed to spread the mutation."
        ),
        DilemmaChoice(
            text="Observe naturally",
            welfare_impact=0,
            ecosystem_impact=2,
            integrity_impact=5,
            intervention_impact=-2,
            outcome_description="Let the mutation spread (or not) through natural selection."
        )
    ],
    trigger_condition="new_rare_trait_appears"
)

# Ecosystem Impact Dilemmas
HABITAT_DEGRADATION_DILEMMA = EthicalDilemma(
    id="habitat_degradation_01",
    category=DilemmaCategory.ECOSYSTEM_IMPACT,
    title="Habitat Degradation",
    description="Creature activity has degraded a section of the habitat. Resources in that area are depleted.",
    choices=[
        DilemmaChoice(
            text="Restore the habitat",
            welfare_impact=4,
            ecosystem_impact=5,
            integrity_impact=-2,
            intervention_impact=6,
            outcome_description="Manually restore resources and environment."
        ),
        DilemmaChoice(
            text="Relocate creatures",
            welfare_impact=1,
            ecosystem_impact=2,
            integrity_impact=0,
            intervention_impact=4,
            outcome_description="Move creatures to healthier areas."
        ),
        DilemmaChoice(
            text="Study adaptation",
            welfare_impact=-2,
            ecosystem_impact=0,
            integrity_impact=4,
            intervention_impact=-3,
            outcome_description="Observe how creatures adapt to degraded conditions."
        )
    ],
    trigger_condition="area_resource_depletion"
)


# ============================================================================
# DILEMMA SYSTEM
# ============================================================================

class DilemmaSystem:
    """
    Manages ethical dilemmas throughout the simulation.
    
    Presents dilemmas to the player based on simulation events,
    tracks resolutions, and manages cooldowns.
    """
    
    def __init__(self):
        """Initialize the dilemma system"""
        self.available_dilemmas: List[EthicalDilemma] = [
            SICK_CREATURE_DILEMMA,
            AGGRESSIVE_CREATURE_DILEMMA,
            OVERPOPULATION_DILEMMA,
            STARVATION_DILEMMA,
            INTERESTING_MUTATION_DILEMMA,
            HABITAT_DEGRADATION_DILEMMA
        ]
        
        self.resolution_history: List[DilemmaResolution] = []
        self.last_trigger_times: Dict[str, float] = {}
        self.pending_dilemma: Optional[EthicalDilemma] = None
        
    def check_for_dilemmas(self, simulation_state: Dict) -> Optional[EthicalDilemma]:
        """
        Check if any dilemmas should trigger based on simulation state.
        
        Args:
            simulation_state: Dictionary with simulation metrics
            
        Returns:
            EthicalDilemma if one should trigger, None otherwise
        """
        current_time = time.time()
        
        for dilemma in self.available_dilemmas:
            # Check cooldown
            last_trigger = self.last_trigger_times.get(dilemma.id, 0)
            if current_time - last_trigger < dilemma.cooldown_seconds:
                continue
                
            # Check trigger condition
            if self._check_trigger_condition(dilemma.trigger_condition, simulation_state):
                self.last_trigger_times[dilemma.id] = current_time
                self.pending_dilemma = dilemma
                return dilemma
                
        return None
        
    def _check_trigger_condition(self, condition: str, state: Dict) -> bool:
        """
        Check if a trigger condition is met.
        
        Args:
            condition: Condition string
            state: Simulation state dictionary
            
        Returns:
            True if condition is met
        """
        # Simplified trigger checking - in real implementation, this would
        # check actual simulation state
        
        if condition == "creature_health_below_20_percent":
            return state.get("min_creature_health", 100) < 20
            
        elif condition == "creature_attack_count_above_threshold":
            return state.get("aggressive_creature_count", 0) > 0
            
        elif condition == "population_above_150_percent_capacity":
            capacity = state.get("capacity", 100)
            population = state.get("population", 0)
            return population > capacity * 1.5
            
        elif condition == "average_hunger_above_80_percent":
            return state.get("average_hunger", 0) > 80
            
        elif condition == "new_rare_trait_appears":
            return state.get("new_rare_trait", False)
            
        elif condition == "area_resource_depletion":
            return state.get("depleted_areas", 0) > 0
            
        return False
        
    def resolve_dilemma(self, dilemma: EthicalDilemma, 
                       choice_index: int,
                       ethics_before: Dict[str, float]) -> DilemmaResolution:
        """
        Record a dilemma resolution.
        
        Args:
            dilemma: The dilemma that was resolved
            choice_index: Index of chosen option
            ethics_before: Ethics scores before choice
            
        Returns:
            DilemmaResolution record
        """
        choice = dilemma.choices[choice_index]
        
        # Calculate new ethics scores
        ethics_after = {
            "welfare": ethics_before.get("welfare", 0) + choice.welfare_impact,
            "ecosystem": ethics_before.get("ecosystem", 0) + choice.ecosystem_impact,
            "integrity": ethics_before.get("integrity", 0) + choice.integrity_impact,
            "intervention": ethics_before.get("intervention", 0) + choice.intervention_impact
        }
        
        resolution = DilemmaResolution(
            dilemma_id=dilemma.id,
            choice_index=choice_index,
            timestamp=time.time(),
            ethics_before=ethics_before,
            ethics_after=ethics_after
        )
        
        self.resolution_history.append(resolution)
        self.pending_dilemma = None
        
        # Note: Outcome callbacks are executed in main.py where battle instance is available
        
        return resolution
        
    def get_resolution_statistics(self) -> Dict:
        """
        Get statistics about player's dilemma resolutions.
        
        Returns:
            Dictionary with statistics
        """
        if not self.resolution_history:
            return {
                "total_dilemmas": 0,
                "by_category": {},
                "average_welfare_impact": 0.0,
                "average_intervention_impact": 0.0
            }
            
        by_category = {}
        total_welfare = 0
        total_intervention = 0
        
        for resolution in self.resolution_history:
            # Find the dilemma
            dilemma = next((d for d in self.available_dilemmas if d.id == resolution.dilemma_id), None)
            if dilemma:
                category = dilemma.category.value
                by_category[category] = by_category.get(category, 0) + 1
                
            # Calculate impacts
            welfare_change = resolution.ethics_after["welfare"] - resolution.ethics_before["welfare"]
            intervention_change = resolution.ethics_after["intervention"] - resolution.ethics_before["intervention"]
            
            total_welfare += welfare_change
            total_intervention += intervention_change
            
        count = len(self.resolution_history)
        
        return {
            "total_dilemmas": count,
            "by_category": by_category,
            "average_welfare_impact": total_welfare / count,
            "average_intervention_impact": total_intervention / count,
            "most_recent": self.resolution_history[-1].timestamp if self.resolution_history else 0
        }
        
    def __repr__(self):
        stats = self.get_resolution_statistics()
        return f"DilemmaSystem(resolved={stats['total_dilemmas']}, pending={self.pending_dilemma is not None})"

