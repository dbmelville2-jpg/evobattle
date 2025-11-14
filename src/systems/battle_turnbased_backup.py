"""
Battle system - Handles combat mechanics and battle simulation.

Supports both instant simulation and real-time step-by-step execution
for animated/visual battles.
"""

from typing import List, Optional, Dict, Tuple, Any, Callable
from enum import Enum
import random
import time

from ..models.creature import Creature
from ..models.ability import Ability, AbilityType, TargetType
from ..models.status_effect import StatusEffect, StatusEffectType
from ..models.stats import StatModifier


class BattleEventType(Enum):
    """Types of battle events for animation/visualization."""
    BATTLE_START = "battle_start"
    TURN_START = "turn_start"
    CREATURE_TURN = "creature_turn"
    ABILITY_USE = "ability_use"
    DAMAGE_DEALT = "damage_dealt"
    HEALING = "healing"
    STATUS_APPLIED = "status_applied"
    STATUS_DAMAGE = "status_damage"
    BUFF_APPLIED = "buff_applied"
    DEBUFF_APPLIED = "debuff_applied"
    MISS = "miss"
    CRITICAL_HIT = "critical_hit"
    SUPER_EFFECTIVE = "super_effective"
    NOT_EFFECTIVE = "not_effective"
    CREATURE_FAINT = "creature_faint"
    TURN_END = "turn_end"
    BATTLE_END = "battle_end"


class BattleEvent:
    """
    Represents a single event in battle for animation/visualization.
    
    Events can be used to trigger animations, sound effects, or UI updates.
    """
    
    def __init__(
        self,
        event_type: BattleEventType,
        actor: Optional[Creature] = None,
        target: Optional[Creature] = None,
        ability: Optional[Ability] = None,
        value: Optional[int] = None,
        message: str = "",
        data: Optional[Dict] = None
    ):
        self.event_type = event_type
        self.actor = actor
        self.target = target
        self.ability = ability
        self.value = value
        self.message = message
        self.data = data or {}
        self.timestamp = time.time()
    
    def __repr__(self):
        return f"BattleEvent({self.event_type.value}: {self.message})"


class BattlePhase(Enum):
    """Phases of a battle turn."""
    START = "start"
    TURN_SELECTION = "turn_selection"
    ACTION = "action"
    END_OF_TURN = "end_of_turn"
    BATTLE_END = "battle_end"


class BattleAction:
    """
    Represents an action taken by a creature in battle.
    
    Attributes:
        creature: The creature taking the action
        action_type: Type of action (ability, item, switch, flee)
        target: The target of the action
        ability: The ability being used (if applicable)
    """
    
    def __init__(
        self,
        creature: Creature,
        action_type: str = "ability",
        target: Optional[Creature] = None,
        ability: Optional[Ability] = None
    ):
        self.creature = creature
        self.action_type = action_type
        self.target = target
        self.ability = ability


class BattleState:
    """
    Manages the state of an active battle.
    
    Tracks participants, turn order, active effects, and battle progress.
    
    Attributes:
        player_team: List of creatures on player's team
        enemy_team: List of creatures on enemy's team
        current_turn: Current turn number
        phase: Current battle phase
        weather: Current weather condition affecting battle
        terrain: Current terrain affecting battle
        events: List of battle events for visualization
    """
    
    def __init__(
        self,
        player_team: List[Creature],
        enemy_team: List[Creature]
    ):
        self.player_team = player_team
        self.enemy_team = enemy_team
        self.current_turn = 0
        self.phase = BattlePhase.START
        self.weather = None
        self.terrain = None
        self.status_effects: Dict[str, List[StatusEffect]] = {}
        self.events: List[BattleEvent] = []
        
        # Initialize status effects for all creatures
        for creature in player_team + enemy_team:
            self.status_effects[creature.creature_id] = []
    
    def get_active_player(self) -> Optional[Creature]:
        """Get the current active creature for player team."""
        for creature in self.player_team:
            if creature.is_alive():
                return creature
        return None
    
    def get_active_enemy(self) -> Optional[Creature]:
        """Get the current active creature for enemy team."""
        for creature in self.enemy_team:
            if creature.is_alive():
                return creature
        return None
    
    def is_battle_over(self) -> bool:
        """Check if battle has ended."""
        player_alive = any(c.is_alive() for c in self.player_team)
        enemy_alive = any(c.is_alive() for c in self.enemy_team)
        return not (player_alive and enemy_alive)
    
    def get_winner(self) -> Optional[str]:
        """
        Determine the winner of the battle.
        
        Returns:
            'player', 'enemy', or None if battle not over
        """
        if not self.is_battle_over():
            return None
        
        player_alive = any(c.is_alive() for c in self.player_team)
        return 'player' if player_alive else 'enemy'


class Battle:
    """
    Manages turn-based combat between creature teams.
    
    The battle system determines combat outcomes based on creature stats,
    abilities, traits, and random factors. It handles turn order, damage
    calculation, special abilities, status effects, and victory conditions.
    
    Attributes:
        state: Current battle state
        battle_log: Record of all battle actions and events
        random_seed: Seed for random number generation (for determinism)
        type_effectiveness: Type matchup chart for damage calculation
    """
    
    # Type effectiveness chart (multiplier for damage)
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
        player_team: List[Creature],
        enemy_team: List[Creature],
        random_seed: Optional[int] = None
    ):
        """
        Initialize a new Battle.
        
        Args:
            player_team: List of creatures on player's team
            enemy_team: List of creatures on enemy's team
            random_seed: Optional seed for reproducible randomness
        """
        self.state = BattleState(player_team, enemy_team)
        self.battle_log: List[str] = []
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
        
        self._started = False
        self._current_turn_order: List[Creature] = []
        self._current_action_index = 0
        self._event_callbacks: List[Callable[[BattleEvent], None]] = []
        
        # Log battle start
        self._log(f"Battle started: {len(player_team)} vs {len(enemy_team)}")
    
    def add_event_callback(self, callback: Callable[[BattleEvent], None]):
        """
        Register a callback function to be called for each battle event.
        
        This allows for real-time visualization/animation of battle events.
        
        Args:
            callback: Function that takes a BattleEvent as parameter
            
        Example:
            def on_event(event):
                if event.event_type == BattleEventType.DAMAGE_DEALT:
                    print(f"{event.target.name} took {event.value} damage!")
            
            battle.add_event_callback(on_event)
        """
        self._event_callbacks.append(callback)
    
    def _emit_event(self, event: BattleEvent):
        """
        Emit a battle event to all registered callbacks.
        
        Args:
            event: The battle event to emit
        """
        self.state.events.append(event)
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                # Don't let callback errors break the battle
                self._log(f"Error in event callback: {e}")
    
    def _log(self, message: str):
        """Add a message to the battle log."""
        self.battle_log.append(message)
    
    def start_battle(self):
        """
        Initialize the battle and prepare for step-by-step execution.
        
        This method should be called before executing turns step by step.
        """
        if self._started:
            return
        
        self._started = True
        self._log("=== Battle Begin ===")
        
        # Emit battle start event
        player = self.state.get_active_player()
        enemy = self.state.get_active_enemy()
        self._emit_event(BattleEvent(
            event_type=BattleEventType.BATTLE_START,
            actor=player,
            target=enemy,
            message="Battle begins!",
            data={
                'player_team': [c.name for c in self.state.player_team],
                'enemy_team': [c.name for c in self.state.enemy_team]
            }
        ))
        
        self._phase_start()
    
    def is_ready_for_action(self) -> bool:
        """
        Check if the battle is ready for the next action.
        
        Returns:
            True if battle has started and is not over
        """
        return self._started and not self.state.is_battle_over()
    
    def get_next_actor(self) -> Optional[Creature]:
        """
        Get the creature that will act next.
        
        Returns:
            The creature that will take the next action, or None if turn needs to be set up
        """
        if not self._current_turn_order or self._current_action_index >= len(self._current_turn_order):
            return None
        return self._current_turn_order[self._current_action_index]
    
    def execute_turn(self) -> bool:
        """
        Execute one complete turn of battle (both creatures act).
        
        This is a step-by-step alternative to simulate(). Call this repeatedly
        until is_battle_over() returns True.
        
        Returns:
            True if battle continues, False if battle has ended
        """
        if not self._started:
            self.start_battle()
        
        if self.state.is_battle_over():
            if self.state.phase != BattlePhase.BATTLE_END:
                self._phase_battle_end()
            return False
        
        self.state.current_turn += 1
        self._log(f"\n--- Turn {self.state.current_turn} ---")
        
        # Process turn
        self._process_turn()
        
        # Check for battle end
        if self.state.is_battle_over():
            self._phase_battle_end()
            return False
        
        return True
    
    def execute_action(self, creature: Creature, ability: Optional[Ability] = None, target: Optional[Creature] = None) -> bool:
        """
        Execute a single action for a specific creature.
        
        This provides fine-grained control for real-time battles where you want
        to execute individual actions with potential delays/animations between them.
        
        Args:
            creature: The creature performing the action
            ability: The ability to use (if None, AI chooses)
            target: The target of the action (if None, automatically selected)
            
        Returns:
            True if action was executed, False if creature cannot act
        """
        if not self._started:
            self.start_battle()
        
        if self.state.is_battle_over():
            return False
        
        # Check if creature can act
        if not creature.is_alive():
            self._log(f"{creature.name} is unable to act (incapacitated)")
            return False
        
        if not self._can_act(creature):
            self._log(f"{creature.name} cannot act due to status effects!")
            return False
        
        # Determine target if not specified
        if target is None:
            player = self.state.get_active_player()
            enemy = self.state.get_active_enemy()
            
            if creature == player:
                target = enemy
            elif creature == enemy:
                target = player
            else:
                # Creature not in active battle
                return False
        
        if not target or not target.is_alive():
            return False
        
        # Execute action
        if ability:
            if not ability.can_use(creature.stats, creature.energy):
                self._log(f"{creature.name} cannot use {ability.name}!")
                return False
            self._execute_ability(creature, target, ability)
        else:
            # AI chooses action
            self._execute_ai_action(creature, target)
        
        return True
    
    def end_turn(self):
        """
        Process end-of-turn effects (status effects, cooldowns, etc.).
        
        Call this after all creatures have acted in a turn.
        """
        player = self.state.get_active_player()
        enemy = self.state.get_active_enemy()
        
        self.state.phase = BattlePhase.END_OF_TURN
        self._phase_end_of_turn(player, enemy)
    
    def simulate(self) -> Creature:
        """
        Simulate the complete battle until one side wins.
        
        Returns:
            The winning creature
        """
        # Use start_battle to ensure events are emitted
        if not self._started:
            self.start_battle()
        else:
            self._log("=== Battle Begin ===")
            self._phase_start()
        
        # Main battle loop
        while not self.state.is_battle_over():
            self.state.current_turn += 1
            self._log(f"\n--- Turn {self.state.current_turn} ---")
            
            # Process turn
            self._process_turn()
            
            # Check for battle end
            if self.state.is_battle_over():
                break
        
        # Battle end phase
        self._phase_battle_end()
        
        winner_side = self.state.get_winner()
        if winner_side == 'player':
            winner = self.state.get_active_player() or self.state.player_team[0]
        else:
            winner = self.state.get_active_enemy() or self.state.enemy_team[0]
        
        self._log(f"\n=== Battle End - Winner: {winner.name} ({winner_side}) ===")
        return winner
    
    def _phase_start(self):
        """Execute battle start phase."""
        self.state.phase = BattlePhase.START
        
        # Log initial creature states
        player = self.state.get_active_player()
        enemy = self.state.get_active_enemy()
        
        if player:
            self._log(f"Player: {player.name} (HP: {player.stats.hp}/{player.stats.max_hp})")
        if enemy:
            self._log(f"Enemy: {enemy.name} (HP: {enemy.stats.hp}/{enemy.stats.max_hp})")
    
    def _process_turn(self):
        """Process a complete battle turn."""
        player = self.state.get_active_player()
        enemy = self.state.get_active_enemy()
        
        if not player or not enemy:
            return
        
        # Turn selection phase
        self.state.phase = BattlePhase.TURN_SELECTION
        
        # Determine turn order based on speed (with random factor for ties)
        turn_order = self._determine_turn_order(player, enemy)
        
        # Action phase - process each creature's action
        self.state.phase = BattlePhase.ACTION
        for creature in turn_order:
            if not creature.is_alive():
                continue
            
            # Check status effects before action
            if not self._can_act(creature):
                self._log(f"{creature.name} cannot act due to status effects!")
                continue
            
            # Get target
            target = enemy if creature == player else player
            
            if not target.is_alive():
                continue
            
            # Choose and execute action
            self._execute_ai_action(creature, target)
            
            # Check if battle ended
            if self.state.is_battle_over():
                break
        
        # End of turn phase
        self.state.phase = BattlePhase.END_OF_TURN
        self._phase_end_of_turn(player, enemy)
    
    def _determine_turn_order(self, player: Creature, enemy: Creature) -> List[Creature]:
        """
        Determine the order of actions for this turn.
        
        Args:
            player: Player's creature
            enemy: Enemy's creature
            
        Returns:
            List of creatures in action order
        """
        player_speed = player.stats.speed
        enemy_speed = enemy.stats.speed
        
        # Add small random factor to break ties
        player_roll = player_speed + random.uniform(-1, 1)
        enemy_roll = enemy_speed + random.uniform(-1, 1)
        
        if player_roll > enemy_roll:
            return [player, enemy]
        else:
            return [enemy, player]
    
    def _can_act(self, creature: Creature) -> bool:
        """
        Check if a creature can act this turn.
        
        Args:
            creature: Creature to check
            
        Returns:
            True if creature can act
        """
        effects = self.state.status_effects.get(creature.creature_id, [])
        
        for effect in effects:
            if effect.prevents_creature_action():
                return False
        
        return True
    
    def _execute_ai_action(self, attacker: Creature, defender: Creature):
        """
        Execute an AI-controlled action.
        
        Args:
            attacker: Creature performing the action
            defender: Target creature
        """
        # Simple AI: choose a usable ability or basic attack
        usable_abilities = [
            ability for ability in attacker.abilities
            if ability.can_use(attacker.stats, attacker.energy)
        ]
        
        if usable_abilities:
            # Choose highest power ability
            ability = max(usable_abilities, key=lambda a: a.power)
        else:
            # Use basic attack if no abilities available
            from ..models.ability import create_ability
            ability = create_ability('tackle')
            if not ability:
                # Fallback basic attack
                ability = Ability(name="Basic Attack", power=10)
        
        # Execute the ability
        self._execute_ability(attacker, defender, ability)
    
    def _execute_ability(self, attacker: Creature, defender: Creature, ability: Ability):
        """
        Execute an ability from attacker to defender.
        
        Args:
            attacker: Creature using the ability
            defender: Target creature
            ability: Ability being used
        """
        self._log(f"{attacker.name} uses {ability.name}!")
        
        # Emit ability use event
        self._emit_event(BattleEvent(
            event_type=BattleEventType.ABILITY_USE,
            actor=attacker,
            target=defender,
            ability=ability,
            message=f"{attacker.name} uses {ability.name}!",
            data={'energy_cost': ability.energy_cost}
        ))
        
        # Use the ability (triggers cooldown)
        ability.use()
        
        # Deduct energy cost
        attacker.energy = max(0, attacker.energy - ability.energy_cost)
        
        # Check accuracy
        if not self._check_accuracy(ability.accuracy):
            self._log(f"{ability.name} missed!")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.MISS,
                actor=attacker,
                target=defender,
                ability=ability,
                message=f"{ability.name} missed!"
            ))
            return
        
        # Calculate and apply damage/effects based on ability type
        if ability.ability_type in [AbilityType.PHYSICAL, AbilityType.SPECIAL]:
            damage = self._calculate_damage(attacker, defender, ability)
            actual_damage = defender.stats.take_damage(damage)
            self._log(f"{defender.name} takes {actual_damage} damage! (HP: {defender.stats.hp}/{defender.stats.max_hp})")
            
            # Emit damage event
            self._emit_event(BattleEvent(
                event_type=BattleEventType.DAMAGE_DEALT,
                actor=attacker,
                target=defender,
                ability=ability,
                value=actual_damage,
                message=f"{defender.name} takes {actual_damage} damage!",
                data={'remaining_hp': defender.stats.hp, 'max_hp': defender.stats.max_hp}
            ))
            
            # Check if creature fainted
            if not defender.is_alive():
                self._emit_event(BattleEvent(
                    event_type=BattleEventType.CREATURE_FAINT,
                    target=defender,
                    message=f"{defender.name} fainted!"
                ))
            
        elif ability.ability_type == AbilityType.HEALING:
            heal_amount = ability.power
            actual_heal = attacker.stats.heal(heal_amount)
            self._log(f"{attacker.name} heals {actual_heal} HP! (HP: {attacker.stats.hp}/{attacker.stats.max_hp})")
            
            # Emit healing event
            self._emit_event(BattleEvent(
                event_type=BattleEventType.HEALING,
                actor=attacker,
                target=attacker,
                ability=ability,
                value=actual_heal,
                message=f"{attacker.name} heals {actual_heal} HP!",
                data={'remaining_hp': attacker.stats.hp, 'max_hp': attacker.stats.max_hp}
            ))
            
        elif ability.ability_type == AbilityType.BUFF:
            self._apply_stat_changes(attacker, ability, is_buff=True)
            
        elif ability.ability_type == AbilityType.DEBUFF:
            self._apply_stat_changes(defender, ability, is_buff=False)
        
        # Apply additional effects from ability
        self._apply_ability_effects(attacker, defender, ability)
    
    def _calculate_damage(
        self,
        attacker: Creature,
        defender: Creature,
        ability: Ability
    ) -> int:
        """
        Calculate damage dealt by an ability.
        
        Args:
            attacker: Creature using the ability
            defender: Target creature
            ability: Ability being used
            
        Returns:
            Final damage amount
        """
        # Base damage calculation
        base_damage = ability.calculate_damage(
            attacker.stats.attack,
            defender.stats.defense
        )
        
        # Apply type effectiveness
        effectiveness = self._get_type_effectiveness(attacker, defender)
        damage = int(base_damage * effectiveness)
        
        if effectiveness > 1.0:
            self._log("It's super effective!")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.SUPER_EFFECTIVE,
                actor=attacker,
                target=defender,
                message="It's super effective!",
                data={'effectiveness': effectiveness}
            ))
        elif effectiveness < 1.0 and effectiveness > 0:
            self._log("It's not very effective...")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.NOT_EFFECTIVE,
                actor=attacker,
                target=defender,
                message="It's not very effective...",
                data={'effectiveness': effectiveness}
            ))
        elif effectiveness == 0:
            self._log("It has no effect!")
        
        # Apply random variance (85-100% of calculated damage)
        damage = int(damage * random.uniform(0.85, 1.0))
        
        # Apply critical hit chance (6.25% chance for 1.5x damage)
        is_critical = random.random() < 0.0625
        if is_critical:
            damage = int(damage * 1.5)
            self._log("Critical hit!")
            self._emit_event(BattleEvent(
                event_type=BattleEventType.CRITICAL_HIT,
                actor=attacker,
                target=defender,
                message="Critical hit!",
                data={'damage_multiplier': 1.5}
            ))
        
        return max(1, damage)
    
    def _get_type_effectiveness(
        self,
        attacker: Creature,
        defender: Creature
    ) -> float:
        """
        Calculate type effectiveness multiplier.
        
        Args:
            attacker: Attacking creature
            defender: Defending creature
            
        Returns:
            Effectiveness multiplier
        """
        # Check if attacker has type tags
        if not attacker.creature_type.type_tags:
            return 1.0
        
        # Check primary type effectiveness
        attacker_type = attacker.creature_type.type_tags[0]
        effectiveness = 1.0
        
        if attacker_type in self.TYPE_EFFECTIVENESS:
            for defender_type in defender.creature_type.type_tags:
                if defender_type in self.TYPE_EFFECTIVENESS[attacker_type]:
                    effectiveness *= self.TYPE_EFFECTIVENESS[attacker_type][defender_type]
        
        return effectiveness
    
    def _check_accuracy(self, accuracy: int) -> bool:
        """
        Check if an ability hits based on accuracy.
        
        Args:
            accuracy: Accuracy value (0-100)
            
        Returns:
            True if ability hits
        """
        roll = random.randint(1, 100)
        return roll <= accuracy
    
    def _apply_stat_changes(self, target: Creature, ability: Ability, is_buff: bool):
        """
        Apply stat changes from buff/debuff abilities.
        
        Args:
            target: Creature receiving the stat change
            ability: Ability applying the change
            is_buff: True if buff, False if debuff
        """
        for effect in ability.effects:
            if effect.effect_type == "stat_change" and effect.stat_affected:
                modifier_value = effect.value if is_buff else -effect.value
                
                # Create stat modifier
                if effect.stat_affected == "attack":
                    modifier = StatModifier(
                        name=f"{ability.name} Effect",
                        duration=effect.duration,
                        attack_bonus=modifier_value
                    )
                elif effect.stat_affected == "defense":
                    modifier = StatModifier(
                        name=f"{ability.name} Effect",
                        duration=effect.duration,
                        defense_bonus=modifier_value
                    )
                elif effect.stat_affected == "speed":
                    modifier = StatModifier(
                        name=f"{ability.name} Effect",
                        duration=effect.duration,
                        speed_bonus=modifier_value
                    )
                else:
                    continue
                
                target.add_modifier(modifier)
                action = "increased" if is_buff else "decreased"
                self._log(f"{target.name}'s {effect.stat_affected} {action}!")
    
    def _apply_ability_effects(self, attacker: Creature, defender: Creature, ability: Ability):
        """
        Apply additional effects from an ability.
        
        Args:
            attacker: Creature using the ability
            defender: Target creature
            ability: Ability being used
        """
        for effect in ability.effects:
            # Status effect application
            if effect.effect_type == "status":
                # This would apply status effects
                # (requires status_effect_name in effect)
                pass
    
    def _phase_end_of_turn(self, player: Optional[Creature], enemy: Optional[Creature]):
        """
        Execute end-of-turn phase.
        
        Args:
            player: Player's creature
            enemy: Enemy's creature
        """
        # Process status effects
        for creature in [player, enemy]:
            if creature and creature.is_alive():
                self._process_status_effects(creature)
                
                # Tick cooldowns on abilities
                for ability in creature.abilities:
                    ability.tick_cooldown()
                
                # Tick stat modifiers
                creature.tick_modifiers()
    
    def _process_status_effects(self, creature: Creature):
        """
        Process all status effects on a creature.
        
        Args:
            creature: Creature with status effects
        """
        effects = self.state.status_effects.get(creature.creature_id, [])
        expired_effects = []
        
        for effect in effects:
            if not effect.is_active():
                expired_effects.append(effect)
                continue
            
            # Apply damage from status
            damage = effect.get_damage()
            if damage > 0:
                actual_damage = creature.stats.take_damage(damage)
                self._log(f"{creature.name} takes {actual_damage} damage from {effect.name}!")
            
            # Apply healing from status
            healing = effect.get_healing()
            if healing > 0:
                actual_heal = creature.stats.heal(healing)
                self._log(f"{creature.name} recovers {actual_heal} HP from {effect.name}!")
            
            # Tick the effect
            effect.tick()
            
            if not effect.is_active():
                expired_effects.append(effect)
                self._log(f"{effect.name} wore off on {creature.name}!")
        
        # Remove expired effects
        for effect in expired_effects:
            effects.remove(effect)
    
    def _phase_battle_end(self):
        """Execute battle end phase."""
        self.state.phase = BattlePhase.BATTLE_END
        
        winner_side = self.state.get_winner()
        if winner_side == 'player':
            # Award experience to surviving player creatures
            for creature in self.state.player_team:
                if creature.is_alive():
                    xp_gained = sum(enemy.level * 50 for enemy in self.state.enemy_team)
                    leveled_up = creature.gain_experience(xp_gained)
                    self._log(f"{creature.name} gained {xp_gained} XP!")
                    if leveled_up:
                        self._log(f"{creature.name} leveled up to level {creature.level}!")
    
    def get_battle_log(self) -> List[str]:
        """
        Get the complete battle log.
        
        Returns:
            List of all recorded battle events
        """
        return self.battle_log
    
    def get_state(self) -> BattleState:
        """Get the current battle state."""
        return self.state
    
    def __repr__(self):
        """String representation of the Battle."""
        player_count = len(self.state.player_team)
        enemy_count = len(self.state.enemy_team)
        return f"Battle(player_team={player_count}, enemy_team={enemy_count}, turn={self.state.current_turn})"
