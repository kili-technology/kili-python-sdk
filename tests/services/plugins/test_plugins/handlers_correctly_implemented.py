from typing import Dict

from kili.plugins import PluginCore


class PluginHandler(PluginCore):
    def on_submit(self, label: Dict, asset_id: str) -> None:
        super().on_submit(label=label, asset_id=asset_id)

    def on_review(self, label: Dict, asset_id: str) -> None:
        super().on_review(label=label, asset_id=asset_id)
