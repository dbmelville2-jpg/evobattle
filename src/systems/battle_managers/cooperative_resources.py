    def spawn_cooperative_resource(self):
        """
        Spawn a large resource cluster that encourages cooperative gathering.
        
        Creates multiple pellets in a small area, rewarding creatures that work together.
        """
        # Choose a random location for the resource cluster
        cluster_center = Vector2D(
            random.uniform(10, self.arena.width - 10),
            random.uniform(10, self.arena.height - 10)
        )
        
        # Spawn 3-5 pellets in a cluster
        cluster_size = random.randint(3, 5)
        cluster_radius = 5.0
        
        for _ in range(cluster_size):
            # Offset from center
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, cluster_radius)
            position = Vector2D(
                cluster_center.x + math.cos(angle) * distance,
                cluster_center.y + math.sin(angle) * distance
            )
            position = self.arena.clamp_position(position)
            
            # Create a high-quality pellet at the position
            pellet = create_random_pellet(position.x, position.y, generation=1)
            pellet.traits.palatability = random.uniform(0.7, 1.0)  # High palatability
            pellet.traits.toxicity = random.uniform(0.0, 0.2)  # Low toxicity
            pellet.traits.nutrient_value = random.uniform(25, 35)  # Good nutrients
            
            self.arena.add_pellet(pellet)
        
        self.event_manager.log(f"COOPERATIVE FOOD! Resource cluster of {cluster_size} pellets appeared")
        self.event_manager.emit_event(BattleEvent(
            event_type=BattleEventType.PELLET_SPAWN,
            message=f"Rich food cluster spawned! {cluster_size} high-quality pellets",
            data={'cluster_size': cluster_size, 'position': cluster_center.to_tuple()}
        ))
