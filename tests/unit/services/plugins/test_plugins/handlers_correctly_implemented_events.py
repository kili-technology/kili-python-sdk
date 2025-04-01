from typing import Dict

from kili.plugins import PluginCore


class PluginHandler(PluginCore):
    def on_event(self, payload: Dict) -> None:
        super().on_event(payload=payload)
