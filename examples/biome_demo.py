"""
Biome Generation Demo

Demonstrates the biome generation system with different biome types.
Shows terrain distribution, weather conditions, and pellet configurations.
"""
import sys
sys.path.insert(0, 'src')

from systems.biome_generator import BiomeGenerator, BiomeType

print("=" * 70)
print("BIOME GENERATION DEMONSTRATION")
print("=" * 70)

generator = BiomeGenerator(seed=42)

# Demonstrate each biome type
biome_types = list(BiomeType)

for biome_type in biome_types:
    print(f"\n{'='*70}")
    print(f"BIOME: {biome_type.value.upper()}")
    print(f"{'='*70}")
    
    # Generate biome
    env = generator.generate_biome(biome_type, width=100, height=100)
    
    # Display biome info
    print(f"\n📋 Biome Information:")
    print(f"  Name: {env.biome_name}")
    print(f"  Description: {env.biome_description}")
    print(f"  Difficulty: {env.biome_difficulty}/5")
    
    # Weather info
    if env.weather:
        print(f"\n🌤️  Weather:")
        print(f"  Type: {env.weather.weather_type.value}")
        print(f"  Temperature: {env.weather.temperature:.1f}°C")
        print(f"  Humidity: {env.weather.humidity*100:.0f}%")
        print(f"  Visibility: {env.weather.visibility*100:.0f}%")
    
    # Terrain distribution
    terrain_counts = {}
    for cell in env.terrain_grid.values():
        terrain_type = cell.terrain_type.value
        terrain_counts[terrain_type] = terrain_counts.get(terrain_type, 0) + 1
    
    total_cells = len(env.terrain_grid)
    print(f"\n🗺️  Terrain Distribution ({total_cells} cells):")
    for terrain, count in sorted(terrain_counts.items(), key=lambda x: -x[1]):
        percentage = (count / total_cells) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {terrain:10s}: {bar:25s} {percentage:5.1f}% ({count} cells)")
    
    # Hazards
    print(f"\n⚠️  Hazards: {len(env.hazards)} active")
    if env.hazards:
        hazard_types = {}
        for hazard in env.hazards:
            h_type = hazard.hazard_type.value
            hazard_types[h_type] = hazard_types.get(h_type, 0) + 1
        for h_type, count in hazard_types.items():
            print(f"  - {h_type}: {count}")
    
    # Pellet spawn config
    pellet_config = generator.get_pellet_spawn_config(biome_type)
    print(f"\n🌱 Pellet Configuration:")
    print(f"  Density Multiplier: {pellet_config['density']:.1f}x")
    print(f"  Initial Count: {pellet_config['initial_count']}")
    print(f"  Toxicity Bias: {pellet_config['toxicity_bias']:+.2f}")
    
    # Movement and resource modifiers
    from models.spatial import Vector2D
    center_pos = Vector2D(50, 50)
    movement_mod = env.get_combined_movement_modifier(center_pos)
    resource_quality = env.get_resource_quality_at(center_pos)
    
    print(f"\n📊 Environmental Modifiers (at center):")
    print(f"  Movement Speed: {movement_mod:.2f}x")
    print(f"  Resource Quality: {resource_quality:.2f}x")

print(f"\n{'='*70}")
print("DEMONSTRATION COMPLETE")
print(f"{'='*70}")

# Show how to use in battle
print(f"\n💡 Usage Example:")
print(f"```python")
print(f"from systems.battle_spatial import SpatialBattle")
print(f"from models.creature import Creature")
print(f"")
print(f"# Create battle with specific biome")
print(f"battle = SpatialBattle(")
print(f"    creatures_or_team1=[creature1, creature2],")
print(f"    biome_type='forest'  # or 'desert', 'marsh', 'random', etc.")
print(f")")
print(f"")
print(f"# Biome will have:")
print(f"# - Terrain patterns matching the biome")
print(f"# - Weather appropriate for the biome")
print(f"# - Pellet density and toxicity for the biome")
print(f"# - Hazards specific to the biome")
print(f"```")
