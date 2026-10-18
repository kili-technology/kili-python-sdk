"""Common functions for plugins."""

import logging

from kili.services.types import LogLevel

PLUGIN_CORE_DEPRECATION = (
    "`kili.plugins.PluginCore` is deprecated and will be removed in a future major release."
    " Subclass `kili.plugins.Plugin` instead: `self.kili` is then the domain client"
    " (`self.kili.assets.list(...)`), and `self.kili.legacy_client` keeps the legacy client's"
    " methods while the plugin migrates."
)


def get_logger(level: LogLevel = "DEBUG"):
    """Get the plugins logger."""
    logger = logging.getLogger("kili.services.plugins")
    logger.setLevel(level)
    if logger.hasHandlers():
        logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
