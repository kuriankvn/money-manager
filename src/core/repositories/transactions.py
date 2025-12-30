from typing import Any
from core.repositories.base import BaseRepository
from core.domain import Category, Account, Transaction


class CategoryRepository(BaseRepository[Category]):
    @property
    def table_name(self) -> str:
        return "categories"
    
    @property
    def columns(self) -> list[str]:
        return ["name"]
    
    def _entity_to_values(self, entity: Category) -> tuple[Any, ...]:
        return (entity.uid, entity.name)
    
    def _row_to_entity(self, row: tuple[Any, ...]) -> Category:
        return Category(uid=row[0], name=row[1])


class AccountRepository(BaseRepository[Account]):
    @property
    def table_name(self) -> str:
        return "accounts"
    
    @property
    def columns(self) -> list[str]:
        return ["name"]
    
    def _entity_to_values(self, entity: Account) -> tuple[Any, ...]:
        return (entity.uid, entity.name)
    
    def _row_to_entity(self, row: tuple[Any, ...]) -> Account:
        return Account(uid=row[0], name=row[1])


class TransactionRepository(BaseRepository[Transaction]):
    @property
    def table_name(self) -> str:
        return "transactions"
    
    @property
    def columns(self) -> list[str]:
        return ["name", "amount", "date", "account_id", "category_id"]
    
    def _entity_to_values(self, entity: Transaction) -> tuple[Any, ...]:
        return (entity.uid, entity.name, entity.amount, entity.date, 
                entity.account_id, entity.category_id)
    
    def _row_to_entity(self, row: tuple[Any, ...]) -> Transaction:
        return Transaction(
            uid=row[0],
            name=row[1],
            amount=row[2],
            date=row[3],
            account_id=row[4],
            category_id=row[5])

# Made with Bob
