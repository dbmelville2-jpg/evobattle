"""
Terrain Affinity Tracker

Tracks which terrain types each creature spends time in, allowing for:
- Terrain preference detection
- Stat bonuses in preferred terrain
- Inheritance of terrain affinity to offspring
"""

from typing import Dict, Optional, Tuple
from collections import defaultdict
from src.models.environment import TerrainType


class TerrainAffinityTracker:
    """
    Tracks creature terrain preferences over time.
    
    Creatures that spend more time in specific terrain types develop
    affinity bonuses and can pass preferences to offspring.
    """
    
    def __init__(self):
        """Initialize the terrain affinity tracker."""
        # creature_id -> {terrain_type: time_spent_seconds}
        self.terrain_time: Dict[str, Dict[TerrainType, float]] = defaultdict(lambda: defaultdict(float))
        
        # creature_id -> preferred_terrain (cached)
        self._preferred_terrain_cache: Dict[str, Optional[TerrainType]] = {}
        
        # Minimum time to establish preference (seconds)
        self.min_time_for_preference = 30.0
        
        # Bonus multiplier for being in preferred terrain
        self.preference_bonus = 1.15  # 15% bonus
    
    def update(self, creature_id: str, terrain_type: TerrainType, delta_time: float):
        """
        Track time spent in terrain.
        
        Args:
            creature_id: Unique creature identifier
            terrain_type: Current terrain type
            delta_time: Time elapsed in seconds
        """
        self.terrain_time[creature_id][terrain_type] += delta_time
        
        # Invalidate cache for this creature
        if creature_id in self._preferred_terrain_cache:
            del self._preferred_terrain_cache[creature_id]
    
    def get_preferred_terrain(self, creature_id: str) -> Optional[TerrainType]:
        """
        Get creature's most-used terrain type.
        
        Args:
            creature_id: Unique creature identifier
            
        Returns:
            Most-used terrain type, or None if no clear preference
        """
        # Check cache first
        if creature_id in self._preferred_terrain_cache:
            return self._preferred_terrain_cache[creature_id]
        
        if creature_id not in self.terrain_time:
            return None
        
        terrain_times = self.terrain_time[creature_id]
        
        if not terrain_times:
            return None
        
        # Find terrain with most time
        max_terrain = max(terrain_times.items(), key=lambda x: x[1])
        terrain_type, time_spent = max_terrain
        
        # Only return preference if creature spent significant time there
        if time_spent < self.min_time_for_preference:
            self._preferred_terrain_cache[creature_id] = None
            return None
        
        self._preferred_terrain_cache[creature_id] = terrain_type
        return terrain_type
    
    def get_terrain_bonus(self, creature_id: str, current_terrain: TerrainType) -> float:
        """
        Get stat bonus for being in preferred terrain.
        
        Args:
            creature_id: Unique creature identifier
            current_terrain: Current terrain type
            
        Returns:
            Multiplier for stats (1.0 = no bonus, >1.0 = bonus)
        """
        preferred = self.get_preferred_terrain(creature_id)
        
        if preferred is None:
            return 1.0
        
        if current_terrain == preferred:
            return self.preference_bonus
        
        return 1.0
    
    def get_terrain_distribution(self, creature_id: str) -> Dict[TerrainType, float]:
        """
        Get percentage of time spent in each terrain type.
        
        Args:
            creature_id: Unique creature identifier
            
        Returns:
            Dictionary of terrain_type -> percentage (0.0 to 1.0)
        """
        if creature_id not in self.terrain_time:
            return {}
        
        terrain_times = self.terrain_time[creature_id]
        total_time = sum(terrain_times.values())
        
        if total_time == 0:
            return {}
        
        return {
            terrain: time / total_time
            for terrain, time in terrain_times.items()
        }
    
    def get_total_time(self, creature_id: str) -> float:
        """
        Get total time tracked for a creature.
        
        Args:
            creature_id: Unique creature identifier
            
        Returns:
            Total seconds tracked
        """
        if creature_id not in self.terrain_time:
            return 0.0
        
        return sum(self.terrain_time[creature_id].values())
    
    def inherit_preference(
        self,
        offspring_id: str,
        parent1_id: str,
        parent2_id: Optional[str] = None
    ):
        """
        Initialize offspring with inherited terrain preference.
        
        Offspring start with a bias toward their parents' preferred terrain.
        
        Args:
            offspring_id: New creature's ID
            parent1_id: First parent's ID
            parent2_id: Optional second parent's ID
        """
        # Get parent preferences
        parent1_pref = self.get_preferred_terrain(parent1_id)
        parent2_pref = self.get_preferred_terrain(parent2_id) if parent2_id else None
        
        # If both parents have same preference, give offspring a strong head start
        if parent1_pref and parent1_pref == parent2_pref:
            # Give offspring 35 seconds in that terrain (enough to establish preference)
            self.terrain_time[offspring_id][parent1_pref] = 35.0
        
        # If parents have different preferences, give small bonus to both
        elif parent1_pref and parent2_pref and parent1_pref != parent2_pref:
            self.terrain_time[offspring_id][parent1_pref] = 15.0
            self.terrain_time[offspring_id][parent2_pref] = 15.0
        
        # If only one parent has preference
        elif parent1_pref:
            self.terrain_time[offspring_id][parent1_pref] = 25.0
        elif parent2_pref:
            self.terrain_time[offspring_id][parent2_pref] = 25.0
    
    def remove_creature(self, creature_id: str):
        """
        Remove tracking data for a creature (when it dies).
        
        Args:
            creature_id: Creature to remove
        """
        if creature_id in self.terrain_time:
            del self.terrain_time[creature_id]
        
        if creature_id in self._preferred_terrain_cache:
            del self._preferred_terrain_cache[creature_id]
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about terrain affinity tracking.
        
        Returns:
            Dictionary with tracking statistics
        """
        total_creatures = len(self.terrain_time)
        creatures_with_preference = sum(
            1 for cid in self.terrain_time.keys()
            if self.get_preferred_terrain(cid) is not None
        )
        
        # Count preferences by terrain type
        preference_counts = defaultdict(int)
        for cid in self.terrain_time.keys():
            pref = self.get_preferred_terrain(cid)
            if pref:
                preference_counts[pref.value] += 1
        
        return {
            'total_creatures_tracked': total_creatures,
            'creatures_with_preference': creatures_with_preference,
            'preference_distribution': dict(preference_counts)
        }
    
    def to_dict(self) -> Dict:
        """
        Serialize to dictionary for saving.
        
        Returns:
            Dictionary representation
        """
        return {
            'terrain_time': {
                creature_id: {
                    terrain.value: time
                    for terrain, time in terrains.items()
                }
                for creature_id, terrains in self.terrain_time.items()
            },
            'min_time_for_preference': self.min_time_for_preference,
            'preference_bonus': self.preference_bonus
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'TerrainAffinityTracker':
        """
        Deserialize from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            TerrainAffinityTracker instance
        """
        tracker = TerrainAffinityTracker()
        tracker.min_time_for_preference = data.get('min_time_for_preference', 30.0)
        tracker.preference_bonus = data.get('preference_bonus', 1.15)
        
        # Restore terrain time data
        for creature_id, terrains in data.get('terrain_time', {}).items():
            for terrain_str, time in terrains.items():
                terrain_type = TerrainType(terrain_str)
                tracker.terrain_time[creature_id][terrain_type] = time
        
        return tracker
