"""
Logger utils
"""

import logging

from kili.services.types import LogLevel


def get_logger(level: LogLevel) -> logging.Logger:
    """Gets the export logger"""
    logger = logging.getLogger("kili.services.export")
    logger.setLevel(level)
    if logger.hasHandlers():
        logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
