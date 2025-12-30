from datetime import date
from decimal import Decimal

from app.subscriptions.models import Subscription, SubscriptionInstance
from app.subscriptions.repository import (
    SubscriptionInstanceRepository,
    SubscriptionRepository,
)


def test_subscription_repository_create_and_get(db_conn) -> None:
    repo=SubscriptionRepository(conn=db_conn)
    
    subscription=Subscription(
        id="sub-1",
        name="Netflix",
        type="OTHER",
        frequency="MONTHLY",
        due_day=15,
        expected_amount=Decimal(value="199.00"),
        start_date=date(year=2024, month=1, day=1),
        notes="Streaming service"
    )
    
    repo.create(subscription=subscription)
    retrieved: list[Subscription] = repo.get_by_id(subscription_id="sub-1")
    
    assert retrieved is not None
    assert retrieved.name == "Netflix"
    assert retrieved.frequency == "MONTHLY"
    assert retrieved.due_day == 15


def test_subscription_repository_get_active(db_conn) -> None:
    repo=SubscriptionRepository(conn=db_conn)
    
    active_sub=Subscription(
        id="sub-1",
        name="Active",
        type="BILL",
        frequency="MONTHLY",
        due_day=10,
        expected_amount=Decimal(value="100.00"),
        start_date=date(year=2024, month=1, day=1)
    )
    
    ended_sub=Subscription(
        id="sub-2",
        name="Ended",
        type="BILL",
        frequency="MONTHLY",
        due_day=10,
        expected_amount=Decimal(value="100.00"),
        start_date=date(year=2023, month=1, day=1),
        end_date=date(year=2023, month=12, day=31)
    )
    
    repo.create(subscription=active_sub)
    repo.create(subscription=ended_sub)
    
    active_subs: list[Subscription] = repo.get_active()
    
    assert len(active_subs) == 1
    assert active_subs[0].name == "Active"


def test_subscription_instance_repository_create_and_get(db_conn) -> None:
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
    retrieved: list[Subscription] = inst_repo.get_by_id(instance_id="inst-1")
    
    assert retrieved is not None
    assert retrieved.period == "2024-01"
    assert retrieved.status == "DUE"


def test_subscription_instance_repository_get_by_period(db_conn) -> None:
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
    
    inst1=SubscriptionInstance(
        id="inst-1",
        subscription_id="sub-1",
        period="2024-01",
        due_date=date(year=2024, month=1, day=15),
        amount=Decimal(value="199.00"),
        status="DUE"
    )
    
    inst2=SubscriptionInstance(
        id="inst-2",
        subscription_id="sub-1",
        period="2024-02",
        due_date=date(year=2024, month=2, day=15),
        amount=Decimal(value="199.00"),
        status="DUE"
    )
    
    inst_repo.create(instance=inst1)
    inst_repo.create(instance=inst2)
    
    instances: list[Subscription] = inst_repo.get_by_period(period="2024-01")
    
    assert len(instances) == 1
    assert instances[0].period == "2024-01"


def test_subscription_instance_repository_get_due_instances(db_conn) -> None:
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
    
    due_inst=SubscriptionInstance(
        id="inst-1",
        subscription_id="sub-1",
        period="2024-01",
        due_date=date(year=2024, month=1, day=15),
        amount=Decimal(value="199.00"),
        status="DUE"
    )
    
    paid_inst=SubscriptionInstance(
        id="inst-2",
        subscription_id="sub-1",
        period="2024-02",
        due_date=date(year=2024, month=2, day=15),
        amount=Decimal(value="199.00"),
        status="PAID",
        paid_date=date(year=2024, month=2, day=15)
    )
    
    inst_repo.create(instance=due_inst)
    inst_repo.create(instance=paid_inst)
    
    due_instances: list[Subscription] = inst_repo.get_due_instances()
    
    assert len(due_instances) == 1
    assert due_instances[0].status == "DUE"

# Made with Bob



