from datetime import date
from decimal import Decimal

from app.accounts.models import Account, Transaction
from app.accounts.repository import AccountRepository, TransactionRepository
from app.accounts.service import AccountService, TransactionService


def test_account_service_create_account(db_conn) -> None:
    repo=AccountRepository(conn=db_conn)
    service=AccountService(repository=repo)
    
    account = service.create_account(
        name="HDFC Savings",
        account_type="BANK",
        institution="HDFC Bank",
        notes="Primary account"
    )
    
    assert account.id is not None
    assert account.name == "HDFC Savings"
    assert account.type == "BANK"
    
    retrieved: list[Account] = repo.get_by_id(account_id=account.id)
    assert retrieved is not None
    assert retrieved.name == "HDFC Savings"


def test_account_service_list_accounts(db_conn) -> None:
    repo=AccountRepository(conn=db_conn)
    service=AccountService(repository=repo)
    
    service.create_account(name="HDFC", account_type="BANK", institution="HDFC")
    service.create_account(name="ICICI", account_type="CARD", institution="ICICI")
    
    accounts: list[Account] = service.list_accounts()
    
    assert len(accounts) == 2


def test_transaction_service_create_transaction(db_conn) -> None:
    acc_repo=AccountRepository(conn=db_conn)
    txn_repo=TransactionRepository(conn=db_conn)
    
    acc_service=AccountService(repository=acc_repo)
    txn_service=TransactionService(repository=txn_repo)
    
    account = acc_service.create_account(
        name="HDFC",
        account_type="BANK",
        institution="HDFC"
    )
    
    transaction = txn_service.create_transaction(
        account_id=account.id,
        transaction_date=date(year=2024, month=1, day=15),
        amount=Decimal(value="1000.00"),
        description="Salary",
        category="Income"
    )
    
    assert transaction.id is not None
    assert transaction.amount == Decimal(value="1000.00")
    assert transaction.is_income is True
    
    retrieved: list[Account] = txn_repo.get_by_id(transaction_id=transaction.id)
    assert retrieved is not None
    assert retrieved.description == "Salary"


def test_transaction_service_list_by_account(db_conn) -> None:
    acc_repo=AccountRepository(conn=db_conn)
    txn_repo=TransactionRepository(conn=db_conn)
    
    acc_service=AccountService(repository=acc_repo)
    txn_service=TransactionService(repository=txn_repo)
    
    account = acc_service.create_account(
        name="HDFC",
        account_type="BANK",
        institution="HDFC"
    )
    
    txn_service.create_transaction(
        account_id=account.id,
        transaction_date=date(year=2024, month=1, day=15),
        amount=Decimal(value="1000.00"),
        description="Salary",
        category="Income"
    )
    
    txn_service.create_transaction(
        account_id=account.id,
        transaction_date=date(year=2024, month=1, day=20),
        amount=Decimal(value="-500.00"),
        description="Groceries",
        category="Food"
    )
    
    transactions: list[Account] = txn_service.list_transactions_by_account(account_id=account.id)
    
    assert len(transactions) == 2
    assert transactions[0].amount == Decimal(value="-500.00")
    assert transactions[1].amount == Decimal(value="1000.00")

# Made with Bob



