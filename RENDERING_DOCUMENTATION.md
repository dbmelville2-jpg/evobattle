# Rendering & UI System Documentation

## Overview

The EvoBattle rendering system provides real-time visualization of spatial battles using Pygame. It features an event-driven architecture that separates game logic from visual presentation, making it easy to extend and customize.

![EvoBattle Rendering Screenshot](https://github.com/user-attachments/assets/e876d6cc-186d-4e7c-bdf3-6d89972b03e8)

## Architecture

### Event-Driven Design

The rendering system subscribes to battle events and reacts with appropriate visual feedback:

```python
battle.add_event_callback(on_battle_event)
```

This allows the rendering layer to remain decoupled from game logic while staying synchronized with battle state.

### Core Components

1. **GameWindow** - Main game loop and Pygame lifecycle management
2. **ArenaRenderer** - Renders the 2D battle arena with team zones
3. **CreatureRenderer** - Displays creatures with HP/energy bars
4. **UIComponents** - Manages HUD overlays and information displays
5. **EventAnimator** - Creates visual effects for battle events

## Quick Start

### Basic Usage

```python
from src.systems.battle_spatial import SpatialBattle
from src.rendering import (
    GameWindow, ArenaRenderer, CreatureRenderer, 
    UIComponents, EventAnimator
)

# Create battle
battle = SpatialBattle(player_team, enemy_team)

# Create rendering components
window = GameWindow(width=1200, height=800, fps=60)
arena_renderer = ArenaRenderer(show_grid=True)
creature_renderer = CreatureRenderer()
ui_components = UIComponents()
event_animator = EventAnimator()

# Connect battle events to UI
def on_battle_event(event):
    ui_components.add_event_to_log(event)
    event_animator.add_battle_event(event)

battle.add_event_callback(on_battle_event)

# Run visualization (simplified)
window.run(battle, arena_renderer, creature_renderer, 
           ui_components, event_animator)
```

### Complete Example

See `examples/pygame_rendering_demo.py` for a full working example.

## Component Details

### GameWindow

Manages the Pygame window, event loop, and frame timing.

**Key Methods:**
- `__init__(width, height, fps, title)` - Initialize window
- `run(battle, renderers...)` - Main game loop
- `handle_events()` - Process input events
- `get_screen_pos_from_world(x, y, arena)` - World-to-screen conversion

**Input Handling:**
- `ESC` - Exit the application
- `SPACE` - Pause/resume the battle
- Custom callbacks via `add_input_callback()`

### ArenaRenderer

Renders the 2D battle arena with visual zones for each team.

**Features:**
- Team-colored background zones (blue for player, red for enemy)
- Optional grid overlay for spatial reference
- Center line dividing teams
- Hazard and resource markers (if present)

**Customization:**
```python
arena_renderer = ArenaRenderer(
    grid_color=(40, 40, 50),
    border_color=(100, 100, 120),
    show_grid=True
)
```

### CreatureRenderer

Displays creatures as colored circles with status information.

**Features:**
- Team-colored creatures (blue = player, red = enemy)
- HP bars above creatures (color-coded by health percentage)
- Energy bars for ability usage
- Creature names and levels below
- Direction indicators showing movement
- Target lines showing AI behavior

**Customization:**
```python
creature_renderer = CreatureRenderer(
    player_color=(80, 120, 255),
    enemy_color=(255, 100, 100),
    radius=15
)
```

### UIComponents

Manages HUD overlays and information displays.

**Features:**
- Top bar with battle title and time
- Team status panels (left and right)
  - Alive count
  - Individual creature HP bars
- Battle feed / event log (bottom)
- Pause indicator (center)
- Battle end overlay with winner
- Controls help (bottom right)

**Customization:**
```python
ui_components = UIComponents(max_log_entries=8)

# Manually add events to log
ui_components.add_event_to_log(battle_event)
```

### EventAnimator

Creates visual effects for battle events.

**Supported Animations:**
- Floating damage numbers (red, rising)
- Floating heal numbers (green, rising)
- "CRIT!" text for critical hits
- "MISS" text for missed attacks
- "Super Effective!" text
- "FAINTED" text for defeated creatures

**Usage:**
```python
event_animator = EventAnimator()

# Process battle events
event_animator.add_battle_event(event)
event_animator.process_events(screen, battle)

# Update and render in game loop
event_animator.update(delta_time)
event_animator.render(screen)
```

## Battle Events

The rendering system responds to these battle events:

| Event Type | Visual Response |
|------------|----------------|
| `BATTLE_START` | Added to event log |
| `CREATURE_SPAWN` | Initial creature placement |
| `CREATURE_MOVE` | Position update |
| `ABILITY_USE` | Event log entry |
| `DAMAGE_DEALT` | Floating damage number, log entry |
| `HEALING` | Floating heal number, log entry |
| `CRITICAL_HIT` | "CRIT!" popup |
| `MISS` | "MISS" popup |
| `SUPER_EFFECTIVE` | "Super Effective!" popup |
| `CREATURE_FAINT` | "FAINTED" popup, log entry |
| `BATTLE_END` | Winner overlay |

## Coordinate Systems

### World Space
- Battle arena uses floating-point coordinates
- Origin (0, 0) at top-left
- Units are abstract (typically 100x60 for arena)

### Screen Space
- Pygame window uses pixel coordinates
- Origin (0, 0) at top-left
- Margins reserved for UI (top: 100px, sides: 50px, bottom: 150px)

### Conversion

All renderers include `_world_to_screen()` methods for coordinate conversion:

```python
screen_x = margin + (world_x / arena_width) * screen_width
screen_y = margin + (world_y / arena_height) * screen_height
```

## Extending the System

### Adding Custom Renderers

Create a new renderer class:

```python
class CustomRenderer:
    def render(self, screen: pygame.Surface, battle: SpatialBattle):
        # Your rendering code here
        pass
```

Add it to the game loop:

```python
custom_renderer = CustomRenderer()

# In game loop
custom_renderer.render(window.screen, battle)
```

### Adding Custom Animations

Extend the `EventAnimator`:

```python
class CustomEventAnimator(EventAnimator):
    def _create_effect_for_event(self, event, screen, battle):
        super()._create_effect_for_event(event, screen, battle)
        
        if event.event_type == BattleEventType.YOUR_CUSTOM_EVENT:
            # Create custom effect
            self.effects.append(AnimatedEffect(...))
```

### Custom UI Panels

Extend `UIComponents`:

```python
class ExtendedUI(UIComponents):
    def render(self, screen, battle, paused):
        super().render(screen, battle, paused)
        
        # Add your custom UI
        self._render_custom_panel(screen)
```

## Performance Considerations

### Optimization Tips

1. **Limit Event Log Size**: Use `max_log_entries` parameter
2. **Reduce FPS**: Lower FPS for less demanding hardware
3. **Disable Grid**: Set `show_grid=False` for simpler rendering
4. **Batch Drawing**: Group similar draw calls together

### Frame Rate

Default is 60 FPS. Adjust based on needs:

```python
window = GameWindow(fps=30)  # Lower for better performance
window = GameWindow(fps=120) # Higher for smoother animation
```

## Troubleshooting

### No Display / Black Screen
- Ensure Pygame is installed: `pip install pygame`
- Check that SDL video driver is available
- For headless testing, set: `os.environ['SDL_VIDEODRIVER'] = 'dummy'`

### Creatures Not Visible
- Verify creatures are alive: `creature.is_alive()`
- Check arena bounds and creature positions
- Ensure world-to-screen conversion is correct

### Events Not Showing
- Verify event callbacks are registered: `battle.add_event_callback(callback)`
- Check that UI components are being updated in the game loop
- Ensure event types are in the supported list

### Performance Issues
- Reduce FPS target
- Disable grid rendering
- Limit number of creatures
- Check for expensive operations in event callbacks

## Examples

### Minimal Example

```python
import pygame
from src.systems.battle_spatial import SpatialBattle
from src.rendering import GameWindow, ArenaRenderer, CreatureRenderer

# Create battle
battle = SpatialBattle([player], [enemy])

# Setup rendering
pygame.init()
window = GameWindow()
arena_renderer = ArenaRenderer()
creature_renderer = CreatureRenderer()

# Simple game loop
while not battle.is_over:
    window.handle_events()
    battle.update(1/60)  # 60 FPS
    
    window.clear_screen()
    arena_renderer.render(window.screen, battle)
    creature_renderer.render(window.screen, battle)
    window.update_display()

window.quit()
```

### Screenshot Generation

See `tests/test_rendering_screenshot.py` for an example of generating screenshots without a visible window.

## Future Enhancements

Potential additions to the rendering system:

- **Sprite Support**: Load and display sprite sheets for creatures
- **Particle Effects**: Add particle systems for abilities
- **Camera Controls**: Zoom and pan functionality
- **Replay System**: Record and playback battles
- **Network Sync**: Multiplayer visualization
- **Menu System**: Main menu, pause menu, settings
- **Sound Effects**: Audio feedback for events
- **Advanced Animations**: Smooth interpolation, attack swooshes
- **Status Effect Icons**: Visual indicators above creatures

## API Reference

### GameWindow

```python
GameWindow(
    width: int = 1200,
    height: int = 800,
    fps: int = 60,
    title: str = "EvoBattle - Spatial Combat Arena"
)
```

### ArenaRenderer

```python
ArenaRenderer(
    grid_color: tuple = (40, 40, 50),
    border_color: tuple = (100, 100, 120),
    hazard_color: tuple = (200, 50, 50),
    resource_color: tuple = (50, 200, 100),
    show_grid: bool = True
)
```

### CreatureRenderer

```python
CreatureRenderer(
    player_color: tuple = (80, 120, 255),
    enemy_color: tuple = (255, 100, 100),
    radius: int = 15
)
```

### UIComponents

```python
UIComponents(
    max_log_entries: int = 8
)
```

### EventAnimator

```python
EventAnimator()
# No parameters for initialization
```

## Contributing

When adding new rendering features:

1. Follow the event-driven pattern
2. Keep renderers modular and independent
3. Use world-to-screen conversion helpers
4. Document new components thoroughly
5. Add examples demonstrating usage
6. Consider performance implications

## See Also

- [Battle System Documentation](BATTLE_SYSTEM_DOCUMENTATION.md)
- [Core Models Documentation](MODELS_DOCUMENTATION.md)
- [Spatial Battle System](src/systems/battle_spatial.py)
- [Pygame Documentation](https://www.pygame.org/docs/)
