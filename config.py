import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # TSA
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, "sponsors.csv")
DB_FILENAME = "sponsorship.db"
DB_PATH = os.path.join(DATA_DIR, DB_FILENAME)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

LOG_ROTATION_LIMIT = 5