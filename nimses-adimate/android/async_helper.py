import logging
from typing import Callable

logger = logging.getLogger(__name__)


def log_error(function: Callable, *args):
    try:
        return function(*args)
    except Exception as e:
        logger.error(e)
