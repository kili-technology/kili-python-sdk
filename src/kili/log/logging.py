import logging
import sys

logger = logging.getLogger("kili")
logger.setLevel(logging.WARNING)
logger.propagate = False
logger.addHandler(logging.StreamHandler(stream=sys.stderr))
