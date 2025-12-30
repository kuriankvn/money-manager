import sqlite3
from core.storage.init_db import get_connection


def init_subscription_tables() -> None:
    """Initialize subscription-related tables"""
    conn: sqlite3.Connection = get_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    
    # Subscriptions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            amount REAL NOT NULL,
            frequency TEXT NOT NULL CHECK (frequency IN ('monthly', 'yearly')),
            interval INTEGER NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('active', 'cancelled')))
    """)
    
    # Subscription instances table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscription_instances (
            uid TEXT PRIMARY KEY,
            subscription_id TEXT NOT NULL,
            amount REAL NOT NULL,
            due_date TEXT NOT NULL,
            transaction_id TEXT,
            status TEXT NOT NULL CHECK (status IN ('due', 'paid', 'overdue')),
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(uid),
            FOREIGN KEY (transaction_id) REFERENCES transactions(uid))
    """)
    
    conn.commit()
    conn.close()

# Made with Bob
