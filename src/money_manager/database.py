import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    return Path(__file__).parent.parent.parent / "money_manager.db"


def init_database() -> None:
    db_path: Path = get_db_path()
    
    conn: sqlite3.Connection = sqlite3.connect(database=db_path)
    cursor: sqlite3.Cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL)
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')))
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            uid TEXT PRIMARY KEY,
            amount REAL NOT NULL,
            datetime REAL NOT NULL,
            user_uid TEXT NOT NULL,
            category_uid TEXT NOT NULL,
            FOREIGN KEY (user_uid) REFERENCES users(uid),
            FOREIGN KEY (category_uid) REFERENCES categories(uid))
    """)
    
    conn.commit()
    conn.close()


def get_connection() -> sqlite3.Connection:
    db_path: Path = get_db_path()
    return sqlite3.connect(database=db_path)
