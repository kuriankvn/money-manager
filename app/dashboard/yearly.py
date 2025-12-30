"""Yearly dashboard view."""
from datetime import date
from decimal import Decimal
from typing import Dict, List

from app.accounts.repository import TransactionRepository
from app.subscriptions.repository import SubscriptionInstanceRepository
from app.core.period import Period
from app.core.dates import get_year_start, get_year_end
from app.core.money import to_decimal


class YearlyDashboard:
    """Provides yearly overview across domains."""
    
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        subscription_instance_repo: SubscriptionInstanceRepository
    ):
        self.transaction_repo = transaction_repo
        self.subscription_instance_repo = subscription_instance_repo
    
    def get_yearly_overview(self, year: int) -> Dict:
        """Get complete yearly overview."""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        # Get transactions for the year
        transactions = self.transaction_repo.get_by_date_range(start_date, end_date)
        
        # Calculate transaction totals
        income = to_decimal(sum(t.amount for t in transactions if t.is_income))
        expenses = to_decimal(abs(sum(t.amount for t in transactions if t.is_expense)))
        net = to_decimal(income - expenses)
        
        # Get monthly breakdown
        monthly_data = self._get_monthly_breakdown(year)
        
        return {
            "year": year,
            "transactions": {
                "income": income,
                "expenses": expenses,
                "net": net,
                "count": len(transactions)
            },
            "monthly_breakdown": monthly_data
        }
    
    def _get_monthly_breakdown(self, year: int) -> List[Dict]:
        """Get month-by-month breakdown for the year."""
        monthly_data = []
        
        for month in range(1, 13):
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year, 12, 31)
            else:
                end_date = date(year, month + 1, 1)
                from datetime import timedelta
                end_date = end_date - timedelta(days=1)
            
            transactions = self.transaction_repo.get_by_date_range(start_date, end_date)
            
            income = to_decimal(sum(t.amount for t in transactions if t.is_income))
            expenses = to_decimal(abs(sum(t.amount for t in transactions if t.is_expense)))
            
            period = Period(year, month)
            instances = self.subscription_instance_repo.get_by_period(period.to_string())
            subscription_total = to_decimal(sum(i.amount for i in instances if i.is_paid))
            
            monthly_data.append({
                "month": month,
                "period": period.to_string(),
                "income": income,
                "expenses": expenses,
                "net": to_decimal(income - expenses),
                "subscriptions_paid": subscription_total
            })
        
        return monthly_data
    
    def get_yearly_category_summary(self, year: int) -> Dict[str, Decimal]:
        """Get category-wise spending for the year."""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        transactions = self.transaction_repo.get_by_date_range(start_date, end_date)
        
        category_totals: Dict[str, Decimal] = {}
        for transaction in transactions:
            category = transaction.category
            if category not in category_totals:
                category_totals[category] = Decimal("0")
            category_totals[category] += abs(transaction.amount)
        
        return {k: to_decimal(v) for k, v in category_totals.items()}
    
    def get_yearly_subscription_summary(self, year: int) -> Dict:
        """Get yearly subscription summary."""
        total_paid = Decimal("0")
        total_due = Decimal("0")
        
        for month in range(1, 13):
            period = Period(year, month)
            instances = self.subscription_instance_repo.get_by_period(period.to_string())
            
            for instance in instances:
                if instance.is_paid:
                    total_paid += instance.amount
                else:
                    total_due += instance.amount
        
        return {
            "year": year,
            "total_paid": to_decimal(total_paid),
            "total_due": to_decimal(total_due),
            "total": to_decimal(total_paid + total_due)
        }

