import sys
import os

sys.path.append(os.path.dirname(__file__))


def initialize_logging():
    import logging
    """initialize logging library for pytest."""
    logging.basicConfig(level=logging.DEBUG)

    logger = logging.getLogger(__name__)
    logger.info("Importing %s", __name__)


initialize_logging()
