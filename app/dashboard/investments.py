"""Investment portfolio dashboard view."""
from decimal import Decimal
from typing import Dict, List

from app.investments.repository import (
    InvestmentRepository,
    InvestmentContributionRepository,
    InvestmentValueSnapshotRepository
)
from app.investments.calculator import InvestmentCalculator
from app.core.money import to_decimal


class InvestmentDashboard:
    """Provides portfolio view for investments."""
    
    def __init__(
        self,
        investment_repo: InvestmentRepository,
        contribution_repo: InvestmentContributionRepository,
        snapshot_repo: InvestmentValueSnapshotRepository,
        calculator: InvestmentCalculator
    ):
        self.investment_repo = investment_repo
        self.contribution_repo = contribution_repo
        self.snapshot_repo = snapshot_repo
        self.calculator = calculator
    
    def get_portfolio_overview(self) -> Dict:
        """Get complete portfolio overview."""
        investments = self.investment_repo.get_all()
        
        investment_summaries = []
        portfolio_data = []
        
        for investment in investments:
            contributions = self.contribution_repo.get_by_investment(investment.id)
            snapshots = self.snapshot_repo.get_by_investment(investment.id)
            
            total_invested = self.calculator.calculate_total_invested(contributions)
            current_value = self.calculator.get_current_value(snapshots)
            gain_loss = self.calculator.calculate_gain_loss(total_invested, current_value)
            gain_loss_pct = self.calculator.calculate_gain_loss_percentage(total_invested, current_value)
            
            investment_summaries.append({
                "investment": investment,
                "total_invested": total_invested,
                "current_value": current_value,
                "gain_loss": gain_loss,
                "gain_loss_percentage": gain_loss_pct,
                "latest_snapshot_date": snapshots[0].date if snapshots else None
            })
            
            portfolio_data.append((total_invested, current_value))
        
        portfolio_summary = self.calculator.calculate_portfolio_summary(portfolio_data)
        
        return {
            "investments": investment_summaries,
            "portfolio_total": portfolio_summary
        }
    
    def get_investment_detail(self, investment_id: str) -> Dict:
        """Get detailed view of a single investment."""
        investment = self.investment_repo.get_by_id(investment_id)
        if not investment:
            raise ValueError(f"Investment {investment_id} not found")
        
        contributions = self.contribution_repo.get_by_investment(investment_id)
        snapshots = self.snapshot_repo.get_by_investment(investment_id)
        
        total_invested = self.calculator.calculate_total_invested(contributions)
        current_value = self.calculator.get_current_value(snapshots)
        gain_loss = self.calculator.calculate_gain_loss(total_invested, current_value)
        gain_loss_pct = self.calculator.calculate_gain_loss_percentage(total_invested, current_value)
        
        return {
            "investment": investment,
            "summary": {
                "total_invested": total_invested,
                "current_value": current_value,
                "gain_loss": gain_loss,
                "gain_loss_percentage": gain_loss_pct
            },
            "contributions": contributions,
            "snapshots": snapshots
        }
    
    def get_portfolio_by_type(self) -> Dict[str, Dict]:
        """Get portfolio breakdown by investment type."""
        investments = self.investment_repo.get_all()
        
        type_summary: Dict[str, Dict] = {}
        
        for investment in investments:
            inv_type = investment.type
            
            if inv_type not in type_summary:
                type_summary[inv_type] = {
                    "total_invested": Decimal("0"),
                    "current_value": Decimal("0"),
                    "count": 0
                }
            
            contributions = self.contribution_repo.get_by_investment(investment.id)
            snapshots = self.snapshot_repo.get_by_investment(investment.id)
            
            total_invested = self.calculator.calculate_total_invested(contributions)
            current_value = self.calculator.get_current_value(snapshots)
            
            type_summary[inv_type]["total_invested"] += total_invested
            if current_value:
                type_summary[inv_type]["current_value"] += current_value
            type_summary[inv_type]["count"] += 1
        
        # Calculate gain/loss for each type
        for inv_type in type_summary:
            invested = type_summary[inv_type]["total_invested"]
            current = type_summary[inv_type]["current_value"]
            type_summary[inv_type]["gain_loss"] = self.calculator.calculate_gain_loss(invested, current)
            type_summary[inv_type]["gain_loss_percentage"] = self.calculator.calculate_gain_loss_percentage(invested, current)
        
        return type_summary

