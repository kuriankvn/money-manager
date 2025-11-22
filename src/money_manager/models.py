from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class User:
    uid: str
    name: str


@dataclass
class Category:
    uid: str
    name: str
    type: TransactionType


@dataclass
class Transaction:
    uid: str
    amount: float
    datetime: float
    user: User
    category: Category
