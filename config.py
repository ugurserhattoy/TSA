"""Constant Configs"""

import os


# DIRs and PATHS
HOME_DIR = os.path.expanduser("~")
APP_DIR = os.path.join(HOME_DIR, "TSA")
LOG_DIR = os.path.join(APP_DIR, "logs")
DATA_DIR = os.path.join(APP_DIR, "data")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, "sponsors.csv")
DB_FILENAME = "sponsorship.db"
DB_PATH = os.path.join(DATA_DIR, DB_FILENAME)
LOG_FILE = os.path.join(LOG_DIR, "app.log")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")

# Default Settings are used in settings_model.py
DEFAULT_SETTINGS = {
    "log_rotation_limit": 5,
    "log_level": "INFO",
    "check_for_release": True,
}

LOG_ROTATION_LIMIT = 5

# Github release api endpoint and version is used for auto check for new releases
GITHUB_REL = "https://api.github.com/repos/ugurserhattoy/TSA/releases/latest"
VERSION = "v0.6.0"
