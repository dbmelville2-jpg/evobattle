# Rendering System Documentation

## Overview

The rendering system in EvoBattle is built on **Pygame** and follows a component-based architecture. It is designed to visualize a real-time spatial simulation with support for zooming, panning, and detailed UI inspection.

The system is orchestrated by the `GameWindow` class, which manages the main game loop and delegates rendering tasks to specialized renderers for different aspects of the simulation (Arena, Creatures, UI, etc.).

## Core Components

### 1. Game Window (`game_window.py`)
The `GameWindow` is the root of the rendering hierarchy.
- **Responsibilities**:
  - Initializes Pygame display and clock.
  - Runs the main game loop (`run()` method).
  - Handles input events (keyboard, mouse) and delegates them.
  - Manages the `Camera`.
  - Coordinates the drawing order: Arena -> Creatures -> UI -> Event FX.
  - Displays FPS and performance metrics.

### 2. Camera System (`camera.py`)
The `Camera` class handles the transformation between **World Coordinates** (simulation space) and **Screen Coordinates** (pixel space).
- **Features**:
  - **Panning**: Moving the view around the arena.
  - **Zooming**: Scaling the view in and out.
  - **Smoothing**: Smooth interpolation for camera movement and zooming.
  - **Coordinate Conversion**: `world_to_screen()` and `screen_to_world()` methods.

### 3. Specialized Renderers

#### Arena Renderer (`arena_renderer.py`)
Responsible for drawing the static and environmental layers.
- **Terrain**: Draws the background tiles (Grass, Desert, Rock, etc.).
- **Grid**: Optional grid overlay.
- **Hazards**: Visualizes environmental hazards (e.g., poison clouds).
- **Weather**: Overlays weather effects (Rain, Fog, Storm) with animation.
- **Delegation**: Calls `PelletRenderer` and `BuildingRenderer` to draw their respective entities.

#### Creature Renderer (`creature_renderer.py`)
Visualizes the agents (creatures) in the simulation.
- **Visuals**: Renders creatures as colored circles (hue based on genetics).
- **LOD (Level of Detail)**: Optimizes rendering based on zoom level and creature count (e.g., hiding names/bars when zoomed out).
- **Status Indicators**:
  - Health bars (Green/Yellow/Red).
  - Hunger/Energy bars.
  - Infection tints (visual feedback for disease).
  - Combat indicators (pulsing rings, target lines).
  - Carrying indicators (icons for materials being carried).

#### Pellet Renderer (`pellet_renderer.py`)
Visualizes food resources.
- **Traits**: Size and color reflect the pellet's nutritional and toxic properties.
- **Generation**: Displays generation numbers for evolved plant life.
- **Tooltips**: Shows detailed stats on hover.

#### Building Renderer (`building_renderer.py`)
Visualizes the construction system.
- **Materials**: Renders raw materials (Logs, Stones, Fiber) on the ground.
- **Buildings**: Renders structures tile-by-tile.
  - Visualizes construction progress (tiles appear as built).
  - Distinct textures/colors for different building types (Shelter, Nest, etc.).

#### Event Animator (`event_animator.py`)
Handles transient visual effects ("juice").
- **Floating Text**: Damage numbers, healing values, "CRIT", "MISS".
- **Particles**: Explosions, blood splatters, eating crumbs.
- **Architecture**: Uses an object pool for performance to reuse effect instances.
- **World Space**: Effects are pinned to world coordinates, so they move correctly when the camera pans.

### 4. UI System

#### UI Components (`ui_components.py`)
The central manager for the Heads-Up Display (HUD).
- **Panels**:
  - **Weather/Time**: Top-left info.
  - **Biome Info**: Terrain details.
  - **Genetic Strains**: Scrollable list of active species/strains.
  - **Disease**: Active pathogens.
  - **Pellet Ecosystem**: Plant life statistics.
  - **Neural Patterns**: Brain statistics.
- **Scientific Toolbar**: Bottom bar for selecting interaction tools (God-game mechanics).
- **Event Log**: Scrolling feed of battle events.

#### Inspectors

**Creature Inspector (`creature_inspector.py`)**

Detailed popup when clicking a creature. Shows stats, history, skills, personality, etc.

**Features:**
- Click any creature to open inspector
- Scrollable panel for long content (handles overflow gracefully)
- Auto-hide when clicking elsewhere in the game view
- Comprehensive information display
- Visual highlighting of selected creature

**Displayed Information:**
- **Basic Info**: Name, Strain ID, Age, Generation
- **Vital Stats**: HP (current/max), Energy, Hunger level
- **Combat Stats**: Attack, Defense, Speed with active modifiers
- **Traits**: All genetic traits with descriptions and effects
- **Skills**: Skill levels, progress bars, recent improvements (Melee Attack, Dodge, Teamwork, Intimidation, Leadership, etc.)
- **Personality**: All 7 personality traits (aggression, caution, loyalty, pride, curiosity, patience, sociability)
- **Relationships**: Parents, children, siblings, allies, rivals, revenge targets
- **History**: Battles fought, kills, damage dealt/received, offspring count, achievements
- **Disease Status**: Active infection, infection stage, disease effects (if infected)
- **Current Focus**: Attention system focus (FORAGING, COMBAT, FLEEING, BUILDING, etc.), target entity, priority scores

**Interaction:**
- Left-click creature → Open inspector
- Mouse wheel / scroll → Scroll through content
- Click outside inspector → Close inspector
- Selected creature highlighted with ring in game view

**Pellet Inspector (`pellet_inspector.py`)**

Similar inspection for food sources, showing detailed nutritional and evolutionary information.

**Features:**
- Click any pellet to inspect
- Shows detailed nutritional information
- Displays evolutionary history and lineage
- Strain and generation tracking

**Displayed Information:**
- **Basic Info**: Pellet ID, Strain ID, Generation number, Age
- **Nutrition**: Food value (hunger restored), Toxicity level (0.0-1.0), Palatability rating
- **Physical Traits**: Size modifier, Visual appearance
- **Growth**: Growth rate, Reproduction cooldown, Max age
- **Lifecycle Stats**: Times targeted by creatures, Times successfully eaten, Survival rate
- **Evolutionary History**: Parent pellet ID, Mutations from parent, Offspring count

**Interaction:**
- Left-click pellet → Open inspector
- Click outside → Close inspector
- Selected pellet highlighted in game view

#### Scientific Cursor (`scientific_cursor.py`)
Manages the player's interaction with the world.
- **Tools**: Observe, Feed, Zap, Mark Area, Move, etc.
- **Resources**: Tracks "Tool Charge" (mana/energy) for using powers.
- **Visuals**: Renders the cursor and active area markers (Safe Zones, Danger Zones).

## Rendering Pipeline

The `GameWindow.run()` loop executes the following sequence every frame:

1.  **Update**:
    *   Physics/Simulation update (`battle.update()`).
    *   Camera smoothing update.
    *   Event Animator update (particles/effects).
2.  **Input**:
    *   Process Pygame events.
    *   Handle UI interactions.
    *   Handle Camera controls.
3.  **Render**:
    *   `screen.fill()` (Clear background).
    *   `ArenaRenderer.render()` (Terrain, Grid, Resources, Buildings).
    *   `CreatureRenderer.render()` (Creatures).
    *   `UIComponents.render()` (HUD, Panels, Toolbar).
    *   `EventAnimator.render()` (Particles, Floating Text).
    *   `ScientificCursor.render()` (Mouse cursor overlay).
    *   `PauseMenu.render()` (If paused).
4.  **Display**:
    *   `pygame.display.flip()` (Swap buffers).
    *   FPS limiting (`clock.tick()`).

## Key Design Patterns

- **Separation of Concerns**: Logic is separated from presentation. The `Battle` model knows nothing about Pygame; Renderers read the `Battle` state to draw it.
- **Coordinate Systems**: Strict separation between World (simulation) and Screen (pixel) coordinates via the `Camera`.
- **Caching**: Text surfaces and heavy assets are cached to maintain high FPS.
- **LOD**: Rendering complexity scales down as the view zooms out to handle large populations.
