"""Common functions for plugins."""

import logging

from kili.services.types import LogLevel


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
