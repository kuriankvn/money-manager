from dataclasses import dataclass
from enum import StrEnum
from core.models.user import User
from core.models.category import Category


class Interval(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class Subscription:
    uid: str
    name: str
    amount: float
    interval: Interval
    multiplier: int
    user: User
    category: Category
    active: bool = True
    
    def __str__(self) -> str:
        return f"{self.name} - {self.amount} - {self.interval} - {self.multiplier} - {self.user} - {self.category} - {self.active}"

