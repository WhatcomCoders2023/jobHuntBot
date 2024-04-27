import logging
import os


def init_logger():
    # Prod mode
    if not os.getenv("DEV_MODE"):
        import google.cloud.logging

        client = google.cloud.logging.Client()
        client.setup_logging()

        return logging.getLogger()

    # Dev mode
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger("JobHuntLogger")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(handler)

    return logger
