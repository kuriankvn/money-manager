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


def init_user_tables() -> None:
    """Initialize user tables only"""
    db_path: Path = get_db_path()
    conn: sqlite3.Connection = sqlite3.connect(database=db_path)
    cursor: sqlite3.Cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL)
    """)
    
    conn.commit()
    conn.close()


def init_category_tables() -> None:
    """Initialize category tables only"""
    db_path: Path = get_db_path()
    conn: sqlite3.Connection = sqlite3.connect(database=db_path)
    cursor: sqlite3.Cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            user_uid TEXT NOT NULL,
            FOREIGN KEY (user_uid) REFERENCES users(uid))
    """)
    
    conn.commit()
    conn.close()


def init_transaction_tables() -> None:
    """Initialize transaction tables (requires user and category tables)"""
    db_path: Path = get_db_path()
    conn: sqlite3.Connection = sqlite3.connect(database=db_path)
    cursor: sqlite3.Cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            datetime REAL NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
            user_uid TEXT NOT NULL,
            category_uid TEXT NOT NULL,
            FOREIGN KEY (user_uid) REFERENCES users(uid),
            FOREIGN KEY (category_uid) REFERENCES categories(uid))
    """)
    
    conn.commit()
    conn.close()


def init_subscription_tables() -> None:
    """Initialize subscription tables (requires user and category tables)"""
    db_path: Path = get_db_path()
    conn: sqlite3.Connection = sqlite3.connect(database=db_path)
    cursor: sqlite3.Cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            interval TEXT NOT NULL CHECK (interval IN ('daily', 'weekly', 'monthly', 'yearly')),
            multiplier INTEGER NOT NULL,
            user_uid TEXT NOT NULL,
            category_uid TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_uid) REFERENCES users(uid),
            FOREIGN KEY (category_uid) REFERENCES categories(uid))
    """)
    
    conn.commit()
    conn.close()


def init_database() -> None:
    """Initialize all database tables for money_manager and subscription_manager"""
    init_user_tables()
    init_category_tables()
    init_transaction_tables()
    init_subscription_tables()


def get_connection() -> sqlite3.Connection:
    db_path: Path = get_db_path()
    return sqlite3.connect(database=db_path)
