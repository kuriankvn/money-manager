import sqlite3
from typing import Any, Optional
from datetime import datetime
from core.database import get_connection
from core.repositories import IRepository, UserRepository, SubscriptionRepository
from core.models import User, Subscription, Payment
from core.exceptions import DuplicateEntityError


class PaymentRepository(IRepository[Payment]):
    def __init__(self) -> None:
        self.user_repo: UserRepository = UserRepository()
        self.subscription_repo: SubscriptionRepository = SubscriptionRepository()
    
    def create(self, entity: Payment) -> str:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        try:
            cursor.execute(
                """INSERT INTO subscription_payments (uid, amount, due_date, user_uid, subscription_uid, paid_date, paid)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (entity.uid, entity.amount, entity.due_date.timestamp(),
                 entity.user.uid, entity.subscription.uid,
                 entity.paid_date.timestamp() if entity.paid_date else None,
                 1 if entity.paid else 0))
            connection.commit()
            return entity.uid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntityError(f"Payment already exists") from e
        finally:
            connection.close()
    
    def get_by_id(self, uid: str) -> Optional[Payment]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """SELECT uid, amount, due_date, user_uid, subscription_uid, paid_date, paid
            FROM subscription_payments WHERE uid = ?""",
            (uid,))
        row = cursor.fetchone()
        connection.close()
        
        if row:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[3])
            if not user:
                return None
            subscription: Optional[Subscription] = self.subscription_repo.get_by_id(uid=row[4])
            if not subscription:
                return None
            return Payment(
                uid=row[0],
                amount=row[1],
                due_date=datetime.fromtimestamp(row[2]),
                user=user,
                subscription=subscription,
                paid_date=datetime.fromtimestamp(row[5]) if row[5] else None,
                paid=bool(row[6]))
        return None
    
    def get_all(self) -> list[Payment]:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            """SELECT uid, amount, due_date, user_uid, subscription_uid, paid_date, paid
            FROM subscription_payments""")
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        payments: list[Payment] = []
        for row in rows:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[3])
            subscription: Optional[Subscription] = self.subscription_repo.get_by_id(uid=row[4])
            if user and subscription:
                payments.append(Payment(
                    uid=row[0],
                    amount=row[1],
                    due_date=datetime.fromtimestamp(row[2]),
                    user=user,
                    subscription=subscription,
                    paid_date=datetime.fromtimestamp(row[5]) if row[5] else None,
                    paid=bool(row[6])))
        return payments
    
    def update(self, entity: Payment) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        try:
            cursor.execute(
                """UPDATE subscription_payments SET amount = ?, due_date = ?, user_uid = ?,
                subscription_uid = ?, paid_date = ?, paid = ? WHERE uid = ?""",
                (entity.amount, entity.due_date.timestamp(), entity.user.uid,
                 entity.subscription.uid,
                 entity.paid_date.timestamp() if entity.paid_date else None,
                 1 if entity.paid else 0, entity.uid))
            affected: int = cursor.rowcount
            connection.commit()
            return affected > 0
        except sqlite3.IntegrityError as e:
            raise DuplicateEntityError(f"Payment update failed") from e
        finally:
            connection.close()
    
    def delete(self, uid: str) -> bool:
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute("DELETE FROM subscription_payments WHERE uid = ?", (uid,))
        affected: int = cursor.rowcount
        connection.commit()
        connection.close()
        return affected > 0
    
    def get_by_month_year(self, month: int, year: int, user_uid: Optional[str] = None) -> list[Payment]:
        """Get payments for a specific month and year, optionally filtered by user"""
        connection: sqlite3.Connection = get_connection()
        cursor: sqlite3.Cursor = connection.cursor()
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        if user_uid:
            cursor.execute(
                """SELECT uid, amount, due_date, user_uid, subscription_uid, paid_date, paid
                FROM subscription_payments 
                WHERE due_date >= ? AND due_date < ? AND user_uid = ?
                ORDER BY due_date""",
                (start_date.timestamp(), end_date.timestamp(), user_uid))
        else:
            cursor.execute(
                """SELECT uid, amount, due_date, user_uid, subscription_uid, paid_date, paid
                FROM subscription_payments 
                WHERE due_date >= ? AND due_date < ?
                ORDER BY due_date""",
                (start_date.timestamp(), end_date.timestamp()))
        
        rows: list[Any] = cursor.fetchall()
        connection.close()
        
        payments: list[Payment] = []
        for row in rows:
            user: Optional[User] = self.user_repo.get_by_id(uid=row[3])
            subscription: Optional[Subscription] = self.subscription_repo.get_by_id(uid=row[4])
            if user and subscription:
                payments.append(Payment(
                    uid=row[0],
                    amount=row[1],
                    due_date=datetime.fromtimestamp(row[2]),
                    user=user,
                    subscription=subscription,
                    paid_date=datetime.fromtimestamp(row[5]) if row[5] else None,
                    paid=bool(row[6])))
        return payments

# Made with Bob
