"""
Disease Model - Core definitions for the disease system.

This module defines the types of diseases, their properties, and the state of
infections in entities (creatures and pellets).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict
import time
import uuid

class DiseaseType(Enum):
    """Types of diseases available in the system."""
    # Creature Diseases
    PLAGUE = "plague"           # High mortality, fast spread
    WASTING = "wasting"         # Low mortality, stat drain
    PARASITE = "parasite"       # Hunger drain, energy drain
    
    # Pellet Diseases
    BLIGHT = "blight"           # Kills pellets
    TOXIN_BLOOM = "toxin_bloom" # Makes pellets toxic
    ROT = "rot"                 # Increases decay rate

class InfectionStage(Enum):
    """Stages of infection progression."""
    INCUBATING = "incubating"   # Infected but no symptoms, contagious
    SYMPTOMATIC = "symptomatic" # Visible symptoms, high contagion, effects active
    RECOVERING = "recovering"   # Effects fading, immune to reinfection
    IMMUNE = "immune"           # Fully recovered, permanent/temporary immunity

@dataclass
class Disease:
    """
    Defines the properties of a specific disease.
    """
    disease_id: str
    name: str
    disease_type: DiseaseType
    description: str
    
    # Transmission
    contagion_radius: float = 15.0
    transmission_rate: float = 0.3  # Chance per second of contact
    
    # Progression (in seconds)
    incubation_time: float = 5.0
    duration: float = 20.0
    
    # Effects
    mortality_rate: float = 0.3     # Chance to die at end of disease
    hp_drain_rate: float = 1.0      # HP lost per second (symptomatic)
    stat_penalty: float = 0.2       # % reduction in stats (speed, damage)
    
    # Visuals
    color_tint: tuple = (100, 255, 100)  # RGB tint for infected entities
    
    # Evolution
    mutation_chance: float = 0.1    # Chance to mutate on transmission
    generation: int = 0             # Evolution generation
    parent_id: Optional[str] = None # ID of parent strain
    
    def mutate(self) -> 'Disease':
        """
        Create a mutated version of this disease.
        Returns a new Disease instance with slightly altered stats.
        """
        import random
        import uuid
        
        # Create new ID
        new_id = f"{self.disease_type.value}_{uuid.uuid4().hex[:6]}"
        new_gen = self.generation + 1
        
        # Strip existing generation suffix to avoid accumulation
        # e.g., "Red Plague (Gen 1)" -> "Red Plague"
        import re
        base_name = re.sub(r'\s*\(Gen \d+\)\s*$', '', self.name).strip()
        new_name = f"{base_name} (Gen {new_gen})"
        
        # Clone and mutate stats
        # Mutation factor: 0.8 to 1.2 (±20% change)
        def mutate_val(val: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
            factor = random.uniform(0.9, 1.15) # Slight bias towards strengthening
            return max(min_val, min(max_val, val * factor))
            
        new_disease = Disease(
            disease_id=new_id,
            name=new_name,
            disease_type=self.disease_type,
            description=self.description,
            
            # Mutate transmission
            contagion_radius=mutate_val(self.contagion_radius, 5.0, 50.0),
            transmission_rate=mutate_val(self.transmission_rate, 0.05, 0.95),
            
            # Mutate progression
            incubation_time=mutate_val(self.incubation_time, 1.0, 60.0),
            duration=mutate_val(self.duration, 5.0, 120.0),
            
            # Mutate effects
            mortality_rate=mutate_val(self.mortality_rate, 0.0, 1.0),
            hp_drain_rate=mutate_val(self.hp_drain_rate, 0.0, 20.0),
            stat_penalty=mutate_val(self.stat_penalty, 0.0, 0.9),
            
            # Visuals (shift tint slightly)
            color_tint=self.color_tint,
            
            # Evolution
            mutation_chance=self.mutation_chance, # Mutation chance stays same
            generation=new_gen,
            parent_id=self.disease_id
        )
        
        return new_disease

@dataclass
class Infection:
    """
    Tracks the state of an active infection in an entity.
    """
    disease: Disease
    infected_at: float = field(default_factory=time.time)
    stage: InfectionStage = InfectionStage.INCUBATING
    time_in_stage: float = 0.0
    
    def update(self, delta_time: float):
        """Update infection timer."""
        self.time_in_stage += delta_time
        
    def get_total_duration(self, current_time: float) -> float:
        """Get total time infected."""
        return current_time - self.infected_at

# Predefined Disease Definitions
DISEASE_DEFINITIONS = {
    DiseaseType.PLAGUE: Disease(
        disease_id="plague_01",
        name="Red Plague",
        disease_type=DiseaseType.PLAGUE,
        description="A deadly pathogen that spreads rapidly in dense populations.",
        contagion_radius=20.0,
        transmission_rate=0.4,
        incubation_time=5.0,
        duration=15.0,
        mortality_rate=0.5,
        hp_drain_rate=3.0,
        stat_penalty=0.4,
        color_tint=(255, 100, 100)
    ),
    DiseaseType.WASTING: Disease(
        disease_id="wasting_01",
        name="Wasting Sickness",
        disease_type=DiseaseType.WASTING,
        description="A chronic condition that weakens the host over time.",
        contagion_radius=15.0,
        transmission_rate=0.2,
        incubation_time=10.0,
        duration=30.0,
        mortality_rate=0.2,
        hp_drain_rate=1.0,
        stat_penalty=0.3,
        color_tint=(200, 200, 150)
    ),
    DiseaseType.PARASITE: Disease(
        disease_id="parasite_01",
        name="Energy Parasite",
        disease_type=DiseaseType.PARASITE,
        description="A parasite that drains host energy and hunger.",
        contagion_radius=10.0,
        transmission_rate=0.25,
        incubation_time=5.0,
        duration=25.0,
        mortality_rate=0.1,
        hp_drain_rate=0.5,
        stat_penalty=0.1,
        color_tint=(150, 100, 255)
    ),
    DiseaseType.BLIGHT: Disease(
        disease_id="blight_01",
        name="Floral Blight",
        disease_type=DiseaseType.BLIGHT,
        description="A fungal infection that destroys plant life.",
        contagion_radius=15.0,
        transmission_rate=0.3,
        incubation_time=3.0,
        duration=10.0,
        mortality_rate=0.8, # High chance to kill pellet
        hp_drain_rate=0.0,
        stat_penalty=0.0,
        color_tint=(100, 100, 100)
    ),
    DiseaseType.TOXIN_BLOOM: Disease(
        disease_id="toxin_01",
        name="Toxic Bloom",
        disease_type=DiseaseType.TOXIN_BLOOM,
        description="Causes plants to produce dangerous toxins.",
        contagion_radius=12.0,
        transmission_rate=0.3,
        incubation_time=5.0,
        duration=20.0,
        mortality_rate=0.1,
        hp_drain_rate=0.0,
        stat_penalty=0.0, # Used for toxicity increase
        color_tint=(150, 0, 150)
    )
}
