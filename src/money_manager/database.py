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
            name TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            uid TEXT PRIMARY KEY,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
            name TEXT NOT NULL,
            parent_category TEXT,
            FOREIGN KEY (parent_category) REFERENCES categories(uid)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            uid TEXT PRIMARY KEY,
            user_uid TEXT NOT NULL,
            amount REAL NOT NULL,
            date_time REAL NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
            category TEXT NOT NULL,
            FOREIGN KEY (user_uid) REFERENCES users(uid),
            FOREIGN KEY (category) REFERENCES categories(uid)
        )
    """)
    
    conn.commit()
    conn.close()


def get_connection() -> sqlite3.Connection:
    db_path: Path = get_db_path()
    return sqlite3.connect(database=db_path)
