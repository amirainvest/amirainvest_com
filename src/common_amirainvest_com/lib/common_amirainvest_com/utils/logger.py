import logging
import sys
from logging import Logger

from common_amirainvest_com.utils import consts


root_logger: Logger = logging.getLogger()
log: Logger = logging.getLogger(__name__)
log_formatter = logging.Formatter(
    "%(asctime)s - "
    "%(levelname)s - "
    "%(processName)s:%(threadName)s - "
    "%(filename)s:%(funcName)s:%(lineno)d - "
    "%(message)s"
)

# Remove all existing log handlers
for handler in root_logger.handlers:
    root_logger.removeHandler(handler)
for handler in log.handlers:
    log.removeHandler(handler)

# Set logging level based on env var
if consts.DEBUG == "true" or consts.ENVIRONMENT == consts.Environments.local.value:
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.INFO)

# Add a stream handler to stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)

log.addHandler(stream_handler)
