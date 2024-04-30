import logging
import os
import google.cloud.logging


def init_logger():
    # Dev mode
    if os.getenv("DEV_MODE"):
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        logger = logging.getLogger("JobHuntLogger")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        logger.addHandler(handler)
        return logger

    # Prod mode
    client = google.cloud.logging.Client()
    client.setup_logging()

    return logging.getLogger()
