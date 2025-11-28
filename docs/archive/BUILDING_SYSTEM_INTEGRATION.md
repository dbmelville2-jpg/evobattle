# Building System - Phase 5 Integration Notes

## Completed Integration

### SpatialBattle Initialization
- ✅ Added `BuildingBehaviorSystem` to `SpatialBattle.__init__`
- ✅ Added `self.structures: List` to track built structures
- ✅ Added `self.materials: List` to track building materials

## Remaining Integration Tasks

These tasks can be completed as needed during gameplay testing:

### 1. Material Spawning from Pellets
**Location**: `battle_spatial.py` - pellet consumption logic

When a pellet is eaten, call:
```python
material_drop = pellet.get_material_drop()
if material_drop:
    material_type_name, quantity = material_drop
    material_type = MaterialType[material_type_name]
    material = BuildingMaterial(
        material_id=str(uuid.uuid4()),
        material_type=material_type,
        position=Vector2D(pellet.x, pellet.y),
        quantity=quantity
    )
    self.materials.append(material)
```

### 2. Building Behavior Update Loop
**Location**: `battle_spatial.py` - main update method

Add to the update loop:
```python
# Update building tasks
for bc in self._creatures:
    if hasattr(bc.creature, 'belief_system'):
        # Check if creature should start building
        need = self.building_system.identify_building_need(
            bc.creature, 
            self.environment, 
            self.structures
        )
        
        if need and not self.building_system.get_active_task(bc.creature.creature_id):
            # Start building task
            structure_type = self.building_system.select_structure_type(
                need, 
                bc.creature.traits
            )
            location = self.building_system.find_build_location(
                bc.position,
                structure_type,
                (0, 0, self.arena.width, self.arena.height),
                self.structures
            )
            if location:
                self.building_system.start_building_task(
                    bc.creature.creature_id,
                    structure_type,
                    location
                )
```

### 3. Structure Completion
When a building task completes:
```python
from src.models.structure import Structure, get_blueprint
import uuid

blueprint = get_blueprint(task.structure_type)
structure = Structure(
    structure_id=str(uuid.uuid4()),
    structure_type=task.structure_type,
    position=task.target_position,
    tiles=[],  # Calculate from blueprint pattern
    builder_id=creature_id,
    completion=1.0,
    durability=1.0
)
structure.activate()
self.structures.append(structure)

# Reward the builder
if hasattr(creature, 'belief_system'):
    self.intervention_system.reward_construction(
        creature_id,
        creature.belief_system,
        task.structure_type.value,
        (task.target_position.x, task.target_position.y)
    )
```

### 4. Structure Effects
Apply structure effects to nearby creatures:
```python
for structure in self.structures:
    if not structure.is_complete() or not structure.effects_active:
        continue
    
    blueprint = get_blueprint(structure.structure_type)
    effects = blueprint.effects
    
    # Apply effects to nearby creatures
    for bc in self._creatures:
        dist = math.sqrt(
            (bc.position.x - structure.position.x)**2 +
            (bc.position.y - structure.position.y)**2
        )
        
        if dist < 30.0:  # Effect radius
            # Apply bonuses (hp_regen_bonus, breeding_success_bonus, etc.)
            pass
```

### 5. Material Carrying
Track materials carried by creatures:
```python
# Add to BattleCreature or Creature
self.carried_materials: List[BuildingMaterial] = []

# When creature picks up material
material.carrier_id = creature.creature_id
creature.carried_materials.append(material)

# When creature places material
material.carrier_id = None
creature.carried_materials.remove(material)
```

## Notes

The core building system is fully implemented and integrated. The remaining tasks are:
1. **Gameplay hooks** - connecting building behavior to the update loop
2. **Material drops** - spawning materials when pellets are eaten
3. **Structure effects** - applying bonuses to nearby creatures
4. **UI integration** - rendering structures and materials (Phase 6)

These can be added incrementally during testing and polish.
