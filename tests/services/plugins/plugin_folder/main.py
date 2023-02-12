from typing import Dict

from kili.plugins import PluginCore

from .sub_folder.helpers import custom_function


class PluginHandler(PluginCore):
    def on_submit(self, label: Dict, asset_id: str) -> None:
        custom_function()
