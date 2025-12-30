"""Money Manager Package - Main Package"""
from core.storage import init_database, get_connection
from core.repositories import (
    IRepository,
    CategoryRepository,
    TransactionRepository,
    SubscriptionRepository,
)
from core.domain import (
    Category,
    Transaction,
    Subscription,
)

__version__ = "0.1.0"
__all__ = [
    "__version__",
    "init_database",
    "get_connection",
    "IRepository",
    "Category",
    "CategoryRepository",
    "Transaction",
    "TransactionRepository",
    "Subscription",
    "SubscriptionRepository",
]
