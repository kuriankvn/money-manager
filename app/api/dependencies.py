"""API dependencies for dependency injection."""
import sqlite3
from typing import Generator

from app.storage.db import get_connection
from app.accounts.repository import AccountRepository, TransactionRepository
from app.accounts.service import AccountService, TransactionService
from app.subscriptions.repository import SubscriptionRepository, SubscriptionInstanceRepository
from app.subscriptions.service import SubscriptionService, SubscriptionInstanceService
from app.subscriptions.generator import SubscriptionInstanceGenerator
from app.investments.repository import (
    InvestmentRepository,
    InvestmentContributionRepository,
    InvestmentValueSnapshotRepository
)
from app.investments.service import (
    InvestmentService,
    InvestmentContributionService,
    InvestmentValueSnapshotService,
    InvestmentAnalysisService
)
from app.investments.calculator import InvestmentCalculator


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def get_account_service(conn: sqlite3.Connection) -> AccountService:
    repo = AccountRepository(conn=conn)
    return AccountService(repository=repo)


def get_transaction_service(conn: sqlite3.Connection) -> TransactionService:
    repo = TransactionRepository(conn=conn)
    return TransactionService(repository=repo)


def get_subscription_service(conn: sqlite3.Connection) -> SubscriptionService:
    sub_repo = SubscriptionRepository(conn=conn)
    inst_repo = SubscriptionInstanceRepository(conn=conn)
    generator = SubscriptionInstanceGenerator()
    return SubscriptionService(
        subscription_repo=sub_repo,
        instance_repo=inst_repo,
        generator=generator
    )


def get_subscription_instance_service(conn: sqlite3.Connection) -> SubscriptionInstanceService:
    repo = SubscriptionInstanceRepository(conn=conn)
    return SubscriptionInstanceService(repository=repo)


def get_investment_service(conn: sqlite3.Connection) -> InvestmentService:
    repo = InvestmentRepository(conn=conn)
    return InvestmentService(repository=repo)


def get_investment_contribution_service(conn: sqlite3.Connection) -> InvestmentContributionService:
    repo = InvestmentContributionRepository(conn=conn)
    return InvestmentContributionService(repository=repo)


def get_investment_snapshot_service(conn: sqlite3.Connection) -> InvestmentValueSnapshotService:
    repo = InvestmentValueSnapshotRepository(conn=conn)
    return InvestmentValueSnapshotService(repository=repo)


def get_investment_analysis_service(conn: sqlite3.Connection) -> InvestmentAnalysisService:
    contrib_repo = InvestmentContributionRepository(conn=conn)
    snapshot_repo = InvestmentValueSnapshotRepository(conn=conn)
    calculator = InvestmentCalculator()
    return InvestmentAnalysisService(
        contribution_repo=contrib_repo,
        snapshot_repo=snapshot_repo,
        calculator=calculator
    )

# Made with Bob
