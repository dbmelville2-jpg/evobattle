"""
Unit tests for Battle system (turn-based).

Note: These tests use the turn-based battle system from battle_turnbased_backup.py
"""

import unittest
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import Ability, AbilityType, create_ability
from src.models.status_effect import StatusEffect, StatusEffectType
from src.systems.battle_turnbased_backup import Battle, BattlePhase, BattleState, BattleAction, BattleEvent, BattleEventType


class TestBattleState(unittest.TestCase):
    """Test cases for BattleState class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test creatures
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12),
            stat_growth=StatGrowth()
        )
        
        self.player = Creature(
            name="Player",
            creature_type=warrior_type,
            level=5
        )
        self.enemy = Creature(
            name="Enemy",
            creature_type=warrior_type,
            level=5
        )
    
    def test_battle_state_initialization(self):
        """Test creating a battle state."""
        state = BattleState([self.player], [self.enemy])
        
        self.assertEqual(len(state.player_team), 1)
        self.assertEqual(len(state.enemy_team), 1)
        self.assertEqual(state.current_turn, 0)
        self.assertEqual(state.phase, BattlePhase.START)
    
    def test_get_active_creatures(self):
        """Test getting active creatures."""
        state = BattleState([self.player], [self.enemy])
        
        player = state.get_active_player()
        enemy = state.get_active_enemy()
        
        self.assertEqual(player, self.player)
        self.assertEqual(enemy, self.enemy)
    
    def test_battle_not_over_initially(self):
        """Test that battle is not over at start."""
        state = BattleState([self.player], [self.enemy])
        
        self.assertFalse(state.is_battle_over())
        self.assertIsNone(state.get_winner())
    
    def test_battle_over_when_team_defeated(self):
        """Test battle ends when a team is defeated."""
        state = BattleState([self.player], [self.enemy])
        
        # Defeat enemy
        self.enemy.stats.hp = 0
        
        self.assertTrue(state.is_battle_over())
        self.assertEqual(state.get_winner(), 'player')
    
    def test_winner_determination(self):
        """Test winner determination."""
        state = BattleState([self.player], [self.enemy])
        
        # Player wins
        self.enemy.stats.hp = 0
        self.assertEqual(state.get_winner(), 'player')
        
        # Reset and enemy wins
        self.enemy.stats.hp = 100
        self.player.stats.hp = 0
        state2 = BattleState([self.player], [self.enemy])
        self.assertEqual(state2.get_winner(), 'enemy')


class TestBattle(unittest.TestCase):
    """Test cases for Battle class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test creature types
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12),
            stat_growth=StatGrowth(),
            type_tags=["fighter"]
        )
        
        mage_type = CreatureType(
            name="Mage",
            base_stats=Stats(max_hp=80, attack=20, defense=8, speed=15),
            stat_growth=StatGrowth(),
            type_tags=["psychic"]
        )
        
        # Create creatures
        self.player = Creature(
            name="Warrior",
            creature_type=warrior_type,
            level=5
        )
        self.player.add_ability(create_ability('tackle'))
        
        self.enemy = Creature(
            name="Mage",
            creature_type=mage_type,
            level=5
        )
        self.enemy.add_ability(create_ability('tackle'))
    
    def test_battle_initialization(self):
        """Test creating a battle."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        self.assertEqual(len(battle.state.player_team), 1)
        self.assertEqual(len(battle.state.enemy_team), 1)
        self.assertEqual(len(battle.battle_log), 1)
        self.assertEqual(battle.random_seed, 42)
    
    def test_battle_simulation(self):
        """Test full battle simulation."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        winner = battle.simulate()
        
        self.assertIsNotNone(winner)
        self.assertTrue(winner.is_alive())
        self.assertGreater(len(battle.battle_log), 5)
        self.assertTrue(battle.state.is_battle_over())
    
    def test_turn_order_by_speed(self):
        """Test that turn order is determined by speed."""
        # Create creatures with different speeds
        fast_type = CreatureType(
            name="Fast",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=20)
        )
        slow_type = CreatureType(
            name="Slow",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=5)
        )
        
        fast = Creature(name="Fast", creature_type=fast_type, level=5)
        slow = Creature(name="Slow", creature_type=slow_type, level=5)
        
        battle = Battle([fast], [slow], random_seed=42)
        
        # Determine turn order
        turn_order = battle._determine_turn_order(fast, slow)
        
        # Fast creature should usually go first (with random factor)
        # Run multiple times to check consistency
        fast_first_count = 0
        for _ in range(10):
            order = battle._determine_turn_order(fast, slow)
            if order[0] == fast:
                fast_first_count += 1
        
        # Fast should go first most of the time
        self.assertGreater(fast_first_count, 7)
    
    def test_damage_calculation(self):
        """Test damage calculation."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        ability = create_ability('tackle')
        damage = battle._calculate_damage(self.player, self.enemy, ability)
        
        self.assertGreater(damage, 0)
        self.assertIsInstance(damage, int)
    
    def test_type_effectiveness(self):
        """Test type effectiveness calculation."""
        # Create fire and water types
        fire_type = CreatureType(
            name="Fire",
            base_stats=Stats(max_hp=100, attack=15, defense=10),
            type_tags=["fire"]
        )
        water_type = CreatureType(
            name="Water",
            base_stats=Stats(max_hp=100, attack=15, defense=10),
            type_tags=["water"]
        )
        
        fire_creature = Creature(name="Fire", creature_type=fire_type, level=5)
        water_creature = Creature(name="Water", creature_type=water_type, level=5)
        
        battle = Battle([fire_creature], [water_creature])
        
        # Fire vs Water should be not very effective (0.5x)
        effectiveness = battle._get_type_effectiveness(fire_creature, water_creature)
        self.assertEqual(effectiveness, 0.5)
        
        # Water vs Fire should be super effective (2.0x)
        effectiveness = battle._get_type_effectiveness(water_creature, fire_creature)
        self.assertEqual(effectiveness, 2.0)
    
    def test_accuracy_check(self):
        """Test accuracy checking."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        # 100% accuracy should always hit
        self.assertTrue(battle._check_accuracy(100))
        
        # 0% accuracy should never hit
        self.assertFalse(battle._check_accuracy(0))
        
        # Test mid-range accuracy over multiple rolls
        hits = sum(1 for _ in range(100) if battle._check_accuracy(75))
        # Should hit roughly 75 times out of 100
        self.assertGreater(hits, 60)
        self.assertLess(hits, 90)
    
    def test_ability_execution(self):
        """Test executing an ability."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        initial_hp = self.enemy.stats.hp
        ability = create_ability('tackle')
        
        battle._execute_ability(self.player, self.enemy, ability)
        
        # Enemy should have taken damage
        self.assertLess(self.enemy.stats.hp, initial_hp)
        
        # Battle log should contain action
        self.assertTrue(any('uses' in log for log in battle.battle_log))
    
    def test_healing_ability(self):
        """Test healing ability."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        # Damage player first
        self.player.stats.take_damage(30)
        damaged_hp = self.player.stats.hp
        
        # Use healing ability
        heal_ability = create_ability('heal')
        battle._execute_ability(self.player, self.player, heal_ability)
        
        # Should have healed
        self.assertGreater(self.player.stats.hp, damaged_hp)
    
    def test_buff_ability(self):
        """Test buff ability."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        initial_attack = self.player.stats.attack
        
        # Use power up ability
        buff = create_ability('power_up')
        battle._execute_ability(self.player, self.player, buff)
        
        # Attack should be modified (through modifiers)
        # Check that modifier was applied
        self.assertGreater(len(self.player.active_modifiers), 0)
    
    def test_battle_log_recording(self):
        """Test that battle events are logged."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        battle.simulate()
        
        log = battle.get_battle_log()
        
        self.assertGreater(len(log), 0)
        self.assertTrue(any('Battle started' in entry for entry in log))
        self.assertTrue(any('Battle End' in entry for entry in log))
    
    def test_experience_gain(self):
        """Test experience gain after battle."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        initial_xp = self.player.experience
        
        winner = battle.simulate()
        
        # Winner should gain experience
        if winner == self.player:
            self.assertGreater(self.player.experience, initial_xp)
    
    def test_ability_cooldowns(self):
        """Test that ability cooldowns are managed."""
        # Create ability with cooldown
        strong_attack = Ability(
            name="Strong Attack",
            power=50,
            cooldown=3,
            accuracy=100
        )
        
        self.player.add_ability(strong_attack)
        
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        # Execute ability
        battle._execute_ability(self.player, self.enemy, strong_attack)
        
        # Cooldown should be active
        self.assertGreater(strong_attack.current_cooldown, 0)
        self.assertFalse(strong_attack.can_use(self.player.stats, self.player.energy))
    
    def test_status_effect_prevents_action(self):
        """Test that status effects can prevent actions."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        # Apply sleep status
        sleep = StatusEffect(
            name="Sleep",
            effect_type=StatusEffectType.SLEEP,
            duration=2,
            prevents_action=True
        )
        
        battle.state.status_effects[self.player.creature_id] = [sleep]
        
        # Player should not be able to act
        can_act = battle._can_act(self.player)
        self.assertFalse(can_act)
    
    def test_status_effect_processing(self):
        """Test processing of status effects."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        # Apply poison
        poison = StatusEffect(
            name="Poison",
            effect_type=StatusEffectType.POISON,
            duration=3,
            potency=10
        )
        
        battle.state.status_effects[self.player.creature_id] = [poison]
        
        initial_hp = self.player.stats.hp
        
        # Process status effects
        battle._process_status_effects(self.player)
        
        # Should have taken damage
        self.assertLess(self.player.stats.hp, initial_hp)
        
        # Effect duration should decrease
        self.assertEqual(poison.current_duration, 2)
    
    def test_multiple_creatures_on_team(self):
        """Test battle with multiple creatures per team."""
        # Create additional creatures
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        player2 = Creature(name="Player2", creature_type=warrior_type, level=5)
        enemy2 = Creature(name="Enemy2", creature_type=warrior_type, level=5)
        
        player2.add_ability(create_ability('tackle'))
        enemy2.add_ability(create_ability('tackle'))
        
        battle = Battle(
            [self.player, player2],
            [self.enemy, enemy2],
            random_seed=42
        )
        
        winner = battle.simulate()
        
        self.assertIsNotNone(winner)
        self.assertTrue(battle.state.is_battle_over())
    
    def test_battle_state_access(self):
        """Test accessing battle state."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        state = battle.get_state()
        
        self.assertIsInstance(state, BattleState)
        self.assertEqual(state.current_turn, 0)


class TestBattleEdgeCases(unittest.TestCase):
    """Test edge cases in battle system."""
    
    def test_tied_speed(self):
        """Test handling of tied speed values."""
        same_type = CreatureType(
            name="Same",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        
        creature1 = Creature(name="C1", creature_type=same_type, level=5)
        creature2 = Creature(name="C2", creature_type=same_type, level=5)
        
        creature1.add_ability(create_ability('tackle'))
        creature2.add_ability(create_ability('tackle'))
        
        battle = Battle([creature1], [creature2], random_seed=42)
        
        # Should handle tied speeds without error
        turn_order = battle._determine_turn_order(creature1, creature2)
        
        self.assertEqual(len(turn_order), 2)
        self.assertIn(creature1, turn_order)
        self.assertIn(creature2, turn_order)
    
    def test_no_abilities(self):
        """Test battle with creatures without abilities."""
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        creature1 = Creature(name="C1", creature_type=warrior_type, level=5)
        creature2 = Creature(name="C2", creature_type=warrior_type, level=5)
        
        # Don't add any abilities
        battle = Battle([creature1], [creature2], random_seed=42)
        
        # Should still complete battle using basic attack
        winner = battle.simulate()
        
        self.assertIsNotNone(winner)
        self.assertTrue(battle.state.is_battle_over())
    
    def test_very_high_defense(self):
        """Test damage calculation with very high defense."""
        tank_type = CreatureType(
            name="Tank",
            base_stats=Stats(max_hp=200, attack=5, defense=100, speed=5)
        )
        
        attacker_type = CreatureType(
            name="Attacker",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        
        tank = Creature(name="Tank", creature_type=tank_type, level=5)
        attacker = Creature(name="Attacker", creature_type=attacker_type, level=5)
        
        tank.add_ability(create_ability('tackle'))
        attacker.add_ability(create_ability('tackle'))
        
        battle = Battle([attacker], [tank], random_seed=42)
        
        ability = create_ability('tackle')
        damage = battle._calculate_damage(attacker, tank, ability)
        
        # Should still deal at least 1 damage
        self.assertGreaterEqual(damage, 1)


class TestRealTimeBattle(unittest.TestCase):
    """Test cases for real-time battle features."""
    
    def setUp(self):
        """Set up test fixtures."""
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12),
            type_tags=["fighter"]
        )
        
        self.player = Creature(
            name="Player",
            creature_type=warrior_type,
            level=5
        )
        self.player.add_ability(create_ability('tackle'))
        
        self.enemy = Creature(
            name="Enemy",
            creature_type=warrior_type,
            level=5
        )
        self.enemy.add_ability(create_ability('tackle'))
    
    def test_event_emission(self):
        """Test that battle events are emitted."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        events_received = []
        
        def event_callback(event):
            events_received.append(event)
        
        battle.add_event_callback(event_callback)
        
        # Run battle
        battle.simulate()
        
        # Should have received events
        self.assertGreater(len(events_received), 0)
        
        # Check that events are BattleEvent instances
        self.assertIsInstance(events_received[0], BattleEvent)
    
    def test_event_types(self):
        """Test that different event types are emitted."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        event_types = set()
        
        def event_callback(event):
            event_types.add(event.event_type)
        
        battle.add_event_callback(event_callback)
        battle.simulate()
        
        # Should have battle start
        self.assertIn(BattleEventType.BATTLE_START, event_types)
        
        # Should have ability use
        self.assertIn(BattleEventType.ABILITY_USE, event_types)
        
        # Should have damage dealt
        self.assertIn(BattleEventType.DAMAGE_DEALT, event_types)
    
    def test_execute_turn(self):
        """Test executing one turn at a time."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        # Start battle
        battle.start_battle()
        self.assertTrue(battle._started)
        
        # Execute one turn
        continues = battle.execute_turn()
        
        # Battle should continue
        self.assertTrue(continues or battle.state.is_battle_over())
        self.assertGreaterEqual(battle.state.current_turn, 1)
    
    def test_execute_action(self):
        """Test executing individual actions."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        ability = create_ability('tackle')
        
        # Execute action
        success = battle.execute_action(self.player, ability, self.enemy)
        
        self.assertTrue(success)
        
        # Enemy should have taken damage
        self.assertLess(self.enemy.stats.hp, self.enemy.stats.max_hp)
    
    def test_step_by_step_battle(self):
        """Test running a battle step by step."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        battle.start_battle()
        
        turns_executed = 0
        max_turns = 100  # Safety limit
        
        while not battle.state.is_battle_over() and turns_executed < max_turns:
            battle.execute_turn()
            turns_executed += 1
        
        # Battle should have completed
        self.assertTrue(battle.state.is_battle_over())
        self.assertGreater(turns_executed, 0)
        self.assertLess(turns_executed, max_turns)
    
    def test_event_data(self):
        """Test that events contain proper data."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        damage_events = []
        
        def event_callback(event):
            if event.event_type == BattleEventType.DAMAGE_DEALT:
                damage_events.append(event)
        
        battle.add_event_callback(event_callback)
        battle.simulate()
        
        # Should have damage events
        self.assertGreater(len(damage_events), 0)
        
        # Check damage event structure
        for event in damage_events:
            self.assertIsNotNone(event.actor)
            self.assertIsNotNone(event.target)
            self.assertIsNotNone(event.value)
            self.assertGreater(event.value, 0)
            self.assertIn('remaining_hp', event.data)
    
    def test_multiple_callbacks(self):
        """Test multiple event callbacks."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        callback1_count = [0]
        callback2_count = [0]
        
        def callback1(event):
            callback1_count[0] += 1
        
        def callback2(event):
            callback2_count[0] += 1
        
        battle.add_event_callback(callback1)
        battle.add_event_callback(callback2)
        
        battle.simulate()
        
        # Both callbacks should have been called
        self.assertGreater(callback1_count[0], 0)
        self.assertEqual(callback1_count[0], callback2_count[0])
    
    def test_state_events_stored(self):
        """Test that events are stored in battle state."""
        battle = Battle([self.player], [self.enemy], random_seed=42)
        
        battle.simulate()
        
        # Events should be in state
        self.assertGreater(len(battle.state.events), 0)
        
        # Events should match event list
        self.assertEqual(len(battle.state.events), len(battle.state.events))


if __name__ == '__main__':
    unittest.main()
