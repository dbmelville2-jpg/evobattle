# Development Tools

This folder contains utility scripts for development, debugging, and analysis.

## Performance & Profiling

### `profile_battle.py`
Performance profiling tool for the battle system.

**Usage:**
```bash
python tools/profile_battle.py
```

**Purpose:**
- Profiles 100 frames with 200 creatures
- Identifies performance bottlenecks
- Shows top functions by CPU time

### `verify_performance_and_regression.py`
Performance regression testing.

**Usage:**
```bash
python tools/verify_performance_and_regression.py
```

**Purpose:**
- Ensures performance hasn't degraded
- Compares against baseline metrics

## Code Analysis

### `find_docstrings.py`
Analyzes codebase for documentation coverage.

**Usage:**
```bash
python tools/find_docstrings.py
```

**Purpose:**
- Finds missing docstrings
- Reports documentation coverage

### `verify_changes.py`
Verification script for code changes.

**Usage:**
```bash
python tools/verify_changes.py
```

**Purpose:**
- Validates code changes
- Runs sanity checks

---

**Note:** These are development tools and are not required for running the game. See `main.py` in the root directory to run the game.
