import sqlite3, os
from TSA.sponsor.csv_manager import CSVManager
from TSA.sponsor.transform_db import TransformDB

class DataManager:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DATA_DIR = os.path.join(BASE_DIR, "data")
        self.db_path = os.path.join(DATA_DIR, "sponsorship.db")
        self.conn = None

    def prepare_database(self):
        csv_manager = CSVManager()
        csv_manager.download_csv()

        transform_db = TransformDB()
        df = transform_db.clean_and_transform_csv()
        transform_db.save_as_sqlite(df, self.db_path)

        self.conn = sqlite3.connect(self.db_path)
        return self.conn
