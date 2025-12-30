"""Database migrations."""
import sqlite3
from pathlib import Path
from app.storage.db import get_connection


def run_migrations() -> None:
    """Run all database migrations in order."""
    conn = get_connection()
    
    # Get migration files
    migrations_dir = Path(__file__).parent
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    for migration_file in migration_files:
        print(f"Running migration: {migration_file.name}")
        with open(migration_file, "r") as f:
            sql = f.read()
            conn.executescript(sql)
    
    conn.commit()
    conn.close()
    print("All migrations completed successfully")

