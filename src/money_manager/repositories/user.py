import sqlite3
from typing import Any, Optional
from money_manager.database import get_connection
from money_manager.repositories.base import IRepository
from money_manager.models.user import User


class UserRepository(IRepository[User]):
    def create(self, entity: User) -> str:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("INSERT INTO users (uid, name) VALUES (?, ?)", (entity.uid, entity.name))
        connection.commit()
        connection.close()
        return entity.uid
    
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
        cursor.execute("UPDATE users SET name = ? WHERE uid = ?", (entity.name, entity.uid))
        affected: int = cursor.rowcount
        connection.commit()
        connection.close()
        return affected > 0
    
    def delete(self, uid: str) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE uid = ?", (uid,))
        affected: int = cursor.rowcount
        connection.commit()
        connection.close()
        return affected > 0

# Made with Bob
