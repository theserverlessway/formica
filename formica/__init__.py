import logging
import sys

__version__ = '0.7.2'

CHANGE_SET_FORMAT = "{stack}-change-set"

logger = logging.getLogger('formica')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
