import os
import sqlite3
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def get_db_path() -> Path:
    db_path_str: Optional[str] = os.getenv(key='MONEY_MANAGER_DB')
    if not db_path_str:
        raise ValueError("MONEY_MANAGER_DB environment variable is not set.")
    
    db_path: Path = Path(db_path_str)
    parent_dir: Path = db_path.parent
    if not parent_dir.exists():
        raise ValueError(f"Parent directory does not exist: {parent_dir}")
    
    return db_path


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
            name TEXT NOT NULL,
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
