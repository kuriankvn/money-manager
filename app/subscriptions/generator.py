"""Subscription instance generator."""
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List

from app.subscriptions.models import Subscription, SubscriptionInstance, Frequency
from app.core.period import Period
from app.utils.ids import generate_id


class SubscriptionInstanceGenerator:
    """Generates subscription instances ahead of time."""
    
    def generate_instances(
        self,
        subscription: Subscription,
        months_ahead: int = 12
    ) -> List[SubscriptionInstance]:
        """Generate instances for the next N months."""
        instances: List[SubscriptionInstance] = []
        current_date = date.today()
        end_date = current_date + relativedelta(months=months_ahead)
        
        # Start from subscription start date or current month, whichever is later
        if subscription.start_date > current_date:
            generation_start = subscription.start_date
        else:
            generation_start = current_date.replace(day=1)
        
        if subscription.frequency == "MONTHLY":
            instances = self._generate_monthly_instances(
                subscription,
                generation_start,
                end_date
            )
        else:  # YEARLY
            instances = self._generate_yearly_instances(
                subscription,
                generation_start,
                end_date
            )
        
        return instances
    
    def _generate_monthly_instances(
        self,
        subscription: Subscription,
        start_date: date,
        end_date: date
    ) -> List[SubscriptionInstance]:
        """Generate monthly instances."""
        instances: List[SubscriptionInstance] = []
        current = start_date.replace(day=1)
        
        while current <= end_date:
            # Check if subscription has ended
            if subscription.end_date and current > subscription.end_date:
                break
            
            # Calculate due date for this month
            due_date = self._get_due_date_for_month(current, subscription.due_day)
            
            # Skip if due date is before subscription start
            if due_date < subscription.start_date:
                current = current + relativedelta(months=1)
                continue
            
            period = Period.from_date(due_date, "MONTHLY")
            
            instance = SubscriptionInstance(
                id=generate_id(),
                subscription_id=subscription.id,
                period=period.to_string(),
                due_date=due_date,
                amount=subscription.expected_amount,
                status="DUE"
            )
            instances.append(instance)
            
            current = current + relativedelta(months=1)
        
        return instances
    
    def _generate_yearly_instances(
        self,
        subscription: Subscription,
        start_date: date,
        end_date: date
    ) -> List[SubscriptionInstance]:
        """Generate yearly instances."""
        instances: List[SubscriptionInstance] = []
        current_year = start_date.year
        end_year = end_date.year
        
        while current_year <= end_year:
            # Check if subscription has ended
            if subscription.end_date and date(current_year, 12, 31) > subscription.end_date:
                break
            
            # Use subscription start date's month for yearly subscriptions
            due_month = subscription.start_date.month
            due_date = self._get_due_date_for_month(
                date(current_year, due_month, 1),
                subscription.due_day
            )
            
            # Skip if due date is before subscription start
            if due_date < subscription.start_date:
                current_year += 1
                continue
            
            # Skip if due date is after end date
            if due_date > end_date:
                break
            
            period = Period.from_date(due_date, "YEARLY")
            
            instance = SubscriptionInstance(
                id=generate_id(),
                subscription_id=subscription.id,
                period=period.to_string(),
                due_date=due_date,
                amount=subscription.expected_amount,
                status="DUE"
            )
            instances.append(instance)
            
            current_year += 1
        
        return instances
    
    def _get_due_date_for_month(self, month_start: date, due_day: int) -> date:
        """Get the due date for a given month, handling month-end edge cases."""
        year = month_start.year
        month = month_start.month
        
        # Get last day of month
        if month == 12:
            last_day = 31
        else:
            next_month = date(year, month + 1, 1)
            last_day = (next_month - timedelta(days=1)).day
        
        # Use the smaller of due_day and last_day
        actual_day = min(due_day, last_day)
        
        return date(year, month, actual_day)

