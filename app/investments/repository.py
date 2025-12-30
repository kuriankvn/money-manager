"""Investment repositories."""
import sqlite3
from datetime import date
from typing import List, Optional

from app.core.money import to_decimal
from app.investments.models import (
    Investment,
    InvestmentContribution,
    InvestmentType,
    InvestmentValueSnapshot,
)


class InvestmentRepository:
    """Repository for Investment operations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
    
    def create(self, investment: Investment) -> None:
        """Create a new investment."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO investments (id, name, provider, type, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (investment.id, investment.name, investment.provider, investment.type, investment.notes)
        )
        self.conn.commit()
    
    def get_by_id(self, investment_id: str) -> Optional[Investment]:
        """Get investment by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM investments WHERE id = ?", (investment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_investment(row)
    
    def get_all(self) -> List[Investment]:
        """Get all investments."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM investments ORDER BY name")
        return [self._row_to_investment(row) for row in cursor.fetchall()]
    
    def update(self, investment: Investment) -> None:
        """Update an investment."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE investments
            SET name = ?, provider = ?, type = ?, notes = ?
            WHERE id = ?
            """,
            (investment.name, investment.provider, investment.type, investment.notes, investment.id)
        )
        self.conn.commit()
    
    def delete(self, investment_id: str) -> None:
        """Delete an investment."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM investments WHERE id = ?", (investment_id,))
        self.conn.commit()
    
    def _row_to_investment(self, row: sqlite3.Row) -> Investment:
        """Convert database row to Investment."""
        return Investment(
            id=row["id"],
            name=row["name"],
            provider=row["provider"],
            type=row["type"],
            notes=row["notes"]
        )


class InvestmentContributionRepository:
    """Repository for InvestmentContribution operations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
    
    def create(self, contribution: InvestmentContribution) -> None:
        """Create a new contribution."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO investment_contributions (id, investment_id, date, amount, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                contribution.id,
                contribution.investment_id,
                contribution.date.isoformat(),
                str(contribution.amount),
                contribution.notes
            )
        )
        self.conn.commit()
    
    def get_by_id(self, contribution_id: str) -> Optional[InvestmentContribution]:
        """Get contribution by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM investment_contributions WHERE id = ?", (contribution_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_contribution(row)
    
    def get_by_investment(self, investment_id: str) -> List[InvestmentContribution]:
        """Get all contributions for an investment."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM investment_contributions
            WHERE investment_id = ?
            ORDER BY date DESC
            """,
            (investment_id,)
        )
        return [self._row_to_contribution(row) for row in cursor.fetchall()]
    
    def get_all(self) -> List[InvestmentContribution]:
        """Get all contributions."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM investment_contributions ORDER BY date DESC")
        return [self._row_to_contribution(row) for row in cursor.fetchall()]
    
    def update(self, contribution: InvestmentContribution) -> None:
        """Update a contribution."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE investment_contributions
            SET investment_id = ?, date = ?, amount = ?, notes = ?
            WHERE id = ?
            """,
            (
                contribution.investment_id,
                contribution.date.isoformat(),
                str(contribution.amount),
                contribution.notes,
                contribution.id
            )
        )
        self.conn.commit()
    
    def delete(self, contribution_id: str) -> None:
        """Delete a contribution."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM investment_contributions WHERE id = ?", (contribution_id,))
        self.conn.commit()
    
    def _row_to_contribution(self, row: sqlite3.Row) -> InvestmentContribution:
        """Convert database row to InvestmentContribution."""
        return InvestmentContribution(
            id=row["id"],
            investment_id=row["investment_id"],
            date=date.fromisoformat(row["date"]),
            amount=to_decimal(row["amount"]),
            notes=row["notes"]
        )


class InvestmentValueSnapshotRepository:
    """Repository for InvestmentValueSnapshot operations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
    
    def create(self, snapshot: InvestmentValueSnapshot) -> None:
        """Create a new snapshot."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO investment_value_snapshots (id, investment_id, date, current_value)
            VALUES (?, ?, ?, ?)
            """,
            (
                snapshot.id,
                snapshot.investment_id,
                snapshot.date.isoformat(),
                str(snapshot.current_value)
            )
        )
        self.conn.commit()
    
    def get_by_id(self, snapshot_id: str) -> Optional[InvestmentValueSnapshot]:
        """Get snapshot by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM investment_value_snapshots WHERE id = ?", (snapshot_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_snapshot(row)
    
    def get_by_investment(self, investment_id: str) -> List[InvestmentValueSnapshot]:
        """Get all snapshots for an investment."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM investment_value_snapshots
            WHERE investment_id = ?
            ORDER BY date DESC
            """,
            (investment_id,)
        )
        return [self._row_to_snapshot(row) for row in cursor.fetchall()]
    
    def get_latest_by_investment(self, investment_id: str) -> Optional[InvestmentValueSnapshot]:
        """Get the latest snapshot for an investment."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM investment_value_snapshots
            WHERE investment_id = ?
            ORDER BY date DESC
            LIMIT 1
            """,
            (investment_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_snapshot(row)
    
    def get_all(self) -> List[InvestmentValueSnapshot]:
        """Get all snapshots."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM investment_value_snapshots ORDER BY date DESC")
        return [self._row_to_snapshot(row) for row in cursor.fetchall()]
    
    def update(self, snapshot: InvestmentValueSnapshot) -> None:
        """Update a snapshot."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE investment_value_snapshots
            SET investment_id = ?, date = ?, current_value = ?
            WHERE id = ?
            """,
            (
                snapshot.investment_id,
                snapshot.date.isoformat(),
                str(snapshot.current_value),
                snapshot.id
            )
        )
        self.conn.commit()
    
    def delete(self, snapshot_id: str) -> None:
        """Delete a snapshot."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM investment_value_snapshots WHERE id = ?", (snapshot_id,))
        self.conn.commit()
    
    def _row_to_snapshot(self, row: sqlite3.Row) -> InvestmentValueSnapshot:
        """Convert database row to InvestmentValueSnapshot."""
        return InvestmentValueSnapshot(
            id=row["id"],
            investment_id=row["investment_id"],
            date=date.fromisoformat(row["date"]),
            current_value=to_decimal(row["current_value"])
        )

