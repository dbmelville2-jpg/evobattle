# EvoBattle Development Agent Specification

## Overview
This document defines the specialized knowledge, capabilities, and standards for AI agents working on the EvoBattle project - an evolutionary battle game combining genetic simulation with Dwarf Fortress-style depth and emergent storytelling.

## Core Game Domain Expertise

### 1. EvoBattle Game Mechanics
**Evolutionary Genetics System**
- Strain-based families with color-coded genetic similarity
- Trait inheritance with mutations (add/remove/modify)
- Natural selection and strain extinction
- Lineage tracking and population analytics

**Turn-Based Combat System**
- Speed-based turn order with random tiebreaking
- Type effectiveness and damage calculations
- Status effects: poison, burn, sleep, paralysis, freeze, confusion
- Buff/debuff system for strategic gameplay
- Multiple ability types: physical, special, healing, buff, debuff

**Ecosystem Survival Mechanics**
- Hunger system with metabolic traits
- Resource gathering and foraging behavior
- Trait-driven wandering and exploration
- Starvation mechanics and survival pressure
- 15+ predefined ecosystem traits (Forager, Efficient Metabolism, Curious, etc.)

**Breeding & Genetics**
- Sexual reproduction with trait inheritance
- Mutation rates and genetic diversity
- Parent selection and offspring generation
- Crossover and recombination mechanics

### 2. Dwarf Fortress-Style Deep Simulation

Agents must be experts in implementing systems that create emergent narratives and deep simulation:

**Individual Histories**
- Detailed action logging for every creature
- Life event tracking (births, evolutions, achievements, rivalries)
- Personality traits affecting behavior and decision-making
- Relationship systems (allies, enemies, family bonds)
- Memorable moments and legendary actions

**Granular Statistics**
- Combat stats: hit rate, dodge rate, critical hits, kills, damage dealt/received
- Survival stats: food consumed, distance traveled, resources gathered
- Breeding stats: offspring count, genetic contribution, strain influence
- Battle participation: battles fought, wins/losses, survival rate
- Lifespan tracking and cause of death analysis

**Skill Systems**
- Skills that develop through use (combat proficiency, evasion, foraging)
- Skill decay from disuse
- Skill inheritance and training
- Expertise levels affecting performance

**Personality Systems**
- Behavioral traits affecting AI decisions:
  - **Aggression**: Attack frequency, target selection, risk-taking
  - **Caution**: Retreat threshold, defensive positioning
  - **Loyalty**: Team cohesion, protecting allies
  - **Ambition**: Challenge-seeking, competitive behavior
  - **Curiosity**: Exploration patterns, experimentation
- Emergent behaviors from personality combinations
- Personality inheritance in breeding

**Historical Records**
- Battle records with full participant details
- Strain histories (rise and fall of genetic lines)
- Record holders (strongest, fastest, longest-lived, most kills)
- Legendary creatures and their achievements
- Era tracking showing which strains dominated when
- Hall of fame and notable events

**Inspection & Query Systems**
- Deep creature inspection UI showing complete history
- Family tree visualization
- Timeline views of creature actions
- Query capabilities (find creatures by criteria)
- Comparison tools for analyzing fighters

## Technical Architecture Knowledge

### Project Structure
```
evobattle/
├── src/
│   ├── models/          # Data models (Creature, Fighter, Trait, Lineage, Ability, Stats)
│   ��── systems/         # Game systems (Battle, Breeding, Betting, Ecosystem)
│   ├── rendering/       # Pygame visualization components
│   └── utils/           # Utilities and helpers
├── examples/            # Demo scripts showcasing features
├── tests/               # Unit and integration tests
└── docs/                # Documentation (BATTLE_SYSTEM_DOCUMENTATION.md, etc.)
```

### Key Systems

**Models** (`src/models/`)
- `creature.py` - Base creature with stats, abilities, traits
- `fighter.py` - Fighter-specific implementations
- `trait.py` - Genetic trait system
- `lineage.py` - Family tree and ancestry tracking
- `ability.py` - Combat abilities and effects
- `stats.py` - Stat modifiers and calculations

**Systems** (`src/systems/`)
- `battle.py` - Turn-based combat engine with event logging
- `breeding.py` - Genetic inheritance and offspring generation
- `betting.py` - Wagering and player engagement
- `ecosystem.py` - Survival mechanics and resource management

**Rendering** (`src/rendering/`)
- Event-driven Pygame visualization
- Real-time battle arena display
- UI panels and overlays
- Animation system

### Architecture Patterns
- **Event-driven design**: Systems publish events, components subscribe
- **Modular boundaries**: Clear separation between gameplay, rendering, and data
- **Interface contracts**: Defined in AGENT_COORDINATION.md
- **Three-agent model**: Core Gameplay Engineer, Graphics & Rendering, Data & Systems

## Agent Capabilities

### What Agents Should Be Able To Do

**1. Implement Deep Simulation Features**
- Life event tracking and history systems
- Skill progression mechanics
- Personality trait systems affecting AI behavior
- Relationship graphs and social dynamics
- Legendary moment detection
- Historical record keeping
- Query and inspection interfaces

**2. Extend Combat Systems**
- New ability types and status effects
- Advanced AI with personality-based decisions
- Team dynamics and synergies
- Environmental effects (terrain, weather)
- Fatigue and injury persistence
- Combat skill progression

**3. Enhance Genetic Systems**
- Advanced trait mechanics (dominant/recessive, synergies)
- Strain dynamics and speciation
- Selective breeding mechanisms
- Genetic diversity metrics
- Mutation types and rates

**4. Create Visualization Features**
- Creature inspector UI (full history, stats, family tree)
- Battle replay system
- Statistics dashboards
- Family tree visualization
- Timeline views
- Hall of fame screens

**5. Build Ecosystem Features**
- Predator/prey dynamics
- Territory and resource systems
- Seasonal effects
- Population pressure mechanics
- Migration and dispersal

**6. Develop Analytics & Tools**
- Data persistence and save/load
- Query systems for historical data
- Performance profiling
- Balance analysis tools
- Debugging visualizations

### Implementation Philosophy

When generating code, agents should prioritize:

✅ **Emergent Complexity** - Simple rules creating complex, interesting outcomes
✅ **Deep Simulation** - Every action logged and tracked for rich histories
✅ **Player Attachment** - Systems that make creatures feel unique and memorable
✅ **Strategic Depth** - Meaningful choices in breeding, betting, and tactics
✅ **Performance** - Efficient algorithms for large-scale simulations
✅ **Modularity** - Clean interfaces between systems
✅ **Testability** - Unit tests for all functionality
✅ **Documentation** - Clear explanations of mechanics and code

### Code Standards

**Required in all implementations:**
- Type hints for all function parameters and returns
- Comprehensive docstrings (Google style)
- Unit tests for new functionality
- Integration with existing event systems
- Updates to relevant documentation files
- Example scripts demonstrating features
- Performance considerations for scale

**Respect interface contracts:**
- Follow AGENT_COORDINATION.md guidelines
- Maintain boundaries between Core Gameplay, Graphics, and Data & Systems
- Use dependency injection for testability
- Document all public APIs

## Example Use Cases

Agents should handle requests like:

**Deep Simulation Requests:**
- "Add a personality trait system where aggressive fighters attack more often but defensive fighters survive longer"
- "Implement a skill system where fighters improve at dodging based on battle experience"
- "Create a relationship system where fighters remember who killed their family members and seek revenge"
- "Add injury persistence so fighters carry wounds between battles that affect performance"
- "Implement a legendary creatures system tracking exceptional achievements"

**Visualization Requests:**
- "Create a creature inspection UI showing complete battle history when clicked"
- "Add a family tree visualization displaying genetic lineage with color-coded strains"
- "Implement a battle replay system with timeline scrubbing"
- "Build a hall of fame screen showing greatest fighters of all time"
- "Create a statistics dashboard with population analytics and strain dominance graphs"

**Gameplay Requests:**
- "Add terrain effects to battles (high ground, obstacles, hazards)"
- "Implement team synergy bonuses when related creatures fight together"
- "Create a fatigue system where fighters need rest between battles"
- "Add seasonal effects that change resource availability"
- "Implement predator/prey dynamics in the ecosystem"

**Genetic System Requests:**
- "Add dominant/recessive gene mechanics for trait inheritance"
- "Implement trait synergies where combinations produce emergent effects"
- "Create speciation mechanics where strains diverge into distinct types"
- "Add player-driven selective breeding through betting choices"
- "Implement genetic bottleneck events that affect population diversity"

## Integration Checklist

For every feature implementation, agents should:

- [ ] Understand which existing systems are affected
- [ ] Review relevant documentation (BATTLE_SYSTEM_DOCUMENTATION.md, LINEAGE_SYSTEM_DOCUMENTATION.md, etc.)
- [ ] Identify interface contracts that must be maintained
- [ ] Determine which of the three agent domains this falls under
- [ ] Implement with proper type hints and docstrings
- [ ] Write unit tests covering new functionality
- [ ] Create integration tests if multiple systems interact
- [ ] Add example script in `examples/` directory
- [ ] Update relevant documentation files
- [ ] Consider performance implications at scale
- [ ] Test with existing examples to ensure no regressions

## Success Criteria

An agent is effective when it:

✅ Understands EvoBattle's unique evolutionary combat mechanics
✅ Implements Dwarf Fortress-style depth and emergent storytelling naturally
✅ Generates working, tested code that integrates seamlessly
✅ Creates features that increase player attachment to creatures
✅ Maintains performance with deep simulation and large populations
✅ Documents implementations clearly
✅ Suggests creative improvements fitting the game's theme
✅ Respects existing architecture and interface contracts
✅ Produces code that other agents/developers can easily extend

## Reference Documentation

Agents should be familiar with:
- `AGENT_COORDINATION.md` - Team coordination and interface contracts
- `BATTLE_SYSTEM_DOCUMENTATION.md` - Combat engine details
- `LINEAGE_SYSTEM_DOCUMENTATION.md` - Genetic system mechanics
- `ECOSYSTEM_DOCUMENTATION.md` - Survival and resource systems
- `RENDERING_DOCUMENTATION.md` - Visualization architecture
- `MODELS_DOCUMENTATION.md` - Core data models
- `CONTRIBUTING.md` - Development guidelines

## Conclusion

This specification defines an AI agent capable of understanding and extending a complex evolutionary battle game with deep simulation mechanics. Agents following this specification should be able to implement features that create emergent narratives, track detailed histories, and make every creature feel unique and memorable - combining the strategic depth of genetic evolution with the rich storytelling of games like Dwarf Fortress.
