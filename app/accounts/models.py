"""Account and Transaction models."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal


AccountType = Literal["BANK", "CARD"]
TransactionType = Literal["INCOME", "EXPENSE"]


@dataclass
class Account:
    """Represents a bank account or card."""
    id: str
    name: str
    type: AccountType
    institution: str
    notes: str | None = None


@dataclass
class Transaction:
    """Represents an actual money movement."""
    id: str
    account_id: str
    date: date
    amount: Decimal  # Negative for expense, positive for income
    description: str
    category: str
    notes: str | None = None
    
    @property
    def is_income(self) -> bool:
        """Check if transaction is income."""
        return self.amount > 0
    
    @property
    def is_expense(self) -> bool:
        """Check if transaction is expense."""
        return self.amount < 0

