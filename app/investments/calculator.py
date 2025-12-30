"""Investment calculations."""
from decimal import Decimal
from typing import List, Optional

from app.investments.models import InvestmentContribution, InvestmentValueSnapshot
from app.core.money import to_decimal


class InvestmentCalculator:
    """Pure calculation functions for investments."""
    
    @staticmethod
    def calculate_total_invested(contributions: List[InvestmentContribution]) -> Decimal:
        """Calculate total amount invested (sum of all contributions)."""
        total = Decimal("0")
        for contribution in contributions:
            total += contribution.amount
        return to_decimal(total)
    
    @staticmethod
    def get_current_value(snapshots: List[InvestmentValueSnapshot]) -> Optional[Decimal]:
        """Get the most recent value from snapshots."""
        if not snapshots:
            return None
        
        # Snapshots should be sorted by date DESC
        latest = snapshots[0]
        return latest.current_value
    
    @staticmethod
    def calculate_gain_loss(
        total_invested: Decimal,
        current_value: Optional[Decimal]
    ) -> Optional[Decimal]:
        """Calculate gain/loss (current value - total invested)."""
        if current_value is None:
            return None
        return to_decimal(current_value - total_invested)
    
    @staticmethod
    def calculate_gain_loss_percentage(
        total_invested: Decimal,
        current_value: Optional[Decimal]
    ) -> Optional[Decimal]:
        """Calculate gain/loss percentage."""
        if current_value is None or total_invested == 0:
            return None
        
        gain_loss = current_value - total_invested
        percentage = (gain_loss / total_invested) * 100
        return to_decimal(percentage)
    
    @staticmethod
    def calculate_portfolio_summary(
        investments_data: List[tuple[Decimal, Optional[Decimal]]]
    ) -> dict:
        """
        Calculate portfolio-wide summary.
        
        Args:
            investments_data: List of (total_invested, current_value) tuples
        
        Returns:
            Dictionary with total_invested, total_current_value, total_gain_loss
        """
        total_invested = Decimal("0")
        total_current_value = Decimal("0")
        
        for invested, current in investments_data:
            total_invested += invested
            if current is not None:
                total_current_value += current
        
        total_gain_loss = total_current_value - total_invested if total_current_value else None
        
        return {
            "total_invested": to_decimal(total_invested),
            "total_current_value": to_decimal(total_current_value) if total_current_value else None,
            "total_gain_loss": to_decimal(total_gain_loss) if total_gain_loss is not None else None
        }

