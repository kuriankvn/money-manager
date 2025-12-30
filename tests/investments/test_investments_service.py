from datetime import date
from decimal import Decimal

from app.investments.calculator import InvestmentCalculator
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
from app.investments.service import (
    InvestmentAnalysisService,
    InvestmentContributionService,
    InvestmentService,
    InvestmentValueSnapshotService,
)


def test_investment_service_create(db_conn) -> None:
    repo=InvestmentRepository(conn=db_conn)
    service=InvestmentService(repository=repo)
    
    investment = service.create_investment(
        name="HDFC Flexi Cap",
        provider="HDFC MF",
        investment_type="MF",
        notes="Growth fund"
    )
    
    assert investment.id is not None
    assert investment.name == "HDFC Flexi Cap"
    
    retrieved: list[Investment] = repo.get_by_id(investment_id=investment.id)
    assert retrieved is not None


def test_contribution_service_add(db_conn) -> None:
    inv_repo=InvestmentRepository(conn=db_conn)
    contrib_repo=InvestmentContributionRepository(conn=db_conn)
    
    inv_service=InvestmentService(repository=inv_repo)
    contrib_service=InvestmentContributionService(repository=contrib_repo)
    
    investment = inv_service.create_investment(
        name="Fund",
        provider="HDFC",
        investment_type="MF"
    )
    
    contribution = contrib_service.add_contribution(
        investment_id=investment.id,
        contribution_date=date(year=2024, month=1, day=15),
        amount=Decimal(value="10000.00"),
        notes="Initial"
    )
    
    assert contribution.id is not None
    assert contribution.amount == Decimal(value="10000.00")


def test_snapshot_service_add(db_conn) -> None:
    inv_repo=InvestmentRepository(conn=db_conn)
    snap_repo=InvestmentValueSnapshotRepository(conn=db_conn)
    
    inv_service=InvestmentService(repository=inv_repo)
    snap_service=InvestmentValueSnapshotService(repository=snap_repo)
    
    investment = inv_service.create_investment(
        name="Fund",
        provider="HDFC",
        investment_type="MF"
    )
    
    snapshot = snap_service.add_snapshot(
        investment_id=investment.id,
        snapshot_date=date(year=2024, month=1, day=31),
        current_value=Decimal(value="11000.00")
    )
    
    assert snapshot.id is not None
    assert snapshot.current_value == Decimal(value="11000.00")


def test_analysis_service_get_investment_summary(db_conn) -> None:
    inv_repo=InvestmentRepository(conn=db_conn)
    contrib_repo=InvestmentContributionRepository(conn=db_conn)
    snap_repo=InvestmentValueSnapshotRepository(conn=db_conn)
    calculator=InvestmentCalculator()
    
    inv_service=InvestmentService(repository=inv_repo)
    contrib_service=InvestmentContributionService(repository=contrib_repo)
    snap_service=InvestmentValueSnapshotService(repository=snap_repo)
    analysis_service=InvestmentAnalysisService(
        contribution_repo=contrib_repo,
        snapshot_repo=snap_repo,
        calculator=calculator
    )
    
    investment = inv_service.create_investment(
        name="Fund",
        provider="HDFC",
        investment_type="MF"
    )
    
    contrib_service.add_contribution(
        investment_id=investment.id,
        contribution_date=date(year=2024, month=1, day=15),
        amount=Decimal(value="10000.00")
    )
    
    snap_service.add_snapshot(
        investment_id=investment.id,
        snapshot_date=date(year=2024, month=1, day=31),
        current_value=Decimal(value="11000.00")
    )
    
    summary = analysis_service.get_investment_summary(investment_id=investment.id)
    
    assert summary["total_invested"] == Decimal(value="10000.00")
    assert summary["current_value"] == Decimal(value="11000.00")
    assert summary["gain_loss"] == Decimal(value="1000.00")


def test_analysis_service_get_portfolio_summary(db_conn) -> None:
    inv_repo=InvestmentRepository(conn=db_conn)
    contrib_repo=InvestmentContributionRepository(conn=db_conn)
    snap_repo=InvestmentValueSnapshotRepository(conn=db_conn)
    calculator=InvestmentCalculator()
    
    inv_service=InvestmentService(repository=inv_repo)
    contrib_service=InvestmentContributionService(repository=contrib_repo)
    snap_service=InvestmentValueSnapshotService(repository=snap_repo)
    analysis_service=InvestmentAnalysisService(
        contribution_repo=contrib_repo,
        snapshot_repo=snap_repo,
        calculator=calculator
    )
    
    inv1 = inv_service.create_investment(name="Fund1", provider="HDFC", investment_type="MF")
    inv2 = inv_service.create_investment(name="Fund2", provider="ICICI", investment_type="MF")
    
    contrib_service.add_contribution(
        investment_id=inv1.id,
        contribution_date=date(year=2024, month=1, day=15),
        amount=Decimal(value="10000.00")
    )
    
    contrib_service.add_contribution(
        investment_id=inv2.id,
        contribution_date=date(year=2024, month=1, day=15),
        amount=Decimal(value="5000.00")
    )
    
    snap_service.add_snapshot(
        investment_id=inv1.id,
        snapshot_date=date(year=2024, month=1, day=31),
        current_value=Decimal(value="11000.00")
    )
    
    snap_service.add_snapshot(
        investment_id=inv2.id,
        snapshot_date=date(year=2024, month=1, day=31),
        current_value=Decimal(value="5500.00")
    )
    
    summary = analysis_service.get_portfolio_summary(investment_ids=[inv1.id, inv2.id])
    
    assert summary["total_invested"] == Decimal(value="15000.00")
    assert summary["total_current_value"] == Decimal(value="16500.00")
    assert summary["total_gain_loss"] == Decimal(value="1500.00")

# Made with Bob



