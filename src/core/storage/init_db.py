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


def get_connection() -> sqlite3.Connection:
    db_path: Path = get_db_path()
    return sqlite3.connect(database=db_path)


def init_database() -> None:
    """Initialize all database tables for money_manager"""
    from .transactions import init_transaction_tables
    from .subscriptions import init_subscription_tables
    from .investments import init_investment_tables
    
    init_transaction_tables()
    init_subscription_tables()
    init_investment_tables()

# Made with Bob
