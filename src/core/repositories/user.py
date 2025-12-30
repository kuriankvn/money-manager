import sqlite3
from typing import Any, Optional
from core.database import get_connection
from core.repositories import IRepository
from core.models import User
from core.exceptions import DuplicateEntityError


class UserRepository(IRepository[User]):
    def create(self, entity: User) -> str:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO users (uid, name) VALUES (?, ?)", (entity.uid, entity.name))
            connection.commit()
            return entity.uid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntityError(f"User '{entity.name}' already exists") from e
        finally:
            connection.close()
    
    def get_by_id(self, uid: str) -> Optional[User]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("SELECT uid, name FROM users WHERE uid = ?", (uid,))
        row = cursor.fetchone()
        connection.close()
        if row:
            return User(uid=row[0], name=row[1])
        return None
    
    def get_all(self) -> list[User]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("SELECT uid, name FROM users")
        rows: list[Any] = cursor.fetchall()
        connection.close()
        return [User(uid=row[0], name=row[1]) for row in rows]
    
    def update(self, entity: User) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        try:
            cursor.execute("UPDATE users SET name = ? WHERE uid = ?", (entity.name, entity.uid))
            affected: int = cursor.rowcount
            connection.commit()
            return affected > 0
        except sqlite3.IntegrityError as e:
            raise DuplicateEntityError(f"User '{entity.name}' already exists") from e
        finally:
            connection.close()
    
    def delete(self, uid: str) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE uid = ?", (uid,))
        affected: int = cursor.rowcount
        connection.commit()
        connection.close()
        return affected > 0
    
    def get_by_name(self, name: str) -> Optional[User]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("SELECT uid, name FROM users WHERE name = ?", (name,))
        row = cursor.fetchone()
        connection.close()
        if row:
            return User(uid=row[0], name=row[1])
        return None
