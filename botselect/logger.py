import logging

from botselect import config

logging.basicConfig(level=config.LOG_LEVEL)
# This is the app logger, not related to EQ logs

getLogger = logging.getLogger
