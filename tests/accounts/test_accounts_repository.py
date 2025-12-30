from datetime import date
from decimal import Decimal

from app.accounts.models import Account, Transaction
from app.accounts.repository import AccountRepository, TransactionRepository


def test_account_repository_create_and_get(db_conn) -> None:
    repo=AccountRepository(conn=db_conn)
    
    account=Account(
        id="acc-1",
        name="HDFC Savings",
        type="BANK",
        institution="HDFC Bank",
        notes="Primary account"
    )
    
    repo.create(account=account)
    retrieved: list[Account] = repo.get_by_id(account_id="acc-1")
    
    assert retrieved is not None
    assert retrieved.id == "acc-1"
    assert retrieved.name == "HDFC Savings"
    assert retrieved.type == "BANK"
    assert retrieved.institution == "HDFC Bank"


def test_account_repository_get_all(db_conn) -> None:
    repo=AccountRepository(conn=db_conn)
    
    account1=Account(id="acc-1", name="HDFC", type="BANK", institution="HDFC")
    account2=Account(id="acc-2", name="ICICI", type="CARD", institution="ICICI")
    
    repo.create(account=account1)
    repo.create(account=account2)
    
    accounts: list[Account] = repo.get_all()
    
    assert len(accounts) == 2
    assert accounts[0].name == "HDFC"
    assert accounts[1].name == "ICICI"


def test_account_repository_update(db_conn) -> None:
    repo=AccountRepository(conn=db_conn)
    
    account=Account(id="acc-1", name="HDFC", type="BANK", institution="HDFC")
    repo.create(account=account)
    
    account.name = "HDFC Updated"
    repo.update(account=account)
    
    retrieved: list[Account] = repo.get_by_id(account_id="acc-1")
    assert retrieved.name == "HDFC Updated"


def test_account_repository_delete(db_conn) -> None:
    repo=AccountRepository(conn=db_conn)
    
    account=Account(id="acc-1", name="HDFC", type="BANK", institution="HDFC")
    repo.create(account=account)
    
    repo.delete(account_id="acc-1")
    
    retrieved: list[Account] = repo.get_by_id(account_id="acc-1")
    assert retrieved is None


def test_transaction_repository_create_and_get(db_conn) -> None:
    acc_repo=AccountRepository(conn=db_conn)
    txn_repo=TransactionRepository(conn=db_conn)
    
    account=Account(id="acc-1", name="HDFC", type="BANK", institution="HDFC")
    acc_repo.create(account=account)
    
    transaction=Transaction(
        id="txn-1",
        account_id="acc-1",
        date=date(year=2024, month=1, day=15),
        amount=Decimal(value="1000.00"),
        description="Salary",
        category="Income",
        notes="Monthly salary"
    )
    
    txn_repo.create(transaction=transaction)
    retrieved: list[Account] = txn_repo.get_by_id(transaction_id="txn-1")
    
    assert retrieved is not None
    assert retrieved.id == "txn-1"
    assert retrieved.amount == Decimal(value="1000.00")
    assert retrieved.description == "Salary"


def test_transaction_repository_get_by_account(db_conn) -> None:
    acc_repo=AccountRepository(conn=db_conn)
    txn_repo=TransactionRepository(conn=db_conn)
    
    account=Account(id="acc-1", name="HDFC", type="BANK", institution="HDFC")
    acc_repo.create(account=account)
    
    txn1=Transaction(
        id="txn-1",
        account_id="acc-1",
        date=date(year=2024, month=1, day=15),
        amount=Decimal(value="1000.00"),
        description="Salary",
        category="Income"
    )
    txn2=Transaction(
        id="txn-2",
        account_id="acc-1",
        date=date(year=2024, month=1, day=20),
        amount=Decimal(value="-500.00"),
        description="Groceries",
        category="Food"
    )
    
    txn_repo.create(transaction=txn1)
    txn_repo.create(transaction=txn2)
    
    transactions: list[Account] = txn_repo.get_by_account(account_id="acc-1")
    
    assert len(transactions) == 2
    assert transactions[0].id == "txn-2"
    assert transactions[1].id == "txn-1"


def test_transaction_repository_get_by_date_range(db_conn) -> None:
    acc_repo=AccountRepository(conn=db_conn)
    txn_repo=TransactionRepository(conn=db_conn)
    
    account=Account(id="acc-1", name="HDFC", type="BANK", institution="HDFC")
    acc_repo.create(account=account)
    
    txn1=Transaction(
        id="txn-1",
        account_id="acc-1",
        date=date(year=2024, month=1, day=15),
        amount=Decimal(value="1000.00"),
        description="Jan",
        category="Income"
    )
    txn2=Transaction(
        id="txn-2",
        account_id="acc-1",
        date=date(year=2024, month=2, day=15),
        amount=Decimal(value="2000.00"),
        description="Feb",
        category="Income"
    )
    
    txn_repo.create(transaction=txn1)
    txn_repo.create(transaction=txn2)
    
    transactions: list[Account] = txn_repo.get_by_date_range(
        start_date=date(year=2024, month=1, day=1),
        end_date=date(year=2024, month=1, day=31)
    )
    
    assert len(transactions) == 1
    assert transactions[0].description == "Jan"

# Made with Bob



