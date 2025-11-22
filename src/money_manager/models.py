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
    type: TransactionType
    name: str
    parent_category: Optional["Category"]


@dataclass
class Transaction:
    uid: str
    user_uid: str
    amount: float
    date_time: float
    type: TransactionType
    category: Category
