import sys
import pathlib
import pygame, os

# Ensure repo root (one level up from scripts/) is on sys.path so "src." imports work
repo_root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

# Initialize pygame and set a minimal display mode so convert_alpha can work
pygame.init()
# Use a hidden display if available; set_mode may create a surface needed for convert_alpha
try:
    pygame.display.set_mode((1, 1))
except Exception:
    pass

try:
    from src.rendering.creature_inspector import CreatureInspector
    ins = CreatureInspector()
    print("Loaded icons:", sorted(ins.icon_surfaces.keys()))
except Exception as e:
    print("ERROR loading CreatureInspector:", type(e).__name__, e)
finally:
    pygame.quit()