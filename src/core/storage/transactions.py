import sqlite3
from core.storage.init_db import get_connection


def init_transaction_tables() -> None:
    """Initialize transaction-related tables"""
    conn: sqlite3.Connection = get_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    
    # Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE)
    """)
    
    # Accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE)
    """)
    
    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            account_id TEXT NOT NULL,
            category_id TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(uid),
            FOREIGN KEY (category_id) REFERENCES categories(uid))
    """)
    
    conn.commit()
    conn.close()

# Made with Bob
