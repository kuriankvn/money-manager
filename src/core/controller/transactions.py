from typing import Optional
from fastapi import APIRouter, status, HTTPException
from core.repositories import CategoryRepository, AccountRepository, TransactionRepository
from core.domain import Category, Account, Transaction
from core.domain import CategorySchema, CategoryResponse, AccountSchema, AccountResponse, TransactionSchema, TransactionResponse
from core.controller.base import BaseController


# Category Controller
class CategoryController(BaseController[Category, CategorySchema, CategoryResponse]):
    """Category controller with CRUD operations"""
    
    def __init__(self) -> None:
        self._repository = CategoryRepository()
    
    @property
    def repository(self) -> CategoryRepository:
        return self._repository
    
    @property
    def entity_name(self) -> str:
        return "Category"
    
    def model_to_entity(self, uid: str, model: CategorySchema) -> Category:
        return Category(uid=uid, name=model.name)
    
    def entity_to_response(self, entity: Category) -> CategoryResponse:
        return CategoryResponse(uid=entity.uid, name=entity.name)


# Account Controller
class AccountController(BaseController[Account, AccountSchema, AccountResponse]):
    """Account controller with CRUD operations"""
    
    def __init__(self) -> None:
        self._repository = AccountRepository()
    
    @property
    def repository(self) -> AccountRepository:
        return self._repository
    
    @property
    def entity_name(self) -> str:
        return "Account"
    
    def model_to_entity(self, uid: str, model: AccountSchema) -> Account:
        return Account(uid=uid, name=model.name)
    
    def entity_to_response(self, entity: Account) -> AccountResponse:
        return AccountResponse(uid=entity.uid, name=entity.name)


# Transaction Controller
class TransactionController(BaseController[Transaction, TransactionSchema, TransactionResponse]):
    """Transaction controller with CRUD operations"""
    
    def __init__(self) -> None:
        self._repository = TransactionRepository()
        self.account_repo = AccountRepository()
        self.category_repo = CategoryRepository()
    
    @property
    def repository(self) -> TransactionRepository:
        return self._repository
    
    @property
    def entity_name(self) -> str:
        return "Transaction"
    
    def validate_dependencies(self, model: TransactionSchema) -> None:
        """Validate account and category exist"""
        account: Optional[Account] = self.account_repo.get_by_id(uid=model.account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        
        category: Optional[Category] = self.category_repo.get_by_id(uid=model.category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    def model_to_entity(self, uid: str, model: TransactionSchema) -> Transaction:
        return Transaction(
            uid=uid,
            name=model.name,
            amount=model.amount,
            date=model.date,
            account_id=model.account_id,
            category_id=model.category_id
        )
    
    def entity_to_response(self, entity: Transaction) -> TransactionResponse:
        return TransactionResponse(
            uid=entity.uid,
            name=entity.name,
            amount=entity.amount,
            date=entity.date,
            account_id=entity.account_id,
            category_id=entity.category_id
        )


# Initialize controllers and routers
category_controller: CategoryController = CategoryController()
categories_router: APIRouter = APIRouter(prefix="/categories", tags=["categories"])

account_controller: AccountController = AccountController()
accounts_router: APIRouter = APIRouter(prefix="/accounts", tags=["accounts"])

transaction_controller: TransactionController = TransactionController()
transactions_router: APIRouter = APIRouter(prefix="/transactions", tags=["transactions"])


# Category Routes
@categories_router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_data: CategorySchema) -> CategoryResponse:
    """Create a new category"""
    return category_controller.create(data=category_data)


@categories_router.get("/{uid}", response_model=CategoryResponse)
def get_category(uid: str) -> CategoryResponse:
    """Get category by ID"""
    return category_controller.get_by_id(uid)


@categories_router.get("/", response_model=list[CategoryResponse])
def get_all_categories() -> list[CategoryResponse]:
    """Get all categories"""
    return category_controller.get_all()


@categories_router.put("/{uid}", response_model=CategoryResponse)
def update_category(uid: str, category_data: CategorySchema) -> CategoryResponse:
    """Update category"""
    return category_controller.update(uid, data=category_data)


@categories_router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(uid: str) -> None:
    """Delete category"""
    category_controller.delete(uid)


# Account Routes
@accounts_router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account_data: AccountSchema) -> AccountResponse:
    """Create a new account"""
    return account_controller.create(data=account_data)


@accounts_router.get("/{uid}", response_model=AccountResponse)
def get_account(uid: str) -> AccountResponse:
    """Get account by ID"""
    return account_controller.get_by_id(uid)


@accounts_router.get("/", response_model=list[AccountResponse])
def get_all_accounts() -> list[AccountResponse]:
    """Get all accounts"""
    return account_controller.get_all()


@accounts_router.put("/{uid}", response_model=AccountResponse)
def update_account(uid: str, account_data: AccountSchema) -> AccountResponse:
    """Update account"""
    return account_controller.update(uid, data=account_data)


@accounts_router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(uid: str) -> None:
    """Delete account"""
    account_controller.delete(uid)


# Transaction Routes
@transactions_router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionSchema) -> TransactionResponse:
    """Create a new transaction"""
    return transaction_controller.create(transaction_data)


@transactions_router.get("/{uid}", response_model=TransactionResponse)
def get_transaction(uid: str) -> TransactionResponse:
    """Get transaction by ID"""
    return transaction_controller.get_by_id(uid)


@transactions_router.get("/", response_model=list[TransactionResponse])
def get_all_transactions() -> list[TransactionResponse]:
    """Get all transactions"""
    return transaction_controller.get_all()


@transactions_router.put("/{uid}", response_model=TransactionResponse)
def update_transaction(uid: str, transaction_data: TransactionSchema) -> TransactionResponse:
    """Update transaction"""
    return transaction_controller.update(uid, data=transaction_data)


@transactions_router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(uid: str) -> None:
    """Delete transaction"""
    transaction_controller.delete(uid)

# Made with Bob
