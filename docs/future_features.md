# Future Features and Enhancements

This document tracks potential future enhancements for EvoBattle that are not currently implemented but would be valuable additions.

## Pellet Evolution Demo Enhancements

### Step Mode
**Description**: Allow frame-by-frame advancement of the simulation for detailed observation.

**Implementation Plan**:
- Add `step_mode` boolean flag
- When 'S' key is pressed, advance exactly one frame and pause
- Display "STEP MODE" indicator in UI

**Benefits**: Allows researchers to observe exact moment-by-moment changes in the ecosystem.

### Fast-Forward Mode
**Description**: Accelerate simulation speed for long-term evolution observation.

**Implementation Plan**:
- Add `fast_forward` boolean flag and `fast_forward_multiplier` (default 5x)
- When 'F' key is pressed, multiply delta time by multiplier
- Display "FAST FORWARD (5x)" indicator in UI
- Consider adding multiple speed levels (2x, 5x, 10x)

**Benefits**: Allows observation of long-term evolutionary trends without waiting in real-time.

## Other Potential Features

### Replay System
- Record simulation state at intervals
- Allow playback of interesting evolutionary moments
- Export/import replay files

### Advanced Statistics Dashboard
- Real-time graphs of population dynamics
- Trait distribution histograms
- Lineage tree visualization

### Scenario Editor
- Custom starting conditions
- Predefined challenges (drought, abundance, etc.)
- Save/load scenarios

## Contributing

If you'd like to implement any of these features, please:
1. Create a new branch
2. Implement the feature with tests
3. Update relevant documentation
4. Submit a pull request

See CONTRIBUTING.md for detailed guidelines.
