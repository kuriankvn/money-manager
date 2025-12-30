"""Subscription and SubscriptionInstance repository."""
import sqlite3
from datetime import date
from typing import List, Optional

from app.core.money import to_decimal
from app.subscriptions.models import (
    Frequency,
    InstanceStatus,
    Subscription,
    SubscriptionInstance,
    SubscriptionType,
)


class SubscriptionRepository:
    """Repository for Subscription operations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
    
    def create(self, subscription: Subscription) -> None:
        """Create a new subscription."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO subscriptions (id, name, type, frequency, due_day, expected_amount, start_date, end_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subscription.id,
                subscription.name,
                subscription.type,
                subscription.frequency,
                subscription.due_day,
                str(subscription.expected_amount),
                subscription.start_date.isoformat(),
                subscription.end_date.isoformat() if subscription.end_date else None,
                subscription.notes
            )
        )
        self.conn.commit()
    
    def get_by_id(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM subscriptions WHERE id = ?", (subscription_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_subscription(row)
    
    def get_all(self) -> List[Subscription]:
        """Get all subscriptions."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM subscriptions ORDER BY name")
        return [self._row_to_subscription(row) for row in cursor.fetchall()]
    
    def get_active(self) -> List[Subscription]:
        """Get active subscriptions (no end_date or end_date in future)."""
        cursor = self.conn.cursor()
        today = date.today().isoformat()
        cursor.execute(
            """
            SELECT * FROM subscriptions
            WHERE end_date IS NULL OR end_date >= ?
            ORDER BY name
            """,
            (today,)
        )
        return [self._row_to_subscription(row) for row in cursor.fetchall()]
    
    def update(self, subscription: Subscription) -> None:
        """Update a subscription."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE subscriptions
            SET name = ?, type = ?, frequency = ?, due_day = ?, expected_amount = ?,
                start_date = ?, end_date = ?, notes = ?
            WHERE id = ?
            """,
            (
                subscription.name,
                subscription.type,
                subscription.frequency,
                subscription.due_day,
                str(subscription.expected_amount),
                subscription.start_date.isoformat(),
                subscription.end_date.isoformat() if subscription.end_date else None,
                subscription.notes,
                subscription.id
            )
        )
        self.conn.commit()
    
    def delete(self, subscription_id: str) -> None:
        """Delete a subscription."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM subscriptions WHERE id = ?", (subscription_id,))
        self.conn.commit()
    
    def _row_to_subscription(self, row: sqlite3.Row) -> Subscription:
        """Convert database row to Subscription."""
        return Subscription(
            id=row["id"],
            name=row["name"],
            type=row["type"],
            frequency=row["frequency"],
            due_day=row["due_day"],
            expected_amount=to_decimal(row["expected_amount"]),
            start_date=date.fromisoformat(row["start_date"]),
            end_date=date.fromisoformat(row["end_date"]) if row["end_date"] else None,
            notes=row["notes"]
        )


class SubscriptionInstanceRepository:
    """Repository for SubscriptionInstance operations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
    
    def create(self, instance: SubscriptionInstance) -> None:
        """Create a new subscription instance."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO subscription_instances (id, subscription_id, period, due_date, amount, status, paid_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                instance.id,
                instance.subscription_id,
                instance.period,
                instance.due_date.isoformat(),
                str(instance.amount),
                instance.status,
                instance.paid_date.isoformat() if instance.paid_date else None
            )
        )
        self.conn.commit()
    
    def get_by_id(self, instance_id: str) -> Optional[SubscriptionInstance]:
        """Get instance by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM subscription_instances WHERE id = ?", (instance_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_instance(row)
    
    def get_by_subscription(self, subscription_id: str) -> List[SubscriptionInstance]:
        """Get all instances for a subscription."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM subscription_instances
            WHERE subscription_id = ?
            ORDER BY due_date DESC
            """,
            (subscription_id,)
        )
        return [self._row_to_instance(row) for row in cursor.fetchall()]
    
    def get_by_period(self, period: str) -> List[SubscriptionInstance]:
        """Get all instances for a period."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM subscription_instances
            WHERE period = ?
            ORDER BY due_date
            """,
            (period,)
        )
        return [self._row_to_instance(row) for row in cursor.fetchall()]
    
    def get_due_instances(self) -> List[SubscriptionInstance]:
        """Get all due (unpaid) instances."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM subscription_instances
            WHERE status = 'DUE'
            ORDER BY due_date
            """
        )
        return [self._row_to_instance(row) for row in cursor.fetchall()]
    
    def update(self, instance: SubscriptionInstance) -> None:
        """Update a subscription instance."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE subscription_instances
            SET subscription_id = ?, period = ?, due_date = ?, amount = ?, status = ?, paid_date = ?
            WHERE id = ?
            """,
            (
                instance.subscription_id,
                instance.period,
                instance.due_date.isoformat(),
                str(instance.amount),
                instance.status,
                instance.paid_date.isoformat() if instance.paid_date else None,
                instance.id
            )
        )
        self.conn.commit()
    
    def delete(self, instance_id: str) -> None:
        """Delete a subscription instance."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM subscription_instances WHERE id = ?", (instance_id,))
        self.conn.commit()
    
    def delete_by_subscription(self, subscription_id: str) -> None:
        """Delete all instances for a subscription."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM subscription_instances WHERE subscription_id = ?", (subscription_id,))
        self.conn.commit()
    
    def _row_to_instance(self, row: sqlite3.Row) -> SubscriptionInstance:
        """Convert database row to SubscriptionInstance."""
        return SubscriptionInstance(
            id=row["id"],
            subscription_id=row["subscription_id"],
            period=row["period"],
            due_date=date.fromisoformat(row["due_date"]),
            amount=to_decimal(row["amount"]),
            status=row["status"],
            paid_date=date.fromisoformat(row["paid_date"]) if row["paid_date"] else None
        )

