import pandas as pd
import os
import sqlite3
from TSA.config import CSV_PATH, DB_PATH

# df = pd.read_csv("sponsors.csv", header=0)
# print(df.columns)
# df.columns = ["organisation", "city", "county", "type_rating", "route"]
# print(df.columns)

class TransformDB:
    def __init__(self, csv_path=CSV_PATH, db_path=DB_PATH):
        """Initial definitions"""
        self.csv_path = csv_path
        self.db_path = db_path
        # if db file location is changed by the user, will make dir
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def clean_and_transform_csv(self):
        """Cleans the csv and transforms to dataframe"""
        print(f"📌 {self.csv_path} is transforming...")

        df = pd.read_csv(self.csv_path, encoding="utf-8")
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("/", "_").str.replace("&", "and").str.lower()
        df = df.fillna("")

        print(f"✅ {self.csv_path} is transformed.")
        return df
    
    def save_as_sqlite(self, df, db_path):
        """Save DataFrame to SQLite"""
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check if table exists and fetch previous applied data
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sponsors'")
            if cursor.fetchone():
                cursor.execute("SELECT organisation_name, applied FROM sponsors")
                applied_data = dict(cursor.fetchall())
            else:
                applied_data = {}

            # Add 'applied' column to DataFrame based on existing data
            df["applied"] = df["organisation_name"].apply(lambda name: applied_data.get(name, 0))

            # Build column creation SQL (excluding 'applied')
            column_names = ", ".join([f"{col} TEXT" for col in df.columns if col != "applied"])
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS sponsors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {column_names},
                    applied INTEGER DEFAULT 0
                )
            """)

            # Clear old data and insert new
            cursor.execute("DELETE FROM sponsors")
            df.to_sql("sponsors", conn, if_exists="append", index=False)
        print(f"✅ Data saved to {db_path}")

if __name__ == "__main__":
    transform = TransformDB()
    df = transform.clean_and_transform_csv()
    print(df.head())
    # print(df["organisation_name"].unique()[:10])
    transform.save_as_sqlite(df, transform.db_path)