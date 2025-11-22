import sqlite3
from typing import Any, Optional

from money_manager.database import get_connection
from money_manager.models import Category, Transaction, TransactionType, User


class UserRepository:
    def create(self, user: User) -> str:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("INSERT INTO users (uid, name) VALUES (?, ?)", (user.uid, user.name))
        conn.commit()
        conn.close()
        return user.uid
    
    def get_by_id(self, uid: str) -> Optional[User]:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("SELECT uid, name FROM users WHERE uid = ?", (uid,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(uid=row[0], name=row[1])
        return None
    
    def get_all(self) -> list[User]:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("SELECT uid, name FROM users")
        rows: list[Any] = cursor.fetchall()
        conn.close()
        
        return [User(uid=row[0], name=row[1]) for row in rows]
    
    def update(self, user: User) -> bool:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("UPDATE users SET name = ? WHERE uid = ?", (user.name, user.uid))
        affected: int = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def delete(self, uid: str) -> bool:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE uid = ?", (uid,))
        affected: int = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0


class CategoryRepository:
    def create(self, category: Category) -> str:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        parent_uid: Optional[str] = category.parent_category.uid if category.parent_category else None
        cursor.execute(
            "INSERT INTO categories (uid, type, name, parent_category) VALUES (?, ?, ?, ?)",
            (category.uid, category.type.value, category.name, parent_uid)
        )
        conn.commit()
        conn.close()
        return category.uid
    
    def get_by_id(self, uid: str) -> Optional[Category]:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(
            "SELECT uid, type, name, parent_category FROM categories WHERE uid = ?",
            (uid,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            parent_category: Optional[Category] = self.get_by_id(uid=row[3]) if row[3] else None
            return Category(
                uid=row[0],
                type=TransactionType(value=row[1]),
                name=row[2],
                parent_category=parent_category
            )
        return None
    
    def get_all(self) -> list[Category]:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("SELECT uid, type, name, parent_category FROM categories")
        rows: list[Any] = cursor.fetchall()
        conn.close()
        
        categories: list[Any] = []
        for row in rows:
            parent_category: Optional[Category] = self.get_by_id(uid=row[3]) if row[3] else None
            categories.append(Category(
                uid=row[0],
                type=TransactionType(value=row[1]),
                name=row[2],
                parent_category=parent_category
            ))
        return categories
    
    def get_by_type(self, transaction_type: TransactionType) -> list[Category]:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(
            "SELECT uid, type, name, parent_category FROM categories WHERE type = ?",
            (transaction_type.value,)
        )
        rows: list[Any] = cursor.fetchall()
        conn.close()
        
        categories:list[Any] = []
        for row in rows:
            parent_category: Optional[Category] = self.get_by_id(uid=row[3]) if row[3] else None
            categories.append(Category(
                uid=row[0],
                type=TransactionType(value=row[1]),
                name=row[2],
                parent_category=parent_category
            ))
        return categories
    
    def update(self, category: Category) -> bool:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        
        parent_uid: Optional[str] = category.parent_category.uid if category.parent_category else None
        
        cursor.execute(
            "UPDATE categories SET type = ?, name = ?, parent_category = ? WHERE uid = ?",
            (category.type.value, category.name, parent_uid, category.uid)
        )
        affected: int = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def delete(self, uid: str) -> bool:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE uid = ?", (uid,))
        affected: int = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0


class TransactionRepository:
    def __init__(self) -> None:
        self.category_repo: CategoryRepository = CategoryRepository()
    
    def create(self, transaction: Transaction) -> str:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO transactions 
            (uid, user_uid, amount, date_time, type, category) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                transaction.uid,
                transaction.user_uid,
                transaction.amount,
                transaction.date_time,
                transaction.type.value,
                transaction.category.uid
            )
        )
        conn.commit()
        conn.close()
        return transaction.uid
    
    def get_by_id(self, uid: str) -> Optional[Transaction]:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(
            """SELECT uid, user_uid, amount, date_time, type, category 
            FROM transactions WHERE uid = ?""",
            (uid,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[5])
            if not category:
                return None
            return Transaction(
                uid=row[0],
                user_uid=row[1],
                amount=row[2],
                date_time=row[3],
                type=TransactionType(value=row[4]),
                category=category
            )
        return None
    
    def get_all(self) -> list[Transaction]:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("SELECT uid, user_uid, amount, date_time, type, category FROM transactions")
        rows: list[Any] = cursor.fetchall()
        conn.close()
        
        transactions: list[Any] = []
        for row in rows:
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[5])
            if category:
                transactions.append(Transaction(
                    uid=row[0],
                    user_uid=row[1],
                    amount=row[2],
                    date_time=row[3],
                    type=TransactionType(value=row[4]),
                    category=category
                ))
        return transactions
    
    def get_by_user(self, user_uid: str) -> list[Transaction]:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(
            """SELECT uid, user_uid, amount, date_time, type, category 
            FROM transactions WHERE user_uid = ?""",
            (user_uid,)
        )
        rows: list[Any] = cursor.fetchall()
        conn.close()
        
        transactions: list[Any] = []
        for row in rows:
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[5])
            if category:
                transactions.append(Transaction(
                    uid=row[0],
                    user_uid=row[1],
                    amount=row[2],
                    date_time=row[3],
                    type=TransactionType(value=row[4]),
                    category=category
                ))
        return transactions
    
    def get_by_user_and_type(
        self,
        user_uid: str,
        transaction_type: TransactionType
    ) -> list[Transaction]:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(
            """SELECT uid, user_uid, amount, date_time, type, category
            FROM transactions WHERE user_uid = ? AND type = ?""",
            (user_uid, transaction_type.value)
        )
        rows: list[Any] = cursor.fetchall()
        conn.close()
        
        transactions: list[Transaction] = []
        for row in rows:
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[5])
            if category:
                transactions.append(Transaction(
                    uid=row[0],
                    user_uid=row[1],
                    amount=row[2],
                    date_time=row[3],
                    type=TransactionType(value=row[4]),
                    category=category
                ))
        return transactions
    
    def get_by_user_type_and_category(
        self,
        user_uid: str,
        transaction_type: TransactionType,
        category_uid: str
    ) -> list[Transaction]:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute(
            """SELECT uid, user_uid, amount, date_time, type, category
            FROM transactions WHERE user_uid = ? AND type = ? AND category = ?""",
            (user_uid, transaction_type.value, category_uid)
        )
        rows: list[Any] = cursor.fetchall()
        conn.close()
        
        transactions: list[Transaction] = []
        for row in rows:
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[5])
            if category:
                transactions.append(Transaction(
                    uid=row[0],
                    user_uid=row[1],
                    amount=row[2],
                    date_time=row[3],
                    type=TransactionType(value=row[4]),
                    category=category
                ))
        return transactions
    
    def update(self, transaction: Transaction) -> bool:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        
        cursor.execute(
            """UPDATE transactions SET user_uid = ?, amount = ?, date_time = ?, type = ?, category = ? WHERE uid = ?""",
            (transaction.user_uid, transaction.amount, transaction.date_time, transaction.type.value, transaction.category.uid, transaction.uid)
        )
        affected: int = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def delete(self, uid: str) -> bool:
        conn: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE uid = ?", (uid,))
        affected: int = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
