import logging
import sys

__version__ = "0.15.0"

CHANGE_SET_FORMAT = "{stack}-change-set"

logger = logging.getLogger("formica")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
