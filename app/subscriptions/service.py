"""Subscription service layer."""
from datetime import date
from decimal import Decimal
from typing import List, Optional

from app.core.money import to_decimal
from app.subscriptions.generator import SubscriptionInstanceGenerator
from app.subscriptions.models import (
    Frequency,
    Subscription,
    SubscriptionInstance,
    SubscriptionType,
)
from app.subscriptions.repository import (
    SubscriptionInstanceRepository,
    SubscriptionRepository,
)
from app.utils.ids import generate_id


class SubscriptionService:
    """Service for subscription operations."""
    
    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        instance_repo: SubscriptionInstanceRepository,
        generator: SubscriptionInstanceGenerator
    ):
        self.subscription_repo = subscription_repo
        self.instance_repo = instance_repo
        self.generator = generator
    
    def create_subscription(
        self,
        name: str,
        subscription_type: SubscriptionType,
        frequency: Frequency,
        due_day: int,
        expected_amount: Decimal,
        start_date: date,
        end_date: Optional[date] = None,
        notes: Optional[str] = None,
        generate_instances: bool = True
    ) -> Subscription:
        """Create a new subscription and optionally generate instances."""
        subscription = Subscription(
            id=generate_id(),
            name=name,
            type=subscription_type,
            frequency=frequency,
            due_day=due_day,
            expected_amount=to_decimal(expected_amount),
            start_date=start_date,
            end_date=end_date,
            notes=notes
        )
        self.subscription_repo.create(subscription)
        
        if generate_instances:
            instances = self.generator.generate_instances(subscription)
            for instance in instances:
                self.instance_repo.create(instance)
        
        return subscription
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        return self.subscription_repo.get_by_id(subscription_id)
    
    def list_subscriptions(self) -> List[Subscription]:
        """List all subscriptions."""
        return self.subscription_repo.get_all()
    
    def list_active_subscriptions(self) -> List[Subscription]:
        """List active subscriptions."""
        return self.subscription_repo.get_active()
    
    def update_subscription(self, subscription: Subscription) -> None:
        """Update a subscription."""
        self.subscription_repo.update(subscription)
    
    def delete_subscription(self, subscription_id: str) -> None:
        """Delete a subscription and its instances."""
        self.instance_repo.delete_by_subscription(subscription_id)
        self.subscription_repo.delete(subscription_id)
    
    def regenerate_instances(self, subscription_id: str, months_ahead: int = 12) -> None:
        """Regenerate instances for a subscription."""
        subscription = self.subscription_repo.get_by_id(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        # Delete existing future instances
        self.instance_repo.delete_by_subscription(subscription_id)
        
        # Generate new instances
        instances = self.generator.generate_instances(subscription, months_ahead)
        for instance in instances:
            self.instance_repo.create(instance)


class SubscriptionInstanceService:
    """Service for subscription instance operations."""
    
    def __init__(self, repository: SubscriptionInstanceRepository):
        self.repository = repository
    
    def get_instance(self, instance_id: str) -> Optional[SubscriptionInstance]:
        """Get instance by ID."""
        return self.repository.get_by_id(instance_id)
    
    def list_instances_by_subscription(self, subscription_id: str) -> List[SubscriptionInstance]:
        """List all instances for a subscription."""
        return self.repository.get_by_subscription(subscription_id)
    
    def list_instances_by_period(self, period: str) -> List[SubscriptionInstance]:
        """List all instances for a period."""
        return self.repository.get_by_period(period)
    
    def list_due_instances(self) -> List[SubscriptionInstance]:
        """List all due (unpaid) instances."""
        return self.repository.get_due_instances()
    
    def mark_as_paid(self, instance_id: str, paid_date: date, actual_amount: Optional[Decimal] = None) -> None:
        """Mark an instance as paid."""
        instance = self.repository.get_by_id(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")
        
        instance.status = "PAID"
        instance.paid_date = paid_date
        if actual_amount is not None:
            instance.amount = to_decimal(actual_amount)
        
        self.repository.update(instance)
    
    def mark_as_due(self, instance_id: str) -> None:
        """Mark an instance as due (unpaid)."""
        instance = self.repository.get_by_id(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")
        
        instance.status = "DUE"
        instance.paid_date = None
        
        self.repository.update(instance)
    
    def update_instance(self, instance: SubscriptionInstance) -> None:
        """Update an instance."""
        self.repository.update(instance)
    
    def delete_instance(self, instance_id: str) -> None:
        """Delete an instance."""
        self.repository.delete(instance_id)

