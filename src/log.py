# Logging File
import logging
import os


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not os.path.exists("./logging"):
        os.makedirs("./logging")

    handler = logging.FileHandler('./logging/{}.log'.format(name))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger
