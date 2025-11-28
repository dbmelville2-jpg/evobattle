# Battle Story Removal - Remaining Work

## Lines to Remove from main.py:

### Docstring (lines 278, 286):
- Line 278: Remove "story generation" from event handling description
- Line 286: Remove "S: View AI-generated battle story" control

### Event Handling (lines 417-448, 466-481):
- Lines 417-448: Remove story viewer event handling block
- Lines 466-467: Remove ESC key story close
- Lines 474: Remove story check from pause condition
- Lines 477-481: Remove 'S' key story toggle

### Update Loop (lines 627, 656-665):
- Line 627: Remove show_story from pause condition
- Lines 656-665: Remove story tracker update block

### Rendering (lines 732, 746, 781):
- Line 732: Remove show_story rendering check
- Line 746: Remove story_viewer.draw() call
- Line 781: Remove story notification check

## Total: ~40 lines to remove across 4 sections
