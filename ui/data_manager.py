import sqlite3
import logging
from sponsor.csv_manager import CSVManager
from sponsor.transform_db import TransformDB
from config import DB_PATH


logger = logging.getLogger()


class DataManager:
    def __init__(self):
        # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # DATA_DIR = os.path.join(BASE_DIR, "data")
        # self.db_path = os.path.join(DATA_DIR, "sponsorship.db")
        self.conn = None

    def prepare_database(self):
        csv_manager = CSVManager()
        csv_manager.download_csv()

        transform_db = TransformDB()
        df = transform_db.clean_and_transform_csv()
        transform_db.save_as_sqlite(df, DB_PATH)

        self.conn = sqlite3.connect(DB_PATH)
        return self.conn

    def toggle_applied(self, organisation_name, town_city, new_status):
        if not self.conn:
            logger.warning("[TOGGLE] conn is None")
            return None

        logger.debug(
            "[TOGGLE] updating: '%s' | '%s' → %s",
            organisation_name, town_city, new_status
        )

        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE sponsors
            SET applied = ?
            WHERE LOWER(TRIM(organisation_name)) = LOWER(TRIM(?))
            AND LOWER(TRIM(town_city)) = LOWER(TRIM(?))
            """,
            (new_status, organisation_name, town_city),
        )
        self.conn.commit()
        # logger.info(f"[TOGGLE] Updated rows: {cursor.rowcount}")
        return new_status
