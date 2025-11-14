# Contributing to EvoBattle

Thank you for contributing to the EvoBattle project! This guide will help you understand how to work effectively within our multi-agent development team.

## Overview

EvoBattle is developed by three specialist agents working in coordination under the guidance of a Project Architect. Each agent has a specific domain of responsibility while collaborating on shared interfaces.

## Getting Started

### 1. Understand Your Role
- **Core Gameplay Engineer**: See [Issue #11](https://github.com/dbmelville2-jpg/evobattle/issues/11)
- **Graphics & Rendering Agent**: See [Issue #12](https://github.com/dbmelville2-jpg/evobattle/issues/12)
- **Data & Systems Agent**: See [Issue #13](https://github.com/dbmelville2-jpg/evobattle/issues/13)

### 2. Read the Documentation
Before starting work, familiarize yourself with:
- [AGENT_COORDINATION.md](AGENT_COORDINATION.md) - Team standards and interface contracts
- [INTEGRATION_CHECKLIST.md](INTEGRATION_CHECKLIST.md) - Current progress and integration milestones
- [Project Architect Vision](https://github.com/dbmelville2-jpg/evobattle/issues/2) - Overall project direction

### 3. Set Up Your Environment
```bash
git clone https://github.com/dbmelville2-jpg/evobattle
cd evobattle
pip install -r requirements.txt
```

## Development Workflow

### Branch Strategy
1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-agent-name/feature-description
   ```
2. Keep your branch focused on a single feature or fix
3. Regularly sync with main to avoid conflicts

### Making Changes

#### For Interface Changes
If your work requires changing an interface contract:
1. **Propose the change** in your agent's issue (#11, #12, or #13)
2. **Tag affected agents** and the Project Architect
3. **Wait for approval** before implementing
4. **Update AGENT_COORDINATION.md** with the new contract
5. **Coordinate implementation** with affected agents

#### For Internal Changes
If your work is internal to your domain:
1. Follow your agent's checklist in INTEGRATION_CHECKLIST.md
2. Write clean, documented code
3. Add tests for new functionality
4. Update relevant documentation

### Code Standards

#### Python Style
- Follow PEP 8 style guidelines
- Use type hints for all public functions
- Write docstrings for all public classes and functions
- Keep functions focused and small

#### Documentation
```python
def process_entity(entity: EntityState) -> RenderData:
    """
    Process an entity state for rendering.
    
    Args:
        entity: The entity state from the gameplay system
        
    Returns:
        RenderData ready for the graphics pipeline
        
    Raises:
        ValueError: If entity position is out of bounds
    """
    pass
```

#### Testing
- Write unit tests for your code
- Participate in integration testing with other agents
- Ensure tests pass before submitting PR

### Commit Messages
Write clear, descriptive commit messages:
```
Add entity collision detection system

- Implement AABB collision detection
- Add collision response handling
- Integrate with physics system
- Add unit tests for edge cases

Refs: #11
```

### Pull Request Process

1. **Before Creating PR**
   - [ ] All tests pass
   - [ ] Code follows style guidelines
   - [ ] Documentation is updated
   - [ ] Interface contracts are maintained (or changes approved)
   - [ ] Integration checklist is updated

2. **PR Description Template**
   ```markdown
   ## Description
   [Brief description of changes]
   
   ## Agent
   [Core Gameplay / Graphics / Data & Systems]
   
   ## Type of Change
   - [ ] New feature
   - [ ] Bug fix
   - [ ] Interface change
   - [ ] Documentation update
   
   ## Related Issues
   Closes #[issue number]
   
   ## Interface Impact
   [Does this affect other agents? List any interface changes]
   
   ## Testing
   [How was this tested?]
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] Interface contracts maintained
   - [ ] Integration checklist updated
   ```

3. **Review Process**
   - Tag relevant agents if your PR affects their work
   - Respond to review comments promptly
   - Make requested changes
   - Merge only after approval

## Communication Guidelines

### Daily Updates
Post brief status updates in your agent's issue:
```markdown
**Status Update - 2025-11-14**

Completed:
- Implemented basic input handling
- Added keyboard event processing

In Progress:
- Working on touch input support

Blocked:
- Need EntityState interface definition from Graphics agent

Next:
- Complete input system
- Begin physics implementation
```

### Asking Questions
- **General questions**: Post in [Issue #10](https://github.com/dbmelville2-jpg/evobattle/issues/10)
- **Agent-specific**: Post in your agent's issue
- **Architecture decisions**: Escalate to Project Architect in [Issue #2](https://github.com/dbmelville2-jpg/evobattle/issues/2)

### Reporting Blockers
If you're blocked:
1. Update the "Blocked Items" table in INTEGRATION_CHECKLIST.md
2. Comment in your agent's issue
3. Tag the blocking agent and Project Architect
4. Provide clear information about what you need

### Design Decisions
Document major design decisions using the template in AGENT_COORDINATION.md:
```markdown
## Design Decision: Collision Detection Algorithm

**Date:** 2025-11-14
**Agent:** Core Gameplay
**Status:** Proposed

### Context
Need efficient collision detection for up to 100 fighters simultaneously.

### Decision
Use spatial hashing with grid size = max(fighter_width, fighter_height).

### Alternatives Considered
- Quad-tree: More complex, overkill for our scale
- Brute force: Too slow for 100 entities

### Consequences
- Positive: O(n) average case performance
- Negative: Requires tuning grid size
- Impact on other agents: Graphics may need grid visualization for debugging

### References
- Issue #11, Comment #5
```

## Integration Points

### Working with Other Agents

#### If You're Core Gameplay:
- Provide EntityState updates to Graphics
- Generate GameEvents for Data logging
- Request RenderingFeedback from Graphics
- Use save/load APIs from Data

#### If You're Graphics:
- Consume EntityState from Gameplay
- Request Assets from Data
- Provide RenderingFeedback to Gameplay
- Implement visual effects for GameEvents

#### If You're Data & Systems:
- Provide Assets to Graphics
- Log GameEvents from Gameplay
- Manage save/load for GameState
- Provide configuration data to all agents

### Integration Testing
Before each integration milestone:
1. Review your interface implementations
2. Coordinate testing with affected agents
3. Run integration test scenarios from INTEGRATION_CHECKLIST.md
4. Document any issues or needed adjustments

## Best Practices

### Do's ✅
- Communicate early and often
- Document your design decisions
- Keep interfaces stable
- Write tests for your code
- Update documentation
- Respect other agents' domains
- Ask for help when needed

### Don'ts ❌
- Don't change interfaces without approval
- Don't break other agents' tests
- Don't skip code reviews
- Don't work in isolation
- Don't make unilateral architecture decisions
- Don't commit untested code

## Getting Help

If you need assistance:
1. Check the documentation first
2. Review your agent's issue and checklist
3. Post in the appropriate issue
4. Tag relevant people
5. Be specific about what you need

## Recognition

We celebrate successes together! When you complete a major milestone:
- Update INTEGRATION_CHECKLIST.md
- Share in your agent's issue
- Thank collaborating agents
- Demo your work if applicable

## Questions?

For questions about this contributing guide or the development process, please comment in [Issue #10](https://github.com/dbmelville2-jpg/evobattle/issues/10).
