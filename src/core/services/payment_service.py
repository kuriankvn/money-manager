from datetime import datetime
from typing import Optional
from core.models import Payment, Subscription
from core.repositories import PaymentRepository, SubscriptionRepository
from core.utils import generate_uid


class PaymentService:
    def __init__(self) -> None:
        self.payment_repo = PaymentRepository()
        self.subscription_repo = SubscriptionRepository()
    
    def generate_payments_for_month(self, month: int, year: int, user_uid: Optional[str] = None) -> dict[str, int]:
        """Generate payment notifications for subscriptions for a given month
        
        Rules:
        - Monthly subscriptions: Generate every month
        - Yearly subscriptions: Generate only in January
        """
        subscriptions: list[Subscription] = self.subscription_repo.get_all()
        
        # Filter active subscriptions and optionally by user
        active_subscriptions = [
            sub for sub in subscriptions
            if sub.active and (user_uid is None or sub.user.uid == user_uid)
        ]
        
        # Check if payments already exist for this month
        existing_payments = self.payment_repo.get_by_month_year(month, year, user_uid)
        existing_sub_uids = {payment.subscription.uid for payment in existing_payments}
        
        created_count = 0
        skipped_count = 0
        skipped_interval = 0
        
        # Generate due date (1st of the month)
        due_date = datetime(year, month, 1)
        
        for subscription in active_subscriptions:
            # Skip if payment already exists for this subscription in this month
            if subscription.uid in existing_sub_uids:
                skipped_count += 1
                continue
            
            # Check subscription interval
            if subscription.interval.value == "yearly" and month != 1:
                # Yearly subscriptions only generate in January
                skipped_interval += 1
                continue
            
            # Create payment notification
            payment = Payment(
                uid=generate_uid(),
                amount=subscription.amount,
                due_date=due_date,
                user=subscription.user,
                subscription=subscription,
                paid_date=None,
                paid=False
            )
            
            self.payment_repo.create(entity=payment)
            created_count += 1
        
        return {
            "created": created_count,
            "skipped": skipped_count,
            "skipped_interval": skipped_interval,
            "total_active_subscriptions": len(active_subscriptions)
        }
    
    def mark_as_paid(self, payment_uid: str, paid_date: Optional[datetime] = None) -> bool:
        """Mark a payment as paid"""
        payment = self.payment_repo.get_by_id(uid=payment_uid)
        if not payment:
            return False
        
        # Use provided date or current datetime
        payment.paid_date = paid_date if paid_date else datetime.now()
        payment.paid = True
        
        return self.payment_repo.update(entity=payment)
    
    def get_payments_by_month(self, month: int, year: int, user_uid: Optional[str] = None) -> list[Payment]:
        """Get all payments for a specific month and year"""
        return self.payment_repo.get_by_month_year(month, year, user_uid)
    
    def get_payment_statistics(self, month: int, year: int, user_uid: Optional[str] = None) -> dict[str, float | int]:
        """Calculate payment statistics for a given month"""
        payments = self.get_payments_by_month(month, year, user_uid)
        
        total_due = sum(payment.amount for payment in payments)
        paid_count = sum(1 for payment in payments if payment.paid)
        pending_count = sum(1 for payment in payments if not payment.paid)
        total_paid = sum(payment.amount for payment in payments if payment.paid)
        total_pending = sum(payment.amount for payment in payments if not payment.paid)
        
        # Calculate overdue (payments not paid and due date has passed)
        now = datetime.now()
        overdue_count = sum(
            1 for payment in payments 
            if not payment.paid and payment.due_date < now
        )
        
        return {
            "total_due": total_due,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "paid_count": paid_count,
            "pending_count": pending_count,
            "overdue_count": overdue_count,
            "total_count": len(payments)
        }

# Made with Bob
