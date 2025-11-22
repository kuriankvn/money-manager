import sqlite3
from typing import Any, Optional

from money_manager.database import get_connection
from money_manager.models import Category, Transaction, TransactionType, User


class UserRepository:
    def create(self, user: User) -> str:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("INSERT INTO users (uid, name) VALUES (?, ?)", (user.uid, user.name))
        connection.commit()
        connection.close()
        return user.uid
    
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
    
    def update(self, user: User) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("UPDATE users SET name = ? WHERE uid = ?", (user.name, user.uid))
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


class CategoryRepository:
    def create(self, category: Category) -> str:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO categories (uid, name, type) VALUES (?, ?, ?)",
            (category.uid, category.name, category.type.value))
        connection.commit()
        connection.close()
        return category.uid
    
    def get_by_id(self, uid: str) -> Optional[Category]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "SELECT uid, name, type FROM categories WHERE uid = ?",
            (uid,))
        row = cursor.fetchone()
        connection.close()
        
        if row:
            return Category(
                uid=row[0],
                name=row[1],
                type=TransactionType(value=row[2]))
        return None
    
    def get_all(self) -> list[Category]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("SELECT uid, name, type FROM categories")
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        categories: list[Category] = []
        for row in rows:
            categories.append(Category(
                uid=row[0],
                name=row[1],
                type=TransactionType(value=row[2])))
        return categories
    
    def get_by_type(self, transaction_type: TransactionType) -> list[Category]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "SELECT uid, name, type FROM categories WHERE type = ?",
            (transaction_type.value,))
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        categories: list[Category] = []
        for row in rows:
            categories.append(Category(
                uid=row[0],
                name=row[1],
                type=TransactionType(value=row[2])))
        return categories
    
    def update(self, category: Category) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        
        cursor.execute(
            "UPDATE categories SET name = ?, type = ? WHERE uid = ?",
            (category.name, category.type.value, category.uid))
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


class TransactionRepository:
    def __init__(self) -> None:
        self.user_repo: UserRepository = UserRepository()
        self.category_repo: CategoryRepository = CategoryRepository()
    
    def create(self, transaction: Transaction) -> str:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO transactions (uid, amount, datetime, user_uid, category_uid) VALUES (?, ?, ?, ?, ?)""",
            (transaction.uid, transaction.amount, transaction.datetime, transaction.user.uid, transaction.category.uid))
        connection.commit()
        connection.close()
        return transaction.uid
    
    def get_by_id(self, uid: str) -> Optional[Transaction]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """SELECT uid, amount, datetime, user_uid, category_uid FROM transactions WHERE uid = ?""",
            (uid,))
        row = cursor.fetchone()
        connection.close()
        
        if row:
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[4])
            if not category:
                return None
            user: Optional[User] = self.user_repo.get_by_id(uid=row[3])
            if not user:
                return None
            return Transaction(
                uid=row[0],
                amount=row[1],
                datetime=row[2],
                user=user,
                category=category)
        return None
    
    def get_all(self) -> list[Transaction]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("SELECT uid, amount, datetime, user_uid, category_uid FROM transactions")
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        transactions: list[Transaction] = []
        for row in rows:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[3])
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[4])
            if user and category:
                transactions.append(Transaction(
                    uid=row[0],
                    amount=row[1],
                    datetime=row[2],
                    user=user,
                    category=category))
        return transactions
    
    def get_by_user(self, user_uid: str) -> list[Transaction]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """SELECT uid, amount, datetime, user_uid, category_uid FROM transactions WHERE user_uid = ?""",
            (user_uid,))
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        transactions: list[Transaction] = []
        for row in rows:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[3])
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[4])
            if user and category:
                transactions.append(Transaction(
                    uid=row[0],
                    amount=row[1],
                    datetime=row[2],
                    user=user,
                    category=category))
        return transactions
    
    def get_by_user_and_type(self, user_uid: str, transaction_type: TransactionType) -> list[Transaction]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """SELECT t.uid, t.amount, t.datetime, t.user_uid, t.category_uid FROM transactions t
            JOIN categories c ON t.category_uid = c.uid WHERE t.user_uid = ? AND c.type = ?""",
            (user_uid, transaction_type.value))
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        transactions: list[Transaction] = []
        for row in rows:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[3])
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[4])
            if user and category:
                transactions.append(Transaction(
                    uid=row[0],
                    amount=row[1],
                    datetime=row[2],
                    user=user,
                    category=category))
        return transactions
    
    def get_by_user_type_and_category(self, user_uid: str, transaction_type: TransactionType, category_uid: str) -> list[Transaction]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """SELECT t.uid, t.amount, t.datetime, t.user_uid, t.category_uid FROM transactions t
            JOIN categories c ON t.category_uid = c.uid WHERE t.user_uid = ? AND c.type = ? AND t.category_uid = ?""",
            (user_uid, transaction_type.value, category_uid))
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        transactions: list[Transaction] = []
        for row in rows:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[3])
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[4])
            if user and category:
                transactions.append(Transaction(
                    uid=row[0],
                    amount=row[1],
                    datetime=row[2],
                    user=user,
                    category=category))
        return transactions
    
    def update(self, transaction: Transaction) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        
        cursor.execute(
            """UPDATE transactions SET amount = ?, datetime = ?, user_uid = ?, category_uid = ? WHERE uid = ?""",
            (transaction.amount, transaction.datetime, transaction.user.uid, transaction.category.uid, transaction.uid)
        )
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
