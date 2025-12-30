"""Account and Transaction repository."""
import sqlite3
from datetime import date
from typing import List, Optional

from app.accounts.models import Account, Transaction
from app.core.money import to_decimal


class AccountRepository:
    """Repository for Account operations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
    
    def create(self, account: Account) -> None:
        """Create a new account."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO accounts (id, name, type, institution, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (account.id, account.name, account.type, account.institution, account.notes)
        )
        self.conn.commit()
    
    def get_by_id(self, account_id: str) -> Optional[Account]:
        """Get account by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_account(row)
    
    def get_all(self) -> List[Account]:
        """Get all accounts."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM accounts ORDER BY name")
        return [self._row_to_account(row) for row in cursor.fetchall()]
    
    def update(self, account: Account) -> None:
        """Update an account."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE accounts
            SET name = ?, type = ?, institution = ?, notes = ?
            WHERE id = ?
            """,
            (account.name, account.type, account.institution, account.notes, account.id)
        )
        self.conn.commit()
    
    def delete(self, account_id: str) -> None:
        """Delete an account."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        self.conn.commit()
    
    def _row_to_account(self, row: sqlite3.Row) -> Account:
        """Convert database row to Account."""
        return Account(
            id=row["id"],
            name=row["name"],
            type=row["type"],
            institution=row["institution"],
            notes=row["notes"]
        )


class TransactionRepository:
    """Repository for Transaction operations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
    
    def create(self, transaction: Transaction) -> None:
        """Create a new transaction."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (id, account_id, date, amount, description, category, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction.id,
                transaction.account_id,
                transaction.date.isoformat(),
                str(transaction.amount),
                transaction.description,
                transaction.category,
                transaction.notes
            )
        )
        self.conn.commit()
    
    def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_transaction(row)
    
    def get_by_account(self, account_id: str) -> List[Transaction]:
        """Get all transactions for an account."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM transactions WHERE account_id = ? ORDER BY date DESC",
            (account_id,)
        )
        return [self._row_to_transaction(row) for row in cursor.fetchall()]
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Transaction]:
        """Get transactions within date range."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM transactions
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
            """,
            (start_date.isoformat(), end_date.isoformat())
        )
        return [self._row_to_transaction(row) for row in cursor.fetchall()]
    
    def get_all(self) -> List[Transaction]:
        """Get all transactions."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        return [self._row_to_transaction(row) for row in cursor.fetchall()]
    
    def update(self, transaction: Transaction) -> None:
        """Update a transaction."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE transactions
            SET account_id = ?, date = ?, amount = ?, description = ?, category = ?, notes = ?
            WHERE id = ?
            """,
            (
                transaction.account_id,
                transaction.date.isoformat(),
                str(transaction.amount),
                transaction.description,
                transaction.category,
                transaction.notes,
                transaction.id
            )
        )
        self.conn.commit()
    
    def delete(self, transaction_id: str) -> None:
        """Delete a transaction."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()
    
    def _row_to_transaction(self, row: sqlite3.Row) -> Transaction:
        """Convert database row to Transaction."""
        return Transaction(
            id=row["id"],
            account_id=row["account_id"],
            date=date.fromisoformat(row["date"]),
            amount=to_decimal(row["amount"]),
            description=row["description"],
            category=row["category"],
            notes=row["notes"]
        )

