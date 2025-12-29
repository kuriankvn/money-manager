import sqlite3
from typing import Any, Optional
from money_manager.database import get_connection
from money_manager.repositories.base import IRepository
from money_manager.repositories.user import UserRepository
from money_manager.repositories.category import CategoryRepository
from money_manager.models.user import User
from money_manager.models.category import Category
from money_manager.models.subscription import Subscription, Interval


class SubscriptionRepository(IRepository[Subscription]):
    def __init__(self) -> None:
        self.user_repo: UserRepository = UserRepository()
        self.category_repo: CategoryRepository = CategoryRepository()
    
    def create(self, entity: Subscription) -> str:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO subscriptions (uid, name, amount, interval, multiplier, user_uid, category_uid, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (entity.uid, entity.name, entity.amount, entity.interval.value,
             entity.multiplier, entity.user.uid, entity.category.uid, 1 if entity.active else 0))
        connection.commit()
        connection.close()
        return entity.uid
    
    def get_by_id(self, uid: str) -> Optional[Subscription]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """SELECT uid, name, amount, interval, multiplier, user_uid, category_uid, active
            FROM subscriptions WHERE uid = ?""",
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
            return Subscription(
                uid=row[0],
                name=row[1],
                amount=row[2],
                interval=Interval(value=row[3]),
                multiplier=row[4],
                user=user,
                category=category,
                active=bool(row[7]))
        return None
    
    def get_all(self) -> list[Subscription]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """SELECT uid, name, amount, interval, multiplier, user_uid, category_uid, active
            FROM subscriptions""")
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        subscriptions: list[Subscription] = []
        for row in rows:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[5])
            category: Optional[Category] = self.category_repo.get_by_id(uid=row[6])
            if user and category:
                subscriptions.append(Subscription(
                    uid=row[0],
                    name=row[1],
                    amount=row[2],
                    interval=Interval(value=row[3]),
                    multiplier=row[4],
                    user=user,
                    category=category,
                    active=bool(row[7])))
        return subscriptions
    
    def update(self, entity: Subscription) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        
        cursor.execute(
            """UPDATE subscriptions SET name = ?, amount = ?, interval = ?, multiplier = ?,
            user_uid = ?, category_uid = ?, active = ? WHERE uid = ?""",
            (entity.name, entity.amount, entity.interval.value, entity.multiplier,
             entity.user.uid, entity.category.uid, 1 if entity.active else 0, entity.uid))
        affected: int = cursor.rowcount
        connection.commit()
        connection.close()
        return affected > 0
    
    def delete(self, uid: str) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("DELETE FROM subscriptions WHERE uid = ?", (uid,))
        affected: int = cursor.rowcount
        connection.commit()
        connection.close()
        return affected > 0

# Made with Bob
