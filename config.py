import os

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

LOG_ROTATION_LIMIT = 5