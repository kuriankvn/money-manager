"""Account and Transaction service layer."""
from datetime import date
from decimal import Decimal
from typing import List, Optional

from app.accounts.models import Account, AccountType, Transaction
from app.accounts.repository import AccountRepository, TransactionRepository
from app.core.money import to_decimal
from app.utils.ids import generate_id


class AccountService:
    """Service for account operations."""
    
    def __init__(self, repository: AccountRepository):
        self.repository = repository
    
    def create_account(
        self,
        name: str,
        account_type: AccountType,
        institution: str,
        notes: str | None = None
    ) -> Account:
        """Create a new account."""
        account = Account(
            id=generate_id(),
            name=name,
            type=account_type,
            institution=institution,
            notes=notes
        )
        self.repository.create(account)
        return account
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID."""
        return self.repository.get_by_id(account_id)
    
    def list_accounts(self) -> List[Account]:
        """List all accounts."""
        return self.repository.get_all()
    
    def update_account(self, account: Account) -> None:
        """Update an account."""
        self.repository.update(account)
    
    def delete_account(self, account_id: str) -> None:
        """Delete an account."""
        self.repository.delete(account_id)


class TransactionService:
    """Service for transaction operations."""
    
    def __init__(self, repository: TransactionRepository):
        self.repository = repository
    
    def create_transaction(
        self,
        account_id: str,
        transaction_date: date,
        amount: Decimal,
        description: str,
        category: str,
        notes: str | None = None
    ) -> Transaction:
        """Create a new transaction."""
        transaction = Transaction(
            id=generate_id(),
            account_id=account_id,
            date=transaction_date,
            amount=to_decimal(amount),
            description=description,
            category=category,
            notes=notes
        )
        self.repository.create(transaction)
        return transaction
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID."""
        return self.repository.get_by_id(transaction_id)
    
    def list_transactions_by_account(self, account_id: str) -> List[Transaction]:
        """List all transactions for an account."""
        return self.repository.get_by_account(account_id)
    
    def list_transactions_by_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[Transaction]:
        """List transactions within date range."""
        return self.repository.get_by_date_range(start_date, end_date)
    
    def list_all_transactions(self) -> List[Transaction]:
        """List all transactions."""
        return self.repository.get_all()
    
    def update_transaction(self, transaction: Transaction) -> None:
        """Update a transaction."""
        self.repository.update(transaction)
    
    def delete_transaction(self, transaction_id: str) -> None:
        """Delete a transaction."""
        self.repository.delete(transaction_id)

