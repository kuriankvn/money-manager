import sqlite3
from typing import Any, Optional
from money_manager.database import get_connection
from money_manager.repositories.base import IRepository
from money_manager.repositories.user import UserRepository
from money_manager.models.category import Category
from money_manager.models.user import User


class CategoryRepository(IRepository[Category]):
    def __init__(self) -> None:
        self.user_repo: UserRepository = UserRepository()
    
    def create(self, entity: Category) -> str:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO categories (uid, name, user_uid) VALUES (?, ?, ?)",
            (entity.uid, entity.name, entity.user.uid))
        connection.commit()
        connection.close()
        return entity.uid
    
    def get_by_id(self, uid: str) -> Optional[Category]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "SELECT uid, name, user_uid FROM categories WHERE uid = ?",
            (uid,))
        row = cursor.fetchone()
        connection.close()
        
        if row:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[2])
            if not user:
                return None
            return Category(
                uid=row[0],
                name=row[1],
                user=user)
        return None
    
    def get_all(self) -> list[Category]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("SELECT uid, name, user_uid FROM categories")
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        categories: list[Category] = []
        for row in rows:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[2])
            if user:
                categories.append(Category(
                    uid=row[0],
                    name=row[1],
                    user=user))
        return categories
    
    def update(self, entity: Category) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        
        cursor.execute(
            "UPDATE categories SET name = ?, user_uid = ? WHERE uid = ?",
            (entity.name, entity.user.uid, entity.uid))
        affected: int = cursor.rowcount
        connection.commit()
        connection.close()
        return affected > 0
    
    def delete(self, uid: str) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("DELETE FROM categories WHERE uid = ?", (uid,))
        affected: int = cursor.rowcount
        connection.commit()
        connection.close()
        return affected > 0

# Made with Bob
