# How to Interact with Black & White Systems

## Current State: Automatic Background Systems

Right now, all Black & White systems work **automatically** during gameplay:

### What's Happening Automatically

1. **Creatures Learn** - When creatures eat pellets, nearby creatures observe and learn
2. **Knowledge Inherits** - When creatures breed, offspring inherit parents' beliefs
3. **Dilemmas Trigger** - Every 30 seconds, the system checks for ethical dilemmas
4. **Ethics Track** - Your actions are tracked (though you can't take actions yet)

### What You Can Observe

**In the Battle Log** (bottom left):
- `"[creature] ate a pellet!"` - Observable action broadcast
- `"[offspring] inherited X instincts"` - Knowledge inheritance
- `"DILEMMA: [title]"` - Ethical dilemma detected
- `"Black & White systems initialized"` - Systems active

**In Creature Behavior**:
- Creatures cluster around successful food sources
- Offspring head to food locations without exploring
- Learning happens faster with hands-off observation

## How to Add Player Interaction (Future Enhancement)

The **ScientificCursor** system from Phase 1 provides player interaction tools, but it's not integrated into the main game UI yet. Here's what's available:

### Available Tools (Not Yet in UI)

From `src/systems/scientific_cursor.py`:

1. **Observe Tool** - Watch creatures without interfering
2. **Food Dispenser** - Reward creatures with food
3. **Area Marker** - Mark zones for study
4. **Stimulus Tool** - Discourage behaviors

### Quick Integration Option

If you want to add basic interaction NOW, here's the simplest approach:

**Add Keyboard Shortcuts** (in `main.py`):

```python
# In the event handling loop, add:

if event.type == pygame.KEYDOWN:
    if event.key == pygame.K_r:  # R = Reward
        # Spawn food pellet at mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Convert screen to world coordinates
        world_x = (mouse_x - offset_x) / zoom
        world_y = (mouse_y - offset_y) / zoom
        # Create pellet at that location
        pellet = create_random_pellet(world_x, world_y)
        battle.arena.add_pellet(pellet)
        # Record ethics action
        if hasattr(battle, 'ethics_system'):
            battle.ethics_system.record_action(
                "reward_food", 
                welfare=5, ecosystem=0, 
                integrity=0, intervention=10
            )
```

### Full UI Integration (Bigger Task)

For complete interaction, you'd need to:

1. **Add Cursor Mode Selector** - UI buttons to switch tools
2. **Mouse Click Handlers** - Detect clicks on creatures/areas
3. **Dilemma Popup** - Modal dialog for ethical choices
4. **Ethics Dashboard** - Show current ethics scores
5. **Assistant Panel** - Display AI advisor recommendations

## Recommended Next Steps

### Option 1: Just Watch (Current)
- Run `py main.py`
- Watch the battle log for learning events
- Observe creature behavior patterns
- See knowledge inheritance in action

### Option 2: Add Simple Keyboard Controls
- Add hotkeys for food dispensing
- Add hotkeys for observation mode
- Display ethics scores in UI

### Option 3: Full UI Integration
- Create cursor tool selector
- Add dilemma resolution popup
- Build ethics dashboard
- Implement assistant advice panel

## What Would You Like?

1. **Keep it automatic** - Just observe the learning happen
2. **Add keyboard shortcuts** - Simple interaction without UI
3. **Build full UI** - Complete Black & White interaction experience

Let me know which direction you'd prefer!

## Current Files

- **Systems**: All in `src/systems/` (working automatically)
- **Cursor Tools**: `src/systems/scientific_cursor.py` (ready but not connected)
- **Main Game**: `main.py` (where UI integration would go)
