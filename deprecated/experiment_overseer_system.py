"""
Experiment Overseer System - Sci-Fi Experimentation Layer

Allows the player (Overseer) to collect Bio-Data from the simulation
and execute experimental protocols (powers) on the subjects.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
import random
import math

from src.systems.battle_spatial import BattleEvent, BattleEventType, SpatialBattle, BattleCreature
from src.models.creature import Creature
from src.models.pellet import create_random_pellet
from src.models.spatial import Vector2D
from src.models.trait import Trait

class ProtocolType(Enum):
    """Types of experimental protocols available to the Overseer."""
    DISPENSE_NUTRIENTS = "dispense_nutrients"  # Feed
    NEURAL_SHOCK = "neural_shock"              # Damage/Punish
    GENETIC_BOOST = "genetic_boost"            # Heal/Buff
    INDUCE_MUTATION = "induce_mutation"        # Force Evolution
    SAMPLE_COLLECTION = "sample_collection"    # Click to gain data

class Protocol:
    """Defines a specific protocol's properties."""
    def __init__(self, name: str, protocol_type: ProtocolType, cost: int, cooldown: float, description: str):
        self.name = name
        self.protocol_type = protocol_type
        self.cost = cost
        self.cooldown = cooldown
        self.description = description
        self.current_cooldown = 0.0

    def is_ready(self) -> bool:
        return self.current_cooldown <= 0

class ExperimentOverseer:
    """
    Manages the player's interaction with the simulation as an Overseer.
    
    Tracks Bio-Data, manages Protocol cooldowns, and handles input execution.
    """
    
    def __init__(self, battle: SpatialBattle):
        self.battle = battle
        
        # Resources
        self.bio_data: float = 50.0
        self.max_bio_data: float = 200.0
        self.passive_data_generation: float = 1.0  # Per second
        
        # Protocols (Powers)
        self.protocols: Dict[ProtocolType, Protocol] = {
            ProtocolType.DISPENSE_NUTRIENTS: Protocol(
                "Nutrient Drop", 
                ProtocolType.DISPENSE_NUTRIENTS, 
                cost=15, 
                cooldown=2.0,
                description="Deploy concentrated nutrient pellets."
            ),
            ProtocolType.NEURAL_SHOCK: Protocol(
                "Neural Shock", 
                ProtocolType.NEURAL_SHOCK, 
                cost=25, 
                cooldown=5.0,
                description="Administer high-voltage shock to subject."
            ),
            ProtocolType.GENETIC_BOOST: Protocol(
                "Genetic Boost", 
                ProtocolType.GENETIC_BOOST, 
                cost=40, 
                cooldown=10.0,
                description="Inject regenerative compounds."
            ),
            ProtocolType.INDUCE_MUTATION: Protocol(
                "Induce Mutation", 
                ProtocolType.INDUCE_MUTATION, 
                cost=100, 
                cooldown=30.0,
                description="Force immediate genetic deviation."
            ),
            ProtocolType.SAMPLE_COLLECTION: Protocol(
                "Collect Sample",
                ProtocolType.SAMPLE_COLLECTION,
                cost=0,
                cooldown=1.0,
                description="Extract bio-data directly from subject."
            )
        }
        
        # Event subscription
        self.battle.add_event_callback(self.on_battle_event)
        
        # Feedback messages
        self.messages: List[str] = []
        self.message_timer: float = 0.0

    def update(self, dt: float):
        """Update system state (cooldowns, passive generation)."""
        # Passive generation
        self.bio_data = min(self.max_bio_data, self.bio_data + self.passive_data_generation * dt)
        
        # Cooldowns
        for protocol in self.protocols.values():
            if protocol.current_cooldown > 0:
                protocol.current_cooldown = max(0, protocol.current_cooldown - dt)
                
        # Message cleanup
        if self.messages:
            self.message_timer += dt
            if self.message_timer > 3.0:
                self.messages.pop(0)
                self.message_timer = 0

    def on_battle_event(self, event: BattleEvent):
        """Generate Bio-Data from significant events."""
        gain = 0.0
        
        if event.event_type == BattleEventType.CREATURE_DEATH:
            gain = 15.0
        elif event.event_type == BattleEventType.CREATURE_BIRTH:
            gain = 20.0
        elif event.event_type == BattleEventType.ABILITY_USE:
            gain = 0.5
        elif event.event_type == BattleEventType.DAMAGE_DEALT:
            # Small gain scaled by damage, capped
            damage = event.value or 0
            gain = min(2.0, damage * 0.1)
            
        if gain > 0:
            self.bio_data = min(self.max_bio_data, self.bio_data + gain)

    def execute_protocol(self, protocol_type: ProtocolType, target_pos: Vector2D = None, target_creature: BattleCreature = None) -> bool:
        """
        Attempt to execute a protocol.
        
        Args:
            protocol_type: The protocol to execute
            target_pos: World position for area effects
            target_creature: Specific creature target
            
        Returns:
            True if successful, False otherwise
        """
        protocol = self.protocols.get(protocol_type)
        if not protocol:
            return False
            
        if protocol.current_cooldown > 0:
            self._add_message(f"Protocol {protocol.name} cooling down...")
            return False
            
        if self.bio_data < protocol.cost:
            self._add_message(f"Insufficient Bio-Data for {protocol.name}")
            return False
            
        success = False
        
        # Execute specific logic
        if protocol_type == ProtocolType.DISPENSE_NUTRIENTS:
            success = self._protocol_dispense_nutrients(target_pos)
        elif protocol_type == ProtocolType.NEURAL_SHOCK:
            success = self._protocol_neural_shock(target_creature)
        elif protocol_type == ProtocolType.GENETIC_BOOST:
            success = self._protocol_genetic_boost(target_creature)
        elif protocol_type == ProtocolType.INDUCE_MUTATION:
            success = self._protocol_induce_mutation(target_creature)
        elif protocol_type == ProtocolType.SAMPLE_COLLECTION:
            success = self._protocol_sample_collection(target_creature)
            
        if success:
            self.bio_data -= protocol.cost
            protocol.current_cooldown = protocol.cooldown
            self._add_message(f"Protocol {protocol.name} executed.")
            
        return success

    def _protocol_dispense_nutrients(self, pos: Vector2D) -> bool:
        """Spawn a cluster of high-value pellets."""
        if not pos:
            # Default to random if no pos provided (shouldn't happen with click)
            pos = Vector2D(random.uniform(0, self.battle.arena.width), random.uniform(0, self.battle.arena.height))
            
        # Spawn 3-5 pellets around the point
        count = random.randint(3, 5)
        for _ in range(count):
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            # Clamp to arena
            x = max(0, min(self.battle.arena.width, pos.x + offset_x))
            y = max(0, min(self.battle.arena.height, pos.y + offset_y))
            
            pellet = create_random_pellet(x, y)
            # Boost nutritional value
            pellet.nutritional_value *= 2.0
            pellet.color = (0, 255, 255) # Cyan for synthetic
            self.battle.arena.add_pellet(pellet)
            
        return True

    def _protocol_neural_shock(self, target: BattleCreature) -> bool:
        """Deal direct damage to a subject."""
        if not target or not target.is_alive():
            return False
            
        damage = 25.0
        target.creature.stats.hp -= damage
        
        # Visual event
        self.battle._emit_event(BattleEvent(
            event_type=BattleEventType.DAMAGE_DEALT,
            target=target,
            value=int(damage),
            message=f"Subject {target.creature.name} received Neural Shock!",
            data={'is_protocol': True}
        ))
        
        return True

    def _protocol_genetic_boost(self, target: BattleCreature) -> bool:
        """Heal and buff a subject."""
        if not target or not target.is_alive():
            return False
            
        heal = 50.0
        target.creature.stats.hp = min(target.creature.stats.max_hp, target.creature.stats.hp + heal)
        
        # Apply a temporary buff (simulated by just modifying stats for now, ideally use StatusEffect)
        # For now, let's just heal and give full energy/hunger
        if hasattr(target.creature, 'hunger'):
            target.creature.hunger = getattr(target.creature, 'max_hunger', 100)
            
        self.battle._emit_event(BattleEvent(
            event_type=BattleEventType.HEALING,
            target=target,
            value=int(heal),
            message=f"Subject {target.creature.name} received Genetic Boost!",
            data={'is_protocol': True}
        ))
        
        return True

    def _protocol_induce_mutation(self, target: BattleCreature) -> bool:
        """Force a random mutation on the subject."""
        if not target or not target.is_alive():
            return False
            
        # Use the battle's breeding system to get a mutation if possible, or just inject one
        # We'll manually inject a random trait from the pool
        from src.models.ecosystem_traits import (
            AGGRESSIVE, CAUTIOUS, FORAGER, EFFICIENT_METABOLISM,
            CURIOUS, GLUTTON, VORACIOUS, WANDERER, PICKY_EATER, INDISCRIMINATE_EATER
        )
        
        # Simple pool for now
        pool = [AGGRESSIVE, CAUTIOUS, FORAGER, EFFICIENT_METABOLISM, CURIOUS, GLUTTON, VORACIOUS, WANDERER]
        new_trait = random.choice(pool).copy()
        new_trait.name = f"Mutated {new_trait.name}" # Mark as mutated
        
        target.creature.add_trait(new_trait)
        
        # Also fully heal them as a side effect of the "procedure"
        target.creature.stats.hp = target.creature.stats.max_hp
        
        self.battle._emit_event(BattleEvent(
            event_type=BattleEventType.STATUS_APPLIED,
            target=target,
            message=f"Subject {target.creature.name} forced to mutate: {new_trait.name}!",
            data={'is_protocol': True}
        ))
        
        return True

    def _protocol_sample_collection(self, target: BattleCreature) -> bool:
        """Click a creature to gain bio-data."""
        if not target or not target.is_alive():
            return False
            
        # Gain data
        gain = 25.0
        self.bio_data = min(self.max_bio_data, self.bio_data + gain)
        
        # Small damage to subject from "needle"
        target.creature.stats.hp -= 1.0
        
        self._add_message(f"Sample collected from {target.creature.name}. +{gain} Data")
        return True

    def _add_message(self, msg: str):
        self.messages.append(msg)
        if len(self.messages) > 3:
            self.messages.pop(0)
