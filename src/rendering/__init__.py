"""
Rendering and UI module for EvoBattle.

Provides Pygame-based visualization for the spatial battle system,
including creature rendering, UI overlays, animations, and input handling.
"""

from .game_window import GameWindow
from .arena_renderer import ArenaRenderer
from .creature_renderer import CreatureRenderer
from .pellet_renderer import PelletRenderer
from .ui_components import UIComponents
from .event_animator import EventAnimator
from .creature_inspector import CreatureInspector
from .pellet_inspector import PelletInspector
from .pause_menu import PauseMenu, PauseMenuAction
from .post_game_summary import PostGameSummary
from .trait_dashboard import TraitAnalyticsDashboard
from .camera import Camera

__all__ = [
    'GameWindow',
    'ArenaRenderer',
    'Camera',
    'CreatureRenderer',
    'PelletRenderer',
    'UIComponents',
    'EventAnimator',
    'CreatureInspector',
    'PelletInspector',
    'PauseMenu',
    'PauseMenuAction',
    'PostGameSummary',
    'TraitAnalyticsDashboard',
]
