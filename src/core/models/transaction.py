from dataclasses import dataclass
from enum import StrEnum
from core.models import User, Category


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class Transaction:
    uid: str
    name: str
    amount: float
    date: float
    type: TransactionType
    user: User
    category: Category
