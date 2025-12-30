from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import Response
from core.repositories import TransactionRepository, UserRepository, CategoryRepository
from core.models import Transaction, TransactionType, User, Category
from core.schemas import TransactionSchema, TransactionResponse
from core.utils import generate_uid
from core.services import TransactionService

router: APIRouter = APIRouter(prefix="/transactions", tags=["transactions"])
transaction_repo: TransactionRepository = TransactionRepository()
user_repo: UserRepository = UserRepository()
category_repo: CategoryRepository = CategoryRepository()
transaction_service: TransactionService = TransactionService()


@router.post(path="/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionSchema) -> TransactionResponse:
    """Create a new transaction"""
    user: Optional[User] = user_repo.get_by_id(uid=transaction_data.user_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    category: Optional[Category] = category_repo.get_by_id(uid=transaction_data.category_uid)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    uid: str = generate_uid()
    transaction: Transaction = Transaction(
        uid=uid,
        name=transaction_data.name,
        amount=transaction_data.amount,
        date=transaction_data.date,
        type=TransactionType(value=transaction_data.type),
        user=user,
        category=category
    )
    transaction_repo.create(entity=transaction)
    return TransactionResponse(
        uid=transaction.uid,
        name=transaction.name,
        amount=transaction.amount,
        date=transaction.date,
        type=transaction.type.value,
        user_uid=user.uid,
        user_name=user.name,
        category_uid=category.uid,
        category_name=category.name
    )


@router.get(path="/{uid}", response_model=TransactionResponse)
def get_transaction(uid: str) -> TransactionResponse:
    """Get transaction by ID"""
    transaction: Optional[Transaction] = transaction_repo.get_by_id(uid=uid)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return TransactionResponse(
        uid=transaction.uid,
        name=transaction.name,
        amount=transaction.amount,
        date=transaction.date,
        type=transaction.type.value,
        user_uid=transaction.user.uid,
        user_name=transaction.user.name,
        category_uid=transaction.category.uid,
        category_name=transaction.category.name
    )


@router.get(path="/", response_model=list[TransactionResponse])
def get_all_transactions() -> list[TransactionResponse]:
    """Get all transactions"""
    transactions: list[Transaction] = transaction_repo.get_all()
    return [
        TransactionResponse(
            uid=txn.uid,
            name=txn.name,
            amount=txn.amount,
            date=txn.date,
            type=txn.type.value,
            user_uid=txn.user.uid,
            user_name=txn.user.name,
            category_uid=txn.category.uid,
            category_name=txn.category.name
        )
        for txn in transactions
    ]


@router.put(path="/{uid}", response_model=TransactionResponse)
def update_transaction(uid: str, transaction_data: TransactionSchema) -> TransactionResponse:
    """Update transaction"""
    existing_transaction: Optional[Transaction] = transaction_repo.get_by_id(uid=uid)
    if not existing_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    
    user: Optional[User] = user_repo.get_by_id(uid=transaction_data.user_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    category: Optional[Category] = category_repo.get_by_id(uid=transaction_data.category_uid)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    transaction: Transaction = Transaction(
        uid=uid,
        name=transaction_data.name,
        amount=transaction_data.amount,
        date=transaction_data.date,
        type=TransactionType(value=transaction_data.type),
        user=user,
        category=category
    )
    success: bool = transaction_repo.update(entity=transaction)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Update failed")
    
    return TransactionResponse(
        uid=transaction.uid,
        name=transaction.name,
        amount=transaction.amount,
        date=transaction.date,
        type=transaction.type.value,
        user_uid=user.uid,
        user_name=user.name,
        category_uid=category.uid,
        category_name=category.name
    )


@router.delete(path="/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(uid: str) -> None:
    """Delete transaction"""
    success: bool = transaction_repo.delete(uid=uid)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")



@router.get(path="/export/csv", response_class=Response)
def export_transactions_csv() -> Response:
    """Export all transactions to CSV"""
    csv_content: str = transaction_service.export_to_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"}
    )


@router.post(path="/import/csv", status_code=status.HTTP_201_CREATED)
def import_transactions_csv(file_content: str = Body(default=..., embed=True)) -> dict[str, Any]:
    """Import transactions from CSV"""
    return transaction_service.import_from_csv(csv_content=file_content)
