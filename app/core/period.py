"""Period parsing and handling for monthly/yearly periods."""
from datetime import date
from typing import Literal
import re


PeriodType = Literal["MONTHLY", "YEARLY"]


class Period:
    """Represents a time period (YYYY-MM or YYYY)."""
    
    def __init__(self, year: int, month: int | None = None):
        self.year = year
        self.month = month
    
    @classmethod
    def from_string(cls, period_str: str) -> "Period":
        """Parse period string (YYYY-MM or YYYY)."""
        if re.match(r"^\d{4}-\d{2}$", period_str):
            year, month = period_str.split("-")
            return cls(int(year), int(month))
        elif re.match(r"^\d{4}$", period_str):
            return cls(int(period_str))
        else:
            raise ValueError(f"Invalid period format: {period_str}")
    
    @classmethod
    def from_date(cls, dt: date, period_type: PeriodType) -> "Period":
        """Create period from date."""
        if period_type == "MONTHLY":
            return cls(dt.year, dt.month)
        else:
            return cls(dt.year)
    
    def to_string(self) -> str:
        """Convert to string representation."""
        if self.month:
            return f"{self.year}-{self.month:02d}"
        return str(self.year)
    
    def is_monthly(self) -> bool:
        """Check if this is a monthly period."""
        return self.month is not None
    
    def is_yearly(self) -> bool:
        """Check if this is a yearly period."""
        return self.month is None
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"Period({self.to_string()})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Period):
            return False
        return self.year == other.year and self.month == other.month
    
    def __hash__(self) -> int:
        return hash((self.year, self.month))

