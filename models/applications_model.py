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

    def get_applications(
        self, organisation_name=None, city=None, limit: int = 50, offset=0
    ):
        query = "SELECT * FROM applications WHERE 1=1"
        params = []
        if organisation_name:
            query += " AND organisation_name LIKE ?"
            params.append(f"%{organisation_name}%")
        if city:
            query += " AND city LIKE ?"
            params.append(f"%{city}%")
        count_query = f"SELECT COUNT(*) FROM ({query})"
        query += " ORDER BY date DESC"
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            count = cursor.execute(count_query, params[:-2]).fetchone()[0]
            cursor.execute(query, params)
            return cursor.fetchall(), count

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
