"""Investment API routes."""
import sqlite3
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_db,
    get_investment_analysis_service,
    get_investment_contribution_service,
    get_investment_service,
    get_investment_snapshot_service,
)
from app.api.schemas import (
    ContributionCreate,
    ContributionResponse,
    InvestmentCreate,
    InvestmentResponse,
    SnapshotCreate,
    SnapshotResponse,
)


router = APIRouter(prefix="/investments", tags=["investments"])


@router.post("/", response_model=InvestmentResponse)
def create_investment(
    inv_data: InvestmentCreate,
    conn: sqlite3.Connection = Depends(get_db)
):
    service = get_investment_service(conn=conn)
    investment = service.create_investment(
        name=inv_data.name,
        provider=inv_data.provider,
        investment_type=inv_data.type,
        notes=inv_data.notes
    )
    return InvestmentResponse(
        id=investment.id,
        name=investment.name,
        provider=investment.provider,
        type=investment.type,
        notes=investment.notes
    )


@router.get("/", response_model=List[InvestmentResponse])
def list_investments(conn: sqlite3.Connection = Depends(get_db)):
    service = get_investment_service(conn=conn)
    investments = service.list_investments()
    return [
        InvestmentResponse(
            id=inv.id,
            name=inv.name,
            provider=inv.provider,
            type=inv.type,
            notes=inv.notes
        )
        for inv in investments
    ]


@router.post("/contributions", response_model=ContributionResponse)
def add_contribution(
    contrib_data: ContributionCreate,
    conn: sqlite3.Connection = Depends(get_db)
):
    service = get_investment_contribution_service(conn=conn)
    contribution = service.add_contribution(
        investment_id=contrib_data.investment_id,
        contribution_date=contrib_data.date,
        amount=contrib_data.amount,
        notes=contrib_data.notes
    )
    return ContributionResponse(
        id=contribution.id,
        investment_id=contribution.investment_id,
        date=contribution.date,
        amount=contribution.amount,
        notes=contribution.notes
    )


@router.get("/{investment_id}/contributions", response_model=List[ContributionResponse])
def list_contributions(
    investment_id: str,
    conn: sqlite3.Connection = Depends(get_db)
):
    service = get_investment_contribution_service(conn=conn)
    contributions = service.list_contributions_by_investment(investment_id=investment_id)
    return [
        ContributionResponse(
            id=c.id,
            investment_id=c.investment_id,
            date=c.date,
            amount=c.amount,
            notes=c.notes
        )
        for c in contributions
    ]


@router.post("/snapshots", response_model=SnapshotResponse)
def add_snapshot(
    snap_data: SnapshotCreate,
    conn: sqlite3.Connection = Depends(get_db)
):
    service = get_investment_snapshot_service(conn=conn)
    snapshot = service.add_snapshot(
        investment_id=snap_data.investment_id,
        snapshot_date=snap_data.date,
        current_value=snap_data.current_value
    )
    return SnapshotResponse(
        id=snapshot.id,
        investment_id=snapshot.investment_id,
        date=snapshot.date,
        current_value=snapshot.current_value
    )


@router.get("/{investment_id}/summary")
def get_investment_summary(
    investment_id: str,
    conn: sqlite3.Connection = Depends(get_db)
):
    service = get_investment_analysis_service(conn=conn)
    return service.get_investment_summary(investment_id=investment_id)


@router.get("/portfolio/summary")
def get_portfolio_summary(conn: sqlite3.Connection = Depends(get_db)):
    inv_service = get_investment_service(conn=conn)
    analysis_service = get_investment_analysis_service(conn=conn)
    
    investments = inv_service.list_investments()
    investment_ids = [inv.id for inv in investments]
    
    return analysis_service.get_portfolio_summary(investment_ids=investment_ids)

@router.get("/export/csv")
def export_investments_csv(conn: sqlite3.Connection = Depends(get_db)):
    """Export all investments to CSV format"""
    import csv
    from io import StringIO
    from fastapi.responses import Response
    
    service = get_investment_service(conn=conn)
    investments = service.list_investments()
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['name', 'provider', 'type', 'notes'])
    
    for inv in investments:
        writer.writerow([
            inv.name,
            inv.provider,
            inv.type,
            inv.notes if inv.notes else ''
        ])
    
    return Response(content=output.getvalue(), media_type="text/csv")


@router.post("/import/csv")
def import_investments_csv(
    file_data: dict,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Import investments from CSV format"""
    import csv
    from io import StringIO
    
    service = get_investment_service(conn=conn)
    csv_content = file_data.get('file_content', '')
    
    reader = csv.DictReader(StringIO(csv_content))
    
    created = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            name = row.get('name', '').strip()
            provider = row.get('provider', '').strip()
            inv_type = row.get('type', '').strip().upper()
            notes = row.get('notes', '').strip() or None
            
            if not name:
                errors.append(f"Row {row_num}: Name is required")
                continue
            
            if not provider:
                errors.append(f"Row {row_num}: Provider is required")
                continue
            
            valid_types = ['MF', 'STOCK', 'FD', 'GOLD']
            if inv_type not in valid_types:
                errors.append(f"Row {row_num}: Invalid type. Must be one of {', '.join(valid_types)}")
                continue
            
            from app.investments.models import InvestmentType
            service.create_investment(
                name=name,
                provider=provider,
                investment_type=inv_type,  # type: ignore
                notes=notes
            )
            created += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    return {
        "created": created,
        "errors": errors,
        "total_rows": created + len(errors)
    }


@router.get("/contributions/export/csv")
def export_contributions_csv(
    investment_id: str | None = None,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Export contributions to CSV format"""
    import csv
    from io import StringIO
    from fastapi.responses import Response
    
    service = get_investment_contribution_service(conn=conn)
    
    if investment_id:
        contributions = service.list_contributions_by_investment(investment_id=investment_id)
    else:
        inv_service = get_investment_service(conn=conn)
        investments = inv_service.list_investments()
        contributions = []
        for inv in investments:
            contributions.extend(service.list_contributions_by_investment(investment_id=inv.id))
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['investment_id', 'date', 'amount', 'notes'])
    
    for contrib in contributions:
        writer.writerow([
            contrib.investment_id,
            contrib.date,
            contrib.amount,
            contrib.notes if contrib.notes else ''
        ])
    
    return Response(content=output.getvalue(), media_type="text/csv")


@router.post("/contributions/import/csv")
def import_contributions_csv(
    file_data: dict,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Import contributions from CSV format"""
    import csv
    from io import StringIO
    from decimal import Decimal
    from datetime import datetime
    
    service = get_investment_contribution_service(conn=conn)
    csv_content = file_data.get('file_content', '')
    
    reader = csv.DictReader(StringIO(csv_content))
    
    created = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            investment_id = row.get('investment_id', '').strip()
            date_str = row.get('date', '').strip()
            amount = Decimal(str(row.get('amount', 0)))
            notes = row.get('notes', '').strip() or None
            
            if not investment_id:
                errors.append(f"Row {row_num}: Investment ID is required")
                continue
            
            if not date_str:
                errors.append(f"Row {row_num}: Date is required")
                continue
            
            if amount <= 0:
                errors.append(f"Row {row_num}: Amount must be positive")
                continue
            
            contribution_date = datetime.fromisoformat(date_str).date()
            
            service.add_contribution(
                investment_id=investment_id,
                contribution_date=contribution_date,
                amount=amount,
                notes=notes
            )
            created += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    return {
        "created": created,
        "errors": errors,
        "total_rows": created + len(errors)
    }

# Made with Bob
