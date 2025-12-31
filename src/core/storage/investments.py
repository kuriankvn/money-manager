import sqlite3
from core.storage.init_db import get_connection


def init_investment_tables() -> None:
    """Initialize investment-related tables"""
    conn: sqlite3.Connection = get_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    
    # Investments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investments (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            start_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('active', 'closed')))
    """)
    
    # Investment value snapshots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investment_value_snapshots (
            uid TEXT PRIMARY KEY,
            investment_id TEXT NOT NULL,
            date TEXT NOT NULL,
            current_value REAL NOT NULL,
            FOREIGN KEY (investment_id) REFERENCES investments(uid))
    """)
    
    # Investment plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investment_plans (
            uid TEXT PRIMARY KEY,
            investment_id TEXT NOT NULL,
            amount REAL NOT NULL,
            frequency TEXT NOT NULL CHECK (frequency IN ('monthly', 'yearly')),
            interval INTEGER NOT NULL,
            due_day INTEGER NOT NULL,
            due_month INTEGER,
            status TEXT NOT NULL CHECK (status IN ('active', 'closed')),
            FOREIGN KEY (investment_id) REFERENCES investments(uid))
    """)
    
    # Investment plan instances table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investment_plan_instances (
            uid TEXT PRIMARY KEY,
            investment_plan_id TEXT NOT NULL,
            amount REAL NOT NULL,
            due_date TEXT NOT NULL,
            transaction_id TEXT,
            status TEXT NOT NULL CHECK (status IN ('planned', 'executed', 'skipped')),
            FOREIGN KEY (investment_plan_id) REFERENCES investment_plans(uid),
            FOREIGN KEY (transaction_id) REFERENCES transactions(uid))
    """)
    
    conn.commit()
    conn.close()

# Made with Bob
