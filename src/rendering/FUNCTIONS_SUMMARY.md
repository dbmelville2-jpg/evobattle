# EvoBattle Rendering - Function Summary

This document provides a comprehensive overview of all functions, classes, and methods in the `src/rendering` directory.

---

## Table of Contents

- [arena_renderer.py](#arena_rendererpy) - 2D battle arena rendering
- [building_renderer.py](#building_rendererpy) - Building and material rendering
- [camera.py](#camerapy) - 2D camera system with pan and zoom
- [creature_inspector.py](#creature_inspectorpy) - Interactive creature details panel
- [creature_renderer.py](#creature_rendererpy) - Creature sprite rendering
- [event_animator.py](#event_animatorpy) - Battle event visual effects
- [game_window.py](#game_windowpy) - Main Pygame window and game loop
- [pause_menu.py](#pause_menupy) - Pause screen with controls
- [pellet_inspector.py](#pellet_inspectorpy) - Interactive pellet details panel
- [pellet_renderer.py](#pellet_rendererpy) - Pellet sprite rendering
- [post_game_summary.py](#post_game_summarypy) - Battle results screen
- [scientific_cursor.py](#scientific_cursorpy) - Player interaction tools
- [trait_dashboard.py](#trait_dashboardpy) - Trait analytics visualization
- [ui_components.py](#ui_componentspy) - Main UI overlays and panels
- [ui_components_expanded_feed.py](#ui_components_expanded_feedpy) - Expanded battle feed mode

---

## arena_renderer.py

### Classes

#### `ArenaRenderer`
Renders the 2D battle arena including boundaries, grid, terrain, and environmental effects.

**Methods:**
- `__init__(grid_color, border_color, hazard_color, resource_color, show_grid, pellet_renderer, building_renderer)` - Initialize renderer
- `_load_assets()` - Load terrain and weather textures
- `render(screen, battle, camera, selected_creature_id, hovered_creature_id, selected_pellet_id, show_debug)` - Render arena and all contents
- `_render_terrain(screen, battle, camera)` - Render terrain background
- `_render_grid(screen, width, height, camera)` - Render grid lines
- `_render_border(screen, width, height, camera)` - Render arena border
- `_render_creature(screen, creature, camera, is_selected, is_hovered, show_debug)` - Render single creature
- `_render_health_bar(screen, creature, screen_pos, radius_px)` - Render health bar above creature
- `_render_hazard(screen, hazard, camera)` - Render environmental hazard
- `_render_resource(screen, pellet, camera)` - Render resource pellet (fallback)
- `_render_weather(screen, weather, camera)` - Render weather effects

---

## building_renderer.py

### Classes

#### `BuildingRenderer`
Renders buildings and building materials in the arena.

**Methods:**
- `__init__()` - Initialize renderer and load assets
- `_load_material_assets()` - Load building material sprite sheet
- `render_materials(screen, materials, arena, camera)` - Render building materials on ground
- `render_buildings(screen, buildings, arena, camera)` - Render all buildings
- `_render_building(screen, structure, arena, camera)` - Render individual building tile-by-tile

---

## camera.py

### Classes

#### `Camera`
A 2D camera for scrolling and zooming around the game world.

**Attributes:**
- `position` - Center position in world coordinates
- `zoom` - Current zoom level (1.0 = normal)
- `viewport_width`, `viewport_height` - View area dimensions
- `min_zoom`, `max_zoom` - Zoom constraints

**Methods:**
- `__init__(viewport_width, viewport_height, initial_position, initial_zoom)` - Initialize camera
- `update(delta_time)` - Update camera position and zoom with smoothing
- `world_to_screen(world_pos)` - Convert world coordinates to screen coordinates
- `screen_to_world(screen_pos)` - Convert screen coordinates to world coordinates
- `move(dx, dy)` - Move the camera target
- `set_zoom(zoom_level, focus_point)` - Set target zoom level
- `_clamp_position(pos)` - Keep camera within world bounds
- `zoom_in(amount)` - Zoom in by fixed amount
- `zoom_out(amount)` - Zoom out by fixed amount
- `pan(dx, dy)` - Pan the camera (alias for move)

---

## creature_inspector.py

### Classes

#### `CreatureInspector`
Interactive UI panel for inspecting creature details.

**Displays:**
- Basic stats and status
- Personality traits
- Skill proficiency
- Battle history and statistics
- Relationships and family
- Current focus/attention

**Methods:**
- `__init__()` - Initialize inspector
- `_render_symbol(surface, key_or_symbol, x, y, base_font, color)` - Render icon or text symbol
- `select_creature(creature)` - Select a creature to inspect
- `show()` - Show inspector panel with animation
- `hide()` - Hide inspector panel with animation
- `toggle_visibility()` - Toggle inspector visibility
- `toggle_pin()` - Toggle pinned state
- `update(dt)` - Update inspector state (animations, auto-hide)
- `_is_mouse_over_panel()` - Check if mouse is over panel
- `handle_scroll(direction)` - Handle scroll input
- `handle_mouse_event(event, screen)` - Handle mouse events for dragging
- `_ensure_icons_converted()` - Convert loaded icons for display
- `render(screen)` - Render the inspector panel
- `_render_content(creature, panel_width, battle_creature)` - Render all content
- `_render_section_header(surface, title, x, y)` - Render section header
- `_render_wrapped_text(surface, text, x, y, max_width, font, color)` - Render text with word wrapping
- `_get_event_icon(event_type)` - Get icon for event type

---

## creature_renderer.py

### Classes

#### `CreatureRenderer`
Renders creatures in the battle arena as colored circles with visual indicators.

**Methods:**
- `__init__(radius)` - Initialize renderer
- `render(screen, battle, camera)` - Render all creatures
- `_render_creature(screen, creature, battle, camera, lod_level, mouse_pos)` - Render single creature
- `_draw_hp_bar(screen, creature, screen_pos, radius, simplified)` - Draw HP bar above creature
- `_draw_hunger_bar(screen, creature, screen_pos, radius)` - Draw hunger bar
- `_draw_energy_bar(screen, creature, screen_pos, radius)` - Draw energy bar
- `_draw_name(screen, creature, screen_pos, radius)` - Draw creature name
- `_get_cached_text(text, font, color)` - Get cached text surface
- `_render_creature_carrying_materials(screen, creature, screen_x, screen_y)` - Show material carrying indicator

---

## event_animator.py

### Classes

#### `Particle`
Represents a simple visual particle in world space.

**Methods:**
- `__init__(position, velocity, color, size, lifetime, shape)` - Initialize particle
- `update(delta_time)` - Update particle position and age
- `is_expired()` - Check if particle should be removed
- `render(screen, camera)` - Render particle

#### `AnimatedEffect`
Represents a temporary visual effect in world space (damage numbers, etc.).

**Methods:**
- `__init__(position, text, color, lifetime, velocity)` - Initialize effect
- `reset(position, text, color, lifetime, velocity)` - Reset for object pooling
- `update(delta_time)` - Update effect animation
- `is_expired()` - Check if effect should be removed
- `render(screen, camera)` - Render the effect

#### `EventAnimator`
Manages visual effects and animations for battle events.

**Methods:**
- `__init__()` - Initialize animator
- `_get_effect_from_pool(position, text, color, lifetime, velocity)` - Get effect from pool
- `_return_effect_to_pool(effect)` - Return effect to pool
- `add_battle_event(event)` - Process battle event and create effects
- `on_battle_event(event)` - Callback for battle events
- `process_events(screen, battle, camera)` - Process pending events
- `create_explosion(position, color, count)` - Create explosion effect
- `create_blood_splatter(position, color, count)` - Create blood splatter effect
- `create_eat_crumbs(position, color, count)` - Create crumb particles
- `_create_effect_for_event(event, screen, battle, camera)` - Create visual effect for event
- `update(delta_time)` - Update all active effects
- `render(screen, camera)` - Render all active effects
- `clear()` - Clear all effects

---

## game_window.py

### Classes

#### `GameWindow`
Main game window that manages the Pygame display and game loop.

**Methods:**
- `__init__(width, height, fps, title)` - Initialize game window
- `set_fps(fps)` - Set target FPS at runtime
- `toggle_fps_display()` - Toggle FPS counter display
- `_render_fps(screen, actual_fps)` - Render FPS counter overlay
- `set_battle(battle)` - Set the battle to visualize
- `add_input_callback(callback)` - Add callback for input events
- `handle_events()` - Process Pygame events
- `clear_screen()` - Clear screen with background color
- `update_display()` - Flip display buffer
- `get_actual_fps()` - Get actual measured FPS
- `run(battle, arena_renderer, creature_renderer, ui_components, event_animator)` - Run main game loop
- `quit()` - Clean up and quit Pygame
- `get_screen_pos_from_world(world_x, world_y, arena_width, arena_height)` - Convert world to screen coordinates
- `get_arena_bounds()` - Get screen bounds for arena rendering area

---

## pause_menu.py

### Classes

#### `PauseMenuAction` (Enum)
Actions that can be taken from the pause menu.
- `NONE`, `RESUME`, `RESTART`, `QUIT`

#### `PauseMenu`
Interactive pause menu with button controls.

**Methods:**
- `__init__()` - Initialize pause menu
- `show()` - Show the pause menu
- `hide()` - Hide the pause menu
- `toggle()` - Toggle pause menu visibility
- `handle_input(event)` - Handle input events, returns action to take
- `_select_option()` - Handle option selection
- `render(screen)` - Render the pause menu
- `_render_main_menu(screen)` - Render main pause menu
- `_render_quit_confirmation(screen)` - Render quit confirmation dialog

---

## pellet_inspector.py

### Classes

#### `PelletInspector`
Interactive UI panel for inspecting pellet details.

**Displays:**
- Basic traits and status
- Lifecycle events timeline
- Targeting and avoidance statistics
- Lineage and offspring information

**Methods:**
- `__init__()` - Initialize inspector
- `select_pellet(pellet)` - Select a pellet to inspect
- `show()` - Show inspector panel
- `hide()` - Hide inspector panel
- `toggle_visibility()` - Toggle inspector visibility
- `update(dt)` - Update inspector state
- `handle_scroll(direction)` - Handle scroll input
- `handle_mouse_event(event, screen)` - Handle mouse events
- `is_mouse_over(mouse_pos, screen_size)` - Check if mouse is over panel
- `render(screen)` - Render the inspector panel
- `_render_content(pellet, panel_width)` - Render all content
- `_render_section_header(surface, title, x, y)` - Render section header
- `_get_event_icon(event_type)` - Get icon for event type

---

## pellet_renderer.py

### Classes

#### `PelletRenderer`
Renders pellets in the battle arena as colored circles with trait-based properties.

**Methods:**
- `__init__(base_radius, show_generation, show_stats_on_hover)` - Initialize renderer
- `render(screen, pellets, camera, selected_pellet_id)` - Render all pellets
- `_render_pellet(screen, pellet, camera, is_selected)` - Render single pellet
- `render_pellet_tooltip(screen, pellet, screen_pos)` - Render tooltip with pellet stats

---

## post_game_summary.py

### Classes

#### `PostGameSummary`
Post-game summary screen showing battle results and statistics.

**Displays:**
- Final battle outcome (winner/survivors)
- Battle duration and statistics
- Top performers and achievements
- Export options

**Methods:**
- `__init__()` - Initialize post-game summary
- `show(battle)` - Show summary for a battle
- `hide()` - Hide the summary
- `_compile_stats()` - Compile battle statistics
- `handle_input(event)` - Handle input events, returns action ('replay', 'menu', 'export')
- `export_stats()` - Export battle statistics to JSON file
- `render(screen)` - Render the summary
- `_render_section(surface, title, center_x, y)` - Render section header
- `_render_buttons(screen)` - Render action buttons

---

## scientific_cursor.py

### Classes

#### `CursorTool` (Enum)
Available scientific tools for player interaction.
- `OBSERVE`, `FOOD_DISPENSER`, `STIMULATOR`, `MARKER`, `SAMPLER`, `RELOCATOR`, `BARRIER`, `PHEROMONE`, `ASTEROID`, `APEX`

#### `MarkerType` (Enum)
Types of area markers.
- `SAFE`, `DANGER`, `FOOD_SOURCE`, `SHELTER`

#### `AreaMarker`
Represents a marked area in the simulation.

**Methods:**
- `is_expired(current_time)` - Check if marker has expired

#### `ScientificCursor`
Player's scientific interaction system managing tool selection and usage.

**Methods:**
- `__init__()` - Initialize cursor system
- `select_tool(tool)` - Select a new tool
- `can_use_tool()` - Check if current tool can be used
- `use_tool_charge()` - Consume charge for current tool
- `update(dt, current_time)` - Update cursor system (recharge, markers)
- `add_marker(position, marker_type, radius, duration, current_time)` - Add area marker
- `get_markers_at_position(position)` - Get all markers affecting a position
- `get_cursor_color()` - Get cursor color based on ethics score
- `get_cursor_size()` - Get cursor size based on current tool
- `get_tool_name()` - Get display name of current tool
- `get_tool_description()` - Get description of current tool

#### `CursorRenderer`
Renders the scientific cursor and its effects.

**Methods:**
- `__init__()` - Initialize cursor renderer
- `_load_icons()` - Load tool icons
- `render_cursor(screen, cursor, mouse_pos)` - Render cursor at mouse position
- `render_markers(screen, cursor, camera)` - Render area markers

---

## trait_dashboard.py

### Classes

#### `TraitAnalyticsDashboard`
Interactive dashboard for trait analytics visualization.

**Displays:**
- Total trait statistics
- Most successful traits
- Recent trait discoveries and injections
- Generation-by-generation timeline

**Methods:**
- `__init__(analytics)` - Initialize dashboard
- `toggle()` - Toggle dashboard visibility
- `show()` - Show the dashboard
- `hide()` - Hide the dashboard
- `refresh_data()` - Refresh cached dashboard data
- `handle_event(event, screen_width, screen_height)` - Handle input events
- `render(screen)` - Render the dashboard
- `_render_content()` - Render all dashboard content
- `_render_stats_overview(surface, x, y)` - Render statistics overview
- `_render_top_traits(surface, x, y)` - Render top traits section
- `_render_recent_events(surface, x, y)` - Render recent events section
- `_render_section_header(surface, text, x, y)` - Render section header

---

## ui_components.py

### Classes

#### `UIComponents`
Manages UI overlays and information displays (main UI system).

**Displays:**
- Battle state and statistics
- Population panels (genetic strains, diseases, pellets, neural patterns)
- Event log/battle feed
- Weather and biome information
- Scientific toolbar
- Pause indicators

**Methods:**
- `__init__(max_log_entries, show_pellet_stats)` - Initialize UI components
- `add_event_to_log(event)` - Add battle event to display log
- `handle_event(event, battle, scientific_cursor)` - Handle UI interaction events
- `_get_cached_text(text, font, color)` - Get cached text surface
- `render(screen, battle, paused, scientific_cursor)` - Render all UI components
- `_load_tool_icons()` - Load tool icons from assets
- `render_scientific_toolbar(screen, battle, scientific_cursor)` - Render scientific toolbar
- `_render_panel_container(screen, x, y, width, height, title, panel_name)` - Render panel container with collapse toggle
- `_render_weather_panel(screen, battle)` - Render weather and time information
- `_render_biome_panel(screen, battle)` - Render biome information panel
- `_render_genetic_strains_panel(screen, battle)` - Render population by genetic strain or disease
- `_render_genetic_list(screen, battle, panel_x, content_y_start, content_height, content_rect)` - Render genetic strains list
- `_render_disease_list(screen, battle, panel_x, content_y_start, content_height, content_rect)` - Render disease strains list
- `_render_scrollbar(screen, panel_x, panel_width, content_y_start, content_height, total_content_height)` - Render scrollbar
- `_render_pellet_list(screen, battle, panel_x, content_y_start, content_height, content_rect)` - Render pellet strains list
- `_render_neural_patterns(screen, battle, panel_x, content_y_start, content_height, content_rect)` - Render neural network statistics
- `_render_strain_details_popup(screen, battle)` - Render detailed strain information popup

**Note:** This file is 2947 lines and contains many more private rendering methods for different UI panels and components.

---

## ui_components_expanded_feed.py

### Classes

#### `UIComponents`
Alternate UI components implementation with expanded battle feed mode.

**Methods:**
- `__init__(max_log_entries, show_pellet_stats)` - Initialize UI components
- `add_event_to_log(event)` - Add battle event to log
- `handle_event(event, battle, scientific_cursor)` - Handle UI events
- `_get_cached_text(text, font, color)` - Get cached text surface
- `render(screen, battle, paused, scientific_cursor)` - Render UI components
- `render_expanded_feed(screen, battle, simulation_speed, paused)` - Render full-screen detailed event log

---

## Summary

The `src/rendering` directory contains **16 Python files** organized into:

### Core Rendering
- **Arena Rendering**: 2D battle arena with terrain, grid, and environmental effects
- **Creature Rendering**: Creature sprites with HP/hunger/energy bars
- **Pellet Rendering**: Food pellets with trait-based visuals
- **Building Rendering**: Buildings and construction materials
- **Event Animation**: Visual effects for battle events (damage numbers, explosions, etc.)

### Camera System
- **Camera**: 2D pan and zoom with smooth interpolation
- **Coordinate Conversion**: World ↔ Screen coordinate transformation

### UI Components
- **Main UI**: Comprehensive HUD with population panels, event feed, weather, biome info
- **Creature Inspector**: Detailed creature information panel
- **Pellet Inspector**: Detailed pellet information panel
- **Pause Menu**: Interactive pause screen with controls
- **Post-Game Summary**: Battle results and statistics
- **Trait Dashboard**: Trait analytics visualization
- **Scientific Cursor**: Player interaction tools system

### Game Loop
- **Game Window**: Main Pygame window and game loop manager
- **Input Handling**: Event processing and callbacks
- **FPS Management**: Frame rate control and display

Each component is designed to work together to create a rich, interactive visualization of the EvoBattle simulation with comprehensive UI panels, inspectors, and visual effects.
