from dataclasses import dataclass
from enum import Enum
from typing import Optional
from money_manager.utils import epoch_to_datetime


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class User:
    uid: str
    name: str
    
    def __str__(self) -> str:
        return self.name


@dataclass
class Category:
    uid: str
    name: str
    type: TransactionType
    
    def __str__(self) -> str:
        return f"{self.name} - {self.type.value}"


@dataclass
class Transaction:
    uid: str
    name: str
    amount: float
    datetime: float
    user: User
    category: Category
    
    def __str__(self) -> str:
        date_str: str = epoch_to_datetime(epoch=self.datetime)
        return f"{self.name} - ${self.amount:.2f} - {self.user.name} - {self.category.name} - {self.category.type.value} ({date_str})"
