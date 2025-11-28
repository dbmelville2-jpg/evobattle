# Battle Story Mode Documentation

## Overview

The Battle Story Mode feature transforms raw battle events into engaging narratives that capture the drama, heroism, and memorable moments of combat. This system **uses local text processing** (completely free, no API required) to automatically generate story summaries at configurable intervals, creating shareable battle reports that bring the simulation to life.

## Features

### Local Story Generation (100% Free)
- **No API Costs**: Runs entirely locally using template-based narrative generation
- **Instant Results**: No network latency, stories generated in milliseconds
- **Works Offline**: No internet connection required
- **Multiple Narrative Tones**: Choose from dramatic, heroic, comedic, serious, or documentary styles
- **Automatic Summarization**: Stories generated at configurable intervals (default: 5 minutes)
- **Rich Context**: Incorporates battle statistics, key moments, and dramatic events

### Story Metrics
The system tracks and analyzes:
- **Combat Statistics**: Total attacks, critical hits, damage dealt, casualties
- **Lifecycle Events**: Births, deaths, resource collection
- **Dramatic Moments**: Comebacks, betrayals, last stands, alliances
- **Key Highlights**: Notable events and turning points

### Export & Sharing
- **Text Format**: Export as `.txt` files
- **Markdown Format**: Export as `.md` with formatting
- **Batch Export**: Save all generated stories at once
- **Directory Organization**: Automatically organized story archives

### Interactive UI
- **Story Viewer Panel**: Dedicated UI component with scrollable text display
- **Tone Selection**: Change narrative style and regenerate stories on the fly
- **Live Access**: View stories at any time during battle (press 'S')
- **Smooth Scrolling**: Mouse wheel and keyboard navigation

## Quick Start

### Basic Usage

```python
from src.systems.battle_story_summarizer import (
    BattleStoryGenerator, BattleStoryTracker, StoryTone
)

# Initialize story generator
generator = BattleStoryGenerator(default_tone=StoryTone.DRAMATIC)

# Create tracker for automatic generation (every 5 minutes)
tracker = BattleStoryTracker(
    generator=generator,
    story_interval_seconds=300.0  # 5 minutes
)

# Start collecting events
tracker.start_tracking()

# Add battle events as they occur
def on_battle_event(event):
    tracker.generator.add_event(event)

battle.add_event_callback(on_battle_event)

# Check if it's time to generate a story
if tracker.should_generate_story():
    story = tracker.generate_and_store_story()
    print(story)

# Export all stories
tracker.export_all_stories('battle_stories', format='txt')
```

### With UI Integration

```python
from src.rendering import StoryViewer, StoryViewerAction

# Create story viewer
viewer = StoryViewer(width=700, height=600)

# Set story content
viewer.set_story(story_text, StoryTone.HEROIC)

# Handle events
result = viewer.handle_event(event, x_offset=350, y_offset=150)
if result:
    action, data = result
    
    if action == StoryViewerAction.CHANGE_TONE:
        new_story = generator.generate_story(tone=data)
        viewer.set_story(new_story, data)
    
    elif action == StoryViewerAction.EXPORT_TXT:
        generator.export_story(story, "my_story.txt", 'txt')

# Draw the viewer
viewer.draw(surface, x=350, y=150)
```

## Running the Demo

The interactive demo showcases all features:

```bash
python3 -m examples.battle_story_mode_demo
```

**Demo Features:**
- Real-time battle visualization
- Automatic story generation every 30 seconds (demo speed)
- Press 'S' to view story panel at any time
- Change tones and regenerate stories interactively
- Export stories with one click
- Notifications when new stories are available

**Controls:**
- `SPACE`: Pause/Resume battle
- `S`: Toggle story viewer
- `ESC`: Close story viewer / Pause menu
- Mouse Wheel / Arrow Keys: Scroll story text

## Story Tones

### Dramatic (Default)
Creates tension-filled narratives with emotional weight and dramatic tension:
> "⚡ **THE ARENA REMEMBERS** ⚡
> 
> Blood and steel met in a 5-minute battle that would echo through eternity. Through 67 brutal exchanges, 1247 points of damage painted the arena red. Amidst the chaos, one name rose above all others: **Aragorn**. Their story would not be forgotten..."

### Heroic
Epic tales celebrating bravery, valor, and legendary feats:
> "⚔️ **LEGENDS OF THE ARENA** ⚔️
> 
> In an epic clash spanning 5 minutes, warriors of renown gathered to test their mettle in glorious combat. **HERO OF THE HOUR**: Aragorn emerged as the champion, their blade singing through the arena with 247 damage dealt. Their deeds shall be sung for generations!"

### Comedic
Lighthearted accounts finding humor in the chaos:
> "🎭 **CHAOS IN THE ARENA** 🎭
> 
> Well, this was supposed to be an organized battle. Our 'fighters' swung wildly 67 times, somehow managing 1247 damage (most of it accidental). **MVP (Most Violent Participant)**: Aragorn somehow managed to not fall over while swinging. Beginner's luck, surely!"

### Serious
Gritty, realistic battle reports:
> "📋 **COMBAT REPORT** 📋
> 
> Engagement duration: 5m 23s. Combatants: 10. Engagement count: 67. Total damage output: 1247. **TOP PERFORMER**: Aragorn. Damage output: 247. Eliminations: 3."

### Documentary
Analytical, nature documentary style:
> "📊 **ARENA ECOLOGY STUDY** 📊
> 
> Here in their natural habitat, we observe 10 specimens engaging in territorial combat. Aggression displays numbered 67, with cumulative damage reaching 1247 units. The alpha specimen, **Aragorn**, demonstrated superior fitness..."

## Configuration

### Story Generation Timing

```python
# Quick stories (for demos/testing)
tracker = BattleStoryTracker(
    generator=generator,
    story_interval_seconds=30.0  # 30 seconds
)

# Standard interval
tracker = BattleStoryTracker(
    generator=generator,
    story_interval_seconds=300.0  # 5 minutes
)

# Extended battles
tracker = BattleStoryTracker(
    generator=generator,
    story_interval_seconds=600.0  # 10 minutes
)
```

### Tone Selection

```python
# Create generator with preferred default tone
generator = BattleStoryGenerator(default_tone=StoryTone.HEROIC)

# Generate with specific tone
story = generator.generate_story(tone=StoryTone.COMEDIC)

# Available tones
# - StoryTone.DRAMATIC (default)
# - StoryTone.HEROIC
# - StoryTone.COMEDIC  
# - StoryTone.SERIOUS
# - StoryTone.DOCUMENTARY
```

## Architecture

### BattleStoryGenerator
Core story generation engine:
- Collects battle events and logs
- Extracts metrics and statistics
- Generates AI prompts based on tone
- Produces fallback stories when API unavailable
- Handles export functionality

### BattleStoryTracker
Manages automatic story generation:
- Tracks time intervals
- Triggers story generation
- Stores story history
- Batch export functionality

### StoryViewer
Pygame UI component:
- Displays formatted stories
- Handles user interaction
- Tone selection interface
- Export controls
- Scroll management

## Integration with Battle System

The story system integrates seamlessly with the existing battle infrastructure:

```python
# Create battle with living world features
battle = SpatialBattle(
    creatures,
    arena_width=120.0,
    arena_height=90.0,
    living_world_enhancer=living_world
)

# Set up story tracking
tracker.start_tracking()

# Connect event callback
battle.add_event_callback(lambda event: tracker.generator.add_event(event))

# Also collect text logs
for log in battle.get_battle_log():
    tracker.generator.add_log(log)

# In game loop
if tracker.should_generate_story():
    story = tracker.generate_and_store_story()
    viewer.set_story(story, current_tone)
```

## Example Story Output

```
⚔️ **TALES OF VALOR** ⚔️

From across the realm they came, 10 brave souls seeking honor and glory 
in 3 minutes of legendary battle.

The warriors clashed 67 times, their mighty blows dealing 1247 damage total. 
12 strikes found critical weaknesses, each one a testament to skill and fortune.

**HERO OF THE HOUR**: Aragorn emerged as the champion, their blade singing 
through the arena with 247 damage dealt and 3 foes vanquished. A true legend 
in the making!

The price of glory was steep: 7 brave warriors fell in combat, yet hope 
endured as 2 new life emerged from the struggle.

**Turning Point**: Gandalf and Aragorn formed an unexpected alliance

**Most Dramatic Moment**: Saruman's last stand against overwhelming odds

When the dust settled, 5 heroes stood victorious, their names forever etched 
in the annals of arena legend. Their deeds shall be sung for generations!

---
📊 Battle Summary: 3m 14s | 67 attacks | 7 casualties | 2 births
```

## API Reference

### BattleStoryGenerator

```python
BattleStoryGenerator(
    default_tone: StoryTone = StoryTone.DRAMATIC
)
```

**Methods:**
- `start_collection()`: Begin collecting events
- `add_event(event)`: Add a battle event
- `add_log(message)`: Add a log message
- `generate_story(tone)`: Generate story with specified tone
- `export_story(story, filepath, format)`: Export to file

### BattleStoryTracker

```python
BattleStoryTracker(
    generator: BattleStoryGenerator,
    story_interval_seconds: float = 300.0
)
```

**Methods:**
- `start_tracking()`: Begin tracking
- `stop_tracking()`: Stop tracking
- `should_generate_story()`: Check if interval elapsed
- `generate_and_store_story(tone)`: Generate and save story
- `get_all_stories()`: Get story history
- `export_all_stories(directory, format)`: Batch export

### StoryViewer

```python
StoryViewer(
    width: int = 600,
    height: int = 500,
    font_size: int = 18
)
```

**Methods:**
- `set_story(story, tone)`: Update displayed story
- `handle_event(event, x_offset, y_offset)`: Process events
- `draw(surface, x, y)`: Render viewer

## Best Practices

1. **Set Appropriate Intervals**: Use longer intervals (5-10 minutes) for production, shorter for demos
2. **Monitor API Costs**: Use `gpt-4o-mini` for cost-effectiveness
3. **Test Fallback Mode**: Ensure your game works without API access
4. **Export Regularly**: Save stories to disk for player sharing
5. **Vary Tones**: Offer players tone selection for replay value
6. **Integrate with Living World**: Richer creature histories = better stories

## Troubleshooting

### Stories Seem Generic
- Add more detailed battle logs for richer context
- Ensure creature names are being tracked properly
- Add key moments and dramatic events to logs

### Export Fails
- Check write permissions for export directory
- Verify directory exists or can be created
- Check disk space

## Performance Notes

- Story generation is instant (< 1ms typically for local processing)
- No network latency - completely offline
- No API rate limits or costs
- Metrics extraction is lightweight
- UI rendering optimized for 60 FPS

## Testing

Run the comprehensive test suite:

```bash
python3 -m unittest tests.test_battle_story_summarizer -v
```

**Test Coverage:**
- Event collection and metric tracking
- Story generation with all tones
- Export functionality (TXT and MD)
- Tracker timing and interval logic
- Story storage and retrieval
- All 20 tests passing ✓

## Support

For issues, feature requests, or questions:
- Check existing documentation
- Review example code in `examples/battle_story_mode_demo.py`
- Run tests to verify functionality
- Check console output for error messages
