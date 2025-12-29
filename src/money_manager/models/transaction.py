from dataclasses import dataclass
from enum import StrEnum
from money_manager.models.user import User
from money_manager.models.category import Category
from money_manager.utils import epoch_to_datetime


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

# Made with Bob
