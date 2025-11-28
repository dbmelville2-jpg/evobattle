import math
import random
from typing import List, Optional, Tuple, Any, Dict

from src.models.ability import Ability, AbilityType
from src.models.spatial import Vector2D
from src.utils.jit_math import distance_sq
from src.models.injury_tracker import DamageType
from src.models.relationships import RelationshipType
from src.models.skills import SkillType
from src.systems.battle_events import BattleEvent, BattleEventType
from src.systems.battle_managers.event_manager import EventManager

class CombatManager:
    """
    Manages combat mechanics for the spatial battle system.
    
    Handles:
    - Attack attempts and range checks
    - Ability execution and energy costs
    - Damage calculation and type effectiveness
    - Accuracy and dodge mechanics
    - Relationship-based damage modifiers
    """
    
    # Type effectiveness chart
    TYPE_EFFECTIVENESS = {
        'fire': {'grass': 2.0, 'water': 0.5, 'ice': 2.0},
        'water': {'fire': 2.0, 'grass': 0.5, 'ground': 2.0},
        'grass': {'water': 2.0, 'fire': 0.5, 'ground': 2.0},
        'electric': {'water': 2.0, 'flying': 2.0, 'ground': 0.0},
        'ice': {'grass': 2.0, 'ground': 2.0, 'flying': 2.0, 'fire': 0.5},
        'fighting': {'normal': 2.0, 'ice': 2.0, 'flying': 0.5},
        'flying': {'fighting': 2.0, 'grass': 2.0, 'electric': 0.5},
        'psychic': {'fighting': 2.0, 'poison': 2.0},
        'dark': {'psychic': 2.0, 'fighting': 0.5},
        'steel': {'ice': 2.0, 'fairy': 2.0, 'fire': 0.5}
    }

    def __init__(
        self, 
        event_manager: EventManager,
        combat_config: Any,
        trait_effects_handler: Any,
        enhancer: Optional[Any] = None
    ):
        self.event_manager = event_manager
        self.combat_config = combat_config
        self.trait_effects = trait_effects_handler
        self.enhancer = enhancer
        self.DEBUG = False

    def attempt_attack(self, attacker: Any, defender: Any, current_time: float, creatures_list: List[Any]):
        """Attempt an attack from attacker to defender."""
        # Safety check: Never attack self
        if attacker == defender:
            if self.DEBUG:
                self.event_manager.log(f"[DEBUG] {attacker.creature.name} tried to attack self - blocked")
            return
        
        # Choose ability
        usable_abilities = [
            a for a in attacker.creature.abilities
            if a is not None and a.can_use(attacker.creature.stats, attacker.creature.energy)
        ]
        
        if usable_abilities:
            ability = max(usable_abilities, key=lambda a: a.power)
        else:
            # Basic attack
            ability = Ability(name="Basic Attack", power=10, accuracy=100)
        
        # Check range - INCREASED from 3.0 to 4.5 to account for separation forces
        # Attack ranges should be larger than separation force threshold (2.5) to allow attacks
        attack_range = 4.5  # Increased from 3.0 - melee range
        if ability.ability_type == AbilityType.PHYSICAL:
            attack_range = 4.5  # Increased from 3.0 - melee range
        elif ability.ability_type == AbilityType.SPECIAL:
            attack_range = self.combat_config.base_attack_range_ranged  # 8.0 - ranged attack
        
        # JIT distance check
        dist_sq = distance_sq(attacker.spatial.position.x, attacker.spatial.position.y,
                            defender.spatial.position.x, defender.spatial.position.y)
        
        if self.DEBUG and random.random() < 0.05:  # 5% chance to log
            distance = math.sqrt(dist_sq)
            self.event_manager.log(f"[DEBUG] {attacker.creature.name} attempting {ability.name} on {defender.creature.name} at distance {distance:.2f} (range: {attack_range})")
        
        if dist_sq > attack_range * attack_range:
            # Debug: Log why attack failed
            if self.DEBUG and random.random() < 0.05:  # 5% chance to log
                distance = math.sqrt(dist_sq)
                self.event_manager.log(f"[DEBUG] {attacker.creature.name} too far to attack {defender.creature.name}: {distance:.2f} > {attack_range}")
            return  # Too far to attack
        
        # Execute attack
        if self.DEBUG and random.random() < 0.1:  # 10% chance to log successful attacks
            self.event_manager.log(f"[DEBUG] {attacker.creature.name} EXECUTING {ability.name} on {defender.creature.name}!")
        
        # We need to pass handle_death_callback to execute_ability if it kills
        # But handle_death is in LifecycleManager. 
        # For now, execute_ability returns a boolean indicating if target died, 
        # and the caller (SpatialBattle) handles the death.
        
        died = self.execute_ability(attacker, defender, ability, creatures_list)
        attacker.last_attack_time = current_time
        return died

    def execute_ability(
        self,
        attacker: Any,
        defender: Any,
        ability: Ability,
        creatures_list: List[Any]
    ) -> bool:
        """
        Execute an ability from attacker to defender.
        Returns True if the defender died.
        """
        self.event_manager.log(f"{attacker.creature.name} uses {ability.name}!")
        self.event_manager.emit_event(BattleEvent(
            event_type=BattleEventType.ABILITY_USE,
            actor=attacker,
            target=defender,
            ability=ability,
            message=f"{attacker.creature.name} uses {ability.name}!",
            data={'distance': attacker.spatial.distance_to(defender.spatial)}
        ))
        
        # Use ability
        ability.use()
        attacker.creature.energy = max(0, attacker.creature.energy - ability.energy_cost)
        
        # Check accuracy with dodge modifier
        hit = self._check_accuracy(ability.accuracy)
        
        # Apply dodge skill - defender can evade based on skill level
        if hit:
            dodge_skill = defender.creature.skills.get_skill(SkillType.DODGE)
            dodge_chance = dodge_skill.get_success_chance_bonus()  # 0-15% bonus
            
            # Apply living world dodge chance
            if self.enhancer:
                dodge_chance += self.enhancer.calculate_dodge_chance_modifier(defender.creature)
            
            # Convert percentage to probability
            if random.random() < (dodge_chance / 100.0):
                hit = False
                # Successful dodge - gain dodge skill experience
                difficulty = attacker.creature.stats.attack / max(1, defender.creature.stats.defense)
                defender.creature.skills.use_skill(SkillType.DODGE, difficulty=difficulty, success=True)
            else:
                # Failed to dodge - still gain some experience
                difficulty = attacker.creature.stats.attack / max(1, defender.creature.stats.defense)
                defender.creature.skills.use_skill(SkillType.DODGE, difficulty=difficulty, success=False)
        
        if not hit:
            self.event_manager.log(f"{ability.name} missed!")
            self.event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.MISS,
                actor=attacker,
                target=defender,
                ability=ability,
                message=f"{ability.name} missed!"
            ))
            # Record miss for living world
            if self.enhancer:
                self.enhancer.on_attack_made(
                    attacker.creature,
                    defender.creature,
                    damage=0,
                    was_critical=False,
                    hit=False
                )
            return False
        
        # Apply damage or effects
        if ability.ability_type in [AbilityType.PHYSICAL, AbilityType.SPECIAL]:
            damage, was_critical = self.calculate_damage(attacker, defender, ability, creatures_list)
            
            # Apply relationship-based damage modifiers
            damage = self._apply_relationship_damage_modifier(attacker, defender, damage, creatures_list)
            
            was_alive_before_damage = defender.is_alive()
            health_before = defender.creature.stats.hp
            actual_damage = defender.creature.stats.take_damage(damage)
            health_after = defender.creature.stats.hp
            self.event_manager.log(f"{defender.creature.name} takes {int(actual_damage)} damage! (HP: {int(defender.creature.stats.hp)}/{int(defender.creature.stats.max_hp)})")
            
            # Record injury for inspector stats
            damage_type = DamageType.PHYSICAL if ability.ability_type == AbilityType.PHYSICAL else DamageType.SPECIAL
            defender.creature.injury_tracker.record_injury(
                attacker_id=attacker.creature.creature_id,
                attacker_name=attacker.creature.name,
                damage_type=damage_type,
                damage_amount=actual_damage,
                health_before=health_before,
                health_after=health_after,
                was_critical=was_critical,
                location=(defender.spatial.position.x, defender.spatial.position.y)
            )
            
            # Record combat memory for both creatures
            attacker.creature.combat_memory.record_attacked(
                defender.creature.creature_id,
                actual_damage,
                killed=(was_alive_before_damage and not defender.is_alive())
            )
            defender.creature.combat_memory.record_attacked_by(
                attacker.creature.creature_id,
                actual_damage
            )
            
            # Record battle history for inspector
            if hasattr(attacker.creature, 'history'):
                attacker.creature.history.record_attack(
                    defender.creature.creature_id,
                    actual_damage,
                    was_critical=was_critical
                )
            if hasattr(defender.creature, 'history'):
                defender.creature.history.record_damage_taken(
                    attacker.creature.creature_id,
                    actual_damage
                )
            
            # Record attack for living world
            if self.enhancer:
                self.enhancer.on_attack_made(
                    attacker.creature,
                    defender.creature,
                    actual_damage,
                    was_critical,
                    hit=True
                )
            
            self.event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.DAMAGE_DEALT,
                actor=attacker,
                target=defender,
                ability=ability,
                value=actual_damage,
                message=f"{defender.creature.name} takes {actual_damage} damage!",
                data={'remaining_hp': defender.creature.stats.hp, 'max_hp': defender.creature.stats.max_hp}
            ))
            
            # Only count death if creature was alive before this attack
            if was_alive_before_damage and not defender.is_alive():
                return True # Signal that defender died
        
        elif ability.ability_type == AbilityType.HEALING:
            heal_amount = ability.power
            actual_heal = attacker.creature.stats.heal(heal_amount)
            self.event_manager.log(f"{attacker.creature.name} heals {actual_heal} HP!")
            
            self.event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.HEALING,
                actor=attacker,
                value=actual_heal,
                message=f"{attacker.creature.name} heals {actual_heal} HP!"
            ))
            
        return False

    def calculate_damage(
        self,
        attacker: Any,
        defender: Any,
        ability: Ability,
        creatures_list: List[Any]
    ) -> Tuple[int, bool]:
        """
        Calculate damage (reuses turn-based formula).
        
        Returns:
            Tuple of (damage, was_critical)
        """
        base_damage = ability.calculate_damage(
            attacker.creature.stats.attack,
            defender.creature.stats.defense
        )
        
        # Type effectiveness
        effectiveness = self.get_type_effectiveness(attacker.creature, defender.creature)
        damage = int(base_damage * effectiveness)
        
        if effectiveness > 1.0:
            self.event_manager.log("It's super effective!")
            self.event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.SUPER_EFFECTIVE,
                message="It's super effective!",
                data={'effectiveness': effectiveness}
            ))
        elif effectiveness < 1.0 and effectiveness > 0:
            self.event_manager.log("It's not very effective...")
            self.event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.NOT_EFFECTIVE,
                message="It's not very effective...",
                data={'effectiveness': effectiveness}
            ))
        
        # Random variance
        damage = int(damage * random.uniform(0.85, 1.0))
        
        # Apply melee attack skill - improves damage output
        melee_skill = attacker.creature.skills.get_skill(SkillType.MELEE_ATTACK)
        difficulty = defender.creature.stats.defense / max(1, attacker.creature.stats.attack)
        skill_modifier = melee_skill.use(difficulty=difficulty, success=True)
        damage = int(damage * skill_modifier)
        
        # Teamwork Skill: Bonus damage for nearby allies
        teamwork_skill = attacker.creature.skills.get_skill(SkillType.TEAMWORK)
        if teamwork_skill.level > 0 and creatures_list:
            nearby_allies = 0
            # Check for allies within range (5.0 units)
            attacker_pos = attacker.spatial.position
            for other in creatures_list:
                if other == attacker or other == defender:
                    continue
                
                # Check alliance (same strain)
                if other.creature.strain_id == attacker.creature.strain_id:
                    dist_sq = (attacker_pos.x - other.spatial.position.x)**2 + \
                              (attacker_pos.y - other.spatial.position.y)**2
                    if dist_sq < 25.0:  # 5.0 radius
                        nearby_allies += 1
            
            if nearby_allies > 0:
                # Bonus: 5% per ally * skill modifier (max 3 allies counted)
                ally_bonus = 0.05 * min(3, nearby_allies) * teamwork_skill.get_performance_modifier()
                damage = int(damage * (1.0 + ally_bonus))
                
                # Gain Teamwork XP
                teamwork_skill.use(difficulty=1.0, success=True)
                
        # Intimidation Skill: Chance to demoralize enemy (bonus damage)
        intimidation_skill = attacker.creature.skills.get_skill(SkillType.INTIMIDATION)
        if intimidation_skill.level > 0:
            # Chance to intimidate: Base 10% + 0.5% per level (max 60%)
            chance = 0.10 + (intimidation_skill.level * 0.005)
            if random.random() < chance:
                # Intimidated! Deal 20% bonus damage
                damage = int(damage * 1.2)
                intimidation_skill.use(difficulty=1.0, success=True)
                self.event_manager.log(f"{attacker.creature.name} intimidates {defender.creature.name}!")
        
        # Critical hit with skill-based modifiers
        crit_skill = attacker.creature.skills.get_skill(SkillType.CRITICAL_STRIKE)
        crit_chance = 0.0625  # Base 6.25% chance
        crit_chance += crit_skill.get_success_chance_bonus() / 100.0  # Add skill bonus (0-15%)
        
        is_critical = random.random() < crit_chance
        if is_critical:
            # Use critical strike skill and apply its modifier
            crit_modifier = crit_skill.use(difficulty=difficulty, success=True)
            damage = int(damage * 1.5 * crit_modifier)
            self.event_manager.log("Critical hit!")
            self.event_manager.emit_event(BattleEvent(
                event_type=BattleEventType.CRITICAL_HIT,
                message="Critical hit!"
            ))
        
        
        # Apply living world damage modifiers
        if self.enhancer:
            damage = self.enhancer.calculate_damage_modifier(
                attacker.creature,
                defender.creature,
                damage,
                is_critical
            )
        
        # Apply trait interaction_effects modifiers (pack hunter, loner, etc.)
        # Use cached ally/enemy data from attacker's BattleCreature to avoid expensive queries
        # These are updated during creature logic updates, not on every attack
        allies_nearby_count = 0
        enemies_nearby_count = 0
        family_nearby_count = 0
        
        # Try to use cached data if available (set during _update_creature_logic)
        if hasattr(attacker, '_cached_allies_count'):
            allies_nearby_count = attacker._cached_allies_count
            enemies_nearby_count = attacker._cached_enemies_count
            family_nearby_count = attacker._cached_family_count
        else:
            # Fallback: calculate now (but this is expensive)
            # We need a way to get allies/enemies here. 
            # For now, we'll skip this fallback or implement a simple distance check if needed.
            # Assuming _cached_allies_count is usually populated.
            pass
        
        trait_modifier = self.trait_effects.get_combat_damage_modifier(
            attacker.creature,
            defender.creature,
            allies_nearby=allies_nearby_count,
            enemies_nearby=enemies_nearby_count,
            family_nearby=family_nearby_count
        )
        damage = int(damage * trait_modifier)
        
        return max(1, int(damage)), is_critical

    def get_type_effectiveness(
        self,
        attacker: Any,
        defender: Any
    ) -> float:
        """Calculate type effectiveness multiplier."""
        if not attacker.creature_type.type_tags:
            return 1.0
        
        attacker_type = attacker.creature_type.type_tags[0]
        effectiveness = 1.0
        
        if attacker_type in self.TYPE_EFFECTIVENESS:
            for defender_type in defender.creature_type.type_tags:
                if defender_type in self.TYPE_EFFECTIVENESS[attacker_type]:
                    effectiveness *= self.TYPE_EFFECTIVENESS[attacker_type][defender_type]
        
        return effectiveness

    def _check_accuracy(self, accuracy: int) -> bool:
        """Check if an ability hits."""
        return random.randint(1, 100) <= accuracy

    def _apply_relationship_damage_modifier(
        self,
        attacker: Any,
        defender: Any,
        base_damage: int,
        creatures_list: List[Any]
    ) -> int:
        """
        Apply damage modifiers based on relationships and combat context.
        """
        modifier = 1.0
        
        # Check for revenge bonus
        relationship = attacker.creature.relationships.get_relationship(
            defender.creature.creature_id
        )
        if relationship:
            if relationship.relationship_type == RelationshipType.REVENGE_TARGET:
                modifier += self.combat_config.revenge_damage_bonus
            elif relationship.relationship_type == RelationshipType.RIVAL:
                modifier += self.combat_config.rival_damage_bonus
            
            # Get combat modifier from relationship
            combat_mod = relationship.get_combat_modifier(fighting_together=False)
            modifier *= combat_mod
        
        # Check for ally support bonus (nearby allies boost damage)
        # We need to find allies nearby.
        # This is expensive without the spatial grid or helper methods.
        # We can use the cached count if available, but that doesn't give us the list of allies to check for family protection.
        # For now, we will rely on the cached counts for the gang up bonus, but might miss the family protection logic if we don't have the list.
        # To properly implement family protection, we need access to the spatial grid or a helper to find neighbors.
        # Since we passed creatures_list, we can iterate, but that's O(N).
        # Ideally, CombatManager should have access to the spatial grid or a "get_neighbors" callback.
        
        # Simplified implementation using cached counts for gang up:
        if hasattr(attacker, '_cached_allies_count'):
             if attacker._cached_allies_count >= self.combat_config.gang_up_threshold:
                gang_bonus = 1.0 + (attacker._cached_allies_count * self.combat_config.gang_up_damage_bonus)
                modifier *= gang_bonus
             elif attacker._cached_allies_count > 0:
                modifier += self.combat_config.ally_support_bonus
        
        # Family protection logic is complex to extract without full context.
        # We'll omit the detailed family protection scan for now to avoid O(N) scan here, 
        # or we could add a 'nearby_allies' argument to attempt_attack if we want to pass it in.
        
        return int(base_damage * modifier)
