"""
Battle Managers Package

Contains focused manager classes extracted from battle_spatial.py
for better separation of concerns and maintainability.
"""

from .event_manager import EventManager

__all__ = ['EventManager']
