import logging


def setup_logger():
    """Sets up a Python logger with some sensible defaults and returns it.

    Returns:
        Logger: A Python logger.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = setup_logger()
