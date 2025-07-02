import sqlite3
from config import DB_PATH


class ApplicationsModel:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organisation_name TEXT NOT NULL,
                    city TEXT NOT NULL,
                    role TEXT,
                    date TEXT,
                    contact TEXT,
                    note TEXT
                )
                """
            )
            conn.commit()

    def add_application(self, organisation_name, city, *, role, date, contact, note):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO applications (organisation_name, city, role, date, contact, note)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (organisation_name, city, role, date, contact, note),
            )
            conn.commit()

    def get_applications_by_organisation(self, organisation_name, city):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM applications WHERE organisation_name=? AND city=?
                ORDER BY date DESC
                """,
                (organisation_name, city),
            )
            return cursor.fetchall()

    def update_application(self, application_id, *, role, date, contact, note):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE applications
                SET role = ?, date = ?, contact = ?, note = ?
                WHERE id = ?
                """,
                (role, date, contact, note, application_id),
            )
            conn.commit()

    def delete_application(self, application_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM applications
                WHERE id = ?
                """,
                (application_id,),
            )
            conn.commit()

    def has_application(self, org, city):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM applications WHERE organisation_name=? AND city=?",
                (org, city),
            )
            return cursor.fetchone()[0] > 0

    def get_application_org_city_pairs(self):
        pairs = set()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT organisation_name, city FROM applications")
            for org, city in cursor.fetchall():
                pairs.add((org, city))
        return pairs
