    def _get_simulation_state(self) -> Dict:
        """
        Get current simulation state for dilemma triggers.
        
        Returns:
            Dictionary with simulation metrics for dilemma checking
        """
        if not self._creatures:
            return {}
        
        alive_creatures = [c for c in self._creatures if c.is_alive()]
        if not alive_creatures:
            return {}
        
        # Calculate metrics
        min_health = min(c.creature.stats.hp / max(1, c.creature.stats.max_hp) * 100 
                        for c in alive_creatures)
        
        avg_hunger = sum(getattr(c.creature, 'hunger', 50) for c in alive_creatures) / len(alive_creatures)
        
        aggressive_count = sum(1 for c in alive_creatures 
                              if any(t.name == "Aggressive" for t in c.creature.traits))
        
        return {
            "min_creature_health": min_health,
            "population": len(alive_creatures),
            "capacity": 100,  # Could be made configurable
            "average_hunger": avg_hunger,
            "aggressive_creature_count": aggressive_count,
            "new_rare_trait": False,  # Would track this properly in full implementation
            "depleted_areas": 0  # Would calculate based on pellet distribution
        }
