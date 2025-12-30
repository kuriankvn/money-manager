from datetime import date
from decimal import Decimal

from app.investments.models import (
    Investment,
    InvestmentContribution,
    InvestmentValueSnapshot,
)
from app.investments.repository import (
    InvestmentContributionRepository,
    InvestmentRepository,
    InvestmentValueSnapshotRepository,
)


def test_investment_repository_create_and_get(db_conn) -> None:
    repo=InvestmentRepository(conn=db_conn)
    
    investment=Investment(
        id="inv-1",
        name="HDFC Flexi Cap",
        provider="HDFC MF",
        type="MF",
        notes="Growth fund"
    )
    
    repo.create(investment=investment)
    retrieved: list[Investment] = repo.get_by_id(investment_id="inv-1")
    
    assert retrieved is not None
    assert retrieved.name == "HDFC Flexi Cap"
    assert retrieved.type == "MF"


def test_investment_repository_get_all(db_conn) -> None:
    repo=InvestmentRepository(conn=db_conn)
    
    inv1=Investment(id="inv-1", name="Fund 1", provider="HDFC", type="MF")
    inv2=Investment(id="inv-2", name="Stock 1", provider="Zerodha", type="STOCK")
    
    repo.create(investment=inv1)
    repo.create(investment=inv2)
    
    investments: list[Investment] = repo.get_all()
    
    assert len(investments) == 2


def test_contribution_repository_create_and_get(db_conn) -> None:
    inv_repo=InvestmentRepository(conn=db_conn)
    contrib_repo=InvestmentContributionRepository(conn=db_conn)
    
    investment=Investment(id="inv-1", name="Fund", provider="HDFC", type="MF")
    inv_repo.create(investment=investment)
    
    contribution=InvestmentContribution(
        id="contrib-1",
        investment_id="inv-1",
        date=date(year=2024, month=1, day=15),
        amount=Decimal(value="10000.00"),
        notes="Initial investment"
    )
    
    contrib_repo.create(contribution=contribution)
    retrieved: list[Investment] = contrib_repo.get_by_id(contribution_id="contrib-1")
    
    assert retrieved is not None
    assert retrieved.amount == Decimal(value="10000.00")
    assert retrieved.is_investment is True


def test_contribution_repository_get_by_investment(db_conn) -> None:
    inv_repo=InvestmentRepository(conn=db_conn)
    contrib_repo=InvestmentContributionRepository(conn=db_conn)
    
    investment=Investment(id="inv-1", name="Fund", provider="HDFC", type="MF")
    inv_repo.create(investment=investment)
    
    contrib1=InvestmentContribution(
        id="contrib-1",
        investment_id="inv-1",
        date=date(year=2024, month=1, day=15),
        amount=Decimal(value="10000.00")
    )
    
    contrib2=InvestmentContribution(
        id="contrib-2",
        investment_id="inv-1",
        date=date(year=2024, month=2, day=15),
        amount=Decimal(value="5000.00")
    )
    
    contrib_repo.create(contribution=contrib1)
    contrib_repo.create(contribution=contrib2)
    
    contributions: list[Investment] = contrib_repo.get_by_investment(investment_id="inv-1")
    
    assert len(contributions) == 2


def test_snapshot_repository_create_and_get(db_conn) -> None:
    inv_repo=InvestmentRepository(conn=db_conn)
    snap_repo=InvestmentValueSnapshotRepository(conn=db_conn)
    
    investment=Investment(id="inv-1", name="Fund", provider="HDFC", type="MF")
    inv_repo.create(investment=investment)
    
    snapshot=InvestmentValueSnapshot(
        id="snap-1",
        investment_id="inv-1",
        date=date(year=2024, month=1, day=31),
        current_value=Decimal(value="11000.00")
    )
    
    snap_repo.create(snapshot=snapshot)
    retrieved: list[Investment] = snap_repo.get_by_id(snapshot_id="snap-1")
    
    assert retrieved is not None
    assert retrieved.current_value == Decimal(value="11000.00")


def test_snapshot_repository_get_latest(db_conn) -> None:
    inv_repo=InvestmentRepository(conn=db_conn)
    snap_repo=InvestmentValueSnapshotRepository(conn=db_conn)
    
    investment=Investment(id="inv-1", name="Fund", provider="HDFC", type="MF")
    inv_repo.create(investment=investment)
    
    snap1=InvestmentValueSnapshot(
        id="snap-1",
        investment_id="inv-1",
        date=date(year=2024, month=1, day=31),
        current_value=Decimal(value="11000.00")
    )
    
    snap2=InvestmentValueSnapshot(
        id="snap-2",
        investment_id="inv-1",
        date=date(year=2024, month=2, day=29),
        current_value=Decimal(value="12000.00")
    )
    
    snap_repo.create(snapshot=snap1)
    snap_repo.create(snapshot=snap2)
    
    latest = snap_repo.get_latest_by_investment(investment_id="inv-1")
    
    assert latest is not None
    assert latest.current_value == Decimal(value="12000.00")
    assert latest.date == date(year=2024, month=2, day=29)

# Made with Bob



