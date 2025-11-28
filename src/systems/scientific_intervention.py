"""
Scientific Intervention System - Player-Guided Learning

This module implements the player's ability to guide creature learning through
scientific tools, replacing Black & White's "praise/punishment" system with
research-appropriate interventions.

Players can:
- Reward behaviors with food (positive reinforcement)
- Discourage behaviors with mild stimulus (negative reinforcement)
- Mark areas to guide creature beliefs
- Track intervention effectiveness
"""

from enum import Enum
from typing import Optional, Tuple, List
from dataclasses import dataclass
import time

from src.models.creature_beliefs import CreatureBeliefSystem, CreatureBelief, BeliefType
from src.systems.research_ethics import ResearchEthicsSystem, ETHICAL_ACTIONS
from src.systems.battle_events import BattleEvent, BattleEventType
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth


class InterventionType(Enum):
    """Types of scientific interventions"""
    REWARD_FOOD = "reward_food"
    APPLY_STIMULUS = "apply_stimulus"
    MARK_LOCATION = "mark_location"
    RELOCATE = "relocate"
    PROVIDE_SHELTER = "provide_shelter"


@dataclass
class InterventionRecord:
    """Record of a scientific intervention"""
    intervention_type: InterventionType
    creature_id: str
    position: Tuple[float, float]
    timestamp: float
    behavior_context: str
    effectiveness: float = 0.0  # 0.0 to 1.0, measured later


class ScientificIntervention:
    """
    Manages player-guided learning through scientific tools.
    
    This system allows players to reinforce or discourage specific behaviors
    by creating strong beliefs in creatures. Unlike direct control, this
    works through the creature's belief system.
    """
    
    def __init__(self, ethics_system: Optional[ResearchEthicsSystem] = None):
        """
        Initialize scientific intervention system.
        
        Args:
            ethics_system: Optional ethics system to track interventions
        """
        self.ethics_system = ethics_system
        self.intervention_history: List[InterventionRecord] = []
        self.max_history = 200
        
    def reward_behavior(self, creature_id: str, 
                       belief_system: CreatureBeliefSystem,
                       position: Tuple[float, float],
                       behavior: str,
                       food_value: int = 20) -> CreatureBelief:
        """
        Reward a behavior with food, creating positive belief.
        
        This is positive reinforcement - the creature learns that this
        location/behavior is good.
        
        Args:
            creature_id: ID of creature to reward
            belief_system: Creature's belief system
            position: Position where behavior occurred
            behavior: Description of behavior (e.g., "explored_new_area")
            food_value: Amount of food reward
            
        Returns:
            CreatureBelief that was created
        """
        # Determine belief type based on behavior
        if "explore" in behavior.lower():
            belief_type = BeliefType.SAFE_AREA
            confidence = 0.8
        elif "forage" in behavior.lower() or "eat" in behavior.lower():
            belief_type = BeliefType.FOOD_LOCATION
            confidence = 0.9
        elif "rest" in behavior.lower() or "shelter" in behavior.lower():
            belief_type = BeliefType.SHELTER
            confidence = 0.7
        else:
            # Generic positive association
            belief_type = BeliefType.SAFE_AREA
            confidence = 0.6
            
        # Create strong positive belief
        belief = CreatureBelief(
            belief_type=belief_type,
            target=f"area_{int(position[0])}_{int(position[1])}",
            confidence=confidence
        )
        
        belief_system.add_belief(belief)
        
        # Record intervention
        record = InterventionRecord(
            intervention_type=InterventionType.REWARD_FOOD,
            creature_id=creature_id,
            position=position,
            timestamp=time.time(),
            behavior_context=behavior
        )
        self._add_to_history(record)
        
        # Update ethics
        if self.ethics_system:
            self.ethics_system.record_action(
                action="reward_food",
                welfare=ETHICAL_ACTIONS["reward_food"]["welfare"],
                ecosystem=ETHICAL_ACTIONS["reward_food"]["ecosystem"],
                integrity=ETHICAL_ACTIONS["reward_food"]["integrity"],
                intervention=ETHICAL_ACTIONS["reward_food"]["intervention"],
                target_creature_id=creature_id,
                notes=f"Rewarded {behavior}"
            )
            
        return belief
        
    def discourage_behavior(self, creature_id: str,
                           belief_system: CreatureBeliefSystem,
                           position: Tuple[float, float],
                           behavior: str,
                           stimulus_intensity: float = 0.5) -> CreatureBelief:
        """
        Discourage a behavior with mild stimulus, creating negative belief.
        
        This is negative reinforcement - the creature learns to avoid this
        location/behavior.
        
        Args:
            creature_id: ID of creature
            belief_system: Creature's belief system
            position: Position where behavior occurred
            behavior: Description of behavior (e.g., "entered_danger_zone")
            stimulus_intensity: Intensity of stimulus (0.0 to 1.0)
            
        Returns:
            CreatureBelief that was created
        """
        # Create strong negative belief
        belief = CreatureBelief(
            belief_type=BeliefType.DANGER_ZONE,
            target=f"area_{int(position[0])}_{int(position[1])}",
            confidence=0.7 + (stimulus_intensity * 0.3)  # Higher stimulus = stronger belief
        )
        
        belief_system.add_belief(belief)
        
        # Record intervention
        record = InterventionRecord(
            intervention_type=InterventionType.APPLY_STIMULUS,
            creature_id=creature_id,
            position=position,
            timestamp=time.time(),
            behavior_context=behavior
        )
        self._add_to_history(record)
        
        # Update ethics (negative impact on welfare)
        if self.ethics_system:
            self.ethics_system.record_action(
                action="apply_stimulus",
                welfare=ETHICAL_ACTIONS["apply_stimulus"]["welfare"],
                ecosystem=ETHICAL_ACTIONS["apply_stimulus"]["ecosystem"],
                integrity=ETHICAL_ACTIONS["apply_stimulus"]["integrity"],
                intervention=ETHICAL_ACTIONS["apply_stimulus"]["intervention"],
                target_creature_id=creature_id,
                notes=f"Discouraged {behavior}"
            )
            
        return belief
        
    def mark_area(self, belief_system: CreatureBeliefSystem,
                 position: Tuple[float, float],
                 marker_type: str,
                 radius: float = 5.0) -> CreatureBelief:
        """
        Mark an area to guide creature beliefs.
        
        Creates a belief about an area without direct creature interaction.
        Useful for preventative guidance.
        
        Args:
            belief_system: Creature's belief system
            position: Position to mark
            marker_type: "safe", "danger", "food", or "shelter"
            radius: Radius of marked area
            
        Returns:
            CreatureBelief that was created
        """
        # Map marker type to belief type
        marker_to_belief = {
            "safe": BeliefType.SAFE_AREA,
            "danger": BeliefType.DANGER_ZONE,
            "food": BeliefType.FOOD_LOCATION,
            "shelter": BeliefType.SHELTER,
            "water": BeliefType.WATER_SOURCE
        }
        
        belief_type = marker_to_belief.get(marker_type, BeliefType.SAFE_AREA)
        
        # Create belief
        belief = CreatureBelief(
            belief_type=belief_type,
            target=f"area_{int(position[0])}_{int(position[1])}",
            confidence=0.5  # Moderate confidence for indirect learning
        )
        
        belief_system.add_belief(belief)
        
        # Update ethics
        if self.ethics_system:
            action_key = f"mark_{marker_type}_area"
            if action_key in ETHICAL_ACTIONS:
                impacts = ETHICAL_ACTIONS[action_key]
                self.ethics_system.record_action(
                    action=action_key,
                    welfare=impacts["welfare"],
                    ecosystem=impacts["ecosystem"],
                    integrity=impacts["integrity"],
                    intervention=impacts["intervention"],
                    notes=f"Marked {marker_type} area at {position}"
                )
                
        return belief
    
    def reward_construction(self, creature_id: str,
                           belief_system: CreatureBeliefSystem,
                           structure_type: str,
                           position: Tuple[float, float]) -> CreatureBelief:
        """
        Reward a creature for building a building.
        
        This reinforces building behavior and creates positive beliefs
        about construction.
        
        Args:
            creature_id: ID of creature
            belief_system: Creature's belief system
            structure_type: Type of building built
            position: Where building was built
            
        Returns:
            CreatureBelief that was created
        """
        # Create strong positive belief about building
        belief = CreatureBelief(
            belief_type=BeliefType.STRUCTURE_BENEFIT,
            target=f"structure_{structure_type}",
            confidence=0.8
        )
        
        belief_system.add_belief(belief)
        
        # Also create belief about construction skill
        skill_belief = CreatureBelief(
            belief_type=BeliefType.CONSTRUCTION_SKILL,
            target="building_ability",
            confidence=0.7
        )
        belief_system.add_belief(skill_belief)
        
        # Record intervention
        record = InterventionRecord(
            intervention_type=InterventionType.REWARD_FOOD,  # Reuse reward type
            creature_id=creature_id,
            position=position,
            timestamp=time.time(),
            behavior_context=f"built_{structure_type}"
        )
        self._add_to_history(record)
        
        # Update ethics (positive impact)
        if self.ethics_system:
            self.ethics_system.record_action(
                action="reward_food",
                welfare=ETHICAL_ACTIONS["reward_food"]["welfare"],
                ecosystem=ETHICAL_ACTIONS["reward_food"]["ecosystem"],
                integrity=ETHICAL_ACTIONS["reward_food"]["integrity"],
                intervention=ETHICAL_ACTIONS["reward_food"]["intervention"],
                target_creature_id=creature_id,
                notes=f"Rewarded building {structure_type}"
            )
        
        return belief
    
    def reinforce_material_gathering(self, creature_id: str,
                                    belief_system: CreatureBeliefSystem,
                                    material_location: Tuple[float, float]) -> CreatureBelief:
        """
        Reinforce belief about material source location.
        
        Args:
            creature_id: ID of creature
            belief_system: Creature's belief system
            material_location: Where materials were found
            
        Returns:
            CreatureBelief that was created
        """
        belief = CreatureBelief(
            belief_type=BeliefType.MATERIAL_SOURCE,
            target=f"area_{int(material_location[0])}_{int(material_location[1])}",
            confidence=0.6
        )
        
        belief_system.add_belief(belief)
        return belief
        
    def measure_intervention_effectiveness(self, creature_id: str,
                                          time_window: float = 60.0) -> dict:
        """
        Measure how effective recent interventions have been.
        
        Args:
            creature_id: ID of creature to analyze
            time_window: Time window in seconds
            
        Returns:
            Dictionary with effectiveness metrics
        """
        current_time = time.time()
        recent = [r for r in self.intervention_history 
                 if r.creature_id == creature_id 
                 and (current_time - r.timestamp) <= time_window]
        
        if not recent:
            return {
                "total_interventions": 0,
                "rewards": 0,
                "discouragements": 0,
                "average_effectiveness": 0.0
            }
            
        rewards = sum(1 for r in recent 
                     if r.intervention_type == InterventionType.REWARD_FOOD)
        discouragements = sum(1 for r in recent 
                             if r.intervention_type == InterventionType.APPLY_STIMULUS)
        
        return {
            "total_interventions": len(recent),
            "rewards": rewards,
            "discouragements": discouragements,
            "average_effectiveness": sum(r.effectiveness for r in recent) / len(recent),
            "reward_ratio": rewards / len(recent) if recent else 0.0
        }
        
    def _add_to_history(self, record: InterventionRecord):
        """Add intervention to history"""
        self.intervention_history.append(record)
        if len(self.intervention_history) > self.max_history:
            self.intervention_history.pop(0)
            
    def get_statistics(self) -> dict:
        """
        Get overall intervention statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self.intervention_history:
            return {
                "total_interventions": 0,
                "by_type": {},
                "unique_creatures": 0
            }
            
        by_type = {}
        for intervention_type in InterventionType:
            by_type[intervention_type.value] = sum(
                1 for r in self.intervention_history 
                if r.intervention_type == intervention_type
            )
            
        unique_creatures = len(set(r.creature_id for r in self.intervention_history))
        
        return {
            "total_interventions": len(self.intervention_history),
            "by_type": by_type,
            "unique_creatures": unique_creatures,
            "most_recent": self.intervention_history[-1].timestamp if self.intervention_history else 0.0
        }
    
    def use_tool(self, tool_id: str, world_pos: Tuple[float, float], battle: 'SpatialBattle', target_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        Apply a scientific tool at the given position.
        
        Args:
            tool_id: ID of the tool to use
            world_pos: Position in world coordinates
            battle: The battle instance
            target_id: Optional ID of specific target creature
            
        Returns:
            Tuple (success, message)
        """
        # Handle global tools first (no target creature needed)
        if tool_id == "asteroid_strike":
            # Orbital Kinetic Strike (God Tool)
            # Deal massive damage in a radius
            radius = 100.0
            damage = 500.0
            
            # Trigger visual effect via event
            hit_count = 0
            for bc in battle.creatures:
                if bc.is_alive():
                    dx = bc.spatial.position.x - world_pos[0]
                    dy = bc.spatial.position.y - world_pos[1]
                    dist = (dx * dx + dy * dy) ** 0.5
                    
                    if dist < radius:
                        bc.creature.stats.hp = max(0, bc.creature.stats.hp - damage)
                        hit_count += 1
                        
                        # Trigger damage event
                        battle._emit_event(BattleEvent(
                            event_type=BattleEventType.DAMAGE_DEALT,
                            message=f"{bc.creature.name} hit by asteroid!",
                            target=bc,
                            value=damage
                        ))
                        
                        if bc.creature.stats.hp <= 0:
                            bc.creature.stats.hp = 0
            
            # Record intervention
            record = InterventionRecord(
                intervention_type=InterventionType.APPLY_STIMULUS,
                creature_id="ALL",
                position=world_pos,
                timestamp=time.time(),
                behavior_context="asteroid_strike"
            )
            self._add_to_history(record)
            
            # Update ethics
            if self.ethics_system:
                self.ethics_system.record_action(
                    action="asteroid_strike",
                    welfare=-50.0,
                    ecosystem=-50.0,
                    integrity=-20.0,
                    intervention=50.0,
                    target_creature_id="ALL",
                    notes=f"Orbital Strike hit {hit_count} creatures"
                )
                
            return (True, f"Orbital Strike initiated! {hit_count} creatures hit.")

        elif tool_id == "monster_drop":
            # Apex Predator Introduction (God Tool)
            
            # Create base stats for a monster
            base_stats = Stats(
                max_hp=200,
                attack=30,
                defense=20,
                speed=25,
                special_attack=15,
                special_defense=15
            )
            
            # Create creature type
            monster_type = CreatureType(
                name="Apex Predator",
                base_stats=base_stats,
                type_tags=["predator", "boss"],
                stat_growth=StatGrowth(hp_growth=20.0, attack_growth=5.0, defense_growth=3.0)
            )
            
            # Create creature
            monster = Creature(
                name=f"Apex-{int(time.time()) % 1000}",
                creature_type=monster_type,
                level=50,
                traits=[] 
            )
            
            # Boost calculated stats manually just in case
            monster.stats.max_hp = 500
            monster.stats.hp = 500
            monster.stats.attack = 50
            monster.stats.defense = 30
            
            # Add to battle
            if hasattr(battle, 'creatures'): # Check if we can access creatures list
                from src.systems.battle_spatial import BattleCreature
                from src.models.spatial import Vector2D
                
                # Create position vector
                position = Vector2D(world_pos[0], world_pos[1])
                
                bc = BattleCreature(monster, position)
                battle.creatures.append(bc)
                if hasattr(battle, 'creature_grid'):
                    battle.creature_grid.insert(bc, position)
                
                battle._emit_event(BattleEvent(
                    event_type=BattleEventType.CREATURE_BIRTH,
                    message=f"Apex Predator {monster.name} dropped!",
                    target=bc
                ))
                
                # Record intervention
                record = InterventionRecord(
                    intervention_type=InterventionType.APPLY_STIMULUS,
                    creature_id=monster.name,
                    position=world_pos,
                    timestamp=time.time(),
                    behavior_context="monster_drop"
                )
                self._add_to_history(record)
                
                # Update ethics
                if self.ethics_system:
                    self.ethics_system.record_action(
                        action="monster_drop",
                        welfare=-20.0,
                        ecosystem=-30.0,
                        integrity=-10.0,
                        intervention=30.0,
                        target_creature_id=monster.name,
                        notes="Introduced Apex Predator"
                    )
                
                return (True, f"Apex Predator {monster.name} dropped!")
            else:
                return (False, "Could not spawn monster (no creatures list)")

        # Targeted tools (require creature nearby)
        # Find nearest creature to click position
        nearest_creature = None
        min_dist = 15.0  # Maximum distance to affect creature
        
        # If target_id is provided, find that specific creature
        if target_id:
            for bc in battle.creatures:
                if bc.creature.creature_id == target_id or bc.creature.name == target_id:
                    nearest_creature = bc
                    break
        else:
            # Otherwise find nearest
            for bc in battle.creatures:
                if bc.is_alive():
                    dx = bc.spatial.position.x - world_pos[0]
                    dy = bc.spatial.position.y - world_pos[1]
                    dist = (dx * dx + dy * dy) ** 0.5
                    
                    if dist < min_dist:
                        min_dist = dist
                        nearest_creature = bc
        
        if not nearest_creature:
            return (False, "No creature nearby")
        
        creature = nearest_creature.creature
        creature_id = creature.name  # Creatures use name as ID
        
        # Apply tool effects
        if tool_id == "nutrient_drop":
            # Restore hunger and give small HP boost
            old_hunger = creature.hunger
            creature.hunger = min(100.0, creature.hunger + 40.0)
            creature.stats.hp = min(creature.stats.max_hp, creature.stats.hp + 10.0)
            
            # Record intervention
            record = InterventionRecord(
                intervention_type=InterventionType.REWARD_FOOD,
                creature_id=creature_id,
                position=world_pos,
                timestamp=time.time(),
                behavior_context="nutrient_drop"
            )
            self._add_to_history(record)
            
            # Update ethics
            if self.ethics_system:
                self.ethics_system.record_action(
                    action="nutrient_drop",
                    welfare=5.0,
                    ecosystem=-2.0,  # Slight ecosystem impact
                    integrity=-1.0,  # Slight integrity cost
                    intervention=3.0,
                    target_creature_id=creature_id,
                    notes=f"Fed {creature.name}"
                )
            
            return (True, f"Fed {creature.name} (+{creature.hunger - old_hunger:.0f} hunger, +10 HP)")
        
        elif tool_id == "neural_shock":
            # Stun creature briefly, reduce aggression
            damage = 5.0
            creature.stats.hp = max(0, creature.stats.hp - damage)
            
            # Add temporary "stunned" effect via belief system if available
            if hasattr(creature, 'belief_system'):
                belief = CreatureBelief(
                    belief_type=BeliefType.DANGER_ZONE,
                    target=f"area_{int(world_pos[0])}_{int(world_pos[1])}",
                    confidence=0.8
                )
                creature.belief_system.add_belief(belief)
            
            # Record intervention
            record = InterventionRecord(
                intervention_type=InterventionType.APPLY_STIMULUS,
                creature_id=creature_id,
                position=world_pos,
                timestamp=time.time(),
                behavior_context="neural_shock"
            )
            self._add_to_history(record)
            
            # Update ethics
            if self.ethics_system:
                self.ethics_system.record_action(
                    action="neural_shock",
                    welfare=-8.0,  # Harmful
                    ecosystem=0.0,
                    integrity=-3.0,  # Questionable ethics
                    intervention=5.0,
                    target_creature_id=creature_id,
                    notes=f"Shocked {creature.name}"
                )
            
            return (True, f"Shocked {creature.name} (-{damage} HP, stunned)")
        
        elif tool_id == "genetic_boost":
            # Temporary stat boost
            boost_amount = 5.0
            creature.stats.attack += boost_amount
            creature.stats.speed += boost_amount * 0.5
            creature.stats.max_hp += boost_amount * 2
            creature.stats.hp = min(creature.stats.max_hp, creature.stats.hp + boost_amount * 2)
            
            # Record intervention
            record = InterventionRecord(
                intervention_type=InterventionType.REWARD_FOOD,  # Using closest type
                creature_id=creature_id,
                position=world_pos,
                timestamp=time.time(),
                behavior_context="genetic_boost"
            )
            self._add_to_history(record)
            
            # Update ethics
            if self.ethics_system:
                self.ethics_system.record_action(
                    action="genetic_boost",
                    welfare=3.0,
                    ecosystem=-5.0,  # Disrupts natural balance
                    integrity=-8.0,  # Major integrity violation
                    intervention=8.0,
                    target_creature_id=creature_id,
                    notes=f"Boosted {creature.name}"
                )
            
            return (True, f"Boosted {creature.name} (+{boost_amount} STR, +{boost_amount*0.5:.1f} SPD, +{boost_amount*2:.0f} HP)")
        
        elif tool_id == "induce_mutation":
            # Add a random trait
            from src.models.ecosystem_traits import ALL_ECOSYSTEM_TRAITS as ECOSYSTEM_TRAITS
            import random
            
            available_traits = [t for t in ECOSYSTEM_TRAITS if t not in creature.traits]
            if available_traits:
                new_trait = random.choice(available_traits)
                creature.traits.append(new_trait)
                
                # Record intervention
                record = InterventionRecord(
                    intervention_type=InterventionType.APPLY_STIMULUS,
                    creature_id=creature_id,
                    position=world_pos,
                    timestamp=time.time(),
                    behavior_context=f"induce_mutation:{new_trait.name}"
                )
                self._add_to_history(record)
                
                # Update ethics
                if self.ethics_system:
                    self.ethics_system.record_action(
                        action="induce_mutation",
                        welfare=-3.0,  # Risky for creature
                        ecosystem=-8.0,  # Major ecosystem disruption
                        integrity=-10.0,  # Severe integrity violation
                        intervention=10.0,
                        target_creature_id=creature_id,
                        notes=f"Mutated {creature.name}: {new_trait.name}"
                    )
                
                return (True, f"Mutated {creature.name} (gained {new_trait.name})")
            else:
                return (False, f"{creature.name} has all traits")
        
        elif tool_id == "collect_sample":
            # Non-invasive data collection
            record = InterventionRecord(
                intervention_type=InterventionType.REWARD_FOOD,  # Using closest type
                creature_id=creature_id,
                position=world_pos,
                timestamp=time.time(),
                behavior_context="collect_sample"
            )
            self._add_to_history(record)
            
            # Update ethics
            if self.ethics_system:
                self.ethics_system.record_action(
                    action="collect_sample",
                    welfare=-1.0,  # Minimal stress
                    ecosystem=0.0,
                    integrity=2.0,  # Good research practice
                    intervention=2.0,
                    target_creature_id=creature_id,
                    notes=f"Sampled {creature.name}"
                )
            
            # Return creature data
            data = f"{creature.name}: Lv{creature.level} HP:{creature.stats.hp:.0f}/{creature.stats.max_hp:.0f} Hunger:{creature.hunger:.0f}"
            return (True, f"Sampled {creature.name}")
        
        elif tool_id == "relocate":
            # Move creature to new position
            # Add disorientation effect
            nearest_creature.spatial.position.x = world_pos[0]
            nearest_creature.spatial.position.y = world_pos[1]
            
            # Apply "confusion" via belief system or temporary stat penalty
            if hasattr(creature, 'belief_system'):
                # Clear immediate pathing/goals by adding a confusion belief
                pass 
                
            # Record intervention
            record = InterventionRecord(
                intervention_type=InterventionType.RELOCATE,
                creature_id=creature_id,
                position=world_pos,
                timestamp=time.time(),
                behavior_context="relocated"
            )
            self._add_to_history(record)
            
            # Update ethics
            if self.ethics_system:
                self.ethics_system.record_action(
                    action="relocate",
                    welfare=-2.0, # Mild stress
                    ecosystem=0.0,
                    integrity=0.0,
                    intervention=4.0,
                    target_creature_id=creature_id,
                    notes=f"Relocated {creature.name}"
                )
                
            return (True, f"Relocated {creature.name}")
            
        else:
            return (False, f"Unknown tool: {tool_id}")

    def create_barrier(self, world_pos: Tuple[float, float], battle: 'SpatialBattle') -> Tuple[bool, str]:
        """
        Create a temporary barrier building.
        
        NOTE: Disabled - buildings should only be built by creatures through the building system.
        """
        return (False, "Barrier creation disabled - creatures must build buildings")

    def create_pheromone(self, world_pos: Tuple[float, float], battle: 'SpatialBattle') -> Tuple[bool, str]:
        """
        Create a pheromone trail.
        """
        from src.models.pheromone import Pheromone, PheromoneType
        
        if not hasattr(battle, 'pheromones'):
            # If battle doesn't support pheromones yet, we might need to add the list
            battle.pheromones = []
            
        pheromone = Pheromone(
            position=world_pos,
            pheromone_type=PheromoneType.ATTRACT, # Default to attract
            strength=1.0,
            radius=30.0,
            decay_rate=0.05, # Lasts ~20 seconds
            created_at=time.time()
        )
        
        battle.pheromones.append(pheromone)
        
        # Record intervention
        record = InterventionRecord(
            intervention_type=InterventionType.MARK_LOCATION,
            creature_id="ENVIRONMENT",
            position=world_pos,
            timestamp=time.time(),
            behavior_context="create_pheromone"
        )
        self._add_to_history(record)
        
        if self.ethics_system:
             self.ethics_system.record_action(
                action="create_pheromone",
                welfare=0.0,
                ecosystem=-2.0, # Chemical interference
                integrity=-2.0,
                intervention=3.0,
                target_creature_id="ENVIRONMENT",
                notes="Created pheromone"
            )
            
        return (True, "Pheromone released")

    def __repr__(self):
        stats = self.get_statistics()
        return f"ScientificIntervention(total={stats['total_interventions']}, creatures={stats['unique_creatures']})"

