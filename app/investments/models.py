"""Investment models."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal, Optional


InvestmentType = Literal["MF", "STOCK", "FD", "GOLD"]


@dataclass
class Investment:
    """Represents an investment asset."""
    id: str
    name: str
    provider: str
    type: InvestmentType
    notes: Optional[str] = None


@dataclass
class InvestmentContribution:
    """Represents money invested or redeemed."""
    id: str
    investment_id: str
    date: date
    amount: Decimal  # Positive for investment, negative for redemption
    notes: Optional[str] = None
    
    @property
    def is_investment(self) -> bool:
        """Check if this is an investment (not redemption)."""
        return self.amount > 0
    
    @property
    def is_redemption(self) -> bool:
        """Check if this is a redemption."""
        return self.amount < 0


@dataclass
class InvestmentValueSnapshot:
    """Represents the value of an investment at a point in time."""
    id: str
    investment_id: str
    date: date
    current_value: Decimal

