# Battle Story Feature Removal Guide

## ✅ Completed
- Moved `docs/BATTLE_STORY_MODE_DOCUMENTATION.md` → `docs/archive/`

## 📝 Manual Updates Needed

### 1. Remove from README.md

**Delete this entire section (around lines 8-17):**

```markdown
### AI-Powered Battle Stories ✓ NEW!
Transform battles into shareable narratives with AI-generated story summaries:
- **Automatic Story Generation**: AI creates engaging battle reports every 5 minutes (configurable)
- **Multiple Tones**: Choose from dramatic, heroic, comedic, serious, or documentary styles
- **Story Viewer UI**: Dedicated panel with scrollable text, tone selection, and export options
- **Export & Share**: Save stories as TXT or Markdown files
- **Key Moments**: Highlights MVPs, turning points, alliances, betrayals, and dramatic events
- **Works Offline**: Fallback mode generates structured summaries without AI API

See [Battle Story Mode Documentation](docs/BATTLE_STORY_MODE_DOCUMENTATION.md) for details.
```

**Remove from "Running Examples" section:**
```markdown
# Battle Story Mode demo
python3 -m examples.battle_story_mode_demo  # AI-powered battle narratives
```

### 2. Update docs/DOCUMENTATION_INDEX.md

**Remove this line:**
```markdown
- [BATTLE_STORY_MODE_DOCUMENTATION.md](BATTLE_STORY_MODE_DOCUMENTATION.md) - AI-powered battle narratives
```

## 🗂️ Optional: Archive Code Files

If you want to fully remove the feature, move these to a `deprecated/` folder:

**Source Code:**
- `src/systems/battle_story_summarizer.py`
- `src/rendering/story_viewer.py`
- `examples/battle_story_mode_demo.py`

**Tests:**
- `tests/test_battle_story_summarizer.py`
- `tests/test_story_hotkey_integration.py`
- `tests/verify_story_hotkey.py`
- `tests/generate_story_screenshot.py`

**Keep (used by other features):**
- `src/models/history.py` - Living World system
- `src/models/pellet_history.py` - Pellet tracking
- `tests/test_pellet_history.py` - Pellet tests
