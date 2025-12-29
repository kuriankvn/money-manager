from dataclasses import dataclass
from enum import StrEnum
from core.models.user import User
from core.models.category import Category
from core.utils import epoch_to_datetime


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class Transaction:
    uid: str
    name: str
    amount: float
    datetime: float
    type: TransactionType
    user: User
    category: Category
    
    def __str__(self) -> str:
        return f"{self.name} - {self.amount} - {epoch_to_datetime(epoch=self.datetime)} - {self.type} - {self.user} - {self.category}"
