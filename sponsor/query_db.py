import sqlite3, os
from TSA.config import DB_PATH

class QueryDB:
    def __init__(self, db_path=DB_PATH):
        """Initial definitions"""
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file {self.db_path} not found!")
    
    def execute_query(self, query, params=()):
        """Executes given query"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        
    def get_all_records(self, limit=10):
        """Fetches all records with an optional limit"""
        query = f"SELECT * FROM sponsors LIMIT {limit}"
        return self.execute_query(query)

    def search_by_city(self, city):
        """Fetches records filtered by city"""
        query = "SELECT * FROM sponsors WHERE town_city LIKE ?"
        return self.execute_query(query, (f"%{city}%",))

    def search_by_route(self, route):
        """Fetches records filtered by route type (e.g., Skilled Worker)"""
        query = "SELECT * FROM sponsors WHERE route LIKE ?"
        return self.execute_query(query, (f"%{route}%",))
    
if __name__ == "__main__":
    query_db = QueryDB()

    print("📌 First 10 records from database:")
    print(query_db.get_all_records())

    # print("\n📌 Searching for sponsors in 'Bristol':")
    # print(query_db.search_by_city("Bristol"))

    # print("\n📌 Searching for 'Skilled Worker' route:")
    # print(query_db.search_by_route("Skilled Worker"))
