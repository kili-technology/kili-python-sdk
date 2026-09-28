"""Develop Plugins for Kili."""

from kili.services.plugins.events import on_kili_event
from kili.services.plugins.model import PluginCore

__all__ = ["PluginCore", "on_kili_event"]
