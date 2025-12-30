from typing import Any
from core.repositories.base import BaseRepository
from core.domain import Subscription, SubscriptionInstance
from core.domain.base import Frequency, SubscriptionStatus, SubscriptionInstanceStatus


class SubscriptionRepository(BaseRepository[Subscription]):
    @property
    def table_name(self) -> str:
        return "subscriptions"
    
    @property
    def columns(self) -> list[str]:
        return ["name", "amount", "frequency", "interval", "due_day", "due_month", "status"]
    
    def _entity_to_values(self, entity: Subscription) -> tuple[Any, ...]:
        return (entity.uid, entity.name, entity.amount, entity.frequency.value,
                entity.interval, entity.due_day, entity.due_month, entity.status.value)
    
    def _row_to_entity(self, row: tuple[Any, ...]) -> Subscription:
        return Subscription(
            uid=row[0],
            name=row[1],
            amount=row[2],
            frequency=Frequency(value=row[3]),
            interval=row[4],
            due_day=row[5],
            due_month=row[6],
            status=SubscriptionStatus(value=row[7]))


class SubscriptionInstanceRepository(BaseRepository[SubscriptionInstance]):
    @property
    def table_name(self) -> str:
        return "subscription_instances"
    
    @property
    def columns(self) -> list[str]:
        return ["subscription_id", "amount", "due_date", "transaction_id", "status"]
    
    def _entity_to_values(self, entity: SubscriptionInstance) -> tuple[Any, ...]:
        return (entity.uid, entity.subscription_id, entity.amount, entity.due_date,
                entity.transaction_id, entity.status.value)
    
    def _row_to_entity(self, row: tuple[Any, ...]) -> SubscriptionInstance:
        return SubscriptionInstance(
            uid=row[0],
            subscription_id=row[1],
            amount=row[2],
            due_date=row[3],
            transaction_id=row[4],
            status=SubscriptionInstanceStatus(value=row[5]))

# Made with Bob
