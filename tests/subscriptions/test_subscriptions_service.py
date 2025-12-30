from datetime import date
from decimal import Decimal

from app.subscriptions.generator import SubscriptionInstanceGenerator
from app.subscriptions.models import Subscription, SubscriptionInstance
from app.subscriptions.repository import (
    SubscriptionInstanceRepository,
    SubscriptionRepository,
)
from app.subscriptions.service import (
    SubscriptionInstanceService,
    SubscriptionService,
)


def test_subscription_service_create(db_conn) -> None:
    sub_repo=SubscriptionRepository(conn=db_conn)
    inst_repo=SubscriptionInstanceRepository(conn=db_conn)
    generator=SubscriptionInstanceGenerator()
    
    service=SubscriptionService(
        subscription_repo=sub_repo,
        instance_repo=inst_repo,
        generator=generator
    )
    
    subscription=service.create_subscription(
        name="Netflix",
        subscription_type="OTHER",
        frequency="MONTHLY",
        due_day=15,
        expected_amount=Decimal(value="199.00"),
        start_date=date(year=2024, month=1, day=1),
        generate_instances=False
    )
    
    assert subscription.id is not None
    assert subscription.name == "Netflix"
    
    retrieved: Subscription | None = sub_repo.get_by_id(subscription_id=subscription.id)
    assert retrieved is not None


def test_subscription_service_create_with_instances(db_conn) -> None:
    sub_repo=SubscriptionRepository(conn=db_conn)
    inst_repo=SubscriptionInstanceRepository(conn=db_conn)
    generator=SubscriptionInstanceGenerator()
    
    service=SubscriptionService(
        subscription_repo=sub_repo,
        instance_repo=inst_repo,
        generator=generator
    )
    
    subscription = service.create_subscription(
        name="Netflix",
        subscription_type="OTHER",
        frequency="MONTHLY",
        due_day=15,
        expected_amount=Decimal(value="199.00"),
        start_date=date(year=2024, month=1, day=1),
        generate_instances=True
    )
    
    instances: list[Subscription] = inst_repo.get_by_subscription(subscription_id=subscription.id)
    assert len(instances) > 0


def test_subscription_instance_service_mark_as_paid(db_conn) -> None:
    sub_repo=SubscriptionRepository(conn=db_conn)
    inst_repo=SubscriptionInstanceRepository(conn=db_conn)
    
    subscription=Subscription(
        id="sub-1",
        name="Netflix",
        type="OTHER",
        frequency="MONTHLY",
        due_day=15,
        expected_amount=Decimal(value="199.00"),
        start_date=date(year=2024, month=1, day=1)
    )
    sub_repo.create(subscription=subscription)
    
    instance=SubscriptionInstance(
        id="inst-1",
        subscription_id="sub-1",
        period="2024-01",
        due_date=date(year=2024, month=1, day=15),
        amount=Decimal(value="199.00"),
        status="DUE"
    )
    inst_repo.create(instance=instance)
    
    service=SubscriptionInstanceService(repository=inst_repo)
    service.mark_as_paid(
        instance_id="inst-1",
        paid_date=date(year=2024, month=1, day=15),
        actual_amount=Decimal(value="199.00")
    )
    
    updated: list[Subscription] = inst_repo.get_by_id(instance_id="inst-1")
    assert updated.status == "PAID"
    assert updated.paid_date == date(year=2024, month=1, day=15)


def test_subscription_instance_service_mark_as_due(db_conn) -> None:
    sub_repo=SubscriptionRepository(conn=db_conn)
    inst_repo=SubscriptionInstanceRepository(conn=db_conn)
    
    subscription=Subscription(
        id="sub-1",
        name="Netflix",
        type="OTHER",
        frequency="MONTHLY",
        due_day=15,
        expected_amount=Decimal(value="199.00"),
        start_date=date(year=2024, month=1, day=1)
    )
    sub_repo.create(subscription=subscription)
    
    instance=SubscriptionInstance(
        id="inst-1",
        subscription_id="sub-1",
        period="2024-01",
        due_date=date(year=2024, month=1, day=15),
        amount=Decimal(value="199.00"),
        status="PAID",
        paid_date=date(year=2024, month=1, day=15)
    )
    inst_repo.create(instance=instance)
    
    service=SubscriptionInstanceService(repository=inst_repo)
    service.mark_as_due(instance_id="inst-1")
    
    updated: list[Subscription] = inst_repo.get_by_id(instance_id="inst-1")
    assert updated.status == "DUE"
    assert updated.paid_date is None

# Made with Bob



