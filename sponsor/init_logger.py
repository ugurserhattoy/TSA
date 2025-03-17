import logging
from logging.handlers import RotatingFileHandler
from TSA.config import LOG_FILE, LOG_ROTATION_LIMIT

def init_logger():
    logger = logging.getLogger("tsa_logger")
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=5 * 1024 * 1024,  # 5 MB filesize limit
        backupCount=LOG_ROTATION_LIMIT  # max file
    )

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger