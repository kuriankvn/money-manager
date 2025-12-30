from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from core.models import User, Subscription


@dataclass
class Payment:
    uid: str
    amount: float
    due_date: datetime
    user: User
    subscription: Subscription
    paid_date: Optional[datetime] = None
    paid: bool = False
