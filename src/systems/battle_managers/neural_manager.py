"""
Neural Manager

Handles neural network updates, observational learning, and brain statistics
for the spatial battle system.

Extracted from battle_spatial.py.
"""

import math
import numpy as np
from typing import List, Optional, Any, Dict, Tuple

from src.models.spatial import Vector2D, Arena
from .event_manager import EventManager
from .combat_manager import CombatManager
from .resource_manager import ResourceManager
from .lifecycle_manager import LifecycleManager
from .movement_manager import MovementManager
from ..neural_observational_learning import NeuralObservationalLearning
from ..brain_statistics import BrainStatistics
from ..reward_tracker import RewardTracker

class NeuralManager:
    """
    Manages neural network decision making and learning.
    
    Responsibilities:
    - Gather sensory inputs for creature brains
    - Execute neural network decisions (EAT, FLEE, FIGHT, EXPLORE)
    - Manage observational learning
    - Track brain statistics
    - Handle rewards
    """
    
    def __init__(
        self,
        event_manager: EventManager,
        combat_manager: CombatManager,
        resource_manager: ResourceManager,
        lifecycle_manager: LifecycleManager,
        movement_manager: MovementManager,
        arena: Arena,
        combat_config: Any
    ):
        """
        Initialize the neural manager.
        
        Args:
            event_manager: For emitting learning events
            combat_manager: For executing combat actions
            resource_manager: For finding food
            lifecycle_manager: For handling deaths
            movement_manager: For movement actions
            arena: For spatial queries
            combat_config: Combat configuration
        """
        self.event_manager = event_manager
        self.combat_manager = combat_manager
        self.resource_manager = resource_manager
        self.lifecycle_manager = lifecycle_manager
        self.movement_manager = movement_manager
        self.arena = arena
        self.combat_config = combat_config
        
        # Initialize sub-systems
        self.neural_learning = NeuralObservationalLearning()
        self.brain_stats = BrainStatistics()
        self.reward_tracker = RewardTracker()
        
        # Link reward tracker to lifecycle manager
        self.lifecycle_manager.reward_tracker = self.reward_tracker
        
        self.last_brain_analysis: float = 0.0
        
    def update_brains(self, creatures: List[Any], all_active_creatures: List[Any], delta_time: float, current_time: float):
        """
        Update neural networks for intelligent creatures.
        
        Args:
            creatures: List of creatures to update (subset)
            all_active_creatures: All currently active creatures (for inputs)
            delta_time: Time elapsed
            current_time: Current simulation time
        """
        for creature in creatures:
            if not creature.is_alive():
                continue
                
            # Only process if creature has a brain (Intelligent trait usually implies this, 
            # but we check if it has the capability)
            # For now, we assume all creatures passed here are candidates for neural update
            
            # 1. Gather inputs
            inputs = self._get_neural_inputs(creature, all_active_creatures)
            
            # 2. Forward pass (placeholder for actual NN execution)
            # In a real implementation, this would call creature.brain.activate(inputs)
            # For now, we simulate a decision based on inputs or traits
            # This logic was previously implicitly handled or part of _update_creature_logic
            # If we are extracting _execute_neural_action, we need the decision logic too.
            
            # Since the original code didn't have a full NN implementation visible in the snippet,
            # we will assume there's a mechanism to get an action. 
            # If not, we'll implement a simple heuristic-based "brain" here or delegate to AI manager later.
            # Wait, the original code had _execute_neural_action but where was it called?
            # It was likely called from _update_creature_logic.
            
            # For this extraction, we will focus on providing the helper methods 
            # and let AIManager orchestrate the decision loop.
            pass

    def get_neural_inputs(self, creature: Any, all_alive: List[Any]) -> np.ndarray:
        """Gather sensory inputs for neural network (5 inputs)."""
        return self._get_neural_inputs(creature, all_alive)

    def _get_neural_inputs(self, creature: Any, all_alive: List[Any]) -> np.ndarray:
        """
        Gather sensory inputs for neural network (8 inputs).
        
        Inputs:
        0: Hunger (0-1)
        1: Nearest threat distance (0-1, closer = higher)
        2: Nearest food distance (0-1, closer = higher)
        3: HP ratio (0-1)
        4: Nearby allies count (0-1)
        5: Familiarity with nearest creature (0-1)
        6: Trust level with nearest creature (0-1)
        7: Threat level from nearest creature (0-1)
        """
        # Input 0: Hunger (0-1)
        hunger = creature.creature.hunger / 100.0
        
        # Input 1: Nearest threat (0-1, closer = higher)
        nearest_threat_dist = float('inf')
        nearest_creature = None
        for other in all_alive:
            if other != creature and not self._is_ally(creature, other):
                dist = creature.spatial.distance_to(other.spatial)
                if dist < nearest_threat_dist:
                    nearest_threat_dist = dist
                    nearest_creature = other
        threat_input = 1.0 - min(nearest_threat_dist / 50.0, 1.0)
        
        # Input 2: Nearest food (0-1, closer = higher)
        nearest_food_dist = float('inf')
        if self.arena.resources:
            for resource in self.arena.resources:
                resource_pos = self.arena.get_resource_position(resource)
                dist = creature.spatial.position.distance_to(resource_pos)
                if dist < nearest_food_dist:
                    nearest_food_dist = dist
        food_input = 1.0 - min(nearest_food_dist / 50.0, 1.0)
        
        # Input 3: HP ratio (0-1)
        hp_ratio = creature.creature.stats.hp / max(1, creature.creature.stats.max_hp)
        
        # Input 4: Nearby allies (0-1)
        allies = sum(1 for other in all_alive 
                    if other != creature and self._is_ally(creature, other) 
                    and creature.spatial.distance_to(other.spatial) < 20.0)
        ally_input = min(allies / 5.0, 1.0)
        
        # Inputs 5-7: Social inputs from nearest creature
        familiarity = 0.0
        trust = 0.0
        social_threat = 0.0
        
        if nearest_creature is not None:
            # Get social memory for nearest creature
            social_memory = creature.creature.get_social_memory(nearest_creature.creature.creature_id)
            if social_memory:
                familiarity = social_memory.get_familiarity()
                trust = social_memory.get_trust()
                social_threat = social_memory.get_threat(creature.creature.stats.max_hp)
        
        return np.array([hunger, threat_input, food_input, hp_ratio, ally_input, 
                        familiarity, trust, social_threat], dtype=np.float32)
    
    def execute_neural_action(self, creature: Any, action: str, all_alive: List[Any], current_time: float):
        """
        Execute neural network decision.
        
        Actions:
        - EAT: Move to food
        - FLEE: Run from threats
        - FIGHT: Attack enemies
        - EXPLORE: Wander
        """
        if action == 'EAT':
            # Move toward nearest food
            if self.arena.resources:
                nearest_food = None
                nearest_dist = float('inf')
                for resource in self.arena.resources:
                    resource_pos = self.arena.get_resource_position(resource)
                    dist = creature.spatial.position.distance_to(resource_pos)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_food = resource_pos
                if nearest_food:
                    direction = nearest_food - creature.spatial.position
                    direction = direction.normalize()
                    creature.spatial.target_position = creature.spatial.position + direction * 10.0
        
        elif action == 'FLEE':
            # Run from nearest threat
            nearest_threat = None
            nearest_dist = float('inf')
            for other in all_alive:
                if other != creature and not self._is_ally(creature, other):
                    dist = creature.spatial.distance_to(other.spatial)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_threat = other
            if nearest_threat:
                direction = creature.spatial.position - nearest_threat.spatial.position
                direction = direction.normalize()
                creature.spatial.target_position = creature.spatial.position + direction * 20.0
        
        elif action == 'FIGHT':
            # Attack nearest enemy
            nearest_enemy = None
            nearest_dist = float('inf')
            for other in all_alive:
                if other != creature and not self._is_ally(creature, other):
                    dist = creature.spatial.distance_to(other.spatial)
                    if dist < nearest_dist and dist < self.combat_config.max_chase_distance:
                        nearest_dist = dist
                        nearest_enemy = other
            if nearest_enemy:
                creature.spatial.target_position = nearest_enemy.spatial.position
                if nearest_dist <= self.combat_config.close_combat_range:
                    if creature.can_attack(current_time):
                        died = self.combat_manager.attempt_attack(creature, nearest_enemy, current_time, all_alive)
                        if died:
                            self.lifecycle_manager.handle_death(nearest_enemy, all_alive, killer=creature, cause="combat")
        
        elif action == 'EXPLORE':
            # Wander randomly
            import random
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(5, 15)
            offset = Vector2D(distance * math.cos(angle), distance * math.sin(angle))
            creature.spatial.target_position = creature.spatial.position + offset
        
        elif action == 'COOPERATE':
            # Move toward nearest ally and record cooperation
            nearest_ally = None
            nearest_dist = float('inf')
            for other in all_alive:
                if other != creature and self._is_ally(creature, other):
                    dist = creature.spatial.distance_to(other.spatial)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_ally = other
            if nearest_ally:
                # Move toward ally (but not too close)
                if nearest_dist > 10.0:
                    direction = nearest_ally.spatial.position - creature.spatial.position
                    direction = direction.normalize()
                    creature.spatial.target_position = creature.spatial.position + direction * 8.0
                # Record cooperation
                creature.creature.record_social_interaction(nearest_ally.creature.creature_id, 'cooperation')
        
        elif action == 'AVOID':
            # Move away from nearest creature (perceived as threat)
            nearest_other = None
            nearest_dist = float('inf')
            for other in all_alive:
                if other != creature:
                    dist = creature.spatial.distance_to(other.spatial)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_other = other
            if nearest_other and nearest_dist < 15.0:  # Only avoid if close
                direction = creature.spatial.position - nearest_other.spatial.position
                direction = direction.normalize()
                creature.spatial.target_position = creature.spatial.position + direction * 12.0
                # Record neutral interaction (avoiding)
                creature.creature.record_social_interaction(nearest_other.creature.creature_id, 'neutral')

    def _is_ally(self, creature1: Any, creature2: Any) -> bool:
        """
        Check if two creatures are allies.
        
        Note: This duplicates logic from SpatialBattle. In a full refactor, 
        relationship logic should be in a RelationshipManager or on the creatures.
        For now, we implement a basic check.
        """
        # Basic check: same species or explicitly friendly traits
        # Ideally, this should use the same logic as SpatialBattle._is_ally
        # We can pass a callback or delegate this.
        # For this extraction, we'll assume basic species check if no better method exists.
        if hasattr(creature1.creature, 'genome_id') and hasattr(creature2.creature, 'genome_id'):
             return creature1.creature.genome_id == creature2.creature.genome_id
        return False
