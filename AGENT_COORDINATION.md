# Agent Coordination Guide for EvoBattle Project

## Overview
This document provides the core instructions and standards for building and coordinating the three main specialist agents working on the EvoBattle project. Each agent should reference this document for team standards, interface contracts, and integration goals.

**Related Issues:**
- Project Architect Vision: [#2](https://github.com/dbmelville2-jpg/evobattle/issues/2)
- Core Gameplay Engineer: [#11](https://github.com/dbmelville2-jpg/evobattle/issues/11)
- Graphics & Rendering Agent: [#12](https://github.com/dbmelville2-jpg/evobattle/issues/12)
- Data & Systems Agent: [#13](https://github.com/dbmelville2-jpg/evobattle/issues/13)

## Team Standards

### 1. Semi-Independent Work with Strong Contracts
- Each agent works within their domain of expertise
- All cross-agent dependencies must be defined through clear interface contracts
- Document all public APIs in code comments and this coordination guide
- Use type hints and docstrings for all public functions and classes

### 2. Code Review Process
- All significant changes require review before merging
- Use pull requests for all feature work
- Tag relevant agents when their interfaces are affected
- Review checklist:
  - [ ] Code follows project style guidelines
  - [ ] Interface contracts are maintained or updated with consent
  - [ ] Documentation is updated
  - [ ] Tests are included for new functionality
  - [ ] No breaking changes to other agents' work without coordination

### 3. Integration Checkpoints
Regular integration checkpoints should occur at these milestones:
- **Checkpoint 1**: Basic interfaces defined (week 1)
- **Checkpoint 2**: Core functionality implemented (week 2)
- **Checkpoint 3**: Integration testing complete (week 3)
- **Checkpoint 4**: Polish and optimization (week 4)

### 4. Communication Protocol
- **Project Architect**: Maintains overall vision and resolves conflicts between agents
- **Daily standup**: Brief status updates in issue comments
- **Blocking issues**: Tag @dbmelville2-jpg and relevant agents immediately
- **Design decisions**: Document in respective sub-issues (#11, #12, #13)
- **Integration questions**: Post in issue #10 (this coordination issue)

## Interface Contracts

### Core Gameplay Engineer ↔ Graphics & Rendering
**Gameplay provides to Graphics:**
```python
# Entity state for rendering
class EntityState:
    position: tuple[float, float]  # (x, y) coordinates
    velocity: tuple[float, float]  # (vx, vy) for animation
    rotation: float  # degrees
    animation_state: str  # e.g., "idle", "attack", "hurt"
    entity_type: str  # e.g., "fighter", "projectile"
```

**Graphics provides to Gameplay:**
```python
# Rendering feedback (for gameplay adjustments)
class RenderingFeedback:
    screen_bounds: tuple[float, float]  # (width, height)
    camera_position: tuple[float, float]  # (x, y)
    viewport_scale: float
```

### Core Gameplay Engineer ↔ Data & Systems
**Gameplay provides to Data:**
```python
# Game events for logging and analytics
class GameEvent:
    event_type: str  # e.g., "battle_start", "fighter_death"
    timestamp: float
    entities_involved: list[str]
    event_data: dict  # flexible data structure
```

**Data provides to Gameplay:**
```python
# Loaded game state
class GameState:
    fighters: list[Fighter]
    battle_history: list[BattleRecord]
    player_stats: dict
    
# Save/load interface
def save_game(state: GameState, filename: str) -> bool
def load_game(filename: str) -> GameState
```

### Graphics & Rendering ↔ Data & Systems
**Graphics provides to Data:**
```python
# Asset loading requests
class AssetRequest:
    asset_type: str  # "sprite", "sound", "texture"
    asset_id: str
    priority: int  # loading priority
```

**Data provides to Graphics:**
```python
# Asset management
class Asset:
    asset_id: str
    asset_data: bytes
    metadata: dict
    
def load_asset(request: AssetRequest) -> Asset
def unload_asset(asset_id: str) -> bool
```

## Integration Goals

### Phase 1: Foundation (Current)
- [ ] Define all interface contracts (all agents)
- [ ] Set up basic project structure (all agents)
- [ ] Establish build/test infrastructure (all agents)

### Phase 2: Core Implementation
- [ ] Implement main game loop (Gameplay)
- [ ] Build input handling system (Gameplay)
- [ ] Create rendering pipeline (Graphics)
- [ ] Implement game state management (Data)

### Phase 3: Feature Integration
- [ ] Connect gameplay to rendering (Gameplay + Graphics)
- [ ] Connect gameplay to data systems (Gameplay + Data)
- [ ] Implement asset pipeline (Graphics + Data)
- [ ] Add audio support (Data)

### Phase 4: Polish & Optimization
- [ ] Performance optimization (all agents)
- [ ] Visual effects and polish (Graphics)
- [ ] Analytics and debugging tools (Data)
- [ ] Integration testing (all agents)

## Design Decision Template

When making major design or implementation decisions, document them in your respective sub-issue using this template:

```markdown
## Design Decision: [Title]

**Date:** YYYY-MM-DD
**Agent:** [Core Gameplay/Graphics/Data & Systems]
**Status:** [Proposed/Accepted/Rejected/Superseded]

### Context
[What problem are you solving? What constraints exist?]

### Decision
[What did you decide to do?]

### Alternatives Considered
[What other options did you consider? Why were they rejected?]

### Consequences
[What are the implications of this decision?]
- **Positive:**
- **Negative:**
- **Impact on other agents:**

### References
[Links to related issues, docs, or discussions]
```

## Project Architect Communication

The Project Architect (see [#2](https://github.com/dbmelville2-jpg/evobattle/issues/2)) maintains the overall vision and integration needs. Consult with the Architect for:

1. **Vision alignment**: When your work might affect the overall game design
2. **Conflict resolution**: When interface contracts are disputed between agents
3. **Priority decisions**: When multiple tasks compete for attention
4. **Technical direction**: When major architectural decisions are needed
5. **Resource allocation**: When additional tools or dependencies are needed

## Best Practices

### Code Organization
- Keep agent-specific code in separate modules
- Use dependency injection for testability
- Minimize coupling between agent domains
- Document all public interfaces

### Testing Strategy
- **Unit tests**: Each agent tests their own code
- **Integration tests**: Shared tests for interface contracts
- **System tests**: End-to-end tests coordinated by Project Architect

### Documentation
- Keep this coordination guide updated
- Document decisions in sub-issues
- Maintain API documentation in code
- Update README with setup instructions

### Version Control
- Use feature branches for all work
- Merge to main only after review
- Keep commits focused and atomic
- Write clear commit messages

## Getting Started

1. Read your agent-specific issue (#11, #12, or #13)
2. Review the interface contracts that apply to your work
3. Set up your development environment
4. Create a feature branch for your first task
5. Document your first design decision
6. Coordinate with other agents as needed

## Questions?

Post questions in:
- **General coordination**: Issue #10
- **Agent-specific**: Your sub-issue (#11, #12, or #13)
- **Architecture/vision**: Issue #2
