"""
This module handles transformation of sponsor CSV data into a cleaned format
and saves it into a SQLite database while preserving certain fields such as 'applied'.
"""

import os
import sqlite3
import logging
import pandas as pd
from config import CSV_PATH, DB_PATH

# from TSA.sponsor.init_logger import init_logger
# from sponsor.settings_manager import SettingsManager


class TransformDB:
    """
    Responsible for reading sponsor data from a CSV file, cleaning it,
    transforming it into a DataFrame, and saving it into an SQLite database.
    Preserves the 'applied' status of organizations if previously stored.
    """

    def __init__(self, csv_path=CSV_PATH, db_path=DB_PATH):
        """Initial definitions"""
        self.csv_path = csv_path
        self.db_path = db_path
        # log_level = SettingsManager().get_log_level()
        self.logger = logging.getLogger()
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def clean_and_transform_csv(self):
        """Cleans the csv and transforms to dataframe"""
        self.logger.info("📌 %s is transforming...", self.csv_path)

        try:
            df = pd.read_csv(self.csv_path, encoding="utf-8")
        except FileNotFoundError:
            self.logger.error("CSV file not found at %s", self.csv_path)
            raise

        df.columns = (
            df.columns.str.strip()
            .str.replace(" ", "_")
            .str.replace("/", "_")
            .str.replace("&", "and")
            .str.lower()
        )
        df = df.fillna("")

        self.logger.info("✅ %s is transformed.", self.csv_path)
        return df

    def save_as_sqlite(self, df, db_path=None):
        """Save DataFrame to SQLite"""
        db_path = db_path or self.db_path
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check if table exists and fetch previous applied data
            # cursor.execute(
            #     "SELECT name FROM sqlite_master WHERE type='table' AND name='sponsors'"
            # )
            # if cursor.fetchone():
            #     cursor.execute("SELECT organisation_name, applied FROM sponsors")
            #     applied_data = dict(cursor.fetchall())
            # else:
            #     applied_data = {}

            # Add 'applied' column to DataFrame based on existing data
            # if "organisation_name" not in df.columns:
            #     raise ValueError("'organisation_name' column is missing from the CSV.")
            # df["applied"] = df["organisation_name"].apply(
            #     lambda name: applied_data.get(name, 0)
            # )

            # Build column creation SQL (excluding 'applied')
            column_names = ", ".join(
                [f"{col} TEXT" for col in df.columns]
            )
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS sponsors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {column_names}
                )
            """
            )
                    # applied INTEGER DEFAULT 0

            # Clear old data and insert new
            cursor.execute("DELETE FROM sponsors")
            df.to_sql("sponsors", conn, if_exists="append", index=False)
        self.logger.info("✅ Data saved to %s", db_path)


if __name__ == "__main__":
    # If run as a script, this block performs the CSV transformation
    # and prints the first few rows of the resulting DataFrame.
    transform = TransformDB()
    transformed_df = transform.clean_and_transform_csv()
    print(transformed_df.head())
