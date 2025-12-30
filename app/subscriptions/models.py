"""Subscription and SubscriptionInstance models."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal, Optional


SubscriptionType = Literal["BILL", "INSURANCE", "OTHER"]
Frequency = Literal["MONTHLY", "YEARLY"]
InstanceStatus = Literal["DUE", "PAID"]


@dataclass
class Subscription:
    """Defines a recurring payment rule."""
    id: str
    name: str
    type: SubscriptionType
    frequency: Frequency
    due_day: int  # Day of month (1-31)
    expected_amount: Decimal
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None


@dataclass
class SubscriptionInstance:
    """Represents one concrete occurrence of a subscription."""
    id: str
    subscription_id: str
    period: str  # YYYY-MM or YYYY
    due_date: date
    amount: Decimal
    status: InstanceStatus
    paid_date: Optional[date] = None
    
    @property
    def is_paid(self) -> bool:
        """Check if instance is paid."""
        return self.status == "PAID"
    
    @property
    def is_due(self) -> bool:
        """Check if instance is due."""
        return self.status == "DUE"

