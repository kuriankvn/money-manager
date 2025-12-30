"""Account and Transaction API routes."""
import sqlite3
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.accounts.service import AccountService, TransactionService
from app.api.dependencies import (
    get_account_service,
    get_db,
    get_transaction_service,
)
from app.api.schemas import (
    AccountCreate,
    AccountResponse,
    TransactionCreate,
    TransactionResponse,
)


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountResponse)
def create_account(
    account_data: AccountCreate,
    conn: sqlite3.Connection = Depends(get_db)
):
    service = get_account_service(conn=conn)
    account = service.create_account(
        name=account_data.name,
        account_type=account_data.type,
        institution=account_data.institution,
        notes=account_data.notes
    )
    return AccountResponse(
        id=account.id,
        name=account.name,
        type=account.type,
        institution=account.institution,
        notes=account.notes
    )


@router.get("/", response_model=List[AccountResponse])
def list_accounts(conn: sqlite3.Connection = Depends(get_db)):
    service = get_account_service(conn=conn)
    accounts = service.list_accounts()
    return [
        AccountResponse(
            id=acc.id,
            name=acc.name,
            type=acc.type,
            institution=acc.institution,
            notes=acc.notes
        )
        for acc in accounts
    ]


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: str, conn: sqlite3.Connection = Depends(get_db)):
    service = get_account_service(conn=conn)
    account = service.get_account(account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountResponse(
        id=account.id,
        name=account.name,
        type=account.type,
        institution=account.institution,
        notes=account.notes
    )


@router.post("/transactions", response_model=TransactionResponse)
def create_transaction(
    txn_data: TransactionCreate,
    conn: sqlite3.Connection = Depends(get_db)
):
    service = get_transaction_service(conn=conn)
    transaction = service.create_transaction(
        account_id=txn_data.account_id,
        transaction_date=txn_data.date,
        amount=txn_data.amount,
        description=txn_data.description,
        category=txn_data.category,
        notes=txn_data.notes
    )
    return TransactionResponse(
        id=transaction.id,
        account_id=transaction.account_id,
        date=transaction.date,
        amount=transaction.amount,
        description=transaction.description,
        category=transaction.category,
        notes=transaction.notes
    )


@router.get("/transactions/", response_model=List[TransactionResponse])
def list_transactions(conn: sqlite3.Connection = Depends(get_db)):
    service = get_transaction_service(conn=conn)
    transactions = service.list_all_transactions()
    return [
        TransactionResponse(
            id=txn.id,
            account_id=txn.account_id,
            date=txn.date,
            amount=txn.amount,
            description=txn.description,
            category=txn.category,
            notes=txn.notes
        )
        for txn in transactions
    ]


@router.get("/{account_id}/transactions", response_model=List[TransactionResponse])
def list_account_transactions(
    account_id: str,
    conn: sqlite3.Connection = Depends(get_db)
):
    service = get_transaction_service(conn=conn)
    transactions = service.list_transactions_by_account(account_id=account_id)
    return [
        TransactionResponse(
            id=txn.id,
            account_id=txn.account_id,
            date=txn.date,
            amount=txn.amount,
            description=txn.description,
            category=txn.category,
            notes=txn.notes
        )
        for txn in transactions
    ]

@router.get("/transactions/export/csv")
def export_transactions_csv(
    account_id: str | None = None,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Export transactions to CSV format"""
    import csv
    from io import StringIO
    from fastapi.responses import Response
    
    service = get_transaction_service(conn=conn)
    
    if account_id:
        transactions = service.list_transactions_by_account(account_id=account_id)
    else:
        transactions = service.list_all_transactions()
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['account_id', 'date', 'amount', 'description', 'category', 'notes'])
    
    for txn in transactions:
        writer.writerow([
            txn.account_id,
            txn.date,
            txn.amount,
            txn.description,
            txn.category,
            txn.notes if txn.notes else ''
        ])
    
    return Response(content=output.getvalue(), media_type="text/csv")


@router.post("/transactions/import/csv")
def import_transactions_csv(
    file_data: dict,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Import transactions from CSV format"""
    import csv
    from io import StringIO
    from decimal import Decimal
    from datetime import datetime
    
    service = get_transaction_service(conn=conn)
    csv_content = file_data.get('file_content', '')
    
    reader = csv.DictReader(StringIO(csv_content))
    
    created = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            account_id = row.get('account_id', '').strip()
            date_str = row.get('date', '').strip()
            amount = Decimal(str(row.get('amount', 0)))
            description = row.get('description', '').strip()
            category = row.get('category', '').strip()
            notes = row.get('notes', '').strip() or None
            
            if not account_id:
                errors.append(f"Row {row_num}: Account ID is required")
                continue
            
            if not date_str:
                errors.append(f"Row {row_num}: Date is required")
                continue
            
            if not description:
                errors.append(f"Row {row_num}: Description is required")
                continue
            
            if not category:
                errors.append(f"Row {row_num}: Category is required")
                continue
            
            transaction_date = datetime.fromisoformat(date_str).date()
            
            service.create_transaction(
                account_id=account_id,
                transaction_date=transaction_date,
                amount=amount,
                description=description,
                category=category,
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
