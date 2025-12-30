"""Database connection handling."""
import sqlite3
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def get_db_path() -> Path:
    """Get database path from environment variable."""
    db_path_str: Optional[str] = os.getenv("MONEY_MANAGER_DB")
    if not db_path_str:
        raise ValueError("MONEY_MANAGER_DB environment variable is not set.")
    
    db_path: Path = Path(db_path_str)
    parent_dir: Path = db_path.parent
    if not parent_dir.exists():
        parent_dir.mkdir(parents=True, exist_ok=True)
    
    return db_path


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    db_path: Path = get_db_path()
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database() -> None:
    """Initialize database with all migrations."""
    from app.storage.migrations import run_migrations
    run_migrations()

