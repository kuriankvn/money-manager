from fastapi import APIRouter, HTTPException, status
from core.repositories.transaction import TransactionRepository
from core.repositories.user import UserRepository
from core.repositories.category import CategoryRepository
from core.models.transaction import Transaction, TransactionType
from core.models.user import User
from core.models.category import Category
from core.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from core.utils import generate_uid

router: APIRouter = APIRouter(prefix="/transactions", tags=["transactions"])
transaction_repo: TransactionRepository = TransactionRepository()
user_repo: UserRepository = UserRepository()
category_repo: CategoryRepository = CategoryRepository()


@router.post(path="/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionCreate) -> TransactionResponse:
    """Create a new transaction"""
    user: User | None = user_repo.get_by_id(uid=transaction_data.user_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    category: Category | None = category_repo.get_by_id(uid=transaction_data.category_uid)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    uid: str = generate_uid()
    transaction: Transaction = Transaction(
        uid=uid,
        name=transaction_data.name,
        amount=transaction_data.amount,
        datetime=transaction_data.datetime,
        type=TransactionType(value=transaction_data.type),
        user=user,
        category=category
    )
    transaction_repo.create(entity=transaction)
    return TransactionResponse(
        uid=transaction.uid,
        name=transaction.name,
        amount=transaction.amount,
        datetime=transaction.datetime,
        type=transaction.type.value,
        user_uid=user.uid,
        user_name=user.name,
        category_uid=category.uid,
        category_name=category.name
    )


@router.get(path="/{uid}", response_model=TransactionResponse)
def get_transaction(uid: str) -> TransactionResponse:
    """Get transaction by ID"""
    transaction: Transaction | None = transaction_repo.get_by_id(uid=uid)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return TransactionResponse(
        uid=transaction.uid,
        name=transaction.name,
        amount=transaction.amount,
        datetime=transaction.datetime,
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
            datetime=txn.datetime,
            type=txn.type.value,
            user_uid=txn.user.uid,
            user_name=txn.user.name,
            category_uid=txn.category.uid,
            category_name=txn.category.name
        )
        for txn in transactions
    ]


@router.put(path="/{uid}", response_model=TransactionResponse)
def update_transaction(uid: str, transaction_data: TransactionUpdate) -> TransactionResponse:
    """Update transaction"""
    existing_transaction: Transaction | None = transaction_repo.get_by_id(uid=uid)
    if not existing_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    
    user: User | None = user_repo.get_by_id(uid=transaction_data.user_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    category: Category | None = category_repo.get_by_id(uid=transaction_data.category_uid)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    transaction: Transaction = Transaction(
        uid=uid,
        name=transaction_data.name,
        amount=transaction_data.amount,
        datetime=transaction_data.datetime,
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
        datetime=transaction.datetime,
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
