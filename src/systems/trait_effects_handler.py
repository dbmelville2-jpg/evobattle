"""
Trait Effects Handler - Apply trait interaction_effects during combat and behavior.

This system extracts and applies the rich interaction_effects data from creature traits,
including pack_hunter bonuses, loner_strength, group coordination, and other behavioral modifiers.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from src.models.trait import Trait

if TYPE_CHECKING:
    from src.models.creature import Creature


class TraitEffectsHandler:
    """
    Handles application of trait interaction_effects in combat and behavior.
    
    This system bridges the gap between trait definitions (which have rich interaction_effects)
    and the battle system (which needs to apply those effects).
    """
    
    def __init__(self):
        """Initialize the trait effects handler."""
        pass
    
    def get_combat_damage_modifier(
        self,
        attacker: 'Creature',
        defender: 'Creature',
        allies_nearby: int = 0,
        enemies_nearby: int = 0,
        family_nearby: int = 0
    ) -> float:
        """
        Calculate combat damage modifier from all trait effects.
        
        Args:
            attacker: Attacking creature
            defender: Defending creature
            allies_nearby: Number of allies within combat range
            enemies_nearby: Number of enemies within combat range
            family_nearby: Number of family members within combat range
            
        Returns:
            Damage multiplier (1.0 = no modifier, >1.0 = bonus, <1.0 = penalty)
        """
        modifier = 1.0
        
        # Process each trait's interaction_effects
        for trait in attacker.traits:
            effects = trait.interaction_effects
            
            # Pack hunter bonus - stronger when fighting with allies
            if effects.get('pack_hunter') and allies_nearby > 0:
                pack_coordination = effects.get('pack_coordination', 1.2)
                # Scale with number of allies (diminishing returns)
                ally_bonus = min(0.3, allies_nearby * 0.1)
                modifier *= (1.0 + ally_bonus) * (pack_coordination - 1.0 + 1.0)
            
            # Loner strength - stronger when fighting alone
            if effects.get('loner_strength') and allies_nearby == 0:
                isolation_resilience = effects.get('isolation_resilience', 1.3)
                modifier *= isolation_resilience
            
            # Group bonus - general bonus when near allies
            if 'group_bonus' in effects and allies_nearby > 0:
                group_bonus = effects['group_bonus']
                modifier *= group_bonus
            
            # Group penalty - weaker when in groups (for loner types)
            if 'group_penalty' in effects and allies_nearby > 0:
                group_penalty = effects['group_penalty']
                modifier *= group_penalty
            
            # Solo bonus - general bonus when alone
            if 'solo_bonus' in effects and allies_nearby == 0:
                solo_bonus = effects['solo_bonus']
                modifier *= solo_bonus
            
            # Outnumbered penalty
            if 'lack_of_support_multiplier' in effects and enemies_nearby > allies_nearby + 1:
                modifier *= effects['lack_of_support_multiplier']
            
            # Executioner - bonus vs low HP targets
            if effects.get('execute_threshold'):
                defender_hp_percent = defender.stats.hp / max(1, defender.stats.max_hp)
                execute_threshold = effects['execute_threshold']
                if defender_hp_percent < execute_threshold:
                    execute_bonus = effects.get('execute_damage_bonus', 1.5)
                    modifier *= execute_bonus
            
            # Brutal - armor penetration
            if effects.get('armor_penetration'):
                # This would need to be applied differently in damage calculation
                # For now, treat as a flat damage bonus
                armor_pen = effects['armor_penetration']
                modifier *= (1.0 + armor_pen * 0.3)
            
            # Berserker - bonus at low HP
            if effects.get('rage_threshold'):
                attacker_hp_percent = attacker.stats.hp / max(1, attacker.stats.max_hp)
                rage_threshold = effects['rage_threshold']
                if attacker_hp_percent < rage_threshold:
                    rage_bonus = effects.get('rage_damage_bonus', 1.5)
                    modifier *= rage_bonus
        
        return modifier
    
    def get_defense_modifier(
        self,
        defender: 'Creature',
        attacker: 'Creature',
        allies_nearby: int = 0
    ) -> float:
        """
        Calculate defense modifier from trait effects.
        
        Args:
            defender: Defending creature
            attacker: Attacking creature
            allies_nearby: Number of allies nearby
            
        Returns:
            Defense multiplier (>1.0 = takes less damage, <1.0 = takes more damage)
        """
        modifier = 1.0
        
        for trait in defender.traits:
            effects = trait.interaction_effects
            
            # Vulnerability when group split
            if effects.get('vulnerability_when_group_split') and allies_nearby == 0:
                modifier *= effects['vulnerability_when_group_split']
            
            # Damage reduction
            if 'damage_reduction' in effects:
                # Convert damage reduction to defense modifier
                # damage_reduction of 0.2 means take 80% damage
                reduction = effects['damage_reduction']
                modifier *= (1.0 - reduction)
            
            # Armor effectiveness
            if 'armor_effectiveness' in effects:
                armor_mult = effects['armor_effectiveness']
                modifier *= (1.0 / armor_mult)  # Higher armor = less damage taken
        
        return modifier
    
    def should_avoid_combat(
        self,
        creature: 'Creature',
        hunger_level: float,
        allies_nearby: int = 0
    ) -> bool:
        """
        Determine if creature should avoid combat based on traits.
        
        Args:
            creature: The creature
            hunger_level: Current hunger (0.0 = starving, 1.0 = full)
            allies_nearby: Number of allies nearby
            
        Returns:
            True if creature should avoid combat
        """
        # Check for aggressive traits first - they override avoidance
        for trait in creature.traits:
            effects = trait.interaction_effects
            if effects.get('aggressive') or effects.get('bloodlust') or effects.get('no_retreat'):
                return False  # Never avoid combat if aggressive
        
        # Now check for avoidance traits
        for trait in creature.traits:
            effects = trait.interaction_effects
            
            # Scaredy cat - flees very easily
            if effects.get('scaredy_cat'):
                return True
            
            # Cautious - avoid combat when VERY low on resources
            if effects.get('cautious_behavior') and hunger_level < 0.2:  # Changed from 0.4 to 0.2
                return True
            
            # Peaceful - avoid combat sometimes (not always)
            # This is now handled probabilistically in the battle system
            # Don't make it absolute here
        
        return False
    
    def get_movement_speed_modifier(
        self,
        creature: 'Creature',
        is_fleeing: bool = False,
        allies_nearby: int = 0
    ) -> float:
        """
        Get movement speed modifier from traits.
        
        Args:
            creature: The creature
            is_fleeing: Whether creature is fleeing
            allies_nearby: Number of allies nearby
            
        Returns:
            Speed multiplier
        """
        modifier = 1.0
        
        for trait in creature.traits:
            effects = trait.interaction_effects
            
            # Panic speed boost when fleeing
            if is_fleeing and effects.get('panic_speed_boost'):
                modifier *= effects['panic_speed_boost']
            
            # Speed penalty when alone (for pack creatures)
            if effects.get('pack_hunter') and allies_nearby == 0:
                modifier *= 0.9  # Slightly slower when separated from pack
            
            # Speed bonus when alone (for loners)
            if effects.get('loner_strength') and allies_nearby == 0:
                modifier *= 1.1  # Slightly faster when alone
        
        return modifier
    
    def get_food_sharing_willingness(
        self,
        creature: 'Creature',
        target_is_family: bool = False
    ) -> float:
        """
        Get willingness to share food (0.0 = never, 1.0 = always).
        
        Args:
            creature: The creature
            target_is_family: Whether target is family member
            
        Returns:
            Sharing willingness (0.0 to 1.0)
        """
        willingness = 0.0
        
        for trait in creature.traits:
            effects = trait.interaction_effects
            
            # Social trait increases sharing
            if 'sharing_willingness' in effects:
                willingness = max(willingness, effects['sharing_willingness'])
            
            # Altruistic trait
            if effects.get('altruistic'):
                willingness = max(willingness, 0.7)
        
        # Family bonus
        if target_is_family:
            willingness = min(1.0, willingness + 0.3)
        
        return willingness
    
    def extract_all_effects(self, creature: 'Creature') -> Dict[str, Any]:
        """
        Extract all interaction_effects from creature's traits.
        
        Args:
            creature: The creature
            
        Returns:
            Dictionary of all effects (merged from all traits)
        """
        all_effects = {}
        
        for trait in creature.traits:
            for key, value in trait.interaction_effects.items():
                if key not in all_effects:
                    all_effects[key] = value
                else:
                    # If effect already exists, take the stronger value
                    if isinstance(value, (int, float)) and isinstance(all_effects[key], (int, float)):
                        # For numeric values, take the maximum
                        all_effects[key] = max(value, all_effects[key])
                    elif isinstance(value, bool):
                        # For booleans, OR them together
                        all_effects[key] = all_effects[key] or value
        
        return all_effects
    
    def get_weather_bonus(
        self,
        creature: 'Creature',
        weather_type,  # WeatherType enum
        stat_type: str = 'damage'
    ) -> float:
        """
        Calculate stat bonus from weather-responsive traits.
        
        Args:
            creature: The creature
            weather_type: Current weather type (WeatherType enum)
            stat_type: Type of stat ('damage', 'speed', 'defense', 'nutrition')
            
        Returns:
            Multiplier for the stat (1.0 = no bonus)
        """
        from src.models.environment import WeatherType
        
        modifier = 1.0
        
        for trait in creature.traits:
            effects = trait.interaction_effects
            
            # Storm bonuses
            if weather_type == WeatherType.STORMY:
                if effects.get('storm_dancer'):
                    if stat_type == 'speed':
                        modifier *= effects.get('storm_speed_bonus', 1.0)
                    elif stat_type == 'damage':
                        modifier *= effects.get('storm_damage_bonus', 1.0)
            
            # Rain bonuses
            elif weather_type == WeatherType.RAINY:
                if effects.get('rain_harvester'):
                    if stat_type == 'nutrition':
                        modifier *= effects.get('rain_nutrition_bonus', 1.0)
                    elif stat_type == 'hunger':
                        modifier *= effects.get('rain_hunger_reduction', 1.0)
            
            # Drought bonuses
            elif weather_type == WeatherType.DROUGHT:
                if effects.get('drought_survivor'):
                    if stat_type == 'hunger':
                        modifier *= effects.get('drought_hunger_reduction', 1.0)
            
            # Fog bonuses
            elif weather_type == WeatherType.FOGGY:
                if effects.get('fog_walker'):
                    if stat_type == 'stealth':
                        modifier *= (1.0 + effects.get('fog_stealth_bonus', 0.0))
                    elif stat_type == 'evasion':
                        modifier *= effects.get('fog_evasion_bonus', 1.0)
        
        return modifier
    
    def get_terrain_bonus(
        self,
        creature: 'Creature',
        terrain_type,  # TerrainType enum
        stat_type: str = 'damage'
    ) -> float:
        """
        Calculate stat bonus from terrain-adaptive traits.
        
        Args:
            creature: The creature
            terrain_type: Current terrain type (TerrainType enum)
            stat_type: Type of stat ('damage', 'speed', 'defense', 'movement')
            
        Returns:
            Multiplier for the stat (1.0 = no bonus)
        """
        from src.models.environment import TerrainType
        
        modifier = 1.0
        
        for trait in creature.traits:
            effects = trait.interaction_effects
            
            # Check terrain affinity
            terrain_affinity = effects.get('terrain_affinity')
            if terrain_affinity:
                # Handle both string and enum values
                if isinstance(terrain_affinity, str):
                    matches = terrain_type.value == terrain_affinity
                else:
                    matches = terrain_type == terrain_affinity
                
                if matches:
                    # Apply terrain-specific bonuses
                    if terrain_type == TerrainType.FOREST:
                        if stat_type == 'stealth':
                            modifier *= (1.0 + effects.get('forest_stealth_bonus', 0.0))
                        elif stat_type == 'defense':
                            modifier *= (1.0 + effects.get('forest_cover_bonus', 0.0))
                        elif stat_type == 'movement':
                            modifier *= effects.get('forest_movement_bonus', 1.0)
                    
                    elif terrain_type == TerrainType.DESERT:
                        if stat_type == 'speed':
                            modifier *= effects.get('desert_speed_bonus', 1.0)
                        elif stat_type == 'hunger':
                            modifier *= effects.get('heat_resistance', 1.0)
                    
                    elif terrain_type == TerrainType.MARSH:
                        if stat_type == 'movement':
                            modifier *= effects.get('marsh_movement_bonus', 1.0)
                        elif stat_type == 'toxin_resistance':
                            modifier *= effects.get('toxin_immunity', 1.0)
                    
                    elif terrain_type == TerrainType.ROCKY:
                        if stat_type == 'movement':
                            modifier *= effects.get('rocky_movement_bonus', 1.0)
                        elif stat_type == 'defense':
                            modifier *= effects.get('rocky_defense_bonus', 1.0)
                    
                    elif terrain_type == TerrainType.WATER:
                        if stat_type == 'movement' and effects.get('amphibious'):
                            modifier *= effects.get('water_movement_bonus', 1.0)
        
        return modifier
    
    def should_absorb_hazard(
        self,
        creature: 'Creature',
        hazard_type  # HazardType enum
    ) -> bool:
        """
        Check if creature can absorb a specific hazard type.
        
        Args:
            creature: The creature
            hazard_type: Type of environmental hazard
            
        Returns:
            True if creature absorbs this hazard type
        """
        from src.models.environment import HazardType
        
        for trait in creature.traits:
            effects = trait.interaction_effects
            
            # Lightning Rod absorbs electrical hazards
            if hazard_type == HazardType.ELECTRICAL:
                if effects.get('lightning_rod') and effects.get('absorb_electrical_hazards'):
                    return True
        
        return False
    
    def get_hazard_absorption_rate(
        self,
        creature: 'Creature',
        hazard_type  # HazardType enum
    ) -> float:
        """
        Get percentage of hazard damage converted to HP.
        
        Args:
            creature: The creature
            hazard_type: Type of environmental hazard
            
        Returns:
            Conversion rate (0.0 to 1.0)
        """
        from src.models.environment import HazardType
        
        for trait in creature.traits:
            effects = trait.interaction_effects
            
            if hazard_type == HazardType.ELECTRICAL:
                if effects.get('lightning_rod'):
                    return effects.get('electrical_damage_to_energy', 0.0)
        
        return 0.0
    
    def get_environmental_synergy_bonus(
        self,
        creature: 'Creature',
        weather_type,  # WeatherType enum
        terrain_type,  # TerrainType enum
        time_of_day=None  # Optional TimeOfDay enum
    ) -> float:
        """
        Calculate bonus from environmental synergies (weather + terrain + time combos).
        
        Args:
            creature: The creature
            weather_type: Current weather
            terrain_type: Current terrain
            time_of_day: Optional time of day
            
        Returns:
            Damage/stat multiplier from synergies
        """
        from src.models.environment import WeatherType, TerrainType, TimeOfDay
        
        modifier = 1.0
        
        for trait in creature.traits:
            effects = trait.interaction_effects
            
            # Toxin Farmer: Marsh + Rain synergy
            if effects.get('toxin_farmer'):
                if terrain_type == TerrainType.MARSH and weather_type == WeatherType.RAINY:
                    modifier *= 1.3  # 30% bonus for perfect conditions
            
            # Illusionist: Desert + Drought synergy
            if effects.get('illusionist'):
                if terrain_type == TerrainType.DESERT and weather_type == WeatherType.DROUGHT:
                    modifier *= effects.get('evasion_bonus', 1.0)
            
            # Nocturnal: Night time bonuses
            if effects.get('nocturnal') and time_of_day:
                if time_of_day == TimeOfDay.NIGHT:
                    modifier *= effects.get('night_damage_bonus', 1.0)
                elif time_of_day == TimeOfDay.DAY:
                    modifier *= effects.get('day_penalty', 1.0)
        
        return modifier
    
    def get_building_bonus(
        self,
        creature: 'Creature',
        stat_type: str = 'speed'
    ) -> float:
        """
        Calculate bonus for building related activities.
        
        Args:
            creature: The creature
            stat_type: 'speed', 'durability', 'carry_capacity'
            
        Returns:
            Multiplier (1.0 = normal)
        """
        modifier = 1.0
        
        for trait in creature.traits:
            effects = trait.interaction_effects
            
            if stat_type == 'speed':
                if effects.get('build_speed_multiplier'):
                    modifier *= effects['build_speed_multiplier']
                if effects.get('construction_speed_bonus'):
                    modifier *= (1.0 + effects['construction_speed_bonus'])
                    
            elif stat_type == 'durability':
                if effects.get('structure_durability_bonus'):
                    modifier *= effects['structure_durability_bonus']
                    
            elif stat_type == 'carry_capacity':
                if effects.get('carry_capacity_multiplier'):
                    modifier *= effects['carry_capacity_multiplier']
                    
        return modifier
