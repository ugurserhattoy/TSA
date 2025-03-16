import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # TSA
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "sponsors.csv")
DB_FILENAME = "sponsorship.db"
DB_PATH = os.path.join(DATA_DIR, DB_FILENAME)