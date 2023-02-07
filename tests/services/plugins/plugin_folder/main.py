from kili.plugins import PluginCore
from kili.types import Label

from .sub_folder.helpers import custom_function


class PluginHandler(PluginCore):
    def on_submit(self, label: Label, asset_id: str) -> None:
        custom_function()
