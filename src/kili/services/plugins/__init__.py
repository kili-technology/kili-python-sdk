"""Service for managing plugins in kili"""

from kili.services.plugins.activation import activate_plugin, deactivate_plugin
from kili.services.plugins.upload import PluginUploader

__all__ = ["PluginUploader", "activate_plugin", "deactivate_plugin"]
