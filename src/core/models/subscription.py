from dataclasses import dataclass
from enum import StrEnum
from core.models import User, Category


class Interval(StrEnum):
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
    active: bool
