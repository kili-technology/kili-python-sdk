from kili.plugins import PluginCore

from .sub_folder.helpers import custom_function


class PluginHandler(PluginCore):
    def on_event(self, label: dict, asset_id: str) -> None:
        custom_function()
