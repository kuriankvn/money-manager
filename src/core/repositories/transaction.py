import sqlite3
from typing import Any, Optional
from core.database import get_connection
from core.repositories import IRepository, UserRepository, CategoryRepository
from core.models import Transaction, TransactionType, User, Category


class TransactionRepository(IRepository[Transaction]):
    def __init__(self) -> None:
        self.user_repo: UserRepository = UserRepository()
        self.category_repo: CategoryRepository = CategoryRepository()
    
    def create(self, entity: Transaction) -> str:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO transactions (uid, name, amount, datetime, type, user_uid, category_uid) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (entity.uid, entity.name, entity.amount, entity.date, entity.type.value, entity.user.uid, entity.category.uid))
        connection.commit()
        connection.close()
        return entity.uid
    
    def get_by_id(self, uid: str) -> Optional[Transaction]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """SELECT uid, name, amount, datetime, type, user_uid, category_uid FROM transactions WHERE uid = ?""",
            (uid,))
        row = cursor.fetchone()
        connection.close()
        
        if row:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[5])
            if not user:
                return None
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[6])
            if not category:
                return None
            return Transaction(
                uid=row[0],
                name=row[1],
                amount=row[2],
                date=row[3],
                type=TransactionType(value=row[4]),
                user=user,
                category=category)
        return None
    
    def get_all(self) -> list[Transaction]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("SELECT uid, name, amount, datetime, type, user_uid, category_uid FROM transactions")
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        transactions: list[Transaction] = []
        for row in rows:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[5])
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[6])
            if user and category:
                transactions.append(Transaction(
                    uid=row[0],
                    name=row[1],
                    amount=row[2],
                    date=row[3],
                    type=TransactionType(value=row[4]),
                    user=user,
                    category=category))
        return transactions
    
    def update(self, entity: Transaction) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        
        cursor.execute(
            """UPDATE transactions SET name = ?, amount = ?, datetime = ?, type = ?, user_uid = ?, category_uid = ? WHERE uid = ?""",
            (entity.name, entity.amount, entity.date, entity.type.value, entity.user.uid, entity.category.uid, entity.uid))
        affected: int = cursor.rowcount
        connection.commit()
        connection.close()
        return affected > 0
    
    def delete(self, uid: str) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("DELETE FROM transactions WHERE uid = ?", (uid,))
        affected: int = cursor.rowcount
        connection.commit()
        connection.close()
        return affected > 0
