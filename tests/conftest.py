import sqlite3
import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def db_conn():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    
    conn.executescript("""
        CREATE TABLE accounts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('BANK', 'CARD')),
            institution TEXT NOT NULL,
            notes TEXT
        );
        
        CREATE TABLE transactions (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            date TEXT NOT NULL,
            amount TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );
        
        CREATE TABLE subscriptions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('BILL', 'INSURANCE', 'OTHER')),
            frequency TEXT NOT NULL CHECK (frequency IN ('MONTHLY', 'YEARLY')),
            due_day INTEGER NOT NULL CHECK (due_day >= 1 AND due_day <= 31),
            expected_amount TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            notes TEXT
        );
        
        CREATE TABLE subscription_instances (
            id TEXT PRIMARY KEY,
            subscription_id TEXT NOT NULL,
            period TEXT NOT NULL,
            due_date TEXT NOT NULL,
            amount TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('DUE', 'PAID')),
            paid_date TEXT,
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE
        );
        
        CREATE TABLE investments (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            provider TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('MF', 'STOCK', 'FD', 'GOLD')),
            notes TEXT
        );
        
        CREATE TABLE investment_contributions (
            id TEXT PRIMARY KEY,
            investment_id TEXT NOT NULL,
            date TEXT NOT NULL,
            amount TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (investment_id) REFERENCES investments(id) ON DELETE CASCADE
        );
        
        CREATE TABLE investment_value_snapshots (
            id TEXT PRIMARY KEY,
            investment_id TEXT NOT NULL,
            date TEXT NOT NULL,
            current_value TEXT NOT NULL,
            FOREIGN KEY (investment_id) REFERENCES investments(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    
    yield conn
    
    conn.close()
    db_path.unlink()

# Made with Bob
