"""Investment service layer."""
from datetime import date
from decimal import Decimal
from typing import List, Optional

from app.core.money import to_decimal
from app.investments.calculator import InvestmentCalculator
from app.investments.models import (
    Investment,
    InvestmentContribution,
    InvestmentType,
    InvestmentValueSnapshot,
)
from app.investments.repository import (
    InvestmentContributionRepository,
    InvestmentRepository,
    InvestmentValueSnapshotRepository,
)
from app.utils.ids import generate_id


class InvestmentService:
    """Service for investment operations."""
    
    def __init__(self, repository: InvestmentRepository):
        self.repository = repository
    
    def create_investment(
        self,
        name: str,
        provider: str,
        investment_type: InvestmentType,
        notes: Optional[str] = None
    ) -> Investment:
        """Create a new investment."""
        investment = Investment(
            id=generate_id(),
            name=name,
            provider=provider,
            type=investment_type,
            notes=notes
        )
        self.repository.create(investment)
        return investment
    
    def get_investment(self, investment_id: str) -> Optional[Investment]:
        """Get investment by ID."""
        return self.repository.get_by_id(investment_id)
    
    def list_investments(self) -> List[Investment]:
        """List all investments."""
        return self.repository.get_all()
    
    def update_investment(self, investment: Investment) -> None:
        """Update an investment."""
        self.repository.update(investment)
    
    def delete_investment(self, investment_id: str) -> None:
        """Delete an investment."""
        self.repository.delete(investment_id)


class InvestmentContributionService:
    """Service for investment contribution operations."""
    
    def __init__(self, repository: InvestmentContributionRepository):
        self.repository = repository
    
    def add_contribution(
        self,
        investment_id: str,
        contribution_date: date,
        amount: Decimal,
        notes: Optional[str] = None
    ) -> InvestmentContribution:
        """Add a contribution (investment or redemption)."""
        contribution = InvestmentContribution(
            id=generate_id(),
            investment_id=investment_id,
            date=contribution_date,
            amount=to_decimal(amount),
            notes=notes
        )
        self.repository.create(contribution)
        return contribution
    
    def get_contribution(self, contribution_id: str) -> Optional[InvestmentContribution]:
        """Get contribution by ID."""
        return self.repository.get_by_id(contribution_id)
    
    def list_contributions_by_investment(self, investment_id: str) -> List[InvestmentContribution]:
        """List all contributions for an investment."""
        return self.repository.get_by_investment(investment_id)
    
    def list_all_contributions(self) -> List[InvestmentContribution]:
        """List all contributions."""
        return self.repository.get_all()
    
    def update_contribution(self, contribution: InvestmentContribution) -> None:
        """Update a contribution."""
        self.repository.update(contribution)
    
    def delete_contribution(self, contribution_id: str) -> None:
        """Delete a contribution."""
        self.repository.delete(contribution_id)


class InvestmentValueSnapshotService:
    """Service for investment value snapshot operations."""
    
    def __init__(self, repository: InvestmentValueSnapshotRepository):
        self.repository = repository
    
    def add_snapshot(
        self,
        investment_id: str,
        snapshot_date: date,
        current_value: Decimal
    ) -> InvestmentValueSnapshot:
        """Add a value snapshot."""
        snapshot = InvestmentValueSnapshot(
            id=generate_id(),
            investment_id=investment_id,
            date=snapshot_date,
            current_value=to_decimal(current_value)
        )
        self.repository.create(snapshot)
        return snapshot
    
    def get_snapshot(self, snapshot_id: str) -> Optional[InvestmentValueSnapshot]:
        """Get snapshot by ID."""
        return self.repository.get_by_id(snapshot_id)
    
    def list_snapshots_by_investment(self, investment_id: str) -> List[InvestmentValueSnapshot]:
        """List all snapshots for an investment."""
        return self.repository.get_by_investment(investment_id)
    
    def get_latest_snapshot(self, investment_id: str) -> Optional[InvestmentValueSnapshot]:
        """Get the latest snapshot for an investment."""
        return self.repository.get_latest_by_investment(investment_id)
    
    def list_all_snapshots(self) -> List[InvestmentValueSnapshot]:
        """List all snapshots."""
        return self.repository.get_all()
    
    def update_snapshot(self, snapshot: InvestmentValueSnapshot) -> None:
        """Update a snapshot."""
        self.repository.update(snapshot)
    
    def delete_snapshot(self, snapshot_id: str) -> None:
        """Delete a snapshot."""
        self.repository.delete(snapshot_id)


class InvestmentAnalysisService:
    """Service for investment analysis and calculations."""
    
    def __init__(
        self,
        contribution_repo: InvestmentContributionRepository,
        snapshot_repo: InvestmentValueSnapshotRepository,
        calculator: InvestmentCalculator
    ):
        self.contribution_repo = contribution_repo
        self.snapshot_repo = snapshot_repo
        self.calculator = calculator
    
    def get_investment_summary(self, investment_id: str) -> dict:
        """Get summary for a single investment."""
        contributions = self.contribution_repo.get_by_investment(investment_id)
        snapshots = self.snapshot_repo.get_by_investment(investment_id)
        
        total_invested = self.calculator.calculate_total_invested(contributions)
        current_value = self.calculator.get_current_value(snapshots)
        gain_loss = self.calculator.calculate_gain_loss(total_invested, current_value)
        gain_loss_pct = self.calculator.calculate_gain_loss_percentage(total_invested, current_value)
        
        return {
            "investment_id": investment_id,
            "total_invested": total_invested,
            "current_value": current_value,
            "gain_loss": gain_loss,
            "gain_loss_percentage": gain_loss_pct,
            "contribution_count": len(contributions),
            "latest_snapshot_date": snapshots[0].date if snapshots else None
        }
    
    def get_portfolio_summary(self, investment_ids: List[str]) -> dict:
        """Get portfolio-wide summary."""
        investments_data = []
        
        for investment_id in investment_ids:
            contributions = self.contribution_repo.get_by_investment(investment_id)
            snapshots = self.snapshot_repo.get_by_investment(investment_id)
            
            total_invested = self.calculator.calculate_total_invested(contributions)
            current_value = self.calculator.get_current_value(snapshots)
            
            investments_data.append((total_invested, current_value))
        
        return self.calculator.calculate_portfolio_summary(investments_data)

