import os, pytest, sqlite3
from sponsor.transform_db import TransformDB
# import pandas as pd

@pytest.fixture
def transform_db():
    """Fresh transform DB instance for each test"""
    db_path = "data/test_sponsorship.db"
    csv_path = "data/sponsors.csv"

    if os.path.exists(db_path):
        os.remove(db_path)

    return TransformDB(csv_path=csv_path, db_path=db_path)

@pytest.fixture
def db_and_conn(transform_db):
    """Prepare df, save it to SQLite, and provide a database connection for tests"""
    df = transform_db.clean_and_transform_csv()
    transform_db.save_as_sqlite(df)

    with sqlite3.connect(transform_db.db_path) as conn:
        yield df, conn # Send df and conn as tuple

def test_save_as_sqlite(db_and_conn):
    """Test if .csv data is successfully transformed into SQLite"""
    df, conn = db_and_conn

    # Check if table exists
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='sponsors'"
    )
    table_exists = cursor.fetchone()
    assert table_exists, "❌ sponsors table was not created"

    # Check column names
    cursor.execute("PRAGMA table_info(sponsors)")
    columns = {col[1] for col in cursor.fetchall()} - {"id"}
    # raw_cols = pd.read_csv("data/sponsors.csv", encoding="utf-8")
    # print("Raw columns:", raw_cols.columns)
    # print("sql columns: "+str(columns))
    # print("df: "+str(set(df.columns)))
    assert set(df.columns) == columns, "❌ Columns do not match"

def test_row_count(db_and_conn):
    """Test if row count in SQLite matches .csv file"""
    df, conn = db_and_conn

    cursor = conn.cursor() 
    cursor.execute("SELECT COUNT(*) FROM sponsors")
    row_count = cursor.fetchone()[0]
    assert row_count == len(df), (
        f"❌ Row count mismatch: Expected {len(df)}, Found {row_count}"
    )

def test_duplication(db_and_conn):
    """Test if data inserts cause duplication"""
    df, conn = db_and_conn
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sponsors")
    initial_row_count = cursor.fetchone()[0]

    transform_db = TransformDB()
    transform_db.save_as_sqlite(df)

    cursor.execute("SELECT COUNT(*) FROM sponsors")
    new_row_count = cursor.fetchone()[0]

    assert initial_row_count == new_row_count, (
        f"❌ Duplicate entries found! Expected {initial_row_count}, but got {new_row_count}"
    )

    print("✅ SQLite transformation tests passed")