"""Service for managing plugins in kili."""

from kili.services.plugins.activation import activate_plugin, deactivate_plugin
from kili.services.plugins.deletion import delete_plugin
from kili.services.plugins.upload import PluginUploader, WebhookUploader

__all__ = [
    "PluginUploader",
    "WebhookUploader",
    "activate_plugin",
    "deactivate_plugin",
    "delete_plugin",
]
