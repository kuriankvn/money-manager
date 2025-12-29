from dataclasses import dataclass
from enum import StrEnum
from money_manager.models.user import User
from money_manager.models.category import Category


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

# Made with Bob

