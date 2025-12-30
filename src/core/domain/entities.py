from dataclasses import dataclass
from enum import StrEnum


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class Interval(StrEnum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class User:
    uid: str
    name: str


@dataclass
class Category:
    uid: str
    name: str
    user: User


@dataclass
class Transaction:
    uid: str
    name: str
    amount: float
    date: float
    type: TransactionType
    user: User
    category: Category


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

# Made with Bob
