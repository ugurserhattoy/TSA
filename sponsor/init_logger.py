"""
Logger initialization module for the TSA application.
Handles log rotation and formatting using application settings.
Initializes and returns a configured logger instance for the TSA application.
Uses settings from SettingsManager for log level and rotation.

Returns:
    logging.Logger: Configured logger with rotation and formatting.
"""

import logging
from logging.handlers import RotatingFileHandler
from TSA.config import LOG_FILE

def init_logger(log_level="INFO", rotation_limit=5):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    print(f"LOG_FILE: {LOG_FILE}")
    handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=5 * 1024 * 1024,  # 5 MB filesize limit
        backupCount=rotation_limit
    )

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    print(f"logger handlers: {logger.handlers}")
    # stream_handler = logging.StreamHandler()
    # stream_handler.setFormatter(formatter)
    # logger.addHandler(stream_handler)
    # Add handler only if not already present to avoid duplicate log entries
    if not logger.handlers:
        logger.addHandler(handler)
    
    print(f"logger handlers: {logger.handlers}")

    # logger.info("Logger initialized ✅")
    # logger.warning("This is a WARNING message")
    # logger.error("This is an ERROR message")
    # logger.debug("This is a DEBUG message")

    logger.propagate = False  # Prevent logs from propagating to the root logger
    return logger