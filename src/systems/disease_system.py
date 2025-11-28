"""
Disease System - Manages disease outbreaks, transmission, and effects.

This system monitors population density to trigger outbreaks, handles the spread
of diseases between entities, and applies the effects of active infections.
"""

import random
import math
from typing import List, Dict, Optional, Tuple, Set
from src.models.disease import Disease, DiseaseType, Infection, InfectionStage, DISEASE_DEFINITIONS
from src.models.creature import Creature
from src.models.pellet import Pellet
from src.models.spatial import Vector2D

class DiseaseSystem:
    """
    Manages the lifecycle of diseases in the simulation.
    """
    
    def __init__(self):
        """Initialize the disease system."""
        self.active_outbreaks: List[Disease] = []
        self.last_outbreak_check = 0.0
        self.outbreak_check_interval = 10.0  # Check every 10 seconds
        
        # Thresholds for outbreaks (per 100x100 area approx)
        self.creature_density_threshold = 0.0015  # ~15 creatures in 100x100
        self.pellet_density_threshold = 0.0050    # ~50 pellets in 100x100
        
    def update(self, delta_time: float, current_time: float, 
               creatures: List['BattleCreature'], resources: List[Pellet], 
               arena_width: float, arena_height: float):
        """
        Main update loop for disease system.
        
        Args:
            delta_time: Time elapsed since last frame
            current_time: Current simulation time
            creatures: List of active creatures
            resources: List of active resources (pellets)
            arena_width: Width of arena
            arena_height: Height of arena
        """
        # 1. Check for new outbreaks
        if current_time - self.last_outbreak_check >= self.outbreak_check_interval:
            self._check_outbreak_conditions(creatures, resources, arena_width, arena_height)
            self.last_outbreak_check = current_time
            
        # 2. Update infections in creatures
        self._update_creature_infections(delta_time, creatures, current_time)
        
        # 3. Update infections in pellets
        self._update_pellet_infections(delta_time, resources, current_time)
        
        # 4. Handle transmission
        self._handle_transmission(delta_time, creatures, resources)

    def _check_outbreak_conditions(self, creatures: List['BattleCreature'], 
                                 resources: List[Pellet], 
                                 width: float, height: float):
        """Check if conditions are met for a spontaneous outbreak."""
        area = width * height
        if area <= 0:
            return

        # Creature density check
        creature_density = len([c for c in creatures if c.is_alive()]) / area
        if creature_density > self.creature_density_threshold:
            # Calculate outbreak chance based on how much we exceed threshold
            excess = (creature_density / self.creature_density_threshold) - 1.0
            chance = 0.05 * (1.0 + excess)  # 5% base chance + scaling
            
            if random.random() < chance:
                # Trigger creature disease
                disease_type = random.choice([DiseaseType.PLAGUE, DiseaseType.WASTING, DiseaseType.PARASITE])
                self._trigger_outbreak(disease_type, creatures, is_creature=True)
                
        # Pellet density check
        pellet_density = len(resources) / area
        if pellet_density > self.pellet_density_threshold:
            excess = (pellet_density / self.pellet_density_threshold) - 1.0
            chance = 0.05 * (1.0 + excess)
            
            if random.random() < chance:
                # Trigger pellet disease
                disease_type = random.choice([DiseaseType.BLIGHT, DiseaseType.TOXIN_BLOOM])
                self._trigger_outbreak(disease_type, resources, is_creature=False)

    def _trigger_outbreak(self, disease_type: DiseaseType, population: List, is_creature: bool):
        """Infect a random individual to start an outbreak."""
        if not population:
            return
            
        disease = DISEASE_DEFINITIONS[disease_type]
        patient_zero = random.choice(population)
        
        if is_creature:
            # For BattleCreature wrapper
            if hasattr(patient_zero, 'creature'):
                self.infect_creature(patient_zero.creature, disease)
        else:
            # For Pellet
            self.infect_pellet(patient_zero, disease)
            
        print(f"OUTBREAK TRIGGERED: {disease.name} started!")

    def infect_creature(self, creature: Creature, disease: Disease) -> bool:
        """
        Attempt to infect a creature.
        
        Returns:
            True if infection was successful
        """
        # Check if already infected
        if hasattr(creature, 'active_infection') and creature.active_infection:
            return False
            
        # Check immunity using new immune_memory system
        if hasattr(creature, 'immune_memory') and disease.disease_id in creature.immune_memory:
            # Check if resistance is high enough to prevent infection
            resistance = creature.immune_memory[disease.disease_id]
            if resistance >= 0.9:  # 90%+ resistance = full immunity
                return False
        
        # Check for partial immunity from parent strain
        if hasattr(creature, 'immune_memory') and disease.parent_id:
            if disease.parent_id in creature.immune_memory:
                parent_resistance = creature.immune_memory[disease.parent_id]
                # Parent strain provides 50% of its resistance to mutated strains
                if parent_resistance * 0.5 >= 0.9:
                    return False
            
        # Create infection
        infection = Infection(
            disease=disease,
            stage=InfectionStage.INCUBATING
        )
        
        # Attach to creature
        creature.active_infection = infection
        return True

    def infect_pellet(self, pellet: Pellet, disease: Disease) -> bool:
        """
        Attempt to infect a pellet.
        
        Returns:
            True if infection was successful
        """
        # Check if already infected
        if hasattr(pellet, 'active_infection') and pellet.active_infection:
            return False
            
        # Create infection
        infection = Infection(
            disease=disease,
            stage=InfectionStage.INCUBATING
        )
        
        # Attach to pellet
        pellet.active_infection = infection
        return True

    def _update_creature_infections(self, delta_time: float, creatures: List['BattleCreature'], current_time: float):
        """Update state of infected creatures."""
        for battle_creature in creatures:
            if not battle_creature.is_alive():
                continue
                
            creature = battle_creature.creature
            if not hasattr(creature, 'active_infection') or not creature.active_infection:
                continue
                
            infection = creature.active_infection
            disease = infection.disease
            
            # Update timer
            infection.update(delta_time)
            
            # Handle stage progression
            if infection.stage == InfectionStage.INCUBATING:
                if infection.time_in_stage >= disease.incubation_time:
                    infection.stage = InfectionStage.SYMPTOMATIC
                    infection.time_in_stage = 0.0
                    
            elif infection.stage == InfectionStage.SYMPTOMATIC:
                # Apply effects
                self._apply_creature_symptoms(creature, disease, delta_time)
                
                # Check for recovery or death
                if infection.time_in_stage >= disease.duration:
                    # Roll for mortality
                    if random.random() < disease.mortality_rate:
                        # Creature dies
                        creature.stats.hp = 0
                    else:
                        # Recovery
                        infection.stage = InfectionStage.RECOVERING
                        infection.time_in_stage = 0.0
                        
            elif infection.stage == InfectionStage.RECOVERING:
                # Recovery period (immune but maybe weak)
                if infection.time_in_stage >= 10.0: # 10s recovery
                    # Fully recovered - grant immunity
                    creature.active_infection = None
                    
                    # Add immunity using new immune_memory system
                    if not hasattr(creature, 'immune_memory'):
                        creature.immune_memory = {}
                    
                    # Grant full immunity (1.0 = 100% resistance) to this specific disease strain
                    creature.immune_memory[disease.disease_id] = 1.0

    def _apply_creature_symptoms(self, creature: Creature, disease: Disease, delta_time: float):
        """Apply active disease effects to creature."""
        # HP Drain
        if disease.hp_drain_rate > 0:
            damage = disease.hp_drain_rate * delta_time
            creature.stats.hp = max(0, creature.stats.hp - damage)
            
        # Stat penalties are handled by accessors in Creature model usually,
        # or we can apply temporary modifiers here.
        # For now, we'll just handle HP drain.

    def _update_pellet_infections(self, delta_time: float, resources: List[Pellet], current_time: float):
        """Update state of infected pellets."""
        for pellet in resources:
            if not hasattr(pellet, 'active_infection') or not pellet.active_infection:
                continue
                
            infection = pellet.active_infection
            disease = infection.disease
            
            infection.update(delta_time)
            
            if infection.stage == InfectionStage.INCUBATING:
                if infection.time_in_stage >= disease.incubation_time:
                    infection.stage = InfectionStage.SYMPTOMATIC
                    
            elif infection.stage == InfectionStage.SYMPTOMATIC:
                # Apply effects
                if disease.disease_type == DiseaseType.BLIGHT:
                    # Chance to rot away
                    if random.random() < 0.1 * delta_time:
                        pellet.age = pellet.max_age if pellet.max_age else 1000 # Force death
                        
                elif disease.disease_type == DiseaseType.TOXIN_BLOOM:
                    # Increase toxicity
                    pellet.traits.toxicity = min(1.0, pellet.traits.toxicity + 0.1 * delta_time)
                
                # Check end of disease
                if infection.time_in_stage >= disease.duration:
                    if random.random() < disease.mortality_rate:
                        pellet.age = pellet.max_age if pellet.max_age else 1000
                    else:
                        pellet.active_infection = None # Recovered

    def _handle_transmission(self, delta_time: float, creatures: List['BattleCreature'], resources: List[Pellet]):
        """Handle disease spread between entities."""
        # This is O(N^2) which is expensive. We should use the spatial grid.
        # For now, we'll use a simplified check or rely on the spatial grid passed from battle.
        
        # Optimization: Only check infected entities spreading to others
        infected_creatures = [c for c in creatures if c.is_alive() and 
                            hasattr(c.creature, 'active_infection') and 
                            c.creature.active_infection]
                            
        infected_pellets = [p for p in resources if 
                          hasattr(p, 'active_infection') and 
                          p.active_infection]
        
        if not infected_creatures and not infected_pellets:
            return

        # Spread from creatures
        for carrier in infected_creatures:
            infection = carrier.creature.active_infection
            disease = infection.disease
            
            # Only spread if contagious (Incubating or Symptomatic)
            if infection.stage == InfectionStage.RECOVERING:
                continue
                
            # Check nearby creatures
            # Ideally use spatial grid query here. 
            # For this implementation, we'll assume the caller handles spatial queries 
            # or we do a naive check if N is small.
            # Let's do a naive check for now, assuming N < 100.
            
            for target in creatures:
                if target == carrier or not target.is_alive():
                    continue
                    
                dist = carrier.spatial.position.distance_to(target.spatial.position)
                if dist <= disease.contagion_radius:
                    # Check immunity first
                    immunity = target.creature.base_immunity
                    
                    # Check specific acquired immunity
                    if hasattr(target.creature, 'immune_memory'):
                        # Check for exact strain match
                        if disease.disease_id in target.creature.immune_memory:
                            immunity += target.creature.immune_memory[disease.disease_id]
                        
                        # Check for parent strain match (partial immunity)
                        elif disease.parent_id and disease.parent_id in target.creature.immune_memory:
                            immunity += target.creature.immune_memory[disease.parent_id] * 0.5
                            
                    # Effective transmission chance
                    # Higher immunity = lower chance
                    chance = disease.transmission_rate * (1.0 - min(0.9, immunity)) * delta_time
                    
                    if random.random() < chance:
                        # Successful transmission!
                        
                        # Check for mutation
                        final_disease = disease
                        if random.random() < disease.mutation_chance:
                            final_disease = disease.mutate()
                            # Log mutation (optional, could be spammy)
                            # print(f"MUTATION: {disease.name} -> {final_disease.name}")
                            
                        self.infect_creature(target.creature, final_disease)

        # Spread from pellets (Blight spreads to other pellets)
        for carrier in infected_pellets:
            infection = carrier.active_infection
            disease = infection.disease
            
            if disease.disease_type in [DiseaseType.BLIGHT, DiseaseType.ROT]:
                for target in resources:
                    if target == carrier:
                        continue
                        
                    # Simple distance check (Pellet doesn't have distance_to method usually, need manual calc)
                    dx = carrier.x - target.x
                    dy = carrier.y - target.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist <= disease.contagion_radius:
                        chance = disease.transmission_rate * delta_time
                        if random.random() < chance:
                            self.infect_pellet(target, disease)
