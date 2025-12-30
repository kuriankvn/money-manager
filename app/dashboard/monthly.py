"""Monthly dashboard view."""
from datetime import date
from decimal import Decimal
from typing import List, Dict

from app.accounts.repository import TransactionRepository
from app.subscriptions.repository import SubscriptionInstanceRepository
from app.core.period import Period
from app.core.dates import get_month_start, get_month_end
from app.core.money import to_decimal


class MonthlyDashboard:
    """Provides monthly overview across domains."""
    
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        subscription_instance_repo: SubscriptionInstanceRepository
    ):
        self.transaction_repo = transaction_repo
        self.subscription_instance_repo = subscription_instance_repo
    
    def get_monthly_overview(self, year: int, month: int) -> Dict:
        """Get complete monthly overview."""
        period = Period(year, month)
        start_date = date(year, month, 1)
        end_date = get_month_end(start_date)
        
        # Get transactions for the month
        transactions = self.transaction_repo.get_by_date_range(start_date, end_date)
        
        # Calculate transaction totals
        income = to_decimal(sum(t.amount for t in transactions if t.is_income))
        expenses = to_decimal(abs(sum(t.amount for t in transactions if t.is_expense)))
        net = to_decimal(income - expenses)
        
        # Get subscription instances for the month
        instances = self.subscription_instance_repo.get_by_period(period.to_string())
        
        # Calculate subscription totals
        total_due = to_decimal(sum(i.amount for i in instances))
        paid_instances = [i for i in instances if i.is_paid]
        total_paid = to_decimal(sum(i.amount for i in paid_instances))
        unpaid_count = len([i for i in instances if i.is_due])
        
        return {
            "period": period.to_string(),
            "transactions": {
                "income": income,
                "expenses": expenses,
                "net": net,
                "count": len(transactions)
            },
            "subscriptions": {
                "total_due": total_due,
                "total_paid": total_paid,
                "unpaid_count": unpaid_count,
                "total_instances": len(instances)
            }
        }
    
    def get_monthly_transactions_by_category(self, year: int, month: int) -> Dict[str, Decimal]:
        """Get transaction breakdown by category for a month."""
        start_date = date(year, month, 1)
        end_date = get_month_end(start_date)
        
        transactions = self.transaction_repo.get_by_date_range(start_date, end_date)
        
        category_totals: Dict[str, Decimal] = {}
        for transaction in transactions:
            category = transaction.category
            if category not in category_totals:
                category_totals[category] = Decimal("0")
            category_totals[category] += abs(transaction.amount)
        
        return {k: to_decimal(v) for k, v in category_totals.items()}
    
    def get_monthly_subscription_status(self, year: int, month: int) -> Dict:
        """Get detailed subscription status for a month."""
        period = Period(year, month)
        instances = self.subscription_instance_repo.get_by_period(period.to_string())
        
        paid = [i for i in instances if i.is_paid]
        due = [i for i in instances if i.is_due]
        
        return {
            "period": period.to_string(),
            "paid": {
                "count": len(paid),
                "total": to_decimal(sum(i.amount for i in paid)),
                "instances": paid
            },
            "due": {
                "count": len(due),
                "total": to_decimal(sum(i.amount for i in due)),
                "instances": due
            }
        }

